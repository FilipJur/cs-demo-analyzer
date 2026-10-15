"""The single Awpy import boundary and ``foundation-v1`` extraction.

``extract`` reads one demo file read-only, batches the six primitive datasets,
takes full-rate typed snapshots (``every=1``), normalizes them through
:mod:`.normalize` and writes the bounded canonical Parquet tables plus
``manifest.json`` into ``request.output_dir``. It never touches the catalog,
storage, SQLite or the app-owned data root: the caller supplies a staging path
and validates/publishes afterwards.
"""

from __future__ import annotations

import errno
import hashlib
import math
import os
import re
from pathlib import Path

import polars as pl
from awpy import Demo, InvalidDemoError

from ..domain.contracts import (
    NORMALIZER_VERSION,
    PARSER_VERSION,
    PROFILE_KEY,
    SCHEMA_VERSION,
    AppError,
    Capability,
    ExtractionRequest,
    Manifest,
    TableDescriptor,
)
from ..domain.tables import SCHEMAS
from .normalize import normalize_tables

MANIFEST_NAME = "manifest.json"
TABLE_SUFFIX = ".parquet"
PARQUET_COMPRESSION = "zstd"

#: The six batched primitive datasets; ``player_state`` comes from snapshots.
LOADED_DATASETS = ("players", "rounds", "kills", "damages", "shots", "bomb")

#: Provenance for each canonical table's capability entry.
TABLE_SOURCES = {
    "players": "awpy.Demo.players",
    "rounds": "awpy.Demo.rounds",
    "player_state": "awpy.Demo.snapshots(every=1)",
    "kills": "awpy.Demo.kills",
    "damages": "awpy.Demo.damages",
    "shots": "awpy.Demo.shots",
    "bomb": "awpy.Demo.bomb",
}

_DIGITS = re.compile(r"\d{6,}")
_CLIENT_VERSION_KEYS = ("demo_version_name", "game_directory")

_BOOLEAN_CAVEAT = (
    "Snapshot reload columns may be null when the active weapon omits the field; "
    "upstream defaulted Booleans are dataset semantics, not proof the wire recorded false."
)
_DAMAGE_CAVEAT = (
    "Upstream damage pre-hit health/armor are estimates and are not normalized; only "
    "dmg_health/dmg_armor are canonical."
)


def extract(request: ExtractionRequest) -> Manifest:
    """Extract and write one ``foundation-v1`` generation; return its manifest."""
    source = Path(request.input_path)
    output = Path(request.output_dir)
    source_size = _source_size(source)

    demo = _open_demo(source)
    demo.load(*LOADED_DATASETS)
    snapshots = demo.snapshots(every=1)
    raw = {
        "players": demo.players,
        "rounds": demo.rounds,
        "player_state": snapshots,
        "kills": demo.kills,
        "damages": demo.damages,
        "shots": demo.shots,
        "bomb": demo.bomb,
    }
    frames, warnings = normalize_tables(raw)

    quality = "complete"
    if _any_is_partial(frames, warnings):
        quality = "partial"

    header = demo.header or {}
    map_name = str(header.get("map_name") or "unknown")
    rate = _tick_rate(demo)
    demo_client_version, demo_version_source = _client_version(header)

    tables = _write_tables(output, frames)
    capabilities = _capabilities(frames, warnings)
    warnings = [*warnings, _BOOLEAN_CAVEAT]

    manifest = Manifest(
        demo_id=request.demo_id,
        job_id=request.job_id,
        generation_id=request.generation_id,
        profile_key=PROFILE_KEY,
        parser_version=PARSER_VERSION,
        normalizer_version=NORMALIZER_VERSION,
        source_size=source_size,
        map_name=map_name,
        tick_rate_hz=rate,
        demo_client_version=demo_client_version,
        demo_version_source=demo_version_source,
        quality=quality,
        tables=tables,
        capabilities=capabilities,
        warnings=warnings,
    )
    _write_manifest(output, manifest)
    return manifest


def _source_size(source: Path) -> int:
    try:
        info = source.stat()
    except FileNotFoundError as exc:
        raise AppError("SOURCE_MISSING", f"Input demo {source} does not exist", "parse", True) from exc
    except PermissionError as exc:
        raise AppError("PERMISSION_DENIED", f"Input demo {source} is not readable", "parse") from exc
    if not source.is_file() or info.st_size == 0:
        raise AppError("SOURCE_MISSING", f"Input demo {source} is not a non-empty regular file", "parse", True)
    return info.st_size


def _open_demo(source: Path) -> Demo:
    try:
        return Demo(str(source))
    except FileNotFoundError as exc:
        raise AppError("SOURCE_MISSING", f"Input demo {source} does not exist", "parse", True) from exc
    except InvalidDemoError as exc:
        raise AppError("INVALID_DEMO", f"Input {source} is not a valid CS2 demo", "parse") from exc


def _tick_rate(demo: Demo) -> float:
    try:
        rate = float(demo.tick_rate)
    except (TypeError, ValueError) as exc:
        raise AppError("PARSE_FAILED", "Demo tick rate is unavailable", "parse") from exc
    if not math.isfinite(rate) or rate <= 0:
        raise AppError("PARSE_FAILED", "Demo tick rate must be finite and positive", "parse")
    return rate


def _digits(value: object) -> str | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        match = _DIGITS.search(value)
        return match.group(0) if match else None
    return None


def _client_version(header: dict) -> tuple[str | None, str | None]:
    for key in _CLIENT_VERSION_KEYS:
        version = _digits(header.get(key))
        if version:
            return version, f"awpy.Demo.header.{key}"
    return None, None


def _any_is_partial(frames: dict[str, pl.DataFrame], warnings: list[str]) -> bool:
    if frames["players"].height and int(
        frames["players"].select(pl.col("steam_id").is_null().sum()).item()
    ):
        return True
    if frames["player_state"].height and int(
        frames["player_state"].select(pl.col("player_id").is_null().sum()).item()
    ):
        return True
    return any("non-finite player_state" in warning for warning in warnings)


def _write_tables(output: Path, frames: dict[str, pl.DataFrame]) -> dict[str, TableDescriptor]:
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptors: dict[str, TableDescriptor] = {}
    for table in SCHEMAS:
        frame = frames[table]
        path = output / f"{table}{TABLE_SUFFIX}"
        _guard_disk(lambda: frame.write_parquet(path, compression=PARQUET_COMPRESSION))
        _fsync_file(path)
        descriptors[table] = TableDescriptor(
            path=path.name,
            row_count=frame.height,
            sha256=_sha256(path),
            schema_version=SCHEMA_VERSION,
        )
    return descriptors


def _write_manifest(output: Path, manifest: Manifest) -> None:
    payload = manifest.model_dump_json(indent=2).encode("utf-8") + b"\n"
    path = output / MANIFEST_NAME
    _guard_disk(lambda: path.write_bytes(payload))
    _fsync_file(path)


def _capabilities(frames: dict[str, pl.DataFrame], warnings: list[str]) -> dict[str, Capability]:
    capabilities: dict[str, Capability] = {}
    for table in SCHEMAS:
        rows = frames[table].height
        capabilities[table] = Capability(
            status="available" if rows else "absent",
            source=TABLE_SOURCES[table],
            note=f"{rows} rows" if rows else "supported dataset, no rows in this recording",
        )
    capabilities["player_identity"] = Capability(
        status="available",
        source="awpy SteamID64 (UInt64)",
        note=(
            "positive IDs map to steam:<exact decimal>; null/zero IDs never join: "
            "unresolved state/event references stay null and each unknown roster "
            "record keeps unresolved:roster:<ordinal>"
        ),
    )
    capabilities["side_vocabulary"] = Capability(
        status="available",
        source="awpy team names",
        note="terrorist/counter-terrorist -> t/ct; spectator preserved; other/null -> unknown",
    )
    capabilities["snapshot_reload_flags"] = Capability(
        status="available",
        source="awpy.Demo.snapshots is_reloading/is_silent_reloading",
        note=_BOOLEAN_CAVEAT,
    )
    capabilities["damage_pre_hit_estimates"] = Capability(
        status="available",
        source="awpy.Demo.damages health_pre/armor_pre",
        note=_DAMAGE_CAVEAT,
    )
    if any("non-finite player_state" in warning for warning in warnings):
        capabilities["player_state_finite_check"] = Capability(
            status="available",
            source="normalize.player_state",
            note="non-finite coordinate/angle/velocity values were replaced with null",
        )
    return capabilities


def _guard_disk(action) -> None:
    try:
        action()
    except OSError as exc:
        if exc.errno == errno.ENOSPC:
            raise AppError(
                "DISK_FULL", "No space left while writing the staged generation", "parse", True
            ) from exc
        raise


def _fsync_file(path: Path) -> None:
    _guard_disk(lambda: _fsync_impl(path))


def _fsync_impl(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()

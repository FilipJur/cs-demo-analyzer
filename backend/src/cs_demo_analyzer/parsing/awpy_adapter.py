"""The single Awpy import boundary and per-profile extraction.

``extract`` reads one demo file read-only, batches the primitive datasets of the
requested named profile, takes full-rate typed snapshots (``every=1``),
normalizes them through :mod:`.normalize` and writes that profile's canonical
Parquet tables plus ``manifest.json`` into ``request.output_dir``. It never
touches the catalog, storage, SQLite or the app-owned data root: the caller
supplies a staging path and validates/publishes afterwards.

Two profiles exist. ``foundation-v1`` batches the six primitive datasets and
writes its seven frozen tables. ``reconstruction-v1`` writes the same seven
tables with unchanged semantics plus the extended typed tables; it therefore
batches the utility/economy datasets as well. Neither profile invents a value
upstream does not record.
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
    PARSER_VERSION,
    PROFILE_NAME,
    RECONSTRUCTION_PROFILE_NAME,
    AppError,
    Capability,
    ExtractionRequest,
    Manifest,
    TableDescriptor,
    normalizer_version_for,
    profile_key_for,
    schema_version_for,
)
from ..domain.tables import schema_for_profile
from .normalize import LIFECYCLE_KINDS, normalize_tables

MANIFEST_NAME = "manifest.json"
TABLE_SUFFIX = ".parquet"
PARQUET_COMPRESSION = "zstd"

#: The six batched primitive datasets; ``player_state`` comes from snapshots.
LOADED_DATASETS = ("players", "rounds", "kills", "damages", "shots", "bomb")

#: Datasets only ``reconstruction-v1`` batches (utility, economy, lifecycles).
EXTENDED_DATASETS = ("blinds", "fires", "smokes", "grenades", "item_events", "round_economy")

#: Recorded lifecycle events read from ``awpy.Demo.events`` (only those present
#: in a recording contribute rows) and normalized into ``player_lifecycle``.
LIFECYCLE_EVENTS: tuple[str, ...] = tuple(LIFECYCLE_KINDS.values())

#: Datasets batched per profile; ``player_state``/``player_state_ext`` come from
#: the single full-rate snapshot call.
DATASETS_BY_PROFILE: dict[str, tuple[str, ...]] = {
    PROFILE_NAME: LOADED_DATASETS,
    RECONSTRUCTION_PROFILE_NAME: LOADED_DATASETS + EXTENDED_DATASETS,
}

#: Provenance for each canonical table's capability entry.
TABLE_SOURCES = {
    "players": "awpy.Demo.players",
    "rounds": "awpy.Demo.rounds",
    "player_state": "awpy.Demo.snapshots(every=1)",
    "kills": "awpy.Demo.kills",
    "damages": "awpy.Demo.damages",
    "shots": "awpy.Demo.shots",
    "bomb": "awpy.Demo.bomb",
    "player_state_ext": "awpy.Demo.snapshots(every=1)",
    "blinds": "awpy.Demo.blinds",
    "smokes": "awpy.Demo.smokes",
    "fires": "awpy.Demo.fires",
    "grenades": "awpy.Demo.grenades",
    "item_events": "awpy.Demo.item_events",
    "round_economy": "awpy.Demo.round_economy",
    "player_lifecycle": (
        "awpy.Demo.events(player_disconnect|player_connect_full|player_spawn|player_team)"
    ),
}

#: Tables whose upstream owner/thrower identity may be absent from a recording.
UTILITY_OWNER_TABLES = ("grenades", "smokes", "fires")

#: Extended tables whose published values are not one recorded event stream, with
#: the upstream basis. Published verbatim with this provenance; never re-derived,
#: contradicted or presented as a raw event stream by this project.
UPSTREAM_PROVENANCE_NOTES = {
    "blinds": (
        "upstream reconstruction from pawn flash state + flashbang_detonate "
        "(awpy documents it also works where player_blind is absent)"
    ),
    "item_events": (
        "upstream reconstruction from inventory state "
        "(awpy documents it also works where item_purchase is absent)"
    ),
    "grenades": "grenade entity state sampled once per tick while the projectile is live",
    "smokes": "deployed smoke-cloud entity lifetime, as upstream's [start_tick, end_tick]",
    "fires": "burning inferno entity lifetime, as upstream's [start_tick, end_tick]",
    "round_economy": (
        "recorded team equipment total at freeze end; buy_type is upstream's deterministic "
        "classification of it (eco < 5000, force < 20000, full otherwise; the first round of "
        "each half is pistol ahead of any value), not a recorded field"
    ),
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
_VIEW_ORIGIN_NOTE = (
    "no eye-origin feature is exposed by awpy 3.0.0; player_state.x/y/z is the entity "
    "origin and yaw/pitch are the recorded eye angles, so a view origin must be derived "
    "from the recorded is_crouched flag (engine view offset 64 standing / 46 crouched)"
)


def extract(request: ExtractionRequest) -> Manifest:
    """Extract and write one generation of ``request.profile``; return its manifest."""
    source = Path(request.input_path)
    output = Path(request.output_dir)
    profile = request.profile
    profile_key = profile_key_for(profile)
    if request.profile_key is not None and request.profile_key != profile_key:
        raise AppError(
            "INVALID_PROFILE",
            f"request claims profile_key {request.profile_key!r} but profile {profile!r} "
            f"is {profile_key!r}; refusing to write a mislabeled generation",
            "parse",
        )
    schemas = schema_for_profile(profile)
    source_size = _source_size(source)

    demo = _open_demo(source)
    datasets = DATASETS_BY_PROFILE[profile]
    demo.load(*datasets)
    snapshots = demo.snapshots(every=1)
    raw = {name: getattr(demo, name) for name in datasets}
    raw["player_state"] = snapshots
    if profile == RECONSTRUCTION_PROFILE_NAME:
        present = set(demo.events.names)
        raw["lifecycle_events"] = {
            name: demo.events[name] for name in LIFECYCLE_EVENTS if name in present
        }
    frames, warnings = normalize_tables(raw, profile)

    quality = "complete"
    if _any_is_partial(frames, warnings):
        quality = "partial"

    header = demo.header or {}
    map_name = str(header.get("map_name") or "unknown")
    rate = _tick_rate(demo)
    demo_client_version, demo_version_source = _client_version(header)

    tables = _write_tables(output, frames, schemas, schema_version_for(profile))
    capabilities = _capabilities(frames, warnings, schemas)
    warnings = [*warnings, _BOOLEAN_CAVEAT]

    manifest = Manifest(
        demo_id=request.demo_id,
        job_id=request.job_id,
        generation_id=request.generation_id,
        profile=profile,
        profile_key=profile_key,
        parser_version=PARSER_VERSION,
        normalizer_version=normalizer_version_for(profile),
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


def _write_tables(
    output: Path,
    frames: dict[str, pl.DataFrame],
    schemas: dict[str, dict[str, pl.DataType]],
    schema_version: int,
) -> dict[str, TableDescriptor]:
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptors: dict[str, TableDescriptor] = {}
    for table in schemas:
        frame = frames[table]
        path = output / f"{table}{TABLE_SUFFIX}"
        _guard_disk(lambda: frame.write_parquet(path, compression=PARQUET_COMPRESSION))
        _fsync_file(path)
        descriptors[table] = TableDescriptor(
            path=path.name,
            row_count=frame.height,
            sha256=_sha256(path),
            schema_version=schema_version,
        )
    return descriptors


def _write_manifest(output: Path, manifest: Manifest) -> None:
    payload = manifest.model_dump_json(indent=2).encode("utf-8") + b"\n"
    path = output / MANIFEST_NAME
    _guard_disk(lambda: path.write_bytes(payload))
    _fsync_file(path)


def _capabilities(
    frames: dict[str, pl.DataFrame],
    warnings: list[str],
    schemas: dict[str, dict[str, pl.DataType]],
) -> dict[str, Capability]:
    capabilities: dict[str, Capability] = {}
    for table in schemas:
        rows = frames[table].height
        note = f"{rows} rows" if rows else "supported dataset, no rows in this recording"
        reconstruction = UPSTREAM_PROVENANCE_NOTES.get(table)
        if rows and reconstruction:
            note = f"{note}; {reconstruction}"
        capabilities[table] = Capability(
            status="available" if rows else "absent",
            source=TABLE_SOURCES[table],
            note=note,
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
        status="unsupported",
        source="awpy.Demo.damages health_pre/armor_pre/health_post/armor_post",
        note=_DAMAGE_CAVEAT,
    )
    if any("non-finite player_state" in warning for warning in warnings):
        capabilities["player_state_finite_check"] = Capability(
            status="available",
            source="normalize.player_state",
            note="non-finite coordinate/angle/velocity values were replaced with null",
        )
    if "player_state_ext" in schemas:
        capabilities["player_state_ext_alignment"] = Capability(
            status="available",
            source="awpy.Demo.snapshots(every=1)",
            note=(
                "player_state_ext is projected from the same full-rate snapshot frame as "
                "player_state, so row_ordinal addresses the identical observation"
            ),
        )
        capabilities["snapshot_blindness_fields"] = Capability(
            status="available",
            source="awpy.Demo.snapshots is_blinded/flash_duration",
            note=(
                "player_state_ext.is_blinded mirrors m_bFlashing and was false in every row of "
                "the recorded GOTV demos, while flash_duration (m_flFlashDuration) is populated; "
                "the recorded player_blind events are the `blinds` table. Treat is_blinded as "
                "unreliable and prefer flash_duration or `blinds`"
            ),
        )
        capabilities["player_view_origin"] = Capability(
            status="absent", source="awpy 3.0.0 SNAPSHOT_PROPERTIES", note=_VIEW_ORIGIN_NOTE
        )
        capabilities["match_statistics"] = Capability(
            status="unsupported",
            source="awpy.Demo.stats / Demo.player_stats / Demo.chat / Demo.convars",
            note=(
                "maintained upstream but not normalized: they are derived or per-match "
                "aggregates, not recorded per-tick state or events"
            ),
        )
        capabilities["raw_engine_events"] = Capability(
            status="unsupported",
            source="awpy.Demo.events / Demo.ticks",
            note=(
                "an untyped per-demo event dump and an arbitrary-property reader; only the "
                "named typed datasets are canonical and no untyped dump is published"
            ),
        )
        capabilities["utility_owner_attribution"] = _utility_owner_capability(frames)
        capabilities["player_lifecycle_kinds"] = _lifecycle_capability(frames["player_lifecycle"])
        capabilities["derived_upstream_classifications"] = Capability(
            status="unsupported",
            source="awpy.Demo.kills is_trade/victim_traded and awpy.Demo.stats",
            note=(
                "upstream *derived* classifications are deliberately not published: awpy's "
                "is_trade/victim_traded apply a computed 5.25-second trade window and its stats "
                "are derived aggregates. This profile publishes recorded fields and upstream "
                "entity/id state only, never a computed exchange or performance label"
            ),
        )
        capabilities["round_economy_buy_type"] = Capability(
            status="available",
            source="awpy.Demo.round_economy buy_type (crates/awpy/src/datasets.rs buy_type)",
            note=(
                "buy_type is upstream's deterministic classification of the recorded team "
                "equipment total at freeze end: eco < 5000, force < 20000, full otherwise; the "
                "first round overall and the first round where most shared players switched side "
                "are labelled pistol ahead of any value. Values observed: pistol/eco/force/full. "
                "A documented computation over a recorded value - not a recorded engine field and "
                "not a tactical or coaching verdict"
            ),
        )
        capabilities["extended_snapshot_flag_provenance"] = Capability(
            status="available",
            source="awpy.SNAPSHOT_PROPERTIES feature -> network property/derivation",
            note=(
                "player_state_ext flags are awpy's deterministic readings of recorded network "
                "properties (each feature is mapped in awpy's own SNAPSHOT_PROPERTIES, e.g. "
                "is_walking = m_bIsWalking, is_jumping = m_fFlags FL_ONGROUND clear, "
                "has_helmet/has_defuser = m_pItemServices, grenade counts and inventory = "
                "m_hMyWeapons, is_defusing = m_bIsDefusing, flash_duration = m_flFlashDuration). "
                + _BOOLEAN_CAVEAT
            ),
        )
        capabilities["snapshot_inventory_serialization"] = Capability(
            status="available",
            source="awpy.Demo.snapshots inventory (m_pWeaponServices.m_hMyWeapons)",
            note=(
                "player_state_ext.inventory is upstream's own text serialization of the resolved "
                "weapon handles: comma-separated weapon class names in slot order (observed "
                "verbatim on the recorded demos, e.g. 'knife,usp_silencer,m4a1,incendiary,"
                "hegrenade,flashbang'). An empty string means no weapon entity was resolved for "
                "that observation, which is not an empty loadout. Treat it as opaque text and use "
                "primary_weapon/secondary_weapon, the per-type grenade counts and "
                "has_helmet/has_defuser for structured facts"
            ),
        )
    return capabilities


def _lifecycle_capability(frame: pl.DataFrame) -> Capability:
    """Which recorded lifecycle kinds exist, and how much identity they resolve."""
    source = TABLE_SOURCES["player_lifecycle"]
    if frame.height == 0:
        return Capability(
            status="absent",
            source=source,
            note="no connect/disconnect/spawn/team-change event is recorded in this demo",
        )
    counts = frame.group_by("kind").len().sort("kind")
    detail = ", ".join(f"{row['kind']}={row['len']}" for row in counts.iter_rows(named=True))
    resolved = frame.height - int(frame.select(pl.col("player_id").is_null().sum()).item())
    return Capability(
        status="available",
        source=source,
        note=(
            f"{detail}; player_id is resolved from an event-recorded SteamID64 on "
            f"{resolved} of {frame.height} rows (only player_disconnect records one), "
            "other kinds keep the recorded connection slot and pawn handle with a null player_id"
        ),
    )


def _utility_owner_capability(frames: dict[str, pl.DataFrame]) -> Capability:
    """Whether any smoke/fire/grenade row carries an upstream thrower identity."""
    resolved = 0
    total = 0
    for table in UTILITY_OWNER_TABLES:
        frame = frames[table]
        total += frame.height
        resolved += frame.height - int(frame.select(pl.col("owner_id").is_null().sum()).item())
    if resolved:
        return Capability(
            status="available",
            source="awpy.Demo.grenades|smokes|fires thrower_steamid",
            note=f"{resolved} of {total} utility rows carry a resolved thrower identity",
        )
    return Capability(
        status="absent",
        source="awpy.Demo.grenades|smokes|fires thrower_steamid",
        note=(
            "no utility row carries an upstream thrower identity in this recording (all "
            "thrower_steamid are null); owner_id/owner_side stay null/unknown and utility "
            "instances are identified only by entity_id/entity_serial"
        ),
    )


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

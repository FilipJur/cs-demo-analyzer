"""Local radar assets: Source2Viewer extraction plus overview normalization (T4).

Reads are limited to the local CS2 installation; writes are limited to
``<data_root>/assets/<ClientVersion>/<map>/`` holding the raw ``overview.txt``,
``radar.png``, one ``<floor>.png`` per declared extra altitude section and a
``manifest.json``. The CLI is provisioned by the caller: a missing tool, install,
pak or texture yields an explicit descriptor warning, never a fabricated image.
Asset IDs are ``radar:<client version>:<map>[:<floor>]`` and
:meth:`RadarService.asset_path` only resolves PNGs listed in a validated cache
manifest, never a caller-supplied path.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any

from srctools.keyvalues import Keyvalues, LeafKeyvalueError, NoKeyError

from ..domain.contracts import AppError, RadarDescriptor, utc_now

CLI_VERSION = "20.1"  # pinned Source2Viewer-CLI release
CLI_TIMEOUT = 120.0
CACHE_SCHEMA = 1
MAX_FLOORS = 4
UNKNOWN_VERSION = "unknown"
OVERVIEW_ENTRY = "resource/overviews/{map}.txt"
RADAR_ENTRY = "panorama/images/overheadmaps/{map}_radar_psd.vtex_c"
FLOOR_ENTRY = "panorama/images/overheadmaps/{map}_{floor}_radar_psd.vtex_c"
MAP_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]{0,63}$")
FLOOR_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]{0,31}$")
ASSET_PATTERN = re.compile(
    r"^radar:(?P<version>[a-z0-9]{1,16}):(?P<map>[a-z0-9][a-z0-9_]{0,63})"
    r"(?::(?P<floor>[a-z0-9][a-z0-9_]{0,31}))?$"
)
STEAM_INF = "game/csgo/steam.inf"
PAK_RELATIVE = "game/csgo/pak01_dir.vpk"
# steam.inf is Valve's unquoted key=value file, which is not KV1.
CLIENT_VERSION = re.compile(r'ClientVersion\s*=\s*"?(\d{1,12})', re.IGNORECASE)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class RadarService:
    """Extract, cache and describe the local radar asset for one map."""

    def __init__(
        self, data_root: Path, install_path: Path | None = None, executable: Path | None = None
    ) -> None:
        self.data_root = Path(data_root)
        self.install_path = Path(install_path) if install_path else None
        self.executable = Path(executable) if executable else None
        self._extraction = threading.Lock()

    def resolve(self, map_name: str, demo_version: str | None = None) -> RadarDescriptor:
        """Describe the map's radar asset, extracting it into cache if needed.

        Total by contract: the name comes from parsed demo data, so an unusable
        name is an explicit absence with no filesystem or tool access.
        """
        name = map_name.strip().casefold() if isinstance(map_name, str) else ""
        demo = _version(demo_version)
        installed = _client_version(self.install_path)
        status = "unknown" if not (installed and demo) else ("exact" if installed == demo else "mismatch")
        notes: list[str] = []
        if status == "mismatch":
            notes.append(
                f"radar assets are from installed client {installed} but the demo was recorded with "
                f"{demo}; geometry is current-build, not historical"
            )

        def absent(reason: str) -> RadarDescriptor:
            return RadarDescriptor(
                asset_id=None, map_name=name, installed_client_version=installed,
                demo_client_version=demo, match_status=status, warning=_warning(*notes, reason),
            )

        if not MAP_PATTERN.match(name):
            return absent(
                f"unsupported map name {str(map_name).strip()[:64]!r}; expected a resource name like 'de_inferno'"
            )
        version = installed or UNKNOWN_VERSION
        cache = self.data_root / "assets" / version / name
        manifest = _read_manifest(cache, version, name)
        if manifest is None:
            if self.install_path is None:
                return absent("no CS2 installation path is configured; radar assets are unavailable")
            executable = self.executable if self.executable and self.executable.is_file() else None
            if executable is None:
                return absent(f"Source2Viewer CLI {CLI_VERSION} is not provisioned; cannot extract assets")
            pak = self.install_path / PAK_RELATIVE
            if not pak.is_file():
                return absent(f"pak01_dir.vpk was not found under {self.install_path}")
            try:
                with self._extraction:  # one extraction at a time; re-check under the lock
                    manifest = _read_manifest(cache, version, name) or self._extract(
                        executable, pak, cache, version, name, demo
                    )
            except AppError as error:
                return absent(error.message)
        return _descriptor(manifest, version, name, installed, demo, status, notes)

    def asset_path(self, asset_id: str) -> Path | None:
        """Resolve a cache-owned radar PNG ID, or ``None`` for anything else."""
        matched = ASSET_PATTERN.match(asset_id.strip()) if isinstance(asset_id, str) else None
        if matched is None:
            return None
        version, name, floor = matched["version"], matched["map"], matched["floor"]
        cache = self.data_root / "assets" / version / name
        manifest = _read_manifest(cache, version, name)
        if manifest is None:
            return None
        if floor is not None and floor not in {level["name"] for level in manifest["levels"]}:
            return None
        try:
            file = (cache / ("radar.png" if floor is None else f"{floor}.png")).resolve(strict=True)
            root = (self.data_root / "assets").resolve()
        except OSError:
            return None
        return file if file.is_file() and file.is_relative_to(root) else None

    def _extract(
        self, cli: Path, pak: Path, cache: Path, version: str, name: str, demo: str | None
    ) -> dict[str, Any]:
        """Extract overview + radar (+ declared floors) into a fresh cache directory."""
        cache.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        staging = cache.parent / f".{name}.tmp"
        shutil.rmtree(staging, ignore_errors=True)  # leftovers from an interrupted extraction
        raw, publish = staging / "raw", staging / "cache"
        raw.mkdir(parents=True, mode=0o700)
        publish.mkdir()
        notes: list[str] = []
        try:
            overview_bytes = self._bytes(cli, pak, OVERVIEW_ENTRY.format(map=name), raw / "overview")
            overview = _parse_overview(overview_bytes.decode("utf-8", errors="replace"))
            if None in (overview["pos_x"], overview["pos_y"], overview["scale"]) or not overview["scale"]:
                raise AppError("OVERVIEW_INCOMPLETE", f"overview for {name} lacks pos_x/pos_y/scale", "assets")
            radar_bytes = self._bytes(cli, pak, RADAR_ENTRY.format(map=name), raw / "radar", decompile=True)
            size = _png_size(radar_bytes)
            if size is None:
                raise AppError("RADAR_IMAGE_INVALID", f"radar for {name} is not a PNG image", "assets")
            (publish / "overview.txt").write_bytes(overview_bytes)
            (publish / "radar.png").write_bytes(radar_bytes)

            levels: list[dict[str, Any]] = []
            for floor, bounds in overview["floors"]:
                if floor == "default" or not FLOOR_PATTERN.match(floor):
                    continue  # "default" is the plain <map>_radar_psd texture already extracted
                if len(levels) >= MAX_FLOORS:
                    notes.append(f"only the first {MAX_FLOORS} declared altitude sections were extracted")
                    break
                try:
                    data = self._bytes(cli, pak, FLOOR_ENTRY.format(map=name, floor=floor), raw / floor, decompile=True)
                    floor_size = _png_size(data)
                except AppError:
                    notes.append(f"declared altitude section {floor!r} has no radar image in this installation")
                    continue
                if floor_size is None:
                    notes.append(f"declared altitude section {floor!r} did not yield a PNG image")
                    continue
                (publish / f"{floor}.png").write_bytes(data)
                levels.append(
                    {"name": floor, "asset_id": f"radar:{version}:{name}:{floor}", **bounds,
                     "width": floor_size[0], "height": floor_size[1]}
                )

            manifest = {
                "schema": CACHE_SCHEMA, "map_name": name, "client_version": version,
                "demo_client_version": demo, "extracted_at": utc_now(),
                "tool": f"Source2Viewer-CLI {CLI_VERSION}", "pak": str(pak),
                "geometry": {**{key: overview[key] for key in ("pos_x", "pos_y", "scale", "rotate", "zoom")},
                             "width": size[0], "height": size[1]},
                "levels": levels, "notes": notes,
                "files": [{"name": path.name, "size": path.stat().st_size, "sha256": _sha256(path)}
                          for path in sorted(publish.iterdir())],
            }
            (publish / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            if cache.exists():
                shutil.rmtree(cache)
            os.replace(publish, cache)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        stored = _read_manifest(cache, version, name)
        if stored is None:
            raise AppError("CACHE_INVALID", f"published radar cache for {name} failed validation", "assets")
        return stored

    def _bytes(self, cli: Path, pak: Path, entry: str, output: Path, *, decompile: bool = False) -> bytes:
        """Run one CLI extraction and return the file it wrote."""
        output.mkdir(parents=True, exist_ok=True)
        argv = [str(cli), "-i", str(pak), "-f", entry, "-o", str(output)] + (["-d"] if decompile else [])
        try:
            done = subprocess.run(argv, capture_output=True, text=True, timeout=CLI_TIMEOUT, check=False)
        except FileNotFoundError:
            raise AppError("TOOL_MISSING", f"{cli.name} could not be executed", "assets") from None
        except subprocess.TimeoutExpired:
            raise AppError("EXTRACTION_TIMEOUT", f"{cli.name} timed out after {CLI_TIMEOUT:g}s", "assets", True) from None
        except OSError as error:
            raise AppError("TOOL_UNAVAILABLE", f"{cli.name} failed: {error.strerror or error.__class__.__name__}", "assets") from None
        if done.returncode != 0:
            detail = " ".join((done.stderr or done.stdout or "no tool output").split())[-200:]
            raise AppError("EXTRACTION_FAILED", f"{cli.name} exited {done.returncode} for {entry}: {detail}", "assets")
        # The CLI mirrors VPK entry paths below the output directory.
        relative = Path(entry).with_suffix(".png") if decompile else Path(entry)
        produced = output / relative
        if produced.is_file():
            return produced.read_bytes()
        raise AppError("EXTRACTION_FAILED", f"{cli.name} produced no file for {entry}", "assets")


def _read_manifest(cache: Path, version: str, name: str) -> dict[str, Any] | None:
    """Return a validated cache manifest, or ``None`` when the cache is unusable."""
    try:
        manifest = json.loads((cache / "manifest.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema") != CACHE_SCHEMA:
            return None
        if manifest.get("map_name") != name or manifest.get("client_version") != version:
            return None
        geometry, files = manifest["geometry"], manifest["files"]
        width, height = _positive(geometry["width"]), _positive(geometry["height"])
        if not (width and height) or None in (_number(geometry["pos_x"]), _number(geometry["pos_y"])):
            return None
        if not _number(geometry["scale"]):
            return None
        for entry in files:
            if not isinstance(entry, dict) or not isinstance(filename := entry.get("name"), str):
                return None
            path = cache / filename
            if not filename or Path(filename).name != filename or path.is_symlink() or not path.is_file():
                return None
            if path.stat().st_size != entry.get("size") or _sha256(path) != entry.get("sha256"):
                return None
        if not (cache / "overview.txt").is_file() or _png_size((cache / "radar.png").read_bytes()) != (width, height):
            return None
    except (OSError, ValueError, TypeError, KeyError):
        return None
    manifest["levels"] = _levels(manifest, cache, version, name)
    raw_notes = manifest.get("notes")
    manifest["notes"] = [note for note in raw_notes if isinstance(note, str)] if isinstance(raw_notes, list) else []
    return manifest


def _levels(manifest: dict[str, Any], cache: Path, version: str, name: str) -> list[dict[str, Any]]:
    """Cache-owned altitude sections; bounds only where the overview declared them."""
    levels: list[dict[str, Any]] = []
    for level in manifest.get("levels", []):
        floor = level.get("name") if isinstance(level, dict) else None
        if not isinstance(floor, str) or not FLOOR_PATTERN.match(floor):
            continue
        if level.get("asset_id") != f"radar:{version}:{name}:{floor}" or not (cache / f"{floor}.png").is_file():
            continue
        levels.append(
            {"name": floor, "asset_id": level["asset_id"]}
            | {key: value for key, value in (
                ("altitude_min", _number(level.get("altitude_min"))),
                ("altitude_max", _number(level.get("altitude_max"))),
                ("width", _positive(level.get("width")) or None),
                ("height", _positive(level.get("height")) or None),
            ) if value is not None}
        )
    return levels


def _descriptor(
    manifest: dict[str, Any], version: str, name: str, installed: str | None,
    demo: str | None, status: str, notes: list[str],
) -> RadarDescriptor:
    """Build the descriptor from a validated manifest."""
    geometry = manifest["geometry"]
    return RadarDescriptor(
        asset_id=f"radar:{version}:{name}", map_name=name, installed_client_version=installed,
        demo_client_version=demo, match_status=status, width=_positive(geometry["width"]),
        height=_positive(geometry["height"]), pos_x=_number(geometry["pos_x"]),
        pos_y=_number(geometry["pos_y"]), scale=_number(geometry["scale"]),
        rotate=_number(geometry["rotate"]), zoom=_number(geometry["zoom"]),
        levels=[dict(level) for level in manifest["levels"]],
        warning=_warning(*notes, *manifest.get("notes", [])),
    )


def _parse_overview(text: str) -> dict[str, Any]:
    """Declared overview geometry plus declared altitude sections (KV1 via srctools)."""
    try:
        tree = Keyvalues.parse(text, filename="overview.txt", single_line=True)
    except Exception:  # malformed KV1 surfaces as our own error below
        raise AppError("OVERVIEW_UNPARSEABLE", "extracted overview is not valid KeyValues", "assets") from None
    block = next((child for child in tree if isinstance(child, Keyvalues) and child.has_children()), None)
    if block is None:
        raise AppError("OVERVIEW_UNPARSEABLE", "extracted overview has no map block", "assets")
    floors: list[tuple[str, dict[str, float]]] = []
    try:
        sections = block.find_key("verticalsections")
    except (NoKeyError, LeafKeyvalueError):
        sections = None
    for section in sections if isinstance(sections, Keyvalues) and sections.has_children() else ():
        if not isinstance(section, Keyvalues) or not section.has_children():
            continue
        bounds = {field: value for field, value in (
            ("altitude_min", _kv_number(section, "AltitudeMin")),
            ("altitude_max", _kv_number(section, "AltitudeMax")),
        ) if value is not None}
        floors.append(((section.real_name or "").strip().casefold(), bounds))
    values = {key: _kv_number(block, key) for key in ("pos_x", "pos_y", "scale", "rotate", "zoom")}
    return values | {"floors": floors}


def _kv_number(block: Keyvalues, key: str) -> float | None:
    """Finite number from a declared leaf key, ignoring blocks and absent keys."""
    try:
        found = block.find_key(key)
    except (NoKeyError, LeafKeyvalueError):
        return None
    if found.has_children():
        return None
    value = found.value
    return _number(value) if isinstance(value, str) else None


def _client_version(install: Path | None) -> str | None:
    """Installed ``ClientVersion`` from the installation's steam.inf, or ``None``."""
    steam_inf = install / STEAM_INF if install else None
    if steam_inf is None or not steam_inf.is_file():
        return None
    try:
        text = steam_inf.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    matched = CLIENT_VERSION.search(text)
    return matched.group(1) if matched else None


def _version(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text if text.isdigit() and len(text) <= 12 else None


def _number(value: Any) -> float | None:
    """Finite float from a KV string or a JSON number, else ``None``."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _positive(value: Any) -> int:
    number = _number(value)
    return int(number) if number and number > 0 else 0


def _png_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 24 or not data.startswith(PNG_SIGNATURE) or data[12:16] != b"IHDR":
        return None
    width, height = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    return (width, height) if width > 0 and height > 0 else None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _warning(*parts: str) -> str | None:
    """Join distinct warning parts into the descriptor's single warning string."""
    seen: list[str] = []
    for part in parts:
        text = " ".join(str(part).split()) if part else ""
        if text and text not in seen:
            seen.append(text)
    return "; ".join(seen)[:480] or None

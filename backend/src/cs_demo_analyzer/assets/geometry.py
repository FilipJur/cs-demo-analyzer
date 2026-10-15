"""Static map collision and navigation assets (Phase 2 slice C).

The source of truth is the installed game's own compiled geometry, read with the
pinned Source2Viewer-CLI: ``maps/<map>/world_physics.vmdl_c`` (the collision
model — rendered meshes are *not* collision) exported to glTF, plus
``maps/<map>.nav`` (the compiled navigation mesh). Both raw entries are hashed
for provenance before anything is derived from them.

``prepare(map_name)`` is the only method that runs the tool; it parses the
exported collision triangles, builds a uniform-cell index and writes a cache
under ``<data_root>/geometry/<client_version>/<map>/``. Query methods never
extract: without a cache they answer ``unsupported``/``unknown`` with a
``not_prepared`` limitation.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import threading
import time
from array import array
from pathlib import Path
from typing import Any

from ..domain.contracts import AppError, Fingerprint, utc_now
from ..domain.geometry import (
    GeometryAsset,
    GeometryCapabilities,
    GeometryComponent,
    GeometrySource,
    MatchStatus,
    NavigationResult,
    PointLocation,
    SegmentResult,
    Vec3,
)
from . import navmesh
from .geometry_math import AABB, TriangleGrid, TriangleSoup, coerce_vec3, dot, normalize, slab_interval
from .radar import CLI_VERSION, MAP_PATTERN, _client_version

CACHE_SCHEMA = 1
PARSER_VERSION = "geometry-v5"
SOURCE_KINDS = frozenset({"vmap", "nav", "physics", "glb"})
CELL_SIZE = 64.0
CLI_TIMEOUT = 900.0
MAX_LOADED_MAPS = 2
GRID_MAGIC = b"CGD1"
MANIFEST_NAME = "manifest.json"
POSITIONS_NAME = "positions.bin"
INDICES_NAME = "indices.bin"
GRID_NAME = "grid.bin"
NAV_NAME = "nav.bin"
STEAM_INF = "game/csgo/steam.inf"
GENERATED_DIR = "geometry"
PHYSICS_ENTRY = "maps/{map}/world_physics.vmdl_c"
NAV_ENTRY = "maps/{map}.nav"
MAP_VPK = "game/csgo/maps/{map}.vpk"
PAK_RELATIVE = "game/csgo/pak01_dir.vpk"
FLOOR_NORMAL_Z = 0.35

GROUP_PREFIX = "physics_group_"
# Movement-only clip volumes are part of the collision model but are invisible and
# do not stop bullets or sight: they are excluded from sightline segments and kept
# for point/floor queries, where "inside a solid the player cannot occupy" matters.
CLIP_SURFACE_MARKERS = ("playerclip", "npcclip", "grenadeclip", "vehicleclip")
# Collision intersection is not optical occlusion: the exported model has no opacity
# information, and any object state outside it is simply absent.
SIGHTLINE_SEMANTICS = (
    "static_clear and static_blocked describe collision-geometry intersection of the installed build's "
    "world_physics model between the given world-space points; this is collision evidence, not proof that "
    "optical visibility was clear or blocked (surface opacity is unknown and is never inferred from material "
    "names, movement-only clip volumes are excluded, and props/doors or any dynamic object state outside that "
    "model are not represented)"
)


def is_clip_surface(surface: str) -> bool:
    """True for movement-only clip volumes that never block bullets or sight."""
    lowered = surface.lower()
    return any(marker in lowered for marker in CLIP_SURFACE_MARKERS)


class GeometryService:
    """Answer static geometry questions for one installed CS2 build."""

    def __init__(self, data_root: str | Path, install_path: str | Path | None = None, source2viewer: str | Path | None = None):
        self.data_root = Path(data_root)
        self.install_path = Path(install_path) if install_path else None
        self.executable = Path(source2viewer) if source2viewer else None
        if self.install_path is not None and not self.install_path.is_dir():
            raise AppError("INVALID_CONFIG", f"Install path is not a directory: {self.install_path}", "geometry")
        self._lock = threading.Lock()
        self._loaded: dict[tuple[str, str], _MapGeometry] = {}

    # ------------------------------------------------------------------ public API

    def prepare(self, map_name: str) -> GeometryCapabilities:
        """Extract, parse and cache one map's geometry; the explicit preprocessing step."""
        name = _map_name(map_name)
        version, status, notes = self._version_context(None)
        cache = self._cache_dir(name, version)
        manifest = self._read(name, version)
        if manifest is not None:
            return _capabilities(manifest, name, version, status, notes, None)
        missing = self._preconditions()
        if missing is not None:
            return _capabilities(_failed_manifest(name, version, missing), name, version, status, notes, None)
        assert self.install_path is not None  # guaranteed by _preconditions
        with self._lock:
            # A changed or missing source resource invalidates the cache: re-extract and
            # drop any loaded index so no query can keep answering from the old geometry.
            self._loaded.pop((version, name), None)
            manifest = self._read(name, version) or self._extract(name, version, cache)
        return _capabilities(manifest, name, version, status, notes, None)

    def capabilities(self, map_name: str, demo_client_version: str | None = None) -> GeometryCapabilities:
        """Describe cached capability for one map without touching geometry files."""
        name = _map_name(map_name)
        version, status, notes = self._version_context(demo_client_version)
        demo = _version_text(demo_client_version)
        manifest = self._read(name, version)
        if manifest is None:
            return _capabilities(_not_prepared_manifest(name, version), name, version, status, notes, demo)
        return _capabilities(manifest, name, version, status, notes, demo)

    def segment(
        self,
        map_name: str,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        demo_client_version: str | None = None,
    ) -> SegmentResult:
        """Static collision along one world-space segment (installed build)."""
        name = _map_name(map_name)
        origin, target = _segment_points(start, end)
        version, match, notes = self._version_context(demo_client_version)
        length = math.dist(origin, target)
        geometry = self._geometry(name, version)
        if geometry is None:
            return _no_geometry_segment(origin, target, length, self._unsupported_reason(name, version), match, notes)
        if geometry.soup is None:
            return _no_geometry_segment(origin, target, length, geometry.physics_detail, match, notes)
        if length <= 1e-6:
            return SegmentResult(
                status="unknown", start=origin, end=target, length=length,
                asset_id=geometry.asset_id, match_status=match,
                limitations=notes + ["zero-length segment has no direction to test"],
            )
        direction = (target[0] - origin[0], target[1] - origin[1], target[2] - origin[2])
        direction = (direction[0] / length, direction[1] / length, direction[2] / length)
        if _outside_bounds(geometry.soup.bounds, origin, direction, length):
            return SegmentResult(
                status="unknown", start=origin, end=target, length=length,
                asset_id=geometry.asset_id, match_status=match,
                limitations=notes + ["the segment lies outside the mapped collision bounds, so no collision data covers it"],
            )
        hit = geometry.grid.ray_first(origin, direction, length, geometry.sightline_skip)
        if hit is None:
            uncovered = [
                name for name, point in (("start", origin), ("end", target)) if not geometry.soup.bounds.contains(point, 1.0)
            ]
            if uncovered:
                # Part of the segment has no collision coverage: unknown, never clear.
                return SegmentResult(
                    status="unknown", start=origin, end=target, length=length,
                    asset_id=geometry.asset_id, match_status=match,
                    limitations=notes + [
                        f"no intersection was found, but the {' and '.join(uncovered)} point lies outside the mapped "
                        "collision bounds, so the segment is only partly covered by collision data"
                    ] + [SIGHTLINE_SEMANTICS],
                )
            return SegmentResult(
                status="static_clear", start=origin, end=target, length=length,
                asset_id=geometry.asset_id, match_status=match, limitations=notes + [SIGHTLINE_SEMANTICS],
            )
        index, distance = hit
        normal = geometry.normal_at(index)
        return SegmentResult(
            status="static_blocked", start=origin, end=target, length=length,
            hit_distance=distance,
            hit_point=(origin[0] + direction[0] * distance, origin[1] + direction[1] * distance, origin[2] + direction[2] * distance),
            hit_normal=None if normal is None else _towards_origin(normal, direction),
            surface=geometry.surface_of(index),
            source=f"triangle:{index}",
            asset_id=geometry.asset_id, match_status=match,
            limitations=notes + [SIGHTLINE_SEMANTICS, f"the intersection is reported on the '{geometry.surface_of(index)}' collision surface"],
        )

    def locate(self, map_name: str, point: tuple[float, float, float], demo_client_version: str | None = None) -> PointLocation:
        """Static location facts for one world-space point (installed build)."""
        name = _map_name(map_name)
        spot = _point(point)
        version, match, notes = self._version_context(demo_client_version)
        geometry = self._geometry(name, version)
        if geometry is None or geometry.soup is None:
            reason = self._unsupported_reason(name, version) if geometry is None else geometry.physics_detail
            return PointLocation(
                point=spot, in_bounds=None, inside_solid=None, asset_id=None, match_status=match,
                limitations=notes + [reason],
            )
        grid, soup = geometry.grid, geometry.soup
        bounds = soup.bounds
        limits = list(notes)
        in_bounds = bounds.contains(spot, 1.0)
        if not in_bounds:
            limits.append("point lies outside the map's collision bounds")
        down = grid.ray_first(spot, (0.0, 0.0, -1.0), max(1.0, spot[2] - bounds.low[2] + 64.0))
        floor_z = floor_distance = None
        if down is not None:
            index, distance = down
            normal = geometry.normal_at(index)
            if normal is not None and normal[2] >= FLOOR_NORMAL_Z:
                floor_z = spot[2] - distance
                floor_distance = distance
            else:
                limits.append("the nearest surface below the point faces downward (ceiling or solid), so floor height is unknown")
        else:
            limits.append("no surface found below the point within the map bounds")
        up = grid.ray_first(spot, (0.0, 0.0, 1.0), max(1.0, bounds.high[2] - spot[2] + 64.0))
        clearance_up = None if up is None else up[1]
        # Solidity is only meaningful where collision data covers the point.
        inside = _inside_solid(grid, soup, spot, bounds) if in_bounds else None
        if inside is None:
            limits.append("solidity is unknown: the point is outside the mapped collision bounds"
                          if not in_bounds else "collision rays disagree about whether the point is inside a solid")
        nav_area = geometry.nav_area_at(spot)
        return PointLocation(
            point=spot, in_bounds=in_bounds, inside_solid=inside, floor_z=floor_z,
            floor_distance=floor_distance, clearance_up=clearance_up, nav_area_id=nav_area,
            asset_id=geometry.asset_id, match_status=match, limitations=limits,
        )

    def navigation(
        self,
        map_name: str,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        demo_client_version: str | None = None,
    ) -> NavigationResult:
        """Static navigation answer between two world-space points (installed build).

        Endpoints must be recorded player positions (the map-space origin at the
        player's feet), not estimated eye points: a navigation area is matched
        within 24 units of the area's polygon plane, so an eye offset of 64 units
        above the floor falls outside the area and answers ``unavailable``.
        """
        name = _map_name(map_name)
        origin, target = _segment_points(start, end)
        version, match, notes = self._version_context(demo_client_version)
        direct = math.dist(origin, target)
        geometry = self._geometry(name, version)
        if geometry is None or geometry.nav_mesh is None:
            detail = self._unsupported_reason(name, version) if geometry is None else geometry.nav_detail
            return NavigationResult(
                status="unsupported", start=origin, end=target, direct_distance=direct,
                match_status=match, limitations=notes + [detail],
            )
        mesh = geometry.nav_mesh
        start_area = mesh.area_at(origin)
        end_area = mesh.area_at(target)
        if start_area is None or end_area is None:
            missing = []
            if start_area is None:
                missing.append("start")
            if end_area is None:
                missing.append("end")
            return NavigationResult(
                status="unavailable", start=origin, end=target, direct_distance=direct, connected=False,
                asset_id=geometry.asset_id, match_status=match,
                limitations=notes + [f"no navigation area contains the {'/'.join(missing)} point(s)"],
            )
        path = mesh.path(start_area.area_id, end_area.area_id)
        if path is None:
            return NavigationResult(
                status="unavailable", start=origin, end=target, direct_distance=direct, connected=False,
                area_ids=[start_area.area_id, end_area.area_id], asset_id=geometry.asset_id, match_status=match,
                limitations=notes + [
                    "no connection path exists between the start and end navigation areas over the nav mesh's stored "
                    f"connections and ladder transitions ({mesh.ladder_count} ladders in this file)"
                ],
            )
        areas = mesh.by_id()
        points = [origin] + [areas[area_id].center for area_id in path] + [target]
        distance = sum(math.dist(points[index], points[index + 1]) for index in range(len(points) - 1))
        ladder_links = mesh.ladder_links()
        ladder_hops = sum(1 for index in range(len(path) - 1) if path[index + 1] in ladder_links.get(path[index], ()))
        scoped = [
            "path and path_distance are an area-centre graph estimate over the nav mesh's stored area connections "
            "(plus ladder transitions), not an exact traversable route, not a shortest-path guarantee and not a "
            "travel time",
            "stored graph links can encode engine traversal assumptions (jump, drop, ladder); link types this "
            "reader does not model stay unrepresented, so a missing path is scoped to exactly this graph",
            f"graph and ladder inventory: {len(mesh.areas)} areas, {mesh.ladder_count} ladders in this file",
        ]
        if ladder_hops:
            scoped.append(
                f"path uses {ladder_hops} ladder transition(s); ladder climb direction is not modelled "
                "(the stored direction is a cardinal facing)"
            )
        return NavigationResult(
            status="available", start=origin, end=target, direct_distance=direct, path_distance=distance,
            connected=True, path=points, area_ids=path, asset_id=geometry.asset_id, match_status=match,
            limitations=notes + scoped + [f"nav version {mesh.version}, {len(mesh.areas)} areas from the installed build"],
        )

    # ------------------------------------------------------------------ internals

    def _version_context(self, demo_client_version: str | None) -> tuple[str, MatchStatus, list[str]]:
        installed = _client_version(self.install_path)
        demo = _version_text(demo_client_version)
        version = installed or "unknown"
        if not installed or not demo:
            return version, "unknown", []
        if installed == demo:
            return version, "exact", []
        return version, "mismatch", [
            f"geometry is from installed client {installed} but the demo was recorded with {demo}; "
            "it describes the current build, so it cannot prove historical collision or visibility"
        ]

    def _preconditions(self) -> str | None:
        if self.install_path is None:
            return "no CS2 installation path is configured; map geometry is unavailable"
        if not self.install_path.is_dir():
            return f"configured CS2 installation is not a directory: {self.install_path}"
        executable = self.executable if self.executable and self.executable.is_file() else None
        if executable is None:
            return f"Source2Viewer CLI {CLI_VERSION} is not provisioned; cannot extract map geometry"
        return None

    def _cache_dir(self, name: str, version: str) -> Path:
        return self.data_root / GENERATED_DIR / version / name

    def _dependencies(self, name: str) -> list[Path]:
        """The installed VPK files that back one map's geometry (map VPK, or the pak set it falls back to)."""
        assert self.install_path is not None
        map_vpk = self.install_path / MAP_VPK.format(map=name)
        if map_vpk.is_file():
            return [map_vpk]
        pak = self.install_path / PAK_RELATIVE
        chunks = sorted(pak.parent.glob("pak01_*.vpk"))
        return ([pak, *chunks] if pak.is_file() else chunks) if chunks else []

    def _read(self, name: str, version: str) -> dict[str, Any] | None:
        """Read a validated cache manifest, or ``None`` when it may not be trusted."""
        return _read_manifest(self._cache_dir(name, version), name, version, self.install_path)

    def _unsupported_reason(self, name: str, version: str) -> str:
        manifest = self._read(name, version)
        if manifest is None:
            return f"geometry for {name} is not prepared; run prepare('{name}') first"
        return str(manifest.get("physics", {}).get("detail", "map geometry is unavailable"))

    def _geometry(self, name: str, version: str) -> _MapGeometry | None:
        key = (version, name)
        with self._lock:
            cached = self._loaded.get(key)
        if cached is not None:
            # Stat-only dependency check on the hot path: a resource that changed under the
            # same client version must never keep answering from the loaded index.
            if _dependencies_unchanged(cached.dependencies, self.install_path):
                return cached
            with self._lock:
                self._loaded.pop(key, None)
            return None
        cache = self._cache_dir(name, version)
        manifest = self._read(name, version)
        if manifest is None:
            return None
        geometry = _load_map(cache, manifest)
        with self._lock:
            self._loaded[key] = geometry
            while len(self._loaded) > MAX_LOADED_MAPS:
                self._loaded.pop(next(iter(self._loaded)))
        return geometry

    def _extract(self, name: str, version: str, cache: Path) -> dict[str, Any]:
        """Run the pinned CLI, derive the collision index and publish a fresh cache."""
        assert self.install_path is not None and self.executable is not None
        total_start = time.perf_counter()
        timings: dict[str, float] = {}
        cache.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        staging = cache.parent / f".{name}.tmp"
        shutil.rmtree(staging, ignore_errors=True)
        raw, publish = staging / "raw", staging / "cache"
        raw.mkdir(parents=True, mode=0o700)
        publish.mkdir()
        map_vpk = self.install_path / MAP_VPK.format(map=name)
        pak = self.install_path / PAK_RELATIVE
        source = map_vpk if map_vpk.is_file() else pak
        manifest: dict[str, Any] = _failed_manifest(name, version, "")
        manifest["vpk"] = str(source)
        try:
            cli_start = time.perf_counter()
            nav_bytes = self._dump_file(source, NAV_ENTRY.format(map=name), raw / f"{name}.nav")
            physics_file = self._dump_file(source, PHYSICS_ENTRY.format(map=name), raw / "world_physics.vmdl_c")
            glb = self._export_gltf(source, PHYSICS_ENTRY.format(map=name), raw / "gltf")
            timings["cli_ms"] = (time.perf_counter() - cli_start) * 1000
            manifest["dependencies"] = [
                {"path": str(path), "fingerprint": _fingerprint(path)} for path in self._dependencies(name)
            ]
            manifest["sources"] = [
                _source("nav", NAV_ENTRY.format(map=name), nav_bytes),
                _source("physics", PHYSICS_ENTRY.format(map=name), physics_file),
                _source("glb", f"maps/{name}/world_physics_physics.glb", glb),
            ]
            parse_start = time.perf_counter()
            positions, indices, groups, bounds = _parse_glb(glb)
            soup = TriangleSoup.from_points(positions, indices, groups)
            grid = TriangleGrid.build(soup, cell_size=CELL_SIZE)
            timings["parse_ms"] = (time.perf_counter() - parse_start) * 1000
            write_start = time.perf_counter()
            with (publish / POSITIONS_NAME).open("wb") as handle:
                positions.tofile(handle)
            with (publish / INDICES_NAME).open("wb") as handle:
                indices.tofile(handle)
            _write_grid(publish / GRID_NAME, grid)
            shutil.copyfile(nav_bytes, publish / NAV_NAME)
            timings["write_ms"] = (time.perf_counter() - write_start) * 1000
            nav_detail = "parsed"
            nav_areas = 0
            try:
                parsed_nav = navmesh.parse(nav_bytes.read_bytes())
                nav_areas = len(parsed_nav.areas)
                manifest["nav"] = {"status": "available", "detail": f"nav version {parsed_nav.version}, {nav_areas} areas", "areas": nav_areas}
            except navmesh.NavMeshError as error:
                nav_detail = f"nav mesh could not be parsed: {error}"
                manifest["nav"] = {"status": "unsupported", "detail": nav_detail, "areas": 0}
            excluded = [(group, count) for group, count in groups if is_clip_surface(group)]
            manifest["physics"] = {
                "status": "available" if soup.triangle_count else "unsupported",
                "detail": f"{soup.triangle_count} collision triangles from the installed build"
                if soup.triangle_count else "the exported collision model has no triangles",
                "triangle_count": soup.triangle_count,
                "vertex_count": len(positions) // 3,
                "groups": [[group, count] for group, count in groups],
                "cell_size": CELL_SIZE,
                "grid_dims": list(grid.dims),
                "grid_cells": len(grid.cell_counts),
                "overflow_triangles": grid.overflow_count,
                "floor_normal_z": FLOOR_NORMAL_Z,
                "excluded_groups": excluded,
                "excluded_triangles": sum(count for _, count in excluded),
                "excluded_reason": "movement-only clip volumes never block bullets or sight",
                "semantics": SIGHTLINE_SEMANTICS,
                "scope": (
                    f"maps/{name}/world_physics.vmdl_c only: the world's collision brushes (brush-built props, "
                    "movement clip volumes and sky) as exported by Source2Viewer-CLI; standalone entity/prop models "
                    f"(maps/{name}/entities/*.vmdl_c), doors, breakables and other dynamic objects are not merged, "
                    "so a sightline blocked only by one of those would be reported static_clear"
                ),
            }
            manifest["bounds_min"], manifest["bounds_max"] = list(bounds.low), list(bounds.high)
            manifest["asset_id"] = _asset_id(name, version, manifest["sources"])
            manifest["timings_ms"] = timings
            manifest["byteorder"] = sys.byteorder
            manifest["created_at"] = utc_now()
            manifest["tool"] = f"Source2Viewer-CLI {CLI_VERSION}"
            timings["total_ms"] = (time.perf_counter() - total_start) * 1000
            (publish / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            if cache.exists():
                shutil.rmtree(cache)
            os.replace(publish, cache)
        except AppError as error:
            manifest["physics"] = {"status": "unavailable", "detail": error.message, "triangle_count": 0}
            manifest["nav"] = {"status": "unavailable", "detail": error.message, "areas": 0}
            publish.mkdir(exist_ok=True)
            (publish / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            if cache.exists():
                shutil.rmtree(cache)
            os.replace(publish, cache)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        stored = self._read(name, version)
        if stored is None:
            raise AppError("CACHE_INVALID", f"published geometry cache for {name} failed validation", "geometry")
        return stored

    def _dump_file(self, vpk: Path, entry: str, target: Path) -> Path:
        """Extract one VPK entry as raw bytes into ``target`` and return the file.

        The CLI writes the entry to ``target`` itself when the path filter matches
        exactly one file, and mirrors the entry path below ``target`` otherwise.
        """
        target.parent.mkdir(parents=True, exist_ok=True)
        candidates = [target, target / entry]
        if not any(candidate.is_file() for candidate in candidates):
            self._run(["-i", str(vpk), "-f", entry, "-o", str(target)])
        produced = next((candidate for candidate in candidates if candidate.is_file()), None)
        if produced is None and target.is_dir():
            found = sorted((path for path in target.rglob("*") if path.is_file()), key=lambda path: path.stat().st_size, reverse=True)
            produced = found[0] if found else None
        if produced is None:
            raise AppError("EXTRACTION_FAILED", f"no file was produced for {entry}", "geometry")
        return produced

    def _export_gltf(self, vpk: Path, entry: str, output: Path) -> Path:
        """Export the collision model as glTF and return the produced binary glTF."""
        output.mkdir(parents=True, exist_ok=True)
        self._run(["-i", str(vpk), "-f", entry, "-o", str(output), "-d", "--gltf_export_format", "glb"])
        produced = sorted(output.rglob("*.glb"), key=lambda path: path.stat().st_size, reverse=True)
        if not produced or produced[0].stat().st_size == 0:
            raise AppError("EXTRACTION_FAILED", f"no glTF collision export was produced for {entry}", "geometry")
        return produced[0]

    def _run(self, arguments: list[str]) -> None:
        assert self.executable is not None
        argv = [str(self.executable), *arguments]
        try:
            done = subprocess.run(argv, capture_output=True, text=True, timeout=CLI_TIMEOUT, check=False)
        except FileNotFoundError:
            raise AppError("TOOL_MISSING", f"{self.executable.name} could not be executed", "geometry") from None
        except subprocess.TimeoutExpired:
            raise AppError("EXTRACTION_TIMEOUT", f"{self.executable.name} timed out after {CLI_TIMEOUT:g}s", "geometry", True) from None
        except OSError as error:
            raise AppError("TOOL_UNAVAILABLE", f"{self.executable.name} failed: {error.strerror or error.__class__.__name__}", "geometry") from None
        if done.returncode != 0:
            detail = " ".join((done.stderr or done.stdout or "no tool output").split())[-200:]
            raise AppError("EXTRACTION_FAILED", f"{self.executable.name} exited {done.returncode}: {detail}", "geometry")


class _MapGeometry:
    """Parsed cache for one map: collision index plus lazily parsed navigation mesh."""

    __slots__ = (
        "manifest", "soup", "grid", "asset_id", "physics_detail", "nav_detail", "dependencies",
        "_nav_bytes", "_nav_mesh", "_nav_error", "_sightline_skip",
    )

    def __init__(self, manifest: dict[str, Any], soup: TriangleSoup | None, grid: TriangleGrid | None, nav_bytes: bytes | None):
        self.manifest = manifest
        self.soup = soup
        self.grid = grid
        self.asset_id = manifest.get("asset_id")
        self.physics_detail = str(manifest.get("physics", {}).get("detail", "collision geometry is unavailable"))
        self.nav_detail = str(manifest.get("nav", {}).get("detail", "navigation data is unavailable"))
        self.dependencies = manifest.get("dependencies", [])
        self._nav_bytes = nav_bytes
        self._nav_mesh: navmesh.NavMesh | None = None
        self._nav_error: str | None = None
        self._sightline_skip: bytearray | None = None

    @property
    def sightline_skip(self) -> bytearray | None:
        """Per-triangle mask of movement-only clip volumes (sightlines ignore them)."""
        if self._sightline_skip is None and self.soup is not None:
            mask = bytearray(self.soup.triangle_count)
            first = 0
            for name, count in self.soup.groups:
                if is_clip_surface(name):
                    mask[first : first + count] = b"\x01" * count
                first += count
            self._sightline_skip = mask
        return self._sightline_skip

    @property
    def nav_mesh(self) -> navmesh.NavMesh | None:
        if self._nav_mesh is None and self._nav_error is None:
            if self._nav_bytes is None:
                self._nav_error = self.nav_detail
            else:
                try:
                    self._nav_mesh = navmesh.parse(self._nav_bytes)
                except navmesh.NavMeshError as error:
                    self._nav_error = f"nav mesh could not be parsed: {error}"
        return self._nav_mesh

    def nav_area_at(self, point: Vec3) -> int | None:
        mesh = self.nav_mesh
        if mesh is None:
            return None
        area = mesh.area_at(point)
        return None if area is None else area.area_id

    def normal_at(self, index: int) -> Vec3 | None:
        assert self.soup is not None
        return self.soup.normal_at(index)

    def surface_of(self, index: int) -> str | None:
        assert self.soup is not None
        return self.soup.surface_of(index)


# ---------------------------------------------------------------------- parsing


def _parse_glb(path: Path) -> tuple[array, array, list[tuple[str, int]], AABB]:
    """Collision triangles from a binary glTF (welded vertices, surface groups)."""
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise AppError("EXTRACTION_FAILED", f"{path.name} is not a binary glTF file", "geometry")
    _, _, total = struct.unpack_from("<III", data, 0)
    offset = 12
    document: dict[str, Any] | None = None
    binary: bytes | None = None
    while offset + 8 <= len(data):
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8 : offset + 8 + chunk_length]
        offset += 8 + chunk_length
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk)
        elif chunk_type == 0x004E4942:
            binary = chunk
    if document is None or binary is None or document.get("buffers", [{}])[0].get("byteLength", 0) > len(binary):
        raise AppError("EXTRACTION_FAILED", f"{path.name} has no readable glTF JSON/binary chunk", "geometry")
    positions = array("f")
    indices = array("i")
    groups: list[tuple[str, int]] = []
    lookup: dict[bytes, int] = {}
    for mesh in document.get("meshes", []):
        name = str(mesh.get("name", "")).removeprefix(GROUP_PREFIX) or "unknown"
        triangles = 0
        for primitive in mesh.get("primitives", []):
            attribute = _accessor(document, binary, primitive["attributes"]["POSITION"])
            index_data = _accessor(document, binary, primitive["indices"])
            vertex_count = len(attribute) // 3
            remapped = array("i", bytes(4 * vertex_count))
            for vertex in range(vertex_count):
                base = vertex * 3
                key = attribute[base : base + 3].tobytes()
                existing = lookup.get(key)
                if existing is None:
                    existing = len(positions) // 3
                    lookup[key] = existing
                    positions.extend(attribute[base : base + 3])
                remapped[vertex] = existing
            for index in index_data:
                if index >= vertex_count:
                    raise AppError("EXTRACTION_FAILED", f"{path.name} triangle index out of range", "geometry")
                indices.append(remapped[index])
            triangles += len(index_data) // 3
        if triangles:
            groups.append((name, triangles))
    if not indices:
        raise AppError("EXTRACTION_FAILED", f"{path.name} contains no collision triangles", "geometry")
    return positions, indices, groups, TriangleSoup.from_points(positions, indices, groups).bounds


def _accessor(document: dict[str, Any], binary: bytes, index: int) -> array:
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    codes = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
    try:
        code = codes[accessor["componentType"]]
    except KeyError:
        raise AppError("EXTRACTION_FAILED", f"unsupported glTF component type {accessor['componentType']}", "geometry") from None
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[accessor["type"]]
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    count = accessor["count"] * width
    values = array(code)
    values.frombytes(binary[start : start + count * values.itemsize])
    return values


GRID_HEADER = "<4s i 3f 3i f i"  # magic, schema, origin, dims, cell size, overflow count


def _write_grid(path: Path, grid: TriangleGrid) -> None:
    counts = grid.cell_counts
    with path.open("wb") as handle:
        handle.write(struct.pack(GRID_HEADER, GRID_MAGIC, CACHE_SCHEMA, *grid.origin, *grid.dims, grid.cell_size, len(grid.overflow)))
        counts.tofile(handle)
        _grid_offsets(counts).tofile(handle)
        grid.items.tofile(handle)
        grid.overflow.tofile(handle)


def _read_grid(path: Path, manifest: dict[str, Any], soup: TriangleSoup) -> TriangleGrid:
    physics = manifest.get("physics", {})
    cell_count = int(physics.get("grid_cells", 0))
    dims = tuple(int(value) for value in physics.get("grid_dims", (0, 0, 0)))
    with path.open("rb") as handle:
        header = struct.unpack(GRID_HEADER, handle.read(struct.calcsize(GRID_HEADER)))
        if header[0] != GRID_MAGIC or header[1] != CACHE_SCHEMA or (header[5], header[6], header[7]) != dims:
            raise AppError("CACHE_INVALID", f"{path.name} has an unexpected grid header", "geometry")
        counts = array("i")
        counts.fromfile(handle, cell_count)
        offsets = array("i")
        offsets.fromfile(handle, cell_count)
        items = array("i")
        items.fromfile(handle, sum(counts))
        overflow = array("i")
        overflow.fromfile(handle, header[9])
    return TriangleGrid.restore(soup, (header[2], header[3], header[4]), header[8], dims, counts, offsets, items, overflow)


def _grid_offsets(counts: array) -> array:
    offsets = array("i", bytes(4 * len(counts)))
    running = 0
    for cell in range(len(counts)):
        offsets[cell] = running
        running += counts[cell]
    return offsets


def _load_map(cache: Path, manifest: dict[str, Any]) -> _MapGeometry:
    physics = manifest.get("physics", {})
    soup = grid = None
    if physics.get("status") == "available":
        positions = array("f")
        with (cache / POSITIONS_NAME).open("rb") as handle:
            positions.fromfile(handle, int(physics.get("vertex_count", 0)) * 3)
        indices = array("i")
        with (cache / INDICES_NAME).open("rb") as handle:
            indices.fromfile(handle, int(physics.get("triangle_count", 0)) * 3)
        groups = [(str(name), int(count)) for name, count in physics.get("groups", [])]
        soup = TriangleSoup(positions, indices, groups, AABB(tuple(manifest["bounds_min"]), tuple(manifest["bounds_max"])))
        grid = _read_grid(cache / GRID_NAME, manifest, soup)
    nav_bytes = (cache / NAV_NAME).read_bytes() if manifest.get("nav", {}).get("status") == "available" else None
    return _MapGeometry(manifest, soup, grid, nav_bytes)


# ---------------------------------------------------------------------- helpers


def _map_name(map_name: str) -> str:
    name = map_name.strip().casefold() if isinstance(map_name, str) else ""
    if not MAP_PATTERN.match(name):
        raise AppError("INVALID_ARGUMENT", f"unsupported map name {str(map_name).strip()[:64]!r}; expected a resource name like 'de_inferno'", "geometry")
    return name


def _version_text(value: str | None) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text if text.isdigit() and len(text) <= 12 else None


def _point(value: object) -> Vec3:
    point = coerce_vec3(value)
    if point is None:
        raise AppError("INVALID_ARGUMENT", f"world point must be three finite numbers, got {value!r}", "geometry")
    return point


def _segment_points(start: object, end: object) -> tuple[Vec3, Vec3]:
    return _point(start), _point(end)


def _outside_bounds(bounds: AABB, origin: Vec3, direction: Vec3, length: float) -> bool:
    """True when the whole segment misses the map's collision bounds (no data covers it)."""
    inverse = (
        math.inf if direction[0] == 0 else 1.0 / direction[0],
        math.inf if direction[1] == 0 else 1.0 / direction[1],
        math.inf if direction[2] == 0 else 1.0 / direction[2],
    )
    near, far = slab_interval(origin, inverse, bounds.low, bounds.high)
    return far < 0 or near > length or near > far


def _towards_origin(normal: Vec3, direction: Vec3) -> Vec3:
    oriented = normal if dot(normal, direction) <= 0 else (-normal[0], -normal[1], -normal[2])
    return normalize(oriented) or oriented


def _inside_solid(grid: TriangleGrid, soup: TriangleSoup, point: Vec3, bounds: AABB) -> bool | None:
    """Whether the point sits inside a closed collision volume.

    A ray leaving a closed volume crosses an exit face (normal pointing along the
    ray); a ray arriving from outside first crosses an entry face. Six axis rays
    therefore classify the point without stepping through the whole map, which a
    crossing-parity count would require. Disagreeing rays report ``None``.
    """
    span = 64.0 + max(bounds.high[axis] - bounds.low[axis] for axis in range(3))
    exits = entries = 0
    for axis in range(3):
        for sign in (-1.0, 1.0):
            direction = [0.0, 0.0, 0.0]
            direction[axis] = sign
            direction = (direction[0], direction[1], direction[2])
            hit = grid.ray_first(point, direction, span)
            if hit is None:
                continue  # the ray leaves the map without meeting a surface
            normal = soup.normal_at(hit[0])
            if normal is None:
                continue
            if dot(normal, direction) > 0.5:
                exits += 1
            elif dot(normal, direction) < -0.5:
                entries += 1
    if exits and not entries:
        return True
    if entries and not exits:
        return False
    if not exits and not entries:
        return False  # no surface in any direction: outside every solid
    return None  # mixed evidence (thin, open or malformed collision surfaces)


def _source(kind: str, entry: str, path: Path) -> dict[str, Any]:
    """Provenance for one extracted artifact, hashed in chunks (they can be hundreds of MB)."""
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            size += len(chunk)
            digest.update(chunk)
    return {"kind": kind, "entry": entry, "byte_size": size, "sha256": digest.hexdigest()}


def _asset_id(name: str, version: str, sources: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for source in sources:
        digest.update(f"{source['kind']}:{source['entry']}:{source['sha256']}".encode())
    return f"geometry:{version}:{name}:{digest.hexdigest()[:16]}"


def _base_manifest(name: str, version: str) -> dict[str, Any]:
    return {
        "schema": CACHE_SCHEMA,
        "map_name": name,
        "client_version": version,
        "parser_version": PARSER_VERSION,
        "created_at": utc_now(),
        "tool": f"Source2Viewer-CLI {CLI_VERSION}",
        "vpk": None,
        "asset_id": None,
        "sources": [],
        "dependencies": [],
        "bounds_min": None,
        "bounds_max": None,
        "physics": {"status": "unavailable", "detail": "", "triangle_count": 0},
        "nav": {"status": "unavailable", "detail": "", "areas": 0},
        "timings_ms": {},
        "byteorder": sys.byteorder,
    }


def _failed_manifest(name: str, version: str, detail: str) -> dict[str, Any]:
    manifest = _base_manifest(name, version)
    manifest["physics"] = {"status": "unavailable", "detail": detail, "triangle_count": 0}
    manifest["nav"] = {"status": "unavailable", "detail": detail, "areas": 0}
    return manifest


def _not_prepared_manifest(name: str, version: str) -> dict[str, Any]:
    return _failed_manifest(name, version, f"geometry for {name} is not prepared; run prepare('{name}') first")


def _fingerprint(path: Path) -> dict[str, int]:
    """Stat-only fingerprint of an installed resource (never rehashes the VPK)."""
    return Fingerprint.from_path(path).model_dump()


def _dependencies_unchanged(dependencies: object, install_path: Path | None) -> bool:
    """True only when every recorded dependency still exists with the same stat identity."""
    if install_path is None or not isinstance(dependencies, list) or not dependencies:
        return False  # unverifiable provenance is not trusted
    for dependency in dependencies:
        if not isinstance(dependency, dict) or not isinstance(dependency.get("fingerprint"), dict):
            return False
        try:
            current = Fingerprint.from_path(Path(str(dependency.get("path", ""))))
        except OSError:
            return False  # removed or replaced: the derived geometry is stale
        if current.model_dump() != dependency["fingerprint"]:
            return False
    return True


def _read_manifest(cache: Path, name: str, version: str, install_path: Path | None) -> dict[str, Any] | None:
    try:
        manifest = json.loads((cache / MANIFEST_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(manifest, dict):
        return None
    if manifest.get("schema") != CACHE_SCHEMA or manifest.get("map_name") != name or manifest.get("client_version") != version:
        return None
    if manifest.get("parser_version") != PARSER_VERSION or manifest.get("byteorder") != sys.byteorder:
        return None
    physics, nav = manifest.get("physics"), manifest.get("nav")
    if not isinstance(physics, dict) or not isinstance(nav, dict):
        return None
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        return None
    available = physics.get("status") == "available" or nav.get("status") == "available"
    if available and not _dependencies_unchanged(manifest.get("dependencies"), install_path):
        return None  # usable geometry whose source resources changed or vanished is stale
    for source in sources:
        # A cache written by an older parser (or a hand-edited manifest) is not
        # trusted: its provenance cannot be validated, so it is re-extracted.
        if not isinstance(source, dict) or source.get("kind") not in SOURCE_KINDS:
            return None
        if not isinstance(source.get("entry"), str) or not isinstance(source.get("sha256"), str):
            return None
        if not isinstance(source.get("byte_size"), int) or source["byte_size"] <= 0:
            return None
    if physics.get("status") == "available":
        if not (int(physics.get("triangle_count", 0)) > 0 and int(physics.get("vertex_count", 0)) > 0):
            return None
        if not ((cache / POSITIONS_NAME).is_file() and (cache / INDICES_NAME).is_file() and (cache / GRID_NAME).is_file()):
            return None
    return manifest


def _component(entry: dict[str, Any], source: str) -> GeometryComponent:
    status = entry.get("status", "unavailable")
    if status not in ("available", "partial", "unavailable", "unsupported"):
        status = "unavailable"
    detail = str(entry.get("detail", "")).strip()
    return GeometryComponent(status=status, source=source, limitations=[detail] if detail else [])


def _asset(manifest: dict[str, Any]) -> GeometryAsset | None:
    asset_id = manifest.get("asset_id")
    if not asset_id:
        return None
    return GeometryAsset(
        asset_id=str(asset_id),
        map_name=str(manifest["map_name"]),
        vpk=str(manifest.get("vpk") or ""),
        client_version=str(manifest["client_version"]),
        parser_version=str(manifest["parser_version"]),
        tool=str(manifest["tool"]),
        sources=[GeometrySource(kind=source["kind"], entry=source["entry"], byte_size=int(source["byte_size"]), sha256=source["sha256"]) for source in manifest.get("sources", [])],
    )


def _capabilities(
    manifest: dict[str, Any], name: str, version: str, match: MatchStatus, notes: list[str], demo_client_version: str | None
) -> GeometryCapabilities:
    physics, nav = manifest["physics"], manifest["nav"]
    bounds_min = tuple(manifest["bounds_min"]) if manifest.get("bounds_min") else None
    bounds_max = tuple(manifest["bounds_max"]) if manifest.get("bounds_max") else None
    limitations = list(notes)
    if physics.get("status") != "available":
        limitations.append(str(physics.get("detail", "")))
    if nav.get("status") != "available":
        limitations.append(str(nav.get("detail", "")))
    distinct: list[str] = []
    for note in limitations:
        if note and note not in distinct:
            distinct.append(note)
    groups = len(physics.get("groups", []))
    excluded = int(physics.get("excluded_triangles", 0))
    if excluded:
        distinct.append(
            f"{excluded} collision triangles of movement-only clip volumes are excluded from sightline results "
            "(invisible, bullet- and sight-transparent); they are still used for point and floor queries"
        )
    if physics.get("status") == "available" and physics.get("scope"):
        distinct.append(str(physics["scope"]))
        distinct.append(SIGHTLINE_SEMANTICS)
    prepared = physics.get("status") == "available" or nav.get("status") == "available"
    return GeometryCapabilities(
        map_name=name,
        prepared=prepared,
        physics=_component(physics, f"installed collision model ({groups} surface groups)" if groups else "installed collision model"),
        navigation=_component(nav, "installed nav mesh"),
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        triangle_count=int(physics.get("triangle_count", 0)),
        nav_area_count=int(nav.get("areas", 0)),
        asset=_asset(manifest),
        asset_id=manifest.get("asset_id"),
        match_status=match,
        install_client_version=None if version == "unknown" else version,
        demo_client_version=demo_client_version,
        preprocessing_ms=_number(manifest.get("timings_ms", {}).get("total_ms")),
        limitations=distinct,
    )


def _no_geometry_segment(origin: Vec3, target: Vec3, length: float, reason: str, match: MatchStatus, notes: list[str]) -> SegmentResult:
    return SegmentResult(
        status="unsupported", start=origin, end=target, length=length, match_status=match, limitations=notes + [reason],
    )


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None

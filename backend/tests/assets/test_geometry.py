"""Consumer-visible behaviour of the static map geometry slice.

Runs against a fake Source2Viewer-CLI, a fake installation and a synthetic
binary glTF collision export in ``tmp_path``: no CS2 install, no network and no
Valve asset is needed. The fixture geometry is chosen so every expectation can
be hand-computed (a floor at z = 0 and a wall plane at x = 8).
"""

from __future__ import annotations

import json
import os
import struct
import sys
from pathlib import Path

import pytest

from cs_demo_analyzer.assets.geometry import GeometryService
from cs_demo_analyzer.domain.contracts import AppError

from test_navmesh import FAR, SQUARE, nav_file, sample_areas  # sibling test module (tests/assets has no package)

FLOOR = [
    ((-64.0, -64.0, 0.0), (64.0, -64.0, 0.0), (64.0, 64.0, 0.0)),
    ((-64.0, -64.0, 0.0), (64.0, 64.0, 0.0), (-64.0, 64.0, 0.0)),
]
WALL = [
    ((8.0, -64.0, 0.0), (8.0, -64.0, 64.0), (8.0, 64.0, 64.0)),
    ((8.0, -64.0, 0.0), (8.0, 64.0, 64.0), (8.0, 64.0, 0.0)),
]
def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> list[tuple[tuple[float, float, float], ...]]:
    """Closed axis-aligned box with outward-facing winding (a real solid, unlike a lone plane)."""
    quads = [
        ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)),
        ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)),
        ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)),
        ((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)),
        ((x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)),
        ((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)),
    ]
    center = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    triangles = []
    for quad in quads:
        for triangle in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])):
            a, b, c = triangle
            edge1 = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
            edge2 = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
            normal = (edge1[1] * edge2[2] - edge1[2] * edge2[1],
                      edge1[2] * edge2[0] - edge1[0] * edge2[2],
                      edge1[0] * edge2[1] - edge1[1] * edge2[0])
            middle = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3)
            outward = tuple(middle[axis] - center[axis] for axis in range(3))
            if sum(normal[axis] * outward[axis] for axis in range(3)) < 0:
                triangle = (a, c, b)
            triangles.append(triangle)
    return triangles


# Movement-only clip volume (as Counter-Strike maps ship): invisible to bullets and
# sight, but still solid for a player position inside it.
CLIP = box(-14.0, -6.0, -16.0, 16.0, 8.0, 56.0)  # clear of the floor plane, so it has an interior
CLIP_SURFACE = "physics_npcclip_playerclip_concrete"

TOOL = '''#!{python}
import os, sys

args = sys.argv[1:]
flags = {}
index = 0
while index < len(args):
    if args[index] in ("-i", "-f", "-o") and index + 1 < len(args):
        flags[args[index]] = args[index + 1]
        index += 2
    else:
        index += 1
entry, output = flags.get("-f", ""), flags.get("-o", "")
root = os.environ["FAKE_TOOL_ROOT"]
if os.environ.get("FAKE_TOOL_LOG"):
    with open(os.environ["FAKE_TOOL_LOG"], "a") as handle:
        handle.write(entry + (" -d" if "-d" in args else "") + "\\n")
if os.environ.get("FAKE_TOOL_FAIL"):
    sys.stderr.write("simulated extraction failure\\n")
    raise SystemExit(3)
if "-d" in args and "--gltf_export_format" in args:
    name = entry.split("/")[1]
    source = os.path.join(root, "gltf", name + ".glb")
    if not os.path.isfile(source):
        sys.stderr.write("no collision export for " + entry + "\\n")
        raise SystemExit(1)
    target = os.path.join(output, "maps", name, "world_physics_physics.glb")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(source, "rb") as handle:
        payload = handle.read()
    with open(target, "wb") as handle:
        handle.write(payload)
    with open(os.path.join(output, "maps", name, "world_physics.glb"), "wb") as handle:
        handle.write(b"")
else:
    source = os.path.join(root, "raw", os.path.basename(entry))
    if not os.path.isfile(source):
        sys.stderr.write("not found in pak: " + entry + "\\n")
        raise SystemExit(1)
    parent = os.path.dirname(output)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(source, "rb") as handle:
        payload = handle.read()
    with open(output, "wb") as handle:
        handle.write(payload)
'''


def glb(meshes: list[tuple[str, list[tuple[tuple[float, float, float], ...]]]]) -> bytes:
    """Binary glTF with one unindexed primitive per named mesh (as VRF writes them)."""
    bin_parts: list[bytes] = []
    views: list[dict] = []
    accessors: list[dict] = []
    document_meshes = []
    for name, triangles in meshes:
        positions: list[float] = []
        indices: list[int] = []
        for triangle in triangles:
            base = len(positions) // 3
            for vertex in triangle:
                positions.extend(vertex)
            indices.extend((base, base + 1, base + 2))
        for payload, code, kind, count in (
            (struct.pack(f"<{len(positions)}f", *positions), 5126, "VEC3", len(positions) // 3),
            (struct.pack(f"<{len(indices)}I", *indices), 5125, "SCALAR", len(indices)),
        ):
            while len(payload) % 4:
                payload += b"\x00"
            views.append({"buffer": 0, "byteOffset": sum(len(part) for part in bin_parts), "byteLength": len(payload)})
            accessors.append({"bufferView": len(views) - 1, "componentType": code, "count": count, "type": kind})
            bin_parts.append(payload)
        document_meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": len(accessors) - 2}, "indices": len(accessors) - 1}]})
    binary = b"".join(bin_parts)
    document = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(document_meshes)))}],
        "nodes": [{"mesh": index, "name": mesh["name"]} for index, mesh in enumerate(document_meshes)],
        "meshes": document_meshes,
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": views,
        "accessors": accessors,
    }
    json_chunk = json.dumps(document).encode()
    while len(json_chunk) % 4:
        json_chunk += b" "
    while len(binary) % 4:
        binary += b"\x00"
    body = struct.pack("<II", len(json_chunk), 0x4E4F534A) + json_chunk + struct.pack("<II", len(binary), 0x004E4942) + binary
    return b"glTF" + struct.pack("<II", 2, 12 + len(body)) + body


class Fake:
    """Fake installation, CLI and payload tree for one test."""

    def __init__(self, tmp_path: Path) -> None:
        self.data_root = tmp_path / "app"
        self.install = tmp_path / "install"
        game = self.install / "game" / "csgo"
        (game / "maps").mkdir(parents=True)
        (game / "steam.inf").write_text("ClientVersion=2000932\nPatchVersion=1.1.0.0\n", encoding="utf-8")
        (game / "pak01_dir.vpk").write_bytes(b"fake vpk payload")
        (game / "maps" / "de_inferno.vpk").write_bytes(b"fake map vpk payload")
        self.payloads = tmp_path / "payloads"
        (self.payloads / "raw").mkdir(parents=True)
        (self.payloads / "gltf").mkdir(parents=True)
        self.log = tmp_path / "tool.log"
        self.tool = tmp_path / "Source2Viewer-CLI"
        self.tool.write_text(TOOL.replace("{python}", sys.executable), encoding="utf-8")
        self.tool.chmod(0o755)
        self.raw("world_physics.vmdl_c", b"fake compiled collision model")
        self.nav = nav_file(sample_areas())
        self.raw("de_inferno.nav", self.nav)
        self.collision((("physics_group_concrete", FLOOR + WALL), (f"physics_group_{CLIP_SURFACE}", CLIP)))

    def raw(self, name: str, payload: bytes) -> None:
        (self.payloads / "raw" / name).write_bytes(payload)

    def collision(self, meshes: list[tuple[str, list[tuple[tuple[float, float, float], ...]]]]) -> None:
        (self.payloads / "gltf" / "de_inferno.glb").write_bytes(glb(meshes))

    def service(self, **overrides) -> GeometryService:
        settings = {"install_path": self.install, "source2viewer": self.tool}
        settings.update(overrides)
        return GeometryService(self.data_root, **settings)

    def calls(self) -> list[str]:
        return self.log.read_text(encoding="utf-8").split("\n") if self.log.is_file() else []

    def cache(self, version: str = "2000932", map_name: str = "de_inferno") -> Path:
        return self.data_root / "geometry" / version / map_name


@pytest.fixture
def fake(tmp_path, monkeypatch) -> Fake:
    built = Fake(tmp_path)
    monkeypatch.setenv("FAKE_TOOL_ROOT", str(built.payloads))
    monkeypatch.setenv("FAKE_TOOL_LOG", str(built.log))
    monkeypatch.delenv("FAKE_TOOL_FAIL", raising=False)
    return built


def prepared(fake: Fake, **overrides) -> GeometryService:
    service = fake.service(**overrides)
    capabilities = service.prepare("de_inferno")
    assert capabilities.physics.status == "available", capabilities.limitations
    return service


def test_prepare_builds_hashed_cache_and_answers_collision_queries(fake: Fake) -> None:
    service = fake.service()
    capabilities = service.prepare("de_inferno")

    assert capabilities.prepared and capabilities.match_status == "unknown"  # no demo version supplied
    assert capabilities.physics.status == "available" and capabilities.navigation.status == "available"
    assert capabilities.triangle_count == len(FLOOR) + len(WALL) + len(CLIP)
    assert capabilities.nav_area_count == len(sample_areas())
    assert capabilities.bounds_min == (-64.0, -64.0, 0.0) and capabilities.bounds_max == (64.0, 64.0, 64.0)
    assert capabilities.asset is not None and capabilities.asset_id == capabilities.asset.asset_id
    kinds = {source.kind for source in capabilities.asset.sources}
    assert kinds == {"nav", "physics", "glb"}
    assert all(len(source.sha256) == 64 and source.byte_size > 0 for source in capabilities.asset.sources)
    assert {path.name for path in fake.cache().iterdir()} == {"manifest.json", "grid.bin", "indices.bin", "nav.bin", "positions.bin"}
    assert capabilities.preprocessing_ms is not None

    calls_after_prepare = len(fake.calls())
    again = service.prepare("de_inferno")
    assert again.asset_id == capabilities.asset_id and len(fake.calls()) == calls_after_prepare  # cache hit, no CLI

    # Straight down onto the floor from above: blocked exactly at the floor.
    down = service.segment("de_inferno", (0.0, 0.0, 64.0), (0.0, 0.0, 0.0))
    assert down.status == "static_blocked"
    assert down.hit_distance == pytest.approx(64.0) and down.hit_point == (0.0, 0.0, 0.0)
    assert down.hit_normal == (0.0, 0.0, 1.0)  # oriented back towards the start point
    assert down.surface == "concrete" and down.source.startswith("triangle:")

    # Through the wall plane at x = 8: blocked 24 units along a 32-unit segment.
    through = service.segment("de_inferno", (-16.0, 0.0, 32.0), (16.0, 0.0, 32.0))
    assert through.status == "static_blocked"
    assert through.hit_distance == pytest.approx(24.0) and through.hit_point[0] == pytest.approx(8.0)

    # Short of the wall, and a segment that stops before the floor: clear.
    assert service.segment("de_inferno", (-16.0, 0.0, 32.0), (-4.0, 0.0, 32.0)).status == "static_clear"
    assert service.segment("de_inferno", (0.0, 0.0, 64.0), (0.0, 0.0, 16.0)).status == "static_clear"

    # The clip volume at x = -8 is traversed by this segment, but movement-only clip
    # volumes never block a bullet or a sightline, so the answer stays clear while the
    # exclusion is stated in capabilities and in the asset scope.
    assert service.segment("de_inferno", (-16.0, 0.0, 32.0), (-1.0, 0.0, 32.0)).status == "static_clear"
    assert any("clip volumes" in note for note in capabilities.limitations)
    inside_clip = service.locate("de_inferno", (-10.0, 0.0, 32.0))
    assert inside_clip.inside_solid is True  # still solid for a point inside the volume

    located = service.locate("de_inferno", (0.0, 0.0, 10.0))
    assert (located.in_bounds, located.inside_solid) == (True, False)
    assert located.floor_z == 0.0 and located.floor_distance == pytest.approx(10.0)
    assert located.nav_area_id == 1  # inside the first synthetic nav polygon

    # Partial coverage: a segment entering the map from outside with no intersection is
    # unknown, not clear (the uncovered part has no collision data).
    partial = service.segment("de_inferno", (0.0, 200.0, 32.0), (0.0, 0.0, 32.0))
    assert partial.status == "unknown" and partial.hit_distance is None
    assert any("only partly covered by collision data" in note for note in partial.limitations)
    assert any("start point lies outside" in note for note in partial.limitations)

    # A real intersection outranks partial coverage: a hit from outside stays blocked.
    crossing = service.segment("de_inferno", (200.0, 0.0, 32.0), (-16.0, 0.0, 32.0))
    assert crossing.status == "static_blocked" and crossing.hit_distance is not None
    assert crossing.hit_point[0] == pytest.approx(8.0)

    # Below the mapped bounds nothing is known: no bounds claim, no floor, no solidity fact.
    buried = service.locate("de_inferno", (0.0, 0.0, -10.0))
    assert buried.in_bounds is False and buried.floor_z is None and buried.inside_solid is None
    assert any("outside the mapped collision bounds" in note for note in buried.limitations)
    outside_location = service.locate("de_inferno", (4096.0, 0.0, 0.0))
    assert outside_location.in_bounds is False
    assert outside_location.inside_solid is None  # unknown where no collision data covers the point
    assert any("outside the mapped collision bounds" in note for note in outside_location.limitations)


def test_navigation_traverses_connected_areas_and_qualifies_gaps(fake: Fake) -> None:
    service = prepared(fake)

    linked = service.navigation("de_inferno", (10.0, 10.0, 0.0), (120.0, 10.0, 0.0))
    assert linked.status == "available" and linked.connected is True
    assert linked.area_ids == [1, 2] and linked.path[0] == (10.0, 10.0, 0.0) and linked.path[-1] == (120.0, 10.0, 0.0)
    assert linked.path_distance is not None and linked.path_distance >= linked.direct_distance

    # Area 3 exists but is not connected to area 1.
    isolated = service.navigation("de_inferno", (10.0, 10.0, 0.0), (510.0, 510.0, 4.0))
    assert isolated.status == "unavailable" and isolated.connected is False and isolated.limitations

    off_mesh = service.navigation("de_inferno", (-2000.0, -2000.0, 0.0), (10.0, 10.0, 0.0))
    assert off_mesh.status == "unavailable" and any("no navigation area" in note for note in off_mesh.limitations)

    # A segment outside the mapped collision bounds has no data: unknown, never clear.
    outside = service.segment("de_inferno", (-2000.0, -2000.0, 0.0), (-1900.0, -2000.0, 0.0))
    assert outside.status == "unknown" and outside.limitations

    # Unprepared maps answer unknown/unsupported with explicit absence, never facts.
    # A separate data root keeps this service genuinely uncached.
    unprepared = GeometryService(fake.data_root.parent / "no-cache", fake.install, fake.tool)
    missing = unprepared.segment("de_inferno", (0.0, 0.0, 0.0), (10.0, 0.0, 0.0))
    assert missing.status == "unsupported" and missing.match_status == "unknown" and missing.limitations
    assert unprepared.navigation("de_inferno", (0.0, 0.0, 0.0), (10.0, 0.0, 0.0)).status == "unsupported"
    absent_capabilities = unprepared.capabilities("de_inferno")
    assert absent_capabilities.prepared is False and absent_capabilities.physics.status == "unavailable"
    absent_location = unprepared.locate("de_inferno", (0.0, 0.0, 0.0))
    assert (absent_location.in_bounds, absent_location.inside_solid) == (None, None)
    assert absent_capabilities.bounds_min is None and absent_capabilities.bounds_max is None


def test_mismatched_client_version_and_invalid_arguments_are_explicit(fake: Fake) -> None:
    service = prepared(fake, )
    exact = service.segment("de_inferno", (0.0, 0.0, 64.0), (0.0, 0.0, 0.0), "2000932")
    mismatch = service.segment("de_inferno", (0.0, 0.0, 64.0), (0.0, 0.0, 0.0), "1999999")

    assert exact.match_status == "exact"
    assert any("collision evidence" in note for note in exact.limitations)  # never claims optical visibility
    assert not any("recorded with" in note for note in exact.limitations)  # no mismatch note on an exact match
    assert mismatch.match_status == "mismatch" and mismatch.status == "static_blocked"
    assert any("cannot prove historical" in note for note in mismatch.limitations)
    assert service.capabilities("de_inferno", "1999999").match_status == "mismatch"

    for bad_point in ((0.0, 0.0), (0.0, float("nan"), 0.0), "origin"):
        with pytest.raises(AppError) as error:
            service.segment("de_inferno", bad_point, (0.0, 0.0, 0.0))
        assert error.value.code == "INVALID_ARGUMENT"
    with pytest.raises(AppError) as error:
        service.capabilities("../etc/passwd")
    assert error.value.code == "INVALID_ARGUMENT"


def test_capabilities_echo_the_requested_demo_version(fake: Fake) -> None:
    service = prepared(fake)
    exact = service.capabilities("de_inferno", "2000932")
    mismatch = service.capabilities("de_inferno", "2000930")

    assert (exact.demo_client_version, exact.install_client_version, exact.match_status) == ("2000932", "2000932", "exact")
    assert (mismatch.demo_client_version, mismatch.install_client_version, mismatch.match_status) == ("2000930", "2000932", "mismatch")
    assert service.capabilities("de_inferno").demo_client_version is None


def test_ladder_only_connection_is_used_and_reported(fake: Fake) -> None:
    # Replace the nav file with one whose only link between area 1 and area 3 is a ladder.
    body = {"id": 3, "top": (500.0, 500.0, 128.0), "bottom": (0.0, 0.0, 0.0), "direction": 1}
    fake.raw("de_inferno.nav", nav_file([
        {"id": 1, "polygon": SQUARE, "connections": [[], [], [], []]},
        {"id": 3, "polygon": FAR, "connections": [[], [], [], []]},
    ], ladders=({**body, "top_areas": (3,), "bottom_areas": (1,)},)))
    service = prepared(fake)

    result = service.navigation("de_inferno", (10.0, 10.0, 0.0), (510.0, 510.0, 4.0))
    assert result.status == "available" and result.area_ids == [1, 3]
    assert any("ladder transition(s)" in note for note in result.limitations)
    assert any("ladder climb direction is not modelled" in note for note in result.limitations)

    disconnected = service.navigation("de_inferno", (-2000.0, -2000.0, 0.0), (10.0, 10.0, 0.0))
    assert disconnected.status == "unavailable" and disconnected.connected is False


def test_missing_or_corrupt_nav_degrades_without_losing_collision(fake: Fake) -> None:
    fake.raw("de_inferno.nav", b"not a nav file at all")
    service = prepared(fake)
    capabilities = service.capabilities("de_inferno")

    assert capabilities.physics.status == "available" and capabilities.navigation.status == "unsupported"
    assert capabilities.nav_area_count == 0
    assert any("nav" in note for note in capabilities.limitations)
    assert service.segment("de_inferno", (0.0, 0.0, 64.0), (0.0, 0.0, 0.0)).status == "static_blocked"
    unsupported = service.navigation("de_inferno", (10.0, 10.0, 0.0), (120.0, 10.0, 0.0))
    assert unsupported.status == "unsupported" and unsupported.connected is None


def test_extraction_failure_is_recorded_as_typed_capability(fake: Fake, monkeypatch) -> None:
    monkeypatch.setenv("FAKE_TOOL_FAIL", "1")
    capabilities = fake.service().prepare("de_inferno")

    assert capabilities.prepared is False and capabilities.physics.status == "unavailable"
    assert capabilities.navigation.status == "unavailable"
    assert any("simulated extraction failure" in note for note in capabilities.limitations)
    assert fake.service().segment("de_inferno", (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)).status == "unsupported"


def test_unprovisioned_tool_reports_absence(fake: Fake, tmp_path) -> None:
    service = GeometryService(fake.data_root, fake.install, tmp_path / "absent-Source2Viewer-CLI")
    capabilities = service.prepare("de_inferno")

    assert capabilities.physics.status == "unavailable"
    assert any("Source2Viewer" in note for note in capabilities.limitations)
    with pytest.raises(AppError) as error:
        GeometryService(fake.data_root, tmp_path / "not-a-directory" / "install", None)
    assert error.value.code == "INVALID_CONFIG"


REAL_INSTALL = os.environ.get("CSDA_TEST_INSTALL")
REAL_TOOL = os.environ.get("CSDA_TEST_S2V")


@pytest.mark.skipif(not REAL_INSTALL, reason="set CSDA_TEST_INSTALL (and CSDA_TEST_S2V) for real-map geometry checks")
def test_real_install_inferno_geometry_matches_recorded_demo_positions(tmp_path) -> None:
    """Real-install check, grounded in recorded demo data (generation 23cd7e44…, tick 65, client 2000930).

    Coordinates below are recorded round-start player origins and nav-area corners of the local
    de_inferno build (installed client 2000932); the blocked pair are two nav areas whose stored
    graph walk is more than three times their direct distance, i.e. actual separating geometry.
    """
    service = GeometryService(tmp_path, REAL_INSTALL, REAL_TOOL)
    capabilities = service.prepare("de_inferno")

    assert capabilities.physics.status == "available" and capabilities.navigation.status == "available"
    assert capabilities.triangle_count > 1_000_000 and capabilities.nav_area_count > 1000
    assert capabilities.asset is not None and capabilities.asset.client_version == "2000932"

    for spawn in ((2493.0, 2090.0, 132.65), (-1586.5, 440.8, -63.87)):
        location = service.locate("de_inferno", (spawn[0], spawn[1], spawn[2] + 2.0))
        assert location.in_bounds is True and location.inside_solid is False
        assert location.floor_z is not None and abs(location.floor_z - spawn[2]) < 2.0
        assert location.nav_area_id is not None

    # clear: two corners of one convex navigation area (areas 1853)
    assert service.segment("de_inferno", (600.5, 2528.5, 244.0), (581.0, 2536.0, 244.0)).status == "static_clear"

    # blocked: separating geometry between nav areas 94 and 146 (direct 490 units, graph walk 3196 units)
    blocked = service.segment("de_inferno", (-28.0, 219.0, 265.3), (400.2, 19.7, 134.0))
    assert blocked.status == "static_blocked"
    assert blocked.hit_distance is not None and blocked.hit_distance < 490.0
    assert blocked.surface is not None and blocked.source is not None and blocked.source.startswith("triangle:")
    assert blocked.hit_normal is not None

    # elevation: the recorded T-spawn origin sits under a ceiling within a few hundred units
    overhead = service.segment("de_inferno", (-1586.5, 440.8, 0.1), (-1586.5, 440.8, 4096.0))
    assert overhead.status == "static_blocked" and overhead.hit_distance is not None and overhead.hit_distance < 1000.0

    # boundary: outside the mapped collision bounds is unknown, never clear
    outside = service.segment("de_inferno", (4480.0, 0.0, 0.0), (4736.0, 0.0, 0.0))
    assert outside.status == "unknown" and outside.limitations
    assert service.locate("de_inferno", (4480.0, 0.0, 0.0)).in_bounds is False

    # navigation between two recorded spawns follows the nav graph
    route = service.navigation("de_inferno", (-1586.5, 440.8, -63.87), (2292.1, 2027.7, 136.06))
    assert route.status == "available" and route.connected is True
    assert route.path_distance is not None and route.path_distance > route.direct_distance
    assert any("area-centre graph estimate" in note for note in route.limitations)

    # the demo build differs from the installed one: results are scoped and never claim history
    scoped = service.segment("de_inferno", (0.0, 0.0, 64.0), (0.0, 0.0, 0.0), "2000930")
    assert scoped.status in {"static_clear", "static_blocked"} and scoped.match_status == "mismatch"
    assert any("cannot prove historical" in note for note in scoped.limitations)


def test_changed_source_under_same_client_version_is_never_silently_stale(fake: Fake) -> None:
    """A changed installed VPK must not leave stale geometry answers behind."""
    service = fake.service()
    first = service.prepare("de_inferno")
    assert first.physics.status == "available" and first.asset is not None
    assert service.segment("de_inferno", (-16.0, 0.0, 32.0), (16.0, 0.0, 32.0)).status == "static_blocked"
    loaded = service._loaded[("2000932", "de_inferno")]  # the index a query path would reuse

    # The installed map VPK changes while the client version stays the same.
    (fake.install / "game" / "csgo" / "maps" / "de_inferno.vpk").write_bytes(b"replaced map vpk payload")

    assert service.capabilities("de_inferno").prepared is False
    stale = service.segment("de_inferno", (-16.0, 0.0, 32.0), (16.0, 0.0, 32.0))
    assert stale.status == "unsupported" and stale.limitations  # never the old static_blocked
    assert service.locate("de_inferno", (0.0, 0.0, 10.0)).in_bounds is None
    assert service.navigation("de_inferno", (10.0, 10.0, 0.0), (120.0, 10.0, 0.0)).status == "unsupported"
    assert ("2000932", "de_inferno") not in service._loaded  # the loaded index was dropped
    assert loaded is not None

    # The new source moved the wall from x = 8 to x = 32: an explicit prepare re-extracts the
    # replacement geometry, and the old (blocked) answer must not survive anywhere.
    moved = [
        ((32.0, -64.0, 0.0), (32.0, -64.0, 64.0), (32.0, 64.0, 64.0)),
        ((32.0, -64.0, 0.0), (32.0, 64.0, 64.0), (32.0, 64.0, 0.0)),
    ]
    fake.collision((("physics_group_concrete", FLOOR + moved),))
    again = service.prepare("de_inferno")

    assert again.physics.status == "available" and again.asset_id != first.asset_id
    assert service.segment("de_inferno", (-16.0, 0.0, 32.0), (16.0, 0.0, 32.0)).status == "static_clear"
    assert service.segment("de_inferno", (-16.0, 0.0, 32.0), (40.0, 0.0, 32.0)).status == "static_blocked"
    assert service.locate("de_inferno", (0.0, 0.0, 10.0)).floor_z == 0.0
    assert service._loaded[("2000932", "de_inferno")].asset_id == again.asset_id


def test_removed_installed_resource_makes_the_cache_unusable(fake: Fake) -> None:
    service = fake.service()
    assert service.prepare("de_inferno").physics.status == "available"

    (fake.install / "game" / "csgo" / "maps" / "de_inferno.vpk").unlink()

    capabilities = service.capabilities("de_inferno")
    assert capabilities.prepared is False and capabilities.asset_id is None
    assert any("not prepared" in note for note in capabilities.limitations)
    assert service.segment("de_inferno", (0.0, 0.0, 64.0), (0.0, 0.0, 0.0)).status == "unsupported"


def test_same_source_keeps_serving_from_cache(fake: Fake) -> None:
    """A stat fingerprint that did not change must not force re-extraction."""
    service = fake.service()
    first = service.prepare("de_inferno")
    calls = len(fake.calls())

    again = service.prepare("de_inferno")

    assert again.asset_id == first.asset_id and len(fake.calls()) == calls
    assert service.segment("de_inferno", (-16.0, 0.0, 32.0), (16.0, 0.0, 32.0)).status == "static_blocked"

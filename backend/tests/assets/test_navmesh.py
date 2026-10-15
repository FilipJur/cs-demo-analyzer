"""Navigation mesh reader contract.

Synthetic version-36 files (the version Counter-Strike 2 writes) pin the reader's
field layout, and unsupported containers are required to report concrete evidence
instead of guessing at geometry.
"""

from __future__ import annotations

import struct

import pytest

from cs_demo_analyzer.assets.navmesh import NavMeshError, parse

KV3_MAGIC = 0x4B563305


def kv3_blob(payload1: bytes = b"\x00" * 4, payload2: bytes = b"\x00" * 5, *, compression: int = 0) -> bytes:
    """Minimal uncompressed binary-KV3 container: only the header is meaningful here."""
    blob = struct.pack("<I", KV3_MAGIC) + b"\x00" * 16 + struct.pack("<I", compression)
    blob += struct.pack("<HH", 0, 0)
    blob += struct.pack("<iiii", 0, 1, 0, 1)
    blob += struct.pack("<HH", 0, 0)
    blob += struct.pack("<ii", len(payload1) + len(payload2), 0)
    blob += struct.pack("<ii", 0, 0)
    blob += struct.pack("<ii", 0, 0)
    blob += struct.pack("<iiii", len(payload1), 0, len(payload2), 0)
    blob += struct.pack("<8i", *([0] * 8))
    return blob + payload1 + payload2


def pad8(blob: bytes) -> bytes:
    """Nav files place binary-KV3 blobs on 8-byte boundaries (the reader aligns before reading)."""
    return blob + b"\x00" * (-len(blob) % 8)


def nav_file(areas: list[dict], *, version: int = 36, sub_version: int = 1, compression: int = 0, ladders: tuple[dict, ...] = ()) -> bytes:
    """Version-36 nav file: polygons, connections and one generation hull."""
    polygons = [polygon for area in areas for polygon in [area["polygon"]]]
    corners = sorted({corner for polygon in polygons for corner in polygon})
    index = {corner: position for position, corner in enumerate(corners)}
    out = struct.pack("<III", 0xFEEDFACE, version, sub_version) + bytes([1]) + struct.pack("<H", 0) + bytes([0])
    out = pad8(out)
    out += kv3_blob(compression=compression)
    out += struct.pack("<I", len(corners)) + b"".join(struct.pack("<3f", *corner) for corner in corners)
    out += struct.pack("<I", len(polygons))
    for polygon in polygons:
        out += bytes([len(polygon)]) + struct.pack(f"<{len(polygon)}I", *[index[corner] for corner in polygon])
        if version >= 35:
            out += struct.pack("<I", 0xFFFFFFFF)
    if version >= 32:
        out += struct.pack("<I", 0)  # corner gravity flag: none
    if version >= 35:
        out += struct.pack("<I", 0)  # movable nav meshes
    if version >= 36:
        out = pad8(out)
        out += kv3_blob()
    out += struct.pack("<I", len(areas))
    for position, area in enumerate(areas):
        out += struct.pack("<I", area["id"])
        out += struct.pack("<q", 0)
        out += bytes([0])
        out += struct.pack("<I", position)
        out += struct.pack("<f", 0.0)
        for connections in area.get("connections", [[] for _ in area["polygon"]]):
            out += struct.pack("<I", len(connections))
            for neighbour, edge in connections:
                out += struct.pack("<II", neighbour, edge)
        out += bytes([0])  # hiding spots
        out += struct.pack("<I", 0)  # encounter paths
        out += struct.pack("<I", 0)  # ladders above
        out += struct.pack("<I", 0)  # ladders below
    out += struct.pack("<I", len(ladders))
    for ladder in ladders:
        out += struct.pack("<I", ladder.get("id", 1))
        out += struct.pack("<f", ladder.get("width", 32.0))
        out += struct.pack("<3f", *ladder.get("top", (0.0, 0.0, 64.0)))
        out += struct.pack("<3f", *ladder.get("bottom", (0.0, 0.0, 0.0)))
        out += struct.pack("<f", ladder.get("length", 64.0))
        out += struct.pack("<I", ladder.get("direction", 0))
        tops = list(ladder.get("top_areas", ()))
        bottoms = list(ladder.get("bottom_areas", ()))
        out += struct.pack("<5I", *(tops + [0] * (4 - len(tops)))[:4], bottoms[0] if bottoms else 0)
        if version >= 33:
            out += struct.pack("<2I", *(bottoms[1:3] + [0, 0])[:2])
    out += struct.pack("<i", 0)  # transformed bounds
    out += struct.pack("<i", 13)  # nav gen version
    out += struct.pack("<Ifffii f f i f i", 1, 16.0, 8.0, 8.0, 1, 1, 16.0, 0.5, 32, 1.5, 4)
    out += struct.pack("<f", -1.0)  # small area on edge removal
    out += b"hulls\0" + b"\0"  # hull preset name, hull definitions file
    out += struct.pack("<i", 1)  # hull count
    out += bytes([1]) + struct.pack("<ff", 16.0, 72.0)  # enabled, radius, height
    out += bytes([0]) + struct.pack("<f", 36.0)  # short height
    out += bytes([0]) + struct.pack("<f", 36.0)  # agent crawl
    out += struct.pack("<fi", 18.0, 45)  # max climb, max slope
    out += struct.pack("<fff", 200.0, 100.0, 200.0)  # jump down / horizontal / up
    out += struct.pack("<i", -1)  # border erosion
    out += bytes([0])  # gravity follows rotation
    if version >= 36:
        out = pad8(out)
        out += kv3_blob()
    return out


SQUARE = ((0.0, 0.0, 0.0), (64.0, 0.0, 0.0), (64.0, 64.0, 0.0), (0.0, 64.0, 0.0))
FAR = ((500.0, 500.0, 4.0), (564.0, 500.0, 4.0), (564.0, 564.0, 4.0), (500.0, 564.0, 4.0))


def sample_areas() -> list[dict]:
    return [
        {"id": 1, "polygon": SQUARE, "connections": [[(2, 0)], [], [], []]},
        {"id": 2, "polygon": ((64.0, 0.0, 0.0), (128.0, 0.0, 0.0), (128.0, 64.0, 0.0), (64.0, 64.0, 0.0)), "connections": [[], [(1, 0)], [], []]},
        {"id": 3, "polygon": FAR, "connections": [[], [], [], []]},
    ]


def test_synthetic_v36_nav_parses_areas_connections_and_paths() -> None:
    mesh = parse(nav_file(sample_areas()))

    assert (mesh.version, mesh.sub_version, mesh.nav_gen_version) == (36, 1, 13)
    assert [area.area_id for area in mesh.areas] == [1, 2, 3]
    assert mesh.areas[0].corners == SQUARE
    assert mesh.areas[0].links == ((2, 0),)  # duplicate/self connections are not reported
    assert mesh.areas[2].links == ()

    assert mesh.area_at((10.0, 10.0, 0.0)).area_id == 1
    assert mesh.area_at((70.0, 10.0, 4.0)).area_id == 2
    assert mesh.area_at((400.0, 400.0, 0.0)) is None  # outside every polygon
    assert mesh.area_at((10.0, 10.0, 500.0)) is None  # far above the polygon plane

    assert mesh.path(1, 2) == [1, 2]
    assert mesh.path(1, 1) == [1]
    assert mesh.path(1, 3) is None  # area 3 is isolated
    assert mesh.path(1, 99) is None


def test_ladders_become_two_way_transitions_between_their_areas() -> None:
    areas = [
        {"id": 1, "polygon": SQUARE, "connections": [[], [], [], []]},
        {"id": 3, "polygon": FAR, "connections": [[], [], [], []]},
    ]
    body = {"id": 7, "width": 32.0, "top": (10.0, 10.0, 64.0), "bottom": (10.0, 10.0, 0.0), "direction": 2}
    mesh = parse(nav_file(areas, ladders=({**body, "top_areas": (1,), "bottom_areas": (3,)},)))

    assert mesh.ladder_count == 1
    assert mesh.ladder_links() == {1: {3}, 3: {1}}
    assert mesh.path(1, 3) == [1, 3]  # only the ladder connects these areas
    assert mesh.path(3, 1) == [3, 1]  # the stored direction is a facing, not a climb restriction
    ladder = mesh.ladders[0]
    assert (ladder.ladder_id, ladder.top_areas, ladder.bottom_areas) == (7, (1,), (3,))


def test_nav_older_versions_without_polygon_table_read_their_corners() -> None:
    areas = [{"id": 1, "polygon": SQUARE, "connections": [[], [], [], []]}]
    out = struct.pack("<III", 0xFEEDFACE, 30, 0) + bytes([0]) + struct.pack("<H", 0) + bytes([0])
    out += struct.pack("<I", 1)  # one area
    out += struct.pack("<I", 1) + struct.pack("<q", 0) + bytes([0]) + struct.pack("<I", len(SQUARE))  # area id 1
    out += b"".join(struct.pack("<3f", *corner) for corner in SQUARE)
    out += struct.pack("<f", 0.0)
    out += struct.pack("<I", 0) * len(SQUARE)
    out += bytes([0]) + struct.pack("<I", 0) + struct.pack("<I", 0) + struct.pack("<I", 0)
    out += struct.pack("<I", 0) + struct.pack("<i", 0)
    out += struct.pack("<i", 6)
    out += struct.pack("<Ifffii f f i f i", 0, 16.0, 8.0, 8.0, 1, 1, 16.0, 0.5, 32, 1.5, 4)
    out += struct.pack("<i", 3)  # hull count ignored below v12
    for _ in range(3):
        out += struct.pack("<ff", 16.0, 72.0) + struct.pack("<fi", 18.0, 45) + struct.pack("<fff", 200.0, 100.0, 200.0)
    mesh = parse(out)

    assert mesh.version == 30
    assert mesh.areas[0].corners == SQUARE
    assert mesh.path(1, 1) == [1]


def test_unsupported_containers_report_concrete_evidence() -> None:
    with pytest.raises(NavMeshError, match="compression method 1"):
        parse(nav_file(sample_areas(), compression=1))
    with pytest.raises(NavMeshError, match="unsupported nav version 99"):
        parse(struct.pack("<III", 0xFEEDFACE, 99, 0) + bytes([0]) + struct.pack("<H", 0) + bytes([0]))
    with pytest.raises(NavMeshError, match="ended early"):
        parse(nav_file(sample_areas())[:200])
    with pytest.raises(NavMeshError, match="unexpected nav magic"):
        parse(b"not a nav file" + b"\x00" * 32)

"""Reader and queries for a map's compiled Source 2 navigation mesh (``.nav``).

Port of ValveResourceFormat 20.1's ``ValveResourceFormat/NavMesh/*.cs``
(MIT, credit to ValveResourceFormat contributors) restricted to what this slice
needs: file header, places, polygons, areas and their connections, ladders and
the generation parameters that must be walked to reach them. Nothing is
inferred: anything the port cannot read raises :class:`NavMeshError`, and the
caller degrades navigation to ``unsupported`` with that evidence.

Counter-Strike 2 writes nav version 36, which embeds two binary KV3 blobs before
and after the polygon table. Only their byte length is needed here, so the KV3
container header is parsed and its payload skipped (uncompressed blobs only;
compressed or block blobs are reported instead of guessed at).
"""

from __future__ import annotations

import heapq
import math
import struct
from dataclasses import dataclass
from typing import Iterable

Vec3 = tuple[float, float, float]

NAV_MAGIC = 0xFEEDFACE
MIN_VERSION = 30
MAX_VERSION = 36
KV3_MAGIC = 0x4B5633  # "3VK" in file order, after the leading version byte
KV3_UNCOMPRESSED = 0
KV3_TRAILER = 0xFFEEDD00


class NavMeshError(Exception):
    """The navigation file could not be parsed (reported, never guessed at)."""


class _Reader:
    __slots__ = ("data", "pos")

    def __init__(self, data: bytes, pos: int = 0) -> None:
        self.data, self.pos = data, pos

    def u8(self) -> int:
        value = self.data[self.pos]
        self.pos += 1
        return value

    def u16(self) -> int:
        (value,) = self.unpack("<H", 2)
        return value

    def u32(self) -> int:
        (value,) = self.unpack("<I", 4)
        return value

    def i32(self) -> int:
        (value,) = self.unpack("<i", 4)
        return value

    def i64(self) -> int:
        (value,) = self.unpack("<q", 8)
        return value

    def f32(self) -> float:
        (value,) = self.unpack("<f", 4)
        return value

    def vec3(self) -> Vec3:
        values = self.unpack("<3f", 12)
        return (values[0], values[1], values[2])

    def take(self, count: int) -> bytes:
        chunk = self.data[self.pos : self.pos + count]
        if len(chunk) != count:
            raise NavMeshError(f"nav file ended early at {self.pos} (wanted {count} bytes)")
        self.pos += count
        return chunk

    def unpack(self, fmt: str, size: int) -> tuple:
        try:
            value = struct.unpack_from(fmt, self.data, self.pos)
        except struct.error:
            raise NavMeshError(f"nav file ended early at {self.pos} (wanted {size} bytes)") from None
        self.pos += size
        return value

    def skip(self, count: int) -> None:
        self.take(count)

    def align(self, boundary: int) -> None:
        self.pos = (self.pos + boundary - 1) & ~(boundary - 1)

    def null_term(self) -> str:
        end = self.data.find(b"\0", self.pos)
        if end < 0:
            raise NavMeshError(f"unterminated string at {self.pos}")
        text = self.data[self.pos : end].decode("utf-8", errors="replace")
        self.pos = end + 1
        return text


@dataclass(frozen=True)
class NavArea:
    """One navigation area (convex polygon) with its connections to neighbours."""

    area_id: int
    hull_index: int
    flags: int
    corners: tuple[Vec3, ...]
    links: tuple[tuple[int, int], ...]  # (neighbour area id, edge id), deduplicated
    ladders_above: tuple[int, ...] = ()
    ladders_below: tuple[int, ...] = ()

    @property
    def bounds(self) -> tuple[Vec3, Vec3]:
        """Axis-aligned bounds of the polygon corners (cheap area rejection)."""
        xs = [corner[0] for corner in self.corners]
        ys = [corner[1] for corner in self.corners]
        zs = [corner[2] for corner in self.corners]
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    @property
    def center(self) -> Vec3:
        count = len(self.corners)
        return (
            sum(corner[0] for corner in self.corners) / count,
            sum(corner[1] for corner in self.corners) / count,
            sum(corner[2] for corner in self.corners) / count,
        )

    def contains(self, point: Vec3, vertical_tolerance: float = 24.0) -> bool:
        """Plane-distance plus in-polygon test (no engine portal/HUGE-area special cases)."""
        if len(self.corners) < 3:
            return False
        normal = _newell(self.corners)
        if normal is None:
            return False
        offset = _dot(normal, self.corners[0])
        if abs(_dot(normal, point) - offset) > vertical_tolerance:
            return False
        axis = max(range(3), key=lambda index: abs(normal[index]))
        other = [index for index in range(3) if index != axis]
        polygon = [(corner[other[0]], corner[other[1]]) for corner in self.corners]
        return _point_in_polygon((point[other[0]], point[other[1]]), polygon)


@dataclass(frozen=True)
class NavLadder:
    """A ladder joining a group of top-side areas with bottom-side areas."""

    ladder_id: int
    width: float
    top: Vec3
    bottom: Vec3
    direction: int
    top_areas: tuple[int, ...]
    bottom_areas: tuple[int, ...]

    @property
    def areas(self) -> tuple[int, ...]:
        return self.top_areas + self.bottom_areas


@dataclass(frozen=True)
class NavMesh:
    version: int
    sub_version: int
    analyzed: bool
    place_names: tuple[str, ...]
    areas: tuple[NavArea, ...]
    ladders: tuple[NavLadder, ...]
    nav_gen_version: int
    hull_count: int

    @property
    def ladder_count(self) -> int:
        return len(self.ladders)

    def by_id(self) -> dict[int, NavArea]:
        return {area.area_id: area for area in self.areas}

    def ladder_links(self) -> dict[int, set[int]]:
        """Area adjacency contributed by ladders, both directions.

        The stored ``direction`` is a cardinal facing (north/east/south/west), not
        a climb restriction, so ladder transitions are modelled as two-way and
        callers are told when a path uses them.
        """
        links: dict[int, set[int]] = {}
        for ladder in self.ladders:
            for top in ladder.top_areas:
                for bottom in ladder.bottom_areas:
                    links.setdefault(top, set()).add(bottom)
                    links.setdefault(bottom, set()).add(top)
        return links

    def area_at(self, point: Vec3, vertical_tolerance: float = 24.0) -> NavArea | None:
        """The closest area containing ``point``, or ``None`` outside walkable space."""
        best: NavArea | None = None
        best_distance = math.inf
        for area in self.areas:
            low, high = area.bounds
            if not (low[0] <= point[0] <= high[0] and low[1] <= point[1] <= high[1] and low[2] - vertical_tolerance <= point[2] <= high[2] + vertical_tolerance):
                continue
            if not area.contains(point, vertical_tolerance):
                continue
            distance = _distance3(area.center, point)
            if distance < best_distance:
                best, best_distance = area, distance
        return best

    def path(self, start_area: int, end_area: int) -> list[int] | None:
        """Area-id path from ``start_area`` to ``end_area`` (A* over stored connections)."""
        if start_area == end_area:
            return [start_area] if start_area in self.by_id() else None
        areas = self.by_id()
        if start_area not in areas or end_area not in areas:
            return None
        ladders = self.ladder_links()
        goal = areas[end_area].center
        frontier: list[tuple[float, int]] = [(0.0, start_area)]
        came_from: dict[int, int] = {}
        cost: dict[int, float] = {start_area: 0.0}
        while frontier:
            _, current = heapq.heappop(frontier)
            if current == end_area:
                path = [current]
                while path[-1] != start_area:
                    path.append(came_from[path[-1]])
                path.reverse()
                return path
            center = areas[current].center
            neighbours = [neighbour for neighbour, _ in areas[current].links]
            neighbours.extend(ladder for ladder in ladders.get(current, ()) if ladder not in neighbours)
            for neighbour in neighbours:
                if neighbour not in areas:
                    continue
                step = cost[current] + _distance3(center, areas[neighbour].center)
                if step < cost.get(neighbour, math.inf):
                    cost[neighbour] = step
                    came_from[neighbour] = current
                    heapq.heappush(frontier, (step + _distance3(areas[neighbour].center, goal), neighbour))
        return None


def parse(data: bytes) -> NavMesh:
    """Parse nav mesh bytes; raises :class:`NavMeshError` with concrete evidence."""
    reader = _Reader(data)
    magic = reader.u32()
    if magic != NAV_MAGIC:
        raise NavMeshError(f"unexpected nav magic {magic:#010x}")
    version = reader.u32()
    if not MIN_VERSION <= version <= MAX_VERSION:
        raise NavMeshError(f"unsupported nav version {version}")
    sub_version = reader.u32()
    analyzed = reader.u8() != 0

    place_count = reader.u16()
    places = []
    for _ in range(place_count):
        length = reader.u16()
        places.append(reader.take(length).decode("utf-8", errors="replace").rstrip("\0"))
    reader.u8()  # has unnamed areas

    if version >= 36:
        _skip_kv3(reader)

    polygons: list[tuple[Vec3, ...]] = []
    if version >= 31:
        corner_count = reader.u32()
        corners = [reader.vec3() for _ in range(corner_count)]
        polygon_count = reader.u32()
        for _ in range(polygon_count):
            polygon_corners = reader.u8()
            indices = [reader.u32() for _ in range(polygon_corners)]
            if version >= 35:
                reader.u32()  # movable mesh id
            try:
                polygons.append(tuple(corners[index] for index in indices))
            except IndexError:
                raise NavMeshError(f"nav polygon corner index out of range at {reader.pos}") from None
        if version >= 32:
            _read_corner_gravity(reader)

    if version >= 35:
        movable_count = reader.u32()
        for _ in range(movable_count):
            reader.null_term()  # movable mesh id
            reader.skip(48)  # matrix3x4

    if version >= 36:
        _skip_kv3(reader)  # game data

    area_count = reader.u32()
    areas = tuple(_read_area(reader, version, polygons) for _ in range(area_count))

    ladders = tuple(_read_ladder(reader, version) for _ in range(reader.u32()))

    bounds_count = reader.i32()
    for _ in range(bounds_count):
        reader.skip(24 + 48)

    generation = _read_generation_params(reader)

    if version >= 36:
        _skip_kv3(reader)  # extra generation parameters

    # A non-zero sub version appends Counter-Strike bot analysis (KV3) as the last
    # section; nothing this slice needs lives there, so the file is left there.

    return NavMesh(
        version=version,
        sub_version=sub_version,
        analyzed=analyzed,
        place_names=tuple(places),
        areas=areas,
        ladders=ladders,
        nav_gen_version=generation,
        hull_count=len({area.hull_index for area in areas}),
    )


def _read_ladder(reader: _Reader, version: int) -> NavLadder:
    ladder_id = reader.u32()
    width = reader.f32()
    top = reader.vec3()
    bottom = reader.vec3()
    reader.f32()  # length
    direction = reader.u32()
    top_forward, top_left, top_right, top_behind, bottom_area = (reader.u32() for _ in range(5))
    bottom_left = bottom_right = 0
    if version >= 33:
        bottom_left, bottom_right = reader.u32(), reader.u32()
    return NavLadder(
        ladder_id=ladder_id,
        width=width,
        top=top,
        bottom=bottom,
        direction=direction,
        top_areas=tuple(area for area in (top_forward, top_left, top_right, top_behind) if area),
        bottom_areas=tuple(area for area in (bottom_area, bottom_left, bottom_right) if area),
    )


def _read_area(reader: _Reader, version: int, polygons: list[tuple[Vec3, ...]]) -> NavArea:
    area_id = reader.u32()
    flags = reader.i64()
    hull_index = reader.u8()
    if version >= 31:
        polygon_index = reader.u32()
        if polygon_index >= len(polygons):
            raise NavMeshError(f"nav area {area_id} references polygon {polygon_index} of {len(polygons)}")
        corners = polygons[polygon_index]
    else:
        count = reader.u32()
        corners = tuple(reader.vec3() for _ in range(count))
    reader.f32()  # unused, always zero

    links: list[tuple[int, int]] = []
    seen: set[int] = set()
    for _ in range(len(corners)):
        connection_count = reader.u32()
        for _ in range(connection_count):
            neighbour = reader.u32()
            edge_id = reader.u32()
            if neighbour != area_id and neighbour not in seen:
                seen.add(neighbour)
                links.append((neighbour, edge_id))

    hiding_spot_count = reader.u8()
    for _ in range(hiding_spot_count):
        reader.skip(4 + 12 + 1)

    encounter_paths = reader.u32()
    if encounter_paths:
        raise NavMeshError(f"nav area {area_id} has {encounter_paths} encounter paths (unsupported)")

    above = tuple(reader.u32() for _ in range(reader.u32()))
    below = tuple(reader.u32() for _ in range(reader.u32()))
    return NavArea(
        area_id=area_id,
        hull_index=hull_index,
        flags=flags,
        corners=corners,
        links=tuple(links),
        ladders_above=above,
        ladders_below=below,
    )


def _read_corner_gravity(reader: _Reader) -> None:
    flags = reader.u32()
    if not flags & 1:
        return
    count = reader.u32()
    reader.skip(count * 12)


def _read_generation_params(reader: _Reader) -> int:
    nav_gen_version = reader.i32()
    if nav_gen_version < 6:
        raise NavMeshError(f"unsupported nav generation version {nav_gen_version}")
    # 11 fields: use-project-defaults, tile size, cell size/height, min+merged region
    # size, sample distance, max sample error, max edge length/error, verts per poly
    reader.skip(4 * 11)
    if nav_gen_version >= 7:
        reader.skip(4)  # small area on edge removal
    if nav_gen_version >= 12:
        reader.null_term()  # hull preset name
        reader.null_term()  # hull definitions file
    hull_count = reader.i32() if nav_gen_version >= 12 else 3
    for _ in range(hull_count):
        _read_hull_params(reader, nav_gen_version)
    if nav_gen_version >= 10:
        reader.skip(1)  # gravity follows rotation
    return nav_gen_version


def _read_hull_params(reader: _Reader, nav_gen_version: int) -> None:
    if nav_gen_version >= 9:
        reader.skip(1)
    reader.skip(8)  # radius, height
    if nav_gen_version >= 8:
        reader.skip(1 + 4)  # short height enabled, short height
    if nav_gen_version >= 13:
        reader.skip(1 + 4)  # agent crawl enabled, crawl height
    reader.skip(4 + 4)  # max climb, max slope
    reader.skip(12)  # jump down / jump horizontal / jump up
    if nav_gen_version >= 11:
        reader.skip(4)  # border erosion


def _skip_kv3(reader: _Reader) -> None:
    """Consume one binary KV3 blob using its container header."""
    reader.align(8)
    start = reader.pos
    word = reader.u32()
    version = word & 0xFF
    if word >> 8 != KV3_MAGIC:
        raise NavMeshError(f"nav KV3 blob at {start} has unknown magic {word:#010x}")
    reader.skip(16)  # encoding/format guid
    compression = reader.u32()
    if compression != KV3_UNCOMPRESSED:
        raise NavMeshError(f"nav KV3 blob at {start} uses compression method {compression} (unsupported)")
    if version == 1:
        raise NavMeshError(f"nav KV3 blob at {start} is version 1 (unsupported)")

    reader.skip(2 + 2)  # compression dictionary id (u16), frame size (u16)
    reader.skip(4 * 4)  # bytes1/bytes4/bytes8/types counts
    reader.skip(2 + 2)  # object and array counts
    uncompressed_total, _compressed_total = reader.i32(), reader.i32()
    block_count, binary_blob_bytes = reader.i32(), reader.i32()
    if version >= 4:
        reader.skip(4 * 2)  # bytes2 count, block compressed sizes bytes
    if version >= 5:
        buffer1, buffer1_compressed = reader.i32(), reader.i32()
        buffer2, buffer2_compressed = reader.i32(), reader.i32()
        reader.skip(4 * 8)  # buffer2 lane counts (bytes1/2/4/8) and four allocation hints
        if buffer1_compressed or buffer2_compressed:
            raise NavMeshError(f"nav KV3 blob at {start} has compressed buffers (unsupported)")
    else:
        buffer1, buffer2 = uncompressed_total, 0
    payload = buffer1 + buffer2
    if block_count:
        payload += binary_blob_bytes + 4  # blob data plus the trailing marker
    reader.skip(payload)


def _newell(corners: Iterable[Vec3]) -> Vec3 | None:
    nx = ny = nz = 0.0
    points = list(corners)
    for index, current in enumerate(points):
        following = points[(index + 1) % len(points)]
        nx += (current[1] - following[1]) * (current[2] + following[2])
        ny += (current[2] - following[2]) * (current[0] + following[0])
        nz += (current[0] - following[0]) * (current[1] + following[1])
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    return None if length < 1e-9 else (nx / length, ny / length, nz / length)


def _point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    inside = False
    count = len(polygon)
    for index in range(count):
        x1, y1 = polygon[index]
        x2, y2 = polygon[(index + 1) % count]
        if (y1 > point[1]) != (y2 > point[1]):
            crossing = x1 + (point[1] - y1) * (x2 - x1) / (y2 - y1)
            if point[0] < crossing:
                inside = not inside
    return inside


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _distance3(a: Vec3, b: Vec3) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)

"""Authored ray math and a uniform-cell index over static collision triangles.

Pure standard library: collision queries are bounded offline work (a handful of
sightline/nav probes per encounter), and the project has no numeric dependency,
so the acceleration structure is a uniform grid with exact AABB-overlap
insertion. Insertion covers every cell a triangle's bounding box touches, so a
traversal that visits every cell the ray crosses cannot miss a hit — callers get
the same answer as a brute-force scan.
"""

from __future__ import annotations

import math
from array import array
from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

Vec3 = tuple[float, float, float]

EPSILON = 1e-9
# Triangles whose bounds cover more cells than this go to the overflow bucket,
# which is tested on every query instead of exploding the cell lists.
MAX_CELLS_PER_TRIANGLE = 256


def dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def subtract(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def scale(a: Vec3, factor: float) -> Vec3:
    return (a[0] * factor, a[1] * factor, a[2] * factor)


def cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def length(a: Vec3) -> float:
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def normalize(a: Vec3) -> Vec3 | None:
    norm = length(a)
    return None if norm <= EPSILON else (a[0] / norm, a[1] / norm, a[2] / norm)


def is_finite_vec3(value: object) -> bool:
    """True for a real 3-sequence of finite numbers (rejects bools and NaN)."""
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        return False
    return all(isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item) for item in value)


def coerce_vec3(value: object) -> Vec3 | None:
    """Finite float triple from a 3-sequence, else ``None``."""
    return (float(value[0]), float(value[1]), float(value[2])) if is_finite_vec3(value) else None  # type: ignore[index]


@dataclass(frozen=True)
class AABB:
    low: Vec3
    high: Vec3

    @classmethod
    def around(cls, points: Iterable[Vec3]) -> AABB | None:
        iterator = iter(points)
        try:
            first = next(iterator)
        except StopIteration:
            return None
        low = high = first
        for point in iterator:
            low = (min(low[0], point[0]), min(low[1], point[1]), min(low[2], point[2]))
            high = (max(high[0], point[0]), max(high[1], point[1]), max(high[2], point[2]))
        return cls(low, high)

    def union(self, other: AABB) -> AABB:
        return AABB(
            (min(self.low[0], other.low[0]), min(self.low[1], other.low[1]), min(self.low[2], other.low[2])),
            (max(self.high[0], other.high[0]), max(self.high[1], other.high[1]), max(self.high[2], other.high[2])),
        )

    def contains(self, point: Vec3, epsilon: float = 0.0) -> bool:
        return all(self.low[axis] - epsilon <= point[axis] <= self.high[axis] + epsilon for axis in range(3))

    def expanded(self, margin: float) -> AABB:
        return AABB(
            (self.low[0] - margin, self.low[1] - margin, self.low[2] - margin),
            (self.high[0] + margin, self.high[1] + margin, self.high[2] + margin),
        )

    @property
    def center(self) -> Vec3:
        return ((self.low[0] + self.high[0]) / 2, (self.low[1] + self.high[1]) / 2, (self.low[2] + self.high[2]) / 2)


def slab_interval(origin: Vec3, inverse: Vec3, low: Vec3, high: Vec3) -> tuple[float, float]:
    """Ray/box interval from an inverse-direction vector; NaN-safe on axis-parallel rays."""
    t_near, t_far = -math.inf, math.inf
    for axis in range(3):
        first = (low[axis] - origin[axis]) * inverse[axis]
        second = (high[axis] - origin[axis]) * inverse[axis]
        if first != first:  # 0 * inf: origin exactly on the slab plane, the ray stays inside on this axis
            first = -math.inf
        if second != second:
            second = math.inf
        if first > second:
            first, second = second, first
        t_near = max(t_near, first)
        t_far = min(t_far, second)
    return t_near, t_far


def ray_triangle(origin: Vec3, direction: Vec3, a: Vec3, b: Vec3, c: Vec3) -> float | None:
    """Möller–Trumbore distance along ``direction`` (two-sided winding), else ``None``."""
    edge1 = subtract(b, a)
    edge2 = subtract(c, a)
    pvec = cross(direction, edge2)
    determinant = dot(edge1, pvec)
    if abs(determinant) < EPSILON:
        return None  # parallel ray or degenerate triangle
    inverse = 1.0 / determinant
    tvec = subtract(origin, a)
    u = dot(tvec, pvec) * inverse
    if u < -EPSILON or u > 1 + EPSILON:
        return None
    qvec = cross(tvec, edge1)
    v = dot(direction, qvec) * inverse
    if v < -EPSILON or u + v > 1 + EPSILON:
        return None
    distance = dot(edge2, qvec) * inverse
    return distance if distance >= 0 else None


def triangle_normal(positions: array, indices: array, index: int) -> Vec3 | None:
    """Geometric normal of one triangle, or ``None`` for a degenerate triangle."""
    base = index * 3
    ia, ib, ic = indices[base] * 3, indices[base + 1] * 3, indices[base + 2] * 3
    a = (positions[ia], positions[ia + 1], positions[ia + 2])
    b = (positions[ib], positions[ib + 1], positions[ib + 2])
    c = (positions[ic], positions[ic + 1], positions[ic + 2])
    return normalize(cross(subtract(b, a), subtract(c, a)))


def _position_bounds(positions: array) -> AABB:
    """Bounds over a flat position array (``array`` keeps this out of the per-point Python path)."""
    low = [math.inf, math.inf, math.inf]
    high = [-math.inf, -math.inf, -math.inf]
    for offset in range(0, len(positions), 3):
        for axis in range(3):
            value = positions[offset + axis]
            if value < low[axis]:
                low[axis] = value
            if value > high[axis]:
                high[axis] = value
    if low[0] == math.inf:
        return AABB((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    return AABB((low[0], low[1], low[2]), (high[0], high[1], high[2]))


class TriangleSoup:
    """Indexed collision triangles plus their source surface groups."""

    __slots__ = ("positions", "indices", "groups", "bounds")

    def __init__(self, positions: array, indices: array, groups: Sequence[tuple[str, int]], bounds: AABB) -> None:
        self.positions = positions
        self.indices = indices
        self.groups = tuple(groups)  # (surface property name, triangle count) in index order
        self.bounds = bounds

    @property
    def triangle_count(self) -> int:
        return len(self.indices) // 3

    @classmethod
    def from_points(cls, positions: array, indices: array, groups: Sequence[tuple[str, int]]) -> TriangleSoup:
        return cls(positions, indices, groups, _position_bounds(positions))

    def points(self, indices: Sequence[int]) -> list[Vec3]:
        return [
            (self.positions[i * 3], self.positions[i * 3 + 1], self.positions[i * 3 + 2]) for i in indices
        ]

    def triangle_bounds(self, index: int) -> AABB:
        base = index * 3
        return AABB.around(self.points([self.indices[base], self.indices[base + 1], self.indices[base + 2]]))  # type: ignore[arg-type]

    def hit(self, index: int, origin: Vec3, direction: Vec3) -> float | None:
        base = index * 3
        ia, ib, ic = self.indices[base] * 3, self.indices[base + 1] * 3, self.indices[base + 2] * 3
        return ray_triangle(
            origin,
            direction,
            (self.positions[ia], self.positions[ia + 1], self.positions[ia + 2]),
            (self.positions[ib], self.positions[ib + 1], self.positions[ib + 2]),
            (self.positions[ic], self.positions[ic + 1], self.positions[ic + 2]),
        )

    def surface_of(self, index: int) -> str | None:
        seen = 0
        for name, count in self.groups:
            seen += count
            if index < seen:
                return name
        return None

    def normal_at(self, index: int) -> Vec3 | None:
        """Geometric normal of one triangle, oriented towards the ray origin by callers."""
        return triangle_normal(self.positions, self.indices, index)

    def ray_first_linear(self, origin: Vec3, direction: Vec3, max_distance: float) -> tuple[int, float] | None:
        """Brute-force nearest hit; the reference the grid must reproduce exactly."""
        best_index, best_distance = -1, max_distance
        for index in range(self.triangle_count):
            distance = self.hit(index, origin, direction)
            if distance is not None and distance <= best_distance:
                best_index, best_distance = index, distance
        return None if best_index < 0 else (best_index, best_distance)


@dataclass(frozen=True)
class CellRange:
    low: tuple[int, int, int]
    high: tuple[int, int, int]


class TriangleGrid:
    """Uniform-cell index over a :class:`TriangleSoup`."""

    __slots__ = ("_soup", "_low", "_cell", "_nx", "_ny", "_nz", "_offsets", "_counts", "_items", "_overflow")

    def __init__(self, soup, low, cell, dims, offsets, counts, items, overflow):
        self._soup, self._low, self._cell, self._nx, self._ny, self._nz = soup, low, cell, dims[0], dims[1], dims[2]
        self._offsets, self._counts, self._items, self._overflow = offsets, counts, items, overflow

    @classmethod
    def restore(cls, soup: TriangleSoup, low: Vec3, cell_size: float, dims: tuple[int, int, int], counts: array, offsets: array, items: array, overflow: array) -> TriangleGrid:
        """Rebuild an index from cached arrays written by :meth:`build`."""
        return cls(soup, low, cell_size, dims, offsets, counts, items, overflow)

    @property
    def items(self) -> array:
        return self._items

    @property
    def overflow(self) -> array:
        return self._overflow

    @property
    def soup(self) -> TriangleSoup:
        return self._soup

    @classmethod
    def build(cls, soup: TriangleSoup, *, cell_size: float = 128.0) -> TriangleGrid:
        bounds = soup.bounds
        low = (bounds.low[0], bounds.low[1], bounds.low[2])
        dims = tuple(max(1, int(math.ceil((bounds.high[axis] - low[axis]) / cell_size)) + 1) for axis in range(3))
        nx, ny, nz = dims
        counts = array("i", bytes(4 * nx * ny * nz))
        overflow: list[int] = []
        ranges: list[CellRange | None] = [None] * soup.triangle_count
        for index in range(soup.triangle_count):
            box = soup.triangle_bounds(index)
            cell_range = _cell_range(box, low, cell_size, dims)
            ranges[index] = cell_range
            if _cell_count(cell_range) > MAX_CELLS_PER_TRIANGLE:
                overflow.append(index)
                continue
            for cz in range(cell_range.low[2], cell_range.high[2] + 1):
                for cy in range(cell_range.low[1], cell_range.high[1] + 1):
                    base = (cz * ny + cy) * nx
                    for cx in range(cell_range.low[0], cell_range.high[0] + 1):
                        counts[base + cx] += 1
        offsets = array("i", bytes(4 * len(counts)))
        running = 0
        for cell in range(len(counts)):
            offsets[cell] = running
            running += counts[cell]
        items = array("i", bytes(4 * running))
        cursor = array("i", offsets)
        for index in range(soup.triangle_count):
            cell_range = ranges[index]
            if cell_range is None or _cell_count(cell_range) > MAX_CELLS_PER_TRIANGLE:
                continue
            for cz in range(cell_range.low[2], cell_range.high[2] + 1):
                for cy in range(cell_range.low[1], cell_range.high[1] + 1):
                    base = (cz * ny + cy) * nx
                    for cx in range(cell_range.low[0], cell_range.high[0] + 1):
                        cell = base + cx
                        items[cursor[cell]] = index
                        cursor[cell] += 1
        return cls(soup, low, cell_size, dims, offsets, counts, items, array("i", overflow))

    @property
    def cell_counts(self) -> array:
        return self._counts

    @property
    def overflow_count(self) -> int:
        return len(self._overflow)

    @property
    def dims(self) -> tuple[int, int, int]:
        return (self._nx, self._ny, self._nz)

    @property
    def cell_size(self) -> float:
        return self._cell

    @property
    def origin(self) -> Vec3:
        return self._low

    def cell_bounds(self, cell: tuple[int, int, int]) -> AABB:
        low = tuple(self._low[axis] + cell[axis] * self._cell for axis in range(3))
        return AABB(low, (low[0] + self._cell, low[1] + self._cell, low[2] + self._cell))  # type: ignore[arg-type]

    def candidates(self, box: AABB) -> Iterator[int]:
        """Every triangle the index considers for ``box`` (cells it touches plus overflow)."""
        cell_range = _cell_range(box, self._low, self._cell, (self._nx, self._ny, self._nz), clamp=True)
        seen: set[int] = set()
        for cz in range(cell_range.low[2], cell_range.high[2] + 1):
            for cy in range(cell_range.low[1], cell_range.high[1] + 1):
                base = (cz * self._ny + cy) * self._nx
                for cx in range(cell_range.low[0], cell_range.high[0] + 1):
                    cell = base + cx
                    for slot in range(self._offsets[cell], self._offsets[cell] + self._counts[cell]):
                        item = self._items[slot]
                        if item not in seen:
                            seen.add(item)
                            yield item
        for item in self._overflow:
            if item not in seen:
                seen.add(item)
                yield item

    def ray_first(self, origin: Vec3, direction: Vec3, max_distance: float, skip: "Sequence[int] | None" = None) -> tuple[int, float] | None:
        """Nearest triangle hit within ``max_distance``, or ``None``.

        ``skip`` is an optional per-triangle mask (truthy = not part of this
        query's surface set), used to answer sightline questions without the
        movement-only clip volumes that never block a bullet or a view.
        """
        soup = self._soup
        best_index, best_distance = -1, max_distance
        for index in self._walk(origin, direction, max_distance):
            if skip is not None and skip[index]:
                continue
            distance = soup.hit(index, origin, direction)
            if distance is not None and distance <= best_distance:
                best_index, best_distance = index, distance
        return None if best_index < 0 else (best_index, best_distance)

    def _walk(self, origin: Vec3, direction: Vec3, max_distance: float) -> Iterator[int]:
        """Triangle indices of every cell the ray crosses, nearest cells first."""
        inverse = (
            math.inf if direction[0] == 0 else 1.0 / direction[0],
            math.inf if direction[1] == 0 else 1.0 / direction[1],
            math.inf if direction[2] == 0 else 1.0 / direction[2],
        )
        grid_low = self._low
        grid_high = (
            grid_low[0] + self._nx * self._cell,
            grid_low[1] + self._ny * self._cell,
            grid_low[2] + self._nz * self._cell,
        )
        enter, exit_ = slab_interval(origin, inverse, grid_low, grid_high)
        if enter > exit_ or exit_ < 0:
            yield from self._overflow
            return
        exit_ = min(exit_, max_distance)
        start = max(enter, 0.0)
        start_point = (origin[0] + direction[0] * start, origin[1] + direction[1] * start, origin[2] + direction[2] * start)
        cell = [
            _clamp(int((start_point[axis] - grid_low[axis]) / self._cell), 0, (self._nx, self._ny, self._nz)[axis] - 1)
            for axis in range(3)
        ]
        step = [0 if direction[axis] == 0 else (1 if direction[axis] > 0 else -1) for axis in range(3)]
        next_crossing = [math.inf, math.inf, math.inf]
        delta = [math.inf, math.inf, math.inf]
        for axis in range(3):
            if step[axis] == 0:
                continue
            boundary = grid_low[axis] + (cell[axis] + (1 if step[axis] > 0 else 0)) * self._cell
            next_crossing[axis] = start + (boundary - start_point[axis]) * inverse[axis]
            delta[axis] = abs(self._cell * inverse[axis])
        distance = start
        dims = (self._nx, self._ny, self._nz)
        while distance <= exit_:
            base = (cell[2] * self._ny + cell[1]) * self._nx
            cell_index = base + cell[0]
            for slot in range(self._offsets[cell_index], self._offsets[cell_index] + self._counts[cell_index]):
                yield self._items[slot]
            axis = 0 if next_crossing[0] <= next_crossing[1] and next_crossing[0] <= next_crossing[2] else (
                1 if next_crossing[1] <= next_crossing[2] else 2
            )
            if next_crossing[axis] > exit_:
                break
            distance = next_crossing[axis]
            cell[axis] += step[axis]
            if not 0 <= cell[axis] < dims[axis]:
                break
            next_crossing[axis] += delta[axis]
        yield from self._overflow


def _clamp(value: int, low: int, high: int) -> int:
    return low if value < low else (high if value > high else value)


def _cell_range(box: AABB, low: Vec3, cell: float, dims: tuple[int, int, int], clamp: bool = False) -> CellRange:
    indices = []
    for axis in range(3):
        first = int(math.floor((box.low[axis] - low[axis]) / cell))
        last = int(math.floor((box.high[axis] - low[axis]) / cell))
        if clamp:
            first, last = _clamp(first, 0, dims[axis] - 1), _clamp(last, 0, dims[axis] - 1)
        indices.append((first, last))
    return CellRange((indices[0][0], indices[1][0], indices[2][0]), (indices[0][1], indices[1][1], indices[2][1]))


def _cell_count(cell_range: CellRange) -> int:
    return (
        (cell_range.high[0] - cell_range.low[0] + 1)
        * (cell_range.high[1] - cell_range.low[1] + 1)
        * (cell_range.high[2] - cell_range.low[2] + 1)
    )

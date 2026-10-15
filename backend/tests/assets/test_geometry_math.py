"""Authored ray/volume math and the collision index contract.

Hand-computed expectations only: the grid must answer exactly what a brute-force
scan over the same triangles answers, including degenerate and overflow cases.
"""

from __future__ import annotations

import math

from cs_demo_analyzer.assets.geometry_math import (
    AABB,
    TriangleGrid,
    TriangleSoup,
    coerce_vec3,
    normalize,
    ray_triangle,
    slab_interval,
    triangle_normal,
)

# A unit right triangle in the z = 0 plane: (0,0,0), (2,0,0), (0,2,0).
TRIANGLE = ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (0.0, 2.0, 0.0))


def test_ray_triangle_hand_computed_cases() -> None:
    a, b, c = TRIANGLE
    # Straight down through the triangle interior from height 5: distance 5.
    assert ray_triangle((0.5, 0.5, 5.0), (0.0, 0.0, -1.0), a, b, c) == 5.0
    # Misses the hypotenuse corner (0.9, 0.9) is outside x + y <= 2... it is inside; use (1.5, 1.5).
    assert ray_triangle((1.5, 1.5, 5.0), (0.0, 0.0, -1.0), a, b, c) is None
    # Parallel to the triangle plane never hits.
    assert ray_triangle((0.5, 0.5, 5.0), (1.0, 0.0, 0.0), a, b, c) is None
    # The hit is behind the ray origin.
    assert ray_triangle((0.5, 0.5, -5.0), (0.0, 0.0, -1.0), a, b, c) is None
    # Two-sided: hitting the back face still counts (collision meshes are not culled).
    assert ray_triangle((0.5, 0.5, -5.0), (0.0, 0.0, 1.0), a, b, c) == 5.0
    # Degenerate triangle (all points equal) has no intersection.
    assert ray_triangle((0.0, 0.0, 5.0), (0.0, 0.0, -1.0), a, a, a) is None


def test_triangle_normal_and_coercion() -> None:
    a, b, c = TRIANGLE
    positions = [coordinate for vertex in (a, b, c) for coordinate in vertex]
    from array import array

    normal = triangle_normal(array("f", positions), array("i", [0, 1, 2]), 0)
    assert normal == (0.0, 0.0, 1.0)  # cross(b - a, c - a) for this counter-clockwise triangle
    assert normalize((0.0, 0.0, 0.0)) is None
    assert coerce_vec3((1, 2, 3)) == (1.0, 2.0, 3.0)
    assert coerce_vec3([1.0, float("nan"), 3.0]) is None
    assert coerce_vec3((1.0, 2.0)) is None
    assert coerce_vec3((True, 2.0, 3.0)) is None


def test_slab_interval_axis_parallel_rays() -> None:
    box = (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
    assert slab_interval((0.5, 0.5, -1.0), (math.inf, math.inf, 1.0), *box) == (1.0, 2.0)
    # Parallel and outside: no interval.
    near, far = slab_interval((5.0, 0.5, -1.0), (math.inf, math.inf, 1.0), *box)
    assert near > far
    # Origin exactly on the slab plane (the 0 * inf case) stays inside that axis.
    assert slab_interval((0.0, 0.5, 0.5), (math.inf, math.inf, math.inf), *box) == (-math.inf, math.inf)


def _soup(triangles: list[tuple[tuple[float, float, float], ...]], name: str = "concrete") -> TriangleSoup:
    from array import array

    positions = array("f")
    indices = array("i")
    for triangle in triangles:
        base = len(positions) // 3
        for vertex in triangle:
            positions.extend(vertex)
        indices.extend((base, base + 1, base + 2))
    return TriangleSoup.from_points(positions, indices, [(name, len(triangles))])


def test_grid_matches_brute_force_including_overflow_and_outside_origin() -> None:
    triangles = [
        TRIANGLE,
        ((5.0, 0.0, 0.0), (7.0, 0.0, 0.0), (5.0, 2.0, 0.0)),
        # A single huge triangle spanning the whole grid: it must land in the
        # overflow bucket and still be tested by every query.
        ((-100.0, -100.0, -50.0), (100.0, -100.0, -50.0), (0.0, 100.0, -50.0)),
    ]
    soup = _soup(triangles)
    grid = TriangleGrid.build(soup, cell_size=4.0)
    assert grid.overflow_count == 1  # the spanning triangle is bucketed, not exploded

    rays = [
        ((0.5, 0.5, 5.0), (0.0, 0.0, -1.0)),
        ((1.5, 1.5, 5.0), (0.0, 0.0, -1.0)),
        ((5.5, 0.5, 5.0), (0.0, 0.0, -1.0)),
        ((-50.0, -50.0, 10.0), (0.0, 0.0, -1.0)),
        ((0.0, 0.0, 1.0), (1.0, 1.0, 0.0)),
        ((60.0, 60.0, 0.0), (-1.0, -1.0, 0.0)),  # starts outside the grid bounds
    ]
    for origin, direction in rays:
        length = math.hypot(*direction) * 1000
        unit = normalize(direction)
        assert unit is not None
        assert grid.ray_first(origin, unit, length) == soup.ray_first_linear(origin, unit, length)


def test_grid_candidates_cover_brute_force_hits() -> None:
    soup = _soup([TRIANGLE, ((5.0, 0.0, 0.0), (7.0, 0.0, 0.0), (5.0, 2.0, 0.0))])
    grid = TriangleGrid.build(soup, cell_size=4.0)
    origin, direction = (0.5, 0.5, 5.0), (0.0, 0.0, -1.0)
    expected = soup.ray_first_linear(origin, direction, 100.0)
    assert expected is not None
    index, _ = expected
    box = soup.triangle_bounds(index)
    assert index in set(grid.candidates(box))
    assert grid.candidates(AABB((-1000.0, -1000.0, -1000.0), (-999.0, -999.0, -999.0)))  # empty region still iterable

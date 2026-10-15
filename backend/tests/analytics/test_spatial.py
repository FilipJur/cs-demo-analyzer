"""Authored-fixture behavior tests for :mod:`cs_demo_analyzer.analytics.spatial`.

Scalar helpers are checked directly; pooled helpers run against small in-memory
coordinate fixtures built from ``helpers.state_row``. Units are Hammer world units,
yaw is degrees, and nothing is interpolated.
"""

from __future__ import annotations

import math
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import polars as pl
import pytest

_TESTS_DIR = Path(__file__).resolve().parents[1]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from cs_demo_analyzer.analytics import spatial  # noqa: E402
from cs_demo_analyzer.domain.contracts import AppError  # noqa: E402
from cs_demo_analyzer.domain.tables import SCHEMAS  # noqa: E402
from helpers import DEMO_ID, PLAYER_A, PLAYER_B, PLAYER_C, PLAYER_D, TICK_RATE_HZ, state_row  # noqa: E402

PROFILE_KEY = "foundation-v1:awpy-3.0.0:schema-1:normalizer-1"
GEN_ID = "gen-0000000000000001"


@contextmanager
def raised(code: str):
    """Assert the body raises an :class:`AppError` whose ``code`` matches."""
    with pytest.raises(AppError) as caught:
        yield
    assert caught.value.code == code


def frame(table: str, rows) -> pl.DataFrame:
    if isinstance(rows, pl.DataFrame):
        return rows.select(list(SCHEMAS[table]))
    return pl.DataFrame(rows, schema=SCHEMAS[table], orient="row").select(list(SCHEMAS[table]))


class FakePool:
    def __init__(self, tables: dict):
        self.frames = {name: frame(name, rows) for name, rows in tables.items()}

    def read(self, gen, table, *, columns=None, predicate=None, limit: int = 0) -> pl.DataFrame:
        result = self.frames[table]
        if predicate is not None:
            result = result.filter(predicate)
        if columns is not None:
            result = result.select(list(columns))
        if limit and result.height > limit:
            raise AppError("WINDOW_TOO_LARGE", f"{result.height} > {limit}", "read")
        return result

    def scan(self, gen, table, *, columns=None, predicate=None) -> pl.LazyFrame:
        return self.read(gen, table, columns=columns, predicate=predicate).lazy()


def build(rows):
    tables = {
        "players": [
            {"player_id": PLAYER_A, "steam_id": None, "name": "alpha", "side": "ct"},
            {"player_id": PLAYER_B, "steam_id": None, "name": "bravo", "side": "ct"},
            {"player_id": PLAYER_C, "steam_id": None, "name": "charlie", "side": "t"},
            {"player_id": PLAYER_D, "steam_id": None, "name": "delta", "side": "t"},
        ],
        "rounds": [],
        "player_state": rows,
        "kills": [],
        "damages": [],
        "shots": [],
        "bomb": [],
    }
    pool = FakePool(tables)
    gen = SimpleNamespace(
        demo_id=DEMO_ID,
        generation_id=GEN_ID,
        profile_key=PROFILE_KEY,
        tick_rate_hz=TICK_RATE_HZ,
        rounds=pool.frames["rounds"],
        players=pool.frames["players"],
        dir=None,
        manifest=None,
    )
    return pool, gen


def row(ordinal: int, tick: int, player_id, *, x: float, y: float, z: float = 0.0):
    result = state_row(ordinal, tick, player_id)
    result.update(x=x, y=y, z=z, yaw=0.0, velocity_x=0.0, velocity_y=0.0, velocity_z=0.0)
    return result


# --------------------------------------------------------------------------- #
# scalar helpers
# --------------------------------------------------------------------------- #
def test_dist2d_and_dist3d():
    assert spatial.dist2d(0.0, 0.0, 3.0, 4.0) == 5.0
    assert spatial.dist3d(0.0, 0.0, 0.0, 2.0, 3.0, 6.0) == 7.0
    assert spatial.dist3d(0.0, 0.0, 5.0, 0.0, 0.0, 5.0) == 0.0


def test_speed_and_displacement():
    assert spatial.speed(3.0, 4.0, 0.0) == 5.0
    assert spatial.displacement(0.0, 0.0, 3.0, 4.0) == (3.0, 4.0, 5.0)


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"), float("-inf")])
def test_scalar_helpers_reject_none_and_non_finite(bad):
    assert spatial.dist2d(0.0, 0.0, bad, 0.0) is None
    assert spatial.dist3d(0.0, 0.0, 0.0, bad, 0.0, 0.0) is None
    assert spatial.speed(bad, 0.0, 0.0) is None
    assert spatial.displacement(0.0, 0.0, bad, 0.0) == (None, None, None)
    assert spatial.yaw_diff(bad, 0.0) is None
    assert spatial.yaw_diff(0.0, bad) is None


def test_yaw_diff_shortest_arc_and_wraparound():
    assert spatial.yaw_diff(0.0, 0.0) == 0.0
    assert spatial.yaw_diff(10.0, 20.0) == 10.0
    assert spatial.yaw_diff(170.0, -170.0) == 20.0
    assert spatial.yaw_diff(-170.0, 170.0) == -20.0
    assert spatial.yaw_diff(179.0, -179.0) == 2.0
    assert spatial.yaw_diff(0.0, 180.0) == -180.0
    assert spatial.yaw_diff(0.0, -180.0) == -180.0
    assert spatial.yaw_diff(None, 10.0) is None


# --------------------------------------------------------------------------- #
# pair_distance_over_time
# --------------------------------------------------------------------------- #
def pair_rows():
    # A present at 100, 101, 103; B present at 100, 102, 103.
    return [
        row(0, 100, PLAYER_A, x=0.0, y=0.0),
        row(1, 100, PLAYER_B, x=0.0, y=100.0),
        row(2, 101, PLAYER_A, x=0.0, y=10.0),
        row(3, 102, PLAYER_B, x=0.0, y=200.0),
        row(4, 103, PLAYER_A, x=0.0, y=30.0),
        row(5, 103, PLAYER_B, x=0.0, y=330.0),
    ]


def test_pair_distance_exact_ticks_only():
    pool, gen = build(pair_rows())
    result = spatial.pair_distance_over_time(pool, gen, PLAYER_A, PLAYER_B, [100, 101, 102, 103])
    assert [entry["tick"] for entry in result] == [100, 101, 102, 103]
    assert [entry["missing"] for entry in result] == [False, True, True, False]
    assert result[0]["d2d"] == 100.0
    assert result[3]["d2d"] == 300.0
    assert result[1]["d2d"] is None and result[2]["d3d"] is None


def test_pair_distance_preserves_input_order_and_duplicates():
    pool, gen = build(pair_rows())
    result = spatial.pair_distance_over_time(pool, gen, PLAYER_A, PLAYER_B, [103, 100, 103])
    assert [entry["tick"] for entry in result] == [103, 100, 103]
    assert result[0]["d2d"] == result[2]["d2d"] == 300.0


def test_pair_distance_caps_and_empty():
    pool, gen = build(pair_rows())
    with raised("INVALID_ARGUMENT"):
        spatial.pair_distance_over_time(pool, gen, PLAYER_A, PLAYER_B, [])
    with raised("INVALID_ARGUMENT"):
        spatial.pair_distance_over_time(pool, gen, PLAYER_A, PLAYER_B, list(range(10_001)))


# --------------------------------------------------------------------------- #
# nearby
# --------------------------------------------------------------------------- #
def nearby_rows():
    return [
        row(0, 200, PLAYER_A, x=0.0, y=0.0),
        row(1, 200, PLAYER_B, x=300.0, y=0.0),
        row(2, 200, PLAYER_C, x=500.0, y=0.0),
        row(3, 200, PLAYER_D, x=1000.0, y=0.0),
    ]


def test_nearby_radius_filter_and_sort():
    pool, gen = build(nearby_rows())
    result = spatial.nearby(pool, gen, 200, PLAYER_A, 400.0)
    assert [entry["player_id"] for entry in result] == [PLAYER_B]
    assert result[0]["d2d"] == 300.0

    wide = spatial.nearby(pool, gen, 200, PLAYER_A, 1200.0)
    assert [entry["player_id"] for entry in wide] == [PLAYER_B, PLAYER_C, PLAYER_D]
    assert [entry["d2d"] for entry in wide] == [300.0, 500.0, 1000.0]


def test_nearby_absent_reference_returns_empty():
    pool, gen = build(nearby_rows())
    assert spatial.nearby(pool, gen, 201, PLAYER_A, 1000.0) == []


@pytest.mark.parametrize("radius", [0.0, -1.0, float("inf"), float("nan")])
def test_nearby_rejects_bad_radius(radius):
    pool, gen = build(nearby_rows())
    with raised("INVALID_ARGUMENT"):
        spatial.nearby(pool, gen, 200, PLAYER_A, radius)


def test_nearby_skips_non_finite_coordinates():
    rows = nearby_rows() + [row(4, 200, PLAYER_D, x=float("nan"), y=0.0)]
    pool, gen = build(rows)
    result = spatial.nearby(pool, gen, 200, PLAYER_A, 2000.0)
    assert [entry["player_id"] for entry in result] == [PLAYER_B, PLAYER_C]


# --------------------------------------------------------------------------- #
# time_within
# --------------------------------------------------------------------------- #
def time_within_rows():
    return [
        row(0, 100, PLAYER_A, x=0.0, y=0.0),
        row(1, 100, PLAYER_B, x=0.0, y=100.0),
        row(2, 101, PLAYER_A, x=0.0, y=0.0),
        row(3, 101, PLAYER_B, x=0.0, y=200.0),
        row(4, 102, PLAYER_A, x=0.0, y=0.0),
        row(5, 102, PLAYER_B, x=0.0, y=300.0),
        row(6, 103, PLAYER_A, x=0.0, y=0.0),
        row(7, 103, PLAYER_B, x=0.0, y=400.0),
    ]


def test_time_within_fraction():
    pool, gen = build(time_within_rows())
    result = spatial.time_within(pool, gen, PLAYER_A, PLAYER_B, 100, 103, 250.0)
    assert result == {"ticks_compared": 4, "ticks_within": 2, "fraction": 0.5}


def test_time_within_no_overlap_is_none():
    rows = [
        row(0, 100, PLAYER_A, x=0.0, y=0.0),
        row(1, 200, PLAYER_B, x=0.0, y=0.0),
    ]
    pool, gen = build(rows)
    result = spatial.time_within(pool, gen, PLAYER_A, PLAYER_B, 100, 200, 50.0)
    assert result == {"ticks_compared": 0, "ticks_within": 0, "fraction": None}


def test_time_within_rejects_bad_radius():
    pool, gen = build(time_within_rows())
    with raised("INVALID_ARGUMENT"):
        spatial.time_within(pool, gen, PLAYER_A, PLAYER_B, 100, 103, 0.0)


def test_time_within_ignores_non_finite_coordinates():
    rows = time_within_rows()
    rows[5] = row(5, 102, PLAYER_B, x=float("nan"), y=300.0)
    pool, gen = build(rows)
    result = spatial.time_within(pool, gen, PLAYER_A, PLAYER_B, 100, 103, 250.0)
    assert result == {"ticks_compared": 3, "ticks_within": 2, "fraction": 2 / 3}

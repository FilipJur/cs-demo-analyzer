"""Authored-fixture behavior tests for :mod:`cs_demo_analyzer.analytics.temporal`.

Fixtures are built locally (a tiny in-memory pool plus the round-one tables from
``helpers``) so the temporal module is exercised without a real demo, catalog or
parquet files. Nothing here interpolates: every assertion checks verbatim rows.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import polars as pl
import pytest

# Make ``helpers`` importable when pytest roots this file under tests/analytics/.
_TESTS_DIR = Path(__file__).resolve().parents[1]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from cs_demo_analyzer.analytics import temporal  # noqa: E402
from cs_demo_analyzer.domain.contracts import AppError  # noqa: E402
from cs_demo_analyzer.domain.tables import SCHEMAS  # noqa: E402
from helpers import (  # noqa: E402
    DEMO_ID,
    PLAYER_A,
    PLAYER_B,
    PLAYER_C,
    PLAYER_D,
    PLAYER_IDS,
    TICK_RATE_HZ,
    inferno_tables,
    state_row,
)

PROFILE_KEY = "foundation-v1:awpy-3.0.0:schema-1:normalizer-1"
GEN_ID = "gen-0000000000000001"


# --------------------------------------------------------------------------- #
# harness: in-memory pool + duck-typed generation
# --------------------------------------------------------------------------- #
def frame(table: str, rows) -> pl.DataFrame:
    if isinstance(rows, pl.DataFrame):
        return rows.select(list(SCHEMAS[table]))
    return pl.DataFrame(rows, schema=SCHEMAS[table], orient="row").select(list(SCHEMAS[table]))


class FakePool:
    """Minimal ``GenerationPool`` surface: bounded reads over eager frames."""

    def __init__(self, tables: dict):
        self.frames = {name: frame(name, rows) for name, rows in tables.items()}

    def read(self, gen, table, *, columns=None, predicate=None, limit: int = 0) -> pl.DataFrame:
        assert table in SCHEMAS, f"unknown table {table}"
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


def generation(pool: FakePool):
    return SimpleNamespace(
        demo_id=DEMO_ID,
        generation_id=GEN_ID,
        profile_key=PROFILE_KEY,
        tick_rate_hz=TICK_RATE_HZ,
        rounds=pool.frames["rounds"],
        players=pool.frames["players"],
        dir=None,
        manifest=None,
    )


def build(rows=None):
    tables = inferno_tables()
    if rows is not None:
        tables["player_state"] = rows
    pool = FakePool(tables)
    return pool, generation(pool)


def temporal_rows():
    """Round-one rows with a two-tick hole for PLAYER_A and off-grid kill rows."""
    rows: list[dict] = []
    ordinal = 0

    def add(tick: int, player_id, **overrides) -> None:
        nonlocal ordinal
        row = state_row(ordinal, tick, player_id)
        row.update(overrides)
        rows.append(row)
        ordinal += 1

    for tick in range(1200, 1241, 8):  # 1200..1240 aligned grid
        for player_id in PLAYER_IDS:
            if player_id == PLAYER_A and tick in (1208, 1216):
                continue
            add(tick, player_id)
    add(1252, PLAYER_A)
    add(1253, PLAYER_A)
    add(1253, PLAYER_B)
    add(1252, None)  # dead entity: observable, never joined by position/name
    return rows


@contextmanager
def raised(code: str):
    """Assert the body raises an :class:`AppError` whose ``code`` matches."""
    with pytest.raises(AppError) as caught:
        yield
    assert caught.value.code == code


# --------------------------------------------------------------------------- #
# state_at
# --------------------------------------------------------------------------- #
def test_state_at_exact_tick_returns_verbatim_rows():
    pool, gen = build(temporal_rows())
    result = temporal.state_at(pool, gen, 1200)
    assert result["exact"] is True
    assert result["actual_tick"] == 1200
    assert result["gap"] == 0
    assert len(result["states"]) == len(PLAYER_IDS)
    assert {row["player_id"] for row in result["states"]} == set(PLAYER_IDS)
    # Verbatim: identical to the raw table rows for that tick.
    raw = pool.frames["player_state"].filter(pl.col("tick") == 1200).sort("row_ordinal")
    assert result["states"] == raw.to_dicts()


def test_state_at_player_filter_exact():
    pool, gen = build(temporal_rows())
    result = temporal.state_at(pool, gen, 1200, player_id=PLAYER_A)
    assert result["exact"] is True
    assert [row["player_id"] for row in result["states"]] == [PLAYER_A]


def test_state_at_missing_player_exact_is_none():
    pool, gen = build(temporal_rows())
    result = temporal.state_at(pool, gen, 1208, player_id=PLAYER_A, max_gap=0)
    assert result == {"actual_tick": None, "gap": None, "exact": False, "states": []}


def test_state_at_nearest_within_gap_and_signed_gap():
    pool, gen = build(temporal_rows())
    result = temporal.state_at(pool, gen, 1204, max_gap=4)
    # 1200 and 1208 are equidistant; the earlier tick wins the tie.
    assert result["actual_tick"] == 1200
    assert result["gap"] == -4
    assert result["exact"] is False
    assert len(result["states"]) == len(PLAYER_IDS)


def test_state_at_gap_zero_reports_none():
    pool, gen = build(temporal_rows())
    result = temporal.state_at(pool, gen, 1204, max_gap=0)
    assert result["actual_tick"] is None
    assert result["states"] == []


def test_state_at_outside_window_is_none():
    pool, gen = build(temporal_rows())
    assert temporal.state_at(pool, gen, 999, max_gap=5)["actual_tick"] is None


def test_state_at_player_filtered_nearest():
    pool, gen = build(temporal_rows())
    result = temporal.state_at(pool, gen, 1251, player_id=PLAYER_A, max_gap=8)
    assert result["actual_tick"] == 1252
    assert result["gap"] == 1
    assert [row["player_id"] for row in result["states"]] == [PLAYER_A]


def test_state_at_rejects_negative_tick_and_gap():
    pool, gen = build(temporal_rows())
    with raised("INVALID_ARGUMENT"):
        temporal.state_at(pool, gen, -1)
    with raised("INVALID_ARGUMENT"):
        temporal.state_at(pool, gen, 1200, max_gap=-1)


# --------------------------------------------------------------------------- #
# player_interval
# --------------------------------------------------------------------------- #
def test_player_interval_reports_coalesced_missing_ranges():
    pool, gen = build(temporal_rows())
    result = temporal.player_interval(pool, gen, PLAYER_A, 1200, 1240, stride=8)
    assert [row["tick"] for row in result["states"]] == [1200, 1224, 1232, 1240]
    assert result["missing_ranges"] == [[1208, 1216]]


def test_player_interval_complete_grid_has_no_missing():
    pool, gen = build(temporal_rows())
    result = temporal.player_interval(pool, gen, PLAYER_B, 1200, 1240, stride=8)
    assert result["missing_ranges"] == []
    assert len(result["states"]) == 6


def test_player_interval_argument_validation():
    pool, gen = build(temporal_rows())
    with raised("INVALID_ARGUMENT"):
        temporal.player_interval(pool, gen, "", 1200, 1240)
    with raised("INVALID_ARGUMENT"):
        temporal.player_interval(pool, gen, PLAYER_A, 1240, 1200)
    with raised("INVALID_ARGUMENT"):
        temporal.player_interval(pool, gen, PLAYER_A, 1200, 1240, stride=0)
    with raised("INVALID_ARGUMENT"):
        temporal.player_interval(pool, gen, PLAYER_A, 1200, 1240, stride=4097)


# --------------------------------------------------------------------------- #
# events_in / timeline
# --------------------------------------------------------------------------- #
def test_events_in_orders_and_maps_actors():
    pool, gen = build(temporal_rows())
    events = temporal.events_in(pool, gen, ["kills", "damages", "shots", "bomb"], 1252, 1350, limit=100)
    # 1252: kills, damages, shots (dataset tie-break); then 1300 kill, 1310 bomb, 1350 kill+damage.
    assert [(e["tick"], e["dataset"], e["row_ordinal"]) for e in events] == [
        (1252, "kills", 0),
        (1252, "damages", 0),
        (1252, "shots", 0),
        (1300, "kills", 1),
        (1310, "bomb", 0),
        (1350, "kills", 2),
        (1350, "damages", 1),
    ]
    first = events[0]
    assert (first["actor1"], first["actor2"], first["detail"]) == (PLAYER_A, PLAYER_B, "ak47")
    damages = next(e for e in events if e["dataset"] == "damages")
    assert damages["detail"] == "27"  # damage_health rendered as text
    bomb = next(e for e in events if e["dataset"] == "bomb")
    assert (bomb["actor1"], bomb["actor2"], bomb["detail"]) == (PLAYER_C, None, "planted")
    shots = next(e for e in events if e["dataset"] == "shots")
    assert (shots["actor1"], shots["actor2"]) == (PLAYER_A, None)


def test_events_in_limit_truncates():
    pool, gen = build(temporal_rows())
    assert len(temporal.events_in(pool, gen, ["kills", "damages", "shots", "bomb"], 1252, 1350, limit=3)) == 3


def test_events_in_validation():
    pool, gen = build(temporal_rows())
    with raised("INVALID_ARGUMENT"):
        temporal.events_in(pool, gen, ["nope"], 0, 100)
    with raised("INVALID_ARGUMENT"):
        temporal.events_in(pool, gen, ["kills"], 0, 100, limit=5001)


def test_events_in_empty_range_is_empty():
    pool, gen = build(temporal_rows())
    assert temporal.events_in(pool, gen, ["kills"], 2000, 1999) == []


def test_timeline_defaults_to_all_datasets():
    pool, gen = build(temporal_rows())
    assert len(temporal.timeline(pool, gen, None, 1252, 1252)) == 3
    assert [e["dataset"] for e in temporal.timeline(pool, gen, ["kills"], 1252, 1252)] == ["kills"]


# --------------------------------------------------------------------------- #
# events_around
# --------------------------------------------------------------------------- #
def test_events_around_nearest_strictly_before_and_after():
    pool, gen = build(temporal_rows())
    result = temporal.events_around(pool, gen, 1252, 2, 2, ["kills", "damages", "shots", "bomb"])
    assert result["before"] == []  # nothing strictly before the first event
    assert [(e["tick"], e["dataset"]) for e in result["after"]] == [(1300, "kills"), (1310, "bomb")]


def test_events_around_picks_nearest_before():
    pool, gen = build(temporal_rows())
    result = temporal.events_around(pool, gen, 1350, 3, 1, ["kills", "damages", "shots", "bomb"])
    assert [(e["tick"], e["dataset"]) for e in result["before"]] == [
        (1252, "shots"),
        (1300, "kills"),
        (1310, "bomb"),
    ]
    assert [(e["tick"], e["dataset"]) for e in result["after"]] == [(1450, "kills")]


def test_events_around_count_validation():
    pool, gen = build(temporal_rows())
    with raised("INVALID_ARGUMENT"):
        temporal.events_around(pool, gen, 1252, 101, 0, ["kills"])
    with raised("INVALID_ARGUMENT"):
        temporal.events_around(pool, gen, 1252, 0, -1, ["kills"])


# --------------------------------------------------------------------------- #
# event_window
# --------------------------------------------------------------------------- #
def test_event_window_scopes_states_and_nearby_events():
    pool, gen = build(temporal_rows())
    result = temporal.event_window(pool, gen, "kills", 0, 52, 0)
    assert result["event"]["tick"] == 1252
    assert {row["player_id"] for row in result["states"]} == {PLAYER_A, PLAYER_B}
    assert len(result["states"]) == 11  # 5 A rows + 6 B rows in [1200, 1252]
    assert all(row["player_id"] is not None for row in result["states"])
    assert [(e["tick"], e["dataset"]) for e in result["nearby_events"]] == [
        (1252, "kills"),
        (1252, "damages"),
        (1252, "shots"),
    ]


def test_event_window_unknown_row_is_not_found():
    pool, gen = build(temporal_rows())
    with raised("NOT_FOUND"):
        temporal.event_window(pool, gen, "kills", 999, 10, 10)


def test_event_window_validation():
    pool, gen = build(temporal_rows())
    with raised("INVALID_ARGUMENT"):
        temporal.event_window(pool, gen, "nope", 0, 10, 10)
    with raised("INVALID_ARGUMENT"):
        temporal.event_window(pool, gen, "kills", 0, 64001, 10)


# --------------------------------------------------------------------------- #
# rounds and clock
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("tick", "expected"),
    [(1000, None), (1200, 1), (1252, 1), (1400, 1), (1401, None), (1450, None), (1700, 2), (1900, 2), (1901, None), (1500, None)],
)
def test_round_of_boundaries(tick, expected):
    pool, gen = build(temporal_rows())
    assert temporal.round_of(pool, gen, tick) == expected


def test_round_window_and_errors():
    pool, gen = build(temporal_rows())
    assert temporal.round_window(pool, gen, 1) == (1200, 1400)
    assert temporal.round_window(pool, gen, 2) == (1700, 1900)
    with raised("PARTIAL_ROUND"):
        temporal.round_window(pool, gen, 3)
    with raised("NOT_FOUND"):
        temporal.round_window(pool, gen, 99)


def test_tick_to_seconds():
    pool, gen = build(temporal_rows())
    assert temporal.tick_to_seconds(pool, gen, 64) == 1.0
    assert temporal.tick_to_seconds(pool, gen, 32) == 0.5


def test_evidence_ref_fields():
    pool, gen = build(temporal_rows())
    ref = temporal.evidence_ref(gen, "kills", 0, 1252, 1, [PLAYER_A, PLAYER_B])
    assert ref.demo_id == DEMO_ID
    assert ref.generation_id == GEN_ID
    assert ref.profile_key == PROFILE_KEY
    assert (ref.dataset, ref.row_ordinal, ref.tick, ref.round_id) == ("kills", 0, 1252, 1)
    assert ref.player_ids == [PLAYER_A, PLAYER_B]

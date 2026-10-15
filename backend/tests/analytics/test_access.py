"""Access behavior: generation pinning, artifact errors, column validation and caps.

Every generation here is published through the real storage path, so these tests
fail if the analytics layer stops agreeing with the catalog/artifact contract.
"""

from __future__ import annotations

import json
import shutil

import polars as pl
import pytest

from cs_demo_analyzer.analytics import MAX_MATERIALIZED_ROWS, Generation, GenerationPool
from cs_demo_analyzer.domain.contracts import PROFILE_KEY, AppError, ErrorResponse
from cs_demo_analyzer.domain.tables import SCHEMAS

from .fixtures import (  # noqa: F401 - `harness` is imported so pytest registers the fixture
    DEMO_ID,
    OTHER_DEMO_ID,
    PLAYER_A,
    PLAYER_B,
    TICK_RATE_HZ,
    AnalyticsHarness,
    dense_state,
    harness,
    players_rows,
    round_row,
    state_row,
)

ROUND_ONE = round_row(1, start=100, freeze_end=120, end=200, official_end=216)


def _tiny_tables(*, players: int = 1, states: list[dict] | None = None) -> dict:
    roster = players_rows(PLAYER_A, PLAYER_B)[:players]
    return {
        "rounds": [ROUND_ONE],
        "players": roster,
        "player_state": states if states is not None else [state_row(0, 100, PLAYER_A)],
    }


# -- opening / pinning ------------------------------------------------------
def test_open_defaults_to_head_with_eager_tables(harness: AnalyticsHarness) -> None:
    manifest = harness.publish(tables=_tiny_tables(players=2))

    gen = harness.open()

    assert isinstance(gen, Generation)
    assert gen.demo_id == DEMO_ID
    assert gen.generation_id == manifest.generation_id
    assert gen.profile_key == PROFILE_KEY
    assert gen.tick_rate_hz == TICK_RATE_HZ
    assert gen.dir == harness.generation_dir(manifest.generation_id)
    assert gen.manifest.generation_id == manifest.generation_id
    assert gen.rounds.columns == list(SCHEMAS["rounds"])
    assert gen.rounds.get_column("round_id").to_list() == [1]
    assert gen.players.columns == list(SCHEMAS["players"])
    assert gen.players.height == 2


def test_open_pins_explicit_generation_after_head_moves(harness: AnalyticsHarness) -> None:
    first = harness.publish(demo_id=DEMO_ID, tables=_tiny_tables(players=1))
    second = harness.publish(
        demo_id=DEMO_ID,
        tables={
            "rounds": [ROUND_ONE, round_row(2, start=300, freeze_end=320, end=400)],
            "players": players_rows(PLAYER_A, PLAYER_B),
            "player_state": [state_row(0, 300, PLAYER_B)],
        },
    )
    assert first.generation_id != second.generation_id  # each publish is its own revision

    head = harness.open()
    pinned = harness.open(first.generation_id)

    assert head.generation_id == second.generation_id
    assert head.players.height == 2
    assert pinned.generation_id == first.generation_id
    assert pinned.dir == harness.generation_dir(first.generation_id)
    assert pinned.players.height == 1
    assert pinned.rounds.height == 1
    assert pinned.manifest.generation_id == first.generation_id


def test_open_default_on_unknown_demo_is_not_found(harness: AnalyticsHarness) -> None:
    with pytest.raises(AppError) as caught:
        harness.pool.open(DEMO_ID)

    assert caught.value.code == "NOT_FOUND"
    assert caught.value.stage == "read"
    assert DEMO_ID in caught.value.message


def test_open_demo_without_generation_is_not_ready(harness: AnalyticsHarness) -> None:
    harness.register(DEMO_ID)

    with pytest.raises(AppError) as caught:
        harness.pool.open(DEMO_ID)

    assert caught.value.code == "NOT_READY"
    assert caught.value.stage == "read"


def test_open_requested_generation_that_was_never_published_is_unavailable(
    harness: AnalyticsHarness,
) -> None:
    harness.publish(tables=_tiny_tables())
    missing = "f" * 32

    with pytest.raises(AppError) as caught:
        harness.open(missing)

    assert caught.value.code == "GENERATION_UNAVAILABLE"
    assert caught.value.stage == "read"
    assert missing in caught.value.message


def test_open_generation_whose_artifacts_are_gone_is_unavailable(harness: AnalyticsHarness) -> None:
    manifest = harness.publish(tables=_tiny_tables())
    shutil.rmtree(harness.generation_dir(manifest.generation_id))

    with pytest.raises(AppError) as caught:
        harness.open(manifest.generation_id)

    assert caught.value.code == "GENERATION_UNAVAILABLE"


def test_open_generation_with_a_missing_table_file_is_artifact_invalid(harness: AnalyticsHarness) -> None:
    manifest = harness.publish(tables=_tiny_tables())
    (harness.generation_dir(manifest.generation_id) / "kills.parquet").unlink()

    with pytest.raises(AppError) as caught:
        harness.open(manifest.generation_id)

    assert caught.value.code == "ARTIFACT_INVALID"
    assert caught.value.stage == "read"
    assert "kills" in caught.value.message


def test_open_generation_with_an_unparseable_manifest_is_artifact_invalid(harness: AnalyticsHarness) -> None:
    manifest = harness.publish(tables=_tiny_tables())
    harness.manifest_path(manifest.generation_id).write_text("{ not a manifest")

    with pytest.raises(AppError) as caught:
        harness.open(manifest.generation_id)

    assert caught.value.code == "ARTIFACT_INVALID"


def test_open_generation_with_a_mismatched_manifest_identity_is_artifact_invalid(
    harness: AnalyticsHarness,
) -> None:
    manifest = harness.publish(tables=_tiny_tables())
    path = harness.manifest_path(manifest.generation_id)
    document = json.loads(path.read_text())

    document["generation_id"] = "0" * 32
    path.write_text(json.dumps(document))
    with pytest.raises(AppError) as caught:
        harness.open(manifest.generation_id)
    assert caught.value.code == "ARTIFACT_INVALID"
    assert "manifest identity" in caught.value.message
    assert "0" * 32 in caught.value.message

    document["generation_id"] = manifest.generation_id
    document["demo_id"] = OTHER_DEMO_ID
    path.write_text(json.dumps(document))
    with pytest.raises(AppError) as caught:
        harness.open(manifest.generation_id)
    assert caught.value.code == "ARTIFACT_INVALID"
    assert OTHER_DEMO_ID in caught.value.message


# -- scan -------------------------------------------------------------------
def test_scan_rejects_unknown_tables(harness: AnalyticsHarness) -> None:
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables()).generation_id)

    with pytest.raises(AppError) as caught:
        harness.pool.scan(gen, "no_such_table")

    assert caught.value.code == "INVALID_ARGUMENT"
    assert caught.value.stage == "read"


def test_scan_rejects_unknown_columns(harness: AnalyticsHarness) -> None:
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables()).generation_id)

    with pytest.raises(AppError) as caught:
        harness.pool.scan(gen, "player_state", columns=["tick", "nope"])

    assert caught.value.code == "INVALID_ARGUMENT"
    assert "nope" in caught.value.message


def test_scan_rejects_non_expression_predicates(harness: AnalyticsHarness) -> None:
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables()).generation_id)

    with pytest.raises(AppError) as caught:
        harness.pool.scan(gen, "player_state", predicate="tick > 0")

    assert caught.value.code == "INVALID_ARGUMENT"


def test_scan_filters_before_projecting(harness: AnalyticsHarness) -> None:
    states = [state_row(0, 100, PLAYER_A), state_row(1, 100, PLAYER_B), state_row(2, 120, PLAYER_A)]
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables(players=2, states=states)).generation_id)

    frame_ = harness.pool.scan(
        gen, "player_state", columns=["tick"], predicate=pl.col("player_id") == PLAYER_A
    ).collect()

    assert frame_.columns == ["tick"]
    assert frame_.get_column("tick").to_list() == [100, 120]


def test_scan_applies_predicate_and_projection_as_a_lazy_frame(harness: AnalyticsHarness) -> None:
    states = [state_row(0, 100, PLAYER_A), state_row(1, 150, PLAYER_A)]
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables(states=states)).generation_id)

    lazy = harness.pool.scan(gen, "player_state", columns=["tick", "player_id"], predicate=pl.col("tick") >= 150)

    assert isinstance(lazy, pl.LazyFrame)
    assert lazy.collect().rows(named=True) == [{"tick": 150, "player_id": PLAYER_A}]


# -- read caps --------------------------------------------------------------
def test_read_rejects_windows_above_the_limit(harness: AnalyticsHarness) -> None:
    states = [state_row(index, 100 + index, PLAYER_A) for index in range(5)]
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables(states=states)).generation_id)

    with pytest.raises(AppError) as caught:
        harness.pool.read(gen, "player_state", limit=4)

    assert caught.value.code == "WINDOW_TOO_LARGE"
    assert caught.value.stage == "read"
    assert "5" in caught.value.message


def test_read_allows_the_exact_limit_boundary(harness: AnalyticsHarness) -> None:
    states = [state_row(index, 100 + index, PLAYER_A) for index in range(5)]
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables(states=states)).generation_id)

    assert harness.pool.read(gen, "player_state", limit=5).height == 5
    assert harness.pool.read(gen, "player_state", limit=6).height == 5
    assert harness.pool.read(gen, "player_state", columns=["tick"], limit=5).columns == ["tick"]


def test_read_counts_only_the_filtered_window(harness: AnalyticsHarness) -> None:
    states = [state_row(index, 100 + index, PLAYER_A) for index in range(10)]
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables(states=states)).generation_id)

    selected = harness.pool.read(gen, "player_state", predicate=pl.col("tick") < 103, limit=3)

    assert selected.height == 3
    with pytest.raises(AppError) as caught:
        harness.pool.read(gen, "player_state", predicate=pl.col("tick") < 103, limit=2)
    assert caught.value.code == "WINDOW_TOO_LARGE"


def test_read_rejects_a_non_positive_limit(harness: AnalyticsHarness) -> None:
    gen = harness.open(generation_id=harness.publish(tables=_tiny_tables()).generation_id)

    with pytest.raises(AppError) as caught:
        harness.pool.read(gen, "player_state", limit=0)

    assert caught.value.code == "INVALID_ARGUMENT"


def test_read_default_cap_is_max_materialized_rows(harness: AnalyticsHarness) -> None:
    assert MAX_MATERIALIZED_ROWS == 120_000
    height = MAX_MATERIALIZED_ROWS + 1
    tables = _tiny_tables()
    tables["player_state"] = dense_state(height, tick_offset=100)
    gen = harness.open(generation_id=harness.publish(tables=tables).generation_id)

    with pytest.raises(AppError) as caught:
        harness.pool.read(gen, "player_state")

    assert caught.value.code == "WINDOW_TOO_LARGE"
    assert str(height) in caught.value.message
    assert harness.pool.read(gen, "player_state", limit=height).height == height


# -- query_many -------------------------------------------------------------
def test_query_many_captures_open_failures_per_demo(harness: AnalyticsHarness) -> None:
    manifest = harness.publish(demo_id=DEMO_ID, tables=_tiny_tables(players=2))
    unpublished = "f" * 32

    results = harness.pool.query_many(
        [(DEMO_ID, None), (OTHER_DEMO_ID, None), (DEMO_ID, unpublished)],
        lambda gen: gen.players.height,
    )

    assert [entry["demo_id"] for entry in results] == [DEMO_ID, OTHER_DEMO_ID, DEMO_ID]
    assert results[0]["result"] == 2
    assert results[0]["generation_id"] == manifest.generation_id
    assert results[0]["error"] is None

    assert results[1]["result"] is None
    assert results[1]["generation_id"] is None
    assert isinstance(results[1]["error"], ErrorResponse)
    assert results[1]["error"].code == "NOT_FOUND"
    assert results[1]["error"].stage == "read"

    assert results[2]["result"] is None
    assert results[2]["generation_id"] == unpublished
    assert results[2]["error"].code == "GENERATION_UNAVAILABLE"


def test_query_many_isolates_callback_failures(harness: AnalyticsHarness) -> None:
    harness.publish(demo_id=DEMO_ID, tables=_tiny_tables())
    harness.publish(demo_id=OTHER_DEMO_ID, tables=_tiny_tables())

    def failing(gen: Generation) -> int:
        if gen.demo_id == OTHER_DEMO_ID:
            raise AppError("WINDOW_TOO_LARGE", "callback refused the window", "analytics")
        return gen.players.height

    results = harness.pool.query_many([(DEMO_ID, None), (OTHER_DEMO_ID, None)], failing)

    assert results[0]["result"] == 1
    assert results[0]["error"] is None
    assert results[1]["result"] is None
    assert results[1]["error"].code == "WINDOW_TOO_LARGE"
    assert results[1]["error"].stage == "analytics"
    assert results[1]["error"].message == "callback refused the window"
    assert results[1]["generation_id"] is not None  # the resolved generation is still reported


def test_query_many_wraps_untyped_callback_errors(harness: AnalyticsHarness) -> None:
    manifest = harness.publish(tables=_tiny_tables())

    def broken(gen: Generation) -> int:
        raise ValueError("boom")

    [entry] = harness.pool.query_many([(DEMO_ID, None)], broken)

    assert entry["result"] is None
    assert entry["generation_id"] == manifest.generation_id
    assert entry["error"].code == "INTERNAL_ERROR"
    assert entry["error"].stage == "analytics"
    assert "boom" in entry["error"].message


def test_query_many_with_no_selections_returns_nothing(harness: AnalyticsHarness) -> None:
    assert harness.pool.query_many([], lambda gen: gen.demo_id) == []


def test_query_many_never_raises_for_an_empty_generation(harness: AnalyticsHarness) -> None:
    """An empty-player generation still opens: only its result is empty."""
    manifest = harness.publish(tables={"players": [], "rounds": [], "player_state": []})

    [entry] = harness.pool.query_many([(DEMO_ID, manifest.generation_id)], lambda gen: gen.players.height)

    assert entry == {
        "demo_id": DEMO_ID,
        "generation_id": manifest.generation_id,
        "result": 0,
        "error": None,
    }


def test_pool_bound_to_its_own_catalog_and_artifacts(harness: AnalyticsHarness) -> None:
    manifest = harness.publish(demo_id=OTHER_DEMO_ID, tables=_tiny_tables())
    pool = GenerationPool(harness.catalog, harness.artifacts)

    gen = pool.open(OTHER_DEMO_ID)

    assert gen.generation_id == manifest.generation_id
    assert pool.read(gen, "players").height == 1

"""Identity coverage and the null-player-id dead-entity rule.

The rule under test: rows with a null ``player_id`` are real observations of dead
entities — counted in totals, never alive, never re-attached to a player by
position, name or ordering.
"""

from __future__ import annotations

import pytest

from cs_demo_analyzer.analytics import GenerationPool, coverage, live_identity_violations
from cs_demo_analyzer.domain.contracts import AppError, IdentityCoverage

from .fixtures import (  # noqa: F401 - `harness` is imported so pytest registers the fixture
    DEMO_ID,
    PLAYER_A,
    PLAYER_B,
    AnalyticsHarness,
    harness,
    players_rows,
    round_row,
    state_row,
)

ROUND_ONE = round_row(1, start=100, freeze_end=100, end=104)


def _publish(harness: AnalyticsHarness, states: list[dict], rounds: list[dict] | None = None) -> None:
    harness.publish(
        tables={
            "player_state": states,
            "rounds": rounds if rounds is not None else [ROUND_ONE],
            "players": players_rows(PLAYER_A, PLAYER_B),
        }
    )


def _generation(harness: AnalyticsHarness, states: list[dict], rounds: list[dict] | None = None):
    _publish(harness, states, rounds)
    return harness.open()


# -- coverage math ----------------------------------------------------------
def test_coverage_counts_corpses_but_measures_live_identity(harness: AnalyticsHarness) -> None:
    gen = _generation(
        harness,
        [
            state_row(0, 100, PLAYER_A),
            state_row(1, 100, PLAYER_B),
            state_row(2, 100, None),  # dead entity at its death position
            state_row(3, 101, PLAYER_A),
            state_row(4, 101, None),
        ],
    )

    result = coverage(harness.pool, gen)

    assert isinstance(result, IdentityCoverage)
    assert result.total_observations == 5
    assert result.identified == 3
    assert result.null_observations == 2
    assert result.alive_total == 3
    assert result.alive_identified == 3
    assert result.alive_null == 0
    assert result.live_coverage == 1.0
    assert "null observations 2" in result.notes[0]
    assert "all health==0" in result.notes[0]
    assert "dead entities" in result.notes[0]
    assert result.notes[-1].startswith("scope generation:")


def test_coverage_of_a_fully_identified_generation_is_complete(harness: AnalyticsHarness) -> None:
    gen = _generation(harness, [state_row(index, 100 + index, PLAYER_A) for index in range(3)])

    result = coverage(harness.pool, gen)

    assert result.total_observations == 3
    assert result.null_observations == 0
    assert result.identified == 3
    assert result.alive_total == 3
    assert result.alive_null == 0
    assert result.live_coverage == 1.0
    assert result.notes[0] == "no null observations: every state row carries an identified player id"
    assert live_identity_violations(harness.pool, gen) == []


def test_coverage_of_a_generation_without_living_rows_has_no_ratio(harness: AnalyticsHarness) -> None:
    gen = _generation(harness, [state_row(0, 100, None), state_row(1, 101, None)])

    result = coverage(harness.pool, gen)

    assert result.total_observations == 2
    assert result.null_observations == 2
    assert result.identified == 0
    assert result.alive_total == 0
    assert result.alive_identified == 0
    assert result.alive_null == 0
    assert result.live_coverage is None
    assert "dead entities" in result.notes[0]


def test_coverage_of_an_empty_generation_is_zeroed(harness: AnalyticsHarness) -> None:
    gen = _generation(harness, [])

    result = coverage(harness.pool, gen)

    assert result.total_observations == 0
    assert result.null_observations == 0
    assert result.alive_total == 0
    assert result.live_coverage is None


# -- the violation case -----------------------------------------------------
def test_alive_null_rows_are_reported_as_violations_and_lower_live_coverage(
    harness: AnalyticsHarness,
) -> None:
    gen = _generation(
        harness,
        [
            state_row(0, 500, PLAYER_A),
            state_row(1, 500, None, health=100),  # alive but unidentified
            state_row(2, 500, None, health=100),  # second violation on the same tick
            state_row(3, 500, None),  # genuine corpse
            state_row(4, 500, PLAYER_B),
        ],
    )

    result = coverage(harness.pool, gen)

    assert result.total_observations == 5
    assert result.null_observations == 3
    assert result.alive_total == 4  # one corpse plus four living rows
    assert result.alive_identified == 2
    assert result.alive_null == 2
    assert result.live_coverage == pytest.approx(0.5)
    assert any("dead-entity rule violated" in note for note in result.notes)
    assert live_identity_violations(harness.pool, gen) == [500]  # distinct ticks


def test_violations_are_scoped_to_the_requested_round(harness: AnalyticsHarness) -> None:
    rounds = [
        round_row(1, start=100, freeze_end=100, end=604),
        round_row(2, start=700, freeze_end=700, end=1000),
    ]
    gen = _generation(
        harness,
        [
            state_row(0, 500, PLAYER_A),
            state_row(1, 500, None, health=100),  # inside round one
            state_row(2, 900, None, health=100),  # inside round two
            state_row(3, 1100, None, health=100),  # outside both rounds
        ],
        rounds,
    )

    assert live_identity_violations(harness.pool, gen) == [500, 900, 1100]
    assert live_identity_violations(harness.pool, gen, round_id=1) == [500]
    assert live_identity_violations(harness.pool, gen, round_id=2) == [900]
    assert coverage(harness.pool, gen, round_id=1).alive_null == 1


# -- round windows ----------------------------------------------------------
def test_round_window_starts_at_the_freeze_end(harness: AnalyticsHarness) -> None:
    rounds = [round_row(1, start=100, freeze_end=140, end=200)]
    gen = _generation(
        harness,
        [
            state_row(0, 50, PLAYER_A),  # before the round
            state_row(1, 110, PLAYER_A),  # previous round's death tail
            state_row(2, 150, PLAYER_A),
            state_row(3, 150, None),
            state_row(4, 250, PLAYER_B),  # after the round
        ],
        rounds,
    )

    in_round = coverage(harness.pool, gen, round_id=1)
    whole = coverage(harness.pool, gen)

    assert in_round.total_observations == 2
    assert in_round.null_observations == 1
    assert in_round.alive_total == 1
    assert in_round.live_coverage == 1.0
    assert in_round.notes[-1].startswith("scope round:1:")

    assert whole.total_observations == 5
    assert whole.alive_total == 4
    assert whole.notes[-1].startswith("scope generation:")


def test_round_window_falls_back_to_the_start_when_freeze_is_missing(
    harness: AnalyticsHarness,
) -> None:
    rounds = [round_row(1, start=100, freeze_end=None, end=200)]
    gen = _generation(harness, [state_row(0, 110, PLAYER_A), state_row(1, 210, PLAYER_A)], rounds)

    result = coverage(harness.pool, gen, round_id=1)

    assert result.total_observations == 1
    assert result.alive_total == 1


def test_an_empty_round_window_has_no_live_ratio(harness: AnalyticsHarness) -> None:
    rounds = [round_row(1, start=100, freeze_end=100, end=200), round_row(2, start=900, freeze_end=900, end=1000)]
    gen = _generation(harness, [state_row(0, 150, PLAYER_A)], rounds)

    result = coverage(harness.pool, gen, round_id=2)

    assert result.total_observations == 0
    assert result.alive_total == 0
    assert result.live_coverage is None
    assert result.notes[-1].startswith("scope round:2:")


def test_unknown_round_is_not_found(harness: AnalyticsHarness) -> None:
    gen = _generation(harness, [state_row(0, 100, PLAYER_A)])

    with pytest.raises(AppError) as caught:
        coverage(harness.pool, gen, round_id=99)

    assert caught.value.code == "NOT_FOUND"
    assert caught.value.stage == "analytics"
    with pytest.raises(AppError) as caught:
        live_identity_violations(harness.pool, gen, round_id=99)
    assert caught.value.code == "NOT_FOUND"


@pytest.mark.parametrize(
    "partial",
    [
        round_row(1, start=100, freeze_end=100, end=None),
        round_row(1, start=None, freeze_end=None, end=200),
        round_row(1, start=200, freeze_end=200, end=100),
    ],
    ids=["no-end", "no-start", "inverted"],
)
def test_incomplete_round_timing_is_partial(harness: AnalyticsHarness, partial: dict) -> None:
    gen = _generation(harness, [state_row(0, 100, PLAYER_A)], [partial])

    with pytest.raises(AppError) as caught:
        coverage(harness.pool, gen, round_id=1)

    assert caught.value.code == "PARTIAL_ROUND"
    assert caught.value.stage == "analytics"


# -- no joining by position or name -----------------------------------------
def test_a_corpse_sharing_a_position_is_not_merged_into_the_living_player(
    harness: AnalyticsHarness,
) -> None:
    gen = _generation(
        harness,
        [
            state_row(0, 300, PLAYER_A, x=10.0, y=20.0),
            state_row(1, 300, None, x=10.0, y=20.0),  # same coordinates, dead entity
            state_row(2, 300, PLAYER_A, x=10.0, y=20.0),  # identical living row
        ],
    )

    result = coverage(harness.pool, gen)

    assert result.total_observations == 3
    assert result.null_observations == 1
    assert result.alive_total == 2
    assert result.alive_identified == 2
    assert result.alive_null == 0
    assert result.live_coverage == 1.0
    assert live_identity_violations(harness.pool, gen) == []


def test_coverage_does_not_depend_on_the_players_roster(harness: AnalyticsHarness) -> None:
    """Identity comes from the state row verbatim, not from a roster join."""
    gen = _generation(harness, [state_row(0, 100, "steam:99999999999999999")])

    result = coverage(harness.pool, gen)

    assert result.identified == 1
    assert result.alive_identified == 1
    assert result.live_coverage == 1.0


def test_null_rows_with_health_data_are_flagged_in_the_notes(harness: AnalyticsHarness) -> None:
    gen = _generation(harness, [state_row(0, 100, PLAYER_A), state_row(1, 100, None, health=100)])

    result = coverage(harness.pool, gen)

    assert result.alive_null == 1
    assert any("carrying health data" in note for note in result.notes)
    assert any("dead-entity rule violated" in note for note in result.notes)


def test_coverage_uses_the_pool_it_was_given(harness: AnalyticsHarness) -> None:
    gen = _generation(harness, [state_row(0, 100, PLAYER_A)])
    pool = GenerationPool(harness.catalog, harness.artifacts)

    assert coverage(pool, gen).total_observations == 1
    assert coverage(pool, harness.open()).total_observations == 1
    assert harness.open().demo_id == DEMO_ID

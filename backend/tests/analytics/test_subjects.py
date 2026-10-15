"""Subject configuration and per-recording participation.

Real generation fixtures (published through the staging/manifest/catalog path)
exercise the service against genuine Parquet tables; nothing here reads a
recorded demo or starts a worker. The subject is the application setting that
the whole analytics surface is keyed on, so these tests cover: exact-string
SteamID64 persistence, the four participation states, and the measurements the
later phases consume (rounds, ticks, identity, position, anomalies, events).
"""

from __future__ import annotations

import sqlite3

import pytest

from cs_demo_analyzer.analytics.subjects import MAX_LIST_LIMIT, SETTING_KEY, SubjectService
from cs_demo_analyzer.domain.contracts import AppError
from cs_demo_analyzer.domain.subjects import (
    DEFAULT_STEAM_ID,
    canonical_player_id,
    normalize_steam_id,
)

from .fixtures import (  # noqa: F401 - `harness` is imported so pytest registers the fixture
    PLAYER_A,
    PLAYER_B,
    AnalyticsHarness,
    frame,
    harness,
    players_rows,
    round_row,
    state_row,
)

OTHER_DEMO = "b" * 64

ROUND_ONE = round_row(1, start=100, freeze_end=100, end=200)
ROUND_TWO = round_row(2, start=300, freeze_end=300, end=400)

PLAYER_A_DIGITS = PLAYER_A.split(":", 1)[1]
PLAYER_B_DIGITS = PLAYER_B.split(":", 1)[1]


def _service(analytics: AnalyticsHarness) -> SubjectService:
    return SubjectService(analytics.catalog, analytics.pool)


def _kill(ordinal: int, tick: int, attacker: str, victim: str) -> dict:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "attacker_id": attacker,
        "victim_id": victim,
        "assister_id": None,
        "weapon": "ak47",
        "headshot": False,
        "attacker_entity_id": 1,
        "attacker_entity_serial": 1,
        "victim_entity_id": 2,
        "victim_entity_serial": 1,
    }


def _shot(ordinal: int, tick: int, player_id: str) -> dict:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "player_id": player_id,
        "weapon": "ak47",
        "x": 1.0,
        "y": 2.0,
        "z": 3.0,
        "yaw": 10.0,
        "pitch": 0.0,
    }


# -- the configured subject -------------------------------------------------
def test_the_built_in_default_subject_is_a_17_digit_steamid64(harness: AnalyticsHarness) -> None:
    config = _service(harness).get()

    assert config.steam_id == DEFAULT_STEAM_ID
    assert config.player_id == canonical_player_id(DEFAULT_STEAM_ID)
    assert len(config.steam_id) == 17 and config.steam_id.isdigit()
    assert isinstance(config.player_id, str)


def test_set_persists_the_exact_digits_in_a_single_row(harness: AnalyticsHarness) -> None:
    service = _service(harness)

    written = service.set(PLAYER_A_DIGITS)
    assert written.steam_id == "76561198000000013"
    assert written.player_id == PLAYER_A

    service.set(PLAYER_B_DIGITS)
    stored = service.get()
    assert stored.steam_id == "76561198000000021"
    assert stored.player_id == PLAYER_B

    connection = sqlite3.connect(harness.root / "catalog.sqlite")
    try:
        rows = connection.execute("SELECT key, value, COUNT(*) FROM app_settings GROUP BY key").fetchall()
    finally:
        connection.close()
    assert rows == [(SETTING_KEY, "76561198000000021", 1)]


@pytest.mark.parametrize(
    "value",
    [
        "7656119800000001",  # 16 digits
        "765611980000000130",  # 18 digits
        "7656119800000001a",  # not decimal
        " 76561198000000013",  # exact string, no trimming
        "76561198057213632.0",  # a float spelling of the default
        "76561197960265727",  # below the individual account base
        "",
    ],
)
def test_set_rejects_non_steamid64_strings(harness: AnalyticsHarness, value: str) -> None:
    service = _service(harness)
    before = service.get()

    with pytest.raises(AppError) as caught:
        service.set(value)

    assert caught.value.code == "INVALID_ARGUMENT"
    assert caught.value.stage == "analytics"
    assert service.get() == before


def test_set_rejects_a_non_string(harness: AnalyticsHarness) -> None:
    with pytest.raises(AppError) as caught:
        _service(harness).set(76561198000000013)  # type: ignore[arg-type]

    assert caught.value.code == "INVALID_ARGUMENT"


def test_normalize_keeps_the_digits_it_was_given() -> None:
    assert normalize_steam_id(DEFAULT_STEAM_ID) == DEFAULT_STEAM_ID
    assert normalize_steam_id("76561198000000001") == "76561198000000001"
    with pytest.raises(ValueError):
        normalize_steam_id("00000000000000000")
    with pytest.raises(ValueError):
        normalize_steam_id(DEFAULT_STEAM_ID + "0")


# -- participation states ---------------------------------------------------
def test_participation_measures_rounds_events_and_positional_coverage(
    harness: AnalyticsHarness,
) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A, PLAYER_B),
            "rounds": [ROUND_ONE, ROUND_TWO],
            "player_state": [
                state_row(0, 100, PLAYER_A),
                state_row(1, 110, PLAYER_A, health=0),
                state_row(2, 320, PLAYER_A),
                state_row(3, 320, PLAYER_B),
                state_row(4, 900, PLAYER_B),  # outside every round window
            ],
            "kills": [_kill(0, 150, PLAYER_A, PLAYER_B), _kill(1, 900, PLAYER_B, PLAYER_A)],
            "shots": [_shot(0, 160, PLAYER_A), _shot(1, 900, PLAYER_A)],
        }
    )

    participation = _service(harness).participation(harness.open().demo_id, player_id=PLAYER_A)
    measurements = participation.measurements
    assert measurements is not None

    assert participation.status == "present"
    assert participation.in_roster is True
    assert participation.player_id == PLAYER_A
    assert participation.player_id_source == "override"
    assert participation.steam_id == DEFAULT_STEAM_ID
    assert participation.map_name == "de_inferno"
    assert participation.recording_kind == "unknown"
    assert participation.quality == "complete"
    assert participation.limitations == []

    assert measurements.tick_rate_hz == 64.0
    assert measurements.rounds_total == 2
    assert measurements.rounds_with_subject == 2
    assert measurements.rounds_alive == 2
    assert (measurements.first_tick, measurements.last_tick) == (100, 320)
    assert measurements.state_rows == 3
    assert measurements.alive_rows == 2
    assert measurements.dead_rows == 1
    assert measurements.health_unknown_rows == 0
    assert measurements.position_rows == 3
    assert measurements.position_missing == 0
    assert measurements.angle_anomalies == 0
    assert measurements.health_anomalies == 0
    assert measurements.rows_outside_rounds == 0
    assert measurements.kills == 1
    assert measurements.deaths == 1
    assert measurements.assists == 0
    assert measurements.shots == 2
    assert measurements.events_outside_rounds == 2  # the tick-900 kill and shot
    assert measurements.null_identity_rows == 0
    assert measurements.replay_available is True


def test_damage_totals_follow_the_subject_role(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A, PLAYER_B),
            "rounds": [ROUND_ONE],
            "player_state": [state_row(0, 100, PLAYER_A)],
            "damages": [
                {"row_ordinal": 0, "tick": 150, "attacker_id": PLAYER_A, "victim_id": PLAYER_B, "damage_health": 30, "damage_armor": 0, "weapon": "ak47"},
                {"row_ordinal": 1, "tick": 160, "attacker_id": PLAYER_B, "victim_id": PLAYER_A, "damage_health": 100, "damage_armor": 0, "weapon": "ak47"},
            ],
        }
    )

    measurements = _service(harness).participation(
        harness.open().demo_id, player_id=PLAYER_A
    ).measurements
    assert measurements is not None
    assert measurements.damages_dealt == 1
    assert measurements.damage_taken == 1
    assert measurements.events_outside_rounds == 0


def test_absent_subject_is_explicit_and_never_substituted(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_B),
            "rounds": [ROUND_ONE],
            "player_state": [state_row(0, 100, PLAYER_B)],
        }
    )

    participation = _service(harness).participation(harness.open().demo_id)
    assert participation.status == "absent"
    assert participation.in_roster is False
    assert participation.player_id == canonical_player_id(DEFAULT_STEAM_ID)
    assert participation.measurements is not None
    assert participation.measurements.state_rows == 0
    assert participation.limitations == []


def test_unresolved_roster_entries_make_the_subject_unresolved(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": frame(
                "players",
                [
                    {"player_id": PLAYER_B, "steam_id": PLAYER_B_DIGITS, "name": "b", "side": "ct"},
                    {"player_id": "unresolved:roster:1", "steam_id": None, "name": None, "side": None},
                ],
            ),
            "rounds": [ROUND_ONE],
            "player_state": [state_row(0, 100, PLAYER_B)],
        }
    )

    participation = _service(harness).participation(harness.open().demo_id)
    assert participation.status == "unresolved"
    assert participation.in_roster is False
    assert any("no resolvable SteamID" in note for note in participation.limitations)


def test_a_generation_without_a_roster_is_unresolved(harness: AnalyticsHarness) -> None:
    harness.publish(tables={"players": [], "rounds": [ROUND_ONE], "player_state": []})

    participation = _service(harness).participation(harness.open().demo_id)
    assert participation.status == "unresolved"
    assert participation.measurements is not None
    assert participation.measurements.state_rows == 0


def test_a_selected_unresolved_roster_record_is_never_present(harness: AnalyticsHarness) -> None:
    """A roster record without a resolvable SteamID is not the selected account.

    ``in_roster`` still reports that the record exists and ``player_id`` keeps its
    own reference, but the Steam account can neither be established as present
    nor be inferred from anonymous (null-identity) rows in the same recording.
    """
    harness.publish(
        tables={
            "players": frame(
                "players",
                [
                    {"player_id": PLAYER_A, "steam_id": PLAYER_A_DIGITS, "name": "a", "side": "ct"},
                    {"player_id": "unresolved:roster:11", "steam_id": None, "name": None, "side": "unknown"},
                ],
            ),
            "rounds": [ROUND_ONE],
            "player_state": [state_row(0, 100, PLAYER_A), state_row(1, 100, None, health=0)],
        }
    )
    service = _service(harness)
    demo_id = harness.open().demo_id

    participation = service.participation(demo_id, player_id="unresolved:roster:11")
    measurements = participation.measurements
    assert measurements is not None

    assert participation.status == "unresolved"
    assert participation.in_roster is True
    assert participation.player_id == "unresolved:roster:11"
    assert participation.player_id_source == "override"
    assert measurements.state_rows == 0  # anonymous dead rows are never attributed to it
    assert measurements.null_identity_rows == 1
    assert any("no resolvable SteamID" in note for note in participation.limitations)

    # The resolvable roster member and the configured subject are unaffected.
    assert service.participation(demo_id, player_id=PLAYER_A).status == "present"
    # The config subject is in no roster; the unresolved roster entry above keeps
    # that path unresolved rather than absent, but never present.
    assert service.participation(demo_id).status != "present"


def test_a_non_account_selection_is_unresolved_not_absent(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A),
            "rounds": [ROUND_ONE],
            "player_state": [state_row(0, 100, PLAYER_A)],
        }
    )

    participation = _service(harness).participation(
        harness.open().demo_id, player_id="not-a-steam-account"
    )

    assert participation.status == "unresolved"
    assert participation.in_roster is False
    assert participation.player_id == "not-a-steam-account"
    assert participation.measurements is not None
    assert participation.measurements.state_rows == 0
    assert any("not a resolvable SteamID64" in note for note in participation.limitations)


def test_participation_without_a_generation_is_not_ready(harness: AnalyticsHarness) -> None:
    harness.register(OTHER_DEMO)

    participation = _service(harness).participation(OTHER_DEMO)

    assert participation.status == "not_ready"
    assert participation.measurements is None
    assert participation.generation_id is None
    assert participation.limitations[0].startswith("NOT_READY")


def test_unknown_generation_of_a_known_demo_is_not_ready(harness: AnalyticsHarness) -> None:
    harness.publish(tables={"players": players_rows(PLAYER_A)})

    participation = _service(harness).participation(harness.open().demo_id, generation_id="c" * 32)

    assert participation.status == "not_ready"
    assert participation.generation_id == "c" * 32
    assert participation.limitations[0].startswith("GENERATION_UNAVAILABLE")


def test_unknown_demo_raises_not_found(harness: AnalyticsHarness) -> None:
    with pytest.raises(AppError) as caught:
        _service(harness).participation("c" * 64)

    assert caught.value.code == "NOT_FOUND"


def test_a_bare_steamid_override_resolves_to_the_canonical_player_id(
    harness: AnalyticsHarness,
) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A),
            "rounds": [ROUND_ONE],
            "player_state": [state_row(0, 100, PLAYER_A)],
        }
    )

    participation = _service(harness).participation(harness.open().demo_id, player_id=PLAYER_A_DIGITS)

    assert participation.status == "present"
    assert participation.player_id == PLAYER_A
    assert participation.player_id_source == "override"


# -- measurement edge cases -------------------------------------------------
def test_null_health_is_not_counted_as_death(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A),
            "rounds": [ROUND_ONE],
            "player_state": [
                {**state_row(0, 100, PLAYER_A), "health": None},
                state_row(1, 101, PLAYER_A, health=0),
            ],
        }
    )

    measurements = _service(harness).participation(
        harness.open().demo_id, player_id=PLAYER_A
    ).measurements
    assert measurements is not None
    assert measurements.state_rows == 2
    assert measurements.health_unknown_rows == 1
    assert measurements.dead_rows == 1
    assert measurements.alive_rows == 0
    assert measurements.health_anomalies == 0


def test_health_angle_and_position_anomalies_are_counted(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A),
            "rounds": [ROUND_ONE],
            "player_state": [
                state_row(0, 100, PLAYER_A, health=150),
                {**state_row(1, 101, PLAYER_A), "pitch": 120.0},
                {**state_row(2, 102, PLAYER_A), "x": None, "yaw": None},
                {**state_row(3, 103, PLAYER_A), "yaw": None},
            ],
        }
    )

    measurements = _service(harness).participation(
        harness.open().demo_id, player_id=PLAYER_A
    ).measurements
    assert measurements is not None
    assert measurements.state_rows == 4
    assert measurements.health_anomalies == 1
    assert measurements.angle_anomalies == 2  # out-of-range pitch and a yaw gap
    assert measurements.position_rows == 3
    assert measurements.position_missing == 1


def test_incomplete_round_windows_do_not_fabricate_outside_rows(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A),
            "rounds": [round_row(1, start=100, freeze_end=100, end=None)],
            "player_state": [state_row(0, 100, PLAYER_A), state_row(1, 500, PLAYER_A)],
        }
    )

    participation = _service(harness).participation(harness.open().demo_id, player_id=PLAYER_A)
    measurements = participation.measurements
    assert measurements is not None
    assert measurements.rounds_total == 1
    assert measurements.rounds_with_subject == 0
    assert measurements.rows_outside_rounds == 0
    assert measurements.events_outside_rounds == 0
    assert any("no complete round windows" in note for note in participation.limitations)
    assert any("no complete tick window" in note for note in participation.limitations)


def test_active_round_windows_start_at_the_freeze_end(harness: AnalyticsHarness) -> None:
    """Inside a round is Phase 1's active window ``[freeze_end_tick or start_tick, end_tick]``.

    Freeze/buy rows are therefore outside the round even though they sit inside
    ``[start_tick, end_tick]``, a round whose only subject rows are in the freeze
    period does not count as played, and a null ``freeze_end_tick`` falls back to
    ``start_tick`` instead of dropping the round. Raw first/last ticks stay
    window-independent.
    """
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A),
            "rounds": [
                round_row(1, start=100, freeze_end=140, end=200),
                round_row(2, start=300, freeze_end=340, end=400),
                round_row(3, start=500, freeze_end=None, end=600),
            ],
            "player_state": [
                state_row(0, 110, PLAYER_A),  # round 1 freeze: outside
                state_row(1, 160, PLAYER_A),  # round 1 active, alive
                state_row(2, 180, PLAYER_A, health=0),  # round 1 active, dead
                state_row(3, 310, PLAYER_A),  # round 2 freeze only: outside
                state_row(4, 320, PLAYER_A),  # round 2 freeze only: outside
                state_row(5, 550, PLAYER_A),  # round 3, null freeze -> start_tick
            ],
            "shots": [_shot(0, 310, PLAYER_A)],  # inside [300, 400] but outside the active window
        }
    )

    participation = _service(harness).participation(harness.open().demo_id, player_id=PLAYER_A)
    measurements = participation.measurements
    assert measurements is not None

    assert participation.limitations == []  # a null freeze_end is a fallback, not an incomplete round
    assert measurements.rounds_total == 3
    assert measurements.rounds_with_subject == 2  # rounds 1 and 3; round 2 has freeze rows only
    assert measurements.rounds_alive == 2
    assert measurements.rows_outside_rounds == 3  # ticks 110, 310, 320
    assert measurements.events_outside_rounds == 1  # the tick-310 shot
    assert measurements.shots == 1
    assert measurements.state_rows == 6
    assert measurements.alive_rows == 5
    assert measurements.dead_rows == 1
    assert (measurements.first_tick, measurements.last_tick) == (110, 550)  # raw, not window-clipped


def test_null_identity_rows_are_reported_as_context(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables={
            "players": players_rows(PLAYER_A),
            "rounds": [ROUND_ONE],
            "player_state": [state_row(0, 100, PLAYER_A), state_row(1, 100, None, health=0)],
        }
    )

    measurements = _service(harness).participation(
        harness.open().demo_id, player_id=PLAYER_A
    ).measurements
    assert measurements is not None
    assert measurements.state_rows == 1
    assert measurements.null_identity_rows == 1


def test_list_participation_pages_the_catalog_and_bounds_its_arguments(
    harness: AnalyticsHarness,
) -> None:
    harness.publish(tables={"players": players_rows(PLAYER_A), "rounds": [ROUND_ONE]})
    harness.register(OTHER_DEMO)
    service = _service(harness)

    listed = service.list_participation()
    assert sorted(item.status for item in listed) == ["absent", "not_ready"]

    assert service.list_participation(limit=1, offset=1) == service.list_participation()[1:]
    with pytest.raises(AppError) as caught:
        service.list_participation(limit=0)
    assert caught.value.code == "INVALID_ARGUMENT"
    with pytest.raises(AppError):
        service.list_participation(limit=MAX_LIST_LIMIT + 1)
    with pytest.raises(AppError):
        service.list_participation(offset=-1)

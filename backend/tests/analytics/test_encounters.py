"""Behavior tests for :mod:`cs_demo_analyzer.analytics.encounters`.

The fixtures are published through the real staging/manifest/catalog path (see
``.fixtures``), so the encounter service is exercised against genuine Parquet
tables and a real :class:`GenerationPool`. Only the consequential invariants are
tested: deterministic content-addressed ids, same-tick event preservation,
gap/round-boundary clamping, death-terminated episodes, verbatim evidence and
the absent-subject contract.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable, Iterator, Mapping

import pytest

from cs_demo_analyzer.analytics.encounters import EncounterService
from cs_demo_analyzer.domain.contracts import AppError
from cs_demo_analyzer.domain.encounters import (
    ENCOUNTER_ID_PREFIX,
    LIMITATION_FIRST_DAMAGE_UNAVAILABLE,
    LIMITATION_GROUPING_HEURISTIC,
    LIMITATION_NO_INTERPERSONAL_EVIDENCE,
)

from .fixtures import (  # noqa: F401 - `harness` is imported so pytest registers the fixture
    AnalyticsHarness,
    harness,
    players_rows,
    round_row,
)

SUBJECT = "steam:76561198000000013"
OPPONENT = "steam:76561198000000021"
OPPONENT_TWO = "steam:76561198000000039"
TEAMMATE = "steam:76561198000000047"

ROUND_START = 1000
FREEZE_END = 1100
ROUND_END = 2000
GAP_TICKS = 192  # 3.0 s at 64 Hz
PRE_TICKS = 192
POST_TICKS = 64


# --------------------------------------------------------------------------- #
# row builders (full frozen schema; omitted keys are null, never invented)
# --------------------------------------------------------------------------- #
def state(ordinal: int, tick: int, player_id: str, *, side: str = "t", health: int = 100) -> dict[str, Any]:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "player_id": player_id,
        "x": 100.0,
        "y": 200.0,
        "z": 0.0,
        "yaw": 0.0,
        "pitch": 0.0,
        "velocity_x": 0.0,
        "velocity_y": 0.0,
        "velocity_z": 0.0,
        "health": health,
        "armor": 100,
        "money": 800,
        "side": side,
        "active_weapon": "ak47",
        "has_bomb": False,
        "is_crouched": False,
        "is_scoped": False,
        "is_reloading": False,
    }


def kill(
    ordinal: int,
    tick: int,
    attacker: str | None,
    victim: str | None,
    *,
    assister: str | None = None,
    weapon: str = "ak47",
    headshot: bool = False,
) -> dict[str, Any]:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "attacker_id": attacker,
        "victim_id": victim,
        "assister_id": assister,
        "weapon": weapon,
        "headshot": headshot,
        "attacker_entity_id": 1,
        "attacker_entity_serial": 10,
        "victim_entity_id": 2,
        "victim_entity_serial": 20,
    }


def damage(ordinal: int, tick: int, attacker: str, victim: str, amount: int = 27) -> dict[str, Any]:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "attacker_id": attacker,
        "victim_id": victim,
        "damage_health": amount,
        "damage_armor": 0,
        "weapon": "ak47",
    }


def shot(ordinal: int, tick: int, player_id: str) -> dict[str, Any]:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "player_id": player_id,
        "weapon": "ak47",
        "x": 100.0,
        "y": 200.0,
        "z": 0.0,
        "yaw": 0.0,
        "pitch": 0.0,
    }


def tables(
    *,
    players: Iterable[str] = (SUBJECT, OPPONENT, OPPONENT_TWO, TEAMMATE),
    states: Iterable[Mapping[str, Any]] = (),
    kills: Iterable[Mapping[str, Any]] = (),
    damages: Iterable[Mapping[str, Any]] = (),
    shots: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    return {
        "players": players_rows(*players),
        "rounds": [round_row(1, start=ROUND_START, freeze_end=FREEZE_END, end=ROUND_END)],
        "player_state": list(states),
        "kills": list(kills),
        "damages": list(damages),
        "shots": list(shots),
        "bomb": [],
    }


@contextmanager
def raised(code: str) -> Iterator[None]:
    """Assert the body raises an :class:`AppError` whose ``code`` matches."""
    with pytest.raises(AppError) as caught:
        yield
    assert caught.value.code == code, f"expected {code}, got {caught.value.code}"


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
def test_gap_grouping_and_round_boundary_clamping(harness: AnalyticsHarness) -> None:
    harness.publish(tables=tables(shots=[shot(0, 1200, SUBJECT), shot(1, 1600, SUBJECT), shot(2, 1990, SUBJECT)]))
    gen = harness.open()
    service = EncounterService(harness.pool)

    out = service.list(gen, SUBJECT)

    assert out.subject_id == SUBJECT
    assert out.grouping.gap_ticks == GAP_TICKS
    assert out.grouping.pre_ticks == PRE_TICKS
    assert out.grouping.post_ticks == POST_TICKS
    assert LIMITATION_GROUPING_HEURISTIC in out.limitations
    assert [summary.start_tick for summary in out.encounters] == [1200, 1600, 1990]
    assert len({summary.encounter_id for summary in out.encounters}) == 3

    first = service.detail(gen, SUBJECT, out.encounters[0].encounter_id)
    assert first.source_window.window_start_tick == FREEZE_END  # 1200 - 192 = 1008 clipped to 1100
    assert first.source_window.truncated_start is True
    assert first.source_window.window_end_tick == 1200 + POST_TICKS

    second = service.detail(gen, SUBJECT, out.encounters[1].encounter_id)
    assert second.source_window.window_start_tick == 1600 - PRE_TICKS
    assert second.source_window.truncated_start is False

    third = service.detail(gen, SUBJECT, out.encounters[2].encounter_id)
    assert third.source_window.window_end_tick == ROUND_END  # 1990 + 64 clipped to 2000
    assert third.source_window.truncated_end is True


def test_same_tick_events_and_multi_opponent_are_preserved(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables=tables(
            kills=[kill(0, 1300, SUBJECT, OPPONENT), kill(1, 1300, SUBJECT, OPPONENT_TWO)],
            damages=[damage(0, 1300, SUBJECT, OPPONENT_TWO, 41)],
        )
    )
    gen = harness.open()
    service = EncounterService(harness.pool)

    out = service.list(gen, SUBJECT)
    assert out.total == 1
    summary = out.encounters[0]
    assert summary.start_tick == summary.end_tick == 1300
    assert summary.event_count == 3
    assert summary.kill_count == 2
    assert summary.death_count == 0
    assert summary.participant_ids == sorted([OPPONENT, OPPONENT_TWO])

    kill_anchors = [anchor for anchor in summary.anchors if anchor.kind == "kill"]
    assert len(kill_anchors) == 2
    assert len({anchor.anchor_id for anchor in kill_anchors}) == 2
    assert all(anchor.evidence and anchor.evidence[0].dataset == "kills" for anchor in kill_anchors)

    detail = service.detail(gen, SUBJECT, summary.encounter_id)
    assert detail.summary == summary  # detail recomputes the identical list-level record
    assert len(detail.events) == 3
    assert {(event.dataset, event.row_ordinal) for event in detail.events} == {
        ("kills", 0),
        ("kills", 1),
        ("damages", 0),
    }
    assert all(event.tick == 1300 and event.round_id == 1 for event in detail.events)
    assert detail.contextual_event_count == 0


def test_detail_evidence_and_trajectory_are_verbatim(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables=tables(
            states=[
                state(0, 1200, SUBJECT, side="t"),
                state(1, 1250, OPPONENT, side="ct"),
                state(2, 1300, SUBJECT, side="t"),
                state(3, 1400, SUBJECT, side="t"),
            ],
            shots=[shot(0, 1200, SUBJECT), shot(1, 1300, SUBJECT)],
            damages=[damage(0, 1250, SUBJECT, OPPONENT, 30)],
        )
    )
    gen = harness.open()
    service = EncounterService(harness.pool)

    out = service.list(gen, SUBJECT)
    assert out.total == 1
    summary = out.encounters[0]
    assert summary.participant_ids == [OPPONENT]

    detail = service.detail(gen, SUBJECT, summary.encounter_id)
    assert detail.summary == summary
    for event in detail.events:
        assert event.evidence.dataset == event.dataset
        assert event.evidence.row_ordinal == event.row_ordinal
        assert event.evidence.tick == event.tick
        assert event.evidence.generation_id == gen.generation_id
        assert event.evidence.round_id == 1

    # Trajectory is exactly the recorded subject rows inside the window: no
    # interpolated ticks, no rows belonging to another player.
    recorded = {1200, 1300}
    ticks = [sample.tick for sample in detail.subject_trajectory]
    assert ticks == sorted(ticks)
    assert set(ticks) == recorded
    assert all(sample.player_id == SUBJECT for sample in detail.subject_trajectory)
    assert 1250 in {tick for lo, hi in detail.trajectory_missing_ranges for tick in (lo, hi)} or any(
        lo <= 1250 <= hi for lo, hi in detail.trajectory_missing_ranges
    )

    participants = {participant.player_id: participant for participant in detail.participants}
    assert participants[OPPONENT].relation == "opponent"
    assert participants[OPPONENT].side == "ct"
    assert participants[OPPONENT].subject_side == "t"
    assert participants[OPPONENT].direct is True
    assert participants[OPPONENT].roles == ["victim"]


def test_subject_death_ends_the_episode(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables=tables(
            shots=[shot(0, 1200, SUBJECT), shot(1, 1400, SUBJECT)],
            kills=[kill(0, 1300, OPPONENT, SUBJECT, weapon="m4a1")],
        )
    )
    gen = harness.open()
    service = EncounterService(harness.pool)

    out = service.list(gen, SUBJECT)
    assert out.total == 2
    first, second = out.encounters
    assert first.start_tick == 1200 and first.end_tick == 1300
    assert first.subject_died is True
    assert first.death_count == 1
    assert [anchor.kind for anchor in first.anchors].count("death") == 1
    # 1400 is within the gap of the death tick, but a dead subject cannot keep
    # fighting: the episode is closed and a new one starts.
    assert second.start_tick == 1400 and second.end_tick == 1400
    assert second.subject_died is False


def test_encounter_ids_are_content_addressed_and_generation_bound(harness: AnalyticsHarness) -> None:
    authored = tables(shots=[shot(0, 1200, SUBJECT), shot(1, 1600, SUBJECT)])
    first_manifest = harness.publish(tables=authored)
    second_manifest = harness.publish(tables=authored)
    assert first_manifest.generation_id != second_manifest.generation_id

    service = EncounterService(harness.pool)
    first_gen = harness.open(first_manifest.generation_id)
    second_gen = harness.open(second_manifest.generation_id)

    once = service.list(first_gen, SUBJECT)
    twice = service.list(first_gen, SUBJECT)
    assert [item.encounter_id for item in once.encounters] == [item.encounter_id for item in twice.encounters]
    assert once.encounters == twice.encounters

    other = service.list(second_gen, SUBJECT)
    assert [item.start_tick for item in other.encounters] == [item.start_tick for item in once.encounters]
    assert {item.encounter_id for item in other.encounters}.isdisjoint(
        {item.encounter_id for item in once.encounters}
    )


def test_anchor_kinds_resolution_and_grouping_identity(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables=tables(shots=[shot(0, 1200, SUBJECT)], kills=[kill(0, 1200, OPPONENT, SUBJECT, weapon="m4a1")])
    )
    gen = harness.open()
    service = EncounterService(harness.pool)

    out = service.list(gen, SUBJECT)
    assert out.total == 1
    summary = out.encounters[0]
    anchors = {anchor.kind: anchor for anchor in summary.anchors}
    assert set(anchors) == {
        "pre_contact",
        "first_interaction",
        "first_shot",
        "first_damage",
        "death",
        "last_interaction",
        "resolution",
        "post_contact",
    }
    # observed anchors stay chronological; unavailable ones are explicit, not fabricated
    observed = [anchor.tick for anchor in summary.anchors if anchor.status == "observed" and anchor.tick is not None]
    assert observed == sorted(observed)

    assert anchors["first_interaction"].evidence_kind == "recorded"
    assert anchors["first_shot"].status == "observed" and anchors["first_shot"].tick == 1200
    assert anchors["first_shot"].evidence[0].dataset == "shots"
    assert anchors["last_interaction"].tick == 1200 and anchors["last_interaction"].evidence
    assert anchors["pre_contact"].evidence_kind == "computed" and anchors["pre_contact"].evidence == []

    # no damage row was recorded: the anchor is explicitly unavailable
    missing = anchors["first_damage"]
    assert missing.status == "unavailable"
    assert missing.tick is None
    assert missing.evidence_kind == "unsupported"
    assert missing.evidence == []
    assert LIMITATION_FIRST_DAMAGE_UNAVAILABLE in summary.limitations

    # the subject died in this episode: the rule is recorded, not guessed
    resolution = anchors["resolution"]
    assert resolution.resolution == "subject_death"
    assert resolution.tick == 1200
    assert resolution.evidence_kind == "recorded"
    assert resolution.evidence[0].dataset == "kills"

    # a shot-only episode keeps existing, with explicit no-interpersonal evidence
    harness.publish(tables=tables(shots=[shot(0, 1500, SUBJECT)]))
    solo_gen = harness.open()
    solo = service.list(solo_gen, SUBJECT)
    assert solo.total == 1
    assert solo.encounters[0].participant_ids == []
    assert LIMITATION_NO_INTERPERSONAL_EVIDENCE in solo.encounters[0].limitations

    # grouping options are part of the encounter identity: same seeds and bounds,
    # different pre window -> different id, and each id only resolves with its own
    # options, so the returned config always reproduces it.
    short = service.list(gen, SUBJECT, pre_seconds=3.0).encounters[0]
    long = service.list(gen, SUBJECT, pre_seconds=5.0).encounters[0]
    assert (short.start_tick, short.end_tick) == (long.start_tick, long.end_tick)
    assert short.encounter_id != long.encounter_id
    assert service.detail(gen, SUBJECT, long.encounter_id, pre_seconds=5.0).summary == long
    with raised("NOT_FOUND"):
        service.detail(gen, SUBJECT, short.encounter_id, pre_seconds=5.0)


def test_adjacent_episode_subject_rows_stay_contextual(harness: AnalyticsHarness) -> None:
    harness.publish(
        tables=tables(
            states=[
                state(0, 1200, SUBJECT, side="t"),
                state(1, 1200, OPPONENT, side="ct"),
                state(2, 1400, SUBJECT, side="t"),
            ],
            shots=[shot(0, 1200, SUBJECT), shot(1, 1400, SUBJECT)],
            kills=[kill(0, 1200, OPPONENT, SUBJECT, weapon="m4a1")],
        )
    )
    gen = harness.open()
    service = EncounterService(harness.pool)

    # The 5 s pre window is wider than the 200-tick seed gap, so the second
    # episode's window reaches into the first episode's seeds.
    out = service.list(gen, SUBJECT, pre_seconds=5.0)
    assert out.total == 2
    first, second = out.encounters
    assert (first.start_tick, first.end_tick) == (1200, 1200)
    assert (second.start_tick, second.end_tick) == (1400, 1400)

    detail = service.detail(gen, SUBJECT, second.encounter_id, pre_seconds=5.0)
    assert detail.summary == second
    # The adjacent episode's rows are inside the window but are not this
    # episode's seeds: neither the seed count nor the event count may inflate.
    assert detail.summary.event_count == 1
    assert detail.subject_event_count == 1
    assert detail.summary.death_count == 0 and detail.summary.subject_died is False

    adjacent = {(event.dataset, event.row_ordinal): event for event in detail.events if event.tick == 1200}
    assert adjacent
    for event in adjacent.values():
        assert event.subject_involved is False
        assert event.contextual is True
    assert adjacent[("shots", 0)].subject_role == "actor"
    assert adjacent[("kills", 0)].subject_role == "target"
    assert detail.contextual_event_count >= len(adjacent)
    # the adjacent opponent is contextual, not a direct participant
    participants = {participant.player_id: participant for participant in detail.participants}
    assert participants[OPPONENT].direct is False

    first_detail = service.detail(gen, SUBJECT, first.encounter_id, pre_seconds=5.0)
    assert first_detail.summary == first
    assert first_detail.subject_event_count == first.event_count == 2
    assert first_detail.summary.death_count == 1


def test_round_filter_reads_only_the_selected_round(harness: AnalyticsHarness) -> None:
    authored = tables(shots=[shot(0, 1050, SUBJECT), shot(1, 1200, SUBJECT), shot(2, 2500, SUBJECT)])
    authored["rounds"] = [
        round_row(1, start=ROUND_START, freeze_end=FREEZE_END, end=ROUND_END),
        round_row(2, start=2100, freeze_end=2200, end=3000),
    ]
    harness.publish(tables=authored)
    gen = harness.open()
    service = EncounterService(harness.pool)

    unfiltered = service.list(gen, SUBJECT)
    assert [summary.round_id for summary in unfiltered.encounters] == [1, 2]
    # the 1050 row is inside round 1's own span but before its usable start
    assert any("warmup/freeze time" in limitation for limitation in unfiltered.limitations)

    only_first = service.list(gen, SUBJECT, round_id=1)
    assert only_first.round_id == 1
    assert [summary.round_id for summary in only_first.encounters] == [1]
    assert only_first.total == 1
    assert any("round filter applied" in limitation for limitation in only_first.limitations)
    assert any("warmup/freeze time" in limitation for limitation in only_first.limitations)
    # round 2's subject rows were never read: had the whole match been scanned they
    # would have been classified as outside the selected round and reported.
    assert not any("outside every complete round" in limitation for limitation in only_first.limitations)


def test_subject_absence_and_invalid_lookups(harness: AnalyticsHarness) -> None:
    harness.publish(tables=tables(players=(OPPONENT, OPPONENT_TWO), shots=[shot(0, 1200, OPPONENT)]))
    absent_gen = harness.open()
    service = EncounterService(harness.pool)

    out = service.list(absent_gen, SUBJECT)
    assert out.total == 0 and out.encounters == []
    assert any("not present" in limitation for limitation in out.limitations)

    harness.publish(tables=tables(shots=[shot(0, 1200, OPPONENT)]))
    quiet_gen = harness.open()
    quiet = service.list(quiet_gen, SUBJECT)
    assert quiet.total == 0
    assert any("no recorded shots, damage, kills or assists" in limitation for limitation in quiet.limitations)

    with raised("INVALID_ARGUMENT"):
        service.detail(quiet_gen, SUBJECT, "not-an-encounter-id")
    with raised("NOT_FOUND"):
        service.detail(quiet_gen, SUBJECT, f"{ENCOUNTER_ID_PREFIX}-r99-0123456789abcdef")
    with raised("NOT_FOUND"):
        service.list(quiet_gen, SUBJECT, round_id=99)
    with raised("INVALID_ARGUMENT"):
        service.list(quiet_gen, SUBJECT, limit=0)
    with raised("INVALID_ARGUMENT"):
        service.list(quiet_gen, SUBJECT, gap_seconds=-1.0)
    with raised("INVALID_ARGUMENT"):
        service.list(quiet_gen, "not-a-steamid")
    with raised("INVALID_ARGUMENT"):
        service.list(quiet_gen, "7656119800")  # not a 17-digit individual SteamID64
    with raised("INVALID_ARGUMENT"):
        service.list(quiet_gen, "unresolved:roster:10")

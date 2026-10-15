"""Encounter context: anchors, contact offsets, utility intervals and exposure.

Behavior under test:

* snapshots are taken at the encounter's *observed* anchors plus this layer's
  contact offsets; an unavailable anchor or one whose tick falls outside the
  encounter window is skipped with a limitation instead of being fabricated;
* utility intervals are read verbatim from the tables of the reconstruction
  profile, matched to the window, and a smoke never blocks a sightline by itself;
* earliest exposure is qualified only where a sampled tick has a clear static
  sightline between living, stance-known endpoints, and a build mismatch keeps
  the answer unknown;
* participant tracks and the subject's facing delta are bounded, verbatim samples.

The pool is a real-schema fake because the anchor/window assertions need a
controlled timeline; the generation is a pinned object built exactly like
``Generation``, so nothing here touches a recorded demo.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import polars as pl
import pytest

from cs_demo_analyzer.analytics import ContextService
from cs_demo_analyzer.analytics.context import MAX_CROSS_PAIRS, UTILITY_SOURCES
from cs_demo_analyzer.domain.contracts import AppError, EvidenceRef
from cs_demo_analyzer.domain.encounters import (
    EncounterAnchor,
    EncounterDetail,
    EncounterGrouping,
    EncounterParticipant,
    EncounterSourceWindow,
    EncounterSummary,
)
from cs_demo_analyzer.domain.evidence import ReconstructionProvenance
from cs_demo_analyzer.domain.geometry import (
    GeometryCapabilities,
    GeometryComponent,
    SegmentResult,
)
from cs_demo_analyzer.domain.tables import RECONSTRUCTION_SCHEMAS

from .fixtures import DEMO_ID, PLAYER_A, PLAYER_B, TICK_RATE_HZ

RECON_PROFILE_KEY = "reconstruction-v1:awpy-3.0.0:schema-2:normalizer-1"
GEN_ID = "gen-00000000000000e1"
ROUND_ID = 1

WINDOW_START = 10_000
INTERACTION = 10_192  # window start + 192 ticks (D's default pre window)
WINDOW_END = 10_256  # INTERACTION + post
FLIP = INTERACTION + 10
TEAMMATE = "steam:76561198000000031"
OPPONENT_TWO = "steam:76561198000000047"
OTHER_ROUND = "steam:76561198000000059"
UNSIDED = "steam:76561198000000067"
ROUND_START = WINDOW_START - 500
ROUND_END = WINDOW_END + 4_000


def _frame(table: str, rows: list[dict]) -> pl.DataFrame:
    schema = RECONSTRUCTION_SCHEMAS[table]
    return pl.DataFrame(
        {name: pl.Series(name, [row.get(name) for row in rows], dtype=dtype) for name, dtype in schema.items()}
    ).select(list(schema))


class FakePool:
    """Read-only pool over authored frames with the real table schemas."""

    def __init__(self, tables: dict[str, list[dict]]) -> None:
        self.frames = {name: _frame(name, rows) for name, rows in tables.items()}

    def read(self, gen, table, *, columns=None, predicate=None, limit: int = 0) -> pl.DataFrame:
        if table not in self.frames:
            raise AppError("INVALID_ARGUMENT", f"generation has no table {table!r}", "read")
        frame = self.frames[table]
        if predicate is not None:
            frame = frame.filter(predicate)
        if columns is not None:
            frame = frame.select(list(columns))
        if limit and frame.height > limit:
            raise AppError("WINDOW_TOO_LARGE", f"{frame.height} > {limit}", "read")
        return frame


class FakeGeometry:
    def __init__(self, *, status="static_clear", match_status="exact", status_fn=None) -> None:
        self.status = status
        self.match_status = match_status
        self.status_fn = status_fn
        self.calls: list[tuple] = []

    def capabilities(self, map_name, demo_client_version=None) -> GeometryCapabilities:
        return GeometryCapabilities(
            map_name=map_name,
            prepared=True,
            physics=GeometryComponent(status="available", source="physics:vpk"),
            navigation=GeometryComponent(status="available", source="nav:vpk"),
            asset_id="asset-2000932",
            match_status=self.match_status,
            install_client_version="2000932",
            demo_client_version=demo_client_version,
        )

    def segment(self, map_name, start, end, demo_client_version=None) -> SegmentResult:
        self.calls.append((map_name, start, end))
        pair = self.status_fn(start, end) if self.status_fn is not None else None
        status, match = pair if pair is not None else (self.status, self.match_status)
        return SegmentResult(
            status=status,
            start=start,
            end=end,
            length=math.dist(start, end),
            match_status=match,
            source="triangle:1",
            asset_id="asset-2000932",
        )

    def navigation(self, map_name, start, end, demo_client_version=None):
        raise AssertionError("navigation must not be called unless requested")


def state(ordinal: int, tick: int, player_id: str | None, *, x: float, side: str | None, health: int = 100) -> dict:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "player_id": player_id,
        "x": x,
        "y": 0.0,
        "z": 0.0,
        "yaw": 0.0,
        "pitch": 0.0,
        "health": health,
        "armor": health,
        "side": side,
        "is_crouched": False,
    }


def build(
    *,
    tables: tuple[str, ...] = (),
    opponent_x: float | None = None,
    subject_health: int = 100,
    teammates: int = 1,
    opponents: int = 2,
    unsided: bool = False,
    states_extra: list[dict] | None = None,
):
    """One pinned generation over the encounter window, plus its fake pool."""
    rows: list[dict] = []
    ordinal = 0
    for tick in range(WINDOW_START, WINDOW_END + 1):
        if subject_health is not None:
            rows.append(state(ordinal, tick, PLAYER_A, x=0.0, side="ct" if subject_health > 0 else None, health=subject_health))
            ordinal += 1
        for index in range(teammates):
            player = TEAMMATE if index == 0 else f"steam:76561198000000{100 + index:04d}"
            rows.append(state(ordinal, tick, player, x=200.0 + 20 * index, side="ct"))
            ordinal += 1
        for index in range(opponents):
            player = PLAYER_B if index == 0 else (OPPONENT_TWO if index == 1 else f"steam:76561198000000{200 + index:04d}")
            if index == 0:
                x = opponent_x if opponent_x is not None else (100.0 if tick < FLIP else 800.0)
            else:
                x = -100.0 - 20 * index
            rows.append(state(ordinal, tick, player, x=x, side="t"))
            ordinal += 1
        if unsided and tick == INTERACTION:
            rows.append(state(ordinal, tick, UNSIDED, x=50.0, side=None))
            ordinal += 1
    if state_extra := states_extra:
        rows.extend(state_extra)

    pool_tables: dict[str, list[dict]] = {
        "player_state": rows,
        "rounds": [
            {
                "round_id": ROUND_ID,
                "source_round_num": ROUND_ID,
                "start_tick": ROUND_START,
                "freeze_end_tick": ROUND_START,
                "end_tick": ROUND_END,
                "official_end_tick": ROUND_END,
                "winner_side": "ct",
                "reason_code": 7,
            }
        ],
        "players": [
            {"player_id": PLAYER_A, "steam_id": "76561198057213632", "name": "alpha", "side": "ct"},
            {"player_id": PLAYER_B, "steam_id": None, "name": "bravo", "side": "t"},
        ],
    }
    if tables:
        for table in tables:
            pool_tables[table] = pool_tables.get(table, [])
    pool = FakePool(pool_tables)
    gen = SimpleNamespace(
        demo_id=DEMO_ID,
        generation_id=GEN_ID,
        profile_key=RECON_PROFILE_KEY,
        tick_rate_hz=TICK_RATE_HZ,
        rounds=pool.frames["rounds"],
        players=pool.frames["players"],
        manifest=SimpleNamespace(
            map_name="de_inferno",
            demo_client_version="2000930",
            tables={name: SimpleNamespace() for name in pool_tables},
        ),
    )
    return pool, gen


def anchor(kind: str, tick: int | None, *, anchor_id: str | None = None, recorded: bool = True,
           dataset: str | None = "shots", ordinal: int | None = 0, resolution: str | None = None) -> EncounterAnchor:
    return EncounterAnchor(
        anchor_id=anchor_id or f"{kind}:{tick}",
        kind=kind,
        tick=tick,
        status="observed" if tick is not None else "unavailable",
        evidence_kind="recorded" if recorded else "computed",
        dataset=dataset,
        row_ordinal=ordinal if recorded else None,
        resolution=resolution,
    )


def detail(*, anchors=None, generation_id: str = GEN_ID, subject: str = PLAYER_A,
           participants: list[EncounterParticipant] | None = None,
           window: tuple[int, int] = (WINDOW_START, WINDOW_END)) -> EncounterDetail:
    grouping = EncounterGrouping(
        gap_seconds=3.0,
        pre_seconds=3.0,
        post_seconds=1.0,
        tick_rate_hz=TICK_RATE_HZ,
        gap_ticks=192,
        pre_ticks=192,
        post_ticks=64,
    )
    summary = EncounterSummary(
        encounter_id="enc-v2-r1-00000000000000ab",
        demo_id=DEMO_ID,
        generation_id=generation_id,
        profile_key=RECON_PROFILE_KEY,
        round_id=ROUND_ID,
        subject_id=subject,
        start_tick=INTERACTION,
        end_tick=INTERACTION + 20,
        first_interaction_tick=INTERACTION,
        last_interaction_tick=INTERACTION + 20,
        participant_ids=[PLAYER_B],
        anchors=anchors
        if anchors is not None
        else [
            anchor("first_interaction", INTERACTION),
            anchor("kill", INTERACTION + 10, dataset="kills", ordinal=4),
            anchor("pre_contact", WINDOW_START, recorded=False, dataset=None),
        ],
        event_count=2,
        kill_count=1,
        death_count=0,
        assist_count=0,
        subject_died=False,
        grouping=grouping,
        limitations=["grouping is heuristic: interactions closer than gap_seconds form one encounter"],
    )
    return EncounterDetail(
        summary=summary,
        source_window=EncounterSourceWindow(
            round_id=ROUND_ID,
            round_start_tick=ROUND_START,
            round_end_tick=ROUND_END,
            window_start_tick=window[0],
            window_end_tick=window[1],
            truncated_start=False,
            truncated_end=False,
        ),
        grouping=grouping,
        events=[],
        participants=participants
        if participants is not None
        else [
            EncounterParticipant(
                player_id=PLAYER_B,
                relation="opponent",
                side="t",
                subject_side="ct",
                roles=["victim"],
                first_seen_tick=INTERACTION,
                last_seen_tick=INTERACTION + 20,
                event_count=2,
                direct=True,
            )
        ],
        subject_event_count=2,
        contextual_event_count=0,
        subject_trajectory=[],
        trajectory_stride=1,
        trajectory_missing_ranges=[],
        provenance=ReconstructionProvenance(
            demo_id=DEMO_ID,
            generation_id=generation_id,
            profile_key=RECON_PROFILE_KEY,
            method="subject-event-grouping",
            method_version="1",
            map_name="de_inferno",
        ),
        limitations=[],
    )


# --------------------------------------------------------------------------- #
# utility
# --------------------------------------------------------------------------- #
def test_utility_intervals_are_read_verbatim_and_matched_to_the_window() -> None:
    pool, gen = build(tables=("smokes", "fires", "blinds"))
    pool.frames["smokes"] = _frame(
        "smokes",
        [
            {
                "row_ordinal": 0,
                "start_tick": WINDOW_START - 40,
                "end_tick": WINDOW_END + 500,
                "entity_id": 77,
                "entity_serial": 3,
                "owner_id": None,
                "owner_side": "unknown",
                "x": 10.0,
                "y": 20.0,
                "z": 30.0,
                "still_active_at_end": True,
            }
        ],
    )
    pool.frames["fires"] = _frame(
        "fires",
        [
            {
                "row_ordinal": 0,
                "start_tick": WINDOW_END + 900,
                "end_tick": WINDOW_END + 1_000,
                "kind": "inferno",
                "owner_id": None,
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "still_active_at_end": False,
            }
        ],
    )
    pool.frames["blinds"] = _frame(
        "blinds",
        [
            {
                "row_ordinal": 0,
                "tick": WINDOW_START + 10,
                "attacker_id": PLAYER_B,
                "attacker_side": "t",
                "victim_id": PLAYER_A,
                "victim_side": "ct",
                "victim_x": 0.0,
                "victim_y": 0.0,
                "victim_z": 0.0,
                "duration_seconds": 0.5,
            }
        ],
    )
    service = ContextService(pool, FakeGeometry())

    assert service.utility_tables(gen) == ["smokes", "fires", "blinds"]
    context = service.encounter(gen, detail())

    kinds = sorted(fact.kind for fact in context.utility)
    assert kinds == ["flash", "smoke"]
    smoke = next(fact for fact in context.utility if fact.kind == "smoke")
    assert smoke.start_tick == WINDOW_START - 40
    assert smoke.end_tick == WINDOW_END + 500  # verbatim, never clipped
    assert smoke.owner_id is None
    assert smoke.semantics_reliable is True
    assert smoke.details["still_active_at_end"] is True
    assert smoke.details["entity_id"] == 77
    assert any("ends after the queried range end" in note for note in smoke.limitations)
    assert any("not evidence of an unknown player" in note for note in smoke.limitations)

    flash = next(fact for fact in context.utility if fact.kind == "flash")
    assert flash.start_tick == WINDOW_START + 10
    assert flash.end_tick == WINDOW_START + 10 + int(round(0.5 * TICK_RATE_HZ))
    assert flash.owner_id == PLAYER_B
    assert any("expire tick is derived" in note for note in flash.limitations)

    # an interval that starts after the window is not part of this encounter
    assert not [fact for fact in context.utility if fact.kind == "inferno"]
    assert not any("utility table fires is not present" in note for note in context.limitations)
    assert not any("utility table smokes is not present" in note for note in context.limitations)


def test_a_smoke_never_blocks_a_static_sightline_by_itself() -> None:
    pool, gen = build(tables=("smokes",))
    pool.frames["smokes"] = _frame(
        "smokes",
        [
            {
                "row_ordinal": 0,
                "start_tick": WINDOW_START,
                "end_tick": WINDOW_END,
                "owner_id": None,
                "owner_side": "unknown",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "still_active_at_end": False,
            }
        ],
    )
    geometry = FakeGeometry(status="static_clear")
    service = ContextService(pool, geometry)

    snapshot = service.at(gen, PLAYER_A, INTERACTION, cross_pairs=True)

    assert [fact.kind for fact in snapshot.utility] == ["smoke"]
    assert all(relation.static_effective_status == "static_clear" for relation in snapshot.relations)
    assert snapshot.counts.opponent_static_clear == 2
    assert snapshot.counts.opponent_static_unknown == 0
    # live grenade projectiles and per-tick grenade counts are deliberately not read here
    assert snapshot.capabilities.utility.status == "partial"


def test_utility_facts_trace_their_source_row() -> None:
    pool, gen = build(tables=("smokes", "blinds"))
    pool.frames["smokes"] = _frame(
        "smokes",
        [
            {
                "row_ordinal": 5, "start_tick": WINDOW_START + 3, "end_tick": WINDOW_END,
                "entity_id": 9, "entity_serial": 1, "owner_id": None, "owner_side": "unknown",
                "x": 1.0, "y": 2.0, "z": 3.0, "still_active_at_end": False,
            }
        ],
    )
    pool.frames["blinds"] = _frame(
        "blinds",
        [
            {
                "row_ordinal": 11, "tick": WINDOW_START + 20, "attacker_id": PLAYER_B, "attacker_side": "t",
                "victim_id": PLAYER_A, "victim_side": "ct", "victim_x": 0.0, "victim_y": 0.0, "victim_z": 0.0,
                "duration_seconds": 1.0,
            }
        ],
    )
    service = ContextService(pool, FakeGeometry())

    context = service.encounter(gen, detail())
    by_kind = {fact.kind: fact for fact in context.utility}

    smoke = by_kind["smoke"]
    assert smoke.evidence is not None
    assert smoke.evidence.dataset == "smokes"
    assert smoke.evidence.row_ordinal == 5
    assert smoke.evidence.tick == smoke.start_tick == WINDOW_START + 3
    assert smoke.evidence.round_id == ROUND_ID
    assert smoke.evidence.generation_id == GEN_ID and smoke.evidence.demo_id == DEMO_ID
    assert smoke.evidence.player_ids == []
    assert smoke.evidence_kind == "recorded"

    flash = by_kind["flash"]
    assert flash.evidence is not None
    assert flash.evidence.dataset == "blinds"
    assert flash.evidence.row_ordinal == 11
    assert flash.evidence.tick == flash.start_tick == WINDOW_START + 20
    assert flash.evidence.player_ids == [PLAYER_B]
    assert flash.evidence_kind == "computed"  # upstream reconstruction, not a raw event
    assert any("upstream reconstruction" in note for note in flash.limitations)


def test_a_generation_without_utility_tables_reports_utility_unavailable() -> None:
    pool, gen = build()
    service = ContextService(pool, FakeGeometry())

    context = service.encounter(gen, detail())

    assert context.utility == []
    assert context.capabilities.utility.status == "unavailable"
    assert any("publishes no utility table" in note for note in context.capabilities.utility.limitations)
    assert pool.frames.keys() >= {"player_state"}
    assert all(source.table not in gen.manifest.tables for source in UTILITY_SOURCES)


# --------------------------------------------------------------------------- #
# anchors and offsets
# --------------------------------------------------------------------------- #
def test_snapshots_cover_anchors_offsets_and_the_window() -> None:
    pool, gen = build()
    service = ContextService(pool, FakeGeometry())

    context = service.encounter(gen, detail())

    # every planned tick is represented exactly once, whichever alias supplied it
    expected = {
        WINDOW_START,  # D's pre_contact anchor, this layer's 3s pre offset and the window start
        WINDOW_END,  # post_contact anchor / window end
        INTERACTION,  # first_interaction anchor
        INTERACTION + 10,  # kill anchor
        INTERACTION + 32,  # post offset
        INTERACTION - 64,  # 1s pre offset
        INTERACTION - 128,  # 2s pre offset
    }
    assert {entry.requested_tick for entry in context.snapshots} == expected
    assert len(context.snapshots) == len(expected)
    assert (context.start_tick, context.end_tick) == (WINDOW_START, WINDOW_END)
    assert (context.interaction_start_tick, context.interaction_end_tick) == (INTERACTION, INTERACTION + 20)
    assert context.encounter_id == "enc-v2-r1-00000000000000ab"
    assert context.round_id == ROUND_ID

    by_tick = {entry.requested_tick: entry for entry in context.snapshots}
    assert by_tick[INTERACTION + 32].offset_seconds == pytest.approx(0.5)

    # D's pre_contact anchor and this layer's 3s pre offset share a tick: merged, not duplicated
    merged = by_tick[WINDOW_START]
    assert "pre_offset_3s" in merged.reason and "window_start" in merged.reason
    assert "encounter anchor pre_contact" in merged.reason

    assert by_tick[INTERACTION + 10].kind == "recorded"
    assert by_tick[INTERACTION + 10].anchor_kind == "kill"
    assert by_tick[INTERACTION - 64].kind == "computed" and by_tick[INTERACTION - 64].anchor_kind is None
    assert by_tick[INTERACTION].snapshot.provenance.generation_id == GEN_ID


def test_unavailable_and_out_of_window_anchors_are_skipped_with_limitations() -> None:
    pool, gen = build()
    service = ContextService(pool, FakeGeometry())
    anchors = [
        anchor("first_interaction", INTERACTION),
        anchor("first_damage", None, recorded=False, dataset=None),  # unavailable, never fabricated
        anchor("resolution", ROUND_END, recorded=False, dataset=None, resolution="round_end"),
    ]

    context = service.encounter(gen, detail(anchors=anchors))

    names = [entry.name for entry in context.snapshots]
    assert not any("first_damage" in name for name in names)
    assert not any("resolution" in name for name in names)
    assert any("first_damage" in note and "unavailable" in note for note in context.limitations)
    assert any("resolution" in note and "outside the encounter window" in note for note in context.limitations)


def test_encounter_refuses_a_detail_from_another_generation() -> None:
    pool, gen = build()
    service = ContextService(pool, FakeGeometry())

    with pytest.raises(AppError) as caught:
        service.encounter(gen, detail(generation_id="gen-other"))

    assert caught.value.code == "INVALID_ARGUMENT"
    assert "belongs to" in caught.value.message


# --------------------------------------------------------------------------- #
# exposure
# --------------------------------------------------------------------------- #
def test_exposure_is_qualified_at_the_first_sampled_clear_tick() -> None:
    pool, gen = build()
    geometry = FakeGeometry(
        status_fn=lambda start, end: ("static_clear", "exact") if end[0] >= 500 else ("static_blocked", "exact")
    )
    service = ContextService(pool, geometry)

    context = service.encounter(gen, detail())
    exposure = context.exposure

    assert exposure.status == "qualified"
    assert exposure.earliest_exposure_player_id == PLAYER_B
    assert exposure.earliest_exposure_tick is not None
    assert FLIP <= exposure.earliest_exposure_tick < FLIP + exposure.sampling.stride_ticks
    assert exposure.sampling.start_tick == WINDOW_START and exposure.sampling.end_tick == WINDOW_END
    assert 1 < exposure.sampling.stride_ticks <= math.ceil((WINDOW_END - WINDOW_START + 1) / 64)
    assert exposure.sampling.samples == len(exposure.sampling.ticks) <= 65
    assert exposure.sampling.ticks[-1] == WINDOW_END  # the window end is always sampled
    assert exposure.sampling.ticks[0] == WINDOW_START
    assert exposure.sampling.subject_alive_samples > 0

    opponent = next(entry for entry in exposure.opponents if entry.player_id == PLAYER_B)
    assert opponent.blocked_ticks > 0 and opponent.clear_ticks > 0
    assert opponent.earliest_clear_tick == exposure.earliest_exposure_tick
    assert opponent.first_alive_tick == WINDOW_START
    assert any("earliest *sampled* tick" in note for note in exposure.limitations)
    assert any("installed map build" in note for note in exposure.limitations)

    # the encounter's pre-contact snapshot really is blocked: the scan is time-dependent
    first = context.snapshots[0]
    assert first.snapshot.relations[0].static_effective_status in ("static_blocked", "static_clear")
    blocked_snapshot = next(
        entry for entry in context.snapshots if entry.requested_tick == WINDOW_START
    )
    assert blocked_snapshot.snapshot.relations[0].static_effective_status == "static_blocked"


def test_a_sightline_that_only_clears_at_the_window_end_is_still_sampled() -> None:
    """Regression: a strided grid that stopped before ``hi`` would miss the answer."""
    pool, gen = build()
    # clear only from the very last tick of the window onwards
    geometry = FakeGeometry(
        status_fn=lambda start, end: ("static_clear", "exact") if end[0] > 1_000 else ("static_blocked", "exact")
    )
    rows = pool.frames["player_state"]
    # move only the other players to the far position at the final tick
    rows = rows.with_columns(
        pl.when((pl.col("tick") == WINDOW_END) & (pl.col("player_id") != PLAYER_A))
        .then(pl.lit(2_000.0))
        .otherwise(pl.col("x"))
        .alias("x")
    )
    pool.frames["player_state"] = rows

    context = ContextService(pool, geometry).encounter(gen, detail())
    exposure = context.exposure

    assert exposure.sampling.ticks[-1] == WINDOW_END
    assert exposure.status == "qualified"
    assert exposure.earliest_exposure_tick == WINDOW_END
    assert exposure.earliest_exposure_player_id in {PLAYER_B, OPPONENT_TWO}


def test_a_build_mismatch_keeps_exposure_unknown() -> None:
    pool, gen = build()
    geometry = FakeGeometry(status_fn=lambda start, end: ("static_clear", "mismatch"))
    service = ContextService(pool, geometry)

    context = service.encounter(gen, detail())
    exposure = context.exposure

    assert exposure.status == "unknown"
    assert exposure.earliest_exposure_tick is None
    assert exposure.earliest_exposure_player_id is None
    assert exposure.mismatches and "do not match the recording" in exposure.mismatches[0]
    opponent = exposure.opponents[0]
    # a mismatched asset can never be promoted: no clear tick and no earliest exposure
    assert opponent.mismatched_ticks > 0
    assert opponent.clear_ticks == 0
    assert opponent.earliest_clear_tick is None
    assert opponent.checked_ticks > 0
    # the verbatim result is kept, but nothing is promoted
    assert context.snapshots[0].snapshot.relations[0].static_sightline.status == "static_clear"
    assert context.snapshots[0].snapshot.relations[0].static_effective_status == "unknown"


def test_a_dead_subject_has_recorded_state_but_no_exposure() -> None:
    pool, gen = build(subject_health=0)
    service = ContextService(pool, FakeGeometry())

    context = service.encounter(gen, detail())

    assert context.exposure.status == "not_applicable"
    assert context.exposure.earliest_exposure_tick is None
    assert context.exposure.sampling.subject_alive_samples == 0
    assert all(
        entry.snapshot.subject is not None and entry.snapshot.subject.alive is False
        for entry in context.snapshots
    )
    assert all(entry.snapshot.relations == [] for entry in context.snapshots)
    assert all(entry.snapshot.inactive_relations for entry in context.snapshots)
    assert any("no exposure" in note for note in context.exposure.limitations)


def test_exposure_is_unsupported_without_geometry() -> None:
    pool, gen = build()
    service = ContextService(pool, None)

    context = service.encounter(gen, detail())

    assert context.exposure.status == "unsupported"
    assert context.exposure.sampling.samples > 0
    assert context.exposure.sampling.subject_alive_samples == 0
    assert any("geometry service unavailable" in note for note in context.exposure.limitations)


# --------------------------------------------------------------------------- #
# pairs, tracks and facing
# --------------------------------------------------------------------------- #
def test_cross_pairs_are_bounded_and_skip_players_without_a_recorded_side() -> None:
    pool, gen = build(teammates=5, opponents=5, unsided=True)
    service = ContextService(pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, INTERACTION, cross_pairs=True)

    assert len(snapshot.pair_relations) == MAX_CROSS_PAIRS
    assert any(f"beyond the {MAX_CROSS_PAIRS}-pair bound" in note for note in snapshot.limitations)
    assert any("no recorded side and were placed in no pair" in note for note in snapshot.limitations)
    distances = [pair.distance_2d for pair in snapshot.pair_relations]
    assert distances == sorted(distances)
    assert all(pair.scope == "installed_map_build" for pair in snapshot.pair_relations)
    assert all(pair.static_effective_status == "static_clear" for pair in snapshot.pair_relations)
    assert snapshot.counts.cross_pairs_evaluated == MAX_CROSS_PAIRS
    assert all(pair.opponent_id != UNSIDED for pair in snapshot.pair_relations)


def test_cross_pairs_are_off_unless_requested() -> None:
    pool, gen = build()
    geometry = FakeGeometry()
    service = ContextService(pool, geometry)

    snapshot = service.at(gen, PLAYER_A, INTERACTION)

    assert snapshot.pair_relations == []
    assert snapshot.counts.cross_pairs_evaluated == 0
    # only the subject's own relations were measured
    assert len(geometry.calls) == len(snapshot.relations)


def test_angular_spread_reports_the_geometry_between_opponent_directions() -> None:
    pool, gen = build(opponents=2, opponent_x=100.0)
    service = ContextService(pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, INTERACTION)

    assert snapshot.angular_spread.opponent_count == 2
    directions = {entry.player_id: entry for entry in snapshot.opponent_directions}
    assert set(directions) == {PLAYER_B, OPPONENT_TWO}
    assert directions[PLAYER_B].bearing_degrees == pytest.approx(0.0)
    assert directions[OPPONENT_TWO].bearing_degrees == pytest.approx(180.0)
    assert snapshot.angular_spread.span_degrees == pytest.approx(180.0)
    assert snapshot.angular_spread.max_pair_separation_degrees == pytest.approx(180.0)
    assert snapshot.angular_spread.subject_yaw_recorded is True


def test_angular_spread_needs_two_opponents() -> None:
    pool, gen = build(opponents=1)
    service = ContextService(pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, INTERACTION)

    assert snapshot.angular_spread.opponent_count == 1
    assert snapshot.angular_spread.span_degrees is None
    assert snapshot.angular_spread.max_pair_separation_degrees is None
    assert any("at least two opponent directions" in note for note in snapshot.angular_spread.limitations)


def test_participant_tracks_and_the_facing_delta_are_verbatim_and_bounded() -> None:
    pool, gen = build()
    service = ContextService(pool, FakeGeometry())

    context = service.encounter(gen, detail())

    subject = context.subject_track
    assert subject is not None and subject.is_subject is True
    assert subject.from_tick == WINDOW_START and subject.to_tick == WINDOW_END
    assert subject.stride_ticks == math.ceil((WINDOW_END - WINDOW_START + 1) / 128)
    assert 0 < len(subject.samples) <= 128
    assert subject.samples[0].tick == WINDOW_START and subject.samples[-1].tick == WINDOW_END
    assert subject.missing_samples == 0
    assert subject.samples[0].tick == WINDOW_START and subject.samples[0].health == 100
    assert any("never interpolated" in note for note in subject.limitations)

    assert [track.player_id for track in context.participant_tracks] == [PLAYER_B]
    assert context.participant_tracks[0].relation == "opponent"

    facing = context.subject_facing_delta
    assert facing is not None
    assert (facing.from_tick, facing.to_tick) == (WINDOW_START, WINDOW_END)
    assert facing.delta_degrees == pytest.approx(0.0)
    assert facing.stride_ticks == subject.stride_ticks


def test_participant_tracks_report_missing_samples_instead_of_filling_them() -> None:
    extra = [state(9_000, tick, OTHER_ROUND, x=300.0, side="t") for tick in range(WINDOW_START, WINDOW_END + 1, 64)]
    pool, gen = build(states_extra=extra)
    service = ContextService(pool, FakeGeometry())
    participants = [
        EncounterParticipant(
            player_id=OTHER_ROUND,
            relation="opponent",
            side="t",
            subject_side="ct",
            roles=[],
            first_seen_tick=WINDOW_START,
            last_seen_tick=WINDOW_END,
            event_count=1,
            direct=False,
        )
    ]

    context = service.encounter(gen, detail(participants=participants))

    track = context.participant_tracks[0]
    assert track.missing_samples > 0
    assert 0 < len(track.samples) < len(track.samples) + track.missing_samples
    assert track.stride_ticks == math.ceil((WINDOW_END - WINDOW_START + 1) / 128)


def test_detail_limitations_are_carried_into_the_context() -> None:
    pool, gen = build()
    service = ContextService(pool, FakeGeometry())
    encounter = detail()

    context = service.encounter(gen, encounter)

    for note in encounter.summary.limitations:
        assert note in context.limitations


# --------------------------------------------------------------------------- #
# recorded lifecycle explains missing state
# --------------------------------------------------------------------------- #
DISCONNECT_TICK = WINDOW_END + 40


def lifecycle_rows(*rows: dict) -> list[dict]:
    return [
        {
            "row_ordinal": index,
            "tick": row["tick"],
            "kind": row["kind"],
            "player_id": row.get("player_id"),
            "user_slot": row.get("user_slot", f"{index + 1}"),
            "pawn_handle": row.get("pawn_handle"),
            "team": row.get("team"),
            "previous_team": row.get("previous_team"),
            "is_bot": row.get("is_bot"),
            "reason_code": row.get("reason_code"),
            "ever_fully_connected": row.get("ever_fully_connected"),
        }
        for index, row in enumerate(rows)
    ]


def test_missing_subject_state_is_explained_by_a_recorded_disconnect() -> None:
    rows = lifecycle_rows(
        {"tick": WINDOW_START, "kind": "spawn", "user_slot": "7", "team": "ct"},
        {
            "tick": DISCONNECT_TICK,
            "kind": "disconnect",
            "player_id": PLAYER_A,
            "reason_code": 79,
            "ever_fully_connected": True,
        },
        {"tick": WINDOW_START + 1, "kind": "connect", "user_slot": "7"},
    )
    pool, gen = build(tables=("player_lifecycle",))
    pool.frames["player_lifecycle"] = _frame("player_lifecycle", rows)
    service = ContextService(pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, DISCONNECT_TICK + 100)

    assert snapshot.exact is False and snapshot.subject is None
    assert snapshot.lifecycle_before is not None
    assert snapshot.lifecycle_before.kind == "disconnect"
    assert snapshot.lifecycle_before.tick == DISCONNECT_TICK
    assert snapshot.lifecycle_before.reason_code == 79
    assert snapshot.lifecycle_before.ever_fully_connected is True
    assert snapshot.lifecycle_before.player_id == PLAYER_A
    assert snapshot.lifecycle_after is None
    assert snapshot.lifecycle_unattributed_rows == 2  # spawn + connect carry only a slot
    assert any("never reported as inactivity" in note for note in snapshot.limitations)
    assert any("lifecycle rows bracket this tick" in note for note in snapshot.limitations)
    assert snapshot.capabilities.lifecycle.status == "available"


def test_lifecycle_rows_without_a_resolved_account_are_only_counted() -> None:
    pool, gen = build(tables=("player_lifecycle",))
    pool.frames["player_lifecycle"] = _frame(
        "player_lifecycle",
        lifecycle_rows(
            {"tick": WINDOW_START, "kind": "spawn", "user_slot": "7"},
            {"tick": WINDOW_START + 5, "kind": "team_change", "user_slot": "7", "team": "t", "previous_team": "ct"},
        ),
    )
    service = ContextService(pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, WINDOW_END + 500)

    assert snapshot.lifecycle_before is None and snapshot.lifecycle_after is None
    assert snapshot.lifecycle_unattributed_rows == 2
    assert not any("lifecycle rows bracket" in note for note in snapshot.limitations)


def test_encounter_reports_the_subjects_lifecycle_rows_inside_the_window() -> None:
    pool, gen = build(tables=("player_lifecycle",))
    pool.frames["player_lifecycle"] = _frame(
        "player_lifecycle",
        lifecycle_rows(
            {"tick": WINDOW_START + 8, "kind": "spawn", "player_id": PLAYER_A, "team": "ct"},
            {"tick": WINDOW_END + 900, "kind": "disconnect", "player_id": PLAYER_A, "reason_code": 59},
            {"tick": WINDOW_START + 9, "kind": "spawn", "user_slot": "3"},
        ),
    )
    service = ContextService(pool, FakeGeometry())

    context = service.encounter(gen, detail())

    assert [fact.kind for fact in context.lifecycle] == ["spawn"]
    assert context.lifecycle[0].tick == WINDOW_START + 8
    assert context.lifecycle[0].team == "ct"
    assert context.lifecycle_unattributed_rows == 1

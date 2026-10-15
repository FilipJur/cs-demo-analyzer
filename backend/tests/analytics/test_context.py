"""Context reconstruction: exact ticks, dynamic membership, geometry and exposure.

The behavior under test:

* a snapshot is pinned to one generation and reports the exact tick, or says so;
* membership and relation kind come from the side each row carries *at that
  tick*, so a side swap flips teammate/opponent with no carry-forward;
* dead players (``health == 0``), players with unknown health and rows with a
  null ``player_id`` are recorded and counted but never become active relations
  and are never measured by geometry or joined to a player by position;
* static geometry is never promoted: ``unknown``/``unsupported`` and results
  produced against mismatched installed assets are never "clear";
* eye positions are stance-based *estimates* (standing 64 / crouched 46) because
  no recorded view origin exists in this profile;
* utility facts are read verbatim from the published tables and a smoke never
  blocks a sightline by itself.
"""

from __future__ import annotations

import math

import pytest

from cs_demo_analyzer.analytics import ContextService
from cs_demo_analyzer.analytics.context import MAX_RELATIONS, UTILITY_SOURCES
from cs_demo_analyzer.domain.contracts import AppError
from cs_demo_analyzer.domain.geometry import (
    GeometryCapabilities,
    GeometryComponent,
    NavigationResult,
    SegmentResult,
)

from .fixtures import (  # noqa: F401 - `harness` is imported so pytest registers the fixture
    DEMO_ID,
    PLAYER_A,
    PLAYER_B,
    TICK_RATE_HZ,
    AnalyticsHarness,
    harness,
    players_rows,
    round_row,
    state_row,
)

PLAYER_C = "steam:76561198000000031"
PLAYER_D = "steam:76561198000000047"
GEN_ID = "gen-000000000000000e"
PROFILE_KEY = "foundation-v1:awpy-3.0.0:schema-1:normalizer-1"
RECON_PROFILE_KEY = "reconstruction-v1:awpy-3.0.0:schema-2:normalizer-1"

STANDING = 64.0
CROUCHED = 46.0


def srow(
    ordinal: int,
    tick: int,
    player_id: str | None,
    *,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    yaw: float = 0.0,
    side: str | None = "ct",
    health: int | None = -1,
    health_null: bool = False,
    crouched: bool = False,
) -> dict:
    """One state row with the exact field control these tests need."""
    row = state_row(ordinal, tick, player_id, None if health == -1 else health, x=x, y=y)
    row.update(z=z, yaw=yaw, is_crouched=crouched, side=side if _alive(row) else None)
    if health_null:
        row["health"] = None
        row.update(armor=None, money=None, active_weapon=None, side=side)
    return row


def _alive(row: dict) -> bool:
    return row.get("health") is not None and int(row["health"]) > 0


class FakeGeometry:
    """Deterministic stand-in for the injected slice-C service."""

    def __init__(
        self,
        *,
        status: str = "static_clear",
        match_status: str = "exact",
        component: str = "available",
        status_fn=None,
        nav_requires_origin_z: bool = False,
    ) -> None:
        self.status = status
        self.match_status = match_status
        self.component = component
        self.status_fn = status_fn
        self.nav_requires_origin_z = nav_requires_origin_z
        self.calls: list[tuple] = []
        self.nav_calls: list[tuple] = []

    def capabilities(self, map_name: str, demo_client_version: str | None = None) -> GeometryCapabilities:
        return GeometryCapabilities(
            map_name=map_name,
            prepared=True,
            physics=GeometryComponent(status=self.component, source="physics:maps/de_inferno.vpk"),
            navigation=GeometryComponent(status="available", source="nav:de_inferno.nav"),
            asset_id="asset-1",
            match_status=self.match_status,
            demo_client_version=demo_client_version,
        )

    def segment(self, map_name, start, end, demo_client_version=None) -> SegmentResult:
        self.calls.append((map_name, start, end, demo_client_version))
        pair = self.status_fn(start, end) if self.status_fn is not None else None
        status, match = pair if pair is not None else (self.status, self.match_status)
        return SegmentResult(
            status=status,
            start=start,
            end=end,
            length=math.dist(start, end),
            source="hull:17",
            asset_id="asset-1",
            match_status=match,
        )

    def navigation(self, map_name, start, end, demo_client_version=None) -> NavigationResult:
        """A nav service whose areas only accept floor-level points (plane tolerance ±24)."""
        self.nav_calls.append((start, end))
        distance = math.dist(start, end)
        if self.nav_requires_origin_z and (start[2] > 24.0 or end[2] > 24.0):
            return NavigationResult(
                status="unavailable",
                start=start,
                end=end,
                direct_distance=distance,
                connected=False,
                asset_id="asset-1",
                limitations=["point is outside the nav area plane"],
            )
        return NavigationResult(
            status="available",
            start=start,
            end=end,
            direct_distance=distance,
            path_distance=distance * 1.5,
            connected=True,
            asset_id="asset-1",
        )


def _publish(harness: AnalyticsHarness, states: list[dict], rounds: list[dict] | None = None, **overrides) -> None:
    harness.publish(
        tables={
            "player_state": states,
            "rounds": rounds if rounds is not None else [round_row(1, start=50, freeze_end=50, end=900)],
            "players": players_rows(PLAYER_A, PLAYER_B, PLAYER_C, PLAYER_D),
        },
        **overrides,
    )


# --------------------------------------------------------------------------- #
# pinning and exact ticks
# --------------------------------------------------------------------------- #
def test_snapshot_is_generation_pinned_and_reports_the_exact_tick(harness: AnalyticsHarness) -> None:
    _publish(harness, [srow(0, 100, PLAYER_A), srow(1, 100, PLAYER_B, x=100.0, side="t")])
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, 100)

    assert snapshot.generation_id == gen.generation_id
    assert snapshot.profile_key == gen.profile_key
    assert snapshot.demo_id == gen.demo_id
    assert snapshot.provenance.generation_id == gen.generation_id
    assert snapshot.provenance.method == "context.exact_tick"
    assert snapshot.provenance.information_scope == "omniscient_replay"
    assert snapshot.tick == 100 and snapshot.actual_tick == 100
    assert snapshot.exact is True and snapshot.gap_ticks == 0
    assert snapshot.tick_rate_hz == TICK_RATE_HZ
    assert snapshot.round_id == 1
    assert snapshot.subject is not None and snapshot.subject.row_ordinal == 0
    assert snapshot.subject.evidence is not None and snapshot.subject.evidence.row_ordinal == 0
    assert snapshot.subject.evidence.dataset == "player_state"
    assert snapshot.subject_alive is True


def test_a_tick_without_recorded_state_is_reported_and_never_snapped(harness: AnalyticsHarness) -> None:
    _publish(harness, [srow(0, 100, PLAYER_A), srow(1, 100, PLAYER_B, x=100.0, side="t")])
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, 999)

    assert snapshot.exact is False
    assert snapshot.actual_tick is None and snapshot.gap_ticks is None
    assert snapshot.subject is None and snapshot.subject_alive is False
    assert snapshot.relations == [] and snapshot.inactive_relations == []
    assert snapshot.counts.state_rows == 0
    assert any("no player_state rows at tick 999" in note for note in snapshot.limitations)


def test_a_subject_absent_from_the_generation_is_reported_verbatim(harness: AnalyticsHarness) -> None:
    _publish(harness, [srow(0, 100, PLAYER_A)])
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    missing_at_tick = service.at(gen, PLAYER_B, 100)
    unknown_player = service.at(gen, "steam:76561198999999999", 100)

    assert missing_at_tick.subject is None and missing_at_tick.exact is True
    assert [row.player_id for row in missing_at_tick.participants] == [PLAYER_A]
    assert missing_at_tick.participants[0].evidence.row_ordinal == 0
    assert missing_at_tick.relations == []
    assert unknown_player.subject is None
    assert unknown_player.subject_id == "steam:76561198999999999"
    assert [row.player_id for row in unknown_player.participants] == [PLAYER_A]
    assert unknown_player.relations == []


@pytest.mark.parametrize(
    "tick,subject_id,message",
    [(-1, PLAYER_A, "non-negative"), (100, "", "subject_id")],
)
def test_invalid_arguments_are_typed_errors(harness: AnalyticsHarness, tick, subject_id, message) -> None:
    _publish(harness, [srow(0, 100, PLAYER_A)])
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    with pytest.raises(AppError) as caught:
        service.at(gen, subject_id, tick)

    assert caught.value.code == "INVALID_ARGUMENT"
    assert message in caught.value.message


# --------------------------------------------------------------------------- #
# dynamic tick-side membership
# --------------------------------------------------------------------------- #
def test_relation_kind_is_resolved_from_the_side_at_that_tick(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, side="ct"),
            srow(1, 100, PLAYER_B, x=100.0, side="ct"),  # same side at 100
            srow(2, 200, PLAYER_A, side="ct"),
            srow(3, 200, PLAYER_B, x=100.0, side="t"),  # side swapped at 200
            srow(4, 300, PLAYER_A, side="ct"),
            srow(5, 300, PLAYER_B, x=100.0, side=None),  # side missing at 300
        ],
    )
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    teammate = service.at(gen, PLAYER_A, 100)
    opponent = service.at(gen, PLAYER_A, 200)
    unknown = service.at(gen, PLAYER_A, 300)

    assert [relation.relation for relation in teammate.relations] == ["teammate"]
    assert teammate.counts.same_side == 1 and teammate.counts.opposite_side == 0
    assert [relation.relation for relation in opponent.relations] == ["opponent"]
    assert opponent.counts.opposite_side == 1 and opponent.counts.same_side == 0
    assert [relation.relation for relation in unknown.relations] == ["unknown"]
    assert unknown.counts.unknown_side == 1
    assert unknown.relations[0].other_side is None
    # Only opponents are counted as opponent sightline counts, all ticks resolve separately.
    assert teammate.counts.opponent_static_clear == 0
    assert opponent.counts.opponent_static_clear == 1


# --------------------------------------------------------------------------- #
# dead, unknown-health and anonymous rows
# --------------------------------------------------------------------------- #
def test_dead_unknown_health_and_anonymous_players_are_never_active(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, side="ct"),  # alive subject
            srow(1, 100, PLAYER_B, x=100.0, side="t", health=0),  # identified dead
            srow(2, 100, PLAYER_C, x=200.0, side="t", health_null=True),  # unknown health
            srow(3, 100, None, x=0.0, side=None, health=0),  # anonymous engine corpse
        ],
    )
    gen = harness.open()
    geometry = FakeGeometry()
    service = ContextService(harness.pool, geometry)

    snapshot = service.at(gen, PLAYER_A, 100)

    assert snapshot.relations == []
    assert {relation.player_id for relation in snapshot.inactive_relations} == {PLAYER_B, PLAYER_C}
    assert all(not relation.active for relation in snapshot.inactive_relations)
    assert any(
        relation.inactive_reason == "this player is not observed alive at this tick"
        for relation in snapshot.inactive_relations
    )
    assert snapshot.counts.living == 1
    assert snapshot.counts.dead == 2  # identified dead + anonymous corpse
    assert snapshot.counts.unknown_health == 1
    assert snapshot.counts.identity_identified == 3
    assert snapshot.counts.identity_null == 1
    assert snapshot.counts.identity_null_alive == 0
    # nothing was measured: a dead or unclassified endpoint is never evaluated
    assert geometry.calls == []
    assert snapshot.counts.sightlines_evaluated == 0
    assert all(relation.static_sightline is None for relation in snapshot.inactive_relations)


def test_a_dead_subject_keeps_its_recorded_state_without_active_relations(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, x=10.0, y=20.0, side="ct", health=0),
            srow(1, 100, PLAYER_B, x=100.0, side="t"),
        ],
    )
    gen = harness.open()
    geometry = FakeGeometry()
    service = ContextService(harness.pool, geometry)

    snapshot = service.at(gen, PLAYER_A, 100)

    assert snapshot.subject is not None  # recorded state is kept
    assert snapshot.subject.health == 0 and snapshot.subject.alive is False
    assert snapshot.subject_alive is False
    assert snapshot.relations == []
    assert [relation.player_id for relation in snapshot.inactive_relations] == [PLAYER_B]
    assert "subject is not observed alive at this tick" in snapshot.inactive_relations[0].inactive_reason
    assert any("every relation is reported inactive" in note for note in snapshot.limitations)
    assert geometry.calls == []


def test_anonymous_rows_are_counted_but_never_joined_by_position(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, x=10.0, y=20.0, side="ct"),
            srow(1, 100, None, x=10.0, y=20.0, side=None, health=100),  # alive, no identity
        ],
    )
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, 100)

    assert snapshot.relations == [] and snapshot.inactive_relations == []
    assert snapshot.counts.identity_null == 1
    assert snapshot.counts.identity_null_alive == 1
    assert any("never joined to a player" in note for note in snapshot.limitations)
    assert any("unidentified living rows" in note for note in snapshot.limitations)


# --------------------------------------------------------------------------- #
# distances, bearing and the estimated eye
# --------------------------------------------------------------------------- #
def test_distances_bearing_and_relative_yaw_use_recorded_origins(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, x=0.0, y=0.0, yaw=0.0, crouched=True, side="ct"),
            srow(1, 100, PLAYER_B, x=100.0, y=0.0, side="t"),
            srow(2, 100, PLAYER_C, x=0.0, y=100.0, side="t"),
            srow(3, 100, PLAYER_D, x=0.0, y=-100.0, side="t"),
        ],
    )
    gen = harness.open()
    geometry = FakeGeometry()
    service = ContextService(harness.pool, geometry)

    snapshot = service.at(gen, PLAYER_A, 100)
    by_player = {relation.player_id: relation for relation in snapshot.relations}

    assert set(by_player) == {PLAYER_B, PLAYER_C, PLAYER_D}
    assert by_player[PLAYER_B].distance_2d == pytest.approx(100.0)
    assert by_player[PLAYER_B].distance_3d == pytest.approx(100.0)  # recorded origins, not eyes
    assert by_player[PLAYER_B].bearing_degrees == pytest.approx(0.0)
    assert by_player[PLAYER_B].relative_yaw == pytest.approx(0.0)
    assert by_player[PLAYER_C].bearing_degrees == pytest.approx(90.0)
    assert by_player[PLAYER_C].relative_yaw == pytest.approx(90.0)
    assert by_player[PLAYER_D].bearing_degrees == pytest.approx(-90.0)
    assert by_player[PLAYER_D].relative_yaw == pytest.approx(-90.0)

    subject_origin = by_player[PLAYER_B].view_origin
    assert subject_origin.mode == "estimated_crouched"
    assert subject_origin.height_units == CROUCHED
    assert subject_origin.z == pytest.approx(CROUCHED)
    assert subject_origin.qualified is False  # an estimate is never qualified
    assert any("stance estimate" in note for note in subject_origin.limitations)
    assert by_player[PLAYER_B].other_view_origin.mode == "estimated_standing"
    assert by_player[PLAYER_B].other_view_origin.z == pytest.approx(STANDING)

    # the sightline is asked about the estimated eyes, never about the origins
    assert geometry.calls[0][1] == (0.0, 0.0, CROUCHED)
    assert geometry.calls[0][2] == (100.0, 0.0, STANDING)
    assert snapshot.counts.opponent_static_clear == 3


def test_a_tick_with_an_unknown_stance_computes_no_sightline(harness: AnalyticsHarness) -> None:
    # a living opponent whose stance is not recorded: eye position is unknown, not assumed standing
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, side="ct"),
            {**srow(1, 100, PLAYER_B, x=100.0, side="t"), "is_crouched": None},
        ],
    )
    gen = harness.open()
    geometry = FakeGeometry()
    snapshot = ContextService(harness.pool, geometry).at(gen, PLAYER_A, 100)

    relation = snapshot.relations[0]
    assert relation.active is True  # both endpoints are living
    assert relation.other_view_origin.mode == "unknown"
    assert relation.other_view_origin.qualified is False
    assert any("stance" in note for note in relation.other_view_origin.limitations)
    assert relation.static_sightline is None
    assert relation.static_effective_status is None
    assert any("sightline not evaluated" in note for note in relation.limitations)
    assert geometry.calls == []
    assert snapshot.counts.opponent_static_unknown == 1
    assert snapshot.counts.sightlines_unavailable == 1


def test_an_opponent_with_unknown_health_is_inactive_and_never_evaluated(
    harness: AnalyticsHarness,
) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, side="ct"),
            srow(1, 100, PLAYER_B, x=100.0, side="t", health_null=True),
        ],
    )
    gen = harness.open()
    geometry = FakeGeometry()

    snapshot = ContextService(harness.pool, geometry).at(gen, PLAYER_A, 100)

    assert snapshot.relations == []
    assert snapshot.counts.unknown_health == 1
    assert snapshot.counts.active_relations == 0
    # an inactive relation is not an opponent sightline count and no ray was fired
    assert snapshot.counts.opponent_static_unknown == 0
    assert snapshot.counts.sightlines_unavailable == 0
    assert geometry.calls == []


# --------------------------------------------------------------------------- #
# geometry status is never promoted
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("status", ["unknown", "unsupported"])
def test_unknown_or_unsupported_geometry_is_never_clear(harness: AnalyticsHarness, status: str) -> None:
    _publish(
        harness,
        [srow(0, 100, PLAYER_A, side="ct"), srow(1, 100, PLAYER_B, x=100.0, side="t")],
    )
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry(status=status))

    snapshot = service.at(gen, PLAYER_A, 100)
    relation = snapshot.relations[0]

    assert relation.static_sightline is not None and relation.static_sightline.status == status
    assert relation.static_effective_status == status
    assert snapshot.counts.opponent_static_clear == 0
    assert snapshot.counts.opponent_static_blocked == 0
    assert snapshot.counts.opponent_static_unknown == 1
    assert snapshot.counts.sightlines_evaluated == 0
    assert any("never treated as clear" in note for note in relation.limitations)


def test_mismatched_installed_assets_downgrade_a_clear_result_to_unknown(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, side="ct"),
            srow(1, 100, PLAYER_B, x=100.0, side="t"),
            srow(2, 100, PLAYER_C, x=10.0, y=100.0, side="t"),
        ],
    )
    gen = harness.open()
    # the asset build (2000932) does not match the recording (2000930) for the far segment
    geometry = FakeGeometry(
        status_fn=lambda start, end: ("static_clear", "mismatch") if end[0] >= 50 else ("static_clear", "exact")
    )
    service = ContextService(harness.pool, geometry)

    snapshot = service.at(gen, PLAYER_A, 100)
    by_player = {relation.player_id: relation for relation in snapshot.relations}

    assert by_player[PLAYER_B].static_sightline.status == "static_clear"  # verbatim, kept
    assert by_player[PLAYER_B].static_sightline.match_status == "mismatch"
    assert by_player[PLAYER_B].static_effective_status == "unknown"  # never promoted
    assert by_player[PLAYER_C].static_effective_status == "static_clear"
    assert snapshot.counts.opponent_static_clear == 1
    assert snapshot.counts.opponent_static_unknown == 1
    assert any("cannot prove the historical sightline" in note for note in by_player[PLAYER_B].limitations)
    assert snapshot.capabilities.sightlines.limitations  # the capability says so as well


def test_missing_geometry_service_degrades_explicitly(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [srow(0, 100, PLAYER_A, side="ct"), srow(1, 100, PLAYER_B, x=100.0, side="t")],
    )
    gen = harness.open()
    service = ContextService(harness.pool, None)

    snapshot = service.at(gen, PLAYER_A, 100)

    assert snapshot.capabilities.geometry.status == "unavailable"
    assert snapshot.capabilities.sightlines.status == "unavailable"
    assert snapshot.capabilities.navigation.status == "unavailable"
    assert snapshot.capabilities.exposure.status == "unsupported"
    assert snapshot.provenance.map_match_status == "unknown"
    relation = snapshot.relations[0]
    assert relation.static_sightline is None and relation.static_effective_status is None
    assert any("geometry service unavailable" in note for note in relation.limitations)
    assert snapshot.counts.opponent_static_unknown == 1
    assert snapshot.counts.opponent_static_clear == 0


def test_navigation_is_optional_and_bounded_by_the_call(harness: AnalyticsHarness) -> None:
    _publish(harness, [srow(0, 100, PLAYER_A, side="ct"), srow(1, 100, PLAYER_B, x=100.0, side="t")])
    gen = harness.open()
    geometry = FakeGeometry()
    service = ContextService(harness.pool, geometry)

    without = service.at(gen, PLAYER_A, 100)
    with_nav = service.at(gen, PLAYER_A, 100, navigation=True)

    assert without.relations[0].navigation is None
    assert len(geometry.nav_calls) == 1
    assert with_nav.relations[0].navigation.status == "available"
    assert with_nav.relations[0].navigation.connected is True


def test_navigation_uses_recorded_origins_while_sightlines_use_eye_estimates(
    harness: AnalyticsHarness,
) -> None:
    _publish(
        harness,
        [
            srow(0, 100, PLAYER_A, side="ct", crouched=True),
            srow(1, 100, PLAYER_B, x=100.0, side="t"),
            srow(2, 100, PLAYER_C, x=10.0, y=100.0, side="ct"),
        ],
    )
    gen = harness.open()
    # the fake nav service only accepts floor-level points, like a nav area plane
    geometry = FakeGeometry(nav_requires_origin_z=True)
    service = ContextService(harness.pool, geometry)

    snapshot = service.at(gen, PLAYER_A, 100, navigation=True, cross_pairs=True)

    # a nav answer is produced for the subject relation and for the pair, despite the floor constraint
    relation = next(item for item in snapshot.relations if item.player_id == PLAYER_B)
    assert relation.navigation is not None and relation.navigation.status == "available"
    pair = snapshot.pair_relations[0]
    assert pair.navigation is not None and pair.navigation.status == "available"
    # every nav query used floor-level recorded origins (an eye endpoint would have been "unavailable")
    assert geometry.nav_calls and all(
        start[2] == 0.0 and end[2] == 0.0 for start, end in geometry.nav_calls
    )
    # the eye-to-eye ray for that relation was still queried at the estimated eye heights
    assert any(
        call[1] == (0.0, 0.0, CROUCHED) and call[2] == (100.0, 0.0, STANDING) for call in geometry.calls
    )


def test_relations_beyond_the_bound_are_dropped_nearest_first(harness: AnalyticsHarness) -> None:
    states = [srow(0, 100, PLAYER_A, side="ct")]
    for index in range(MAX_RELATIONS + 3):
        states.append(srow(index + 1, 100, f"steam:7656119800{index:09d}", x=float(10 * (index + 1)), side="t"))
    _publish(harness, states)
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    snapshot = service.at(gen, PLAYER_A, 100)

    assert len(snapshot.relations) == MAX_RELATIONS
    assert any(f"beyond the {MAX_RELATIONS}-relation bound" in note for note in snapshot.limitations)
    distances = [relation.distance_2d for relation in snapshot.relations]
    assert distances == sorted(distances)  # nearest kept
    assert snapshot.counts.opposite_side == MAX_RELATIONS + 3


# --------------------------------------------------------------------------- #
# movement window
# --------------------------------------------------------------------------- #
def test_position_change_is_withheld_when_a_missing_tick_breaks_the_run(harness: AnalyticsHarness) -> None:
    states = [
        srow(index, tick, PLAYER_A, x=float(tick - 96), y=0.0, side="ct")
        for index, tick in enumerate(range(96, 161, 8))
        if tick != 112
    ]
    _publish(harness, states)
    gen = harness.open()
    service = ContextService(harness.pool, None)

    snapshot = service.at(gen, PLAYER_A, 128, stride_ticks=8, position_window_ticks=32)
    change = snapshot.position_change

    assert change is not None
    assert change.samples == 8 and change.missing_samples == 1
    assert change.living_samples == 8 and change.dead_samples == 0
    assert change.contiguous_living is False
    # a hole in the grid is never bridged into a displacement or a path length
    assert change.dx is None and change.displacement_2d is None and change.path_length_2d is None
    assert any("never interpolated" in note for note in change.limitations)
    assert any("not one contiguous run" in note for note in change.limitations)


def test_position_change_is_reported_over_a_contiguous_living_run(harness: AnalyticsHarness) -> None:
    states = [
        srow(index, tick, PLAYER_A, x=float(tick - 96), y=0.0, side="ct")
        for index, tick in enumerate(range(96, 161, 8))
    ]
    _publish(harness, states)
    gen = harness.open()
    service = ContextService(harness.pool, None)

    change = service.at(gen, PLAYER_A, 128, stride_ticks=8, position_window_ticks=32).position_change

    assert change is not None and change.contiguous_living is True
    assert (change.from_tick, change.to_tick) == (96, 160)
    assert change.samples == 9 and change.living_samples == 9 and change.missing_samples == 0
    assert change.displacement_2d == pytest.approx(64.0)
    assert change.path_length_2d == pytest.approx(64.0)


def test_position_change_is_withheld_across_a_death(harness: AnalyticsHarness) -> None:
    states = [
        srow(index, tick, PLAYER_A, x=float(tick - 96), y=0.0, side="ct", health=0 if tick == 120 else 100)
        for index, tick in enumerate(range(96, 161, 8))
    ]
    _publish(harness, states)
    gen = harness.open()
    service = ContextService(harness.pool, None)

    change = service.at(gen, PLAYER_A, 128, stride_ticks=8, position_window_ticks=32).position_change

    assert change is not None
    assert change.dead_samples == 1 and change.living_samples == 8
    assert change.contiguous_living is False
    assert change.displacement_2d is None and change.path_length_2d is None
    assert any("death, respawn or round boundary" in note for note in change.limitations)
    # the corpse row is still an observation, just not a movement endpoint
    assert change.samples == 9


def test_position_change_is_withheld_across_a_round_boundary(harness: AnalyticsHarness) -> None:
    rounds = [
        round_row(1, start=90, freeze_end=90, end=127),
        round_row(2, start=128, freeze_end=128, end=170),
    ]
    states = [
        srow(index, tick, PLAYER_A, x=float(tick - 96), y=0.0, side="ct")
        for index, tick in enumerate(range(96, 161, 8))
    ]
    _publish(harness, states, rounds)
    gen = harness.open()
    service = ContextService(harness.pool, None)

    change = service.at(gen, PLAYER_A, 128, stride_ticks=8, position_window_ticks=32).position_change

    assert change is not None
    assert change.contiguous_living is False
    assert change.displacement_2d is None and change.path_length_2d is None
    assert any("spans rounds 1 to 2" in note for note in change.limitations)


def test_position_change_can_be_switched_off(harness: AnalyticsHarness) -> None:
    _publish(harness, [srow(0, 100, PLAYER_A, side="ct")])
    gen = harness.open()

    snapshot = ContextService(harness.pool, None).at(gen, PLAYER_A, 100, position_window_ticks=0)

    assert snapshot.position_change is None


def test_subject_position_change_covers_the_requested_window(harness: AnalyticsHarness) -> None:
    _publish(
        harness,
        [srow(index, tick, PLAYER_A, x=float(tick), y=0.0, side="ct") for index, tick in enumerate(range(100, 165, 4))],
    )
    gen = harness.open()

    change = ContextService(harness.pool, None).subject_position_change(gen, PLAYER_A, 100, 164, stride_ticks=4)

    assert (change.from_tick, change.to_tick) == (100, 164)
    assert change.displacement_2d == pytest.approx(64.0)
    assert change.path_length_2d == pytest.approx(64.0)


# --------------------------------------------------------------------------- #
# utility capability on a profile that publishes none
# --------------------------------------------------------------------------- #
def test_foundation_profile_reports_utility_unavailable(harness: AnalyticsHarness) -> None:
    _publish(harness, [srow(0, 100, PLAYER_A, side="ct")])
    gen = harness.open()
    service = ContextService(harness.pool, FakeGeometry())

    assert service.utility_tables(gen) == []
    snapshot = service.at(gen, PLAYER_A, 100)

    assert snapshot.capabilities.utility.status == "unavailable"
    assert snapshot.utility == []
    assert all(source.table not in gen.manifest.tables for source in UTILITY_SOURCES)



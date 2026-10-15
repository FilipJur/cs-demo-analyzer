"""Exact-tick player-centric context reconstruction (slice E).

What this module answers
------------------------
``ContextService.at`` describes one player at one exact tick: the verbatim
``player_state`` observation, every *other* identified player at that same tick
classified by the side each row carries at that tick, planar/3D distances, the
bearing and view-relative angle, a static sightline from the injected geometry
service, the recorded utility active at that tick, and a bounded window of
observed movement.

``ContextService.encounter`` turns an encounter detail (slice D) into snapshots
at that encounter's recorded anchors and pre/post-contact offsets, plus a
qualified earliest exposure, the utility intervals matched to the window, and the
subject's bounded observed movement.

Deliberate limits
-----------------
* Exact ticks only; a tick with no rows reports ``exact=False`` and an empty
  subject/relation set. Nothing is interpolated, snapped or carry-forwarded.
* Active relationships require ``health > 0`` on *both* endpoints. Dead rows are
  counted and reported but never become active relations, and a dead subject
  never contributes to an exposure count.
* Rows with a null ``player_id`` are observations, not players: they are counted
  and flagged, never joined to a player by position, name or ordering.
* Static geometry is never promoted. ``unknown``/``unsupported`` and results
  produced against mismatched installed assets are never "clear", and no
  awareness/perception/risk claim is made anywhere: perception is always unknown.
* Eye positions come from the generation when it actually carries a recorded view
  origin; ``reconstruction-v1`` carries none, so they are *estimates* from the
  recorded stance (engine view offset: standing 64, crouched 46 Hammer units above
  the origin) and every relation says so. A stance that is not recorded means an
  unknown eye position, and no sightline is computed from a guessed one.
* Utility facts are read verbatim from the tables the reconstruction profile
  publishes; nothing is interpreted. ``unknown``/``unsupported``/truncated
  sources are reported instead of being resolved.

Bounded reads
-------------
Every read is generation-pinned and bounded: one tick of state per snapshot, one
bounded window for movement and exposure, at most :data:`MAX_RELATIONS` relations
per tick, at most :data:`MAX_EXPOSURE_SAMPLES` strided exposure samples plus the
window end, at most :data:`MAX_SNAPSHOTS` snapshots per encounter. Nothing loads a
whole match, and the dense tables are always read with an explicit limit.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, NamedTuple, Protocol, Sequence

import polars as pl

from ..domain.context import (
    CROUCHED_EYE_HEIGHT_UNITS,
    MAX_CROSS_PAIRS,
    MAX_CROSS_PAIR_ANCHORS,
    MAX_PARTICIPANTS,
    MAX_TRACKED_PARTICIPANTS,
    MAX_TRACK_SAMPLES,
    STANDING_EYE_HEIGHT_UNITS,
    STATIC_SCOPE,
    AnchorKind,
    AngularSpread,
    ContextAnchorSnapshot,
    ContextCapabilities,
    ContextCounts,
    ContextPositionChange,
    ContextRelation,
    ContextSnapshot,
    ContextStateRef,
    ContextUtilityFact,
    CrossSightline,
    EncounterContext,
    EncounterExposure,
    ExposureSampling,
    FacingDelta,
    LifecycleFact,
    OpponentDirection,
    OpponentExposure,
    ParticipantTrack,
    RelationKind,
    TrajectorySample,
    ViewOrigin,
)
from ..domain.contracts import AppError, EvidenceRef
from ..domain.encounters import EncounterDetail
from ..domain.evidence import EvidenceCapability, EvidenceKind, ReconstructionProvenance
from ..domain.geometry import (
    GeometryCapabilities,
    MatchStatus,
    NavigationResult,
    SegmentResult,
    SegmentStatus,
)
from .access import Generation, GenerationPool
from .spatial import dist2d, dist3d, yaw_diff
from .temporal import round_of

STAGE = "analytics"

METHOD = "context.exact_tick"
METHOD_VERSION = "1"

#: Hard bounds: nothing here ever scales with match length.
MAX_RELATIONS = 32
MAX_SNAPSHOTS = 64
MAX_EXPOSURE_SAMPLES = 64
"""Grid ticks from the strided scan; the window end is always sampled in addition."""
MAX_EXPOSURE_WINDOW_TICKS = 4_096
MAX_UTILITY_ROWS = 4_096
STATE_TICK_LIMIT = 1_024
DEFAULT_STRIDE_TICKS = 8
DEFAULT_POSITION_WINDOW_TICKS = 64
DEFAULT_PRE_OFFSETS_SECONDS = (1.0, 2.0, 3.0)
DEFAULT_POST_OFFSETS_SECONDS = (0.5,)
MAX_OFFSETS = 8

_STATE_COLUMNS = [
    "row_ordinal",
    "tick",
    "player_id",
    "x",
    "y",
    "z",
    "yaw",
    "pitch",
    "health",
    "side",
    "is_crouched",
    "is_scoped",
    "active_weapon",
]


# --------------------------------------------------------------------------- #
# provider-published sources (slice B, reconstruction-v1)
# --------------------------------------------------------------------------- #
class UtilitySource(NamedTuple):
    """One published utility table mapped onto Context's semantic fields.

    ``columns`` maps a semantic field to the published column name: ``tick``,
    ``end_tick`` (optional), ``duration_seconds`` (optional, when the source
    records a duration instead of an end tick), ``owner`` (optional), ``kind``
    (optional), ``x``/``y``/``z``/``site`` (optional).

    ``reliable`` states whether the source promises what a row means (interval
    bounds, geometry and identity). An interval whose identity is absent upstream
    is still a reliable *interval*: the missing owner is reported per fact.
    """

    table: str
    kind: str
    reliable: bool
    columns: Mapping[str, str]
    evidence_kind: EvidenceKind = "recorded"
    limitations: tuple[str, ...] = ()


class ViewOriginSource(NamedTuple):
    """A published source carrying a *recorded* view origin (eye position)."""

    table: str
    x: str
    y: str
    z: str


_ABSENT_OWNER_NOTE = (
    "thrower/owner identity is absent in this profile (all-null upstream); a null owner is "
    "not evidence of an unknown player"
)

#: Utility lifecycle tables of `reconstruction-v1`. `smokes`/`fires` carry a
#: recorded interval; `blinds` carries the recorded blind onset tick plus a
#: recorded duration, from which the expire tick is derived at the generation's
#: tick rate. `grenades` is a dense per-tick projectile trajectory and
#: `player_state_ext` a dense per-player extension, so neither is read here.
UTILITY_SOURCES: tuple[UtilitySource, ...] = (
    UtilitySource(
        table="smokes",
        kind="smoke",
        reliable=True,
        columns={
            "tick": "start_tick",
            "end_tick": "end_tick",
            "owner": "owner_id",
            "x": "x",
            "y": "y",
            "z": "z",
        },
        limitations=(
            _ABSENT_OWNER_NOTE,
            "still_active_at_end marks recording truncation, not a real expiry",
        ),
    ),
    UtilitySource(
        table="fires",
        kind="inferno",
        reliable=True,
        columns={
            "tick": "start_tick",
            "end_tick": "end_tick",
            "kind": "kind",
            "owner": "owner_id",
            "x": "x",
            "y": "y",
            "z": "z",
        },
        limitations=(_ABSENT_OWNER_NOTE, "still_active_at_end marks recording truncation, not a real expiry"),
    ),
    UtilitySource(
        table="blinds",
        kind="flash",
        reliable=True,
        evidence_kind="computed",
        columns={
            "tick": "tick",
            "duration_seconds": "duration_seconds",
            "owner": "attacker_id",
            "x": "victim_x",
            "y": "victim_y",
            "z": "victim_z",
        },
        limitations=(
            "slice B publishes blinds as an upstream reconstruction from pawn flash state and "
            "flashbang_detonate (not a raw player_blind event stream); it is an observation of recorded "
            "engine state, reported verbatim here",
            "tick is the blind-onset tick; the expire tick is derived from the recorded "
            "duration at the generation tick rate",
        ),
    ),
)

#: Sources carrying a recorded eye position. `reconstruction-v1` publishes none
#: (verified with slice B: awpy exposes no eye-origin snapshot and
#: ``player_state.x/y/z`` is the entity origin), so eye positions are stance-based
#: estimates and every relation says so.
VIEW_ORIGIN_SOURCES: tuple[ViewOriginSource, ...] = ()

#: Recorded identity-continuity table (slice B ``player_lifecycle``): connect,
#: disconnect, spawn and team-change rows. It explains why a participant has no
#: state at a tick with a *recorded* fact instead of an inference.
LIFECYCLE_TABLE = "player_lifecycle"
MAX_LIFECYCLE_ROWS = 4_096

_LIFECYCLE_COLUMNS = {
    "tick": "tick",
    "kind": "kind",
    "player_id": "player_id",
    "user_slot": "user_slot",
    "team": "team",
    "previous_team": "previous_team",
    "is_bot": "is_bot",
    "reason_code": "reason_code",
    "ever_fully_connected": "ever_fully_connected",
}


class GeometryProvider(Protocol):
    """Structural type of the injected ``assets.geometry.GeometryService``."""

    def capabilities(self, map_name: str, demo_client_version: str | None = None) -> GeometryCapabilities: ...

    def segment(
        self,
        map_name: str,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        demo_client_version: str | None = None,
    ) -> SegmentResult: ...

    def navigation(
        self,
        map_name: str,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        demo_client_version: str | None = None,
    ) -> NavigationResult: ...


def _invalid(message: str) -> AppError:
    return AppError("INVALID_ARGUMENT", message, STAGE)


def _merge_limitations(*groups: Sequence[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for text in group:
            if text not in merged:
                merged.append(text)
    return merged


def _finite(*values: float | None) -> bool:
    return all(value is not None and math.isfinite(value) for value in values)


def _point(row: Mapping[str, Any]) -> tuple[float, float, float] | None:
    if not _finite(row.get("x"), row.get("y"), row.get("z")):
        return None
    return (float(row["x"]), float(row["y"]), float(row["z"]))


def _alive(row: Mapping[str, Any]) -> bool:
    health = row.get("health")
    return health is not None and int(health) > 0


def _relation_kind(subject_side: str | None, other_side: str | None) -> RelationKind:
    if subject_side is None or other_side is None:
        return "unknown"
    return "teammate" if subject_side == other_side else "opponent"


def _bearing(x1: float, y1: float, x2: float, y2: float) -> float:
    """Planar bearing in degrees, counter-clockwise from +X (the engine's yaw axis)."""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


# --------------------------------------------------------------------------- #
# capability reporting
# --------------------------------------------------------------------------- #
class _CapabilitySet(NamedTuple):
    capabilities: ContextCapabilities
    geometry: GeometryCapabilities | None
    map_name: str | None
    demo_client_version: str | None
    map_asset_id: str | None
    map_match_status: MatchStatus


def _capability_set(
    geometry: GeometryProvider | None, gen: Generation, utility_tables: Sequence[str]
) -> _CapabilitySet:
    map_name = gen.manifest.map_name or None
    demo_client_version = gen.manifest.demo_client_version

    state = EvidenceCapability(
        status="available",
        source="player_state",
        limitations=["exact ticks only; nothing is interpolated or snapped"],
    )

    geometry_caps: GeometryCapabilities | None = None
    geometry_failure: str | None = None
    if geometry is None:
        geometry_failure = "geometry service not configured for this service instance"
    elif not map_name:
        geometry_failure = "generation manifest carries no map name"
    else:
        try:
            geometry_caps = geometry.capabilities(map_name, demo_client_version)
        except Exception as exc:  # provider trust boundary: degrade, never fail the snapshot
            geometry_failure = f"geometry capabilities unavailable ({type(exc).__name__}: {exc})"

    match_status: MatchStatus = "unknown"
    if geometry_failure is not None:
        geometry_cap = EvidenceCapability(status="unavailable", source="geometry", limitations=[geometry_failure])
        sightlines = EvidenceCapability(
            status="unavailable",
            source="geometry",
            limitations=[f"{geometry_failure}; no sightline is claimed"],
        )
        navigation = EvidenceCapability(status="unavailable", source="geometry", limitations=[geometry_failure])
        map_asset_id = None
        map_notes = [geometry_failure]
    else:
        assert geometry_caps is not None
        physics_notes = list(geometry_caps.limitations) + list(geometry_caps.physics.limitations)
        geometry_cap = EvidenceCapability(
            status=geometry_caps.physics.status,
            source=geometry_caps.physics.source,
            limitations=physics_notes,
        )
        navigation = EvidenceCapability(
            status=geometry_caps.navigation.status,
            source=geometry_caps.navigation.source,
            limitations=list(geometry_caps.limitations) + list(geometry_caps.navigation.limitations),
        )
        match_status = geometry_caps.match_status
        match_notes: list[str] = []
        if match_status == "mismatch":
            match_notes.append(
                "installed map assets do not match the recorded client version; a static result cannot "
                "prove the historical sightline and is reported as unknown"
            )
        elif match_status == "unknown":
            match_notes.append(
                "map asset identity is unknown; static sightlines are installed-asset-scoped"
            )
        if not geometry_caps.prepared:
            match_notes.append("map geometry is not prepared; expensive extraction is not run on scrub")
        sightlines = EvidenceCapability(
            status=geometry_caps.physics.status,
            source=geometry_caps.physics.source,
            limitations=physics_notes
            + match_notes
            + [
                f"static results are scoped to the installed map build ({geometry_caps.asset_id or 'unknown asset'}"
                f", match {geometry_caps.match_status}); they are not a statement of what any player could see or know"
            ],
        )
        map_asset_id = geometry_caps.asset_id
        map_notes = match_notes

    if utility_tables:
        utility = EvidenceCapability(
            status="partial",
            source=", ".join(utility_tables),
            limitations=[
                "utility rows are returned verbatim; a missing owner is an absent upstream field, not an "
                "unknown player, and perception stays unknown",
                "grenade projectile trajectories and per-tick grenade counts are not read by Context",
            ],
        )
    else:
        utility = EvidenceCapability(
            status="unavailable",
            source="reconstruction utility tables",
            limitations=[f"profile {gen.profile_key} publishes no utility table; no utility fact is claimed"],
        )

    recorded_origin = [source for source in VIEW_ORIGIN_SOURCES if source.table in gen.manifest.tables]
    if recorded_origin:
        view_origin = EvidenceCapability(
            status="available", source=", ".join(source.table for source in recorded_origin), limitations=[]
        )
    else:
        view_origin = EvidenceCapability(
            status="partial",
            source="player_state stance",
            limitations=[
                "no recorded view origin in this profile; eye position is estimated from the recorded "
                f"stance (engine view offset: standing {STANDING_EYE_HEIGHT_UNITS:g} / crouched "
                f"{CROUCHED_EYE_HEIGHT_UNITS:g} Hammer units above the origin), which is wrong mid "
                "duck/unduck, in air, and for dead rows"
            ],
        )

    if sightlines.status in ("available", "partial"):
        exposure = EvidenceCapability(
            status="available", source="context.exposure", limitations=list(sightlines.limitations)
        )
    else:
        exposure = EvidenceCapability(
            status="unsupported",
            source=f"context.exposure; {sightlines.source}",
            limitations=[f"{sightlines.source} is {sightlines.status}; earliest exposure cannot be derived"],
        )

    if LIFECYCLE_TABLE in gen.manifest.tables:
        lifecycle = EvidenceCapability(
            status="available",
            source=LIFECYCLE_TABLE,
            limitations=[
                "only rows with a resolved account id are attributable to a player; slot-only rows are "
                "counted and never assigned",
                "a disconnect explains missing state; it is not evidence about play",
            ],
        )
    else:
        lifecycle = EvidenceCapability(
            status="unavailable",
            source=LIFECYCLE_TABLE,
            limitations=[
                f"profile {gen.profile_key} publishes no lifecycle table; missing participant state has no "
                "recorded explanation here"
            ],
        )

    limitations = list(map_notes)
    if not utility_tables:
        limitations.append("utility capability unavailable: this generation declares no utility table")

    capabilities = ContextCapabilities(
        state=state,
        geometry=geometry_cap,
        sightlines=sightlines,
        navigation=navigation,
        utility=utility,
        exposure=exposure,
        view_origin=view_origin,
        lifecycle=lifecycle,
        limitations=limitations,
    )
    return _CapabilitySet(
        capabilities=capabilities,
        geometry=geometry_caps,
        map_name=map_name,
        demo_client_version=demo_client_version,
        map_asset_id=map_asset_id,
        map_match_status=match_status,
    )


def _provenance(gen: Generation, caps: _CapabilitySet) -> ReconstructionProvenance:
    return ReconstructionProvenance(
        demo_id=gen.demo_id,
        generation_id=gen.generation_id,
        profile_key=gen.profile_key,
        method=METHOD,
        method_version=METHOD_VERSION,
        map_name=gen.manifest.map_name,
        demo_client_version=caps.demo_client_version,
        map_asset_id=caps.map_asset_id,
        map_match_status=caps.map_match_status,
        limitations=list(caps.capabilities.limitations),
    )


# --------------------------------------------------------------------------- #
# per-player facts
# --------------------------------------------------------------------------- #
def _state_ref(gen: Generation, row: Mapping[str, Any], round_id: int | None) -> ContextStateRef:
    player_id = row.get("player_id")
    return ContextStateRef(
        dataset="player_state",
        row_ordinal=int(row["row_ordinal"]),
        tick=int(row["tick"]),
        player_id=player_id,
        health=None if row.get("health") is None else int(row["health"]),
        alive=_alive(row),
        side=row.get("side"),
        is_crouched=row.get("is_crouched"),
        is_scoped=row.get("is_scoped"),
        active_weapon=row.get("active_weapon"),
        evidence=EvidenceRef(
            demo_id=gen.demo_id,
            generation_id=gen.generation_id,
            profile_key=gen.profile_key,
            dataset="player_state",
            row_ordinal=int(row["row_ordinal"]),
            tick=int(row["tick"]),
            round_id=round_id,
            player_ids=[player_id] if player_id else [],
        ),
    )


def _recorded_origin(row: Mapping[str, Any]) -> tuple[float, float, float] | None:
    for source in VIEW_ORIGIN_SOURCES:
        if source.table != "player_state":
            continue
        if not all(column in row for column in (source.x, source.y, source.z)):
            continue
        if not _finite(row.get(source.x), row.get(source.y), row.get(source.z)):
            continue
        return (float(row[source.x]), float(row[source.y]), float(row[source.z]))
    return None


def _view_origin(row: Mapping[str, Any]) -> ViewOrigin:
    """Recorded eye when the generation carries one, else an explicitly estimated stance eye."""
    recorded = _recorded_origin(row)
    if recorded is not None:
        return ViewOrigin(
            mode="recorded",
            x=recorded[0],
            y=recorded[1],
            z=recorded[2],
            yaw=None if row.get("yaw") is None else float(row["yaw"]),
            pitch=None if row.get("pitch") is None else float(row["pitch"]),
            qualified=True,
            source="recorded view origin",
        )

    point = _point(row)
    yaw = None if row.get("yaw") is None else float(row["yaw"])
    pitch = None if row.get("pitch") is None else float(row["pitch"])
    crouched = row.get("is_crouched")
    if point is None or yaw is None or crouched is None:
        missing = []
        if point is None:
            missing.append("position")
        if yaw is None:
            missing.append("view yaw")
        if crouched is None:
            missing.append("stance")
        return ViewOrigin(
            mode="unknown",
            qualified=False,
            source="player_state",
            limitations=[f"eye position unknown at this tick: missing {'/'.join(missing)}"],
        )

    height = CROUCHED_EYE_HEIGHT_UNITS if crouched else STANDING_EYE_HEIGHT_UNITS
    return ViewOrigin(
        mode="estimated_crouched" if crouched else "estimated_standing",
        x=point[0],
        y=point[1],
        z=point[2] + height,
        yaw=yaw,
        pitch=pitch,
        height_units=height,
        qualified=False,
        source="player_state stance estimate",
        limitations=[
            f"eye position is a stance estimate ({height:g} Hammer units above the recorded origin), "
            "not a recorded view origin"
        ],
    )


def _eye_point(origin: ViewOrigin) -> tuple[float, float, float] | None:
    if origin.mode == "unknown" or not _finite(origin.x, origin.y, origin.z):
        return None
    return (float(origin.x), float(origin.y), float(origin.z))


def _position_change(
    pool: GenerationPool,
    gen: Generation,
    player_id: str,
    center_tick: int,
    stride_ticks: int,
    window_ticks: int,
) -> ContextPositionChange | None:
    """Observed movement over a bounded window, never bridged across a break.

    A sample counts only when it has a recorded position; the derived metrics are
    reported only when the *living* samples form one contiguous run on the grid
    inside a single round. A death (``health == 0`` rows keep being emitted), a
    respawn, a missing sample or a round boundary breaks that run and the metrics
    stay ``None``.
    """
    if window_ticks <= 0:
        return None
    lo = max(0, center_tick - window_ticks)
    hi = center_tick + window_ticks
    grid = sorted(set(range(lo, hi + 1, stride_ticks)) | {center_tick})
    frame = pool.read(
        gen,
        "player_state",
        columns=["row_ordinal", "tick", "player_id", "x", "y", "z", "health"],
        predicate=(pl.col("player_id") == player_id) & (pl.col("tick") >= lo) & (pl.col("tick") <= hi),
        limit=STATE_TICK_LIMIT * 4,
    )
    points: dict[int, tuple[float, float, float]] = {}
    living: dict[int, bool] = {}
    for row in frame.sort("row_ordinal").to_dicts():
        point = _point(row)
        if point is not None:
            points[int(row["tick"])] = point
            living[int(row["tick"])] = _alive(row)

    observed = [tick for tick in grid if tick in points]
    living_ticks = [tick for tick in observed if living[tick]]
    change = ContextPositionChange(
        player_id=player_id,
        from_tick=living_ticks[0] if living_ticks else center_tick,
        to_tick=living_ticks[-1] if living_ticks else center_tick,
        stride_ticks=stride_ticks,
        samples=len(observed),
        living_samples=len(living_ticks),
        dead_samples=len(observed) - len(living_ticks),
        missing_samples=len(grid) - len(observed),
        bounded=True,
        limitations=[
            "observed window only; missing grid ticks are never interpolated",
            "a death, respawn or round boundary breaks the run and its metrics are withheld",
        ],
    )
    if not living_ticks:
        change.limitations.append(
            f"no living observed sample for {player_id} within [{lo}, {hi}]; no movement is reported"
        )
        return change

    contiguous = all(
        after - before == stride_ticks for before, after in zip(living_ticks, living_ticks[1:])
    )
    first_round = round_of(pool, gen, living_ticks[0])
    last_round = round_of(pool, gen, living_ticks[-1])
    if contiguous and first_round != last_round:
        contiguous = False
        change.limitations.append(
            f"the window spans rounds {first_round} to {last_round}; movement across a round boundary is "
            "not reported as one displacement"
        )
    if not contiguous:
        change.limitations.append(
            "the living samples are not one contiguous run on the sampling grid (or a round boundary "
            "intervenes); displacement and path length are withheld rather than bridged"
        )
        return change

    change.contiguous_living = True
    first, last = points[living_ticks[0]], points[living_ticks[-1]]
    change.dx = last[0] - first[0]
    change.dy = last[1] - first[1]
    change.dz = last[2] - first[2]
    change.displacement_2d = dist2d(first[0], first[1], last[0], last[1])
    change.displacement_3d = dist3d(*first, *last)
    change.path_length_2d = sum(
        step
        for before, after in zip(living_ticks, living_ticks[1:])
        for step in [dist2d(points[before][0], points[before][1], points[after][0], points[after][1])]
        if step is not None
    )
    return change


# --------------------------------------------------------------------------- #
# relations and sightlines
# --------------------------------------------------------------------------- #
def _sightline(
    geometry: GeometryProvider | None,
    caps: _CapabilitySet,
    subject_origin: ViewOrigin,
    other_origin: ViewOrigin,
) -> tuple[SegmentResult | None, SegmentStatus | None, list[str]]:
    """One static sightline between two estimated/recorded eye positions."""
    limitations: list[str] = []
    start = _eye_point(subject_origin)
    end = _eye_point(other_origin)
    if start is None or end is None:
        limitations.append("sightline not evaluated: an eye position is unknown at this tick")
        return None, None, limitations
    if geometry is None or caps.map_name is None:
        limitations.append("sightline not evaluated: geometry service unavailable")
        return None, None, limitations
    try:
        result = geometry.segment(caps.map_name, start, end, caps.demo_client_version)
    except Exception as exc:  # provider trust boundary
        limitations.append(f"sightline query failed ({type(exc).__name__}: {exc})")
        return None, None, limitations

    effective: SegmentStatus = result.status
    if result.match_status == "mismatch":
        result = result.model_copy(
            update={
                "limitations": list(result.limitations)
                + [
                    "installed assets differ from the recorded client version; this result cannot prove "
                    "the historical sightline"
                ]
            }
        )
        effective = "unknown"
    if result.status in ("unknown", "unsupported"):
        limitations.append(f"static sightline status {result.status}: never treated as clear")
    if effective == "static_clear" and not (subject_origin.qualified and other_origin.qualified):
        limitations.append(
            "clear sightline between unqualified eye positions; at least one endpoint is an estimate, "
            "not a recorded view origin"
        )
    limitations.extend(result.limitations)
    return result, effective, limitations


def _navigation(
    geometry: GeometryProvider | None,
    caps: _CapabilitySet,
    start: tuple[float, float, float] | None,
    end: tuple[float, float, float] | None,
) -> NavigationResult | None:
    """Navigation between recorded player *origins*.

    The nav mesh describes walkable floor, so its polygon planes sit around the
    recorded origin height; an estimated eye point (origin + 64/46) can fall outside
    the area and report a false "unavailable". Sightline rays stay eye-to-eye, but
    navigation endpoints are the verbatim recorded origin positions.
    """
    if geometry is None or caps.map_name is None or start is None or end is None:
        return None
    try:
        return geometry.navigation(caps.map_name, start, end, caps.demo_client_version)
    except Exception:  # provider trust boundary: navigation is optional by contract
        return None


def _relation(
    gen: Generation,
    subject_row: Mapping[str, Any],
    other_row: Mapping[str, Any],
    round_id: int | None,
    caps: _CapabilitySet,
    geometry: GeometryProvider | None,
    *,
    subject_origin: ViewOrigin,
    other_origin: ViewOrigin,
    sightlines: bool,
    navigation: bool,
) -> ContextRelation:
    subject = _state_ref(gen, subject_row, round_id)
    other = _state_ref(gen, other_row, round_id)
    relation_kind = _relation_kind(subject.side, other.side)

    limitations: list[str] = []
    start_point = _point(subject_row)
    other_point = _point(other_row)
    distance_2d = distance_3d = bearing = relative_yaw = None
    if start_point is not None and other_point is not None:
        distance_2d = dist2d(start_point[0], start_point[1], other_point[0], other_point[1])
        distance_3d = dist3d(*start_point, *other_point)
        bearing = _bearing(start_point[0], start_point[1], other_point[0], other_point[1])
        relative_yaw = yaw_diff(subject_origin.yaw, bearing)
    else:
        limitations.append("distance and bearing unavailable: an exact-tick position is missing")

    active = subject.alive and other.alive
    inactive_reason: str | None = None
    if not active:
        if not subject.alive and not other.alive:
            inactive_reason = "neither the subject nor this player is observed alive at this tick"
        elif not subject.alive:
            inactive_reason = "subject is not observed alive at this tick"
        else:
            inactive_reason = "this player is not observed alive at this tick"
        limitations.append(f"inactive relation: {inactive_reason}; recorded state is still reported")

    sightline: SegmentResult | None = None
    effective: SegmentStatus | None = None
    nav: NavigationResult | None = None
    if active and sightlines:
        sightline, effective, sight_notes = _sightline(geometry, caps, subject_origin, other_origin)
        limitations.extend(sight_notes)
        if navigation:
            nav = _navigation(geometry, caps, start_point, other_point)
    elif not active:
        limitations.append("no sightline evaluated: an active relation requires both endpoints alive")
    else:
        limitations.append("sightlines not requested for this snapshot")

    return ContextRelation(
        subject_id=subject.player_id or "",
        player_id=other.player_id or "",
        relation=relation_kind,
        subject_side=subject.side,
        other_side=other.side,
        active=active,
        inactive_reason=inactive_reason,
        distance_2d=distance_2d,
        distance_3d=distance_3d,
        bearing_degrees=bearing,
        relative_yaw=relative_yaw,
        view_origin=subject_origin,
        other_view_origin=other_origin,
        static_sightline=sightline,
        static_effective_status=effective,
        navigation=nav,
        other_state=other,
        evidence=other.evidence,
        limitations=limitations,
    )


# --------------------------------------------------------------------------- #
# utility facts
# --------------------------------------------------------------------------- #
def _utility_facts(
    pool: GenerationPool, gen: Generation, lo: int, hi: int
) -> tuple[list[ContextUtilityFact], list[str]]:
    """Recorded utility facts whose interval covers ``[lo, hi]``.

    A fact is matched when its recorded interval intersects the queried range, so a
    single-tick query answers "utility active at this tick" and a window query
    answers "utility overlapping this window". Sources that record a duration
    instead of an end tick are matched on their derived expire tick.
    """
    facts: list[ContextUtilityFact] = []
    limitations: list[str] = []
    for source in UTILITY_SOURCES:
        if source.table not in gen.manifest.tables:
            limitations.append(f"utility table {source.table} is not present in this generation")
            continue
        name = source.columns
        tick_column = name["tick"]
        end_column = name.get("end_tick")

        if end_column is not None and source.reliable:
            covers = pl.col(end_column) >= lo
        elif "duration_seconds" in name and source.reliable:
            duration = pl.col(name["duration_seconds"]) * gen.tick_rate_hz
            covers = (pl.col(tick_column) + duration.round().fill_null(0.0)) >= lo
        else:
            covers = pl.col(tick_column) >= lo
        predicate = (pl.col(tick_column) <= hi) & covers
        try:
            frame = pool.read(gen, source.table, predicate=predicate, limit=MAX_UTILITY_ROWS)
        except AppError as exc:
            limitations.append(f"utility table {source.table} unreadable ({exc.code}: {exc.message})")
            continue

        semantic_columns = set(name.values())
        for row in frame.sort(["row_ordinal"]).to_dicts():
            tick = row.get(tick_column)
            if tick is None:
                limitations.append(f"utility table {source.table}: a row carries no tick and was skipped")
                continue
            row_limitations = list(source.limitations)
            end_tick: int | None = None
            if end_column is not None:
                raw_end = row.get(end_column)
                if raw_end is not None:
                    end_tick = int(raw_end)
            elif source.reliable and "duration_seconds" in name:
                duration = row.get(name["duration_seconds"])
                if duration is not None:
                    end_tick = int(tick) + int(round(float(duration) * gen.tick_rate_hz))
            if end_tick is not None and end_tick > hi:
                row_limitations.append(f"interval ends after the queried range end ({hi})")
            if end_tick is not None and end_tick < int(tick):
                row_limitations.append("end tick precedes start tick in the source row")
                end_tick = None

            ordinal = row.get("row_ordinal")
            owner = row.get(name["owner"]) if "owner" in name else None
            facts.append(
                ContextUtilityFact(
                    kind=str(row[name["kind"]])
                    if "kind" in name and row.get(name["kind"]) is not None
                    else source.kind,
                    owner_id=owner,
                    start_tick=int(tick),
                    end_tick=end_tick,
                    x=row.get(name["x"]) if "x" in name else None,
                    y=row.get(name["y"]) if "y" in name else None,
                    z=row.get(name["z"]) if "z" in name else None,
                    site=row.get(name["site"]) if "site" in name else None,
                    details={
                        column: value
                        for column, value in row.items()
                        if column not in semantic_columns and column != "row_ordinal"
                    },
                    semantics_reliable=source.reliable,
                    evidence_kind=source.evidence_kind,
                    evidence=None
                    if ordinal is None
                    else EvidenceRef(
                        demo_id=gen.demo_id,
                        generation_id=gen.generation_id,
                        profile_key=gen.profile_key,
                        dataset=source.table,
                        row_ordinal=int(ordinal),
                        tick=int(tick),
                        round_id=round_of(pool, gen, int(tick)),
                        player_ids=[owner] if owner else [],
                    ),
                    limitations=row_limitations,
                )
            )
    facts.sort(key=lambda fact: (fact.start_tick, fact.kind, fact.owner_id or ""))
    return facts, limitations


# --------------------------------------------------------------------------- #
# snapshots
# --------------------------------------------------------------------------- #
def _state_rows(pool: GenerationPool, gen: Generation, tick: int) -> list[dict[str, Any]]:
    frame = pool.read(
        gen,
        "player_state",
        columns=_STATE_COLUMNS,
        predicate=pl.col("tick") == tick,
        limit=STATE_TICK_LIMIT,
    )
    return frame.sort("row_ordinal").to_dicts()


def _lifecycle_rows(
    pool: GenerationPool, gen: Generation
) -> tuple[list[dict[str, Any]], int, list[str]]:
    """Bounded read of the recorded lifecycle table: rows, unattributed count, notes.

    The table is small (one row per connect/disconnect/spawn/team-change), so it is
    read whole under ``MAX_LIFECYCLE_ROWS``. Rows without a resolved ``player_id``
    are counted only: the source records an account id for disconnects alone, and a
    slot is never mapped onto a player here.
    """
    if LIFECYCLE_TABLE not in gen.manifest.tables:
        return [], 0, [
            f"this generation declares no {LIFECYCLE_TABLE} table; a missing participant state has no "
            "recorded lifecycle explanation here"
        ]
    try:
        frame = pool.read(gen, LIFECYCLE_TABLE, limit=MAX_LIFECYCLE_ROWS)
    except AppError as exc:
        return [], 0, [f"{LIFECYCLE_TABLE} is unreadable ({exc.code}: {exc.message})"]
    rows = frame.sort(["tick", "row_ordinal"]).to_dicts() if "row_ordinal" in frame.columns else frame.sort("tick").to_dicts()
    unattributed = sum(1 for row in rows if row.get("player_id") is None)
    return rows, unattributed, []


def _lifecycle_fact(row: Mapping[str, Any]) -> LifecycleFact:
    limitations = [
        "recorded lifecycle row supplied verbatim; a null account id means the source recorded no SteamID64",
    ]
    fact = LifecycleFact(
        tick=int(row["tick"]),
        kind=str(row.get("kind") or "unknown"),
        player_id=row.get("player_id"),
        user_slot=None if row.get("user_slot") is None else str(row.get("user_slot")),
        team=row.get("team"),
        previous_team=row.get("previous_team"),
        is_bot=row.get("is_bot"),
        reason_code=None if row.get("reason_code") is None else int(row["reason_code"]),
        ever_fully_connected=row.get("ever_fully_connected"),
        details={
            column: value
            for column, value in row.items()
            if column not in set(_LIFECYCLE_COLUMNS.values()) | {"row_ordinal"}
        },
        limitations=limitations,
    )
    return fact


def _lifecycle_bracket(
    rows: Sequence[Mapping[str, Any]], subject_id: str, tick: int
) -> tuple[LifecycleFact | None, LifecycleFact | None]:
    """Last subject-resolved lifecycle row at/before ``tick`` and the first one after."""
    before: LifecycleFact | None = None
    after: LifecycleFact | None = None
    for row in rows:
        if row.get("player_id") != subject_id:
            continue
        if int(row["tick"]) <= tick:
            before = _lifecycle_fact(row)
        elif after is None:
            after = _lifecycle_fact(row)
    return before, after


def _lifecycle_window(
    rows: Sequence[Mapping[str, Any]], subject_id: str, lo: int, hi: int
) -> list[LifecycleFact]:
    return [
        _lifecycle_fact(row)
        for row in rows
        if row.get("player_id") == subject_id and lo <= int(row["tick"]) <= hi
    ]


def _cross_pairs(
    rows: Sequence[Mapping[str, Any]],
    origins: Mapping[str, ViewOrigin],
    subject_id: str,
    subject_side: str | None,
    caps: _CapabilitySet,
    geometry: GeometryProvider | None,
    *,
    sightlines: bool,
    navigation: bool,
) -> tuple[list[CrossSightline], list[str]]:
    """Living teammate→opponent potential sightlines at one tick, nearest first.

    Only players whose recorded side is known take part: an unrecorded side is
    never guessed, so those players appear in no pair. The pair list is bounded by
    :data:`MAX_CROSS_PAIRS` (nearest kept).
    """
    limitations: list[str] = []
    if not sightlines:
        return [], ["teammate→opponent pair sightlines not requested for this snapshot"]
    if subject_side is None:
        return [], ["no teammate→opponent pairs evaluated: the subject's side is not recorded at this tick"]

    living = [row for row in rows if row.get("player_id") is not None and _alive(row)]
    unclassified = [
        row["player_id"] for row in living if row["player_id"] != subject_id and row.get("side") is None
    ]
    teammates = [
        row for row in living if row.get("side") == subject_side and row["player_id"] != subject_id
    ]
    opponents = [row for row in living if row.get("side") is not None and row.get("side") != subject_side]

    candidates: list[tuple[float, Mapping[str, Any], Mapping[str, Any]]] = []
    for teammate in teammates:
        first = _point(teammate)
        for opponent in opponents:
            second = _point(opponent)
            distance = None if first is None or second is None else dist2d(first[0], first[1], second[0], second[1])
            candidates.append((distance if distance is not None else float("inf"), teammate, opponent))
    candidates.sort(key=lambda item: (item[0], item[1]["player_id"] or "", item[2]["player_id"] or ""))

    if len(candidates) > MAX_CROSS_PAIRS:
        limitations.append(
            f"{len(candidates) - MAX_CROSS_PAIRS} living teammate→opponent pair(s) beyond the "
            f"{MAX_CROSS_PAIRS}-pair bound were not evaluated (nearest kept)"
        )
    if unclassified:
        limitations.append(
            f"{len(unclassified)} living player(s) have no recorded side and were placed in no pair"
        )
    if not candidates:
        limitations.append("no living teammate→opponent pair exists at this tick")

    pairs: list[CrossSightline] = []
    for _, teammate_row, opponent_row in candidates[:MAX_CROSS_PAIRS]:
        teammate_id = teammate_row["player_id"]
        opponent_id = opponent_row["player_id"]
        teammate_origin = origins[teammate_id]
        opponent_origin = origins[opponent_id]
        pair_limitations: list[str] = []
        first = _point(teammate_row)
        second = _point(opponent_row)
        distance_2d = distance_3d = bearing = relative_yaw = None
        if first is not None and second is not None:
            distance_2d = dist2d(first[0], first[1], second[0], second[1])
            distance_3d = dist3d(*first, *second)
            bearing = _bearing(first[0], first[1], second[0], second[1])
            relative_yaw = yaw_diff(teammate_origin.yaw, bearing)
        else:
            pair_limitations.append("distance and bearing unavailable: a position is missing")

        sightline, effective, notes = _sightline(geometry, caps, teammate_origin, opponent_origin)
        pair_limitations.extend(notes)
        nav = _navigation(geometry, caps, first, second) if navigation else None
        pairs.append(
            CrossSightline(
                teammate_id=teammate_id,
                opponent_id=opponent_id,
                teammate_origin=teammate_origin,
                opponent_origin=opponent_origin,
                distance_2d=distance_2d,
                distance_3d=distance_3d,
                bearing_degrees=bearing,
                relative_yaw=relative_yaw,
                static_sightline=sightline,
                static_effective_status=effective,
                navigation=nav,
                limitations=pair_limitations,
            )
        )
    return pairs, limitations


def _opponent_directions(
    relations: Sequence[ContextRelation],
) -> tuple[list[OpponentDirection], AngularSpread]:
    """Directions to the living opponents and the angular geometry between them."""
    directions = [
        OpponentDirection(
            player_id=relation.player_id,
            bearing_degrees=relation.bearing_degrees,
            relative_yaw=relation.relative_yaw,
        )
        for relation in relations
        if relation.relation == "opponent"
    ]
    directions.sort(key=lambda entry: (entry.relative_yaw is None, entry.relative_yaw or 0.0, entry.player_id))

    spread = AngularSpread(
        opponent_count=len(directions),
        subject_yaw=relations[0].view_origin.yaw if relations else None,
        subject_yaw_recorded=bool(relations) and relations[0].view_origin.yaw is not None,
    )
    relative = [entry.relative_yaw for entry in directions if entry.relative_yaw is not None]
    if len(relative) < 2:
        spread.limitations.append("angular span and separation need at least two opponent directions")
        return directions, spread

    ordered = sorted(relative)
    gaps = [ordered[index + 1] - ordered[index] for index in range(len(ordered) - 1)]
    gaps.append(360.0 - (ordered[-1] - ordered[0]))
    spread.span_degrees = 360.0 - max(gaps)
    largest = 0.0
    for index, first in enumerate(ordered):
        for second in ordered[index + 1 :]:
            difference = yaw_diff(first, second)
            if difference is not None and abs(difference) > largest:
                largest = abs(difference)
    spread.max_pair_separation_degrees = largest
    return directions, spread


def _track(
    pool: GenerationPool,
    gen: Generation,
    player_id: str,
    lo: int,
    hi: int,
    *,
    relation: RelationKind = "unknown",
    side: str | None = None,
    is_subject: bool = False,
) -> ParticipantTrack:
    """Bounded verbatim sample track on an even stride, always ending at ``hi``."""
    span = max(hi - lo + 1, 1)
    stride = max(1, math.ceil(span / MAX_TRACK_SAMPLES))
    grid = sorted(set(range(lo, hi + 1, stride)) | {hi})
    frame = pool.read(
        gen,
        "player_state",
        columns=["row_ordinal", "tick", "player_id", "x", "y", "z", "yaw", "health"],
        predicate=(pl.col("player_id") == player_id) & (pl.col("tick") >= lo) & (pl.col("tick") <= hi),
        limit=STATE_TICK_LIMIT * 4,
    )
    by_tick: dict[int, dict[str, Any]] = {}
    for row in frame.sort("row_ordinal").to_dicts():
        by_tick[int(row["tick"])] = row

    samples = [
        TrajectorySample(
            tick=tick,
            x=by_tick[tick].get("x"),
            y=by_tick[tick].get("y"),
            z=by_tick[tick].get("z"),
            yaw=by_tick[tick].get("yaw"),
            health=by_tick[tick].get("health"),
        )
        for tick in grid
        if tick in by_tick
    ]
    present = [sample.tick for sample in samples]
    track = ParticipantTrack(
        player_id=player_id,
        relation=relation,  # type: ignore[arg-type]
        side=side,
        is_subject=is_subject,
        stride_ticks=stride,
        from_tick=present[0] if present else None,
        to_tick=present[-1] if present else None,
        samples=samples,
        missing_samples=len(grid) - len(samples),
        limitations=["verbatim recorded samples only; missing grid ticks are never interpolated"],
    )
    if not samples:
        track.limitations.append(f"no recorded rows for {player_id} in [{lo}, {hi}]")
    return track


def _facing_delta(track: ParticipantTrack) -> tuple[FacingDelta | None, str | None]:
    """View-yaw change between the first and last *living* recorded samples of a track."""
    living = [sample for sample in track.samples if sample.health is not None and sample.health > 0 and sample.yaw is not None]
    if len(living) < 2:
        return None, (
            "subject facing delta not reported: fewer than two living samples with a recorded view yaw in the window"
        )
    first, last = living[0], living[-1]
    delta = yaw_diff(first.yaw, last.yaw)
    if delta is None:
        return None, "subject facing delta not reported: the recorded view yaw is not finite"
    return (
        FacingDelta(
            from_tick=first.tick,
            to_tick=last.tick,
            yaw_from=float(first.yaw),
            yaw_to=float(last.yaw),
            delta_degrees=delta,
            stride_ticks=track.stride_ticks,
            limitations=[
                "recorded view yaw only; a player between samples may have turned arbitrarily",
            ],
        ),
        None,
    )


def _counts(rows: Sequence[Mapping[str, Any]]) -> ContextCounts:
    counts = ContextCounts(state_rows=len(rows))
    for row in rows:
        if row.get("player_id") is not None:
            counts.identity_identified += 1
        else:
            counts.identity_null += 1
            if _alive(row):
                counts.identity_null_alive += 1
        if _alive(row):
            counts.living += 1
        elif row.get("health") is None:
            counts.unknown_health += 1
        else:
            counts.dead += 1
    return counts


def _lifecycle_context(
    pool: GenerationPool, gen: Generation, subject_id: str, tick: int, *, needed: bool
) -> tuple[LifecycleFact | None, LifecycleFact | None, int, list[str]]:
    """The subject's recorded lifecycle bracket around ``tick``, read only when it explains something."""
    if not needed:
        return None, None, 0, []
    rows, unattributed, notes = _lifecycle_rows(pool, gen)
    before, after = _lifecycle_bracket(rows, subject_id, tick)
    return before, after, unattributed, notes


def _empty_snapshot(
    gen: Generation,
    caps: _CapabilitySet,
    subject_id: str,
    tick: int,
    round_id: int | None,
    counts: ContextCounts,
    *,
    exact: bool,
    limitations: list[str],
    lifecycle_before: LifecycleFact | None = None,
    lifecycle_after: LifecycleFact | None = None,
    lifecycle_unattributed_rows: int = 0,
    participants: list[ContextStateRef] | None = None,
    utility_facts: list[ContextUtilityFact] | None = None,
) -> ContextSnapshot:
    return ContextSnapshot(
        demo_id=gen.demo_id,
        generation_id=gen.generation_id,
        profile_key=gen.profile_key,
        subject_id=subject_id,
        tick=tick,
        round_id=round_id,
        tick_rate_hz=gen.tick_rate_hz,
        actual_tick=tick if exact else None,
        exact=exact,
        gap_ticks=0 if exact else None,
        subject=None,
        subject_alive=False,
        relations=[],
        inactive_relations=[],
        participants=participants or [],
        pair_relations=[],
        opponent_directions=[],
        counts=counts,
        position_change=None,
        utility=utility_facts or [],
        lifecycle_before=lifecycle_before,
        lifecycle_after=lifecycle_after,
        lifecycle_unattributed_rows=lifecycle_unattributed_rows,
        capabilities=caps.capabilities,
        provenance=_provenance(gen, caps),
        limitations=limitations,
    )


def _snapshot(
    pool: GenerationPool,
    gen: Generation,
    subject_id: str,
    tick: int,
    caps: _CapabilitySet,
    geometry: GeometryProvider | None,
    *,
    stride_ticks: int,
    position_window_ticks: int,
    sightlines: bool,
    navigation: bool,
    utility: bool,
    cross_pairs: bool = False,
) -> ContextSnapshot:
    round_id = round_of(pool, gen, tick)
    rows = _state_rows(pool, gen, tick)
    counts = _counts(rows)
    limitations: list[str] = []
    facts, utility_notes = _utility_facts(pool, gen, tick, tick) if utility else ([], [])
    limitations.extend(utility_notes)

    if not rows:
        limitations.append(f"no player_state rows at tick {tick}; nothing is snapped to a nearby tick")
        before, after, unattributed, lifecycle_notes = _lifecycle_context(
            pool, gen, subject_id, tick, needed=True
        )
        limitations.extend(lifecycle_notes)
        if before is not None or after is not None:
            limitations.append(
                "the subject's recorded lifecycle rows bracket this tick (see lifecycle_before/lifecycle_after); "
                "missing state is never reported as inactivity"
            )
        return _empty_snapshot(
            gen,
            caps,
            subject_id,
            tick,
            round_id,
            counts,
            exact=False,
            limitations=limitations,
            lifecycle_before=before,
            lifecycle_after=after,
            lifecycle_unattributed_rows=unattributed,
            utility_facts=facts,
        )

    identified = [row for row in rows if row.get("player_id") is not None]
    subject_row: dict[str, Any] | None = None
    duplicates = 0
    for row in identified:
        if row["player_id"] == subject_id:
            if subject_row is not None:
                duplicates += 1
            subject_row = row
    if subject_row is None:
        roster = gen.players
        if roster is not None and roster.height:
            if subject_id not in set(roster.get_column("player_id").to_list()):
                limitations.append(
                    f"subject {subject_id} is not in this generation's player roster; the requested id was "
                    "used verbatim and never substituted"
                )
        limitations.append(f"subject {subject_id} has no player_state row at tick {tick}")
        before, after, unattributed, lifecycle_notes = _lifecycle_context(
            pool, gen, subject_id, tick, needed=True
        )
        limitations.extend(lifecycle_notes)
        if before is not None or after is not None:
            limitations.append(
                "the subject's recorded lifecycle rows bracket this tick (see lifecycle_before/lifecycle_after); "
                "a gap in recorded state is never reported as inactivity"
            )
        return _empty_snapshot(
            gen,
            caps,
            subject_id,
            tick,
            round_id,
            counts,
            exact=True,
            limitations=limitations,
            lifecycle_before=before,
            lifecycle_after=after,
            lifecycle_unattributed_rows=unattributed,
            participants=[_state_ref(gen, row, round_id) for row in identified[:MAX_PARTICIPANTS]],
            utility_facts=facts,
        )

    if duplicates:
        limitations.append(
            f"{duplicates} duplicate extra state row(s) for {subject_id} at tick {tick}; the last ordinal is used"
        )
    if counts.identity_null:
        detail = (
            f" ({counts.identity_null_alive} of them carry health > 0 and are flagged as unidentified "
            "living rows)"
            if counts.identity_null_alive
            else " (all with health == 0 on this data, i.e. engine corpse entities)"
        )
        limitations.append(
            f"{counts.identity_null} state row(s) at this tick have a null player_id; they are counted but "
            f"never joined to a player{detail}"
        )

    # one eye estimate per identified player, reused by both relation families
    origins = {row["player_id"]: _view_origin(row) for row in identified}
    subject_origin = origins[subject_id]
    others = [row for row in identified if row["player_id"] != subject_id]
    relations = []
    for row in others:
        kind = _relation_kind(subject_row.get("side"), row.get("side"))
        if kind == "teammate":
            counts.same_side += 1
        elif kind == "opponent":
            counts.opposite_side += 1
        else:
            counts.unknown_side += 1
        relations.append(
            _relation(
                gen,
                subject_row,
                row,
                round_id,
                caps,
                geometry,
                subject_origin=subject_origin,
                other_origin=origins[row["player_id"]],
                sightlines=sightlines,
                navigation=navigation,
            )
        )

    active = [relation for relation in relations if relation.active]
    inactive = [relation for relation in relations if not relation.active]
    key = lambda relation: (relation.distance_2d is None, relation.distance_2d or 0.0, relation.player_id)
    active.sort(key=key)
    inactive.sort(key=key)

    if len(relations) > MAX_RELATIONS:
        limitations.append(
            f"{len(relations) - MAX_RELATIONS} relation(s) beyond the {MAX_RELATIONS}-relation bound were not "
            "reported (nearest kept)"
        )
        active = active[:MAX_RELATIONS]
        inactive = inactive[: max(MAX_RELATIONS - len(active), 0)]

    counts.active_relations = len(active)
    counts.inactive_relations = len(inactive)
    for relation in active:
        status = relation.static_effective_status
        if relation.relation == "opponent":
            if status == "static_clear":
                counts.opponent_static_clear += 1
            elif status == "static_blocked":
                counts.opponent_static_blocked += 1
            else:
                counts.opponent_static_unknown += 1
        if status in ("static_clear", "static_blocked"):
            counts.sightlines_evaluated += 1
        else:
            counts.sightlines_unavailable += 1

    if not _alive(subject_row):
        limitations.append("subject is not observed alive at this tick; every relation is reported inactive")

    before, after, unattributed, lifecycle_notes = _lifecycle_context(
        pool, gen, subject_id, tick, needed=not _alive(subject_row)
    )
    limitations.extend(lifecycle_notes)
    if before is not None or after is not None:
        limitations.append(
            "the subject's recorded lifecycle rows bracket this tick (see lifecycle_before/lifecycle_after)"
        )

    pairs: list[CrossSightline] = []
    if cross_pairs:
        pairs, pair_notes = _cross_pairs(
            identified,
            origins,
            subject_id,
            subject_row.get("side"),
            caps,
            geometry,
            sightlines=sightlines,
            navigation=navigation,
        )
        limitations.extend(pair_notes)
        counts.cross_pairs_evaluated = sum(
            1 for pair in pairs if pair.static_effective_status in ("static_clear", "static_blocked")
        )

    directions, angular_spread = _opponent_directions(active)
    if counts.sightlines_evaluated:
        limitations.append(
            f"{counts.sightlines_evaluated} static sightline(s) were resolved against the installed map build "
            f"(asset {caps.map_asset_id or 'unknown'}, match {caps.map_match_status}); scope {STATIC_SCOPE}, "
            "not confirmed historical exposure"
        )

    position_change = (
        _position_change(pool, gen, subject_id, tick, stride_ticks, position_window_ticks)
        if position_window_ticks > 0
        else None
    )

    return ContextSnapshot(
        demo_id=gen.demo_id,
        generation_id=gen.generation_id,
        profile_key=gen.profile_key,
        subject_id=subject_id,
        tick=tick,
        round_id=round_id,
        tick_rate_hz=gen.tick_rate_hz,
        actual_tick=tick,
        exact=True,
        gap_ticks=0,
        subject=_state_ref(gen, subject_row, round_id),
        subject_alive=_alive(subject_row),
        relations=active,
        inactive_relations=inactive,
        participants=[_state_ref(gen, row, round_id) for row in identified[:MAX_PARTICIPANTS]],
        pair_relations=pairs,
        opponent_directions=directions,
        angular_spread=angular_spread,
        counts=counts,
        position_change=position_change,
        utility=facts,
        lifecycle_before=before,
        lifecycle_after=after,
        lifecycle_unattributed_rows=unattributed,
        capabilities=caps.capabilities,
        provenance=_provenance(gen, caps),
        limitations=limitations,
    )


# --------------------------------------------------------------------------- #
# exposure
# --------------------------------------------------------------------------- #
def _stride_for(span: int) -> int:
    if span <= 0:
        return 1
    return max(1, math.ceil((span + 1) / MAX_EXPOSURE_SAMPLES))


def _exposure(
    pool: GenerationPool,
    gen: Generation,
    caps: _CapabilitySet,
    geometry: GeometryProvider | None,
    subject_id: str,
    lo: int,
    hi: int,
) -> EncounterExposure:
    """Earliest *sampled* static exposure, or an explicit reason it is unknown."""
    clamped = False
    if hi - lo + 1 > MAX_EXPOSURE_WINDOW_TICKS:
        hi = lo + MAX_EXPOSURE_WINDOW_TICKS - 1
        clamped = True

    stride = _stride_for(hi - lo)
    grid = sorted(set(range(lo, hi + 1, stride)) | {hi})
    sampling = ExposureSampling(
        start_tick=lo,
        end_tick=hi,
        stride_ticks=stride,
        samples=len(grid),
        ticks=grid,
        tick_rate_hz=gen.tick_rate_hz,
    )
    exposure = EncounterExposure(status="unknown", sampling=sampling)
    if clamped:
        exposure.limitations.append(
            f"exposure scan truncated to {MAX_EXPOSURE_WINDOW_TICKS} ticks from the encounter window start"
        )

    if geometry is None or caps.map_name is None or caps.capabilities.sightlines.status not in (
        "available",
        "partial",
    ):
        exposure.status = "unsupported"
        exposure.limitations.append(
            "earliest exposure not derived: "
            + (
                "geometry service unavailable for this map"
                if geometry is None or caps.map_name is None
                else f"static sightlines are {caps.capabilities.sightlines.status} for this map"
            )
        )
        exposure.unknown_dynamics.append(
            "the exposure scan was not performed, so the sampling grid below was planned but not read"
        )
        return exposure

    frame = pool.read(
        gen,
        "player_state",
        columns=_STATE_COLUMNS,
        predicate=(pl.col("tick") >= lo) & (pl.col("tick") <= hi),
        limit=120_000,
    )
    by_tick: dict[int, list[dict[str, Any]]] = {}
    for row in frame.sort("row_ordinal").to_dicts():
        by_tick.setdefault(int(row["tick"]), []).append(row)

    opponents: dict[str, OpponentExposure] = {}
    unqualified: dict[str, int] = {}
    mismatch_ticks = 0
    unknown_stance_ticks = 0
    missing_ticks = 0

    def note(reason: str) -> None:
        unqualified[reason] = unqualified.get(reason, 0) + 1

    for tick in grid:
        rows = by_tick.get(tick)
        if not rows:
            missing_ticks += 1
            continue
        subject_row = next(
            (row for row in rows if row.get("player_id") == subject_id),
            None,
        )
        if subject_row is None:
            missing_ticks += 1
            continue
        if not _alive(subject_row):
            continue
        sampling.subject_alive_samples += 1
        subject_origin = _view_origin(subject_row)
        if _eye_point(subject_origin) is None:
            unknown_stance_ticks += 1
            note("subject eye position unknown (missing stance or position)")
            continue

        for row in rows:
            other_id = row.get("player_id")
            if other_id is None or other_id == subject_id:
                continue
            if _relation_kind(subject_row.get("side"), row.get("side")) != "opponent":
                continue
            if not _alive(row):
                continue
            entry = opponents.get(other_id) or OpponentExposure(player_id=other_id)
            opponents[other_id] = entry
            if entry.first_alive_tick is None:
                entry.first_alive_tick = tick
            other_origin = _view_origin(row)
            if _eye_point(other_origin) is None:
                entry.unknown_ticks += 1
                note("opponent eye position unknown (missing stance or position)")
                continue
            entry.checked_ticks += 1
            sightline, effective, notes = _sightline(geometry, caps, subject_origin, other_origin)
            for text in notes:
                if text not in entry.limitations:
                    entry.limitations.append(text)
            if sightline is None:
                entry.unknown_ticks += 1
                note("sightline unavailable")
                continue
            if sightline.match_status == "mismatch":
                entry.mismatched_ticks += 1
                mismatch_ticks += 1
                note("installed map assets mismatch the recording")
            if effective == "static_clear":
                entry.clear_ticks += 1
                if entry.earliest_clear_tick is None and sightline.match_status != "mismatch":
                    entry.earliest_clear_tick = tick
            elif effective == "static_blocked":
                entry.blocked_ticks += 1
            else:
                entry.unknown_ticks += 1

    exposure.opponents = sorted(opponents.values(), key=lambda entry: entry.player_id)
    qualified = [
        (entry.earliest_clear_tick, entry.player_id)
        for entry in exposure.opponents
        if entry.earliest_clear_tick is not None
    ]
    if qualified:
        tick, player_id = min(qualified, key=lambda item: (item[0], item[1]))
        exposure.status = "qualified"
        exposure.earliest_exposure_tick = tick
        exposure.earliest_exposure_player_id = player_id
    elif sampling.subject_alive_samples == 0:
        exposure.status = "not_applicable"
        exposure.limitations.append(
            "subject was never observed alive at a sampled tick in this window; a dead subject carries "
            "recorded state but no exposure"
        )
    else:
        exposure.status = "unknown"
        exposure.limitations.append(
            "no opponent was observed alive on a sampled tick inside this window"
            if not exposure.opponents
            else "no sampled tick had a clear sightline between living, stance-known endpoints"
        )

    if unknown_stance_ticks:
        exposure.unknown_dynamics.append(
            f"{unknown_stance_ticks} sampled tick(s) had an unknown subject eye position (missing stance or position)"
        )
    if missing_ticks:
        exposure.unknown_dynamics.append(f"{missing_ticks} sampled tick(s) had no subject state row and were skipped")
    if mismatch_ticks:
        exposure.mismatches.append(
            f"{mismatch_ticks} sampled sightline(s) used installed assets that do not match the recording and "
            "cannot prove the historical sightline"
        )
    for reason, count in sorted(unqualified.items()):
        exposure.unknown_dynamics.append(f"{count} sampled sightline(s) not clear: {reason}")
    exposure.unknown_dynamics.append(
        "player dynamics between sampled ticks, intent and perception are unknown here; only static geometry and "
        "recorded state are reported"
    )
    if exposure.status == "qualified":
        exposure.limitations.append(
            "earliest exposure is the earliest *sampled* tick with a static clear sightline between living, "
            "stance-known endpoints"
        )
    exposure.limitations.append(
        f"every sightline here is scoped to the installed map build ({STATIC_SCOPE}, asset "
        f"{caps.map_asset_id or 'unknown'}, match {caps.map_match_status}); a clear reading is not confirmed "
        "historical exposure, and nothing about perception, intent or ability is claimed"
    )
    return exposure


# --------------------------------------------------------------------------- #
# service
# --------------------------------------------------------------------------- #
class ContextService:
    """Exact-tick context reconstruction over one pinned generation.

    ``geometry`` is the injected slice-C service. ``None`` degrades the geometry
    capabilities explicitly instead of fabricating sightlines; that path exists for
    authored fixtures and a genuinely missing injected dependency.
    """

    def __init__(self, pool: GenerationPool, geometry: GeometryProvider | None = None) -> None:
        self.pool = pool
        self.geometry = geometry

    # -- capability probe --------------------------------------------------
    def utility_tables(self, gen: Generation) -> list[str]:
        """Utility tables this generation actually declares that Context reads."""
        return [source.table for source in UTILITY_SOURCES if source.table in gen.manifest.tables]

    # -- one tick ----------------------------------------------------------
    def at(
        self,
        gen: Generation,
        subject_id: str,
        tick: int,
        *,
        stride_ticks: int = DEFAULT_STRIDE_TICKS,
        position_window_ticks: int = DEFAULT_POSITION_WINDOW_TICKS,
        sightlines: bool = True,
        navigation: bool = False,
        cross_pairs: bool = False,
    ) -> ContextSnapshot:
        """Exact-tick snapshot for ``subject_id``; a tick with no rows reports ``exact=False``.

        ``cross_pairs`` additionally resolves living teammate→opponent potential
        sightlines at this tick (bounded by ``MAX_CROSS_PAIRS``), which is off by
        default because ``encounter`` drives that scan.
        """
        if not subject_id:
            raise _invalid("subject_id must be a non-empty player id")
        if tick < 0:
            raise _invalid("tick must be non-negative")
        if stride_ticks < 1:
            raise _invalid("stride_ticks must be positive")
        if position_window_ticks < 0:
            raise _invalid("position_window_ticks must be non-negative")

        utility_tables = self.utility_tables(gen)
        caps = _capability_set(self.geometry, gen, utility_tables)
        return _snapshot(
            self.pool,
            gen,
            subject_id,
            tick,
            caps,
            self.geometry,
            stride_ticks=stride_ticks,
            position_window_ticks=position_window_ticks,
            sightlines=sightlines,
            navigation=navigation,
            utility=bool(utility_tables),
            cross_pairs=cross_pairs,
        )

    # -- one encounter -----------------------------------------------------
    def encounter(
        self,
        gen: Generation,
        detail: EncounterDetail,
        *,
        pre_offsets_seconds: Sequence[float] = DEFAULT_PRE_OFFSETS_SECONDS,
        post_offsets_seconds: Sequence[float] = DEFAULT_POST_OFFSETS_SECONDS,
        stride_ticks: int = DEFAULT_STRIDE_TICKS,
        navigation: bool = False,
    ) -> EncounterContext:
        """Anchor/pre-contact snapshots, matched utility intervals and qualified exposure.

        ``detail`` must belong to ``gen``: the encounter and the generation are both
        pinned, and a mismatch is refused instead of analysed across revisions.
        """
        if len(pre_offsets_seconds) > MAX_OFFSETS or len(post_offsets_seconds) > MAX_OFFSETS:
            raise _invalid(f"at most {MAX_OFFSETS} offsets per side are accepted")
        if any(offset < 0 for offset in pre_offsets_seconds) or any(offset < 0 for offset in post_offsets_seconds):
            raise _invalid("offsets must be non-negative seconds")
        if stride_ticks < 1:
            raise _invalid("stride_ticks must be positive")

        summary = detail.summary
        if summary.generation_id != gen.generation_id or summary.demo_id != gen.demo_id:
            raise _invalid(
                f"encounter {summary.encounter_id} belongs to {summary.demo_id}/{summary.generation_id}, "
                f"not {gen.demo_id}/{gen.generation_id}"
            )
        subject_id = summary.subject_id
        if not subject_id:
            raise _invalid("encounter summary carries no subject_id")

        window = detail.source_window
        start_tick = int(window.window_start_tick)
        end_tick = int(window.window_end_tick)
        if end_tick < start_tick:
            raise _invalid(f"encounter {summary.encounter_id} has a window ending before it starts")

        utility_tables = self.utility_tables(gen)
        caps = _capability_set(self.geometry, gen, utility_tables)
        limitations = _merge_limitations(detail.limitations, summary.limitations)
        limitations.append(
            f"snapshots and the exposure scan cover the encounter window [{start_tick}, {end_tick}] "
            f"(interaction bounds {summary.start_tick}-{summary.end_tick})"
        )
        if window.truncated_start or window.truncated_end:
            limitations.append(
                f"encounter window clipped by the round bound "
                f"[{window.round_start_tick}, {window.round_end_tick}]"
            )
        if detail.trajectory_missing_ranges:
            limitations.append(
                f"subject trajectory has {len(detail.trajectory_missing_ranges)} unrecorded tick range(s) "
                "inside the window; none were filled"
            )

        interaction: int | None = summary.first_interaction_tick
        if interaction is None:
            limitations.append(
                "encounter has no first interaction tick; contact offsets are measured from the window start"
            )
            interaction = start_tick

        planned: list[tuple[str, AnchorKind, str, int, float | None, str | None]] = []
        for anchor in summary.anchors:
            if anchor.status != "observed" or anchor.tick is None:
                limitations.append(
                    f"anchor {anchor.anchor_id} ({anchor.kind}) is unavailable for this episode; "
                    "no snapshot was taken for it"
                )
                continue
            tick = int(anchor.tick)
            if not start_tick <= tick <= end_tick:
                limitations.append(
                    f"anchor {anchor.anchor_id} ({anchor.kind}) at tick {tick} lies outside the encounter "
                    f"window [{start_tick}, {end_tick}]; nothing was snapshotted outside the window"
                )
                continue
            source = f" ({anchor.dataset} row {anchor.row_ordinal})" if anchor.dataset is not None else ""
            resolution = f", resolution {anchor.resolution}" if anchor.resolution is not None else ""
            planned.append(
                (
                    anchor.anchor_id,
                    anchor.evidence_kind,
                    f"encounter anchor {anchor.kind}{resolution}{source}",
                    tick,
                    None,
                    anchor.kind,
                )
            )
        for seconds in pre_offsets_seconds:
            planned.append(
                (
                    f"pre_offset_{seconds:g}s",
                    "computed",
                    "contact offset before the first interaction",
                    int(interaction) - int(round(seconds * gen.tick_rate_hz)),
                    float(seconds),
                    None,
                )
            )
        for seconds in post_offsets_seconds:
            planned.append(
                (
                    f"post_offset_{seconds:g}s",
                    "computed",
                    "contact offset after the first interaction",
                    int(interaction) + int(round(seconds * gen.tick_rate_hz)),
                    float(seconds),
                    None,
                )
            )
        planned.append(("window_start", "recorded", "encounter window start", start_tick, None, None))
        planned.append(("window_end", "recorded", "encounter window end", end_tick, None, None))

        # Cross-pair sightlines are the most expensive part of a snapshot, so they are
        # resolved at a bounded set of anchors: evidence-backed anchors first, then the
        # remaining offsets in planned order.
        wanted = [entry[3] for entry in planned if entry[1] == "recorded"]
        wanted += [entry[3] for entry in planned if entry[1] != "recorded"]
        cross_ticks: list[int] = []
        for candidate in wanted:
            if candidate < 0 or candidate in cross_ticks:
                continue
            if len(cross_ticks) >= MAX_CROSS_PAIR_ANCHORS:
                break
            cross_ticks.append(candidate)
        snapshotted = {candidate for candidate in wanted if candidate >= 0}
        if len(snapshotted) > len(cross_ticks):
            limitations.append(
                f"teammate→opponent pair sightlines were resolved at {len(cross_ticks)} of "
                f"{len(snapshotted)} snapshotted ticks (bound {MAX_CROSS_PAIR_ANCHORS})"
            )

        snapshots: list[ContextAnchorSnapshot] = []
        seen: dict[int, int] = {}
        for name, kind, reason, tick, offset, anchor_kind in planned:
            if tick < 0:
                limitations.append(f"{name}: tick {tick} is before tick 0 and was not snapshotted")
                continue
            if tick in seen:
                existing = snapshots[seen[tick]]
                existing.reason = f"{existing.reason}; also {name}"
                continue
            if len(snapshots) >= MAX_SNAPSHOTS:
                limitations.append(f"snapshot bound of {MAX_SNAPSHOTS} reached; {name} was not snapshotted")
                continue
            seen[tick] = len(snapshots)
            snapshots.append(
                ContextAnchorSnapshot(
                    name=name,
                    kind=kind,
                    anchor_kind=anchor_kind,
                    reason=reason,
                    requested_tick=tick,
                    offset_seconds=offset,
                    snapshot=_snapshot(
                        self.pool,
                        gen,
                        subject_id,
                        tick,
                        caps,
                        self.geometry,
                        stride_ticks=stride_ticks,
                        position_window_ticks=0,
                        sightlines=True,
                        navigation=navigation,
                        utility=False,
                        cross_pairs=tick in cross_ticks,
                    ),
                )
            )
        snapshots.sort(key=lambda entry: (entry.requested_tick or 0, entry.name))

        subject_track = _track(self.pool, gen, subject_id, start_tick, end_tick, is_subject=True)
        tracks = [
            _track(
                self.pool,
                gen,
                participant.player_id,
                start_tick,
                end_tick,
                relation=participant.relation,
                side=participant.side,
            )
            for participant in detail.participants[:MAX_TRACKED_PARTICIPANTS]
        ]
        if len(detail.participants) > MAX_TRACKED_PARTICIPANTS:
            limitations.append(
                f"{len(detail.participants) - MAX_TRACKED_PARTICIPANTS} participant track(s) beyond the "
                f"{MAX_TRACKED_PARTICIPANTS}-track bound were not sampled"
            )
        facing_delta, facing_note = _facing_delta(subject_track)
        if facing_note:
            limitations.append(facing_note)

        facts, utility_notes = _utility_facts(self.pool, gen, start_tick, end_tick)
        limitations.extend(utility_notes)
        lifecycle_rows, lifecycle_unattributed, lifecycle_notes = _lifecycle_rows(self.pool, gen)
        limitations.extend(lifecycle_notes)
        lifecycle = _lifecycle_window(lifecycle_rows, subject_id, start_tick, end_tick)
        if lifecycle_rows and not lifecycle:
            limitations.append(
                "no recorded lifecycle row of the subject falls inside this window; a gap in recorded state "
                "has no lifecycle explanation here and is never reported as inactivity"
            )
        exposure = _exposure(self.pool, gen, caps, self.geometry, subject_id, start_tick, end_tick)

        return EncounterContext(
            demo_id=gen.demo_id,
            generation_id=gen.generation_id,
            profile_key=gen.profile_key,
            encounter_id=summary.encounter_id,
            round_id=int(summary.round_id),
            subject_id=subject_id,
            start_tick=start_tick,
            end_tick=end_tick,
            interaction_start_tick=int(summary.start_tick),
            interaction_end_tick=int(summary.end_tick),
            first_interaction_tick=None if summary.first_interaction_tick is None else int(summary.first_interaction_tick),
            snapshots=snapshots,
            subject_track=subject_track,
            participant_tracks=tracks,
            subject_facing_delta=facing_delta,
            exposure=exposure,
            utility=facts,
            lifecycle=lifecycle,
            lifecycle_unattributed_rows=lifecycle_unattributed,
            capabilities=caps.capabilities,
            provenance=_provenance(gen, caps),
            limitations=limitations,
        )

    # -- encounter movement ------------------------------------------------
    def subject_position_change(
        self,
        gen: Generation,
        subject_id: str,
        start_tick: int,
        end_tick: int,
        *,
        stride_ticks: int = DEFAULT_STRIDE_TICKS,
    ) -> ContextPositionChange:
        """Bounded observed movement of the subject across ``[start_tick, end_tick]``.

        Derived metrics are reported only when the living samples form one contiguous
        run inside a single round; otherwise the counts are returned with ``None``
        metrics and a limitation naming the break.
        """
        if stride_ticks < 1:
            raise _invalid("stride_ticks must be positive")
        if end_tick < start_tick:
            raise _invalid("end_tick must not precede start_tick")
        center = (start_tick + end_tick) // 2
        change = _position_change(
            self.pool, gen, subject_id, center, stride_ticks, max(end_tick - center, center - start_tick)
        )
        assert change is not None  # the window is positive by construction
        return change

"""Typed context reconstruction over one pinned generation.

Units and conventions
---------------------
* Coordinates are Hammer world units, Z-up, exactly as stored in
  ``player_state`` (``x``/``y``/``z``); distances and positions are never
  re-projected or converted. ``yaw`` is degrees in ``[-180, 180]``.
* ``relative_yaw`` is the subject's *shortest signed* planar bearing towards the
  other player minus the subject's stored view yaw (``spatial.yaw_diff(yaw,
  bearing)`` in ``[-180, 180]``): ``0`` means the other player is straight ahead
  and ``-90`` to the subject's right.
* One snapshot belongs to exactly one ``generation_id``. Nothing drifts onto a
  newer head.
* Exact ticks only. A requested tick with no ``player_state`` rows reports
  ``exact=False`` with an empty subject/relation set; ticks are never snapped or
  interpolated to a nearby observation.
* Relationship membership is resolved *per tick* from that tick's rows, so a
  side swap flips teammate/opponent classification from one tick to the next
  with no carry-forward.
* Active relationships require ``health > 0`` on both endpoints. Rows with
  ``health == 0``, unknown health, or a null ``player_id`` are recorded in
  counts but are never counted as available players, and a dead subject never
  contributes to an exposure count.
* Geometry status is never promoted: ``unknown``, ``unsupported`` and results
  produced against mismatched installed assets are never reported as clear
  sightlines. There is no awareness, risk, or coaching vocabulary here, and no
  claim about what any player could see or know.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .contracts import EvidenceRef, Model
from .evidence import CapabilityStatus, EvidenceCapability, EvidenceKind, ReconstructionProvenance
from .geometry import NavigationResult, SegmentResult, SegmentStatus

RelationKind = Literal["teammate", "opponent", "unknown"]
ViewOriginMode = Literal["recorded", "estimated_standing", "estimated_crouched", "unknown"]
ExposureStatus = Literal["qualified", "unknown", "unsupported", "not_applicable"]
AnchorKind = Literal["recorded", "computed", "geometry_dependent", "estimated", "unsupported"]

#: Recorded eye height above the player origin (Hammer units) used when the
#: generation carries no recorded view origin. Both are *estimates*.
STANDING_EYE_HEIGHT_UNITS = 64.0
CROUCHED_EYE_HEIGHT_UNITS = 46.0

#: Bounds for the widest context payloads. Nothing scales with match length.
MAX_CROSS_PAIRS = 20
MAX_PARTICIPANTS = 32
MAX_TRACKED_PARTICIPANTS = 12
MAX_TRACK_SAMPLES = 128
MAX_CROSS_PAIR_ANCHORS = 8

#: Every sightline's scope. A static result describes the *installed* map build,
#: never a confirmed historical sightline or anyone's perception.
STATIC_SCOPE = "installed_map_build"


class ContextCapabilities(Model):
    """Per-snapshot capability report; every field names its source."""

    state: EvidenceCapability
    geometry: EvidenceCapability
    sightlines: EvidenceCapability
    navigation: EvidenceCapability
    utility: EvidenceCapability
    exposure: EvidenceCapability
    view_origin: EvidenceCapability
    lifecycle: EvidenceCapability
    limitations: list[str] = Field(default_factory=list)


class ViewOrigin(Model):
    """Where a player's eye is taken to be, and how that was established.

    ``recorded`` means the generation itself carries an observed view origin, and
    then — and only then — ``qualified`` is ``True``. Every other mode is an
    explicitly unqualified estimate derived from the stance recorded at that tick,
    never a measurement, so a sightline built from it always keeps its endpoint
    limitation.
    """

    mode: ViewOriginMode
    x: float | None = None
    y: float | None = None
    z: float | None = None
    yaw: float | None = None
    pitch: float | None = None
    height_units: float | None = None
    qualified: bool = False
    """``True`` only when ``mode == "recorded"``; estimates are unqualified."""
    source: str = "player_state"
    limitations: list[str] = Field(default_factory=list)


class ContextStateRef(Model):
    """One verbatim ``player_state`` observation, addressed by row ordinal."""

    dataset: str = "player_state"
    row_ordinal: int
    tick: int
    player_id: str | None = None
    health: int | None = None
    alive: bool = False
    side: str | None = None
    is_crouched: bool | None = None
    is_scoped: bool | None = None
    active_weapon: str | None = None
    evidence: EvidenceRef | None = None


class ContextRelation(Model):
    """The subject's relationship to one other player at one exact tick."""

    subject_id: str
    player_id: str
    relation: RelationKind
    subject_side: str | None = None
    other_side: str | None = None
    active: bool = False
    inactive_reason: str | None = None
    distance_2d: float | None = None
    distance_3d: float | None = None
    bearing_degrees: float | None = None
    relative_yaw: float | None = None
    view_origin: ViewOrigin
    other_view_origin: ViewOrigin
    static_sightline: SegmentResult | None = None
    static_effective_status: SegmentStatus | None = None
    """Sightline status after downgrading mismatched/unprovable results."""
    navigation: NavigationResult | None = None
    other_state: ContextStateRef | None = None
    evidence: EvidenceRef | None = None
    limitations: list[str] = Field(default_factory=list)


class ContextCounts(Model):
    """Observations at the exact tick, with unknowns kept separate.

    ``opponent_static_*`` count *active opponent* sightlines only; a dead or
    unclassified player is never counted as a clear or blocked opponent. Every
    ``static_clear``/``static_blocked`` here is scoped to the installed map build
    (:data:`STATIC_SCOPE`): it is a static-geometry reading, not confirmed
    visibility or exposure for the recording.
    """

    state_rows: int = 0
    identity_identified: int = 0
    identity_null: int = 0
    identity_null_alive: int = 0
    living: int = 0
    dead: int = 0
    unknown_health: int = 0
    active_relations: int = 0
    inactive_relations: int = 0
    same_side: int = 0
    """Tick-side membership over every *identified* other player, alive or not."""
    opposite_side: int = 0
    unknown_side: int = 0
    opponent_static_clear: int = 0
    opponent_static_blocked: int = 0
    opponent_static_unknown: int = 0
    sightlines_evaluated: int = 0
    sightlines_unavailable: int = 0
    cross_pairs_evaluated: int = 0
    """Living teammate→opponent pair sightlines evaluated at this tick."""


class CrossSightline(Model):
    """One potential living teammate→opponent sightline at one exact tick.

    Both endpoints are living recorded players, and the segment runs between
    stance-based (or recorded) eye positions. The result is static geometry scoped
    to the installed map build: it is never a statement about who could see,
    trade, or react to whom.
    """

    teammate_id: str
    opponent_id: str
    teammate_origin: ViewOrigin
    opponent_origin: ViewOrigin
    distance_2d: float | None = None
    distance_3d: float | None = None
    bearing_degrees: float | None = None
    relative_yaw: float | None = None
    """The teammate's recorded view yaw relative to the bearing towards the opponent."""
    static_sightline: SegmentResult | None = None
    static_effective_status: SegmentStatus | None = None
    navigation: NavigationResult | None = None
    scope: str = STATIC_SCOPE
    limitations: list[str] = Field(default_factory=list)


class OpponentDirection(Model):
    """Direction from the subject to one living opponent at the exact tick."""

    player_id: str
    bearing_degrees: float | None = None
    relative_yaw: float | None = None
    """Signed angle from the subject's recorded view yaw to the opponent; 0 = ahead."""


class AngularSpread(Model):
    """Angular geometry of the directions the subject faces at one tick.

    Pure geometry over recorded yaw and positions: no risk, threat or awareness
    interpretation is derived from it.
    """

    opponent_count: int = 0
    span_degrees: float | None = None
    """Smallest arc containing every opponent direction; ``None`` below two opponents."""
    max_pair_separation_degrees: float | None = None
    """Largest pairwise angular separation between opponent directions."""
    subject_yaw: float | None = None
    subject_yaw_recorded: bool = False
    limitations: list[str] = Field(default_factory=list)


class TrajectorySample(Model):
    """One verbatim recorded position sample of a tracked player."""

    tick: int
    x: float | None = None
    y: float | None = None
    z: float | None = None
    yaw: float | None = None
    health: int | None = None


class ParticipantTrack(Model):
    """A bounded, evenly strided sample track for one participant.

    Samples are verbatim ``player_state`` rows; missing grid ticks are reported as
    ``missing_samples`` and never filled.
    """

    player_id: str
    relation: RelationKind = "unknown"
    side: str | None = None
    is_subject: bool = False
    stride_ticks: int = 1
    from_tick: int | None = None
    to_tick: int | None = None
    samples: list[TrajectorySample] = Field(default_factory=list)
    missing_samples: int = 0
    limitations: list[str] = Field(default_factory=list)


class FacingDelta(Model):
    """Change in the subject's recorded view yaw between two living samples."""

    from_tick: int
    to_tick: int
    yaw_from: float
    yaw_to: float
    delta_degrees: float
    stride_ticks: int
    limitations: list[str] = Field(default_factory=list)


class ContextPositionChange(Model):
    """Observed movement of one player over a bounded exact-tick window.

    ``dx``/``dy``/``dz``/``displacement_*``/``path_length_2d`` are reported only when
    the living, position-carrying samples form one *contiguous* run on the sampling
    grid inside a single round (``contiguous_living``). A death, a respawn, a missing
    sample or a round boundary breaks the run and the derived metrics stay ``None``
    instead of bridging across it; ``missing_samples``/``dead_samples`` keep the
    counts and ``limitations`` names the break.
    """

    player_id: str
    from_tick: int
    to_tick: int
    stride_ticks: int
    samples: int = 0
    """Grid ticks with a recorded position, alive or not."""
    living_samples: int = 0
    dead_samples: int = 0
    """Observed samples with ``health == 0`` or a null health."""
    missing_samples: int = 0
    contiguous_living: bool = False
    dx: float | None = None
    dy: float | None = None
    dz: float | None = None
    displacement_2d: float | None = None
    displacement_3d: float | None = None
    path_length_2d: float | None = None
    bounded: bool = True
    limitations: list[str] = Field(default_factory=list)


class LifecycleFact(Model):
    """One recorded connect/disconnect/spawn/team-change row (slice B ``player_lifecycle``).

    Only rows whose ``player_id`` is resolved to an account are attributable to a
    player: the source records a SteamID64 for disconnects only, so a row with a
    null ``player_id`` is counted and never guessed onto a subject by slot.
    """

    tick: int
    kind: str
    player_id: str | None = None
    user_slot: str | None = None
    team: str | None = None
    previous_team: str | None = None
    is_bot: bool | None = None
    reason_code: int | None = None
    ever_fully_connected: bool | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)


class ContextUtilityFact(Model):
    """One recorded utility fact (slice B table row), never inferred.

    ``semantics_reliable`` is ``False`` when the source cannot promise what the
    row means (throw versus detonation versus expiry, unknown endpoint), in which
    case the interval end is left unresolved. ``evidence`` points at the exact
    source row (``dataset`` = the utility table, its ``row_ordinal``, ``tick`` =
    ``start_tick``, and the round containing that tick), and ``evidence_kind``
    states whether the row is recorded engine state or an upstream reconstruction.
    """

    kind: str
    owner_id: str | None = None
    start_tick: int
    end_tick: int | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None
    site: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    semantics_reliable: bool = False
    evidence_kind: EvidenceKind = "recorded"
    evidence: EvidenceRef | None = None
    limitations: list[str] = Field(default_factory=list)


class ContextSnapshot(Model):
    """Exact-tick state of the subject, its relations and recorded utility."""

    demo_id: str
    generation_id: str
    profile_key: str
    subject_id: str
    tick: int
    round_id: int | None = None
    tick_rate_hz: float
    actual_tick: int | None = None
    exact: bool = False
    gap_ticks: int | None = None
    subject: ContextStateRef | None = None
    subject_alive: bool = False
    relations: list[ContextRelation] = Field(default_factory=list)
    inactive_relations: list[ContextRelation] = Field(default_factory=list)
    participants: list[ContextStateRef] = Field(default_factory=list)
    """Every identified player observed at this tick, so relations and pairs trace to rows."""
    pair_relations: list[CrossSightline] = Field(default_factory=list)
    """Living teammate→opponent potential sightlines, nearest first (bounded)."""
    opponent_directions: list[OpponentDirection] = Field(default_factory=list)
    angular_spread: AngularSpread = Field(default_factory=AngularSpread)
    counts: ContextCounts = Field(default_factory=ContextCounts)
    position_change: ContextPositionChange | None = None
    utility: list[ContextUtilityFact] = Field(default_factory=list)
    lifecycle_before: LifecycleFact | None = None
    """Last recorded lifecycle row of the subject at or before this tick, when the table exists."""
    lifecycle_after: LifecycleFact | None = None
    """First recorded lifecycle row of the subject after this tick."""
    lifecycle_unattributed_rows: int = 0
    """Lifecycle rows in the table with no resolved account id; never assigned to the subject."""
    static_scope: str = STATIC_SCOPE
    capabilities: ContextCapabilities
    provenance: ReconstructionProvenance
    limitations: list[str] = Field(default_factory=list)


class ContextAnchorSnapshot(Model):
    """A snapshot taken at one encounter anchor or pre/post-contact offset."""

    name: str
    kind: AnchorKind = "computed"
    """How this snapshot is backed: ``recorded`` when the anchor carries evidence rows."""
    anchor_kind: str | None = None
    """The encounter anchor's own kind (slice D) verbatim; ``None`` for offsets taken here."""
    reason: str
    requested_tick: int | None = None
    offset_seconds: float | None = None
    snapshot: ContextSnapshot


class ExposureSampling(Model):
    """Bounds and the actual grid of the exposure scan.

    ``ticks`` is the exact sampled grid, which always includes ``end_tick``, so a
    result can never claim more coverage than was read.
    """

    start_tick: int
    end_tick: int
    stride_ticks: int
    samples: int = 0
    ticks: list[int] = Field(default_factory=list)
    subject_alive_samples: int = 0
    tick_rate_hz: float


class OpponentExposure(Model):
    """Per-opponent sightline scan inside the encounter window."""

    player_id: str
    relation: RelationKind = "opponent"
    first_alive_tick: int | None = None
    earliest_clear_tick: int | None = None
    checked_ticks: int = 0
    clear_ticks: int = 0
    blocked_ticks: int = 0
    unknown_ticks: int = 0
    mismatched_ticks: int = 0
    missing_ticks: int = 0
    limitations: list[str] = Field(default_factory=list)


class EncounterExposure(Model):
    """Qualified earliest exposure for the encounter, or why it is unknown.

    ``qualified`` requires both a known static sightline and both endpoints
    observed alive at that exact tick; the scan bounds and every unknown dynamic
    are reported next to the result.
    """

    status: ExposureStatus
    earliest_exposure_tick: int | None = None
    earliest_exposure_player_id: str | None = None
    opponents: list[OpponentExposure] = Field(default_factory=list)
    sampling: ExposureSampling
    unknown_dynamics: list[str] = Field(default_factory=list)
    mismatches: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class EncounterContext(Model):
    """Snapshots at the encounter's anchors plus the exposure/utility timeline."""

    demo_id: str
    generation_id: str
    profile_key: str
    encounter_id: str
    round_id: int
    subject_id: str
    start_tick: int
    """First tick actually snapshotted and scanned (the encounter's source window)."""
    end_tick: int
    interaction_start_tick: int | None = None
    """First subject-involved event tick (slice D summary bounds)."""
    interaction_end_tick: int | None = None
    first_interaction_tick: int | None = None
    snapshots: list[ContextAnchorSnapshot] = Field(default_factory=list)
    subject_track: ParticipantTrack | None = None
    participant_tracks: list[ParticipantTrack] = Field(default_factory=list)
    """Bounded verbatim sample tracks of the encounter's participants (subject excluded)."""
    subject_facing_delta: FacingDelta | None = None
    """Recorded view-yaw change of the living subject across the window, when trustworthy."""
    exposure: EncounterExposure
    utility: list[ContextUtilityFact] = Field(default_factory=list)
    lifecycle: list[LifecycleFact] = Field(default_factory=list)
    """Recorded lifecycle rows of the subject inside the window; explains missing state."""
    lifecycle_unattributed_rows: int = 0
    capabilities: ContextCapabilities
    provenance: ReconstructionProvenance
    limitations: list[str] = Field(default_factory=list)


class CapabilitySummary(Model):
    """Small roll-up used by callers that only need the statuses."""

    state: CapabilityStatus
    geometry: CapabilityStatus
    sightlines: CapabilityStatus
    navigation: CapabilityStatus
    utility: CapabilityStatus
    exposure: CapabilityStatus
    view_origin: CapabilityStatus

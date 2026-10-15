"""Encounter domain models: subject-centric interaction episodes.

An *encounter* is a bounded, deterministic episode of recorded interaction that
involves one subject player. Episodes are grouped from the subject's own
recorded event rows (shots, damage dealt/received, kills, assists) inside one
round; nothing is interpolated, extrapolated or synthesized, and every claim is
traceable to exact ``(dataset, row_ordinal)`` rows through
:class:`~cs_demo_analyzer.domain.contracts.EvidenceRef`.

Two levels of aggregation exist:

``EncounterSummary``
    List view. Contains only what the subject's own event rows determine:
    window bounds, anchors, the other players directly involved, counts and
    limitations. It never requires reading ``player_state``, so a list query
    stays bounded per round.
``EncounterDetail``
    Detail view. ``summary`` plus the window's contextual events, per-player
    relations (resolved from recorded per-tick sides), the verbatim subject
    trajectory and provenance. The detail-level participant set may be wider
    than ``summary.participant_ids`` because it adds players whom the subject
    never interacted with directly but who acted inside the same window.

The subject is addressed as a canonical ``player_id`` (``steam:<SteamID64>``);
``participant_ids`` never contains the subject itself.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .contracts import AnalyticState, EvidenceRef, Model
from .evidence import EvidenceKind, ReconstructionProvenance

#: Version prefix of :data:`EncounterSummary.encounter_id`; bump on shape/semantics change.
#: ``v2`` folds the grouping options into the id (see ``analytics.encounters``).
ENCOUNTER_ID_VERSION = "v2"

#: Canonical encounter id: ``enc-v2-r<round_id>-<16 hex>`` (see ``analytics.encounters``).
ENCOUNTER_ID_PREFIX = f"enc-{ENCOUNTER_ID_VERSION}"

#: Grouping method reported in provenance.
ENCOUNTER_METHOD = "subject-event-grouping"
ENCOUNTER_METHOD_VERSION = "1"

DEFAULT_LIMIT = 100
MIN_LIMIT = 1
MAX_LIMIT = 500
DEFAULT_GAP_SECONDS = 3.0
DEFAULT_PRE_SECONDS = 3.0
DEFAULT_POST_SECONDS = 1.0
MAX_GAP_SECONDS = 60.0
MAX_PRE_SECONDS = 60.0
MAX_POST_SECONDS = 60.0

#: Hard bound on the subject trajectory returned by one detail read.
MAX_TRAJECTORY_ROWS = 4096

#: Event datasets an encounter is built from, in canonical tie-break order.
EVENT_DATASETS: tuple[str, ...] = ("kills", "damages", "shots", "bomb")

AnchorKind = Literal[
    "first_interaction",
    "first_shot",
    "first_damage",
    "last_interaction",
    "kill",
    "death",
    "assist",
    "pre_contact",
    "post_contact",
    "resolution",
]
#: ``observed`` anchors are backed by recorded rows; ``unavailable`` ones record
#: that the anchor could not be observed in this episode (never fabricated).
AnchorStatus = Literal["observed", "unavailable"]
#: How the episode's seed set was segmented. This describes the segmentation
#: bound, not the cause of a participant's absence: ``event_gap`` only means no
#: further subject event was recorded inside the configured grouping gap.
ResolutionKind = Literal["subject_death", "event_gap", "round_end"]

#: Prose meaning of each rule, for API docs and UI copy. ``event_gap`` is a
#: segmentation bound, NOT proof that a participant was inactive -- recorded
#: lifecycle evidence (disconnect, death) belongs to the context layer.
RESOLUTION_DESCRIPTIONS: dict[str, str] = {
    "subject_death": "the episode contains the subject's recorded death",
    "event_gap": (
        "no further subject event in the configured grouping gap, not proof any participant was inactive"
    ),
    "round_end": "the interaction window reached the end of the round",
}
ParticipantRelation = Literal["teammate", "opponent", "unknown"]
SubjectRole = Literal["actor", "target", "assister"]
EventDataset = Literal["kills", "damages", "shots", "bomb"]

#: Anchor kinds whose tick is an exact recorded event row.
EVIDENCE_ANCHOR_KINDS: tuple[str, ...] = (
    "first_interaction",
    "first_shot",
    "first_damage",
    "last_interaction",
    "kill",
    "death",
    "assist",
)

#: Stable limitation strings; consumers may match on these exact values.
LIMITATION_GROUPING_HEURISTIC = "grouping is heuristic: interactions closer than gap_seconds form one encounter, and a larger gap splits them"
LIMITATION_WINDOW_CLIPPED_START = "window clipped at the round start boundary"
LIMITATION_WINDOW_CLIPPED_END = "window clipped at the round end boundary"
LIMITATION_TRAJECTORY_DOWNSAMPLED = "subject trajectory is downsampled to stay within the trajectory row bound"
LIMITATION_UNRESOLVED_EVENT_IDENTITY = "event rows with an unresolved player identity are kept as evidence but never joined to a participant"
LIMITATION_FIRST_SHOT_UNAVAILABLE = "no shot by the subject was recorded in this episode"
LIMITATION_FIRST_DAMAGE_UNAVAILABLE = "no damage dealt or received by the subject was recorded in this episode"
LIMITATION_NO_INTERPERSONAL_EVIDENCE = "episode has no recorded interaction with another player (subject events only)"


class EncounterGrouping(Model):
    """Resolved grouping configuration; ticks are derived from ``tick_rate_hz``."""

    gap_seconds: float
    pre_seconds: float
    post_seconds: float
    tick_rate_hz: float
    gap_ticks: int
    pre_ticks: int
    post_ticks: int


class EncounterAnchor(Model):
    """One anchor inside an encounter.

    ``observed`` anchors whose kind is in :data:`EVIDENCE_ANCHOR_KINDS`
    (``first_interaction``, ``first_shot``, ``first_damage``,
    ``last_interaction``, ``kill``, ``death``, ``assist``) carry exactly one
    :class:`EvidenceRef` and name the source row, so ``tick`` is the exact
    recorded tick. ``pre_contact``/``post_contact`` and ``resolution`` are
    derived from the grouping configuration and the seed set; they carry
    ``evidence_kind="computed"`` (``resolution`` keeps the recorded death row as
    evidence for the ``subject_death`` rule, in which case its
    ``evidence_kind`` stays ``"recorded"``).

    An anchor that cannot be observed in this episode (for example no shot was
    recorded) is still returned, with ``status="unavailable"``, ``tick=None``,
    ``evidence_kind="unsupported"`` and no evidence, instead of being omitted or
    given a fabricated tick. ``resolution`` is only set on the ``resolution``
    anchor and states the segmentation rule that ended it.
    """

    anchor_id: str
    kind: AnchorKind
    #: ``None`` only when ``status == "unavailable"``.
    tick: int | None
    status: AnchorStatus = "observed"
    #: ``recorded`` when ``tick`` is an exact recorded row, ``computed`` when it
    #: is derived, ``unsupported`` when the anchor is unavailable here.
    evidence_kind: EvidenceKind = "recorded"
    player_ids: list[str] = Field(default_factory=list)
    dataset: str | None = None
    row_ordinal: int | None = None
    #: Free text for event anchors; the segmentation rule name for ``resolution``.
    detail: str | None = None
    #: Segmentation rule; set only when ``kind == "resolution"`` (never a claim
    #: about why a participant was absent).
    resolution: ResolutionKind | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)


class EncounterEvent(Model):
    """One verbatim event row inside an encounter window."""

    dataset: EventDataset
    row_ordinal: int
    tick: int
    round_id: int
    actor_id: str | None = None
    target_id: str | None = None
    assister_id: str | None = None
    weapon: str | None = None
    headshot: bool | None = None
    damage_health: int | None = None
    damage_armor: int | None = None
    detail: str | None = None
    #: The subject's role in this row, ``None`` when the subject is not in it.
    subject_role: SubjectRole | None = None
    #: ``True`` only for this episode's seed rows (the subject's own event rows
    #: inside its grouping). A window that overlaps an adjacent episode brings that
    #: episode's subject rows in as contextual evidence instead, so this flag never
    #: inflates ``subject_event_count`` with another episode's interactions.
    subject_involved: bool = False
    #: ``True`` when the row is in the window and touches the subject or a
    #: participant without being a seed of this episode (an adjacent episode's
    #: subject row, or a teammate/opponent action).
    contextual: bool = False
    evidence: EvidenceRef


class EncounterParticipant(Model):
    """A player involved in an encounter, with the relation recorded at contact."""

    player_id: str
    relation: ParticipantRelation
    side: str | None = None
    subject_side: str | None = None
    #: Roles the player holds in this encounter's event rows (sorted).
    roles: list[str] = Field(default_factory=list)
    first_seen_tick: int
    last_seen_tick: int
    event_count: int
    #: ``True`` when the subject interacted with this player directly.
    direct: bool


class EncounterSummary(Model):
    """List-level encounter record: derivable without reading ``player_state``."""

    encounter_id: str
    demo_id: str
    generation_id: str
    profile_key: str
    round_id: int
    subject_id: str
    #: Interaction bounds: first and last subject-involved event row of the episode.
    start_tick: int
    end_tick: int
    first_interaction_tick: int
    last_interaction_tick: int
    #: Other players the subject interacted with directly (sorted, subject excluded).
    participant_ids: list[str] = Field(default_factory=list)
    anchors: list[EncounterAnchor] = Field(default_factory=list)
    #: Number of subject-involved event rows (detail adds contextual rows).
    event_count: int
    kill_count: int
    death_count: int
    assist_count: int
    subject_died: bool
    grouping: EncounterGrouping
    limitations: list[str] = Field(default_factory=list)


class EncounterSourceWindow(Model):
    """Bounds of the read window, with explicit clipping against the round."""

    round_id: int
    round_start_tick: int
    round_end_tick: int
    window_start_tick: int
    window_end_tick: int
    truncated_start: bool
    truncated_end: bool


class EncounterDetail(Model):
    """Detail view: ``summary`` plus window context, participants and trajectory.

    ``summary`` is byte-identical to the same encounter in
    :class:`EncounterList` for the same grouping options.
    """

    summary: EncounterSummary
    source_window: EncounterSourceWindow
    grouping: EncounterGrouping
    #: Subject-involved rows first, then contextual rows; chronological order.
    events: list[EncounterEvent] = Field(default_factory=list)
    participants: list[EncounterParticipant] = Field(default_factory=list)
    subject_event_count: int
    contextual_event_count: int
    #: Verbatim ``player_state`` rows of the subject in the window, on ``trajectory_stride``.
    subject_trajectory: list[AnalyticState] = Field(default_factory=list)
    trajectory_stride: int
    #: Grid ticks inside the window with no recorded subject row (never filled).
    trajectory_missing_ranges: list[list[int]] = Field(default_factory=list)
    provenance: ReconstructionProvenance
    limitations: list[str] = Field(default_factory=list)


class EncounterList(Model):
    """One page of encounters for a generation and subject."""

    demo_id: str
    generation_id: str
    profile_key: str
    subject_id: str
    grouping: EncounterGrouping
    round_id: int | None = None
    #: Encounters matching the filter, before ``offset``/``limit``.
    total: int
    offset: int
    limit: int
    encounters: list[EncounterSummary] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

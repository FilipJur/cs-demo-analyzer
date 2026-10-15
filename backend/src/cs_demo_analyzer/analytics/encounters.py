"""Deterministic, bounded, subject-centric encounter episodes.

What an encounter is
--------------------
An encounter is one episode of recorded interaction involving a subject player
inside a single round. Seeds are the subject's *own* event rows only:

* ``kills`` where the subject is attacker, victim or assister,
* ``damages`` where the subject is attacker or victim,
* ``shots`` fired by the subject.

Seeds are ordered by ``(tick, dataset, row_ordinal)`` and split when the gap to
the previous seed exceeds ``gap_seconds`` (rounded to ticks) or when the episode
already contains the subject's death. Every seed row is preserved, including
several rows on the same tick, so a multi-kill or a simultaneous
damage/kill/assist never collapses.

Anchors
-------
Each episode reports distinct anchors: ``pre_contact`` (window marker),
``first_interaction`` (earliest subject event row), ``first_shot``,
``first_damage``, every ``kill``/``death``/``assist``, ``last_interaction``
(latest subject event row), ``post_contact`` (window marker) and ``resolution``.
``first_interaction`` may itself be a shot, a damage or an assist, which is why
``first_shot``/``first_damage`` exist separately. An anchor that this episode
cannot exhibit (no shot recorded, no damage recorded) is returned with
``status="unavailable"`` and ``tick=None`` rather than fabricated, and the
matching limitation string is added.

``resolution`` says how the seed set was segmented (not the cause of anyone's
absence), with the ``resolution`` field set to the rule name:

* ``subject_death`` -- the episode contains the subject's death; the anchor's
  tick is the recorded death tick and carries that row as evidence (so its
  ``evidence_kind`` stays ``recorded``);
* ``event_gap`` -- no further subject event within ``gap_ticks``; the tick
  is the last interaction tick (``computed``). This is a segmentation bound over
  the subject's own event rows: it is *not* proof that any participant became
  inactive, and recorded lifecycle evidence belongs to the context layer;
* ``round_end`` -- the window ran out of round; the tick is the round end
  (``computed``).

Everything is verbatim data
---------------------------
Nothing is interpolated or synthesized. Windows are ``[first_seed - pre_seconds,
last_seed + post_seconds]`` clipped to the round's ``[freeze_end_tick or
start_tick, end_tick]``. Events keep their exact ``(dataset, row_ordinal)``
identity and each one carries an :class:`EvidenceRef`; the subject trajectory is
a verbatim slice of ``player_state`` on an explicit stride (no interpolation).
Uncertainty is reported as stable limitation strings instead of guesses.

Bounds
------
Reusing the temporal layer's primitives (``temporal._read_span`` for bounded
chunked reads and ``temporal._round_begin`` for the round's usable start) keeps
one definition of "how a table is read boundedly" in the package.

* The subject's own event rows are read over the selected rounds' own spans (each
  round's ``start_tick`` to its ``end_tick``) with an explicit subject predicate,
  so a ``round_id``-filtered list never reads the rest of the match, and only a
  few hundred to a few thousand rows ever materialize (``_read_span`` splits the
  span and ``pool.read`` enforces the materialization cap).
* ``player_state`` is never read whole-match. The detail view reads exactly one
  bounded window for the subject trajectory and one for the participants' sides.
* Contextual events of a detail view are read only inside that encounter's
  window, and only rows touching the subject or a participant are kept; one hop
  of participant expansion is applied, so a fight's teammates and opponents stay
  contextual without dragging in the rest of the round.

Provenance and reproducibility
------------------------------
``encounter_id`` is content-addressed from the generation, subject, round,
interaction bounds, the grouping options and the exact seed ordinals, so the same
data always yields the same id, a different generation never collides, and the
same seeds read with a different ``pre``/``post`` window do not reuse an id
produced under another shape. ``EncounterList.grouping`` echoes the options that
produced the id. The detail view recomputes only the round named by the id, so
lookups stay bounded.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import polars as pl

from ..domain.contracts import AnalyticState, AppError, EvidenceRef
from ..domain.encounters import (
    DEFAULT_GAP_SECONDS,
    DEFAULT_LIMIT,
    DEFAULT_POST_SECONDS,
    DEFAULT_PRE_SECONDS,
    ENCOUNTER_ID_PREFIX,
    ENCOUNTER_METHOD,
    ENCOUNTER_METHOD_VERSION,
    EVENT_DATASETS,
    LIMITATION_FIRST_DAMAGE_UNAVAILABLE,
    LIMITATION_FIRST_SHOT_UNAVAILABLE,
    LIMITATION_GROUPING_HEURISTIC,
    LIMITATION_NO_INTERPERSONAL_EVIDENCE,
    LIMITATION_TRAJECTORY_DOWNSAMPLED,
    LIMITATION_UNRESOLVED_EVENT_IDENTITY,
    LIMITATION_WINDOW_CLIPPED_END,
    LIMITATION_WINDOW_CLIPPED_START,
    MAX_GAP_SECONDS,
    MAX_LIMIT,
    MAX_POST_SECONDS,
    MAX_PRE_SECONDS,
    MAX_TRAJECTORY_ROWS,
    MIN_LIMIT,
    AnchorKind,
    EncounterAnchor,
    EncounterDetail,
    EncounterEvent,
    EncounterGrouping,
    EncounterList,
    EncounterParticipant,
    EncounterSourceWindow,
    EncounterSummary,
    EventDataset,
    ResolutionKind,
)
from ..domain.evidence import ReconstructionProvenance
from ..domain.subjects import canonical_player_id
from .temporal import _read_span, _round_begin, evidence_ref

STAGE = "analytics"

#: Columns read per dataset; a superset of what the predicates need.
_EVENT_COLUMNS: dict[str, list[str]] = {
    "kills": ["row_ordinal", "tick", "attacker_id", "victim_id", "assister_id", "weapon", "headshot"],
    "damages": ["row_ordinal", "tick", "attacker_id", "victim_id", "damage_health", "damage_armor", "weapon"],
    "shots": ["row_ordinal", "tick", "player_id", "weapon"],
    "bomb": ["row_ordinal", "tick", "player_id", "action", "bombsite"],
}

_DATASET_ORDER: dict[str, int] = {name: index for index, name in enumerate(EVENT_DATASETS)}

_STATE_COLUMNS = ["tick", "row_ordinal", "player_id", "side"]


# --------------------------------------------------------------------------- #
# input resolution
# --------------------------------------------------------------------------- #
def _normalize_subject(subject_id: str) -> str:
    """``steam:<SteamID64>`` or a bare SteamID64 into the canonical player key.

    Validation is delegated to :func:`domain.subjects.canonical_player_id`, so the
    encounters slice shares the subject slice's single definition of a canonical
    player id (exact 17-digit individual SteamID64) instead of inventing a second
    convention.
    """
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise AppError("INVALID_ARGUMENT", "subject_id must be a non-empty string", STAGE)
    text = subject_id.strip()
    digits = text.split(":", 1)[1] if text.startswith("steam:") else text
    try:
        return canonical_player_id(digits)
    except ValueError as exc:
        raise AppError("INVALID_ARGUMENT", f"subject_id {subject_id!r} is not a SteamID64: {exc}", STAGE) from None


def _seconds(value: float, name: str, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise AppError("INVALID_ARGUMENT", f"{name} must be a finite number", STAGE)
    if value < 0 or value > maximum:
        raise AppError("INVALID_ARGUMENT", f"{name} must be in 0..{maximum} seconds", STAGE)
    return float(value)


def _ticks(seconds: float, rate: float) -> int:
    return max(0, int(math.floor(seconds * rate + 0.5)))


def _grouping(
    gen: Any, gap_seconds: float, pre_seconds: float, post_seconds: float
) -> EncounterGrouping:
    gap = _seconds(gap_seconds, "gap_seconds", MAX_GAP_SECONDS)
    pre = _seconds(pre_seconds, "pre_seconds", MAX_PRE_SECONDS)
    post = _seconds(post_seconds, "post_seconds", MAX_POST_SECONDS)
    rate = float(gen.tick_rate_hz)
    if not math.isfinite(rate) or rate <= 0:
        raise AppError("INVALID_ARGUMENT", f"generation tick rate {rate} is not usable", STAGE)
    return EncounterGrouping(
        gap_seconds=gap,
        pre_seconds=pre,
        post_seconds=post,
        tick_rate_hz=rate,
        gap_ticks=_ticks(gap, rate),
        pre_ticks=_ticks(pre, rate),
        post_ticks=_ticks(post, rate),
    )


@dataclass(frozen=True)
class _Round:
    """One round with usable timing.

    ``begin`` is the round's usable start (``freeze_end_tick`` or ``start_tick``);
    ``raw_start`` is the round row's ``start_tick`` when present, so the rows
    inside the round's own span but before ``begin`` (warmup/freeze time) can be
    read and reported as explicitly excluded instead of silently dropped.
    """

    round_id: int
    begin: int
    end: int
    raw_start: int


def _complete_rounds(gen: Any) -> tuple[list[_Round], int]:
    """Rounds with usable timing, ordered by start; plus the count of unusable ones."""
    rounds = getattr(gen, "rounds", None)
    if rounds is None or rounds.height == 0:
        return [], 0
    usable: list[_Round] = []
    incomplete = 0
    for row in rounds.iter_rows(named=True):
        begin = _round_begin(row)
        end = row.get("end_tick")
        if begin is None or end is None or int(end) < int(begin):
            incomplete += 1
            continue
        start = row.get("start_tick")
        raw_start = int(begin) if start is None else min(int(start), int(begin))
        usable.append(_Round(int(row["round_id"]), int(begin), int(end), raw_start))
    usable.sort(key=lambda item: (item.begin, item.round_id))
    return usable, incomplete


def _round_extent(rounds: Sequence[_Round]) -> tuple[int, int]:
    """Read bounds of a round selection: from the earliest raw start to the last end."""
    return min(item.raw_start for item in rounds), max(item.end for item in rounds)


# --------------------------------------------------------------------------- #
# event rows
# --------------------------------------------------------------------------- #
def _subject_predicate(dataset: str, subject: str) -> pl.Expr | None:
    if dataset == "kills":
        return (
            (pl.col("attacker_id") == subject)
            | (pl.col("victim_id") == subject)
            | (pl.col("assister_id") == subject)
        )
    if dataset == "damages":
        return (pl.col("attacker_id") == subject) | (pl.col("victim_id") == subject)
    if dataset in ("shots", "bomb"):
        return pl.col("player_id") == subject
    return None


@dataclass(frozen=True)
class _Seed:
    dataset: str
    row_ordinal: int
    tick: int
    #: Owning round id, or ``None`` when the row matches no round's own span.
    round_id: int | None
    subject_role: str
    actor_id: str | None
    target_id: str | None
    assister_id: str | None
    weapon: str | None
    headshot: bool | None
    damage_health: int | None
    damage_armor: int | None
    detail: str | None
    players: tuple[str, ...]
    evidence: EvidenceRef


def _row_fields(dataset: str, row: dict[str, Any]) -> tuple[str | None, str | None, str | None, str | None]:
    """``(actor, target, assister, detail)`` for one event row."""
    if dataset == "kills":
        return row.get("attacker_id"), row.get("victim_id"), row.get("assister_id"), None
    if dataset == "damages":
        return row.get("attacker_id"), row.get("victim_id"), None, None
    if dataset == "shots":
        return row.get("player_id"), None, None, None
    return row.get("player_id"), None, None, row.get("action")


def _row_players(dataset: str, row: dict[str, Any]) -> tuple[str, ...]:
    actor, target, assister, _ = _row_fields(dataset, row)
    players: list[str] = []
    for value in (actor, target, assister):
        if value is not None and value not in players:
            players.append(value)
    return tuple(players)


def _subject_role(dataset: str, row: dict[str, Any], subject: str) -> str | None:
    actor, target, assister, _ = _row_fields(dataset, row)
    if actor == subject:
        return "actor"
    if target == subject:
        return "target"
    if dataset == "kills" and assister == subject:
        return "assister"
    return None


def _seed(gen: Any, dataset: str, row: dict[str, Any], subject: str, round_id: int | None) -> _Seed:
    actor, target, assister, detail = _row_fields(dataset, row)
    players = _row_players(dataset, row)
    tick = int(row["tick"])
    ordinal = int(row["row_ordinal"])
    return _Seed(
        dataset=dataset,
        row_ordinal=ordinal,
        tick=tick,
        round_id=round_id,
        subject_role=_subject_role(dataset, row, subject) or "actor",
        actor_id=actor,
        target_id=target,
        assister_id=assister,
        weapon=row.get("weapon"),
        headshot=row.get("headshot"),
        damage_health=row.get("damage_health"),
        damage_armor=row.get("damage_armor"),
        detail=detail,
        players=players,
        evidence=evidence_ref(gen, dataset, ordinal, tick, round_id, list(players)),
    )


def _read_subject_seeds(
    pool: Any, gen: Any, subject: str, lo: int, hi: int, rounds: Sequence[_Round]
) -> list[_Seed]:
    """The subject's own event rows with ``lo <= tick <= hi``, round-resolved.

    ``lo``/``hi`` come from the caller's round selection, so a round-filtered
    query never reads the rest of the match. A row that matches no round's own
    span keeps ``round_id=None`` in its evidence ref; it is never grouped.
    """
    seeds: list[_Seed] = []
    for dataset in EVENT_DATASETS:
        predicate = _subject_predicate(dataset, subject)
        frame = _read_span(pool, gen, dataset, lo, hi, columns=_EVENT_COLUMNS[dataset], predicate=predicate)
        if frame.height == 0:
            continue
        for row in frame.to_dicts():
            tick = int(row["tick"])
            match = next((item for item in rounds if item.raw_start <= tick <= item.end), None)
            seeds.append(_seed(gen, dataset, row, subject, match.round_id if match else None))
    seeds.sort(key=_seed_key)
    return seeds


def _classify_subject_seeds(
    seeds: Sequence[_Seed], rounds: Sequence[_Round]
) -> tuple[list[_Seed], int, int]:
    """Split subject rows into groupable seeds, freeze-time rows and outside rows.

    Groupable seeds lie in a round's usable window ``[begin, end]``. Rows inside a
    round's own span but before ``begin`` (warmup/freeze time) and rows matching no
    round are counted separately; both are reported as explicit limitations rather
    than being treated as interactions.
    """
    groupable: list[_Seed] = []
    freeze_time = 0
    outside = 0
    for seed in seeds:
        span = next((item for item in rounds if item.raw_start <= seed.tick <= item.end), None)
        if span is None:
            outside += 1
        elif seed.tick < span.begin:
            freeze_time += 1
        else:
            groupable.append(seed)
    groupable.sort(key=_seed_key)
    return groupable, freeze_time, outside


def _seed_key(seed: _Seed) -> tuple[int, int, int]:
    return (seed.tick, _DATASET_ORDER.get(seed.dataset, len(EVENT_DATASETS)), seed.row_ordinal)


def _clusters(seeds: Sequence[_Seed], gap_ticks: int) -> list[list[_Seed]]:
    """Split seeds on the configured gap or on a subject death inside the episode."""
    clusters: list[list[_Seed]] = []
    current: list[_Seed] = []
    death_tick: int | None = None
    for seed in seeds:
        if current:
            previous = current[-1]
            if seed.tick - previous.tick > gap_ticks:
                clusters.append(current)
                current, death_tick = [], None
            elif death_tick is not None and seed.tick > death_tick:
                clusters.append(current)
                current, death_tick = [], None
        current.append(seed)
        if seed.dataset == "kills" and seed.target_id is not None and seed.subject_role == "target":
            death_tick = seed.tick
    if current:
        clusters.append(current)
    return clusters


def _encounter_id(
    generation_id: str,
    subject: str,
    round_id: int,
    start_tick: int,
    end_tick: int,
    grouping: EncounterGrouping,
    seeds: Sequence[_Seed],
) -> str:
    """Content-addressed id; the grouping options are part of the identity.

    The same seed set read with different ``pre``/``post`` windows is a different
    episode shape, so it must not reuse an id produced under other options; the
    returned ``EncounterList.grouping`` therefore always reproduces the id.
    """
    digest = hashlib.sha256()
    digest.update(
        (
            f"{ENCOUNTER_METHOD_VERSION}\n{generation_id}\n{subject}\n{round_id}\n{start_tick}\n{end_tick}\n"
            f"gap={grouping.gap_seconds}\npre={grouping.pre_seconds}\npost={grouping.post_seconds}\n"
            f"rate={grouping.tick_rate_hz}\n"
        ).encode()
    )
    for seed in seeds:
        digest.update(f"{seed.dataset}:{seed.row_ordinal}@{seed.tick}\n".encode())
    return f"{ENCOUNTER_ID_PREFIX}-r{round_id}-{digest.hexdigest()[:16]}"


def _anchor_id(kind: str, tick: int, row_ordinal: int | None) -> str:
    return f"{kind}:{tick}" if row_ordinal is None else f"{kind}:{tick}:{row_ordinal}"


def _event_anchor(kind: AnchorKind, seed: _Seed, subject: str, other: str | None, detail: str) -> EncounterAnchor:
    players = [subject] + ([other] if other and other != subject else [])
    return EncounterAnchor(
        anchor_id=_anchor_id(kind, seed.tick, seed.row_ordinal),
        kind=kind,
        tick=seed.tick,
        status="observed",
        evidence_kind="recorded",
        player_ids=sorted(players),
        dataset=seed.dataset,
        row_ordinal=seed.row_ordinal,
        detail=detail,
        evidence=[seed.evidence],
    )


def _unavailable_anchor(kind: AnchorKind, subject: str, detail: str) -> EncounterAnchor:
    return EncounterAnchor(
        anchor_id=_anchor_id(kind, 0, None),
        kind=kind,
        tick=None,
        status="unavailable",
        evidence_kind="unsupported",
        player_ids=[subject],
        detail=detail,
    )


def _resolution(
    span: _Round, cluster: Sequence[_Seed], grouping: EncounterGrouping
) -> tuple[ResolutionKind, int, _Seed | None]:
    """How the episode's seed set was segmented, evaluated on the seeds and the round.

    Death outranks the gap, which outranks the round boundary: with no subject
    event within ``gap_ticks`` after the last interaction the episode is over
    before the round ends, and only a window that runs out of round does not.
    ``event_gap`` says nothing about *why* the subject stopped being recorded
    (inactivity, disconnect, warmup): it is a bound on the seeds, not a cause.
    """
    deaths = [seed for seed in cluster if seed.dataset == "kills" and seed.subject_role == "target"]
    if deaths:
        death = deaths[-1]
        return "subject_death", death.tick, death
    last = cluster[-1]
    if last.tick + grouping.gap_ticks >= span.end:
        return "round_end", span.end, None
    return "event_gap", last.tick, None


def _anchors(
    span: _Round,
    seeds: Sequence[_Seed],
    grouping: EncounterGrouping,
    subject: str,
) -> tuple[list[EncounterAnchor], int, int]:
    first = seeds[0]
    last = seeds[-1]
    anchors: list[EncounterAnchor] = []
    window_start = max(span.begin, first.tick - grouping.pre_ticks)
    window_end = min(span.end, last.tick + grouping.post_ticks)
    anchors.append(
        EncounterAnchor(
            anchor_id=_anchor_id("pre_contact", window_start, None),
            kind="pre_contact",
            tick=window_start,
            status="observed",
            evidence_kind="computed",
            player_ids=[subject],
            detail="grouping pre_seconds before the first interaction",
        )
    )
    anchors.append(_event_anchor("first_interaction", first, subject, None, f"{first.dataset} row"))

    shots = [seed for seed in seeds if seed.dataset == "shots"]
    if shots:
        anchors.append(_event_anchor("first_shot", shots[0], subject, None, "first recorded shot by the subject"))
    else:
        anchors.append(
            _unavailable_anchor("first_shot", subject, "no shot by the subject was recorded in this episode")
        )
    damages = [seed for seed in seeds if seed.dataset == "damages"]
    if damages:
        seed = damages[0]
        other = seed.target_id if seed.actor_id == subject else seed.actor_id
        anchors.append(_event_anchor("first_damage", seed, subject, other, "first recorded damage involving the subject"))
    else:
        anchors.append(
            _unavailable_anchor(
                "first_damage", subject, "no damage dealt or received by the subject was recorded in this episode"
            )
        )

    for seed in seeds:
        if seed.dataset != "kills":
            continue
        if seed.actor_id == subject:
            anchors.append(_event_anchor("kill", seed, subject, seed.target_id, _kill_detail(seed)))
        if seed.target_id == subject:
            anchors.append(_event_anchor("death", seed, subject, seed.actor_id, _kill_detail(seed)))
        if seed.assister_id == subject:
            anchors.append(_event_anchor("assist", seed, subject, seed.target_id, _kill_detail(seed)))

    anchors.append(_event_anchor("last_interaction", last, subject, None, f"{last.dataset} row"))

    rule, tick, backing = _resolution(span, seeds, grouping)
    anchors.append(
        EncounterAnchor(
            anchor_id=_anchor_id("resolution", tick, backing.row_ordinal if backing else None),
            kind="resolution",
            tick=tick,
            status="observed",
            evidence_kind="recorded" if backing is not None else "computed",
            player_ids=[subject],
            dataset=backing.dataset if backing else None,
            row_ordinal=backing.row_ordinal if backing else None,
            detail=rule,
            resolution=rule,
            evidence=[backing.evidence] if backing else [],
        )
    )
    anchors.append(
        EncounterAnchor(
            anchor_id=_anchor_id("post_contact", window_end, None),
            kind="post_contact",
            tick=window_end,
            status="observed",
            evidence_kind="computed",
            player_ids=[subject],
            detail="grouping post_seconds after the last interaction",
        )
    )
    anchors.sort(key=lambda anchor: (anchor.tick is None, anchor.tick or 0, _anchor_rank(anchor.kind), anchor.anchor_id))
    return anchors, window_start, window_end


def _anchor_rank(kind: str) -> int:
    order = (
        "pre_contact",
        "first_interaction",
        "first_shot",
        "first_damage",
        "kill",
        "death",
        "assist",
        "last_interaction",
        "post_contact",
        "resolution",
    )
    return order.index(kind) if kind in order else len(order)


def _kill_detail(seed: _Seed) -> str:
    parts = [part for part in (seed.weapon, "headshot" if seed.headshot else None) if part]
    return " ".join(parts) if parts else "kill"


def _build_encounters(
    gen: Any,
    span: _Round,
    seeds: Sequence[_Seed],
    grouping: EncounterGrouping,
    subject: str,
) -> list[tuple[EncounterSummary, list[_Seed]]]:
    built: list[tuple[EncounterSummary, list[_Seed]]] = []
    for cluster in _clusters(seeds, grouping.gap_ticks):
        built.append(_summarize(gen, span, cluster, grouping, subject))
    return built


def _summarize(
    gen: Any, span: _Round, cluster: Sequence[_Seed], grouping: EncounterGrouping, subject: str
) -> tuple[EncounterSummary, list[_Seed]]:
    first = cluster[0]
    last = cluster[-1]
    anchors, window_start, window_end = _anchors(span, cluster, grouping, subject)
    participants: set[str] = set()
    kill_count = death_count = assist_count = 0
    unresolved = 0
    has_shot = False
    has_damage = False
    for seed in cluster:
        if seed.dataset == "kills":
            if seed.actor_id == subject:
                kill_count += 1
            if seed.target_id == subject:
                death_count += 1
            if seed.assister_id == subject:
                assist_count += 1
        has_shot = has_shot or seed.dataset == "shots"
        has_damage = has_damage or seed.dataset == "damages"
        for player in seed.players:
            if player != subject:
                participants.add(player)
        if seed.dataset in ("kills", "damages") and (seed.actor_id is None or seed.target_id is None):
            unresolved += 1
    limitations: set[str] = set()
    if window_start > first.tick - grouping.pre_ticks:
        limitations.add(LIMITATION_WINDOW_CLIPPED_START)
    if window_end < last.tick + grouping.post_ticks:
        limitations.add(LIMITATION_WINDOW_CLIPPED_END)
    if unresolved:
        limitations.add(LIMITATION_UNRESOLVED_EVENT_IDENTITY)
    if not has_shot:
        limitations.add(LIMITATION_FIRST_SHOT_UNAVAILABLE)
    if not has_damage:
        limitations.add(LIMITATION_FIRST_DAMAGE_UNAVAILABLE)
    if not participants:
        limitations.add(LIMITATION_NO_INTERPERSONAL_EVIDENCE)
    summary = EncounterSummary(
        encounter_id=_encounter_id(
            gen.generation_id, subject, span.round_id, first.tick, last.tick, grouping, cluster
        ),
        demo_id=gen.demo_id,
        generation_id=gen.generation_id,
        profile_key=gen.profile_key,
        round_id=span.round_id,
        subject_id=subject,
        start_tick=first.tick,
        end_tick=last.tick,
        first_interaction_tick=first.tick,
        last_interaction_tick=last.tick,
        participant_ids=sorted(participants),
        anchors=anchors,
        event_count=len(cluster),
        kill_count=kill_count,
        death_count=death_count,
        assist_count=assist_count,
        subject_died=death_count > 0,
        grouping=grouping,
        limitations=sorted(limitations),
    )
    return summary, list(cluster)


# --------------------------------------------------------------------------- #
# detail assembly
# --------------------------------------------------------------------------- #
def _detail_events(
    pool: Any,
    gen: Any,
    span: _Round,
    window_start: int,
    window_end: int,
    subject: str,
    participant_ids: Sequence[str],
    seed_keys: set[tuple[str, int]],
) -> tuple[list[EncounterEvent], set[str]]:
    """Window events of one encounter.

    ``seed_keys`` are the ``(dataset, row_ordinal)`` identities of *this* episode's
    seeds. Rows are only marked ``subject_involved`` when they are one of those
    seeds: the window can reach into an adjacent episode's seeds (its pre/post
    window overlaps), and those rows must stay contextual evidence instead of
    being counted as this episode's interactions.
    """
    involved = set(participant_ids) | {subject}
    selected: list[tuple[EventDataset, dict[str, Any], bool, bool]] = []
    extra_players: set[str] = set()
    for dataset in EVENT_DATASETS:
        frame = _read_span(pool, gen, dataset, window_start, window_end, columns=_EVENT_COLUMNS[dataset])
        if frame.height == 0:
            continue
        for row in frame.to_dicts():
            players = _row_players(dataset, row)
            if not players:
                continue
            subject_involved = (dataset, int(row["row_ordinal"])) in seed_keys
            contextual = (not subject_involved) and bool(set(players) & involved)
            if not (subject_involved or contextual):
                continue
            selected.append((dataset, row, subject_involved, contextual))
            if contextual:
                extra_players.update(player for player in players if player != subject)
    selected.sort(key=lambda item: (int(item[1]["tick"]), _DATASET_ORDER[item[0]], int(item[1]["row_ordinal"])))
    events: list[EncounterEvent] = []
    for dataset, row, subject_involved, contextual in selected:
        actor, target, assister, detail = _row_fields(dataset, row)
        players = list(_row_players(dataset, row))
        events.append(
            EncounterEvent(
                dataset=dataset,  # type: ignore[arg-type]
                row_ordinal=int(row["row_ordinal"]),
                tick=int(row["tick"]),
                round_id=span.round_id,
                actor_id=actor,
                target_id=target,
                assister_id=assister,
                weapon=row.get("weapon"),
                headshot=row.get("headshot"),
                damage_health=row.get("damage_health"),
                damage_armor=row.get("damage_armor"),
                detail=detail,
                subject_role=_subject_role(dataset, row, subject),  # type: ignore[arg-type]
                subject_involved=subject_involved,
                contextual=contextual,
                evidence=evidence_ref(gen, dataset, int(row["row_ordinal"]), int(row["tick"]), span.round_id, players),
            )
        )
    return events, extra_players


def _participants(
    events: Sequence[EncounterEvent],
    direct_ids: Sequence[str],
    states: pl.DataFrame,
    subject: str,
    window_start: int,
) -> tuple[list[EncounterParticipant], list[str]]:
    """Per-player relations resolved from recorded per-tick sides (exact, else nearest)."""
    direct = set(direct_ids)
    roles: dict[str, set[str]] = {}
    first_seen: dict[str, int] = {}
    last_seen: dict[str, int] = {}
    counts: dict[str, int] = {}
    for event in events:
        role_players: list[tuple[str, str]] = []
        if event.actor_id:
            role_players.append((event.actor_id, "attacker"))
        if event.target_id:
            role_players.append((event.target_id, "victim"))
        if event.assister_id:
            role_players.append((event.assister_id, "assister"))
        if event.dataset == "shots" and event.actor_id:
            role_players[:] = [(event.actor_id, "shooter")]
        if event.dataset == "bomb" and event.actor_id:
            role_players[:] = [(event.actor_id, "bomb")]
        for player, role in role_players:
            if player == subject:
                continue
            roles.setdefault(player, set()).add(role)
            first_seen[player] = min(first_seen.get(player, event.tick), event.tick)
            last_seen[player] = max(last_seen.get(player, event.tick), event.tick)
            counts[player] = counts.get(player, 0) + 1

    sides: dict[str, list[tuple[int, str]]] = {}
    for row in states.iter_rows(named=True):
        player = row.get("player_id")
        side = row.get("side")
        if player is None or side is None:
            continue
        sides.setdefault(player, []).append((int(row["tick"]), str(side)))

    def side_at(player: str, tick: int) -> tuple[str | None, bool]:
        rows = sides.get(player)
        if not rows:
            return None, False
        exact = next((side for at, side in rows if at == tick), None)
        if exact is not None:
            return exact, True
        at, side = min(rows, key=lambda item: (abs(item[0] - tick), item[0]))
        return side, False

    approximated: list[str] = []
    built: list[EncounterParticipant] = []
    for player in sorted(set(roles) | set(direct)):
        subject_side, subject_exact = side_at(subject, first_seen.get(player, window_start))
        player_side, player_exact = side_at(player, first_seen.get(player, window_start))
        if not (subject_exact and player_exact):
            approximated.append(player)
        if subject_side is None or player_side is None:
            relation = "unknown"
        elif subject_side == player_side:
            relation = "teammate"
        else:
            relation = "opponent"
        built.append(
            EncounterParticipant(
                player_id=player,
                relation=relation,  # type: ignore[arg-type]
                side=player_side,
                subject_side=subject_side,
                roles=sorted(roles.get(player, set())),
                first_seen_tick=first_seen.get(player, window_start),
                last_seen_tick=last_seen.get(player, window_start),
                event_count=counts.get(player, 0),
                direct=player in direct,
            )
        )
    built.sort(key=lambda item: (not item.direct, item.player_id))
    return built, approximated


def _map_name(gen: Any) -> str:
    manifest = getattr(gen, "manifest", None)
    value = getattr(manifest, "map_name", None)
    return str(value) if value else "unknown"


def _provenance(gen: Any, limitations: Iterable[str]) -> ReconstructionProvenance:
    manifest = getattr(gen, "manifest", None)
    return ReconstructionProvenance(
        demo_id=gen.demo_id,
        generation_id=gen.generation_id,
        profile_key=gen.profile_key,
        method=ENCOUNTER_METHOD,
        method_version=ENCOUNTER_METHOD_VERSION,
        map_name=_map_name(gen),
        demo_client_version=getattr(manifest, "demo_client_version", None),
        map_asset_id=None,
        map_match_status="unknown",
        limitations=sorted(set(limitations)),
    )


# --------------------------------------------------------------------------- #
# service
# --------------------------------------------------------------------------- #
class EncounterService:
    """Subject-centric encounter episodes over one generation-pinned pool."""

    def __init__(self, pool: Any) -> None:
        self.pool = pool

    # -- list --------------------------------------------------------------
    def list(
        self,
        gen: Any,
        subject_id: str,
        *,
        round_id: int | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        gap_seconds: float = DEFAULT_GAP_SECONDS,
        pre_seconds: float = DEFAULT_PRE_SECONDS,
        post_seconds: float = DEFAULT_POST_SECONDS,
    ) -> EncounterList:
        subject = _normalize_subject(subject_id)
        grouping = _grouping(gen, gap_seconds, pre_seconds, post_seconds)
        if limit < MIN_LIMIT or limit > MAX_LIMIT:
            raise AppError("INVALID_ARGUMENT", f"limit must be in {MIN_LIMIT}..{MAX_LIMIT}", STAGE)
        if offset < 0:
            raise AppError("INVALID_ARGUMENT", "offset must be non-negative", STAGE)

        rounds, incomplete = _complete_rounds(gen)
        selected = rounds
        if round_id is not None:
            match = next((item for item in rounds if item.round_id == round_id), None)
            if match is None:
                raise AppError("NOT_FOUND", f"round {round_id} is not a complete round of {gen.generation_id}", STAGE)
            selected = [match]

        limitations: set[str] = {LIMITATION_GROUPING_HEURISTIC}
        if not rounds:
            limitations.add("generation has no round with usable timing")
            seeds, freeze_time, outside = [], 0, 0
        else:
            lo, hi = _round_extent(selected)
            seeds, freeze_time, outside = _classify_subject_seeds(
                _read_subject_seeds(self.pool, gen, subject, lo, hi, selected), selected
            )
        if round_id is not None:
            limitations.add(
                f"round filter applied: only subject event rows of round {round_id} were read and grouped"
            )
        if incomplete:
            limitations.add(
                f"{incomplete} round(s) have incomplete timing and were not grouped"
            )
        if freeze_time:
            limitations.add(
                f"{freeze_time} subject event row(s) inside warmup/freeze time "
                "(before a round's usable start) were not grouped"
            )
        if outside:
            limitations.add(
                f"{outside} subject event row(s) lie outside every complete round and were not grouped"
            )
        if not seeds:
            limitations.add(self._absence_limitation(gen, subject))

        summaries: list[EncounterSummary] = []
        for span in selected:
            in_span = [seed for seed in seeds if span.begin <= seed.tick <= span.end]
            if not in_span:
                continue
            for summary, _cluster in _build_encounters(gen, span, in_span, grouping, subject):
                summaries.append(summary)
        summaries.sort(key=lambda item: (item.round_id, item.start_tick, item.encounter_id))
        page = summaries[offset : offset + limit]
        return EncounterList(
            demo_id=gen.demo_id,
            generation_id=gen.generation_id,
            profile_key=gen.profile_key,
            subject_id=subject,
            grouping=grouping,
            round_id=round_id,
            total=len(summaries),
            offset=offset,
            limit=limit,
            encounters=page,
            limitations=sorted(limitations),
        )

    # -- detail ------------------------------------------------------------
    def detail(
        self,
        gen: Any,
        subject_id: str,
        encounter_id: str,
        *,
        gap_seconds: float = DEFAULT_GAP_SECONDS,
        pre_seconds: float = DEFAULT_PRE_SECONDS,
        post_seconds: float = DEFAULT_POST_SECONDS,
    ) -> EncounterDetail:
        subject = _normalize_subject(subject_id)
        grouping = _grouping(gen, gap_seconds, pre_seconds, post_seconds)
        round_id = _round_from_id(encounter_id)
        rounds, incomplete = _complete_rounds(gen)
        span = next((item for item in rounds if item.round_id == round_id), None)
        if span is None:
            raise AppError(
                "NOT_FOUND",
                f"encounter {encounter_id} names round {round_id}, which is not a complete round of {gen.generation_id}",
                STAGE,
            )
        seeds, _freeze, _outside = _classify_subject_seeds(
            _read_subject_seeds(self.pool, gen, subject, span.raw_start, span.end, [span]), [span]
        )
        in_span = [seed for seed in seeds if span.begin <= seed.tick <= span.end]
        found: tuple[EncounterSummary, list[_Seed]] | None = None
        for candidate in _build_encounters(gen, span, in_span, grouping, subject):
            if candidate[0].encounter_id == encounter_id:
                found = candidate
                break
        if found is None:
            raise AppError(
                "NOT_FOUND",
                f"encounter {encounter_id} not found for {subject} in round {round_id}; "
                "grouping options may differ from the list query that produced the id",
                STAGE,
            )
        summary, cluster = found
        _, window_start, window_end = _anchors(span, cluster, grouping, subject)
        seed_keys = {(seed.dataset, seed.row_ordinal) for seed in cluster}

        events, extra_players = self._detail_context(
            gen, span, window_start, window_end, subject, summary.participant_ids, seed_keys
        )
        participants, approximated = self._detail_participants(
            gen, summary, events, window_start, window_end, subject, extra_players
        )
        trajectory, stride, missing = self._trajectory(gen, subject, window_start, window_end)

        limitations: set[str] = {LIMITATION_GROUPING_HEURISTIC}
        limitations.update(summary.limitations)
        if stride > 1:
            limitations.add(LIMITATION_TRAJECTORY_DOWNSAMPLED)
        if approximated:
            limitations.add(
                "participant side resolved from the nearest recorded state tick for: "
                + ", ".join(sorted(approximated))
            )
        if not trajectory:
            limitations.add("no recorded subject state rows inside the encounter window")
        return EncounterDetail(
            summary=summary,
            source_window=EncounterSourceWindow(
                round_id=span.round_id,
                round_start_tick=span.begin,
                round_end_tick=span.end,
                window_start_tick=window_start,
                window_end_tick=window_end,
                truncated_start=window_start > summary.first_interaction_tick - grouping.pre_ticks,
                truncated_end=window_end < summary.last_interaction_tick + grouping.post_ticks,
            ),
            grouping=grouping,
            events=events,
            participants=participants,
            subject_event_count=sum(1 for event in events if event.subject_involved),
            contextual_event_count=sum(1 for event in events if event.contextual),
            subject_trajectory=trajectory,
            trajectory_stride=stride,
            trajectory_missing_ranges=missing,
            provenance=_provenance(gen, limitations),
            limitations=sorted(limitations),
        )

    # -- internals ---------------------------------------------------------
    def _detail_context(
        self,
        gen: Any,
        span: _Round,
        window_start: int,
        window_end: int,
        subject: str,
        participant_ids: Sequence[str],
        seed_keys: set[tuple[str, int]],
    ) -> tuple[list[EncounterEvent], set[str]]:
        return _detail_events(
            self.pool, gen, span, window_start, window_end, subject, participant_ids, seed_keys
        )

    def _detail_participants(
        self,
        gen: Any,
        summary: EncounterSummary,
        events: Sequence[EncounterEvent],
        window_start: int,
        window_end: int,
        subject: str,
        extra_players: set[str],
    ) -> tuple[list[EncounterParticipant], list[str]]:
        player_ids = sorted(set(summary.participant_ids) | extra_players)
        if player_ids:
            predicate = pl.col("player_id").is_in([subject, *player_ids])
            states = _read_span(
                self.pool, gen, "player_state", window_start, window_end, columns=_STATE_COLUMNS, predicate=predicate
            )
        else:
            states = pl.DataFrame(
                {"tick": [], "row_ordinal": [], "player_id": [], "side": []},
                schema={"tick": pl.Int64, "row_ordinal": pl.Int64, "player_id": pl.String, "side": pl.String},
            )
        return _participants(events, summary.participant_ids, states, subject, window_start)

    def _trajectory(
        self, gen: Any, subject: str, window_start: int, window_end: int
    ) -> tuple[list[AnalyticState], int, list[list[int]]]:
        from .temporal import player_interval

        length = window_end - window_start + 1
        stride = max(1, math.ceil(length / MAX_TRAJECTORY_ROWS))
        result = player_interval(self.pool, gen, subject, window_start, window_end, stride)
        states = [AnalyticState(**row) for row in result["states"]]
        return states, stride, [list(item) for item in result["missing_ranges"]]

    def _absence_limitation(self, gen: Any, subject: str) -> str:
        players = getattr(gen, "players", None)
        if players is not None and players.height:
            ids = set(players.get_column("player_id").to_list())
            if subject not in ids:
                return (
                    f"subject {subject} is not present in generation {gen.generation_id}; "
                    "no encounters were reconstructed"
                )
        return (
            f"subject {subject} has no recorded shots, damage, kills or assists in "
            f"generation {gen.generation_id}"
        )


def _round_from_id(encounter_id: str) -> int:
    if not isinstance(encounter_id, str):
        raise AppError("INVALID_ARGUMENT", "encounter_id must be a string", STAGE)
    prefix = f"{ENCOUNTER_ID_PREFIX}-r"
    if not encounter_id.startswith(prefix):
        raise AppError(
            "INVALID_ARGUMENT",
            f"encounter_id {encounter_id!r} is not in the {ENCOUNTER_ID_PREFIX}-r<round_id>-<16 hex> format",
            STAGE,
        )
    head, _, tail = encounter_id[len(prefix) :].partition("-")
    if not head.isdigit() or len(tail) != 16 or any(char not in "0123456789abcdef" for char in tail):
        raise AppError(
            "INVALID_ARGUMENT",
            f"encounter_id {encounter_id!r} is malformed; expected {ENCOUNTER_ID_PREFIX}-r<round_id>-<16 hex>",
            STAGE,
        )
    return int(head)

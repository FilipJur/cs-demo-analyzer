"""Temporal analytics over a generation's normalized tables.

Units
-----
Ticks are integer simulation ticks sampled at ``gen.tick_rate_hz`` per second;
seconds are derived only through :func:`tick_to_seconds`. State values are returned
verbatim from ``player_state`` (Hammer world units, degrees yaw), never re-projected.

Interpolation policy
--------------------
Rows are always returned verbatim. Nothing is synthesized, interpolated or
extrapolated:

* :func:`state_at` finds the exact tick, or the nearest tick *within* ``max_gap``
  that actually contains rows; otherwise it reports ``actual_tick=None`` and an
  empty state list.
* :func:`player_interval` reports holes explicitly as ``missing_ranges`` (tick
  values, coalesced along the sampling grid) instead of filling them in.
* Searches never bridge deaths, round boundaries or gaps wider than the caller's
  ``max_gap`` -- there is no implicit carry-forward of the last observation.

Bounded reads
-------------
Every scan is split into fixed tick spans (:data:`_CHUNK_TICKS`) and materialized
through ``pool.read`` with an explicit row cap, so a single call can never pull an
unbounded table into memory.

The ``pool`` argument is injected (duck-typed :class:`PoolLike`); this module never
imports the catalog or the concrete pool implementation.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence

import polars as pl

from ..domain.contracts import AppError, EvidenceRef
from ..domain.tables import SCHEMAS

#: Event datasets merged by the timeline helpers, in their canonical tie-break order.
EVENT_DATASETS: tuple[str, ...] = ("kills", "damages", "shots", "bomb")
_EVENT_ORDER: dict[str, int] = {name: index for index, name in enumerate(EVENT_DATASETS)}

#: Columns needed from each event table to build a timeline entry.
_EVENT_COLUMNS: dict[str, list[str]] = {
    "kills": ["row_ordinal", "tick", "attacker_id", "victim_id", "weapon"],
    "damages": ["row_ordinal", "tick", "attacker_id", "victim_id", "damage_health"],
    "shots": ["row_ordinal", "tick", "player_id", "weapon"],
    "bomb": ["row_ordinal", "tick", "player_id", "action"],
}

_CHUNK_TICKS = 20_000
#: Span for the unfiltered tick-presence search in :func:`state_at` (all entities/tick).
_TICK_SEARCH_CHUNK = 4_096
_FETCH_LIMIT = 100_000

MAX_EVENT_LIMIT = 5_000
MAX_NEARBY_EVENTS = 100
MAX_WINDOW_TICKS = 64_000
MAX_INTERVAL_STRIDE = 4_096


class PoolLike(Protocol):
    """Structural type of the injected :class:`GenerationPool`."""

    def read(
        self,
        gen: Any,
        table: str,
        *,
        columns: list[str] | None = None,
        predicate: pl.Expr | None = None,
        limit: int = 0,
    ) -> pl.DataFrame: ...


class GenerationLike(Protocol):
    """Structural type of the injected :class:`Generation`."""

    demo_id: str
    generation_id: str
    profile_key: str
    tick_rate_hz: float
    rounds: pl.DataFrame
    players: pl.DataFrame


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #
def err(code: str, message: str, stage: str = "analytics") -> AppError:
    return AppError(code, message, stage)


def invalid(message: str) -> AppError:
    return err("INVALID_ARGUMENT", message)


def _empty_frame(table: str, columns: Sequence[str] | None) -> pl.DataFrame:
    schema = SCHEMAS[table]
    names = list(schema) if columns is None else list(columns)
    return pl.DataFrame(schema={name: schema[name] for name in names})


def _read_span(
    pool: PoolLike,
    gen: GenerationLike,
    table: str,
    lo: int,
    hi: int,
    *,
    columns: Sequence[str] | None = None,
    predicate: pl.Expr | None = None,
    chunk: int = _CHUNK_TICKS,
    limit: int = _FETCH_LIMIT,
) -> pl.DataFrame:
    """Materialize ``table`` rows with ``lo <= tick <= hi`` in bounded tick spans."""
    frames: list[pl.DataFrame] = []
    start = lo
    while start <= hi:
        stop = min(start + chunk - 1, hi)
        span = (pl.col("tick") >= start) & (pl.col("tick") <= stop)
        if predicate is not None:
            span = span & predicate
        frames.append(pool.read(gen, table, columns=columns, predicate=span, limit=limit))
        start = stop + 1
    if not frames:
        return _empty_frame(table, columns)
    return pl.concat(frames, how="vertical")


def _validate_datasets(datasets: Sequence[str]) -> list[str]:
    ordered: list[str] = []
    for dataset in datasets:
        if dataset not in _EVENT_ORDER:
            raise invalid(f"unknown dataset {dataset!r}; expected one of {list(EVENT_DATASETS)}")
        if dataset not in ordered:
            ordered.append(dataset)
    return ordered


def _event_sort_key(event: dict[str, Any]) -> tuple[int, int, int]:
    return (event["tick"], _EVENT_ORDER[event["dataset"]], event["row_ordinal"])


def _event_dict(dataset: str, row: dict[str, Any]) -> dict[str, Any]:
    if dataset == "kills":
        actor1, actor2, detail = row["attacker_id"], row["victim_id"], row["weapon"]
    elif dataset == "damages":
        actor1, actor2 = row["attacker_id"], row["victim_id"]
        detail = None if row["damage_health"] is None else str(row["damage_health"])
    elif dataset == "shots":
        actor1, actor2, detail = row["player_id"], None, row["weapon"]
    else:  # bomb
        actor1, actor2, detail = row["player_id"], None, row["action"]
    return {
        "dataset": dataset,
        "row_ordinal": int(row["row_ordinal"]),
        "tick": int(row["tick"]),
        "actor1": actor1,
        "actor2": actor2,
        "detail": detail,
    }


def _event_rows(
    pool: PoolLike, gen: GenerationLike, dataset: str, lo: int, hi: int
) -> list[dict[str, Any]]:
    if lo > hi:
        return []
    frame = _read_span(pool, gen, dataset, lo, hi, columns=_EVENT_COLUMNS[dataset])
    return [_event_dict(dataset, row) for row in frame.iter_rows(named=True)]


def _round_bounds(gen: GenerationLike) -> tuple[int, int] | None:
    rounds = gen.rounds
    if rounds is None or rounds.height == 0:
        return None
    starts = [int(value) for value in rounds["start_tick"].to_list() if value is not None]
    ends = [int(value) for value in rounds["end_tick"].to_list() if value is not None]
    if not starts or not ends:
        return None
    return min(starts), max(ends)


def _state_dicts(frame: pl.DataFrame) -> list[dict[str, Any]]:
    return frame.sort("tick", "row_ordinal").to_dicts()


def _round_row(gen: GenerationLike, round_id: int) -> dict[str, Any] | None:
    rounds = gen.rounds
    if rounds is None or rounds.height == 0:
        return None
    match = rounds.filter(pl.col("round_id") == round_id)
    if match.height == 0:
        return None
    return match.row(0, named=True)


def _round_begin(row: dict[str, Any]) -> int | None:
    freeze_end = row.get("freeze_end_tick")
    return freeze_end if freeze_end is not None else row.get("start_tick")


# --------------------------------------------------------------------------- #
# state access
# --------------------------------------------------------------------------- #
def state_at(
    pool: PoolLike,
    gen: GenerationLike,
    tick: int,
    player_id: str | None = None,
    max_gap: int = 0,
) -> dict[str, Any]:
    """Verbatim ``player_state`` rows at ``tick`` or the nearest tick within ``max_gap``.

    Returns ``{actual_tick, gap, exact, states}``. ``gap`` is signed
    (``actual_tick - tick``); ``actual_tick`` is ``None`` with empty ``states`` when
    nothing lies within ``max_gap``.
    """
    if tick < 0:
        raise invalid("tick must be non-negative")
    if max_gap < 0:
        raise invalid("max_gap must be non-negative")

    predicate = (pl.col("player_id") == player_id) if player_id is not None else None

    exact = pool.read(
        gen,
        "player_state",
        predicate=(pl.col("tick") == tick) if predicate is None else (pl.col("tick") == tick) & predicate,
        limit=_FETCH_LIMIT,
    )
    if exact.height:
        return {"actual_tick": tick, "gap": 0, "exact": True, "states": _state_dicts(exact)}

    if max_gap == 0:
        return {"actual_tick": None, "gap": None, "exact": False, "states": []}

    # Unfiltered tick search reads every entity per tick, so keep the span small
    # enough that ~11 entities per tick stay well under the materialization cap.
    window = _read_span(
        pool,
        gen,
        "player_state",
        tick - max_gap,
        tick + max_gap,
        columns=["tick"],
        predicate=predicate,
        chunk=_TICK_SEARCH_CHUNK,
    )
    present = sorted(set(window["tick"].to_list())) if window.height else []
    if not present:
        return {"actual_tick": None, "gap": None, "exact": False, "states": []}

    actual = min(present, key=lambda value: (abs(value - tick), value))
    rows = pool.read(
        gen,
        "player_state",
        predicate=(pl.col("tick") == actual) if predicate is None else (pl.col("tick") == actual) & predicate,
        limit=_FETCH_LIMIT,
    )
    return {
        "actual_tick": int(actual),
        "gap": int(actual) - tick,
        "exact": int(actual) == tick,
        "states": _state_dicts(rows),
    }


def player_interval(
    pool: PoolLike,
    gen: GenerationLike,
    player_id: str,
    start: int,
    end: int,
    stride: int = 1,
) -> dict[str, Any]:
    """Verbatim ``player_state`` rows for one player over ``[start, end]`` on ``stride``.

    ``missing_ranges`` lists the grid ticks with no row, coalesced into ``[lo, hi]``
    tick pairs; holes are never filled.
    """
    if not player_id:
        raise invalid("player_id must be a non-empty string")
    if start > end:
        raise invalid("start must not exceed end")
    if stride < 1 or stride > MAX_INTERVAL_STRIDE:
        raise invalid(f"stride must be in 1..{MAX_INTERVAL_STRIDE}")

    grid = list(range(start, end + 1, stride))
    predicate = pl.col("player_id") == player_id

    states: list[dict[str, Any]] = []
    seen: set[int] = set()
    for offset in range(0, len(grid), _CHUNK_TICKS):
        batch = grid[offset : offset + _CHUNK_TICKS]
        frame = pool.read(
            gen,
            "player_state",
            predicate=predicate & pl.col("tick").is_in(batch),
            limit=_FETCH_LIMIT,
        )
        if frame.height:
            states.extend(frame.to_dicts())
            seen.update(frame["tick"].to_list())

    states.sort(key=lambda row: row["tick"])

    missing_ranges: list[list[int]] = []
    hole_lo: int | None = None
    last_missing: int | None = None
    for tick in grid:
        if tick in seen:
            if hole_lo is not None:
                missing_ranges.append([hole_lo, last_missing])
                hole_lo = None
        else:
            if hole_lo is None:
                hole_lo = tick
            last_missing = tick
    if hole_lo is not None:
        missing_ranges.append([hole_lo, last_missing])

    return {"states": states, "missing_ranges": missing_ranges}


# --------------------------------------------------------------------------- #
# events
# --------------------------------------------------------------------------- #
def events_in(
    pool: PoolLike,
    gen: GenerationLike,
    datasets: Sequence[str],
    start: int,
    end: int,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """Events from ``datasets`` within ``[start, end]``, merged chronologically.

    Ordering is ``(tick, dataset kills<damages<shots<bomb, row_ordinal)``; the
    result is truncated to ``limit`` (max :data:`MAX_EVENT_LIMIT`).
    """
    ordered = _validate_datasets(datasets)
    if limit < 0 or limit > MAX_EVENT_LIMIT:
        raise invalid(f"limit must be in 0..{MAX_EVENT_LIMIT}")

    merged: list[dict[str, Any]] = []
    for dataset in ordered:
        merged.extend(_event_rows(pool, gen, dataset, start, end))
    merged.sort(key=_event_sort_key)
    return merged[:limit]


def events_around(
    pool: PoolLike,
    gen: GenerationLike,
    tick: int,
    before_n: int,
    after_n: int,
    datasets: Sequence[str],
) -> dict[str, Any]:
    """The ``before_n`` / ``after_n`` events nearest to (strictly before/after) ``tick``.

    Counts are 0..:data:`MAX_NEARBY_EVENTS`; the search is bounded by the extent of
    the generation's rounds. Both lists are chronological (nearest last for
    ``before``, nearest first for ``after``).
    """
    ordered = _validate_datasets(datasets)
    if before_n < 0 or before_n > MAX_NEARBY_EVENTS:
        raise invalid(f"before_n must be in 0..{MAX_NEARBY_EVENTS}")
    if after_n < 0 or after_n > MAX_NEARBY_EVENTS:
        raise invalid(f"after_n must be in 0..{MAX_NEARBY_EVENTS}")

    bounds = _round_bounds(gen)
    if bounds is None:
        return {"before": [], "after": []}
    lo, hi = bounds

    before: list[dict[str, Any]] = []
    if before_n and tick - 1 >= lo:
        before = _collect_directional(pool, gen, ordered, tick, before_n, lo, tick - 1, forward=False)

    after: list[dict[str, Any]] = []
    if after_n and tick + 1 <= hi:
        after = _collect_directional(pool, gen, ordered, tick, after_n, tick + 1, hi, forward=True)

    return {"before": before, "after": after}


def _collect_directional(
    pool: PoolLike,
    gen: GenerationLike,
    datasets: Sequence[str],
    tick: int,
    want: int,
    lo: int,
    hi: int,
    *,
    forward: bool,
) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    if forward:
        cursor = tick + 1
        while cursor <= hi and len(collected) < want:
            stop = min(cursor + _CHUNK_TICKS - 1, hi)
            for dataset in datasets:
                collected.extend(_event_rows(pool, gen, dataset, cursor, stop))
            cursor = stop + 1
    else:
        cursor = tick - 1
        while cursor >= lo and len(collected) < want:
            start = max(cursor - _CHUNK_TICKS + 1, lo)
            for dataset in datasets:
                collected.extend(_event_rows(pool, gen, dataset, start, cursor))
            cursor = start - 1
    collected.sort(key=_event_sort_key)
    return collected[:want] if forward else collected[-want:]


def event_window(
    pool: PoolLike,
    gen: GenerationLike,
    dataset: str,
    row_ordinal: int,
    before_ticks: int,
    after_ticks: int,
) -> dict[str, Any]:
    """One event plus the identified states and neighbouring events around it.

    ``states`` are verbatim identified rows of the event's involved players within
    ``[tick-before_ticks, tick+after_ticks]``; ``nearby_events`` is :func:`events_in`
    over the same range.
    """
    _validate_datasets([dataset])
    if before_ticks < 0 or before_ticks > MAX_WINDOW_TICKS:
        raise invalid(f"before_ticks must be in 0..{MAX_WINDOW_TICKS}")
    if after_ticks < 0 or after_ticks > MAX_WINDOW_TICKS:
        raise invalid(f"after_ticks must be in 0..{MAX_WINDOW_TICKS}")

    frame = pool.read(
        gen,
        dataset,
        columns=_EVENT_COLUMNS[dataset],
        predicate=pl.col("row_ordinal") == row_ordinal,
        limit=2,
    )
    if frame.height == 0:
        raise err("NOT_FOUND", f"no {dataset} row with row_ordinal {row_ordinal}")
    event = _event_dict(dataset, frame.row(0, named=True))

    involved: list[str] = []
    for actor in (event["actor1"], event["actor2"]):
        if actor is not None and actor not in involved:
            involved.append(actor)

    lo = event["tick"] - before_ticks
    hi = event["tick"] + after_ticks

    states: list[dict[str, Any]] = []
    if involved:
        predicate = pl.col("player_id").is_in(involved)
        state_frame = _read_span(pool, gen, "player_state", lo, hi, predicate=predicate)
        states = _state_dicts(state_frame)

    nearby = events_in(pool, gen, list(EVENT_DATASETS), lo, hi)
    return {"event": event, "states": states, "nearby_events": nearby}


def timeline(
    pool: PoolLike,
    gen: GenerationLike,
    datasets: Sequence[str] | None,
    start: int,
    end: int,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """Alias of :func:`events_in`; ``datasets=None`` means all four datasets."""
    return events_in(pool, gen, list(EVENT_DATASETS) if datasets is None else datasets, start, end, limit)


# --------------------------------------------------------------------------- #
# rounds and clocks
# --------------------------------------------------------------------------- #
def round_of(pool: PoolLike, gen: GenerationLike, tick: int) -> int | None:
    """``round_id`` whose ``[freeze_end_tick or start_tick, end_tick]`` contains ``tick``."""
    rounds = gen.rounds
    if rounds is None or rounds.height == 0:
        return None
    for row in rounds.iter_rows(named=True):
        begin = _round_begin(row)
        end = row.get("end_tick")
        if begin is None or end is None:
            continue
        if begin <= tick <= end:
            return int(row["round_id"])
    return None


def round_window(pool: PoolLike, gen: GenerationLike, round_id: int) -> tuple[int, int]:
    """``(begin, end)`` for ``round_id``; ``PARTIAL_ROUND`` when its timing is incomplete."""
    row = _round_row(gen, round_id)
    if row is None:
        raise err("NOT_FOUND", f"round {round_id} not found")
    begin = _round_begin(row)
    end = row.get("end_tick")
    if begin is None or end is None:
        raise err("PARTIAL_ROUND", f"round {round_id} has incomplete timing")
    return int(begin), int(end)


def tick_to_seconds(pool: PoolLike, gen: GenerationLike, tick: int) -> float:
    """Convert a tick index to seconds using ``gen.tick_rate_hz``."""
    return tick / gen.tick_rate_hz


# --------------------------------------------------------------------------- #
# provenance
# --------------------------------------------------------------------------- #
def evidence_ref(
    gen: GenerationLike,
    dataset: str,
    row_ordinal: int,
    tick: int,
    round_id: int | None,
    player_ids: list[str],
) -> EvidenceRef:
    """Build a provenance reference pointing at one row of ``dataset``."""
    return EvidenceRef(
        demo_id=gen.demo_id,
        generation_id=gen.generation_id,
        profile_key=gen.profile_key,
        dataset=dataset,
        row_ordinal=row_ordinal,
        tick=tick,
        round_id=round_id,
        player_ids=list(player_ids),
    )

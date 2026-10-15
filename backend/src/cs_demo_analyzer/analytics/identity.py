"""Identity coverage over generation-pinned state.

Dead-entity rule (measured on the retained Inferno demo, Phase 1 gate)
---------------------------------------------------------------------
A ``player_state`` row with a null ``player_id`` is an observable *dead entity*
(the engine keeps emitting the corpse entity at its death position). Such rows
are real observations and are therefore:

* **included** in raw counts (``total_observations``, ``null_observations``),
* **excluded** from live-player operations (they are never "alive" here),
* **never** re-attached to a player by position, name or ordering — the module
  reads only ``tick``, ``player_id`` and ``health``, so a corpse row that shares
  a position with a living player cannot be mistaken for that player.

"Alive" is defined as ``health > 0``; a null health counts as not alive. On
healthy data ``alive_null == 0`` and ``live_coverage == 1.0``. A non-empty
``live_identity_violations`` therefore always means genuinely unidentified
living rows, never corpses.
"""

from __future__ import annotations

import polars as pl

from ..domain.contracts import AppError, IdentityCoverage
from .access import Generation, GenerationPool

STAGE = "analytics"

_ALIVE = pl.col("health") > 0
_NULL_ID = pl.col("player_id").is_null()

_STATE_COLUMNS = ["tick", "player_id", "health"]


def _range_predicate(begin: int | None, end: int | None) -> pl.Expr | None:
    if begin is None or end is None:
        return None
    return (pl.col("tick") >= begin) & (pl.col("tick") <= end)


def _scope(gen: Generation, round_id: int | None) -> tuple[str, int | None, int | None]:
    """``(scope_label, begin, end)``; ``round_id is None`` spans the whole generation.

    A round window is ``[freeze_end_tick or start_tick, end_tick]``: ticks before
    the freeze end belong to the previous round's death tail.
    """
    if round_id is None:
        return "generation", None, None

    matching = gen.rounds.filter(pl.col("round_id") == round_id)
    if matching.height == 0:
        raise AppError("NOT_FOUND", f"round {round_id} is not in generation {gen.generation_id}", STAGE)

    row = matching.select("start_tick", "freeze_end_tick", "end_tick").to_dicts()[0]
    end = row["end_tick"]
    begin = row["freeze_end_tick"] if row["freeze_end_tick"] is not None else row["start_tick"]
    if begin is None or end is None or begin > end:
        raise AppError(
            "PARTIAL_ROUND",
            f"round {round_id} has incomplete timing (start={row['start_tick']}, "
            f"freeze_end={row['freeze_end_tick']}, end={end})",
            STAGE,
        )
    return f"round:{round_id}", int(begin), int(end)


def coverage(pool: GenerationPool, gen: Generation, round_id: int | None = None) -> IdentityCoverage:
    """Identity coverage for a whole generation or one round window.

    ``live_coverage = alive_identified / alive_total`` and is ``None`` when the
    window contains no living row at all. ``notes`` characterize the null rows
    that were counted, so a reader can tell corpses from missing identities
    without re-deriving it.
    """
    scope, begin, end = _scope(gen, round_id)
    frame = pool.scan(gen, "player_state", columns=_STATE_COLUMNS, predicate=_range_predicate(begin, end))

    totals = frame.select(
        pl.len().alias("total"),
        _NULL_ID.sum().alias("null_observations"),
        _ALIVE.sum().alias("alive_total"),
        (_ALIVE & _NULL_ID).sum().alias("alive_null"),
        (_ALIVE & pl.col("player_id").is_not_null()).sum().alias("alive_identified"),
        (_NULL_ID & ((pl.col("health") != 0) | pl.col("health").is_null())).sum().alias("null_with_health"),
    ).collect()
    values = totals.row(0, named=True)

    total = int(values["total"])
    null_observations = int(values["null_observations"])
    alive_total = int(values["alive_total"])
    alive_identified = int(values["alive_identified"])
    alive_null = int(values["alive_null"])

    notes: list[str] = []
    if null_observations:
        if int(values["null_with_health"]) == 0:
            notes.append(f"null observations {null_observations}, all health==0 (dead entities)")
        else:
            notes.append(
                f"null observations {null_observations}, {int(values['null_with_health'])} of them "
                "carrying health data (dead entities expected)"
            )
    else:
        notes.append("no null observations: every state row carries an identified player id")
    if alive_null:
        notes.append(f"alive-with-null-id violations: {alive_null} (dead-entity rule violated)")
    notes.append(
        f"scope {scope}: {total} observations, {alive_total} alive, {total - alive_total} dead entities"
    )

    return IdentityCoverage(
        total_observations=total,
        identified=total - null_observations,
        null_observations=null_observations,
        alive_total=alive_total,
        alive_identified=alive_identified,
        alive_null=alive_null,
        live_coverage=(alive_identified / alive_total) if alive_total else None,
        notes=notes,
    )


def live_identity_violations(pool: GenerationPool, gen: Generation, round_id: int | None = None) -> list[int]:
    """Distinct ticks holding at least one alive row with a null player id.

    Empty on healthy data; a violation here is a genuinely unidentified living
    player, not a corpse row.
    """
    _, begin, end = _scope(gen, round_id)
    window = _range_predicate(begin, end)
    predicate = _ALIVE & _NULL_ID
    if window is not None:
        predicate = predicate & window

    frame = pool.scan(gen, "player_state", columns=["tick"], predicate=predicate).unique().collect()
    return sorted(int(tick) for tick in frame.get_column("tick").to_list())

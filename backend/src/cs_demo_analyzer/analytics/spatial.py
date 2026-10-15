"""Pure spatial math for Counter-Strike (Source 2) replay analytics.

Units and conventions
---------------------
* Coordinates are **Hammer world units**, Z-up, right-handed, exactly as stored in
  ``player_state`` (``x``/``y``/``z``). One Hammer unit is 0.75 in (1.905 cm); this
  module deliberately works in units and never converts to meters.
* ``yaw`` is degrees in ``[-180, 180]``; :func:`yaw_diff` returns the shortest-arc
  *signed* difference in the same range.
* This module is geometric only: there is **no line-of-sight**, raycast, visibility
  or nav-mesh logic here.

Living versus recorded positions
--------------------------------
``player_state`` keeps emitting rows after death (``health == 0``), so the
pooled helpers see corpse positions as well as living players. All three report
raw geometry by default: a nearby corpse still counts as nearby. Pass
``alive_only=True`` when the question is about active players (support,
trading, spacing) so ``health == 0`` rows are skipped instead of measured.
Default behavior is unchanged.

The ``pool`` argument is injected (duck-typed :class:`~.temporal.PoolLike`); this
module never imports the catalog or a concrete pool.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import polars as pl

from .temporal import (
    GenerationLike,
    PoolLike,
    _read_span,
    _FETCH_LIMIT,
    invalid,
)

MAX_PAIR_TICKS = 10_000


# --------------------------------------------------------------------------- #
# scalar helpers
# --------------------------------------------------------------------------- #
def _finite(*values: float | None) -> bool:
    return all(value is not None and math.isfinite(value) for value in values)


def dist2d(x1: float | None, y1: float | None, x2: float | None, y2: float | None) -> float | None:
    """Planar (XY) distance in Hammer units, or ``None`` if any input is None/non-finite."""
    if not _finite(x1, y1, x2, y2):
        return None
    return math.hypot(x2 - x1, y2 - y1)


def dist3d(
    x1: float | None,
    y1: float | None,
    z1: float | None,
    x2: float | None,
    y2: float | None,
    z2: float | None,
) -> float | None:
    """Full 3D distance in Hammer units, or ``None`` if any input is None/non-finite."""
    if not _finite(x1, y1, z1, x2, y2, z2):
        return None
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def speed(vx: float | None, vy: float | None, vz: float | None) -> float | None:
    """Velocity magnitude in the stored velocity units, or ``None`` if any input is bad."""
    if not _finite(vx, vy, vz):
        return None
    return math.sqrt(vx * vx + vy * vy + vz * vz)


def yaw_diff(a: float | None, b: float | None) -> float | None:
    """Shortest-arc signed difference ``b - a`` in degrees, within ``[-180, 180]``."""
    if not _finite(a, b):
        return None
    return ((b - a + 180.0) % 360.0) - 180.0


def displacement(
    x1: float | None, y1: float | None, x2: float | None, y2: float | None
) -> tuple[float | None, float | None, float | None]:
    """``(dx, dy, dist2d)`` between two planar points; all ``None`` when inputs are bad."""
    if not _finite(x1, y1, x2, y2):
        return (None, None, None)
    dx = x2 - x1
    dy = y2 - y1
    return (dx, dy, math.hypot(dx, dy))


# --------------------------------------------------------------------------- #
# pooled helpers
# --------------------------------------------------------------------------- #
def _read_pair_spans(
    pool: PoolLike,
    gen: GenerationLike,
    a: str,
    b: str,
    lo: int,
    hi: int,
    *,
    columns: Sequence[str],
) -> pl.DataFrame:
    predicate = pl.col("player_id").is_in([a, b])
    return _read_span(pool, gen, "player_state", lo, hi, columns=columns, predicate=predicate)


def _coords(frame: pl.DataFrame) -> dict[tuple[int, str], tuple[Any, Any, Any]]:
    coords: dict[tuple[int, str], tuple[Any, Any, Any]] = {}
    for row in frame.iter_rows(named=True):
        coords[(int(row["tick"]), row["player_id"])] = (row["x"], row["y"], row["z"])
    return coords


def pair_distance_over_time(
    pool: PoolLike,
    gen: GenerationLike,
    a: str,
    b: str,
    ticks: Sequence[int],
    *,
    alive_only: bool = False,
) -> list[dict[str, Any]]:
    """Per-tick distances between players ``a`` and ``b``; exact ticks only.

    Returns ``[{tick, d2d, d3d, missing}]`` preserving the order of ``ticks`` (which
    may repeat). ``missing`` is ``True`` when either player has no row at that tick or
    their coordinates are not finite, in which case both distances are ``None``.
    At most :data:`MAX_PAIR_TICKS` ticks are accepted.

    Raw geometry by default: ``health == 0`` rows still count. With
    ``alive_only=True`` a tick where either side is not ``health > 0`` reports
    ``missing=True`` instead of a distance.
    """
    tick_list = [int(tick) for tick in ticks]
    if not tick_list:
        raise invalid("ticks must not be empty")
    if len(tick_list) > MAX_PAIR_TICKS:
        raise invalid(f"ticks must contain at most {MAX_PAIR_TICKS} entries")

    coords: dict[tuple[int, str], tuple[Any, Any, Any]] = {}
    for offset in range(0, len(tick_list), 512):
        batch = tick_list[offset : offset + 512]
        predicate = (pl.col("tick").is_in(batch)) & pl.col("player_id").is_in([a, b])
        columns = (
            ["tick", "player_id", "x", "y", "z", "health"] if alive_only else ["tick", "player_id", "x", "y", "z"]
        )
        if alive_only:
            predicate = predicate & (pl.col("health") > 0)
        frame = pool.read(
            gen,
            "player_state",
            columns=columns,
            predicate=predicate,
            limit=_FETCH_LIMIT,
        )
        coords.update(_coords(frame))

    results: list[dict[str, Any]] = []
    for tick in tick_list:
        first = coords.get((tick, a))
        second = coords.get((tick, b))
        if first is None or second is None:
            results.append({"tick": tick, "d2d": None, "d3d": None, "missing": True})
            continue
        d2d = dist2d(first[0], first[1], second[0], second[1])
        d3d = dist3d(first[0], first[1], first[2], second[0], second[1], second[2])
        if d2d is None or d3d is None:
            results.append({"tick": tick, "d2d": None, "d3d": None, "missing": True})
            continue
        results.append({"tick": tick, "d2d": d2d, "d3d": d3d, "missing": False})
    return results


def nearby(
    pool: PoolLike,
    gen: GenerationLike,
    tick: int,
    player_id: str,
    radius: float,
    *,
    alive_only: bool = False,
) -> list[dict[str, Any]]:
    """Other players within ``radius`` planar units of ``player_id`` at the exact ``tick``.

    Only players with finite coordinates at that exact tick are considered; the result
    is sorted by ``(d2d, player_id)``. Returns ``[]`` if the reference player is absent.

    Raw geometry by default: ``health == 0`` rows still count. With
    ``alive_only=True`` only ``health > 0`` rows are considered, and a dead or
    absent reference player yields ``[]``.
    """
    if radius is None or not math.isfinite(radius) or radius <= 0:
        raise invalid("radius must be a positive finite number")

    columns = ["player_id", "x", "y", "z", "health"] if alive_only else ["player_id", "x", "y", "z"]
    if alive_only:
        predicate = (pl.col("tick") == tick) & (pl.col("health") > 0)
    else:
        predicate = pl.col("tick") == tick
    frame = pool.read(
        gen,
        "player_state",
        columns=columns,
        predicate=predicate,
        limit=_FETCH_LIMIT,
    )

    coords: dict[str, tuple[Any, Any, Any]] = {}
    for row in frame.iter_rows(named=True):
        if row["player_id"] is not None:
            coords[row["player_id"]] = (row["x"], row["y"], row["z"])

    origin = coords.get(player_id)
    if origin is None or not _finite(origin[0], origin[1]):
        return []

    found: list[dict[str, Any]] = []
    for other, point in coords.items():
        if other == player_id:
            continue
        d2d = dist2d(origin[0], origin[1], point[0], point[1])
        if d2d is None or d2d > radius:
            continue
        found.append(
            {
                "player_id": other,
                "d2d": d2d,
                "d3d": dist3d(origin[0], origin[1], origin[2], point[0], point[1], point[2]),
            }
        )
    found.sort(key=lambda entry: (entry["d2d"], entry["player_id"]))
    return found


def time_within(
    pool: PoolLike,
    gen: GenerationLike,
    a: str,
    b: str,
    start: int,
    end: int,
    radius: float,
    *,
    alive_only: bool = False,
) -> dict[str, Any]:
    """Fraction of ticks in ``[start, end]`` where ``a`` and ``b`` are within ``radius`` (2D).

    Only exact ticks at which *both* players have finite coordinates are compared.
    ``fraction`` is ``None`` when no such tick exists.

    Raw geometry by default: rows with ``health == 0`` still count. With
    ``alive_only=True`` only ``health > 0`` rows are compared, so ticks where
    either side is dead are skipped rather than counted.
    """
    if radius is None or not math.isfinite(radius) or radius <= 0:
        raise invalid("radius must be a positive finite number")

    compared = 0
    within = 0
    if start <= end:
        state_columns = (
            ["tick", "player_id", "x", "y", "health"] if alive_only else ["tick", "player_id", "x", "y"]
        )
        frame = _read_pair_spans(pool, gen, a, b, start, end, columns=state_columns)
        if alive_only:
            frame = frame.filter(pl.col("health") > 0)
        points: dict[tuple[int, str], tuple[Any, Any]] = {}
        ticks: set[int] = set()
        for row in frame.iter_rows(named=True):
            tick = int(row["tick"])
            points[(tick, row["player_id"])] = (row["x"], row["y"])
            ticks.add(tick)
        for tick in ticks:
            pa = points.get((tick, a))
            pb = points.get((tick, b))
            if pa is None or pb is None or not _finite(pa[0], pa[1], pb[0], pb[1]):
                continue
            compared += 1
            if dist2d(pa[0], pa[1], pb[0], pb[1]) <= radius:
                within += 1

    fraction = (within / compared) if compared else None
    return {"ticks_compared": compared, "ticks_within": within, "fraction": fraction}

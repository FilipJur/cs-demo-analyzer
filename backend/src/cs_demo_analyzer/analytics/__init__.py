"""Analytics foundation: generation-pinned access, identity, time and space.

Public surface for Phase 1: :class:`GenerationPool` opens pinned
:class:`Generation` handles under the :data:`MAX_MATERIALIZED_ROWS` cap,
``coverage``/``live_identity_violations`` measure identity coverage under the
null-player-id dead-entity rule (see ``identity``), and ``temporal``/``spatial``
provide verbatim-row time operations and unit-documented spatial math.
"""

from . import spatial, temporal
from .access import MAX_MATERIALIZED_ROWS, Generation, GenerationPool
from .identity import coverage, live_identity_violations
from .spatial import (
    displacement,
    dist2d,
    dist3d,
    nearby,
    pair_distance_over_time,
    speed,
    time_within,
    yaw_diff,
)
from .temporal import (
    EVENT_DATASETS,
    event_window,
    events_around,
    events_in,
    evidence_ref,
    player_interval,
    round_of,
    round_window,
    state_at,
    tick_to_seconds,
    timeline,
)

__all__ = [
    "EVENT_DATASETS",
    "MAX_MATERIALIZED_ROWS",
    "Generation",
    "GenerationPool",
    "coverage",
    "displacement",
    "dist2d",
    "dist3d",
    "event_window",
    "events_around",
    "events_in",
    "evidence_ref",
    "live_identity_violations",
    "nearby",
    "pair_distance_over_time",
    "player_interval",
    "round_of",
    "round_window",
    "spatial",
    "speed",
    "state_at",
    "temporal",
    "tick_to_seconds",
    "time_within",
    "timeline",
    "yaw_diff",
]

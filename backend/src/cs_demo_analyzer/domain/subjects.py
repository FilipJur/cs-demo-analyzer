"""The analysis subject: configured SteamID64 and per-recording participation.

A SteamID64 is an exact decimal string everywhere in this application. It is
never routed through ``float`` (which cannot represent a 17-digit account
exactly) and it is never re-formatted: :func:`normalize_steam_id` returns the
same digits it was given, so the value survives a round trip through SQLite and
matches ``parsing.normalize``'s ``players.steam_id`` column byte for byte.

The canonical player id (``steam:<digits>``) is derived through
``domain.tables.player_key``, the same helper the parser uses to build
``player_id``, so a configured subject resolves to exactly the ids the recorded
tables carry.

``Participation`` deliberately distinguishes four states instead of collapsing
them into a boolean: the subject is in this recording (``present``), the
recording's evidence says the subject is not in it (``absent``), the recording
cannot say (``unresolved`` — a roster entry whose SteamID was not resolvable, or
a generation with no roster at all), or there is nothing to measure yet
(``not_ready``). Fields with no recorded value stay ``None``; nothing is
invented, and a missing health/position never counts as death or as zero.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .contracts import Model, utc_now
from .tables import player_key

#: Built-in subject when no explicit setting has been written.
DEFAULT_STEAM_ID = "76561198057213632"

#: SteamID64 = individual base + 32-bit account id; the leading digit is always 7
#: for individual accounts, which is what makes every SteamID64 17 digits long.
STEAM_ID64_INDIVIDUAL_BASE = 76561197960265728
STEAM_ID64_INDIVIDUAL_LIMIT = STEAM_ID64_INDIVIDUAL_BASE + 2**32 - 1

ParticipationStatus = Literal["present", "absent", "unresolved", "not_ready"]


def normalize_steam_id(value: str) -> str:
    """Validate an exact 17-digit positive SteamID64 individual account.

    Returns the input unchanged (same characters, no int/float round trip) or
    raises :class:`ValueError` with a message fit for an API client.
    """
    if not isinstance(value, str):
        raise ValueError(f"SteamID64 must be a string, got {type(value).__name__}")
    if len(value) != 17 or not value.isascii() or not value.isdigit():
        raise ValueError("SteamID64 must be exactly 17 decimal digits")
    if not STEAM_ID64_INDIVIDUAL_BASE <= int(value) <= STEAM_ID64_INDIVIDUAL_LIMIT:
        raise ValueError(
            f"SteamID64 {value} is outside the individual account range "
            f"{STEAM_ID64_INDIVIDUAL_BASE}..{STEAM_ID64_INDIVIDUAL_LIMIT}"
        )
    return value


def canonical_player_id(steam_id: str) -> str:
    """``steam:<digits>`` for a validated SteamID64, exactly as the parser writes it."""
    key = player_key(normalize_steam_id(steam_id))
    assert key is not None  # normalize_steam_id rejects 0 and non-digits
    return key


class SubjectConfig(Model):
    """The configured analysis subject.

    ``player_id`` is the canonical id for ``steam_id``; it is ``None`` only when
    the persisted value is not a valid SteamID64 (a corrupted setting row), which
    downstream participation reports as ``unresolved`` rather than silently
    substituting another player.
    """

    steam_id: str
    player_id: str | None
    updated_at: str = Field(default_factory=utc_now)


class ParticipationMeasurements(Model):
    """Recorded measurements for one subject in one generation.

    Every count is derived from the generation's own tables with bounded
    aggregations; ``None`` means "not computable from this recording" and is
    never substituted by ``0``. ``health_unknown_rows`` counts rows whose health
    is null — they are neither alive nor dead.
    """

    tick_rate_hz: float
    # rounds and ticks; "inside a round" is the active window
    # [freeze_end_tick or start_tick, end_tick] (Phase 1 temporal semantics)
    rounds_total: int
    rounds_with_subject: int  # active window holds at least one subject row
    rounds_alive: int  # active window holds at least one subject row with health > 0
    first_tick: int | None  # raw subject ticks, never clipped to a round window
    last_tick: int | None
    rows_outside_rounds: int  # subject rows outside every active round window
    # identity and life
    state_rows: int
    alive_rows: int
    dead_rows: int
    health_unknown_rows: int
    null_identity_rows: int
    # positional and angular completeness
    position_rows: int
    position_missing: int
    angle_anomalies: int
    health_anomalies: int
    # events touching the subject (attacker/victim/assister/actor)
    kills: int
    deaths: int
    assists: int
    damages_dealt: int
    damage_taken: int
    shots: int
    bomb_events: int
    events_outside_rounds: int  # subject-involved events outside every active round window
    replay_available: bool


class Participation(Model):
    """What one recording says about the subject (or the explicit override)."""

    demo_id: str
    generation_id: str | None
    steam_id: str
    player_id: str | None
    player_id_source: Literal["config", "override"]
    status: ParticipationStatus
    in_roster: bool
    map_name: str | None = None
    demo_client_version: str | None = None
    recording_kind: str | None = None
    quality: str | None = None
    limitations: list[str] = Field(default_factory=list)
    measurements: ParticipationMeasurements | None = None

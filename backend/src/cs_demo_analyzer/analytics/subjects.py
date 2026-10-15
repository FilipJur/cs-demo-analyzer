"""Subject participation: which recordings contain the configured player.

Everything here is a *measurement* of the recording, taken from the pinned
generation's own tables:

* the subject is resolved only through recorded identity (``players.player_id``
  / ``players.steam_id``), never by position, name or ordering;
* state rows are counted with bounded polars aggregations against a
  ``player_id``-equality predicate, so no dense frame is materialized and no
  unbounded Python state accumulates;
* a null health is neither alive nor dead, a null position is not zeroed, and a
  generation with no complete round windows reports ``0`` outside-round rows
  together with an explicit limitation rather than claiming every row is
  outside every round;
* "inside a round" means Phase 1's *active* window — ``[freeze_end_tick or
  start_tick, end_tick]`` via ``temporal._round_begin``, the window
  ``temporal.round_of``/``round_window`` and ``identity.coverage`` use — so
  freeze/buy time, warmup and intermissions count as outside even though they
  are inside ``[start_tick, end_tick]``. ``first_tick``/``last_tick`` stay raw
  subject ticks, independent of any window.

Status vocabulary (see :class:`domain.subjects.Participation`):

``present``     recorded evidence says the subject was in this recording: state
                rows carrying the selected canonical id, and/or a roster record
                that carries a resolvable SteamID for it;
``absent``      the roster is complete and resolvable, the selection is a
                resolvable Steam account, and neither holds the selection — the
                recording is not about them;
``unresolved``  the recording cannot say: the configured SteamID64 is invalid,
                the generation has no roster at all, the roster itself has
                entries whose SteamID was not resolvable, or the selection is
                not a resolvable Steam account (an ``unresolved:roster:*``
                record reference, or an id that is not ``steam:<digits>``).
                Absence is only ever asserted for a resolvable account over a
                complete resolvable roster;
``not_ready``   no published generation is readable yet (pending or missing),
                so there is nothing to measure.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from ..domain.contracts import AppError, utc_now
from ..domain.subjects import (
    DEFAULT_STEAM_ID,
    Participation,
    ParticipationMeasurements,
    SubjectConfig,
    canonical_player_id,
    normalize_steam_id,
)
from .access import Generation, GenerationPool
from .identity import coverage
from .temporal import _round_begin

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..storage.catalog import Catalog

STAGE = "analytics"

#: One key in ``app_settings``; the row is seeded by migration 0002.
SETTING_KEY = "subject.steam_id"

#: Upper bound accepted by :meth:`SubjectService.list_participation`.
MAX_LIST_LIMIT = 500

#: Tables a replay/trajectory read needs; presence is recorded, not assumed.
_REPLAY_TABLES = ("players", "rounds", "player_state")

_FAILED_OPEN_CODES = frozenset({"NOT_READY", "GENERATION_UNAVAILABLE", "ARTIFACT_INVALID"})


def _count(condition: pl.Expr) -> pl.Expr:
    """Count true values: a null comparison is neither true nor false, so it never counts."""
    return condition.cast(pl.Int64).sum()


def _is_resolved_account(player_id: str | None) -> bool:
    """True only for a canonical resolved account id, ``steam:<17-digit SteamID64>``.

    ``unresolved:roster:*`` references and any other id scheme are not Steam
    accounts, so their absence from a recording cannot be asserted.
    """
    if not player_id or not player_id.startswith("steam:"):
        return False
    try:
        normalize_steam_id(player_id.split(":", 1)[1])
    except ValueError:
        return False
    return True


def _round_windows(rounds: pl.DataFrame) -> tuple[list[tuple[int, int]], int]:
    """Active ``(begin, end)`` windows plus the count of rounds without usable timing.

    The window is Phase 1's *active* round window, ``[freeze_end_tick or
    start_tick, end_tick]`` (``temporal._round_begin``, the same window
    ``temporal.round_of``/``round_window`` and ``identity.coverage`` use), so
    rows from the freeze/buy period, warmup and intermissions are outside every
    window. A round whose timing is incomplete (no ``freeze_end_tick`` *and* no
    ``start_tick``, or no ``end_tick``) contributes no window instead of a
    fabricated one.
    """
    windows: list[tuple[int, int]] = []
    incomplete = 0
    for row in rounds.iter_rows(named=True):
        begin = _round_begin(row)
        end = row["end_tick"]
        if begin is None or end is None:
            incomplete += 1
            continue
        windows.append((int(begin), int(end)))
    return windows, incomplete


def _inside_rounds(windows: list[tuple[int, int]]) -> pl.Expr:
    expression = pl.lit(False)
    for begin, end in windows:
        expression = expression | ((pl.col("tick") >= begin) & (pl.col("tick") <= end))
    return expression


class SubjectService:
    """Configured analysis subject plus per-recording participation.

    ``catalog`` persists one singleton setting row (``app_settings``) and lists
    recordings; ``pool`` opens generation-pinned analytics handles. Both are
    owned by the runtime and shared with the other analytics services.
    """

    def __init__(self, catalog: Catalog, pool: GenerationPool) -> None:
        self.catalog = catalog
        self.pool = pool

    # -- the configured subject -------------------------------------------
    def get(self) -> SubjectConfig:
        """The effective subject: the persisted SteamID64 or the built-in default.

        A persisted value that is not a valid SteamID64 is returned as-is with
        ``player_id=None`` (participation then reports ``unresolved``); it is
        never silently replaced by the default.
        """
        rows = self.catalog._query(
            "SELECT value, updated_at FROM app_settings WHERE key = ?", (SETTING_KEY,)
        )
        if not rows:
            # Only reachable when the seeded row was deleted by hand; the built-in
            # default is the effective setting either way.
            return SubjectConfig(
                steam_id=DEFAULT_STEAM_ID,
                player_id=canonical_player_id(DEFAULT_STEAM_ID),
                updated_at=utc_now(),
            )
        stored, updated_at = rows[0]["value"], rows[0]["updated_at"]
        try:
            player_id: str | None = canonical_player_id(stored)
        except ValueError:
            player_id = None
        return SubjectConfig(steam_id=stored, player_id=player_id, updated_at=updated_at)

    def set(self, steam_id: str) -> SubjectConfig:
        """Persist an exact 17-digit SteamID64 and return the effective config."""
        try:
            canonical = normalize_steam_id(steam_id)
        except ValueError as exc:
            raise AppError("INVALID_ARGUMENT", str(exc), STAGE) from exc
        now = utc_now()
        with self.catalog._tx() as conn:
            conn.execute(
                """
                INSERT INTO app_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (SETTING_KEY, canonical, now),
            )
        return SubjectConfig(steam_id=canonical, player_id=canonical_player_id(canonical), updated_at=now)

    # -- participation -----------------------------------------------------
    def participation(
        self,
        demo_id: str,
        generation_id: str | None = None,
        player_id: str | None = None,
    ) -> Participation:
        """What ``demo_id`` says about the subject (or the explicit override).

        ``player_id`` overrides the configured subject for this call only; on an
        absent result the override is reported absent — the configured subject
        is never substituted back in. An unknown ``demo_id`` raises
        ``NOT_FOUND``; a known demo without a readable generation returns
        ``status="not_ready"`` instead of raising.

        Presence and absence are properties of the *selected Steam account*: a
        roster record whose SteamID could not be resolved (``unresolved:roster:*``)
        is reported ``in_roster=True`` with its own reference as ``player_id``, but
        never makes the selection ``present``, and a selection that is not a
        resolvable account id at all is ``unresolved`` rather than ``absent`` —
        no identity is guessed and no row is joined by position or name.
        """
        if player_id is not None and not isinstance(player_id, str):
            raise AppError("INVALID_ARGUMENT", "player_id must be a string", STAGE)
        config = self.get()
        source = "override" if player_id is not None else "config"
        selected = player_id if player_id is not None else config.player_id

        try:
            gen = self.pool.open(demo_id, generation_id)
        except AppError as exc:
            if exc.code not in _FAILED_OPEN_CODES:
                raise
            demo = self.catalog.get_demo(demo_id)
            return Participation(
                demo_id=demo_id,
                generation_id=generation_id,
                steam_id=config.steam_id,
                player_id=selected,
                player_id_source=source,
                status="not_ready",
                in_roster=False,
                map_name=demo.map_name if demo is not None else None,
                quality=demo.quality if demo is not None else None,
                limitations=[f"{exc.code}: {exc.message}"],
            )

        limitations: list[str] = []
        roster = gen.players
        matched = (
            roster.filter((pl.col("player_id") == selected) | (pl.col("steam_id") == selected))
            if selected is not None
            else roster.head(0)
        )
        in_roster = matched.height > 0
        if in_roster:
            measured_id: str | None = str(matched.item(0, "player_id"))
            # A roster record whose SteamID could not be resolved is not an account:
            # it must never make the selected Steam account look present.
            unresolved_record = matched.item(0, "steam_id") is None or measured_id.startswith("unresolved:")
        else:
            measured_id = self._canonicalize(selected)
            unresolved_record = False

        measurements = self._measure(gen, measured_id, limitations)
        roster_unresolved = int(roster.filter(pl.col("steam_id").is_null()).height)
        if roster_unresolved:
            limitations.append(f"{roster_unresolved} roster entries have no resolvable SteamID")
        if selected is None:
            limitations.append(
                f"configured subject {config.steam_id!r} is not a valid SteamID64; "
                "no player could be measured"
            )
        if gen.manifest.recording_kind == "pov":
            limitations.append("POV recording: the roster describes one recorded perspective")

        if unresolved_record:
            limitations.append(
                f"selected player_id {measured_id!r} is a roster record without a resolvable SteamID; "
                "the selected Steam account cannot be established as present and no identity was guessed"
            )
            status = "unresolved"
        elif measurements.state_rows > 0 or in_roster:
            status = "present"
        elif selected is None:
            status = "unresolved"
        elif roster.height == 0:
            status = "unresolved"
        elif not _is_resolved_account(measured_id):
            limitations.append(
                f"selection {measured_id!r} is not a resolvable SteamID64 account id; "
                "its absence cannot be asserted"
            )
            status = "unresolved"
        elif roster_unresolved > 0:
            status = "unresolved"
        else:
            status = "absent"

        return Participation(
            demo_id=demo_id,
            generation_id=gen.generation_id,
            steam_id=config.steam_id,
            player_id=measured_id if measured_id is not None else selected,
            player_id_source=source,
            status=status,
            in_roster=in_roster,
            map_name=gen.manifest.map_name,
            demo_client_version=gen.manifest.demo_client_version,
            recording_kind=gen.manifest.recording_kind,
            quality=gen.manifest.quality,
            limitations=limitations,
            measurements=measurements,
        )

    def list_participation(self, limit: int = 100, offset: int = 0) -> list[Participation]:
        """Participation for the most recent ``limit`` recordings, in catalog order."""
        if not 1 <= limit <= MAX_LIST_LIMIT:
            raise AppError("INVALID_ARGUMENT", f"limit must be in 1..{MAX_LIST_LIMIT}, got {limit}", STAGE)
        if offset < 0:
            raise AppError("INVALID_ARGUMENT", f"offset must be >= 0, got {offset}", STAGE)
        return [
            self.participation(demo.demo_id)
            for demo in self.catalog.list_demos(limit=limit, offset=offset)
        ]

    # -- measurements ------------------------------------------------------
    @staticmethod
    def _canonicalize(value: str | None) -> str | None:
        """A bare SteamID64 override resolves to the canonical ``steam:<digits>`` id."""
        if value is None:
            return None
        try:
            return canonical_player_id(value)
        except ValueError:
            return value

    def _measure(
        self, gen: Generation, measured_id: str | None, limitations: list[str]
    ) -> ParticipationMeasurements:
        windows, incomplete_rounds = _round_windows(gen.rounds)
        if incomplete_rounds:
            limitations.append(f"{incomplete_rounds} rounds have no complete tick window")

        def equals(column: str) -> pl.Expr:
            return pl.col(column) == measured_id if measured_id is not None else pl.lit(False)

        health = pl.col("health")
        position_complete = pl.col("x").is_not_null() & pl.col("y").is_not_null() & pl.col("z").is_not_null()
        pitch_out_of_range = pl.col("pitch").is_not_null() & ((pl.col("pitch") < -90) | (pl.col("pitch") > 90))
        angle_gap = position_complete & (pl.col("yaw").is_null() | pl.col("pitch").is_null())
        health_out_of_range = health.is_not_null() & ((health < 0) | (health > 100))

        if windows:
            outside = ~_inside_rounds(windows)
            window_stats = [
                expression
                for index, (begin, end) in enumerate(windows)
                for expression in (
                    ((pl.col("tick") >= begin) & (pl.col("tick") <= end)).any().alias(f"in{index}"),
                    (((pl.col("tick") >= begin) & (pl.col("tick") <= end)) & (health > 0))
                    .any()
                    .alias(f"alive{index}"),
                )
            ]
        else:
            outside = pl.lit(False)
            window_stats = []
            limitations.append(
                "no complete round windows (freeze_end_tick or start_tick .. end_tick): "
                "rows_outside_rounds and events_outside_rounds were not computed"
            )

        state = self.pool.scan(gen, "player_state", predicate=equals("player_id")).select(
            [
                pl.len().alias("state_rows"),
                _count(health > 0).alias("alive_rows"),
                _count(health == 0).alias("dead_rows"),
                _count(health.is_null()).alias("health_unknown_rows"),
                pl.col("tick").min().alias("first_tick"),
                pl.col("tick").max().alias("last_tick"),
                _count(outside).alias("rows_outside_rounds"),
                _count(position_complete).alias("position_rows"),
                _count(~position_complete).alias("position_missing"),
                _count(pitch_out_of_range | angle_gap).alias("angle_anomalies"),
                _count(health_out_of_range).alias("health_anomalies"),
                *window_stats,
            ]
        ).collect().row(0, named=True)

        kills = self._event_counts(
            gen,
            "kills",
            {
                "kills": equals("attacker_id"),
                "deaths": equals("victim_id"),
                "assists": equals("assister_id"),
            },
            outside,
        )
        damages = self._event_counts(
            gen,
            "damages",
            {"damages_dealt": equals("attacker_id"), "damage_taken": equals("victim_id")},
            outside,
        )
        shots = self._event_counts(gen, "shots", {"shots": equals("player_id")}, outside)
        bomb = self._event_counts(gen, "bomb", {"bomb_events": equals("player_id")}, outside)

        return ParticipationMeasurements(
            tick_rate_hz=gen.tick_rate_hz,
            rounds_total=gen.rounds.height,
            rounds_with_subject=sum(bool(state[f"in{index}"]) for index in range(len(windows))),
            rounds_alive=sum(bool(state[f"alive{index}"]) for index in range(len(windows))),
            first_tick=state["first_tick"],
            last_tick=state["last_tick"],
            rows_outside_rounds=int(state["rows_outside_rounds"]),
            state_rows=int(state["state_rows"]),
            alive_rows=int(state["alive_rows"]),
            dead_rows=int(state["dead_rows"]),
            health_unknown_rows=int(state["health_unknown_rows"]),
            null_identity_rows=coverage(self.pool, gen).null_observations,
            position_rows=int(state["position_rows"]),
            position_missing=int(state["position_missing"]),
            angle_anomalies=int(state["angle_anomalies"]),
            health_anomalies=int(state["health_anomalies"]),
            kills=kills["kills"],
            deaths=kills["deaths"],
            assists=kills["assists"],
            damages_dealt=damages["damages_dealt"],
            damage_taken=damages["damage_taken"],
            shots=shots["shots"],
            bomb_events=bomb["bomb_events"],
            events_outside_rounds=(
                kills["outside"] + damages["outside"] + shots["outside"] + bomb["outside"]
            ),
            replay_available=all(table in gen.manifest.tables for table in _REPLAY_TABLES),
        )

    def _event_counts(
        self,
        gen: Generation,
        table: str,
        roles: dict[str, pl.Expr],
        outside: pl.Expr,
    ) -> dict[str, int]:
        """One bounded scan per event table: per-role counts plus rows outside every round."""
        matched = pl.lit(False)
        for expression in roles.values():
            matched = matched | expression
        frame = self.pool.scan(gen, table, predicate=matched)
        selection = [_count(expression).alias(name) for name, expression in roles.items()]
        selection.append(_count(matched & outside).alias("outside"))
        row = frame.select(selection).collect().row(0, named=True)
        return {name: int(value) for name, value in row.items()}


__all__ = ["MAX_LIST_LIMIT", "SETTING_KEY", "SubjectService"]

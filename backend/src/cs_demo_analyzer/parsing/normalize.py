"""Explicit Awpy-to-canonical mapping for profile ``foundation-v1``.

Only the listed :data:`~cs_demo_analyzer.domain.tables.SCHEMAS` columns of the
seven bounded tables are produced. No utility, economy or unknown upstream field
is normalized, and nothing is joined by player name, zero ID or position.

Identity rules (frozen contract):

* a positive Steam ID becomes ``steam:<exact decimal>`` (``player_id``) and its
  exact decimal string (``steam_id``); it is never routed through a float;
* null or zero Steam IDs never collapse into a shared account: unresolved
  ``player_state``/event references stay ``null`` while every unresolved roster
  record keeps its own ``unresolved:roster:<ordinal>`` key;
* unresolved observations keep a unique ``row_ordinal`` and are never inferred
  from a name or a stale position.

Sides use the canonical vocabulary ``t``/``ct``/``spectator``/``unknown``:
Awpy's ``terrorist``/``counter-terrorist`` map to ``t``/``ct``, ``spectator`` is
preserved and every other upstream value (``unassigned``, ``TEAM_NOT_FOUND``,
null) becomes ``unknown``. ``side`` is non-null in the canonical tables.

All work is vectorized Polars expressions; no per-row Python is used.
"""

from __future__ import annotations

from typing import Callable, Mapping

import polars as pl

from ..domain.contracts import AppError
from ..domain.tables import SCHEMAS

# Awpy emits all Steam ID columns as Polars UInt64, including empty/all-null
# columns. Anything that is not an integer risks float precision loss for
# 17-digit IDs, so it is rejected rather than silently coerced.
_INTEGER_DTYPES = frozenset(
    {pl.UInt64, pl.Int64, pl.UInt32, pl.Int32, pl.UInt16, pl.Int16, pl.UInt8, pl.Int8}
)
_NUMERIC_DTYPES = _INTEGER_DTYPES | {pl.Float32, pl.Float64}

_SIDE_T = ("terrorist", "t")
_SIDE_CT = ("counter-terrorist", "ct")

#: The five numeric fields that must be real numbers for a non-empty state table.
_CRITICAL_STATE_NUMERICS = ("x", "y", "z", "yaw", "pitch")

_STATE_NUMERICS = (
    "x",
    "y",
    "z",
    "yaw",
    "pitch",
    "velocity_x",
    "velocity_y",
    "velocity_z",
)


def _require_columns(raw: pl.DataFrame, table: str, columns: tuple[str, ...]) -> None:
    missing = [name for name in columns if name not in raw.columns]
    if missing:
        raise AppError(
            "PARSE_FAILED",
            f"awpy {table} dataset is missing columns {missing}; refusing to invent a partial schema",
            "parse",
            retryable=False,
        )


def _require_integer_id(raw: pl.DataFrame, table: str, column: str) -> None:
    dtype = raw.schema[column]
    if dtype not in _INTEGER_DTYPES:
        raise AppError(
            "PARSE_FAILED",
            f"awpy {table}.{column} is {dtype}, not an integer Steam ID; "
            "refusing to risk float precision loss",
            "parse",
            retryable=False,
        )


def _require_numeric(raw: pl.DataFrame, table: str, column: str) -> None:
    dtype = raw.schema[column]
    if dtype not in _NUMERIC_DTYPES:
        raise AppError(
            "PARSE_FAILED",
            f"awpy {table}.{column} is {dtype}, not numeric; refusing to treat "
            "all-null/string columns as coordinates or angles",
            "parse",
            retryable=False,
        )


def side_expr(column: str) -> pl.Expr:
    """Vectorized canonical side for a raw side/winner-side column."""
    lowered = pl.col(column).cast(pl.String, strict=False).str.to_lowercase()
    return (
        pl.when(lowered.is_in(list(_SIDE_T)))
        .then(pl.lit("t"))
        .when(lowered.is_in(list(_SIDE_CT)))
        .then(pl.lit("ct"))
        .when(lowered == "spectator")
        .then(pl.lit("spectator"))
        .otherwise(pl.lit("unknown"))
        .cast(pl.String)
    )


def player_ref(column: str) -> pl.Expr:
    """Vectorized ``player_key``: null/zero -> null, positive -> ``steam:<id>``.

    Mirrors :func:`cs_demo_analyzer.domain.tables.player_key` without a
    per-row Python call. Requires :func:`_require_integer_id` to have passed.
    """
    steam = pl.col(column).cast(pl.UInt64)
    return (
        pl.when(steam.is_null() | (steam == 0))
        .then(None)
        .otherwise(pl.concat_str([pl.lit("steam:"), steam.cast(pl.String)]))
        .cast(pl.String)
    )


def _empty(table: str) -> pl.DataFrame:
    return pl.DataFrame(schema=SCHEMAS[table])


def _cast(table: str, frame: pl.DataFrame) -> pl.DataFrame:
    return frame.cast(SCHEMAS[table])


def normalize_players(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Roster, including unresolvable records, keyed by roster-local ordinals."""
    if raw.height == 0:
        return _empty("players"), []
    _require_columns(raw, "players", ("steamid", "name", "side"))
    _require_integer_id(raw, "players", "steamid")
    steam = pl.col("steamid").cast(pl.UInt64)
    resolved = steam.is_not_null() & (steam != 0)
    frame = raw.with_row_index("_ordinal").select(
        pl.when(resolved)
        .then(pl.concat_str([pl.lit("steam:"), steam.cast(pl.String)]))
        .otherwise(
            pl.concat_str([pl.lit("unresolved:roster:"), pl.col("_ordinal").cast(pl.String)])
        )
        .alias("player_id"),
        pl.when(resolved).then(steam.cast(pl.String)).otherwise(None).alias("steam_id"),
        pl.col("name").cast(pl.String, strict=False).alias("name"),
        side_expr("side").alias("side"),
    )
    warnings: list[str] = []
    unresolved = frame.filter(pl.col("steam_id").is_null())["player_id"].to_list()
    if unresolved:
        warnings.append(
            "roster records without a resolvable SteamID were kept as distinct "
            f"observations: {', '.join(unresolved)}"
        )
    return _cast("players", frame), warnings


def normalize_rounds(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Recording-scoped round ordinals plus the preserved upstream round number."""
    if raw.height == 0:
        return _empty("rounds"), []
    _require_columns(
        raw,
        "rounds",
        (
            "round_num",
            "start_tick",
            "freeze_end_tick",
            "end_tick",
            "official_end_tick",
            "winner_side",
            "reason",
        ),
    )
    frame = raw.with_row_index("_ordinal").select(
        (pl.col("_ordinal") + 1).cast(pl.Int32).alias("round_id"),
        pl.col("round_num").cast(pl.Int32).alias("source_round_num"),
        pl.col("start_tick").cast(pl.Int64).alias("start_tick"),
        pl.col("freeze_end_tick").cast(pl.Int64).alias("freeze_end_tick"),
        pl.col("end_tick").cast(pl.Int64).alias("end_tick"),
        pl.col("official_end_tick").cast(pl.Int64).alias("official_end_tick"),
        side_expr("winner_side").alias("winner_side"),
        pl.col("reason").cast(pl.Int32).alias("reason_code"),
    )
    return _cast("rounds", frame), []


def normalize_player_state(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Full-rate typed player state; null identities preserved with an ordinal."""
    if raw.height == 0:
        return _empty("player_state"), []
    _require_columns(
        raw,
        "player_state",
        (
            "tick",
            "steamid",
            "health",
            "armor",
            "money",
            "side",
            "active_weapon",
            "has_bomb",
            "is_crouched",
            "is_scoped",
            "is_reloading",
            *_STATE_NUMERICS,
        ),
    )
    _require_integer_id(raw, "player_state", "steamid")
    for column in _STATE_NUMERICS:
        _require_numeric(raw, "player_state", column)

    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        player_ref("steamid").alias("player_id"),
        pl.col("x").cast(pl.Float32).alias("x"),
        pl.col("y").cast(pl.Float32).alias("y"),
        pl.col("z").cast(pl.Float32).alias("z"),
        pl.col("yaw").cast(pl.Float32).alias("yaw"),
        pl.col("pitch").cast(pl.Float32).alias("pitch"),
        pl.col("velocity_x").cast(pl.Float32).alias("velocity_x"),
        pl.col("velocity_y").cast(pl.Float32).alias("velocity_y"),
        pl.col("velocity_z").cast(pl.Float32).alias("velocity_z"),
        pl.col("health").cast(pl.Int32).alias("health"),
        pl.col("armor").cast(pl.Int32).alias("armor"),
        pl.col("money").cast(pl.Int32).alias("money"),
        side_expr("side").alias("side"),
        pl.col("active_weapon").cast(pl.String, strict=False).alias("active_weapon"),
        pl.col("has_bomb").cast(pl.Boolean).alias("has_bomb"),
        pl.col("is_crouched").cast(pl.Boolean).alias("is_crouched"),
        pl.col("is_scoped").cast(pl.Boolean).alias("is_scoped"),
        pl.col("is_reloading").cast(pl.Boolean).alias("is_reloading"),
    )

    warnings: list[str] = []
    non_finite = _non_finite_mask(frame, _CRITICAL_STATE_NUMERICS)
    if non_finite is not None:
        count = int(frame.select(non_finite.sum()).item())
        if count:
            frame = frame.with_columns(
                pl.when(pl.col(column).is_finite())
                .then(pl.col(column))
                .otherwise(None)
                .alias(column)
                for column in _STATE_NUMERICS
            )
            warnings.append(
                f"{count} non-finite player_state coordinate/angle/velocity values "
                "were replaced with null"
            )

    finite_xy = int(
        frame.select(
            (pl.col("x").is_finite().fill_null(False) & pl.col("y").is_finite().fill_null(False)).sum()
        ).item()
    )
    if finite_xy == 0:
        raise AppError(
            "PARSE_FAILED",
            "player_state has no finite X/Y sample; angles/positions are missing",
            "parse",
            retryable=False,
        )
    unresolved = int(frame.select(pl.col("player_id").is_null().sum()).item())
    if unresolved:
        warnings.append(
            f"{unresolved} player_state observations have no resolvable SteamID; "
            "their player_id stays null and row_ordinal keeps them distinct"
        )
    return _cast("player_state", frame), warnings


def _non_finite_mask(frame: pl.DataFrame, columns: tuple[str, ...]) -> pl.Expr | None:
    mask: pl.Expr | None = None
    for column in columns:
        current = pl.col(column).is_finite().fill_null(True).not_()
        mask = current if mask is None else (mask | current)
    return mask


def normalize_kills(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    if raw.height == 0:
        return _empty("kills"), []
    _require_columns(
        raw,
        "kills",
        (
            "tick",
            "attacker_steamid",
            "victim_steamid",
            "assister_steamid",
            "weapon",
            "headshot",
            "attacker_entity_id",
            "attacker_entity_serial",
            "victim_entity_id",
            "victim_entity_serial",
        ),
    )
    for column in ("attacker_steamid", "victim_steamid", "assister_steamid"):
        _require_integer_id(raw, "kills", column)
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        player_ref("attacker_steamid").alias("attacker_id"),
        player_ref("victim_steamid").alias("victim_id"),
        player_ref("assister_steamid").alias("assister_id"),
        pl.col("weapon").cast(pl.String, strict=False).alias("weapon"),
        pl.col("headshot").cast(pl.Boolean).alias("headshot"),
        pl.col("attacker_entity_id").cast(pl.Int64).alias("attacker_entity_id"),
        pl.col("attacker_entity_serial").cast(pl.Int64).alias("attacker_entity_serial"),
        pl.col("victim_entity_id").cast(pl.Int64).alias("victim_entity_id"),
        pl.col("victim_entity_serial").cast(pl.Int64).alias("victim_entity_serial"),
    )
    return _cast("kills", frame), []


def normalize_damages(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    if raw.height == 0:
        return _empty("damages"), []
    _require_columns(
        raw,
        "damages",
        ("tick", "attacker_steamid", "victim_steamid", "dmg_health", "dmg_armor", "weapon"),
    )
    for column in ("attacker_steamid", "victim_steamid"):
        _require_integer_id(raw, "damages", column)
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        player_ref("attacker_steamid").alias("attacker_id"),
        player_ref("victim_steamid").alias("victim_id"),
        pl.col("dmg_health").cast(pl.Int32).alias("damage_health"),
        pl.col("dmg_armor").cast(pl.Int32).alias("damage_armor"),
        pl.col("weapon").cast(pl.String, strict=False).alias("weapon"),
    )
    return _cast("damages", frame), []


def normalize_shots(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    if raw.height == 0:
        return _empty("shots"), []
    _require_columns(
        raw, "shots", ("tick", "steamid", "weapon", "x", "y", "z", "yaw", "pitch")
    )
    _require_integer_id(raw, "shots", "steamid")
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        player_ref("steamid").alias("player_id"),
        pl.col("weapon").cast(pl.String, strict=False).alias("weapon"),
        pl.col("x").cast(pl.Float32).alias("x"),
        pl.col("y").cast(pl.Float32).alias("y"),
        pl.col("z").cast(pl.Float32).alias("z"),
        pl.col("yaw").cast(pl.Float32).alias("yaw"),
        pl.col("pitch").cast(pl.Float32).alias("pitch"),
    )
    return _cast("shots", frame), []


def normalize_bomb(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    if raw.height == 0:
        return _empty("bomb"), []
    _require_columns(raw, "bomb", ("tick", "steamid", "event", "bombsite", "x", "y", "z"))
    _require_integer_id(raw, "bomb", "steamid")
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        player_ref("steamid").alias("player_id"),
        pl.col("event").cast(pl.String, strict=False).alias("action"),
        pl.col("bombsite").cast(pl.String, strict=False).alias("bombsite"),
        pl.col("x").cast(pl.Float32).alias("x"),
        pl.col("y").cast(pl.Float32).alias("y"),
        pl.col("z").cast(pl.Float32).alias("z"),
    )
    return _cast("bomb", frame), []


#: One normalizer per canonical table, keyed exactly as in ``SCHEMAS``.
TABLE_NORMALIZERS: dict[str, Callable[[pl.DataFrame], tuple[pl.DataFrame, list[str]]]] = {
    "players": normalize_players,
    "rounds": normalize_rounds,
    "player_state": normalize_player_state,
    "kills": normalize_kills,
    "damages": normalize_damages,
    "shots": normalize_shots,
    "bomb": normalize_bomb,
}


def normalize_tables(
    raw: Mapping[str, pl.DataFrame],
) -> tuple[dict[str, pl.DataFrame], list[str]]:
    """Normalize every canonical table from a raw awpy frame mapping."""
    missing = [table for table in SCHEMAS if table not in raw]
    if missing:
        raise AppError(
            "PARSE_FAILED", f"awpy did not produce datasets {missing}", "parse", retryable=False
        )
    frames: dict[str, pl.DataFrame] = {}
    warnings: list[str] = []
    for table in SCHEMAS:
        frame, table_warnings = TABLE_NORMALIZERS[table](raw[table])
        frames[table] = frame
        warnings.extend(table_warnings)
    return frames, warnings

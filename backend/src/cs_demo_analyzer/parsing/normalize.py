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

Profile ``reconstruction-v1`` reuses these exact rules and the same seven tables
(``kills``/``damages``/``shots``/``bomb`` gain further recorded upstream columns,
which are pure additions to identical rows) and adds typed utility, economy and
lifecycle tables. Its extra columns are declared in
:data:`~cs_demo_analyzer.domain.tables.RECONSTRUCTION_SCHEMAS`; nothing is
interpolated and no upstream estimate is promoted to a recorded fact.

All work is vectorized Polars expressions; no per-row Python is used.
"""

from __future__ import annotations

from typing import Callable, Mapping

import polars as pl

from ..domain.contracts import PROFILE_NAME, RECONSTRUCTION_PROFILE_NAME, AppError
from ..domain.tables import RECONSTRUCTION_SCHEMAS, SCHEMAS, schema_for_profile

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


def _empty(schema: dict[str, pl.DataType]) -> pl.DataFrame:
    return pl.DataFrame(schema=schema)


def _cast(frame: pl.DataFrame, schema: dict[str, pl.DataType]) -> pl.DataFrame:
    return frame.cast(schema)


def normalize_players(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Roster, including unresolvable records, keyed by roster-local ordinals."""
    if raw.height == 0:
        return _empty(SCHEMAS["players"]), []
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
    return _cast(frame, SCHEMAS["players"]), warnings


def normalize_rounds(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Recording-scoped round ordinals plus the preserved upstream round number."""
    if raw.height == 0:
        return _empty(SCHEMAS["rounds"]), []
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
    return _cast(frame, SCHEMAS["rounds"]), []


def normalize_player_state(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Full-rate typed player state; null identities preserved with an ordinal."""
    if raw.height == 0:
        return _empty(SCHEMAS["player_state"]), []
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
    return _cast(frame, SCHEMAS["player_state"]), warnings


def _non_finite_mask(frame: pl.DataFrame, columns: tuple[str, ...]) -> pl.Expr | None:
    mask: pl.Expr | None = None
    for column in columns:
        current = pl.col(column).is_finite().fill_null(True).not_()
        mask = current if mask is None else (mask | current)
    return mask


def normalize_kills(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    return _kills(raw, SCHEMAS["kills"], extended=False)


def normalize_damages(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    return _damages(raw, SCHEMAS["damages"], extended=False)


def normalize_shots(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    return _shots(raw, SCHEMAS["shots"], extended=False)


def normalize_bomb(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    return _bomb(raw, SCHEMAS["bomb"], extended=False)


_KILLS_REQUIRED = (
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
)
#: Recorded upstream columns only ``reconstruction-v1`` normalizes. Upstream
#: *derived* classifications (``is_trade``/``victim_traded``, a computed 5.25 s
#: trade window) are intentionally not normalized: they are not recorded facts.
_KILLS_EXTENDED_REQUIRED = (
    "assister_entity_id",
    "assister_entity_serial",
    "attacker_x",
    "attacker_y",
    "attacker_z",
    "victim_x",
    "victim_y",
    "victim_z",
    "assister_x",
    "assister_y",
    "assister_z",
    "hitgroup",
    "hitgroup_name",
    "assist_flash",
    "noscope",
    "penetrated",
    "dominated",
    "revenge",
    "thrusmoke",
)


def _kills(
    raw: pl.DataFrame, schema: dict[str, pl.DataType], *, extended: bool
) -> tuple[pl.DataFrame, list[str]]:
    """``player_death`` rows; ``extended`` adds the recorded position/hitgroup fields."""
    if raw.height == 0:
        return _empty(schema), []
    _require_columns(raw, "kills", _KILLS_REQUIRED + (_KILLS_EXTENDED_REQUIRED if extended else ()))
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
        *(
            [
                pl.col("assister_entity_id").cast(pl.Int64).alias("assister_entity_id"),
                pl.col("assister_entity_serial").cast(pl.Int64).alias("assister_entity_serial"),
                pl.col("attacker_x").cast(pl.Float32).alias("attacker_x"),
                pl.col("attacker_y").cast(pl.Float32).alias("attacker_y"),
                pl.col("attacker_z").cast(pl.Float32).alias("attacker_z"),
                pl.col("victim_x").cast(pl.Float32).alias("victim_x"),
                pl.col("victim_y").cast(pl.Float32).alias("victim_y"),
                pl.col("victim_z").cast(pl.Float32).alias("victim_z"),
                pl.col("assister_x").cast(pl.Float32).alias("assister_x"),
                pl.col("assister_y").cast(pl.Float32).alias("assister_y"),
                pl.col("assister_z").cast(pl.Float32).alias("assister_z"),
                pl.col("hitgroup").cast(pl.Int32).alias("hitgroup_code"),
                pl.col("hitgroup_name").cast(pl.String, strict=False).alias("hitgroup_name"),
                pl.col("assist_flash").cast(pl.Boolean).alias("assist_flash"),
                pl.col("noscope").cast(pl.Boolean).alias("noscope"),
                pl.col("thrusmoke").cast(pl.Boolean).alias("thrusmoke"),
                pl.col("penetrated").cast(pl.Int32).alias("penetrated"),
                pl.col("dominated").cast(pl.Int32).alias("dominated"),
                pl.col("revenge").cast(pl.Int32).alias("revenge"),
            ]
            if extended
            else []
        ),
    )
    return _cast(frame.select(list(schema)), schema), []


def _damages(
    raw: pl.DataFrame, schema: dict[str, pl.DataType], *, extended: bool
) -> tuple[pl.DataFrame, list[str]]:
    """``player_hurt`` rows.

    ``dmg_health``/``dmg_armor`` are the recorded damage values. Upstream
    ``health_pre``/``armor_pre``/``health_post``/``armor_post`` stay out of both
    profiles: they are upstream estimates, not recorded facts. ``extended`` adds
    the recorded positions and hitgroup of the same row.
    """
    if raw.height == 0:
        return _empty(schema), []
    required = ("tick", "attacker_steamid", "victim_steamid", "dmg_health", "dmg_armor", "weapon")
    if extended:
        required += (
            "attacker_x",
            "attacker_y",
            "attacker_z",
            "victim_x",
            "victim_y",
            "victim_z",
            "hitgroup",
            "hitgroup_name",
        )
    _require_columns(raw, "damages", required)
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
        *(
            [
                pl.col("attacker_x").cast(pl.Float32).alias("attacker_x"),
                pl.col("attacker_y").cast(pl.Float32).alias("attacker_y"),
                pl.col("attacker_z").cast(pl.Float32).alias("attacker_z"),
                pl.col("victim_x").cast(pl.Float32).alias("victim_x"),
                pl.col("victim_y").cast(pl.Float32).alias("victim_y"),
                pl.col("victim_z").cast(pl.Float32).alias("victim_z"),
                pl.col("hitgroup").cast(pl.Int32).alias("hitgroup_code"),
                pl.col("hitgroup_name").cast(pl.String, strict=False).alias("hitgroup_name"),
            ]
            if extended
            else []
        ),
    )
    return _cast(frame.select(list(schema)), schema), []


def _shots(
    raw: pl.DataFrame, schema: dict[str, pl.DataType], *, extended: bool
) -> tuple[pl.DataFrame, list[str]]:
    """``weapon_fire`` rows; ``extended`` adds the recorded weapon/entity fields."""
    if raw.height == 0:
        return _empty(schema), []
    required = ("tick", "steamid", "weapon", "x", "y", "z", "yaw", "pitch")
    if extended:
        required += ("entity_id", "entity_serial", "scoped", "inaccuracy", "num_bullets_remaining")
    _require_columns(raw, "shots", required)
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
        *(
            [
                pl.col("entity_id").cast(pl.Int64).alias("entity_id"),
                pl.col("entity_serial").cast(pl.Int64).alias("entity_serial"),
                pl.col("scoped").cast(pl.Boolean).alias("scoped"),
                pl.col("inaccuracy").cast(pl.Float32).alias("inaccuracy"),
                pl.col("num_bullets_remaining").cast(pl.Int32).alias("num_bullets_remaining"),
            ]
            if extended
            else []
        ),
    )
    return _cast(frame.select(list(schema)), schema), []


def _bomb(
    raw: pl.DataFrame, schema: dict[str, pl.DataType], *, extended: bool
) -> tuple[pl.DataFrame, list[str]]:
    """Bomb action rows; ``extended`` adds the recorded bomb entity identity."""
    if raw.height == 0:
        return _empty(schema), []
    required = ("tick", "steamid", "event", "bombsite", "x", "y", "z")
    if extended:
        required += ("entity_id", "entity_serial")
    _require_columns(raw, "bomb", required)
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
        *(
            [
                pl.col("entity_id").cast(pl.Int64).alias("entity_id"),
                pl.col("entity_serial").cast(pl.Int64).alias("entity_serial"),
            ]
            if extended
            else []
        ),
    )
    return _cast(frame.select(list(schema)), schema), []


# --------------------------------------------------------------------------- #
# reconstruction-v1 only tables
# --------------------------------------------------------------------------- #
_STATE_EXT_REQUIRED = (
    "tick",
    "steamid",
    "velocity",
    "has_helmet",
    "has_defuser",
    "primary_weapon",
    "secondary_weapon",
    "fire_grenades",
    "smoke_grenades",
    "he_grenades",
    "flashbangs",
    "decoy_grenades",
    "equipment_value",
    "equipment_value_round_start",
    "is_walking",
    "is_jumping",
    "is_in_bomb_zone",
    "is_silent_reloading",
    "is_defusing",
    "is_blinded",
    "flash_duration",
    "inventory",
)


def normalize_player_state_ext(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Recorded per-player fields beyond ``player_state`` from the same snapshot.

    Row-for-row aligned with ``player_state``: both are projected from the same
    full-rate snapshot frame with the same ``with_row_index`` order, so
    ``player_state_ext.row_ordinal`` addresses the identical observation.
    """
    schema = RECONSTRUCTION_SCHEMAS["player_state_ext"]
    if raw.height == 0:
        return _empty(schema), []
    _require_columns(raw, "player_state", _STATE_EXT_REQUIRED)
    _require_integer_id(raw, "player_state", "steamid")
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        player_ref("steamid").alias("player_id"),
        pl.col("velocity").cast(pl.Float32).alias("velocity"),
        pl.col("has_helmet").cast(pl.Boolean).alias("has_helmet"),
        pl.col("has_defuser").cast(pl.Boolean).alias("has_defuser"),
        pl.col("primary_weapon").cast(pl.String, strict=False).alias("primary_weapon"),
        pl.col("secondary_weapon").cast(pl.String, strict=False).alias("secondary_weapon"),
        pl.col("fire_grenades").cast(pl.Int32).alias("fire_grenades"),
        pl.col("smoke_grenades").cast(pl.Int32).alias("smoke_grenades"),
        pl.col("he_grenades").cast(pl.Int32).alias("he_grenades"),
        pl.col("flashbangs").cast(pl.Int32).alias("flashbangs"),
        pl.col("decoy_grenades").cast(pl.Int32).alias("decoy_grenades"),
        pl.col("equipment_value").cast(pl.Int32).alias("equipment_value"),
        pl.col("equipment_value_round_start").cast(pl.Int32).alias("equipment_value_round_start"),
        pl.col("is_walking").cast(pl.Boolean).alias("is_walking"),
        pl.col("is_jumping").cast(pl.Boolean).alias("is_jumping"),
        pl.col("is_in_bomb_zone").cast(pl.Boolean).alias("is_in_bomb_zone"),
        pl.col("is_silent_reloading").cast(pl.Boolean).alias("is_silent_reloading"),
        pl.col("is_defusing").cast(pl.Boolean).alias("is_defusing"),
        pl.col("is_blinded").cast(pl.Boolean).alias("is_blinded"),
        pl.col("flash_duration").cast(pl.Float32).alias("flash_duration"),
        pl.col("inventory").cast(pl.String, strict=False).alias("inventory"),
    )
    return _cast(frame, schema), []


def normalize_blinds(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """``player_blind`` rows: onset tick, attacker, victim and onset duration."""
    schema = RECONSTRUCTION_SCHEMAS["blinds"]
    if raw.height == 0:
        return _empty(schema), []
    _require_columns(
        raw,
        "blinds",
        (
            "tick",
            "attacker_steamid",
            "attacker_side",
            "attacker_entity_id",
            "attacker_entity_serial",
            "attacker_x",
            "attacker_y",
            "attacker_z",
            "victim_steamid",
            "victim_side",
            "victim_entity_id",
            "victim_entity_serial",
            "victim_x",
            "victim_y",
            "victim_z",
            "duration",
        ),
    )
    for column in ("attacker_steamid", "victim_steamid"):
        _require_integer_id(raw, "blinds", column)
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        player_ref("attacker_steamid").alias("attacker_id"),
        side_expr("attacker_side").alias("attacker_side"),
        pl.col("attacker_entity_id").cast(pl.Int64).alias("attacker_entity_id"),
        pl.col("attacker_entity_serial").cast(pl.Int64).alias("attacker_entity_serial"),
        pl.col("attacker_x").cast(pl.Float32).alias("attacker_x"),
        pl.col("attacker_y").cast(pl.Float32).alias("attacker_y"),
        pl.col("attacker_z").cast(pl.Float32).alias("attacker_z"),
        player_ref("victim_steamid").alias("victim_id"),
        side_expr("victim_side").alias("victim_side"),
        pl.col("victim_entity_id").cast(pl.Int64).alias("victim_entity_id"),
        pl.col("victim_entity_serial").cast(pl.Int64).alias("victim_entity_serial"),
        pl.col("victim_x").cast(pl.Float32).alias("victim_x"),
        pl.col("victim_y").cast(pl.Float32).alias("victim_y"),
        pl.col("victim_z").cast(pl.Float32).alias("victim_z"),
        pl.col("duration").cast(pl.Float32).alias("duration_seconds"),
    )
    return _cast(frame, schema), []


def _interval(
    table: str,
    raw: pl.DataFrame,
    max_tick: int | None,
    *,
    kind_column: str | None,
) -> tuple[pl.DataFrame, list[str]]:
    """Shared shape of the smoke-cloud and inferno-fire interval tables."""
    schema = RECONSTRUCTION_SCHEMAS[table]
    if raw.height == 0:
        return _empty(schema), []
    required = (
        "start_tick",
        "end_tick",
        "thrower_steamid",
        "thrower_side",
        "entity_id",
        "entity_serial",
        "x",
        "y",
        "z",
    )
    if kind_column is not None:
        required += (kind_column,)
    _require_columns(raw, table, required)
    _require_integer_id(raw, table, "thrower_steamid")
    still: pl.Expr = (
        pl.lit(None, dtype=pl.Boolean) if max_tick is None else (pl.col("end_tick") >= max_tick)
    )
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("start_tick").cast(pl.Int64).alias("start_tick"),
        pl.col("end_tick").cast(pl.Int64).alias("end_tick"),
        *(
            [pl.col(kind_column).cast(pl.String, strict=False).alias("kind")]
            if kind_column is not None
            else []
        ),
        pl.col("entity_id").cast(pl.Int64).alias("entity_id"),
        pl.col("entity_serial").cast(pl.Int64).alias("entity_serial"),
        player_ref("thrower_steamid").alias("owner_id"),
        side_expr("thrower_side").alias("owner_side"),
        pl.col("x").cast(pl.Float32).alias("x"),
        pl.col("y").cast(pl.Float32).alias("y"),
        pl.col("z").cast(pl.Float32).alias("z"),
        still.alias("still_active_at_end"),
    )
    frame = _cast(frame, schema)
    warnings: list[str] = []
    if frame.height and int(frame.select(pl.col("owner_id").is_null().sum()).item()) == frame.height:
        warnings.append(
            f"awpy {table} carries no thrower identity in this recording "
            "(all thrower_steamid are null); owner_id/owner_side stay null/unknown"
        )
    if max_tick is not None:
        still_active = int(frame.select(pl.col("still_active_at_end").fill_null(False).sum()).item())
        if still_active:
            warnings.append(
                f"{still_active} {table} intervals have no expiry before the recording ends; "
                "still_active_at_end marks them"
            )
    return frame, warnings


def normalize_smokes(raw: pl.DataFrame, max_tick: int | None) -> tuple[pl.DataFrame, list[str]]:
    """Deployed smoke clouds: one row per cloud with its upstream lifetime."""
    return _interval("smokes", raw, max_tick, kind_column=None)


def normalize_fires(raw: pl.DataFrame, max_tick: int | None) -> tuple[pl.DataFrame, list[str]]:
    """Burning infernos: one row per fire with its upstream lifetime and type."""
    return _interval("fires", raw, max_tick, kind_column="type")


def normalize_grenades(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Live thrown-grenade projectiles: one row per tick each projectile exists."""
    schema = RECONSTRUCTION_SCHEMAS["grenades"]
    if raw.height == 0:
        return _empty(schema), []
    _require_columns(
        raw,
        "grenades",
        ("tick", "thrower_steamid", "thrower_side", "type", "entity_id", "entity_serial", "x", "y", "z"),
    )
    _require_integer_id(raw, "grenades", "thrower_steamid")
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        pl.col("entity_id").cast(pl.Int64).alias("entity_id"),
        pl.col("entity_serial").cast(pl.Int64).alias("entity_serial"),
        pl.col("type").cast(pl.String, strict=False).alias("kind"),
        player_ref("thrower_steamid").alias("owner_id"),
        side_expr("thrower_side").alias("owner_side"),
        pl.col("x").cast(pl.Float32).alias("x"),
        pl.col("y").cast(pl.Float32).alias("y"),
        pl.col("z").cast(pl.Float32).alias("z"),
    )
    frame = _cast(frame, schema)
    warnings: list[str] = []
    if frame.height and int(frame.select(pl.col("owner_id").is_null().sum()).item()) == frame.height:
        warnings.append(
            "awpy grenades carries no thrower identity in this recording "
            "(all thrower_steamid are null); owner_id/owner_side stay null/unknown"
        )
    return frame, warnings


def normalize_item_events(raw: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Item transactions (purchase/pickup/drop) with resolved acting identity."""
    schema = RECONSTRUCTION_SCHEMAS["item_events"]
    if raw.height == 0:
        return _empty(schema), []
    _require_columns(
        raw,
        "item_events",
        (
            "tick",
            "entity_id",
            "entity_serial",
            "action",
            "steamid",
            "side",
            "item",
            "cost",
            "original_owner_steamid",
            "near_buy_zone",
            "x",
            "y",
            "z",
        ),
    )
    for column in ("steamid", "original_owner_steamid"):
        _require_integer_id(raw, "item_events", column)
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("tick").cast(pl.Int64).alias("tick"),
        pl.col("entity_id").cast(pl.Int64).alias("entity_id"),
        pl.col("entity_serial").cast(pl.Int64).alias("entity_serial"),
        pl.col("action").cast(pl.String, strict=False).alias("action"),
        player_ref("steamid").alias("player_id"),
        side_expr("side").alias("side"),
        pl.col("item").cast(pl.String, strict=False).alias("item"),
        pl.col("cost").cast(pl.Int32).alias("cost"),
        player_ref("original_owner_steamid").alias("original_owner_id"),
        pl.col("near_buy_zone").cast(pl.Boolean).alias("near_buy_zone"),
        pl.col("x").cast(pl.Float32).alias("x"),
        pl.col("y").cast(pl.Float32).alias("y"),
        pl.col("z").cast(pl.Float32).alias("z"),
    )
    return _cast(frame, schema), []


def normalize_round_economy(
    raw: pl.DataFrame, rounds: pl.DataFrame
) -> tuple[pl.DataFrame, list[str]]:
    """Team economy per round, joined to the canonical ``rounds.round_id``.

    ``round_id`` is the recording-scoped ordinal from the normalized rounds
    table, matched on the preserved upstream round number; an economy row whose
    round is not in that table keeps a null ``round_id`` instead of guessing one.
    """
    schema = RECONSTRUCTION_SCHEMAS["round_economy"]
    if raw.height == 0:
        return _empty(schema), []
    _require_columns(raw, "round_economy", ("round_num", "side", "equipment_value", "buy_type", "n_players"))
    mapping = rounds.select(
        pl.col("source_round_num").alias("round_num"), pl.col("round_id")
    )
    frame = raw.with_row_index("row_ordinal").select(
        pl.col("row_ordinal").cast(pl.Int64).alias("row_ordinal"),
        pl.col("round_num").cast(pl.Int32).alias("round_num"),
        side_expr("side").alias("side"),
        pl.col("equipment_value").cast(pl.Int32).alias("equipment_value"),
        pl.col("buy_type").cast(pl.String, strict=False).alias("buy_type"),
        pl.col("n_players").cast(pl.Int32).alias("n_players"),
    ).join(mapping, on="round_num", how="left")
    frame = _cast(frame.select(list(schema)), schema)
    warnings: list[str] = []
    unmatched = int(frame.select(pl.col("round_id").is_null().sum()).item())
    if unmatched:
        warnings.append(
            f"{unmatched} round_economy rows match no round in the normalized rounds table; "
            "their round_id stays null"
        )
    return frame, warnings


#: Recorded lifecycle events, keyed by the canonical ``kind`` they produce.
LIFECYCLE_KINDS: dict[str, str] = {
    "disconnect": "player_disconnect",
    "connect": "player_connect_full",
    "spawn": "player_spawn",
    "team_change": "player_team",
}

#: Engine team numbers awpy documents for the snapshot ``side`` feature
#: (``m_iTeamNum``: 2 = terrorist, 3 = counter-terrorist). Any other recorded
#: number becomes ``unknown`` rather than being guessed.
_TEAM_NUMBER_SIDES = ("2", "3")


def team_number_expr(column: str) -> pl.Expr:
    """Canonical side for a recorded ``m_iTeamNum`` value; anything else is unknown."""
    text = pl.col(column).cast(pl.String, strict=False).str.strip_chars()
    return (
        pl.when(
            (text == _TEAM_NUMBER_SIDES[0]) | (text == _TEAM_NUMBER_SIDES[1])
        )
        .then(pl.when(text == _TEAM_NUMBER_SIDES[0]).then(pl.lit("t")).otherwise(pl.lit("ct")))
        .otherwise(pl.lit("unknown"))
        .cast(pl.String)
    )


def player_ref_from_text(column: str) -> pl.Expr:
    """``player_key`` for a SteamID64 recorded as text; malformed text stays null.

    The value is read as an unsigned integer, so it never passes through a float
    and the canonical key matches :func:`player_key` exactly.
    """
    steam = pl.col(column).cast(pl.String, strict=False).cast(pl.UInt64, strict=False)
    return (
        pl.when(steam.is_null() | (steam == 0))
        .then(None)
        .otherwise(pl.concat_str([pl.lit("steam:"), steam.cast(pl.String)]))
        .cast(pl.String)
    )


def _bool_from_text(column: str) -> pl.Expr:
    """Upstream string flags ("true"/"false") as nullable Booleans."""
    text = pl.col(column).cast(pl.String, strict=False).str.to_lowercase()
    return (
        pl.when(text == "true")
        .then(pl.lit(True))
        .when(text == "false")
        .then(pl.lit(False))
        .otherwise(pl.lit(None, dtype=pl.Boolean))
        .cast(pl.Boolean)
    )


def normalize_player_lifecycle(
    events: Mapping[str, pl.DataFrame],
) -> tuple[pl.DataFrame, list[str]]:
    """Recorded connect/disconnect/spawn/team-change events as one typed table.

    Only the events present in the recording contribute rows, and the upstream
    order inside each kind is preserved. ``player_id`` is resolved only when the
    event itself records a SteamID64 (``player_disconnect`` carries ``xuid``);
    every other kind keeps a null ``player_id`` plus the recorded connection slot
    (``user_slot``) and pawn handle, so an unresolved participant is never joined
    by name. ``pawn_handle`` is the upstream decimal exactly as recorded and is
    not decoded into an entity index/serial pair.
    """
    schema = RECONSTRUCTION_SCHEMAS["player_lifecycle"]
    parts: list[pl.DataFrame] = []
    warnings: list[str] = []

    disconnect = events.get("player_disconnect")
    if disconnect is not None and disconnect.height:
        _require_columns(
            disconnect,
            "player_disconnect",
            ("tick", "userid", "reason", "xuid", "ever_fully_connected"),
        )
        part = disconnect.select(
            pl.col("tick").cast(pl.Int64).alias("tick"),
            pl.lit("disconnect", dtype=pl.String).alias("kind"),
            player_ref_from_text("xuid").alias("player_id"),
            pl.col("userid").cast(pl.String, strict=False).alias("user_slot"),
            pl.lit(None, dtype=pl.Int64).alias("pawn_handle"),
            pl.lit(None, dtype=pl.String).alias("team"),
            pl.lit(None, dtype=pl.String).alias("previous_team"),
            pl.lit(None, dtype=pl.Boolean).alias("is_bot"),
            pl.col("reason").cast(pl.Int32, strict=False).alias("reason_code"),
            _bool_from_text("ever_fully_connected").alias("ever_fully_connected"),
        )
        unresolved = int(
            part.select((pl.col("user_slot").is_not_null() & pl.col("player_id").is_null()).sum()).item()
        )
        if unresolved:
            warnings.append(
                f"{unresolved} player_disconnect events carry no resolvable SteamID64; "
                "their player_id stays null"
            )
        parts.append(part)

    connect = events.get("player_connect_full")
    if connect is not None and connect.height:
        _require_columns(connect, "player_connect_full", ("tick", "userid"))
        parts.append(
            connect.select(
                pl.col("tick").cast(pl.Int64).alias("tick"),
                pl.lit("connect", dtype=pl.String).alias("kind"),
                pl.lit(None, dtype=pl.String).alias("player_id"),
                pl.col("userid").cast(pl.String, strict=False).alias("user_slot"),
                pl.lit(None, dtype=pl.Int64).alias("pawn_handle"),
                pl.lit(None, dtype=pl.String).alias("team"),
                pl.lit(None, dtype=pl.String).alias("previous_team"),
                pl.lit(None, dtype=pl.Boolean).alias("is_bot"),
                pl.lit(None, dtype=pl.Int32).alias("reason_code"),
                pl.lit(None, dtype=pl.Boolean).alias("ever_fully_connected"),
            )
        )

    spawn = events.get("player_spawn")
    if spawn is not None and spawn.height:
        _require_columns(spawn, "player_spawn", ("tick", "userid", "userid_pawn"))
        parts.append(
            spawn.select(
                pl.col("tick").cast(pl.Int64).alias("tick"),
                pl.lit("spawn", dtype=pl.String).alias("kind"),
                pl.lit(None, dtype=pl.String).alias("player_id"),
                pl.col("userid").cast(pl.String, strict=False).alias("user_slot"),
                pl.col("userid_pawn").cast(pl.Int64, strict=False).alias("pawn_handle"),
                pl.lit(None, dtype=pl.String).alias("team"),
                pl.lit(None, dtype=pl.String).alias("previous_team"),
                pl.lit(None, dtype=pl.Boolean).alias("is_bot"),
                pl.lit(None, dtype=pl.Int32).alias("reason_code"),
                pl.lit(None, dtype=pl.Boolean).alias("ever_fully_connected"),
            )
        )

    team = events.get("player_team")
    if team is not None and team.height:
        _require_columns(
            team, "player_team", ("tick", "userid", "userid_pawn", "team", "oldteam", "isbot")
        )
        parts.append(
            team.select(
                pl.col("tick").cast(pl.Int64).alias("tick"),
                pl.lit("team_change", dtype=pl.String).alias("kind"),
                pl.lit(None, dtype=pl.String).alias("player_id"),
                pl.col("userid").cast(pl.String, strict=False).alias("user_slot"),
                pl.col("userid_pawn").cast(pl.Int64, strict=False).alias("pawn_handle"),
                team_number_expr("team").alias("team"),
                team_number_expr("oldteam").alias("previous_team"),
                _bool_from_text("isbot").alias("is_bot"),
                pl.lit(None, dtype=pl.Int32).alias("reason_code"),
                pl.lit(None, dtype=pl.Boolean).alias("ever_fully_connected"),
            )
        )

    if not parts:
        return _empty(schema), warnings

    frame = (
        pl.concat(parts, how="vertical")
        .sort(["tick", "kind"], maintain_order=True)
        .with_row_index("row_ordinal")
    )
    return _cast(frame.select(list(schema)), schema), warnings


def _player_state_max_tick(raw: Mapping[str, pl.DataFrame]) -> int | None:
    """Last recorded snapshot tick, used only to flag a lifecycle that never expired."""
    frame = raw.get("player_state")
    if frame is None or frame.height == 0:
        return None
    value = frame["tick"].max()
    return None if value is None else int(value)


#: Normalizer per canonical table, keyed by profile. Each takes the raw awpy
#: frame mapping (not just its own frame) and returns the canonical frame plus
#: the warnings that belong to it.
NormalizerFn = Callable[[Mapping[str, pl.DataFrame]], tuple[pl.DataFrame, list[str]]]

PROFILE_NORMALIZERS: dict[str, dict[str, NormalizerFn]] = {
    PROFILE_NAME: {
        "players": lambda raw: normalize_players(raw["players"]),
        "rounds": lambda raw: normalize_rounds(raw["rounds"]),
        "player_state": lambda raw: normalize_player_state(raw["player_state"]),
        "kills": lambda raw: normalize_kills(raw["kills"]),
        "damages": lambda raw: normalize_damages(raw["damages"]),
        "shots": lambda raw: normalize_shots(raw["shots"]),
        "bomb": lambda raw: normalize_bomb(raw["bomb"]),
    },
    RECONSTRUCTION_PROFILE_NAME: {
        "players": lambda raw: normalize_players(raw["players"]),
        "rounds": lambda raw: normalize_rounds(raw["rounds"]),
        "player_state": lambda raw: normalize_player_state(raw["player_state"]),
        "kills": lambda raw: _kills(raw["kills"], RECONSTRUCTION_SCHEMAS["kills"], extended=True),
        "damages": lambda raw: _damages(raw["damages"], RECONSTRUCTION_SCHEMAS["damages"], extended=True),
        "shots": lambda raw: _shots(raw["shots"], RECONSTRUCTION_SCHEMAS["shots"], extended=True),
        "bomb": lambda raw: _bomb(raw["bomb"], RECONSTRUCTION_SCHEMAS["bomb"], extended=True),
        "player_state_ext": lambda raw: normalize_player_state_ext(raw["player_state"]),
        "blinds": lambda raw: normalize_blinds(raw["blinds"]),
        "smokes": lambda raw: normalize_smokes(raw["smokes"], _player_state_max_tick(raw)),
        "fires": lambda raw: normalize_fires(raw["fires"], _player_state_max_tick(raw)),
        "grenades": lambda raw: normalize_grenades(raw["grenades"]),
        "item_events": lambda raw: normalize_item_events(raw["item_events"]),
        "round_economy": lambda raw: normalize_round_economy(
            raw["round_economy"], normalize_rounds(raw["rounds"])[0]
        ),
        "player_lifecycle": lambda raw: normalize_player_lifecycle(raw["lifecycle_events"]),
    },
}

#: Raw awpy frame keys each profile's normalizers read. Table names and raw
#: dataset names are not one-to-one: ``player_state`` feeds both the foundation
#: state table and ``player_state_ext``, and ``lifecycle_events`` (a mapping of
#: present recorded events) feeds ``player_lifecycle``.
PROFILE_RAW_KEYS: dict[str, tuple[str, ...]] = {
    PROFILE_NAME: tuple(SCHEMAS),
    RECONSTRUCTION_PROFILE_NAME: (
        "players",
        "rounds",
        "player_state",
        "kills",
        "damages",
        "shots",
        "bomb",
        "blinds",
        "fires",
        "smokes",
        "grenades",
        "item_events",
        "round_economy",
        "lifecycle_events",
    ),
}


def normalize_tables(
    raw: Mapping[str, pl.DataFrame],
    profile: str = PROFILE_NAME,
) -> tuple[dict[str, pl.DataFrame], list[str]]:
    """Normalize every table of ``profile`` from a raw awpy frame mapping."""
    required = PROFILE_RAW_KEYS[profile]
    missing = [name for name in required if name not in raw]
    if missing:
        raise AppError(
            "PARSE_FAILED", f"awpy did not produce datasets {missing}", "parse", retryable=False
        )
    normalizers = PROFILE_NORMALIZERS[profile]
    frames: dict[str, pl.DataFrame] = {}
    warnings: list[str] = []
    for table in schema_for_profile(profile):
        frame, table_warnings = normalizers[table](raw)
        frames[table] = frame
        warnings.extend(table_warnings)
    return frames, warnings

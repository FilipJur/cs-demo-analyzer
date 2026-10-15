import polars as pl

from .contracts import PROFILE_NAME, RECONSTRUCTION_PROFILE_NAME

# This profile is deliberately finite. New fields/tables require a new profile/schema key.
SCHEMAS: dict[str, dict[str, pl.DataType]] = {
    "players": {"player_id": pl.String, "steam_id": pl.String, "name": pl.String, "side": pl.String},
    "rounds": {
        "round_id": pl.Int32, "source_round_num": pl.Int32,
        "start_tick": pl.Int64, "freeze_end_tick": pl.Int64, "end_tick": pl.Int64,
        "official_end_tick": pl.Int64, "winner_side": pl.String, "reason_code": pl.Int32,
    },
    "player_state": {
        "row_ordinal": pl.Int64, "tick": pl.Int64, "player_id": pl.String,
        "x": pl.Float32, "y": pl.Float32, "z": pl.Float32,
        "yaw": pl.Float32, "pitch": pl.Float32,
        "velocity_x": pl.Float32, "velocity_y": pl.Float32, "velocity_z": pl.Float32,
        "health": pl.Int32, "armor": pl.Int32, "money": pl.Int32,
        "side": pl.String, "active_weapon": pl.String,
        "has_bomb": pl.Boolean, "is_crouched": pl.Boolean,
        "is_scoped": pl.Boolean, "is_reloading": pl.Boolean,
    },
    "kills": {
        "row_ordinal": pl.Int64, "tick": pl.Int64,
        "attacker_id": pl.String, "victim_id": pl.String, "assister_id": pl.String,
        "weapon": pl.String, "headshot": pl.Boolean,
        "attacker_entity_id": pl.Int64, "attacker_entity_serial": pl.Int64,
        "victim_entity_id": pl.Int64, "victim_entity_serial": pl.Int64,
    },
    "damages": {
        "row_ordinal": pl.Int64, "tick": pl.Int64, "attacker_id": pl.String,
        "victim_id": pl.String, "damage_health": pl.Int32,
        "damage_armor": pl.Int32, "weapon": pl.String,
    },
    "shots": {
        "row_ordinal": pl.Int64, "tick": pl.Int64, "player_id": pl.String,
        "weapon": pl.String, "x": pl.Float32, "y": pl.Float32, "z": pl.Float32,
        "yaw": pl.Float32, "pitch": pl.Float32,
    },
    "bomb": {
        "row_ordinal": pl.Int64, "tick": pl.Int64, "player_id": pl.String,
        "action": pl.String, "bombsite": pl.String,
        "x": pl.Float32, "y": pl.Float32, "z": pl.Float32,
    },
}

#: ``reconstruction-v1``: the seven frozen foundation tables with unchanged
#: semantics (``kills``/``damages``/``shots``/``bomb`` gain further *recorded*
#: upstream columns, which are pure additions to the same rows) plus typed
#: utility, economy and lifecycle tables. Every added column is either a
#: recorded engine value or an upstream-derived geometry value; nothing here is
#: interpolated, estimated or invented by this project.
RECONSTRUCTION_SCHEMAS: dict[str, dict[str, pl.DataType]] = {
    **SCHEMAS,
    "kills": {
        **SCHEMAS["kills"],
        # Raw ``player_death`` event fields plus the recorded positions of the
        # same event. ``hitgroup_name`` is a deterministic label for the recorded
        # ``hitgroup`` code. Upstream *derived* classifications are deliberately
        # not published here: awpy computes ``is_trade``/``victim_traded`` from a
        # 5.25 s trade window (see its own documentation), which is a derived
        # exchange label, not a recorded engine fact.
        "assister_entity_id": pl.Int64, "assister_entity_serial": pl.Int64,
        "attacker_x": pl.Float32, "attacker_y": pl.Float32, "attacker_z": pl.Float32,
        "victim_x": pl.Float32, "victim_y": pl.Float32, "victim_z": pl.Float32,
        "assister_x": pl.Float32, "assister_y": pl.Float32, "assister_z": pl.Float32,
        "hitgroup_code": pl.Int32, "hitgroup_name": pl.String,
        "assist_flash": pl.Boolean, "noscope": pl.Boolean, "thrusmoke": pl.Boolean,
        "penetrated": pl.Int32, "dominated": pl.Int32, "revenge": pl.Int32,
    },
    "damages": {
        **SCHEMAS["damages"],
        "attacker_x": pl.Float32, "attacker_y": pl.Float32, "attacker_z": pl.Float32,
        "victim_x": pl.Float32, "victim_y": pl.Float32, "victim_z": pl.Float32,
        "hitgroup_code": pl.Int32, "hitgroup_name": pl.String,
    },
    "shots": {
        **SCHEMAS["shots"],
        "entity_id": pl.Int64, "entity_serial": pl.Int64, "scoped": pl.Boolean,
        "inaccuracy": pl.Float32, "num_bullets_remaining": pl.Int32,
    },
    "bomb": {**SCHEMAS["bomb"], "entity_id": pl.Int64, "entity_serial": pl.Int64},
    # Per-player per-tick recorded fields beyond ``player_state``. Same rows, in
    # the same order: ``row_ordinal`` is the join key into ``player_state``.
    "player_state_ext": {
        "row_ordinal": pl.Int64, "tick": pl.Int64, "player_id": pl.String,
        "velocity": pl.Float32,
        "has_helmet": pl.Boolean, "has_defuser": pl.Boolean,
        "primary_weapon": pl.String, "secondary_weapon": pl.String,
        "fire_grenades": pl.Int32, "smoke_grenades": pl.Int32, "he_grenades": pl.Int32,
        "flashbangs": pl.Int32, "decoy_grenades": pl.Int32,
        "equipment_value": pl.Int32, "equipment_value_round_start": pl.Int32,
        "is_walking": pl.Boolean, "is_jumping": pl.Boolean, "is_in_bomb_zone": pl.Boolean,
        "is_silent_reloading": pl.Boolean, "is_defusing": pl.Boolean, "is_blinded": pl.Boolean,
        "flash_duration": pl.Float32,
        # Upstream serialization of the resolved ``m_hMyWeapons`` handles as
        # comma-separated weapon class names in slot order; an empty string means
        # no weapon entity was resolved for that observation, which is not the
        # same as "carried nothing". Opaque text: do not parse it as structure,
        # use the typed columns (primary/secondary weapon, per-type grenade
        # counts, has_helmet/has_defuser) for those facts.
        "inventory": pl.String,
    },
    # One row per blinded player; ``tick`` is the blind onset tick and
    # ``duration_seconds`` the replicated onset duration.
    "blinds": {
        "row_ordinal": pl.Int64, "tick": pl.Int64,
        "attacker_id": pl.String, "attacker_side": pl.String,
        "attacker_entity_id": pl.Int64, "attacker_entity_serial": pl.Int64,
        "attacker_x": pl.Float32, "attacker_y": pl.Float32, "attacker_z": pl.Float32,
        "victim_id": pl.String, "victim_side": pl.String,
        "victim_entity_id": pl.Int64, "victim_entity_serial": pl.Int64,
        "victim_x": pl.Float32, "victim_y": pl.Float32, "victim_z": pl.Float32,
        "duration_seconds": pl.Float32,
    },
    # Smoke cloud / inferno fire intervals: one row per cloud or fire, with the
    # upstream [start_tick, end_tick] lifetime and the entity that owned it.
    "smokes": {
        "row_ordinal": pl.Int64, "start_tick": pl.Int64, "end_tick": pl.Int64,
        "entity_id": pl.Int64, "entity_serial": pl.Int64,
        "owner_id": pl.String, "owner_side": pl.String,
        "x": pl.Float32, "y": pl.Float32, "z": pl.Float32,
        "still_active_at_end": pl.Boolean,
    },
    "fires": {
        "row_ordinal": pl.Int64, "start_tick": pl.Int64, "end_tick": pl.Int64,
        "kind": pl.String,
        "entity_id": pl.Int64, "entity_serial": pl.Int64,
        "owner_id": pl.String, "owner_side": pl.String,
        "x": pl.Float32, "y": pl.Float32, "z": pl.Float32,
        "still_active_at_end": pl.Boolean,
    },
    # Live thrown-grenade projectiles, one row per tick each projectile exists.
    "grenades": {
        "row_ordinal": pl.Int64, "tick": pl.Int64,
        "entity_id": pl.Int64, "entity_serial": pl.Int64, "kind": pl.String,
        "owner_id": pl.String, "owner_side": pl.String,
        "x": pl.Float32, "y": pl.Float32, "z": pl.Float32,
    },
    # Item transactions (purchases, pickups, drops) with resolved identity.
    "item_events": {
        "row_ordinal": pl.Int64, "tick": pl.Int64,
        "entity_id": pl.Int64, "entity_serial": pl.Int64, "action": pl.String,
        "player_id": pl.String, "side": pl.String, "item": pl.String,
        "cost": pl.Int32, "original_owner_id": pl.String,
        "near_buy_zone": pl.Boolean,
        "x": pl.Float32, "y": pl.Float32, "z": pl.Float32,
    },
    # Team economy per round, joined to ``rounds.round_id``.
    # ``equipment_value`` is the recorded team total at freeze end; ``buy_type``
    # is awpy's deterministic classification of that recorded value
    # (``eco`` < 5000, ``force`` < 20000, ``full`` otherwise; the first round of
    # each half is labelled ``pistol`` ahead of any value classification). It is
    # a documented computation over a recorded value, not a recorded field and
    # not a tactical verdict; see ``manifest.capabilities["round_economy_buy_type"]``.
    "round_economy": {
        "row_ordinal": pl.Int64, "round_id": pl.Int32, "side": pl.String,
        "equipment_value": pl.Int32, "buy_type": pl.String, "n_players": pl.Int32,
    },
    # Recorded connection/pawn lifecycle events (disconnect, connect, spawn and
    # team change). These explain a participant's absence or hand-over with a
    # recorded event instead of inferring inactivity from missing state.
    "player_lifecycle": {
        "row_ordinal": pl.Int64, "tick": pl.Int64, "kind": pl.String,
        "player_id": pl.String, "user_slot": pl.String, "pawn_handle": pl.Int64,
        "team": pl.String, "previous_team": pl.String,
        "is_bot": pl.Boolean, "reason_code": pl.Int32, "ever_fully_connected": pl.Boolean,
    },
}

#: Named profiles, in the order their tables are written.
PROFILE_SCHEMAS: dict[str, dict[str, dict[str, pl.DataType]]] = {
    PROFILE_NAME: SCHEMAS,
    RECONSTRUCTION_PROFILE_NAME: RECONSTRUCTION_SCHEMAS,
}


def schema_for_profile(profile: str) -> dict[str, dict[str, pl.DataType]]:
    """Tables and column dtypes for ``profile``; ``KeyError`` when it is unknown."""
    return PROFILE_SCHEMAS[profile]


def player_key(value: int | str | None) -> str | None:
    if value is None or int(value) <= 0:
        return None
    return f"steam:{int(value)}"

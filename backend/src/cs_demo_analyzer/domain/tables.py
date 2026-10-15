import polars as pl

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


def player_key(value: int | str | None) -> str | None:
    if value is None or int(value) <= 0:
        return None
    return f"steam:{int(value)}"

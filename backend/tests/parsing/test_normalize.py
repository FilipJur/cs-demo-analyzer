"""Behavior tests for awpy -> canonical normalization.

These use authored awpy-shaped frames (no real demo, no download) and assert
consumer-visible semantics: exact schemas, exact-string IDs, preserved null
identities with unique ordinals, side vocabulary and finite-number rejection.
"""

from __future__ import annotations

import polars as pl
import pytest

from cs_demo_analyzer.domain.contracts import AppError
from cs_demo_analyzer.domain.tables import SCHEMAS
from cs_demo_analyzer.parsing import normalize

POSITIVE = 76561198000000001
OTHER = 76561198000000002


def _state(**overrides) -> pl.DataFrame:
    base = {
        "tick": pl.Series([64, 64], dtype=pl.Int64),
        "steamid": pl.Series([None, POSITIVE], dtype=pl.UInt64),
        "x": pl.Series([-100.0, 200.0], dtype=pl.Float32),
        "y": pl.Series([10.0, -20.0], dtype=pl.Float32),
        "z": pl.Series([0.0, 64.5], dtype=pl.Float32),
        "yaw": pl.Series([90.0, -90.0], dtype=pl.Float32),
        "pitch": pl.Series([0.0, 12.5], dtype=pl.Float32),
        "velocity_x": pl.Series([0.0, 1.0], dtype=pl.Float32),
        "velocity_y": pl.Series([0.0, 2.0], dtype=pl.Float32),
        "velocity_z": pl.Series([0.0, 3.0], dtype=pl.Float32),
        "health": pl.Series([0, 100], dtype=pl.Int32),
        "armor": pl.Series([0, 100], dtype=pl.Int32),
        "money": pl.Series([0, 800], dtype=pl.Int32),
        "side": pl.Series(["counter-terrorist", "terrorist"], dtype=pl.String),
        "active_weapon": pl.Series([None, "ak47"], dtype=pl.String),
        "has_bomb": pl.Series([False, False], dtype=pl.Boolean),
        "is_crouched": pl.Series([False, True], dtype=pl.Boolean),
        "is_scoped": pl.Series([False, False], dtype=pl.Boolean),
        "is_reloading": pl.Series([None, False], dtype=pl.Boolean),
    }
    base.update(overrides)
    return pl.DataFrame(base)


def _schema_of(frame: pl.DataFrame) -> dict[str, pl.DataType]:
    return dict(frame.schema)


def test_players_keep_unresolved_records_with_roster_keys():
    raw = pl.DataFrame(
        {
            "steamid": pl.Series([POSITIVE, None, 0], dtype=pl.UInt64),
            "name": pl.Series(["alpha", None, "camera"], dtype=pl.String),
            "side": pl.Series(["terrorist", "counter-terrorist", "spectator"], dtype=pl.String),
            "team_clan_name": pl.Series([None, None, None], dtype=pl.String),
        }
    )
    frame, warnings = normalize.normalize_players(raw)

    assert frame["player_id"].to_list() == [
        f"steam:{POSITIVE}",
        "unresolved:roster:1",
        "unresolved:roster:2",
    ]
    assert frame["steam_id"].to_list() == [str(POSITIVE), None, None]
    assert frame["side"].to_list() == ["t", "ct", "spectator"]
    assert _schema_of(frame) == SCHEMAS["players"]
    assert frame.get_column("player_id").null_count() == 0
    assert warnings


def test_players_do_not_collapse_zero_and_null_into_one_account():
    raw = pl.DataFrame(
        {
            "steamid": pl.Series([None, 0], dtype=pl.UInt64),
            "name": pl.Series([None, None], dtype=pl.String),
            "side": pl.Series([None, None], dtype=pl.String),
        }
    )
    frame, _ = normalize.normalize_players(raw)
    assert frame["player_id"].n_unique() == 2
    assert frame["side"].to_list() == ["unknown", "unknown"]


def test_state_preserves_null_identity_with_unique_ordinals_and_schema():
    frame, warnings = normalize.normalize_player_state(_state())

    assert list(frame.schema) == list(SCHEMAS["player_state"])
    assert _schema_of(frame) == SCHEMAS["player_state"]
    assert frame["row_ordinal"].to_list() == [0, 1]
    assert frame["row_ordinal"].n_unique() == 2
    assert frame["player_id"].to_list() == [None, f"steam:{POSITIVE}"]
    assert frame["side"].to_list() == ["ct", "t"]
    assert warnings


def test_state_rejects_string_angles_instead_of_promoting_them():
    raw = _state(x=pl.Series(["nope", "nope"], dtype=pl.String))
    with pytest.raises(AppError) as excinfo:
        normalize.normalize_player_state(raw)
    assert excinfo.value.code == "PARSE_FAILED"


def test_state_rejects_float_steamid_to_protect_id_precision():
    raw = _state(steamid=pl.Series([None, float(POSITIVE)], dtype=pl.Float64))
    with pytest.raises(AppError) as excinfo:
        normalize.normalize_player_state(raw)
    assert excinfo.value.code == "PARSE_FAILED"


def test_state_replaces_non_finite_values_with_null():
    raw = _state(
        x=pl.Series([float("inf"), 1.0], dtype=pl.Float32),
        yaw=pl.Series([float("nan"), 5.0], dtype=pl.Float32),
    )
    frame, warnings = normalize.normalize_player_state(raw)
    assert frame["x"].to_list()[0] is None
    assert frame["yaw"].to_list()[0] is None
    assert frame["x"].to_list()[1] == pytest.approx(1.0)
    assert any("non-finite" in warning for warning in warnings)


def test_state_requires_a_finite_position_sample():
    raw = _state(
        x=pl.Series([None, None], dtype=pl.Float32),
        y=pl.Series([None, None], dtype=pl.Float32),
    )
    with pytest.raises(AppError) as excinfo:
        normalize.normalize_player_state(raw)
    assert excinfo.value.code == "PARSE_FAILED"


def test_rounds_assign_recording_ordinals_and_keep_source_number():
    raw = pl.DataFrame(
        {
            "round_num": pl.Series([1, 2], dtype=pl.Int32),
            "start_tick": pl.Series([0, 2000], dtype=pl.Int32),
            "freeze_end_tick": pl.Series([100, 2100], dtype=pl.Int32),
            "end_tick": pl.Series([1900, 4000], dtype=pl.Int32),
            "official_end_tick": pl.Series([1980, None], dtype=pl.Int32),
            "winner": pl.Series([2, 3], dtype=pl.Int32),
            "winner_side": pl.Series(["terrorist", "counter-terrorist"], dtype=pl.String),
            "reason": pl.Series([1, 7], dtype=pl.Int32),
            "reason_name": pl.Series(["x", "y"], dtype=pl.String),
            "is_knife_round": pl.Series([False, False], dtype=pl.Boolean),
        }
    )
    frame, _ = normalize.normalize_rounds(raw)
    assert frame["round_id"].to_list() == [1, 2]
    assert frame["source_round_num"].to_list() == [1, 2]
    assert frame["winner_side"].to_list() == ["t", "ct"]
    assert frame["official_end_tick"].to_list() == [1980, None]
    assert _schema_of(frame) == SCHEMAS["rounds"]


def _kill_row() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "tick": pl.Series([100], dtype=pl.Int32),
            "attacker_entity_id": pl.Series([None], dtype=pl.Int32),
            "attacker_entity_serial": pl.Series([None], dtype=pl.UInt32),
            "attacker_steamid": pl.Series([None], dtype=pl.UInt64),
            "attacker_name": pl.Series([None], dtype=pl.String),
            "attacker_side": pl.Series([None], dtype=pl.String),
            "victim_entity_id": pl.Series([12], dtype=pl.Int32),
            "victim_entity_serial": pl.Series([3], dtype=pl.UInt32),
            "victim_steamid": pl.Series([OTHER], dtype=pl.UInt64),
            "victim_name": pl.Series(["beta"], dtype=pl.String),
            "victim_side": pl.Series(["terrorist"], dtype=pl.String),
            "assister_steamid": pl.Series([None], dtype=pl.UInt64),
            "weapon": pl.Series(["world"], dtype=pl.String),
            "headshot": pl.Series([False], dtype=pl.Boolean),
        }
    )


def test_kills_allow_world_deaths_with_null_attacker():
    frame, _ = normalize.normalize_kills(_kill_row())
    row = frame.row(0, named=True)
    assert row["attacker_id"] is None
    assert row["victim_id"] == f"steam:{OTHER}"
    assert row["row_ordinal"] == 0
    assert row["victim_entity_id"] == 12
    assert _schema_of(frame) == SCHEMAS["kills"]


def test_damages_map_awpy_damage_columns():
    raw = pl.DataFrame(
        {
            "tick": pl.Series([5], dtype=pl.Int32),
            "attacker_steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
            "victim_steamid": pl.Series([OTHER], dtype=pl.UInt64),
            "dmg_health": pl.Series([27], dtype=pl.Int32),
            "dmg_armor": pl.Series([3], dtype=pl.Int32),
            "weapon": pl.Series(["ak47"], dtype=pl.String),
        }
    )
    frame, _ = normalize.normalize_damages(raw)
    row = frame.row(0, named=True)
    assert row["attacker_id"] == f"steam:{POSITIVE}"
    assert row["damage_health"] == 27
    assert row["damage_armor"] == 3
    assert "dmg_health" not in frame.columns
    assert _schema_of(frame) == SCHEMAS["damages"]


def test_shots_and_bomb_use_player_id_and_action_names():
    shots = pl.DataFrame(
        {
            "tick": pl.Series([9], dtype=pl.Int32),
            "steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
            "weapon": pl.Series(["ak47"], dtype=pl.String),
            "x": pl.Series([1.0], dtype=pl.Float32),
            "y": pl.Series([2.0], dtype=pl.Float32),
            "z": pl.Series([3.0], dtype=pl.Float32),
            "yaw": pl.Series([45.0], dtype=pl.Float32),
            "pitch": pl.Series([-5.0], dtype=pl.Float32),
        }
    )
    shot_frame, _ = normalize.normalize_shots(shots)
    assert shot_frame["player_id"].to_list() == [f"steam:{POSITIVE}"]
    assert "steamid" not in shot_frame.columns
    assert _schema_of(shot_frame) == SCHEMAS["shots"]

    bomb = pl.DataFrame(
        {
            "tick": pl.Series([42], dtype=pl.Int32),
            "steamid": pl.Series([None], dtype=pl.UInt64),
            "event": pl.Series(["finish_plant"], dtype=pl.String),
            "bombsite": pl.Series(["A"], dtype=pl.String),
            "x": pl.Series([1.0], dtype=pl.Float32),
            "y": pl.Series([2.0], dtype=pl.Float32),
            "z": pl.Series([3.0], dtype=pl.Float32),
        }
    )
    bomb_frame, _ = normalize.normalize_bomb(bomb)
    row = bomb_frame.row(0, named=True)
    assert row["action"] == "finish_plant"
    assert row["player_id"] is None
    assert "event" not in bomb_frame.columns
    assert _schema_of(bomb_frame) == SCHEMAS["bomb"]


def test_side_vocabulary_is_total_and_non_null():
    raw = pl.DataFrame(
        {
            "steamid": pl.Series([POSITIVE] * 5, dtype=pl.UInt64),
            "name": pl.Series([None] * 5, dtype=pl.String),
            "side": pl.Series(
                ["terrorist", "counter-terrorist", "spectator", "unassigned", None],
                dtype=pl.String,
            ),
        }
    )
    frame, _ = normalize.normalize_players(raw)
    assert frame["side"].to_list() == ["t", "ct", "spectator", "unknown", "unknown"]
    assert frame["side"].null_count() == 0


def test_absent_event_family_yields_typed_empty_table():
    raw = {table: pl.DataFrame() for table in SCHEMAS}
    frames, _ = normalize.normalize_tables(raw)
    for table, schema in SCHEMAS.items():
        assert frames[table].height == 0
        assert _schema_of(frames[table]) == schema


def test_missing_dataset_key_is_rejected():
    raw = {table: pl.DataFrame() for table in SCHEMAS if table != "bomb"}
    with pytest.raises(AppError):
        normalize.normalize_tables(raw)

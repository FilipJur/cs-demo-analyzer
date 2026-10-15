"""Behavior tests for the ``reconstruction-v1`` extraction profile.

The seven foundation tables must stay byte-identical in schema and semantics;
the extension is purely additive. These tests exercise the profile dispatch in
``parsing.normalize`` and the profile identity an extended extraction publishes,
using authored awpy-shaped frames (no real demo, no download).
"""

from __future__ import annotations

import polars as pl
import pytest

from cs_demo_analyzer.domain.contracts import (
    PROFILE_KEY,
    RECONSTRUCTION_PROFILE_KEY,
    RECONSTRUCTION_PROFILE_NAME,
    RECONSTRUCTION_SCHEMA_VERSION,
    AppError,
    ExtractionRequest,
    Manifest,
)
from cs_demo_analyzer.domain.tables import RECONSTRUCTION_SCHEMAS, SCHEMAS
from cs_demo_analyzer.parsing import awpy_adapter, normalize

POSITIVE = 76561198000000001
OTHER = 76561198000000002


def _raw_frames() -> dict[str, pl.DataFrame]:
    """The raw awpy frames one extended extraction reads, with real column shapes."""
    return {
        "players": pl.DataFrame(
            {
                "steamid": pl.Series([POSITIVE, OTHER], dtype=pl.UInt64),
                "name": pl.Series(["alpha", "beta"], dtype=pl.String),
                "side": pl.Series(["terrorist", "counter-terrorist"], dtype=pl.String),
                "team_clan_name": pl.Series([None, None], dtype=pl.String),
            }
        ),
        "rounds": pl.DataFrame(
            {
                "round_num": pl.Series([1], dtype=pl.Int32),
                "start_tick": pl.Series([0], dtype=pl.Int32),
                "freeze_end_tick": pl.Series([100], dtype=pl.Int32),
                "end_tick": pl.Series([1900], dtype=pl.Int32),
                "official_end_tick": pl.Series([1980], dtype=pl.Int32),
                "winner_side": pl.Series(["terrorist"], dtype=pl.String),
                "reason": pl.Series([1], dtype=pl.Int32),
            }
        ),
        "player_state": _snapshots(),
        "kills": pl.DataFrame(
            {
                "tick": pl.Series([1000], dtype=pl.Int32),
                "attacker_steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "victim_steamid": pl.Series([OTHER], dtype=pl.UInt64),
                "assister_steamid": pl.Series([None], dtype=pl.UInt64),
                "weapon": pl.Series(["ak47"], dtype=pl.String),
                "headshot": pl.Series([True], dtype=pl.Boolean),
                "attacker_entity_id": pl.Series([1], dtype=pl.Int32),
                "attacker_entity_serial": pl.Series([2], dtype=pl.UInt32),
                "victim_entity_id": pl.Series([3], dtype=pl.Int32),
                "victim_entity_serial": pl.Series([4], dtype=pl.UInt32),
                "assister_entity_id": pl.Series([5], dtype=pl.Int32),
                "assister_entity_serial": pl.Series([6], dtype=pl.UInt32),
                "attacker_x": pl.Series([10.0], dtype=pl.Float32),
                "attacker_y": pl.Series([11.0], dtype=pl.Float32),
                "attacker_z": pl.Series([12.0], dtype=pl.Float32),
                "victim_x": pl.Series([20.0], dtype=pl.Float32),
                "victim_y": pl.Series([21.0], dtype=pl.Float32),
                "victim_z": pl.Series([22.0], dtype=pl.Float32),
                "assister_x": pl.Series([30.0], dtype=pl.Float32),
                "assister_y": pl.Series([31.0], dtype=pl.Float32),
                "assister_z": pl.Series([32.0], dtype=pl.Float32),
                "hitgroup": pl.Series([1], dtype=pl.Int32),
                "hitgroup_name": pl.Series(["head"], dtype=pl.String),
                "assist_flash": pl.Series([False], dtype=pl.Boolean),
                "noscope": pl.Series([False], dtype=pl.Boolean),
                "thrusmoke": pl.Series([True], dtype=pl.Boolean),
                "is_trade": pl.Series([False], dtype=pl.Boolean),
                "victim_traded": pl.Series([False], dtype=pl.Boolean),
                "penetrated": pl.Series([0], dtype=pl.Int32),
                "dominated": pl.Series([0], dtype=pl.Int32),
                "revenge": pl.Series([0], dtype=pl.Int32),
            }
        ),
        "damages": pl.DataFrame(
            {
                "tick": pl.Series([900], dtype=pl.Int32),
                "attacker_steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "victim_steamid": pl.Series([OTHER], dtype=pl.UInt64),
                "dmg_health": pl.Series([27], dtype=pl.Int32),
                "dmg_armor": pl.Series([3], dtype=pl.Int32),
                "weapon": pl.Series(["ak47"], dtype=pl.String),
                "attacker_x": pl.Series([10.0], dtype=pl.Float32),
                "attacker_y": pl.Series([11.0], dtype=pl.Float32),
                "attacker_z": pl.Series([12.0], dtype=pl.Float32),
                "victim_x": pl.Series([20.0], dtype=pl.Float32),
                "victim_y": pl.Series([21.0], dtype=pl.Float32),
                "victim_z": pl.Series([22.0], dtype=pl.Float32),
                "hitgroup": pl.Series([3], dtype=pl.Int32),
                "hitgroup_name": pl.Series(["chest"], dtype=pl.String),
                "health_pre": pl.Series([100], dtype=pl.Int32),
                "health_post": pl.Series([73], dtype=pl.Int32),
                "armor_pre": pl.Series([100], dtype=pl.Int32),
                "armor_post": pl.Series([97], dtype=pl.Int32),
            }
        ),
        "shots": pl.DataFrame(
            {
                "tick": pl.Series([890], dtype=pl.Int32),
                "steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "weapon": pl.Series(["ak47"], dtype=pl.String),
                "x": pl.Series([1.0], dtype=pl.Float32),
                "y": pl.Series([2.0], dtype=pl.Float32),
                "z": pl.Series([3.0], dtype=pl.Float32),
                "yaw": pl.Series([45.0], dtype=pl.Float32),
                "pitch": pl.Series([-5.0], dtype=pl.Float32),
                "entity_id": pl.Series([7], dtype=pl.Int32),
                "entity_serial": pl.Series([8], dtype=pl.UInt32),
                "scoped": pl.Series([False], dtype=pl.Boolean),
                "inaccuracy": pl.Series([0.25], dtype=pl.Float32),
                "num_bullets_remaining": pl.Series([17], dtype=pl.Int32),
            }
        ),
        "bomb": pl.DataFrame(
            {
                "tick": pl.Series([640], dtype=pl.Int32),
                "event": pl.Series(["bomb_planted"], dtype=pl.String),
                "steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "bombsite": pl.Series(["a"], dtype=pl.String),
                "x": pl.Series([0.0], dtype=pl.Float32),
                "y": pl.Series([0.0], dtype=pl.Float32),
                "z": pl.Series([-128.0], dtype=pl.Float32),
                "entity_id": pl.Series([9], dtype=pl.Int32),
                "entity_serial": pl.Series([10], dtype=pl.UInt32),
            }
        ),
        "blinds": pl.DataFrame(
            {
                "tick": pl.Series([1000], dtype=pl.Int32),
                "attacker_entity_id": pl.Series([1], dtype=pl.Int32),
                "attacker_entity_serial": pl.Series([2], dtype=pl.UInt32),
                "attacker_steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "attacker_name": pl.Series(["alpha"], dtype=pl.String),
                "attacker_side": pl.Series(["terrorist"], dtype=pl.String),
                "attacker_x": pl.Series([10.0], dtype=pl.Float32),
                "attacker_y": pl.Series([11.0], dtype=pl.Float32),
                "attacker_z": pl.Series([12.0], dtype=pl.Float32),
                "victim_entity_id": pl.Series([3], dtype=pl.Int32),
                "victim_entity_serial": pl.Series([4], dtype=pl.UInt32),
                "victim_steamid": pl.Series([OTHER], dtype=pl.UInt64),
                "victim_name": pl.Series(["beta"], dtype=pl.String),
                "victim_side": pl.Series(["counter-terrorist"], dtype=pl.String),
                "victim_x": pl.Series([20.0], dtype=pl.Float32),
                "victim_y": pl.Series([21.0], dtype=pl.Float32),
                "victim_z": pl.Series([22.0], dtype=pl.Float32),
                "duration": pl.Series([3.5], dtype=pl.Float32),
            }
        ),
        "smokes": pl.DataFrame(
            {
                "start_tick": pl.Series([90], dtype=pl.Int32),
                "end_tick": pl.Series([100], dtype=pl.Int32),
                "thrower_name": pl.Series([None], dtype=pl.String),
                "thrower_steamid": pl.Series([None], dtype=pl.UInt64),
                "thrower_side": pl.Series([None], dtype=pl.String),
                "entity_id": pl.Series([390], dtype=pl.Int32),
                "entity_serial": pl.Series([376], dtype=pl.UInt32),
                "x": pl.Series([870.9], dtype=pl.Float32),
                "y": pl.Series([2300.9], dtype=pl.Float32),
                "z": pl.Series([140.0], dtype=pl.Float32),
            }
        ),
        "fires": pl.DataFrame(
            {
                "start_tick": pl.Series([950], dtype=pl.Int32),
                "end_tick": pl.Series([1800], dtype=pl.Int32),
                "thrower_name": pl.Series([None], dtype=pl.String),
                "thrower_steamid": pl.Series([None], dtype=pl.UInt64),
                "thrower_side": pl.Series([None], dtype=pl.String),
                "type": pl.Series(["inferno"], dtype=pl.String),
                "entity_id": pl.Series([399], dtype=pl.Int32),
                "entity_serial": pl.Series([156], dtype=pl.UInt32),
                "x": pl.Series([1677.5], dtype=pl.Float32),
                "y": pl.Series([24.2], dtype=pl.Float32),
                "z": pl.Series([131.8], dtype=pl.Float32),
            }
        ),
        "grenades": pl.DataFrame(
            {
                "tick": pl.Series([500, 501], dtype=pl.Int32),
                "thrower_name": pl.Series([None, None], dtype=pl.String),
                "thrower_steamid": pl.Series([None, None], dtype=pl.UInt64),
                "thrower_side": pl.Series([None, None], dtype=pl.String),
                "type": pl.Series(["smoke", "smoke"], dtype=pl.String),
                "entity_id": pl.Series([584, 584], dtype=pl.Int32),
                "entity_serial": pl.Series([47, 47], dtype=pl.UInt32),
                "x": pl.Series([615.3, 608.2], dtype=pl.Float32),
                "y": pl.Series([1475.4, 1472.7], dtype=pl.Float32),
                "z": pl.Series([673.9, 665.8], dtype=pl.Float32),
            }
        ),
        "item_events": pl.DataFrame(
            {
                "tick": pl.Series([640], dtype=pl.Int32),
                "entity_id": pl.Series([549], dtype=pl.Int32),
                "entity_serial": pl.Series([747], dtype=pl.UInt32),
                "action": pl.Series(["purchase"], dtype=pl.String),
                "steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "name": pl.Series(["alpha"], dtype=pl.String),
                "side": pl.Series(["terrorist"], dtype=pl.String),
                "item": pl.Series(["smokegrenade"], dtype=pl.String),
                "x": pl.Series([2353.0], dtype=pl.Float32),
                "y": pl.Series([1977.0], dtype=pl.Float32),
                "z": pl.Series([135.5], dtype=pl.Float32),
                "original_owner_steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "cost": pl.Series([300], dtype=pl.Int32),
                "near_buy_zone": pl.Series([None], dtype=pl.Boolean),
            }
        ),
        "round_economy": pl.DataFrame(
            {
                "round_num": pl.Series([1, 9], dtype=pl.Int32),
                "side": pl.Series(["terrorist", "counter-terrorist"], dtype=pl.String),
                "equipment_value": pl.Series([3950, 4200], dtype=pl.Int32),
                "buy_type": pl.Series(["pistol", "full"], dtype=pl.String),
                "n_players": pl.Series([5, 5], dtype=pl.Int32),
            }
        ),
    }


def _snapshots() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "tick": pl.Series([64, 128], dtype=pl.Int64),
            "steamid": pl.Series([None, POSITIVE], dtype=pl.UInt64),
            "name": pl.Series([None, "alpha"], dtype=pl.String),
            "side": pl.Series(["terrorist", "terrorist"], dtype=pl.String),
            "x": pl.Series([None, 200.0], dtype=pl.Float32),
            "y": pl.Series([None, -20.0], dtype=pl.Float32),
            "z": pl.Series([None, 64.5], dtype=pl.Float32),
            "velocity_x": pl.Series([0.0, 1.0], dtype=pl.Float32),
            "velocity_y": pl.Series([0.0, 2.0], dtype=pl.Float32),
            "velocity_z": pl.Series([0.0, 3.0], dtype=pl.Float32),
            "velocity": pl.Series([0.0, 3.7], dtype=pl.Float32),
            "yaw": pl.Series([0.0, -90.0], dtype=pl.Float32),
            "pitch": pl.Series([0.0, 12.5], dtype=pl.Float32),
            "health": pl.Series([0, 100], dtype=pl.Int32),
            "armor": pl.Series([0, 100], dtype=pl.Int32),
            "money": pl.Series([0, 800], dtype=pl.Int32),
            "has_helmet": pl.Series([False, True], dtype=pl.Boolean),
            "has_defuser": pl.Series([False, False], dtype=pl.Boolean),
            "has_bomb": pl.Series([False, False], dtype=pl.Boolean),
            "active_weapon": pl.Series([None, "ak47"], dtype=pl.String),
            "primary_weapon": pl.Series([None, "ak47"], dtype=pl.String),
            "secondary_weapon": pl.Series([None, "glock"], dtype=pl.String),
            "fire_grenades": pl.Series([0, 1], dtype=pl.Int32),
            "smoke_grenades": pl.Series([0, 1], dtype=pl.Int32),
            "he_grenades": pl.Series([0, 0], dtype=pl.Int32),
            "flashbangs": pl.Series([0, 2], dtype=pl.Int32),
            "decoy_grenades": pl.Series([0, 0], dtype=pl.Int32),
            "equipment_value": pl.Series([0, 3300], dtype=pl.Int32),
            "equipment_value_round_start": pl.Series([0, 800], dtype=pl.Int32),
            "is_crouched": pl.Series([False, True], dtype=pl.Boolean),
            "is_walking": pl.Series([False, True], dtype=pl.Boolean),
            "is_jumping": pl.Series([False, False], dtype=pl.Boolean),
            "is_in_bomb_zone": pl.Series([False, False], dtype=pl.Boolean),
            "is_scoped": pl.Series([False, False], dtype=pl.Boolean),
            "is_reloading": pl.Series([None, False], dtype=pl.Boolean),
            "is_silent_reloading": pl.Series([None, False], dtype=pl.Boolean),
            "is_defusing": pl.Series([False, False], dtype=pl.Boolean),
            "is_blinded": pl.Series([False, True], dtype=pl.Boolean),
            "flash_duration": pl.Series([0.0, 1.5], dtype=pl.Float32),
            "inventory": pl.Series(["", "ak47,glock,smokegrenade"], dtype=pl.String),
        }
    )


def _lifecycle_events() -> dict[str, pl.DataFrame]:
    return {
        "player_disconnect": pl.DataFrame(
            {
                "tick": pl.Series([8215], dtype=pl.Int64),
                "userid": pl.Series(["4"], dtype=pl.String),
                "reason": pl.Series(["79"], dtype=pl.String),
                "xuid": pl.Series([str(POSITIVE)], dtype=pl.String),
                "ever_fully_connected": pl.Series(["true"], dtype=pl.String),
            }
        ),
        "player_connect_full": pl.DataFrame(
            {
                "tick": pl.Series([9787], dtype=pl.Int64),
                "userid": pl.Series(["7"], dtype=pl.String),
            }
        ),
        "player_spawn": pl.DataFrame(
            {
                "tick": pl.Series([65], dtype=pl.Int64),
                "userid": pl.Series(["9"], dtype=pl.String),
                "userid_pawn": pl.Series(["1567195542"], dtype=pl.String),
            }
        ),
        "player_team": pl.DataFrame(
            {
                "tick": pl.Series([66802], dtype=pl.Int64),
                "userid": pl.Series(["0"], dtype=pl.String),
                "userid_pawn": pl.Series(["-889355902"], dtype=pl.String),
                "team": pl.Series(["3"], dtype=pl.String),
                "oldteam": pl.Series(["2"], dtype=pl.String),
                "isbot": pl.Series(["false"], dtype=pl.String),
            }
        ),
    }


def _extended_frames() -> tuple[dict[str, pl.DataFrame], list[str]]:
    raw = {**_raw_frames(), "lifecycle_events": _lifecycle_events()}
    return normalize.normalize_tables(raw, RECONSTRUCTION_PROFILE_NAME)


def test_reconstruction_tables_match_their_declared_schemas():
    frames, _ = _extended_frames()

    assert list(frames) == list(RECONSTRUCTION_SCHEMAS)
    for table, schema in RECONSTRUCTION_SCHEMAS.items():
        assert dict(frames[table].schema) == schema
    # Every foundation table keeps its frozen columns, in the frozen order.
    for table, schema in SCHEMAS.items():
        assert list(frames[table].columns)[: len(schema)] == list(schema)


def test_extension_columns_are_additive_to_foundation_event_rows():
    frames, _ = _extended_frames()
    foundation, _ = normalize.normalize_tables(_raw_frames(), "foundation-v1")

    for table in ("kills", "damages", "shots", "bomb"):
        extended = frames[table].select(list(SCHEMAS[table]))
        assert extended.equals(foundation[table]), table

    kill = frames["kills"].row(0, named=True)
    assert kill["thrusmoke"] is True
    assert kill["hitgroup_code"] == 1
    assert kill["attacker_x"] == 10.0
    assert kill["attacker_id"] == f"steam:{POSITIVE}"
    # Upstream *derived* field on the raw frame is ignored, not republished.
    assert "is_trade" not in frames["kills"].columns
    assert "victim_traded" not in frames["kills"].columns
    # Upstream pre-hit health/armor estimates stay out of the canonical profile.
    damage = frames["damages"].row(0, named=True)
    assert damage["hitgroup_name"] == "chest"
    assert "health_pre" not in frames["damages"].columns
    assert "armor_pre" not in frames["damages"].columns


def test_player_state_ext_aligns_row_for_row_with_player_state():
    frames, _ = _extended_frames()

    state = frames["player_state"]
    extended = frames["player_state_ext"]
    assert extended.height == state.height
    assert extended["row_ordinal"].to_list() == state["row_ordinal"].to_list()
    assert extended["tick"].to_list() == state["tick"].to_list()
    assert extended["player_id"].to_list() == state["player_id"].to_list()
    assert extended["is_blinded"].to_list() == [False, True]
    assert extended["smoke_grenades"].to_list() == [0, 1]


def test_utility_intervals_keep_the_recorded_lifetime_and_truncation_flag():
    frames, _ = _extended_frames()

    smoke = frames["smokes"].row(0, named=True)
    fire = frames["fires"].row(0, named=True)
    assert (smoke["start_tick"], smoke["end_tick"]) == (90, 100)
    assert smoke["still_active_at_end"] is False
    # The recording ends at tick 128, before the fire expires.
    assert (fire["start_tick"], fire["end_tick"]) == (950, 1800)
    assert fire["still_active_at_end"] is True
    assert fire["kind"] == "inferno"


def test_utility_owner_identity_is_never_invented():
    frames, _ = _extended_frames()

    for table in ("grenades", "smokes", "fires"):
        assert frames[table]["owner_id"].null_count() == frames[table].height
        assert set(frames[table]["owner_side"].to_list()) == {"unknown"}


def test_grenade_trajectory_rows_keep_entity_and_tick():
    frames, _ = _extended_frames()

    grenades = frames["grenades"]
    assert grenades["tick"].to_list() == [500, 501]
    assert grenades["kind"].to_list() == ["smoke", "smoke"]
    assert grenades["entity_id"].to_list() == [584, 584]
    assert grenades["row_ordinal"].to_list() == [0, 1]


def test_round_economy_joins_the_canonical_round_and_flags_unmatched_rounds():
    frames, _ = _extended_frames()

    economy = frames["round_economy"].sort("round_id", nulls_last=True)
    assert economy["round_id"].to_list() == [1, None]
    assert economy["buy_type"].to_list() == ["pistol", "full"]


def test_player_lifecycle_keeps_recorded_events_and_only_recorded_identities():
    frames, _ = _extended_frames()

    lifecycle = frames["player_lifecycle"].sort("tick")
    assert lifecycle["kind"].to_list() == ["spawn", "disconnect", "connect", "team_change"]
    assert lifecycle["row_ordinal"].to_list() == [0, 1, 2, 3]
    by_kind = {row["kind"]: row for row in lifecycle.iter_rows(named=True)}
    assert by_kind["disconnect"]["player_id"] == f"steam:{POSITIVE}"
    assert by_kind["disconnect"]["reason_code"] == 79
    assert by_kind["disconnect"]["ever_fully_connected"] is True
    # Kinds whose upstream event records no SteamID64 keep a null identity.
    for kind in ("spawn", "connect", "team_change"):
        assert by_kind[kind]["player_id"] is None
    assert by_kind["spawn"]["pawn_handle"] == 1567195542
    assert by_kind["team_change"]["team"] == "ct"
    assert by_kind["team_change"]["previous_team"] == "t"
    assert by_kind["team_change"]["is_bot"] is False


def test_missing_extended_dataset_is_rejected():
    raw = _raw_frames()
    raw["lifecycle_events"] = _lifecycle_events()
    del raw["blinds"]

    with pytest.raises(AppError) as error:
        normalize.normalize_tables(raw, RECONSTRUCTION_PROFILE_NAME)
    assert error.value.code == "PARSE_FAILED"
    assert "blinds" in error.value.message


class _FakeExtendedDemo:
    """An awpy-shaped demo exposing every dataset the extended profile reads."""

    def __init__(self) -> None:
        self.tick_rate = 64.0
        self.header = {"map_name": "de_inferno", "demo_version_name": "2000930"}
        for name, frame in _raw_frames().items():
            setattr(self, name, frame)
        self.events = _FakeEvents(_lifecycle_events())

    def load(self, *datasets: str) -> None:
        return None

    def snapshots(self, *, every: int | None = None, **_: object) -> pl.DataFrame:
        return _snapshots()


class _FakeEvents:
    def __init__(self, frames: dict[str, pl.DataFrame]) -> None:
        self._frames = frames

    @property
    def names(self) -> list[str]:
        return list(self._frames)

    def __getitem__(self, name: str) -> pl.DataFrame:
        return self._frames[name]


def _extended_request(tmp_path) -> ExtractionRequest:
    demo_file = tmp_path / "demo.dem"
    demo_file.write_bytes(b"PBDEMS2\x00" + b"\x00" * 32)
    return ExtractionRequest(
        job_id="job-1",
        generation_id="gen-1",
        demo_id="demo-1",
        input_path=str(demo_file),
        output_dir=str(tmp_path / "out"),
        profile=RECONSTRUCTION_PROFILE_NAME,
        profile_key=RECONSTRUCTION_PROFILE_KEY,
    )


def test_extended_extraction_publishes_the_reconstruction_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(awpy_adapter, "Demo", lambda path: _FakeExtendedDemo())
    manifest = awpy_adapter.extract(_extended_request(tmp_path))

    assert manifest.profile == RECONSTRUCTION_PROFILE_NAME
    assert manifest.profile_key == RECONSTRUCTION_PROFILE_KEY
    assert set(manifest.tables) == set(RECONSTRUCTION_SCHEMAS)
    assert all(
        descriptor.schema_version == RECONSTRUCTION_SCHEMA_VERSION
        for descriptor in manifest.tables.values()
    )
    directory = tmp_path / "out"
    for table, descriptor in manifest.tables.items():
        file = directory / descriptor.path
        assert pl.read_parquet(file).height == descriptor.row_count
        assert dict(pl.read_parquet(file).schema) == RECONSTRUCTION_SCHEMAS[table]
    assert Manifest.model_validate_json((directory / awpy_adapter.MANIFEST_NAME).read_text()) == manifest
    assert manifest.capabilities["player_lifecycle"].status == "available"
    assert manifest.capabilities["utility_owner_attribution"].status == "absent"
    assert manifest.capabilities["player_lifecycle_kinds"].status == "available"
    assert manifest.capabilities["player_view_origin"].status == "absent"


def test_extract_refuses_a_profile_key_that_does_not_match_the_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(awpy_adapter, "Demo", lambda path: _FakeExtendedDemo())
    request = _extended_request(tmp_path).model_copy(update={"profile_key": PROFILE_KEY})

    with pytest.raises(AppError) as error:
        awpy_adapter.extract(request)
    assert error.value.code == "INVALID_PROFILE"
    assert not (tmp_path / "out" / "manifest.json").exists()



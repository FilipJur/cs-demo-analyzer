"""Behavior tests for the extraction adapter.

A fake ``Demo`` supplies awpy-shaped frames so the adapter's observable output
is tested without a real recording: exactly the seven tables, descriptor hashes
and row counts that match the files, the frozen profile provenance, partial
quality for unresolved identities, and ENOSPC reporting.
"""

from __future__ import annotations

import errno
import hashlib

import polars as pl
import pytest

from cs_demo_analyzer.domain.contracts import (
    NORMALIZER_VERSION,
    PARSER_VERSION,
    PROFILE_KEY,
    AppError,
    ExtractionRequest,
    Manifest,
)
from cs_demo_analyzer.domain.tables import SCHEMAS
from cs_demo_analyzer.parsing import awpy_adapter

POSITIVE = 76561198000000001
OTHER = 76561198000000002


def _snapshots(resolved: bool) -> pl.DataFrame:
    steamids = [OTHER, POSITIVE] if resolved else [None, POSITIVE]
    return pl.DataFrame(
        {
            "tick": pl.Series([64, 64], dtype=pl.Int64),
            "steamid": pl.Series(steamids, dtype=pl.UInt64),
            "name": pl.Series([None, None], dtype=pl.String),
            "side": pl.Series(["terrorist", "counter-terrorist"], dtype=pl.String),
            "x": pl.Series([-100.0, 200.0], dtype=pl.Float32),
            "y": pl.Series([10.0, -20.0], dtype=pl.Float32),
            "z": pl.Series([0.0, 64.5], dtype=pl.Float32),
            "velocity_x": pl.Series([0.0, 1.0], dtype=pl.Float32),
            "velocity_y": pl.Series([0.0, 2.0], dtype=pl.Float32),
            "velocity_z": pl.Series([0.0, 3.0], dtype=pl.Float32),
            "yaw": pl.Series([90.0, -90.0], dtype=pl.Float32),
            "pitch": pl.Series([0.0, 12.5], dtype=pl.Float32),
            "health": pl.Series([0, 100], dtype=pl.Int32),
            "armor": pl.Series([0, 100], dtype=pl.Int32),
            "money": pl.Series([0, 800], dtype=pl.Int32),
            "active_weapon": pl.Series([None, "ak47"], dtype=pl.String),
            "has_bomb": pl.Series([False, False], dtype=pl.Boolean),
            "is_crouched": pl.Series([False, True], dtype=pl.Boolean),
            "is_scoped": pl.Series([False, False], dtype=pl.Boolean),
            "is_reloading": pl.Series([None, False], dtype=pl.Boolean),
        }
    )


class _FakeDemo:
    def __init__(self, *, resolved: bool = True) -> None:
        self.tick_rate = 64.0
        self.header = {"map_name": "de_inferno", "demo_version_name": "2000930"}
        steamids = [OTHER, POSITIVE] if resolved else [POSITIVE, None, 0]
        names = ["alpha", "beta"] if resolved else ["alpha", None, "camera"]
        sides = (
            ["terrorist", "counter-terrorist"]
            if resolved
            else ["terrorist", "counter-terrorist", "spectator"]
        )
        self.players = pl.DataFrame(
            {
                "steamid": pl.Series(steamids, dtype=pl.UInt64),
                "name": pl.Series(names, dtype=pl.String),
                "side": pl.Series(sides, dtype=pl.String),
                "team_clan_name": pl.Series([None] * len(steamids), dtype=pl.String),
            }
        )
        self.rounds = pl.DataFrame(
            {
                "round_num": pl.Series([1], dtype=pl.Int32),
                "start_tick": pl.Series([0], dtype=pl.Int32),
                "freeze_end_tick": pl.Series([100], dtype=pl.Int32),
                "end_tick": pl.Series([1900], dtype=pl.Int32),
                "official_end_tick": pl.Series([1980], dtype=pl.Int32),
                "winner": pl.Series([2], dtype=pl.Int32),
                "winner_side": pl.Series(["terrorist"], dtype=pl.String),
                "reason": pl.Series([1], dtype=pl.Int32),
            }
        )
        self.kills = pl.DataFrame(
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
            }
        )
        self.damages = pl.DataFrame(
            {
                "tick": pl.Series([900], dtype=pl.Int32),
                "attacker_steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "victim_steamid": pl.Series([OTHER], dtype=pl.UInt64),
                "dmg_health": pl.Series([27], dtype=pl.Int32),
                "dmg_armor": pl.Series([3], dtype=pl.Int32),
                "weapon": pl.Series(["ak47"], dtype=pl.String),
            }
        )
        self.shots = pl.DataFrame(
            {
                "tick": pl.Series([890], dtype=pl.Int32),
                "steamid": pl.Series([POSITIVE], dtype=pl.UInt64),
                "weapon": pl.Series(["ak47"], dtype=pl.String),
                "x": pl.Series([1.0], dtype=pl.Float32),
                "y": pl.Series([2.0], dtype=pl.Float32),
                "z": pl.Series([3.0], dtype=pl.Float32),
                "yaw": pl.Series([45.0], dtype=pl.Float32),
                "pitch": pl.Series([-5.0], dtype=pl.Float32),
            }
        )
        self.bomb = pl.DataFrame()
        self._resolved = resolved

    def load(self, *datasets: str) -> None:
        return None

    def snapshots(self, *, every: int | None = None, **_: object) -> pl.DataFrame:
        return _snapshots(self._resolved)


def _request(tmp_path, demo_file) -> ExtractionRequest:
    return ExtractionRequest(
        job_id="job-1",
        generation_id="gen-1",
        demo_id="demo-1",
        input_path=str(demo_file),
        output_dir=str(tmp_path / "out"),
    )


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _prepare(tmp_path, monkeypatch, *, resolved: bool = True):
    demo_file = tmp_path / "demo.dem"
    demo_file.write_bytes(b"PBDEMS2\x00" + b"\x00" * 32)
    fake = _FakeDemo(resolved=resolved)
    monkeypatch.setattr(awpy_adapter, "Demo", lambda path: fake)
    return _request(tmp_path, demo_file)


def test_extract_writes_seven_tables_matching_their_descriptors(tmp_path, monkeypatch):
    request = _prepare(tmp_path, monkeypatch)
    manifest = awpy_adapter.extract(request)

    assert set(manifest.tables) == set(SCHEMAS)

    directory = tmp_path / "out"
    for table, descriptor in manifest.tables.items():
        file = directory / descriptor.path
        assert file.is_file()
        assert descriptor.sha256 == _sha256(file)
        assert pl.read_parquet(file).height == descriptor.row_count
        assert dict(pl.read_parquet(file).schema) == SCHEMAS[table]

    manifest_path = directory / awpy_adapter.MANIFEST_NAME
    assert manifest_path.is_file()
    assert Manifest.model_validate_json(manifest_path.read_text()) == manifest
    assert manifest.quality == "complete"
    assert manifest.capabilities["players"].status == "available"
    assert manifest.capabilities["bomb"].status == "absent"


def test_extract_marks_unresolved_identities_partial(tmp_path, monkeypatch):
    request = _prepare(tmp_path, monkeypatch, resolved=False)
    manifest = awpy_adapter.extract(request)
    assert manifest.quality == "partial"


def test_extract_maps_enospc_to_disk_full(tmp_path, monkeypatch):
    request = _prepare(tmp_path, monkeypatch)

    def _no_space(self, *args, **kwargs):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(pl.DataFrame, "write_parquet", _no_space)
    with pytest.raises(AppError) as excinfo:
        awpy_adapter.extract(request)
    assert excinfo.value.code == "DISK_FULL"
    assert excinfo.value.retryable is True


def test_extract_rejects_missing_source(tmp_path, monkeypatch):
    monkeypatch.setattr(awpy_adapter, "Demo", lambda path: _FakeDemo())
    request = ExtractionRequest(
        job_id="j",
        generation_id="g",
        demo_id="d",
        input_path=str(tmp_path / "missing.dem"),
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(AppError) as excinfo:
        awpy_adapter.extract(request)
    assert excinfo.value.code == "SOURCE_MISSING"


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf"), None, "invalid"])
def test_unavailable_clock_cannot_publish_an_invented_tick_rate(tmp_path, monkeypatch, rate):
    request = _prepare(tmp_path, monkeypatch)
    fake = _FakeDemo()
    fake.tick_rate = rate
    monkeypatch.setattr(awpy_adapter, "Demo", lambda path: fake)
    with pytest.raises(AppError) as failure:
        awpy_adapter.extract(request)
    assert failure.value.code == "PARSE_FAILED"
    assert not (tmp_path / "out" / "manifest.json").exists()

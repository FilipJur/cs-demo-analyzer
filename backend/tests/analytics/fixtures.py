"""Authored generation fixtures for the analytics access/identity tests.

Generations are built through the real publication path (staging directory ->
manifest -> ``Artifacts.publish`` -> ``Catalog.complete``), so the analytics
layer is exercised against genuine Parquet files, checksums and catalog state.
Nothing here reads a recorded demo, touches the network or starts a worker.

These builders deliberately mirror the shape of ``tests/helpers.py`` (schema
typed frames, verbatim string ids, missing keys left null); the shared helpers
themselves are not modified.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

import polars as pl
import pytest

from cs_demo_analyzer.analytics import Generation, GenerationPool
from cs_demo_analyzer.domain.contracts import (
    PROFILE_KEY,
    Fingerprint,
    Manifest,
    Snapshot,
    TableDescriptor,
)
from cs_demo_analyzer.domain.tables import SCHEMAS
from cs_demo_analyzer.storage import Artifacts, Catalog
from cs_demo_analyzer.storage.artifacts import MANIFEST_NAME, sha256_file

TABLE_NAMES = tuple(SCHEMAS)

DEMO_ID = "a" * 64
OTHER_DEMO_ID = "b" * 64

TICK_RATE_HZ = 64.0

PLAYER_A = "steam:76561198000000013"
PLAYER_B = "steam:76561198000000021"


# -- table builders ---------------------------------------------------------
def frame(table: str, rows: Iterable[Mapping[str, Any]] | None = None) -> pl.DataFrame:
    """One frozen table from partial dicts; omitted keys are null, not invented."""
    schema = SCHEMAS[table]
    selected = list(rows) if rows is not None else []
    return pl.DataFrame(
        {name: pl.Series(name, [row.get(name) for row in selected], dtype=dtype) for name, dtype in schema.items()}
    )


def state_row(
    ordinal: int,
    tick: int,
    player_id: str | None,
    health: int | None = None,
    *,
    x: float = 0.0,
    y: float = 0.0,
) -> dict[str, Any]:
    """One state observation. ``player_id=None`` models an engine dead entity."""
    alive = player_id is not None if health is None else health > 0
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "player_id": player_id,
        "x": x,
        "y": y,
        "z": 0.0,
        "yaw": 0.0,
        "pitch": 0.0,
        "velocity_x": 0.0,
        "velocity_y": 0.0,
        "velocity_z": 0.0,
        "health": (100 if player_id is not None else 0) if health is None else health,
        "armor": 100 if alive else 0,
        "money": 800 if alive else 0,
        "side": "ct" if alive else None,
        "active_weapon": "ak47" if alive else None,
        "has_bomb": False,
        "is_crouched": False,
        "is_scoped": False,
        "is_reloading": False,
    }


def players_rows(*player_ids: str) -> list[dict[str, Any]]:
    return [
        {
            "player_id": player_id,
            "steam_id": player_id.split(":", 1)[1] if player_id.startswith("steam:") else None,
            "name": player_id,
            "side": "ct",
        }
        for player_id in player_ids
    ]


def round_row(
    round_id: int,
    *,
    start: int | None,
    freeze_end: int | None,
    end: int | None,
    official_end: int | None = None,
    winner: str | None = "ct",
    reason: int | None = 7,
) -> dict[str, Any]:
    return {
        "round_id": round_id,
        "source_round_num": round_id,
        "start_tick": start,
        "freeze_end_tick": freeze_end,
        "end_tick": end,
        "official_end_tick": official_end,
        "winner_side": winner,
        "reason_code": reason,
    }


def dense_state(height: int, player_id: str = PLAYER_A, *, health: int = 100, tick_offset: int = 0) -> pl.DataFrame:
    """Dense state grid built with polars, for materialization-cap tests."""
    return (
        pl.DataFrame({"tick": pl.int_range(tick_offset, tick_offset + height, eager=True, dtype=pl.Int64)})
        .with_columns(
            pl.int_range(0, height, eager=True, dtype=pl.Int64).alias("row_ordinal"),
            pl.lit(player_id).alias("player_id"),
            pl.lit(0.0, dtype=pl.Float32).alias("x"),
            pl.lit(0.0, dtype=pl.Float32).alias("y"),
            pl.lit(0.0, dtype=pl.Float32).alias("z"),
            pl.lit(0.0, dtype=pl.Float32).alias("yaw"),
            pl.lit(0.0, dtype=pl.Float32).alias("pitch"),
            pl.lit(0.0, dtype=pl.Float32).alias("velocity_x"),
            pl.lit(0.0, dtype=pl.Float32).alias("velocity_y"),
            pl.lit(0.0, dtype=pl.Float32).alias("velocity_z"),
            pl.lit(health, dtype=pl.Int32).alias("health"),
            pl.lit(100, dtype=pl.Int32).alias("armor"),
            pl.lit(800, dtype=pl.Int32).alias("money"),
            pl.lit("ct").alias("side"),
            pl.lit("ak47").alias("active_weapon"),
            pl.lit(False).alias("has_bomb"),
            pl.lit(False).alias("is_crouched"),
            pl.lit(False).alias("is_scoped"),
            pl.lit(False).alias("is_reloading"),
        )
        .select(list(SCHEMAS["player_state"]))
    )


# -- harness ----------------------------------------------------------------
class AnalyticsHarness:
    """Catalog, artifacts and pool over one temporary data root."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.catalog = Catalog(self.root)
        self.artifacts = Artifacts(self.root)
        self.pool = GenerationPool(self.catalog, self.artifacts)

    def close(self) -> None:
        self.catalog.close()

    # -- demos and generations --------------------------------------------
    def register(self, demo_id: str = DEMO_ID, source: str = "/demos/match.dem") -> None:
        raw = self.root / "raw" / demo_id / "source.dem"
        raw.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        raw.write_bytes(b"PBDEMS2\0" + demo_id.encode())
        info = raw.stat()
        self.catalog.register_demo(
            Snapshot(
                demo_id=demo_id,
                raw_path=str(raw),
                size=info.st_size,
                source_path=source,
                fingerprint=Fingerprint(
                    device=info.st_dev,
                    inode=info.st_ino,
                    size=info.st_size,
                    mtime_ns=info.st_mtime_ns,
                    ctime_ns=info.st_ctime_ns,
                ),
            )
        )

    def publish(
        self,
        *,
        demo_id: str = DEMO_ID,
        tables: Mapping[str, pl.DataFrame | list[dict[str, Any]]] | None = None,
        **manifest_overrides: Any,
    ) -> Manifest:
        """Publish one generation through the real staging/validation/catalog path."""
        if self.catalog.get_demo(demo_id) is None:
            self.register(demo_id)
        self.catalog.enqueue(demo_id, force=True)
        job = self.catalog.claim_next()
        assert job is not None and job.demo_id == demo_id, "expected the queued job to be claimable"

        staging = self.artifacts.stage_dir(job)
        descriptors: dict[str, TableDescriptor] = {}
        for table in TABLE_NAMES:
            data = (tables or {}).get(table)
            if data is None:
                data = frame(table)
            elif not isinstance(data, pl.DataFrame):
                data = frame(table, data)
            descriptors[table] = self._write(staging, table, data)

        values: dict[str, Any] = dict(
            demo_id=demo_id,
            job_id=job.id,
            generation_id=job.generation_id,
            profile_key=PROFILE_KEY,
            source_size=4096,
            map_name="de_inferno",
            tick_rate_hz=TICK_RATE_HZ,
        )
        values.update(manifest_overrides)
        manifest = Manifest(**values, tables=descriptors)
        staged = staging / MANIFEST_NAME
        staged.write_text(manifest.model_dump_json(indent=2) + "\n")
        published, final_path = self.artifacts.publish(job, staged)
        self.catalog.complete(job.id, published, final_path)
        return published

    def open(self, generation_id: str | None = None, demo_id: str = DEMO_ID) -> Generation:
        return self.pool.open(demo_id, generation_id)

    # -- paths -------------------------------------------------------------
    def generation_dir(self, generation_id: str, demo_id: str = DEMO_ID) -> Path:
        return Path(self.artifacts.generation_dir(demo_id, generation_id))

    def manifest_path(self, generation_id: str, demo_id: str = DEMO_ID) -> Path:
        return self.generation_dir(generation_id, demo_id) / MANIFEST_NAME

    def _write(self, directory: Path, table: str, data: pl.DataFrame) -> TableDescriptor:
        data = data.select(list(SCHEMAS[table]))
        path = directory / f"{table}.parquet"
        data.write_parquet(path)
        return TableDescriptor(path=path.name, row_count=data.height, sha256=sha256_file(path))


# -- pytest fixtures --------------------------------------------------------
@pytest.fixture
def harness(tmp_path: Path):
    instance = AnalyticsHarness(tmp_path / "data")
    try:
        yield instance
    finally:
        instance.close()

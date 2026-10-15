"""Real Parquet/catalog helpers for storage tests.

Datasets are built from ``domain.tables.SCHEMAS`` with genuine checksums and row
counts, so publication and validation are exercised against real files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import polars as pl

from cs_demo_analyzer.domain.contracts import (
    PROFILE_KEY,
    Fingerprint,
    JobRecord,
    Manifest,
    Snapshot,
    TableDescriptor,
)
from cs_demo_analyzer.domain.tables import SCHEMAS
from cs_demo_analyzer.storage import Artifacts, Catalog

TABLE_NAMES = tuple(SCHEMAS)

SAMPLE_ROWS: dict[str, list[dict]] = {
    "players": [
        {"player_id": "steam:76561198000000001", "steam_id": "76561198000000001", "name": "alpha", "side": "ct"},
        {"player_id": "unresolved:roster:11", "steam_id": None, "name": None, "side": None},
    ],
    "rounds": [
        {
            "round_id": 1,
            "source_round_num": 1,
            "start_tick": 0,
            "freeze_end_tick": 100,
            "end_tick": 250,
            "official_end_tick": 250,
            "winner_side": "ct",
            "reason_code": 7,
        }
    ],
    "player_state": [
        {
            "row_ordinal": 0,
            "tick": 100,
            "player_id": "steam:76561198000000001",
            "x": 1.5,
            "y": -2.25,
            "z": 0.0,
            "yaw": 179.9,
            "pitch": -3.0,
            "velocity_x": 0.0,
            "velocity_y": 12.5,
            "velocity_z": 0.0,
            "health": 100,
            "armor": 100,
            "money": 800,
            "side": "ct",
            "active_weapon": "weapon_ak47",
            "has_bomb": False,
            "is_crouched": False,
            "is_scoped": False,
            "is_reloading": False,
        },
        {
            "row_ordinal": 1,
            "tick": 100,
            "player_id": None,
            "x": None,
            "y": None,
            "z": None,
            "yaw": None,
            "pitch": None,
            "velocity_x": None,
            "velocity_y": None,
            "velocity_z": None,
            "health": 0,
            "armor": 0,
            "money": 0,
            "side": None,
            "active_weapon": None,
            "has_bomb": None,
            "is_crouched": None,
            "is_scoped": None,
            "is_reloading": None,
        },
    ],
    "kills": [
        {
            "row_ordinal": 0,
            "tick": 2177,
            "attacker_id": "steam:76561198000000001",
            "victim_id": "steam:76561198000000002",
            "assister_id": None,
            "weapon": "ak47",
            "headshot": True,
            "attacker_entity_id": 12,
            "attacker_entity_serial": 3,
            "victim_entity_id": 21,
            "victim_entity_serial": 5,
        }
    ],
    "damages": [
        {
            "row_ordinal": 0,
            "tick": 2177,
            "attacker_id": "steam:76561198000000001",
            "victim_id": "steam:76561198000000002",
            "damage_health": 100,
            "damage_armor": 0,
            "weapon": "ak47",
        }
    ],
    "shots": [
        {
            "row_ordinal": 0,
            "tick": 2175,
            "player_id": "steam:76561198000000001",
            "weapon": "ak47",
            "x": 10.0,
            "y": 20.0,
            "z": 30.0,
            "yaw": -45.0,
            "pitch": 1.0,
        }
    ],
    "bomb": [
        {
            "row_ordinal": 0,
            "tick": 640,
            "player_id": "steam:76561198000000001",
            "action": "planted",
            "bombsite": "a",
            "x": 0.0,
            "y": 0.0,
            "z": -128.0,
        }
    ],
}


def build_frame(table: str, rows: list[dict] | None = None) -> pl.DataFrame:
    """One frozen table, tolerating null rows."""
    schema = SCHEMAS[table]
    selected = SAMPLE_ROWS[table] if rows is None else rows
    columns = {
        column: pl.Series(column, [row.get(column) for row in selected], dtype=dtype)
        for column, dtype in schema.items()
    }
    return pl.DataFrame(columns)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class DatasetBuilder:
    """Writes generation-shaped datasets into one directory."""

    def __init__(self, directory: Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)

    def make(
        self,
        *,
        demo_id: str,
        job_id: str,
        generation_id: str,
        tables: dict[str, pl.DataFrame] | None = None,
        omit: set[str] | None = None,
        extra: dict[str, pl.DataFrame] | None = None,
        descriptor_overrides: dict[str, dict] | None = None,
        manifest_overrides: dict | None = None,
    ) -> tuple[Path, Manifest]:
        omit = omit or set()
        descriptor_overrides = descriptor_overrides or {}
        descriptors: dict[str, TableDescriptor] = {}
        for table in TABLE_NAMES:
            if table in omit:
                continue
            frame = (tables or {}).get(table)
            descriptors[table] = self.write_table(table, build_frame(table) if frame is None else frame)
        for name, frame in (extra or {}).items():
            descriptors[name] = self.write_table(name, frame)
        for table, patch in descriptor_overrides.items():
            descriptors[table] = descriptors[table].model_copy(update=patch)
        values = dict(
            demo_id=demo_id,
            job_id=job_id,
            generation_id=generation_id,
            profile_key=PROFILE_KEY,
            source_size=301_894_448,
            map_name="de_inferno",
            tick_rate_hz=64.0,
            quality="complete",
        )
        values.update(manifest_overrides or {})
        manifest = Manifest(**values, tables=descriptors)
        path = self.directory / "manifest.json"
        path.write_text(manifest.model_dump_json(indent=2) + "\n")
        return path, manifest

    def write_table(self, table: str, frame: pl.DataFrame) -> TableDescriptor:
        name = f"{table}.parquet"
        path = self.directory / name
        frame.write_parquet(path)
        return TableDescriptor(path=name, row_count=frame.height, sha256=sha256_file(path))


class Harness:
    """Catalog plus artifacts over one shared temporary data root."""

    def __init__(self, catalog: Catalog, artifacts: Artifacts) -> None:
        self.catalog = catalog
        self.artifacts = artifacts
        self.root = catalog.data_root

    def demo(self, demo_id: str = "a" * 64, source: str = "/demos/match.dem") -> None:
        raw = self.root / "raw" / demo_id / "source.dem"
        raw.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not raw.exists():
            raw.write_bytes(b"PBDEMS2\0" + demo_id.encode())
        stat = raw.stat()
        self.catalog.register_demo(
            Snapshot(
                demo_id=demo_id,
                raw_path=str(raw),
                size=stat.st_size,
                source_path=source,
                fingerprint=Fingerprint(
                    device=stat.st_dev,
                    inode=stat.st_ino,
                    size=stat.st_size,
                    mtime_ns=stat.st_mtime_ns,
                    ctime_ns=stat.st_ctime_ns,
                ),
            )
        )

    def job(self, demo_id: str = "a" * 64, *, force: bool = False) -> JobRecord:
        if self.catalog.get_demo(demo_id) is None:
            self.demo(demo_id)
        self.catalog.enqueue(demo_id, force=force)
        job = self.catalog.claim_next()
        assert job is not None, "expected a claimable job"
        assert job.demo_id == demo_id
        return job

    def stage(self, job: JobRecord, **builder_kwargs) -> tuple[Path, Manifest]:
        builder_kwargs.setdefault("demo_id", job.demo_id)
        builder_kwargs.setdefault("job_id", job.id)
        builder_kwargs.setdefault("generation_id", job.generation_id)
        return DatasetBuilder(self.artifacts.stage_dir(job)).make(**builder_kwargs)

    def publish(self, job: JobRecord, **builder_kwargs) -> tuple[Manifest, Path]:
        manifest_path, _ = self.stage(job, **builder_kwargs)
        return self.artifacts.publish(job, manifest_path)

    def run(self, demo_id: str = "a" * 64, *, force: bool = False, **builder_kwargs):
        job = self.job(demo_id, force=force)
        manifest, final_path = self.publish(job, **builder_kwargs)
        self.catalog.complete(job.id, manifest, final_path)
        return job, manifest, final_path

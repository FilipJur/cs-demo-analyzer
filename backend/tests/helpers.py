"""Private fixtures shared by the Phase 0 application and HTTP test modules.

Every generation here is produced through the real storage services
(``Catalog``/``Artifacts``): canonical Parquet tables, a hashed manifest and a
catalog.sqlite. Nothing mocks a data response, so assertions observe the same
code paths the coordinator and the API use in production.

Timings, ticks and identifiers are fixed constants so that window, generation
and sampling assertions never drift. Imported as a plain module (pytest puts the
test directory on ``sys.path``); deliberately not a ``conftest.py`` so no global
fixture or plugin state leaks into other suites.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import polars as pl
from fastapi.testclient import TestClient

from cs_demo_analyzer.application import Application
from cs_demo_analyzer.config import Settings
from cs_demo_analyzer.domain.contracts import Fingerprint, Manifest, Snapshot, TableDescriptor
from cs_demo_analyzer.domain.tables import SCHEMAS
from cs_demo_analyzer.storage.artifacts import MANIFEST_NAME, sha256_file

API = "/api/v1"
BASE_URL = "http://127.0.0.1:8765"

TICK_RATE_HZ = 64.0

# A 64-hex content digest, exactly like ``snapshot_source`` derives demo ids.
DEMO_ID = "3a7f19c4" * 8
PENDING_DEMO_ID = "9c1eb042" * 8

# Seventeen-digit account ids exceed IEEE-754 integer precision, so every
# response must carry them as untouched strings.
STEAM_A = "76561198000000013"
STEAM_B = "76561198000000021"
STEAM_C = "76561198000000039"
STEAM_D = "76561198000000047"
PLAYER_A, PLAYER_B = f"steam:{STEAM_A}", f"steam:{STEAM_B}"
PLAYER_C, PLAYER_D = f"steam:{STEAM_C}", f"steam:{STEAM_D}"
PLAYER_IDS = (PLAYER_A, PLAYER_B, PLAYER_C, PLAYER_D)
# Roster entry with no resolvable identity, kept verbatim as an unresolved key.
UNRESOLVED_PLAYER = "unresolved:roster:11"

# Round one of the "inferno" generation: an 8 Hz sampling grid over 1200..1400.
ROUND_ONE_FREEZE_END = 1200
ROUND_ONE_END = 1400
ALIGNED_TICKS = tuple(range(ROUND_ONE_FREEZE_END, ROUND_ONE_END + 1, 8))
OFF_GRID_TICK = 1253  # neither on the grid nor an event tick
KILL_TICKS = (1252, 1300, 1350)
OUT_OF_ROUND_KILL_TICK = 1450
SAMPLES_IN_ROUND_ONE = len(ALIGNED_TICKS) * len(PLAYER_IDS) + 2 + 4 + 4


# -- identities -------------------------------------------------------------
def players_rows() -> list[dict[str, Any]]:
    """Roster with exact string ids, one null name and one unresolved entry."""
    return [
        {"player_id": PLAYER_A, "steam_id": STEAM_A, "name": "alpha", "side": "ct"},
        {"player_id": PLAYER_B, "steam_id": STEAM_B, "name": "bravo", "side": "ct"},
        {"player_id": PLAYER_C, "steam_id": STEAM_C, "name": None, "side": "t"},
        {"player_id": PLAYER_D, "steam_id": STEAM_D, "name": "delta", "side": "t"},
        {"player_id": UNRESOLVED_PLAYER, "steam_id": None, "name": None, "side": "unknown"},
    ]


def state_row(ordinal: int, tick: int, player_id: str | None) -> dict[str, Any]:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "player_id": player_id,
        "x": -1234.5,
        "y": 987.25,
        "z": 64.0,
        "yaw": 12.5,
        "pitch": -3.25,
        "velocity_x": 0.0,
        "velocity_y": 0.0,
        "velocity_z": 0.0,
        "health": 0 if player_id is None else 100,
        "armor": 0 if player_id is None else 100,
        "money": 800,
        "side": "ct" if player_id in (PLAYER_A, PLAYER_B) else "t",
        "active_weapon": "ak47",
        "has_bomb": player_id == PLAYER_C,
        "is_crouched": False,
        "is_scoped": False,
        "is_reloading": False,
    }


def kill_row(
    ordinal: int,
    tick: int,
    attacker_id: str | None,
    victim_id: str | None,
    weapon: str | None,
    headshot: bool | None,
) -> dict[str, Any]:
    return {
        "row_ordinal": ordinal,
        "tick": tick,
        "attacker_id": attacker_id,
        "victim_id": victim_id,
        "assister_id": None,
        "weapon": weapon,
        "headshot": headshot,
        "attacker_entity_id": 1,
        "attacker_entity_serial": 10,
        "victim_entity_id": 2,
        "victim_entity_serial": 20,
    }


def dense_player_state(player_ids: Iterable[str], ticks: Iterable[int]) -> pl.DataFrame:
    """Dense state grid built with polars instead of one dict per observation."""
    base = pl.DataFrame({"tick": pl.Series(list(ticks), dtype=pl.Int64)}).join(
        pl.DataFrame({"player_id": pl.Series(list(player_ids), dtype=pl.String)}), how="cross"
    )
    return base.with_columns(
        pl.int_range(0, base.height, eager=True).alias("row_ordinal"),
        pl.lit(-1234.5, dtype=pl.Float32).alias("x"),
        pl.lit(987.25, dtype=pl.Float32).alias("y"),
        pl.lit(64.0, dtype=pl.Float32).alias("z"),
        pl.lit(12.5, dtype=pl.Float32).alias("yaw"),
        pl.lit(-3.25, dtype=pl.Float32).alias("pitch"),
        pl.lit(0.0, dtype=pl.Float32).alias("velocity_x"),
        pl.lit(0.0, dtype=pl.Float32).alias("velocity_y"),
        pl.lit(0.0, dtype=pl.Float32).alias("velocity_z"),
        pl.lit(100, dtype=pl.Int32).alias("health"),
        pl.lit(100, dtype=pl.Int32).alias("armor"),
        pl.lit(800, dtype=pl.Int32).alias("money"),
        pl.lit("ct").alias("side"),
        pl.lit("ak47").alias("active_weapon"),
        pl.lit(False).alias("has_bomb"),
        pl.lit(False).alias("is_crouched"),
        pl.lit(False).alias("is_scoped"),
        pl.lit(False).alias("is_reloading"),
    ).select(list(SCHEMAS["player_state"]))


# -- generations ------------------------------------------------------------
def inferno_tables() -> dict[str, Any]:
    """Round-one generation with off-grid event ticks, null actors and a partial round."""
    rows: list[dict[str, Any]] = []
    ordinal = 0

    def add(tick: int, player_id: str | None) -> None:
        nonlocal ordinal
        rows.append(state_row(ordinal, tick, player_id))
        ordinal += 1

    for tick in ALIGNED_TICKS:
        for player_id in PLAYER_IDS:
            add(tick, player_id)
    for player_id in (PLAYER_A, PLAYER_B):
        add(KILL_TICKS[0], player_id)
    for player_id in (PLAYER_A, PLAYER_B):
        add(OFF_GRID_TICK, player_id)
    for tick in KILL_TICKS[1:]:
        for player_id in PLAYER_IDS:
            add(tick, player_id)
    add(KILL_TICKS[0], None)  # dead/unknown reference: never joined by name or coordinate

    return {
        "players": players_rows(),
        "rounds": [
            {
                "round_id": 1,
                "source_round_num": 1,
                "start_tick": 1000,
                "freeze_end_tick": ROUND_ONE_FREEZE_END,
                "end_tick": ROUND_ONE_END,
                "official_end_tick": 1416,
                "winner_side": "ct",
                "reason_code": 8,
            },
            {
                "round_id": 2,
                "source_round_num": 2,
                "start_tick": 1500,
                "freeze_end_tick": 1700,
                "end_tick": 1900,
                "official_end_tick": 1916,
                "winner_side": "t",
                "reason_code": 7,
            },
            {
                "round_id": 3,
                "source_round_num": None,
                "start_tick": None,
                "freeze_end_tick": None,
                "end_tick": None,
                "official_end_tick": None,
                "winner_side": None,
                "reason_code": None,
            },
        ],
        "player_state": rows,
        "kills": [
            kill_row(0, KILL_TICKS[0], PLAYER_A, PLAYER_B, "ak47", True),
            kill_row(1, KILL_TICKS[1], None, PLAYER_C, None, None),
            kill_row(2, KILL_TICKS[2], PLAYER_D, None, "hegrenade", False),
            kill_row(3, OUT_OF_ROUND_KILL_TICK, PLAYER_A, PLAYER_D, "deagle", False),
        ],
        "damages": [
            {
                "row_ordinal": 0,
                "tick": KILL_TICKS[0],
                "attacker_id": PLAYER_A,
                "victim_id": PLAYER_B,
                "damage_health": 27,
                "damage_armor": 0,
                "weapon": "ak47",
            },
            {
                "row_ordinal": 1,
                "tick": KILL_TICKS[2],
                "attacker_id": PLAYER_D,
                "victim_id": None,
                "damage_health": 12,
                "damage_armor": 3,
                "weapon": "hegrenade",
            },
        ],
        "shots": [
            {
                "row_ordinal": 0,
                "tick": KILL_TICKS[0],
                "player_id": PLAYER_A,
                "weapon": "ak47",
                "x": -1234.5,
                "y": 987.25,
                "z": 64.0,
                "yaw": 12.5,
                "pitch": -3.25,
            }
        ],
        "bomb": [
            {
                "row_ordinal": 0,
                "tick": 1310,
                "player_id": PLAYER_C,
                "action": "planted",
                "bombsite": "B",
                "x": -1000.0,
                "y": 700.0,
                "z": 64.0,
            }
        ],
    }


def mirage_tables() -> dict[str, Any]:
    """Superseding generation: different rounds and ticks for pinning assertions."""
    return {
        "players": players_rows(),
        "rounds": [
            {
                "round_id": 1,
                "source_round_num": 1,
                "start_tick": 3000,
                "freeze_end_tick": 3200,
                "end_tick": 3400,
                "official_end_tick": 3416,
                "winner_side": "t",
                "reason_code": 1,
            }
        ],
        "player_state": [state_row(0, 3200, PLAYER_A), state_row(1, 3200, PLAYER_B)],
        "kills": [kill_row(0, 3250, PLAYER_A, PLAYER_B, "m4a1", False)],
        "damages": [],
        "shots": [],
        "bomb": [],
    }


def oversized_tables() -> dict[str, Any]:
    """One very long round with 120,004 in-range player samples."""
    return {
        "players": players_rows(),
        "rounds": [
            {
                "round_id": 1,
                "source_round_num": 1,
                "start_tick": 1000,
                "freeze_end_tick": 1000,
                "end_tick": 31000,
                "official_end_tick": 31016,
                "winner_side": "ct",
                "reason_code": 8,
            }
        ],
        "player_state": dense_player_state(PLAYER_IDS, range(1000, 31001)),
        "kills": [],
        "damages": [],
        "shots": [],
        "bomb": [],
    }


# -- application harness ----------------------------------------------------
def settings_for(tmp_path: Path) -> Settings:
    """Isolated data root plus a stub installation so no real Steam path is touched."""
    install = tmp_path / "install"
    install.mkdir(exist_ok=True)
    return Settings(
        data_root=tmp_path / "data",
        install_path=install,
        settle_seconds=0.0,
        scan_seconds=3600.0,
        poll_seconds=1.0,
        reserve_bytes=0,
        worker_timeout=30.0,
    )


def create_application(tmp_path: Path) -> Application:
    return Application(settings_for(tmp_path))


def register_demo(app: Application, demo_id: str):
    """Persist exactly the catalog state the ingestion service would leave behind."""
    raw_dir = app.settings.data_root / "raw" / demo_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw = raw_dir / "source.dem"
    raw.write_bytes(b"PBDEMS2\0" + demo_id.encode("ascii"))
    snapshot = Snapshot(
        demo_id=demo_id,
        raw_path=str(raw),
        size=raw.stat().st_size,
        source_path=str(raw),
        fingerprint=Fingerprint.from_path(raw),
    )
    app.catalog.register_demo(snapshot)
    app.catalog.set_source(str(raw), snapshot.fingerprint, "imported", demo_id=demo_id)
    demo = app.catalog.get_demo(demo_id)
    assert demo is not None and demo.raw_path == str(raw)
    return demo


def start_job(app: Application, demo_id: str, *, force: bool = False):
    """Queue an extraction and claim it, leaving the job in the running state."""
    queued = app.catalog.enqueue(demo_id, force=force)
    claimed = app.catalog.claim_next()
    assert claimed is not None and claimed.id == queued.id
    return claimed


def start_reprocess(app: Application, demo_id: str):
    """Deliberate reprocess through the coordinator entry point, claimed and running."""
    accepted = app.reprocess(demo_id)
    assert accepted.job_id is not None
    claimed = app.catalog.claim_next()
    assert claimed is not None and claimed.id == accepted.job_id
    return claimed


def generation_manifest(data_root: Path, demo_id: str, generation_id: str) -> Path:
    return data_root / "datasets" / demo_id / generation_id / MANIFEST_NAME


def resolve_generation(app: Application, demo_id: str, generation_id: str) -> Path | None:
    """Manifest path of a registered generation, coerced to a Path for comparison."""
    value = app.catalog.generation_path(demo_id, generation_id)
    return None if value is None else Path(value)


def _frame(table: str, rows: Any) -> pl.DataFrame:
    frame = rows if isinstance(rows, pl.DataFrame) else pl.DataFrame(rows, schema=SCHEMAS[table], orient="row")
    return frame.select(list(SCHEMAS[table]))


def publish_generation(
    app: Application,
    job,
    *,
    map_name: str,
    tables: dict[str, Any],
    warnings: Iterable[str] = (),
) -> tuple[Manifest, Path]:
    """Write a staged seven-table generation and publish it, as the parser would."""
    unknown = set(tables) ^ set(SCHEMAS)
    assert not unknown, f"generation tables must be exactly the frozen profile: {sorted(unknown)}"
    stage = app.artifacts.stage_dir(job)
    descriptors: dict[str, TableDescriptor] = {}
    for table in SCHEMAS:
        frame = _frame(table, tables[table])
        path = stage / f"{table}.parquet"
        frame.write_parquet(path)
        descriptors[table] = TableDescriptor(
            path=path.name, row_count=frame.height, sha256=sha256_file(path)
        )
    demo = app.catalog.get_demo(job.demo_id)
    manifest = Manifest(
        demo_id=job.demo_id,
        job_id=job.id,
        generation_id=job.generation_id,
        source_size=demo.size,
        map_name=map_name,
        tick_rate_hz=TICK_RATE_HZ,
        tables=descriptors,
        warnings=list(warnings),
    )
    staged = stage / MANIFEST_NAME
    staged.write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return app.artifacts.publish(job, staged)


def commit_generation(
    app: Application,
    demo_id: str,
    *,
    map_name: str,
    tables: dict[str, Any] | None = None,
    warnings: Iterable[str] = (),
    force: bool = True,
) -> Manifest:
    """Publish and commit one generation, returning its manifest."""
    job = start_job(app, demo_id, force=force)
    manifest, final = publish_generation(
        app, job, map_name=map_name, tables=inferno_tables() if tables is None else tables, warnings=warnings
    )
    app.catalog.complete(job.id, manifest, final)
    return manifest


def restart(app: Application, monkeypatch) -> None:
    """Run the real startup path while the coordinator thread only waits.

    ``start()`` performs recovery synchronously before the coordinator loop
    begins; stubbing the loop body keeps a requeued job from being claimed by a
    parser subprocess while the test inspects the recovered state.
    """
    monkeypatch.setattr(app, "_loop", app._stop.wait)
    app.start(discover=False)


@dataclass
class Api:
    """A real application and a loopback HTTP client bound to it."""

    app: Application
    client: TestClient
    first: Manifest
    second: Manifest

    @property
    def data_root(self) -> Path:
        return self.app.settings.data_root

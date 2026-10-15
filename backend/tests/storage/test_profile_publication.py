"""Behavior of profile-aware publication, reading and head selection.

A generation is validated against the table contract of *its own* named profile:
an extended generation publishes and reads its extra tables, a mislabeled
``profile_key`` is refused, a foundation generation keeps reading exactly as
before, and the reported demo head prefers the current extended profile without
hiding the older generation.
"""

from __future__ import annotations

import polars as pl
import pytest

from cs_demo_analyzer.analytics import GenerationPool
from cs_demo_analyzer.domain.contracts import (
    PROFILE_KEY,
    RECONSTRUCTION_PROFILE_KEY,
    RECONSTRUCTION_PROFILE_NAME,
    AppError,
    ErrorResponse,
    JobRecord,
)
from cs_demo_analyzer.domain.tables import RECONSTRUCTION_SCHEMAS, SCHEMAS

from .support import Harness

DEMO = "a" * 64

#: One recorded value per column, so every table carries a real (non-empty) row.
_ROWS: dict[str, dict] = {
    "kills": {"thrusmoke": True, "hitgroup_code": 1, "attacker_x": 10.0},
    "damages": {"hitgroup_name": "chest"},
    "shots": {"scoped": True, "inaccuracy": 0.25},
    "bomb": {"entity_id": 9},
    "player_state_ext": {
        "velocity": 3.7,
        "smoke_grenades": 1,
        "is_blinded": True,
        "inventory": "ak47,glock,smokegrenade",
    },
    "blinds": {"duration_seconds": 3.5, "victim_x": 20.0},
    "smokes": {"start_tick": 90, "end_tick": 1800, "still_active_at_end": True},
    "fires": {"start_tick": 950, "end_tick": 1800, "kind": "inferno"},
    "grenades": {"tick": 500, "kind": "smoke", "entity_id": 584},
    "item_events": {"action": "purchase", "item": "smokegrenade", "cost": 300},
    "round_economy": {"round_id": 1, "buy_type": "pistol", "n_players": 5},
    "player_lifecycle": {"kind": "disconnect", "player_id": "steam:76561198000000001"},
}


def _canonical(table: str) -> pl.DataFrame:
    """One-row canonical frame shaped exactly like ``table``'s declared schema."""
    schema = RECONSTRUCTION_SCHEMAS[table]
    row = _ROWS.get(table, {})
    return pl.DataFrame(
        {name: pl.Series(name, [row.get(name)], dtype=dtype) for name, dtype in schema.items()}
    )


def _frames() -> dict[str, pl.DataFrame]:
    return {table: _canonical(table) for table in RECONSTRUCTION_SCHEMAS}


def _builder_kwargs() -> dict:
    frames = _frames()
    return {
        "tables": {table: frames[table] for table in SCHEMAS},
        "extra": {table: frames[table] for table in RECONSTRUCTION_SCHEMAS if table not in SCHEMAS},
        "manifest_overrides": {
            "profile": RECONSTRUCTION_PROFILE_NAME,
            "profile_key": RECONSTRUCTION_PROFILE_KEY,
        },
    }


def _extended_job(harness: Harness, *, force: bool = True) -> JobRecord:
    if harness.catalog.get_demo(DEMO) is None:
        harness.demo(DEMO)
    queued = harness.catalog.enqueue(DEMO, force=force, profile_key=RECONSTRUCTION_PROFILE_KEY)
    job = harness.catalog.claim_next()
    assert job is not None and job.id == queued.id
    return job


def _publish_extended(harness: Harness, job: JobRecord, **builder_overrides):
    kwargs = _builder_kwargs()
    kwargs.update(builder_overrides)
    manifest_path, _ = harness.stage(job, **kwargs)
    return harness.artifacts.publish(job, manifest_path)


def test_extended_generation_publishes_and_reads_its_own_tables(harness: Harness):
    job = _extended_job(harness)
    manifest, final = _publish_extended(harness, job)
    harness.catalog.complete(job.id, manifest, final)

    assert manifest.profile == RECONSTRUCTION_PROFILE_NAME
    assert set(manifest.tables) == set(RECONSTRUCTION_SCHEMAS)
    assert harness.artifacts.validate(final) == manifest

    pool = GenerationPool(harness.catalog, harness.artifacts)
    gen = pool.open(DEMO, job.generation_id)
    assert gen.profile_key == RECONSTRUCTION_PROFILE_KEY
    assert gen.manifest.profile == RECONSTRUCTION_PROFILE_NAME
    assert gen.rounds.columns == list(RECONSTRUCTION_SCHEMAS["rounds"])

    smokes = pool.read(gen, "smokes", predicate=pl.col("start_tick") == 90)
    assert smokes.height == 1
    assert smokes["still_active_at_end"].to_list() == [True]
    lifecycle = pool.read(gen, "player_lifecycle", columns=["kind", "player_id"])
    assert lifecycle["kind"].to_list() == ["disconnect"]
    extended = pool.read(gen, "player_state_ext", columns=["row_ordinal", "is_blinded"])
    assert extended["is_blinded"].to_list() == [True]
    kills = pool.read(gen, "kills", columns=["row_ordinal", "thrusmoke", "hitgroup_code"])
    assert kills["thrusmoke"].to_list() == [True]


def test_foundation_generation_keeps_its_exact_contract(harness: Harness):
    job, manifest, final = harness.run(DEMO)

    assert manifest.profile == "foundation-v1"
    assert manifest.profile_key == PROFILE_KEY
    assert set(manifest.tables) == set(SCHEMAS)
    assert harness.artifacts.validate(final) == manifest

    pool = GenerationPool(harness.catalog, harness.artifacts)
    gen = pool.open(DEMO, job.generation_id)
    assert gen.profile_key == PROFILE_KEY
    assert list(gen.rounds.columns) == list(SCHEMAS["rounds"])
    assert list(gen.players.columns) == list(SCHEMAS["players"])
    state = pool.read(gen, "player_state")
    assert list(state.columns) == list(SCHEMAS["player_state"])
    frozen = pool.read(gen, "kills")
    assert list(frozen.columns) == list(SCHEMAS["kills"])
    assert "thrusmoke" not in frozen.columns


def test_mislabeled_profile_key_is_refused_at_publication(harness: Harness):
    job = _extended_job(harness)

    with pytest.raises(AppError) as error:
        _publish_extended(
            harness,
            job,
            manifest_overrides={
                "profile": RECONSTRUCTION_PROFILE_NAME,
                "profile_key": PROFILE_KEY,
            },
        )
    assert error.value.code == "ARTIFACT_INVALID"
    assert "profile" in error.value.message


def test_foundation_manifest_cannot_claim_extended_tables(harness: Harness):
    job = harness.job(DEMO)

    with pytest.raises(AppError) as error:
        harness.publish(job, extra={"blinds": _canonical("blinds")})
    assert error.value.code == "ARTIFACT_INVALID"
    assert "blinds" in error.value.message


def test_extended_tables_and_columns_are_unavailable_on_a_foundation_generation(harness: Harness):
    harness.run(DEMO)
    pool = GenerationPool(harness.catalog, harness.artifacts)
    gen = pool.open(DEMO)

    with pytest.raises(AppError) as missing_table:
        pool.read(gen, "blinds")
    assert missing_table.value.code == "INVALID_ARGUMENT"
    assert "blinds" in missing_table.value.message

    with pytest.raises(AppError) as missing_column:
        pool.read(gen, "kills", columns=["row_ordinal", "thrusmoke"])
    assert missing_column.value.code == "INVALID_ARGUMENT"
    assert "thrusmoke" in missing_column.value.message


def test_publication_requires_every_extended_table_file(harness: Harness):
    job = _extended_job(harness)
    kwargs = _builder_kwargs()
    kwargs["extra"] = {table: frame for table, frame in kwargs["extra"].items() if table != "grenades"}

    with pytest.raises(AppError) as error:
        _publish_extended(harness, job, **kwargs)
    assert error.value.code == "ARTIFACT_INVALID"
    assert "grenades" in error.value.message


def test_demo_head_prefers_the_default_profile_without_hiding_the_older_generation(harness: Harness):
    foundation_job, foundation_manifest, foundation_path = harness.run(DEMO)
    extended_job = _extended_job(harness)
    extended_manifest, extended_path = _publish_extended(harness, extended_job)
    harness.catalog.complete(extended_job.id, extended_manifest, extended_path)

    demo = harness.catalog.get_demo(DEMO)
    assert demo.generation_id == extended_job.generation_id
    assert demo.manifest_path == str(extended_path)
    # The superseded generation stays registered, readable and still valid.
    assert harness.catalog.generation_path(DEMO, foundation_job.generation_id) == foundation_path
    assert harness.artifacts.validate(foundation_path) == foundation_manifest
    pool = GenerationPool(harness.catalog, harness.artifacts)
    assert pool.open(DEMO, foundation_job.generation_id).profile_key == PROFILE_KEY
    assert pool.open(DEMO).generation_id == extended_job.generation_id


def test_enqueue_scopes_one_active_job_per_demo_and_profile(harness: Harness):
    harness.demo(DEMO)

    foundation = harness.catalog.enqueue(DEMO)
    extended = harness.catalog.enqueue(DEMO, profile_key=RECONSTRUCTION_PROFILE_KEY)
    assert foundation.id != extended.id
    assert foundation.profile_key == PROFILE_KEY
    assert extended.profile_key == RECONSTRUCTION_PROFILE_KEY
    # Each profile still coalesces its own active job.
    assert harness.catalog.enqueue(DEMO).id == foundation.id
    assert harness.catalog.enqueue(DEMO, profile_key=RECONSTRUCTION_PROFILE_KEY).id == extended.id
    assert harness.catalog.enqueue(DEMO, force=True).id == foundation.id
    assert len(harness.catalog.list_jobs()) == 2


def test_enqueue_rejects_an_unsupported_profile_key(harness: Harness):
    harness.demo(DEMO)

    with pytest.raises(AppError) as error:
        harness.catalog.enqueue(DEMO, profile_key="reconstruction-v9:awpy-9.9.9")
    assert error.value.code == "INVALID_PROFILE"
    assert harness.catalog.list_jobs() == [], "no durable job may be created for an unknown profile"
    # The demo is still extractable under a supported profile.
    assert harness.catalog.enqueue(DEMO).profile_key == PROFILE_KEY


def test_a_failed_extended_reprocess_leaves_the_foundation_generation_readable(harness: Harness):
    good_job, good_manifest, good_path = harness.run(DEMO)
    extended_job = _extended_job(harness)
    harness.stage(extended_job, **_builder_kwargs())
    harness.catalog.fail(
        extended_job.id,
        ErrorResponse(code="PARSE_FAILED", message="extended parser rejected the recording", stage="parse"),
    )

    assert harness.catalog.get_job(extended_job.id).state == "failed"
    assert harness.artifacts.validate(good_path) == good_manifest
    demo = harness.catalog.get_demo(DEMO)
    assert demo.generation_id == good_job.generation_id
    assert demo.manifest_path == str(good_path)
    # The foundation head is reused instead of being silently re-extracted.
    assert harness.catalog.enqueue(DEMO).id == good_job.id

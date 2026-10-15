"""Behavior of artifact staging, validation and publication."""

from __future__ import annotations

import os
from pathlib import Path

import polars as pl
import pytest

from cs_demo_analyzer.domain.contracts import AppError, ErrorResponse
from cs_demo_analyzer.storage import artifacts as artifacts_module
from cs_demo_analyzer.storage.artifacts import MANIFEST_NAME

from .support import TABLE_NAMES, DatasetBuilder, Harness, build_frame, sha256_file

DEMO = "a" * 64


def _publish_failure(code: str = "ARTIFACT_INVALID") -> ErrorResponse:
    return ErrorResponse(code=code, message=f"{code} during artifact test", stage="publish")


def _stage_and_publish(harness: Harness, *, force: bool = False, **builder_kwargs):
    job = harness.job(DEMO, force=force)
    stage = harness.artifacts.stage_dir(job)
    manifest_path, _ = harness.stage(job, **builder_kwargs)
    manifest, final_path = harness.artifacts.publish(job, manifest_path)
    return job, stage, manifest, final_path


def test_stage_dir_is_scoped_to_the_job_and_generation(harness: Harness):
    job = harness.job(DEMO)
    stage = harness.artifacts.stage_dir(job)

    assert stage == harness.root / "staging" / job.id / job.generation_id
    assert stage.is_dir()
    assert harness.artifacts.stage_dir(job) == stage

    unsafe = job.model_copy(update={"generation_id": "../escape"})
    with pytest.raises(AppError) as error:
        harness.artifacts.stage_dir(unsafe)
    assert error.value.code == "INVALID_ARGUMENT"


def test_publish_moves_a_validated_generation_into_place(harness: Harness):
    job, stage, manifest, final_path = _stage_and_publish(harness)

    assert final_path == harness.root / "datasets" / DEMO / job.generation_id / MANIFEST_NAME
    assert {entry.name for entry in final_path.parent.iterdir()} == {
        f"{table}.parquet" for table in TABLE_NAMES
    } | {MANIFEST_NAME}

    for table, descriptor in manifest.tables.items():
        path = final_path.parent / descriptor.path
        assert path.name == descriptor.path
        assert path.is_file()
        assert sha256_file(path) == descriptor.sha256
        assert descriptor.sha256 != "0" * 64
    assert manifest.job_id == job.id
    assert harness.artifacts.validate(final_path) == manifest


def test_publish_refuses_an_existing_generation_directory(harness: Harness):
    job = harness.job(DEMO)
    manifest_path, manifest = harness.stage(job)
    final_dir = harness.root / "datasets" / DEMO / job.generation_id
    final_dir.mkdir(parents=True)
    sentinel = final_dir / "keep.txt"
    sentinel.write_text("previous attempt\n")

    with pytest.raises(AppError) as error:
        harness.artifacts.publish(job, manifest_path)
    assert error.value.code == "ARTIFACT_INVALID"
    assert sentinel.read_text() == "previous attempt\n"
    assert {entry.name for entry in final_dir.iterdir()} == {"keep.txt"}
    assert manifest.generation_id == job.generation_id


def test_publish_requires_a_running_job_and_a_staged_manifest(harness: Harness):
    harness.demo(DEMO)
    queued = harness.catalog.enqueue(DEMO)
    staged, _ = harness.stage(queued)

    with pytest.raises(AppError) as error:
        harness.artifacts.publish(queued, staged)
    assert error.value.code == "ARTIFACT_INVALID"

    running = harness.job(DEMO)
    staged_manifest, _ = harness.stage(running)
    elsewhere = harness.root / "staging" / running.id / "moved-manifest.json"
    elsewhere.write_text(staged_manifest.read_text())

    with pytest.raises(AppError) as error:
        harness.artifacts.publish(running, elsewhere)
    assert error.value.code == "ARTIFACT_INVALID"
    assert not (harness.root / "datasets" / DEMO / running.generation_id).exists()


def test_publish_rejects_a_manifest_that_does_not_match_the_job(harness: Harness):
    for override in (
        {"job_id": "other-job"},
        {"demo_id": "b" * 64},
        {"generation_id": "other-generation"},
        {"profile_key": "foundation-v2:other"},
    ):
        job = harness.job(DEMO, force=True)
        manifest_path, _ = harness.stage(job, manifest_overrides=override)
        with pytest.raises(AppError) as error:
            harness.artifacts.publish(job, manifest_path)
        assert error.value.code == "ARTIFACT_INVALID", override
        assert not (harness.root / "datasets" / job.demo_id / job.generation_id).exists()
        harness.catalog.fail(job.id, _publish_failure())


def test_validate_rejects_a_wrong_table_set(harness: Harness):
    job = harness.job(DEMO)

    missing_path, _ = harness.stage(job, omit={"bomb"})
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(missing_path)
    assert error.value.code == "ARTIFACT_INVALID"

    extra_path, _ = harness.stage(job, extra={"utility": build_frame("bomb")})
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(extra_path)
    assert error.value.code == "ARTIFACT_INVALID"


def test_validate_rejects_checksum_row_count_and_dtype_lies(harness: Harness):
    job = harness.job(DEMO)

    bad_hash, _ = harness.stage(job, descriptor_overrides={"players": {"sha256": "0" * 64}})
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(bad_hash)
    assert error.value.code == "ARTIFACT_INVALID"

    bad_rows, _ = harness.stage(job, descriptor_overrides={"players": {"row_count": 99}})
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(bad_rows)
    assert error.value.code == "ARTIFACT_INVALID"

    wrong_dtype = build_frame("damages").with_columns(pl.col("damage_health").cast(pl.Int64))
    bad_schema, _ = harness.stage(job, tables={"damages": wrong_dtype})
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(bad_schema)
    assert error.value.code == "ARTIFACT_INVALID"


def test_validate_rejects_missing_and_symlinked_table_files(harness: Harness):
    job = harness.job(DEMO)

    missing, _ = harness.stage(job)
    (missing.parent / "kills.parquet").unlink()
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(missing)
    assert error.value.code == "ARTIFACT_INVALID"

    symlinked, _ = harness.stage(job)
    target = symlinked.parent / "players.parquet"
    real = symlinked.parent / "players-real.parquet"
    os.rename(target, real)
    os.symlink(real, target)
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(symlinked)
    assert error.value.code == "ARTIFACT_INVALID"

    linked_manifest, _ = harness.stage(job)
    moved = linked_manifest.parent / "manifest-real.json"
    os.rename(linked_manifest, moved)
    os.symlink(moved, linked_manifest)
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(linked_manifest)
    assert error.value.code == "ARTIFACT_INVALID"


def test_validate_rejects_path_traversal_and_absolute_table_paths(harness: Harness):
    job = harness.job(DEMO)
    (harness.root / "players.parquet").write_bytes(b"a table that lives outside the generation")

    for path in ("../players.parquet", "/etc/passwd.parquet", "sub/players.parquet", MANIFEST_NAME):
        manifest_path, _ = harness.stage(job, descriptor_overrides={"players": {"path": path}})
        with pytest.raises(AppError) as error:
            harness.artifacts.validate(manifest_path)
        assert error.value.code == "ARTIFACT_INVALID", path


def test_validate_rejects_a_manifest_outside_the_data_root(harness: Harness, builder: DatasetBuilder):
    manifest_path, _ = builder.make(demo_id=DEMO, job_id="job", generation_id="generation")

    with pytest.raises(AppError) as error:
        harness.artifacts.validate(manifest_path)
    assert error.value.code == "ARTIFACT_INVALID"


def test_validate_rejects_a_malformed_manifest(harness: Harness):
    job = harness.job(DEMO)
    manifest_path, _ = harness.stage(job)

    manifest_path.write_bytes(b"{not json")
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(manifest_path)
    assert error.value.code == "ARTIFACT_INVALID"

    manifest_path.write_text('{"demo_id": "a"}\n')
    with pytest.raises(AppError) as error:
        harness.artifacts.validate(manifest_path)
    assert error.value.code == "ARTIFACT_INVALID"


def test_validate_accepts_typed_empty_tables(harness: Harness):
    job = harness.job(DEMO)
    manifest_path, _ = harness.stage(
        job,
        tables={"shots": build_frame("shots", rows=[]), "bomb": build_frame("bomb", rows=[])},
    )
    manifest = harness.artifacts.validate(manifest_path)

    assert manifest.tables["shots"].row_count == 0
    assert manifest.tables["bomb"].row_count == 0
    assert manifest.tables["players"].row_count == 2


def test_publish_cleans_up_when_publication_fails(harness: Harness, monkeypatch: pytest.MonkeyPatch):
    job = harness.job(DEMO)
    manifest_path, _ = harness.stage(job)
    original_fsync = artifacts_module._fsync_dir

    def guarded(path: Path) -> None:
        raise OSError("simulated fsync failure")

    monkeypatch.setattr(artifacts_module, "_fsync_dir", guarded)
    with pytest.raises(OSError):
        harness.artifacts.publish(job, manifest_path)
    monkeypatch.undo()

    final_dir = harness.root / "datasets" / DEMO / job.generation_id
    assert not final_dir.exists()
    assert manifest_path.is_file(), "staged input must survive a failed publication"

    manifest, published = harness.artifacts.publish(job, manifest_path)
    assert published.parent == final_dir
    assert sha256_file(published.parent / manifest.tables["players"].path) == manifest.tables["players"].sha256


def test_recovery_can_complete_an_already_published_generation(harness: Harness):
    """A crash between the rename and the catalog commit must stay recoverable."""
    job, _, published_manifest, final_path = _stage_and_publish(harness)

    recovered = harness.artifacts.validate(final_path)
    assert recovered == published_manifest
    assert harness.catalog.get_job(job.id).state == "running"
    assert harness.catalog.get_demo(DEMO).generation_id is None

    harness.catalog.complete(job.id, recovered, final_path)

    demo = harness.catalog.get_demo(DEMO)
    assert demo.generation_id == job.generation_id
    assert demo.manifest_path == str(final_path)
    assert harness.catalog.get_job(job.id).state == "succeeded"


def test_reprocessing_publishes_a_second_generation_and_keeps_the_first(harness: Harness):
    first_job, _, first_manifest, first_path = _stage_and_publish(harness)
    harness.catalog.complete(first_job.id, first_manifest, first_path)

    second_job, _, second_manifest, second_path = _stage_and_publish(harness, force=True)

    assert second_job.generation_id != first_job.generation_id
    assert second_path != first_path
    assert first_path.is_file() and second_path.is_file()

    harness.catalog.complete(second_job.id, second_manifest, second_path)
    assert harness.catalog.get_demo(DEMO).generation_id == second_job.generation_id
    assert harness.catalog.generation_path(DEMO, first_job.generation_id) == first_path

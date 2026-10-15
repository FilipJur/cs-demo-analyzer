"""Coordinator ownership and restart recovery, exercised against the real application.

These tests drive ``Application`` itself: the flock ownership file, the startup
recovery path and the catalog's job/generation transitions. A generation is only
ever produced by the real ``Catalog``/``Artifacts`` services.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cs_demo_analyzer.domain.contracts import AppError, ErrorResponse
from helpers import (
    DEMO_ID,
    commit_generation,
    create_application,
    generation_manifest,
    inferno_tables,
    publish_generation,
    register_demo,
    resolve_generation,
    restart,
    start_job,
    start_reprocess,
)


@pytest.fixture
def app(tmp_path):
    application = create_application(tmp_path)
    yield application
    application.close()


def jobs_for(app, demo_id: str):
    return [job for job in app.catalog.list_jobs() if job.demo_id == demo_id]


def test_second_instance_cannot_own_the_same_data_root(app, tmp_path):
    with pytest.raises(AppError) as failure:
        create_application(tmp_path)
    assert failure.value.code == "ALREADY_RUNNING"
    assert failure.value.stage == "startup"

    app.close()
    successor = create_application(tmp_path)
    try:
        assert successor.settings.data_root == app.settings.data_root
    finally:
        successor.close()


def test_restart_requeues_a_single_new_attempt_for_a_running_job(app, tmp_path, monkeypatch):
    register_demo(app, DEMO_ID)
    interrupted = start_job(app, DEMO_ID)
    assert interrupted.state == "running"
    assert not generation_manifest(app.settings.data_root, DEMO_ID, interrupted.generation_id).is_file()

    restart(app, monkeypatch)

    assert app.catalog.get_job(interrupted.id).state == "interrupted"
    error = app.catalog.get_job(interrupted.id).error
    assert error is not None and error.code == "INTERRUPTED" and error.retryable is True

    attempts = jobs_for(app, DEMO_ID)
    assert len(attempts) == 2
    queued = [job for job in attempts if job.state == "queued"]
    assert len(queued) == 1
    assert queued[0].generation_id != interrupted.generation_id

    # Recovery is not a second scheduler: another restart neither requeues nor duplicates.
    app.close()
    successor = create_application(tmp_path)
    try:
        restart(successor, monkeypatch)
        successors = jobs_for(successor, DEMO_ID)
        assert len(successors) == 2
        assert [job.id for job in successors if job.state == "queued"] == [queued[0].id]
    finally:
        successor.close()


def test_restart_commits_a_published_but_uncommitted_generation(app, monkeypatch):
    register_demo(app, DEMO_ID)
    job = start_job(app, DEMO_ID)
    manifest, final = publish_generation(app, job, map_name="inferno", tables=inferno_tables())
    assert final == generation_manifest(app.settings.data_root, DEMO_ID, job.generation_id)
    assert app.catalog.get_demo(DEMO_ID).generation_id is None

    restart(app, monkeypatch)

    assert app.catalog.get_job(job.id).state == "succeeded"
    demo = app.catalog.get_demo(DEMO_ID)
    assert demo.generation_id == job.generation_id
    assert demo.manifest_path == str(final)
    assert resolve_generation(app, DEMO_ID, job.generation_id) == final
    assert app.artifacts.validate(final).generation_id == job.generation_id
    # The published generation was adopted, not re-parsed.
    assert [job.id for job in jobs_for(app, DEMO_ID)] == [job.id]


def test_restart_recovers_a_completed_then_superseding_pair_of_generations(app, monkeypatch):
    register_demo(app, DEMO_ID)
    good = commit_generation(app, DEMO_ID, map_name="inferno", tables=inferno_tables())
    reprocess = start_reprocess(app, DEMO_ID)
    assert reprocess.generation_id != good.generation_id
    published, final = publish_generation(app, reprocess, map_name="mirage", tables=inferno_tables())

    restart(app, monkeypatch)

    assert app.catalog.get_job(reprocess.id).state == "succeeded"
    demo = app.catalog.get_demo(DEMO_ID)
    assert demo.generation_id == reprocess.generation_id
    assert resolve_generation(app, DEMO_ID, reprocess.generation_id) == final
    # The superseded generation stays registered and readable after the switch.
    previous = resolve_generation(app, DEMO_ID, good.generation_id)
    assert previous is not None and Path(previous).is_file()
    assert app.artifacts.validate(Path(previous)).generation_id == good.generation_id
    assert published.generation_id == reprocess.generation_id


def test_interrupted_reprocess_keeps_the_last_good_generation_readable(app, monkeypatch):
    register_demo(app, DEMO_ID)
    good = commit_generation(app, DEMO_ID, map_name="inferno", tables=inferno_tables())
    good_path = resolve_generation(app, DEMO_ID, good.generation_id)
    assert good_path is not None

    reprocess = start_reprocess(app, DEMO_ID)
    assert reprocess.generation_id != good.generation_id
    restart(app, monkeypatch)

    demo = app.catalog.get_demo(DEMO_ID)
    assert demo.generation_id == good.generation_id
    assert resolve_generation(app, DEMO_ID, good.generation_id) == good_path
    assert app.artifacts.validate(Path(good_path)).generation_id == good.generation_id
    assert app.catalog.get_job(reprocess.id).state == "interrupted"
    states = [job.state for job in jobs_for(app, DEMO_ID)]
    assert states.count("queued") == 1 and states.count("succeeded") == 1


def test_failed_reprocess_keeps_the_last_good_generation_readable(app):
    register_demo(app, DEMO_ID)
    good = commit_generation(app, DEMO_ID, map_name="inferno", tables=inferno_tables())
    good_path = resolve_generation(app, DEMO_ID, good.generation_id)
    assert good_path is not None

    reprocess = start_reprocess(app, DEMO_ID)
    app.catalog.fail(
        reprocess.id,
        ErrorResponse(code="PARSE_FAILED", message="parser rejected the recording", stage="parse"),
        state="failed",
    )

    failed = app.catalog.get_job(reprocess.id)
    assert failed.state == "failed"
    assert failed.error is not None and failed.error.code == "PARSE_FAILED"
    assert app.catalog.get_demo(DEMO_ID).generation_id == good.generation_id
    assert resolve_generation(app, DEMO_ID, good.generation_id) == good_path
    assert app.artifacts.validate(Path(good_path)).generation_id == good.generation_id
    assert sorted(job.state for job in jobs_for(app, DEMO_ID)) == ["failed", "succeeded"]


def test_raw_rename_survives_crash_before_catalog_registration(app, tmp_path):
    from cs_demo_analyzer.domain.contracts import Fingerprint, Observation
    from cs_demo_analyzer.ingestion.service import snapshot_source

    source = tmp_path / "lost-source.dem"
    content = b"PBDEMS2\0snapshot published before catalog registration"
    source.write_bytes(content)
    snapshot = snapshot_source(
        Observation(path=str(source), fingerprint=Fingerprint.from_path(source)), app.settings
    )
    assert app.catalog.get_demo(snapshot.demo_id) is None
    source.unlink()
    app.start(discover=False)
    recovered = app.catalog.get_demo(snapshot.demo_id)
    assert recovered is not None
    assert recovered.demo_id == snapshot.demo_id
    assert Path(recovered.raw_path).read_bytes() == content


def test_gracefully_interrupted_latest_attempt_resumes_once(app, monkeypatch):
    register_demo(app, DEMO_ID)
    interrupted = start_job(app, DEMO_ID)
    app.catalog.fail(
        interrupted.id,
        ErrorResponse(code="INTERRUPTED", message="Application stopped", stage="parse", retryable=True),
        state="interrupted",
    )
    restart(app, monkeypatch)
    attempts = jobs_for(app, DEMO_ID)
    assert sorted(job.state for job in attempts) == ["interrupted", "queued"]
    replacement = next(job for job in attempts if job.state == "queued")
    assert replacement.generation_id != interrupted.generation_id
    restart(app, monkeypatch)
    assert {job.id for job in jobs_for(app, DEMO_ID)} == {job.id for job in attempts}

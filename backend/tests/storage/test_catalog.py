"""Behavior of the durable catalog: identity, coalescing, fencing and recovery."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

import pytest

from cs_demo_analyzer.domain.contracts import (
    PROFILE_KEY,
    AppError,
    ErrorResponse,
    Fingerprint,
    JobRecord,
    Manifest,
    Snapshot,
)

from .support import TABLE_NAMES, Harness

DEMO = "a" * 64
OTHER_DEMO = "b" * 64

CATALOG_TABLES = (
    "schema_migrations",
    "roots",
    "demos",
    "sources",
    "jobs",
    "generations",
    "demo_heads",
)


def _fingerprint(size: int = 64) -> Fingerprint:
    return Fingerprint(device=1, inode=2, size=size, mtime_ns=3, ctime_ns=4)


def _snapshot(demo_id: str, raw_path: str, source_path: str, size: int = 64) -> Snapshot:
    return Snapshot(
        demo_id=demo_id,
        raw_path=raw_path,
        size=size,
        source_path=source_path,
        fingerprint=_fingerprint(size),
    )


def _error(code: str = "PARSE_FAILED") -> ErrorResponse:
    return ErrorResponse(code=code, message=f"{code} happened", stage="parse")


def _table_names(root: Path) -> set[str]:
    connection = sqlite3.connect(root / "catalog.sqlite")
    try:
        return {
            name
            for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    finally:
        connection.close()


def test_migrations_create_the_catalog_schema_and_reopen_is_idempotent(catalog, data_root: Path):
    names = _table_names(data_root)
    assert set(CATALOG_TABLES) <= names
    assert names & set(TABLE_NAMES) == set(), "canonical gameplay tables must stay in Parquet, not SQLite"
    assert catalog.catalog_version == 1

    from cs_demo_analyzer.storage import Catalog

    reopened = Catalog(data_root)
    try:
        assert reopened.catalog_version == 1
        assert reopened.list_roots() == []
    finally:
        reopened.close()


def test_add_root_is_idempotent_and_update_root_reports_availability(catalog):
    first = catalog.add_root("/demos/nested", recursive=True)
    assert first.path == "/demos/nested"
    assert first.recursive is True
    assert first.available is True
    assert first.error is None
    assert first.id > 0

    again = catalog.add_root("/demos/nested", recursive=False)
    assert again.id == first.id
    assert again.recursive is False
    assert len(catalog.list_roots()) == 1

    catalog.update_root(first.id, False, "root missing")
    updated = catalog.list_roots()[0]
    assert updated.available is False and updated.error == "root missing"

    catalog.update_root(9999, True)  # unknown root is a no-op, not a crash
    assert len(catalog.list_roots()) == 1


def test_sources_upsert_round_trip_and_filter_by_demo(catalog, harness: Harness):
    harness.demo(DEMO)
    fingerprint = _fingerprint(301_894_448)

    settling = catalog.set_source("/demos/one.dem", fingerprint, "settling")
    assert settling.status == "settling"
    assert settling.fingerprint == fingerprint
    assert settling.demo_id is None

    imported = catalog.set_source("/demos/one.dem", fingerprint, "imported", demo_id=DEMO)
    assert imported.demo_id == DEMO
    assert catalog.get_source("/demos/one.dem") == imported
    assert len(catalog.list_sources()) == 1

    catalog.set_source("/demos/two.dem", None, "missing", error=_error("SOURCE_MISSING"))
    assert catalog.get_source("/demos/two.dem").error.code == "SOURCE_MISSING"
    assert catalog.get_source("/demos/unknown.dem") is None
    assert [source.path for source in catalog.list_sources(demo_id=DEMO)] == ["/demos/one.dem"]
    assert catalog.list_sources(demo_id=OTHER_DEMO) == []


def test_register_demo_converges_identical_bytes_from_two_paths(catalog):
    first = catalog.register_demo(_snapshot(DEMO, "raw/a/source.dem", "/demos/one.dem"))
    second = catalog.register_demo(_snapshot(DEMO, "raw/a/source.dem", "/elsewhere/two.dem"))

    assert first.demo_id == second.demo_id == DEMO
    assert second.created_at == first.created_at
    assert second.size == first.size == 64
    assert len(catalog.list_demos()) == 1
    assert catalog.list_demos()[0].generation_id is None
    assert catalog.list_demos()[0].manifest_path is None


def test_list_demos_paginates_newest_first(catalog):
    for index in range(3):
        catalog.register_demo(_snapshot(f"{index:064x}", f"raw/{index}/source.dem", f"/demos/{index}.dem"))

    first_page = catalog.list_demos(limit=2)
    second_page = catalog.list_demos(limit=2, offset=2)
    assert len(first_page) == 2
    assert len(second_page) == 1
    assert {demo.demo_id for demo in first_page + second_page} == {f"{index:064x}" for index in range(3)}
    assert catalog.list_demos(limit=0) == []


def test_enqueue_coalesces_the_active_job(catalog, harness: Harness):
    harness.demo(DEMO)

    queued = catalog.enqueue(DEMO)
    assert queued.state == "queued"
    assert queued.profile_key == PROFILE_KEY
    assert queued.attempt == 1
    assert catalog.enqueue(DEMO).id == queued.id
    assert catalog.enqueue(DEMO, force=True).id == queued.id, "force must not duplicate an active job"

    running = catalog.claim_next()
    assert running.id == queued.id and running.state == "running"
    assert catalog.enqueue(DEMO).id == queued.id
    assert len(catalog.list_jobs()) == 1


def test_enqueue_reuses_a_successful_profile_unless_forced(catalog, harness: Harness):
    job, _, _ = harness.run(DEMO)

    reused = catalog.enqueue(DEMO)
    assert reused.id == job.id
    assert reused.state == "succeeded"
    assert len(catalog.list_jobs()) == 1

    forced = catalog.enqueue(DEMO, force=True)
    assert forced.id != job.id
    assert forced.state == "queued"
    assert forced.generation_id != job.generation_id
    assert forced.attempt == 2
    assert len(catalog.list_jobs()) == 2


def test_enqueue_rejects_an_unknown_demo(catalog):
    with pytest.raises(AppError) as error:
        catalog.enqueue(DEMO)
    assert error.value.code == "UNKNOWN_DEMO"


def test_claim_next_is_fifo_and_gives_every_job_its_own_token(catalog, harness: Harness):
    demo_ids = [f"{index:064x}" for index in range(3)]
    for demo_id in demo_ids:
        harness.demo(demo_id, source=f"/demos/{demo_id}.dem")
        catalog.enqueue(demo_id)

    claimed = [catalog.claim_next() for _ in range(3)]
    assert [job.demo_id for job in claimed] == demo_ids
    assert all(job.state == "running" for job in claimed)
    assert len({job.generation_id for job in claimed}) == 3
    assert all(job.generation_id != job.id for job in claimed)
    assert catalog.claim_next() is None


def test_set_worker_records_and_clears_the_pid(catalog, harness: Harness):
    job = harness.job(DEMO)
    assert job.worker_pid is None

    catalog.set_worker(job.id, 4321)
    assert catalog.get_job(job.id).worker_pid == 4321

    catalog.set_worker(job.id, None)
    assert catalog.get_job(job.id).worker_pid is None


def test_complete_switches_the_last_good_pointer_and_finishes_the_job(catalog, harness: Harness):
    job, manifest, final_path = harness.run(DEMO)

    demo = catalog.get_demo(DEMO)
    assert demo.generation_id == job.generation_id
    assert demo.manifest_path == str(final_path)
    assert demo.map_name == "de_inferno"
    assert demo.quality == "complete"
    assert demo.warnings == []
    assert catalog.generation_path(DEMO, job.generation_id) == final_path
    assert final_path.name == "manifest.json"
    assert {entry.name for entry in final_path.parent.iterdir()} == {
        f"{table}.parquet" for table in TABLE_NAMES
    } | {"manifest.json"}

    finished = catalog.get_job(job.id)
    assert finished.state == "succeeded"
    assert finished.error is None
    assert finished.worker_pid is None
    assert harness.catalog.running_jobs() == []
    assert manifest.demo_id == DEMO


def test_complete_requires_the_expected_published_manifest_path(catalog, harness: Harness):
    job = harness.job(DEMO)
    manifest, _ = harness.publish(job)
    stray = harness.root / "datasets" / job.demo_id / job.generation_id / "manifest-copy.json"

    with pytest.raises(AppError) as error:
        catalog.complete(job.id, manifest, stray)
    assert error.value.code == "ARTIFACT_INVALID"
    assert catalog.get_job(job.id).state == "running"
    assert catalog.get_demo(DEMO).generation_id is None


def test_complete_fences_identity_against_the_running_job(catalog, harness: Harness):
    job = harness.job(DEMO)
    manifest, final_path = harness.publish(job)

    for patch in (
        {"job_id": "other-job"},
        {"demo_id": OTHER_DEMO},
        {"generation_id": "other-generation"},
        {"profile_key": "foundation-v2:other"},
    ):
        with pytest.raises(AppError) as error:
            catalog.complete(job.id, manifest.model_copy(update=patch), final_path)
        assert error.value.code == "ARTIFACT_INVALID", patch
        assert catalog.get_job(job.id).state == "running"
        assert catalog.get_demo(DEMO).generation_id is None


def test_complete_refuses_jobs_that_are_not_running(catalog, harness: Harness):
    harness.demo(DEMO)
    queued = catalog.enqueue(DEMO)
    empty = Manifest(
        demo_id=DEMO,
        job_id=queued.id,
        generation_id=queued.generation_id,
        source_size=1,
        map_name="de_inferno",
        tick_rate_hz=64.0,
        tables={},
    )
    expected = harness.root / "datasets" / DEMO / queued.generation_id / "manifest.json"

    with pytest.raises(AppError) as error:
        catalog.complete(queued.id, empty, expected)
    assert error.value.code == "JOB_STATE"

    with pytest.raises(AppError) as error:
        catalog.complete("missing-job", empty, expected)
    assert error.value.code == "UNKNOWN_JOB"

    running = catalog.claim_next()
    manifest, final_path = harness.publish(running)
    catalog.complete(running.id, manifest, final_path)
    with pytest.raises(AppError) as error:
        catalog.complete(running.id, manifest, final_path)
    assert error.value.code == "JOB_STATE"
    assert catalog.get_job(running.id).state == "succeeded"


def test_complete_rejects_a_generation_with_a_missing_table_file(catalog, harness: Harness):
    job = harness.job(DEMO)
    manifest, final_path = harness.publish(job)
    (final_path.parent / "players.parquet").unlink()

    with pytest.raises(AppError) as error:
        catalog.complete(job.id, manifest, final_path)
    assert error.value.code == "ARTIFACT_INVALID"
    assert catalog.get_job(job.id).state == "running"
    assert catalog.get_demo(DEMO).generation_id is None


def test_failed_reprocess_keeps_the_last_good_generation_readable(catalog, harness: Harness):
    good_job, _, good_path = harness.run(DEMO)

    reprocess = harness.job(DEMO, force=True)
    harness.stage(reprocess)
    catalog.fail(reprocess.id, _error("PARSE_FAILED"))

    demo = catalog.get_demo(DEMO)
    assert demo.generation_id == good_job.generation_id
    assert demo.manifest_path == str(good_path)
    assert catalog.generation_path(DEMO, good_job.generation_id) == good_path
    assert (good_path.parent / "players.parquet").is_file()
    assert (good_path.parent / "player_state.parquet").is_file()

    failed = catalog.get_job(reprocess.id)
    assert failed.state == "failed"
    assert failed.error.code == "PARSE_FAILED"

    assert catalog.enqueue(DEMO).id == good_job.id


def test_interrupted_job_can_be_requeued_as_a_new_attempt(catalog, harness: Harness):
    job = harness.job(DEMO)
    assert [running.id for running in catalog.running_jobs()] == [job.id]

    catalog.fail(job.id, _error("INTERRUPTED"), state="interrupted")
    assert catalog.running_jobs() == []
    assert catalog.get_job(job.id).state == "interrupted"

    requeued = harness.job(DEMO, force=True)
    assert requeued.id != job.id
    assert requeued.generation_id != job.generation_id
    assert requeued.attempt == 2

    with pytest.raises(AppError) as error:
        catalog.fail(job.id, _error())
    assert error.value.code == "JOB_STATE"

    with pytest.raises(AppError) as error:
        catalog.fail(requeued.id, _error(), state="succeeded")
    assert error.value.code == "INVALID_ARGUMENT"
    assert catalog.get_job(requeued.id).state == "running"


def test_generation_path_hides_unknown_or_unusable_generations(catalog, harness: Harness):
    job, _, final_path = harness.run(DEMO)

    assert catalog.generation_path(DEMO, job.generation_id) == final_path
    assert catalog.generation_path(DEMO, "0" * 32) is None
    assert catalog.generation_path(OTHER_DEMO, job.generation_id) is None

    final_path.unlink()
    assert catalog.generation_path(DEMO, job.generation_id) is None

    final_path.symlink_to(harness.root / "elsewhere.json")
    assert catalog.generation_path(DEMO, job.generation_id) is None


def test_concurrent_claims_hand_each_job_to_exactly_one_thread(catalog, harness: Harness):
    demo_ids = [f"{index:064x}" for index in range(8)]
    for demo_id in demo_ids:
        harness.demo(demo_id, source=f"/demos/{demo_id}.dem")
        catalog.enqueue(demo_id)

    workers = 8
    barrier = threading.Barrier(workers)
    claimed: list[JobRecord] = []
    failures: list[BaseException] = []
    lock = threading.Lock()

    def claim() -> None:
        try:
            barrier.wait(timeout=10)
            job = catalog.claim_next()
        except BaseException as exc:  # pragma: no cover - reported below
            with lock:
                failures.append(exc)
            return
        with lock:
            if job is not None:
                claimed.append(job)

    threads = [threading.Thread(target=claim) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert failures == []
    assert len(claimed) == workers
    assert {job.demo_id for job in claimed} == set(demo_ids)
    assert len({job.generation_id for job in claimed}) == workers
    assert all(job.state == "running" for job in claimed)
    assert catalog.claim_next() is None
    assert len(catalog.running_jobs()) == workers


def test_concurrent_enqueue_creates_one_active_job_per_demo_and_profile(catalog, harness: Harness):
    harness.demo(DEMO)
    workers = 8
    barrier = threading.Barrier(workers)
    created: list[str] = []
    failures: list[BaseException] = []
    lock = threading.Lock()

    def enqueue() -> None:
        try:
            barrier.wait(timeout=10)
            job = catalog.enqueue(DEMO)
        except BaseException as exc:  # pragma: no cover - reported below
            with lock:
                failures.append(exc)
            return
        with lock:
            created.append(job.id)

    threads = [threading.Thread(target=enqueue) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert failures == []
    assert len(set(created)) == 1
    assert len(catalog.list_jobs()) == 1


def test_close_is_idempotent_and_blocks_further_use(catalog, data_root: Path):
    catalog.add_root("/demos")
    catalog.close()
    catalog.close()

    with pytest.raises(AppError) as error:
        catalog.add_root("/other")
    assert error.value.code == "CATALOG_CLOSED"
    with pytest.raises(AppError):
        catalog.list_roots()

    from cs_demo_analyzer.storage import Catalog

    reopened = Catalog(data_root)
    try:
        assert [root.path for root in reopened.list_roots()] == ["/demos"]
    finally:
        reopened.close()

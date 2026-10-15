"""Durable catalog: roots, source locations, demos, jobs and generations.

One ``Catalog`` owns ``catalog.sqlite`` for one data root. The coordinator is the
only writer; ``check_same_thread=False`` plus an ``RLock`` lets API threads read
safely while the coordinator writes. Every mutation is a short
``BEGIN IMMEDIATE`` transaction, so no copy, parse or hash ever runs while the
write lock is held.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from uuid import uuid4

from ..domain.contracts import (
    DEFAULT_PROFILE_KEY,
    PROFILE_KEY,
    PROFILE_KEYS,
    DemoRecord,
    ErrorResponse,
    Fingerprint,
    JobRecord,
    Manifest,
    RootRecord,
    Snapshot,
    SourceRecord,
    utc_now,
)
from .artifacts import (
    MANIFEST_NAME,
    assert_table_layout,
    is_safe_token,
    normalize_path,
    read_manifest,
)
from .errors import ArtifactInvalid, CatalogError
from .schema import apply_migrations

ACTIVE_STATES = ("queued", "running")
FAIL_STATES = ("failed", "interrupted")


def _error_from_json(payload: str | None) -> ErrorResponse | None:
    if payload is None:
        return None
    return ErrorResponse.model_validate(json.loads(payload))


def _fingerprint_from_json(payload: str | None) -> Fingerprint | None:
    if payload is None:
        return None
    return Fingerprint.model_validate(json.loads(payload))


def _root(row: sqlite3.Row) -> RootRecord:
    return RootRecord(
        id=row["root_id"],
        path=row["path"],
        recursive=bool(row["recursive"]),
        available=bool(row["available"]),
        error=row["error"],
    )


def _source(row: sqlite3.Row) -> SourceRecord:
    return SourceRecord(
        path=row["path"],
        fingerprint=_fingerprint_from_json(row["fingerprint_json"]),
        demo_id=row["demo_id"],
        status=row["status"],
        error=_error_from_json(row["error_json"]),
        updated_at=row["updated_at"],
    )


def _job(row: sqlite3.Row) -> JobRecord:
    return JobRecord(
        id=row["id"],
        demo_id=row["demo_id"],
        profile_key=row["profile_key"],
        state=row["state"],
        generation_id=row["generation_id"],
        attempt=row["attempt"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        error=_error_from_json(row["error_json"]),
        worker_pid=row["worker_pid"],
    )


class Catalog:
    def __init__(self, data_root: Path | str) -> None:
        root = normalize_path(data_root)
        if not root.is_absolute():
            raise CatalogError(f"data root must be absolute, got {data_root}", code="INVALID_ARGUMENT")
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.data_root = root
        self._lock = threading.RLock()
        self._closed = False
        self._conn = sqlite3.connect(
            root / "catalog.sqlite", isolation_level=None, check_same_thread=False, timeout=5.0
        )
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL").fetchall()
            self._conn.execute("PRAGMA synchronous=FULL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.execute("PRAGMA busy_timeout=5000")
            self.catalog_version = apply_migrations(self._conn)

    # -- plumbing ----------------------------------------------------------
    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._ensure_open()
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                yield self._conn
            except BaseException:
                self._conn.execute("ROLLBACK")
                raise
            else:
                self._conn.execute("COMMIT")

    def _query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self._lock:
            self._ensure_open()
            return self._conn.execute(sql, params).fetchall()

    def _ensure_open(self) -> None:
        if self._closed:
            raise CatalogError("catalog is closed", code="CATALOG_CLOSED")

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._conn.close()

    # -- roots -------------------------------------------------------------
    def add_root(self, path: str, recursive: bool = False) -> RootRecord:
        now = utc_now()
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO roots (path, recursive, available, created_at, updated_at)
                VALUES (?, ?, 1, ?, ?)
                ON CONFLICT (path) DO UPDATE SET recursive = excluded.recursive, updated_at = excluded.updated_at
                """,
                (path, int(recursive), now, now),
            )
            row = conn.execute("SELECT * FROM roots WHERE path = ?", (path,)).fetchone()
        return _root(row)

    def list_roots(self) -> list[RootRecord]:
        return [_root(row) for row in self._query("SELECT * FROM roots ORDER BY root_id")]

    def update_root(self, root_id: int, available: bool, error: str | None = None) -> None:
        with self._tx() as conn:
            conn.execute(
                "UPDATE roots SET available = ?, error = ?, updated_at = ? WHERE root_id = ?",
                (int(available), error, utc_now(), root_id),
            )

    # -- source locations --------------------------------------------------
    def set_source(
        self,
        path: str,
        fingerprint: Fingerprint | None,
        status: str,
        demo_id: str | None = None,
        error: ErrorResponse | None = None,
    ) -> SourceRecord:
        params = (
            path,
            fingerprint.model_dump_json() if fingerprint is not None else None,
            status,
            demo_id,
            error.model_dump_json() if error is not None else None,
            utc_now(),
        )
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO sources (path, fingerprint_json, status, demo_id, error_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (path) DO UPDATE SET
                    fingerprint_json = excluded.fingerprint_json,
                    status = excluded.status,
                    demo_id = excluded.demo_id,
                    error_json = excluded.error_json,
                    updated_at = excluded.updated_at
                """,
                params,
            )
            row = conn.execute("SELECT * FROM sources WHERE path = ?", (path,)).fetchone()
        return _source(row)

    def get_source(self, path: str) -> SourceRecord | None:
        rows = self._query("SELECT * FROM sources WHERE path = ?", (path,))
        return _source(rows[0]) if rows else None

    def list_sources(self, demo_id: str | None = None) -> list[SourceRecord]:
        if demo_id is None:
            rows = self._query("SELECT * FROM sources ORDER BY path")
        else:
            rows = self._query("SELECT * FROM sources WHERE demo_id = ? ORDER BY path", (demo_id,))
        return [_source(row) for row in rows]

    # -- demos -------------------------------------------------------------
    def register_demo(self, snapshot: Snapshot) -> DemoRecord:
        if not is_safe_token(snapshot.demo_id):
            raise CatalogError(f"unsafe demo id {snapshot.demo_id!r}", code="INVALID_ARGUMENT")
        now = utc_now()
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO demos (demo_id, raw_path, size, source_path, fingerprint_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (demo_id) DO UPDATE SET
                    raw_path = excluded.raw_path,
                    size = excluded.size,
                    source_path = excluded.source_path,
                    fingerprint_json = excluded.fingerprint_json,
                    updated_at = excluded.updated_at
                """,
                (
                    snapshot.demo_id,
                    snapshot.raw_path,
                    snapshot.size,
                    snapshot.source_path,
                    snapshot.fingerprint.model_dump_json(),
                    now,
                    now,
                ),
            )
        record = self.get_demo(snapshot.demo_id)
        if record is None:  # pragma: no cover - the upsert above wrote the row
            raise CatalogError(f"demo {snapshot.demo_id} disappeared during registration", code="INTERNAL_ERROR")
        return record

    def get_demo(self, demo_id: str) -> DemoRecord | None:
        rows = self._query(
            f"{self._DEMO_SELECT} WHERE d.demo_id = ?", (DEFAULT_PROFILE_KEY, PROFILE_KEY, demo_id)
        )
        return self._demo(rows[0]) if rows else None

    def list_demos(self, limit: int = 100, offset: int = 0) -> list[DemoRecord]:
        if limit <= 0:
            return []
        rows = self._query(
            f"{self._DEMO_SELECT} ORDER BY d.created_at DESC, d.rowid DESC LIMIT ? OFFSET ?",
            (DEFAULT_PROFILE_KEY, PROFILE_KEY, limit, max(offset, 0)),
        )
        return [self._demo(row) for row in rows]

    #: A demo can hold one head per profile. The reported head is the preferred
    #: (default) profile when it exists, otherwise the frozen foundation head, so
    #: a demo extracted only by the older profile keeps reporting that generation
    #: while a demo extracted by the current profile reports the newer one.
    _DEMO_SELECT = """
        SELECT d.demo_id, d.raw_path, d.size, d.created_at, d.fingerprint_json,
               s.fingerprint_json AS current_source_fingerprint, s.status AS current_source_status,
               h.generation_id AS head_generation, g.manifest_relpath, g.map_name,
               g.quality, g.warnings_json
        FROM demos AS d
        LEFT JOIN demo_heads AS h ON h.rowid = (
            SELECT candidate.rowid FROM demo_heads AS candidate
            WHERE candidate.demo_id = d.demo_id
            ORDER BY CASE candidate.profile_key WHEN ? THEN 0 WHEN ? THEN 1 ELSE 2 END,
                     candidate.updated_at DESC
            LIMIT 1
        )
        LEFT JOIN generations AS g ON g.generation_id = h.generation_id
        LEFT JOIN sources AS s ON s.path = d.source_path
    """

    def _demo(self, row: sqlite3.Row) -> DemoRecord:
        relpath = row["manifest_relpath"]
        warnings = list(json.loads(row["warnings_json"])) if row["head_generation"] else []
        if row["current_source_fingerprint"] and row["current_source_fingerprint"] != row["fingerprint_json"]:
            warnings.append("Source path changed after this recording was preserved; retained bytes are unchanged.")
        elif row["current_source_status"] == "missing":
            warnings.append("Original source is unavailable; the owned recording remains preserved.")
        return DemoRecord(
            demo_id=row["demo_id"],
            raw_path=row["raw_path"],
            size=row["size"],
            created_at=row["created_at"],
            generation_id=row["head_generation"],
            manifest_path=str(self.data_root / relpath) if relpath else None,
            map_name=row["map_name"],
            quality=row["quality"],
            warnings=warnings,
        )

    # -- jobs --------------------------------------------------------------
    def enqueue(
        self, demo_id: str, force: bool = False, profile_key: str | None = None
    ) -> JobRecord:
        """Queue one extraction attempt for ``demo_id`` under ``profile_key``.

        ``profile_key=None`` keeps the frozen ``foundation-v1`` profile for direct
        library callers. The application and ingestion layers pass
        :data:`~cs_demo_analyzer.domain.contracts.DEFAULT_PROFILE_KEY` so new work
        is extracted by the current extended profile, while an explicit
        foundation request stays a supported, ordinary job. Attempts and the
        single-active-job rule are scoped to ``(demo, profile)``.

        The profile key is a trust boundary: a key this build does not implement
        is rejected before anything durable is written, so the catalog never
        holds a job that is guaranteed to fail in the parser.
        """
        profile = PROFILE_KEY if profile_key is None else profile_key
        if profile not in PROFILE_KEYS.values():
            raise CatalogError(
                f"unsupported profile key {profile!r}; supported keys {sorted(PROFILE_KEYS.values())}",
                code="INVALID_PROFILE",
            )
        now = utc_now()
        with self._tx() as conn:
            if conn.execute("SELECT 1 FROM demos WHERE demo_id = ?", (demo_id,)).fetchone() is None:
                raise CatalogError(f"unknown demo {demo_id}", code="UNKNOWN_DEMO")
            active = self._active_job(conn, demo_id, profile)
            if active is not None:
                return _job(active)
            if not force:
                reusable = self._reusable_job(conn, demo_id, profile)
                if reusable is not None:
                    return _job(reusable)
            attempt = conn.execute(
                "SELECT COALESCE(MAX(attempt), 0) + 1 AS next FROM jobs WHERE demo_id = ? AND profile_key = ?",
                (demo_id, profile),
            ).fetchone()["next"]
            job_id = uuid4().hex
            try:
                conn.execute(
                    """
                    INSERT INTO jobs
                        (id, demo_id, profile_key, state, generation_id, attempt, force, created_at, updated_at)
                    VALUES (?, ?, ?, 'queued', ?, ?, ?, ?, ?)
                    """,
                    (job_id, demo_id, profile, uuid4().hex, attempt, int(force), now, now),
                )
            except sqlite3.IntegrityError:
                winner = self._active_job(conn, demo_id, profile)
                if winner is None:
                    raise
                return _job(winner)
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return _job(row)

    def _active_job(self, conn: sqlite3.Connection, demo_id: str, profile: str) -> sqlite3.Row | None:
        return conn.execute(
            """
            SELECT * FROM jobs WHERE demo_id = ? AND profile_key = ? AND state IN ('queued', 'running')
            ORDER BY created_at, rowid LIMIT 1
            """,
            (demo_id, profile),
        ).fetchone()

    def _reusable_job(self, conn: sqlite3.Connection, demo_id: str, profile: str) -> sqlite3.Row | None:
        head = conn.execute(
            "SELECT generation_id FROM demo_heads WHERE demo_id = ? AND profile_key = ?", (demo_id, profile)
        ).fetchone()
        if head is not None:
            row = conn.execute(
                "SELECT * FROM jobs WHERE demo_id = ? AND profile_key = ? AND state = 'succeeded' AND generation_id = ?",
                (demo_id, profile, head["generation_id"]),
            ).fetchone()
            if row is not None:
                return row
        return conn.execute(
            """
            SELECT * FROM jobs WHERE demo_id = ? AND profile_key = ? AND state = 'succeeded'
            ORDER BY finished_at DESC, rowid DESC LIMIT 1
            """,
            (demo_id, profile),
        ).fetchone()

    def claim_next(self) -> JobRecord | None:
        with self._tx() as conn:
            row = conn.execute(
                "SELECT * FROM jobs WHERE state = 'queued' ORDER BY created_at, rowid LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            now = utc_now()
            updated = conn.execute(
                "UPDATE jobs SET state = 'running', started_at = ?, updated_at = ? WHERE id = ? AND state = 'queued'",
                (now, now, row["id"]),
            )
            if updated.rowcount != 1:
                raise CatalogError(f"job {row['id']} was claimed concurrently", code="JOB_STATE", retryable=True)
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone()
        return _job(row)

    def get_job(self, id: str) -> JobRecord | None:
        rows = self._query("SELECT * FROM jobs WHERE id = ?", (id,))
        return _job(rows[0]) if rows else None

    def list_jobs(self, limit: int = 100) -> list[JobRecord]:
        if limit <= 0:
            return []
        rows = self._query(
            "SELECT * FROM jobs ORDER BY created_at DESC, rowid DESC LIMIT ?", (limit,)
        )
        return [_job(row) for row in rows]

    def running_jobs(self) -> list[JobRecord]:
        rows = self._query("SELECT * FROM jobs WHERE state = 'running' ORDER BY created_at, rowid")
        return [_job(row) for row in rows]

    def interrupted_jobs(self) -> list[JobRecord]:
        """Latest interrupted attempt per demo and profile; older attempts never requeue."""
        rows = self._query(
            """SELECT j.* FROM jobs AS j
               WHERE j.state = 'interrupted'
                 AND NOT EXISTS (
                     SELECT 1 FROM jobs AS newer
                     WHERE newer.demo_id = j.demo_id AND newer.profile_key = j.profile_key
                       AND newer.attempt > j.attempt
                 )
               ORDER BY j.created_at, j.rowid"""
        )
        return [_job(row) for row in rows]

    def set_worker(self, job_id: str, pid: int | None) -> None:
        with self._tx() as conn:
            conn.execute(
                "UPDATE jobs SET worker_pid = ?, updated_at = ? WHERE id = ?", (pid, utc_now(), job_id)
            )

    # -- publication -------------------------------------------------------
    def complete(self, job_id: str, manifest: Manifest, manifest_path: Path) -> None:
        """Fence a running job against a published generation and switch the pointer.

        The artifact set has already been published (and fully verified) by
        ``Artifacts.publish``. Inside the write transaction we re-check the job
        state, the identity carried by the caller's manifest and the manifest
        file on disk, then record the generation, move the last-good pointer and
        finish the job. Files are only stat-ed here, never read or hashed, so the
        transaction stays short.
        """
        path = normalize_path(manifest_path)
        now = utc_now()
        with self._tx() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if row is None:
                raise CatalogError(f"unknown job {job_id}", code="UNKNOWN_JOB")
            if row["state"] != "running":
                raise CatalogError(
                    f"job {job_id} is {row['state']}; only a running job may complete", code="JOB_STATE"
                )
            for token, label in ((row["demo_id"], "demo id"), (row["generation_id"], "generation id")):
                if not is_safe_token(token):
                    raise CatalogError(f"unsafe {label} {token!r} on job {job_id}", code="INVALID_ARGUMENT")
            expected = (
                self.data_root / "datasets" / row["demo_id"] / row["generation_id"] / MANIFEST_NAME
            )
            if path != normalize_path(expected):
                raise ArtifactInvalid(f"published manifest must be {expected}, got {path}")
            identity = (
                ("job_id", manifest.job_id, job_id),
                ("demo_id", manifest.demo_id, row["demo_id"]),
                ("generation_id", manifest.generation_id, row["generation_id"]),
                ("profile_key", manifest.profile_key, row["profile_key"]),
            )
            for field, actual, wanted in identity:
                if actual != wanted:
                    raise ArtifactInvalid(f"manifest {field} {actual!r} does not match running job {wanted!r}")
            file_manifest = read_manifest(path)
            for field in ("job_id", "demo_id", "generation_id", "profile_key"):
                actual = getattr(file_manifest, field)
                wanted = getattr(manifest, field)
                if actual != wanted:
                    raise ArtifactInvalid(f"published manifest {field} {actual!r} != {wanted!r}")
            assert_table_layout(file_manifest, path.parent)
            relpath = expected.relative_to(self.data_root).as_posix()
            conn.execute(
                """
                INSERT INTO generations
                    (generation_id, demo_id, profile_key, job_id, manifest_relpath, map_name, quality,
                     source_size, warnings_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (generation_id) DO UPDATE SET
                    manifest_relpath = excluded.manifest_relpath,
                    map_name = excluded.map_name,
                    quality = excluded.quality,
                    source_size = excluded.source_size,
                    warnings_json = excluded.warnings_json
                """,
                (
                    row["generation_id"],
                    row["demo_id"],
                    row["profile_key"],
                    job_id,
                    relpath,
                    file_manifest.map_name,
                    file_manifest.quality,
                    file_manifest.source_size,
                    json.dumps(file_manifest.warnings),
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO demo_heads (demo_id, profile_key, generation_id, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (demo_id, profile_key) DO UPDATE SET
                    generation_id = excluded.generation_id, updated_at = excluded.updated_at
                """,
                (row["demo_id"], row["profile_key"], row["generation_id"], now),
            )
            finished = conn.execute(
                """
                UPDATE jobs SET state = 'succeeded', finished_at = ?, updated_at = ?,
                                error_json = NULL, worker_pid = NULL
                WHERE id = ? AND state = 'running'
                """,
                (now, now, job_id),
            )
            if finished.rowcount != 1:
                raise CatalogError(f"job {job_id} changed state during completion", code="JOB_STATE", retryable=True)

    def fail(self, job_id: str, error: ErrorResponse, state: str = "failed") -> None:
        if state not in FAIL_STATES:
            raise CatalogError(f"state {state!r} is not a failure state", code="INVALID_ARGUMENT")
        now = utc_now()
        with self._tx() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if row is None:
                raise CatalogError(f"unknown job {job_id}", code="UNKNOWN_JOB")
            if row["state"] not in ACTIVE_STATES:
                raise CatalogError(
                    f"job {job_id} is already {row['state']} and cannot become {state}", code="JOB_STATE"
                )
            conn.execute(
                """
                UPDATE jobs SET state = ?, error_json = ?, finished_at = ?, updated_at = ?, worker_pid = NULL
                WHERE id = ?
                """,
                (state, error.model_dump_json(), now, now, job_id),
            )

    def generation_path(self, demo_id: str, generation_id: str) -> Path | None:
        """Manifest path of a published generation, or None when it is unusable."""
        rows = self._query(
            "SELECT manifest_relpath FROM generations WHERE generation_id = ? AND demo_id = ?",
            (generation_id, demo_id),
        )
        if not rows:
            return None
        candidate = normalize_path(self.data_root / rows[0]["manifest_relpath"])
        root = self.data_root
        if not (len(candidate.parts) > len(root.parts) and candidate.parts[: len(root.parts)] == root.parts):
            return None
        if os.path.islink(candidate) or not candidate.is_file():
            return None
        return candidate

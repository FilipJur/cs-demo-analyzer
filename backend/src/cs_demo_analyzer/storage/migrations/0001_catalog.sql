-- Catalog schema 1: roots, content identity, source locations, durable jobs,
-- published generations and the last-good pointer per profile.
--
-- Gameplay tables never live in SQLite: the seven bounded canonical tables are
-- Parquet datasets owned by their generation (see domain/tables.py SCHEMAS).
-- The application is the only writer; every migration file records its own
-- version so re-applying is idempotent.

CREATE TABLE IF NOT EXISTS schema_migrations (
    version    INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

-- Discovery roots, kept even while unavailable so the watcher can rearm them.
CREATE TABLE IF NOT EXISTS roots (
    root_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT    NOT NULL UNIQUE,
    recursive  INTEGER NOT NULL DEFAULT 0 CHECK (recursive IN (0, 1)),
    available  INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0, 1)),
    error      TEXT,
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL
);

-- One row per distinct recording. demo_id is the SHA-256 of the exact .dem
-- bytes, so identical bytes found at two locations converge here.
CREATE TABLE IF NOT EXISTS demos (
    demo_id          TEXT PRIMARY KEY,
    raw_path         TEXT NOT NULL,
    size             INTEGER NOT NULL,
    source_path      TEXT NOT NULL,
    fingerprint_json TEXT,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
);

-- Source locations observed on disk (candidates and alternates for one demo).
-- status is deliberately free-form app vocabulary: settling, snapshotting,
-- imported, missing, unsupported, error.
CREATE TABLE IF NOT EXISTS sources (
    path             TEXT PRIMARY KEY,
    fingerprint_json TEXT,
    status           TEXT NOT NULL,
    demo_id          TEXT REFERENCES demos (demo_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    error_json       TEXT,
    updated_at       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS sources_demo_idx ON sources (demo_id);

-- Durable extraction jobs. generation_id is the attempt token: it is unique per
-- job row and uniquely names that attempt's staged and published artifacts, so a
-- stale child can never publish over a newer attempt.
CREATE TABLE IF NOT EXISTS jobs (
    id            TEXT PRIMARY KEY,
    demo_id       TEXT    NOT NULL REFERENCES demos (demo_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    profile_key   TEXT    NOT NULL,
    state         TEXT    NOT NULL CHECK (state IN ('queued', 'running', 'succeeded', 'failed', 'interrupted')),
    generation_id TEXT    NOT NULL UNIQUE,
    attempt       INTEGER NOT NULL DEFAULT 1 CHECK (attempt >= 1),
    force         INTEGER NOT NULL DEFAULT 0 CHECK (force IN (0, 1)),
    created_at    TEXT    NOT NULL,
    updated_at    TEXT    NOT NULL,
    started_at    TEXT,
    finished_at   TEXT,
    error_json    TEXT,
    worker_pid    INTEGER
);

CREATE INDEX IF NOT EXISTS jobs_queue_idx ON jobs (state, created_at, id);
CREATE INDEX IF NOT EXISTS jobs_demo_profile_idx ON jobs (demo_id, profile_key, state);
-- At most one active extraction job per demo and profile; explicit reprocessing
-- is a new row, and coalescing in Catalog.enqueue returns the active row.
CREATE UNIQUE INDEX IF NOT EXISTS jobs_active_unique ON jobs (demo_id, profile_key)
    WHERE state IN ('queued', 'running');

-- Published, immutable artifact sets. manifest_relpath is relative to the data
-- root so the catalog survives the root being moved; the manifest file itself
-- carries the table descriptors, hashes and row counts.
CREATE TABLE IF NOT EXISTS generations (
    generation_id    TEXT PRIMARY KEY,
    demo_id          TEXT    NOT NULL REFERENCES demos (demo_id) ON UPDATE CASCADE ON DELETE CASCADE,
    profile_key      TEXT    NOT NULL,
    job_id           TEXT,
    manifest_relpath TEXT    NOT NULL,
    map_name         TEXT,
    quality          TEXT,
    source_size      INTEGER,
    warnings_json    TEXT    NOT NULL DEFAULT '[]',
    created_at       TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS generations_demo_profile_idx ON generations (demo_id, profile_key, created_at);

-- The last-good pointer: a failed reprocess leaves the previous generation
-- readable because nothing here is touched until publication commits.
CREATE TABLE IF NOT EXISTS demo_heads (
    demo_id       TEXT NOT NULL REFERENCES demos (demo_id) ON UPDATE CASCADE ON DELETE CASCADE,
    profile_key   TEXT NOT NULL,
    generation_id TEXT NOT NULL REFERENCES generations (generation_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    updated_at    TEXT NOT NULL,
    PRIMARY KEY (demo_id, profile_key)
);

INSERT INTO schema_migrations (version, applied_at) VALUES (1, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));

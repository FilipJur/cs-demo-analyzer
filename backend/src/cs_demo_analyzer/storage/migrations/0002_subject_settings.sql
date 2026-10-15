-- Catalog schema 2: one singleton application setting row.
--
-- The analysis subject (a 17-digit SteamID64, stored as TEXT so it is never
-- routed through a float) lives in a key/value table rather than in the demo
-- tables: it is application state, not recorded evidence. The row is seeded
-- here so ``SubjectService.get`` always has a defined default; a re-run after a
-- crash between DDL and bookkeeping stays safe.

CREATE TABLE IF NOT EXISTS app_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

INSERT OR IGNORE INTO app_settings (key, value, updated_at)
VALUES ('subject.steam_id', '76561198057213632', strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));

INSERT INTO schema_migrations (version, applied_at) VALUES (2, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));

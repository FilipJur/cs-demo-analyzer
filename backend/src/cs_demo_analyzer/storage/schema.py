"""Ordered SQL migrations for catalog.sqlite.

Migration files live in ``storage/migrations`` and are applied in numeric order.
Each file creates its own objects with ``IF NOT EXISTS`` and records its own
version row, so a re-run after a crash between DDL and bookkeeping is safe.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
CATALOG_SCHEMA_VERSION = 1

_NAME_RE = re.compile(r"^(\d+)_[a-z0-9_]+\.sql$")


def ordered_migrations() -> list[tuple[int, Path]]:
    entries: list[tuple[int, Path]] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        match = _NAME_RE.match(path.name)
        if match is None:
            raise RuntimeError(f"Unrecognised migration file name: {path.name}")
        entries.append((int(match.group(1)), path))
    if not entries:
        raise RuntimeError(f"No SQL migrations found in {MIGRATIONS_DIR}")
    versions = [version for version, _ in entries]
    if len(set(versions)) != len(versions):
        raise RuntimeError(f"Duplicate migration versions in {MIGRATIONS_DIR}")
    return entries


def applied_versions(conn: sqlite3.Connection) -> set[int]:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
    ).fetchone()
    if row is None:
        return set()
    return {int(version) for (version,) in conn.execute("SELECT version FROM schema_migrations")}


def apply_migrations(conn: sqlite3.Connection) -> int:
    """Apply pending migrations and return the resulting catalog schema version."""
    migrations = ordered_migrations()
    known = {version for version, _ in migrations}
    done = applied_versions(conn)
    unknown = done - known
    if unknown:
        raise RuntimeError(
            f"catalog.sqlite was written by a newer application: unknown schema versions {sorted(unknown)}"
        )
    for version, path in migrations:
        if version in done:
            continue
        conn.executescript(path.read_text(encoding="utf-8"))
    return max(applied_versions(conn) or {0})

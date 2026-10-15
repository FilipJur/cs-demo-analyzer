"""Generation-pinned, bounded access to published demo artifacts.

Conventions
-----------
* Every read is *pinned*: a caller holds a :class:`Generation` and cannot drift
  onto a newer head halfway through an analysis. ``generation_id=None`` resolves
  the current head once, at :meth:`GenerationPool.open` time.
* Dense tables are never materialized above ``MAX_MATERIALIZED_ROWS``; callers
  that need more narrow the selection with a predicate or project fewer columns.
  The count is taken before anything is collected, so an oversized window is
  rejected instead of being pulled into memory first.
* Missing data is reported as a typed :class:`AppError` (``NOT_FOUND``,
  ``NOT_READY``, ``GENERATION_UNAVAILABLE``, ``ARTIFACT_INVALID``,
  ``INVALID_ARGUMENT``, ``WINDOW_TOO_LARGE``, all with stage ``"read"``).
  Nothing is fabricated and no empty frame is silently substituted for a
  missing one.
* ``Generation.rounds`` and ``Generation.players`` are the only eager tables
  (one row per round/player). Everything else is reached through
  :meth:`GenerationPool.read`/:meth:`GenerationPool.scan`.
* Opening a generation validates structurally (manifest parses, every table file
  is present, regular and not a symlink) rather than by re-hashing: content
  hashes are verified once at publication time by ``Artifacts.validate``, and
  hashing a dense state table on every analytics open would be wasted work.
  Anything cheaply detectable is still reported as ``ARTIFACT_INVALID``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar

import polars as pl

from ..domain.contracts import AppError, ErrorResponse, Manifest
from ..domain.tables import schema_for_profile
from ..storage.artifacts import MANIFEST_NAME, assert_table_layout, read_manifest
from ..storage.errors import ArtifactInvalid

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ..storage.artifacts import Artifacts
    from ..storage.catalog import Catalog

MAX_MATERIALIZED_ROWS = 120_000

STAGE = "read"

T = TypeVar("T")


@dataclass(frozen=True)
class Generation:
    """One published generation, addressed by an immutable identity."""

    demo_id: str
    generation_id: str
    profile_key: str
    tick_rate_hz: float
    manifest: Manifest
    dir: Path
    rounds: pl.DataFrame
    players: pl.DataFrame


def _profile_schemas(profile: str, generation_id: str) -> dict[str, dict[str, pl.DataType]]:
    """Table schemas of a generation's profile; an unknown profile is a read error."""
    try:
        return schema_for_profile(profile)
    except KeyError:
        raise AppError(
            "ARTIFACT_INVALID",
            f"generation {generation_id} names unknown profile {profile!r}",
            STAGE,
        ) from None


def _empty(schema: dict[str, pl.DataType]) -> pl.DataFrame:
    """Schema-shaped empty frame, used only while a generation is being opened."""
    return pl.DataFrame({name: pl.Series(name, [], dtype=dtype) for name, dtype in schema.items()})


def _error_response(exc: Exception) -> ErrorResponse:
    if isinstance(exc, AppError):
        return ErrorResponse(code=exc.code, message=exc.message, stage=exc.stage, retryable=exc.retryable)
    return ErrorResponse(code="INTERNAL_ERROR", message=str(exc), stage="analytics")


class GenerationPool:
    """Opens pinned generations and reads their tables under a materialization cap."""

    def __init__(self, catalog: Catalog, artifacts: Artifacts) -> None:
        self.catalog = catalog
        self.artifacts = artifacts

    # -- opening -----------------------------------------------------------
    def open(self, demo_id: str, generation_id: str | None = None) -> Generation:
        """Open ``generation_id`` of ``demo_id``; ``None`` resolves the current head.

        Raises a typed :class:`AppError` with stage ``"read"``:
        ``NOT_FOUND`` when the demo is unknown, ``NOT_READY`` when it has no
        published generation yet, ``GENERATION_UNAVAILABLE`` when the requested
        revision is not published (or its bytes are gone), and
        ``ARTIFACT_INVALID`` when the manifest or table layout cannot be used.
        """
        demo = self.catalog.get_demo(demo_id)
        if demo is None:
            raise AppError("NOT_FOUND", f"unknown demo {demo_id}", STAGE)

        wanted = demo.generation_id if generation_id is None else generation_id
        if wanted is None:
            raise AppError("NOT_READY", f"demo {demo_id} has no published generation", STAGE)

        if self.catalog.generation_path(demo_id, wanted) is None:
            raise AppError(
                "GENERATION_UNAVAILABLE",
                f"generation {wanted} of demo {demo_id} is not published or its artifacts are gone",
                STAGE,
            )

        directory = Path(self.artifacts.generation_dir(demo_id, wanted))
        manifest_path = directory / MANIFEST_NAME
        try:
            manifest = read_manifest(manifest_path)
            assert_table_layout(manifest, directory)
        except ArtifactInvalid as exc:
            raise AppError("ARTIFACT_INVALID", str(exc), STAGE) from exc

        if manifest.demo_id != demo_id or manifest.generation_id != wanted:
            raise AppError(
                "ARTIFACT_INVALID",
                f"manifest identity {manifest.demo_id}/{manifest.generation_id} does not match "
                f"the requested {demo_id}/{wanted}",
                STAGE,
            )

        schemas = _profile_schemas(manifest.profile, manifest.generation_id)
        gen = Generation(
            demo_id=demo_id,
            generation_id=wanted,
            profile_key=manifest.profile_key,
            tick_rate_hz=manifest.tick_rate_hz,
            manifest=manifest,
            dir=directory,
            rounds=_empty(schemas["rounds"]),
            players=_empty(schemas["players"]),
        )
        try:
            rounds = self.read(gen, "rounds")
            players = self.read(gen, "players")
        except AppError:
            raise
        except Exception as exc:
            raise AppError("ARTIFACT_INVALID", f"generation {wanted}: tables are unreadable ({exc})", STAGE) from exc
        return replace(gen, rounds=rounds, players=players)

    # -- reading -----------------------------------------------------------
    def scan(
        self,
        gen: Generation,
        table: str,
        *,
        columns: list[str] | None = None,
        predicate: pl.Expr | None = None,
    ) -> pl.LazyFrame:
        """Lazy scan of one table with optional projection and row filter.

        ``table`` must be a table of the generation's profile and ``columns`` a
        subset of it; anything else is ``INVALID_ARGUMENT``. The predicate is
        applied before the projection, so it may reference any column of the table.
        """
        schemas = _profile_schemas(gen.manifest.profile, gen.generation_id)
        schema = schemas.get(table)
        if schema is None:
            raise AppError(
                "INVALID_ARGUMENT",
                f"unknown table {table!r} for profile {gen.manifest.profile!r}; "
                f"known tables {sorted(schemas)}",
                STAGE,
            )
        descriptor = gen.manifest.tables.get(table)
        if descriptor is None:
            raise AppError("INVALID_ARGUMENT", f"generation {gen.generation_id} has no table {table!r}", STAGE)
        if columns is not None:
            unknown = [column for column in columns if column not in schema]
            if unknown:
                raise AppError(
                    "INVALID_ARGUMENT",
                    f"unknown columns {unknown} for table {table!r}; available columns {sorted(schema)}",
                    STAGE,
                )
        if predicate is not None and not isinstance(predicate, pl.Expr):
            raise AppError("INVALID_ARGUMENT", f"predicate must be a polars expression, got {type(predicate).__name__}", STAGE)

        frame = pl.scan_parquet(gen.dir / descriptor.path)
        if predicate is not None:
            frame = frame.filter(predicate)
        if columns is not None:
            frame = frame.select(list(columns))
        return frame

    def read(
        self,
        gen: Generation,
        table: str,
        *,
        columns: list[str] | None = None,
        predicate: pl.Expr | None = None,
        limit: int = MAX_MATERIALIZED_ROWS,
    ) -> pl.DataFrame:
        """Materialize one table selection, refusing windows above ``limit`` rows."""
        if limit <= 0:
            raise AppError("INVALID_ARGUMENT", f"limit must be positive, got {limit}", STAGE)
        counted = self.scan(gen, table, predicate=predicate).select(pl.len()).collect().item()
        total = int(counted)
        if total > limit:
            raise AppError(
                "WINDOW_TOO_LARGE",
                f"table {table} selection has {total} rows, above the {limit}-row materialization cap",
                STAGE,
            )
        # ``limit`` also bounds the collect itself: the table may grow between the
        # count and the read.
        return self.scan(gen, table, columns=columns, predicate=predicate).limit(limit).collect()

    # -- fan-out -----------------------------------------------------------
    def query_many(
        self,
        selections: list[tuple[str, str | None]],
        fn: Callable[[Generation], T],
    ) -> list[dict[str, Any]]:
        """Apply ``fn`` to several demos, capturing per-demo failures.

        Returns one entry per selection, in order:
        ``{"demo_id", "generation_id", "result", "error"}``. A demo that cannot
        be opened, or ``fn`` raising, yields ``result=None`` and an
        :class:`ErrorResponse`; this method itself never raises for a per-demo
        failure. ``generation_id`` echoes what was used: the resolved head on
        success, the requested revision when opening failed.
        """
        results: list[dict[str, Any]] = []
        for demo_id, generation_id in selections:
            try:
                gen = self.open(demo_id, generation_id)
            except Exception as exc:
                results.append(
                    {
                        "demo_id": demo_id,
                        "generation_id": generation_id,
                        "result": None,
                        "error": _error_response(exc),
                    }
                )
                continue
            try:
                value = fn(gen)
            except Exception as exc:
                results.append(
                    {
                        "demo_id": demo_id,
                        "generation_id": gen.generation_id,
                        "result": None,
                        "error": _error_response(exc),
                    }
                )
                continue
            results.append(
                {"demo_id": demo_id, "generation_id": gen.generation_id, "result": value, "error": None}
            )
        return results

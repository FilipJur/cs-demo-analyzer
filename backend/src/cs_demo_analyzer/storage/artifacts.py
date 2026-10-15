"""Immutable artifact staging, validation and publication.

The parser finishes its attempt-specific directory before publication. Validate,
fsync and rename that directory on the same filesystem; do not copy/re-encode
the dataset a second time. The coordinator commits the catalog pointer afterward.

Nothing here schedules, retries or mutates the catalog: the coordinator calls
``Catalog.complete`` after publication.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path

from pydantic import ValidationError

from ..domain.contracts import JobRecord, Manifest
from ..domain.tables import SCHEMAS
from .errors import ArtifactInvalid, StorageError

MANIFEST_NAME = "manifest.json"
TABLE_SUFFIX = ".parquet"
_COPY_CHUNK = 1024 * 1024

_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def is_safe_token(value: str) -> bool:
    """True when ``value`` is a safe single path component for ids we build paths from."""
    return bool(value) and value not in {".", ".."} and _TOKEN_RE.match(value) is not None


def normalize_path(path: str | os.PathLike[str]) -> Path:
    """Lexical normalisation: no filesystem access, no symlink resolution."""
    return Path(os.path.normpath(os.fspath(path)))


def is_within(root: Path, path: Path) -> bool:
    root_parts = root.parts
    path_parts = path.parts
    return len(path_parts) >= len(root_parts) and path_parts[: len(root_parts)] == root_parts


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(_COPY_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _dtype_names(schema: object) -> dict[str, str]:
    items = schema.items() if hasattr(schema, "items") else schema
    return {str(name): str(dtype) for name, dtype in items}  # type: ignore[union-attr]


def _parquet_facts(path: Path) -> tuple[int, dict[str, str]]:
    """Read schema and row-count metadata without materializing dense state."""
    import polars as pl

    schema = pl.read_parquet_schema(path)
    rows = pl.scan_parquet(path).select(pl.len()).collect().item()
    return rows, _dtype_names(schema)


def read_manifest(manifest_path: Path) -> Manifest:
    """Parse a manifest file. Structural table checks are separate and cheap."""
    if os.path.islink(manifest_path) or not manifest_path.is_file():
        raise ArtifactInvalid(f"manifest {manifest_path} is not a regular file")
    try:
        raw = manifest_path.read_bytes()
    except OSError as exc:
        raise ArtifactInvalid(f"manifest {manifest_path} is unreadable: {exc}") from exc
    try:
        return Manifest.model_validate_json(raw)
    except ValidationError as exc:
        raise ArtifactInvalid(f"manifest {manifest_path} does not match the contract: {exc}") from exc


def _table_file_name(descriptor_path: str, table: str) -> str:
    """Bounded single-component Parquet file name for one table descriptor."""
    if not descriptor_path:
        raise ArtifactInvalid(f"table {table}: descriptor path is empty")
    candidate = Path(descriptor_path)
    if candidate.is_absolute() or candidate.name != descriptor_path:
        raise ArtifactInvalid(f"table {table}: descriptor path {descriptor_path!r} must be a relative file name")
    if descriptor_path == MANIFEST_NAME or not descriptor_path.endswith(TABLE_SUFFIX):
        raise ArtifactInvalid(f"table {table}: descriptor path {descriptor_path!r} is not a table file")
    if descriptor_path.startswith("."):
        raise ArtifactInvalid(f"table {table}: descriptor path {descriptor_path!r} looks like a temporary file")
    return descriptor_path


def assert_table_layout(manifest: Manifest, directory: Path) -> dict[str, str]:
    """Check the manifest table set and that each referenced file exists.

    Cheap enough for a short catalog transaction: it stats files and never reads
    or hashes them. Returns table name -> file name.
    """
    expected = set(SCHEMAS)
    found = set(manifest.tables)
    if found != expected:
        missing = sorted(expected - found)
        extra = sorted(found - expected)
        raise ArtifactInvalid(
            f"manifest tables do not match the frozen profile (missing={missing}, unexpected={extra})"
        )
    names: dict[str, str] = {}
    owner: dict[str, str] = {}
    for table in sorted(found):
        name = _table_file_name(manifest.tables[table].path, table)
        if name in owner:
            raise ArtifactInvalid(f"tables {owner[name]} and {table} share table file {name!r}")
        owner[name] = table
        path = directory / name
        if os.path.islink(path):
            raise ArtifactInvalid(f"table {table}: {name} is a symlink")
        try:
            info = os.stat(path, follow_symlinks=False)
        except OSError as exc:
            raise ArtifactInvalid(f"table {table}: missing table file {name} ({exc})") from exc
        if not stat.S_ISREG(info.st_mode):
            raise ArtifactInvalid(f"table {table}: {name} is not a regular file")
        names[table] = name
    return names


class Artifacts:
    """Filesystem side of generation publication for one configured data root."""

    def __init__(self, data_root: Path | str) -> None:
        root = normalize_path(data_root)
        if not root.is_absolute():
            raise StorageError(f"data root must be absolute, got {data_root}", code="INVALID_ARGUMENT")
        self.data_root = root

    # -- paths -------------------------------------------------------------
    def stage_dir(self, job: JobRecord) -> Path:
        if not is_safe_token(job.id) or not is_safe_token(job.generation_id):
            raise StorageError(
                f"unsafe staging token in job {job.id!r}/{job.generation_id!r}", code="INVALID_ARGUMENT"
            )
        directory = self.data_root / "staging" / job.id / job.generation_id
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        return directory

    def generation_dir(self, demo_id: str, generation_id: str) -> Path:
        for token, label in ((demo_id, "demo id"), (generation_id, "generation id")):
            if not is_safe_token(token):
                raise StorageError(f"unsafe {label} {token!r}", code="INVALID_ARGUMENT")
        return self.data_root / "datasets" / demo_id / generation_id

    # -- validation --------------------------------------------------------
    def validate(self, manifest_path: Path) -> Manifest:
        """Full validation of a published or staged generation."""
        path = normalize_path(manifest_path)
        if not is_within(self.data_root, path):
            raise ArtifactInvalid(f"manifest {path} is outside the data root")
        self._assert_no_symlink_components(path)
        manifest = read_manifest(path)
        directory = path.parent
        names = assert_table_layout(manifest, directory)
        self._verify_tables(manifest, directory, names)
        return manifest

    def _assert_no_symlink_components(self, path: Path) -> None:
        relative = path.relative_to(self.data_root)
        current = self.data_root
        for part in relative.parts:
            current = current / part
            if os.path.islink(current):
                raise ArtifactInvalid(f"path component {current} is a symlink")

    def _verify_tables(self, manifest: Manifest, directory: Path, names: dict[str, str]) -> None:
        for table in sorted(SCHEMAS):
            descriptor = manifest.tables[table]
            path = directory / names[table]
            expected_dtypes = {column: str(dtype) for column, dtype in SCHEMAS[table].items()}
            try:
                rows, dtypes = _parquet_facts(path)
            except Exception as exc:
                raise ArtifactInvalid(f"table {table}: {names[table]} is not a readable Parquet file ({exc})") from exc
            if rows != descriptor.row_count:
                raise ArtifactInvalid(
                    f"table {table}: {names[table]} has {rows} rows, descriptor claims {descriptor.row_count}"
                )
            if set(dtypes) != set(expected_dtypes):
                raise ArtifactInvalid(
                    f"table {table}: columns {sorted(dtypes)} do not match the frozen schema {sorted(expected_dtypes)}"
                )
            mismatched = {
                column: (dtypes[column], expected_dtypes[column])
                for column in expected_dtypes
                if dtypes[column] != expected_dtypes[column]
            }
            if mismatched:
                raise ArtifactInvalid(f"table {table}: declared dtypes do not match the file: {mismatched}")
            digest = sha256_file(path)
            if digest.lower() != descriptor.sha256.lower():
                raise ArtifactInvalid(
                    f"table {table}: sha256 mismatch for {names[table]} ({digest} != {descriptor.sha256})"
                )

    # -- publication -------------------------------------------------------
    def publish(self, job: JobRecord, manifest_path: Path) -> tuple[Manifest, Path]:
        """Validate the staged generation and rename it into ``datasets/``."""
        if job.state != "running":
            raise ArtifactInvalid(f"job {job.id} is {job.state}; only a running job may publish")
        staging = self.stage_dir(job)
        stage = normalize_path(manifest_path)
        if stage != normalize_path(staging / MANIFEST_NAME):
            raise ArtifactInvalid(f"staged manifest must be {staging / MANIFEST_NAME}, got {stage}")
        manifest = self.validate(stage)
        self._fence(job, manifest)

        final_dir = self.generation_dir(manifest.demo_id, manifest.generation_id)
        if final_dir.exists() or os.path.islink(final_dir):
            raise ArtifactInvalid(f"generation {manifest.generation_id} is already published at {final_dir}")

        demo_dir = final_dir.parent
        demo_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._assert_no_symlink_components(demo_dir)
        for name in [descriptor.path for descriptor in manifest.tables.values()] + [MANIFEST_NAME]:
            with (staging / name).open("rb") as handle:
                os.fsync(handle.fileno())
        _fsync_dir(staging)
        os.rename(staging, final_dir)
        _fsync_dir(demo_dir)
        _fsync_dir(demo_dir.parent)
        _fsync_dir(staging.parent)
        return manifest, final_dir / MANIFEST_NAME

    def _fence(self, job: JobRecord, manifest: Manifest) -> None:
        pairs = (
            ("job_id", manifest.job_id, job.id),
            ("demo_id", manifest.demo_id, job.demo_id),
            ("generation_id", manifest.generation_id, job.generation_id),
            ("profile_key", manifest.profile_key, job.profile_key),
        )
        for field, actual, expected in pairs:
            if actual != expected:
                raise ArtifactInvalid(
                    f"manifest {field} {actual!r} does not match the running job's {expected!r}"
                )


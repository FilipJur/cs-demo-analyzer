from __future__ import annotations

import errno
import hashlib
import os
import shutil
import stat
import threading
import time
from pathlib import Path
from uuid import uuid4

from ..config import Settings
from ..domain.contracts import AppError, ErrorResponse, Fingerprint, Observation, Snapshot

MAGIC = b"PBDEMS2\0"
COMPRESSED = (".dem.gz", ".dem.bz2", ".dem.zst", ".dem.zip")


def error_from(exc: Exception, stage: str) -> ErrorResponse:
    if isinstance(exc, AppError):
        return ErrorResponse(**exc.payload())
    if isinstance(exc, OSError):
        code = {errno.ENOSPC: "DISK_FULL", errno.EDQUOT: "DISK_FULL", errno.ENOENT: "SOURCE_MISSING", errno.EACCES: "PERMISSION_DENIED", errno.EPERM: "PERMISSION_DENIED"}.get(exc.errno, "IO_ERROR")
        return ErrorResponse(code=code, message=str(exc), stage=stage, retryable=True)
    return ErrorResponse(code="INTERNAL_ERROR", message=str(exc), stage=stage, retryable=False)


def _fingerprint(s: os.stat_result) -> Fingerprint:
    return Fingerprint(device=s.st_dev, inode=s.st_ino, size=s.st_size, mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def snapshot_source(observation: Observation, settings: Settings) -> Snapshot:
    source = Path(observation.path)
    if any(source.name.lower().endswith(suffix) for suffix in COMPRESSED):
        raise AppError("UNSUPPORTED_COMPRESSED", "Compressed demos are unsupported; supply the decompressed .dem", "snapshot")
    if source.suffix.lower() != ".dem":
        raise AppError("UNSUPPORTED_FORMAT", "Only ordinary CS2 .dem files are supported", "snapshot")
    settings.check_space(observation.fingerprint.size, copying=True)
    stage = settings.data_root / "staging" / f"import-{uuid4().hex}"
    stage.mkdir(mode=0o700)
    temporary = stage / "source.dem"
    try:
        fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as src:
            before = os.fstat(src.fileno())
            if not stat.S_ISREG(before.st_mode) or _fingerprint(before) != observation.fingerprint:
                raise AppError("SOURCE_UNSTABLE", "Source changed before snapshotting", "snapshot", True)
            magic = src.read(8)
            if magic != MAGIC:
                raise AppError("INVALID_DEMO", "File is not a CS2 PBDEMS2 demo", "snapshot")
            digest = hashlib.sha256(magic)
            with temporary.open("xb") as dst:
                dst.write(magic)
                while chunk := src.read(1024 * 1024):
                    digest.update(chunk)
                    dst.write(chunk)
                dst.flush()
                os.fsync(dst.fileno())
            if _fingerprint(os.fstat(src.fileno())) != observation.fingerprint or Fingerprint.from_path(source) != observation.fingerprint:
                raise AppError("SOURCE_UNSTABLE", "Source changed during snapshotting", "snapshot", True)
        demo_id = digest.hexdigest()
        directory = settings.data_root / "raw" / demo_id
        directory.mkdir(exist_ok=True, mode=0o700)
        target = directory / "source.dem"
        if target.is_symlink():
            raise AppError("ARTIFACT_INVALID", "Owned raw path is a symlink", "snapshot")
        if target.exists():
            with target.open("rb") as existing:
                if target.stat().st_size != observation.fingerprint.size or hashlib.file_digest(existing, "sha256").hexdigest() != demo_id:
                    raise AppError("ARTIFACT_INVALID", "Existing owned recording failed content verification", "snapshot")
        else:
            # Import is serialized by the coordinator, and raw files are never modified.
            os.rename(temporary, target)
            target.chmod(0o400)
            fsync_dir(directory)
            fsync_dir(directory.parent)
        return Snapshot(demo_id=demo_id, raw_path=str(target), size=observation.fingerprint.size, source_path=str(source), fingerprint=observation.fingerprint)
    finally:
        shutil.rmtree(stage)


class IngestionService:
    def __init__(self, settings: Settings, catalog):
        self.settings, self.catalog = settings, catalog
        self._pending: dict[str, tuple[Fingerprint, float, int]] = {}
        self._sidecars: dict[str, Fingerprint] = {}
        self._lock = threading.RLock()

    def consider(self, observation: Observation, *, force: bool = False) -> str | None:
        with self._lock:
            return self._consider(observation, force=force)

    def _consider(self, observation: Observation, *, force: bool) -> str | None:
        path = observation.path
        previous = self.catalog.get_source(path)
        if not force and previous and previous.fingerprint == observation.fingerprint and previous.status in ("imported", "error", "unsupported"):
            if previous.demo_id and previous.status == "imported":
                self.catalog.enqueue(previous.demo_id)
                self.capture_sidecar(path, previous.demo_id)
            return previous.demo_id
        pending = self._pending.get(path)
        if force or pending is None or pending[0] != observation.fingerprint:
            self._pending[path] = (observation.fingerprint, time.monotonic(), 1)
            self.catalog.set_source(path, observation.fingerprint, "settling")
            return None
        fingerprint, began, count = pending
        count += 1
        self._pending[path] = (fingerprint, began, count)
        if count < 3 or time.monotonic() - began < self.settings.settle_seconds:
            return None
        self.catalog.set_source(path, fingerprint, "snapshotting")
        try:
            snapshot = snapshot_source(observation, self.settings)
            self.catalog.register_demo(snapshot)
            self.catalog.set_source(path, fingerprint, "imported", demo_id=snapshot.demo_id)
            self.catalog.enqueue(snapshot.demo_id)
            self.capture_sidecar(path, snapshot.demo_id)
            return snapshot.demo_id
        except Exception as exc:
            error = error_from(exc, "snapshot")
            status = "unsupported" if error.code.startswith("UNSUPPORTED") else "error"
            self.catalog.set_source(path, fingerprint, status, error=error)
            if error.code == "SOURCE_UNSTABLE":
                self._pending.pop(path, None)
            return None
        finally:
            self._pending.pop(path, None)

    def pending_paths(self) -> list[str]:
        with self._lock:
            return list(self._pending)

    def missing(self, path: str, exc: Exception) -> None:
        with self._lock:
            previous = self.catalog.get_source(path)
            self._pending.pop(path, None)
            self.catalog.set_source(path, previous.fingerprint if previous else None, "missing", error=error_from(exc, "discovery"))

    def capture_sidecar(self, source: str, demo_id: str) -> None:
        sidecar = Path(source + ".info")
        if not sidecar.is_file() or sidecar.is_symlink():
            return
        try:
            fingerprint = Fingerprint.from_path(sidecar)
            if self._sidecars.get(source) == fingerprint:
                return
            if fingerprint.size > 1024 * 1024:
                raise AppError("SIDECAR_TOO_LARGE", "Optional sidecar exceeds 1 MiB", "sidecar")
            content = sidecar.read_bytes()
            if Fingerprint.from_path(sidecar) != fingerprint:
                return
            digest = hashlib.sha256(content).hexdigest()
            directory = self.settings.data_root / "raw" / demo_id / "sidecars"
            directory.mkdir(exist_ok=True, mode=0o700)
            target = directory / f"{digest}.dem.info"
            valid = (
                target.is_file() and not target.is_symlink()
                and target.stat().st_size == len(content)
                and hashlib.sha256(target.read_bytes()).hexdigest() == digest
            )
            if not valid:
                temporary = directory / f".{uuid4().hex}.tmp"
                try:
                    with temporary.open("xb") as f:
                        f.write(content)
                        f.flush()
                        os.fsync(f.fileno())
                    temporary.chmod(0o400)
                    os.replace(temporary, target)
                    fsync_dir(directory)
                finally:
                    temporary.unlink(missing_ok=True)
            self._sidecars[source] = fingerprint
            previous = self.catalog.get_source(source)
            if previous and previous.error and previous.error.stage == "sidecar":
                self.catalog.set_source(source, previous.fingerprint, previous.status, demo_id=demo_id)
        except Exception as exc:
            previous = self.catalog.get_source(source)
            if previous:
                self.catalog.set_source(source, previous.fingerprint, previous.status, demo_id=demo_id, error=error_from(exc, "sidecar"))

from __future__ import annotations

import fcntl
import hashlib
import json
import logging
import os
import queue
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from .assets.radar import RadarService
from .config import Settings
from .discovery.steam import discover_install, discover_roots
from .discovery.watcher import scan_root, watch_roots
from .domain.contracts import Accepted, AppError, ErrorResponse, ExtractionRequest, Fingerprint, Observation, RootRequest, WorkerResult
from .domain.contracts import Snapshot
from .ingestion.service import IngestionService, error_from
from .storage.artifacts import Artifacts
from .storage.catalog import Catalog

logger = logging.getLogger(__name__)


class Application:
    def __init__(self, settings: Settings):
        self.settings = settings
        install = discover_install(settings.install_path)
        if install and settings.data_root.is_relative_to(install.resolve()):
            raise AppError("INVALID_CONFIG", "Data root must be outside the CS2 installation", "startup")
        settings.prepare()
        self._lock_file = (settings.data_root / ".instance.lock").open("a+")
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock_file.close()
            raise AppError("ALREADY_RUNNING", "Another application owns this data root", "startup") from None
        self.catalog = Catalog(settings.data_root)
        self.artifacts = Artifacts(settings.data_root)
        self.ingestion = IngestionService(settings, self.catalog)
        self.radar = RadarService(settings.data_root, install, settings.source2viewer)
        self._stop, self._wake = threading.Event(), threading.Event()
        self._requests: queue.Queue[tuple[str, bool]] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._watcher: threading.Thread | None = None
        self._watch_stop = threading.Event()
        self._watch_signature: tuple = ()
        self._process: subprocess.Popen | None = None
        self._closed = False

    @property
    def worker_running(self) -> bool:
        return self._process is not None

    def start(self, *, discover: bool = True) -> None:
        if self._thread:
            return
        self._recover()
        if discover:
            for root in discover_roots(self.settings.install_path):
                self.catalog.add_root(root.path, root.recursive)
        self._ensure_watcher()
        self._thread = threading.Thread(target=self._loop, name="csda-coordinator", daemon=True)
        self._thread.start()
        self._wake.set()

    def _recover(self) -> None:
        for job in self.catalog.running_jobs():
            final = self.settings.data_root / "datasets" / job.demo_id / job.generation_id / "manifest.json"
            try:
                if final.is_file():
                    manifest = self.artifacts.validate(final)
                    self.catalog.complete(job.id, manifest, final)
                else:
                    self.catalog.fail(job.id, ErrorResponse(code="INTERRUPTED", message="Previous extraction was interrupted", stage="recovery", retryable=True), state="interrupted")
                    self.catalog.enqueue(job.demo_id, force=True)
            except Exception as exc:
                self.catalog.fail(job.id, error_from(exc, "recovery"))
        for job in self.catalog.interrupted_jobs():
            self.catalog.enqueue(job.demo_id, force=True)
        # Recover a raw rename interrupted before catalog registration, even
        # when the external source has disappeared in the meantime.
        for directory in (self.settings.data_root / "raw").iterdir():
            demo_id = directory.name
            if len(demo_id) != 64 or any(c not in "0123456789abcdef" for c in demo_id) or self.catalog.get_demo(demo_id):
                continue
            raw = directory / "source.dem"
            if directory.is_symlink() or raw.is_symlink() or not raw.is_file():
                continue
            with raw.open("rb") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
            if digest != demo_id:
                logger.error("Unregistered raw recording failed content verification: %s", demo_id)
                continue
            self.catalog.register_demo(Snapshot(demo_id=demo_id, raw_path=str(raw), size=raw.stat().st_size, source_path=str(raw), fingerprint=Fingerprint.from_path(raw)))
            self.catalog.enqueue(demo_id)
        # Import copying happens only in this process, never in an orphan child.
        for path in (self.settings.data_root / "staging").glob("import-*"):
            suffix = path.name.removeprefix("import-")
            if len(suffix) == 32 and all(c in "0123456789abcdef" for c in suffix) and path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)

    def request_import(self, path: str) -> Accepted:
        source = Path(path).expanduser()
        if not source.is_absolute():
            raise AppError("INVALID_PATH", "Import path must be absolute", "import")
        if source.is_symlink():
            raise AppError("INVALID_PATH", "Import source cannot be a symlink", "import")
        source = source.resolve()
        if source.is_relative_to(self.settings.data_root):
            raise AppError("INVALID_PATH", "The application data root cannot be imported", "import")
        self._requests.put((str(source), True))
        self._wake.set()
        return Accepted(status="settling")

    def request_scan(self) -> Accepted:
        self._wake.set()
        return Accepted(status="scheduled")

    def add_root(self, request: RootRequest):
        path = Path(request.path).expanduser()
        if not path.is_absolute():
            raise AppError("INVALID_PATH", "Root path must be absolute", "discovery")
        resolved = path.resolve()
        if resolved.is_relative_to(self.settings.data_root):
            raise AppError("INVALID_PATH", "The application data root cannot be watched", "discovery")
        root = self.catalog.add_root(str(resolved), request.recursive)
        self._wake.set()
        return root

    def reprocess(self, demo_id: str):
        if self.catalog.get_demo(demo_id) is None:
            raise AppError("NOT_FOUND", "Demo does not exist", "reprocess")
        job = self.catalog.enqueue(demo_id, force=True)
        self._wake.set()
        return Accepted(status=job.state, job_id=job.id, demo_id=demo_id)

    def _ensure_watcher(self) -> None:
        roots = self.catalog.list_roots()
        signature = tuple((r.id, r.path, r.recursive, r.available) for r in roots)
        if signature == self._watch_signature and self._watcher and self._watcher.is_alive():
            return
        self._watch_stop.set()
        if self._watcher:
            self._watcher.join(timeout=6)
        self._watch_stop = threading.Event()
        self._watch_signature = signature
        if roots and not self._stop.is_set():
            self._watcher = threading.Thread(target=watch_roots, args=(roots, self._watch_stop, self._wake.set), name="csda-watcher", daemon=True)
            self._watcher.start()

    def _observe_path(self, path: str, *, force: bool = False) -> None:
        try:
            p = Path(path)
            if p.is_symlink() or not p.is_file():
                raise FileNotFoundError(f"Not a regular local file: {path}")
            if p.resolve().is_relative_to(self.settings.data_root):
                return
            self.ingestion.consider(Observation(path=str(p), fingerprint=Fingerprint.from_path(p)), force=force)
        except Exception as exc:
            self.ingestion.missing(path, exc)

    def _scan(self) -> None:
        seen = set()
        for root in self.catalog.list_roots():
            try:
                observations = scan_root(root, self.settings.data_root)
                self.catalog.update_root(root.id, True)
                for observation in observations:
                    if observation.path not in seen:
                        seen.add(observation.path)
                        self.ingestion.consider(observation)
            except Exception as exc:
                self.catalog.update_root(root.id, False, str(exc))
        for source in self.catalog.list_sources():
            if source.status == "imported" and not Path(source.path).exists():
                self.ingestion.missing(source.path, FileNotFoundError(source.path))

    def _loop(self) -> None:
        last_scan = 0.0
        while not self._stop.is_set():
            try:
                triggered = self._wake.is_set()
                self._wake.clear()
                while True:
                    try:
                        path, force = self._requests.get_nowait()
                    except queue.Empty:
                        break
                    self._observe_path(path, force=force)
                if triggered or time.monotonic() - last_scan >= self.settings.scan_seconds:
                    self._scan()
                    last_scan = time.monotonic()
                for path in self.ingestion.pending_paths():
                    self._observe_path(path)
                self._ensure_watcher()
                if job := self.catalog.claim_next():
                    self._run_job(job)
                    continue
            except Exception:
                logger.exception("Coordinator iteration failed; pending state remains durable")
            self._wake.wait(self.settings.poll_seconds)

    def _run_job(self, job) -> None:
        process = None
        try:
            demo = self.catalog.get_demo(job.demo_id)
            if demo is None:
                raise AppError("NOT_FOUND", "Queued recording is unavailable", "parse")
            self.settings.check_space(demo.size, copying=False)
            stage = self.artifacts.stage_dir(job)
            request = ExtractionRequest(job_id=job.id, generation_id=job.generation_id, demo_id=job.demo_id, input_path=demo.raw_path, output_dir=str(stage), parent_pid=os.getpid())
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                process = subprocess.Popen([sys.executable, "-m", "cs_demo_analyzer.worker.main"], stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, start_new_session=True)
                self._process = process
                self.catalog.set_worker(job.id, process.pid)
                try:
                    process.communicate(request.model_dump_json().encode() + b"\n", timeout=self.settings.worker_timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    raise AppError("RESOURCE_LIMIT", "Parser exceeded its time budget", "parse", True) from None
                stdout.seek(0)
                payload = stdout.read(65537)
                stderr.seek(0, os.SEEK_END)
                stderr.seek(max(0, stderr.tell() - 4096))
                diagnostic = stderr.read().decode(errors="replace")
                if self._stop.is_set():
                    raise AppError("INTERRUPTED", "Application stopped during extraction", "parse", True)
                if len(payload) > 65536:
                    raise AppError("WORKER_PROTOCOL", "Parser response exceeded its bound", "parse")
                try:
                    result = WorkerResult.model_validate_json(payload)
                except ValueError:
                    raise AppError("PARSE_FAILED", f"Parser exited {process.returncode}; {diagnostic[-1000:]}", "parse") from None
                if result.error:
                    raise AppError(result.error.code, result.error.message, result.error.stage, result.error.retryable)
                if process.returncode != 0 or not result.manifest_path:
                    raise AppError("PARSE_FAILED", f"Parser exited {process.returncode}", "parse")
            manifest, final = self.artifacts.publish(job, Path(result.manifest_path))
            self.catalog.complete(job.id, manifest, final)
        except Exception as exc:
            error = error_from(exc, "parse")
            self.catalog.fail(job.id, error, state="interrupted" if self._stop.is_set() else "failed")
        finally:
            if process and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            self._process = None

    def close(self) -> None:
        if self._closed:
            return
        self._stop.set()
        self._wake.set()
        self._watch_stop.set()
        process = self._process
        if process and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        if self._thread:
            self._thread.join(timeout=self.settings.worker_timeout + 5)
        if self._watcher:
            self._watcher.join(timeout=6)
        self.catalog.close()
        self._lock_file.close()
        self._closed = True

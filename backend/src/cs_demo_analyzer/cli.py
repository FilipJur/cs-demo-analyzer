from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import uvicorn

from .application import Application
from .api.routes import create_app
from .config import Settings
from .domain.contracts import AppError


def wait_job(app: Application, job_id: str, timeout: float):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = app.catalog.get_job(job_id)
        if job and job.state == "succeeded":
            return job
        if job and job.state in {"failed", "interrupted"}:
            error = job.error
            raise AppError(error.code if error else "PARSE_FAILED", error.message if error else "Extraction failed", error.stage if error else "parse", error.retryable if error else False)
        time.sleep(0.1)
    raise AppError("TIMEOUT", "Timed out waiting for extraction", "cli", True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local CS2 demo discovery, preservation and replay")
    parser.add_argument("--data-root", help="Absolute data directory; overrides CSDA_DATA_ROOT, config and XDG default")
    parser.add_argument("--config", help="Configuration TOML path")
    parser.add_argument("--install-path", type=Path, help="Explicit local CS2 installation")
    parser.add_argument("--source2viewer", type=Path, help="Local Source2Viewer-CLI executable")
    parser.add_argument("--settle-seconds", type=float, help="Quiet-window policy; at least three observations still required")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Run automatic discovery and the loopback web application")
    serve.add_argument("--port", type=int, default=8765)
    ingest = sub.add_parser("import", help="Preserve and parse a local ordinary .dem, then wait for its result")
    ingest.add_argument("path")
    reprocess = sub.add_parser("reprocess", help="Parse a retained recording into a new generation")
    reprocess.add_argument("demo_id")
    sub.add_parser("scan", help="Discover local demos, settle and process the discovered queue, then exit")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    app = None
    try:
        settings = Settings.load(args.data_root, args.config, install_path=args.install_path, source2viewer=args.source2viewer, settle_seconds=args.settle_seconds)
        app = Application(settings)
        if args.command == "serve":
            uvicorn.run(create_app(app), host="127.0.0.1", port=args.port, workers=1)
            return 0
        app.start(discover=args.command == "scan")
        timeout = settings.worker_timeout + settings.settle_seconds + 30
        if args.command == "import":
            path = str(Path(args.path).expanduser().absolute())
            app.request_import(path)
            path = str(Path(path).resolve())
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                source = app.catalog.get_source(path)
                if source and source.status in {"error", "unsupported", "missing"}:
                    e = source.error
                    raise AppError(e.code if e else "IMPORT_FAILED", e.message if e else "Import failed", e.stage if e else "import", e.retryable if e else False)
                if source and source.demo_id:
                    demo = app.catalog.get_demo(source.demo_id)
                    candidates = [j for j in app.catalog.list_jobs() if j.demo_id == source.demo_id]
                    job = next((j for j in candidates if j.state in {"queued", "running"}), None)
                    if job is None:
                        job = next((j for j in candidates if j.state == "succeeded" and j.generation_id == demo.generation_id), None)
                    if job is None:
                        job = next(iter(candidates), None)
                    if job:
                        result = wait_job(app, job.id, timeout)
                        print(json.dumps({"demo": app.catalog.get_demo(source.demo_id).model_dump(), "job": result.model_dump()}))
                        return 0
                time.sleep(0.1)
            raise AppError("TIMEOUT", "Timed out waiting for import", "cli", True)
        if args.command == "reprocess":
            accepted = app.reprocess(args.demo_id)
            result = wait_job(app, accepted.job_id, timeout)
            print(result.model_dump_json())
            return 0
        # A scan includes the quiet window and all discovered jobs; require a
        # brief idle period so the coordinator's first enumeration can finish.
        deadline = time.monotonic() + timeout
        idle_since = None
        while time.monotonic() < deadline:
            sources, jobs = app.catalog.list_sources(), app.catalog.list_jobs()
            active = any(s.status in {"settling", "snapshotting"} for s in sources) or any(j.state in {"queued", "running"} for j in jobs)
            if active:
                idle_since = None
            elif idle_since is None:
                idle_since = time.monotonic()
            elif time.monotonic() - idle_since > max(3, settings.poll_seconds * 2):
                print(json.dumps({"roots": [r.model_dump() for r in app.catalog.list_roots()], "sources": [s.model_dump() for s in sources], "jobs": [j.model_dump() for j in jobs]}))
                return 1 if any(s.error for s in sources) or any(j.state == "failed" for j in jobs) else 0
            time.sleep(0.1)
        raise AppError("TIMEOUT", "Scan did not become idle before timeout", "cli", True)
    except AppError as exc:
        print(json.dumps(exc.payload()), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    finally:
        if app:
            app.close()


if __name__ == "__main__":
    raise SystemExit(main())

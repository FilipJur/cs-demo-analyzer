from __future__ import annotations

import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..domain.contracts import Accepted, AppError, DemoDetail, DemoRecord, ErrorResponse, HealthResponse, ImportRequest, JobRecord, RootRecord, RootRequest, RoundResponse, ReplayChunk, SourceRecord
from .replay import ReplayReader


def create_app(runtime, *, manage_lifetime: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        if manage_lifetime:
            runtime.start()
        try:
            yield
        finally:
            if manage_lifetime:
                runtime.close()

    app = FastAPI(title="CS2 Demo Analyzer", version="0.1.0", lifespan=lifespan)
    reader = ReplayReader(runtime)

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        host = request.url.hostname
        if host not in {"127.0.0.1", "localhost"}:
            return JSONResponse(ErrorResponse(code="INVALID_HOST", message="Only loopback hosts are allowed", stage="http").model_dump(), status_code=403)
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            allowed = {f"{request.url.scheme}://{request.url.netloc}"}
            if development_origin := os.environ.get("CSDA_DEV_ORIGIN"):
                parsed = urlsplit(development_origin)
                if parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1"}:
                    allowed.add(development_origin.rstrip("/"))
            if origin and origin not in allowed:
                return JSONResponse(ErrorResponse(code="INVALID_ORIGIN", message="Cross-origin writes are forbidden", stage="http").model_dump(), status_code=403)
            if request.headers.get("content-type", "").split(";", 1)[0] != "application/json":
                return JSONResponse(ErrorResponse(code="INVALID_CONTENT_TYPE", message="Mutations require application/json", stage="http").model_dump(), status_code=415)
        return await call_next(request)

    @app.exception_handler(AppError)
    async def application_error(request: Request, exc: AppError):
        status = 404 if exc.code in {"NOT_FOUND", "GENERATION_UNAVAILABLE"} else 409 if exc.code in {"NOT_READY", "PARTIAL_ROUND"} else 507 if exc.code == "DISK_FULL" else 400
        return JSONResponse(exc.payload(), status_code=status)

    @app.exception_handler(OSError)
    async def io_error(request: Request, exc: OSError):
        return JSONResponse(ErrorResponse(code="ARTIFACT_INVALID", message=str(exc), stage="read", retryable=True).model_dump(), status_code=409)

    prefix = "/api/v1"
    errors = {400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 507: {"model": ErrorResponse}}

    @app.get(prefix + "/health", response_model=HealthResponse)
    def health():
        return HealthResponse(status="ready", data_root=str(runtime.settings.data_root), worker_running=runtime.worker_running, free_bytes=shutil.disk_usage(runtime.settings.data_root).free)

    @app.get(prefix + "/roots", response_model=list[RootRecord])
    def roots():
        return runtime.catalog.list_roots()

    @app.post(prefix + "/roots", response_model=RootRecord, responses=errors)
    def add_root(body: RootRequest):
        return runtime.add_root(body)

    @app.post(prefix + "/scans", response_model=Accepted, status_code=202)
    def scan():
        return runtime.request_scan()

    @app.post(prefix + "/imports", response_model=Accepted, status_code=202, responses=errors)
    def import_file(body: ImportRequest):
        return runtime.request_import(body.path)

    @app.get(prefix + "/sources", response_model=list[SourceRecord])
    def sources():
        return runtime.catalog.list_sources()

    @app.get(prefix + "/demos", response_model=list[DemoRecord])
    def demos(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
        return runtime.catalog.list_demos(limit, offset)

    @app.get(prefix + "/demos/{demo_id}", response_model=DemoDetail, responses=errors)
    def demo_detail(demo_id: str):
        demo = runtime.catalog.get_demo(demo_id)
        if demo is None:
            raise AppError("NOT_FOUND", "Demo does not exist", "read")
        manifest = reader.manifest(demo_id)[0] if demo.generation_id else None
        return DemoDetail(demo=demo, sources=runtime.catalog.list_sources(demo_id), manifest=manifest)

    @app.get(prefix + "/jobs", response_model=list[JobRecord])
    def jobs():
        return runtime.catalog.list_jobs()

    @app.get(prefix + "/jobs/{job_id}", response_model=JobRecord, responses=errors)
    def job(job_id: str):
        value = runtime.catalog.get_job(job_id)
        if value is None:
            raise AppError("NOT_FOUND", "Job does not exist", "read")
        return value

    @app.post(prefix + "/demos/{demo_id}/reprocess", response_model=Accepted, status_code=202, responses=errors)
    def reprocess(demo_id: str):
        return runtime.reprocess(demo_id)

    @app.get(prefix + "/demos/{demo_id}/rounds", response_model=RoundResponse, responses=errors)
    def rounds(demo_id: str, generation_id: str | None = None):
        return reader.rounds(demo_id, generation_id)

    @app.get(prefix + "/demos/{demo_id}/replay", response_model=ReplayChunk, responses=errors)
    def replay(demo_id: str, generation_id: str, round_id: int = Query(ge=1), stride_ticks: int | None = Query(None, ge=1, le=4096), start_tick: int | None = None, end_tick: int | None = None):
        return reader.replay(demo_id, generation_id, round_id, stride_ticks, start_tick, end_tick)

    @app.get(prefix + "/assets/{asset_id}", responses=errors)
    def asset(asset_id: str):
        path = runtime.radar.asset_path(asset_id)
        if path is None:
            raise AppError("NOT_FOUND", "Asset is unavailable", "assets")
        return FileResponse(path, media_type="image/png")

    dist = Path(__file__).resolve().parents[4] / "web/dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="web")
    return app

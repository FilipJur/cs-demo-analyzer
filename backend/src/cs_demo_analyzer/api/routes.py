from __future__ import annotations

import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Callable, Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from ..analytics import identity, spatial, temporal
from ..analytics.access import Generation, GenerationPool
from ..domain.contracts import (
    SCHEMA_VERSION,
    Accepted,
    AnalyticState,
    AppError,
    CoverageResponse,
    DemoDetail,
    DemoRecord,
    DistanceResponse,
    ErrorResponse,
    EventWindowResponse,
    EventsResponse,
    HealthResponse,
    ImportRequest,
    JobRecord,
    Model,
    ReplayChunk,
    RootRecord,
    RootRequest,
    RoundResponse,
    SourceRecord,
    StateResponse,
    TimelineEvent,
    TrajectoryResponse,
)
from .phase2 import phase2_router
from .replay import ReplayReader

#: Hard bound on the demos fanned out by the multi-query endpoint.
MULTI_SELECTION_LIMIT = 20


class MultiQuerySelection(Model):
    """One ``demo_id``/``generation_id`` pair resolved independently by the fan-out."""

    demo_id: str
    generation_id: str | None = None


class MultiQueryRequest(Model):
    """Bounded fan-out request; ``op`` chooses the analytics call made per selection."""

    selections: list[MultiQuerySelection]
    op: Literal["coverage", "events"]
    params: dict[str, Any] = Field(default_factory=dict)


class MultiQueryResult(Model):
    """Outcome of one selection: ``result`` on success, ``error`` when that demo failed."""

    demo_id: str
    generation_id: str | None = None
    result: dict[str, Any] | None = None
    error: ErrorResponse | None = None


class MultiQueryResponse(Model):
    schema_version: int = SCHEMA_VERSION
    results: list[MultiQueryResult]


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

    # -- Phase 1 analytics: thin wrappers over analytics/{identity,temporal,spatial} --
    def analytics_pool() -> GenerationPool:
        """Per-request pool over the runtime's live catalog and artifacts."""
        return GenerationPool(runtime.catalog, runtime.artifacts)

    def _optional_int(params: dict[str, Any], name: str) -> int | None:
        value = params.get(name)
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise AppError("INVALID_ARGUMENT", f"{name} must be a non-negative integer", "analytics")
        return value

    def _required_int(params: dict[str, Any], name: str) -> int:
        value = _optional_int(params, name)
        if value is None:
            raise AppError("INVALID_ARGUMENT", f"{name} is required for this op", "analytics")
        return value

    def _optional_limit(params: dict[str, Any]) -> int:
        value = params.get("limit")
        if value is None:
            return 1000
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= temporal.MAX_EVENT_LIMIT:
            raise AppError(
                "INVALID_ARGUMENT", f"limit must be an integer in 0..{temporal.MAX_EVENT_LIMIT}", "analytics"
            )
        return value

    def _datasets(value: Any) -> list[str]:
        """Normalize an event-dataset selection from a CSV string or a JSON list."""
        if value is None:
            chosen = list(temporal.EVENT_DATASETS)
        elif isinstance(value, str):
            chosen = [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            chosen = list(value)
        else:
            raise AppError(
                "INVALID_ARGUMENT", "datasets must be a comma-separated string or a list of names", "analytics"
            )
        if not chosen or any(name not in temporal.EVENT_DATASETS for name in chosen):
            raise AppError(
                "INVALID_ARGUMENT", f"datasets must be a non-empty subset of {list(temporal.EVENT_DATASETS)}", "analytics"
            )
        return chosen

    def _scope_label(round_id: int | None) -> str:
        return "generation" if round_id is None else f"round:{round_id}"

    def _coverage_operation(pool: GenerationPool, round_id: int | None) -> Callable[[Generation], dict[str, Any]]:
        scope = _scope_label(round_id)

        def run(gen: Generation) -> dict[str, Any]:
            return {"scope": scope, "coverage": identity.coverage(pool, gen, round_id).model_dump()}

        return run

    def _events_operation(
        pool: GenerationPool, start: int, end: int, datasets: list[str], limit: int
    ) -> Callable[[Generation], dict[str, Any]]:
        def run(gen: Generation) -> dict[str, Any]:
            events = temporal.events_in(pool, gen, datasets, start, end, limit)
            return {"start_tick": start, "end_tick": end, "event_count": len(events), "events": events}

        return run

    @app.get(prefix + "/demos/{demo_id}/analytics/state", response_model=StateResponse, responses=errors)
    def analytics_state(
        demo_id: str,
        tick: int = Query(ge=0),
        generation_id: str | None = None,
        player_id: str | None = None,
        max_gap: int = Query(0, ge=0),
    ):
        pool = analytics_pool()
        gen = pool.open(demo_id, generation_id)
        snapshot = temporal.state_at(pool, gen, tick, player_id, max_gap)
        return StateResponse(
            generation_id=gen.generation_id,
            tick_rate_hz=gen.tick_rate_hz,
            requested_tick=tick,
            actual_tick=snapshot["actual_tick"],
            gap_ticks=snapshot["gap"],
            exact=snapshot["exact"],
            states=[AnalyticState(**row) for row in snapshot["states"]],
        )

    @app.get(prefix + "/demos/{demo_id}/analytics/trajectory", response_model=TrajectoryResponse, responses=errors)
    def analytics_trajectory(
        demo_id: str,
        player_id: str,
        start: int = Query(ge=0),
        end: int = Query(ge=0),
        generation_id: str | None = None,
        stride: int = Query(1, ge=1, le=temporal.MAX_INTERVAL_STRIDE),
    ):
        pool = analytics_pool()
        gen = pool.open(demo_id, generation_id)
        interval = temporal.player_interval(pool, gen, player_id, start, end, stride)
        states = [AnalyticState(**row) for row in interval["states"]]
        return TrajectoryResponse(
            generation_id=gen.generation_id,
            tick_rate_hz=gen.tick_rate_hz,
            player_id=player_id,
            start_tick=start,
            end_tick=end,
            stride=stride,
            sample_count=len(states),
            missing_ranges=interval["missing_ranges"],
            states=states,
        )

    @app.get(prefix + "/demos/{demo_id}/analytics/events", response_model=EventsResponse, responses=errors)
    def analytics_events(
        demo_id: str,
        start: int = Query(ge=0),
        end: int = Query(ge=0),
        generation_id: str | None = None,
        datasets: str | None = None,
        limit: int = Query(1000, ge=0, le=temporal.MAX_EVENT_LIMIT),
    ):
        pool = analytics_pool()
        gen = pool.open(demo_id, generation_id)
        events = temporal.events_in(pool, gen, _datasets(datasets), start, end, limit)
        return EventsResponse(
            generation_id=gen.generation_id,
            start_tick=start,
            end_tick=end,
            event_count=len(events),
            events=[TimelineEvent(**event) for event in events],
        )

    @app.get(prefix + "/demos/{demo_id}/analytics/event-window", response_model=EventWindowResponse, responses=errors)
    def analytics_event_window(
        demo_id: str,
        dataset: str,
        row_ordinal: int = Query(ge=0),
        generation_id: str | None = None,
        before: int = Query(0, ge=0, le=temporal.MAX_WINDOW_TICKS),
        after: int = Query(0, ge=0, le=temporal.MAX_WINDOW_TICKS),
    ):
        pool = analytics_pool()
        gen = pool.open(demo_id, generation_id)
        window = temporal.event_window(pool, gen, dataset, row_ordinal, before, after)
        return EventWindowResponse(
            generation_id=gen.generation_id,
            tick_rate_hz=gen.tick_rate_hz,
            event=TimelineEvent(**window["event"]),
            states=[AnalyticState(**row) for row in window["states"]],
            nearby_events=[TimelineEvent(**event) for event in window["nearby_events"]],
        )

    @app.get(prefix + "/demos/{demo_id}/analytics/coverage", response_model=CoverageResponse, responses=errors)
    def analytics_coverage(
        demo_id: str,
        generation_id: str | None = None,
        round_id: int | None = Query(None, ge=1),
    ):
        pool = analytics_pool()
        gen = pool.open(demo_id, generation_id)
        return CoverageResponse(
            generation_id=gen.generation_id,
            scope=_scope_label(round_id),
            coverage=identity.coverage(pool, gen, round_id),
        )

    @app.get(prefix + "/demos/{demo_id}/analytics/distance", response_model=DistanceResponse, responses=errors)
    def analytics_distance(
        demo_id: str,
        player_a: str,
        player_b: str,
        tick: int = Query(ge=0),
        generation_id: str | None = None,
    ):
        pool = analytics_pool()
        gen = pool.open(demo_id, generation_id)
        point = spatial.pair_distance_over_time(pool, gen, player_a, player_b, [tick])[0]
        return DistanceResponse(
            generation_id=gen.generation_id,
            tick=tick,
            player_a=player_a,
            player_b=player_b,
            distance_2d=point["d2d"],
            distance_3d=point["d3d"],
            missing=point["missing"],
        )

    @app.post(prefix + "/demos/multi/query", response_model=MultiQueryResponse, responses=errors)
    def multi_query(body: MultiQueryRequest):
        if len(body.selections) > MULTI_SELECTION_LIMIT:
            raise AppError(
                "INVALID_ARGUMENT", f"at most {MULTI_SELECTION_LIMIT} selections per query", "analytics"
            )
        pool = analytics_pool()
        params = body.params
        if body.op == "coverage":
            operation = _coverage_operation(pool, _optional_int(params, "round_id"))
        else:
            operation = _events_operation(
                pool,
                _required_int(params, "start"),
                _required_int(params, "end"),
                _datasets(params.get("datasets")),
                _optional_limit(params),
            )
        entries = pool.query_many(
            [(selection.demo_id, selection.generation_id) for selection in body.selections], operation
        )
        return MultiQueryResponse(results=[MultiQueryResult(**entry) for entry in entries])

    # -- Phase 2 reconstruction: subject, encounters, context and geometry ------
    app.include_router(phase2_router(runtime, prefix=prefix, errors=errors))

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

"""Phase 2 read surface: subject, participation, encounters, context and geometry.

Everything here is a thin, bounded, generation-pinned wrapper around the
provider services (``SubjectService``, ``EncounterService``, ``ContextService``,
``GeometryService``). No response shape is redefined: the routes answer with the
provider-owned domain models, so a provider rename breaks this module at import
time instead of silently diverging.

Three invariants the UI depends on:

* **No substitution.** A read either uses the explicitly requested subject or the
  configured primary when that primary is actually present in the pinned
  generation. It never falls back to another participant; an absent/unresolved
  primary raises ``SUBJECT_UNAVAILABLE``.
* **Bounded.** Every list route carries a hard ``Query`` ceiling and geometry
  coordinates are finite and inside the CS2 world scale. Nothing loads a whole
  match.
* **No eager extraction.** The services are instantiated on the first request
  (``create_app(None).openapi()`` must stay import-only) and geometry resources
  are only processed by the explicit ``POST /geometry/{map_name}/prepare``.
"""

from __future__ import annotations

import threading
from typing import Any

from fastapi import APIRouter, Path, Query
from pydantic import Field

from ..analytics.access import Generation, GenerationPool
from ..analytics.context import ContextService
from ..analytics.encounters import EncounterService
from ..analytics.subjects import MAX_LIST_LIMIT as MAX_PARTICIPATION_LIMIT
from ..analytics.subjects import SubjectService
from ..assets.geometry import GeometryService
from ..domain.contracts import AppError, ErrorResponse, Model
from ..domain.context import ContextSnapshot, EncounterContext
from ..domain.encounters import (
    DEFAULT_GAP_SECONDS,
    DEFAULT_POST_SECONDS,
    DEFAULT_PRE_SECONDS,
    MAX_GAP_SECONDS,
    MAX_LIMIT as MAX_ENCOUNTER_LIMIT,
    MAX_POST_SECONDS,
    MAX_PRE_SECONDS,
    EncounterDetail,
    EncounterList,
)
from ..domain.geometry import GeometryCapabilities, NavigationResult, PointLocation, SegmentResult
from ..domain.subjects import Participation, SubjectConfig

#: CS2 world coordinates stay far inside this bound (Hammer units).
MAX_COORDINATE = 32768.0
#: Map names and client versions are internal identifiers, not free text.
MAX_MAP_NAME = 64
MAX_CLIENT_VERSION = 64


class SubjectRequest(Model):
    """Body of ``PUT /api/v1/analysis-subject``.

    The value is passed to ``SubjectService.set`` verbatim; the service owns
    SteamID64 validation (17-digit positive account id) and rejects anything
    else with ``INVALID_ARGUMENT``.
    """

    steam_id: str = Field(min_length=1, max_length=32)


class _Services:
    """Single lazily-built set of provider services for one application.

    Built on the first request rather than at ``create_app`` time so the OpenAPI
    export never needs a runtime, and so no geometry preprocessing can be
    triggered by merely serving a page.
    """

    def __init__(self, runtime: Any) -> None:
        self._runtime = runtime
        # Reentrant: several services are built from within another's property.
        self._lock = threading.RLock()
        self._pool: GenerationPool | None = None
        self._subjects: SubjectService | None = None
        self._encounters: EncounterService | None = None
        self._geometry: GeometryService | None = None
        self._context: ContextService | None = None

    def _require_runtime(self) -> Any:
        if self._runtime is None:
            raise AppError("NOT_READY", "The application runtime is unavailable", "startup")
        return self._runtime

    @property
    def pool(self) -> GenerationPool:
        with self._lock:
            if self._pool is None:
                runtime = self._require_runtime()
                self._pool = GenerationPool(runtime.catalog, runtime.artifacts)
            return self._pool

    @property
    def subjects(self) -> SubjectService:
        with self._lock:
            if self._subjects is None:
                self._subjects = SubjectService(self._require_runtime().catalog, self.pool)
            return self._subjects

    @property
    def geometry(self) -> GeometryService:
        with self._lock:
            if self._geometry is None:
                runtime = self._require_runtime()
                settings = runtime.settings
                # The coordinator discovers the installation separately from the
                # settings file; the radar service already holds that discovered
                # path, so geometry works without an explicit install flag.
                install = runtime.radar.install_path or settings.install_path
                self._geometry = GeometryService(settings.data_root, install, settings.source2viewer)
            return self._geometry

    @property
    def encounters(self) -> EncounterService:
        with self._lock:
            if self._encounters is None:
                self._encounters = EncounterService(self.pool)
            return self._encounters

    @property
    def context(self) -> ContextService:
        with self._lock:
            if self._context is None:
                self._context = ContextService(self.pool, self.geometry)
            return self._context


def phase2_router(runtime: Any, *, prefix: str = "/api/v1", errors: dict[int, dict[str, Any]] | None = None) -> APIRouter:
    """Router for the Phase 2 reconstruction endpoints.

    ``runtime`` may be ``None``: the contract export calls ``create_app(None)``
    and only reads the resulting OpenAPI document.
    """
    services = _Services(runtime)
    router = APIRouter()
    failures = errors if errors is not None else {400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}

    def pinned_generation(demo_id: str, generation_id: str | None) -> Generation:
        """Open the requested generation; only an explicit pin is ever honoured."""
        return services.pool.open(demo_id, generation_id)

    def subject_key(demo_id: str, generation_id: str, requested: str | None) -> str:
        """Resolve the subject for encounter/context reads.

        An explicit selection always wins and is used verbatim. Otherwise the
        configured primary is used only when the pinned generation records it as
        present. An absent, unresolved or not-ready primary is reported as such;
        another participant is never chosen in its place.
        """
        if requested:
            return requested
        participation = services.subjects.participation(demo_id, generation_id)
        if participation.status == "present" and participation.player_id is not None:
            return participation.player_id
        raise AppError(
            "SUBJECT_UNAVAILABLE",
            f"the configured subject is {participation.status} in generation {generation_id}; select a participant explicitly",
            "subject",
        )

    # -- subject configuration -------------------------------------------------
    @router.get(prefix + "/analysis-subject", response_model=SubjectConfig)
    def analysis_subject() -> SubjectConfig:
        """The persisted primary subject; unchanged by any per-demo selection."""
        return services.subjects.get()

    @router.put(prefix + "/analysis-subject", response_model=SubjectConfig, responses=failures)
    def set_analysis_subject(body: SubjectRequest) -> SubjectConfig:
        """Persist the primary subject. This never re-ingests or reprocesses a demo."""
        return services.subjects.set(body.steam_id)

    @router.get(prefix + "/subject-participation", response_model=list[Participation], responses=failures)
    def subject_participation(
        limit: int = Query(100, ge=1, le=MAX_PARTICIPATION_LIMIT),
        offset: int = Query(0, ge=0),
    ) -> list[Participation]:
        """The primary subject's participation in catalog demos, bounded and paged."""
        return services.subjects.list_participation(limit, offset)

    @router.get(prefix + "/demos/{demo_id}/participation", response_model=Participation, responses=failures)
    def demo_participation(
        demo_id: str,
        generation_id: str | None = None,
        player_id: str | None = None,
    ) -> Participation:
        """Participation of the primary subject, or of an explicit ``player_id`` override.

        An override that is missing reports ``absent`` for that override; it is
        never replaced by the configured subject.
        """
        return services.subjects.participation(demo_id, generation_id, player_id)

    # -- encounters ------------------------------------------------------------
    @router.get(prefix + "/demos/{demo_id}/encounters", response_model=EncounterList, responses=failures)
    def demo_encounters(
        demo_id: str,
        generation_id: str | None = None,
        subject_id: str | None = Query(None, max_length=128, description="Recording identity key; defaults to the configured subject when present"),
        round_id: int | None = Query(None, ge=1),
        limit: int = Query(100, ge=1, le=MAX_ENCOUNTER_LIMIT),
        offset: int = Query(0, ge=0),
        gap_seconds: float = Query(DEFAULT_GAP_SECONDS, ge=0.0, le=MAX_GAP_SECONDS),
        pre_seconds: float = Query(DEFAULT_PRE_SECONDS, ge=0.0, le=MAX_PRE_SECONDS),
        post_seconds: float = Query(DEFAULT_POST_SECONDS, ge=0.0, le=MAX_POST_SECONDS),
    ) -> EncounterList:
        """Encounters of the pinned generation involving the subject, one bounded page."""
        gen = pinned_generation(demo_id, generation_id)
        subject = subject_key(demo_id, gen.generation_id, subject_id)
        return services.encounters.list(
            gen,
            subject,
            round_id=round_id,
            limit=limit,
            offset=offset,
            gap_seconds=gap_seconds,
            pre_seconds=pre_seconds,
            post_seconds=post_seconds,
        )

    @router.get(prefix + "/demos/{demo_id}/encounters/{encounter_id}", response_model=EncounterDetail, responses=failures)
    def demo_encounter(
        demo_id: str,
        encounter_id: str,
        generation_id: str | None = None,
        subject_id: str | None = Query(None, max_length=128),
        gap_seconds: float = Query(DEFAULT_GAP_SECONDS, ge=0.0, le=MAX_GAP_SECONDS),
        pre_seconds: float = Query(DEFAULT_PRE_SECONDS, ge=0.0, le=MAX_PRE_SECONDS),
        post_seconds: float = Query(DEFAULT_POST_SECONDS, ge=0.0, le=MAX_POST_SECONDS),
    ) -> EncounterDetail:
        """One encounter with its anchors, events, evidence refs and subject trajectory.

        The grouping options must match the ones the encounter was listed with;
        ``encounter_id`` is resolved inside the same grouping.
        """
        gen = pinned_generation(demo_id, generation_id)
        subject = subject_key(demo_id, gen.generation_id, subject_id)
        return services.encounters.detail(
            gen,
            subject,
            encounter_id,
            gap_seconds=gap_seconds,
            pre_seconds=pre_seconds,
            post_seconds=post_seconds,
        )

    # -- context ---------------------------------------------------------------
    @router.get(prefix + "/demos/{demo_id}/context", response_model=ContextSnapshot, responses=failures)
    def demo_context(
        demo_id: str,
        tick: int = Query(ge=0),
        generation_id: str | None = None,
        subject_id: str | None = Query(None, max_length=128),
        cross_pairs: bool = Query(False, description="Also resolve living teammate-to-opponent potential sightlines at this tick"),
        navigation: bool = Query(False, description="Also resolve navigation-graph estimates for the subject's relations"),
    ) -> ContextSnapshot:
        """Context of the subject at exactly ``tick`` of the pinned generation.

        The requested tick is used verbatim; a tick with no recorded state is
        reported through the snapshot's own coverage fields, never snapped to a
        neighbouring tick. ``cross_pairs`` and ``navigation`` are opt-in because
        both add static-graph work to an otherwise recorded-state read.
        """
        gen = pinned_generation(demo_id, generation_id)
        subject = subject_key(demo_id, gen.generation_id, subject_id)
        return services.context.at(gen, subject, tick, cross_pairs=cross_pairs, navigation=navigation)

    @router.get(prefix + "/demos/{demo_id}/encounters/{encounter_id}/context", response_model=EncounterContext, responses=failures)
    def demo_encounter_context(
        demo_id: str,
        encounter_id: str,
        generation_id: str | None = None,
        subject_id: str | None = Query(None, max_length=128),
        gap_seconds: float = Query(DEFAULT_GAP_SECONDS, ge=0.0, le=MAX_GAP_SECONDS),
        pre_seconds: float = Query(DEFAULT_PRE_SECONDS, ge=0.0, le=MAX_PRE_SECONDS),
        post_seconds: float = Query(DEFAULT_POST_SECONDS, ge=0.0, le=MAX_POST_SECONDS),
        navigation: bool = Query(False, description="Also resolve navigation-graph estimates for the subject's relations"),
    ) -> EncounterContext:
        """Context snaps at the encounter's anchors plus the pre-contact offsets."""
        gen = pinned_generation(demo_id, generation_id)
        subject = subject_key(demo_id, gen.generation_id, subject_id)
        detail = services.encounters.detail(
            gen,
            subject,
            encounter_id,
            gap_seconds=gap_seconds,
            pre_seconds=pre_seconds,
            post_seconds=post_seconds,
        )
        return services.context.encounter(gen, detail, navigation=navigation)

    # -- geometry --------------------------------------------------------------
    @router.get(prefix + "/geometry/capabilities", response_model=GeometryCapabilities)
    def geometry_capabilities(
        map_name: str = Query(min_length=1, max_length=MAX_MAP_NAME),
        demo_client_version: str | None = Query(None, max_length=MAX_CLIENT_VERSION),
    ) -> GeometryCapabilities:
        """Which installed geometry components exist for a map, and for which client version."""
        return services.geometry.capabilities(map_name, demo_client_version)

    @router.get(prefix + "/geometry/segment", response_model=SegmentResult)
    def geometry_segment(
        map_name: str = Query(min_length=1, max_length=MAX_MAP_NAME),
        start_x: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        start_y: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        start_z: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        end_x: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        end_y: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        end_z: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        demo_client_version: str | None = Query(None, max_length=MAX_CLIENT_VERSION),
    ) -> SegmentResult:
        """Static sightline between two world points of the installed map assets.

        ``unknown``/``unsupported``/``mismatch`` are capability answers, not
        errors: they mean the historical sightline is not proven.
        """
        return services.geometry.segment(
            map_name, (start_x, start_y, start_z), (end_x, end_y, end_z), demo_client_version
        )

    @router.get(prefix + "/geometry/navigation", response_model=NavigationResult)
    def geometry_navigation(
        map_name: str = Query(min_length=1, max_length=MAX_MAP_NAME),
        start_x: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        start_y: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        start_z: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        end_x: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        end_y: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        end_z: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        demo_client_version: str | None = Query(None, max_length=MAX_CLIENT_VERSION),
    ) -> NavigationResult:
        """Navigation path between two world points, with its own availability status."""
        return services.geometry.navigation(
            map_name, (start_x, start_y, start_z), (end_x, end_y, end_z), demo_client_version
        )

    @router.get(prefix + "/geometry/location", response_model=PointLocation)
    def geometry_location(
        map_name: str = Query(min_length=1, max_length=MAX_MAP_NAME),
        x: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        y: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        z: float = Query(ge=-MAX_COORDINATE, le=MAX_COORDINATE),
        demo_client_version: str | None = Query(None, max_length=MAX_CLIENT_VERSION),
    ) -> PointLocation:
        """Static facts about one world point: bounds, solidity, floor, nav area.

        The point is used verbatim. It is a *ground* question (floor height, nav
        area), so callers should pass a recorded player origin rather than an eye
        position; coordinates outside the map report ``in_bounds=false`` instead
        of being corrected.
        """
        return services.geometry.locate(map_name, (x, y, z), demo_client_version)

    @router.post(prefix + "/geometry/{map_name}/prepare", response_model=GeometryCapabilities, responses=failures)
    def geometry_prepare(map_name: str = Path(min_length=1, max_length=MAX_MAP_NAME)) -> GeometryCapabilities:
        """Explicitly preprocess one map's physics/navigation components.

        Deliberately a separate write: scrubbing or listing never triggers
        resource extraction, and an unprepared map answers with typed component
        statuses instead of failing.
        """
        return services.geometry.prepare(map_name)

    return router

"""Static map geometry models for player-centric reconstruction (slice C).

These models describe the *installed* build's collision and navigation assets.
``static_clear`` is only produced when collision data exists and no obstacle
intersects the segment; ``unknown`` and ``unsupported`` are never clear, and
``match_status == "mismatch"`` means the geometry cannot prove a historical
sightline.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .contracts import Model

Vec3 = tuple[float, float, float]
MatchStatus = Literal["exact", "mismatch", "unknown"]
SegmentStatus = Literal["static_clear", "static_blocked", "unknown", "unsupported"]
NavigationStatus = Literal["available", "unavailable", "unsupported"]
ComponentStatus = Literal["available", "partial", "unavailable", "unsupported"]
SourceKind = Literal["vmap", "nav", "physics", "glb"]


class GeometrySource(Model):
    """One extracted VPK entry backing a map's geometry cache."""

    kind: SourceKind
    entry: str
    byte_size: int
    sha256: str


class GeometryAsset(Model):
    """Asset provenance for one prepared map at one installed client version."""

    asset_id: str
    map_name: str
    vpk: str
    client_version: str
    parser_version: str
    tool: str
    sources: list[GeometrySource] = Field(default_factory=list)


class GeometryComponent(Model):
    """Capability of one geometry component (collision physics or navigation)."""

    status: ComponentStatus
    source: str
    limitations: list[str] = Field(default_factory=list)


class GeometryCapabilities(Model):
    """What static geometry is available for one map, without querying it."""

    map_name: str
    prepared: bool
    physics: GeometryComponent
    navigation: GeometryComponent
    bounds_min: Vec3 | None = None
    bounds_max: Vec3 | None = None
    triangle_count: int = 0
    nav_area_count: int = 0
    asset: GeometryAsset | None = None
    asset_id: str | None = None
    match_status: MatchStatus = "unknown"
    install_client_version: str | None = None
    demo_client_version: str | None = None
    preprocessing_ms: float | None = None
    limitations: list[str] = Field(default_factory=list)


class SegmentResult(Model):
    """Static collision result for one world-space segment."""

    status: SegmentStatus
    start: Vec3
    end: Vec3
    length: float
    hit_distance: float | None = None
    hit_point: Vec3 | None = None
    hit_normal: Vec3 | None = None
    surface: str | None = None
    source: str | None = None
    asset_id: str | None = None
    match_status: MatchStatus = "unknown"
    limitations: list[str] = Field(default_factory=list)


class PointLocation(Model):
    """Static location facts for one world-space point.

    ``in_bounds``/``inside_solid`` are ``None`` when no collision data is
    available: absence of geometry is unknown, never "outside" or "clear".
    """

    point: Vec3
    in_bounds: bool | None = None
    inside_solid: bool | None = None
    floor_z: float | None = None
    floor_distance: float | None = None
    clearance_up: float | None = None
    nav_area_id: int | None = None
    asset_id: str | None = None
    match_status: MatchStatus = "unknown"
    limitations: list[str] = Field(default_factory=list)


class NavArea(Model):
    """One navigation area polygon from the installed map's nav data."""

    area_id: int
    corners: list[Vec3]
    center: Vec3
    flags: int = 0


class NavigationResult(Model):
    """Static navigation answer for one segment.

    ``available`` carries a path; ``unavailable`` means the map has nav data but
    the endpoints do not connect; ``unsupported`` means no usable nav source.
    """

    status: NavigationStatus
    start: Vec3
    end: Vec3
    direct_distance: float
    path_distance: float | None = None
    connected: bool | None = None
    path: list[Vec3] = Field(default_factory=list)
    area_ids: list[int] = Field(default_factory=list)
    asset_id: str | None = None
    match_status: MatchStatus = "unknown"
    limitations: list[str] = Field(default_factory=list)

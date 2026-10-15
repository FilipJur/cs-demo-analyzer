from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1
PROFILE_NAME = "foundation-v1"
PARSER_VERSION = "3.0.0"
NORMALIZER_VERSION = "1"
PROFILE_KEY = "foundation-v1:awpy-3.0.0:schema-1:normalizer-1"

#: The extended profile keeps every ``foundation-v1`` table, column and semantic
#: exactly as published and adds utility/economy/lifecycle tables plus further
#: *recorded* upstream fields. It never reinterprets a foundation column.
RECONSTRUCTION_PROFILE_NAME = "reconstruction-v1"
RECONSTRUCTION_SCHEMA_VERSION = 2
RECONSTRUCTION_NORMALIZER_VERSION = "1"
RECONSTRUCTION_PROFILE_KEY = "reconstruction-v1:awpy-3.0.0:schema-2:normalizer-1"

#: What new extraction work asks for. ``foundation-v1`` stays a named, explicitly
#: requestable profile so previously published generations keep their exact meaning.
DEFAULT_PROFILE_NAME = RECONSTRUCTION_PROFILE_NAME
DEFAULT_PROFILE_KEY = RECONSTRUCTION_PROFILE_KEY

ProfileName = Literal["foundation-v1", "reconstruction-v1"]

PROFILE_KEYS: dict[str, str] = {
    PROFILE_NAME: PROFILE_KEY,
    RECONSTRUCTION_PROFILE_NAME: RECONSTRUCTION_PROFILE_KEY,
}
PROFILE_SCHEMA_VERSIONS: dict[str, int] = {
    PROFILE_NAME: SCHEMA_VERSION,
    RECONSTRUCTION_PROFILE_NAME: RECONSTRUCTION_SCHEMA_VERSION,
}
PROFILE_NORMALIZER_VERSIONS: dict[str, str] = {
    PROFILE_NAME: NORMALIZER_VERSION,
    RECONSTRUCTION_PROFILE_NAME: RECONSTRUCTION_NORMALIZER_VERSION,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_serialization_defaults_required=True)


class AppError(Exception):
    def __init__(self, code: str, message: str, stage: str, retryable: bool = False):
        super().__init__(message)
        self.code, self.message, self.stage, self.retryable = code, message, stage, retryable

    def payload(self) -> dict:
        return dict(code=self.code, message=self.message, stage=self.stage, retryable=self.retryable)


def profile_key_for(profile: str) -> str:
    """The canonical ``<profile>:<parser>:schema-<n>:normalizer-<n>`` key."""
    try:
        return PROFILE_KEYS[profile]
    except KeyError:
        raise AppError(
            "INVALID_PROFILE",
            f"unknown profile {profile!r}; known profiles {sorted(PROFILE_KEYS)}",
            "parse",
        ) from None


def profile_for_key(profile_key: str) -> str:
    """The named profile a key belongs to; raises ``AppError`` for an unknown key."""
    for profile, key in PROFILE_KEYS.items():
        if key == profile_key:
            return profile
    raise AppError(
        "INVALID_PROFILE",
        f"unknown profile key {profile_key!r}; known keys {sorted(PROFILE_KEYS.values())}",
        "parse",
    )


def schema_version_for(profile: str) -> int:
    return PROFILE_SCHEMA_VERSIONS[profile]


def normalizer_version_for(profile: str) -> str:
    return PROFILE_NORMALIZER_VERSIONS[profile]


class ErrorResponse(Model):
    code: str
    message: str
    stage: str
    retryable: bool = False
    job_id: str | None = None


class Fingerprint(Model):
    device: int
    inode: int
    size: int
    mtime_ns: int
    ctime_ns: int

    @classmethod
    def from_path(cls, path: Path) -> Fingerprint:
        s = path.stat(follow_symlinks=False)
        return cls(device=s.st_dev, inode=s.st_ino, size=s.st_size, mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns)


class Observation(Model):
    path: str
    fingerprint: Fingerprint
    root_id: int | None = None


class RootRequest(Model):
    path: str
    recursive: bool = False


class RootRecord(RootRequest):
    id: int
    available: bool = True
    error: str | None = None


class Snapshot(Model):
    demo_id: str
    raw_path: str
    size: int
    source_path: str
    fingerprint: Fingerprint


class TableDescriptor(Model):
    path: str
    row_count: int = Field(ge=0)
    sha256: str
    schema_version: int = SCHEMA_VERSION


class Capability(Model):
    status: Literal["available", "absent", "unsupported", "failed"]
    source: str
    note: str = ""


class ExtractionRequest(Model):
    protocol_version: Literal[1] = 1
    job_id: str
    generation_id: str
    demo_id: str
    input_path: str
    output_dir: str
    profile: ProfileName = PROFILE_NAME
    #: Canonical key of the requested profile. The worker rejects a mismatch
    #: instead of writing a generation under a key it did not implement.
    profile_key: str | None = None
    parent_pid: int | None = None


class Manifest(Model):
    schema_version: Literal[1] = SCHEMA_VERSION
    demo_id: str
    job_id: str
    generation_id: str
    profile: ProfileName = PROFILE_NAME
    profile_key: str = PROFILE_KEY
    parser_version: str = PARSER_VERSION
    normalizer_version: str = NORMALIZER_VERSION
    created_at: str = Field(default_factory=utc_now)
    source_size: int
    map_name: str
    tick_rate_hz: float = Field(gt=0)
    tick_origin: int = 0
    clock: Literal["awpy_demo_tick"] = "awpy_demo_tick"
    tick_rate_source: str = "awpy.Demo.tick_rate"
    recording_kind: Literal["gotv", "pov", "unknown"] = "unknown"
    quality: Literal["complete", "partial"] = "complete"
    demo_client_version: str | None = None
    demo_version_source: str | None = None
    tables: dict[str, TableDescriptor]
    capabilities: dict[str, Capability] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class WorkerResult(Model):
    protocol_version: Literal[1] = 1
    manifest_path: str | None = None
    error: ErrorResponse | None = None


class JobRecord(Model):
    id: str
    demo_id: str
    profile_key: str = PROFILE_KEY
    state: Literal["queued", "running", "succeeded", "failed", "interrupted"]
    generation_id: str
    attempt: int = 1
    created_at: str
    updated_at: str
    error: ErrorResponse | None = None
    worker_pid: int | None = None


class DemoRecord(Model):
    demo_id: str
    raw_path: str
    size: int
    created_at: str
    generation_id: str | None = None
    manifest_path: str | None = None
    map_name: str | None = None
    quality: str | None = None
    warnings: list[str] = Field(default_factory=list)


class SourceRecord(Model):
    path: str
    fingerprint: Fingerprint | None = None
    demo_id: str | None = None
    status: str
    error: ErrorResponse | None = None
    updated_at: str


class ImportRequest(Model):
    path: str


class Accepted(Model):
    status: str
    job_id: str | None = None
    demo_id: str | None = None


class RadarDescriptor(Model):
    asset_id: str | None = None
    map_name: str
    installed_client_version: str | None = None
    demo_client_version: str | None = None
    match_status: Literal["exact", "mismatch", "unknown"] = "unknown"
    width: int = 1024
    height: int = 1024
    pos_x: float | None = None
    pos_y: float | None = None
    scale: float | None = None
    rotate: float | None = None
    zoom: float | None = None
    levels: list[dict] = Field(default_factory=list)
    warning: str | None = None


class RoundRecord(Model):
    round_id: int
    source_round_num: int | None
    start_tick: int | None
    freeze_end_tick: int | None
    end_tick: int | None
    official_end_tick: int | None
    winner_side: str | None
    reason_code: int | None


class RoundResponse(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    rounds: list[RoundRecord]


class ReplayPlayer(Model):
    player_id: str
    steam_id: str | None
    name: str | None
    side: str


class ReplaySample(Model):
    tick: int
    player_id: str
    x: float | None
    y: float | None
    z: float | None
    yaw: float | None
    health: int | None
    side: str
    active_weapon: str | None


class ReplayEvent(Model):
    tick: int
    row_ordinal: int
    attacker_id: str | None
    victim_id: str | None
    weapon: str | None
    headshot: bool | None


class ReplayChunk(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    clock: str = "awpy_demo_tick"
    tick_rate_hz: float
    start_tick: int
    end_tick: int
    stride_ticks: int
    players: list[ReplayPlayer]
    samples: list[ReplaySample]
    events: list[ReplayEvent]
    radar: RadarDescriptor
    warnings: list[str]


class DemoDetail(Model):
    demo: DemoRecord
    sources: list[SourceRecord]
    manifest: Manifest | None


class HealthResponse(Model):
    status: str
    schema_version: int = SCHEMA_VERSION
    data_root: str
    worker_running: bool
    free_bytes: int

class AnalyticState(Model):
    row_ordinal: int
    tick: int
    player_id: str | None
    x: float | None
    y: float | None
    z: float | None
    yaw: float | None
    pitch: float | None
    velocity_x: float | None
    velocity_y: float | None
    velocity_z: float | None
    health: int | None
    armor: int | None
    money: int | None
    side: str
    active_weapon: str | None
    has_bomb: bool | None
    is_crouched: bool | None
    is_scoped: bool | None
    is_reloading: bool | None


class StateResponse(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    tick_rate_hz: float
    requested_tick: int
    actual_tick: int | None
    gap_ticks: int | None = None
    exact: bool
    states: list[AnalyticState]


class TrajectoryResponse(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    tick_rate_hz: float
    player_id: str
    start_tick: int
    end_tick: int
    stride: int
    sample_count: int
    missing_ranges: list[list[int]]
    states: list[AnalyticState]


class TimelineEvent(Model):
    dataset: str
    row_ordinal: int
    tick: int
    actor1: str | None = None
    actor2: str | None = None
    detail: str | None = None


class EventsResponse(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    start_tick: int
    end_tick: int
    event_count: int
    events: list[TimelineEvent]


class EventWindowResponse(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    tick_rate_hz: float
    event: TimelineEvent
    states: list[AnalyticState]
    nearby_events: list[TimelineEvent]


class IdentityCoverage(Model):
    total_observations: int
    identified: int
    null_observations: int
    alive_total: int
    alive_identified: int
    alive_null: int
    live_coverage: float | None = None
    notes: list[str] = Field(default_factory=list)


class CoverageResponse(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    scope: str
    coverage: IdentityCoverage


class DistanceResponse(Model):
    generation_id: str
    schema_version: int = SCHEMA_VERSION
    tick: int
    player_a: str
    player_b: str
    distance_2d: float | None = None
    distance_3d: float | None = None
    missing: bool = False


class EvidenceRef(Model):
    demo_id: str
    generation_id: str
    profile_key: str
    dataset: str
    row_ordinal: int
    tick: int
    round_id: int | None = None
    player_ids: list[str] = Field(default_factory=list)

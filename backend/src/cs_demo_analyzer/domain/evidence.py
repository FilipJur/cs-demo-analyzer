"""Small shared evidence vocabulary; capability is not player perception."""
from typing import Literal

from pydantic import Field

from .contracts import Model

EvidenceKind = Literal["recorded", "computed", "geometry_dependent", "estimated", "unsupported"]
CapabilityStatus = Literal["available", "partial", "unavailable", "unsupported"]


class EvidenceCapability(Model):
    status: CapabilityStatus
    source: str
    limitations: list[str] = Field(default_factory=list)


class ReconstructionProvenance(Model):
    demo_id: str
    generation_id: str
    profile_key: str
    method: str
    method_version: str
    map_name: str
    demo_client_version: str | None = None
    map_asset_id: str | None = None
    map_match_status: Literal["exact", "mismatch", "unknown"] = "unknown"
    information_scope: Literal["omniscient_replay"] = "omniscient_replay"
    limitations: list[str] = Field(default_factory=list)

"""HTTP surface of the Phase 2 reconstruction endpoints over a genuine generation.

Like ``test_api``/``test_analytics_api``, every response is served from the real
catalog, canonical Parquet tables and hashed manifests produced by the shared
Phase 0 builders; the client is bound to ``http://127.0.0.1:8765`` with
``manage_lifetime=False`` so no coordinator is started.

The cases here are the consequential ones: subject persistence and exact
SteamID64 handling, the four participation states with an explicit override,
generation pinning, bounded list/pages, exact-tick context semantics, encounter
detail/context identity, and the geometry contract that an unproven sightline is
never reported as clear.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cs_demo_analyzer.api.routes import create_app
from cs_demo_analyzer.domain.encounters import ENCOUNTER_ID_PREFIX
from cs_demo_analyzer.domain.subjects import DEFAULT_STEAM_ID
from helpers import (
    API,
    BASE_URL,
    DEMO_ID,
    PENDING_DEMO_ID,
    PLAYER_A,
    PLAYER_B,
    PLAYER_IDS,
    STEAM_A,
    UNRESOLVED_PLAYER,
    Api,
    commit_generation,
    create_application,
    inferno_tables,
    mirage_tables,
    register_demo,
)

#: A valid individual SteamID64 that the fixture roster does not contain.
ABSENT_STEAM_ID = "76561198000000099"

UNKNOWN_GENERATION_ID = "0" * 64
UNKNOWN_DEMO_ID = "f" * 64


@pytest.fixture
def api(tmp_path):
    app = create_application(tmp_path)
    register_demo(app, DEMO_ID)
    first = commit_generation(app, DEMO_ID, map_name="inferno", tables=inferno_tables())
    second = commit_generation(app, DEMO_ID, map_name="mirage", tables=mirage_tables())
    register_demo(app, PENDING_DEMO_ID)
    try:
        with TestClient(create_app(app, manage_lifetime=False), base_url=BASE_URL) as client:
            yield Api(app=app, client=client, first=first, second=second)
    finally:
        app.close()


def encounter_query(api: Api, generation_id: str, **params) -> dict[str, str]:
    params.setdefault("subject_id", PLAYER_A)
    return {"generation_id": generation_id, **params}


# -- subject configuration --------------------------------------------------
def test_subject_default_is_exact_string_and_round_trips(api: Api) -> None:
    response = api.client.get(f"{API}/analysis-subject")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["steam_id"] == DEFAULT_STEAM_ID
    assert body["player_id"] == f"steam:{DEFAULT_STEAM_ID}"
    # The 17-digit id must arrive as text; a JSON number would lose precision.
    assert isinstance(body["steam_id"], str)

    invalid = api.client.put(f"{API}/analysis-subject", json={"steam_id": "12345"})
    assert invalid.status_code == 400, invalid.text
    assert invalid.json()["code"] == "INVALID_ARGUMENT"
    assert api.client.get(f"{API}/analysis-subject").json()["steam_id"] == DEFAULT_STEAM_ID

    updated = api.client.put(f"{API}/analysis-subject", json={"steam_id": STEAM_A})
    assert updated.status_code == 200, updated.text
    assert updated.json()["steam_id"] == STEAM_A
    assert updated.json()["player_id"] == PLAYER_A
    assert api.client.get(f"{API}/analysis-subject").json()["steam_id"] == STEAM_A


def test_participation_states_and_explicit_override(api: Api) -> None:
    pending = api.client.get(f"{API}/demos/{PENDING_DEMO_ID}/participation")
    assert pending.status_code == 200, pending.text
    assert pending.json()["status"] == "not_ready"
    assert pending.json()["measurements"] is None

    default = api.client.get(f"{API}/demos/{DEMO_ID}/participation")
    assert default.status_code == 200, default.text
    body = default.json()
    # The configured subject is in no fixture roster. The read reports that
    # absence for *that* identity: the canonical configured player id is kept
    # verbatim and no other participant is substituted for it.
    assert body["status"] in {"absent", "unresolved"}
    assert body["player_id"] == f"steam:{DEFAULT_STEAM_ID}"
    assert body["player_id_source"] == "config"
    assert body["in_roster"] is False
    # Without a pin, the read resolves the catalog's current head generation.
    assert body["generation_id"] == api.second.generation_id

    override = api.client.get(f"{API}/demos/{DEMO_ID}/participation", params={"player_id": PLAYER_A})
    assert override.status_code == 200, override.text
    assert override.json()["status"] == "present"
    assert override.json()["player_id"] == PLAYER_A
    assert override.json()["player_id_source"] == "override"
    assert override.json()["measurements"] is not None

    # An override that is missing stays missing for that override.
    unresolved = api.client.get(f"{API}/demos/{DEMO_ID}/participation", params={"player_id": UNRESOLVED_PLAYER})
    assert unresolved.status_code == 200, unresolved.text
    assert unresolved.json()["status"] != "present"

    missing = api.client.get(f"{API}/demos/{UNKNOWN_DEMO_ID}/participation")
    assert missing.status_code == 404, missing.text
    assert missing.json()["code"] == "NOT_FOUND"

    oversized = api.client.get(f"{API}/subject-participation", params={"limit": 501})
    assert oversized.status_code == 422, oversized.text


# -- encounters -------------------------------------------------------------
def test_encounters_are_pinned_bounded_and_typed(api: Api) -> None:
    pinned = api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id))
    assert pinned.status_code == 200, pinned.text
    body = pinned.json()
    assert body["generation_id"] == api.first.generation_id
    assert body["subject_id"] == PLAYER_A
    assert body["grouping"]["gap_seconds"] == 3.0
    assert body["grouping"]["tick_rate_hz"] > 0
    assert body["total"] >= 1
    assert body["encounters"], body
    summary = body["encounters"][0]
    assert summary["subject_id"] == PLAYER_A
    assert PLAYER_A not in summary["participant_ids"]

    other = api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.second.generation_id))
    assert other.status_code == 200, other.text
    assert other.json()["generation_id"] == api.second.generation_id

    # A page ceiling the provider enforces, surfaced as a request error.
    assert api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id, limit=501)).status_code == 422
    assert api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id, limit=0)).status_code == 422
    # A grouping window beyond the provider bound is a request error, not a silent clamp.
    assert api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id, gap_seconds=120)).status_code == 422

    # A round without complete timing cannot be grouped.
    assert api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id, round_id=3)).status_code == 404
    # A generation that is not published for this demo.
    assert api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, UNKNOWN_GENERATION_ID)).status_code == 404

    # An explicitly requested subject with no rows is a typed empty page.
    absent = api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id, subject_id=ABSENT_STEAM_ID))
    assert absent.status_code == 200, absent.text
    assert absent.json()["total"] == 0
    assert absent.json()["encounters"] == []
    assert absent.json()["subject_id"] == f"steam:{ABSENT_STEAM_ID}"


def test_encounter_detail_matches_list_grouping(api: Api) -> None:
    listing = api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id, round_id=1))
    assert listing.status_code == 200, listing.text
    encounter_id = listing.json()["encounters"][0]["encounter_id"]

    detail = api.client.get(f"{API}/demos/{DEMO_ID}/encounters/{encounter_id}", params=encounter_query(api, api.first.generation_id))
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["summary"]["encounter_id"] == encounter_id
    assert body["summary"]["round_id"] == 1
    assert body["events"], body
    assert body["subject_event_count"] >= 1
    assert body["source_window"]["round_id"] == 1
    assert body["source_window"]["window_start_tick"] <= body["source_window"]["window_end_tick"]
    assert body["trajectory_stride"] >= 1
    assert len(body["subject_trajectory"]) <= 4096
    assert body["provenance"]["generation_id"] == api.first.generation_id
    for event in body["events"]:
        assert event["evidence"]["generation_id"] == api.first.generation_id
        assert event["evidence"]["row_ordinal"] >= 0

    # A well-formed id that this generation and grouping never produced.
    missing = api.client.get(
        f"{API}/demos/{DEMO_ID}/encounters/{ENCOUNTER_ID_PREFIX}-r1-0000000000000000", params=encounter_query(api, api.first.generation_id)
    )
    assert missing.status_code == 404, missing.text
    # A malformed id is a request error, not a lookup miss.
    malformed = api.client.get(f"{API}/demos/{DEMO_ID}/encounters/not-an-encounter", params=encounter_query(api, api.first.generation_id))
    assert malformed.status_code == 400, malformed.text
    assert malformed.json()["code"] == "INVALID_ARGUMENT"


def test_encounter_context_exposure_never_claims_unproven_exposure(api: Api) -> None:
    listing = api.client.get(f"{API}/demos/{DEMO_ID}/encounters", params=encounter_query(api, api.first.generation_id, round_id=1))
    encounter_id = listing.json()["encounters"][0]["encounter_id"]

    response = api.client.get(f"{API}/demos/{DEMO_ID}/encounters/{encounter_id}/context", params=encounter_query(api, api.first.generation_id))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["encounter_id"] == encounter_id
    assert body["subject_id"] == PLAYER_A
    assert body["snapshots"], body
    exposure = body["exposure"]
    assert exposure["status"] in {"qualified", "unknown", "unsupported", "not_applicable"}
    assert exposure["sampling"]["stride_ticks"] >= 1
    assert exposure["sampling"]["end_tick"] >= exposure["sampling"]["start_tick"]
    if exposure["status"] != "qualified":
        # An unqualified exposure must not name an earliest exposure tick.
        assert exposure["earliest_exposure_tick"] is None


# -- context ----------------------------------------------------------------
def test_context_is_exact_tick_and_reports_gaps(api: Api) -> None:
    exact = api.client.get(
        f"{API}/demos/{DEMO_ID}/context",
        params={"generation_id": api.first.generation_id, "subject_id": PLAYER_A, "tick": 1300},
    )
    assert exact.status_code == 200, exact.text
    body = exact.json()
    assert body["tick"] == 1300
    assert body["exact"] is True
    assert body["subject_id"] == PLAYER_A
    assert body["round_id"] == 1
    assert body["generation_id"] == api.first.generation_id
    assert body["subject"] is not None
    assert body["counts"]["state_rows"] == len(PLAYER_IDS)
    assert body["provenance"]["generation_id"] == api.first.generation_id

    # A tick with no recorded rows at all: reported as a gap, never snapped.
    gap = api.client.get(
        f"{API}/demos/{DEMO_ID}/context",
        params={"generation_id": api.first.generation_id, "subject_id": PLAYER_A, "tick": 1234},
    )
    assert gap.status_code == 200, gap.text
    assert gap.json()["exact"] is False
    assert gap.json()["counts"]["state_rows"] == 0
    assert gap.json()["subject"] is None

    pinned = api.client.get(
        f"{API}/demos/{DEMO_ID}/context",
        params={"generation_id": api.second.generation_id, "subject_id": PLAYER_A, "tick": 3200},
    )
    assert pinned.status_code == 200, pinned.text
    assert pinned.json()["generation_id"] == api.second.generation_id

    assert api.client.get(f"{API}/demos/{DEMO_ID}/context", params={"subject_id": PLAYER_A, "tick": -1}).status_code == 422


def test_context_without_subject_never_substitutes(api: Api) -> None:
    api.client.put(f"{API}/analysis-subject", json={"steam_id": ABSENT_STEAM_ID})
    response = api.client.get(f"{API}/demos/{DEMO_ID}/context", params={"generation_id": api.first.generation_id, "tick": 1300})
    assert response.status_code == 400, response.text
    assert response.json()["code"] == "SUBJECT_UNAVAILABLE"

    # The same read succeeds for an explicitly selected participant.
    selected = api.client.get(
        f"{API}/demos/{DEMO_ID}/context",
        params={"generation_id": api.first.generation_id, "tick": 1300, "subject_id": PLAYER_B},
    )
    assert selected.status_code == 200, selected.text
    assert selected.json()["subject_id"] == PLAYER_B


# -- geometry ---------------------------------------------------------------
def test_geometry_routes_are_bounded_and_never_clear_when_unproven(api: Api) -> None:
    capabilities = api.client.get(f"{API}/geometry/capabilities", params={"map_name": "inferno"})
    assert capabilities.status_code == 200, capabilities.text
    body = capabilities.json()
    assert body["map_name"] == "inferno"
    assert isinstance(body["prepared"], bool)
    assert body["physics"]["status"] in {"available", "partial", "unavailable", "unsupported"}
    assert body["match_status"] in {"exact", "mismatch", "unknown"}

    segment_params = {
        "map_name": "inferno",
        "start_x": -1234.0,
        "start_y": 987.0,
        "start_z": 64.0,
        "end_x": -1100.0,
        "end_y": 900.0,
        "end_z": 64.0,
    }
    segment = api.client.get(f"{API}/geometry/segment", params=segment_params)
    assert segment.status_code == 200, segment.text
    segment_body = segment.json()
    assert segment_body["status"] in {"static_clear", "static_blocked", "unknown", "unsupported"}
    assert segment_body["match_status"] in {"exact", "mismatch", "unknown"}
    if segment_body["match_status"] != "exact":
        # A sightline against non-matching assets can never be reported as clear.
        assert segment_body["status"] != "static_clear"

    navigation = api.client.get(f"{API}/geometry/navigation", params=segment_params)
    assert navigation.status_code == 200, navigation.text
    assert navigation.json()["status"] in {"available", "unavailable", "unsupported"}
    if navigation.json()["status"] != "available":
        assert navigation.json()["connected"] is not True

    # Coordinates and identifiers outside the bounded request model.
    out_of_bounds = {**segment_params, "start_x": 99999.0}
    assert api.client.get(f"{API}/geometry/segment", params=out_of_bounds).status_code == 422
    assert api.client.get(f"{API}/geometry/capabilities", params={"map_name": "m" * 65}).status_code == 422

    prepared = api.client.post(f"{API}/geometry/inferno/prepare", json={})
    assert prepared.status_code == 200, prepared.text
    assert prepared.json()["map_name"] == "inferno"


# -- regression -------------------------------------------------------------
def test_phase1_reads_are_unchanged(api: Api) -> None:
    assert api.client.get(f"{API}/health").status_code == 200
    state = api.client.get(
        f"{API}/demos/{DEMO_ID}/analytics/state",
        params={"generation_id": api.first.generation_id, "tick": 1300},
    )
    assert state.status_code == 200, state.text
    assert len(state.json()["states"]) == len(PLAYER_IDS)

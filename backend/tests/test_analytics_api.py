"""HTTP surface of the Phase 1 analytics endpoints over a genuine generation.

Like ``test_api``, every response is served from canonical Parquet tables through
a real catalog/artifact pair; the client is bound to ``http://127.0.0.1:8765``
with ``manage_lifetime=False`` so the coordinator is never started. The fixtures
here are the shared Phase 0 builders (``inferno_tables``/``mirage_tables``); this
module adds no new generation data of its own.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cs_demo_analyzer.api.routes import create_app
from helpers import (
    ALIGNED_TICKS,
    API,
    BASE_URL,
    DEMO_ID,
    KILL_TICKS,
    OFF_GRID_TICK,
    PENDING_DEMO_ID,
    PLAYER_A,
    PLAYER_B,
    PLAYER_C,
    PLAYER_IDS,
    ROUND_ONE_FREEZE_END,
    ROUND_ONE_END,
    STEAM_A,
    TICK_RATE_HZ,
    UNRESOLVED_PLAYER,
    Api,
    commit_generation,
    create_application,
    inferno_tables,
    mirage_tables,
    register_demo,
)

# "inferno" holds 26 aligned ticks x 4 players, the two off-grid kill ticks for
# A/B, the 1300/1350 kill ticks for all four, and one null corpse row at 1252.
INFERNO_OBSERVATIONS = len(ALIGNED_TICKS) * len(PLAYER_IDS) + 2 + 2 + 4 + 4 + 1
INFERNO_IDENTIFIED = INFERNO_OBSERVATIONS - 1

# A tick with no state row at all: the aligned grid steps 1232 -> 1240.
ABSENT_TICK = 1234

UNKNOWN_DEMO_ID = "f" * 64
UNKNOWN_GENERATION_ID = "0" * 64


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


def analytics(api: Api, path: str, **params):
    return api.client.get(f"{API}/demos/{DEMO_ID}/analytics/{path}", params=params)


def multi(api: Api, selections, op: str, **params):
    return api.client.post(
        f"{API}/demos/multi/query", json={"selections": selections, "op": op, "params": params}
    )


def selection(demo_id: str = DEMO_ID, generation_id: str | None = None) -> dict[str, object]:
    return {"demo_id": demo_id, "generation_id": generation_id}


# -- state ------------------------------------------------------------------
def test_state_serves_verbatim_rows_and_echoes_the_pinned_generation(api: Api):
    generation = api.first.generation_id
    response = analytics(api, "state", generation_id=generation, tick=KILL_TICKS[0])
    assert response.status_code == 200
    body = response.json()
    assert body["generation_id"] == generation
    assert body["tick_rate_hz"] == TICK_RATE_HZ
    assert body["requested_tick"] == KILL_TICKS[0]
    assert body["actual_tick"] == KILL_TICKS[0]
    assert body["gap_ticks"] == 0
    assert body["exact"] is True
    # Both live players of that tick plus the null corpse entity are observations.
    assert len(body["states"]) == 3
    assert any(state["player_id"] is None for state in body["states"])
    assert PLAYER_A in response.text and "e+16" not in response.text

    filtered = analytics(api, "state", generation_id=generation, tick=KILL_TICKS[0], player_id=PLAYER_A)
    assert [state["player_id"] for state in filtered.json()["states"]] == [PLAYER_A]


def test_state_head_generation_and_gap_search(api: Api):
    # No generation_id: the current head (the mirage generation) is served.
    head = analytics(api, "state", tick=KILL_TICKS[0])
    assert head.status_code == 200
    assert head.json()["generation_id"] == api.second.generation_id
    assert head.json()["actual_tick"] is None
    assert head.json()["exact"] is False
    assert head.json()["states"] == []

    # A superseded generation stays addressable when it is pinned explicitly.
    superseded = analytics(api, "state", generation_id=api.first.generation_id, tick=OFF_GRID_TICK)
    assert superseded.json()["generation_id"] == api.first.generation_id
    assert superseded.json()["actual_tick"] == OFF_GRID_TICK
    assert len(superseded.json()["states"]) == 2

    empty = analytics(api, "state", generation_id=api.first.generation_id, tick=ABSENT_TICK, max_gap=0)
    assert empty.json()["actual_tick"] is None
    assert empty.json()["gap_ticks"] is None
    assert empty.json()["states"] == []

    nearest = analytics(api, "state", generation_id=api.first.generation_id, tick=ABSENT_TICK, max_gap=8)
    assert nearest.json()["actual_tick"] == 1232
    assert nearest.json()["gap_ticks"] == -2
    assert nearest.json()["exact"] is False

    # The gap search honours the player filter: only C's ticks are candidates.
    player = analytics(
        api,
        "state",
        generation_id=api.first.generation_id,
        tick=1250,
        player_id=PLAYER_C,
        max_gap=8,
    )
    assert player.json()["actual_tick"] == 1248
    assert {state["player_id"] for state in player.json()["states"]} == {PLAYER_C}


def test_state_rejects_malformed_input_and_unavailable_generations(api: Api):
    assert analytics(api, "state", generation_id=api.first.generation_id, tick=-1).status_code == 422
    assert analytics(api, "state", generation_id=api.first.generation_id).status_code == 422
    assert (
        analytics(api, "state", generation_id=api.first.generation_id, tick=KILL_TICKS[0], max_gap=-1).status_code
        == 422
    )

    unknown_generation = analytics(api, "state", generation_id=UNKNOWN_GENERATION_ID, tick=KILL_TICKS[0])
    assert unknown_generation.status_code == 404
    assert unknown_generation.json()["code"] == "GENERATION_UNAVAILABLE"

    pending = api.client.get(
        f"{API}/demos/{PENDING_DEMO_ID}/analytics/state", params={"tick": KILL_TICKS[0]}
    )
    assert pending.status_code == 409
    assert pending.json()["code"] == "NOT_READY"

    missing_demo = api.client.get(
        f"{API}/demos/{UNKNOWN_DEMO_ID}/analytics/state", params={"tick": KILL_TICKS[0]}
    )
    assert missing_demo.status_code == 404
    assert missing_demo.json()["code"] == "NOT_FOUND"


# -- trajectory -------------------------------------------------------------
def test_trajectory_preserves_string_ids_and_reports_holes(api: Api):
    generation = api.first.generation_id
    response = analytics(
        api,
        "trajectory",
        generation_id=generation,
        player_id=PLAYER_A,
        start=ROUND_ONE_FREEZE_END,
        end=ROUND_ONE_END,
        stride=8,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["generation_id"] == generation
    assert body["player_id"] == PLAYER_A
    assert body["start_tick"] == ROUND_ONE_FREEZE_END
    assert body["end_tick"] == ROUND_ONE_END
    assert body["stride"] == 8
    assert body["sample_count"] == len(ALIGNED_TICKS)
    assert body["missing_ranges"] == []
    assert {state["player_id"] for state in body["states"]} == {PLAYER_A}
    assert STEAM_A in response.text and "e+16" not in response.text

    holed = analytics(
        api,
        "trajectory",
        generation_id=generation,
        player_id=PLAYER_A,
        start=1200,
        end=1210,
        stride=1,
    ).json()
    assert holed["missing_ranges"] == [[1201, 1207], [1209, 1210]]
    assert [state["tick"] for state in holed["states"]] == [1200, 1208]

    absent = analytics(
        api,
        "trajectory",
        generation_id=generation,
        player_id=UNRESOLVED_PLAYER,
        start=ROUND_ONE_FREEZE_END,
        end=ROUND_ONE_END,
        stride=8,
    ).json()
    assert absent["states"] == []
    assert absent["missing_ranges"] == [[ROUND_ONE_FREEZE_END, ROUND_ONE_END]]


def test_trajectory_stride_bounds_and_rejections(api: Api):
    generation = api.first.generation_id
    boundary = analytics(
        api, "trajectory", generation_id=generation, player_id=PLAYER_A, start=1200, end=1400, stride=4096
    )
    assert boundary.status_code == 200
    assert boundary.json()["stride"] == 4096
    assert boundary.json()["sample_count"] == 1

    base = {"generation_id": generation, "player_id": PLAYER_A, "start": 1200, "end": 1400}
    assert analytics(api, "trajectory", **base, stride=0).status_code == 422
    assert analytics(api, "trajectory", **base, stride=4097).status_code == 422
    assert analytics(
        api, "trajectory", generation_id=generation, player_id=PLAYER_A, start=-1, end=1400
    ).status_code == 422
    blank_player = analytics(
        api, "trajectory", generation_id=generation, player_id="", start=1200, end=1400
    )
    assert blank_player.status_code == 400
    assert blank_player.json()["code"] == "INVALID_ARGUMENT"
    inverted = analytics(
        api, "trajectory", generation_id=generation, player_id=PLAYER_A, start=1300, end=1200
    )
    assert inverted.status_code == 400
    assert inverted.json()["code"] == "INVALID_ARGUMENT"


# -- events -----------------------------------------------------------------
def test_events_merge_datasets_with_verbatim_actors(api: Api):
    generation = api.first.generation_id
    response = analytics(
        api,
        "events",
        generation_id=generation,
        datasets="kills,damages",
        start=1250,
        end=1355,
        limit=100,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["generation_id"] == generation
    assert body["start_tick"] == 1250
    assert body["end_tick"] == 1355
    assert body["event_count"] == 5 == len(body["events"])
    assert [event["tick"] for event in body["events"]] == sorted(event["tick"] for event in body["events"])
    # Same-tick ordering is kills before damages.
    assert [event["dataset"] for event in body["events"][:2]] == ["kills", "damages"]
    assert body["events"][0]["actor1"] == PLAYER_A
    assert body["events"][0]["actor2"] == PLAYER_B
    assert PLAYER_B in response.text and "e+16" not in response.text

    kills_only = analytics(
        api, "events", generation_id=generation, datasets="kills", start=1250, end=1355, limit=100
    ).json()
    assert kills_only["event_count"] == 3
    assert {event["dataset"] for event in kills_only["events"]} == {"kills"}

    all_default = analytics(api, "events", generation_id=generation, start=1250, end=1355).json()
    # kills 1252/1300/1350, damages 1252/1350, shots 1252, bomb 1310.
    assert all_default["event_count"] == 7
    assert {event["dataset"] for event in all_default["events"]} == {"kills", "damages", "shots", "bomb"}

    capped = analytics(
        api, "events", generation_id=generation, datasets="kills,damages", start=1250, end=1355, limit=2
    ).json()
    assert capped["event_count"] == 2

    none = analytics(
        api, "events", generation_id=generation, datasets="kills,damages", start=1250, end=1355, limit=0
    ).json()
    assert none["event_count"] == 0 and none["events"] == []

    # An empty tick range is honestly empty, not an error.
    inverted = analytics(api, "events", generation_id=generation, start=1355, end=1250).json()
    assert inverted["event_count"] == 0


def test_events_reject_bad_datasets_and_out_of_range_limits(api: Api):
    generation = api.first.generation_id
    unknown = analytics(api, "events", generation_id=generation, datasets="kills,smokes", start=0, end=1400)
    assert unknown.status_code == 400
    assert unknown.json()["code"] == "INVALID_ARGUMENT"

    empty = analytics(api, "events", generation_id=generation, datasets="", start=0, end=1400)
    assert empty.status_code == 400
    assert empty.json()["code"] == "INVALID_ARGUMENT"

    assert analytics(api, "events", generation_id=generation, start=0, end=1400, limit=5001).status_code == 422
    assert analytics(api, "events", generation_id=generation, start=0, end=1400, limit=-1).status_code == 422
    assert analytics(api, "events", generation_id=generation, end=1400).status_code == 422
    assert analytics(api, "events", generation_id=generation, start=-1, end=1400).status_code == 422


def test_event_window_returns_the_event_its_states_and_neighbours(api: Api):
    generation = api.first.generation_id
    response = analytics(
        api,
        "event-window",
        generation_id=generation,
        dataset="kills",
        row_ordinal=0,
        before=10,
        after=10,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["generation_id"] == generation
    assert body["tick_rate_hz"] == TICK_RATE_HZ
    assert body["event"] == {
        "dataset": "kills",
        "row_ordinal": 0,
        "tick": KILL_TICKS[0],
        "actor1": PLAYER_A,
        "actor2": PLAYER_B,
        "detail": "ak47",
    }
    # Only identified rows of the involved players, never the corpse row.
    assert body["states"]
    assert {state["player_id"] for state in body["states"]} == {PLAYER_A, PLAYER_B}
    assert {event["tick"] for event in body["nearby_events"]} == {KILL_TICKS[0]}
    assert {event["dataset"] for event in body["nearby_events"]} == {"kills", "damages", "shots"}

    missing = analytics(
        api, "event-window", generation_id=generation, dataset="kills", row_ordinal=99, before=1, after=1
    )
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"

    unknown_dataset = analytics(
        api, "event-window", generation_id=generation, dataset="smokes", row_ordinal=0
    )
    assert unknown_dataset.status_code == 400
    assert unknown_dataset.json()["code"] == "INVALID_ARGUMENT"

    assert (
        analytics(
            api, "event-window", generation_id=generation, dataset="kills", row_ordinal=0, before=64001
        ).status_code
        == 422
    )
    assert (
        analytics(
            api, "event-window", generation_id=generation, dataset="kills", row_ordinal=-1
        ).status_code
        == 422
    )


# -- coverage ---------------------------------------------------------------
def test_coverage_counts_corpse_rows_without_counting_them_as_alive(api: Api):
    generation = api.first.generation_id
    response = analytics(api, "coverage", generation_id=generation)
    assert response.status_code == 200
    body = response.json()
    assert body["generation_id"] == generation
    assert body["scope"] == "generation"
    coverage = body["coverage"]
    assert coverage["total_observations"] == INFERNO_OBSERVATIONS
    assert coverage["identified"] == INFERNO_IDENTIFIED
    assert coverage["null_observations"] == 1
    assert coverage["alive_total"] == INFERNO_IDENTIFIED
    assert coverage["alive_identified"] == INFERNO_IDENTIFIED
    assert coverage["alive_null"] == 0
    assert coverage["live_coverage"] == 1.0
    assert coverage["notes"]

    round_scoped = analytics(api, "coverage", generation_id=generation, round_id=1).json()
    assert round_scoped["scope"] == "round:1"
    for field in (
        "total_observations",
        "identified",
        "null_observations",
        "alive_total",
        "alive_identified",
        "alive_null",
        "live_coverage",
    ):
        assert round_scoped["coverage"][field] == coverage[field], field
    # The notes carry the measured scope, which is the only scope-dependent field.
    assert any("round:1" in note for note in round_scoped["coverage"]["notes"])
    assert any("generation" in note for note in coverage["notes"])

    empty_round = analytics(api, "coverage", generation_id=generation, round_id=2).json()
    assert empty_round["scope"] == "round:2"
    assert empty_round["coverage"]["total_observations"] == 0
    assert empty_round["coverage"]["live_coverage"] is None


def test_coverage_round_errors(api: Api):
    generation = api.first.generation_id
    partial = analytics(api, "coverage", generation_id=generation, round_id=3)
    assert partial.status_code == 409
    assert partial.json()["code"] == "PARTIAL_ROUND"

    unknown_round = analytics(api, "coverage", generation_id=generation, round_id=99)
    assert unknown_round.status_code == 404
    assert unknown_round.json()["code"] == "NOT_FOUND"

    assert analytics(api, "coverage", generation_id=generation, round_id=0).status_code == 422


# -- distance ---------------------------------------------------------------
def test_distance_is_exact_tick_only_and_reports_missing_pairs(api: Api):
    generation = api.first.generation_id
    response = analytics(
        api,
        "distance",
        generation_id=generation,
        tick=KILL_TICKS[0],
        player_a=PLAYER_A,
        player_b=PLAYER_B,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["generation_id"] == generation
    assert body["tick"] == KILL_TICKS[0]
    assert body["player_a"] == PLAYER_A
    assert body["player_b"] == PLAYER_B
    # Every authored row shares one position, so a present pair is exactly zero.
    assert body["distance_2d"] == 0.0
    assert body["distance_3d"] == 0.0
    assert body["missing"] is False
    assert PLAYER_A in response.text and "e+16" not in response.text

    # C has no row at 1252: the pair is missing rather than interpolated.
    absent_player = analytics(
        api,
        "distance",
        generation_id=generation,
        tick=KILL_TICKS[0],
        player_a=PLAYER_A,
        player_b=PLAYER_C,
    ).json()
    assert absent_player["missing"] is True
    assert absent_player["distance_2d"] is None and absent_player["distance_3d"] is None

    absent_tick = analytics(
        api,
        "distance",
        generation_id=generation,
        tick=ABSENT_TICK,
        player_a=PLAYER_A,
        player_b=PLAYER_B,
    ).json()
    assert absent_tick["missing"] is True

    off_grid = analytics(
        api,
        "distance",
        generation_id=generation,
        tick=OFF_GRID_TICK,
        player_a=PLAYER_A,
        player_b=PLAYER_B,
    ).json()
    assert off_grid["missing"] is False


def test_distance_rejects_malformed_requests(api: Api):
    generation = api.first.generation_id
    base = {"player_a": PLAYER_A, "player_b": PLAYER_B}
    assert analytics(api, "distance", **base, generation_id=generation, tick=-1).status_code == 422
    assert analytics(api, "distance", **base, generation_id=generation).status_code == 422
    assert (
        analytics(
            api, "distance", generation_id=generation, tick=KILL_TICKS[0], player_b=PLAYER_B
        ).status_code
        == 422
    )
    unknown_generation = analytics(
        api, "distance", **base, generation_id=UNKNOWN_GENERATION_ID, tick=KILL_TICKS[0]
    )
    assert unknown_generation.status_code == 404
    assert unknown_generation.json()["code"] == "GENERATION_UNAVAILABLE"


# -- multi/query ------------------------------------------------------------
def test_multi_query_pins_each_selection_and_captures_per_demo_errors(api: Api):
    response = multi(
        api,
        [
            selection(DEMO_ID, api.first.generation_id),
            selection(DEMO_ID),
            selection(PENDING_DEMO_ID),
            selection(UNKNOWN_DEMO_ID),
        ],
        "coverage",
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 4

    pinned, head, pending, unknown_demo = body["results"]
    assert pinned["demo_id"] == DEMO_ID
    assert pinned["generation_id"] == api.first.generation_id
    assert pinned["error"] is None
    assert pinned["result"]["coverage"]["total_observations"] == INFERNO_OBSERVATIONS

    assert head["generation_id"] == api.second.generation_id
    assert head["error"] is None
    assert head["result"]["coverage"]["total_observations"] == 2

    assert pending["demo_id"] == PENDING_DEMO_ID
    assert pending["generation_id"] is None
    assert pending["result"] is None
    assert pending["error"]["code"] == "NOT_READY"

    assert unknown_demo["demo_id"] == UNKNOWN_DEMO_ID
    assert unknown_demo["result"] is None
    assert unknown_demo["error"]["code"] == "NOT_FOUND"


def test_multi_query_captures_analytics_errors_per_selection(api: Api):
    partial = multi(api, [selection(DEMO_ID, api.first.generation_id)], "coverage", round_id=3)
    assert partial.status_code == 200
    entry = partial.json()["results"][0]
    assert entry["result"] is None
    assert entry["error"]["code"] == "PARTIAL_ROUND"
    assert entry["generation_id"] == api.first.generation_id

    unknown_generation = multi(api, [selection(DEMO_ID, UNKNOWN_GENERATION_ID)], "coverage")
    entry = unknown_generation.json()["results"][0]
    assert entry["error"]["code"] == "GENERATION_UNAVAILABLE"
    # A failed open echoes the revision that was requested.
    assert entry["generation_id"] == UNKNOWN_GENERATION_ID


def test_multi_query_events_op_matches_the_single_demo_endpoint(api: Api):
    response = multi(
        api,
        [selection(DEMO_ID, api.first.generation_id)],
        "events",
        start=1250,
        end=1355,
        datasets=["kills", "damages"],
        limit=10,
    )
    assert response.status_code == 200
    entry = response.json()["results"][0]
    assert entry["error"] is None
    assert entry["result"]["start_tick"] == 1250
    assert entry["result"]["end_tick"] == 1355
    assert entry["result"]["event_count"] == 5
    assert [event["dataset"] for event in entry["result"]["events"][:2]] == ["kills", "damages"]

    single = analytics(
        api,
        "events",
        generation_id=api.first.generation_id,
        datasets="kills,damages",
        start=1250,
        end=1355,
        limit=10,
    ).json()
    assert entry["result"]["events"] == single["events"]

    empty = multi(api, [], "coverage")
    assert empty.status_code == 200
    assert empty.json()["results"] == []


def test_multi_query_validates_bounds_and_params(api: Api):
    too_many = multi(api, [selection(DEMO_ID) for _ in range(21)], "coverage")
    assert too_many.status_code == 400
    assert too_many.json()["code"] == "INVALID_ARGUMENT"

    boundary = multi(api, [selection(DEMO_ID) for _ in range(20)], "coverage")
    assert boundary.status_code == 200
    assert len(boundary.json()["results"]) == 20

    assert multi(api, [selection(DEMO_ID)], "timeline").status_code == 422
    assert multi(api, [selection(DEMO_ID)], "events", end=1400).status_code == 400
    assert multi(api, [selection(DEMO_ID)], "events", start=0, end=1400, limit=5001).status_code == 400
    assert multi(api, [selection(DEMO_ID)], "events", start=0, end=1400, datasets=["smokes"]).status_code == 400
    assert multi(api, [selection(DEMO_ID)], "coverage", round_id=-1).status_code == 400
    assert api.client.post(f"{API}/demos/multi/query", json={"selections": [], "op": "coverage"}).status_code == 200
    # ``params`` may be omitted entirely; the body still fans out.
    default_params = api.client.post(
        f"{API}/demos/multi/query",
        json={"op": "coverage", "selections": [{"demo_id": PENDING_DEMO_ID}]},
    )
    assert default_params.status_code == 200
    assert default_params.json()["results"][0]["error"]["code"] == "NOT_READY"

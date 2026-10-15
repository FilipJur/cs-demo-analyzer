"""HTTP surface of the real application over a genuine published generation.

Every response is served from canonical Parquet tables, hashed manifests and a
catalog.sqlite produced by the storage services in ``helpers``; no endpoint is
stubbed. The client is bound to ``http://127.0.0.1:8765`` with
``manage_lifetime=False`` so the coordinator is never started by a test.
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
    OUT_OF_ROUND_KILL_TICK,
    PENDING_DEMO_ID,
    PLAYER_A,
    PLAYER_B,
    PLAYER_C,
    PLAYER_D,
    PLAYER_IDS,
    ROUND_ONE_END,
    ROUND_ONE_FREEZE_END,
    SAMPLES_IN_ROUND_ONE,
    STEAM_A,
    TICK_RATE_HZ,
    UNRESOLVED_PLAYER,
    Api,
    commit_generation,
    create_application,
    inferno_tables,
    mirage_tables,
    oversized_tables,
    register_demo,
)


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


def replay_request(api: Api, generation_id: str, **params):
    params.setdefault("round_id", 1)
    return api.client.get(f"{API}/demos/{DEMO_ID}/replay", params={"generation_id": generation_id, **params})


def test_health_and_library_expose_exact_identities(api: Api):
    health = api.client.get(f"{API}/health")
    assert health.status_code == 200
    body = health.json()
    assert body["status"] == "ready"
    assert body["data_root"] == str(api.data_root)
    assert body["worker_running"] is False

    listing = api.client.get(f"{API}/demos")
    assert listing.status_code == 200
    assert sorted(item["demo_id"] for item in listing.json()) == sorted([DEMO_ID, PENDING_DEMO_ID])

    detail = api.client.get(f"{API}/demos/{DEMO_ID}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["demo"]["demo_id"] == DEMO_ID
    assert payload["demo"]["generation_id"] == api.second.generation_id
    assert payload["demo"]["raw_path"].endswith("source.dem")
    assert payload["manifest"]["generation_id"] == api.second.generation_id
    assert payload["manifest"]["map_name"] == "mirage"
    assert [source["demo_id"] for source in payload["sources"]] == [DEMO_ID]
    assert [source["status"] for source in payload["sources"]] == ["imported"]

    missing = api.client.get(f"{API}/demos/{'0' * 64}")
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"


def test_replay_preserves_exact_string_ids_and_null_identities(api: Api):
    response = replay_request(api, api.first.generation_id)
    assert response.status_code == 200
    chunk = response.json()
    assert chunk["generation_id"] == api.first.generation_id
    assert chunk["clock"] == "awpy_demo_tick"
    assert chunk["tick_rate_hz"] == TICK_RATE_HZ

    players = {player["player_id"]: player for player in chunk["players"]}
    assert set(players) == set(PLAYER_IDS) | {UNRESOLVED_PLAYER}
    assert players[PLAYER_A]["steam_id"] == STEAM_A
    assert isinstance(players[PLAYER_A]["steam_id"], str)
    assert players[PLAYER_C]["name"] is None
    assert players[UNRESOLVED_PLAYER]["steam_id"] is None
    # Seventeen digits survive as a quoted literal, never as a float or exponent.
    assert f'"{STEAM_A}"' in response.text
    assert "e+16" not in response.text


def test_replay_events_keep_null_and_world_actors(api: Api):
    response = replay_request(api, api.first.generation_id)
    assert response.status_code == 200
    chunk = response.json()
    events = {event["tick"]: event for event in chunk["events"]}
    assert sorted(events) == sorted(KILL_TICKS)
    assert OUT_OF_ROUND_KILL_TICK not in events

    assert events[KILL_TICKS[0]]["attacker_id"] == PLAYER_A
    assert events[KILL_TICKS[0]]["victim_id"] == PLAYER_B
    assert events[KILL_TICKS[0]]["headshot"] is True
    # World death: no attacker identity, still reported with its victim.
    assert events[KILL_TICKS[1]]["attacker_id"] is None
    assert events[KILL_TICKS[1]]["victim_id"] == PLAYER_C
    # Unrecorded victim identity is carried through as null, not dropped.
    assert events[KILL_TICKS[2]]["attacker_id"] == PLAYER_D
    assert events[KILL_TICKS[2]]["victim_id"] is None

    # Dead/unknown state rows (null player_id) never become replay actors.
    assert all(sample["player_id"] is not None for sample in chunk["samples"])
    assert len({(sample["tick"], sample["player_id"]) for sample in chunk["samples"]}) == len(chunk["samples"])
    assert all(sample["player_id"] in set(PLAYER_IDS) for sample in chunk["samples"])

    radar = chunk["radar"]
    assert radar["asset_id"] is None
    assert radar["warning"]


def test_replay_samples_include_off_grid_event_ticks(api: Api):
    response = replay_request(api, api.first.generation_id, stride_ticks=8)
    assert response.status_code == 200
    chunk = response.json()
    assert chunk["stride_ticks"] == 8
    assert (chunk["start_tick"], chunk["end_tick"]) == (ROUND_ONE_FREEZE_END, ROUND_ONE_END)

    samples = {(sample["tick"], sample["player_id"]) for sample in chunk["samples"]}
    expected = {(tick, player_id) for tick in ALIGNED_TICKS for player_id in PLAYER_IDS}
    expected |= {(KILL_TICKS[0], PLAYER_A), (KILL_TICKS[0], PLAYER_B)}
    expected |= {(tick, player_id) for tick in KILL_TICKS[1:] for player_id in PLAYER_IDS}
    assert len(chunk["samples"]) == SAMPLES_IN_ROUND_ONE == len(expected)
    assert samples == expected
    # Every kill tick is off the 8 Hz grid, so only event-tick evidence can include it.
    assert all((tick - ROUND_ONE_FREEZE_END) % 8 != 0 for tick in KILL_TICKS)
    assert (KILL_TICKS[1], PLAYER_C) in samples
    assert (KILL_TICKS[2], PLAYER_D) in samples
    # Off-grid and event-free: excluded, as is the null-identity state row at 1252.
    assert not any(tick == OFF_GRID_TICK for tick, _ in samples)
    assert not any(tick == KILL_TICKS[0] and player_id in (PLAYER_C, PLAYER_D) for tick, player_id in samples)

    default = replay_request(api, api.first.generation_id)
    assert default.status_code == 200
    assert default.json()["stride_ticks"] == 8
    assert default.json()["samples"] == chunk["samples"]


def test_generation_pinning_serves_superseded_generations(api: Api):
    latest = api.client.get(f"{API}/demos/{DEMO_ID}/rounds")
    assert latest.status_code == 200
    assert latest.json()["generation_id"] == api.second.generation_id
    assert latest.json()["rounds"][0]["end_tick"] == 3400
    assert latest.json()["rounds"][0]["winner_side"] == "t"

    pinned = api.client.get(
        f"{API}/demos/{DEMO_ID}/rounds", params={"generation_id": api.first.generation_id}
    )
    assert pinned.status_code == 200
    assert pinned.json()["generation_id"] == api.first.generation_id
    assert [round_["round_id"] for round_ in pinned.json()["rounds"]] == [1, 2, 3]
    assert pinned.json()["rounds"][0]["end_tick"] == ROUND_ONE_END
    assert pinned.json()["rounds"][0]["winner_side"] == "ct"
    assert pinned.json()["rounds"][2]["end_tick"] is None

    superseded = replay_request(api, api.first.generation_id)
    assert superseded.status_code == 200
    assert superseded.json()["generation_id"] == api.first.generation_id
    assert superseded.json()["events"]
    assert (api.data_root / "datasets" / DEMO_ID / api.first.generation_id / "manifest.json").is_file()

    unknown = replay_request(api, "0" * 32)
    assert unknown.status_code == 404
    assert unknown.json()["code"] == "GENERATION_UNAVAILABLE"


def test_demo_without_a_generation_reports_not_ready(api: Api):
    detail = api.client.get(f"{API}/demos/{PENDING_DEMO_ID}")
    assert detail.status_code == 200
    assert detail.json()["demo"]["generation_id"] is None
    assert detail.json()["manifest"] is None

    rounds = api.client.get(f"{API}/demos/{PENDING_DEMO_ID}/rounds")
    assert rounds.status_code == 409
    assert rounds.json()["code"] == "NOT_READY"

    unavailable = api.client.get(
        f"{API}/demos/{PENDING_DEMO_ID}/replay", params={"generation_id": "0" * 32, "round_id": 1}
    )
    assert unavailable.status_code == 404
    assert unavailable.json()["code"] == "GENERATION_UNAVAILABLE"


def test_reprocess_returns_a_durable_job_and_keeps_the_current_generation(api: Api):
    before = api.client.get(f"{API}/demos/{DEMO_ID}").json()["demo"]["generation_id"]

    response = api.client.post(
        f"{API}/demos/{DEMO_ID}/reprocess", headers={"content-type": "application/json"}
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    assert job_id

    job = api.client.get(f"{API}/jobs/{job_id}")
    assert job.status_code == 200
    assert job.json()["demo_id"] == DEMO_ID
    assert job.json()["state"] == "queued"
    assert job.json()["generation_id"] != before

    listed = api.client.get(f"{API}/jobs").json()
    assert job_id in [item["id"] for item in listed]

    # Reprocessing never hides the last-good generation while the new attempt runs.
    assert api.client.get(f"{API}/demos/{DEMO_ID}").json()["demo"]["generation_id"] == before
    assert replay_request(api, before).status_code == 200

    unknown = api.client.get(f"{API}/jobs/{'0' * 32}")
    assert unknown.status_code == 404
    assert unknown.json()["code"] == "NOT_FOUND"


def test_malformed_ranges_and_windows_return_typed_errors(api: Api):
    generation = api.first.generation_id

    outside_start = replay_request(api, generation, start_tick=ROUND_ONE_FREEZE_END - 1)
    assert outside_start.status_code == 400 and outside_start.json()["code"] == "INVALID_WINDOW"
    outside_end = replay_request(api, generation, end_tick=ROUND_ONE_END + 1)
    assert outside_end.status_code == 400 and outside_end.json()["code"] == "INVALID_WINDOW"
    inverted = replay_request(api, generation, start_tick=1300, end_tick=1250)
    assert inverted.status_code == 400 and inverted.json()["code"] == "INVALID_WINDOW"
    # A window is confined to exactly one round.
    other_round = replay_request(api, generation, start_tick=1800, end_tick=1900)
    assert other_round.status_code == 400 and other_round.json()["code"] == "INVALID_WINDOW"

    assert replay_request(api, generation, round_id=99).status_code == 404
    partial = replay_request(api, generation, round_id=3)
    assert partial.status_code == 409 and partial.json()["code"] == "PARTIAL_ROUND"

    assert replay_request(api, generation, round_id=0).status_code == 422
    assert replay_request(api, generation, stride_ticks=0).status_code == 422
    assert replay_request(api, generation, stride_ticks=4097).status_code == 422
    assert api.client.get(
        f"{API}/demos/{DEMO_ID}/replay", params={"round_id": 1}
    ).status_code == 422

    boundary = replay_request(
        api, generation, stride_ticks=4096, start_tick=ROUND_ONE_FREEZE_END, end_tick=ROUND_ONE_END
    )
    assert boundary.status_code == 200
    assert boundary.json()["stride_ticks"] == 4096

    assert api.client.get(f"{API}/demos", params={"limit": 0}).status_code == 422
    assert api.client.get(f"{API}/demos", params={"limit": 501}).status_code == 422
    assert api.client.get(f"{API}/demos", params={"offset": -1}).status_code == 422
    assert api.client.get(f"{API}/demos", params={"limit": 1, "offset": 1}).status_code == 200


def test_cross_site_and_spoofed_requests_are_rejected(api: Api, monkeypatch):
    # Assert the shipped default policy: no development origin is configured.
    monkeypatch.delenv("CSDA_DEV_ORIGIN", raising=False)
    hostile = "https://evil.example"
    before = api.client.get(f"{API}/jobs").json()

    cross_site = api.client.post(
        f"{API}/scans", headers={"origin": hostile, "content-type": "application/json"}
    )
    assert cross_site.status_code == 403
    assert cross_site.json()["code"] == "INVALID_ORIGIN"
    assert "access-control-allow-origin" not in cross_site.headers

    # The loopback allowlist is exact: localhost is not this origin.
    lookalike = api.client.post(
        f"{API}/scans", headers={"origin": "http://localhost:8765", "content-type": "application/json"}
    )
    assert lookalike.status_code == 403
    assert lookalike.json()["code"] == "INVALID_ORIGIN"

    spoofed_host = api.client.post(f"{API}/scans", headers={"host": "evil.example"})
    assert spoofed_host.status_code == 403
    assert spoofed_host.json()["code"] == "INVALID_HOST"
    assert api.client.get(f"{API}/health", headers={"host": "evil.example"}).status_code == 403

    wrong_type = api.client.post(f"{API}/scans", headers={"content-type": "text/plain"})
    assert wrong_type.status_code == 415
    assert wrong_type.json()["code"] == "INVALID_CONTENT_TYPE"

    relative = api.client.post(
        f"{API}/imports",
        json={"path": "relative/recording.dem"},
        headers={"content-type": "application/json"},
    )
    assert relative.status_code == 400
    assert relative.json()["code"] == "INVALID_PATH"

    # No rejected mutation reached the coordinator.
    assert api.client.get(f"{API}/jobs").json() == before

    accepted = api.client.post(f"{API}/scans", headers={"content-type": "application/json"})
    assert accepted.status_code == 202
    assert accepted.json()["status"] == "scheduled"


def test_malicious_paths_never_serve_local_files(api: Api):
    # Multi-segment traversal never matches a route at all.
    for url in (
        f"{API}/assets/..%2F..%2F..%2Fetc%2Fpasswd",
        f"{API}/assets/%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        f"{API}/assets/%2Fetc%2Fpasswd",
        f"{API}/demos/..%2F..%2Fetc/rounds",
    ):
        response = api.client.get(url)
        assert response.status_code == 404, url
        assert "root:" not in response.text

    # Single-segment traversal does reach the handler and is refused there.
    for url in (f"{API}/assets/%2e%2e", f"{API}/assets/unknown-asset-id"):
        response = api.client.get(url)
        assert response.status_code == 404, url
        assert response.json()["code"] == "NOT_FOUND"
        assert "root:" not in response.text

    # Query values are percent-encoded by the client, so the server sees the
    # literal traversal text; it must never resolve to a file or fall back.
    generation_traversal = api.client.get(
        f"{API}/demos/{DEMO_ID}/rounds", params={"generation_id": "../../../../etc/passwd"}
    )
    assert generation_traversal.status_code in (400, 404)
    assert generation_traversal.json()["code"] in {"GENERATION_UNAVAILABLE", "INVALID_ARGUMENT"}
    assert "root:" not in generation_traversal.text

    replay_traversal = api.client.get(
        f"{API}/demos/{DEMO_ID}/replay",
        params={"generation_id": "../../../../etc/passwd", "round_id": 1},
    )
    assert replay_traversal.status_code in (400, 404)
    assert replay_traversal.json()["code"] in {"GENERATION_UNAVAILABLE", "INVALID_ARGUMENT"}
    assert "root:" not in replay_traversal.text


def test_oversized_window_is_rejected_with_a_typed_error(tmp_path):
    app = create_application(tmp_path)
    try:
        register_demo(app, DEMO_ID)
        manifest = commit_generation(app, DEMO_ID, map_name="inferno", tables=oversized_tables())
        with TestClient(create_app(app, manage_lifetime=False), base_url=BASE_URL) as client:
            api = Api(app=app, client=client, first=manifest, second=manifest)
            oversized = replay_request(
                api, manifest.generation_id, stride_ticks=1, start_tick=1000, end_tick=31000
            )
            assert oversized.status_code == 400
            assert oversized.json()["code"] == "WINDOW_TOO_LARGE"

            # The same generation still serves a bounded window.
            bounded = replay_request(
                api, manifest.generation_id, stride_ticks=8, start_tick=1000, end_tick=2000
            )
            assert bounded.status_code == 200
            assert len(bounded.json()["samples"]) == 504
    finally:
        app.close()

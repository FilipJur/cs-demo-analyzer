# Phase 1 — Gameplay Analytics Foundation & Identity Correctness

Status: implemented and verified on the retained Inferno demo. Builds on Phase 0 (`foundation-v1`, generation-pinned Parquet, SQLite catalog) without changing it.

## 1. Identity gate (mandatory first objective — closed)

Measured on the retained Inferno generation (`6ce06d39`, 1,581,200 state rows):

- 408,814 null-`player_id` rows (25.9%), **all** `health == 0`, armor 0, money 0, weapon null, velocity zero. **Zero alive-null rows.**
- Live-player coverage **100%** (1,141,438/1,141,438 alive rows identified); every round starts 10/10 alive-and-identified at freeze end.
- Mechanism: null rows are stationary corpse entities at death positions — 161/172 kills match a corpse position exactly; one corpse persisted 4,632 ticks (~72 s) from death through round end.
- 77,469 null rows fall between active rounds; the 265 all-unknown ticks are all outside active rounds.
- Events unaffected: shots/bomb 0 null actors; kills 0 null victims (1 null attacker = world kill); damages 0 null victims.
- Cause is upstream: raw `awpy snapshots()` emits these rows with `steamid: None, name: None`. Corpse-to-victim attribution would require position-joining, which the project forbids. No second parser introduced, no custom identity system.

Decision per the correction policy: **no correction, no reprocessing** — the recoverable-active-data condition is not met. Replay exclusion of null rows loses no live trajectories. Null rows are observable dead entities: counted in totals, excluded from live-player ops, never joined by position/name. `identity.coverage` / `live_identity_violations` encode this rule; 18 regression tests cover it (corpse counting, alive-null flagging, corpse-position non-join).

## 2. What was built

`backend/src/cs_demo_analyzer/analytics/` — reusable primitives over existing canonical data, no new storage:

| Module | Contents |
|---|---|
| `access.py` | `Generation` (pinned demo+generation+rounds+players), `GenerationPool.open/scan/read/query_many`; lazy scan with predicate/projection pushdown; 120,000-row materialization cap; typed errors (`NOT_FOUND`/`NOT_READY`/`GENERATION_UNAVAILABLE`/`ARTIFACT_INVALID`/`INVALID_ARGUMENT`/`WINDOW_TOO_LARGE`) |
| `identity.py` | `coverage` (whole generation or one round; `live_coverage` ratio, `None` when no alive rows), `live_identity_violations` (ticks with alive-null rows) |
| `temporal.py` | `state_at` (exact or nearest within max_gap, verbatim rows only), `player_interval` (stride grid + coalesced `missing_ranges`), `events_in`/`timeline` (merged kills/damages/shots/bomb), `events_around`, `event_window`, `round_of`, `round_window`, `tick_to_seconds`, `evidence_ref` (demo/generation/dataset/row/tick/round/players) |
| `spatial.py` | `dist2d`/`dist3d`/`speed`/`yaw_diff`/`displacement` (None on missing/non-finite), `pair_distance_over_time`, `nearby`, `time_within`. Hammer world units documented; no meters, no LOS, no nav |

Interpolation policy: verbatim rows only, never across deaths/rounds/gaps beyond the stated maximum; missing results explicit.

## 3. HTTP + UI

Seven thin routes under `/api/v1/demos/{demo_id}/analytics/` (`state`, `trajectory`, `events`, `event-window`, `coverage`, `distance`) plus `POST /api/v1/demos/multi/query` (≤20 selections, per-demo error capture, ops `coverage`/`events`). Handlers validate and delegate; no analytics logic in routes. OpenAPI + generated TS types resynced; UI types extended in `web/src/api/types.ts` (project convention: `Schemas[...]` aliases; `EvidenceRef` mirrored locally since no endpoint returns it).

UI: player inspector (state table, trajectory gaps, nearby events, event→replay jump) and event list, wired into the existing replay panel with +19 lines. Browser computes nothing; all numbers are API rows.

## 4. Verification

- Backend suite: **237 passed** (was 123; +114 analytics/API tests).
- Real demo via production code: coverage in 0.01 s (live 1.0, zero violations), `state_at` 4 ms, 98-event timeline 5 ms, 1,000-tick pair distances 18 ms, `time_within` over a full round 18 ms.
- Browser against the running app: inspector opened with full roster, event jump landed the replay on tick 2177, canvas/DOM ticks agreed, zero console errors.
- Cross-demo path (`query_many`) covered by tests; single local demo exists so multi-demo behavior on real data is untested.

## 5. Limits and non-goals (kept)

- Corpse rows carry stale death-pose yaw/pitch: present but not live orientation. Do not use for facing analysis.
- Known-dead identified rows (health 0, 30,948) and corpse rows are two complementary dead-state representations; neither is attributed across the boundary.
- POV/bot/overtime/multilevel fidelity still unverified (single GOTV recording).
- No visibility, nav, smoke, coaching, AI, DuckDB, or schema changes. `foundation-v1` untouched.

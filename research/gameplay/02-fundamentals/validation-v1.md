# Demo Validation — First Pass (de_train, local GOTV)

**Status:** validation, not research. Read-only parse of one local demo; output to
`/tmp/fund-validation` (repo untouched). Date: 2026-10-15. Profile:
`reconstruction-v1` (extended). Demo:
`match730_003847735914142892513_1770210822_191.dem` (144 MB), map de_train,
18 rounds, quality `partial`.

## V0 — Release-decay coast (FUND-P06 peer-delta check)

Method: monotonic-decrease runs from >200 u/s to <80 u/s within ≤60 ticks, all
players (n=945 runs; 913 crossed 34%).

- Total-run median **9 ticks** (p10 1, p90 23); to-34% median **7 ticks**. Mixed
  braking (includes active counter-strafe) — faster than pure-release computed
  ~13 to 34% / ~24–26 to zero (friction 5.2/stopspeed 80 via Memorin 2026-07-27,
  peer-slice computation), consistent with counter-strafe beating coast. Guide
  "1–2 vs ~10 frames" understates pure coast ~2.5×; SteamAnalyst "~88 u/s" is
  arithmetically wrong (0.34×215=73.1). 34% threshold upgraded to model-doc +
  lineage-measured (VScript accuracy model + 2015 DevinDTV/SlothSquadron 73/74
  sweep) — still not Valve-CS2-primary. `m_flTurningInaccuracy` noted as flick
  confound (peer slice; yaw-delta gating recommended).


## Extraction (backend `extract()`, ~5 s)

players 11 · rounds 18 · player_state 878,360 · player_state_ext 878,360 ·
kills 131 · damages 536 · shots 2,738 · bomb 93 · blinds 93 · smokes 41 ·
fires 28 · grenades 26,636 · item_events 835 · round_economy 36 ·
player_lifecycle 195. Tick-join shots→state: 2,738/2,738 (100%).

## V1 — Velocity-at-fire (FUND-P06)

Method: per-shot speed = |(vx,vy,vz)| from same-tick state row; first-of-burst =
gap >32 ticks (~0.5 s @64 Hz) since shooter's previous shot.

- All shots (n=2,738): stopped (≤1 u/s) **12.6%**; ≤73 u/s (≈34% of 215 rifle max)
  **55.9%**; median **58.8 u/s**; p90 240 / p99 263 / max 380 u/s.
- First-of-burst (n=710): stopped **13.7%**; ≤73 u/s **37.6%**; median **120.8 u/s**.

Interpretation (measured, n=1 demo — do not generalize): first-burst median EXCEEDS
all-shots median because opening shots happen on the move (entries/trades) while
mid-spray bullets land after planting. A naive "speed>0 at shot = error" detector
would flag ~86% of first shots — confirming FUND-P06's FP warning (LOW only if
velocity measured AND burst-aware; outcome-inferred = HIGH). Burst-aware gating
(first-of-burst + weapon-class threshold) is REQUIRED before any moving-fire verdict.
Top weapons: AK-47 432, Negev 253, M4A1-S 252, MP7 189, Glock 187.

## V2 — AWP scoped / noscope / hitgroup / reposition (FUND-A01/A02)

- AWP shots 52, AWP kills 19. `shots.scoped` TRUE fraction: **0/52** (all recorded
  unscoped-at-fire in extended table — needs cross-check vs `is_scoped` at tick;
  possible upstream `weapon_fire`-vs-scope-timing artifact, DO NOT conclude
  "never scoped" — flagged as parser-semantics open question).
- `kills.noscope`: 0/19 TRUE. Hitgroups: chest/head/right_arm observed, **zero leg
  hits** in sample — leg-shot failure mode present in schema, absent in this sample
  (expected: leg hits rarely kill; need `damages.hitgroup` non-fatal analysis).
- Repositioning (46 consecutive-shot pairs): stayed <50 u: 12; moved ≥300 u: 20.
  Short-gap pairs (≤300 ticks) show mixed behavior (10–355 u) — bolt-wait vs
  micro-adjust co-exist; long-gap pairs skew to large moves (round breaks aside).

## V3 — What this changes in the slice

1. FUND-P06's "LOW if velocity measured" now carries a measured caveat: LOW only
   with **burst-aware + weapon-class gating**; naive per-shot flag rate ~86% on
   first shots (n=1 demo).
2. FUND-A02's noscope/leg-shot detectors confirmed schema-present
   (`kills.noscope`, `hitgroup_name`) with zero positives in n=19 — detectors are
   buildable but need multi-demo baselines before any threshold.
3. RESOLVED by second demo (see V4): `shots.scoped` works (33/2561 TRUE) — demo 1's
   all-FALSE is genuine sample property, not parser bug. Trust with per-demo sanity
   rates.
4. Remaining: flash→peek timing (P10); repeek intervals (P07). Three more local
   demos untouched.

## V4 — Second demo (de_vertigo, 18 rounds, n=2,561 shots)

Same pipeline, reconstruction-v1, quality `partial`. Output to `/tmp/fund-validation-2`.
Demo: `match730_003847743468990365878_1602058667_274.dem` (150 MB).

- Velocity-at-fire: all-shots stopped **21.3%** (vs 12.6% demo 1), ≤73 u/s **62.0%**
  (vs 55.9%), median **40.9** (vs 58.8). First-of-burst (n=559): stopped **18.8%**
  (vs 13.7%), ≤73 **47.0%** (vs 37.6%), median **79.9** (vs 120.8). Direction
  corroborated (first-burst median > all-shots median, both demos); magnitudes differ
  by map/playstyle — per-cohort baselines required, never a global cutoff.
- AWP: 15 kills, **0 noscope** (0/34 combined); hitgroups chest 9 / stomach 2 /
  right_arm 2 (+1 unlisted row). Leg-hit kills in this demo: **6**; nonfatal
  `damages.hitgroup` leg/foot/thigh hits: **44** — leg-shot failure analysis fully
  computable from recorded fields, no inference.
- `shots.scoped` TRUE: **33/2561** (vs 0/2738 demo 1) — field works; see V3.3.

## V5 — Utility-combined peeks + repeek intervals (FUND-P10/P07, two demos)

- Flash→peek (thrower's own follow-up shot within 128 ticks / ~2 s of their blind
  event): demo 1 **30/93 (32%)**, demo 2 **6/49 (12%)**; median gap **69 / 62 ticks**
  (~1 s). Most blinds are NOT immediately peeked by the thrower — teammate peeks,
  mistimed swings, or defensive flashes dominate. Blind durations: median 1.34/1.02 s,
  p90 3.74/4.69 s (recorded `duration_seconds`, both demos).
- Repeek proxy (same-attacker consecutive-kill gaps ≤640 ticks / 10 s): demo 1:
  31 gaps, median 320 ticks; demo 2: 20 gaps, median 285. Fast (≤192 ticks / 3 s):
  9 + 6 = 15 candidate punish-vs-impatient windows across 261 kills (~6%).
  Position change within fast windows not yet joined — punish vs impatient repeek
  still needs the displacement join before any verdict.

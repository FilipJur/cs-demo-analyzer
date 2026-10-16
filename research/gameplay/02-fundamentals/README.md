# CS2 Individual Gameplay Fundamentals — Research Index

**Scope:** individual CS2 gameplay knowledge for future mistake analysis: execution mechanics,
fight decisions, utility, match fundamentals, skill progression.
Researched 2026-10-15/16. **Research only — no code, no thresholds, no detectors.**

**Status:** complete. Five required deliverables present, plus two appendices.
Prior work is built on, not redone (see "Relationship to prior work").

## Navigation

| File | Contents |
|---|---|
| `README.md` (this file) | Principles, key conclusions, contradictions, gaps |
| `mechanics.md` | Execution mechanics with evidence tiers + patch sensitivity |
| `common-mistakes.md` | Searchable patterns `FUND-001`–`FUND-045`, causes + exceptions + reviewer checks |
| `progression.md` | Stage descriptions, diagnostic protocol, intent-vs-outcome |
| `sources.md` | Annotated, verifiable bibliography for all four files |
| `weapon-data.md` (appendix) | Build-stamped per-weapon numbers: falloff, damage, RPM, ammo, speeds |
| `validation-v1.md` (appendix) | First demo validation pass (de_train GOTV, n=2,738 shots) |
| `concepts.md` (appendix) | Peek/angle/weapon concepts `FUND-P/R/W/A/X` with 9-point schema |

`common-mistakes.md` IDs are the canonical pattern IDs. Appendix `concepts.md` IDs
(`FUND-P01`, `FUND-A02`, …) are cross-referenced where they overlap, not duplicated.

## Fundamental principles

1. **Judge ex ante, never by outcome.** Score the decision against the information set at
   decision time. A correct play that fails is execution or variance, not a decision error.
   (Basis: Baron & Hershey 1988; Fischhoff 1975 — see `progression.md` §3.)
2. **Facts first, verdicts never bare.** Every finding must separate (1) directly observable
   error, (2) measured characteristic, (3) potential execution issue, (4) context-dependent
   decision, (5) unsupported attribution. Category 5 is never emitted as a mistake.
3. **Decision ≠ execution, per event.** A missed shot by a correct decision belongs in the
   mechanics bucket. No validated method separates them per-event — keep two findings.
4. **Habit = repetition × cross-outcome survival.** One demo event is never a habit.
   Flag only cohort-rare ∧ repeatedly-negative patterns (Leetify's "what repeatedly
   happened, not why").
5. **Condition on role and plan.** Entry, trader, lurker, anchor, AWPer are judged by
   different denominators. Demos contain no comms — verdicts without plan info are provisional.
6. **Compute, don't sloganize.** Range, damage, timing, and window claims come from the
   formula + build-stamped table, never from class folklore or CS:GO carryover.
7. **State the information set.** Every judgment lists what the player plausibly knew,
   what is demo-present vs demo-absent, and what was assumed.
8. **Patch-date-parameterize everything.** May-2024 (incendiary/M4A4/plant award), July-2025
   (CT shared income/incendiary spread), March-2026 (magazine discard), Sept-2025 (subtick
   shooting), Animgraph2 Apr-2026 all move constants. Never hardcode.

## Key conclusions

1. **Counter-strafing still matters in CS2.** Movement inaccuracy accrues past ~34% of max
   speed (Leetify definition + shared-model documentation); full-speed release takes ~13 ticks
   to the threshold. "Sub-tick removed counter-strafing" is a myth. (`mechanics.md` §1)
2. **Velocity-at-fire is the strongest demo-backed mechanical signal** — but only
   burst-aware and weapon-class-gated. Naive per-shot flagging hits ~86% of first shots in
   the validation demo. (`validation-v1.md` V1)
3. **Peeker's advantage is real but unquantified for CS2.** The only measured numbers (FDG 2024)
   are non-CS2 lab data and must not be ported. No per-duel millisecond claim may ship.
4. **Peek type is a purpose decision, not a skill ranking.** Info → jiggle; commit → wide;
   AWP-bait → shoulder. Blind wide into unknown AWP angles is the canonical punishable error;
   flagging correct aggression as "over-peek" is the canonical false positive (HIGH).
5. **AWP scope-settle timing is a five-voice dispute** (100 ms / 150–250 ms / +200 ms / ~0.3 s /
   ~1 s) — none shippable. Scoped-vs-unscoped *state* is demo-available; settle-at-fire is not.
6. **No universal HP threshold exists.** Any fixed "below X HP must…" rule is category (5).
   Post-damage play is judged by role alternative + utility + clock, never by cutoff.
7. **Trade windows are tool-relative, not universal.** awpy 3.0.0 = 5.25 s recovery;
   HLTV denial/failed-trade = 5 s; HLTV saved-teammate = 1 s readiness. Label every flag;
   always report opportunity → attempt → success, never success-rate alone.
8. **Held utility is not wasted utility.** Retake holds, eco nades, exit-over-stick are
   sanctioned counterexamples. End-of-round inventory alone never supports a verdict.
9. **Smoke is 18 s, incendiary ≠ molotov, plant-loss pays $600.** Three corrected engine
   facts (Farmskins "20 s" retracted 4:1; May-2024 incendiary nerf; $800→$600 award cut).
10. **Aim plateaus are structural, not motivational.** Practice quantity explains little at
    the top (Pluss 2021); motor learning saturates (Listman 2021); transfer from trainers
    is unproven (Yeh 2024 null). Aim-volume is the wrong default intervention.
11. **Tracking/target-switching has no CS2 evidence base** and must not ship as a mistake
    class until an annotated pro-demo study exists. Same for info-discipline detectors.
12. **Demos cannot show intent, comms, gaze, ping, or rendered frames.** Any reviewer that
    asserts these hallucinates by construction. (`mechanics.md` §10)

## Central reasoning rule

> For any observed action, ask: **"What was the player trying to accomplish with the
> information they plausibly had, and under which circumstances would this actually
> represent a mistake?"** Separate demo-inferable facts (positions, velocity, damage)
> from unavailable intent (info vs commit vs bait, calls, plans).

## Contradictions found (resolved or quarantined)

- **Wide peek vs AWPers.** "Wide best vs AWPers" applies only *after* bait/info, never blind.
- **Smoke duration.** 18 s (4 sources) retracted Farmskins 20 s. Use 18 s (18.5 max).
- **T plant-loss award.** $600 (Official May-2024), not $800. GuildOrder stale.
- **Deagle base damage.** Tradeit 53 vs Codex 63 — build-check before use; third voice
  (Mythras armored-head 191) supports the 53 family.
- **AWP settle ms.** Five-way dispute, none usable. Withhold.
- **"80% of pros use M4A1-S."** Unattributed survey claim — category (5) despite plausible direction.
- **CS2 recoil vs CS:GO.** Single-tester ~8–10% tighter — directional only, plus CS:GO
  pattern coordinates are invalid CS2 references regardless.

## Unresolved gaps

1. Per-weapon rangeModifier binary verification (spreadsheet-derived only).
2. Per-shot `shots.inaccuracy` vs per-tick `m_bIsScoped` cross-check
   (`shots.scoped` all-FALSE in validation sample — parser-semantics open question).
3. `damages.hitgroup` non-fatal leg-hit rate; flash→peek timing; repeek intervals;
   multi-demo velocity distributions (four local demos untouched).
4. Incendiary post-nerf exact duration/area (Official says "reduced", no value).
5. Annotated pro-demo study for tracking/switch errors + placement-proxy validation.
6. Measured peek exposure-duration distributions (no source gives peek ms).
7. Stage-transition quantitative markers; Stage-D verdict FP rates (comms absent).
8. Compiled `weapons.vdata_c` mining (real numbers live there, not in prefabs).

## Relationship to prior work (built on, not redone)

- `research/muse/D-mistakes.md` — 52-class taxonomy, fact/indicator/verdict split,
  smoke + information-set blockers, per-demo parser probing. This directory adds
  gameplay substance (mechanics values, decision doctrine, utility/match patterns),
  never a second taxonomy.
- `research/muse/G-coaching-eval.md` + `parts/g-coaching/` — outcome bias, aim-plateau
  evidence (Pluss/Listman/Yeh/Proteau), coach interview base (kassad/ash/zews/zonic/B1ad3/valens).
  Progression/diagnosis here defers where overlapping, contributes stage structure + checklists.
- `research/gameplay/01-modern-meta/`, `04-decision-evaluation/` — 9-point concept schema,
  trading opportunity→attempt→success, review methodology, slogan critiques.

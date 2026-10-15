# §7 — Mistake Taxonomy & Detection Feasibility Matrix

**Slice:** `D-mistakes` (MistakeTaxonomy) · **Date:** 2026-10-15 · **Status:** research only, no implementation.
**Scope:** mistake taxonomy across the five brief categories (positioning, decision-making, teamplay, mechanics, utility/economy), evidence required, demo-data requirements, library support, candidate algorithms, context-dependence, LLM need, false-positive risk, coach's assessment view, objective validatability, coaching value — plus a single consolidated feasibility matrix and ranked top-5/bottom-5.
**Non-goals:** longitudinal/cross-match methods (owned by `LongitudinalAnalysis`), fog-of-war reconstruction internals (owned by `DemoDataFogOfWar`), data acquisition/licensing strategy (owned by `AcquisitionAutomation`), model/architecture & cost (owned by `AIModelsArchCosts`), coaching-science & feedback efficacy (owned by `CoachingScienceEval`).

> **Note to Main (gap in the brief):** the workspace contained no brief document enumerating §7's "listed sub-items". The taxonomy below is a superset reconstructed from primary sources (HLTV/Leetify/Refrag/Scope published metric sets, the action-valuation literature, CS2 demo/schema inventories) and standard CS decomposition. If the brief has an explicit item list, map it onto the IDs here (POS/DEC/TM/MECH/UEC).

### Executive summary (10 lines)

1. **No published artefact — paper or product — outputs validated per-action CS2 "mistake" labels.** Every existing error-detection method (OSE, MOBA deviant-behaviour mining, StratIncon, generic sports LLM-feedback) needs either a **reference/norm model** or an **outcome-anchored value function**. The system must supply one of those, and must never present model-relative output as fact.
2. **52 candidate mistake classes** were decomposed across the five brief categories; **18 are demonstrably detectable today** from demo data alone (engine events / arithmetic), **15** are detectable as facts but not as verdicts, and **8** are speculative to infeasible.
3. The **feasibility ordering is epistemic, not qualitative**: tiered by how much modelling sits between the demo and the claim (engine truth → geometry+constants → cohort/value model → belief counterfactual).
4. **Decision quality ≠ outcome** is operationalised as T0 outcome-conditioned → T1 realised-state (WPA/Leetify/HLTV Round Swing) → T2 action-value/regret. T1 is the severity substrate; **T1 is not decision quality** (it still credits lucky execution and carries three documented attribution side-effects: save penalty, passive-play bias, zero-sum distortion).
5. The **only defensible automatic method** today is cohort/reference-relative: "cohort-rare ∧ repeatedly T1-negative", with bootstrap CIs, never per-event verdicts.
6. **Chess supplies the taxonomy template** (win%-loss severity bands + a separate error-type label) and the caveat that objective evaluation loss ≠ human-likely error (*Maia*).
7. **Biggest hard blocker: smoke.** awpy's LOS is smoke-blind by documentation, no open tool reconstructs post-hoc smoke occlusion, and the networked `m_VoxelFrameData` is extractable but its format is undocumented. Utility-smoke and smoke-dependent positioning verdicts are therefore unreliable *by construction* today.
8. **Second blocker: information set.** No voice comms, no gaze, no POV frames; visibility/audibility must be modelled, and Result is only approximate (Leetify's hitbox change moved Aim Rating ~+4). Every finding must state its assumed information set.
9. **LLM role is narration over structured claims** (evidence pointers, no free numerics, no new findings) — consistent with every credible pipeline and with the documented failure modes of LLM/VLM judges.
10. **Operational caution for the FACEIT user:** demos recorded from ~2026-07-10 use a new usercmd encoding (fixed in demoparser2 0.42.0, 2026-08-08); per-demo capability probing and parser pinning are mandatory for any mechanics metric.

---

## 0. How to read this document

### 0.1 Evidence grades

| Grade | Meaning | Test applied |
|---|---|---|
| **D — Demonstrated** | Shipped or reproducible today in an existing artifact (parser field, library function, published product metric/formula). Verified by me against a primary source. | "Can this be computed today by someone with the demo?" |
| **E — Experimental** | Working code or study prototype with measured results; small scale, single author/map, or unvalidated thresholds. | "Does working code exist, but without validation?" |
| **R — Research-supported** | Peer-reviewed / arXiv method exists that transfers to CS2 mistake *detection*, though not applied to it. | "Is there a defensible method, applied elsewhere?" |
| **P — Plausible-untested** | No implementation found; design is coherent but unvalidated. | "Could it be built? Nobody has shown it." |
| **I — Infeasible** | Not derivable from demo data (now or with any known method), or definitionally impossible. | "Is the required information absent?" |

Grades attach to **detection of the mistake class**, not to the general topic. A topic can be **D** as measurement and **I** as verdict.

### 0.2 The single most important distinction

For almost every item in this document there are three different claim strengths:

1. **Fact** — engine- or event-level, objectively recorded (e.g. "blinded a teammate for 2.3 s"). **D** almost always.
2. **Indicator** — a computed quantity with declared constants and approximations (e.g. "crosshair placement: 7.4° angular error at first visibility"). **D/E**, error bound increases.
3. **Verdict** — "this was a mistake". Requires an explicit counterfactual + information-set caveat. Almost always **P/R** and frequently **I**.

**Design implication (used throughout):** the system must emit **facts + explicitly-stated model counterfactuals**, never bare verdicts. This is also what the strongest commercial pipeline does: Leetify states it reports "what repeatedly happened", not "why" ([leetify.com/blog/leetify-stats-glossary](https://leetify.com/blog/leetify-stats-glossary/), page modified 2025-01-10); mLkoach ships 38 measures and **explicitly omits values it cannot measure rather than estimating them** ([mlkoach.com/en](https://mlkoach.com/en/), 2026).

### 0.3 What I verified myself vs delegated

Verified directly (read the primary page/source): WPA paper text and model results; OSE paper abstract + its data/limits (via scout extraction from the PDF, flagged below where secondary); HLTV Rating 3.0 + Attributes articles; HLTV ToS text; awpy `visibility`/`map_control` docs; CS2 `CSmokeGrenadeProjectile` schema fields; demoparser2 issue #340 and #345/#321 references; Leetify utility-rating formula page; `cs2-evalbar` README (features + reported log-loss); JumpThrow/counterstrikestats aim-metric definitions; `awpy` `VisibilityChecker` limits; peeker's-advantage FDG 2024 numbers.

Delegated to four read-only scouts (all sources URL+date, primary-first): `/tmp`-verified library/field inventories (mechanisms), utility/economy/teamplay literature, tools/LLM/dataset/licensing. Items I could not confirm from a primary page are marked **[unverified]** or **[secondary-sourced]** and listed in §9.1.

---

## 1. Governing principle: decision quality is independent of outcome

### 1.1 The trap, stated precisely

**Outcome conditioning** = any label, weight, or ranking that depends on the final round or match result (win/loss, K/D in wins, "clutches won", rating gained because the team won). It is a trap because:

* The psychological effect is well documented outside esports: evaluators rate the **same decision** more favourably when they know it produced a good outcome, even holding the decision-maker's information fixed — **outcome bias** (Baron & Hershey, *JPSP* 54(4):569–579, 1988, [doi](https://doi.org/10.1037/0022-3514.54.4.569)).
* It is measurable inside CS: HLTV's own worked example shows EliGE's 133 ADR / 23-frag game scoring **2.06** under Rating 2.1 and **1.40** under 3.0 once 12 of 23 kills are revealed to be anti-eco/anti-force — i.e. raw outcome counting rewarded kills that were, contextually, near-worthless ([hltv.org/news/42485](https://www.hltv.org/news/42485/introducing-rating-30), 2025-08-20).
* Industry models avoid the crudest form: WPA values an action as a change in estimated win probability, not as a win/loss label ([arXiv:2011.01324](https://arxiv.org/abs/2011.01324), 2020-11-04). **Precise reading (important — a common misreading):** WPA's "*independence*" claim is about **non-correlation with other metrics** (KDR correlation 0.73 vs Rating 2.0's 0.93), and the paper's *stability* claim is month-to-month correlation (WPA 0.40 vs KDR 0.38, ADR 0.24, KAST 0.30, Rating 2.0 0.29) under the Franks et al. meta-analytics criteria. The paper **never claims outcome-independence**, and its model is *trained on the round outcome as the target*. Do not repeat the misreading in design docs.

### 1.1b Two distinct traps (keep them separate)

| Trap | Mechanism | Documented evidence |
|---|---|---|
| **T1 — Outcome bias in judgment/valuation** | Evaluators (human or model) rate the same decision better when they know it succeeded; models that learn on outcomes conflate *execution quality* with *intent* | Baron & Hershey 1988; **Paul, Klemp & Memmert, MLSA25 (KU Leuven, 2025)** show original VAEP/xT "rely on outcome-driven learning, which conflates execution quality with tactical intent" and construct **xSuccess** (completion probability) + `xValue_adj = f(VAEP ⊥ P_success, P_success)` on 3.6 M StatsBomb actions, which removes the systematic success/failure separation visible in raw VAEP |
| **T2 — Statistical leakage / invalid evaluation** | Adjacent play-by-play states are massively correlated; random (snapshot-level) splits leak; post-match statistics used as features | WPA admits correlated adjacent states; **Brill, Yurko & Wyner** ([arXiv:2406.16171](https://arxiv.org/abs/2406.16171), v5 2025-08-20, accepted JQAS) quantify that dependence "substantially inflates the bias and variance of estimators and lowers the effective sample size"; **Davis et al.**, *Machine Learning* 113:6977–7010 (2024-07-17) on partitioning under dependence; `cs2-evalbar` and TaiZo1 both implement match-grouped/temporal splits and a D−1 cutoff for external stats |

**Where outcome-conditioning genuinely bites a coaching product (all first-party admissions):** saves/survivorship (HLTV 2.1 punished saves because "as teams saved more … the averages … diverted", [news/40051](https://www.hltv.org/news/40051), 2024-10-14); zero-sum attribution that favours passive play (HLTV 3.0: "Round Swing slightly favors more passive players"; Leetify re-weighting to stop "baiters" being rewarded); **model-relative "optimal"** (OSE's optimum is the argmax of a model that omits opponent/team identity — see §3.5); **circular validation** (OSE ↔ round win rate r = −0.45 uses quantities derived from the same model); and **metric-vs-community validity** (HLTV re-weighted Round Swing within ~2 months of launch, then again 2026-10-01).

**Also carry forward (from the fourth scout):** no published CS/CS2 work outputs validated per-action *mistake* labels. The closest existing error-detection methods are (a) OSE, (b) MOBA **deviant-behaviour detection** against a reference transition graph built from high-skill traces ([DSAA 2016](https://perso.liris.cnrs.fr/jean-francois.boulicaut/dsaa2016.pdf)), (c) **StratIncon** strategy-inconsistency detector ([arXiv:2503.09060](https://arxiv.org/abs/2503.09060), IUI'25), (d) a conceptual 5-level **EPS** diagnostic framework separating "mental errors" (strategy/tactics) from "physical slips" (motor execution) ([arXiv:2608.09156](https://arxiv.org/abs/2608.09156), 2026-08, unvalidated), and (e) tactical-label GNNs that explicitly **cannot** separate "failed execution of a good tactic" from "poor tactical choice" (Kirna, U. Twente TScIT 43, 2025-07-04). Every one of them requires either a **reference/norm model** or an **outcome-anchored value function**. Fully automatic mistake detection *without* one is infeasible per the located evidence.

### 1.2 Three tiers of valuation (the core analytical frame for this system)

| Tier | Definition | Examples | Independent of final round result? | Independent of luck *within* the action? |
|---|---|---|---|---|
| **T0 Outcome-conditioned** | Label depends on final result | win rate, K/D, rounds won, "clutch %", MVP votes | ❌ | ❌ |
| **T1 Realized-state (result-independent)** | Value = Ŷ(s_{t+1}) − Ŷ(s_t), the estimated win-probability change across the realised state transition. **Not conditioned on the result label, but the model is outcome-trained and the successor state is the one that actually happened** | WPA, Leetify Rating, HLTV Round Swing, FACEIT Round Swing | ✅ | ❌ (a 15 % spray that connects is still credited as a good *state* change) |
| **T2 Action-value / counterfactual** | Q(s,a) = E[Ŷ | s, a]; error = regret = max_{a′}Q(s,a′) − Q(s,a) | (no CS2 implementation exists) | ✅ | partially (expectation over execution) |

Consequences the system must encode:

* **T1 is the floor, not the goal.** Tier-1 metrics still credit lucky execution. They are the right substrate for *severity*, not for *decision quality*. HLTV itself ships 3.0's Round Swing as an approximation with admitted drawbacks ("a feature, not a bug" that multi-kills diminish; early rounds under-weighted) and states it "should not be treated as a perfect measure of impact" ([hltv.org/news/42485](https://www.hltv.org/news/42485/introducing-rating-30)).
* **T1 carries three documented attribution side-effects** that must be logged with every finding: (i) **saves/survivorship** — zero-sum credit means "saving players are punished the same as if they had lost that clutch" (HLTV 3.0), and Leetify states plainly it "considers rounds in isolation. There is no consideration to what the current scoreline is" — so multi-round economy plans are systematically penalised; (ii) **passive-play preference** — HLTV: Round Swing "slightly favors more passive players"; (iii) **zero-sum team distortion** — a teammate's gain is another's loss even when attribution is genuinely ambiguous (WPA's own limitation: "if the T side plants the bomb and there are three CT remaining, it is not immediately obvious how the loss in win probability should be divided").
* **T2-lite is the practical target.** Full counterfactual action models need a simulator or a learned action-value model. What *is* buildable now from demos: a **reference-policy comparison** (the MOBA deviant-behaviour method) — how often do comparable players (same cohort, same state bucket) choose action *a*, and what is the typical T1 value of that state bucket's chosen actions? A finding is defensible when a behaviour is both **cohort-rare** and **T1-negative across repeated instances**, never from a single round.
* **Decompose luck explicitly.** Observed outcome = decision + execution + variance. The transferable construct is the soccer literature's separation of **intention vs execution value** (I-VAEP/O-VAEP, Mendes-Neves et al., [arXiv:2209.03882](https://arxiv.org/abs/2209.03882), 2022) and Paul et al.'s **completion-probability × reward** split (xSuccess + adjusted VAEP). Only cross-sample aggregation separates noise from habit, which is why cross-match longitudinal methods (sibling slice) are load-bearing here: per-round mistake lists are noisy; per-habit distributions are not.
* **Validate the indicator and the model separately, with calibration and uncertainty** (Davis et al. 2024; Franks et al. 2016 criteria: stability / discrimination / independence). Win-probability estimators on dependent play-by-play data are **high-variance** (Brill, Yurko & Wyner, arXiv:2406.16171, accepted JQAS 2025) — severity bands need bootstrap CIs, not point estimates.

### 1.3 Chess is the working analogy (and its caveats)

The most mature "mistake classifier" in games is chess, and its design is directly transferable:

* **Lichess** converts Stockfish centipawns to win probability (`Win% = 50 + 50·(2/(1+e^(−0.00368208·cp)) − 1)`) and labels by **winning-chance loss**: inaccuracy ≈10–20 pp, mistake ≈20–30 pp, blunder ≥30 pp; game accuracy is a **volatility-weighted harmonic mean** so one big error dominates ([lichess.org/page/accuracy](https://lichess.org/page/accuracy); [lila `AccuracyPercent.scala`](https://github.com/lichess-org/lila/blob/master/modules/analyse/src/main/AccuracyPercent.scala)).
* **Chess.com Classification V2** uses **Expected Points lost** bands (inaccuracy 0.05–0.10, mistake 0.10–0.20, blunder >0.20) ([support.chess.com](https://support.chess.com/en/articles/8572705-how-are-moves-classified-what-is-a-blunder-or-brilliant-etc)).
* **Objective ≠ human-likely.** *Maia* models what a player *of a given rating* is likely to play and predicts the blunders they will actually make (McIlroy-Young et al., [arXiv:2006.01855](https://arxiv.org/abs/2006.01855), 2020) — the exact split this system needs: **severity band (objective ΔP) vs error-type label (human/intent-flavoured)**.
* **Caveats that transfer verbatim to CS2:** engine labels measure *evaluation loss*, not *difficulty*; thresholds are platform-specific and not comparable; some flagged items are stylistic (chess: opening book moves). Lichess states the scoring is not comparable across platforms.

**CS2 transfer:** label each decision by **Δ round-win probability in percentage points** with bands (minor/major/critical), and **separately** assign an error *type* (isolation, unused utility, economy, timing, mechanic). This mirrors chess's severity-vs-type split and is what the action-valuation literature (WPA, THGNN) already provides for CS.

### 1.4 Rules the detection layer must obey (encodable as asserts)

1. **No label may read the final round/match result.** Features are causal (state at t only); targets may use outcomes, labels may not.
2. **No verdict without a counterfactual + information-set qualifier.** "You had X info; you chose Y; comparable players choose Z; state value changed by W" — never "you threw".
3. **Execution ≠ decision.** A missed shot by a correct decision belongs in the mechanics bucket, not the decision bucket. The literature has no validated method to separate them per-event (**I**, see MECH-notes §3.4); the system must keep them as separate findings, not merge them into one "mistake".
4. **Availability check.** An alternative action must have been *physically reachable* — use nav-graph travel time (awpy `NavMesh.find_path`, directional weighting) to compute whether the "better" choice was even possible before the window closed.
5. **Report per-habit, not per-event.** Aggregate severity over ≥N instances before surfacing (and never below a sample floor).
6. **Precision over recall, and never silently third-party.** A coach-flavoured tool that flags 20 mistakes/round is unusable; cap findings and rank by expected value.

---

## 2. Data substrate: what feasibility rests on

### 2.1 Parsers (all three are viable; pick by language + API shape)

| Library | Language | Status / licence | Notes relevant to mistake detection |
|---|---|---|---|
| **awpy 2.x** | Python | MIT; awpy 2.0 released 2025-03-03, backend = demoparser2 Rust core ([pypi](https://pypi.org/project/awpy/)) | High-level datasets: `kills` (with `thrusmoke`, trade flags), `damages`, `blinds`, `grenades`, `smokes`, `fires`, `shots`, `item_events`, `round_economy`, `snapshots`, `ticks`; `Nav`/`NavMesh` pathfinding; `VisibilityChecker`; `map_control`. Best fit for this system. |
| **demoparser2** | Python/JS (Rust core) | Active; ~733★ ([repo](https://github.com/LaihoE/demoparser)) | Fine-grained per-tick property queries (`parse_ticks`), arbitrary prop discovery (`list_updated_fields()`), `parse_event`, `parse_grenades(extra=[...])`. Needed for fields awpy does not surface. |
| **demoinfocs-golang v5** | Go | Maintained; v5.0.5 2025-12-05, v5.2.0 (~30–35 % faster), v6.0.0-alpha adds full CS2 user-command decoding ([releases](https://github.com/markus-wa/demoinfocs-golang/releases)) | Event-callback model; good if the pipeline is Go. |

**Parser fragility is a first-class design constraint, not an edge case:** Valve patches have broken parsing wholesale (demoparser issue #321, patch 14152 → `EntityNotFound` on all `parse_event`/`parse_ticks`, opened 2026-04-21, open), and FACEIT changed user-command encoding on ~2026-07-10 (issue #340, see §2.4). Pin versions, keep a regression corpus, version findings with (parser version, CS2 build).

### 2.2 Fields and events that exist (the feasibility floor)

Per-tick (verified in demoparser2 README/awpy docs, 2026-10-15):

* **Motion/pose:** `X/Y/Z`, `velocity` / `velocity_X/Y/Z`, `max_speed` (`m_flMaxspeed`), **`velo_modifier` (`m_flVelocityModifier` — the engine's own movement-accuracy factor)**, `ground_accel_linear_frac_last_time`, `duck_amount`, `is_airborne`, `is_walking`, `is_strafing`, `fall_velo`, `stamina`.
* **View/aim:** `yaw`/`pitch` = `m_angEyeAngles[0..1]`; **`aim_punch_angle` / `aim_punch_angle_vel`** (recoil kick — required to recover the *true* crosshair); `is_scoped`, `zoom_lvl`; **`accuracy_penalty` (`m_fAccuracyPenalty`)**, `i_recoil_idx`/`fl_recoil_idx`, `shots_fired`, `fire_seq_start_time`.
* **Weapon:** `active_weapon_name` (+item def index), `active_weapon_ammo`, `total_ammo_left`, `is_in_reload`, `next_attack_time`, `num_empty_attacks`.
* **Perception** (server truth, with caveats): `spotted` / `approximate_spotted_by` (`m_bSpottedByMask` — radar visibility bitmask; **Leetify abandoned it**: 0–500 ms lag, stale "shadows", fails before AWP shots, [blog](https://leetify.com/blog/enemy-actually-spotted/, 2020-10-04)), `flash_duration`, `flash_max_alpha`, `direction_last_injury`, `time_last_injury`.
* **Economy/state:** `health`, `armor`, `helmet`, `money`, `equipment_value`, per-item inventory counts, `is_defusing`, `has_bomb`, `is_controlling_bot`.
* **Buttons / inputs:** `FORWARD/LEFT/RIGHT/BACK/FIRE/RIGHTCLICK/RELOAD/WALK/ZOOM/...`, `buttons` (`m_nButtonDownMaskPrev`); **`usercmd_*`** (`usercmd_mouse_dx/dy`, `usercmd_buttonstate_1..3`, `usercmd_forward_move`, `usercmd_left_move`, `usercmd_subtick_moves`) — closest thing to raw input, **fragile** (§2.4).

Events/datasets:

* `weapon_fire` / awpy `shots` (per-shot x,y,z,pitch,yaw,weapon,scoped,inaccuracy,ammo).
* **`fire_bullets`** ← `CMsgTeFireBullets` (verified in demoparser source): origin+angles, `weapon_id`, `attack_type`, **`seed`, `inaccuracy`, `recoil_index`, `spread`**, `num_bullets_remaining`, `player_inair`, `player_scoped`.
* **`player_bullet_hit`**: attacker/victim slot, victim position, `hit_group`, `damage`, `penetration_count`, `is_kill`.
* `player_hurt` (attacker/victim/dmg_health/dmg_armor/hitgroup/weapon), `player_death`, `round_start/end`, `bomb_*`, `flashbang_detonate`, `smokegrenade_*`, `inferno_*`, `player_blind` (`userid`, `attacker`, **`blind_duration`**), **`player_footstep`** (**verified valid CS2 event names** in `mod.gameevents`; availability is per-demo — `list_game_events()` must be checked).
* awpy `kills.thrusmoke` — **engine ground truth** that a kill passed through smoke; `blinds` (reconstructed, includes self/team flashes); awpy trade flags (see §3.3).

**Correction to a common assumption (important):** `bullet_impact` is *not* exposed by demoparser2 (scout verified by grep of `game_events.rs`; only `fire_bullets`/`player_bullet_hit` exist). Bullet landing points on world geometry are therefore **not directly available**; where-a-miss-went must either be approximated from `fire_bullets` (origin+angles+`seed`+`inaccuracy`+`spread`, which permits deterministic recomputation *only if the weapon spread RNG is reimplemented* — **P**) or treated as unavailable (**I**).

### 2.3 Fog-of-war primitives available today (and their documented limits)

| Primitive | What it gives | Documented limits (verbatim substance) |
|---|---|---|
| `awpy.VisibilityChecker` | Segment-vs-static-collision-mesh BVH raycast → `is_visible` / `is_occluded` | "**Does not model smokes, moving doors, or bullet penetration**"; demo positions are **feet**, not eye positions ([docs](https://awpy.readthedocs.io/en/stable/visibility.html)) |
| `awpy` `map_control` | Per-nav-area labels ct/t/contested/neutral; `raycast` (all directions) / `vision` (horizontal FOV, default 90°) / `reachability` (travel distance) | "Vision **ignores pitch**… These models **estimate control, not exact player perception**"; smoke modelled as a **sphere** (`smoke_radius` 144 HU, `smoke_height` 60 HU); fires block paths (radius 150); blinded players (`flash_threshold` 1.0) project no vision ([docs](https://awpy.readthedocs.io/en/stable/map_control.html)) |
| Smokes | awpy `smokes` = `start_tick,end_tick,thrower,x,y,z` — **one row per cloud, no volume/radius/density** | Real CS2 smokes are volumetric with bullet/HE holes; sphere approximation is the only open-tool option |
| **Smoke voxels** | Server entity `CSmokeGrenadeProjectile` carries **`m_VoxelFrameData` (`CNetworkUtlVectorBase<uint8>`), `m_nVoxelFrameDataSize`, `m_nVoxelUpdate`** — **extractable** from demos via `demoparser2.parse_grenades(extra=[...])` (verified against the CS2 schema dump and a working public script) | The **byte format is not publicly documented**; the known public script only measures length/entropy/diffs and explicitly does not decode the grid. Valve has published no format → occlusion-from-voxels is **P**, not D |
| In-engine smoke truth | `XBribo/CS2-Bot-Vision` (Metamod plugin, AGPL) evaluates smoke **density** + HE holes (r 250) + bullet holes (r 20 / shotgun 80) before bot LOS; `smoke.mode 0/1` (volumetric vs stock ball), `density_threshold 0.23` | **Demonstrated in-engine, server-side — not applicable post-hoc to a demo** |
| Offline reconstruction attempt | `NC1107/cs2-smoke-solver` (DESIGN.md, **Status: Draft**): VRF physics hulls + BFS voxel flood-fill + density ray-march; targets IoU ≥0.85 and 90 % recall of known lineups; **success metrics not reported as met** | **E (incomplete)** |
| Sound | `player_footstep` events + `weapon_fire` + positions → distance-based audibility proxy | No audio occlusion/mix model in any open tool; community-measured footstep earshot ≈800–1 100 units (**non-primary**); Valve only patched jump-landing sound max distance (2023-11-08 change notes) |

**Bottom line for fog-of-war:** a *geometric* information-state model (static LOS + FOV + flash + sphere-smoke) is available **today (D)**; a *perceptual* model (volumetric smoke, sound occlusion, what was on the player's screen, teammate comms) is **not**. Every decision-quality finding must therefore be conditioned on a *modelled* information set and labelled as such. This is the single biggest source of false positives in the whole matrix.

### 2.4 Hard gaps (near-infeasible from demo alone)

1. **Voice comms** — never in GOTV/HLTV/FACEIT demos (awpy exposes only text `chat`). Comms research exists and is inapplicable ([JSEP 2025, doi 10.1123/jsep.2024-0343]; Rusk et al. 2023). Coordination/communication mistakes are **I** as *detection*, high value if the user records their own comms.
2. **Rendered frames / gaze** — no POV video in a demo; gaze/fixation requires eye-tracking (external to demo). Aim kinematics research (Bediou et al. 2022, [Frontiers](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2022.979293/full)) used 120 Hz recorded view orientation in a controlled task, not demos.
3. **True reaction time** — needs input/click timestamps + attention state; tick quantisation (official CS2 = **64 tick** → 15.6 ms/tick) plus replay-timing caveats make this **I**. Leetify states outright that TTD "is **NOT** reaction time" ([glossary](https://leetify.com/blog/leetify-stats-glossary/)).
4. **Replay fidelity caveat (new):** Valve shipped **TrueView** in the CS2 update of **2025-11-04** because legacy playback ignored the observed player's latency/client prediction; Valve states TrueView still does not reconstruct rendered-frame timing (recoil/muzzle flash can be 1–2 frames late) and the click frame is accurate only to the nearest playback frame ([Steam news](https://store.steampowered.com/news/posts/?appids=730&enddate=1762988292)). "What the player saw" is therefore server-truth *approximately*.
5. **Hitbox/bone geometry absent** — crosshair-to-target must assume a player volume. Leetify's history is the best public error estimate: they replaced the game's `spotted` event with their own raycaster, then on **2026-08-11** replaced an 8-point box with human-shaped hitboxes, which **shifted Aim Rating by ≈+4 for many users and forced benchmark renormalisation** ([blog](https://leetify.com/blog/aim-stat-calculation-hitboxes-improved/)).
6. **User-command fragility (FACEIT-relevant):** FACEIT demos recorded from ~**2026-07-10** store commands in `CMsgServerUserCmd.delta_data`; parsers decoding only `data` silently return stale/defaulted input (measured: 143,975 vs 217 value changes on an older vs affected demo, issue [#340](https://github.com/LaihoE/demoparser/issues/340), 2026-07-11, closed; decoder merged in demoparser2 0.42.0, 2026-08-08). `usercmd_subtick_moves` is silently dropped by `parse_ticks()` (issue [#345](https://github.com/LaihoE/demoparser/issues/345), 2026-08-10, open). **Any mouse-level or button-level mechanics metric must be validated per demo source before use.**
7. **Reconstructed-ish bookkeeping:** awpy `damages.health_pre` is *estimated* (post-hit + damage, capped at 100 — "not recorded pre-hit values"); `blinds` are reconstructed from flash-duration increases and are empty without `flashbang_detonate` events; trades use a reconstructed **5.25 s** window. Treat `parse_ticks()` output as parsed observations, not a dense series.
8. **Friendly fire specifics:** competitive/Premier config has `mp_friendlyfire 1` with reduced multipliers (`ff_damage_reduction_bullets 0.33`, `…_grenade 0.85`, `…_other 0.4`) → teammate hits do produce `player_hurt`; in FF-off modes teammate-directed fire leaves **no** hit event and must be inferred from `fire_bullets` angles only.
9. **Intent, role, team plan, coaching context** — absent; stated as a hard limit by Leetify itself and by the literature (§9).

### 2.5 Baseline / cohort data

* **ESTA** — 1,558 pro CS:GO demos, 41,782 rounds, 8.6 M actions, 7.9 M frames, 417 k trajectories ([arXiv:2209.09861](https://arxiv.org/abs/2209.09861), 2022-09-20). **Stale:** requires awpy 1.3.1, not awpy 2.x.
* **X-Ego-CS** — CS2: 101 matches / 2,168 rounds / 21,680 ego-clips / 279.4 h synced first-person video + **64 Hz tick-level actions incl. mouse dx/dy**, video↔tick offsets, raw `.dem`; MIT licence tag; **v2 Sep 2026** ([HF: wangyz1999/X-EGO-CS](https://huggingface.co/datasets/wangyz1999/X-EGO-CS), [arXiv:2510.19150](https://arxiv.org/abs/2510.19150)). Source is FACEIT matches → provenance caveat for redistribution (see sibling acquisition slice).
* **awpy-data** — MIT scripts, but packaged Valve map assets remain Valve property ([repo](https://github.com/pnxenopoulos/awpy-data)).
* **No standard CS2 tactical embedding exists.** Nearest analogues: `player2vec` behaviour embeddings ([arXiv:2404.04234](https://arxiv.org/abs/2404.04234)) and V-JEPA2 video latents. Cohort comparison is done today via win-probability/action-value models, not vector similarity.

### 2.6 Win-probability / action-value models (the severity substrate)

| Model | Task | Reported performance | Limits |
|---|---|---|---|
| WPA / Xenopoulos et al. 2020 ([arXiv:2011.01324](https://arxiv.org/abs/2011.01324)) | P(CT wins round \| state); value actions by ΔP | **8 features only**: map, ticks since round start, round-start equipment value, players remaining, total HP remaining, bomb planted, plant site, team bombsite distance (nav-mesh A*, not Euclidean). XGBoost: **AUC 0.7913, log loss 0.5353, Brier 0.1842** on 18 M test states (55 M train, 4,682 LAN demos; states sampled per footstep/damage/bomb event). Feature importance: equipment ≫ HP > players > … map 5th | Only **damage events** valued (plant/defuse/movement attribution explicitly unsolved in the paper); CS:GO/MR15; assumes analysed teams have **similar skill**; adjacent states highly correlated (self-acknowledged) |
| HLTV Round Swing (Rating 3.0, 2025-08-20) | Per-kill ΔP(round win) with map/side/economy/plant/alive context, credit split by damage share/flash assist/trade | Elite ≈ +3.7–3.8 % per round season-long; mortals ±1.5 % | Diminishing multi-kill returns; undervalues early round (opening ≈ +20 % vs 1v1 clutch ≈ +50 %); "not a complete player-value model"; HLTV later rebalanced weights ([news/43047](https://www.hltv.org/news/43047/rating-30-adjustments-go-live)) |
| Leetify Rating (2024→2026) | Round impact from a win-prob model (economy, alive players, prior kill, result, saves); 35/30/15/20 kill-credit split | Published as zero-sum per match; recalibrated on CS2 pro data 2024-11 | Formula for Positioning unpublished; API since 2026-01-23 returns data only for Leetify-registered users |
| THGNN / Szmida & Toka (MIT Sloan SSAC 2026) | Temporal heterogeneous GNN over player+map graph; SHAP attribution of Δ win-prob to actions | **AUC 0.8549, F1 0.7463** | Inferno only, 114 matches (Oct 2023–Sep 2024) |
| `cs2-evalbar` (open source, 2026) | Round-win probability from CS2 demos, local-first (Inferno only) | Keeper 5-seed **log loss 0.534 ± 0.012**; phase accuracy 0.60 (<15 s) / 0.68 (30–60 s) / 0.88 (≥90 s); estimated irreducible log loss ≈0.47–0.48 | 0★, single author, single map; **player-skill features did not improve `ct_win`; raw aim, skill, bomb-timer, event, utility and sound feature groups contributed ≈0 permutation importance** |
| Community CS2 models | In-round winner prediction | XGBoost 77.85 % / log loss 0.4272 on 764 pro maps (bachelor thesis, [vskp.vse.cz/100656](https://vskp.vse.cz/100656)); logistic regression 61.8–62.6 % (normal rounds) / ~80 % (post-pistol) / ~50 % (pistol) ([GitHub TaiZo1](https://github.com/TaiZo1/cs2-win-prediction)); MLP 95.75 % claim is leakage-prone mid-round snapshots ([GitHub](https://github.com/ratulsarker/CS2RoundPrediction)) | **Split by match/demo, never by snapshot**; report calibration (Brier/ECE), not accuracy |

**Two negative results that must shape the design:**

1. `cs2-evalbar`'s own ablation: **utility- and event-family features contributed ≈0** to round-win prediction. Utility value is not recoverable from round-outcome labels alone → utility findings need their own local causal tests (did the smoke change LOS? did the flash precede the kill?), not ΔP(win).
2. Szmida & Toka's counter-smoke example shows a defensible smoke yielding **zero net WP change** — a reminder that "no value" ≠ "misplay".

**Model-quality requirement for this system:** a mistake detector's severity bands inherit the win-probability model's calibration error. Report **Brier/ECE per round phase and per map**, and suppress findings in phases where calibration is poor (early round, pistol rounds).

**Two cautions when reading that table.** (1) **The published numbers are not comparable** — different maps, splits, snapshot densities and label rates; THGNN's log loss 0.4587, evalbar's 0.534, TaiZo1's AUC 0.860 and WPA's 0.5353 must never be ranked against each other. (2) **THGNN feeds prior-year HLTV Rating 2.1 / KAST / Impact as player features** — a design choice that disqualifies it as an independent critic of those ratings, and a reminder that any baseline model must quarantine third-party ratings from its inputs. Also note FACEIT shipped its own **Round Swing** (support article, 2026-04-29) that explicitly does not affect Elo, and HLTV's 3.0 update of **2026-10-01** now gives *no* swing for kills when the bomb is unstoppable (<10 s, or <5 s with kit) — i.e. exit frags are excluded by the industry already.

---

## 3. Taxonomy and per-item detection feasibility

### 3.0 Framework

**Two axes, never merged.** (1) **Severity** = Δ round-win probability in percentage points, banded chess-style (convention to calibrate: minor < 10 pp, major 10–25 pp, critical > 25 pp). (2) **Type** = a named error class (the ID column below). A finding is `(type, severity, evidence pointer, confidence, caveats)`.

**Level mapping (adapting the conceptual EPS framework, [arXiv:2608.09156](https://arxiv.org/abs/2608.09156)):** strategy (buy/plan) → tactics (execute/setup/rotation) → tasks (trade, crossfire, coverage) → actions (peek, swing, throw) → operations (mechanics/inputs). The framework's key claim transfers directly: *mental errors* (wrong plan/intent) and *physical slips* (motor execution failure) must be diagnosed separately, because misattribution obscures the cause.

**Column legend.** `Grade` = evidence grade for *detecting this class* (§0.1). `Evidence` = observable facts that constitute the candidate error. `Lib` = library support (`awpy:nav|vis|mc|events|stats`, `dp2:ticks|events|grenades`, `none`). `Algo` = candidate algorithm; **all constants are conventions and must be declared with the finding**. `CD` = context-dependence. `LLM` = none / terse (narrate) / essential (hypothesis-forming). `FP` = false-positive risk. `OBJ` = objective validatability. `Value` = coaching value at ~2000 FACEIT.

> **Universal caveat:** every "mistake" claim inherits §2.4's information gaps (no comms, no gaze, approximate visibility, approximate smoke). Findings must state which information set they assumed.

### 3.1 Positioning & spatial

| ID | Grade | Evidence | Data | Lib | Algo (constants declared) | CD | LLM | FP | Coach view | OBJ | Value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **POS1** Isolation death (untradeable) | D/E | Player dies; no living teammate could reach LOS of the killer within the trade window | ticks, kills, nav mesh, LOS | awpy:nav,vis,events | For each death: compute per-teammate nav-ETA (A* on nav mesh) + LOS to killer position; if min(ETA) > window (5.25 s awpy convention) → "isolated death" | High | Terse | Med-High | Replay t−3 s…death with teammate ETAs drawn | Y-with-model (window) | High |
| **POS2** Overextension / no-support advance | E | Advance creates large nav-distance to nearest teammate while enemy count unknown; death to ≥2 attackers from distinct angles | ticks, kills, LOS, positions | awpy:nav,events | Support-distance percentile vs same-state cohort + multi-attacker death + weapon disadvantage | High | Terse | High | Advance replay with distances | Model-relative | Med-High |
| **POS3** Predictable re-peek | D | Same nav area/angle engaged ≥2× within N s; player was visible to enemy before re-peek; hit/die on re-peek | ticks (yaw/pos), wounds, LOS | awpy:vis,events | Repeat-engagement detector (same area id within 30 s) + visibility-before-peek flag; compare survival of re-peeks vs matched first-peeks | Med | Terse | Med | Both peeks side by side | Y-with-model | High |
| **POS4** Angle/position *choice* quality (wrong hold, off-angle) | P | None objective — depends on team plan and enemy routes | team strategy labels, enemy route priors | none | Only a weak peer-baseline prior: hold-position frequency and outcome by state bucket | Very High | Essential | High | Cohort/pro heatmap comparison | No | Med |
| **POS5** Rotation/commitment error (late rotate, site abandoned with no info) | D/E | Departure from an area with zero information events before it; or arrival ETA > window in which the fight was decided | ticks, footstep/shot events, bomb events, nav | awpy:nav,mc,events | ETA feasibility windows (nav A* travel time vs round/plant timer); "arrival after decision" = arrival tick > last relevant kill tick; info set at departure | High | Terse→Essential | Med-High | Rotation timeline with ETAs | Y-with-model | High |
| **POS6** Lurk without coordination/impact | E | Isolation time with no contact, no information gained, no kills; or arrival after round decided | ticks, events, nav | awpy:nav,events; Kumar SOM features | Isolation-time + information-gain + realised T1 impact; cohort comparison | High | Essential | High | Lurk timeline + value endpoints | Model-relative | Med |
| **POS7** Post-plant setup error | D/E | Post-plant: teammate spacing, crossfire angle vs site, coverage of retake approaches, contact before N s ("no time play"), all-stacked | ticks, bomb events, nav, LOS | awpy:mc,vis,events | Coverage score = fraction of retake-approach nav areas under T vision (map_control on the retake side); pairwise spacing/angle stats; contact-time rule | Med-High | Terse | Med | Post-plant coverage diagram | Y-with-model | High |
| **POS8** Exposed pathing under known threat | D/E | Traversal of an area while opponents' positions are known/audible; takes damage from an angle the path exposed | ticks, damage, known-info model | awpy:vis,mc; sound proxy | Raycast LOS from opponents onto each path sample during traversal; combine with info-state flags; report exposure fraction | Med | Terse | Med | Path-exposure diagram | Y-with-model | Med-High |
| **POS9** Baiting / exit-fragging | P | Pattern of teammate deaths with the player in trade position but never attempting; low traded-death rate with high survival | kills, LOS, positions | awpy:events,vis | Trade-opportunity vs attempt-rate + response latency; needs ≥N instances across matches | Very High | Essential | High | Repeated clips, neutral framing | Model-relative | Med (sensitive) |
| **POS10** Caught in bad weapon/utility state | D | Death while reloading, holding a grenade/knife, or with an empty magazine, with enemy contact present | ticks: active weapon, is_in_reload, ammo, is_scoped | dp2:ticks, awpy:events | Deterministic rule: weapon/reload/ammo state within 500 ms before taking damage or dying while an enemy is/was visible | Low-Med | None | Low | Exact tick-trimmed clip | Y | High |

**Notes.** POS1/POS5/POS7 are the strongest positioning items because each reduces to *geometry + a declared constant* (nav ETA, timer, coverage). POS4 and POS9 are the weakest: they require intent or team plan, and HLTV's own entry/trading analysis warns that this family measures **style, not effectiveness** ("entry is a role by round, not by map or team"; opening-kill statistics do **not** identify who enters a site because "the first kill in a round can occur miles away from a bomb site", [news/35286](https://www.hltv.org/news/35286), 2022-12-26). POS10 is the most objectively verifiable item in the entire taxonomy.

### 3.2 Decision-making

| ID | Grade | Evidence | Data | Lib | Algo (constants declared) | CD | LLM | FP | Coach view | OBJ | Value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **DEC1** Negative-EV duel selection | E | Engagement taken in adverse pre-duel conditions (low HP, weapon-class disadvantage, no trade support, long range vs better gun, exposed) | ticks (HP/weapon/armour), LOS, win-prob model | awpy:events,vis; win-prob model | Pre-duel condition scorecard + T1 ΔP across the duel + cohort rate of "taking that duel"; role-conditioned (entry vs anchor) | High | Terse | High | Duel card: conditions at t−1 s vs cohort | Model-relative | Med-High |
| **DEC2** Missed required duel / hesitation | D/E | Teammate dies; player had LOS + range to the killer; no shot fired within the window (Leetify's opportunity/attempt split) | kills, LOS, shots, positions | awpy:events,vis | Opportunity detection (visibility + distance + weapon readiness) → attempt latency distribution; report latency, not verdict | High | Terse | Med-High | Opportunity clip + latency | Y-with-model | Med-High |
| **DEC3** Aggression timing vs information | P | Commitment while modelled known-info is low and enemy state suggests danger; or passivity with a numerical/utility advantage | known-info model, economy, timer, positions | awpy:mc + win-prob model | Cohort-conditioned action-rate (aggression frequency given info state) + T1 value of that bucket; needs reference policy | Very High | Essential | High | Info-state timeline | Model-relative | Med |
| **DEC4** Utility-in-hand at contact | D | Contact within ~500 ms of pulling a grenade, or grenade thrown at very short range to a visible enemy | ticks: active weapon; kills | dp2:ticks, awpy:events | Deterministic proximity/timing rule: nade-active window vs contact tick; distance at contact | Med | Terse | Med | Tick-trimmed clip | Y-with-model | Med |
| **DEC5** Round-state misjudgement (play-for-kills when lost; late/early save) | E/R | Died with savable weapon when modelled round-win prob was very low; or saved when it was high; or exit-fragged a decided round | ticks, items, win-prob model, economy state | win-prob model + awpy:events | Compare realised choice to model value: value-of-save = next-round state value; requires a **game-level / next-round-aware** model (OSE-style, §3.5) | High | Terse | Med | Value-of-save arithmetic shown | Model-relative (OSE) | High |
| **DEC6** Clutch pathing/time/kit errors | D | Defuse feasibility errors (attempt without kit when impossible; not attempting when feasible); wrong path ETA; engaging vs waiting | ticks, nav, bomb timer, kit flag, defuse start/abort events | awpy:nav,events | Deterministic feasibility: distance→nav ETA + kit + defuse duration (5 s/10 s) vs remaining timer; report feasible/impossible at decision ticks | Med | Terse | Low-Med | Feasibility tree at clutch start | Y for feasibility | High |
| **DEC7** Bomb decisions (fake vs commit, plant choice/timing, defuse-vs-kill) | D/E | Planting with teammates dead (1v3 plant), plant in an exposed spot with poor post-plant cover, no-plant with control and losing to time | bomb events, ticks, timer, alive counts | awpy:events,nav,vis | Time-to-plant vs enemy ETA; post-plant exposure via LOS coverage of the plant position; site-conditional plant timing stats | High | Essential | Med | Bomb timeline + cover map | Y-with-model | High |
| **DEC8** Commitment under unknown enemy positions | P | All-in commitment with no contingency; "guess" plays | enemy belief model (does not exist) | none | Research-level only (belief modelling / DECOY testbed, [arXiv:2509.06355](https://arxiv.org/abs/2509.06355)) | Very High | Essential | Very High | Hypothesis only | No | Low-Med |
| **DEC9** Information hygiene (ignoring sound/timer/teammate contact; no re-clear) | P | Approximations: audible footstep/gunshot within proxy radius, damage-direction indicator, radar spot; then a decision inconsistent with that info | footstep/shot events, `direction_last_injury`, `spotted`, positions | dp2:events,ticks | Build an "available info" set (with caveats) → flag decisions inconsistent with it; needs a decision-normality model (cohort) | Very High | Essential | High | Info timeline (+ audio note) | No (perception unobservable) | Med |
| **DEC10** Tempo errors (slow after picks/plant; fast on save) | E | After a favourable state change, time-to-next-objective action vs cohort; value decay per second of inaction | ticks, timer, events, win-prob model | win-prob model + events | Compute dP(win)/dt across the round; flag sustained high-decay segments; compare action onset latency to cohort | High | Terse | Med | Tempo chart | Model-relative | Med-High |

**Notes.** DEC1/DEC2/DEC3/DEC9 are the classes where **role and plan conditioning is unavoidable**; they must be presented with a cohort comparison and a confidence grade, never as verdicts. DEC6's feasibility half is the most objective decision item in the taxonomy (defuse arithmetic is deterministic given distance/kit/timer). DEC5 is economically important but requires a **next-round-aware** model; note Leetify explicitly does not model scoreline ("considers rounds in isolation"), so off-the-shelf round-level ratings cannot support it.

### 3.3 Teamplay

| ID | Grade | Evidence | Data | Lib | Algo (constants declared) | CD | LLM | FP | Coach view | OBJ | Value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **TM1** Missed trade (in position, no attempt) | D/E | Teammate dies; player had LOS + range + weapon readiness to the killer; no shot within the window | kills, LOS, positions, shots, ammo/reload state | awpy:events,vis | Opportunity → attempt → success decomposition (Leetify's model); opportunity = visibility + distance + not reloading; **window is a free parameter** (1 s HLTV "saved teammate", 5 s cs-demo-analyzer, 5.25 s awpy) | Med-High | None | Med | Trade-opportunity map + latency | Y-with-model (window) | High |
| **TM2** Failed trade / untradeable cluster | D | Two teammates die within 5 s to the same killer/area with no return kill; HLTV's "trade denial" and "failed trade" semantics | kills, positions, timing | awpy:events | Cluster deaths within window; check return kill; label failed trade (both died) | Low-Med | None | Low | Cluster clip | Y-with-model | High |
| **TM3** Angle duplication / stacking | D/E | Two teammates occupy near-identical angular positions from a threat's viewpoint and lie within one HE/molotov area | ticks (pos/yaw), enemy positions, nav | awpy:vis,events | From each enemy's viewpoint: angular separation < ~5° **and** within blast radius (~150 HU fire radius) → "duplicated angle" | Med | None | Med | Sightline-cone replay | Y-with-model | Med-High |
| **TM4** Friendly flash | D | Blind event where victim side == attacker side, duration above threshold | `player_blind`/awpy `blinds` (attacker, victim, duration) | awpy:stats,events; dp2:events | Deterministic; exclude partial blinds (<1.1 s Leetify convention); strong claim only when the blinded teammate dies within the window (Scope.gg's rule) | Low | None | Low | Clip + duration | Y (engine truth) | Med-High |
| **TM5** Team damage | D | `player_hurt` with attacker side == victim side and dmg > 0 (competitive FF: bullets ×0.33, grenades ×0.85) | `player_hurt`, convars | dp2:events; awpy:events | Deterministic; classify by weapon (HE/fire/other) and by whether it caused the death | Low | None | Low (FF-off: no event → infer from `fire_bullets` angles) | Clip | Y | Med |
| **TM6** Sequential-entry error (one-by-one) | E | Entries separated by > N s with deaths between them; or simultaneous entry into the same angle | kills, ticks, positions | awpy:events | Inter-entry interval distribution vs cohort; attribute deaths between entries | Med-High | Terse | Med | Entry timeline | Model-relative | Med-High |
| **TM7** Route/flank coverage gap | E | Enemy traversed a nav route unopposed; no teammate vision covered any point of it | ticks, nav, LOS, enemy path | awpy:mc,vis,nav | For each enemy traversal, compute whether any route sample was in an "uncovered" state (no friendly vision, `vision` model); aggregate coverage gaps per round | High | Terse | Med-High | Coverage map vs enemy path | Model-relative | Med |
| **TM8** Utility sequencing/coordination error | D/E | Duplicate smokes on the same callout set within a window; utility thrown long before contact (expires); no utility left at execute | grenades, smoke/fire intervals, events, timer | awpy:grenades,events | Sequence rules: ≥2 throwers smoking the same callout within 6 s (CSReplays convention); smoke/fire lifetime vs contact tick; resource accounting at commit | High | Terse | Med | Utility timeline | Y-with-model | Med-High |
| **TM9** Support omission / smoke that blocks nothing | P | No flash precedes an entry; a smoke changes no enemy sightline (needs a smoke model) | grenades, LOS, positions, smoke geometry | awpy:vis (**explicitly smoke-blind**), map_control smoke sphere (r 144, h 60) | Pre/post-smoke LOS delta over enemy sightlines using the sphere approximation; report "no modelled sightline change", never "bad smoke" | High | Terse | High | LOS visualisation | Model-relative | Med |
| **TM10** Communication/coordination error | I (as detection) | None — voice comms are never in demos | only text `chat` | none | **Not derivable.** Optional: user-recorded comms (then it becomes a different problem) | N/A | N/A | N/A | Human review only | No | High if solvable (not solvable) |

**Notes.** The trade family (TM1/TM2) is definitional rather than objective — trade-rate outputs are **not comparable across tools** because the window differs (1 s HLTV, 5 s cs-demo-analyzer, 5.25 s awpy). HLTV's own framing: trade-based profiles measure **style, not effectiveness**, and low trade involvement is expected for entries, lurkers and AWPers ([news/35389](https://www.hltv.org/news/35389), 2023-01-26). TM10 is the only **I**-grade teamplay class, and it is the highest-value unsolved item — see §9.2.

### 3.4 Mechanics

| ID | Grade | Evidence | Data | Lib | Algo (constants declared) | CD | LLM | FP | Coach view | OBJ | Value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **MECH1** Missed easy shot | D/E | Shot at a close, near-stationary visible opponent misses (no `player_bullet_hit` / no damage despite favourable geometry) | `fire_bullets` (origin/angles/inaccuracy/seed/spread), victim pos, hits | dp2:events, awpy:shots | Angular error between shot direction and true target direction at fire tick; classify "easy miss" if distance small and target speed low; **no hitbox data** → assume a volume | Low-Med | None | Med (spread RNG, penetration, model volume) | Tick-trimmed clip | Y-with-model | High |
| **MECH2** Crosshair placement / pre-aim error | E | Angular distance between view direction at **first visibility** and the target's head direction; recovery time to first hit | ticks (yaw/pitch + **aim_punch**), LOS model, assumed player volume | dp2:ticks, awpy:vis | Leetify/JumpThrow definition: degrees of eye-angle movement from first appearance in FOV to the first damaging shot (median, outliers excluded); DSN17's F1 = cos(view, to-enemy) at first visibility | Med | Terse | Med-High | Overlay crosshair vs target | Model-relative | High |
| **MECH3** Spray/recoil-control failure | D (measure) / P (validated score) | Spray length beyond cohort; large deviation of the view series from ideal compensation; hits/all shots inside sprays | `aim_punch_angle`, `i_recoil_idx`, `shots_fired`, `fire_bullets.angles`, hits | dp2:ticks,events | Reconstruct "true crosshair" = view angle − view punch; compare to reference spray patterns ([Leetify patterns](https://leetify.com/cs2-spray-patterns)) and scorer; classify long ineffective sprays | Low | None | Med (moving targets, intentional taps) | Spray chart overlay | Y-with-model (**no validated metric exists** — SBGames 2026 names it future work) | High |
| **MECH4** Counter-strafe / moving-inaccuracy shot | D | Velocity at fire above threshold (Leetify: **34 % of weapon max speed**, rifles, no crouch) or airborne fire; high `inaccuracy` | `velocity`, `max_speed`, `velo_modifier`, `accuracy_penalty`, `is_airborne`, `fire_bullets.player_inair/inaccuracy` | dp2:ticks,events | Deterministic per-shot velocity fraction + inaccuracy; correlate with hit/miss; engine's own `m_flVelocityModifier` available as a cross-check | Low | None | Low | Shot-by-shot velocity chart | Y (engine fields; threshold is convention) | High |
| **MECH5** Slow time-to-damage | E | Time from first visibility to first damage (Leetify TTD), median, excluding engagements ≥1 s | LOS model, damage events | awpy:vis,events | Median TTD per map/tickrate; percentile vs cohort; **explicitly not reaction time** | Med | None | Med | TTD distribution | Model-relative | Med-High |
| **MECH6** Peek quality/choice (wide swing vs jiggle; re-peek) | E-P | Peek width/exposure vs need; re-peek after being spotted; duel outcome by peek type | ticks (pos/vel/yaw), LOS, damage | dp2:ticks, awpy:vis | Classify peeks by exposed angle and speed; outcome-conditioned survival per type; calibrate with peeker's-advantage research (peeker TT-damage 290.5 ms vs defender 301.0 ms; ~+30 pp advantage at 60 ms defender latency, FDG 2024) | High | Terse | High | Peek comparison clips | Model-relative | Med |
| **MECH7** Weapon handling (reload/swap timing, AWP follow-up, secondary unused) | D | Death during reload/switch; AWP fired unscoped at close range; pistol available and unused | ticks: weapon, `is_in_reload`, `is_scoped`, ammo | dp2:ticks, awpy:events | Deterministic rules on weapon/reload/scope state around contact | Med | None | Low-Med | Tick clip | Y-with-model | Med |
| **MECH8** Movement mechanics (failed jump/boost, fall damage, stuck, inefficient routing) | D/E | Fall damage; failed jump/boost sequences; traversal time ÷ optimal nav time ≫ cohort | ticks, nav (A* ETA), damage events | awpy:nav,events | Movement-efficiency ratio per traversal (actual time vs nav shortest-path time); jump/boost heuristics; compare against MLMove-style reference | Med | None | Med | Route diagram with ETA | Y-with-model | Med |
| **MECH9** Nade mechanics (self-flash, blocked bounce, wrong throw) | D | Blind events where attacker == victim; detonation position far from any known lineup/unintended area | grenades trajectory + detonation, `blinds` | awpy:grenades,stats; lineups DB (external) | Self-blind counting; detonation-position clustering vs lineups DB; blocked-throw detection is approximate (no impact event) | Med | None | Med | Trajectory overlay | Y-with-model | Med-High |
| **MECH10** Ammo/engagement economy (empty on entry, reload mid-duel) | D | `shots_fired`/ammo state at entry contact; reload during a duel | ammo fields, reload, kills | dp2:ticks,events | Deterministic rules | Low | None | Low | Clip | Y | Med |

**Notes on what is *not* possible (mechanics).**
* **No `bullet_impact` event** in demoparser2 (only `fire_bullets` + `player_bullet_hit`) → where a missed bullet landed is **P** (recomputable only by reimplementing weapon spread RNG from `seed`/`inaccuracy`/`spread`) or **I** otherwise.
* **No bone/hitbox/pose data** → all crosshair-to-target metrics assume a player volume. Leetify's public history quantifies the resulting error: radar `spotted` (0–500 ms lag) → own raycaster with an 8-point box → human-shaped hitboxes (2026-08-11), which moved Aim Rating by ≈+4 and forced benchmark renormalisation.
* **True reaction time is I** (no gaze/attention, tick quantisation 15.6 ms at 64 tick, TrueView click-frame caveat).
* **"Mechanical vs decision" attribution per event is I** without annotation; keep the two buckets separate (this is the operational form of the EPS mental-error/physical-slip split).
* **Cheat/skill confound:** the same pitch/yaw+fire features are the standard anticheat signal (BotScreen USENIX Sec 2023, 97.64 % accuracy on 7.8 M frames; XGuardian USENIX Sec 2026; VACnet's per-shot "atoms"; DSN17's 7 features). Thresholds tuned on demo data can therefore double as weak cheat detectors — label outputs as descriptive, and never as a "skill ranking" (adaptive aimbots evade VAC/VACnet/Overwatch: Witschel & Wressnegger, EuroSec 2020).

### 3.5 Utility & economy

**Objective utility facts available (engine truth):** enemies flashed + durations (the >1.1 s convention is Leetify's, not Valve's), **self- and team-flashes** (awpy's `blinds` includes them; reconstructed from flash-duration increases), HE damage to enemies and teammates, utility held at death, `thrusmoke` kills, per-item purchase cost, smoke/fire intervals (one row per cloud, no volume).

| ID | Grade | Evidence | Data | Lib | Algo (constants declared) | CD | LLM | FP | Coach view | OBJ | Value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **UEC1** Utility unspent at death / round end | D | Inventory at death shows grenades held; valued by price | ticks inventory, money, deaths | awpy:snapshots,stats; dp2:ticks | Deterministic + value-weighting (Leetify's "unused utility on death" analogue) | Low-Med (holding for retake/post-plant is legitimate) | None | Low-Med | Per-death list | Y | High |
| **UEC2** Utility thrown with zero effect | D (facts) / P (verdict) | 0 enemies blinded (`blind_duration` ≤ threshold), 0 damage, or no LOS change (smoke) | grenades, blinds, damage, LOS | awpy:grenades,stats; smoke sphere | Attribute effects with windows; report zero-effect throws as facts, never as "wasted" | High (fakes, baiting anti-flash, denial — HLTV: flashes are part of a "cat-and-mouse, fake-heavy meta") | Terse | High | Per-throw effect table | Facts Y; verdict model-relative | Med-High |
| **UEC3** Flash ineffective / self- or team-flash only | D | Own flash's victims are self/teammates only, or enemy blind < 1.1 s | `player_blind`/`blinds` (attacker, victim, duration) | awpy:stats; dp2:events | Deterministic attribution + duration threshold; separate "flashed enemy but no follow-up" from "flashed nobody" | Med | None | Med | Flash table | Y (with convention) | High |
| **UEC4** Smoke that blocks no enemy sightline | P | Pre/post LOS delta for each enemy's sightlines to relevant routes ≈ 0 | smokes (position, start/end tick), enemy positions, geometry | awpy:mc smoke sphere; **voxels undecoded** | Pre/post raycast delta with sphere approximation; **must** be labelled as approximation — awpy's LOS is documented as smoke-blind, so naive LOS inference is wrong by construction wherever smoke matters | High (fake/post-plant/denial smokes) | Terse | High | LOS visualisation + caveat | Model-relative | Med |
| **UEC5** Molotov/HE placement ineffective | D/E | 0 damage on a known-position denial; fire region intersects no enemy-usable nav path; HE damages teammates | inferno intervals, damage, nav paths | awpy:fires,damages,nav | Fire region ∩ enemy traversal path within its lifetime (reachability blocking); damage accounting incl. team damage | High | None | Med-High | Fire coverage diagram | Y-with-model | Med |
| **UEC6** Utility timing vs execute | D/E | Utility thrown long before contact (expired); no utility left at commit; smoke expires before entry | events + timings, timer, contact tick | awpy:events | Timing rules vs contact windows; resource accounting at commit | High | Terse | Med | Utility timeline | Y-with-model | Med-High |
| **UEC7** Utility spend on eco/save rounds | D (facts) | Grenades thrown during a declared eco buy-class without enemy contact | buy classification, purchases, throws | awpy:round_economy,item_events | Rule: throws during eco-class rounds; quantify spend | Med (eco strats use nades to deny/steal) | None | Med | Eco rounds list | Facts Y; verdict model-relative | Med |
| **UEC8** Buy-type errors (unfunded rifle w/o armour; CT no kit with money; wrong weapon for state) | D | Equipment at freeze-end vs money: rifle + no armour; kit affordable and unbought; SMG on full-buy rounds | money, purchases + costs, equipment value, armour/helmet/kit flags | awpy:round_economy,item_events; dp2:ticks | Deterministic affordability/consistency rules + declared buy taxonomy; role/state-conditional conventions | Low-Med | None | Low | Buy table with $ arithmetic | Y (rules) / model-relative (optimality) | High |
| **UEC9** Save/force/eco decision errors (OSE) | R (paper) / P (CS2) | Observed buy class ≠ model-optimal class; OSE = mean over rounds of (W_actual − W_optimal)² | game-level WP model (scores, money, equipment, buys, map) + round state | **none open-source** | Reimplement OSE for CS2/MR12: game-level classifier → argmax buy class per round; report squared win-prob loss per round | High (multi-round planning) | Terse | Med-High | OSE chart + top rounds | Model-relative (**paper explicit: not causal**) | High |
| **UEC10** Team buy incoordination | D/E | Equipment-value dispersion at freeze-end (e.g. 2 full + 3 eco); team spend vs affordable plan | per-player money/equipment, purchases | awpy:events,stats | Dispersion metrics + buy-class classification per team-round | Med | None | Med | Buy chart | Y-with-model | Med-High |
| **UEC11** Money hygiene (no drop; buy after commit; wasted refund) | D/E | Teammate unarmed/£0 while player has surplus; purchases after freeze end | money, `item_events` (action/item/cost), inventory | awpy:item_events | Surplus-vs-unarmed rule; purchase-timing checks | Med (dropping is a team decision) | None | Med | Money table | Y-with-model | Med |
| **UEC12** Kit/armour/defuser omissions | D | CT with money ≥ 400 and no kit in a retake-plausible round; rifle without armour | money, purchases, kit/armour flags | awpy:events,ticks | Deterministic rules with round-phase conditions | Low | None | Low-Med | Per-round buy checklist | Y | Med-High |

**Economy rules (to hard-code, all primary/secondary-sourced):** MR12 halves, first to 13; loss ladder $1,400/$1,900/$2,400/$2,900/$3,400, **loss count −1 per win, each half starts at loss count 1** (so a pistol loss pays $1,900); round win $3,250 / $3,500 (objective); plant/defuse $300; T lose-after-plant bonus **$600 in CS2** ($800 in CS:GO); kill rewards (rifle $300, AWP $100, SMG $600, shotgun $900/XM1014 $600, pistol $300, knife $1,500); teamkill −$300; short-handed +$1,000. **CS2-specific:** a **$50 CT award per Terrorist eliminated** under competitive rules (CT-side kill economy), reported as shipped 2025-07-15/16 — **[secondary-sourced]**, confirm against current game files before relying on it.

**OSE reference numbers (worth keeping for calibration targets):** 6,538 online demos, Apr 2020–Apr 2021; models: LR 0.793, XGBoost 0.739, NN 0.736 weighted log loss; buy taxonomy with observed win % (Eco 3 %, Low 27 %, Half 34 %, Hero-Low 25 %, Hero-Half 48 %, Full 59 %); in ~2,000 CT test eco rounds the model's optimum was Low/Half in >90 % of cases at an estimated cost of **≈3 pp map-win probability**; OSE ↔ round-win-rate r = **−0.45**; **T-sided round 2 after a pistol loss: actual 27 % eco / 10 % low / 63 % half vs model-optimal 0/0/100**; CT 6/3/91 vs optimal 4/0/96. Limitations: CS:GO/MR15, organised semi-pro/pro only (little buy-variation), correlational, and the OSE↔win-rate correlation is partly circular because both derive from the same model. **No open-source, current, validated CS2 expected-buy optimiser exists** (negative result).

---

## 4. Consolidated feasibility matrix (all 52 classes, tiered)

Tiers are ordered by *epistemic strength of the evidence*, which is the binding constraint on false positives — not by coaching value.

### Tier A — engine truth: deterministic, no geometry model, no counterfactual needed

| IDs | Grade | Why this is Tier A | FP | OBJ | Value |
|---|---|---|---|---|---|
| UEC1 (unused utility at death), UEC3 (flash attribution incl. self/team), UEC7 (utility spend on eco), UEC2-facts (zero-effect throw), UEC11 (money hygiene), UEC10 (buy incoordination, dispersion) | D | Every quantity is an event or an inventory/money field; the only constants are price tables and a blind-duration convention (>1.1 s) | Low-Med | Y | Med-High |
| UEC8 (buy-consistency), UEC12 (kit/armour omissions) | D | Affordability arithmetic on recorded purchases; rules are checkable line by line | Low | Y | High |
| TM4 (friendly flash), TM5 (team damage), TM2 (trade cluster within a declared window), MECH10 (ammo/reload), MECH9-self (self-flash) | D | Engine events with attacker/victim attribution; only the trade window is a convention | Low | Y | Med-High |
| POS10 (caught in bad weapon/utility state), DEC4 (utility-in-hand at contact), DEC6-feasibility (defuse/plant arithmetic), MECH4 (counter-strafe/velocity at fire), MECH7 (weapon handling rules) | D | Tick-level state predicates + deterministic thresholds; MECH4 uses the engine's own movement-accuracy fields | Low | Y | High |

### Tier B — geometry + declared constants (nav mesh, LOS, timers); sound method, bounded error

| IDs | Grade | Why this is Tier B | FP | OBJ | Value |
|---|---|---|---|---|---|
| POS1 (isolation/untradeable death), POS5 (rotation ETA/abandonment), POS7 (post-plant coverage/spacing), POS8 (path exposure), MECH8 (movement efficiency vs nav ETA) | D/E | Requires the nav mesh + raycasts; every constant (trade window, ETA slack, coverage threshold) is a declared convention | Med | Y-with-model | Med-High |
| TM1 (missed trade), TM3 (angle duplication), TM7 (coverage gap), TM6 (entry sequencing) | D/E | Same geometry stack, applied team-relatively; TM1's window is the known non-comparable parameter | Med | Y-with-model | Med-High |
| TM8 (utility sequencing), UEC5 (fire placement/denial), UEC6 (utility timing) | D/E | Event geometry + lifetimes (smoke/fire duration) vs contact ticks | Med | Y-with-model | Med-High |
| DEC2 (missed duel opportunity), DEC7-feasibility (plant timing/cover), MECH9-positioning (nade landing vs lineups) | D/E | Opportunity detection needs LOS + readiness heuristics | Med | Y-with-model | Med-High |
| MECH2 (crosshair placement), MECH5 (time-to-damage), MECH1 (missed easy shot), MECH3-measure (spray deviation) | E/D | Fully computable **only** through an assumed player volume + visibility model; Leetify's +4 rating shift after hitbox change is the error bound | Med-High | Model-relative | High |

### Tier C — cohort/model-relative: requires a reference policy or a win-probability model

| IDs | Grade | Why this is Tier C | FP | OBJ | Value |
|---|---|---|---|---|---|
| DEC5 (save/play-for-kills), DEC10 (tempo/inaction decay) | E/R | Needs a calibrated win-probability model plus, for DEC5, a **next-round-aware** (game-level) model | Med | Model-relative | Med-High |
| UEC9 (OSE buy optimality) | R (2021 CS:GO) / P (CS2) | Reimplementation of a published metric; paper explicitly non-causal; "optimal" is the argmax of the modeller's own model | Med-High | Model-relative | High |
| DEC1 (negative-EV duel selection), POS2 (overextension), POS6 (lurk value) | E | Cohort-conditioned behaviour rates + T1 value; role/plan confounding is severe | High | Model-relative | Med |
| MECH6 (peek choice), POS3 (predictable re-peek) | E | Definitional patterns; outcome-conditioned statistics; needs matched controls | Med-High | Model-relative | Med-High |

### Tier D — speculative / infeasible as *detection* from demo data

| IDs | Grade | Why it fails today | FP | OBJ | Value |
|---|---|---|---|---|---|
| TM10 (comms/coordination) | **I** | Voice is never in demos; only text chat | N/A | No | High but unreachable |
| DEC8 (commitment under unknown enemy positions) | P/I | Needs a belief model and a counterfactual over enemy distributions; no ground truth | Very High | No | Low-Med |
| POS4 (angle/position *choice* quality) | P | Strategy-conditional; the closest published critique says outcome-driven models cannot separate failed-good-tactic from bad-tactic | High | No | Med |
| POS9 (baiting/exit-fragging) | P | Style ≠ effectiveness by HLTV's own statement; same behaviour is correct in other roles; needs cross-match N | High | No | Med |
| TM9 / UEC4 (smoke-quality verdicts) | P | No open post-hoc smoke occlusion model; `m_VoxelFrameData` format undocumented; awpy LOS is smoke-blind, so naive inference is **wrong by construction** where smoke matters | High | Model-relative | Med |
| DEC9 (information hygiene) | P | Perception is unobservable; sound occlusion/mix unmodelled; the `spotted` mask is documented as unreliable (0–500 ms lag) | High | No | Med |
| DEC3 (aggression-timing quality) | P | Requires a reference policy + information-state model simultaneously | High | Model-relative | Med |
| MECH "missed bullet location", "true reaction time", "mechanical-vs-decision attribution" | I | No impact event; no gaze/input timing; no label source | N/A | No | — |

### Grade counts

Item count: **52 classes** (POS 10, DEC 10, TM 10, MECH 10, UEC 12). Split grades are counted in their strongest bucket, except where noted.

| Grade | Count | Comment |
|---|---|---|
| **D** Demonstrated as detection | 18 | Includes everything in Tier A plus MECH3 (measurement), MECH7, MECH9, MECH10, POS3, POS10 |
| **D/E** (D facts, E verdict) | 15 | Tier B core: geometry + declared constants |
| **E** Experimental | 9 | Pattern/cohort classes (POS2, POS6, DEC1, DEC10, TM6, TM7, MECH2, MECH5, MECH6) |
| **R** Research-supported (transfer) | 2 | DEC5 (process/outcome decomposition), UEC9 (OSE) |
| **P** Plausible-untested | 7 | POS4, POS9, DEC3, DEC8, DEC9, TM9, UEC4 |
| **I** Infeasible as detection | 1 class (TM10) | **Plus 3 capability-level infeasibilities that are not taxonomy classes:** true reaction time (MECH5 caveat), bullet-impact location, and mechanical-vs-decision attribution |

---

## 5. Ranked recommendations

### 5.1 Top 5 most reliably detectable (build these first)

| # | Class(es) | One-line why |
|---|---|---|
| 1 | **UEC12 kit/armour/defuser omissions + UEC8 buy-consistency** (Tier A, D) | Pure arithmetic over recorded purchases and money: zero geometry, zero counterfactual, instantly checkable by the user, and directly Elo-relevant at 2000. |
| 2 | **MECH4 counter-strafe / moving-inaccuracy shots** (Tier A, D) | The engine itself exposes `velocity`, `max_speed`, `m_flVelocityModifier`, `accuracy_penalty` and per-shot `inaccuracy`/`player_inair`, so the metric is measurable without any visibility model — the single most fixable mechanic. |
| 3 | **UEC1 utility unspent at death + UEC3 flash attribution** (Tier A, D) | Inventory-at-death and `player_blind` (attacker + `blind_duration`) are direct events; only a published convention (>1.1 s) needs declaring; self/team flashes are engine-truth. |
| 4 | **TM2 trade clusters + TM4 friendly flash + TM5 team damage** (Tier A, D) | Death clustering, blind attribution and friendly-fire damage are all recorded events; only the trade window is a free parameter, which the report can state explicitly. |
| 5 | **POS10 caught in bad weapon/utility state + DEC6 clutch defuse/plant arithmetic** (Tier A, D) | Deterministic state predicates and feasibility arithmetic (nav-ETA + kit + 5 s/10 s defuse vs timer) — objective, low-FP, and highly teachable. |

*Next tier to add once a win-probability model is calibrated:* MECH2/MECH1/MECH3 (Tier B, high coaching value, needs the visibility model) and DEC5/UEC9 (Tier C, needs the game-level model).

### 5.2 Bottom 5 least feasible (do not promise these)

| # | Class | One-line why |
|---|---|---|
| 1 | **TM10 communication/coordination mistakes** | Voice comms are absent from every demo format; the only related signals (text chat) carry almost no coordination information — detection is infeasible, not merely hard. |
| 2 | **DEC8 commitment quality under unknown enemy positions** | Requires a belief model over hidden enemies *and* a counterfactual action model; no CS2 implementation or ground truth exists (the closest artefact is a waypoint planning testbed, DECOY). |
| 3 | **POS4 "wrong angle"/off-position judgement** | The correctness of an angle depends on the team's plan, the opponent's tendencies and the round context; published work states outcome-driven models cannot distinguish a failed good tactic from a bad choice. |
| 4 | **TM9/UEC4 smoke-quality verdicts** | No open tool reconstructs post-hoc smoke occlusion (voxel format undocumented; the one offline solver is an unmet-target draft), and awpy's LOS explicitly ignores smoke — so geometry-only smoke verdicts are wrong by construction. |
| 5 | **POS9 baiting / exit-fragging** | The identical behaviour is correct for a lurk, an anchor or an AWPer; HLTV's own framing is "style, not effectiveness", and separating intent requires cross-match aggregation the per-round data cannot supply. |

*Honourable mentions (mid-tier, wire them with confidence gating):* DEC1 negative-EV duel selection, DEC9 information hygiene, MECH6 peek choice, DEC3 aggression timing.

---

## 6. Reference architecture for mistake detection (recommended)

The literature converges on one shape: **deterministic measurement first, language last**. Every credible pipeline separates them — Leetify's deterministic stats + win-probability model; mLkoach's explicit "omit what we cannot measure"; the "analysis first, language second" academic recipe (ExpertAF [arXiv:2408.00672](https://arxiv.org/abs/2408.00672); Talking Tennis [arXiv:2510.03921](https://arxiv.org/abs/2510.03921); SportsGPT/SportsRAG which deliberately **does not feed raw coordinates to the LLM** [arXiv:2512.14121](https://arxiv.org/abs/2512.14121)); and the confirmed gap that **no CS2 paper implements an end-to-end LLM coach**, only pieces.

```
Layer 0  Demo ingest + parsing        awpy 2.x (Polars) + demoparser2 extras; pin versions; per-demo
                                      capability probe (list_game_events / list_updated_fields / usercmd sanity)
Layer 1  Fact extraction              deterministic events: kills, trades(with declared window), blinds,
                                      damage, grenades/smokes/fires, purchases, bomb, defuse start/abort,
                                      footsteps, per-tick state predicates (§2.2)
Layer 2  State valuation              calibrated P(win | causal state) per map/side; XGBoost/LightGBM baseline
                                      (WPA feature set) + game-level model for economy (OSE-style);
                                      report Brier/ECE per phase; match-grouped splits only
Layer 3  Information model            modelled known-info per player per tick: static LOS (awpy VisibilityChecker),
                                      FOV 90°, flash state, sphere-smoke approximation; sound proxy;
                                      label every output "modelled information set"
Layer 4  Candidate detectors          one detector per taxonomy ID; each emits
                                      {type, severity ΔP with bootstrap CI, evidence pointers (ticks/entities),
                                       constants used, information-set assumption, confidence}
Layer 5  Cohort comparison            peer distribution for the same state bucket (own history, cohort, pro ref);
                                      frequency + typical T1 value; flag only cohort-rare ∧ repeatedly negative
Layer 6  LLM narration                claim objects → prose. The LLM may rank, group, explain, and ask questions.
                                      It may NOT introduce a finding, a number, or a causal claim not in the object.
```

**Hard gates before a finding is surfaced** (each gate exists to suppress a specific documented failure mode):

1. **Availability gate** — the "better" alternative was reachable in time (nav-graph ETA). Prevents flagging physically impossible advice.
2. **Information gate** — the finding states the modelled information set; decisions that were reasonable under the player's *modelled* info are demoted to "question" rather than "mistake" (comms are unobservable, so info-error vs decision-error cannot be fully separated).
3. **Calibration gate** — the win-probability model's ECE in that map/phase must be below a declared threshold; otherwise severity is reported as `unknown` (pistol rounds and early-round states are the weakest).
4. **Sample gate** — per-habit aggregation with a minimum instance count and a CI that excludes zero; single-instance findings are labelled "anecdote" and never used for prioritisation.
5. **Definition gate** — every constant (trade window, blind threshold, velocity fraction, coverage radius) is printed in the finding, and the UI states that cross-tool comparison is invalid where definitions differ.
6. **Recall budget** — cap findings per round/half, ranked by severity × reliability; a mistake *list* that is 60 items long is a product failure, not a completeness win.

**LLM contract (evidence-grounded coaching).** The LLM receives only structured claims with pointers; its output must cite tick ranges; any number it produces must come from the claim object (a "no free numerics" rule). Justification: (a) CS2-specific LLM coaching has no validated precedent; (b) LLM judges/explainers show systematic biases — position bias is measured across judges ([arXiv:2406.07791](https://arxiv.org/html/2406.07791v9), ACL IJCNLP 2025) — and VLM gameplay narration reports **hallucinated game state** as a failure mode ([arXiv:2608.14016](https://arxiv.org/abs/2608.14016), 2026-08); (c) sports coaching studies warn that LLM-only coaching lacks causal validation (single-athlete half-marathon case, [arXiv:2509.26593](https://arxiv.org/abs/2509.26593)) and that coaches still expect human oversight ([arXiv:2502.14632](https://arxiv.org/abs/2502.14632)).

**Where the LLM *is* genuinely needed (per taxonomy column):** hypothesis-forming on intent-laden classes (POS4, POS6, POS9, DEC3, DEC9), narrative synthesis across findings, and turning cohort deltas into practice prescriptions. Everywhere else it should be silent or terse.

---

## 7. Validation plan

There is **no ground-truth label set** for CS2 mistakes (negative result across arXiv, SSAC, JQAS, SAGE searches). Validation must therefore be layered, and no layer alone justifies shipping a verdict.

1. **Fact layer (sanity):** cross-parser agreement (awpy vs demoparser2 vs demoinfocs-golang) on events; hand-audited sample of 20 rounds per detector; unit tests on synthetic states. Expect parser-level discrepancies and document them.
2. **Human agreement layer:** 2–3 independent reviewers (ideally one coach-level) blind to detector output; rate a stratified sample of flagged and unflagged instances; report **weighted κ / Krippendorff's α** for category labels, **ICC (two-way absolute agreement)** for severity scores, plus raw agreement, confusion matrices and 95 % CIs; **report reviewer-vs-reviewer agreement as the ceiling** — a system cannot be more valid than its reference. Include a **disagreement audit** by map, role, round phase and detector. (Methodology as used in sports-analytics validation practice, incl. mixed-effects models for clustered observations.)
3. **Stability layer (the metric-quality criterion the literature uses — Franks et al. 2016):** test–retest across sessions/weeks; month-to-month correlation of per-player habit rates; **must beat the stability of naive baselines** (the WPA paper's own test: WPA 0.40 vs KDR 0.38, ADR 0.24, KAST 0.30, Rating 2.0 0.29).
4. **Predictive layer:** do flagged habit rates predict *future* round-win probability / Elo change beyond a baseline (K/D, ADR, KAST, rating)? Must use **match-grouped, chronological splits** and pre-register the baseline. Note the circularity hazard: never validate against quantities produced by the same model that generated the flags.
5. **Intervention layer (the only causal evidence):** A/B or pre/post with targeted practice on one flagged category at a time; primary outcome = the detector's own metric (did counter-strafe rate improve?), secondary = Elo/Win-rate over ≥100 matches. Sibling slice `CoachingScienceEval` owns feedback-efficacy design; this slice's requirement is only that the detection layer can emit a measurable pre/post target.
6. **Leakage audits (mandatory, automated in CI):** no post-decision state in features; no match-group overlap between splits; no third-party ratings (HLTV/Leetify) in inputs; label timestamps < feature timestamps; `usercmd` sanity probe per demo source.

**Definition of "validated" for this system:** *not* "agrees with one coach on one match". The defensible claim is: "predefined categories with substantial agreement against independent reviewers, stable across sessions, predictive beyond conventional statistics, and actionable" — the framing used in sports-video performance-analysis validation studies.

---

## 8. Failure modes and traps (checklist to encode as tests)

1. **Outcome conditioning** — any label that reads the final result; survivorship in saves; zero-sum credit that punishes saving (both documented industry admissions).
2. **Leakage** — adjacent-state correlation, snapshot-level splits, post-match stats as features, match-group bleed, baselines that share the detector's model.
3. **Model-relative "mistake"** — reporting the modeller's optimum as a fact (OSE's own caveat; no causal evidence for any CS metric).
4. **Approximation drift** — visibility/hitbox models change (Leetify's +4 shift); every stored finding must record (parser version, model version, CS2 build, constants).
5. **Definition drift** — trade windows (1 s vs 5 s vs 5.25 s), blind thresholds (>1.1 s), velocity fraction (34 %), coverage radii: **cross-tool comparisons are invalid**; state this in the UI.
6. **Patch drift** — CS2 economy/utility/gameplay change (CT $50 kill award, MR12 economy, smoke behaviour); models and rule tables must be versioned and re-validated.
7. **Role/strategy confounding** — lurk/AWP/entry behaviours flagged as errors (HLTV: style, not effectiveness; Kumar's role-consistency study found a **tight null**: prior role consistency does not predict the next round, β = 0.32, 95 % CI [−0.88, 1.52]).
8. **Intent confounding** — "missed trade/duel" may be a correct reset, a save round, or an aborted execute (HLTV: flashes live in a "cat-and-mouse, fake-heavy meta").
9. **Cheat/skill confound in mechanics** — the same features are anticheat signals; adaptive aimbots defeat thresholds (EuroSec 2020), so mechanics metrics must not be presented as skill or integrity verdicts.
10. **Small-sample volatility** — clutches/Round Swing fluctuate on single maps (HLTV says so twice); enforce the sample gate and show CIs.
11. **Goodhart / metric corruption** — once the user optimises a flagged metric, the metric stops measuring the habit; rotate detectors and keep human review in the loop.
12. **Demo-source variance** — GOTV vs FACEIT vs tournament; `player_bullet_hit` empty in some platform demos; usercmd `delta_data` breakage (issue #340) and silently dropped `usercmd_subtick_moves` (issue #345); **probe capabilities per demo, never assume**.
13. **Parser breakage after Valve patches** — issue #321 shows total parse failure after a patch; findings must be reproducible from stored (demo hash, parser version).
14. **LLM overreach** — hallucinated state, invented numbers, confident causal claims; enforce the evidence-object contract and no-free-numerics rule.

---

## 9. Open questions, upgrade paths, and unverified items

### 9.1 Items I could not verify from a primary source (do not cite as established)

* CS2 **$50 CT-per-T-kill** award and its 2025-07-15/16 shipping date — **secondary-sourced** (wiki tables citing patch notes; Valve newsentry page not directly readable). Verify against current game convars before using in economy rules.
* **liquipedia** pages (loss bonus, economy, weapon chart) returned 403 during research; MR12/loss-bonus values above rest on wiki/secondary sources plus an academic MR12 statement.
* A **"AI Coach for Valorant" IEEE paper** (claimed crosshair-offset/rotation/utility error detection) — page returned HTTP 418; **[unverified]**.
* **SCOPE.GG "No Trade" label**, Leetify's exact Positioning formula, and a "Leetify Feb 2026 rating update" — asserted only in search summaries, not confirmed on primaries; treat as **[unverified]**.
* Community footstep-earsot distances (~800–1 100 units) — non-primary (audio-config sites); only Valve's jump-landing-distance change is documented.
* Jing et al. 2025 (SHAP-based CS player analysis, paywalled) — cited as existing, contents unverified.
* Some 2026 "AI coach" products (Mercurial "AI Deep Scan", UpForge, Breakdown/ReplayLab) — marketing only; no methodology found.

### 9.2 What would upgrade grades

| Upgrade | Blocking item | Consequence |
|---|---|---|
| Smoke-quality verdicts TM9/UEC4: P → D/E | Decode `m_VoxelFrameData` (networked uint8 vector, extractable today; format undocumented) or complete the offline flood-fill solver to its IoU target | Unlocks the largest remaining utility category and materially improves the information model for POS/DEC classes |
| Communication/coordination TM10: I → ? | Capture the user's own **voice comms** (or a structured call-log) alongside the demo | Unlocks the highest-value unsolved class; without it, keep it out of the taxonomy's promises |
| Intent-laden classes (POS4/POS9/DEC3/DEC9): P → E | A reference policy model (what comparable players do in that state) + a coach-agreement study | Converts "cohort-rare" heuristics into defensible findings |
| Economy DEC5/UEC9: P → D | A CS2/MR12 **game-level** win-probability model (round-level models cannot represent saves) + OSE reimplementation | Enables save/buy coaching with explicit assumptions |
| Mechanics MECH3: P → D | Reimplement weapon spread from `fire_bullets.seed`/`inaccuracy`/`spread` (or obtain bullet impacts) | Turns "spray measurement" into a validated recoil-control score — explicitly named as unbuilt future work (SBGames 2026) |
| Any class → validated | Human-agreement + stability + predictive + intervention studies (§7) | Moves findings from "indicator" to "verdict"-grade claims |

### 9.3 Open research questions worth a spike (each ≤ a few days)

1. Does the `awpy` sphere-smoke approximation agree with in-engine smoke truth (`CS2-Bot-Vision` density model) on a sample of lineups? If yes, TM9/UEC4 becomes E.
2. How many FACEIT demos (2026-07-10+) still yield usable `usercmd` data after the demoparser2 0.42.0 fix, and what fraction of mechanics findings depend on it?
3. What is the true intra-player stability of each detector's habit rate (test–retest over 20 matches)? This sets the sample floor.
4. Do coach reviewers agree with the Tier A detectors at a rate that supports automated surfacing without review? (Expect yes for UEC12/MECH4/UEC1; expect no for DEC1/DEC9.)

---

## 10. Sources (grouped; dates/status as observed 2026-10-15)

**Action valuation / decision science**
* Xenopoulos, Doraiswamy, Silva — *Valuing Player Actions in CS:GO*, [arXiv:2011.01324](https://arxiv.org/abs/2011.01324) (IEEE BigData 2020; v2 2020-11-04).
* Xenopoulos, Coelho, Silva — *Optimal Team Economic Decisions in Counter-Strike* (OSE), [arXiv:2109.12990](https://arxiv.org/abs/2109.12990) (IJCAI 2021 AISA workshop; 2021-09-20).
* Szmida & Toka — *Evaluating Player Actions in Professional Counter-Strike using Temporal Heterogeneous GNNs*, MIT Sloan SSAC 2026 (Inferno, 114 matches; AUC 0.8549).
* Decroos et al. — VAEP, KDD 2019; *xT vs VAEP critical comparison*; Mendes-Neves et al. — *Valuing Players Over Time* [arXiv:2209.03882](https://arxiv.org/abs/2209.03882) (2022-09-08).
* Paul, Klemp, Memmert — *Beyond Outcome Bias* (xSuccess + adjusted VAEP), MLSA25 (KU Leuven, 2025).
* Baron & Hershey — *Outcome bias in decision evaluation*, JPSP 54(4):569–579 (1988).
* Franks et al. — *Meta-analytics*, JQAS 12(4) (2016); Brill, Yurko, Wyner — [arXiv:2406.16171](https://arxiv.org/abs/2406.16171) (JQAS, 2024/2025); Davis et al. — *Machine Learning* 113:6977–7010 (2024-07-17).
* Xavier (KU Leuven) — *Three key design decisions for possession state value models* (2024-11-13).
* Ma et al. — *StratIncon*, [arXiv:2503.09060](https://arxiv.org/abs/2503.09060) (IUI'25); Boulicaut et al. — *What did I do Wrong in my MOBA Game?* DSAA 2016; Trotter et al. — EPS framework [arXiv:2608.09156](https://arxiv.org/abs/2608.09156) (2026-08).

**Industry metric definitions (primary first-party)**
* HLTV — [Rating 3.0](https://www.hltv.org/news/42485/introducing-rating-30) (2025-08-20); [3.0 adjustments](https://www.hltv.org/news/43047/rating-30-adjustments-go-live) (2025-10-29); [accuracy update](https://www.hltv.org/news/45596/rating-30-receives-small-accuracy-improvements) (2026-10-01); [Attributes](https://www.hltv.org/news/39672/introducing-hltv-attributes) (2024-08-21); Rating 2.1 (2024-10-14); [entry-role analysis](https://www.hltv.org/news/35286) (2022-12-26); [flash statistics](https://www.hltv.org/news/34796/using-flashbang-statistics-effectively) (2022-10-25); [Lone Wolf/saved teammates](https://www.hltv.org/news/35389) (2023-01-26); [ToS](https://www.hltv.org/terms) (effective 2025-01-27).
* Leetify — [Rating explained](https://leetify.com/blog/leetify-rating-explained/) (2024-11-25, upd. 2025-04-24); [stats glossary](https://leetify.com/blog/leetify-stats-glossary/) (mod. 2025-01-10); [utility ratings](https://leetify.com/blog/utility-ratings/) (2025-10-24); [hitbox improvement](https://leetify.com/blog/aim-stat-calculation-hitboxes-improved/) (2026-08-11); [enemy actually spotted](https://leetify.com/blog/enemy-actually-spotted/) (2020-10-04); [benchmarks](https://leetify.com/blog/cs2-benchmarks/); [spray patterns](https://leetify.com/cs2-spray-patterns).
* FACEIT — Round Swing support article (2026-04-29); [Data API](https://docs.faceit.com/docs/data-api/) + Downloads API.
* Scope.gg — [site](https://scope.gg/) / [match history](https://scope.gg/match-history/) (marketing-level claims); Refrag — [Coach](https://refrag.gg/coach/) + [stats explained](https://refrag.gg/blog/cs2-stats-explained/); Skybox EDGE — [pricing/features](https://www.skybox.gg/pricing/); CSReplays — [heuristics + classifier methodology](https://csreplays.com/blog/heuristics-and-classifier) (2026-06-01); mLkoach — [mlkoach.com/en](https://mlkoach.com/en/); JumpThrow/CounterStrikeStats — [aim analysis definitions](https://counterstrikestats.com/features/aim-analysis/) (reviewed 2026-10-06).

**Tooling / data / parsers**
* awpy — [datasets](https://awpy.readthedocs.io/en/latest/datasets.html), [visibility](https://awpy.readthedocs.io/en/stable/visibility.html), [map control](https://awpy.readthedocs.io/en/stable/map_control.html) (read 2026-10-15); [awpy-data](https://github.com/pnxenopoulos/awpy-data).
* demoparser2 — [repo](https://github.com/LaihoE/demoparser), issues [#340](https://github.com/LaihoE/demoparser/issues/340) (2026-07-11), [#345](https://github.com/LaihoE/demoparser/issues/345) (2026-08-10), [#321](https://github.com/LaihoE/demoparser/issues/321) (2026-04-21); PyPI 0.42.0 (2026-08-08).
* demoinfocs-golang — [releases](https://github.com/markus-wa/demoinfocs-golang/releases) (v5.0.5 2025-12-05; v5.2.0; v6 alpha).
* CS2 schema — [CSmokeGrenadeProjectile](https://cs2opendev.github.io/CS2OpenDev-Docs/schemas/server/CSmokeGrenadeProjectile/) (build 25218825, Steam date 2026-09-09); [CS2DemoKit](https://github.com/CS2OpenDev/CS2DemoKit).
* Smoke modelling — [XBribo/CS2-Bot-Vision](https://github.com/XBribo/CS2-Bot-Vision); [NC1107/cs2-smoke-solver DESIGN.md](https://github.com/NC1107/cs2-smoke-solver/blob/master/DESIGN.md) (draft); voxel-extraction script [CS2-insight-agent](https://github.com/DrEAmSs59/CS2-insight-agent/blob/main/backend/scripts/analyze_smoke_voxel_frames.py).
* Round-win toolkits — [cs2-evalbar](https://github.com/eigenpaul/cs2-evalbar); [TaiZo1/cs2-win-prediction](https://github.com/TaiZo1/cs2-win-prediction); cited thesis [vskp.vse.cz/100656](https://vskp.vse.cz/100656).
* Datasets — ESTA [arXiv:2209.09861](https://arxiv.org/abs/2209.09861); X-Ego-CS [arXiv:2510.19150](https://arxiv.org/abs/2510.19150) / [HF](https://huggingface.co/datasets/wangyz1999/X-EGO-CS); awpy-data; blanchon/opencs2_dataset_demo.

**Mechanics / aim / anticheat feature literature**
* BotScreen, USENIX Security 2023 (97.64 %, 7.8 M frames); XGuardian [arXiv:2601.18068](https://arxiv.org/abs/2601.18068) (USENIX Sec 2026); YAACS [arXiv:2607.04336](https://arxiv.org/abs/2607.04336) (2026-07-05); AimDetect/Liu et al., DSN 2017; VACnet GDC 2018; Witschel & Wressnegger, EuroSec 2020 [arXiv:2004.12183](https://arxiv.org/abs/2004.12183); GAN-Aimbots, IEEE ToG 2022 [arXiv:2205.07060](https://arxiv.org/abs/2205.07060).
* Santos & Garcia — *Complexity Analysis in Counter-Strike 2 Spray Patterns*, SBGames 2026 (12,091 pro sprays ≥3 shots; names per-player recoil-control scoring as unbuilt).
* Murakami et al. — pre-aim skill (J-STAGE, small n); Bediou et al. — movement kinematics, Frontiers 2022; Liu et al. — eye movements (2025); FirstPersonScience (NVIDIA); Tokey et al. — peeker's advantage, FDG 2024; Xu, Liu, Claypool — CS:GO latency.
* Durst et al. — MLMove [arXiv:2408.13934](https://arxiv.org/abs/2408.13934) (SCA/CGF 2024); Pearce & Zhu — behavioural cloning [arXiv:2104.04258](https://arxiv.org/abs/2104.04258) (repo stale, CS:GO offsets).

**Positioning / teamplay / role literature**
* Xenopoulos & Silva — ESTA (2022); ggViz [arXiv:2107.06495](https://arxiv.org/abs/2107.06495) (CHI PLAY 2022); Yamada — trajectory clustering, DiGRA Japan 2025; Xia, Salinas, Morstatter — *Precision Under Fire*, IEEE CoG 2025; Kumar — SOM role discovery thesis (2025, null on role consistency); Kuzhii & Furgala — role feature engineering (2025); Xenopoulos & Silva — GNN crossfire visualisation [arXiv:2207.14124](https://arxiv.org/abs/2207.14124); Kirna — tactical labels thesis (Twente, 2025-07-04); Csapó — tactic GNN (Twente, 2025-07-04); Maymin — *Smart kills and worthless deaths*, JQAS 17(1):11–27 (2020).

**LLM coach / narration**
* ExpertAF [arXiv:2408.00672](https://arxiv.org/abs/2408.00672); Talking Tennis [arXiv:2510.03921](https://arxiv.org/abs/2510.03921); CrossTrainer [arXiv:2511.13993](https://arxiv.org/abs/2511.13993); SportsGPT [arXiv:2512.14121](https://arxiv.org/abs/2512.14121); Lee — LLM interactive sports coach [arXiv:2509.26593](https://arxiv.org/abs/2509.26593); Haase — GenAI coaching survey [arXiv:2502.14632](https://arxiv.org/abs/2502.14632); Wang & Yoshinaga — esports commentary generation [arXiv:2212.10935](https://arxiv.org/abs/2212.10935); player2vec [arXiv:2404.04234](https://arxiv.org/abs/2404.04234); Varghese — VLM narration + hallucination failure [arXiv:2608.14016](https://arxiv.org/abs/2608.14016); position bias in LLM judges [arXiv:2406.07791](https://arxiv.org/html/2406.07791v9).

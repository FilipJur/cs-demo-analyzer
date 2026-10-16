# Judgment Criteria — Evidence Requirements, Counterexamples, Uncertainty & Abstention

Research only. Grades: **Demonstrated** · **Experimental** · **Research-supported** · **Plausible-untested** · **Infeasible**. Evidence-kind labels map to the app's `domain/evidence.py` vocabulary (`recorded / computed / geometry_dependent / estimated / unsupported`); capability reading ("capability is not player perception") is the app's own boundary and is respected throughout.

## 1. Evidence tiers for review questions

| Tier | Meaning | Example | Reviewer license |
|---|---|---|---|
| **Recorded / extractable** | Engine event or networked field; objective | buy state, positions, HP, inventory, damage/death events, timer, bomb state | State as fact; cite the field |
| **Deterministically computable** | Arithmetic over recorded fields with declared constants | arrival-time math, economy consequences, trade-window timing, defuse feasibility (kit + distance + 5 s/10 s vs timer) | State with constants shown |
| **Geometry-dependent** | Needs installed map assets + raycast/nav; degrades on mismatch | LOS potential, crossfire existence, smoke occlusion (exact voxels only via cs2parser decode; awpy LOS documented smoke-blind) | State with asset-match status; never promote `unknown` to clear |
| **Contextually inferred** | Model over recorded data with stated assumptions | known-info set, role/objective, alternative realism, situation similarity | State with assumptions + uncertainty; withhold when load-bearing and weak |
| **Unavailable** | Never in the demo (or encrypted/absent) | voice comms (MM-absent), team chat (encrypted 2026-09-09), gaze/attention, intent/motive, POV-only pings in GOTV | Withhold any verdict turning on it; surface "indeterminate: evidence missing" |

Hard constraints (prior-slice C, not re-argued): `spotted` is a laggy radar flag (0–500 ms lag, "shadow" retention, 16-bit partial mask, possibly spectator-side in GOTV) — noisy corroborator, never ground truth; sub-tick order approximate; `player_sound` radius recorded, perception not; dead-player rows keep emitting (`health == 0`) and must be filtered for availability questions.

## 2. Per-question evidence classification

For every proposed review question: what it needs, how that maps, and exactly what is missing when it cannot be evaluated.

| Review question | Required information | Classification | Missing evidence (exact) |
|---|---|---|---|
| Was the buy/force correct? | economy state, loss bonus, opponent buy inference | recorded + computed | opponent exact money (inferred); treat as range |
| Was this fight selection sound? | pre-engagement numbers, positions, timer, known-info | recorded + inferred | player's info set (see below) |
| Was the trade available? | positions, LOS, weapon readiness, swing timing | recorded/computed/geometry | reaction-window exactness (sub-tick approximate); window constant is conventional, not objective |
| Was the rotation timely? | heard/seen set, bomb-spotted, fake tells, arrival math | math computed; heard/seen estimated; comms unavailable | listener info set + calls — **withhold without them** |
| Was the save correct? | live equity vs saved-weapon value, retake loadout | computed + recorded | disciplined-vs-defeatist intent — needs recurrence, not one round |
| Was the repeek justified? | peek-1→peek-2 info delta, enemy weapon/pos | delta estimated/inferred | what peek 1 taught + any unheard call |
| Was utility-in-hand negligent? | called plan, contact foreseeability | plan unavailable | the call itself |
| Was map-control conceded wrongly? | motivating read, stack odds, contest cost | read unavailable | the conceding team's info set |
| Was this 0-damage death a donation? | what death bought (info/space/utility/trade), role | downstream recorded; role inferred | downstream conversion at death time — grade after, not at, the death |
| What did the player know? (load-bearing for all above) | visible/audible set, spotted flags, smoke occlusion | recorded + geometry-dependent + estimated | gaze/attention (**Infeasible**); processed audio; voice/chat content |
| What was the player's role/objective? | spawn, strat, assignment, mid-round calls | inferred (behavior suggests; nothing assigns) | called strat, exceptions, calls — all role labels are hypotheses |
| What were the realistic alternatives? | loadout/position/time feasibility + realism | feasibility recorded/computed; realism inferred | coordinated alternatives need comms; repertoire needs longitudinal data |
| Same situation, different outcome? | matched instances + similarity metric | retrieval recorded; matching inferred | preregistered similarity metric (methodological gap); opponent info states; sample depth |

Where a finding cannot currently be evaluated, the reviewer states exactly which row above fails — never a bare verdict.

## 3. Opportunity-based evaluation (anti-selection-bias rules)

Deaths-only review conditions on bad outcomes: Q2 (bad decision, win) escapes; Q3 (good decision, loss) gets "fixed" into worse play (Duke 2×2 matrix). Mandatory corrections:

1. **Review won rounds.** Won rounds are aviation's near-misses — code *recovery factors*: why the round was won *despite* the error (ASRS Pub. 51, **Demonstrated** institutional precedent).
2. **Run the Q3 test on every flagged mistake:** "would this decision be endorsed if the outcome had flipped?" If outcome knowledge could flip the verdict, re-run blinded or withhold (criterion 7). Instruction-to-ignore does not debias (hindsight r≈.17; Guilbault).
3. **Credit abstentions longitudinally.** A save's value is an economy-trajectory consequence (computed — good); disciplined-vs-defeatist is info-state-dependent (unavailable single-instance — bad). One refused repeek proves nothing; forty with a computed economy bar is evidence.
4. **Name every reference population.** "Average decision" trained on observed (mostly pro, mostly action) data tilts toward the least-average players — the xG 17%-Messi mechanism (**Demonstrated**). Baselines read like "average LEM pugger, Mirage A-anchor, full-buy" or they smuggle selection in; proxy baselines must be validated Romer-style (mean-diff ≈ 0, SE reported) or capped.
5. **Counterfactuals are model outputs.** EV-lost = best-alternative EV − chosen EV needs a named reference policy + validated proxy + uncertainty. The unobserved alternative is the fundamental problem of causal inference — theoretical counterfactuals are never observable ground truth.

## 4. Counterexamples: misleading conventional advice

Each slogan fails because it deletes a premise the table in §2 requires.

| # | Slogan | Deleted premise | Corrective (with grade) |
|---|---|---|---|
| 1 | "Always trade" | role (§2 row: role inferred) | Entries/lurkers/AWPers structurally untraded — HLTV trade-structure + Attributes sacrificial-entry vs baiter split (**Demonstrated** snippet). Same non-trade expected-or-damning by role |
| 2 | "ADR/KAST tells the story" | buy context (eco vs full) | Rating 3.0 built to "reduce the impact of eco frags" — EliGE 133 ADR/23-frag half: 2.06 under 2.1 → 1.40 under 3.0 (**Demonstrated** that HLTV concedes the inflation) |
| 3 | "Never save" | next-round equity (computed) | MR12 concentrates round value; Jame's save-heavy Rio 2022 MVP run is the existence proof that save-tolerant style wins Majors (**Demonstrated** practice contradicts slogan) |
| 4 | "Never repeek" | peek-1→peek-2 info delta (estimated) | Conflates committing repeeks with free info jiggles; no peer-reviewed CS repeek study exists — unappliable without the delta |
| 5 | "Always rotate fast" | listener info set (estimated/unavailable) | Dies to every fake; fake-patience is slow *correctly*; most hindsight-contaminated judgment in the set (Baron & Hershey transfer, **Research-supported**) |
| — | "Don't lurk" / "never peek without flash" | plan / utility state | Collapse into #1 and the dry-peek row — listed to prevent double-counting, not graded separately |

## 5. The 13-behavior must-know/withhold table

| Behavior | Must be known | Withhold when |
|---|---|---|
| Isolated engagements | all positions, timer, bomb, info set, alternatives | info set unknown or outcome-only input |
| Lurking | called plan, arrival math, enemy rotation state | plan unknown (demo cannot split "lurk" from "lost") |
| Not trading | role, positions, swing timing, weapon | role unknown |
| Aggressive CT peeks | banked info, exit/cover, economy, score | economy + info unknown |
| Late rotations | heard/seen set, bomb-spotted, fake tells, arrival math | listener info set unknown |
| Saving | live equity vs saved value, retake loadout | economy context missing |
| Passive positioning | objective, risk of aggression, repetition | single-round sample |
| Repeeking | peek-1→peek-2 info delta, enemy weapon/pos | peek-1 state unknown |
| Dry peeking | flash availability, known/unknown angles, timer | utility state unknown |
| Giving up map control | motivating read, stack odds, contest cost | conceder's info set unknown |
| Dying without damage | what death bought, role, downstream conversion | downstream unknown (grade after, not at, the death) |
| Utility-in-hand at contact | called plan, contact foreseeability, reaction window | plan unknown |
| Numbers up/down fights | pre-fight equity, alternatives, baselines | pre-fight equity unknown |

Global rule: any behavior judged from omniscient replay **without reconstructing the player's info set** is outcome-biased by construction — withhold or label hypothetical.

## 6. Abstention criteria (mandatory withholds)

A verdict is supported only if every load-bearing premise is recorded, computed, or geometry-resolved. Otherwise withhold as T0 facts + missing premise + fired criterion. A withhold is a completed review output, not a failure.

1. **Comms-dependence** — verdict turns on what was said/called/agreed. Voice absent (MM); team chat encrypted 2026-09-09. Unevidenced "additional information" never rescues a verdict (Romer, **Demonstrated**).
2. **Perception-dependence** — verdict turns on what the player saw/heard/noticed vs what was merely visible/audible omnisciently. Attention unrecorded; spotted-mask traps make replay actively misleading.
3. **Intent-dependence** — verdict attributes motive ("baiting", "tilted", "threw"). Intent never recorded. Describe behavior; withhold motive.
4. **Single-instance abstention credit** — one disciplined save/refused repeek/held rotation cannot be credited as correct vs lucky-passive without recurrence or a computed economy bar (xG variance lesson: sustained signal needs volume).
5. **Unmatched comparison** — same-situation claim with no retrieved counterpart, or ad-hoc counterparts, is cherry-picking until matching rules are preregistered and opponent states comparable.
6. **Unvalidated EV numbers** — EV-lost from an unnamed reference population or unvalidated proxy is unsupported (xG 17% bias; Romer proxy bar).
7. **Unblinded outcome-known review** — where outcome knowledge could flip the verdict (Q3 test fails or cannot run), re-run blinded or withhold. Instruction-to-ignore does not debias.
8. **Geometry-unresolved occlusion** — LOS/smoke/timing claims that assets + voxels + recorded ticks cannot resolve (sub-tick edges, voxel gaps) → withhold the awareness/avoidability premise specifically, even if the action description stands.

## 7. What makes the central question answerable

"Given the player's likely responsibilities, available information, actual situation, and realistic alternatives, is there sufficient evidence that a different decision was preferable?" — answerable iff:

- **Responsibilities:** a role hypothesis with stated uncertainty (never a label) — else criterion 1/3 fires.
- **Available information:** a reconstructed info set with per-premise tiers (§1) — else criterion 2 fires.
- **Actual situation:** recorded pre-decision state (score/economy/numbers/clock/positions) — structurally available; opponent *intent* excluded by design.
- **Realistic alternatives:** feasibility-checked options (loadout/position/time) with realism marked inferred and team-coordinated options flagged infeasible-without-comms — else criterion 5/6 fires.
- **Sufficient evidence:** the Q3 test passes (or blinded re-run), counterexamples sought (step 7 — currently the highest-value step with zero verified CS precedent), and recurrence shown before any habit claim.

If any clause fails, the honest output is facts + missing evidence + fired criteria — which is exactly what a future reviewer must be built to emit.

# Skill Progression and Expert Diagnosis

**No rigid Elo thresholds unless sourced — none are.** Stages are qualitative marker sets.
Access date for all sources: 2026-10-15/16. Tiers Measured / Official / Expert / Community
as in `sources.md`. Claim classes (1)–(5) as in `README.md`.

## 1. Beginner — learning what to do

**Observable markers (1):** full-buy rounds with missing utility/no kit; unshifted loud
movement; stationary wide-peeks into multiple angles; crosshair at floor/ceiling;
saving with no exit plan vs hunting won rounds.
**Priority mistakes:** economy illiteracy (FUND-036/038), sound discipline (FUND-018),
placement basics (FUND-006), no trade positioning at all (FUND-030).
All directly demo-observable (economy snapshots, velocity vectors, view pitch).
**False-positive severity: LOW** — rarely excused by role.
**What persists upward:** none of the *errors* persist as errors; the underlying fundamentals
(buy correctly, move quietly when unspotted, aim at head height) persist as automated
background at every level.

Coaching note: fix one list at a time and re-measure over weeks; judge change over
samples ("Last 30 days"), never one demo (Leetify improvement guide — Official,
https://leetify.com/blog/leetify-guide-how-to-start-improving-in-csgo/).

## 2. Intermediate competitive — learning how, inconsistently

**Observable markers (1)/(3):** utility *thrown* but ineffective (pop-flashes blinding nobody,
smokes with gaps — FUND-031/033); duels taken without numbers/setup (FUND-021/024);
rotates off sound cues alone (FUND-025/045-weak); wins isolated duels but loses
round-impact stats.
**Priority mistakes:** low-impact frags (eco-padding, exit frags — Leetify FAQ: "low impact
kills… deaths in 2v2/1v1 swing the round heavily" — Official,
https://leetify.com/blog/leetify-rating-explained/); untraded entries (FUND-030);
utility without setup (FUND-031–035).
Refrag Coach operationalizes this staging: benchmarks General/Aim/Utility/Entry&Trades
against players *above your level*, flags only underperforming stats (Official,
https://refrag.gg/blog/cs2-stats-explained/).
**FP severity: LOW** — markers are demo-computable and rarely excused by role.

## 3. Advanced FACEIT — individual optimization, team-context poverty

**Observable markers (2)/(4):** strong mechanical metrics (counter-strafe %, TTK, spotted
accuracy) but flat round-win impact; defaulting without info plays; tilt-queue hero peeks.
Canonical failure signature (Official, https://refrag.gg/blog/cs2-stats-explained/):
**"Why is my K/D good but my rating bad? Usually because your kills aren't happening in
moments when they matter. Exit frags, late-round kills in lost rounds, and baiting all pad
K/D without contributing to round wins"** — (2)-in-round, (4)-as-verdict.
Role confound stated on the same page: **"support players naturally post lower ADR than
star riflers"** — condition on role before flagging low output.
Leetify Rating is **"a performance metric, not a skill metric… in *their* games"**
(https://leetify.com/blog/leetify-rating-explained/) — cross-lobby comparisons are (5).

| Subtler habit | Type | Legit exception | Reviewer check | Demo | FP |
|---|---|---|---|---|---|
| Baiting (late arrival, high K/D low impact) | mixed | designated trade-bait / crossfire anchor per plan | planned crossfire or self-preservation? needs plan | positions+timing yes; intent no | HIGH without plan |
| Untraded entrying | tactical | solo contact with info mandate | trade position possible? | positions at death yes | MEDIUM |
| Over-rotation off single cue | tactical | IGL-called gamble/stack | second confirmation? team call? | cues yes; calls no | HIGH without comms |

Diagnostic priority at this stage: impact-vs-padding and role fit (FUND-021/024/028/030),
not mechanics volume.

## 4. High-level coordinated play — system execution under pressure

Errors become **plan-relative and marginal** (4):
- **ash (GamerLegion):** "everyone understands what they need to do in their roles… a team
  doesn't really work if you just throw in star players" + stats-only evaluation is "a poor
  way to do it" (acoR 0.88 rating but "what he's added to the team has been massive… extra
  voice") — Expert, https://www.dust2.us/news/61800/ash-a-team-doesnt-really-work-if-you-just-throw-in-star-players
- **B1ad3:** a "system" is "simply a way to make five players understand each other…
  patience, hard work, clearly explaining ideas"; mechanics/communication/synergy come
  *after* shared understanding — Expert, https://bo3.gg/news/b1ad3-the-cs2-system-is-simple
- **valens (EG Blueprint):** tier-one requires "learn while performing"; tier-2→tier-1
  transitions usually fail on first stint; role changes cause months-long resets;
  practice-observed improvement ≠ results — Expert,
  https://www.dust2.us/news/34627/valens-we-have-to-perform-while-were-in-this-tier-one-circuit-we-cant-just-be-learning
- **kassad:** pro losses reduce to "fundamentally bad CS… many simple mistakes" — fundamentals
  *persist* as failure mode at the top in subtler form (timing, spacing, pressure discipline) —
  Expert, https://www.hltv.org/news/29053/kassad-we-had-two-days-of-fundamentally-bad-cs-we-made-many-simple-mistakes-that-cost-us-both-games
- **zonic:** international-team "teamplay and tactical aspects are very limited" —
  coordination ceiling constrains which mistakes are fixable — Expert,
  https://www.hltv.org/news/33944/zonic-on-coaching-an-international-team-teamplay-and-the-tactical-aspects-are-very-limited

**Stage-D mistake character:** mistimed utility within executes (FUND-033); spacing drift
mid-round (FUND-029); discipline breaks when winning / anti-eco looseness (FUND-024/039);
role/plan conditioning **mandatory** — same positioning correct for an anchor, wrong for
a playmaker. Demo-unavailable evidence (calls, setups, mandates) makes C/D verdicts
provisional by construction — report "unverifiable from demo," never guess.

## 5. What persists vs what is stage-specific

- **Persist at all levels:** crosshair placement, counter-strafing, sound discipline,
  economy obedience, trade proximity, blinding/holding utility, advantage discipline.
  (kassad's "simple mistakes" at pro level + Refrag's per-bracket weighting: "metrics that
  separate 5k from 10k aren't the same as 25k from 30k" — Official,
  https://refrag.gg/blog/refrag-rating-explained/ — jointly imply same fundamentals,
  shifting *discriminative* margin.)
- **Stage-specific:** buy basics (beginner only); flash effectiveness (intermediate);
  impact-vs-padding and role fit (advanced FACEIT); plan-relative timing/spacing and
  pressure discipline (coordinated).

## 6. How expert coaches diagnose root cause vs symptom

Synthesized protocol (practitioner statements + decision science):

1. **Error-class separation first.** Mechanical (1)/(3) (missed spray, unsynced timing —
   demo-computable) vs tactical (4) (wrong choice given info) vs systemic (role/plan
   violation — needs plan). Template: ash's acoR (stat symptom 0.88 vs root contribution:
   voice, system fit) — never diagnose from the stat alone. (zews' per-round taxonomy:
   miscommunication / over-aggression / whiffed duel / caught-off-guard strat — same split.)
2. **Decision-vs-execution counterfactual.** Replay the decision point with the player's
   information set (no comms/gaze = stated assumption): *"If executed perfectly, would this
   still have been a bad decision?"* Yes → decision problem. No → execution problem.
   **Do not solve a decision problem with aim training.**
3. **Habit test = repetition + survival across outcomes.** One demo event is never a habit
   (Leetify's "what repeatedly happened, not why"; 30-day window — Official).
   A mistake surviving wins *and* losses is character; one appearing only in losses is often
   outcome noise. Per-habit, never per-event; aggregate severity over ≥N instances with a
   sample floor; cap findings, rank by expected value (frequency × controllability × effect).
4. **Role/plan conditioning.** valens (role resets take months) + ash (role clarity as team
   mechanism) + B1ad3 (system = shared understanding): every verdict states the assumed
   role/plan. **Opportunity confound:** "always takes isolated duels" may be a role effect
   (entry) — condition or systematically mislabel good aggressive-role players.
5. **Availability check.** An alternative must have been physically reachable (nav-graph
   travel time vs window) before calling the chosen action wrong.

**Diagnostic question bank:** (a) What info did the player plausibly have? (b) What would the
same action be worth if it worked (ex-ante value)? (c) Has it recurred ≥N matches regardless
of outcome? (d) Would the role/plan excuse it? (e) Which evidence is demo-present vs absent?

## 7. Intent vs outcome, hindsight, fair duels

- **Outcome bias (Measured, psychology).** Baron & Hershey (1988) — identical decisions rated
  better / decision-maker more competent when outcome favorable, even while endorsing that
  outcomes shouldn't count; 5 studies, medical + monetary —
  https://pubmed.ncbi.nlm.nih.gov/3367280/.
  Transfer: won-round actions over-credited, lost-round actions over-blamed. Mitigation: score
  ex-ante quality (info set at decision time); capture pre-round predictions before resolution;
  include won rounds in review (decision-density selection, not impact selection). Lab-demonstrated;
  CS transfer untested but the safer default (cost asymmetry: teaching repeat of a bad decision
  that worked).
- **Hindsight bias (Measured).** Fischhoff (1975/2003) — outcome knowledge raises postdicted
  likelihood and changes perceived evidence relevance; judges largely unaware —
  https://pmc.ncbi.nlm.nih.gov/articles/PMC1743746/.
  Transfer: "obviously he was there" reviews must reconstruct fog (knowable), not narrate
  from killcam. Telling reviewers "don't be biased" fails meta-analysis — only structural
  fixes work (pre-outcome capture, point-of-judgment prompts).
- **Inside-CS acknowledgment (Official).** HLTV Rating 3.0 Round Swing + Leetify
  win-probability weighting + Refrag bracket-relative weighting all exist because raw
  kills/ADR confound outcome with quality — but all are still **realized-state valuations
  (T1), not decision quality (T2)**: they credit lucky execution and punish correct plays
  that fail. T1 carries save/survivorship penalty, passive-play preference, zero-sum
  distortion — log all three with every severity reading.
- **Fair-duel framing (coaching synthesis, Community-labeled).** At advanced levels the frame
  is not "win more fair duels" but **"take fewer fair duels"**: create numbers, timing,
  crossfires, utility advantage so the duel is unfair in your favor (valens' "fair duels won /
  unfair-ification rate"). Demo proxy (1): fraction of kills with pre-existing advantage
  (numbers/flash/off-angle) vs isolated evens — computable; calling an even duel a "mistake"
  stays (4) with HIGH FP absent plan context.

## 8. Why strong aim plateaus (structural, not motivational)

1. **Practice quantity explains little at the top (Research-supported).** Pluss et al. 2021 —
   43 pro CS:GO players, ~32 h/week, 8 weeks, final R² = 0.30; per-SD practice K/D → +7.94%
   tournament score; quantity "limited association"; team random effect large —
   https://jses.net/wp-content/uploads/2021/02/Pluss-et-al.-2021.pdf.
2. **Perceptual-motor tests ceiling early (Research-supported).** Pluss et al. 2020 — 25 pro /
   25 rec / 25 control: pros beat non-players on speed-accuracy-tradeoff resistance but
   tests "limited" at pro-vs-committed-rec separation —
   https://www.journalofexpertise.org/articles/volume3_issue2/JoE_3_2/JoE_3_2_Pluss_etal.pdf.
   The motor substrate saturates; remaining gaps are spatial-cognition/decision
   (Miao et al. 2024 meta: overall g = 0.373, spatial g = 0.822; largely correlational —
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11316462/).
3. **Learning saturates non-monotonically (Measured).** Listman et al. 2021 — N=7,174 Aim Lab
   Gridshot, 682k runs: motor acuity improves over weeks; ~90% of daily benefit within
   ~30 min, peak ~1 h; 40–60% day-to-day retention; rate non-linear in baseline/volume —
   https://pmc.ncbi.nlm.nih.gov/articles/PMC8720934/.
   Do not diagnose "low effort" from hours; volume past ~1 h/day has diminishing returns.
4. **Practice is specific; transfer is unproven (Demonstrated mechanism + Experimental nulls).**
   Proteau et al. 1992 — learning tied to acquisition conditions; changing feedback degrades
   performance — https://pubmed.ncbi.nlm.nih.gov/1631322/.
   Roldan n=6 weak-positive (only avg-damage/round significant) vs Yeh et al. 2024
   pre-registered 20-h null on visual transfer (https://www.nature.com/articles/s41598-024-71987-y);
   KovaaK's pilot ICC .947–.995 *with authors warning off match extrapolation*
   (https://pmc.ncbi.nlm.nih.gov/articles/PMC10925653/);
   Lamers James & O'Connor 2023 attention-focus null in Aim Lab
   (https://pmc.ncbi.nlm.nih.gov/articles/PMC10368276/).
   **Aim-trainer scores are reliable measurements of themselves with no demonstrated
   match-transfer trial at high Elo. Aim-volume is the wrong default intervention.**
   Diagnose match aim from match demos, never trainer scores.
5. **Expertise = perception/decision speed, not multitasking (Research-supported).**
   FPS experts differ in stimulus-encoding speed, selective attention, anticipatory
   context use — not domain-general multitasking; "awareness" is prediction-matching
   (did behavior match contextual priors?), not "looking around more."

## 9. Metric caveats for reviewers (Official — vendor docs against themselves)

- Leetify color thresholds are percentile-relative (Poor = bottom 10%, Great = top 10%) and
  mostly rank-dependent; Aim/Utility/Positioning re-baselined with CS2 data (average reset
  to 50) — **a rating drop can mean the playerbase improved, not the player worsened**
  (https://leetify.com/blog/cs2-benchmarks/). Rating = performance, not skill; zero-sum;
  kill credit 35/30/15/20; saving rewarded via next-round win-prob.
- Refrag Rating normalizes 30+ metrics 0–1 then weights per Premier bracket; ADR/KAST bands
  are ranked-play approximations, role-conditioned (https://refrag.gg/blog/refrag-rating-explained/,
  https://refrag.gg/blog/cs2-stats-explained/).
- HLTV 3.0 (2025-08-20; refreshed 2026-10-01: 29,030 maps thru 2026-09-29, map-specific
  averages, Cache CT-sided in buys, negative-Swing-after-kill floored at 0, bomb-unpreventable
  kills give no Swing): Round Swing "slightly favors passive players," multi-kills diminish
  by design, early rounds under-weighted — "should not be treated as a perfect measure."
- All vendor metrics shift with game/economy changes (MR12 cited by Leetify) — date-stamp
  every benchmark; never hardcode thresholds into verdicts. No public validated decision-quality
  measure exists (Leetify = impact not intent; Refrag TTD conflates aim with selection;
  Scope composites undisclosed).

## 10. Ladder-reading honesty (no-Elo-threshold contract)

- Premier bands / per-map Competitive / FACEIT 1–10 tables situate stages, never define them;
  no-conversion rule across systems (Community-analyst,
  https://csstatlab.com/academy/rankings/cs2-ranks-explained).
- Rating mechanics: outcome-dominant, opponent-weighted, uncertainty-driven volatility;
  personal-stat role unpublished — never attribute rating moves to stat lines; diagnose
  match-winning habits instead (https://csstatlab.com/academy/rankings/how-cs2-rating-works).
- Band mythology warning (14.8k vs 15.2k not different species); confounds
  (maps, role difficulty, losing-habits, stack-vs-solo, tilt, frequency); trend-over-noise
  (1/5/20+ match ladder); placement-block demos are high-variance, not baselines;
  early-season verdicts carry recalibration uncertainty; non-Prime demos carry
  opponent-integrity uncertainty (cheat-distorted rounds pollute patterns).

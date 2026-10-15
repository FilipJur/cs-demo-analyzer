# G — Coaching Methodology, Learning Science, and the Validation Framework

**Slice:** §§13–15 of the brief. **Audience:** ~2000 FACEIT Elo (ex-2400) CS2 player, experienced developer. No beginner content.
**Compiled:** 2026-10-15. **Scope:** research only — no implementation.

**Evidence tags used throughout** (per the research contract):

| Tag | Meaning |
|---|---|
| **Demonstrated** | Directly evidenced by a primary artifact, experiment, or official documentation. |
| **Experimental** | From a controlled / pre-registered study (includes weak, null, and underpowered results). |
| **Research-supported** | Multiple studies or reviews; mostly observational or survey-level. |
| **Plausible-untested** | Reasoned extrapolation with no direct evidence in this domain. |
| **Infeasible** | Ruled out by recorded fact, cost, or physics. |

**Reading note on provenance.** CS coaching is largely oral tradition. Where a claim comes only from coaching-vendor SEO content (Boosteria, GapTo10, RankRise, Upforge, csstatlab, cs2lore …), it is **quarantined and labelled `VENDOR-UNVERIFIED`** — it is admissible only as an artifact of *what coaches claim they check*, never as evidence a method works. Peer-reviewed work, Valve documentation, and first-person HLTV coach/analyst interviews carry the load.

**Mapping of the four brief items to sections.** §13 = item 1 (coaching methodology). §14 = items 2 and 3 (learning science, feedback-loop design). §15 = item 4 (evaluation framework, 10 test questions, baseline-before-AI).

**Interface with sibling briefing slices (avoid duplication, avoid contradiction).**

| Sibling slice | Owns | This slice's dependency on it |
|---|---|---|
| `C-data-fogofwar` (§6) | Per-tick **information-state** reconstruction: LOS raycasting, smoke/flash occlusion, the `spotted`-mask verdict, the `omniscient / confirmed / inferable / relayed / unknown` representation, and the raw fact inventory. | §13.7 and §15.13 **Q3/Q5** are stated in terms of that representation. The claim here that "fog of war is only inferable" matches C's verdict that the `spotted` mask is "good as a noisy corroborator … and bad as ground truth". |
| `D-mistakes` (§7) | The **mistake taxonomy** (52 classes), the fact-vs-verdict distinction, detection-feasibility tiers, and the **fact layer** of validation (cross-parser agreement, hand-audited rounds). | §15.2's label set is the *judgment* counterpart to D's taxonomy. D's §7 explicitly delegates "feedback-efficacy design" to this slice — that is §14.11, §15.13 Q10, and §15.14 here. |
| `E-longitudinal` | Cross-match aggregation, cohort/reference distributions, stability estimates over time. | Supplies the denominator and reference population for §13.3 (habit detection) and §15.13 **Q4**. |
| `F-ai-arch` | Model/prompt architecture, cost, retention. | §15.7's pinning/migration discipline and §15.12's baseline B2 (strong LLM without domain signal) are constraints on that architecture. |

---

## §13 — How excellent CS coaches actually review demos

### 13.0 Executive answer

Three things are well-supported by primary sources, and three things are folklore.

**Supported:**
1. Top-level review is a **behaviour/decision test, not a statistics test**. Data filters a longlist; the demo decides. kassad, ash, valens, DeMarsDeRover all say versions of this in the same 2024 HLTV feature.
2. Review works by **converting observations into repeatable drilled actions**, not into commentary (zonic's counter-call; Astralis "double-nade" drilling).
3. Coaches **explicitly separate error classes** (mechanical vs decision vs macro vs mindset vs communication vs variance) before prescribing anything.

**Folklore / unverified:**
4. The popular "review order" frameworks (macro → micro → utility; root-cause-before-symptom; one-habit-per-review) are vendor content with no citation and no efficacy evidence. There is **no peer-reviewed study of CS demo-review methodology** (`Plausible-untested`, absence established by search across PubMed/PMC/JSES/Collabra).
5. "Aim is the ceiling" / "aim isn't the problem at high Elo" are both asserted; the actual evidence points to **perception and decision factors** separating experts from amateurs, but that evidence is largely cross-sectional.
6. Outcome-blind review is a sound transfer from decision science (Baron & Hershey 1988 is a robust lab result) but is **untested in CS**.

---

### 13.1 What coaches look at first, and why ordering matters

**13.1.1 — The first filter at top level is pressure behaviour, mid-round reaction, and initiative — not the scoreboard.** `Research-supported`
kassad (Aleksandar Trifunović): *"There are dozens of more important factors when making a team… demo reviews mainly focused on seeing how the player handles high-pressure situations, how he reacts to certain situations happening mid-rounds, does he have the amount of initiative needed for his position, decision making."* He states flatly: *"Stats aren't that important when choosing new players."*
HLTV, *Why we're still waiting for Counter-Strike's data revolution*, 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution

The same feature documents that 2024 scouting is still done *"in much the same way it was in 2016"*: a coach, an IGL and an org rep sieve a longlist **by watching demos** and checking references from former teammates.

**13.1.2 — Where data is used, it narrows the list; the demo still decides.** `Research-supported`
- ash (GamerLegion coach), on the Skybox-driven search that found FL4MUS: *"the statistics make the shortlist, and then from there I go through and break down if the numbers are that good, is it sustainable the way he's playing, can he fit in a system."* Also: *"I literally had no idea who FL4MUS was."*
- DeMarsDeRover (Liquid analyst): *"The stats can help us look at a wider range of players… get us a shortlist… [Analysts] are not as experienced as the players when it came to the eye test."*
Same source, HLTV 2024-10-28.

**13.1.3 — The one documented, verifiable example of demo study producing a mid-match decision.** `Demonstrated`
zonic, ESL One New York 2016 vs G2: *"I saw a couple of demos before the match where they were either explosive on B or doing the smoke line on A, and when they had done both of those, I took a timeout and said 'They're going to try and do an A split now, go short.' … And they did exactly what I thought."*
HLTV, 2016-09-30 — https://www.hltv.org/news/18798/zonic-we-had-a-way-better-ct-side

This is the shape of a *useful* review output: a conditional, falsifiable prediction, not a verdict. It is also the shape an AI coach should imitate — "given this evidence, expect X" — because it is testable against the following rounds.

**13.1.4 — Review is used to build drilled routine, not to deliver commentary.** `Research-supported`
Xyp9x on zonic: *"Thanks to zonic it's become a thing that we have to find spots we can double-nade."* HLTV, 2018-04 — https://www.hltv.org/news/23626/xyp9x-thanks-to-zonic-its-become-a-thing-that-we-have-to-find-spots-we-can-double-nade
zonic also described maintaining a "deep playbook" record of practice sessions/maps. HLTV, 2019-04 — https://www.hltv.org/news/26567/zonic-we-have-a-deep-playbook-and-it-worked-out-even-if-we-had-a-bit-of-a-rocky-start

**13.1.5 — On ordering: the only coach-sourced statement of *what comes first* is "the problem", not "the category of play".** `Plausible-untested`
B1ad3's documented model classifies opponents (known / new / map-specific) and treats the veto as preparation, and he separates *"mistakes in decision-making and macro analysis"* from mechanical error while valuing mindset — HLTV 2023-05 https://www.hltv.org/news/34073/b1ad3-as-navi-this-is-the-main-problem-we-always-look-for-the-trophy ; 2024-04 https://www.hltv.org/news/38801/b1ad3-i-didnt-expect-to-win-a-major-so-fast ; 2026 https://www.hltv.org/news/45287/b1ad3-we-were-close-to-making-some-changes .
No coach interview found states a fixed macro→micro→utility order. **VENDOR-UNVERIFIED** sources that do: Boosteria https://boosteria.org/guides/cs2-demo-review-guide-2026-analyze-gameplay-step-step ; GapTo10 https://gapto10.com/guides/cs2-demo-review-framework/ ; Upforge https://upforge.gg/blog/cs2-demo-review-workflow-coaching ; cs2lore https://cs2lore.com/blog/game-mechanics/cs2-demo-review-guide (all accessed 2026-10).

**Design implication.** An AI reviewer should not claim a validated review order. It should claim a *convergent* one: prioritise by (a) frequency of occurrence, (b) controllability by the player, (c) effect size on round outcome, (d) whether the same behaviour appears in rounds that were *won* (see §13.5). Criteria (a)–(d) are the operational version of "one habit per review" and are defensible without claiming a validated ordering. Note that this priority rule is itself `Plausible-untested` — and §15.7 specifies how to test it.

**13.1.6 — Data-augmented review exists at the highest level, and its features are the interesting part.** `Research-supported` (single team, self-reported)
valens (Major-winning coach, Cloud9/EG): EG built an internal rating ("EGR") factoring *"communication, utility quantity, utility quality, mechanical skill, and how well you perform in moments that really dictate the outcome of a game."* As far back as 2019 they combined in-game data **with communication files** to analyse who was over-calling or under-calling. The emphasis is on *"how many 'fair duels' a player wins and how often a player can make a duel 'unfair' in their favor."* HLTV 2024-10-28.
valens' own caveat: *"The majority of CS, you need to have a feel for the game."* Data is *"an enhancer… not a miracle worker."*

Note the transferable concept: **fair-duel win rate and "unfair-ification" rate** are decision-relevant aggregates that survive outcome noise far better than K/D. They are exactly the kind of derived metric §15 should evaluate.

---

**13.1.7 — "Good at CS" is itself contested, and the disagreement is between stakeholders, not just methods.** `Research-supported` (consensus framework)
Sharpe et al. (2023), *Journal of Electronic Gaming and Esports* 1(1) — a Delphi panel (researchers, practitioners, coaches, analysts, professionals) over a review identifying 32 performance variables, separating **outcome performance** (score, kills, rank) from **action performance** (reaction/response time, shooting accuracy, mouse control), **task performance** (contribution to objectives) and **contextual performance** (teamwork/communication). Professional players preferred match outcomes and game score; researchers and practitioners preferred action measures. doi:10.1123/jege.2022-0017 — https://doi.org/10.1123/jege.2022-0017
→ **Direct consequence for §15's Q9** ("do recommendations correspond with expert assessments?"): *which* experts are asked is a design variable that changes the answer. A panel of pros and a panel of analysts will not agree on what "correct" means, and the eval must say which panel it used and report the disagreement.

---

### 13.2 Symptom vs root cause

**13.2.1 — Coaches separate error *classes* explicitly; this is the practitioner form of root-causing.** `Research-supported`
- zews (Liquid, 2024) gives a concrete per-round taxonomy: *"just a miscommunication, over-aggression, it can be a bad whiffed duel, it can even be some strat that we were caught off guard."* He also notes his own sessions are *"20-25% of the tactical stuff"* and mostly personality management, and that the process is *"all a collaboration."* HLTV, 2024-01-24 — https://www.hltv.org/news/38013/zews-interview-naf-twistzzs-growth-shaping-liquids-new-foundation-skullzs-process
- ImAPet (CLG) treats clutch outcomes as variance rather than reviewable fault — *"some players just have the better ability to clutch… All you can do is watch the VoD and try to improve on it"* — while his review method is *"breaking down their defaults and saying what will work and what won't work."* HLTV, 2017-06-19 — https://www.hltv.org/news/20757/imapet-i-just-watch-a-lot-of-demos

**13.2.2 — The mechanism: outcome quality and decision quality must be scored separately.** `Demonstrated` (lab) / `Plausible-untested` (CS)
Outcome bias: Baron, J. & Hershey, J.C. (1988), *Outcome bias in decision evaluation*, J. Pers. Soc. Psychol. 54(4):569–579. In five studies, subjects rated the **same** decision process as better when it turned out well — despite having been told the decision-maker possessed all relevant information. Critically: *"subjects who were asked felt that they should not consider outcomes in making these evaluations, [but] they did so."* PMID 3367280 — https://pubmed.ncbi.nlm.nih.gov/3367280/
No CS-specific study of outcome or hindsight bias in demo review was found.

**13.2.3 — A defensible root-cause chain for CS2.** `Plausible-untested` (synthesis)
```
Outcome → first observable mistake → decision error or execution error →
repeated pattern (habit) → underlying cause → training intervention
```
The load-bearing diagnostic is the decision/execution split, expressed as a counterfactual question: *"if I had executed perfectly, would this still have been a bad decision?"* Yes → decision problem. No → execution problem. Do not solve a decision problem with aim training. **VENDOR-UNVERIFIED** as a documented template (e.g. cs2lore https://cs2lore.com/blog/game-mechanics/cs2-demo-review-guide ; racoon.gg https://racoon.gg/counter-stirke-2/blog/cs2-demo-review-guide-analyze-gameplay-spot-flaws), but it is the natural operationalisation of zews' and zonic's error-class separation, and it is testable (§15).

**13.2.4 — What the demo can and cannot prove about a decision.** `Demonstrated`
- The demo does **not** contain voice comms, has never contained them, and team chat in demo files became encrypted in the 2026-09-09 CS2 update: *"Chat is now encrypted in demo files using the same rules as CS:GO. Team chat is no longer readable when playing back demo files."* Valve patch notes, 2026-09-09 — https://www.counter-strike.net/news/updates ; extractor project confirming the absence of voice: https://github.com/DandrewsDev/CS2VoiceData
  → **Consequence:** any claim about "you should have known because a teammate called it" is *unfalsifiable from the demo alone* and must never be asserted by an automated reviewer.
- Fog of war is only *inferable*: available per-tick fields include X/Y/Z, `pitch`/`yaw`, and the radar mask `m_bSpotted` / `m_bSpottedByMask` (`spotted`, `approximate_spotted_by` in demoparser2 — https://github.com/LaihoE/demoparser ). There are no rendered frames, no FOV-accurate occlusion, no audio. See §13.7.

---

### 13.3 Habit detection

**13.3.1 — The practitioner proxy for a "habit" is repetition across rounds plus survival across outcomes.** `Research-supported` (by construction of coach workflow)
The review output that coaches actually produce is a *rule* ("find spots we can double-nade"; "never re-peek alone after first contact" as the vendor form). Detecting a habit therefore requires the same event recurring enough times to be distinguishable from variance.

**13.3.2 — Statistical anchor for how much repetition is needed.** `Research-supported`
Sports-metric meta-analytics gives the formal vocabulary for "is this pattern real?": **discrimination** (does it separate), **stability** (does it persist for the same player across time), **independence** (does it add information beyond existing metrics). A player-level behavioural pattern is only a habit if it is *stable* — which is directly measurable from a player's own match history and is the correct definition to put in the eval harness.
Franks, D'Amour, Cervone, Bornn (2016), *Meta-analytics: tools for understanding the statistical properties of sports metrics*, J. Quant. Anal. Sports 12(4):151–165 — https://arxiv.org/abs/1609.09830

**13.3.3 — Multi-match, not single-match, is where habits become visible.** `Plausible-untested` in CS specifics; supported by the stability requirement above.
Any product that reports "your habit" from one demo is asserting stability from one sample. §15.4 (test question 4) makes this an explicit gate.

**13.3.4 — Beware the false-habit confound: opportunity.** `Plausible-untested`
A "habit" such as "always takes isolated duels" may be a *role* effect (entry player) rather than a behavioural one. This is the CS analogue of the sports-analytics position/role adjustment (HLTV's own *Target Rating* adjusts expected rating by position — https://www.hltv.org/news/38785/target-rating-identifying-over-and-under-performers-on-ct-side ; ash's Skybox use relies on role-split ratings). Any habit claim must be conditioned on role/position/context or it will systematically mislabel good players in aggressive roles.

---

### 13.4 Decision under uncertainty, fight selection, positioning, awareness

These are the four things §13.1's coaches named ("initiative", "mid-round reaction", "decision making", "fair duels"). The honest position is that **there is no validated metric for any of them in CS**, but there are usable *structurally defined* constructs.

**13.4.1 — Fight selection: the central concept is exposure count, i.e. how many enemies can see you at the moment of the fight.** `Plausible-untested` (community/practitioner consensus; no academic validation)
Community/practitioner definitions converge on: isolate one angle at a time, prefer fights where a *trade* is available within ~1 s, prefer fights where you hold the angle advantage (geometry, who sees whom first) — e.g. csstatlab https://csstatlab.com/academy/gameplay/peekers-advantage-explained and counterstrikewiki https://counterstrikewiki.com/Trade_Fragging (both `VENDOR-UNVERIFIED`, accessed 2026-10). These are *geometric* and therefore computable from a demo (positions + eye rays + occlusion), which makes "number of enemies with potential line-of-sight to the player at fight start" a defensible derived metric — with the caveat that it is potential visibility, not perception (§13.7).

**13.4.2 — Positioning is only meaningful relative to a role and a plan.** `Research-supported` (analogy) / `Plausible-untested` (CS specifics)
valens' "fair duel / unfair duel" framing and the role-adjusted rating practice are the professional version of "positioning". The generalisable measurement is *engagement fairness distribution*: what fraction of a player's duels were taken with a mechanical/positional/utility advantage, and how often did the player create such an advantage themselves. HLTV 2024-10-28.

**13.4.3 — "Initiative" is a coach-recognised construct with no public metric.** `Plausible-untested`
kassad lists *"does he have the amount of initiative needed for his position"* as a top scouting criterion (HLTV 2024-10-28). This is a role-conditional count of proactive actions (first to contest space, first util usage, first contact) weighted by whether the action was warranted. Building this is a *design* task; validating it is a §15 task.

**13.4.4 — "Awareness" in expert terms is selective attention and anticipation, not "looking around more".** `Research-supported`
Expert FPS players differ from novices mainly in **perceptual encoding speed, selective visual attention, and anticipatory use of game-specific context**, not in a domain-general multitasking capacity. Recent Counter-Strike work (230 players classified novice/skilled/emerging/expert) attributes the expert advantage primarily to faster stimulus encoding and motor-response execution, finding no reliable difference in decision-boundary/risk-caution parameters — White Rose eprint 246278, *First-Person Shooter Expertise: A Processing Speed, Not Multitasking, Advantage* — https://eprints.whiterose.ac.uk/id/eprint/246278/
Meta-analytic corroboration: Miao, He, Hou, Wang, Chi (2024), *Cognitive expertise in esport experts: a three-level model meta-analysis*, PeerJ 12:e17857 — 15 studies, 142 effect sizes, N=1,085, overall g = 0.373 (p = .012), spatial cognition g = 0.822 (p < .001); authors stress the evidence is *"largely correlational"*. PMCID PMC11316462 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11316462/
Player-perspective corroboration: top-level game-sport athletes describe deciding **intuitively under time pressure via if-then automatisms**, using contextual priors early and kinematic cues late to confirm/override, and explicitly describe a "control mechanism" — checking that the anticipated situation actually unfolded. Magnaguagno & Beck (2025), Front. Sports Act. Living 7:1653834 — https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1653834/full

**Design implication.** "Awareness" is not a state to be scored ("didn't check minimap"); it is a *prediction-based* construct. An evaluable question is: *at decision time, did the player's observed behaviour match what their contextual priors should have led them to expect?* That requires explicit priors, which is exactly what a demo-derived model can supply — and exactly what makes §15's "can it evaluate the actual information available" (test Q3) the hardest test in the set.

**13.4.5 — Prioritisation of rounds to review: rank by decision density, not by impact.** `Plausible-untested`
Nothing in the primary sources validates a specific round-selection rule. Note the tension: smartCoach's own positioning — *"Find the rounds that cost the match"* — is a **results/impact framing**, i.e. it selects rounds by outcome, which is exactly the outcome-bias trap that §13.2 warns about. A better default is to select rounds by *decision density* (moments where the player chose among plausible alternatives) and to include **rounds that were won** (§13.5).

---

### 13.5 Intent vs outcome, and hindsight-bias avoidance — the operational rules

**13.5.1 — Outcome bias is demonstrated; CS transfer is not.** `Demonstrated` (lab) / `Plausible-untested` (CS)
See 13.2.2. The practical conclusion is that outcome-blind review is the *safer* default even though its benefit is unproven — the cost of the alternative (teaching a player to repeat a bad decision because it worked) is asymmetric.

**13.5.2 — Ex-ante note-taking is the standard debiasing device in adjacent domains.** `Research-supported` (forecasting/debiasing)
Write the prediction *before* revealing the result: expected value/probability, reasoning, main uncertainty, best alternative, abort condition. Then compare across *many* situations rather than litigating one. Calibration-training literature supports the loop (record probabilistic predictions → wait → show individualised accuracy feedback) while warning that effects are task-specific, that training may lower confidence without improving accuracy, and that recent large-N tests found **null** results relative to controls (Martin et al. 2024, *Futures & Foresight Science*, N=610 and N=871 — https://onlinelibrary.wiley.com/doi/10.1002/ffo2.199 ). See §14.8.

**13.5.3 — Hindsight *instruction* fails; only *structural* fixes work.** `Demonstrated` (negative)
- Christensen-Szalanski & Willham (1991), *OBHDP* 48(1):147–168 — meta-analysis of 122 studies: weighted **r = .17** (95% CI .14–.20, ≈ d = 0.35); reliability-corrected r = .25; larger for unfamiliar tasks. https://doi.org/10.1016/0749-5978(91)90010-Q
- Guilbault et al. (2004), *Basic and Applied Social Psychology* 26(2–3):103–111 — 95 studies (d ≈ .39 overall hindsight effect); **interventions intended to reduce hindsight bias did not significantly lower it overall.** Telling a reviewer "don't be outcome-biased" does not work. https://doi.org/10.1080/01973533.2004.9646399
- What *does* work is a task-specific prompt at the point of judgment, and preserving the pre-outcome judgment: a 2024 forensic-risk study reduced induced hindsight bias in novices by stating explicitly that the later outcome was unavailable at the decision point (experts showed no induced bias) — https://doi.org/10.1080/24732850.2024.2396991 ; Salmen, Ermark & Fiedler (2023) found participants could lower post-outcome probability judgments when instructed to reason from the earlier perspective, and the last communicated judgment still influenced judgments two weeks later — https://pubmed.ncbi.nlm.nih.gov/35953669/
→ **This is a design requirement, not an attitude.** The pre-round prediction must be *captured by the system before the round resolves*, because that is the only mechanism with evidence behind it. Any "we will review outcome-blind" policy implemented as a written instruction to a human reviewer is the intervention class that failed meta-analysis.

**13.5.4 — Repeated-outcome, not single-outcome, adjudication.** `Plausible-untested` (CS) / `Research-supported` (EV framing)
The poker/EV framing is exact for the decision-theoretic content: decision quality is judged **ex ante**, outcome quality **ex post**, and a single result is weak evidence about decision quality. Baron & Hershey 1988 (URL above) is the canonical experimental result; the CS application is `Plausible-untested`.

**13.5.5 — Coaches do verbalise process-over-result, implicitly.** `Research-supported`
kassad weights decision-making as an attribute independent of result; zews rejects a single verdict for a lost round and names distinct causes; ImAPet separates clutch outcomes (variance) from reviewable faults. (All HLTV URLs above.) This is the practitioner standard the AI's output should match: **never** "you died, therefore you misplayed".

---

### 13.6 Aim specialists vs pro players vs analysts — and why strong aim plateaus

**13.6.1 — The three roles look at different objects.** `Research-supported`
- **Analyst / data**: constructs ratings and filters longlists; DeMarsDeRover — *"I didn't play the game at all"* — and doubts the efficiency of hiring data staff: *"These skills do not overlap."*
- **Pro coach**: the eye test plus systems, with data as a filter (ash) or an enhancer (valens); valens — *"the majority of CS, you need to have a feel for the game."*
- **Aim specialist**: measures isolated mechanics, with no model of decision quality.
All three from HLTV 2024-10-28 (URL above). The disagreement between analyst and coach is documented and live, not folkloric.

**13.6.2 — What aim specialists actually claim, and its evidentiary status.** `Demonstrated` (artifacts) / `Plausible-untested` (efficacy)
- AIMER7's guide (the canonical community document) decomposes aim into trainable sub-skills; it contains no controlled evidence of in-game transfer — https://steamcommunity.com/sharedfiles/filedetails/?id=1679977919
- Voltaic ranks are a designed aggregation (harmonic mean of subcategory scores; categories below a threshold are prevented from bottlenecking the rank), reset each season — https://voltaic.medium.com/voltaic-kovaaks-benchmarks-season-4-35f3e3fb7512 , https://app.voltaic.gg/benchmarks . No external validation that Voltaic rank predicts in-game duel outcomes was found.

**13.6.3 — The measurement platform is reliable; the transfer claim is not.** `Experimental`
KovaaK's test–retest ICC 0.947–0.995, n=10, with authors explicitly warning that real FPS play *"includes movement, positioning, game awareness, stress, target uncertainty, weapon mechanics, and other cognitive demands absent from isolated aim tasks."* Rogers, Trotter, Johnson, Desbrow, King (2024), Front. Sports Act. Living 6:1309991 — PMID 38469227 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10925653/

**13.6.4 — Motor-acuity learning in trainers is real, saturating, and non-monotonic.** `Research-supported` (N=7,174, observational)
Listman, Tsay, Kim, Mackey, Heeger (2021), *Long-Term Motor Learning in the "Wild"…*, Front. Hum. Neurosci. 15:777779: motor acuity (hits/sec) improved substantially over months with 40–60% day-to-day retention; accuracy improved only modestly; learning rate was a non-linear function of baseline level and practice amount; *"the greatest improvements in motor acuity were evident with about an hour of practice and 90% of the learning benefit was achieved by practicing 30 min per day."* PMCID PMC8720934 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8720934/
→ At high Elo, the *baseline* term dominates: the same daily volume yields less improvement. This is the mechanical part of the plateau.

**13.6.5 — Practice *quantity* explains little of pro tournament performance; team and practice-quality do more.** `Research-supported`
Pluss, Novak, Bennett, Panchuk, Coutts, Fransen (2021), JSES 5(1):69–76 — 43 pro CS:GO players, ~32 h/week, 8 weeks, final model R² = 0.30; per SD increase in **practice K/D** → +7.94% tournament score; practice quantity had *"limited association"*; the random effect (team) explained much variance. — https://jses.net/wp-content/uploads/2021/02/Pluss-et-al.-2021.pdf

**13.6.6 — Perceptual-motor tests separate pros from *non-players* but poorly separate pros from committed recreational players.** `Research-supported` (selection/ceiling signal)
Pluss et al. (2020), *Perceptual-motor Abilities Underlying Expertise in Esports*, J. Expertise 3(2):133–143 — 75 participants; pros were *"less susceptible to the speed-accuracy trade-off"* and faster than controls, but the authors conclude *"their ability to distinguish between professional and recreational esports players is limited."* — https://www.journalofexpertise.org/articles/volume3_issue2/JoE_3_2/JoE_3_2_Pluss_etal.pdf

**13.6.7 — Transfer from training to match performance is unproven, and the strongest null is pre-registered.** `Experimental` (null)
- The frequently cited Aim Lab→Valorant study is n=6, one week, no control, and only *average damage per round* reached significance (p≈0.029) while KAD, K/D, HS% and score/round did not; 1/6 improved HS%. Roldan & Prasetyo (2021), IEEE ICIEA 465–470 — https://ieeexplore.ieee.org/abstract/document/9436822
- A pre-registered 20-hour study found **no** transfer of action-FPS training to low-level visual discrimination: *"Our study found no evidence, in either accuracy or reaction time, that AVG training transferred to motion discrimination."* Yeh, Li, Huang, Liu (2024), Sci. Rep. 14:27864 — https://www.nature.com/articles/s41598-024-71987-y
- The broader literature carries a documented publication-bias critique: Hilgard, Sala, Boot, Simons (2019), *Overestimation of action-game training effects*, Collabra: Psychology 5(1):30.

**13.6.8 — Gains are specific to the conditions of practice — the mechanistic reason isolated drills under-transfer.** `Demonstrated` (foundational motor-learning)
Proteau, Marteniuk & Lévesque (1992), *A sensorimotor basis for motor learning: evidence indicating specificity of practice*, Q. J. Exp. Psychol. A — PMID 1631322 — https://pubmed.ncbi.nlm.nih.gov/1631322/

**13.6.9 — Synthesis: why strong aim plateaus at high Elo.** `Plausible-untested` (synthesis of 13.6.4–13.6.8)
Four compounding mechanisms, each independently evidenced:
1. **Saturating, non-monotonic learning** in the trained skill (13.6.4).
2. **Specificity of practice** — the trained task is not the match task (13.6.8), and the one clean pre-registered transfer test is null (13.6.7).
3. **Ceiling/selection effects** — the ability measures that separate pros from non-players do not separate pros from committed amateurs (13.6.6).
4. **The residual variance at the top is team/context and decision quality, not practice volume** (13.6.5, 13.6.4).

None of this proves "aim is not your problem at 2000 Elo". It does establish that **aim-volume is the wrong default intervention**, and that a system claiming otherwise must produce the transfer evidence §15.10 demands.

---

### 13.7 What a CS2 demo cannot tell you — hard constraints on any review claim

These are load-bearing for the eval framework: an AI reviewer that asserts any of the following is hallucinating *by construction*.

**13.7.1 — A demo is a network/replay stream, not video and not input capture.** `Demonstrated`
`CBaseUserCmdPB` contains `buttons_pb`, `viewangles`, `forwardmove`/`leftmove`/`upmove`, `impulse`, `weaponselect`, `mousedx`/`mousedy`, `random_seed`, and `repeated CSubtickMoveStep subtick_moves`. Source: SteamTracking/GameTracking-CS2 `Protobufs/usercmd.proto` — https://github.com/SteamTracking/GameTracking-CS2/blob/master/Protobufs/usercmd.proto

**13.7.2 — Voice comms are absent, and team chat became encrypted.** `Demonstrated`
See 13.2.4. Valve patch notes 2026-09-09: *"Chat is now encrypted in demo files using the same rules as CS:GO. Team chat is no longer readable when playing back demo files."* https://www.counter-strike.net/news/updates
→ Any "communication" feature built on 2025-and-earlier data is broken; any claim about what was called must come from a separate voice recording the player provides.

**13.7.3 — Sub-tick timestamps actions within server-update intervals, but the reconstruction algorithm is undocumented.** `Demonstrated` (Valve claim) + `Plausible-untested` (exactness)
Valve: *"Thanks to Counter-Strike 2's sub-tick update architecture, servers know the exact instant that motion starts, a shot is fired, or a 'nade is thrown… regardless of tick rate, your moving and shooting will be equally responsive and your grenades will always land the same way."* — https://www.counter-strike.net/cs2/features
Valve has not published how interpolation/lag compensation are reconstructed. Per-tick "exactly what happened" is therefore approximate by construction.

**13.7.4 — "Tick" is ambiguous; parser correctness depends on reading the tick interval from the file.** `Research-supported` (tooling docs)
CS2DemoKit documents the demo/frame tick vs absolute server tick distinction and warns that mixing them yields plausible-looking wrong timings — https://github.com/CS2OpenDev/CS2DemoKit . Valve MM runs 64 Hz with sub-tick; FACEIT runs 128-tick CS2 servers.

**13.7.5 — The command stream is delta-compressed and may contain server substitutes.** `Research-supported` (tooling docs)
CS2DemoKit: modern demos may store user commands as deltas against the previous command (`svc_UserCmds`), so reading only the full `data` field *"can report missing or stale buttons, movement, and subtick values"*; the server may also execute substitute commands when a client command is late. → Mouse-delta-derived "flick"/"crosshair placement" metrics are **indirect and corruptible**. https://github.com/CS2OpenDev/CS2DemoKit

**13.7.6 — Fog of war is only inferable, and the `spotted` mask is not a substitute.** `Demonstrated` (fields) / `Plausible-untested` (perception model)
Available: X/Y/Z, `pitch`/`yaw`, `spotted` (`m_bSpotted`), `approximate_spotted_by` (`m_bSpottedByMask`) — https://github.com/LaihoE/demoparser . Awpy's `VisibilityChecker` does a *static-collision-mesh raycast*, documented as visibility against map geometry, not a reconstruction of the rendered screen — https://awpy.readthedocs.io/en/latest/api.html . Missing: FOV-accurate occlusion, smoke as rendered volume, flash blindness as an image, client interpolation, what the client had actually received.
Three further constraints specific to the `spotted` field (established in the `C-data-fogofwar` slice, §5.6):
- `demoinfocs-golang`'s `IsSpottedBy()` carries the verbatim warning **"This is NOT 'Line of Sight' / FOV"**, and notes it "may not behave as expected with multiple spotters" — https://github.com/markus-wa/demoinfocs-golang (`pkg/demoinfocs/common/player.go`).
- demoparser2's "approximate" prefix has a concrete mechanism: the mask↔player resolution maps only mask bits 0..15 to controller ids 1..16, so even per-player attribution is a partial mapping.
- In a GOTV demo the mask most plausibly reflects the **GOTV/spectator client's** spotting rather than each player's own (`[INFERENCE]`, unverified).
→ **Correct phrasing: "potential line-of-sight reconstruction", never "what the player saw"; the `spotted` mask is a noisy corroborator, never a label.**

**13.7.7 — Sound is not stored; utility/vision effects only partially.** `Demonstrated`
Awpy exposes `smokes` and `fires` as one row per deployed cloud/burning inferno with position, thrower and `[start_tick, end_tick]`, and `blinds` with thrower, blinded player and duration — https://github.com/pnxenopoulos/awpy . That supports smoke-timing geometry, not rendered occlusion. No audio stream exists; "who heard what" is not recorded.
ESTA's parsed frames confirm the field inventory (40+ attributes per player; smokes/fires/bomb state as globals). Xenopoulos & Silva (2022), *ESTA: An Esports Trajectory and Action Dataset*, arXiv:2209.09861 — https://arxiv.org/html/2209.09861v1

**13.7.8 — Consequence for §15.** Tests Q1, Q3, Q5 and Q7 in §15.6 are all *grounding* tests against these constraints. Any reviewer that cannot cite a demo field for its claim is asserting beyond the artifact.

---

### 13.8 Improvement measurement (what coaches do, and what it costs)

**13.8.1 — Coaches measure improvement in behaviour, not in ratings.** `Research-supported`
zonic's "assign each player something to work on" after review (HLTV, *Become a pro: Player* — https://www.hltv.org/news/2129/become-a-pro-player) and the drilled-utility example (13.1.4) imply a target behaviour per player per block. The public tooling stack, by contrast, measures *ratings*.

**13.8.2 — Consumer ratings are relative, drift, and are explicitly not skill metrics.** `Demonstrated`
- Leetify Rating is zero-sum and win-probability-weighted (kill credit split 35% killer / 30% damage-dealers / 15% flash assist / 20% traded death), built on HLTV CS2 data, and Leetify itself says *"Leetify Rating is a performance metric, not a skill metric."* https://leetify.com/blog/leetify-rating-explained/
- Leetify's Aim/Utility/Positioning ratings are z-scores against benchmarks that drift; the 2024-03-27 recalibration moved an **unchanged raw score to a lower rating** because the playerbase improved over 2.5 years. https://leetify.com/blog/cs2-benchmarks/
- Scope.gg publishes concrete outputs (TTK, first-bullet accuracy, opening duels, flash time) but its composite formulas are undisclosed: https://scope.gg/
- Refrag Coach reports crosshair placement as *degrees of deviation*, counter-strafe %, TTD, spotted accuracy, and maps them to drills — https://refrag.gg/blog/what-is-refrag-coach/ — with no independent validation, and with TTD conflating aim, weapon, range, target motion and engagement selection.

**13.8.3 — The measurable-gain literature that does exist uses win-probability change and calibration, not ratings.** `Research-supported`
ESTA benchmarks evaluate win-probability models by **log loss and expected calibration error (ECE)**, reporting per-map ECE ≈ 0.033–0.061 — arXiv:2209.09861. This is the correct template for "did our model get better?" (see §15.8) and it is *not* the same question as "did the player improve".

**13.8.4 — No public, validated measure of decision quality exists.** `Plausible-untested` (absence established)
Leetify Rating is WP-delta (impact, not intent); Refrag's TTK/TTD conflate aim with engagement selection; Scope's composites are undisclosed. There is no labelled corpus of "correct/incorrect decision" in CS. **This is the central obstacle for §15 and the reason §15.9 requires a hand-labelled set.**

---

### 13.9 §13 contradictions and open questions

1. **Stats vs eye test is a live, unresolved industry disagreement** (kassad vs ash/valens vs DeMarsDeRover), and nobody has measured which produces better outcomes. HLTV 2024-10-28.
2. **Do aim trainers transfer at high Elo?** No adequately powered, pre-registered trial on CS2 rank or duel outcomes exists. The only transfer datapoint is n=6/1 week; the only pre-registered test is null.
3. **Are high-Elo gains decision-limited or mechanic-limited?** Pluss 2020 and Miao 2024 point at perception/decision, but both are largely cross-sectional with self-selection risk, and neither measured CS2 match play.
4. **Every consumer rating is relative and drifts** (Leetify's forced 2024 reset).
5. **Outcome bias is demonstrated in the lab but untested in CS review**; no study shows outcome-blind review improves player performance.
6. **Demo integrity limits are moving targets.** Team chat became encrypted 2026-09-09; any chat-based coaching feature dies with the patch.
7. **"Fog of war reconstructable per tick" is routinely asserted and is false as stated.** The `spotted` masks are a radar-spot flag, not a visibility model.
8. **No peer-reviewed study of demo-review method efficacy exists** — review ordering, root-cause-vs-symptom, and habit-detection are all workflow preferences, not validated methods.

---

### 13.10 §13 top sources

**Peer-reviewed**
1. Baron & Hershey (1988), *Outcome bias in decision evaluation*, JPSP 54(4) — https://pubmed.ncbi.nlm.nih.gov/3367280/
2. Listman et al. (2021), *Long-Term Motor Learning in the "Wild"…*, Front. Hum. Neurosci. 15:777779 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8720934/
3. Rogers et al. (2024), *KovaaK's aim trainer as a reliable metrics platform…*, Front. Sports Act. Living 6:1309991 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10925653/
4. Donovan et al. (2022), *Assessment of human expertise and movement kinematics in FPS games*, Front. Hum. Neurosci. 16:979293 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9744923/
5. Yeh et al. (2024), *Comparing conventional and action video game training in visual perceptual learning* (Registered Report), Sci. Rep. 14:27864 — https://www.nature.com/articles/s41598-024-71987-y
6. Roldan & Prasetyo (2021), *Evaluating the Effects of Aim Lab Training…*, IEEE ICIEA — https://ieeexplore.ieee.org/abstract/document/9436822
7. Pluss et al. (2021), JSES 5(1):69–76 — https://jses.net/wp-content/uploads/2021/02/Pluss-et-al.-2021.pdf
8. Pluss et al. (2020), *Perceptual-motor Abilities Underlying Expertise in Esports*, J. Expertise 3(2) — https://www.journalofexpertise.org/articles/volume3_issue2/JoE_3_2/JoE_3_2_Pluss_etal.pdf
9. Miao et al. (2024), *Cognitive expertise in esport experts: a three-level model meta-analysis*, PeerJ 12:e17857 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11316462/
10. Proteau et al. (1992), *…specificity of practice*, PMID 1631322 — https://pubmed.ncbi.nlm.nih.gov/1631322/
11. White Rose, *First-Person Shooter Expertise: A Processing Speed, Not Multitasking, Advantage* — https://eprints.whiterose.ac.uk/id/eprint/246278/
12. Magnaguagno & Beck (2025), *Decision-making process in game sports…*, Front. Sports Act. Living 7:1653834 — https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1653834/full
13. Franks et al. (2016), *Meta-analytics…*, arXiv:1609.09830 — https://arxiv.org/abs/1609.09830
14. Xenopoulos & Silva (2022), *ESTA…*, arXiv:2209.09861 — https://arxiv.org/html/2209.09861v1

**Practitioner / first-person (CS)**
15. HLTV, *Why we're still waiting for Counter-Strike's data revolution*, 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution
16. HLTV, *zonic: "We had a way better CT side"*, 2016-09-30 — https://www.hltv.org/news/18798/zonic-we-had-a-way-better-ct-side
17. HLTV, *ImAPet: I just watch a lot of demos*, 2017-06-19 — https://www.hltv.org/news/20757/imapet-i-just-watch-a-lot-of-demos
18. HLTV, *zews interview…*, 2024-01-24 — https://www.hltv.org/news/38013/zews-interview-naf-twistzzs-growth-shaping-liquids-new-foundation-skullzs-process
19. HLTV, Xyp9x on zonic's double-nades, 2018-04 — https://www.hltv.org/news/23626/xyp9x-thanks-to-zonic-its-become-a-thing-that-we-have-to-find-spots-we-can-double-nade
20. HLTV, *Become a pro: Player*, zonic — https://www.hltv.org/news/2129/become-a-pro-player
21. HLTV, B1ad3 interviews — https://www.hltv.org/news/38801/ ; https://www.hltv.org/news/45287/ ; https://www.hltv.org/news/34073/
22. HLTV, *Target Rating: Identifying over and under performers on CT side* — https://www.hltv.org/news/38785/target-rating-identifying-over-and-under-performers-on-ct-side

**Official / technical**
23. Valve, CS2 features / sub-tick — https://www.counter-strike.net/cs2/features
24. Valve, CS2 update notes (2026-09-09 chat encryption) — https://www.counter-strike.net/news/updates
25. SteamTracking/GameTracking-CS2 `usercmd.proto` — https://github.com/SteamTracking/GameTracking-CS2/blob/master/Protobufs/usercmd.proto
26. awpy — https://github.com/pnxenopoulos/awpy ; https://awpy.readthedocs.io/en/latest/api.html
27. demoparser2 — https://github.com/LaihoE/demoparser
28. CS2DemoKit — https://github.com/CS2OpenDev/CS2DemoKit

**Vendor (method claims only; not efficacy evidence)**
29. Leetify — https://leetify.com/blog/leetify-rating-explained/ ; https://leetify.com/blog/cs2-benchmarks/
30. Scope.gg — https://scope.gg/ ; Refrag — https://refrag.gg/blog/what-is-refrag-coach/ ; Voltaic — https://app.voltaic.gg/benchmarks ; AIMER7 — https://steamcommunity.com/sharedfiles/filedetails/?id=1679977919

---

## §14 — Learning science, and the design of the feedback loop

### 14.0 Executive answer

Five findings should change the product's shape, and three popular heuristics should be dropped.

**Adopt:**
1. **Deliberate practice = error-specific, feedback-closed practice.** Hours are a near-zero predictor at this player's level (≈1% of variance *among elites*; β = .02 for CS:GO rank in the only registered report). The product must never sell volume.
2. **Spacing is the cheapest, most robust lever** (motor d = 0.97 for simple psychomotor; classroom d = 0.54 in a 2025 meta-analysis) — and a 162k-player LoL dataset agrees that distributed > massed.
3. **Structured after-action review is the best-supported intervention in the whole stack** (Tannenbaum & Cerasoli 2013: overall d = 0.67; aligned/team d = 1.20, non-aligned d = 0.41).
4. **Implementation intentions (if–then plans) are the one habit technique with strong controlled evidence** (Gollwitzer & Sheeran 2006: 94 tests, N=8,461, d = 0.65).
5. **Occlusion-based anticipation training is the highest-value, best-evidenced buildable feature** (2024 *Sports Medicine* meta: d = 1.21 overall; field transfer d = 0.85) — and it is constructible from demos the system already has.

**Drop:**
6. **"Reduce feedback frequency to improve learning."** The guidance hypothesis failed its best meta-analysis (McKay et al. 2022: 61 papers, 75 experiments, 2,228 participants; no reliable reduction benefit at acquisition, immediate retention, or delayed retention).
7. **"Random/interleaved practice is better."** True in the lab (transfer SMD ≈ 0.55, sensitivity-adjusted ≈ 0.38, I² ≈ 86%) but the canonical pattern appears in only ~20% of outcomes in the critical multilevel review and does **not** generalise to applied sport skill.
8. **"Long detailed reports = good coaching."** Expertise reversal is large (reversal contrast d = 0.971 vs novices; high-assistance is *worse* for high-prior-knowledge learners) and seductive details measurably reduce transfer (g ≈ −0.4). For a 2000-Elo ex-2400 player, verbosity costs learning.

---

### 14.1 Deliberate practice: the honest numbers

**14.1.1 — The construct is narrower than its popular citation, and "10,000 hours" was never a law.** `Research-supported` (construct) / `Infeasible` (as a threshold claim)
Ericsson, Krampe & Tesch-Römer (1993), *Psychological Review* 100(3):363–406: deliberate practice = individualised, effortful activity explicitly designed to improve specific aspects of performance, with immediate informative feedback, repeated with refinement, typically teacher-designed. The contrast set is explicitly play, competition, paid work, and exposure. The 10,000 figure is an *average for the best violin students in one conservatory sample*, not a threshold. https://doi.org/10.1037/0033-295X.100.3.363

**14.1.2 — Practice explains a minority of variance overall, and almost none among elites.** `Research-supported`
- Macnamara, Hambrick & Oswald (2014), *Psych. Science* — 88 studies, 111 samples, 157 effect sizes, N=11,135: pooled r ≈ .35; by domain: games 26%, music 21%, sports 18%, education 4%, professions <1%. Corrigendum revises some domain values but not the pattern. https://journals.sagepub.com/doi/full/10.1177/0956797614535810
- **Macnamara, Moreau & Hambrick (2016), *Perspectives on Psych. Science* — sports: 18% overall, but only ~1% among elite performers.** This is the load-bearing number. https://journals.sagepub.com/doi/10.1177/1745691616635591

**14.1.3 — The preregistered replication halved the flagship result and found best ≈ good.** `Demonstrated`
Macnamara & Maitra (2019), *Royal Society Open Science* — results-blind preregistered replication of the violinist study (39 violinists): accumulated "practice alone" through age 18 → **η² = .26** (vs ~48% originally); **the best group had not practised significantly more than the good group**; the discriminator was between good and less-accomplished. https://doi.org/10.1098/rsos.190327

**14.1.4 — In CS:GO specifically, retrospective practice volume predicts rank at β = .02.** `Experimental` (registered report)
Martončik et al. (2024), *Collabra: Psychology* — 186 CS:GO + 411 LoL ranked players; deliberate practice → rank: **β = .02 (CS:GO)**, β = −.01 (LoL), both confirmed nulls at prespecified thresholds. https://online.ucpress.edu/collabra/article/10/1/117677/200964/Psychological-Predictors-of-Long-term-Esports

**14.1.5 — The dispute is definitional and unresolved: 1% – 18% – 29% – 61%.** `Research-supported` (the disagreement is the finding)
Ericsson & Harwell's reanalysis reports ~29%, rising to ~61% after attenuation correction; Macnamara et al. counter that removing the allegedly invalid practice categories moved the estimate only 18% → 17%, and that the definition narrowed after the result was known. https://pmc.ncbi.nlm.nih.gov/articles/PMC6824411/ ; https://journals.sagepub.com/doi/10.1177/1745691616635600
**Product floor:** hours are not a usable predictor; practice *quality* is unquantified but the only remaining candidate, which is exactly what a demo-derived analysis system can supply.

**14.1.6b — At the extreme, professionals accumulate 16,000+ game-specific hours over ~10 years, and the players themselves do not believe the grind works.** `Experimental` (observational/qualitative)
Pluss et al. (2022), *Computers in Human Behavior* 137:107421 — 52-week longitudinal study of professional vs semi-professional players: same weak quantity–performance relation; professionals trained more (30.9 ± 8.2 h/week game-specific vs 24.7 ± 3.6) without the volume predicting expertise. Abbott et al. (2022) found LoL players **perceive their own training as ineffective** and believe the "grind" approach is not the best route to expertise. https://doi.org/10.1016/j.chb.2022.107421
→ Useful as a diagnostic: if the player's own belief is "I need more hours", that belief is the thing to test, not the thing to satisfy.

**14.1.7 — Massed grinding is measurably worse than distributed play at scale — with a small effect size.** `Experimental` (large-N observational)
162,417 LoL players' first 100 ranked matches: most-distributed group (95 matches over 136–150 days) vs most-massed (1–15 days) → GPM 399.71 vs 392.81 (**d = 0.146**), KDA 3.76 vs 3.27 (**d = 0.265**), both p < .001 after matching on early performance. The *timing* of breaks mattered negligibly. Limits: observational, ~2/3 of raw data dropped in preprocessing, motivation/intensity confounds not ruled out. https://doi.org/10.1371/journal.pone.0275843
→ The direction is consistent with the experimental spacing literature (14.6.1), but the effect is an order of magnitude smaller than the motor-learning laboratory numbers. Do not oversell "play fewer games at a time".

---

### 14.2 Motor and perceptual-cognitive learning

**14.2.1 — Specificity of learning: skill is bound to the information structure of practice.** `Research-supported` (lab) / `Demonstrated` (foundational)
Proteau et al. (1992) — training with a particular visual-feedback condition and then altering available visual information produced substantial decrement. Later reinterpretation: part of this is an optimised *movement plan* that becomes inefficient when conditions change. https://pubmed.ncbi.nlm.nih.gov/1631322/
**Transfer-appropriate processing** (Morris, Bransford & Franks 1977) is the mechanism: transfer depends on overlap in the *operations* engaged, not surface similarity. https://www.sciencedirect.com/science/article/pii/S0022537177800169

**14.2.2 — Contextual interference is real in the lab, weaker and conditional in application.** `Demonstrated` (lab) / `Research-supported` (applied, limiting)
- Czyż et al. (2024) transfer meta-analysis: 34 studies, 86 effect sizes, N=1,421 — **SMD = 0.55** [0.25, 0.86]; adults 0.54; sensitivity-adjusted ≈ 0.38; **I² ≈ 86%**. Retention meta: pooled ≈ 0.63, sensitivity ≈ 0.45. https://pmc.ncbi.nlm.nih.gov/articles/PMC11349744/
- Ammar et al. (2024), *Educational Psychology Review* — 36 studies, 264 effect sizes: the canonical pattern appeared in only **~20%** of outcomes; high-interference practice showed **no significant overall advantage** in pre-to-retention improvement for gross-motor/applied sport skills. https://link.springer.com/article/10.1007/s10648-024-09892-z
- Discriminator: variability helps when variants require **different action plans** (generalised motor programs), and is inconsistent when they differ only in parameters. https://pubmed.ncbi.nlm.nih.gov/15064191/
- "More is not better": structured *moderate* variability beat extreme variability in at least one motor task. https://pmc.ncbi.nlm.nih.gov/articles/PMC11212619/

**14.2.3 — Reduced feedback frequency (the guidance hypothesis) failed meta-analysis.** `Demonstrated` (as a null)
McKay et al. (2022) — 61 papers, 75 experiments, 2,228 participants: no significant overall benefit of reduced relative feedback frequency; **no reliable crossing-over** from frequent-feedback advantage in practice to reduced-feedback advantage in retention; many studies severely underpowered. https://www.sciencedirect.com/science/article/pii/S1469029222000334
Counterpoint that survives: **frequency is not the active ingredient — what you attach feedback to is.** Wulf et al. found 100% feedback better than 50% for a *complex* task; bandwidth feedback (only outside a tolerance) has shown automatization benefits; and feedback after *good* trials produces better retention than after poor trials (Chiviacowsky & Wulf 2007), as does learner-selected feedback timing (2002, 2005). https://www.sciencedirect.com/science/article/abs/pii/S0167945715300555 ; https://www.tandfonline.com/doi/full/10.1080/02701367.2007.10599402

**14.2.3b — The reversal effect is largely a laboratory artefact, and does not hold for sport tasks.** `Experimental` (independently corroborating null)
Marschall, Wiemeyer & Bund's meta-analysis of 40 studies: the global reversal effect is tiny (acquisition Δ = −0.21, late retention Δ = +0.22) and unstable — a fail-safe N of only **2–3** zero-effect studies erases it. It appeared in only 7 of 20 moderator factor levels, essentially only in simple **laboratory** tasks with >90 acquisition trials; **no systematic frequency effect was found for sport tasks.** Sampling bias was directly demonstrated: 39/43 of non-includable studies did *not* confirm the reversal, vs 14/25 among included studies. https://uol.de/f/4/inst/sport/download/andreasbund/publikationen/Publikation_44.pdf
This independently corroborates McKay et al. (14.2.3) from a different literature and with a different failure mode (publication/sampling bias).

**14.2.3c — Learner *control* over feedback is the variable that survives: acquisition null, retention and transfer positive.** `Experimental` (with detected publication bias)
Wang et al. (2025), *Behavioral Sciences* 15(9):1291 — 29 RCTs, 1,147 participants: self-controlled vs passively-received feedback → acquisition SMD = 0.199 (ns), **retention SMD = 0.630**, **transfer SMD = 0.684**; vs schedule-matched (yoked) controls → acquisition 0.175 (ns), retention 0.695, transfer 0.648. **Significant publication bias was detected in the retention and transfer analyses (Egger p < 0.01)**, so magnitudes are optimistic. https://doi.org/10.3390/bs15091291
→ The design rule: **let the player decide *when* and *about what* to receive analysis** (an on-demand report over a fixed push schedule), and grade the intervention on later games, not on the review session.

**14.2.4 — Expert advantage is anticipatory and search-efficient.** `Demonstrated` (meta-analytic)
Mann, Williams, Ward & Janelle (2007), *JSEP*: expert advantage in response time rpb = **.43** (anticipation) and **.31** (decision-making); experts make **fewer fixations** (rpb = .44 for decision-making) with **longer fixation durations**. https://pubmed.ncbi.nlm.nih.gov/17968048/

**14.2.5 — Perceptual expertise is structured long-term-memory retrieval.** `Demonstrated` (highly replicated, with the critical control)
Chase & Simon (1973): expert recall superiority appears for legal, structured chess positions and **largely vanishes for random positions** — the null is the control that makes the claim credible. Template theory extends chunking to larger schematic structures. https://doi.org/10.1016/0010-0285(73)90004-2 ; https://doi.org/10.3758/BF03200937

**14.2.6 — Perceptual-cognitive training transfers to near tasks, at ~40% of the trained-task effect.** `Research-supported`
2024 systematic review + meta-analysis (22 studies, 45 effect sizes): trained/lab task **ES = 1.51** [0.98, 2.05]; **on-court performance ES = 0.65** [0.15, 1.16]. Stimulus-format subgroups (screen video 0.19 with CI including zero; life-size 2D 0.46; 3D/VR 0.96) — **the subgroup difference was not significant (p = .449)**, 3D/VR I² = 84.7%. https://pmc.ncbi.nlm.nih.gov/articles/PMC11505547/

**14.2.7 — Temporal-occlusion training is the best-evidenced buildable feature.** `Research-supported`
2024 *Sports Medicine* meta-analysis (12 intervention studies, 25 effect sizes, N=248): overall **d = 1.21** [0.83, 1.59]; video-test transfer 1.26; **field/perception–action transfer 0.85**. The paradigm — clip cut *before* the critical action — is directly implementable from a demo pipeline. https://pmc.ncbi.nlm.nih.gov/articles/PMC11467115/

**14.2.8 — 3D/2D improves decision *speed*, not decision *quality*.** `Experimental`
Six-week 3D vs 2D video training, national-level youth handball: the 3D group was faster on first-option decisions, with no pronounced difference in decision quality, and faster than a tactic-board control. https://pubmed.ncbi.nlm.nih.gov/26207956/

**14.2.9 — Far transfer from generic cognitive/perceptual training: no supporting evidence.** `Research-supported` (negative)
2024 *Sports Medicine* critical review finds no consistent evidence of far transfer of general perceptual or cognitive training to sport performance. 3D multiple-object-tracking training produced **no transfer to soccer game performance**. Action-game far transfer: second-order meta-analysis ≈ **g = −0.01** after correction; Hilgard et al. (2019) document publication bias and salami-slicing in the positive meta-analyses. https://doi.org/10.1007/s40279-024-02060-x ; https://doi.org/10.1016/j.psychsport.2024.102770 ; https://doi.org/10.1525/collabra.203 ; https://online.ucpress.edu/collabra/article/5/1/30/113031/Overestimation-of-Action-Game-Training-Effects

**14.2.10 — Quiet eye: strong correlation, contested causation.** `Research-supported` (association) / `Experimental` (causal)
Lebeau et al. (2016): expert–novice QE duration **d = 1.04**; success vs failure d = 0.58; QE training → QE duration d = 1.53 and performance d = 0.84. But the correlation between QE-duration gains and performance gains was only r = .45 (p = .12). Klostermann's inhibition account and null results from disrupting visual input during the fixation argue against a simple "longer QE causes better performance" rule. https://pubmed.ncbi.nlm.nih.gov/27633956/ ; https://doi.org/10.1016/j.psychsport.2020.101736

---

### 14.3 Feedback timing and after-action review

**14.3.0 — Feedback is a double-edged intervention: 38% of its measured effects are negative.** `Demonstrated` (meta-analytic)
Kluger & DeNisi (1996), *Psychological Bulletin* 119(2):254–284 — 131 studies, **607 effect sizes**, ~23,663 observations. Mean weighted effect of feedback interventions on performance **d = 0.41**, but **38% of the 607 effects (231) were negative** — performance was *worse* after feedback than in the comparison condition. Feedback Intervention Theory's mechanism: feedback can shift attention away from the task and toward self-evaluation/self-related concerns, and effectiveness declines as attention moves up that hierarchy. https://doi.org/10.1037/0033-2909.119.2.254
→ **Design consequence, and the strongest argument in this document against a "mistake catalogue" report:** the feedback must stay at *task* level (this cue, this timing, this option) and must never become self-level ("you have poor awareness", "you always choke"). Self-focused framing is the documented route to the negative third. Goal specificity and a forward-looking next action (feed-forward, in Hattie & Timperley's terms) are the mitigating structure. https://www.tandfonline.com/doi/abs/10.1207/s15326985ep4201_4

**14.3.0b — What predicts benefit is the feedback's *informational content*, not its sign.** `Demonstrated`
Wisniewski, Zierer & Hattie (2020), *Frontiers in Psychology* 10:3087 — rebuilt the dataset from unique primary studies behind the famous "feedback d = 0.79" figure (435 studies, k = 994, N > 61,000), deduplicated overlapping samples, random-effects with robust variance estimation: **d = 0.55 raw → 0.48 after removing outliers**, I² = 86.5% → 83.4%, **17% of effects negative**; published papers larger than dissertations (0.49 vs 0.36) and an asymmetric funnel → the published average still overstates the typical effect. https://doi.org/10.3389/fpsyg.2019.03087
The load-bearing moderator: **reinforcement/punishment d = 0.24; corrective feedback d = 0.46; high-information feedback (what was wrong, why, and what to do next) d = 0.99.** Kluger & DeNisi had already found that feedback *sign* did **not** reliably separate positive from negative effects.
→ This is the single most actionable number in §14. A coaching output is worth ~4× more if it states *what was wrong, why, and the next action* than if it merely grades. And "d = 0.79 for feedback" should never be quoted as a causal effect — it is a meta-synthesis artefact with double-counted primary studies.

**14.3.0c — The four levels of feedback, and where praise sits.** `Research-supported` (level effects are meta-analytic; the mechanism is theory)
Hattie & Timperley (2007) classify feedback as task → process → self-regulation → **self** (praise), with self-level feedback the least effective and the most commonly received. In Hattie's synthesis, **praise sits at d = 0.14 while video/audio feedback sits at d = 0.64**. Kluger & DeNisi's Feedback Intervention Theory supplies the mechanism: feedback shifts the locus of attention up a hierarchy from task-learning to task-motivation to meta-task/self; attention to the self consumes resources and triggers ego-protective processing. https://doi.org/10.3102/003465430298487
Brummer et al. (2024), 116 studies of digitally delivered instructional feedback: g = 0.41, I² ≈ 61%, and **process-focused feedback outperformed purely task-focused feedback** — because task feedback can be too situation-specific to transfer. https://doi.org/10.1007/s10984-024-09501-4
Anseel & Sherf's 25-year review (2025) concludes there is no single universal feedback effect: content, interpretation, social context, timing and consequences all moderate it. https://doi.org/10.1146/annurev-orgpsych-110622-031927
→ **Target the *process* level ("when you have no visual on the second angle, re-anchor behind cover"), name the mechanism, and never evaluate the player as a person.** The "no visual on the second angle" framing is also what makes the advice transferable, per Brummer.

**14.3.0d — Positive vs negative framing is unresolved, and negative feedback alone often does nothing.** `Experimental`
Aarvik et al. (2024) on professional-performance data: positive feedback improved subsequent performance (short-term, strongest for highly relevant tasks); **negative feedback showed no overall performance effect**. A 2025 six-year multilevel field experiment with 331 managers found developmental feedback ineffective short-term but positive long-term, with larger gains for lower performers and a strong effect of *feedback source*. https://doi.org/10.1016/j.serev.2024.100045
**Reconciliation caveat:** this only coheres with 14.3.0b if *sign* and *informational content* are separated — most published work does not separate them cleanly, so do not design on "be positive".

**14.3.1 — Instantaneous knowledge of results can be *worse* for retention than slightly delayed KR.** `Experimental` (motor) / `Research-supported` (small effects)
Swinnen et al. (1990), *JEP:LMC*: instantaneous KR facilitated acquisition but degraded delayed no-KR retention relative to KR delayed by a few seconds — interpretation: it undercuts the learner's own error detection. Travlos & Pratt (1995) meta-analysis of 17 articles: significant but comparatively small effects. Note: in *verbal* learning immediate feedback tends to win — different task demands. https://www.sciencedirect.com/science/article/abs/pii/016794579090007Z ; https://journals.sagepub.com/doi/10.2466/pms.1995.80.1.3

**14.3.2 — Structured after-action review is the best-supported intervention in the learning stack.** `Demonstrated` (meta-analytic; team contexts)
Tannenbaum & Cerasoli (2013), *Human Factors* — 46 independent samples, N=2,136: overall debrief **d = 0.67** (~25% improvement); **alignment effect**: team-conducted, team-focused debrief with team-level measurement **d = 1.20**, team debriefs measured on individual outcomes **d = 0.41**. The definition is active participation + developmental intent + reflection on specific events + multiple information sources — **explicitly not passive feedback receipt**. https://pubmed.ncbi.nlm.nih.gov/23516804/
**Critical scoping caveat:** a solo self-coaching tool can only ever claim the individual branch (d ≈ 0.41), and the field evidence is largely team/organisational.

**14.3.3 — Video feedback works as an adjunct, but the evidence base is weak and mostly measures practice performance.** `Research-supported` (adjunct) / weak for durable transfer
- 2022 trial-sequential meta-analysis in PE (15 studies): feedback improved motor-skill learning **SMD = 0.47**; favourable sensitivity results for visual, visual+verbal, **visual self-modelling** and expert modelling. https://pubmed.ncbi.nlm.nih.gov/36430079/
- Petancevski et al. (2022) systematic review (24 studies, 895 participants): most studies positive, but **18/24 at high risk of bias**; optimal frequency/timing/duration unclear. https://www.sciencedirect.com/science/article/pii/S1469029222001455
- Ashford et al. (2007) meta-analysis of observational modelling (55 studies): adults gained on **movement form/dynamics (δ ≈ 0.80)** with **no outcome benefit (δ ≈ −0.02)**. Watching a model teaches *how the movement looks*, not *how well the task is done*. https://pubmed.ncbi.nlm.nih.gov/17365541/

**14.3.3b — Video self-modelling produces moderate-to-large gains that decay within a week, and the effect is dose-dependent.** `Experimental`
Wang et al. (2026), *Front. Sports Act. Living* 8:1809566 — meta-analysis of 10 RCTs (26 effect sizes, N = 244): athletic performance **SMD = 0.81 (95% CI 0.28–1.33)**, I² = 73%; self-efficacy SMD = 0.62. **At one-week follow-up the performance effect was non-significant (SMD = 0.59, p = 0.09)** and not robust to outlier removal. Effects were **dose-dependent** (total minutes and session count were significant moderators); age, experience, skill class and control type were not. https://doi.org/10.3389/fspor.2026.1809566
Surgical-training corroboration, with the same collapse on post-test: Daniel et al. (2023), 11 RCTs, 298 residents — pre–post change **SMD 1.62 (0.62–2.63, I² = 85%)**, but post-intervention skill-score difference only **SMD 0.53 (0.00–1.01, p = 0.05)**, with the authors attributing the benefit to low-baseline learners. https://pubmed.ncbi.nlm.nih.gov/35739431/
→ **Two consequences: (a) a review's value must be measured in the games that follow, never in the review session; (b) the large self-modelling effects in the literature are concentrated in novices and early training — an ex-2400 player is not that population.**

**14.3.3c — Self-observation without a "reference of correctness" is the documented failure mode of VOD review.** `Research-supported` (mechanism well established in motor learning; "harm" effect sizes not)
Comparative motor-learning work: self-observation supplies information about *what happened* but not whether it was *correct*; expert modelling supplies a correctness model but not the athlete's own execution; **combining the two produced better short-term learning than either alone.** Self-observation may be neutral or actively harmful when the learner confidently adopts a wrong interpretation, or when visually salient but functionally irrelevant details capture attention. https://www.frontiersin.org/journals/ict/articles/10.3389/fict.2019.00016/full
→ **This is the strongest single argument for what an AI coach is *for*.** The player already watches his own demos; what he lacks is the correctness reference. The product's job is exactly the missing half of the pair — not a description of what happened, which he can already see.

**14.3.3d — Improved performance *during* feedback is not learning.** `Research-supported`
In motor adaptation, removing visual error feedback causes errors to return — i.e. the feedback supported online correction rather than a durable change in the motor representation. This is the classic performance/learning distinction (Salmoni, Schmidt & Walter 1984 lineage). https://uol.de/f/4/inst/sport/download/andreasbund/publikationen/Publikation_44.pdf
→ Never grade a review session by how good the player looks *during* it; grade later games (14.3.3b, 14.2.3c).

**14.3.4 — "Watch your own VOD" for FPS *decision-making* is untested.** `Plausible-untested`
Self-modelling evidence is about visible movement form. Reviewing your own tactical errors is mostly episodic-memory retrieval plus counterfactual reasoning — a metacognition task (§14.7), not a perceptual-modelling task. No controlled study isolates the incremental effect of self-VOD review on CS outcomes.

---

### 14.4 Error-based learning

**14.4.1 — Error management training: worse during training, better after — especially on novel tasks.** `Research-supported`
Keith & Frese (2008), *JAP* — 24 studies, N=2,183: EMT vs comparison overall **d = 0.44**; **post-training transfer d = 0.56**; **adaptive transfer (structurally different tasks) d = 0.80**; **within-training performance d = −0.15**. EMT = active exploration + explicit framing that errors are expected, informative, and not penalised. https://pubmed.ncbi.nlm.nih.gov/18211135/
**Design consequence:** a dashboard that headlines *practice-session* accuracy will punish exactly the behaviour that transfers. Do not surface practice stats as a headline metric. A 2024 re-examination questions whether the "error encouragement" framing component or the active-exploration component carries the effect — so the load-bearing requirement is *exploration*, not cheerleading about errors. https://econtent.hogrefe.com/doi/full/10.1027/1866-5888/a000333

**14.4.2 — Desirable difficulties: the framework, and its limits.** `Research-supported` (framework) / `Experimental` (components)
Bjork: retrieval, spacing, interleaving, generation, variation, and delayed testing depress fluency during learning but improve durability. It is a *prediction-generator*, not one testable hypothesis — and its components differ sharply in evidence quality (spacing: strong; interleaving: conditional; "variability" in sport: mixed). https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-introducing-desirable-difficulties-into-practice-and-instruction-bjork-and-bjork.pdf

**14.4.3 — Prediction error is the mechanistic currency, but reward framing is task-dependent.** `Experimental`
Sensory (limb) prediction errors and task-performance errors drive learning through **separate mechanisms** (*PLOS Biology* 2024); explicit reward-prediction-error information facilitates agile motor adaptation. **Counter-evidence:** "Reinforcement feedback impairs locomotor adaptation and retention" (*Front. Behav. Neurosci.* 2024). Do not assume reward framing helps. https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.3002703 ; https://www.frontiersin.org/journals/behavioral-neuroscience/articles/10.3389/fnbeh.2024.1388495/full

**14.4.4 — Error-avoidance cost in ranked elite play is untested.** `Plausible-untested`
No clean sports experiment shows that an elite player's error-avoidance in ranked play directly suppresses learning rate — and the ranked ladder structurally penalises exploration, which makes the transfer prediction genuinely uncertain.

---

### 14.5 Transfer: why drills don't show up in matches

**14.5.1 — The transfer gradient is the most consistent finding in the literature.** `Demonstrated`
Trained task ES ≈ 1.51 → on-court ≈ 0.65; occlusion video test d = 1.26 → field d = 0.85; action-game far transfer ≈ 0; 3D-MOT → no soccer transfer; aim trainers validated as instruments but no demonstrated game transfer. Mechanism = specificity + TAP. https://doi.org/10.1007/s40279-024-02060-x ; https://pmc.ncbi.nlm.nih.gov/articles/PMC11467115/

**14.5.2 — Why FPS aim drills under-transfer is derivable, and the fix is adding the decision layer.** `Plausible-untested` (as stated for CS) / derived from demonstrated principles
Aim-trainer and shooting-range tasks are perception–action loops with a single externally specified goal, no opponent intent, no information ambiguity, no economy, no consequence. TAP predicts near-zero transfer to round-level decisions; the CI literature predicts that a drill with no *selection* demand cannot train selection. The positive corollary: **keep the target sub-skill constant while adding representative information (a real opponent pattern, real timing pressure)**. https://pmc.ncbi.nlm.nih.gov/articles/PMC11349744/ ; https://www.sciencedirect.com/science/article/pii/B9780123942937000066

---

**14.5.3 — Randomised component-training trials in esports reliably improve the component and not the game skill.** `Experimental` (including clean nulls)
- Wachholz et al. (2025), *Front. Sports Act. Living* — 8-week RCT, physical training ~3 sessions/week: physical measures improved, **no significant between-group improvement in Aimlabs performance, reaction time, or anticipation**. A clean demonstration that improving a component does not transfer to game skill. https://doi.org/10.3389/fspor.2024.1504205
- Kim & Chang (2022), *JSEP* — randomly assigned LoL players (5 per group) to a nine-session psychological-skills and counselling programme: significant group × time effects on psychological skills, coping and communication — **not** on objective in-game skill. https://doi.org/10.1123/jsep.2022-0071
→ **Combined with 14.5.1 and 14.5.2, the pattern is unambiguous: component metrics are the easiest thing to move and the least predictive of match performance.** Any prescription must therefore carry a representativeness score and be judged on match-level behaviour, never on the drill metric.

### 14.6 Spacing and interleaving

**14.6.1 — Spacing is the most robust effect in this document.** `Demonstrated`
Donovan & Radosevich (1999), *JAP* — 63 studies, 112 effect sizes: distributed > massed overall **d = 0.46**; **simple psychomotor tasks d = 0.97**; interval moderators <1 min d = 0.71, 1–10 min 0.48, 10 min–1 h 0.26, >1 day 0.16. Cepeda et al. (2008): the optimal gap grows with the retention interval but **sub-proportionally** (≈20–40% of a 1-week interval; only ≈5–10% of a 1-year interval). https://gwern.net/doc/psychology/spaced-repetition/1999-donovan.pdf ; https://pubmed.ncbi.nlm.nih.gov/19076480/
2025 classroom meta-analysis: 22 reports, 31 effect sizes, >3,000 learners — **d = 0.54** [0.31, 0.77], larger for longer retention intervals. https://pubmed.ncbi.nlm.nih.gov/40564553/

**14.6.2 — Interleaving is a discrimination technique with conditional benefit, and it backfires for some materials.** `Research-supported` (conditional)
Brunmair & Richter (2019), *Psychological Bulletin* — 59 studies, 238 effect sizes, 158 samples: overall **g = 0.42**; mathematics 0.34; visual category learning 0.67; **word learning g = −0.39 (blocking better)**. Effects larger when to-be-discriminated categories are similar and within-category items dissimilar. https://pubmed.ncbi.nlm.nih.gov/31556629/
Learners *prefer* blocking because it feels smoother — an illusion-of-competence instance (§14.7). https://doi.org/10.1037/edu0000909

**14.6.3 — Applied motor-skill interleaving is the weakest branch.** `Research-supported` (limiting)
See 14.2.2 — no significant overall advantage in the critical applied review; sensitivity-adjusted adult effect SMD ≈ 0.38 with I² ≈ 86%.

---

### 14.7 Metacognition and calibration

**14.7.1 — The Dunning–Kruger effect as popularly understood is largely a statistical artifact.** `Research-supported`
Gignac & Zajenkowski (2020), *Intelligence*: the classic pattern is mostly regression to the mean / measurement artifact on noisy bounded measures; valid tests require individual-differences approaches, not tertile plots. 2024 *Intelligence* reanalysis: the robust component is small and confined. https://www.sciencedirect.com/science/article/abs/pii/S0160289620300271 ; https://www.sciencedirect.com/science/article/pii/S0160289624000242
**Consequence:** any dashboard copy reading "low performers overestimate themselves" is trading on a partly artifactual pattern. The real, actionable phenomenon is the fluency illusion (14.7.2).

**14.7.2 — Illusions of competence come from fluency, and they are exactly what a self-coaching player cannot see.** `Research-supported`
Bjork, Dunlosky & Kornell (2013), *Annual Review of Psychology*: learners regulate study via subjective fluency; fluency during study ≠ retrieval success later. Effective techniques *feel* worse. The FPS analogue: "watching my own VOD feels like learning"; "I know this lineup" (recognition) vs executing it under a 6-second site take (retrieval under load). https://www.annualreviews.org/content/journals/10.1146/annurev-psych-113011-143823

**14.7.3 — Expertise does not buy calibration.** `Experimental`
Interval-estimation research: experts produce narrower and better-centred intervals but are **not necessarily less overconfident** — confidence can rise faster than accuracy. "He's ex-2400, he knows his own game" is not a supported generalisation. https://www.sciencedirect.com/science/article/pii/S0749597808000186

**14.7.4 — Calibration training works modestly, via repeated externally-scored predictions.** `Experimental`
Common active ingredient across the literature: repeated, quantified predictions with prompt resolution and individualised feedback. Effects are modest, transfer is limited, and recent large-N tests found **null** effects vs controls; training may lower confidence without improving accuracy, and can worsen calibration where people were initially *under*confident. https://onlinelibrary.wiley.com/doi/10.1002/acp.4236 ; https://onlinelibrary.wiley.com/doi/10.1002/ffo2.199 ; https://pubmed.ncbi.nlm.nih.gov/25987508/

**14.7.5 — Intentions barely predict behaviour.** `Research-supported`
Webb & Sheeran (2006), *Psychological Bulletin*: medium-to-large intention changes produce only small-to-moderate behaviour changes (**d ≈ 0.36**). A player who says he will review VODs often will not; the system must engineer the behaviour, not exhort it. https://pubmed.ncbi.nlm.nih.gov/16536643/

---

**14.7.6 — Expert self-assessment is not a usable substitute for an external record.** `Research-supported`
Davis, Mazmanian, Fordis, Harrison, Thorpe & Perrier (2006), *JAMA* 296(9):1094–1102: 725 articles screened, 17 studies, **20 comparisons** of physicians' self-assessment vs observed competence; **13 of 20 showed little, no, or an inverse relationship**; only 7 were positive; self-assessment was particularly inaccurate among the *least skilled* and the *most confident*. The authors recommend emphasis on **external assessment**. https://jamanetwork.com/journals/jama/article-abstract/203258 ; PMID 16954489
→ This is the strongest support for the product's core premise: the value of a demo-derived external record is not that the player lacks insight in general, but that self-assessment has a *documented, systematic* gap to observed behaviour — and the gap is largest exactly where the player is weakest. It pairs with the fluency illusion (14.7.2) and the intention–behaviour gap (14.7.5).

**14.7.6b — Across domains, self-assessment explains roughly 8% of the variance in actual performance.** `Demonstrated` (metasynthesis)
Zell & Krizan (2014), *Perspectives on Psychological Science* 9(2):111–125 — metasynthesis of 22 meta-analyses (academic, intelligence, language, medicine, sport, vocational): moderate relative accuracy (**r ≈ .29**) that improves when the judged task is domain-specific, objective, familiar and narrowly scoped — but still far too weak to use as an individual-level measure. https://doi.org/10.1177/1745691613518075
→ **The usable nuance:** accuracy rises with specificity. "How did I play this round?" is unfalsifiable; "how many of my six early-round buys produced a kill or a plant?" is checkable. Every question the system asks the player must be the checkable version.

**14.7.6c — Athletes systematically overestimate themselves against coach ratings, and the strongest overestimators develop worse.** `Experimental`
Hofseth et al. (2017), *Sport, Exercise, and Performance Psychology* 6:370–383 — 267 youth-elite footballers (~17.6 y): players on average rated their skills above their coaches' ratings; the "strong overestimator" group had odds ratio **0.71** for later high performance vs the underestimating group, controlling for age and prior/current performance (association, not causation). https://doi.org/10.1037/spy0000094

**14.7.6d — But coach ratings are not ground truth either.** `Experimental`
Coaches' estimates of athletes' exertion diverge from the athletes' own by sport (soccer coaches underestimated, lacrosse coaches overestimated) and diverge most on high-exertion days; and athletes construct self-other assessments from salient extremes, over-weighting their best-ever performance relative to its informativeness. https://pubmed.ncbi.nlm.nih.gov/36820706/
→ **Both sides of a coach–player comparison are noisy; only instrumented data breaks the tie.** This is the strongest argument for a *demo-derived* record over a coach-rated one.

**14.7.6e — The productive reformulation is "self-directed assessment seeking", not "better self-rating".** `Research-supported`
Eva & Regehr (2005) argue the relevant professional capacity is recognising a need, **obtaining external data** (observation, scores, audits, outcomes), and acting on it — rather than introspective global self-judgment. https://doi.org/10.1097/00001888-200510001-00015
→ The design justification for an objective record generated from demos rather than a prompt to "think about your mistakes".

---

### 14.8 Habit formation

**14.8.1 — "21 days" is folklore; the best-known estimate is ~66 days with an 18–254-day range.** `Demonstrated` (as described)
Lally et al. (2010), *EJSP*: median modelled time to 95% of asymptote = **66 days**, individual range 18–254; missing a single opportunity did not derail the trajectory. The outcome was **self-reported automaticity**, not verified behaviour. https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674

**14.8.2 — No meta-analysable formation time exists.** `Research-supported` (null on the headline question)
Singh et al. (2024), *Healthcare*: medians 59–66 days, means 91–154, range 4–335; only four studies reported a formation time; methodological differences prevented a duration meta-analysis. Any product claim "habits form in N days" is unsupported. https://pmc.ncbi.nlm.nih.gov/articles/PMC11641623/

**14.8.3 — Self-report habit indices are partly circular.** `Research-supported` (measurement critique)
The SRHI mixes behavioural frequency, automaticity, and identity; using it to predict behaviour frequency puts the criterion in the predictor. Use the 4-item automaticity subscale (SRBAI). https://academic.oup.com/abm/article-abstract/43/1/139/4563935 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3552971/
**Consequence:** a "habit score" that includes frequency will make the product prove its own effectiveness circularly.

**14.8.4 — Implementation intentions are the one strong habit-adjacent technique.** `Demonstrated`
Gollwitzer & Sheeran (2006): **94 independent tests, 63 reports, N=8,461**, mean **d = 0.65** [0.60, 0.70] for goal attainment, across varied goals and objective/self-report outcomes. Mechanism: heightened cue accessibility plus automatic initiation of the planned response. https://doi.org/10.1016/S0065-2601(06)38002-1

**14.8.5 — Habit discontinuity is real but tiny.** `Experimental` (small effect, single field study)
Verplanken & Roy (2016): ~800 residents, half recent movers — intervention × relocation interaction significant but **β ≈ −.08** (~0.6–1.1% of residual variance), confined to those who moved within ~3 months. The esports analogue (patch day, new team, new role, hardware change) is `Plausible-untested`. https://www.sciencedirect.com/science/article/pii/S0272494415300487

---

### 14.9 Cognitive load: how verbose the report should be

**14.9.1 — Expertise reversal is large, and the direction is unfavourable for long reports.** `Demonstrated` (meta-analytic)
Tetzlaff et al. (2025), *Learning and Instruction* — 60 studies, 176 effect sizes, N=5,924: for **low**-prior-knowledge learners high-assistance beats low-assistance (**d = 0.505**); for **high**-prior-knowledge learners low-assistance beats high-assistance (**d = −0.428**); the reversal contrast **d = 0.971**. Asymmetry: helping novices is more reliably beneficial than stripping help from experts. https://www.sciencedirect.com/science/article/pii/S0959475225000660

**14.9.2 — Seductive details actively harm transfer.** `Research-supported` (moderated)
Sundararajan & Adesope (2020), *Educational Psychology Review* — 58 papers, 68 effect sizes, N=7,521: retention-only **g = −0.37** [−0.60, −0.13]; studies measuring both retention and transfer **g = −0.41** [−0.55, −0.28]; time pressure was a significant moderator. https://eric.ed.gov/?id=EJ1263249

**14.9.3 — Redundancy is a different error from seductive detail: duplicated relevant content also costs processing.** `Research-supported`
Sweller's CLT: the same content in multiple mutually redundant formats imposes extraneous load; use complementary, not duplicative, channels. Boundary: text is *not* uniformly bad — it helps when the learner controls pace or terminology must be consistent. https://www.sciencedirect.com/science/article/pii/S0361476X12000677

**14.9.4 — Caveat: ERE was established on well-structured tasks; CS decisions are ill-structured.** `Experimental` (contested boundary)
A legal-reasoning study found worked examples helped both novices and advanced learners on ill-structured tasks (no reversal). So "give experts less guidance" can be over-applied. The safe rule is remove **redundant** guidance, keep **necessary** guidance — a design judgment, not a measured quantity. https://doi.org/10.1016/j.learninstruc.2025.102142

---

### 14.10 Constraints-led practice (and what to take from it)

**14.10.1 — The 2025 systematic review finds directional promise at low confidence.** `Experimental` (low certainty)
Burkett et al. (2025), *Sports Medicine – Open*: 7,450 records screened, **only 9 studies included** (~78% soccer); technical skill 34% of outcomes favoured nonlinear pedagogy / 66% no difference; tactical skill 62.5% favoured NP (crossing the ≥66% threshold only after excluding a serious-risk-of-bias study); **no meta-analysis possible** → vote counting, which ignores magnitude and precision. https://link.springer.com/article/10.1186/s40798-025-00893-y

**14.10.2 — Related CLA meta-analyses are so heterogeneous that pooling is uninformative.** `Research-supported` (critique)
I² = 99.56% with publication/inflation-bias evidence in a CLA team-synergies review; the 2019 interceptive-sports review reports 77.7% positive studies but most with poor quality scores. https://www.sciencedirect.com/science/article/pii/S1469029219303188

**14.10.3 — Much of "CLA vs traditional" is a straw man.** `Research-supported` (critique)
Lindsay & Spittle (2024): the opposition is overstated — contemporary direct instruction already includes representative practice, variable practice, bandwidth feedback, external-focus cues, guided discovery, and progressive complexity. The real question is *which principle, when, for which learner*. https://journals.sagepub.com/doi/10.1177/17479541241240853

**14.10.4 — The one CLA principle worth adopting is representativeness.** `Research-supported`
Make practice representative of competition — preserve information sources, decision requirements, and action possibilities. This is the same prediction as specificity/TAP (14.2.1) and is corroborated by the transfer gradient (14.5.1) and the stimulus-fidelity findings (14.2.6). Newell's constraints taxonomy is **theory**, not an empirical claim. https://pmc.ncbi.nlm.nih.gov/articles/PMC8776195/

**14.10.5 — "Differential learning" is the weakest sub-branch.** `Plausible-untested`
No high-quality preregistered trial in elite performers was identified; the variability-is-not-monotonic findings (14.2.2) constrain the claim.

---

### 14.11 The feedback loop: mistake → explanation → evidence → alternative → practice objective → measurement

This is item 3 of the brief. Below, each stage is specified with the evidence that supports or undercuts it. **The loop is a design artifact, not a validated method** — but every stage has a defensible evidence anchor, and each has a named failure mode.

**Stage 0 — Trigger selection (which moments enter the loop).**
- Rule: select **decision-dense** moments (player chose among plausible alternatives) and include moments from **won** rounds. Do not select by outcome impact (`Plausible-untested`; argued in §13.4.5, §13.5).
- Evidence anchor: AAR's alignment effect requires the review to be about *specific events* (14.3.2); outcome blindness is licensed by Baron & Hershey (13.2.2).
- Failure mode: selecting "rounds that cost the match" reproduces outcome bias (smartCoach's public product framing — *"Find the rounds that cost the match"* — does exactly this).

**Stage 1 — Mistake statement (what actually happened).**
- Must be a **fact citation**: tick, position, angle, event id, and the demo field it comes from. §13.7 enumerates what is and is not in the file.
- Evidence anchor: seductive details and redundancy damage transfer (14.9.2, 14.9.3) → state the fact, not the narrative.
- Failure mode: **fabricated evidence**. This is the single highest-severity defect and is directly testable (§15.3).

**Stage 2 — Explanation (why it was a mistake).**
- Must be *ex ante*: "given the information available at decision time". Requires an explicit statement of the information set (§13.4.4) and its uncertainty.
- Evidence anchor: TAP/specificity — the explanation must reuse the same processing the decision required (14.2.1); calibration research requires the prediction to be resolvable (14.7.4).
- Failure mode: hindsight narration ("you should have known"), and unfalsifiable claims from missing data (voice comms — 13.2.4).

**Stage 3 — Evidence (grounding).**
- The claim must be *traceable* to demo facts, and the trace must be checkable by the player in the demo viewer.
- Evidence anchor: the CSReplays approach — a **verification pass that re-checks every round reference against the parsed demo rather than against the model** — is the practitioner form of this, and it is the right architecture. https://csreplays.com/blog/training-the-coach-with-pro-demos (vendor, but the *method* is verifiable by construction).
- Failure mode: plausible-sounding round references that are wrong by one round.

**Stage 4 — Alternative.**
- Must be a *reachable* alternative — an option genuinely available in the information set, and the system must state the uncertainty of the counterfactual.
- Evidence anchor: counterfactual evaluation is intrinsically limited. Demonstrations: the Bayesian counterfactual-xG framework explicitly restricts "counterfactual" to *holding measured circumstances fixed and evaluating an alternative actor* — it does **not** license "what would have been if you had played differently", and its own owner-comparisons yield differences small relative to posterior uncertainty. Mahmudlu et al., arXiv:2511.23072 — https://arxiv.org/html/2511.23072
  Causal inference in sport additionally requires **overlap/common support**: you can only estimate the effect of an action in situations where both the action and its alternative actually occur. Alam et al., *Framing Causal Questions in Sports Analytics* (soccer crossing case study) — https://arxiv.org/html/2505.11841
- Failure mode: offering alternatives that no human player in that state ever takes (no common support) and asserting them as better.

**Stage 5 — Practice objective.**
- Must be an **if–then plan bound to a concrete in-game cue**, one at a time, and it must be *representative* (contains the decision, the information, and the time pressure) and *spaced* across days.
- Evidence anchors: implementation intentions d = 0.65 (14.8.4); spacing d = 0.46–0.97 (14.6.1); representativeness (14.10.4); error management's transfer payoff with its within-training cost (14.4.1); no more than 1–2 active targets, because "more is not better" (14.2.2, and CLT).
- **The strongest available moderator is goal *type*: process ≫ performance ≫ outcome.** A 2022 meta-analysis of 27 sport studies found overall d = 0.47 (95% CI 0.30–0.63; I² ≈ 76.6%; prediction interval −0.26 to 1.19) with **process goals d = 1.36, performance goals d = 0.44, outcome goals d = 0.09**. https://doi.org/10.1080/1750984X.2022.2116723
  Kyllo & Landers (1995), 36 experimental studies: overall g = 0.34; moderately difficult goals 0.53, absolute/specific goals 0.93, "do your best" 0.38, **very difficult goals −0.01**, public goals 0.79. https://doi.org/10.1123/jsep.17.2.117
  Locke & Latham (2002): difficult vs easy d = .52–.82; specific-and-difficult vs "do your best" d = .42–.80; and for complex/unfamiliar tasks a **learning goal** can beat a performance goal. https://doi.org/10.1037/0003-066X.57.9.705
  → "Win more clutches" (outcome, d = 0.09) is the worst possible objective. "When I am last alive with a smoke in hand, use it before re-peeking" (process, d = 1.36) is the best. Note the **−0.01 for very difficult goals**: an unrealistic target is worse than no target.
- Failure mode: goals instead of plans ("play smarter"); five objectives at once; unrepresentative drills.

**Stage 6 — Measurement.**
- Must be a **behavioural rate** on a defined opportunity set, tracked across days, with a baseline, not a rating delta.
- Evidence anchors: goal-setting in sport is strongest when goals are specific, self-selected, behaviourally defined, and reviewed with feedback; the recommended primary measure is `correct responses / total opportunities` — Swain & Jones (1995) https://pubmed.ncbi.nlm.nih.gov/7777696/ ; Ward & Carnes (2002) https://pubmed.ncbi.nlm.nih.gov/11936542/ ; Mellalieu et al. (2006) https://pmc.ncbi.nlm.nih.gov/articles/PMC1479782/
- **Measurement is not overhead — it is part of the treatment.** Harkin et al. (2016), *Psychological Bulletin* 142(2):198–232 — meta-analysis of **138 studies, 19,951 participants**: monitoring goal progress raised goal attainment by **d⁺ = 0.40 (95% CI 0.32–0.48)**, with larger effects for more frequent monitoring, public monitoring, and physical recording. https://doi.org/10.1037/bul0000025
  → This is the single strongest justification for building the measurement layer at all, and a reason to make the tracked behaviour **visible to the player between sessions** rather than computed silently. It is also why a purely descriptive dashboard leaves the largest available effect on the table (14.3.0b).
- For n = 1, use a **single-case experimental design**: multiple-baseline across behaviours with staggered introduction, ≥8–12 observations per tier, stabilised baseline, operational definitions, inter-observer agreement, procedural fidelity, and non-targeted comparison behaviours. Meta-regression of 121 SCED papers finds large average effects but with positive publication bias and unrealistically large effects in studies with few baseline observations. https://www.sciencedirect.com/science/article/pii/S1469029218304370 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC1479782/
- Failure mode: measuring the metric the system is good at; measuring ratings that drift (§13.8.2); measuring practice-session stats (14.4.1).

**14.11.1 — The loop's weakest link is stage 0/1 (trigger + fact) and stage 4 (counterfactual).** `Plausible-untested`
Everything downstream inherits an error from those. §15 therefore front-loads tests against them.

**14.11.2 — The loop must be delivered on a delay, and the player must answer first.**
`Research-supported` (motor) / `Plausible-untested` (CS)
Instantaneous KR can degrade retention relative to short-delayed KR (14.3.1); learner-generated error estimation before feedback is the mechanism that survived meta-analysis (14.2.3); AAR is defined as *active participation*, explicitly not passive receipt (14.3.2). Concretely: the report should ask the player to judge each selected round *before* revealing the system's verdict, and the system should keep score on those predictions (14.7.4).

**14.11.3 — A worked 6-stage example (illustrative, no data).**
| Stage | Content | Demo/host evidence required |
|---|---|---|
| 0 Trigger | Round 14, T-side, first contact at 0:52 into the round | round id, tick, event id |
| 1 Mistake | Player swung wide into a lane with potential LOS from 2 defenders | per-tick positions + eye angles + raycast occlusion; **stated as "2 defenders had potential LOS", not "you were seen"** |
| 2 Explanation | At decision time the player had no visual on either defender; a smoke covering one lane was still active for 6 s | smoke start/end tick; player view angle at decision tick |
| 3 Evidence | Clips + tick references; verifier re-checks each reference | parser re-derivation |
| 4 Alternative | "Re-peek from cover after the smoke fades, or jiggle for information" — with the note that no comparable situation in the player's last N matches was resolved this way | state-similarity search; explicitly flag low support |
| 5 Objective | If–then: "If I have no visual on a second angle at contact, then I re-anchor behind cover instead of wide-swinging." Practised in a representative DM/retake scenario this week. | drill spec |
| 6 Measurement | `isolated-exposure contacts / total contacts` per match, baseline over the previous 10 matches | per-match rate, tracked over days |

---

### 14.12 §14 contradictions and open questions

1. **Deliberate practice: 1% vs 18% vs 29% vs 61% vs ≈0% for CS:GO rank.** Definitional and measurement-based; no agreed resolution. Product floor: hours are not a predictor.
2. **Contextual interference lab vs applied.** Meta-analytic support (SMD 0.38–0.55) coexists with ~20% canonical-pattern replication and no applied-sport advantage. Whether CS decision drilling is "lab-like" or "applied-like" is unresolved.
3. **Guidance hypothesis falsified, yet bandwidth feedback still shows benefits.** Unresolved whether the benefit comes from frequency, from *which* trials get feedback, from implicit reinforcement, or from reduced conscious control.
4. **Quiet eye: cause, correlate, or inhibition artifact?** d = 1.04/0.84 vs a QE-gain↔performance-gain correlation of only r ≈ .45 (p = .12). No preregistered multi-lab QE-training trial.
5. **3D/VR vs 2D.** Subgroup ES 0.96 vs 0.19 looks compelling but is not significant (p = .449), I² = 84.7%, and the direct experiment found speed gains only.
6. **Video feedback / self-modelling.** Positive PE meta (SMD = 0.47) coexists with 18/24 studies at high risk of bias and adult modelling benefits confined to movement *form* with no outcome effect. "Watch your own VOD" for tactical decisions is an extrapolation.
7. **Error management generalisation.** d = 0.80 adaptive transfer comes from organisational training tasks; a 2024 reanalysis questions which component carries it. Whether error-eliciting practice helps an already-elite performer on a rank-penalised ladder is untested.
8. **Dunning–Kruger.** Popular usage vs the artifact critique. The practical phenomenon is real but better explained by fluency illusions and absent calibration feedback.
9. **Habit timescale and measurement.** No meta-analysable formation time; SRHI-type measures are partly circular. Any "N days" claim is unsupported.
10. **Expertise reversal in ill-structured domains.** Large overall, established on well-structured tasks, with no reversal in at least one ill-structured study. "Less guidance for experts" can be over-applied.
11. **CLA evidence quality.** Nine studies, vote counting, serious/some-concerns risk of bias, no retention/transfer data in the review, I² = 99.56% in a related meta. Only the representativeness heuristic is defensible.

---

### 14.13 §14 top sources

**Deliberate practice & practice structure**
1. Ericsson, Krampe & Tesch-Römer (1993), *Psych. Review* 100(3):363–406 — https://doi.org/10.1037/0033-295X.100.3.363
2. Macnamara, Hambrick & Oswald (2014), *Psych. Science* — https://journals.sagepub.com/doi/full/10.1177/0956797614535810
3. Macnamara, Moreau & Hambrick (2016), *Persp. Psych. Science* (1% among elites) — https://journals.sagepub.com/doi/10.1177/1745691616635591
4. Macnamara & Maitra (2019), *Roy. Soc. Open Sci.* (preregistered replication) — https://doi.org/10.1098/rsos.190327
5. Ericsson & Harwell (2019) reanalysis — https://pmc.ncbi.nlm.nih.gov/articles/PMC6824411/
6. Martončik et al. (2024), *Collabra: Psychology* (CS:GO/LoL registered report) — https://online.ucpress.edu/collabra/article/10/1/117677/200964/Psychological-Predictors-of-Long-term-Esports
7. *PLOS ONE* (2022) distributed practice, 162,417 LoL players — https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0275843

**Motor learning, feedback, transfer**
8. Czyż et al. (2024) CI transfer meta-analysis — https://pmc.ncbi.nlm.nih.gov/articles/PMC11349744/
9. Ammar et al. (2024), *Educ. Psych. Review* (critical CI review) — https://link.springer.com/article/10.1007/s10648-024-09892-z
10. McKay et al. (2022) reduced-feedback-frequency meta-analysis — https://www.sciencedirect.com/science/article/pii/S1469029222000334
11. Chiviacowsky & Wulf (2007) feedback after good trials — https://www.tandfonline.com/doi/full/10.1080/02701367.2007.10599402
12. Swinnen et al. (1990) instantaneous KR degrades retention — https://www.sciencedirect.com/science/article/abs/pii/016794579090007Z
13. Proteau et al. (1992) specificity of practice — https://pubmed.ncbi.nlm.nih.gov/1631322/
14. Morris, Bransford & Franks (1977) transfer-appropriate processing — https://www.sciencedirect.com/science/article/pii/S0022537177800169

**Perceptual-cognitive expertise & perceptual training**
15. Mann et al. (2007), *JSEP* — https://pubmed.ncbi.nlm.nih.gov/17968048/
16. Chase & Simon (1973) chunking — https://doi.org/10.1016/0010-0285(73)90004-2
17. Lebeau et al. (2016), *JSEP* quiet eye — https://pubmed.ncbi.nlm.nih.gov/27633956/
18. 2024 perceptual-cognitive training meta-analysis — https://pmc.ncbi.nlm.nih.gov/articles/PMC11505547/
19. 2024 temporal-occlusion video training meta-analysis, *Sports Medicine* — https://pmc.ncbi.nlm.nih.gov/articles/PMC11467115/
20. 2024 far-transfer critical review, *Sports Medicine* — https://doi.org/10.1007/s40279-024-02060-x
21. Sala et al. (2019) second-order meta-analysis — https://doi.org/10.1525/collabra.203
22. Hilgard et al. (2019) action-game publication-bias reanalysis — https://online.ucpress.edu/collabra/article/5/1/30/113031/Overestimation-of-Action-Game-Training-Effects

**Error-based learning, AAR, spacing, metacognition, habits, CLT, CLA**
23. Keith & Frese (2008), *JAP* error management training — https://pubmed.ncbi.nlm.nih.gov/18211135/
24. Tannenbaum & Cerasoli (2013), *Human Factors* debrief meta-analysis — https://pubmed.ncbi.nlm.nih.gov/23516804/
25. Donovan & Radosevich (1999), *JAP* distribution of practice — https://gwern.net/doc/psychology/spaced-repetition/1999-donovan.pdf
26. Cepeda et al. (2008) temporal ridgeline — https://pubmed.ncbi.nlm.nih.gov/19076480/
27. Brunmair & Richter (2019) interleaving meta-analysis — https://pubmed.ncbi.nlm.nih.gov/31556629/
28. Bjork, Dunlosky & Kornell (2013), *Annual Review of Psychology* — https://www.annualreviews.org/content/journals/10.1146/annurev-psych-113011-143823
29. Gignac & Zajenkowski (2020), *Intelligence* (D–K artifact) — https://www.sciencedirect.com/science/article/abs/pii/S0160289620300271
30. Gollwitzer & Sheeran (2006), *Adv. Exp. Soc. Psych.* — https://doi.org/10.1016/S0065-2601(06)38002-1
31. Lally et al. (2010), *EJSP* — https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674
32. Singh et al. (2024), *Healthcare* time-to-habit review — https://pmc.ncbi.nlm.nih.gov/articles/PMC11641623/
33. Sniehotta & Presseau (2012), *Ann. Behav. Med.* (SRHI critique) — https://academic.oup.com/abm/article-abstract/43/1/139/4563935
34. Tetzlaff et al. (2025), *Learning and Instruction* expertise reversal — https://www.sciencedirect.com/article/pii/S0959475225000660
35. Sundararajan & Adesope (2020) seductive details — https://eric.ed.gov/?id=EJ1263249
36. Burkett et al. (2025), *Sports Medicine – Open* CLA review — https://link.springer.com/article/10.1186/s40798-025-00893-y
37. Lindsay & Spittle (2024) direct instruction vs constraints-led — https://journals.sagepub.com/doi/10.1177/17479541241240853

**Intervention design / n = 1 measurement**
38. Swain & Jones (1995) single-subject goal setting in basketball — https://pubmed.ncbi.nlm.nih.gov/7777696/
39. Ward & Carnes (2002) self-set goals + public posting — https://pubmed.ncbi.nlm.nih.gov/11936542/
40. Mellalieu, Hanton & O'Brien (2006) rugby goal setting — https://pmc.ncbi.nlm.nih.gov/articles/PMC1479782/
41. SCED meta-regression (121 papers; bias findings) — https://www.sciencedirect.com/science/article/pii/S1469029218304370

**Counterfactual / causal limits**
42. Mahmudlu et al., *Counterfactual Expected Goals*, arXiv:2511.23072 — https://arxiv.org/html/2511.23072
43. Alam et al., *Framing Causal Questions in Sports Analytics*, arXiv:2505.11841 — https://arxiv.org/html/2505.11841

**Feedback interventions, self-assessment, debiasing, process scoring (added in integration)**
44. Wisniewski, Zierer & Hattie (2020), *The Power of Feedback Revisited*, Front. Psych. 10:3087 — https://doi.org/10.3389/fpsyg.2019.03087
45. Hattie & Timperley (2007), *The Power of Feedback*, RER 77(1):81–112 — https://doi.org/10.3102/003465430298487
46. Brummer et al. (2024), *Learning Environments Research* — https://doi.org/10.1007/s10984-024-09501-4
47. Anseel & Sherf (2025), *Annual Review of Organizational Psychology and Organizational Behavior* — https://doi.org/10.1146/annurev-orgpsych-110622-031927
48. Aarvik et al. (2024), *Journal of Sports Economics*/SEREV — https://doi.org/10.1016/j.serev.2024.100045
49. Marschall, Bund & Wiemeyer (2022), *Psychology of Sport and Exercise* (guidance-hypothesis meta) — https://uol.de/f/4/inst/sport/download/andreasbund/publikationen/Publikation_44.pdf
50. Wang et al. (2025), *Behavioral Sciences* 15(9):1291 (self-controlled feedback meta) — https://doi.org/10.3390/bs15091291
51. Wang et al. (2026), *Front. Sports Act. Living* 8:1809566 (self-modelling meta) — https://doi.org/10.3389/fspor.2026.1809566
52. Daniel et al. (2023), *Surgical Endoscopy* (video-based coaching RCTs) — https://pubmed.ncbi.nlm.nih.gov/35739431/
53. *Self-observation without a reference of correctness*, Front. ICT 6:16 (2019) — https://www.frontiersin.org/journals/ict/articles/10.3389/fict.2019.00016/full
54. Christensen-Szalanski & Willham (1991), *OBHDP* 48(1):147–168 (hindsight bias meta) — https://doi.org/10.1016/0749-5978(91)90010-Q
55. Guilbault et al. (2004), *Basic and Applied Social Psychology* 26(2–3):103–111 (debiasing fails) — https://doi.org/10.1080/01973533.2004.9646399
56. Salmen, Ermark & Fiedler (2023) — https://pubmed.ncbi.nlm.nih.gov/35953669/ ; forensic-risk hindsight prompt (2024) — https://doi.org/10.1080/24732850.2024.2396991
57. Zell & Krizan (2014), *Perspectives on Psychological Science* 9(2):111–125 — https://doi.org/10.1177/1745691613518075
58. Eva & Regehr (2005), *JCEHP* 25(S1):S11–S21 — https://doi.org/10.1097/00001888-200510001-00015
59. Hofseth et al. (2017), *Sport, Exercise, and Performance Psychology* 6:370–383 — https://doi.org/10.1037/spy0000094
60. Locke & Latham (2002), *American Psychologist* 57(9):705–717 — https://doi.org/10.1037/0003-066X.57.9.705
61. Kyllo & Landers (1995), *JSEP* 17(2):117–137 — https://doi.org/10.1123/jsep.17.2.117 ; 2022 sport goal-setting meta — https://doi.org/10.1080/1750984X.2022.2116723
62. Harkin et al. (2016), *Psychological Bulletin* 142(2):198–232 (monitoring as intervention) — https://doi.org/10.1037/bul0000025
63. Romer (2006), *Journal of Political Economy* 114(2):340–365 — https://doi.org/10.1086/501171
64. Potter van Loon, van den Assem & van Dolder (2015), *PLOS ONE* 10(2):e0115479 — https://doi.org/10.1371/journal.pone.0115479 ; Levitt & Miles (2011) — https://www.nber.org/papers/w17023
65. Billings & Kan (2006), *ICGA Journal* 29(3) (DIVAT) — https://doi.org/10.3233/ICG-2006-29302
66. White, Miltenberger & Concepcion (2024), *Behavioral Interventions* (esports single-case video feedback) — https://doi.org/10.1002/bin.2056
67. Wachholz et al. (2025), *Front. Sports Act. Living* (physical training RCT, null transfer) — https://doi.org/10.3389/fspor.2024.1504205 ; Kim & Chang (2022) — https://doi.org/10.1123/jsep.2022-0071
68. Sharpe et al. (2023), *Journal of Electronic Gaming and Esports* 1(1) — https://doi.org/10.1123/jege.2022-0017

---

## §15 — Evaluation framework

### 15.0 Executive answer: the must-haves

The system is an **LLM judge of domain-expert decisions with no ground truth**. That is harder than anything in the LLM-judge literature's happy path, and the evaluation must be designed around that fact rather than around benchmark folklore.

**Nine non-negotiables:**

1. **The human reference standard is the binding constraint, and it is not ground truth.** In a subjective domain, expert–expert agreement *is* the ceiling. Median quadratically-weighted κ for expert–LLM 0.60 vs expert–expert 0.58 in the best head-to-head study — i.e. a judge can match experts without experts agreeing with each other. Kumar et al., *Nature Machine Intelligence* — https://www.nature.com/articles/s42256-025-01169-6
2. **Report a three-way reliability triangle**: expert–expert (ceiling), LLM–expert (the claim), novice/crowd–expert (the floor). Without the ceiling, an LLM-vs-expert number is uninterpretable.
3. **Grounding is tested by entailment, not by fluency.** Extract atomic claims; each must link to a logged demo fact; score coverage, link correctness, and **negative-control firing**. An ungrounded metric that does not fire on injected false facts is worthless.
4. **Never ship a single-run judge score.** Same judge, same item, different run → different score ("Rating Roulette", Findings of EMNLP 2025 — https://aclanthology.org/2025.findings-emnlp.1361/ ). Every number is a distribution; report intervals and pass^k.
5. **Blind the evaluators, randomise order, control for length, and use a judge from a different family than the generator.** Position bias (Shi et al., >150k instances — https://arxiv.org/abs/2406.07791 ), verbosity bias (https://arxiv.org/abs/2404.04475 ), self-preference (https://arxiv.org/abs/2410.21819 ), and preference leakage (~23.6% same-model — https://arxiv.org/abs/2502.01534 ) are all demonstrated.
6. **Score outcome-blind.** The evaluator must not see whether the round was won (Baron & Hershey 1988 — §13.2.2).
7. **Measure abstention explicitly**, including *false abstention*. Reasoning-tuned models degraded **24%** on abstention vs their non-reasoning counterparts (AbstentionBench, 20 datasets, >35k unanswerable questions — https://arxiv.org/abs/2506.09038 ).
8. **Baseline before AI, and a strong baseline at that.** The relevant comparison is not "our pipeline vs an empty prompt" but "our pipeline vs a strong LLM with no domain signal **and** vs a simple non-LLM rule" (see §15.12).
9. **No claim of player improvement without a single-case design.** The unit of proof is a behavioural rate on a defined opportunity set, with baseline, staggered introduction, and pre-registered metrics (§15.14).

**Explicitly out of scope as evidence:** public benchmarks (saturated and contaminated — TruthfulQA best model 58% vs human 94% at publication and heavily contaminated by 2026: https://arxiv.org/abs/2109.07958 ; contamination effects under-reported: https://arxiv.org/abs/2411.03923 ), hallucination leaderboards resting on a detector with self-reported F1 of 45–67% (https://github.com/vectara/hallucination-leaderboard/issues/128 ), and reference-free faithfulness scores as *independent* grounding evidence (RAGAS-style metrics embed a judge — https://arxiv.org/abs/2309.15217 ).

---

### 15.1 The core problem, stated precisely

Three facts define the design space:

**15.1.1 — There is no public, validated measure of CS decision quality.** `Plausible-untested` (absence established)
Leetify Rating is win-probability delta (impact, not intent); Refrag's TTK/TTD conflate aim with engagement selection; Scope's composites are undisclosed (§13.8). No labelled corpus of "correct/incorrect CS decision" exists.

**15.1.2 — Action-valuation research says explicitly that it lacks ground truth and a standardised evaluation framework.** `Demonstrated` (as a field-level statement)
Xarles, Escalera, Moeslund & Clapés, *Action Valuation in Sports: A Survey*, arXiv:2504.06163 (2025-04-08): *"the lack of a standardized evaluation framework due to the absence of explicit ground-truth annotations… These limitations hinder the comparability of methods and the establishment of benchmarks."* https://arxiv.org/html/2504.06163

**15.1.3 — Judge skill on "which answer is nicer" does not transfer to "was this the right play".** `Experimental`
JudgeBench pairs responses with labels reflecting objective correctness rather than crowd preference; prompted judges, fine-tuned judges, multi-agent judges and reward models all struggled — GPT-4o was only slightly better than chance. https://arxiv.org/abs/2410.12784
And on expert-knowledge tasks (dietetics, clinical psychology), judge–SME agreement drops to ~64–68%, with LLMs agreeing more with **lay users** than with SMEs on some items; adding an "expert persona" to the judge helped but did not close the gap. Szymanski et al., IUI 2025 — https://arxiv.org/abs/2410.20266

**15.1.4 — Where judges *do* work, the pattern is: narrow, operationalised, observable sub-components of a rubric, grounded in a supplied reference.** `Research-supported` (pattern across studies)
- Kumar et al. (above): agreement strongest for observable behaviours, weakest for ambiguous constructs.
- Clinical-summary scoring vs 7 physicians: **ICC 0.818** (95% CI 0.772–0.854) for the best judge; weaker judges 0.33–0.76. https://doi.org/10.1038/s41746-025-02005-2
- Bounded fact-checking against a seven-physician majority: **κ = 0.81** vs κ = 0.67 for a single human evaluator. https://arxiv.org/abs/2509.05878
- **Counterexample:** GPT-4o as a fifth "clinician" on factuality: ICC ≈ **−0.10 to 0.14**. https://ai.jmir.org/2025/1/e72153
→ **Design rule: decompose the coaching judgment into narrow, observable sub-claims and score those separately. Do not score "was the analysis good" as a single item.**

---

### 15.2 Labelled situations: how to build and sample the set

**15.2.1 — Definition of the unit.** `Plausible-untested` (design)
A "situation" = (round id, side, role, tick window, player state at decision time, information set, options enumerated, action taken). The label is not "good/bad play" — it is the *set of sub-claims* the system is allowed to make:
`{observed_fact | decision_flaw_information | decision_flaw_option_selection | execution_error | role_confounded | insufficient_information}`.
The last two categories are what make §15.6's false-positive analysis meaningful. They are our invention; no external standard exists.

**15.2.2 — Sampling must be stratified, and difficulty strata must be declared in advance.** `Standard` (methodology, by analogy)
Radiology MRMC practice: prespecify the primary estimand, stratify by case difficulty, report per-reader effects and case-difficulty strata (Radiology 2021 — https://pubs.rsna.org/doi/10.1148/radiol.211593 ). Forensic latent-print work is the direct warning: on **difficult** comparisons, individualisation decisions were reproduced by other examiners ~55% (vs ~85% for easy/medium) and exclusions ~50% (vs ~77%); false-negative decisions were reproduced by another examiner only ~19.2%. Ulery et al., PNAS 2011/2012 — https://pmc.ncbi.nlm.nih.gov/articles/PMC3093498/ , https://pmc.ncbi.nlm.nih.gov/articles/PMC3299696/
→ Expect low expert reproducibility on low-information rounds. Size the annotation budget accordingly and report per-stratum.

**15.2.3 — Sample size is a precision question, and n counts *rated units*, not ratings.** `Research-supported`
Krippendorff's own approximate minimum-coder-values table: for a category with prevalence 0.50, 60 values for α = .667 and 103 for α = .800; at prevalence 0.10, 172 and 293; at prevalence 0.05, 329 and 560. https://repository.upenn.edu/bitstreams/b6ea3a5b-3dee-4f27-a159-e44393eda7d4/download
Simplified precision form: n ≈ z²·p_o(1−p_o)/(d²(1−p_e)²). Worked example from that arithmetic: p_o = .80, p_e = .50, 95% CI, half-width d = .10 ⇒ n ≈ 246 units; halving d to .05 quadruples it to ≈ 984. For >2 raters, weighted κ or ordinal data, these closed forms do not apply — simulate (kappaSize — https://cran.r-project.org/web/packages/kappaSize/kappaSize.pdf ; Donner & Eliasziw 1992 — https://onlinelibrary.wiley.com/doi/abs/10.1002/sim.4780111109 ).
→ "30 doubly-coded units" is a folk rule, not a sample-size justification, and it is inadequate for rare error types.

**15.2.4 — Opportunity/role confounds must be controlled in labelling, not after.** `Plausible-untested`
An aggressive entry player's "repeated isolated duels" may be a role effect. Condition habit claims on role/position/context or the label set will systematically mislabel good players in aggressive roles (§13.3.4). This is the CS analogue of role-adjusted rating.

**15.2.5 — Held-out discipline.** `Standard`
Frozen eval set; a retained never-touched set; pre-registered rubric and codebook versions; and a judge prompt authored by someone other than the coaching-prompt author. The realistic contamination risk here is **self-inflicted iteration on the same rounds until the harness overfits them** (the self-inflicted-contamination point).
Prompt-format sensitivity alone can move accuracy by up to **76 points** (Sclar et al., ICLR 2024 — https://arxiv.org/abs/2310.11324 ), so "we tuned the prompt against the eval set" is an overfitting operation, not a neutral one.

---

### 15.3 Grounding: testing whether the coach's claims trace to demo facts

**15.3.1 — The method is atomic-fact decomposition plus entailment checking.** `Standard` (shape) / `Experimental` (transfer)
FActScore (EMNLP 2023 — https://aclanthology.org/2023.emnlp-main.741/ ) decomposes a generation into atomic facts and computes the supported fraction. ALCE (https://arxiv.org/abs/2305.14627 ) separates citation **precision** from **recall** and reports the headline negative: on ELI5 even the best systems lack complete citation support **50% of the time**. Attributed-QA established the recipe of human gold + correlated automatic metric (https://arxiv.org/abs/2212.08037 ).

**15.3.2 — The concrete CS2 grounding test.**
Adapted from the standard pattern, but with a *machine-checkable* fact base rather than retrieved documents:

| Step | Action | Failure if skipped |
|---|---|---|
| 1 | Decompose each coaching paragraph into atomic claims (numbers, event attributions, positional claims, timestamps, economy). | Narrative-level scoring hides fabricated specifics. |
| 2 | Require each claim to carry an artefact link: `round=14, tick=…, entity=…, stat=…` **or** `derived: <named derivation>` over the parsed demo. | Claims become unfalsifiable. |
| 3 | Score **coverage** = claims with a valid link / total claims. | Measures omission of grounding. |
| 4 | Score **link correctness** = fraction where the linked fact *entails* the claim. Adjudicate on a human subsample; do not trust an LLM verifier alone. | Measures wrong linkage. |
| 5 | **Negative controls**: run outputs generated with injected false facts (wrong map, swapped players, wrong score, impossible tick). Any metric that does not fire is useless. | The metric is decorative. |
| 6 | **Attack tests**: append content-free filler and confirm coverage/correctness do not rise (the factuality-metric gaming result — https://arxiv.org/abs/2411.16638 ); test long-context degradation (HalluMix: specialists do not generally beat prompted general models, and performance collapses from short to long context — https://arxiv.org/abs/2505.00506 ). | The metric is gameable and inflated. |

**15.3.3 — A cheap local detector is plausible, but it must be validated against this fact base.** `Demonstrated`
RAGTruth: ~18,000 human-annotated RAG responses with word-level labels; fine-tuning a *small* LLM on it reached performance competitive with GPT-4-prompted detectors. https://arxiv.org/abs/2401.00396

**15.3.4 — Domain-specific grounding requirement: every claim must respect §13.7.** `Plausible-untested` (violation detection is easy; recovery is not)
Hard failure classes, mechanically detectable:
- asserting what the player **saw** (only potential LOS is reconstructable — §13.7.6);
- asserting what was **called on voice** (absent, and team chat encrypted since 2026-09-09 — §13.7.2);
- asserting **frame-accurate** timing/peek mechanics (sub-tick reconstruction undocumented — §13.7.3–13.7.5);
- asserting **sound** information (`who heard what` is not recorded — §13.7.7).
These four should be **lint rules** that fire a hard failure regardless of the judge's score.

**15.3.5 — The verification-pass architecture is the practitioner form of this.** `Plausible-untested` (vendor, but structure is verifiable)
CSReplays describes a **verification pass that re-checks round references against the parsed demo rather than against the model**, and uses pro demos as a seed corpus for the verifier's tests. https://csreplays.com/blog/training-the-coach-with-pro-demos
This is correct by construction: verification against the artifact is the only kind that can be automated soundly.

---

### 15.4 Expert comparison: panel design when there is no gold standard

**15.4.1 — MRMC-style design is the discipline, and the correct summary is a distribution, not a majority label.** `Standard`
Fully-crossed design (all readers × all cases × all conditions); prespecify the primary estimand; randomise reading order and enforce washout; **do not pool reader–case observations as if independent** (produces too-narrow CIs and too-small p-values); typically ≥5 readers, ~10+ for consequential claims, with the number determined by **simulation** using plausible reader and case variance components. Radiology 2021 — https://pubs.rsna.org/doi/10.1148/radiol.211593
Report the panel verdict as **5/5, 3/5, 2/5 + 1 equivocal**, never as a majority label. FDA guidance explicitly allows a reference standard that is absent, disputed or wrong in a non-negligible fraction of cases, and requires it to be defined before the study — https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda

**15.4.2 — The precedent for "experts agree on facts, disagree on quality" is direct and in sport.** `Demonstrated`
Malagoli Lanzoni, Di Michele & Merni (2012), *Reliability of selected table tennis performance indicators* — 10 highly experienced national-level coaches coding the same Olympic final: Krippendorff's α = **0.894** for stroke *type*, but only **0.469** for stroke *efficacy*. Intra-observer was very high (α 0.990–0.997). https://sasportssience.blob.core.windows.net/ijtts/IJTTS_7_pdf%20files/IJTTS_7_61-64_Malagoli_1.pdf
→ **Two separate evaluation tracks are required: an "occurrence/description" track (where high agreement is achievable and expected) and a "quality" track (where it is not).** Collapsing them produces a misleading single number.

**15.4.3 — Esports-specific coding reliability precedent.** `Experimental`
Novak, Bennett, Pluss & Fransen (2019), *Performance analysis in esports, Part 1* (LoL; 30 pro matches): Krippendorff's α = **.861–1.000** between experienced player-coders, and **.868–1.000** between an experienced coder and published match statistics — **with the novice coder diverging** on variables such as First Tower Time and First Inhibitor Team. https://research.rug.nl/en/publications/performance-analysis-in-esports-part-1-the-validity-and-reliabili/
→ Two consequences: (a) expert-dependent events need expert coders, so a novice-coded "ground truth" silently depresses measured coach accuracy; (b) public match statistics can serve as a reliability reference for objective events.

**15.4.4 — Human–AI combination does not reliably beat the better of the two alone.** `Demonstrated` (meta-analytic)
Vaccaro, Almaatouq & Malone (2024): 106 experiments, 370 effect sizes — combinations beat humans alone (g = 0.64) but were **worse than the better of human-alone or AI-alone** (g = −0.23; g = −0.27 for decision tasks). Synergy was positive when humans alone outperformed AI (g = 0.46) and negative when AI alone outperformed humans (g = −0.54). https://arxiv.org/abs/2405.06087
→ Do not design an eval that assumes the coach+player beats either; measure both arms.

**15.4.5 — Comparative judgment is more defensible than absolute optimality.** `Research-supported` (by analogy)
Chess practice: Maia predicts the human move conditioned on skill band (KDD 2020 — https://arxiv.org/abs/2006.01855 ); Go practice: PAGE attaches per-move **engine analysis** to 98,525 games by 2,007 professionals, with human annotation on a subsample (https://arxiv.org/abs/2211.01559 ). In both, the *objective* target is "which move is better than which", not "was the decision good". 
→ For CS, the defensible label is **"was the chosen action better or worse than a named plausible alternative, and why"** — a pairwise construct — not "was this optimal".

**15.4.6 — When the outcome is noisy, the honest design is many trials plus variance reduction, with pre-registered one-tailed hypotheses and no expert labelling of the AI's decisions.** `Demonstrated`
Brown & Sandholm, *Science* 2019: 13 professionals (>$1M each) playing 10,000 hands vs Pluribus, with AIVAT variance reduction → +48 mbb/game (SE 25, one-tailed p = 0.028) and +32 mbb/game (SE 15, p = 0.014); limitations reported openly (table-composition changes, only two subjects in the reversed condition, variance too high for individual win rates). https://doi.org/10.1126/science.aay2400
→ This is the best available template for "does the coach make the player better" in a noisy team game — and note that **the AI's own decisions were never labelled good or bad by experts**.

**15.4.7 — Process scoring is a fielded method, not an aspiration, and it exposes systematic expert error.** `Demonstrated`
- **Romer (2006)**, *Journal of Political Economy* 114(2):340–365: estimated the expected value of every fourth-down option by dynamic programming over 700+ NFL games and graded decisions by whether the team chose the higher-EV action. Found systematic over-conservatism — 512 fourth downs in own half where the model favoured going for it; teams went for it **7 times**. Estimated aggregate gain from optimal play ≈ 0.35 points per decision, ≈ 2.1 percentage points of win probability per game. https://doi.org/10.1086/501171
  → Note what this establishes: the documented failure mode of outcome-based evaluation is **systematically miscalibrated, not merely noisy**, and it is explained by a different implicit objective (avoiding visible failure) plus imperfect optimisation. That is precisely the distortion a coaching system must not reinforce.
- **Poker**: Potter van Loon, van den Assem & van Dolder (2015), *PLOS ONE* 10(2):e0115479 — 456 million player-hands; performance persisted across six-month periods but individual rank correlations were only ~0.074–0.104; top vs bottom decile differed by ~+5.1 vs −5.9 bb/100; simulation indicated skill "predominated" only after ~**1,500 hands**. Levitt & Miles (2011) identified skilled WSOP entrants ex ante by ROI (>30% vs ≈−15%) — https://www.nber.org/papers/w17023 — and a 2023 study of 91,439 players (>85M hands) estimated skill explained ~17.2% of hand-level outcome variance.
  → **Skill changes the distribution of outcomes; it does not eliminate variance.** This is the calibration for how many rounds are needed before a CS behavioural rate can be read at all.
- **DIVAT** (Billings & Kan, 2006, *ICGA Journal* 29(3)): score poker decisions by the expected-value difference between the action taken and the alternatives — a lower-variance estimate of decision quality than winnings. The transferable recipe: (1) what information was available ex ante; (2) what actions were available; (3) expected value of each; (4) EV lost relative to best; (5) the counterfactual runouts. https://doi.org/10.3233/ICG-2006-29302
- **Caution on expected-value metrics**: a 2024 analysis shows xG-family models contain systematic biases that confound finishing ability — **a metric built to be outcome-independent can still smuggle outcome information or shooter-independent assumptions into individual ratings** (arXiv:2401.09940 — https://arxiv.org/pdf/2401.09940 ). Treat any CS2 "expected kill / expected survival" metric as a model with a *stated bias budget*, not as truth.

**15.4.8 — Ranked reference-standard options, worst to best.** `Research-supported` (synthesis)
1. **Absolute "was this optimal" labels** — least defensible at this player level; expect low expert agreement and a κ-paradox mess (§15.5).
2. **Blinded expert panel with adjudication**, reported as a distribution, with expert–expert κ as the ceiling and hard-case reproducibility estimated.
3. **Comparison against a named plausible alternative** (pairwise), which sidesteps the need for an absolute label and matches chess/Go practice.
4. **Behavioural criterion where one exists** (does the flagged pattern predict round loss / economic damage beyond chance), with variance reduction and pre-registered hypotheses — objective, but confounded by teammates and variance.

---

### 15.5 Inter-rater agreement: which statistic, and how to read it

**15.5.1 — Coefficient choice depends on data structure, not preference.** `Standard`

| Structure | Statistic | Note |
|---|---|---|
| 2 raters, nominal | Cohen's κ (weighted if ordinal) | Report raw agreement + 2×2/κ table. |
| ≥3 raters, one nominal label each, no missing | Fleiss' κ | Fleiss' κ fixes raters per item; not a drop-in with missing data. |
| ≥3 raters, missing ratings, and/or mixed levels | Krippendorff's α | Nominal/ordinal/interval/ratio difference functions. |
| Continuous / fine-grained ordinal scores | ICC (**state absolute agreement vs consistency**) or Bland–Altman | Different estimands. |
| Counts/durations/timestamps | Agreement within a tolerance window + ICC/Bland–Altman | **κ is inappropriate for timestamps.** |

Sources: standard methodology summaries — https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/ ; sports notational-analysis convention of weighted κ on ordinal, spatially-structured categories — https://www.tandfonline.com/doi/abs/10.1080/24748668.2007.11868383

**15.5.2 — The κ threshold bands are a 1977 convention, and a low κ on a rare code is not evidence of a bad codebook.** `Demonstrated` (mathematical property)
Landis & Koch (1977) introduced the methodology and illustrated it; the verbal bands ("substantial", "almost perfect") are interpretive conventions that the field hardened into rules. https://pubmed.ncbi.nlm.nih.gov/843571/
Feinstein & Cicchetti (1990) — the canonical statement of the two κ paradoxes (marginal imbalance/asymmetry): **high agreement can coexist with κ ≈ 0**. https://pubmed.ncbi.nlm.nih.gov/2348207/
Byrt, Bishop & Carlin (1993): κ is driven by both prevalence and bias; report both. https://www.sciencedirect.com/science/article/pii/089543569390018V
→ A low κ on "bad utility usage" (a 5%-prevalence code) is expected and is not a defect.

**15.5.3 — A stricter reading exists: κ < 0.60 inadequate, and point estimates without CIs and raw agreement are uninterpretable.** `Research-supported`
McHugh (2012) proposes 0.60–0.79 = moderate, 0.80–0.90 = strong, and argues the usual bands are too permissive for decisions with consequences. https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/

**15.5.4 — Krippendorff's own guidance, with the cost-of-error caveat.** `Research-supported`
α ≥ .800 for conclusions; .667–.800 only for tentative/exploratory conclusions; the cut-off should depend on the cost of error; report a confidence interval, not a magic number. (Cite: the UPenn repository copy — https://repository.upenn.edu/bitstreams/b6ea3a5b-3dee-4f27-a159-e44393eda7d4/download )
Note: this is the *same author* who later cautioned against treating α as a threshold test — report α, its CI, and the raw table.

**15.5.5 — The choice among κ, Gwet's AC1/AC2, and PABAK is itself contested.** `Contested`
Gwet's coefficients use a different chance-agreement model and are more stable under high prevalence, but the *Journal of Clinical Epidemiology* published an exchange arguing they are **not substitutes** for κ (different estimands) — https://www.jclinepi.com/article/S0895-4356(21)00284-5/fulltext ; comparative studies find estimator rankings change with the true reliability and design — https://link.springer.com/article/10.1186/s12874-022-01707-5 ; PABAK can look better without recovering the true reliability and should not be read as the same parameter — https://pmc.ncbi.nlm.nih.gov/articles/PMC2636838/
→ Pick one, justify it, and run a sensitivity analysis with a second coefficient.

**15.5.6 — What sport and medicine actually accept.** `Research-supported`
- Sports notational analysis: κ ≥ .80 target for main variables; .61–.79 often defensible for complex tactical/subjective judgments; <.40 generally insufficient. https://www.tandfonline.com/doi/abs/10.1080/24748668.2007.11868383
- Methodological quality scales for sports video analysis (QA-SIVAS) formalise clear coding units, trained coders, a random reliability subsample, and per-variable reporting. https://pmc.ncbi.nlm.nih.gov/articles/PMC10799118/
- Video-review reliability in sport (BJSM 2025) reports the same asymmetry: clearly defined visible events reach high agreement; inferential/tactical constructs do not. https://bjsm.bmj.com/content/59/23/1678

**15.5.7 — Consequence for the coach: run the agreement analysis twice.** `Plausible-untested` (design)
Track A — **description/occurrence** (was there a wide swing? did a smoke cover the lane at tick T? was a trade available?) — expect α ≥ .80. Track B — **quality/counterfactual** (was swinging wrong? was the alternative better?) — expect α ≈ .4–.7, and treat that as a *measured property of the task*, not a failure. Which track the system is graded on must be stated for every reported number.

---

### 15.6 False positives, false negatives, and the error matrix

**15.6.1 — The right frame is a 2×2 over claims, not over rounds.** `Plausible-untested` (design)

| | System claims "this was a flaw" | System says nothing / abstains |
|---|---|---|
| **Expert panel agrees there was a flaw** | **TP** (true positive) | **FN** (missed error) |
| **Panel disagrees / flaw is role- or information-justified** | **FP** (false accusation) — *highest severity* | **TN** (correct abstention) |
| **Panel cannot agree / insufficient information** | **FP-ambiguous** — must be reported separately | **Correct abstention on low-information round** |

Three additional categories the matrix hides and must be reported independently:
- **Unsupported-but-not-false**: claim is true in general but not grounded in this round (a grounding-coverage failure, not a factual error — §15.3).
- **Outcome-driven false positive**: the "flaw" exists only because the round was lost (detectable by re-running with outcome labels removed and measuring label flips).
- **Template/distributional FP**: the same complaint repeated across many rounds (produces habit claims from one instance — §13.3.3).

**15.6.2 — Severity weighting matters more than raw rates.** `Plausible-untested` (design)
A false accusation that tells an expert player to stop doing something correct is far more costly than a missed minor inefficiency (it can degrade a strength). Report **severity-weighted FP/FN**, and report FP rate *separately for high-Elo-typical correct-but-unconventional plays* — those are where the system's parametric "correct CS" priors will fire wrongly.

**15.6.3 — Expect difficulty-dependent reproducibility, and stratify accordingly.** `Demonstrated`
Forensic and radiology evidence (§15.2.2, §15.4.1): hard cases have low reproducibility. Report per-stratum rates (high-information vs low-information rounds, decisive vs non-decisive). A single aggregate FP rate on a mixed set is not interpretable.

**15.6.4 — The sycophancy failure mode is the specific FP risk for coaching.** `Demonstrated`
Sharma et al. (Anthropic, 2023) — five state-of-the-art assistants showed sycophancy across four free-form tasks; both humans **and preference models** preferred convincingly-written sycophantic answers over correct ones a non-negligible fraction of the time. https://arxiv.org/abs/2310.13548
Cheng et al. (arXiv 2025-10-01; *Science* 2026-03-26, DOI 10.1126/science.aec8352): 11 models affirmed users **~49% more often than human responders**; three preregistered experiments (n = 2,405) showed reduced willingness to apologise or take responsibility. https://arxiv.org/abs/2510.01395
→ A coach that validates the player's in-game choice instead of calling it wrong is the sycophancy failure mode. **It must be tested explicitly**: a set of rounds where the player's action is definitively wrong and the player's own framing in comms/notes defends it.

**15.6.5 — The "results-driven FP" test is cheap and should be mandatory.** `Plausible-untested` (design)
Take a fixed set of rounds. Run the analyser twice: (a) with outcome labels visible, (b) with outcome labels stripped. Measure **label flip rate**. A system whose judgments change when only the result changes is violating §13.5, and the flip rate is a direct, quantitative outcome-bias measure.

---

### 15.7 Consistency and reproducibility

**15.7.1 — "Temperature 0 with a fixed seed" is not deterministic in hosted APIs.** `Demonstrated`
Atil et al. (2024-08-06): 5 LLMs × 8 tasks × 10 runs; accuracy variation across naturally occurring runs up to **15 percentage points**; best-possible to worst-possible gap up to **70 points**; no model gave repeatable accuracy across all tasks. Non-determinism is likely *structural* to batched hosted serving. https://arxiv.org/abs/2408.04667

**15.7.2 — Judge intra-rater reliability is low: same judge, same item, different run, different score.** `Demonstrated`
Haldar & Hockenmaier, *Rating Roulette*, Findings of EMNLP 2025: scores inconsistent across runs, "almost arbitrary in the worst case". https://aclanthology.org/2025.findings-emnlp.1361/
→ **Every judge call must be repeated, and per-item score variance reported.** Any single-run score is a sample, not a measurement.

**15.7.3 — Repeated-attempt reliability needs pass^k, not pass@1.** `Demonstrated`
τ-bench: even GPT-4o-class function-calling agents succeed on <50% of tasks, with **pass^8 < 25%** in the retail domain. https://arxiv.org/abs/2406.12045
→ The right metric for "does the coach give consistent advice about the same round" is `pass^k` over k independent re-runs, plus the score distribution.

**15.7.4 — Benchmark scores need intervals.** `Research-supported`
Blackwell, Barry & Cohn (2024-10-04, rev. 2025-06-27) motivate quantifying benchmark uncertainty exactly because models are stochastic even at temperature 0 with a fixed seed and few studies do it. https://arxiv.org/abs/2410.03492

**15.7.5 — Prompt format alone moves accuracy by up to 76 points, and format performance correlates only weakly across models.** `Demonstrated`
Sclar et al., ICLR 2024: sensitivity persisted with scale, more shots, and instruction tuning. They propose **FormatSpread** — report an *interval* of performance across plausible prompt formats, and treat single-format comparisons between systems as methodologically invalid. https://arxiv.org/abs/2310.11324

**15.7.6 — The same endpoint changes behaviour without a version change.** `Demonstrated`
Chen, Zaharia & Zou (2023-07-18): GPT-4's prime/composite accuracy went from 84% to 51% between March and June 2023 — *"the behavior of the 'same' LLM service can change substantially in a relatively short amount of time, highlighting the need for continuous monitoring."* https://arxiv.org/abs/2307.09009

**15.7.7 — Version pinning is necessary but insufficient: snapshots are retired on a schedule.** `Standard` (provider policy)
OpenAI deprecation policy (accessed 2026-10-15): ≥6 months' notice for GA models, ≥3 months for specialised variants, and **as little as ~2 weeks for preview models**; `shutdown_date` is exposed on `GET /v1/models` for programmatic monitoring. As of 2026-10-14, GPT-4o, GPT-4o mini, GPT-4.1 and GPT-4.1 mini snapshots are scheduled for shutdown on **2027-01-14**. https://developers.openai.com/api/docs/deprecations
→ **A model migration is an evaluation event.** The harness must be re-run and re-baselined at every migration, and no coaching-quality number is valid across a migration.

**15.7.8 — A concrete consistency protocol.** `Plausible-untested` (design)
1. For each eval item, run the full pipeline **k ≥ 5** times with a pinned model snapshot.
2. Report: mean score, per-item SD, and pass^k for the claim types that must be stable.
3. Run each item under **≥3 prompt formats** (paraphrases, ordering variants) and report the FormatSpread interval.
4. Re-run the entire suite on every model migration, and whenever a provider announces a shutdown date.
5. Report results as **distributions**, and compare distributions (e.g. P(A beats B) across bootstrap resamples) rather than means (§15.11.3).

---

### 15.8 Calibration and uncertainty expression

**15.8.1 — Verbalised confidence is systematically overconfident and clusters at 80–100%.** `Demonstrated`
Xiong et al., ICLR 2024: 8 datasets, 5 models. Average ECE ≈ 0.52 (GPT-3), 0.377 (GPT-3.5), 0.18 (GPT-4) in the vanilla verbalised setting; GPT-4's average AUROC ≈ **62.7%** (50% = random). Crucially: prompting (CoT, Top-K, self-probing) can **reduce ECE without improving discrimination**, because accuracy rises while the model still says "confident" to nearly everything. Sampling consistency across independent generations was often the better failure-prediction signal. Authors' stated limitation: fixed-form QA with unique answers; open-ended generation not covered. https://arxiv.org/abs/2306.13063

**15.8.2 — Counterpoint: verbalised confidence can beat token probabilities.** `Demonstrated`
Tian et al., EMNLP 2023: for ChatGPT, GPT-4 and Claude, verbalised confidences emitted as output tokens were typically better calibrated than conditional token probabilities on TriviaQA, SciQ and TruthfulQA — often ~50% relative ECE reduction. https://arxiv.org/abs/2305.14975
**Reconciliation:** verbalised confidence carries real information, but its absolute level is inflated and its ordering quality is task-dependent. **Measure it; do not assume it.**

**15.8.3 — The coach produces *claims*, not probabilities — so calibrate the claim.** `Plausible-untested` (design)
For each judgement the system emits, elicit a probability (e.g. "70% that this was a mistake") and calibrate it against the panel label. Then report:
- a **reliability diagram** and **ECE with CIs**;
- **AUROC** for discrimination (separate from calibration — the two are distinct and prompting can move one without the other);
- the **risk–coverage curve** for the decision "commit a claim vs abstain".

**15.8.4 — ECE is itself a biased estimator at realistic sample sizes.** `Demonstrated` (statistical property)
Kumar, Liang & Ma, NeurIPS 2019: binning-based ECE estimates are biased with limited data; debiased estimators exist; "ECE = x" comparisons across different n are not apples to apples. https://arxiv.org/abs/1909.10155
→ Report ECE with CIs and state n and binning; do not compare ECE across sets of different size.

**15.8.5 — The "should the coach speak?" decision is a selective-prediction problem.** `Standard` (methodology) / `Plausible-untested` (for LLM coaching)
Geifman & El-Yaniv (2017): construct a selective classifier that lets the user *set a desired risk level* and reject to meet it (e.g. 2% top-5 ImageNet error at 99.9% probability with ~60% coverage). https://arxiv.org/abs/1705.08500
→ Choose an operating point on the coverage axis ("the coach only commits on the N% of decisions it can judge"), commit to a risk bound, and report the curve.

**15.8.6 — Abstention is measurable and reasoning models are worse at it.** `Demonstrated`
AbstentionBench (2025-06-10): 20 datasets, 6 abstention scenarios (unknown answer, underspecified, false premise, ambiguous/subjective, outdated, underspecified reasoning), >35,000 unanswerable questions. Headline: reasoning models showed an average **24% degradation** in abstention vs their non-reasoning counterparts; scaling helped little; system prompts helped but did not fix it. https://arxiv.org/abs/2506.09038
Also: Madhusudhan et al. (2024) black-box Abstain-QA benchmark with an answerable/unanswerable confusion matrix — https://arxiv.org/abs/2407.16221 ; TACL 2025 survey of abstention — https://aclanthology.org/2025.tacl-1.26.pdf

**15.8.7 — The concrete protocol.** `Research-supported` (synthesis)
(a) Elicit verbal confidence **and** sample k ≥ 5 judgments, using agreement as a second signal;
(b) fit a calibration map on a held-out set; report a reliability diagram plus ECE with CIs;
(c) evaluate the risk–coverage curve for commit-vs-abstain;
(d) score abstention with an answerable/unanswerable confusion matrix, **including false abstention on answerable items**, because reasoning-tuned models over-answer.

---

### 15.9 Blind evaluation, and debiasing the evaluators

**15.9.1 — Position bias is systematic and worst when the two options are close in quality.** `Demonstrated`
Shi et al. (v1 2024-06-12; v9 2025-11-11; AACL-IJCNLP 2025): 15 judge models, MTBench+DevBench, ~40 generating models, >150,000 evaluation instances; introduces repetition stability, position consistency, preference fairness. https://arxiv.org/abs/2406.07791
→ Any pairwise comparison (decision taken vs alternative) must be run **in both orders** (or order-randomised), and the residual order effect reported.

**15.9.2 — Verbosity bias is measurable and correctable.** `Demonstrated`
Dubois et al. (COLM 2024), length-controlled AlpacaEval: controlling for length difference raised Spearman correlation with Chatbot Arena from 0.94 to 0.98. https://arxiv.org/abs/2404.04475
→ A longer coaching answer is preferred by the judge unless output length is controlled or comparisons are length-matched. **This matters directly for §14.9's "short reports" conclusion: a judge comparison will systematically prefer the verbose version.**

**15.9.3 — Self-preference, and generator–judge leakage.** `Demonstrated` / `Experimental`
- Self-preference is best explained by familiarity/perplexity: GPT-4 assigns higher scores to low-perplexity text regardless of who wrote it. https://arxiv.org/abs/2410.21819
- Self-recognition accuracy correlates linearly with self-preference strength under fine-tuning. https://arxiv.org/abs/2404.13076
- **Preference leakage**: same-model generator/judge inflates scores by ~**23.6%** on average; judges could not reliably identify the related model, so the bias is subtle. https://arxiv.org/abs/2502.01534
→ **Never use the same model family as both generator and sole judge.** Use a different family, or blinded human grading on a subsample (or both).

**15.9.4 — Score compression and scale/prompt sensitivity are large enough to swamp real differences.** `Experimental`
Vaugrante & Hagendorff (2026-10-04): 10 reasoning models, multiple designs. Changing only the rating scale shifted measured bias by ~**0.93 points on a 1–7 scale**; prompt detail changed leniency by **28.9 percentage points**; **model identity was the dominant variance source (up to 56.1pp)**. Counter-intuitively, lower reasoning effort changed neither accuracy nor leniency. https://arxiv.org/abs/2610.05094

**15.9.5 — Agreement percentage is an inadequate alignment metric.** `Experimental`
Thakur et al. (GEM² 2025): 13 judge models, 9 exam-taker models; only the largest models showed reasonable human alignment; found sensitivity to prompt complexity and a leniency bias; judges differ from human point scores by up to 5 points. https://aclanthology.org/2025.gem-1.33/

**15.9.6 — Blinding rules for our harness.** `Plausible-untested` (design)
1. **Outcome-blind adjudication**: panellists see the decision point and the information set, not the round result. (Directly implements the §13.5 principle; Baron & Hershey 1988 is the reason.)
2. **Source-blind**: panellists cannot tell whether a judgement came from the AI or a human (controls for the "it's an LLM" halo and its inverse).
3. **Order-randomised pairwise presentation** with position-effect reported.
4. **Length-matched** AI vs human items, or length as a covariate.
5. **Cross-family judging** where an LLM judge is used at all.
6. **Time-and-place rules** designed so a panellist does not see the same round twice across conditions in one sitting (washout, radiographic-reader style).

---

### 15.10 Counterfactual limits: what the system may and may not claim

**15.10.1 — "Counterfactual" must be restricted to *holding measured circumstances fixed*.** `Demonstrated` (as a definitional restriction)
Mahmudlu et al., *What If They Took the Shot? A Hierarchical Bayesian Framework for Counterfactual Expected Goals* (arXiv:2511.23072, v2 2026-10-14). The paper is explicit: *"we use the term 'counterfactual' in a deliberately restricted sense. It refers to evaluating an alternative shooter under the measured circumstances of a recorded attempt, rather than predicting what would actually happen following a substitution… Replacing a player could alter movement, interactions with teammates, shot selection and the opportunities that arise, none of which is represented by holding the recorded context fixed."* And empirically: the owner-effects it estimates are **small relative to posterior uncertainty**, with intervals including zero. https://arxiv.org/html/2511.23072
→ **The CS translation:** "given the state at tick T, what does a comparable population do from here, and what does that imply?" — **not** "if you had done X, you would have won the round."

**15.10.2 — Causal claims require overlap/common support.** `Research-supported`
Alam et al., *Framing Causal Questions in Sports Analytics: A Case Study of Crossing in Soccer* (arXiv:2505.11841): the effect of an action is estimable only where both the action and its alternative actually occur in comparable states; the paper identifies positivity/overlap as a required assumption and reports ATE 0.033 vs ATT 0.035 with strong common support in its data. https://arxiv.org/abs/2505.11841
→ **Concrete rule for the coach:** only offer an alternative if comparable states in the reference population show players actually taking it. Otherwise say so. This is a direct, implementable guard that doubles as free calibration.

**15.10.3 — The general counterfactual problem is acknowledged field-wide.** `Demonstrated`
The Action Valuation survey (arXiv:2504.06163) frames the two field-level difficulties as data scarcity and the absence of explicit ground-truth annotations, and notes that AV "off-ball actions" and sparsity of desired outcomes remain open. https://arxiv.org/html/2504.06163
2025–2026 work is actively extending to counterfactuals: *Monte Carlo Pass Search* for 3D counterfactual pass evaluation (CVPR 2026 workshop — https://openaccess.thecvf.com/content/CVPR2026W/CVsports/papers/Kang_Monte_Carlo_Pass_Search_Using_Trajectory_Generation_for_3D_Counterfactual_CVPRW_2026_paper.pdf ) and *Beyond Outcome Bias* (KU Leuven, MLSA 2025 — https://dtai.cs.kuleuven.be/events/MLSA25/papers/MLSA25_paper_225.pdf ). These are research directions, not solved methods.

**15.10.4 — The wording rules.** `Plausible-untested` (design, but mechanically enforceable)
| Forbidden | Required form |
|---|---|
| "You should have won that fight." | "In this state, the reference population's contact outcomes were … (n = …, 95% interval …)." |
| "If you hadn't peeked, you'd have won the round." | "Players who did not take this contact in comparable states went on to … in X% of cases (support: n = …)." |
| "You would have had time to rotate." | "Travel time from your position to X was ~Y s at the observed velocity; the round clock had Z s remaining." |
| "They always hit B in 3v3s." | "In this dataset, B was hit in …% of 3v3 rounds on this map (n = …), which is/ is not different from base rate (p = …)." |
→ Every alternative offered must come with **support count and uncertainty**, or it must not be offered.

---

### 15.11 Ablations

**15.11.1 — A single-component ablation does not license a causal claim; implementation choices can produce disjoint conclusions.** `Demonstrated` (in the cited setting) / `Research-supported` (general caution)
Huang (2026-09-30): in GPT-2-small attention-head ablation, a natural post-projection implementation of "zero the head" was nearly uncorrelated with a corrected pre-projection ablation (Pearson r = **0.057**) and selected a **completely disjoint top-5 set**. Binary accuracy hid effects at behavioural floors and ceilings. What made *that* result defensible: a discovery/held-out split, **1,000 matched random-head and layer-matched-head control draws**, a non-saturated continuous metric, ranking stable across splits (Spearman ρ = 0.974), top-5 exceeding both control distributions (Monte Carlo p = 0.001), and replication on a second model. https://arxiv.org/abs/2610.00373

**15.11.2 — The classical pitfalls are catalogued, and they are all present in the naive version of our study.** `Demonstrated` (meta-review)
Liao, Taori, Raji & Schmidt, *Are We Learning Yet?* (NeurIPS 2021 D&B; 107 survey papers): inadequate baselines; implementation variation; finite test sets; metric misalignment; badly computed human baselines. Specifics: implementations of the same algorithm can differ by factors; baselines are routinely under-tuned while proposed methods are tuned hard; **>65% of sampled papers evaluated on ≤3 datasets and ≤2 metrics**; human baselines are often computed from a single annotator — and **expert annotators agree more and detect more errors than novices**. https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/file/757b505cfd34c64c85ca5b5690ee5293-Paper-round2.pdf

**15.11.3 — Seed-only repetition is insufficient; data sampling usually dominates variance.** `Demonstrated`
Bouthillier et al., MLSys 2021: benchmark results should be treated as random variables; data-sampling (bootstrap) variance generally exceeded initialisation variance (typically below half); running hyperparameter optimisation only once biases comparisons; randomising more sources of variation approached the ideal estimator while cutting compute ~51×. Recommend comparing **distributions** (e.g. probability that A beats B) rather than means. https://arxiv.org/abs/2103.03098
Companion: Dodge et al., EMNLP 2019 — rankings can flip with the tuning budget; in a survey of 50 EMNLP 2018 papers, **none** reported all recommended checklist items. https://aclanthology.org/D19-1224/
Also: classic deep-RL reproducibility work (Henderson et al., AAAI 2018) — reported improvements frequently fall within run-to-run variance. https://arxiv.org/abs/1709.06560

**15.11.4 — A general ML-pitfalls checklist worth adopting verbatim.** `Research-supported`
Lones, *Avoiding common machine learning pitfalls* — data leakage, inappropriate baselines, wrong metrics, inadequate validation. https://arxiv.org/abs/2108.02497 ; companion on testing hazards: https://ar5iv.labs.arxiv.org/html/2309.05381

**15.11.5 — Design pattern for our ablations.** `Research-supported` (synthesis)
1. **State the target claim before running**: a specific claim about a specific metric on a specific population. Unstated targets produce post-hoc narratives.
2. **Leave-one-out (full minus X) as primary; forward-selection (empty plus X) as secondary.** A component that matters under one but not the other is interacting with something else — and that is the finding.
3. **Matched random controls.** For each ablation, remove the same number of inputs of the same type/shape. Without this, "removing X hurts" is confounded with "removing anything of that size hurts."
4. **Continuous, non-saturated metrics.** Avoid binary accuracy near floor/ceiling; use graded scores (rank correlation with the panel, mean absolute deviation) and report saturation status.
5. **Discovery/held-out split** plus replication across a second provider, because model identity is the dominant variance source (§15.9.4).
6. **Repeat every cell ≥k times; report intervals; compare distributions** (§15.7, §15.11.3).
7. **Avoid the weak-baseline trap** (§15.12).
8. **Measure headroom first.** If the pipeline already scores near the measured expert–expert ceiling, no component can show a gain.

---

### 15.12 Baseline before AI — the requirement, and what counts as a baseline

**15.12.1 — The requirement as stated.** The brief requires a baseline *before* AI. The literature makes this non-negotiable for three separate reasons: (a) under-tuned baselines are among the most common evaluation failures (§15.11.2); (b) prompt-only strong models already carry substantial parametric CS2 knowledge, so the empty baseline is not weak (§15.12.3); (c) simple, adequately-tuned baselines often match complex methods (§15.11.2).

**15.12.2 — The metric must be evaluated as a metric, not just as a model output.** `Demonstrated` (methodology)
Franks, D'Amour, Cervone & Bornn (2016), *Meta-analytics: tools for understanding the statistical properties of sports metrics*: a metric must be assessed on **discrimination** (does it separate players?), **stability** (does it persist for the same player across seasons?), and **independence** (does it add information beyond existing metrics?) — plus out-of-sample predictive improvement over a fair baseline. The paper also shows that many available metrics are redundant and that model-based adjustments reduce sampling variation. https://arxiv.org/abs/1609.09830
And note Leetify's own drift problem as an illustration: an **unchanged raw score moved to a lower rating** after the 2024-03-27 recalibration because the playerbase improved (§13.8.2).

**15.12.3 — The four baselines that must be beaten, in increasing strength.**
| # | Baseline | Why it is required |
|---|---|---|
| B0 | **Random/trivial** (say nothing / generic advice) | Sanity floor. |
| B1 | **Simple non-LLM rule set** ("you died with no teammate within trade distance" / "you peeked with no util") | Adequately-tuned simple baselines match complex methods surprisingly often (§15.11.2). Rules are also auditable and cheap. |
| B2 | **Strong LLM, no domain signal** (same prompt, digest stripped of demo-derived facts) | This is the true competitor: it measures what the *domain signal* adds, not what the LLM adds over nothing. Directly addresses the §31 parametric-knowledge confound. |
| B3 | **Human expert** (the panel itself, or a paid coach) | The ceiling; and the source of the expert–expert reliability that makes B2's numbers interpretable. |
Also required: **B4, the shipped product of a competitor** where one exists (`Plausible-untested` — none of the 2025–2026 AI-coach products publish validation; see §13.8.2 and the vendor list in §13.10).

**15.12.4 — Human baselines must be held to the same rigour as model baselines.** `Research-supported`
*Position: Human Baselines in Model Evaluations Need Rigor and Transparency (With Recommendations & Reporting Checklist)*, PMLR v267 (ICML 2025) — https://proceedings.mlr.press/v267/wei25s.html ; checklist paper: https://arxiv.org/html/2506.13776
Also relevant: *Preliminary suggestions for rigorous GPAI model evaluations* (arXiv 2508.00875 — https://arxiv.org/pdf/2508.00875v1.pdf ) and *A Practical Guide for Evaluating LLMs and LLM-Reliant Systems* (https://arxiv.org/html/2506.13023v2 ).
And: expert annotators agree more and detect more errors than novices (§15.4.3, §15.11.2) — so **who annotates is a variable that must be reported.**

**15.12.5 — Long-horizon, domain-expert agents are far weaker than short-task benchmarks suggest — establishing the expectation.** `Experimental`
- PaperBench (reproduce 20 ICML 2024 papers; rubrics co-developed with the original authors; 8,316 gradable outcomes): best agent **21.0%**, often planning plausibly but failing to execute. https://openai.com/index/paperbench/
- ScienceAgentBench (102 tasks, validated by nine subject-matter experts): best agent **32.4%** independently, **34.3%** with expert-provided knowledge — i.e. **expert facts alone added ~2 points**. https://hal.cs.princeton.edu/scienceagentbench
- RExBench (novel extensions to research codebases): all evaluated agents failed the majority; best below 40% even with human hints. https://arxiv.org/abs/2506.22598
→ The ~2-point delta from expert knowledge is the single most important number for §15.12.3's B2 baseline: **supplying the right facts is not where the difficulty lives.** Expect the same for CS2: the digest is necessary and probably not sufficient, and the eval must be able to show that.

**15.12.6 — The honest pre-AI protocol.** `Plausible-untested` (design)
1. Hand-label ~200 decision points (stratified by difficulty and information level) with a 3-expert panel; report panel agreement (Track A and Track B, §15.5.7).
2. Run B0–B2 on the same set; report per-claim-type FP/FN with intervals.
3. **Only if B2 is beaten on the pre-registered primary metric** does the domain-signal layer earn its place.
4. Report the *effect size over B2*, not over B0, in any external claim.

---

### 15.13 The brief's 10 test questions, mapped to concrete tests

Every row states: what the question really asks, how to operationalise it, the metric, a pass criterion, and the main threat to validity. **Pass criteria are proposals, not standards** — no external benchmark exists for any of them (`Plausible-untested`).

| # | Question | Operational test | Metric | Proposed pass criterion | Main threat |
|---|---|---|---|---|---|
| **Q1** | Can the model recognize an unnecessary isolated peek? | Build a **negative-control set** of peeks that are *necessary* (entry with utility + trade partner ready; retake with numbers; info-peek with abort plan) alongside genuinely unnecessary ones (no util, no trader, no abort). All annotated by the panel with an explicit information set. | Precision/recall on "unnecessary exposure", **reported separately for the two classes**; plus severity-weighted FP. | Recall ≥ 0.7 on true cases **and** FP-rate ≤ 0.15 on necessary peeks. A high-FP system that flags all peeks fails. | Role confound (§15.2.4): an entry player's job is to peek. **Condition on role or the metric is meaningless.** |
| **Q2** | Good decision / bad outcome vs bad decision / good outcome? | The **outcome-strip test** (§15.6.5): run the analyser on fixed rounds with outcome labels visible vs stripped; measure **label flip rate**. Separately, a hand-built set of 4 cells (good/bad × good/bad outcome) with panel labels. | Flip rate; accuracy on the 4-cell set. | Flip rate **< 5%**; ≥ 80% on the 4-cell set. | Small n per cell; needs deliberate over-sampling of the rare "good decision, bad outcome" cell. |
| **Q3** | Can it evaluate the *actual information available* to the player? | **Information-set reconstruction test.** For each decision, the panel states ground truth from the demo (positions, angles, smokes, blinds, spotted-mask). The system must output its information set; compare. Include cases where the answer is "insufficient information". | Per-claim information-set accuracy; **false-certainty rate** (asserting a fact not derivable from demo fields); abstention accuracy on unanswerable cases. | Info-set accuracy ≥ 0.8 on reconstructable items; **false-certainty = 0 on the four hard-forbidden classes of §13.7**. | §13.7 is binding: the player's rendered view is unknowable. The test must be scored on "potential LOS and recorded state", never "what he saw". |
| **Q4** | Can it identify a genuine pattern across multiple matches? | **Stability test**: require the pattern to recur with a stated denominator across ≥N matches; apply the meta-analytics stability criterion (§15.12.2). Compare system-claimed patterns against panel-identified patterns using a **partition-identification** score (not just per-instance detection). Also: repeat the same corpus analysis on k independent re-runs and on a second model provider. | Stability estimate; pattern-level precision/recall; **replication rate across runs and providers**. | Pattern must replicate across runs and providers; claimed frequency within ±25% of panel estimate; FP-pattern rate ≤ 0.2. | Sampling: a 10-match window is small; role/context drift; the same pattern can be an opportunity effect (§13.3.4). |
| **Q5** | Can it avoid criticizing plays based on omniscient information? | **Omniscience probe**: for each criticism, the evaluator asks "was this derivable from the player's information set (Q3)?" Any criticism whose justification requires information the player did not have is a violation. Complements the outcome-strip test. | **Omniscience-violation rate**: criticisms requiring non-available information / total criticisms. | ≤ 5%, and **0** on the four hard-forbidden classes (voice comms, rendered view, frame-accurate timing, audio). | Requires Q3 to be solved first — this test is downstream of it. |
| **Q6** | Can it explain uncertainty instead of inventing certainty? | Elicit a numeric confidence per claim; check (a) **verbal hedging is present and specific** (names what is unknown), (b) confidence is **calibrated** against the panel (§15.8.3), (c) the counterfactual support count is stated (§15.10.4). | ECE with CIs; AUROC; **calibration-curve slope**; % of alternatives offered with support counts; risk–coverage curve. | ECE below the pre-registered threshold **with CI**, AUROC > 0.65, and **100%** of offered alternatives carrying support counts. | Verbalised confidence is inflated and its AUROC is poor even for strong models (§15.8.1); prompting can reduce ECE without improving discrimination — report both. |
| **Q7** | Can it recognize when insufficient information exists? | **Answerable/unanswerable partition** (§15.8.6): build a set with a known unanswerable fraction (low-information rounds, encrypted-comms-dependent questions, sub-tick-precision questions). Score with an answerable/unanswerable confusion matrix. | Correct-abstention rate; **false-abstention rate**; false-commitment rate. | On the unanswerable set: correct abstention ≥ 0.8. On the answerable set: false abstention ≤ 0.2. | Reasoning-tuned models degrade **24%** on abstention and scaling barely helps (§15.8.6) — set the prior expectation accordingly. |
| **Q8** | Can it offer actionable alternatives? | **Reachability audit**: for each offered alternative, verify (a) it was physically available at that state, (b) comparable states in the reference corpus show players actually taking it (overlap — §15.10.2), (c) it is expressed as an if–then plan with a cue, not a goal (§14.8.4). Panel rates actionability on a defined rubric. | **Support-coverage rate** (% alternatives with adequate common support); reachability-violation rate; mean actionability rating; % formulated as if–then plans. | Support-coverage ≥ 0.8; reachability violations ≤ 5%; ≥ 80% if–then formulation. | "Actionable" is subjective — it must be rubricised into observable sub-components or the LLM judge is unreliable (§15.1.4). |
| **Q9** | Do the recommendations correspond with expert assessments? | **Three-way reliability triangle** (§15.0 rule 2): expert–expert (ceiling), system–expert (claim), novice–expert (floor). Weighted κ or Krippendorff's α by data level; CI, raw agreement, category frequencies; separately for Track A (description) and Track B (quality). | κw / α with 95% CI, per track; discrimination and stability of the system's ratings. | System–expert κw **not materially below expert–expert κw**, and ≥ .60 for Track A. Report the ceiling next to the number, always. | **The ceiling is low.** Expert–expert κw can be ~0.58 in subjective domains and efficacy judgments in sport can score α ≈ .47. A system–expert number without the ceiling is uninterpretable. |
| **Q10** | Does applying the feedback lead to measurable behavioural changes? | **Single-case experimental design** (§15.14), not a win-rate comparison: multiple-baseline across 2–3 target behaviours, staggered introduction, ≥8–12 observations per tier, operational definitions, baseline before feedback, non-targeted comparison behaviours, maintenance at 2–4 weeks. | `correct responses / total opportunities` per target behaviour per match; visual analysis (level, trend, variability, immediacy, overlap, consistency) plus Tau-U. | Change occurs **only after** the intervention is introduced in each tier, with a stable baseline and no comparable change in non-targeted behaviours. | Confounds: patch, meta, team, role, motivation. Pre-register the metric, the target behaviour, and the analysis; otherwise any post-hoc improvement "proves" effectiveness. |

**15.13.1 — Dependency order.** Q3 → Q5; Q1, Q2 → Q4; Q6, Q7 → Q8; Q9 gates any external claim; Q10 is the only test that answers "does it help". Build in that order and do not report Q9/Q10 before Q3 is passing, because everything downstream inherits the information-set error.

**15.13.2 — What these ten tests do not cover, and should.** `Plausible-untested`
- **Player-facing harm**: does the feedback reduce confidence, increase tilt, or cause the player to abandon a correct unconventional style? (Not measured by any of the ten.)
- **Follow-through**: the intention–behaviour gap (d ≈ 0.36, §14.7.5) means a recommendation being *generated* says nothing about it being *executed*. Q10 measures execution, but only for the target behaviours selected.
- **Cost**: token/API cost per report and expert-minutes per eval cycle are first-class practical constraints; report them alongside quality, or the quality claim is not deployable.

---

### 15.14 Measuring behaviour change for one player (how Q10 is actually run)

**15.14.1 — The design is a multiple-baseline SCED, not a before/after.** `Research-supported`
Preferred: **multiple baseline across behaviours** — introduce the goal-setting/feedback intervention at *different times* for 2–3 target behaviours, so that each behaviour changes only after its own intervention begins. This provides repeated demonstrations of effect without withdrawing a beneficial intervention. A **changing-criterion design** is appropriate for shaping a behaviour gradually (e.g. 40% → 50% → 60% of opportunities).
Sources: Mellalieu, Hanton & O'Brien (2006) — https://pmc.ncbi.nlm.nih.gov/articles/PMC1479782/ ; goal-setting-in-sport systematic review — https://www.tandfonline.com/doi/pdf/10.1080/1750984X.2021.1901298

**15.14.2 — The primary measure is a rate, not a count.** `Research-supported`
`behavioural success rate = correct responses / total opportunities × 100`. Raw frequency is confounded by playing time, opponent strength, tempo, and opportunity count — the rugby study explicitly notes absolute counts are affected by weather, opponents, and opportunities to perform the behaviour. https://pmc.ncbi.nlm.nih.gov/articles/PMC1479782/

**15.14.3 — Minimum methodological standards, and the known biases.** `Research-supported`
Required: ≥3 baseline tiers; ideally 8–12 observations per tier; stable or interpretable baselines; staggered (preferably randomised) intervention introduction; operational definitions another observer can apply; inter-observer agreement on 20–30% of sessions; procedural-fidelity checks; non-targeted comparison behaviours; maintenance/follow-up; social validity.
The 2020 meta-regression of 121 SCED papers found **large average effects but positive publication bias, overly large effects in studies with few baseline observations, frequent failure to use multiple-baseline designs, and inadequate procedural-reliability reporting.** https://www.sciencedirect.com/science/article/pii/S1469029218304370
→ Design against those four biases explicitly, or the n = 1 result will be a story rather than a finding.

**15.14.4 — Analysis: visual first, statistic second.** `Research-supported`
Visual analysis across level, trend, variability, immediacy of change, overlap, and consistency across tiers; then a supplementary index (Tau-U, percentage of non-overlapping data) — but statistical indices must not replace visual analysis and experimental logic. https://www.sciencedirect.com/science/article/pii/S1469029218304370

**15.14.5 — Pre-registration is the cheapest credibility upgrade available.** `Plausible-untested`
Write down, before the intervention: the target behaviour, the operational definition, the opportunity set, the primary metric, the number of baseline observations, the introduction schedule, and the success criterion. This is the same discipline the paper-replication literature has converged on (registered reports: Martončik et al. confirmed a null where an unregistered design would likely have found something — §14.1.4).

**15.14.6 — The baseline requirement is quantified: at least six baseline data points.** `Demonstrated` (standard)
The US What Works Clearinghouse (Handbook v5.0) requires **at least six data points in the initial baseline phase** for a design to earn the strongest evidence rating, with limited exceptions for zero within-phase variance. WWC does not require Tau-U or a randomisation p-value — design quality, replication, reliability, fidelity and visual analysis come first. https://ies.ed.gov/ncee/wwc/Handbooks
→ A "first 10 matches" baseline is barely adequate; plan for it explicitly rather than starting the intervention as soon as the tool works.

**15.14.7 — Randomisation plus an exact randomisation test gives n = 1 real inferential statistics.** `Demonstrated` (method)
Randomise the order of conditions (e.g. which of two review protocols is used in a given week, or the start point of the intervention across behaviour targets), prespecify the statistic, then compute the exact p-value as the proportion of allowable assignments producing an effect at least as large as observed. Validity depends on the randomisation being specified and implemented **before** data collection — it is not a post-hoc reshuffle. https://pmc.ncbi.nlm.nih.gov/articles/PMC3652808/

**15.14.8 — Tau-U is the standard non-overlap effect size, and it is a supplement to visual analysis, not a replacement.** `Demonstrated` (method, with documented limits)
Parker, Vannest, Davis & Sauber (2011), *Behavior Therapy* 42(2):284–299 — combines between-phase nonoverlap with within-intervention trend (optionally corrected for baseline trend); range −1 to +1. Cautions: baseline-trend correction applied mechanically can inflate effects; it is sensitive to the number and pattern of observations; **it cannot rescue a weak design.** Report the exact variant, direction and rationale. https://doi.org/10.1016/j.beth.2010.08.006

**15.14.9 — Reporting checklists exist, and which one applies depends on the design.** `Demonstrated` (standard)
**CENT 2015** extends CONSORT to N-of-1 trials (25 items, 44 sub-items; treatment sequence, periods, randomisation, blinding, washout, per-period outcomes) — https://doi.org/10.1136/bmj.h1738 . **SCRIBE 2016** covers the broader single-case family in the behavioural sciences (26-item checklist; withdrawal, multiple-baseline, alternating-treatments, changing-criterion) — https://pmc.ncbi.nlm.nih.gov/articles/PMC5214372/ . Neither is a risk-of-bias tool.

**15.14.10 — The closest esports precedent, and the template to copy.** `Experimental`
White, Miltenberger & Concepcion (2024), *Behavioral Interventions* — a **nonconcurrent multiple-baseline single-case design** with three *Street Fighter V* players: all three improved the targeted anti-air behaviour, **and the improvement generalised to ranked online matches.** n = 3, non-randomised, one game, one behaviour — but it is the closest existing artifact to "one player, video review, measured change in real ranked play". https://doi.org/10.1002/bin.2056

**15.14.11 — Expect your own effect size to be inflated, and count your null results.** `Demonstrated` (negative, about the literature)
Barker et al. (2020) meta-regressed 121 papers (71 usable) of psychological-skills and behavioural interventions in sport using single-case designs: mean effects ≈ **Δ = 2.40 weighted / 2.83 unweighted**, associated with positive publication bias, **short baseline phases**, failure to use multiple-baseline designs, and failure to establish procedural reliability. https://researchonline.gcu.ac.uk/en/publications/the-effectiveness-of-psychological-skills-training-and-behavioral/
→ **If a review protocol shows a huge effect, the first hypothesis is design weakness, not a breakthrough.** Log intervention fidelity and pre-declare the expectation that the true effect is smaller than the observed one.

**15.14.12 — What cannot be demonstrated with the available data.** `Plausible-untested` (absence established)
- **That coaching caused an Elo/rank change.** There is no validated CS2 coach-feedback efficacy trial (§15.1.1); component improvements routinely fail to transfer — an 8-week RCT of physical training improved physical measures but produced **no significant between-group improvement in Aimlabs performance, reaction time or anticipation** (Wachholz et al. 2025, https://doi.org/10.3389/fspor.2024.1504205 ); a 9-session psychological-skills RCT in LoL improved psychological skills and communication but **not** objective in-game skill (Kim & Chang 2022, https://doi.org/10.1123/jsep.2022-0071 ); and practice volume does not predict performance (§14.1.4, §13.6.5). Rank change is a downstream, low-power, multi-cause outcome: report it as a descriptive secondary measure with a confidence interval, never as primary evidence.
- **That the coaching "works in general"** from n = 1. Generalisation requires replication *across behaviours* (multiple baseline), not statistical inference to a population.
- **Which behaviour to target**, because nothing in the literature specifies the CS2 decision taxonomy that process scoring requires. That is the largest single source of unquantified error in any "did coaching change behaviour" claim — and it is what §15.2 and the `D-mistakes` slice's fact layer are for.

**15.14.13 — The minimum viable evidence package for one player.** `Plausible-untested` (design)
Operationalised behaviour + stable ≥6-point baseline + prespecified randomisation or multiple-baseline structure + ex-ante decision records captured before outcomes + process scoring (EV-difference style, not win/loss) + post-review retention/transfer window + Tau-U alongside visual analysis + fidelity log + a declared expectation that the true effect is smaller than the observed one.

---

### 15.15 A minimum viable harness (build order)

`Plausible-untested` (engineering sequence, derived from the dependencies above)

1. **Freeze and version the fact base.** Parser + digest schema version pinned; every derived field traceable to a demo field.
2. **Hard lint rules** for the four forbidden claim classes (§13.7). These need no eval set and catch the worst failures immediately.
3. **Claim decomposer + grounding checker** with negative controls and the two attack tests (§15.3).
4. **Hand-labelled set v1**: ~200 stratified decision points, 3 panellists, Track A / Track B labels, panel agreement reported. Freeze it; the coaching prompt is *not* tuned on it.
5. **Repeatability runner**: k ≥ 5 runs per item, ≥3 prompt formats, cross-family judging.
6. **Baselines B0–B2** wired into the same runner (§15.12.3).
7. **Q3 and Q5** (information set + omniscience) — the gating tests.
8. **Q1, Q2, Q7** (isolated peek, outcome-strip, abstention).
9. **Q6, Q8** (calibration, reachability/actionability).
10. **Q4** (multi-match pattern stability) once ≥N matches are available.
11. **Q9** (three-way reliability) on a fresh held-out slice.
12. **Q10** (SCED) — the only stage that involves changing the player's behaviour, and the only one that can be run concurrently with normal play.

---

### 15.16 §15 contradictions and open questions

1. **Verbalised confidence: overconfident or well-calibrated?** Xiong et al. (ICLR 2024) find it badly calibrated and clustered at 80–100%; Tian et al. (EMNLP 2023) find it better calibrated than token probabilities with ~50% relative ECE reduction. Both are credible; the reconciliation (task type, elicitation, proximity to ceiling) is unsettled. **Unresolved — measure it on our own data.**
2. **How good are LLM judges on expert tasks, really?** Evidence spans 64–68% SME agreement (Szymanski et al., IUI 2025 — https://arxiv.org/abs/2410.20266 ), κw 0.60 ≈ expert–expert 0.58 (§12), ICC 0.818 and κ 0.81 in medicine, and ICC ≈ 0 in one medical factuality study. The pattern *looks* like "operationalised rubric ⇒ usable; open-ended ⇒ not", but that is a cross-study inference, not a controlled comparison.
3. **Is an expert panel a gold standard at all?** No — expert–expert κw ≈ 0.58 in subjective domains, fingerprints show 56% reproducibility on hard decisions, and sport efficacy coding scores α ≈ .47. Yet MRMC machinery still requires *some* reference standard. Nobody in esports has published a judgment-quality standard; the retrieved esports work covers coding of *visible events* only.
4. **Score compression vs intra-rater noise.** Both depress observed agreement, and separating them requires a between-item vs within-item variance decomposition that most judge studies do not report.
5. **Does judged reliability survive a whole report?** Judge benchmarks are almost all single-response or pairwise; our coach emits a *sequence* of claims read as a whole. Long-horizon judge reliability is measured only indirectly, via agentic pass^k.
6. **Parametric CS2 knowledge contamination.** A strong model has likely seen pro strategies and HLTV numbers; we cannot cleanly separate "the judge knows CS2" from "the judge read our facts" without a controlled perturbation study (facts altered, prose kept plausible). Baselines B2 (§15.12.3) partially address this; only the perturbation study resolves it.
7. **What does "ablation" mean when the judge is the same model used to score the ablation?** Requires cross-family judging, or blinded human grading on a subsample. Neither is standard practice yet.
8. **Preview/nondeterministic endpoints make longitudinal evaluation unstable.** Preview models can vanish in ~2 weeks and endpoints drift silently. Any coaching-quality metric that assumes a stable endpoint is invalid.

---

### 15.17 §15 top sources

**Judges, their biases, and judge reliability**
1. Zheng et al., *MT-Bench / Chatbot Arena* (2023-06-09) — https://arxiv.org/abs/2306.05685
2. Shi et al., *Judging the Judges: Position Bias* (v1 2024-06-12; v9 2025-11-11) — https://arxiv.org/abs/2406.07791
3. Thakur et al., GEM² 2025 — https://aclanthology.org/2025.gem-1.33/
4. Szymanski et al., IUI 2025 (expert knowledge tasks) — https://arxiv.org/abs/2410.20266
5. Kumar et al., *Nature Machine Intelligence* (2026-02-11) — https://www.nature.com/articles/s42256-025-01169-6
6. Vaugrante & Hagendorff (2026-10-04) — https://arxiv.org/abs/2610.05094
7. Tan et al., *JudgeBench* (2024-10-16) — https://arxiv.org/abs/2410.12784
8. Li et al., *Preference Leakage* (2025-02-03) — https://arxiv.org/abs/2502.01534
9. Sharma et al., *Sycophancy* (2023-10-23) — https://arxiv.org/abs/2310.13548
10. Cheng et al., *Sycophantic AI* (arXiv 2025-10-01; *Science* 2026-03-26) — https://arxiv.org/abs/2510.01395
11. Dubois et al., *Length-Controlled AlpacaEval* (2024-04-06) — https://arxiv.org/abs/2404.04475
12. Wataoka et al., *Self-Preference Bias* (2024-10-29) — https://arxiv.org/abs/2410.21819
13. Panickssery et al., *LLM Evaluators Recognize and Favor Their Own Generations* (2024-04-15) — https://arxiv.org/abs/2404.13076

**Agreement statistics and expert coding**
14. Landis & Koch (1977) — https://pubmed.ncbi.nlm.nih.gov/843571/
15. Feinstein & Cicchetti (1990) — https://pubmed.ncbi.nlm.nih.gov/2348207/
16. Byrt, Bishop & Carlin (1993) — https://www.sciencedirect.com/science/article/pii/089543569390018V
17. McHugh (2012) — https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/
18. Donner & Eliasziw (1992) κ sample size — https://onlinelibrary.wiley.com/doi/abs/10.1002/sim.4780111109 ; kappaSize — https://cran.r-project.org/web/packages/kappaSize/kappaSize.pdf
19. Krippendorff α guidance and sample-size table — https://repository.upenn.edu/bitstreams/b6ea3a5b-3dee-4f27-a159-e44393eda7d4/download
20. *Interrater reliability estimators tested against true interrater reliabilities* (BMC MRM 2022) — https://link.springer.com/article/10.1186/s12874-022-01707-5
21. Malagoli Lanzoni et al. (2012) table-tennis indicator reliability (α .894 type vs .469 efficacy) — https://sasportssience.blob.core.windows.net/ijtts/IJTTS_7_pdf%20files/IJTTS_7_61-64_Malagoli_1.pdf
22. Novak et al. (2019) esports performance-analysis reliability — https://research.rug.nl/en/publications/performance-analysis-in-esports-part-1-the-validity-and-reliabili/
23. QA-SIVAS methodological quality scale for sports video analysis — https://pmc.ncbi.nlm.nih.gov/articles/PMC10799118/
24. Video-review reliability in sport (BJSM 2025) — https://bjsm.bmj.com/content/59/23/1678
25. Sports notational analysis / weighted κ convention — https://www.tandfonline.com/doi/abs/10.1080/24748668.2007.11868383

**Grounding / hallucination**
26. Min et al., *FActScore*, EMNLP 2023 — https://aclanthology.org/2023.emnlp-main.741/
27. Gao et al., *ALCE*, EMNLP 2023 — https://arxiv.org/abs/2305.14627
28. Bohnet et al., *Attributed QA* (2022-12-15) — https://arxiv.org/abs/2212.08037
29. Es et al., *RAGAS* (2023-09-26) — https://arxiv.org/abs/2309.15217
30. Ramprasad & Wallace, *Do Automatic Factuality Metrics Measure Factuality?* (2024-11-25) — https://arxiv.org/abs/2411.16638
31. Niu et al., *RAGTruth* (2023-12-31) — https://arxiv.org/abs/2401.00396
32. Emery et al., *HalluMix* (2025-05-01) — https://arxiv.org/abs/2505.00506
33. Vectara leaderboard criticism, GitHub issue #128 (open) — https://github.com/vectara/hallucination-leaderboard/issues/128
34. Lin, Hilton & Evans, *TruthfulQA* (2021-09-08) — https://arxiv.org/abs/2109.07958
35. Bang et al., *HalluLens* (2025-04-24) — https://arxiv.org/abs/2504.17550

**Calibration / abstention**
36. Xiong et al., ICLR 2024 — https://arxiv.org/abs/2306.13063
37. Tian et al., *Just Ask for Calibration*, EMNLP 2023 — https://arxiv.org/abs/2305.14975
38. Kadavath et al., *P(True)/P(IK)* (2022-07-11) — https://arxiv.org/abs/2207.05221
39. Kumar, Liang & Ma, *Verified Uncertainty Calibration*, NeurIPS 2019 — https://arxiv.org/abs/1909.10155
40. Geifman & El-Yaniv, *Selective Classification* (2017-05-23) — https://arxiv.org/abs/1705.08500
41. Kirichenko et al., *AbstentionBench* (2025-06-10) — https://arxiv.org/abs/2506.09038
42. Madhusudhan et al., *Abstain-QA* (2024-07-23) — https://arxiv.org/abs/2407.16221
43. *A Survey of Abstention in LLMs*, TACL 2025 — https://aclanthology.org/2025.tacl-1.26.pdf

**Reproducibility / contamination / model drift**
44. Atil et al., *Non-Determinism of "Deterministic" LLM Settings* (2024-08-06) — https://arxiv.org/abs/2408.04667
45. Blackwell, Barry & Cohn (2024-10-04) — https://arxiv.org/abs/2410.03492
46. Haldar & Hockenmaier, *Rating Roulette*, Findings of EMNLP 2025 — https://aclanthology.org/2025.findings-emnlp.1361/
47. Sclar et al., prompt-format sensitivity, ICLR 2024 — https://arxiv.org/abs/2310.11324
48. Chen, Zaharia & Zou, *How is ChatGPT's behavior changing over time?* (2023-07-18) — https://arxiv.org/abs/2307.09009
49. Singh et al., *Evaluation data contamination* (2024-11-06) — https://arxiv.org/abs/2411.03923
50. OpenAI deprecations and notice periods (accessed 2026-10-15) — https://developers.openai.com/api/docs/deprecations

**Other-domain designs, ablations, baselines**
51. McIlroy-Young et al., *Maia*, KDD 2020 — https://arxiv.org/abs/2006.01855
52. Gao, Zhang & Li, *PAGE* Go annotation dataset (2022-11-03) — https://arxiv.org/abs/2211.01559
53. Shin et al., PNAS 2023 — https://www.pnas.org/doi/10.1073/pnas.2214840120
54. Brown & Sandholm, *Superhuman AI for multiplayer poker*, Science 2019 — https://doi.org/10.1126/science.aay2400
55. *Multireader Diagnostic Accuracy Imaging Studies*, Radiology 2021 — https://pubs.rsna.org/doi/10.1148/radiol.211593
56. FDA statistical guidance for diagnostic-test studies — https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda
57. Ulery et al., PNAS 2011 + 2012 reproducibility — https://pmc.ncbi.nlm.nih.gov/articles/PMC3093498/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3299696/
58. Vaccaro, Almaatouq & Malone, human–AI combination meta-analysis (2024) — https://arxiv.org/abs/2405.06087
59. LLM vs clinical professionals meta-analysis (2024) — https://pmc.ncbi.nlm.nih.gov/articles/PMC12047852/
60. Huang, *When Do Attention-Head Ablations Support Causal Claims?* (2026-09-30) — https://arxiv.org/abs/2610.00373
61. Liao et al., *Are We Learning Yet?*, NeurIPS 2021 D&B — https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/file/757b505cfd34c64c85ca5b5690ee5293-Paper-round2.pdf
62. Bouthillier et al., *Accounting for Variance in ML Benchmarks*, MLSys 2021 — https://arxiv.org/abs/2103.03098
63. Dodge et al., *Show Your Work*, EMNLP 2019 — https://aclanthology.org/D19-1224/
64. Henderson et al., *Deep RL that Matters*, AAAI 2018 — https://arxiv.org/abs/1709.06560
65. Lones, *Avoiding common machine learning pitfalls* — https://arxiv.org/abs/2108.02497
66. *Human Baselines in Model Evaluations* (ICML 2025 PMLR v267) — https://proceedings.mlr.press/v267/wei25s.html ; checklist — https://arxiv.org/html/2506.13776
67. *A Practical Guide for Evaluating LLMs and LLM-Reliant Systems* — https://arxiv.org/html/2506.13023v2
68. OpenAI, *PaperBench* — https://openai.com/index/paperbench/ ; *ScienceAgentBench* — https://hal.cs.princeton.edu/scienceagentbench ; *RExBench* — https://arxiv.org/abs/2506.22598
69. Franks et al., *Meta-analytics* (2016) — https://arxiv.org/abs/1609.09830
70. Xarles et al., *Action Valuation in Sports: A Survey* (2025-04-08) — https://arxiv.org/html/2504.06163
71. Mahmudlu et al., *Counterfactual Expected Goals* — https://arxiv.org/html/2511.23072
72. Alam et al., *Framing Causal Questions in Sports Analytics* — https://arxiv.org/abs/2505.11841
73. Yao et al., τ-bench (2024-06-17) — https://arxiv.org/abs/2406.12045
74. CSReplays, *Training the coach* (verification-pass method) — https://csreplays.com/blog/training-the-coach-with-pro-demos

**Single-case design, process scoring, and n = 1 reporting standards (added in integration)**
75. Barker et al. (2013), single-case design review in sport — https://eprints.staffs.ac.uk/2218/1/Barker%20et%20al.%202013%20SCD%20Review.pdf
76. Barker et al. (2020), *Psychology of Sport and Exercise* 51:101746 (SCED effects inflated) — https://researchonline.gcu.ac.uk/en/publications/the-effectiveness-of-psychological-skills-training-and-behavioral/
77. Parker, Vannest, Davis & Sauber (2011), Tau-U, *Behavior Therapy* 42(2):284–299 — https://doi.org/10.1016/j.beth.2010.08.006
78. US What Works Clearinghouse Handbook v5.0 (≥6 baseline points) — https://ies.ed.gov/ncee/wwc/Handbooks
79. Single-case randomisation tests — https://pmc.ncbi.nlm.nih.gov/articles/PMC3652808/
80. CENT 2015 (N-of-1 CONSORT extension) — https://doi.org/10.1136/bmj.h1738 ; SCRIBE 2016 — https://pmc.ncbi.nlm.nih.gov/articles/PMC5214372/
81. White, Miltenberger & Concepcion (2024), *Behavioral Interventions* — https://doi.org/10.1002/bin.2056
82. Romer (2006), *Journal of Political Economy* 114(2) — https://doi.org/10.1086/501171
83. Potter van Loon et al. (2015), *PLOS ONE* 10(2):e0115479 — https://doi.org/10.1371/journal.pone.0115479 ; Levitt & Miles (2011) — https://www.nber.org/papers/w17023
84. Billings & Kan (2006), DIVAT, *ICGA Journal* 29(3) — https://doi.org/10.3233/ICG-2006-29302
85. xG model bias analysis (2024) — https://arxiv.org/pdf/2401.09940
86. Sharpe et al. (2023), *Journal of Electronic Gaming and Esports* 1(1) (multi-dimensional CS:GO performance; pros vs researchers disagree on what "good" means) — https://doi.org/10.1123/jege.2022-0017

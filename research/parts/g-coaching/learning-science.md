# Learning Science for an Expert-Level Competitive FPS Player — Evidence Review

**Scope.** What the learning-science literature actually supports about improving an *already elite* performer (reference case: ~2000 FACEIT Elo, ex-~2400), and what it implies for an AI system that only delivers **analysis + practice prescriptions** (no live coaching, no in-session cueing, no hands on the player).

**Method / epistemic hygiene.** Primary sources (meta-analyses, systematic reviews, preregistered replications, original experimental papers) were retrieved and read at abstract/results level. Every claim below carries a URL. Dates/status as of 2026-10-15. Where a widely repeated number is *not* what the source says, it is corrected. Labels used:

| Tag | Meaning |
|---|---|
| **Demonstrated** | Replicated under design control (multiple labs or a high-quality meta-analysis with consistent direction), effect size quantified. |
| **Experimental** | Real experiment(s), correct direction, but thin: single lab, small n, or heterogeneity that leaves the point estimate fragile. |
| **Research-supported** | Convergent meta-analytic + mechanistic evidence, but causal status or boundary conditions remain debated. |
| **Plausible-untested** | Theory and face validity are good; the specific causal claim in the specific population (elite FPS) has not been tested. |
| **Infeasible** | Cannot be delivered or measured by the stated system, or evidence says the effect does not exist at usable magnitude. |

**Theory vs. study** is marked inline (`[THEORY]` / `[STUDY]`).

---

## 1. Deliberate practice (Ericsson) and its meta-analytic demolition among elites

**1.1 The original construct is narrower than how it is usually cited.**
`[THEORY]` Ericsson, Krampe & Tesch-Römer (1993) defined deliberate practice as *individualized, effortful activity explicitly designed to improve specific aspects of performance, with immediate informative feedback, repeated with refinement, and typically designed/supervised by a teacher or coach who diagnoses errors and sequences progressively harder tasks*. The paper explicitly contrasts it with play, competition/performance, paid work, and mere exposure. The often-cited "10,000 hours" is an **average for the best violin students in one Berlin conservatory sample by ~age 20**, not a threshold or a law; Ericsson himself later said nothing is magical about the number and cited piano-competition winners exceeding 20,000 h. In the 1993 analysis, practice alone was reported to explain ~**48%** of variance in performance.
Category: **Research-supported** (as a construct); the popular 10,000-hour version is **Infeasible** as a claim.
https://doi.org/10.1037/0033-295X.100.3.363 · https://review.firstround.com/content/files/images/blogs/freakonomics/pdf/deliberatepractice-psychologicalreview.pdf

**1.2 The broad meta-analysis: deliberate practice explains a minority of performance variance, and least in professions.**
`[STUDY]` Meta-analysis of **88 studies / 111 independent samples / 157 effect sizes / 11,135 participants** (Macnamara, Hambrick & Oswald, 2014, *Psychological Science*). Pooled *r* ≈ .35 (~12% of variance; ~14% under their corrected dependent-effect-size treatment) — i.e. **~86–88% unexplained**. By domain: games *r* = .51 (**26%**), music .46 (21%), sports .42 (18%), education .21 (4%), professions .05 (n.s., <1%). A later corrigendum revised some domain estimates (e.g. music ≈23%, sports ≈20%, education ≈5%); the qualitative pattern is unchanged.
Category: **Research-supported** (meta-analytic, heavily contested — see 1.5).
https://journals.sagepub.com/doi/full/10.1177/0956797614535810 · https://www.psychologicalscience.org/journals/psychological-science/0956797614535810/ · corrigendum: https://journals.sagepub.com/doi/abs/10.1177/0956797618769891

**1.3 In sport, practice explains almost nothing *among elites*.**
`[STUDY]` Sport-specific meta-analysis (Macnamara, Moreau & Hambrick, 2016, *Perspectives on Psychological Science*): deliberate practice explained **18% of variance overall** in sports performance but only about **1% among elite performers**. Robustness checks: objective performance measures 20%, individual (not group) practice 22%, excluding play/competition composites 17%. The "1% among elites" figure is the single most important number for this project.
Category: **Research-supported**.
https://journals.sagepub.com/doi/10.1177/1745691616635591 · https://scottbarrykaufman.com/wp-content/uploads/2016/06/Macnamara-et-al.-2016-Reply-to-Ericsson.pdf

**1.4 Why elite variance is not explained by hours: range restriction plus ceiling on trainable components.**
`[THEORY]` Once selection has already happened, everyone at the top has accumulated large hours; variance in *accumulated* hours collapses (range restriction) while variance in *outcome* remains. Add measurement error in retrospective self-reported hours, the fact that rank/rating is a noisy criterion, and that many determinants of elite performance (starting age, prior ability, decision speed, team context, patch/meta, opportunity, genetics) are not hours. Macnamara et al.'s answer to "why elites?" is that the remaining variance must be attributed to factors other than accumulated practice or to better measurement of practice *quality* — a claim neither side has fully resolved.
Category: **Research-supported** (as an explanatory account of a meta-analytic finding).
https://pmc.ncbi.nlm.nih.gov/articles/PMC7461852/ · https://pubmed.ncbi.nlm.nih.gov/31708836/

**1.5 Ericsson's rebuttal is definitional, and the reanalysis moves the number — but not to "most."**
`[THEORY]` Ericsson (2016) argued Macnamara et al. "summed hours of any type of practice" (group activity, play, competition) and diluted the construct; Ericsson & Harwell's reanalysis of the same literature reported accumulated practice explaining ~**29%**, rising to ~**61%** after correction for attenuation (unreliable self-report → attenuation). Macnamara et al. replied that Ericsson's own earlier wording allowed performer-designed practice, that removing the allegedly invalid categories barely moved the estimate (18% → 17%), and that the definitional narrowing appeared *after* seeing the result. Practical consequence: **1–61% depending on definition and correction** — the honest reading is "hours of self-reported practice quality are a weak-to-moderate predictor at elite level, and the construct is not operationalized consistently enough to settle it."
Category: **Research-supported** (contested), with the *disagreement itself* being the reliable finding.
https://journals.sagepub.com/doi/10.1177/1745691616635600 · https://pmc.ncbi.nlm.nih.gov/articles/PMC6824411/ · https://journals.sagepub.com/doi/10.1177/1745691616635614

**1.6 The preregistered replication of the flagship study cut the key number roughly in half.**
`[STUDY]` Macnamara & Maitra (2019, *Royal Society Open Science*) ran a **results-blind, preregistered** replication of Ericsson et al.'s violinist study (39 violinists; best / good / less-accomplished). Accumulated "practice alone" through age 18 explained **η² = .26 (26%)**; teacher-designed practice **η² = .23 (23%)** — versus ~48% in the original. Critically, **the best group had not practiced significantly more than the good group**; the difference lay between good and less-accomplished. This is the cleanest evidence that at the elite end, *more practice is no longer the discriminator*.
Category: **Demonstrated** (preregistered replication).
https://doi.org/10.1098/rsos.190327 · https://pmc.ncbi.nlm.nih.gov/articles/PMC6731745/

**1.7 Chess: practice explains ~34%, not most.**
`[STUDY]` Hambrick et al. (2014, *Intelligence*) reanalysis of chess studies: deliberate practice explained ~**34%** of chess-performance variance corrected for measurement error (~30% for music); controlling for IQ reduced the practice–performance correlation from ~.69 to ~.60. Category: **Research-supported**.
https://www.sciencedirect.com/science/article/pii/S0160289613000421

**1.8 In esports the null is direct, and game-specific.**
`[STUDY]` Registered report with **186 CS:GO + 411 LoL ranked players** (Martončik et al., 2024, *Collabra: Psychology*): self-reported deliberate practice predicted rank with standardized **β = .02 (CS:GO)** and **β = −.01 (LoL)** — confirmed nulls at prespecified thresholds. "Ordinary" practice predicted LoL rank at ~*r* = .30 and was null/small for CS:GO (*r* ≈ .13). Average cumulative CS:GO practice ≈ 279 h in that sample (wide spread; not a prescription). This is the closest thing to a CS-specific test, and it says: **retrospective practice-hours self-report has ~zero incremental predictive value for rank in CS:GO.**
Category: **Experimental** (prospective registered report; self-report exposure, cross-sectional outcome).
https://online.ucpress.edu/collabra/article/10/1/117677/200964/Psychological-Predictors-of-Long-term-Esports

**1.9 What elites actually do differs in volume from semi-pros — descriptively.**
`[STUDY]` 52-week longitudinal tracking of professional vs semi-professional esports players: professionals 30.9 ± 8.2 h/week game-specific (19.6 ± 6.9 competitive), semi-pros 24.7 ± 3.6 (15.0 ± 2.7). Descriptive, not causal; an esports coaching framework review notes professional players may accumulate 16,000+ game-specific hours over ~10 years while prior work finds only weak quantity–expertise relations.
Category: **Experimental** (observational).
https://www.sciencedirect.com/science/article/pii/S0747563222002436 · https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2023.1191801/full

**1.10 Massed grinding is measurably worse than distributed play in a very large natural dataset.**
`[STUDY]` Analysis of **162,417 League of Legends players**: players who distributed games across longer time windows achieved higher subsequent performance than those compressing play into short bursts. Observational (selection/motivation confounds), but the effect direction matches the experimental spacing literature (§7) and contradicts "grind 10 games in a row."
Category: **Experimental** (large-N observational).
https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0275843

> **Section verdict: Research-supported.** Deliberate practice is a real and necessary ingredient, but accumulated hours are a weak predictor at elite level (≈1% of variance among elites in sport; ≈0 among CS:GO rank in the only preregistered esports test).
>
> **Implication for an analysis-only AI coach.** Do not optimize for hours, volume, or "grinding more ranked." The defensible design target is **practice quality and error specificity**, because (a) that is the only part of the DP construct still standing, and (b) hours demonstrably do not discriminate at this player's level. Concretely: every prescription should name a *targeted sub-skill*, a *measurable criterion*, and *what feedback closes the loop* — and the system should refuse to present raw session counts as progress. Also: at 2000 Elo, the coach's value cannot be "get the hours in"; it must be *diagnosis at a granularity the player cannot self-observe*.

---

## 2. Motor learning: variability, contextual interference, specificity, feedback schedules

**2.1 The contextual-interference effect is real but small-to-moderate, and strongest in the lab.**
`[STUDY]` Original (Shea & Morgan, 1979, 72 college students; blocked vs random on 3 tasks): random → worse acquisition, better retention/transfer. Modern meta-analysis of **transfer** (Czyż et al., 2024; 34 studies, 86 effect sizes, 1,421 participants): **SMD = 0.55, 95% CI [0.25, 0.86]**, adults **SMD = 0.54**, dropping to **SMD ≈ 0.38** after sensitivity exclusions; heterogeneity **I² ≈ 86%**. Companion **retention** meta-analysis: pooled ~**0.63**, sensitivity **≈ 0.45**.
Category: **Demonstrated** (lab), **Research-supported** (applied).
https://pmc.ncbi.nlm.nih.gov/articles/PMC11349744/ · https://pubmed.ncbi.nlm.nih.gov/38987617/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC11237090/

**2.2 The strongest critical review says the classic pattern holds in only ~20% of outcomes and does *not* generalize to sport skills.**
`[STUDY]` Multilevel critical review (Ammar et al., 2024, *Educational Psychology Review*; 36 studies, 264 effect sizes): only ~**20%** of pooled outcomes showed the canonical pattern (blocked better in acquisition, high interference better for relatively permanent gains); high-interference practice did *not* show a significant overall advantage in pre-to-retention improvement. Conclusion: the CI effect cannot be reliably generalized to gross-motor and applied sport skills.
Category: **Research-supported** (negative/limiting result).
https://link.springer.com/article/10.1007/s10648-024-09892-z

**2.3 Variability helps when variants need *different action plans*, not merely different parameters.**
`[STUDY]` CI effects are robust when task variations require distinct generalized motor programs, and inconsistent when tasks differ only in force/distance/timing parameters (parameter-learning studies). This is the discriminator that decides whether randomization is worth the acquisition cost.
Category: **Experimental**.
https://pubmed.ncbi.nlm.nih.gov/15064191/

**2.4 The guidance hypothesis — "less frequent feedback is better for learning" — failed its best meta-analytic test.**
`[STUDY]` McKay et al. (2022; **61 papers, 75 experiments, 2,228 participants**): **no significant overall benefit of reduced relative feedback frequency**, no reliable benefit at acquisition, immediate retention, or delayed retention, **no reliable crossing-over** from frequent-feedback advantage in practice to reduced-feedback advantage in retention; many studies severely underpowered; wide uncertainty. This is a landmark negative result: an entire coaching heuristic rests on an effect that does not survive pooling.
Category: **Demonstrated** (as a null).
https://www.sciencedirect.com/science/article/pii/S1469029222000334

**2.5 Frequent feedback is *better* for complex skills.**
`[STUDY]` Wulf et al.'s ski-simulator work found 100% feedback produced better retention than 50% for a complex task — the opposite of the naive "reduce feedback" rule; reduced frequency advantaged generalized-motor-program learning but harmed parameterization learning (1993). Bandwidth feedback (feedback only when error exceeds a tolerance) has shown automatization benefits (e.g. complex gymnastic skill), but authors note the effect may come from *which* trials get feedback and from implicit positive reinforcement, not from frequency per se.
Category: **Experimental**.
https://pubmed.ncbi.nlm.nih.gov/20037033/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC3796837/ · https://www.sciencedirect.com/science/article/abs/pii/S0167945715300555

**2.6 Feedback after *good* trials beats feedback after bad trials for retention — with self-control doing part of the work.**
`[STUDY]` Chiviacowsky & Wulf: (a) learners who *self-select* when to receive KR outperform yoked learners on delayed transfer (2002); (b) KR after the three best trials per block produced better no-KR retention than KR after the three poorest (2007), despite identical practice performance; (c) deciding about feedback *after* the trial (i.e. after estimating own error) beats deciding before (2005). Proposed mechanism: learner control plus pre-feedback error estimation builds the intrinsic error-detection loop.
Category: **Experimental** (small samples, few direct replications; direction is consistent across the same lab).
https://www.tandfonline.com/doi/full/10.1080/02701367.2002.10609040 · https://www.tandfonline.com/doi/full/10.1080/02701367.2007.10599402 · https://pubmed.ncbi.nlm.nih.gov/15810769/ · https://pubmed.ncbi.nlm.nih.gov/25477846/

**2.7 Specificity of learning: skill is bound to the practice conditions' information structure.**
`[STUDY]` Proteau et al.: training a manual aiming task with a particular visual-feedback condition, then altering available visual information, produced substantial performance decrement — learning incorporated an integrated sensorimotor representation including the *feedback conditions*. Later work reinterprets part of this as an optimized *movement plan* that becomes inefficient when conditions change (so specificity ≠ rigid motor program).
Category: **Research-supported** (lab).
https://pubmed.ncbi.nlm.nih.gov/1631322/ · https://pubmed.ncbi.nlm.nih.gov/17618424/

**2.8 Transfer-appropriate processing (TAP) explains *why* specificity shows up: match the processing, not the surface.**
`[THEORY]` Morris, Bransford & Franks (1977): encoding effects depend on the overlap between the *operations* engaged at learning and those required at test. Applied to skill: practice should preserve the perceptual cues, decision requirements, timing pressure, and perception–action coupling of the target context — not merely the movement.
Category: **Research-supported** (memory experiments + motor generalization).
https://www.sciencedirect.com/science/article/pii/S0022537177800169 · https://www.sciencedirect.com/science/article/pii/B9780123942937000066

> **Section verdict: Demonstrated for specificity & TAP; Research-supported/Mixed for CI and feedback frequency.**
>
> **Implication for an analysis-only AI coach.** (i) Do **not** prescribe "random practice" globally; prescribe variability where the player must *discriminate and select* between distinct action plans (e.g. mixed entry-vs-retake decision sets, mixed utility lineups), and blocked repetition where a single motor parameter is being refined (e.g. spray control, counter-strafe timing). (ii) Because reduced feedback is not reliably better, the coach should not deliberately withhold feedback for pedagogical purity — but should hand the player *error-estimation* tasks before revealing the answer (2.6), which is the mechanism that survived. (iii) Design drills so practice conditions match match conditions (specificity/TAP): if a drill has no information sources, no time pressure, and no decision, expect no competitive transfer. This is the strongest, most actionable section for the system.

---

## 3. Perceptual-cognitive expertise: anticipation, chunking, gaze, decision training

**3.1 Experts' advantage is primarily anticipatory and search-efficiency, not "better eyes."**
`[STUDY]` Mann, Williams, Ward & Janelle (2007, *JSEP*) meta-analysis: expert advantage in **response time** *r*pb = **.43** (anticipation) and **.31** (decision-making); experts make **fewer fixations** (*r*pb = .12 anticipation; **.44** decision-making) with **longer fixation durations** (overall *r*pb = **.23**, 95% CI [.16, .30]). So the expert signature is *fewer, longer, better-aimed fixations* plus faster anticipation — an information-extraction advantage.
Category: **Demonstrated** (meta-analytic).
https://pubmed.ncbi.nlm.nih.gov/17968048/

**3.2 Chunking / templates: expert memory superiority is position-structure-specific.**
`[STUDY]` Chase & Simon (1973) and successors: chess experts' recall superiority over weaker players appears for *legal, structured* positions and largely vanishes for random positions; Gobet & Simon's **template theory** extends chunking to larger schematic structures with slots. This is the canonical demonstration that perceptual expertise is domain-structured long-term-memory retrieval, not raw span.
Category: **Demonstrated** (highly replicated; random-position null is the control that makes it credible).
https://doi.org/10.1016/0010-0285(73)90004-2 · Gobet & Simon (1996), *Memory & Cognition* 24(4):493–503 (templates; ~50,000 chunks): https://doi.org/10.3758/BF03200937 · https://pubmed.ncbi.nlm.nih.gov/8757497/

**3.3 Quiet eye (QE) correlates strongly with expertise and outcome — the causal claim is contested.**
`[STUDY]` Lebeau et al. (2016, *JSEP*) meta-analysis: 36 included studies (27 nonintervention → 38 effect sizes; 9 intervention → 29 effect sizes). Experts vs novices in QE duration **d = 1.04**; successful vs unsuccessful attempts **d = 0.58**; QE *training* increases QE duration **d = 1.53** and improves performance **d = 0.84**. Caution: the correlation between QE-duration gains and performance gains was only *r* = .45 (p = .12), improving to *r* = .58 after removing one outlier — i.e. the mediating link is fragile.
Category: **Research-supported** (association), **Experimental** (causal, few labs).
https://pubmed.ncbi.nlm.nih.gov/27633956/ · https://www.optilab.net/uploads/2/3/6/1/23618728/lebeau16qe-ma.pdf

**3.4 The QE causal story is actively disputed.**
`[STUDY]` Klostermann's inhibition account: QE duration increases when response-selection/inhibition demands rise (competing actions similar), consistent with QE *suppressing* alternative motor programmes rather than "aiming attention" magically. Other work shows manipulating/disrupting visual information during the fixation has little effect, while task constraints that shorten QE do affect interception performance — a conditional, task-dependent role rather than a universal "longer QE causes better performance." Also, expert QE is not a fixed signature: experts *change* gaze when demonstrating to novices.
Category: **Research-supported** (as a contested mechanism).
https://doi.org/10.1016/j.psychsport.2020.101736 · https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0293955 · https://pmc.ncbi.nlm.nih.gov/articles/PMC7540081/ · https://journals.lww.com/optvissci/fulltext/2021/07000/review__the_quiet_eye_in_sports_performance_is_the.8.aspx

**3.5 Video/perceptual-cognitive training works — on near-transfer tasks; transfer to real play is roughly 40% of the trained-task effect.**
`[STUDY]` 2024 systematic review + meta-analysis of perceptual-cognitive training in team sports (**22 studies, 45 effect sizes**): trained/lab-task improvement **ES = 1.51** [0.98, 2.05]; **on-court performance ES = 0.65** [0.15, 1.16]. Stimulus-format subgroups for decision accuracy: computer-screen video **0.19** (CI **includes zero**), life-size projected 2D video **0.46**, 3D/VR **0.96** — but the subgroup difference was **not significant (p = .449)** and 3D/VR was highly heterogeneous (**I² = 84.7%**).
Category: **Research-supported** (near transfer), **Experimental** (fidelity ranking).
https://pmc.ncbi.nlm.nih.gov/articles/PMC11505547/

**3.6 Temporal-occlusion video training transfers to anticipation, including field tests.**
`[STUDY]` 2024 *Sports Medicine* meta-analysis (**12 intervention studies, 25 effect sizes, 248 participants**): overall **d = 1.21** [0.83, 1.59]; video-test transfer **d = 1.26**; field/perception–action transfer **d = 0.85**; video vs field difference not significant. Note this is anticipatory *perception* training, and the occlusion paradigm (clip cut before the critical action) is directly implementable in a demo-analysis product.
Category: **Research-supported**.
https://pmc.ncbi.nlm.nih.gov/articles/PMC11467115/

**3.7 Direct 3D-vs-2D test: faster decisions, not better ones.**
`[STUDY]` Six-week 3D vs 2D video training in national-level youth handball players: the 3D group produced **faster first-option decisions**, with no pronounced difference in decision *quality*; the 3D group was also faster than a tactic-board control. So "3D improves decision speed" is the only well-replicated component.
Category: **Experimental**.
https://pubmed.ncbi.nlm.nih.gov/26207956/

**3.8 Far transfer from generic perceptual/cognitive training to sport performance: no supporting evidence.**
`[STUDY]` 2024 *Sports Medicine* critical review: no consistent evidence for far transfer of general perceptual or cognitive training to sport performance; typical studies use small samples, weak controls, and outcome measures that resemble the training task. A 2024 follow-up found **no transfer of 3D multiple-object-tracking training to soccer game performance** — immersion ≠ transfer.
Category: **Research-supported** (negative).
https://doi.org/10.1007/s40279-024-02060-x · https://doi.org/10.1016/j.psychsport.2024.102770

**3.9 The action-video-game "brain training" debate: small near-transfer effects, ~zero far transfer.**
`[STUDY]` Bediou et al. (2018) meta-analysis: action-game intervention ***g* = 0.34**; Bediou et al. (2023) preregistered update: ***g* = 0.30** [0.11, 0.50] with substantial heterogeneity and no detected publication bias *in the intervention set*. Counter-evidence: Sala, Tatlidil & Gobet (2018, *Psychological Bulletin*) — small or null training effects on general cognitive ability; Hilgard, Sala, Boot & Simons (2019) reanalysis of Bediou's dataset — publication bias, small-study effects, "salami slicing" (overlapping samples counted as independent), larger effects from a single research network ⇒ bias-adjusted estimates near zero; Sala et al. (2019) second-order meta-analysis — action-game **far-transfer *g* = −0.01** after correction (uncorrected 0.08, CI includes zero).
Oei & Patterson (2013, *PLOS ONE*) is often miscited as a "brain training" demonstration: their own interpretation was **game-specific near transfer** (their trains were 20 h across genres; different genres improved different task families). The misleading *Nature* paper people conflate with it is Anguera et al. (2013, NeuroRacer in older adults) — a custom game with limited, task-adjacent transfer.
Category: **Research-supported:** near transfer **Experimental**; far transfer **Infeasible**.
https://pubmed.ncbi.nlm.nih.gov/29172564/ · https://tmb.apaopen.org/pub/qj0c4ij2/download/pdf · https://pubmed.ncbi.nlm.nih.gov/29239631/ · https://online.ucpress.edu/collabra/article/5/1/30/113031/Overestimation-of-Action-Game-Training-Effects · https://doi.org/10.1525/collabra.203 · https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0058546 · https://www.nature.com/articles/nature12486

**3.10 Aim trainers are validated as *instruments*, not as *interventions* — and returns diminish fast.**
`[STUDY]` KovaaK's (Rogers et al., 2024, *Frontiers in Sports and Active Living*, n = 10 FPS esports players): test–retest **ICC = 0.947–0.995** across four scenarios (Micro/Macro Flicking, Strafe Tracking, Wall Peeking) ⇒ good-to-excellent *measurement* reliability. The authors explicitly caution against extrapolating to in-game transfer (in-game adds cognitive load, movement, recoil, map context). A large longitudinal Aim Lab dataset found shooting accuracy ceilings after ~**5 days**, with hits-per-second improving longer, and diminishing returns after ~**30–60 min per session**. A 2021 randomized three-week CS:GO training study (FPS-naïve participants, in-game training conditions) improved in-game aim-course and firing-range performance — evidence that *in-game* structured practice works, not that trainer practice transfers.
Category: **Demonstrated** (reliability), **Plausible-untested** (trainer→game transfer).
https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2024.1309991/pdf · https://public-pages-files-2025.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.777779/pdf · https://pubmed.ncbi.nlm.nih.gov/34177682/

> **Section verdict: Demonstrated (anticipation/chunking metrics), Research-supported (video/occlusion training near transfer), Experimental (3D-vs-2D, QE causality), Infeasible (far transfer).**
>
> **Implication for an analysis-only AI coach.** The product's highest-evidence play is **occlusion-based anticipation training built from the player's own demos**: cut footage immediately before the opponent's decisive action (peek, utility commit, rotation) and require a decision + confidence rating, then reveal. That paradigm has meta-analytic support (d ≈ 1.2) *and* is buildable from files the system already has. Secondary: prescribe aim-trainer scenarios as *measurement* (ICC-supported) with short sessions (≤30–60 min) and in-game validation, never as proven transfer. Do not sell generic cognitive drills, VR immersion, or "visual acuity" training as performance gains — the far-transfer evidence is negative. Gaze/QE variables should not be prescribed as targets unless the system can actually measure the player's gaze; without eye tracking, "look here longer" is an unverifiable instruction.

---

## 4. Error-based learning, prediction error, and desirable difficulties

**4.1 Error management training: worse during training, better after — especially on novel tasks.**
`[STUDY]` Keith & Frese (2008, *JAP*) meta-analysis (**24 studies, 2,183 participants**): EMT vs comparison training overall ***d* = 0.44**; **post-training transfer *d* = 0.56**; **adaptive transfer (structurally different tasks) *d* = 0.80**; **within-training performance *d* = −0.15**. vs error-avoidant training *d* ≈ 0.58; vs exploratory training (no error encouragement) *d* ≈ 0.19. EMT = active exploration + explicit framing that errors are expected, informative, and not penalized.
Category: **Research-supported**.
https://pubmed.ncbi.nlm.nih.gov/18211135/ · https://www.humanw.tu-darmstadt.de/media/orgpsy/preversioneffectivenessoferrormanagement.pdf

**4.2 Desirable difficulties: conditions that depress practice performance can raise retention.**
`[THEORY]` Bjork: retrieval, spacing, interleaving, generation, variation, and delayed testing are "desirable difficulties" — they reduce fluency during learning but improve durable performance. The framework is a *prediction-generator*, not a single testable hypothesis; individual instantiations vary in evidence quality (spacing: strong; interleaving: conditional; "variability" in sport: mixed — see §2). A reciprocal caution: a 2024 *Journal of Personnel Psychology* re-examination questions the "error encouragement" component specifically, arguing the active-exploration component carries most of EMT's effect.
Category: **Research-supported** (framework), **Experimental** (components).
https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-introducing-desirable-difficulties-into-practice-and-instruction-bjork-and-bjork.pdf · https://econtent.hogrefe.com/doi/full/10.1027/1866-5888/a000333

**4.3 Prediction error is the mechanistic currency of both sensory-motor and reward learning — with an important negative result.**
`[STUDY]` Recent primary work: explicit reward-prediction-error (RPE) information facilitates agile motor adaptation; sensory (limb) prediction errors and task-performance errors drive learning through **separate mechanisms** (*PLOS Biology*, 2024); an integrative framework paper treats motor skill acquisition as reasoning + refinement + retrieval. **Counter-evidence:** "Reinforcement feedback impairs locomotor adaptation and retention" (*Frontiers in Behavioral Neuroscience*, 2024) — reward framing is not uniformly beneficial; it can degrade adaptation. Treat "reward/punishment framing improves learning" as task-dependent.
Category: **Experimental**.
https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0295274 · https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.3002703 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11293869/ · https://www.frontiersin.org/journals/behavioral-neuroscience/articles/10.3389/fnbeh.2024.1388495/full

**4.4 Error-avoidance costs are real but usually inferred, not isolated.**
`[THEORY]` The error-avoidance argument (people who avoid errors reduce exploration, obtain less diagnostic feedback, and thus learn slower) is supported mainly by EMT's transfer advantage (4.1) and by the self-controlled-feedback/error-estimation findings (2.6). There is no clean sports experiment showing that *an elite player's* error-avoidance in ranked play directly suppresses learning rate.
Category: **Plausible-untested** (in this population).
https://pubmed.ncbi.nlm.nih.gov/16060786/

> **Section verdict: Research-supported (error-based learning is a legitimate strategy), Experimental (prediction-error mechanisms), Plausible-untested (sport-specific error-avoidance cost).**
>
> **Implication for an analysis-only AI coach.** The report should not just catalog mistakes; it should **reframe them as the training signal** and, critically, *separate "error in practice" from "error in ranked"*. Highest-leverage deliverable: a **deliberate error-elicitation drill** ("in this DM/retake you must attempt the aggressive peek you normally avoid; here's what to watch for"), because the EMT evidence says the payoff appears *after* training, on novel tasks, and is invisible in practice performance. Design note: because within-training performance actually drops, a metrics dashboard that rewards practice-session stats will punish exactly the behavior that transfers. Do not surface "practice accuracy" as a headline metric.

---

## 5. Feedback timing, after-action review, and video feedback/self-observation

**5.1 Immediate knowledge of results can be worse for retention than slightly delayed KR.**
`[STUDY]` Swinnen et al. (1990, *JEP:LMC*): instantaneous KR improved/facilitated acquisition but **degraded delayed, no-KR retention** relative to KR delayed by a few seconds (interpretation: instantaneous feedback undercuts the learner's intrinsic error-detection). The supporting meta-analysis is Travlos & Pratt (1995, *Perceptual and Motor Skills*, 17 articles): significant but **comparatively small** effects for KR-delay/post-KR-interval during acquisition. Do not cite Swinnen as reporting a meta-analytic *d* — it is an experiment. In *verbal* learning, immediate feedback tends to win (Kulik & Kulik), which is a different literature with different task demands.
Category: **Experimental** (motor), **Research-supported** (small effects).
https://www.sciencedirect.com/science/article/abs/pii/016794579090007Z · https://journals.sagepub.com/doi/10.2466/pms.1995.80.1.3

**5.2 After-action review is one of the better-supported interventions in the entire human-performance literature.**
`[STUDY]` Tannenbaum & Cerasoli (2013, *Human Factors*) meta-analysis (**46 independent samples, 2,136 participants**): overall debrief effect ***d* = 0.67** (~25% performance improvement; ~21% after removing three outliers). The **alignment effect**: when the debrief was conducted with the team, focused on improving the team, and performance measured at team level, ***d* = 1.20** (~38%); when team debriefs were evaluated on *individual* outcomes, ***d* = 0.41**. Definition matters: an AAR is active participation, developmental intent, reflection on specific events, and multiple information sources — **explicitly not passive feedback receipt**.
Category: **Demonstrated** (meta-analytic; mostly team/organizational contexts — generalization to solo FPS is an extrapolation).
https://pubmed.ncbi.nlm.nih.gov/23516804/ · https://cebma.org/assets/Uploads/Tannenbaum-Cerasoli.pdf

**5.3 Video feedback / modelling helps, but the evidence base is low-quality and mostly measures practice performance.**
`[STUDY]` 2022 trial-sequential meta-analysis in PE (15 studies): feedback improved motor-skill learning **SMD = 0.47**, with favourable sensitivity results for visual feedback, visual+verbal, visual **self-modelling**, and expert modelling. Petancevski et al. (2022) systematic review (24 studies, 895 participants): most studies positive, but **18/24 had high risk of bias**, and optimal frequency/timing/duration remain unclear. Ashford et al. (2007) meta-analysis of observational modelling (**55 studies**): adults gained on **movement form/dynamics (δ ≈ 0.80)** but showed **no outcome benefit (δ ≈ −0.02)**; children showed the reverse pattern — i.e. watching a model teaches *how the movement looks*, not *how well the task is done*. Video-modelling studies in soccer (2024) found no consistent superiority of adding an expert model to the learner's own footage. A 2022 PE systematic review (18 studies) reported strong qualitative evidence for observational learning but explicitly declined to pool.
Category: **Research-supported** (as an adjunct), weak for durable transfer.
https://pubmed.ncbi.nlm.nih.gov/36430079/ · https://www.sciencedirect.com/science/article/pii/S1469029222001455 · https://pubmed.ncbi.nlm.nih.gov/17365541/ · https://doi.org/10.1002/jaba.2903 · https://pmc.ncbi.nlm.nih.gov/articles/PMC9407861/ · https://pubmed.ncbi.nlm.nih.gov/32004119/

**5.4 The specific "watch your own VOD" claim for FPS decision-making is untested.**
`[THEORY]` Self-observation/self-modelling is supported for *visible movement form* in motor tasks (5.3). Self-VOD review of tactical/decision errors in an FPS is a different act: it is mostly **episodic memory retrieval + counterfactual reasoning** (metacognition, §8), not perceptual modelling of one's own body. No controlled study identified isolates the incremental effect of self-VOD review on CS-competitive outcomes.
Category: **Plausible-untested** (the burden is on anyone claiming a controlled effect).
https://www.sciencedirect.com/science/article/pii/S1469029222001455 (the closest systematic review, and its risk-of-bias finding)

> **Section verdict: Demonstrated (AAR/debrief effects), Research-supported (video feedback as adjunct, delayed KR small), Plausible-untested (self-VOD review specifically).**
>
> **Implication for an analysis-only AI coach.** The AAR meta-analysis licenses the product's core shape — *structured, event-specific, active review* — and gives a defensible design rule: the review must make the player **generate** the reasoning, not read a verdict. Alignment logic also implies an evaluation caveat: team-level debriefs are worth far more than individually-targeted ones (d = 1.20 vs 0.41); a solo-player tool can only ever claim the individual branch, so the expected effect is materially smaller. Timing: place the report a short delay *after* play (not instant in-game overlays) to protect intrinsic error detection, and never present the score/verdict before the player has judged their own rounds (see 2.6/8.x).

---

## 6. Transfer: near vs far, and why drills don't show up in matches

**6.1 The transfer gradient is the single most consistent finding in this literature.**
`[THEORY + STUDY]` Effects shrink monotonically from trained task → near transfer → far transfer. Numbers from §3: trained task ES ≈ 1.51, on-court ≈ 0.65; occlusion video test d = 1.26, field d = 0.85; action-game far transfer ≈ 0; 3D-MOT → no soccer transfer; aim trainers validated as instruments but no demonstrated game transfer. The mechanism is TAP + specificity (§2.7–2.8): transfer requires overlap in *processing operations and information structure*, not surface similarity of the movement.
Category: **Demonstrated**.
https://doi.org/10.1007/s40279-024-02060-x · https://pmc.ncbi.nlm.nih.gov/articles/PMC11505547/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC11467115/ · https://doi.org/10.1016/j.psychsport.2024.102770

**6.2 The specific reason FPS drills fail to transfer to competitive play is measurable, and it is the missing decision layer.**
`[THEORY]` Aim-training and shooting-range tasks are perception–action loops with a single, externally specified goal and no opponent intent, no information ambiguity, no economy (weapons/utility/money), and no consequence. TAP predicts near-zero transfer from that to round-level decisions, and the CI literature predicts that drills containing no *selection* demand cannot train selection. The corollary is positive: adding representative information (a real opponent pattern, a real timing pressure) while keeping the target sub-skill constant is the transfer-preserving move.
Category: **Plausible-untested** (as stated for CS; derived from demonstrated general principles).
https://pmc.ncbi.nlm.nih.gov/articles/PMC11349744/ · https://www.sciencedirect.com/science/article/pii/B9780123942937000066

> **Section verdict: Demonstrated (gradient), Plausible-untested (the exact CS2 decision-layer account).**
>
> **Implication for an analysis-only AI coach.** Every prescribed drill should be scored on a **representativeness axis** (does it contain the decision, the information, and the time pressure of the target situation?) and the system should publish that score. Concretely: prefer "replay-realistic decision drills with a decision + rationale output" over "mechanical repetitions." The system should also set expectations honestly: a drill improving its own metric by 30% implies a much smaller competitive effect; a claim of far transfer should be treated as a bug in the reasoning, not a feature in the marketing.

---

## 7. Spacing and interleaving

**7.1 Spacing is the most robust effect discussed in this document.**
`[STUDY]` Donovan & Radosevich (1999, *JAP*) meta-analysis (**63 studies, 112 effect sizes**): distributed > massed overall ***d* = 0.46** [0.42, 0.50]; for **simple psychomotor tasks *d* = 0.97**; interval moderators: **<1 min *d* = 0.71**, 1–10 min 0.48, 10 min–1 h 0.26, **>1 day 0.16** (i.e. for motor tasks the *inter-trial rest* does much of the work; "retention" here = ≥24 h). Cepeda et al. (2006, *Psychological Bulletin*) quantitative synthesis of distributed practice in verbal recall reaches the same direction; Cepeda et al. (2008) "temporal ridgeline" shows the **optimal gap grows with the retention interval but sub-proportionally** (≈20–40% of a 1-week interval, only ≈5–10% of a 1-year interval).
Category: **Demonstrated**.
https://gwern.net/doc/psychology/spaced-repetition/1999-donovan.pdf · https://pubmed.ncbi.nlm.nih.gov/16719566/ · https://pubmed.ncbi.nlm.nih.gov/19076480/

**7.2 Classroom-level spacing replicates at scale in 2025.**
`[STUDY]` 2025 meta-analysis of classroom distributed practice (**22 reports, 31 effect sizes, >3,000 learners**): **d = 0.54** [0.31, 0.77], with larger effects for longer retention intervals and higher educational levels. Mathematics-specific 2025 meta-analysis: spacing **g = 0.28** (isolated learning g = 0.43; course-embedded g = 0.24); retrieval-vs-restudy g = 0.18 with CI crossing zero. Note: written/pedagogical literature, not motor.
Category: **Demonstrated** (in its domain).
https://pubmed.ncbi.nlm.nih.gov/40564553/ · https://eprints.whiterose.ac.uk/id/eprint/229807/

**7.3 Interleaving's benefit is conditional — it is a *discrimination* technique, and it backfires for some materials.**
`[STUDY]` Brunmair & Richter (2019) meta-analysis (**59 studies, 238 effect sizes, 158 samples**): overall interleaving **g = 0.42**; mathematics **g = 0.34**; visual category learning **g = 0.67**; **word learning g = −0.39 (blocking better)**. Effects were larger when to-be-discriminated categories were *similar* and within-category items *dissimilar*. A 2024 fraction-arithmetic study found interleaving added **no reliable benefit** on top of explicit instruction. A 2025 study of self-regulated inductive learning showed learners *prefer* blocking because it feels smoother, and that individualized feedback about the evidence can shift their choices.
Category: **Research-supported** (conditional).
https://pubmed.ncbi.nlm.nih.gov/31556629/ · https://www.sciencedirect.com/science/article/pii/S0022537177800169 (TAP background) · https://doi.org/10.1016/j.learninstruc.2023.101854 · https://doi.org/10.1037/edu0000909

**7.4 Applied motor-skill interleaving is the *weakest* branch of the CI family.**
`[STUDY]` See §2.2: in applied sport/gross-motor settings, high-interference practice showed no significant overall advantage (Ammar et al., 2024); the transfer meta-analysis's sensitivity-adjusted adult effect fell to SMD ≈ 0.38 with I² ≈ 86%.
Category: **Research-supported** (as a limiting result).
https://link.springer.com/article/10.1007/s10648-024-09892-z

**7.5 "More variability" is not monotonically better.**
`[STUDY]` "Applying different levels of practice variability for motor learning: more is not better" (2024, *PMC*) — structured moderate variability outperformed extreme variability in at least one motor task. Combined with the schema-variability critique (many studies never verified that learning occurred during acquisition), the honest rule is *calibrated* variability.
Category: **Experimental**.
https://pmc.ncbi.nlm.nih.gov/articles/PMC11212619/

> **Section verdict: Demonstrated (spacing), Research-supported (interleaving, conditional).**
>
> **Implication for an analysis-only AI coach.** Scheduling is the cheapest, most reliable lever the system owns: prescribe distributed short sessions across days (the 162k-player LoL dataset agrees), not weekend blocks. For interleaving, apply it where CS2 has genuinely confusable decision categories (site takes vs retakes; default vs execute; eco vs force vs full-buy decision trees) and *not* to mechanics acquisition. And add a metacognitive surface: because players prefer blocking and feel it works better (§8), the system should explain the expected discomfort — and record predicted-vs-actual so the player learns to trust the metric, not the feel.

---

## 8. Metacognition and judgment calibration

**8.1 The Dunning–Kruger effect, as popularly understood, is largely a statistical artifact of the data structure — and this matters for interpreting "you don't know what you don't know."**
`[STUDY]` Gignac & Zajenkowski (2020, *Intelligence*): the classic low-ability-overestimate/high-ability-underestimate pattern is **mostly a regression-to-the-mean / measurement-artifact phenomenon** arising when both accuracy and self-assessment are on noisy, bounded measures; valid tests require *individual-differences* approaches (e.g. latent variable modelling), not tertile plots. Subsequent work: a 2022 response-plus-replication, and a 2024 *Intelligence* reanalysis ("Rethinking the Dunning-Kruger effect: negligible influence on a limited segment of the population") finding the robust component is small and confined. McIntosh et al. (2019, "Wise Up") found skill related to calibration, but metacognitive differences were a **weak** contributor; when task difficulty was equated so everyone performed comparably, **the DK pattern disappeared**.
Category: **Research-supported** (artifact/limited-effect). Implication: any dashboard that says "low performers overestimate themselves" is trading on a partly artifactual pattern.
https://www.sciencedirect.com/science/article/abs/pii/S0160289620300271 · https://www.sciencedirect.com/science/article/pii/S0160289624000242 · https://www.sciencedirect.com/science/article/abs/pii/S0160289622000988 · https://pubmed.ncbi.nlm.nih.gov/30802096/

**8.2 Expertise does not automatically buy calibration.**
`[STUDY]` Interval-estimation research ("Overconfidence in interval estimates: What does expertise buy you?"): experts produce **narrower and better-centred** intervals but are **not necessarily less overconfident** — confidence can rise faster than accuracy. So "he's a 2400 ex-pro, he knows his own game" is not supported as a general rule; expertise improves *estimates*, not necessarily *calibration*.
Category: **Experimental**.
https://www.sciencedirect.com/science/article/pii/S0749597808000186

**8.3 Illusions of competence are driven by fluency, and they are exactly what a self-coaching player cannot see.**
`[THEORY + STUDY]` Bjork, Dunlosky & Kornell (2013, *Annual Review of Psychology*): learners regulate study via subjective fluency and judgments of learning; fluency during study ≠ retrieval success later, producing illusions of competence. Effective techniques *feel* worse. Empirically: immediate performance cues can inflate JOLs while leaving durable learning unchanged. For an FPS player the analogous trap is "Watching my own VOD feels like learning" and "I know this lineup" (recognition) vs "I execute it under a 6-second site take" (retrieval under load).
Category: **Research-supported**.
https://www.annualreviews.org/content/journals/10.1146/annurev-psych-113011-143823 · https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/RBjork_Dunlosky_Kornell_2013.pdf

**8.4 Calibration training works, modestly, and mostly on the well-defined parts.**
`[STUDY]` Calibration-training literature (Applied Cognitive Psychology, 2024; *Futures & Foresight Science*, 2024, interactive-app calibration training): training with feedback on probability judgments improves calibration, with modest effect sizes and transfer limits; the geopolitical forecasting tournaments (Tetlock/Mellers line, "identifying and cultivating superforecasters") show that **training + practice + frequent scoring** produces modest accuracy improvements and identifies a small elite-quartile, not that everyone becomes calibrated. Key ingredient common to all: **repeated, quantified, externally scored predictions with prompt resolution**.
Category: **Experimental**.
https://onlinelibrary.wiley.com/doi/10.1002/acp.4236 · https://ideas.repec.org/a/wly/fufsci/v6y2024i2ne177.html · https://pubmed.ncbi.nlm.nih.gov/25987508/ · https://www.sas.upenn.edu/~baron/journal/16/16511/jdm16511.html

**8.5 Feedback-seeking is a trainable behavior with a real intention-action gap.**
`[STUDY]` Webb & Sheeran (2006, *Psychological Bulletin*) meta-analysis: medium-to-large changes in intention produce only small-to-moderate changes in behavior (d ≈ 0.36) — the "intention–behavior gap." Relevant corollary: a player who *says* he will review VODs will often not; systems must engineer the behavior, not exhort it (see §9).
Category: **Research-supported**.
https://pubmed.ncbi.nlm.nih.gov/16536643/

> **Section verdict: Research-supported (illusions of competence, intention–behaviour gap), Research-supported/limited (D–K), Experimental (calibration training).**
>
> **Implication for an analysis-only AI coach.** The system can do something no human coach can do cheaply: **keep score on the player's own predictions**. Consistent with 8.4's active ingredient, the highest-value metacognitive feature is a *calibration loop*: before revealing each round's outcome (or before a drill), the player states a probability ("60% they hit B"), then the system resolves it and reports long-run calibration and Brier-style scores. This (a) is the mechanism with experimental support, (b) generates the exactly-aligned feedback that TAP predicts will transfer to in-game probabilistic reasoning (e.g. probability of retake, of an eco-flip), and (c) counters the fluency illusion by making "I know it" resolvable. Conversely: do **not** build features on the folk D–K story; and do not assume the player's self-diagnosis is trustworthy — but do *elicit* it, because the calibration data is the product.

---

## 9. Habit formation

**9.1 The "21 days" figure is folkloric; the best-known estimate is ~2 months, with enormous spread.**
`[STUDY]` Lally et al. (2010, *European Journal of Social Psychology*): tracked daily behaviours (eating/drinking/exercise) with self-reported automaticity; **median modeled time to 95% of asymptote = 66 days, individual range 18–254 days** — and this was computed on the subset whose data fit the asymptotic curve. Missing a single opportunity did not materially derail the trajectory. Critically, the outcome was **self-reported automaticity**, not verified behaviour, and the "95% of asymptote" is a modeling construct, not "then it's a habit."
Category: **Demonstrated** (as described) — but see 9.3 for the measurement critique.
https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674 · https://citeseerx.ist.psu.edu/document?doi=debfb5cc29b7d074b5d2a8951809dfeac0a9867a&repid=rep1&type=pdf

**9.2 The 2024 systematic review cannot meta-analyze "time to habit" at all.**
`[STUDY]` Singh et al. (2024, *Healthcare*, "Time to Form a Habit"): across studies, **medians 59–66 days, means 91–154 days, individual range 4–335 days**; only four studies reported a formation time and methodological differences **prevented a duration meta-analysis**. The review pooled *habit-strength change*, not time. ⇒ Any product claim of the form "habits form in N days" is unsupported.
Category: **Research-supported** (null on the headline question).
https://pmc.ncbi.nlm.nih.gov/articles/PMC11641623/

**9.3 Self-report habit indices conflate automaticity with frequency — so "habit" dashboards can be circular.**
`[STUDY/THEORY]` Sniehotta & Presseau (2012, *Annals of Behavioral Medicine*) and the Gardner et al. reply/rejoinder: the **SRHI mixes behavioural frequency, automaticity, and identity**; when used to predict behaviour frequency, the predictor contains the criterion (inflated associations). Remedy: the four-item **SRBAI** automaticity subscale (Gardner et al., 2012), which retains the expected associations while measuring automaticity specifically. Think-aloud work shows people *infer* automaticity retrospectively (from frequency, difficulty resisting, or not remembering doing it) rather than observing it.
Category: **Research-supported** (measurement critique).
https://academic.oup.com/abm/article-abstract/43/1/139/4563935 · https://pmc.ncbi.nlm.nih.gov/articles/PMC3552971/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC4296343/

**9.4 Implementation intentions ("if situation Y, then behaviour X") have the strongest controlled evidence of any single habit-adjacent technique.**
`[STUDY]` Gollwitzer & Sheeran (2006, *Advances in Experimental Social Psychology*) meta-analysis: **94 independent tests from 63 reports, 8,461 participants**, mean ***d* = 0.65** [0.60, 0.70] for goal attainment versus goal-intention-only/comparison conditions, across varied goals and objective & self-report outcomes. Mechanism evidence: heightened cue accessibility and automatic initiation of the planned response.
Category: **Demonstrated** (in the lab and in health/behavior domains; not tested for esports practice adherence specifically).
https://doi.org/10.1016/S0065-2601(06)38002-1 · https://www.decisionskills.com/uploads/5/1/6/0/5160560/2006_gollwitzersheeran_implementation_intentions_1.pdf

**9.5 Context discontinuity is a real but small window of opportunity.**
`[STUDY]` Verplanken & Roy (2016) field experiment (≈800 residents, half recent movers; ~8-week follow-up; clustered assignment): the intervention × relocation interaction was significant but **small (β ≈ −.08; ~0.6–1.1% of residual variance)**, with the effect statistically confined to those who had moved within ~**3 months**. So: habit disruption opens a window, but the demonstrated effect size is far too small to build a product's theory on. The esports analogue (new patch, new team, new role, hardware change) is a **Plausible-untested** generalization.
Category: **Experimental** (small effect, single field study).
https://www.sciencedirect.com/science/article/pii/S0272494415300487

> **Section verdict: Demonstrated (implementation intentions), Research-supported (habit measurement critiques, no reliable formation timescale), Experimental (habit discontinuity), Plausible-untested (all of it for CS2 practice habits).**
>
> **Implication for an analysis-only AI coach.** Prescribe habits as **if–then plans bound to concrete in-game cues**, not as goals or resolutions: "If we lose the pistol round on T side, then I load the eco-decision drill before the next game." This is the one habit technique with d ≈ 0.65 behind it, and it is trivially representable in a coaching report. Measure **automaticity with an SRBAI-style 4-item scale administered longitudinally**, never with a compound "habit score" that includes frequency (9.3) — otherwise the system will "prove" its own effectiveness circularly. Do not promise habit formation in weeks; the best available distribution is weeks-to-months with a 4–335-day range. Exploit context changes (patch day, new team/role, hardware) as the moment to install new routines, but don't oversell it: the demonstrated effect is small.

---

## 10. Cognitive load theory, expertise reversal, and how verbose the report should be

**10.1 The expertise reversal effect is one of the better-quantified interactions in instructional psychology.**
`[STUDY]` Tetzlaff et al. (2025, *Learning and Instruction*) meta-analysis of the ERE (**60 experimental studies, 176 effect sizes, 5,924 participants**): for **low-prior-knowledge** learners, high-assistance instruction beat low-assistance (**d = 0.505**, 95% CI [0.260, 0.750]); for **high-prior-knowledge** learners, low-assistance beat high-assistance (**d = −0.428** [−0.647, −0.209]); the reversal contrast itself **d = 0.971** [0.631, 1.312]. Heterogeneity was substantial; the authors also report an **asymmetry** — helping novices is more reliably beneficial than stripping help from experts. Origin: Kalyuga, Ayres, Chandler & Sweller (2003), theorized as redundant processing of information the learner could generate from long-term-memory schemas.
Category: **Demonstrated** (meta-analytic), with important boundary conditions (10.3).
https://www.sciencedirect.com/science/article/pii/S0959475225000660 · https://www.tandfonline.com/doi/abs/10.1207/S15326985EP3801_4

**10.2 Irrelevant detail actively harms learning — the seductive-details effect.**
`[STUDY]` Rey (2012, *Educational Research Review*, 39 effects): retention **d = 0.30**, transfer **d = 0.48** *worse* with seductive details; note only 11/39 studies supported the effect, 13 mixed, 15 unsupported. Sundararajan & Adesope (2020, *Educational Psychology Review*; **58 papers, 68 effect sizes, 7,521 participants**): retention-only **g = −0.37** [−0.60, −0.13]; studies measuring both retention and transfer **g = −0.41** [−0.55, −0.28]; **transfer-only not significant**. Time pressure was a significant moderator (larger effects under time limits). Mechanism is not settled (overload vs attention capture vs coherence disruption vs arousal).
Category: **Research-supported** (general but moderated).
https://eric.ed.gov/?id=EJ986386 · https://eric.ed.gov/?id=EJ1263249 · https://pmc.ncbi.nlm.nih.gov/articles/PMC10176302/

**10.3 The redundancy effect is a *different* error from seductive details: duplicated relevant information also costs processing.**
`[THEORY + STUDY]` CLT (Sweller): presenting the same content in multiple, mutually redundant formats (animated diagram + narration + identical on-screen paragraph) imposes extraneous load; the fix is complementary rather than duplicative channels. Boundary: written text helps when the learner controls pace, material is unfamiliar, terminology must be spelled consistently, or the content is not visually dynamic — so "delete all text" is not the rule. Two limits worth noting for AI-generated reports: (a) the ERE was established mostly on **well-structured tasks**; a legal-reasoning study found worked examples helped *both* novices and advanced learners on ill-structured tasks (no reversal) — CS2 decision-making is closer to ill-structured; (b) "high assistance" is not one treatment (hint vs worked solution vs imposed sequence differ), and prior knowledge/assistance are continuous variables often dichotomized artificially.
Category: **Research-supported** (CLT principles), with domain caveats.
https://www.sciencedirect.com/science/article/pii/S0361476X12000677 · https://doi.org/10.1016/j.learninstruc.2025.102142

> **Section verdict: Demonstrated (ERE exists and is large overall), Research-supported (seductive details, redundancy), Experimental/contested (ERE in ill-structured decision domains).**
>
> **Implication for an analysis-only AI coach.** The ERE plus seductive-details results give a concrete answer on report verbosity for a 2000-Elo player: **the long, pedagogical, everything-explained report is the wrong artifact for this user.** The player already has the schemas; a step-by-step explanation of fundamentals is redundant processing, and narrative colour ("this round was lost because...") is seductive detail that measurably reduces transfer (d ≈ −0.4). Design: (i) default to a *short* ranked list of 2–4 decision points with the counterfactual and the cue to watch for; (ii) put full reasoning behind an explicit expand/"why" affordance (learner control); (iii) never duplicate the same finding in a summary, a chart caption, and a "coach's note" — pick one channel; (iv) spend the saved budget on *generation prompts* (ask the player to predict/explain) rather than on more text. Caveat: because CS2 decisions are ill-structured, do not swing to "no guidance" — the legal-reasoning result warns that some worked reasoning still helps even experts; the rule is *remove guidance that duplicates what the player knows*, not remove guidance.

---

## 11. Constraints-led approach / nonlinear pedagogy (Newell's constraints; Renshaw/Davids/Chow)

**11.1 The 2025 systematic review finds promising directional evidence and low confidence.**
`[STUDY]` Burkett et al. (2025, *Sports Medicine – Open*), the most directly relevant review: searched six databases to 2024-05-01, screened **7,450 records, included only 9 studies** (~78% soccer). Technical skill: **34% of outcomes favoured nonlinear pedagogy (NP), 66% showed no significant difference**; tactical skill: **62.5% favoured NP** (one favoured linear), crossing the review's ≥66% threshold only after excluding one serious-risk-of-bias study. No meta-analysis was possible (heterogeneous outcomes) → findings come from **statistical-significance vote counting**, which ignores effect magnitude and precision. Risk of bias: 2 non-randomised studies "serious," the 6 randomised studies "some concerns" (no prespecified analysis plans; 2 lacked randomisation detail). Interventions averaged ~**15.8 sessions over ~7 weeks**, mostly with immediate post-testing, little retention/transfer data.
Category: **Experimental** (evidence of low certainty; direction, not magnitude).
https://link.springer.com/article/10.1186/s40798-025-00893-y

**11.2 Better-controlled CLA meta-analyses show heterogeneity so extreme that pooling is not informative.**
`[STUDY]` Systematic review + meta-analysis of CLA for team synergies: **I² = 99.56%**, with evidence of publication and inflation bias. The 2019 CLA review in interceptive sports reported 77.7% of studies positive but **most with poor quality scores**. Conclusion: the CLA literature's positive ratio is not evidence of magnitude; small sport-science studies with flexible outcomes and no preregistration produce unstable literatures.
Category: **Research-supported** (as a critique).
https://www.sciencedirect.com/science/article/pii/S1469029219303188 · https://journals.sagepub.com/doi/full/10.1177/1747954118812461

**11.3 Much of the "CLA vs traditional" comparison is a straw man.**
`[THEORY]` Lindsay & Spittle (2024, *International Review of Sport and Exercise Psychology* / *IRSE*): the opposition between direct instruction and constraints-led coaching is overstated; contemporary direct instruction already includes representative practice, variable practice, bandwidth feedback, external focus cues, guided discovery, and progressive complexity. The real question is *which principle, when, for which learner* — not which ideology. Note also that the theoretically cleanest CLA claims (perception–action coupling, affordance detection, degeneracy) are **theory**, and studies often bundle task+environment+individual constraints with coach questioning and scoring changes, so causal attribution is impossible.
Category: **Research-supported** (critique) / **Plausible-untested** (the theory's specific causal claims).
https://journals.sagepub.com/doi/10.1177/17479541241240853

**11.4 "Differential learning" (systematic variation/noise) is the weakest sub-branch.**
`[STUDY]` An exploratory meta-analytic review (Frontiers in Psychology, 2021) claims enhanced motor learning; German-language critique literature ("Differenzielles Lehren und Lernen: eine Kritik") and the broader variability-is-not-monotonic findings (§7.5) constrain this. No high-quality preregistered trial in elite performers was identified. Category: **Plausible-untested**.
https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.533033/full · https://link.springer.com/article/10.1007/s12662-012-0251-y

**11.5 Representativeness is the CLA principle that *is* independently supported.**
`[THEORY + STUDY]` The core CLA design heuristic — make practice *representative* of competition (preserve information sources, decision requirements, and action possibilities) — is the same prediction as specificity/TAP (§2.7–2.8) and is corroborated by the transfer gradient (§6) and the stimulus-fidelity findings (life-size first-person > small-screen; §3.5). This is the piece of CLA worth adopting, and it can be evaluated without adopting the rest of the framework. Newell's constraints model (1986) itself is a **theoretical taxonomy** (organism/task/environment), not an empirical claim, and is only as good as the predictions derived from it.
Category: **Research-supported** (representativeness), **Theory** (the taxonomy). Newell's constraints model is Newell (1986), "Constraints on the development of coordination," in Wade & Whiting (eds.), *Motor Development in Children: Aspects of Coordination and Control* (Martinus Nijhoff) — a book chapter with no stable public DOI; see the discussion and citation in https://pmc.ncbi.nlm.nih.gov/articles/PMC8776195/
https://pmc.ncbi.nlm.nih.gov/articles/PMC8776195/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC11505547/

> **Section verdict: Experimental/low-certainty (CLA superiority claims), Research-supported (representativeness as a design principle), Plausible-untested (differential learning).**
>
> **Implication for an analysis-only AI coach.** Adopt CLA's *representativeness* heuristic as a design score on every prescription, and **do not** adopt its stronger claim that explicit instruction is inferior — that claim is not supported at this evidence quality, and the ERE (§10) already tells you the failure mode of over-explaining to an expert is *redundancy*, not directiveness per se. Practically: prefer drills built from the player's own rounds with opponent-context preserved (task constraints varied: 3v2 retake, low-time executes, eco-vs-buy economics) over decontextualised mechanical repetition; and where a specific technical error must be corrected, allow explicit instruction — the review found technical-skill outcomes largely equivalent between pedagogies, so there is no evidence penalty for being direct when directness is what the error requires.

---

## Contradictions / open questions

1. **Deliberate practice: 1% vs 29% vs 61%.** The same literature yields ~1% of elite sport variance, ~18% overall, ~29% for accumulated practice, ~61% attenuation-corrected, and ~0% for CS:GO rank. The disagreement is *definitional and measurement-based* (what counts as practice; self-report unreliability; range restriction) and has no agreed resolution. For a product, the practical floor is: **hours are not a usable predictor; quality is unquantified but the only remaining candidate.**
2. **Contextual interference vs applied reality.** Meta-analytic transfer/retention supports random > blocked (SMD ≈ 0.38–0.55), while the most critical multilevel review finds the canonical pattern in only ~20% of outcomes and no general advantage for applied gross-motor/sport skills. Unresolved: whether CS2 decision drilling is closer to "lab motor task with distinct action plans" (effect plausible) or "applied sport skill" (effect unreliable).
3. **Guidance hypothesis falsified, yet bandwidth feedback still shows benefits.** McKay et al. (2022) found no reliable reduced-frequency advantage; Wulf's bandwidth studies find automatization benefits. Unresolved: whether bandwidth's benefit comes from frequency, from *which* trials get feedback (error-triggered), from implicit positive reinforcement on below-threshold trials, or from reduced conscious control. This matters directly for how an AI coach should schedule its own feedback.
4. **Quiet eye: cause, correlate, or inhibition artifact?** d = 1.04 expert–novice and d = 0.84 for QE training on performance, versus the finding that the QE→performance effect-size correlation is only r ≈ .45 (p = .12) and that disrupting visual input during the fixation has little effect. Unresolved, and the field lacks a preregistered multi-lab QE-training trial.
5. **3D/VR vs 2D for decision training.** 3D/VR subgroup ES 0.96 vs 0.19 for screen video looks compelling, but the subgroup contrast is *not significant* (p = .449), 3D/VR has I² = 84.7%, and the direct 3D-vs-2D experiment found speed gains only. The fidelity ranking should be treated as a hypothesis.
6. **Video feedback / self-modelling.** Positive PE meta (SMD = 0.47) and positive reviews coexist with 18/24 studies at high risk of bias and adult modelling benefits confined to movement *form* (δ ≈ 0.80) with no outcome effect (δ ≈ −0.02). For FPS, "watch your VOD" is an extrapolation from motor-form modelling to tactical cognition — unvalidated.
7. **Error-management generalization.** d = 0.80 for adaptive transfer is impressive but comes from organizational training tasks; a 2024 reanalysis questions whether the "error encouragement" component (vs active exploration) carries the effect. Whether deliberately error-eliciting practice helps an *already-elite* performer in a *ranked-skill* game (where errors cost Elo) is untested — and the ranked ladder structurally penalizes exploration.
8. **Dunning–Kruger.** Popular usage vs the artifact critique: the pattern is largely a data-structure consequence, and its robust component is small. Yet the *practical* phenomenon (players misjudging their own errors) is real and is better explained by fluency illusions and lack of calibrated feedback than by a DK "unskilled-and-unaware" mechanism.
9. **Habit timescales and measurement.** No meta-analyzable formation time exists (only 4 studies report one); SRHI-based measures of "habit" are partly circular when correlating with behaviour frequency. Any claim about how long a new practice routine takes to become automatic in an esports context is unsupported.
10. **Expertise reversal in ill-structured domains.** The ERE is large overall (reversal d = 0.971) but was established on well-structured tasks; a legal-reasoning study found no reversal. CS2 decision-making is ill-structured — so "give experts less guidance" may be over-applied. The safe rule (remove *redundant* guidance, keep *necessary* guidance) is a design judgment, not a measured quantity.
11. **CLA evidence quality.** Nine included studies, vote counting, serious/some-concerns risk of bias, no retention/transfer data, ~78% soccer, and I² = 99.56% in a related meta-analysis. Any strong CLA claim in a product document would be unsupported; the representativeness heuristic is the defensible extraction.

---

## Top sources

**Deliberate practice**
1. Ericsson, Krampe & Tesch-Römer (1993), *Psychological Review* 100(3):363–406 — https://doi.org/10.1037/0033-295X.100.3.363 (PDF: https://review.firstround.com/content/files/images/blogs/freakonomics/pdf/deliberatepractice-psychologicalreview.pdf)
2. Macnamara, Hambrick & Oswald (2014), *Psychological Science* — https://journals.sagepub.com/doi/full/10.1177/0956797614535810
3. Macnamara, Moreau & Hambrick (2016), *Perspectives on Psychological Science* (sport; 1% among elites) — https://journals.sagepub.com/doi/10.1177/1745691616635591
4. Macnamara & Maitra (2019), *Royal Society Open Science* (preregistered replication) — https://doi.org/10.1098/rsos.190327
5. Ericsson & Harwell (2019), *Frontiers in Psychology* (rebuttal/reanalysis) — https://pmc.ncbi.nlm.nih.gov/articles/PMC6824411/
6. Hambrick et al. (2014), *Intelligence* (chess, 34%) — https://www.sciencedirect.com/science/article/pii/S0160289613000421
7. Martončik et al. (2024), *Collabra: Psychology* (CS:GO/LoL registered report, null) — https://online.ucpress.edu/collabra/article/10/1/117677/200964/Psychological-Predictors-of-Long-term-Esports
8. *PLOS ONE* (2022) distributed practice, 162,417 LoL players — https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0275843

**Motor learning & feedback**
9. Czyż et al. (2024) CI transfer meta-analysis — https://pmc.ncbi.nlm.nih.gov/articles/PMC11349744/
10. Czyż et al. (2024) CI retention meta-analysis — https://pubmed.ncbi.nlm.nih.gov/38987617/
11. Ammar et al. (2024), *Educational Psychology Review* (critical CI review) — https://link.springer.com/article/10.1007/s10648-024-09892-z
12. McKay et al. (2022) reduced-feedback-frequency meta-analysis — https://www.sciencedirect.com/science/article/pii/S1469029222000334
13. Chiviacowsky & Wulf (2007) feedback after good trials — https://www.tandfonline.com/doi/full/10.1080/02701367.2007.10599402
14. Swinnen et al. (1990) instantaneous KR degrades learning — https://www.sciencedirect.com/science/article/abs/pii/016794579090007Z

**Perceptual-cognitive & transfer**
15. Mann et al. (2007), *JSEP* perceptual-cognitive expertise meta-analysis — https://pubmed.ncbi.nlm.nih.gov/17968048/
16. Lebeau et al. (2016), *JSEP* quiet eye meta-analysis — https://pubmed.ncbi.nlm.nih.gov/27633956/
17. 2024 perceptual-cognitive training meta-analysis (team sports) — https://pmc.ncbi.nlm.nih.gov/articles/PMC11505547/
18. 2024 temporal-occlusion video training meta-analysis, *Sports Medicine* — https://pmc.ncbi.nlm.nih.gov/articles/PMC11467115/
19. 2024 "No Supporting Evidence for a Far Transfer…", *Sports Medicine* — https://doi.org/10.1007/s40279-024-02060-x
20. Sala et al. (2019) second-order meta-analysis of cognitive training — https://doi.org/10.1525/collabra.203
21. Hilgard et al. (2019) action-game training publication-bias reanalysis — https://online.ucpress.edu/collabra/article/5/1/30/113031/Overestimation-of-Action-Game-Training-Effects
22. Rogers et al. (2024) KovaaK's reliability — https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2024.1309991/pdf

**Error-based learning, AAR, spacing, habits, CLT, CLA**
23. Keith & Frese (2008), *JAP* error management training meta-analysis — https://pubmed.ncbi.nlm.nih.gov/18211135/
24. Tannenbaum & Cerasoli (2013), *Human Factors* debrief meta-analysis — https://pubmed.ncbi.nlm.nih.gov/23516804/
25. Donovan & Radosevich (1999), *JAP* distribution of practice meta-analysis — https://gwern.net/doc/psychology/spaced-repetition/1999-donovan.pdf
26. Cepeda et al. (2008), *Psychological Science* temporal ridgeline — https://pubmed.ncbi.nlm.nih.gov/19076480/
27. Brunmair & Richter (2019) interleaving meta-analysis, *Psychological Bulletin* — https://pubmed.ncbi.nlm.nih.gov/31556629/
28. Bjork, Dunlosky & Kornell (2013), *Annual Review of Psychology* — https://www.annualreviews.org/content/journals/10.1146/annurev-psych-113011-143823
29. Gignac & Zajenkowski (2020), *Intelligence* (D–K artifact) — https://www.sciencedirect.com/science/article/abs/pii/S0160289620300271
30. Gollwitzer & Sheeran (2006), *Advances in Experimental Social Psychology* — https://doi.org/10.1016/S0065-2601(06)38002-1
31. Lally et al. (2010), *EJSP* habit formation — https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674
32. Singh et al. (2024), *Healthcare* time-to-habit review — https://pmc.ncbi.nlm.nih.gov/articles/PMC11641623/
33. Sniehotta & Presseau (2012), *Annals of Behavioral Medicine* (SRHI critique) — https://academic.oup.com/abm/article-abstract/43/1/139/4563935
34. Tetzlaff et al. (2025) expertise reversal meta-analysis, *Learning and Instruction* — https://www.sciencedirect.com/science/article/pii/S0959475225000660
35. Sundararajan & Adesope (2020), *Educational Psychology Review* seductive details meta-analysis — https://eric.ed.gov/?id=EJ1263249
36. Burkett et al. (2025), *Sports Medicine – Open* linear vs nonlinear pedagogy review — https://link.springer.com/article/10.1186/s40798-025-00893-y

# Coaching feedback: does it change performance, and how is that measured?

**Scope.** This is research for a local-first CS2 demo-analysis / self-coaching system used by one experienced player (~2000 FACEIT Elo, ex-2400). Question: does coaching-type feedback actually change performance, and what does it take to *demonstrate* that for a single person?

**Method.** Primary sources prioritised (journal articles, meta-analyses, PMC/Frontiers, official documentation, military doctrine). Landmark older work cited where it is the canonical source (Kluger & DeNisi 1996, Sweller-era excluded as out-of-scope, Ericsson 1993, Baron & Hershey 1988, Fischhoff-lineage). Critiques, null results and replication failures are included deliberately.

**Category legend**
- **Demonstrated** — replicated across independent studies/meta-analysis with convergent methods.
- **Experimental** — shown in controlled experiments, often single studies or narrow samples.
- **Research-supported** — consistent directional evidence with material methodological caveats.
- **Plausible-untested** — theory/mechanism is coherent, no adequate direct test (esp. for CS2).
- **Infeasible** — cannot be established with the available data or design.

---

## 1. Feedback intervention effects (does feedback help at all?)

**1. Feedback improves performance on average, but a large minority of feedback interventions make performance *worse*.** Kluger & DeNisi (1996) meta-analysed 131 studies, 607 effect sizes, 12,652 participants, 23,663 observations: weighted mean *d* = 0.41; **more than 38% of observed effect sizes were negative** (abstract: "over one-third of the FIs decreased performance"). Excluding the Mikulincer cluster, 33% of remaining effects were still negative. This is the single most important result for anyone building a feedback product.
Evidence: *Psychological Bulletin* 119(2):254–284, 1996. **Demonstrated.**
https://doi.org/10.1037/0033-2909.119.2.254 (text: https://mrbartonmaths.com/resourcesnew/8.%20Research/Marking%20and%20Feedback/The%20effects%20of%20feedback%20interventions.pdf)

**2. The popular "feedback has *d* = 0.79" figure is a meta-synthesis artefact, not a primary meta-analytic estimate.** Hattie & Timperley (2007) combined 12 existing meta-analyses (196 studies, 6,972 effect sizes) and reported ≈0.79 – approximately "twice the average effect of schooling" (*d* = 0.40). The *d* = 0.40 benchmark is itself constructed from a different aggregation, and the same primary studies can appear in several of the 12 source meta-analyses (unit-of-analysis/double-counting), with fixed-effect aggregation of a heterogenous pool.
Evidence: *Review of Educational Research* 77(1):81–112, 2007. **Experimental (methodologically contested).**
https://doi.org/10.3102/003465430298487

**3. Re-analysing the *primary* studies behind that figure drops the effect to *d* ≈ 0.48, with 17% negative effects.** Wisniewski, Zierer & Hattie (2020) rebuilt the dataset from unique primary studies (435 studies, k = 994, N > 61,000), deduplicated overlapping samples, applied random-effects with robust variance estimation: *d* = 0.55 raw → **0.48 after removing outliers**, I² = 86.5% → 83.4%, **17% of effects negative**. Published papers had larger effects (*d* = 0.49) than dissertations (*d* = 0.36), and the funnel plot was asymmetric → the published average likely still overstates the typical effect.
Evidence: *Frontiers in Psychology* 10:3087, 22 Jan 2020, PMID 32038429. **Demonstrated.**
https://doi.org/10.3389/fpsyg.2019.03087 · https://pmc.ncbi.nlm.nih.gov/articles/PMC6987456/

**4. What the feedback *contains* predicts benefit far more than whether it is positive or negative.** Kluger & DeNisi found feedback *sign* did **not** reliably separate positive from negative effects. Wisniewski et al. coded informational content: reinforcement/punishment *d* = 0.24; corrective feedback *d* = 0.46; **high-information feedback (what was wrong, why, and what to do next) *d* = 0.99**. Negative-motivation effects clustered on uninformative rewards/punishments (21% of motivational effect sizes negative; mean motivational effect *d* = 0.33).
Evidence: Kluger & DeNisi 1996; Wisniewski et al. 2020 (PMC6987456). **Demonstrated.**
https://doi.org/10.3389/fpsyg.2019.03087

**5. Feedback that directs attention to the *self* (praise, ability attributions, evaluation concerns) is the least effective level.** Hattie & Timperley's four-level taxonomy — task → process → self-regulation → **self (praise)** — with self-level feedback identified as the least effective and most received/least useful in classrooms. In Hattie's synthesis, praise sits at *d* = 0.14 while video/audio feedback sits at *d* = 0.64. Kluger & DeNisi's Feedback Intervention Theory explains the mechanism: feedback shifts the locus of attention along a hierarchy (task-learning → task-motivation → meta-task/self); attention to the self consumes resources and triggers ego-protective processing.
Evidence: Hattie & Timperley 2007; Kluger & DeNisi 1996 (FIT). **Research-supported** (FIT mechanism is theory-driven; level effects are meta-analytic). 
https://doi.org/10.3102/003465430298487

**6. Modern replications keep landing on a moderate, highly heterogeneous effect — the "one feedback effect" does not exist.** Brummer et al. (2024), 116 studies of digitally delivered instructional feedback: *g* = 0.41, I² ≈ 61%; **process-focused feedback outperformed purely task-focused feedback** (task feedback can be too situation-specific to transfer). Anseel & Sherf's 25-year review (2025) concludes the field does not support a single universal feedback effect: content, interpretation, social context, timing and consequences all moderate it.
Evidence: *Learning Environments Research*, 2024; *Annual Review of Organizational Psychology and Organizational Behavior*, 2025. **Demonstrated.**
https://doi.org/10.1007/s10984-024-09501-4 · https://doi.org/10.1146/annurev-orgpsych-110622-031927

**7. Positive feedback can help short-term; negative feedback alone often does nothing.** Aarvik et al. (2024) on professional-performance data: positive feedback improved subsequent performance (short-term, repeatable, strongest for highly relevant tasks); **negative feedback showed no overall performance effect**. A 2025 six-year multilevel field experiment with 331 managers found developmental feedback ineffective short-term but positive long-term, with larger gains for lower performers and strong effects of *feedback source*.
Evidence: *Journal of Sports Economics*/SEREV 2024; *Journal of Organizational Excellence* 2025. **Experimental.**
https://doi.org/10.1016/j.serev.2024.100045 · https://doi.org/10.1002/joe.22299

**8. More feedback is not better; the "reduced feedback frequency improves learning" (reversal/guidance) effect is largely an artefact of specific lab designs.** Marschall, Wiemeyer & Bund's meta-analysis of 40 studies: the global reversal effect is small (acquisition Δ = −0.21, late retention Δ = +0.22) and unstable (fail-safe N of 2–3 zero-effect studies erases it). It appeared in only 7 of 20 moderator factor levels, essentially only in simple **laboratory** tasks with >90 acquisition trials; **no systematic frequency effect was found for sport tasks**. Sampling bias was demonstrated: among non-includable studies, 39/43 did *not* confirm the reversal effect vs 14/25 among included studies.
Evidence: meta-analysis (published version: Marschall, Bund & Wiemeyer, *Psychology of Sport and Exercise* 2022). **Experimental (with a strong negative result against the guidance hypothesis).**
https://uol.de/f/4/inst/sport/download/andreasbund/publikationen/Publikation_44.pdf

---

## 2. Video-based feedback / self-observation

**9. Video self-modelling produces moderate-to-large performance gains — but they decay within a week.** Wang et al. (2026) meta-analysed 10 RCTs (26 effect sizes, N = 244): athletic performance **SMD = 0.81 (95% CI 0.28–1.33)**, I² = 73%; self-efficacy SMD = 0.62 (95% CI 0.14–1.08). At **1-week follow-up the performance effect was non-significant (SMD = 0.59, p = 0.09)** and not robust to outlier removal. Effects were **dose-dependent** (total minutes and session count were significant moderators); age, experience, skill class and control type were not.
Evidence: *Frontiers in Sports and Active Living* 8:1809566, 19 Aug 2026, PMID 42688263. **Experimental.**
https://doi.org/10.3389/fspor.2026.1809566 · https://pmc.ncbi.nlm.nih.gov/articles/PMC13533993/

**10. Letting the learner control *when* they get feedback improves retention and transfer, not in-session performance.** Wang et al. (2025), 29 RCTs, 1,147 participants: self-controlled vs passively-received feedback — acquisition SMD = 0.199 (ns), **retention SMD = 0.630**, **transfer SMD = 0.684**; vs yoked (schedule-matched) controls — acquisition 0.175 (ns), retention 0.695, transfer 0.648. Significant publication bias was detected in the retention and transfer analyses (Egger p < 0.01), so magnitudes are optimistic. Practical reading: video review's value shows up *after* the session, on later games — not in the review session itself.
Evidence: *Behavioral Sciences* 15(9):1291, 22 Sep 2025, PMID 41009321. **Experimental.**
https://doi.org/10.3390/bs15091291

**11. Video-based coaching beats standard teaching in surgical training, but the effect concentrates in the weakest performers.** Daniel et al. (2023), 11 RCTs, 298 surgical residents: pre-post change **SMD 1.62 (0.62–2.63, I² = 85%)**; post-intervention skill score difference only **SMD 0.53 (0.00–1.01, p = 0.05)**. Interpretation offered by the authors: benefit is largest for low-baseline learners/early training.
Evidence: *Surgical Endoscopy* 2023, PMID 35739431. **Experimental.**
https://pmc.ncbi.nlm.nih.gov/articles/PMC9225812/ · https://pubmed.ncbi.nlm.nih.gov/35739431/

**12. Augmented (including visual) feedback in sport: favourable direction, weak evidence base.** A 2022 systematic review of gross-motor and sport-specific skills found 24 randomised studies (895 participants); most reported improvement, but **18 of 24 were judged high risk of bias**. General video/visual feedback added to verbal feedback gives a small pooled effect (≈ES 0.21); the larger effects come from *edited* self-modelling (≈0.81), not from raw replay.
Evidence: *Psychology of Sport and Exercise* 2022 (review); see also #9. **Research-supported (low confidence in the point estimate).**
https://www.sciencedirect.com/science/article/pii/S1469029222001455

**13. Self-observation without a "reference of correctness" is the documented failure mode — the athlete sees the movement but cannot tell what was wrong.** Comparative motor-learning work shows self-observation supplies information about what happened but not whether it was correct; expert modelling supplies a correctness model but not the athlete's own execution. Combining the two produced better short-term learning than either alone. Self-observation may be neutral or actively harmful when the learner confidently adopts a wrong interpretation, or when visually salient but functionally irrelevant details capture attention.
Evidence: *Frontiers in ICT* 6:16, 2019; motor-learning reviews; combined self + model observation studies (PMC5599820). **Research-supported (mechanism well established in motor learning; effect sizes for "harm" are not).**
https://www.frontiersin.org/journals/ict/articles/10.3389/fict.2019.00016/full

**14. Improved performance *during* feedback ≠ learning.** Removing visual error feedback in motor adaptation causes errors to return, i.e. the feedback supported online correction rather than a durable change in the motor representation. This is the classic performance/learning distinction (Salmoni, Schmidt & Walter 1984 lineage) and is the strongest argument against judging a review session by how good the player looks *during* the review.
Evidence: motor-adaptation literature; see #8 and #10 for the retention/transfer design logic. **Research-supported.**
https://doi.org/10.1016/j.cub.2016.09.024 (related adaptation work) · https://uol.de/f/4/inst/sport/download/andreasbund/publikationen/Publikation_44.pdf

**15. One direct esports demonstration exists: video feedback + positive/corrective coaching improved a specific in-game behaviour and generalised to ranked play.** White, Miltenberger & Concepcion (2024) used a nonconcurrent multiple-baseline single-case design with three *Street Fighter V* players: all three improved the targeted anti-air behaviour and the improvement **generalised to ranked online matches**. Non-randomised, n = 3 — but this is the closest existing template to "one player, video review, measured change".
Evidence: *Behavioral Interventions* 2024. **Experimental.**
https://doi.org/10.1002/bin.2056

---

## 3. Debriefing / after-action review methodology

**16. Debriefs do improve performance on average, with a medium effect.** Tannenbaum & Cerasoli (2013), 46 samples, 2,136 participants: **d = 0.67** (≈20–25% improvement), broadly similar for individual vs team debriefs and for simulated vs real-world settings. Effect depended on how well the debrief was conducted (facilitation, alignment of participants, purpose, and performance measure).
Evidence: *Human Factors* 55(1):231–245, 2013, PMID 23516804. **Demonstrated.**
https://doi.org/10.1177/0018720812448394

**17. Structured debriefing beats no debriefing, but no named framework is proven superior to another.** Systematic reviews in healthcare simulation find debriefing improves knowledge, technical and non-technical performance, teamwork and situational awareness — but the field still lacks high-quality, multicentre head-to-head comparisons of named models, and many studies evaluate the whole simulation rather than isolating the debrief.
Evidence: *Effectiveness of debriefing in simulation-based learning* systematic review, PMID 27820479; 2024 review PMID 38240623. **Research-supported.**
https://pubmed.ncbi.nlm.nih.gov/27820479/ · https://pubmed.ncbi.nlm.nih.gov/38240623/

**18. PEARLS integrates self-assessment, advocacy-inquiry and directive teaching; its evidence is conceptual plus extensive practice, not superiority trials.** PEARLS was designed to blend learner self-assessment with facilitator-led analysis and targeted teaching, varying style by learner and objective.
Evidence: *Simulation in Healthcare* 10(2):106–115, 2015. **Research-supported (framework, not an effect size).**
https://doi.org/10.1097/SIH.0000000000000072

**19. In healthcare, highly structured and less structured AARs performed comparably — structure is not the active ingredient.** A meta-analysis of after-action review/debriefing found overall benefit; unlike military settings, in healthcare the degree of structure did not clearly change outcomes. TALK (Target–Analysis–Learning–Key actions) is a short clinical-event variant intended to be led by any team member; its evidence base is implementation/feasibility-oriented, with low-level outcome evidence.
Evidence: *Human Factors* 2013 AAR meta-analysis, PMID 24096913; TALK, *BMJ* 2021;374:n2042; clinical debriefing tools systematic review, *BMJ Quality & Safety* 2024;33:187–197. **Research-supported.**
https://pubmed.ncbi.nlm.nih.gov/24096913/ · https://www.bmj.com/content/374/bmj.n2042 · https://qualitysafety.bmj.com/content/33/3/187

**20. Plus–delta is a fast format, not a debriefing theory.** The AMEE Guide 82 (best-evidence practical guide) treats "what went well / what should change" as useful under time pressure but insufficient alone: it identifies *what* to change without exploring intent, cognition, systems factors or causal mechanism.
Evidence: *Medical Teacher* 35(8):e1511-30, 2013 (AMEE Guide No. 82). **Research-supported.**
https://doi.org/10.3109/0142159X.2013.818632

**21. The military AAR is a doctrine-level, not evidence-level, standard.** US Army AAR doctrine defines a professional discussion of an event focused on performance standards (what was intended, what happened, why, what to improve) and is the origin of most corporate "AAR" practice. Formal experimental evaluations of AAR's incremental effect in Army combat training exist (DTIC; thesis-level work) but the doctrine is institutionalised on professional-judgment grounds rather than on trial evidence.
Evidence: US Army AAR doctrine (Virginia Defense Force reprint); DTIC ADA474305 "After Action Review in Simulation-Based Training". **Plausible-untested at the effect-size level.**
https://vdf.virginia.gov/pdf/FORMS/After%20Action%20Review.pdf · https://apps.dtic.mil/sti/pdfs/ADA474305.pdf

---

## 4. Expertise in self-assessment

**22. Physicians' self-assessment correlates poorly with observed competence — 13 of 20 comparisons showed little, none, or an inverse relationship.** Davis et al. (2006) screened 725 articles, included 17 studies (20 comparisons). Self-assessment was least accurate among the *least* skilled; some of the most confident physicians were badly calibrated. Authors' conclusion: lifelong-learning systems should weight **external assessment** over self-perception.
Evidence: *JAMA* 296(9):1094–1102, 6 Sep 2006, PMID 16954489. **Demonstrated.**
https://doi.org/10.1001/jama.296.9.1094

**23. The productive reformulation is not "make people better at self-rating" but "make them seek external assessment."** Eva & Regehr (2005) argue the relevant professional capacity is **self-directed assessment seeking** — recognising a need, obtaining external data (supervisor observation, scores, audits, outcomes), and acting on it — rather than introspective global self-judgment. This is the direct design justification for giving the player an objective record generated from demos instead of asking him to "think about his mistakes".
Evidence: *Journal of Continuing Education in the Health Professions* 25(Suppl 1):S11–S21, 2005 (with Regehr, *JCEHP* 2008). **Research-supported.**
https://doi.org/10.1097/00001888-200510001-00015

**24. Across domains, self-assessment explains only ~8% of the variance in actual performance (*r* ≈ .29).** Zell & Krizan's (2014) metasynthesis of 22 meta-analyses (academic, intelligence, language, medicine, sport, vocational) found moderate relative accuracy that improves when judgments are domain-specific, objective and familiar — but still far too weak to use as an individual-level measure.
Evidence: *Perspectives on Psychological Science* 9(2):111–125, 2014. **Demonstrated.**
https://doi.org/10.1177/1745691613518075

**25. Athletes systematically overestimate themselves against coach ratings, and the strongest overestimators develop worse.** Hofseth et al. (2017), 267 youth-elite footballers (~17.6 y): players on average rated their skills above their coaches' ratings; the "strong overestimator" group had odds ratio **0.71** for later high performance vs the underestimating group, controlling for age and prior/current performance (association, not causation).
Evidence: *Sport, Exercise, and Performance Psychology* 6:370–383, 2017. **Experimental.**
https://doi.org/10.1037/spy0000094

**26. The famous "unskilled-and-unaware" pattern is real but its canonical magnitude is substantially a statistical artefact.** Kruger & Dunning (1999) reported bottom-quartile performers at ~12th percentile estimating ~62nd. Gignac & Zajenkowski (2020) showed that better-than-average bias plus regression to the mean, combined with quartile binning and difference-score dependence, reproduces the graph; in 929 participants they found no heteroscedasticity (*r* ≈ −.05) and an essentially linear objective–self relationship. Dunkel et al. (2023) found a statistically significant but **minimal** residual effect in a nationally representative sample. Do not build a coaching system on "low-skill players can't see their own errors" as a large, established quantity.
Evidence: *JPSP* 77(6):1121–1134, 1999; *Intelligence* 80:101449, 2020; *Intelligence* 2023 replies/rejoinders. **Contested.**
https://doi.org/10.1016/j.intell.2020.101449 · https://gwern.net/doc/psychology/1999-kruger.pdf

**27. Coach ratings are not ground truth either.** Coaches' estimates of athletes' exertion diverge from the athletes' own by sport (soccer coaches underestimated; lacrosse coaches overestimated) and diverge most on high-exertion days. And athletes construct self/other assessments from salient extremes: collegiate baseball players over-weighted their best-ever performance relative to its informativeness. **Both sides of the coach–player comparison are noisy; only instrumented data breaks the tie.**
Evidence: *J Strength Cond Res* 2023 (PMID 36820706); *J Applied Social Psychology* 2015 (Guenther et al.). **Experimental.**
https://pubmed.ncbi.nlm.nih.gov/36820706/

**28. Self-assessment accuracy is *domain- and specificity-dependent*, which is the one usable nuance.** Zell & Krizan's moderators: accuracy rises when the judged task is concrete, objective, familiar, and narrowly scoped. "How did I play this round?" is unfalsifiable; "How many of my 6 early-round buys did I convert into a kill or a bomb-site plant?" is checkable. Design the prompt around the checkable version.
Evidence: Zell & Krizan 2014 (see #24). **Research-supported.**
https://doi.org/10.1177/1745691613518075

---

## 5. Debiasing hindsight and outcome bias

**29. Hindsight bias is real but small on average — *r* ≈ .17 across 122 studies.** Christensen-Szalanski & Willham (1991): weighted *r* = .17 (95% CI .14–.20), ≈ *d* 0.35; reliability-corrected *r* = .25 (≈ *d* 0.52). Larger for unfamiliar tasks and certain outcome-information formats; the authors estimated ~0–7–27% of participants might change a decision because of hindsight information. The asymmetry favoured a *cognitive reconstruction* explanation over a motivational one.
Evidence: *OBHDP* 48(1):147–168, 1991. **Demonstrated.**
https://doi.org/10.1016/0749-5978(91)90010-Q

**30. Debiasing hindsight by instruction mostly fails.** Guilbault et al. (2004) meta-analysed 95 studies (*d* ≈ .39 overall hindsight effect) and found that **interventions intended to reduce hindsight bias did not significantly lower it overall**. This is the load-bearing negative result: telling a reviewer "don't be outcome-biased" does not work.
Evidence: *Basic and Applied Social Psychology* 26(2–3):103–111, 2004. **Demonstrated (negative).**
https://doi.org/10.1080/01973533.2004.9646399

**31. What *does* work is task-specific prompting at the point of judgment, and preserving the pre-outcome judgment.** A 2024 forensic-risk study reduced induced hindsight bias in novices with a prompt stating explicitly that the later outcome was unavailable at the decision point (experts showed no induced bias). Salmen, Ermark & Fiedler (2023) found participants could lower post-outcome probability judgments when instructed to reason from the earlier perspective, and the last communicated judgment still influenced judgments two weeks later. Generic "be aware of bias" training remained weak.
Evidence: *Journal of Forensic Psychology Research and Practice* 2024, doi:10.1080/24732850.2024.2396991; Salmen et al. 2023, PMID 35953669. **Experimental.**
https://doi.org/10.1080/24732850.2024.2396991 · https://pubmed.ncbi.nlm.nih.gov/35953669/

**32. Recording the judgment *before* the outcome is the strongest prevention — it is a design fix, not a debiasing trick.** If the pre-round expectation (e.g. "I predict they go B-site with an eco, because the economy supports it") is captured before the round resolves, hindsight reconstruction cannot overwrite it. This is why an up-front criteria / prediction layer belongs in the tool, not in the player's head.
Evidence: synthesis of #29–#31; the principle is standard in decision-audit practice. **Research-supported (mechanism strong; no direct n=1 trial).**
https://pubmed.ncbi.nlm.nih.gov/35953669/

**33. Outcome bias: people rate the same decision as better when the result happened to be good, even when the probabilities are fully known.** Baron & Hershey (1988) held the decision information constant and varied only the outcome; participants rated reasoning as better, the decision maker as more competent, and were more willing to let them decide again after favourable outcomes — and evaluated a choice more favourably when the *unchosen* option later turned out badly.
Evidence: *JPSP* 54(4):569–579, 1988, PMID 3367280. **Demonstrated.**
https://doi.org/10.1037/0022-3514.54.4.569

**34. The corrective norm is explicit: judge the process prospectively, the outcome retrospectively.** Baron & Hershey's procedure — ignore the actual outcome, reconstruct the information available at the time, enumerate alternatives, estimate risks, then ask whether the choice was reasonable given that information — is directly implementable as a review protocol (score the decision from the demo information state; score the result separately).
Evidence: Baron & Hershey 1988. **Research-supported.**
https://bear.warrington.ufl.edu/brenner/mar7588/Papers/baron-hershey-jpsp1988.pdf

**35. Prospective hindsight ("pre-mortem") increases the number of failure causes generated — mechanism only, not a proven accuracy improvement.** Mitchell, Russo & Pennington (1989) found that imagining an event as already having occurred produced longer, more episodic explanations; Klein (2007) popularised this as the project pre-mortem, citing ≈30% more reasons identified. Caution: the original study measured explanation quantity/type, not forecast accuracy. For CS2 the analogue is "the round is already lost — why?" applied to setup decisions before they are made.
Evidence: *Journal of Behavioral Decision Making* 2(1):25–38, 1989; *Harvard Business Review*, Sep 2007. **Plausible-untested (mechanism experimental; downstream benefit unproven).**
https://doi.org/10.1002/bdm.3960020103

---

## 6. Process vs outcome metrics

**36. Evaluating decisions independently of results is an established, fielded method — not a theoretical aspiration.** Romer (2006) estimated the expected value of every fourth-down option using dynamic programming over 700+ NFL games and graded decisions by whether the team chose the higher-EV action, finding systematic over-conservatism (e.g. 512 fourth downs in own half where the model favoured going for it; teams went for it 7 times). Estimated aggregate gain from optimal play: ~0.35 points per decision, ~2.1 percentage points of win probability per game.
Evidence: *Journal of Political Economy* 114(2):340–365, April 2006. **Demonstrated.**
https://doi.org/10.1086/501171

**37. Poker research gives the cleanest formal statement of "good process, bad result" and shows how long a persistent skill edge takes to separate from noise.** Potter van Loon, van den Assem & van Dolder (2015) analysed 456 million player-hands: performance persisted across six-month periods but individual rank correlations were only ~0.074–0.104; top vs bottom decile differed by ~+5.1 vs −5.9 bb/100; simulation indicated skill "predominated" after ~1,500 hands *in that population*. Levitt & Miles (2011) identified skilled WSOP entrants ex ante (ROI >30% vs ≈−15% for others). A 2023 study of 91,439 players (>85M hands) estimated measurable skill explained ~17.2% of hand-level outcome variance. **Skill changes the distribution of outcomes; it does not eliminate bad results.**
Evidence: *PLOS ONE* 10(2):e0115479, 2015; NBER WP 17023, 2011; 2023 online-poker study. **Demonstrated.**
https://doi.org/10.1371/journal.pone.0115479 · https://www.nber.org/papers/w17023

**38. Decision-quality metrics that compare the chosen action against alternatives are the direct analogue for CS2 round decisions.** Billings & Kan's DIVAT framework scores poker decisions by the expected-value difference between the action taken and alternatives, giving a lower-variance estimate of decision quality than winnings. The transferable recipe: (1) what information was available ex ante; (2) what actions were available; (3) expected value of each; (4) EV lost relative to best; (5) counterfactual/alternative runouts.
Evidence: *ICGA Journal* 29(3), 2006. **Research-supported.**
https://doi.org/10.3233/ICG-2006-29302

**39. Expected-value style metrics (xG family) are useful but demonstrably biased in ways that matter for individual evaluation.** A 2024 analysis shows xG models contain systematic biases that confound finishing ability — a metric built to be outcome-independent can still smuggle outcome information or shooter-independent assumptions into individual ratings. Treat any CS2 "expected kill / expected survival" metric as a model with a stated bias budget, not as truth.
Evidence: arXiv:2401.09940, Jan 2024 (see also xG model validation literature, e.g. *PLOS ONE* 2024 improved xG models). **Experimental.**
https://arxiv.org/pdf/2401.09940

**40. Documented failure mode of outcome-based evaluation: it is systematically miscalibrated, not merely noisy.** Romer's finding is that expert practitioners (NFL coaches) chose the lower-EV option in a stable, predictable direction over hundreds of comparable decisions, and the "error" was not random — it was explained by a different implicit objective (avoiding visible failure, job security) plus imperfect optimisation. Outcome-based evaluation reinforces exactly that distortion.
Evidence: Romer 2006 (see #36). **Demonstrated.**
https://media.clemson.edu/economics/gated/data/cfb-plays/Romer-JPE.pdf

**41. Practical rule that follows from §6:** never attribute a single round's loss to a decision, and never let a won round validate a bad decision. Aggregate decisions into cohorts (same situation class, same economy state), score the process, and only then look at outcomes as a *distribution*. With CS2 sample sizes per situation class this means months, not sessions — see §7.
Evidence: synthesis of #36–#40. **Research-supported.**
https://doi.org/10.1371/journal.pone.0115479

---

## 7. Behaviour-change measurement for n = 1

**42. Specific, difficult goals beat vague ones — with a linearly increasing difficulty–performance relationship.** Locke & Latham's 35-year review: difficult vs easy goals *d* = .52–.82; specific-and-difficult vs "do your best" *d* = .42–.80; mechanisms are direction, effort, persistence and strategy development. Critically for complex/unfamiliar tasks, a **learning goal** can outperform a performance goal. Feedback is treated as a *necessary adjunct* — goals without progress information do not work.
Evidence: *American Psychologist* 57(9):705–717, 2002. **Demonstrated.**
https://doi.org/10.1037/0003-066X.57.9.705

**43. In sport specifically, goal setting works but modestly, and *process* goals dominate outcome goals.** Kyllo & Landers (1995), 36 experimental studies: overall *g* = 0.34; moderators — moderately difficult goals 0.53, absolute/specific goals 0.93, "do your best" 0.38, very difficult −0.01, public goals 0.79. A 2022 update (27 studies) found overall *d* = 0.47 (95% CI 0.30–0.63; I² ≈ 76.6%) with prediction interval −0.26 to 1.19, and moderator effects of **process goals *d* = 1.36 vs performance goals 0.44 vs outcome goals 0.09**.
Evidence: *JSEP* 17(2):117–137, 1995; *International Review of Sport and Exercise Psychology* 2022. **Demonstrated + Experimental.**
https://doi.org/10.1123/jsep.17.2.117 · https://doi.org/10.1080/1750984X.2022.2116723

**44. If–then planning adds a medium-to-large increment on top of goals.** Gollwitzer & Sheeran (2006): 94 independent tests, 8,461 participants, implementation intentions raised goal attainment by **d = 0.65 (95% CI ≈ 0.60–0.70)**.
Evidence: *Advances in Experimental Social Psychology* 38:69–119, 2006. **Demonstrated.**
https://doi.org/10.1016/S0065-2601(06)38002-1

**45. Measuring progress *is* the intervention, and it has an effect size.** Harkin et al. (2016) meta-analysed 138 studies, 19,951 participants: monitoring goal progress raised goal attainment by **d⁺ = 0.40 (95% CI 0.32–0.48)**; effects were larger with more frequent monitoring, public monitoring, and physical recording. This is the strongest single argument that the tool's measurement layer is not overhead — it is part of the treatment.
Evidence: *Psychological Bulletin* 142(2):198–232, 2016, PMID 26479070. **Demonstrated.**
https://doi.org/10.1037/bul0000025

**46. Habit formation is slower and more variable than the folklore.** Lally et al. (2010): among 39 participants with good asymptotic fits, **median 66 days to reach 95% of modelled automaticity, range 18–254 days**; missing one opportunity did not materially disrupt the process. Any "21-day habit" or "one week fixes it" claim is unsupported.
Evidence: *European Journal of Social Psychology* 40(6):998–1009, 2010. **Experimental.**
https://doi.org/10.1002/ejsp.674

**47. Single-case experimental design (SCED) is the correct statistical apparatus for one player — and it is a real design, not a case report.** Required features: repeated measurement; stable baseline; planned, systematic introduction/manipulation of the intervention; phase comparison; replication of the effect. Design families: A-B (weakest; confounded with development/practice/regression), **A-B-A-B / withdrawal** (strongest causal inference where withdrawal is ethical), **multiple baseline** across behaviours/settings/contexts (best practical option when withdrawal is undesirable), alternating treatments (compare two interventions), changing criterion (gradual targets).
Evidence: Barker, McCarthy, Jones & Moran, *Single-Case Research Methods in Sport and Exercise Psychology* (Routledge, 2011); Barker et al. 2013 review. **Research-supported.**
https://eprints.staffs.ac.uk/2218/1/Barker%20et%20al.%202013%20SCD%20Review.pdf

**48. Randomisation plus a randomisation test gives n = 1 designs genuine inferential statistics.** Randomise the order of conditions (e.g. which of two review protocols is used in a given week, or the start point of an intervention across behaviour targets), prespecify the statistic, then compute the exact p-value as the proportion of allowable assignments producing an effect at least as large as observed. Validity depends on the randomisation being specified and implemented *before* data collection — it is not a post-hoc reshuffle.
Evidence: single-case randomisation-test methodology (Onghena & Edgington lineage); SCED standards literature. **Demonstrated (method).**
https://pmc.ncbi.nlm.nih.gov/articles/PMC3652808/

**49. Tau-U is the standard non-overlap effect size for single-case data — and it is a supplement, not a substitute for visual analysis.** Parker, Vannest, Davis & Sauber (2011) combine between-phase nonoverlap with within-intervention trend (and optionally control baseline trend); range −1 to +1. Cautions: baseline-trend correction applied mechanically can inflate effects; it is sensitive to number/pattern of observations; it cannot rescue a weak design. Report the exact variant, direction, and rationale.
Evidence: *Behavior Therapy* 42(2):284–299, 2011, PMID 21496513. **Demonstrated (method, with documented limits).**
https://doi.org/10.1016/j.beth.2010.08.006

**50. Visual analysis remains the primary arbiter in SCED, and the formal standards now require adequate baselines.** Visual analysis criteria: level, trend, variability, immediacy, overlap, consistency, replication. US What Works Clearinghouse (Handbook v5.0) requires **at least six data points in the initial baseline phase** for designs to earn the strongest rating (with limited exceptions for zero within-phase variance). WWC does not require Tau-U or a randomisation p-value; design quality, replication, reliability, fidelity and visual analysis come first.
Evidence: WWC Handbook v5.0 / SCD technical documentation, IES. **Demonstrated (standard).**
https://ies.ed.gov/ncee/wwc/Handbooks

**51. Reporting guidelines exist for exactly this kind of study.** CENT 2015 extends CONSORT to N-of-1 trials (25 items, 44 sub-items; treatment sequence, periods, randomisation, blinding, washout, per-period outcomes). SCRIBE 2016 covers the broader single-case family in behavioural sciences (26-item checklist; withdrawal, multiple-baseline, alternating-treatments, changing-criterion). Neither is a risk-of-bias tool.
Evidence: *BMJ* 2015;350:h1738 (CENT); *J Clin Epidemiol* 2016;73:142–152 (SCRIBE). **Demonstrated (standard).**
https://doi.org/10.1136/bmj.h1738 · https://pmc.ncbi.nlm.nih.gov/articles/PMC5214372/

**52. Published single-case effects in sport psychology are systematically inflated — expect your own n = 1 result to be optimistic.** Barker et al. (2020) meta-regressed 121 papers (71 usable): mean effects ≈ Δ = 2.40 weighted / 2.83 unweighted. These were associated with positive publication bias, **short baseline phases**, failure to use multiple-baseline designs, and failure to establish procedural reliability. Practical consequence: if a review protocol shows a huge effect, the first hypothesis is design weakness, not a breakthrough.
Evidence: *Psychology of Sport and Exercise* 51:101746, 2020. **Demonstrated (negative, about the literature).**
https://researchonline.gcu.ac.uk/en/publications/the-effectiveness-of-psychological-skills-training-and-behavioral/

---

## 8. Esports-specific evidence (including null results)

**53. Practice *quantity* explains almost none of esports performance at the professional level.** Pluss et al. (2021), eight-week pre-competition study: quantity of practice explained only a very small fraction of in-game performance. Pluss et al. (2022), 52-week longitudinal study of professional and semi-professional players: same weak correlation; players can accumulate 16,000+ hours over 10 years, professionals train more, yet volume does not predict expertise. Abbott et al. (2022) found LoL players **perceive their own training as ineffective** and believe the "grind" approach is not the best route to expertise.
Evidence: *JSES* 2021; *Computers in Human Behavior* 137:107421, 2022; *JEGE* 2022, doi:10.1123/jege.2022-0011. **Demonstrated (null/weak).**
https://jses.net/wp-content/uploads/2021/02/Pluss-et-al.-2021.pdf · https://doi.org/10.1016/j.chb.2022.107421

**54. Distributed practice beats massed practice in a real MOBA, but the effect is small and observational.** Vardal et al. (2022) analysed 162,417 *League of Legends* players' first 100 ranked matches: the most distributed group (95 matches over 136–150 days) vs the most massed (1–15 days) — GPM 399.71 vs 392.81 (*d* = 0.146), KDA 3.76 vs 3.27 (*d* = 0.265), both p < .001 after matching on early performance. The *timing* of the breaks mattered negligibly. Limits: observational, cannot rule out motivation/intensity confounds, ~2/3 of raw data dropped in preprocessing.
Evidence: *PLOS ONE* 17(10):e0275843, 14 Oct 2022. **Experimental (large-n observational).**
https://doi.org/10.1371/journal.pone.0275843

**55. The best available direct esports coaching/feedback evidence is a single-case video-feedback study.** White et al. (2024, #15) is the strongest match to "does targeted video feedback change a specific CS-like behaviour in one player" — but n = 3, non-randomised, single game (Street Fighter V), and one behaviour.
Evidence: *Behavioral Interventions* 2024, doi:10.1002/bin.2056. **Experimental.**
https://doi.org/10.1002/bin.2056

**56. Randomised esports interventions usually improve a proxy, not the game skill.** Kim & Chang (2022) randomly assigned LoL players (5 per group) to a nine-session psychological-skills and counselling programme: significant group × time effects on psychological skills, coping and communication — **not** on objective in-game skill. Wachholz et al. (2025 RCT, 8-week physical training, ~3 sessions/week): physical measures improved, **no significant between-group improvement in Aimlabs performance, reaction time or anticipation** — a clean demonstration that improving a component does not transfer to game skill.
Evidence: *JSEP* 2022, doi:10.1123/jsep.2022-0071; *Frontiers in Sports and Active Living* 2025, doi:10.3389/fspor.2024.1504205. **Experimental (incl. null transfer).**
https://doi.org/10.1123/jsep.2022-0071 · https://doi.org/10.3389/fspor.2024.1504205

**57. Structured deliberate-practice-style feedback helps initially *low* performers most, in an experimental action game.** Clark et al. (2022) gave 90-minute video demonstrations plus continuous auditory feedback on *Space Fortress*; after 4 hours of subsequent gameplay, initially low-performing participants outperformed undirected-practice controls and the improvement persisted after feedback removal.
Evidence: *Acta Psychologica* 228:103656, 2022, PMID 35763961. **Experimental.**
https://doi.org/10.1016/j.actpsy.2022.103656

**58. Aim trainers: reliable *measures*, unproven *interventions*.** KovaaK's reliability pilot (10 FPS players) found excellent test–retest ICC ≈ 0.947–0.995 but explicitly warns against extrapolating to live matches (movement, positioning, target uncertainty, stress, decision-making, teammates, opponents). A small 2021 IEEE study of six VALORANT players found 5/6 improved in-game shooting accuracy after Aim Lab training — underpowered. Large observational Aim Lab data show within-trainer improvement (task learning), not far transfer.
Evidence: KovaaK's pilot, *Frontiers in Sports and Active Living* 2024 (PMC10925653); IEEE 2021. **Plausible-untested (transfer), Experimental (measurement reliability).**
https://pmc.ncbi.nlm.nih.gov/articles/PMC10925653/

**59. The action-video-game-training literature is the cautionary tale for any "training improves skill" claim.** Bediou et al. (2018) reported cross-sectional *g* = 0.55 and intervention *g* = 0.34; the 2023 update: cross-sectional *g* = 0.64, **intervention *g* = 0.30 (95% CI 0.11–0.50)**, with publication bias detected in the cross-sectional set. Hilgard et al. (2019) re-analysed the same studies with bias adjustments: unadjusted *g* = 0.34 versus PET *g* = −1.69, PEESE *g* = −0.53, *p*-uniform *g* = 0.11 (ns), selection model *g* = 0.16 (ns); a Bavelier-lab effect (*g* = 0.92 vs 0.22 elsewhere) was largely explained by publication bias plus **salami slicing** (same participants' outcomes spread across papers without disclosure). Bediou's own trim-and-fill *g* = 0.48 sits between these. Conclusion: a "video games improve cognition" style claim can survive peer review, then collapse under bias correction.
Evidence: *Psychological Bulletin* 144(1):77–110, 2018; *Technology, Mind and Behavior* 2023; *Collabra: Psychology* 5(1):30, 2019. **Demonstrated (contested; bias correction is the negative result).**
https://doi.org/10.1037/bul0000130 · https://tmb.apaopen.org/pub/qj0c4ij2 · https://doi.org/10.1525/collabra.231

**60. Deliberate practice explains a minority of performance variance in games, and the definition fight is unresolved.** Macnamara, Hambrick & Oswald (2014): practice–performance association accounted for **26% of games variance** (21% music, 18% sports, 4% education, <1% professions); the 2018 corrigendum revised games to 24% and overall to 14%. Ericsson & Harwell countered that the meta-analysis used a broad definition (structured activity, not strict deliberate practice) and reported *r* ≈ .78 (≈61% of reliable variance) under stricter criteria; Macnamara et al. disputed the inclusion standards. The defensible reading: high-quality practice is important and probably necessary, but the 2014 meta-analysis does not support practice being *sufficient* — and none of this says practice *causes* nothing.
Evidence: *Psychological Science* 25(8):1608–1618, 2014 + 2018 corrigendum; *Frontiers in Psychology* 10:2396, 2019; *Psychonomic Bulletin & Review* rebuttals. **Contested.**
https://doi.org/10.1177/0956797614535810 · https://doi.org/10.3389/fpsyg.2019.02396

**61. CS:GO performance is explicitly multi-dimensional; K/D and rank are inadequate proxies.** Sharpe et al. (2023) ran a Delphi panel (researchers, practitioners, coaches, analysts, professionals) over a review identifying 32 performance variables, and separated **outcome performance** (score, kills, rank) from **action performance** (reaction/response time, shooting accuracy, mouse control) from **task performance** (contribution to objectives) from **contextual performance** (teamwork/communication). Professional players preferred match outcomes and game score; researchers and practitioners preferred action measures — a live disagreement about what "good" means.
Evidence: *Journal of Electronic Gaming and Esports* 1(1), 2023, doi:10.1123/jege.2022-0017. **Research-supported (consensus framework).**
https://doi.org/10.1123/jege.2022-0017

**62. There is no validated, published CS2 coach-feedback efficacy trial.** Peer-reviewed esports coaching work as of 2026 is: theoretical frameworks (Bubna et al. 2023 propose a constraints-led approach and note CLA has **not yet been studied** in esports); qualitative accounts of perceived training quality; component-level interventions (physical, psychological, aim); and one n = 3 single-case video-feedback study in a *different* game. Pedraza-Ramirez et al.'s systematic review of esports psychology confirms the field's empirical thinness.
Evidence: *Frontiers in Psychology* 14:1191801, 2023; *International Review of Sport and Exercise Psychology* 13(1):319–352, 2020. **Plausible-untested.**
https://doi.org/10.3389/fpsyg.2023.1191801 · https://doi.org/10.1080/1750984X.2020.1723122

---

## 9. Synthesis: how we would prove our coaching changed behaviour for one player

The literature converges on a specific, achievable design. This is the answer to the brief.

**What can be demonstrated**
1. **Target a behaviour, not a feeling or a rank.** Use process goals (*d* = 1.36) rather than outcome goals (*d* = 0.09) (#43); operationalise a countable in-game behaviour (e.g. "checks teammate economy state before calling a force buy"; "first contact taken with utility available"). This mirrors the only successful esports self-review precedent, which targeted one anti-air behaviour and measured transfer to ranked play (#15, #55).
2. **Record the ex-ante judgment before the outcome exists.** This is the only reliable anti-hindsight mechanism (#32); generic warnings fail (#30). Store the player's pre-round or pre-session prediction, then score the decision from the information state at that moment (#34).
3. **Score process separately from result, and aggregate decision classes.** Use the EV-difference family (#38) rather than "did we win the round" (#33, #36, #40). Single results are noise; the poker evidence says a persistent edge takes hundreds-to-thousands of observations to separate from variance (#37).
4. **Use a single-case experimental design with a real baseline.** Establish baseline stability (WWC v5.0: ≥6 baseline points, #50), then use a multiple-baseline across behaviours/contexts, or an A-B-A-B withdrawal where ethical, or randomised alternating conditions with a randomisation test (#47, #48). Report Tau-U alongside systematic visual analysis (#49), and pre-register the design using CENT/SCRIBE items (#51).
5. **Measure retention and transfer, not in-session performance.** Self-modelling gains vanished at one week (#9) and video-feedback benefits appear in retention/transfer, not acquisition (#10, #14). The measurement window must be games played *after* the review.
6. **Treat your own effect size as inflated.** Published sport-psychology single-case effects average Δ ≈ 2.4–2.8 and are associated with short baselines and absent fidelity checks (#52); publication bias and salami slicing inflated the canonical game-training meta-analysis by a large factor (#59). Prespecify, measure intervention fidelity, and count your own null results.
7. **Make measurement part of the intervention.** Progress monitoring raises goal attainment by *d* = 0.40 (#45); feedback with high informational content (what was wrong, why, what next) reached *d* = 0.99 versus 0.24 for reinforcement/punishment (#4). A dashboard that is merely descriptive gives up the strongest available effect.

**What cannot be demonstrated with current data**
- that a change in a measured behaviour *caused* an MMR/Elo/rank change (#62: no validated CS2 coaching trial; #56: component improvements routinely fail to transfer; #53: practice volume does not predict performance). Rank change is a downstream, low-power, multi-cause outcome. Report it as a descriptive secondary measure with a stated confidence interval, never as the primary evidence.
- that the coaching "works in general" from n = 1. Generalisation requires replication across behaviours (multiple baseline) — not statistical inference to a population.

**Minimum viable evidence package for one player**
operationalised behaviour + stable ≥6-point baseline + prespecified randomisation or multiple-baseline structure + ex-ante decision records + process scoring (EV-difference) + post-review retention/transfer window + Tau-U + visual analysis + fidelity log + declared expectation that the true effect is smaller than the observed one.

---

## Contradictions / open questions

1. **Is feedback's average effect ~0.41 (Kluger & DeNisi), ~0.48 (Wisniewski deduplicated), or ~0.79 (Hattie meta-synthesis)?** The three numbers are not interchangeable: they differ in unit of analysis, weighting, deduplication and inclusion. The deduplicated random-effects estimate (*d* ≈ 0.48) is the most defensible for planning; the 0.79 figure should not be quoted as a causal effect of "feedback". Note also that Kluger & DeNisi's paper is variously cited as weighted mean *d* = 0.41 and as 0.38 by later authors — the discrepancy is in how effects were weighted.
2. **Does the *direction* of feedback matter?** Kluger & DeNisi (1996) found sign was not a reliable moderator. Aarvik et al. (2024) found positive feedback helped and negative feedback did nothing. Wisniewski et al. (2020) found the damage came from *uninformative* feedback (rewards/punishments), not from negative valence. These are reconcilable only if "sign" and "informational content" are separated — most published work does not separate them cleanly.
3. **Self-assessment: is low-performer overconfidence a real psychological effect or a statistical artefact?** Kruger & Dunning (1999) versus Gignac & Zajenkowski (2020); Dunkel et al. (2023) find a statistically significant but *minimal* residual. Davis et al. (2006) and Zell & Krizan (2014) show poor self-assessment accuracy *without* committing to the Dunning–Kruger mechanism. The practical implication (use external data) survives either way, but the mechanism claim does not.
4. **Does debiasing hindsight work?** Guilbault et al. (2004) found reduction manipulations did not lower bias overall; a 2024 study found task-specific, point-of-judgment prompts did reduce it in novices; Salmen et al. (2023) found foresight instruction effective even post-outcome. The consistent signal is that *structural* fixes (record the judgment first) beat *instructional* fixes (tell people to be unbiased), and durability beyond a few weeks is essentially unestablished.
5. **Does video review help experts or novices?** Self-observation without a reference of correctness is theorised to fail for novices (#13), and video coaching shows the largest benefit for low-baseline learners (#11). But for a 2000-Elo player the useful comparison is expert-with-reference vs expert-without — and no study isolates that. The "expert self-analysis backfires" claim is theoretically motivated but **not experimentally established** for this population.
6. **Is more feedback worse?** The guidance hypothesis predicted frequent augmented feedback degrades learning; Marschall et al.'s meta-analysis found the reversal effect to be largely a laboratory artifact with no systematic effect in sport tasks (#8). Yet self-controlled feedback clearly beats passively-received feedback in retention/transfer (#10). The open question is whether "control over feedback" rather than "frequency" is the real variable.
7. **Multiple-baseline vs withdrawal in a competitive game.** Withdrawal designs give the strongest causal inference but are ethically/practically awkward for a player mid-season; multiple-baseline across behaviours is the usual compromise, at the cost of weaker within-behaviour replication. There is no worked precedent in CS2.
8. **Publication bias contaminates most of the relevant esports/feedback evidence bases** (#10, #59, #52, #53's null is one of the few unbiased-looking results). Every favourable number above should be treated as an upper bound.
9. **Nothing in the literature specifies the CS2 decision taxonomy that process scoring requires** — what counts as a decision, at what granularity, and what the ex-ante information state is. That is an unsolved modelling problem, and it is the largest single source of unquantified error in any "did coaching change behaviour" claim for this game.

---

## Top sources

1. Kluger, A. N., & DeNisi, A. (1996). The effects of feedback interventions on performance. *Psychological Bulletin* 119(2):254–284. https://doi.org/10.1037/0033-2909.119.2.254 — the negative-effects result and Feedback Intervention Theory.
2. Wisniewski, B., Zierer, K., & Hattie, J. (2020). The Power of Feedback Revisited. *Frontiers in Psychology* 10:3087. https://doi.org/10.3389/fpsyg.2019.03087 — the deduplicated primary-study estimate (0.48), 17% negative, and the informational-content moderator.
3. Hattie, J., & Timperley, H. (2007). The Power of Feedback. *Review of Educational Research* 77(1):81–112. https://doi.org/10.3102/003465430298487 — four levels of feedback; the source of the contested 0.79.
4. Tannenbaum, S. I., & Cerasoli, C. P. (2013). Do team and individual debriefs enhance performance? *Human Factors* 55(1):231–245. https://doi.org/10.1177/0018720812448394 — debriefs *d* = 0.67.
5. Davis, D. A., et al. (2006). Accuracy of physician self-assessment. *JAMA* 296(9):1094–1102. https://doi.org/10.1001/jama.296.9.1094 — 13/20 comparisons weak/absent/inverse.
6. Eva, K. W., & Regehr, G. (2005). Self-assessment in the health professions: a reformulation. *JCEHP* 25(S1):S11–S21. https://doi.org/10.1097/00001888-200510001-00015 — self-directed assessment seeking.
7. Baron, J., & Hershey, J. C. (1988). Outcome bias in decision evaluation. *JPSP* 54(4):569–579. https://doi.org/10.1037/0022-3514.54.4.569 — process vs outcome evaluation.
8. Romer, D. (2006). Do Firms Maximize? Evidence from Professional Football. *Journal of Political Economy* 114(2):340–365. https://doi.org/10.1086/501171 — decision quality measured by EV, independent of results.
9. Wang, B., et al. (2025). Self-Controlled Feedback and Behavioral Outcomes in Motor Skill Learning: A Meta-Analysis. *Behavioral Sciences* 15(9):1291. https://doi.org/10.3390/bs15091291 — acquisition null, retention/transfer positive.
10. Wang, Z., et al. (2026). The impact of self-modeling on athletic performance and self-efficacy. *Frontiers in Sports and Active Living* 8:1809566. https://doi.org/10.3389/fspor.2026.1809566 — SMD 0.81, decaying by one week, dose-dependent.
11. Harkin, B., et al. (2016). Does monitoring goal progress promote goal attainment? *Psychological Bulletin* 142(2):198–232. https://doi.org/10.1037/bul0000025 — measurement as intervention, *d* = 0.40.
12. Locke, E. A., & Latham, G. P. (2002). Building a practically useful theory of goal setting and task motivation. *American Psychologist* 57(9):705–717. https://doi.org/10.1037/0003-066X.57.9.705
13. Parker, R. I., Vannest, K. J., Davis, J. L., & Sauber, S. B. (2011). Combining nonoverlap and trend for single-case research: Tau-U. *Behavior Therapy* 42(2):284–299. https://doi.org/10.1016/j.beth.2010.08.006
14. Barker, J. B., et al. (2020). The effectiveness of psychological skills training and behavioral interventions in sport using single-case designs. *Psychology of Sport and Exercise* 51:101746. https://researchonline.gcu.ac.uk/en/publications/the-effectiveness-of-psychological-skills-training-and-behavioral/
15. Hilgard, J., Sala, G., Boot, W. R., & Simons, D. J. (2019). Overestimation of Action-Game Training Effects: Publication Bias and Salami Slicing. *Collabra: Psychology* 5(1):30. https://doi.org/10.1525/collabra.231 — the replication/critique anchor for "training improves skill" claims.
16. White, R., Miltenberger, R., & Concepcion, A. (2024). Evaluating video feedback to improve eSports performance in Street Fighter V. *Behavioral Interventions*. https://doi.org/10.1002/bin.2056 — the closest esports self-review precedent.
17. Pluss, M. A., et al. (2022). Game-specific practice behaviors of professional and semi-professional esports players: a 52-week longitudinal study. *Computers in Human Behavior* 137:107421. https://doi.org/10.1016/j.chb.2022.107421 — practice volume does not predict performance.
18. Vardal, O., et al. (2022). Mind the gap: Distributed practice enhances performance in a MOBA game. *PLOS ONE* 17(10):e0275843. https://doi.org/10.1371/journal.pone.0275843
19. Sharpe, B. T., et al. (2023). Indexing esport performance. *Journal of Electronic Gaming and Esports* 1(1). https://doi.org/10.1123/jege.2022-0017 — multi-dimensional performance taxonomy for CS:GO.
20. Bubna, K., Trotter, M. G., Watson, M., & Polman, R. (2023). Coaching and talent development in esports. *Frontiers in Psychology* 14:1191801. https://doi.org/10.3389/fpsyg.2023.1191801 — the field's own statement that constraints-led coaching is untested in esports.

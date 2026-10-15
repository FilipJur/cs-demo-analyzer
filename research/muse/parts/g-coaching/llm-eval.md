# LLM Evaluation Methodology for a CS2 Coaching Judge

**Scope.** Honest, state-of-the-art evaluation methodology for a system where a commercial-API LLM reads CS2 demo-derived facts and emits coaching judgments about an expert human player's decisions. No implementation, no code. Sources verified as of **2026-10-15**; preference for 2024→2026 with landmark older work where it is the canonical citation.

**Tag legend** (per finding):

- `Demonstrated` — reproduced, controlled or large-scale empirical result with clear methodology.
- `Experimental` — single controlled study / benchmark result; not yet replicated broadly.
- `Research-supported` — convergent literature or strong theory + partial empirical support; mechanism not fully nailed.
- `Plausible-untested` — argued or analogical; no direct evidence in the relevant setting.
- `Infeasible` — literature indicates it cannot be done as stated.

**How to read this for our case.** Our target task is *harder than anything in the LLM-judge literature's happy path*: it is (a) long-horizon (a round/decisions-over-time), (b) domain-expert (top-2000 FACEIT), (c) partly subjective (was this the right call *for this player's role/team*?), and (d) grounded in a fact base that is *ours* (demo-derived numbers), not a retrieved document. Sections 2 (IRR) and 6 (reader studies) are therefore load-bearing: the human reference standard is itself the bottleneck.

---

## 1. LLM-as-a-judge: state, biases, reliability (2024–2026)

### 1. The canonical "judges match humans" result is real but narrow: GPT-4-class judges reached >80% agreement with human preferences on pairwise chatbot-quality comparisons.

Zheng et al. (MT-Bench / Chatbot Arena), 2023-06-09. Agreement was on *general chat preference*, using *pairwise* comparison, with strong judges; the same paper already names position, verbosity and self-enhancement biases and limited reasoning ability as caveats. This is the number everyone cites and it does not transfer to expert, long-horizon judgment without re-validation.
`Demonstrated` (for that setting) / `Plausible-untested` (for ours).
https://arxiv.org/abs/2306.05685

### 2. Position bias in pairwise judging is systematic, not noise, and is worst when the two options are close in quality.

Shi et al., first version 2024-06-12, latest revision v9 2025-11-11, AACL-IJCNLP 2025. 15 judge models, MTBench+DevBench, ~40 generating models, >150,000 evaluation instances. Introduces repetition stability, position consistency, preference fairness. Key operational consequence: our judge must be run in both orders (or with order randomisation) whenever we compare two candidate decisions/advice items, and the residual order effect reported.
`Demonstrated`.
https://arxiv.org/abs/2406.07791

### 3. Verbosity/length bias is measurable and correctable by regression; it inflates scores of longer outputs independently of quality.

Dubois et al., 2024-04-06 (COLM 2024), length-controlled AlpacaEval. Controlling for length difference raised Spearman correlation with Chatbot Arena from 0.94 to 0.98. Direct analogue for us: a longer coaching answer will be preferred by the judge unless we control for output length or use length-matched comparisons.
`Demonstrated`.
https://arxiv.org/abs/2404.04475

### 4. Self-preference bias exists and is best explained by familiarity/perplexity, not by the model literally recognising itself.

Wataoka et al., 2024-10-29 (NeurIPS 2024 Safe GenAI Workshop); GPT-4 assigns higher scores to low-perplexity text than human evaluators do, regardless of who wrote it. Practical: never let the same model family generate the candidate coaching text *and* be the only judge; also expect bias toward "LLM-flavoured" phrasings regardless of correctness.
`Experimental`.
https://arxiv.org/abs/2410.21819

### 5. Self-preference is causally linked to self-recognition capability under fine-tuning.

Panickssery, Bowman, Feng, 2024-04-15. Out-of-the-box GPT-4/Llama-2 have non-trivial accuracy at distinguishing their own text; fine-tuning shows a linear correlation between self-recognition and strength of self-preference, with controls for straightforward confounders.
`Experimental`.
https://arxiv.org/abs/2404.13076

### 6. "Preference leakage": if the generator and the judge are related (same model, same family, or trained on the generator's synthetic data), the judge systematically inflates scores — about 23.6% average leakage for same-model generator/judge.

Li et al., 2025-02-03. Measured across Arena-Hard and AlpacaEval 2.0 with a Preference Leakage Score. Judges could not reliably *identify* the related model, so the bias is subtle.
`Experimental`.
https://arxiv.org/abs/2502.01534

### 7. Sycophancy is a general property of RLHF-trained assistants and is partly driven by human-preference data itself.

Sharma et al. (Anthropic), 2023-10-23. Five state-of-the-art assistants showed sycophancy across four free-form tasks; both humans and preference models preferred convincingly-written sycophantic answers over correct ones a non-negligible fraction of the time. For a coach, this predicts exactly the failure we care about: agreeing with the player's in-game choice instead of calling it wrong.
`Demonstrated`.
https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models · https://arxiv.org/abs/2310.13548

### 8. User-facing sycophancy harm is now measured experimentally, and the harmful responses are the *more popular* ones.

Cheng, Lee, Khadpe, Yu, Han, Jurafsky; arXiv 2025-10-01; peer-reviewed in *Science* 2026-03-26 (DOI 10.1126/science.aec8352). 11 models affirmed users ~49% more often than human responders, including for deceptive/illegal conduct; three preregistered experiments (n=2,405) showed reduced willingness to apologise/take responsibility. Caveat acknowledged by the authors: outcomes are self-reported intentions, short horizon.
`Experimental`.
https://arxiv.org/abs/2510.01395

### 9. Score compression, central-tendency bias and scale sensitivity are quantifiable; changing only the rating scale can shift measured bias by ~0.93 points on a 1–7 scale.

Vaugrante & Hagendorff, 2026-10-04. 10 reasoning models, multiple designs. Also: prompt detail changed leniency by 28.9 percentage points and model identity by up to 56.1pp; model identity was the dominant variance source. Counter-intuitively, lower reasoning effort changed neither accuracy nor leniency.
`Experimental`.
https://arxiv.org/abs/2610.05094

### 10. High agreement with humans does not imply the judge's *scores* match; judges differ from human point scores by up to 5 points.

Thakur, Choudhary, Ramayapally, Vaidyanathan, Hupkes — GEM² 2025 (published 2025-07). 13 judge models, 9 exam-taker models. Only the largest models showed reasonable human alignment; found sensitivity to prompt complexity and a leniency bias. Their explicit methodological point: percent agreement is an inadequate alignment metric.
`Experimental`.
https://aclanthology.org/2025.gem-1.33/

### 11. On expert-knowledge tasks, judge–SME agreement drops to ~64–68% and LLM judges agree *more* with lay users than with subject-matter experts on some general-preference items.

Szymanski et al., IUI 2025 (arXiv 2024-10-26). Domains: dietetics (registered dietitians) and mental health (clinical psychologists); pairwise comparisons. Adding an "expert persona" to the judge improved SME alignment but did not close the gap. This is the strongest single warning for a domain-expert coaching judge.
`Experimental`.
https://arxiv.org/abs/2410.20266

### 12. On well-operationalised, observable sub-components of a subjective rubric, LLM judges can approach expert–expert reliability — and the correct benchmark is the experts' own agreement, not a fictional gold standard.

Kumar et al., *Nature Machine Intelligence* (arXiv 2025-06-11, rev. 2025-10-03; journal publication 2026-02-11), 200 conversations, 3,150 expert / 2,844 crowd / 3,150 LLM annotations. Median quadratically-weighted Cohen's κ: expert–LLM 0.60 vs expert–expert 0.58 (ranges 0.17–0.86 and 0.11–0.84). Agreement was strongest for observable behaviours and weakest for ambiguous constructs. The authors argue expert disagreement reveals genuine ambiguity, so "expert ground truth" should not be treated as objective truth.
`Demonstrated`.
https://www.nature.com/articles/s42256-025-01169-6 · https://arxiv.org/abs/2506.10150

### 13. When the comparison has an objectively correct answer, judge reliability collapses: GPT-4o was only slightly better than chance on JudgeBench.

Tan et al., 2024-10-16. JudgeBench pairs responses across knowledge, reasoning, math and coding with preference labels reflecting objective correctness (not crowd preference). Prompted judges, fine-tuned judges, multi-agent judges and reward models all struggled. Implication: a judge that is good at "which answer is nicer" is not thereby good at "was this the right play".
`Experimental`.
https://arxiv.org/abs/2410.12784

### 14. For long-horizon agentic behaviour, single-run success rates massively overstate reliability; the field uses pass^k.

Yao, Shinn, Razavi, Narasimhan — τ-bench, 2024-06-17. Even GPT-4o-class function-calling agents succeed on <50% of tasks; **pass^8 <25%** in the retail domain. pass^k (probability of succeeding k times in a row) is the right family of metric for "does the coach give consistent advice across re-runs of the same round".
`Demonstrated`.
https://arxiv.org/abs/2406.12045

### 15. In medicine, judge agreement with experts is strongly task-dependent: excellent on narrow rubric-anchored scoring, poor on factuality.

Evidence, deliberately mixed:
- Croxford et al., *npj Digital Medicine* 2025 — LLM scoring of clinical summaries on the PDSQI-9 rubric vs 7 physicians: **ICC 0.818** (95% CI 0.772–0.854) for the best judge, median difference 0 points; weaker judges 0.33–0.76. https://doi.org/10.1038/s41746-025-02005-2
- MedFactEval (arXiv 2025-09) — multi-LLM jury vs a **seven-physician majority vote**: **κ = 0.81**, vs κ = 0.67 for a single human evaluator; the task was bounded fact-checking of clinician-defined key facts. https://arxiv.org/abs/2509.05878
- CLEVER (*JMIR AI* 2025) — GPT-4o as a fifth "clinician" alongside four professionals: for factuality, absolute-agreement ICC ≈ **−0.10 to 0.14**; authors flag possible self-preference. https://ai.jmir.org/2025/1/e72153
`Experimental` (each) / `Research-supported` (the pattern: narrow + rubric + grounded ⇒ usable; open-ended + factual ⇒ not).
https://doi.org/10.1038/s41746-025-02005-2 · https://arxiv.org/abs/2509.05878 · https://ai.jmir.org/2025/1/e72153

### 16. Known-bias inventory for judge design (consolidated).

| Bias | Evidence | Status |
|---|---|---|
| Position/order | Shi et al. 2024/2025, >150k instances | Demonstrated |
| Verbosity/length | Dubois et al. 2024 | Demonstrated |
| Self-preference | Wataoka 2024; Panickssery 2024 | Demonstrated/Experimental |
| Generator–judge leakage | Li et al. 2025 | Experimental |
| Sycophancy | Sharma 2023; Cheng 2026 | Demonstrated |
| Score compression / central tendency | Vaugrante & Hagendorff 2026 | Experimental |
| Scale/prompt-format sensitivity | Vaugrante & Hagendorff 2026; Sclar 2024 (§5) | Demonstrated (LLM behaviour) |
| Leniency | Thakur et al. 2025 | Experimental |
| Degradation on expert/objective tasks | Szymanski 2025; Tan 2024 | Experimental |

---

## 2. Inter-rater agreement for subjective coding

### 17. Cohen's κ is only interpretable alongside the contingency table: high agreement can coexist with κ ≈ 0, and the "kappa paradox" is a property of the statistic, not evidence of bad raters.

Feinstein & Cicchetti, *J Clin Epidemiol* 1990;43(6):543-9 — the canonical statement of the two paradoxes (marginal imbalance / asymmetry). Byrt, Bishop & Carlin (1993) showed κ is driven by both prevalence and bias and recommended reporting both. Both are still the standard citations for why a low κ on a rare-event code (e.g. "bad utility usage" occurring in 5% of decisions) is not evidence of a bad codebook.
`Demonstrated` (mathematical property).
https://pubmed.ncbi.nlm.nih.gov/2348207/ · https://www.sciencedirect.com/science/article/pii/089543569390018V

### 18. The famous κ bands (0.61–0.80 "substantial", >0.80 "almost perfect") are a 1977 convention, not a standard.

Landis & Koch, *Biometrics* 1977;33(1):159-74. The paper introduced the methodology and illustrated it on a clinical-diagnosis example; the verbal bands that get quoted everywhere are interpretive conventions that the field later hardened into thresholds.
`Research-supported` (convention, widely mis-cited as a rule).
https://pubmed.ncbi.nlm.nih.gov/843571/

### 19. A stricter, healthcare-oriented reading exists: κ < 0.60 should be treated as inadequate, and κ plus raw agreement plus CIs must all be reported.

McHugh, *Biochemia Medica* 2012. Proposes 0.60–0.79 = "moderate", 0.80–0.90 = "strong", and argues the usual bands are too permissive for clinical decisions; insists that a point estimate without a CI and without percent agreement is uninterpretable.
`Research-supported`.
https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/

### 20. Which coefficient to use depends on data structure, not preference.

- 2 raters, nominal → Cohen's κ (weighted if ordinal).
- ≥3 raters, one nominal label each → Fleiss' κ (note: Fleiss' κ fixes the number of raters per item; it is not a drop-in for missing data).
- ≥3 raters, missing ratings, and/or mixed measurement levels → Krippendorff's α (nominal/ordinal/interval/ratio difference functions).
- Continuous or fine-grained ordinal scores → ICC (absolute agreement vs consistency are different estimands) or Bland–Altman.
- Counts/durations/timestamps → agreement within a tolerance window + ICC or Bland–Altman; κ is inappropriate.
Sports performance analysis has an explicit precedent for weighted κ on ordinal, spatially-structured categories.
`Standard` (method choice); `Demonstrated` (properties).
https://www.tandfonline.com/doi/abs/10.1080/24748668.2007.11868383 · https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/

### 21. Krippendorff's own guidance: α ≥ .800 for conclusions, .667–.800 only for tentative/exploratory conclusions, and the cut-off should depend on the cost of error — report a confidence interval, not a magic number.

As reproduced in Krippendorff's reliability guidance documents (University of Pennsylvania repository copies): the same source gives an approximate **minimum coder-values** table at p=.05 — for a category with prevalence 0.50, 60 values for α=.667 and 103 for α=.800; at prevalence 0.10, 172 and 293; at prevalence 0.05, 329 and 560. Rare codes are expensive.
`Research-supported` (documented convention + sample-size arithmetic).
https://repository.upenn.edu/bitstreams/b6ea3a5b-3dee-4f27-a159-e44393eda7d4/download

### 22. Number of raters/doubly-coded units should be chosen for *precision*, not by a folk rule like "30 units".

Donner & Eliasziw (*Stat Med* 1992) developed CI construction, significance testing and sample-size estimation for κ via a goodness-of-fit approach designed for small samples; Cantor (1996) gave sample sizes for two raters/two categories including unequal frequencies. The precision form is n ≈ z²·V_κ/d² (or the simpler n ≈ z²·p_o(1−p_o)/(d²(1−p_e)²)). Worked example: p_o=.80, p_e=.50, 95% CI, half-width d=.10 ⇒ n ≈ 246 units; halving the half-width to .05 quadruples it to ≈ 984. **Note: n counts rated units, not ratings.** For >2 raters, weighted κ, or ordinal data these closed forms do not apply — simulate.
`Research-supported` (statistical method).
https://onlinelibrary.wiley.com/doi/abs/10.1002/sim.4780111109 · https://cran.r-project.org/web/packages/kappaSize/kappaSize.pdf

### 23. CONTRADICTED / CONTESTED: the choice of agreement coefficient is itself disputed, and adjusted coefficients can overstate reliability.

- Gwet's AC1/AC2 use a different chance-agreement model and are more stable under high prevalence; the Journal of Clinical Epidemiology has published an exchange arguing they are *not* substitutes for κ (different estimands). https://www.jclinepi.com/article/S0895-4356(21)00284-5/fulltext
- Comparative studies: "A comparison of Cohen's Kappa and Gwet's AC1 when calculating inter-rater reliability" (PMC3643869); "Interrater reliability estimators tested against true interrater reliabilities" (BMC Med Res Methodol 2022) — estimator rankings change with the true reliability and design. https://link.springer.com/article/10.1186/s12874-022-01707-5
- PABAK (prevalence-adjusted) can look better but does not recover the "true" reliability and should not be interpreted as the same parameter (PMC2636838).
`Contested`.
https://pmc.ncbi.nlm.nih.gov/articles/PMC2636838/

### 24. What the sports/medicine literature actually accepts for expert judgment.

- Sports notational analysis: κ ≥ .80 as a target for main variables; .61–.79 often defensible for complex tactical/subjective judgments; <.40 generally insufficient; weighted κ for ordinal ratings; report CI + % agreement + category frequencies. https://www.tandfonline.com/doi/abs/10.1080/24748668.2007.11868383
- Methodological quality scales for sports video analysis (QA-SIVAS) formalise exactly this: clear coding units, trained coders, a random reliability subsample, per-variable reporting. https://pmc.ncbi.nlm.nih.gov/articles/PMC10799118/
- Video-review reliability in sport (BJSM 2025) reports the same asymmetry: clearly defined visible events reach high agreement; inferential/tactical constructs do not. https://bjsm.bmj.com/content/59/23/1678
- Medicine: the same Moderate/Substantial/Almost-perfect framing is used, but κ<0.60 is commonly treated as inadequate for clinical decisions (McHugh). https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/
`Research-supported`.
https://pmc.ncbi.nlm.nih.gov/articles/PMC10799118/

### 25. Esports-specific precedent: experienced-coder reliability can be very high for *observable* events and drops for novices on expert-dependent events.

Novak, Bennett, Pluss & Fransen (2019), *Performance analysis in esports, Part 1* (League of Legends; SportRxiv preprint, DOI 10.31236/osf.io/sm3nj). 30 professional matches; three experienced player-coders vs a novice coder; Krippendorff's α = .861–1.000 between experienced coders, and .868–1.000 between an experienced coder and published match statistics, with the novice diverging on variables such as *First Tower Time* and *First Inhibitor Team*. Two consequences: (a) some events need domain expertise to code, so a novice-coded "ground truth" would silently depress measured coach accuracy; (b) liberally-used public match statistics can themselves serve as a reliability reference for objective events.
`Experimental`.
https://research.rug.nl/en/publications/performance-analysis-in-esports-part-1-the-validity-and-reliabili/

### 26. For our purposes: the human reference standard is the binding constraint, and it should be reported as such.

Across §6 ("expert panel ground truth is unreliable"), §12 (expert–expert κw = 0.58 in a subjective domain), and §25 (novice coders diverge on expert events), the defensible design is not "LLM vs truth" but a **three-way**: expert–expert reliability as the ceiling, LLM–expert reliability as the claim, and crowd/novice–expert reliability as the floor that shows what expertise buys.
`Research-supported`.
(composite of the cited sources)

---

## 3. Grounding / faithfulness / hallucination evaluation

### 27. Atomic-fact decomposition + verification is the canonical long-form factual-precision metric, and its original evaluation used a strong-model verifier with human-verified cost/accuracy trade-offs.

Min et al., "FActScore", EMNLP 2023 (arXiv 2023-05). Breaks generation into atomic facts and computes the fraction supported by a knowledge source. Useful shape for us: decompose a coaching paragraph into individual claims, each of which must be checkable against logged demo facts.
`Standard` for factual precision on biographies/long-form; `Experimental` for transfer.
https://aclanthology.org/2023.emnlp-main.741/ · https://arxiv.org/abs/2305.14251

### 28. Citation quality has two separate axes — precision and recall — and state-of-the-art systems fail badly on recall.

Gao, Yen, Yu & Chen, "ALCE", EMNLP 2023 (arXiv 2023-05-24, rev. 2023-10-31). Automatic metrics for fluency, correctness and citation quality correlated with human judgements. Headline negative result: on ELI5, even the best systems **lack complete citation support 50% of the time**. Directly relevant: our coach will happily state a number it did not derive from the demo.
`Demonstrated`.
https://arxiv.org/abs/2305.14627

### 29. Attributed QA established the evaluation recipe: human annotations as gold, plus a correlated automatic metric — and asked explicitly "how to measure attribution".

Bohnet et al., 2022-12-15 (rev. 2023-02-10). Reproducible framework, broad architecture benchmark.
`Research-supported` (methodological template).
https://arxiv.org/abs/2212.08037

### 30. Reference-free faithfulness metrics (RAGAS-style) make iterative evaluation cheap but put a judge model inside the metric.

Es, James, Espinosa-Anke & Schockaert, 2023-09-26 (rev. 2025-04-28). Suite of metrics for retrieval relevance, faithfulness and answer quality *without* ground-truth human annotations. Consequence: a RAGAS-style faithfulness score inherits every judge bias in §1 — it is not an independent measurement.
`Standard` (widely used) / `Contested` (as evidence of grounding).
https://arxiv.org/abs/2309.15217

### 31. Automatic factuality metrics are gameable: appending innocuous content-free sentences inflates most of their scores, and all of them degrade on hard examples.

Ramprasad & Wallace, 2024-11-25 (rev. 2025-11-05). A shallow classifier separated "easy" (surface-feature-sufficient) from "hard" (requiring reasoning) cases; **all** metrics dropped substantially on hard cases; some were more sensitive to benign fact-preserving edits than to real factual errors. Among tested metrics, prompt-based ChatGPT-DA was most robust — but it over-relies on parametric knowledge rather than the provided reference.
`Demonstrated`.
https://arxiv.org/abs/2411.16638

### 32. RAGTruth is the reference human-annotated hallucination corpus for RAG, with word-level annotation and intensity labels.

Niu et al., 2023-12-31 (rev. 2024-05-17). ~18,000 naturally generated responses from diverse LLMs under RAG, manually annotated at case and word level. Also: fine-tuning a *small* LLM on this corpus reached performance competitive with GPT-4-prompted detectors — i.e. a cheap local grounding detector is plausible.
`Demonstrated`.
https://arxiv.org/abs/2401.00396

### 33. Special-purpose hallucination detectors do not generally beat general LLMs with good prompting, and performance collapses from short to long contexts.

Emery, Goitia, Vargus & Neagu, "HalluMix", 2025-05-01. Seven detection systems across domains. Quotient Detections best overall (accuracy 0.82, F1 0.84). Explicit finding quoted in the wild against the Vectara leaderboard: fine-tuned specialists (Patronus Lynx 8B, Vectara HHEM-2.1-Open, Bespoke-MiniCheck-7B) do not generally outperform prompted general-purpose models.
`Experimental`.
https://arxiv.org/abs/2505.00506

### 34. A widely-cited hallucination leaderboard rests on an evaluator whose self-reported F1 is 45–66%, and the criticism is public and unanswered at that level.

GitHub issue #128 on `vectara/hallucination-leaderboard`, opened 2025-06-13 (still open per page state). Reproduces HHEM-2.1-Open's own numbers: AggreFact-SOTA F1 66.77%, RAGTruth-Summ F1 44.83%, RAGTruth-QA F1 60.00%. Complainant's point: ranking models by a 0.5–2.5% hallucination rate using an evaluator at ~45–67% F1 is mostly noise. The proprietary HHEM-2.1 used for the actual leaderboard is not independently benchmarked.
`Demonstrated` (the F1 numbers are self-reported by the vendor for the open model) / `Contested` (leaderboard validity).
https://github.com/vectara/hallucination-leaderboard/issues/128

### 35. TruthfulQA is a *siteland* negative result: bigger models were less truthful, and scaling alone does not fix imitation of falsehoods.

Lin, Hilton & Evans, 2021-09-08 (ACL 2022). 817 questions across 38 categories designed so that mimicry of human text produces false answers; best model 58% truthful vs human 94%; the largest models were generally the least truthful.
`Demonstrated` (at the time) / `Contested` (saturated and heavily contaminated by 2026; see §44).
https://arxiv.org/abs/2109.07958

### 36. Hallucination benchmarking now separates intrinsic from extrinsic hallucination and dynamically regenerates test data to resist leakage.

Bang et al., "HalluLens", 2025-04-24. Explicitly disentangles hallucination from factuality, analyses existing benchmarks' saturation, and builds dynamic test-set generation because static hallucination benchmarks leak.
`Experimental`.
https://arxiv.org/abs/2504.17550

### 37. **Design pattern for our domain-specific grounding test.**

Synthesised from §27–§32, `Research-supported` as a method, `Plausible-untested` as a whole system:
1. Extract every **atomic factual claim** from a coaching output (numbers, event attributions, positional claims, timestamps, economics).
2. For each claim, require an artefact-level link to a **logged demo fact** with an ID (e.g. `round=14, t=63.2s, entity=playerA, stat=kills`, or `derived: utility_damage_sum(round=14)`).
3. Score **claim coverage** (fraction of claims with a valid link) and **link correctness** (fraction where the linked fact actually entails the claim — this is the part that needs human adjudication on a subsample; an LLM verifier alone is contaminated by §31).
4. Add a **negative control set**: coaching outputs generated with deliberate injected false facts (wrong map, wrong score, player swapped). Any grounding metric that does not fire on those is useless.
5. Attack it: append content-free filler and confirm the score does not rise (the §31 test), and check long-context degradation (the §33 test).

---

## 4. Calibration, uncertainty expression, abstention

### 38. Verbalized confidence is systematically overconfident and clusters at 80–100%; calibration improves with model capability but discrimination stays poor.

Xiong et al., ICLR 2024 (arXiv 2023-06-22). 8 datasets, 5 models. Reported average ECE ≈ 0.52 (GPT-3), 0.377 (GPT-3.5), 0.18 (GPT-4) in the vanilla verbalized setting; GPT-4's average AUROC ≈ 62.7% (50% = random). Critical nuance: prompting (CoT, Top-K, self-probing) can *reduce ECE without improving discrimination*, because accuracy rises while the model still says "confident" to nearly everything. Sampling consistency across independent generations was often the better failure-prediction signal. Stated limitation by the authors: fixed-form QA with unique answers; open-ended generation not covered.
`Demonstrated`.
https://proceedings.iclr.cc/paper_files/paper/2024/file/6733cf15e10e2cd1d59af033c3bb8507-Paper-Conference.pdf · https://arxiv.org/abs/2306.13063

### 39. COUNTERPOINT: verbalized confidence can be *better* calibrated than token probabilities on RLHF models.

Tian et al., "Just Ask for Calibration", EMNLP 2023 (arXiv 2023-05-24). For ChatGPT, GPT-4 and Claude, verbalized confidences emitted as output tokens were typically better calibrated than the model's conditional probabilities on TriviaQA, SciQ and TruthfulQA — often reducing ECE by a relative ~50%. Reconciling §38 and §39: verbalized confidence carries real information, but its *absolute* level is inflated and its ordering quality is task-dependent, so it must be measured, not assumed.
`Demonstrated`.
https://arxiv.org/abs/2305.14975

### 40. Pretrained models can partially self-evaluate ("P(True)", "P(IK)"), but calibration of "I know" does not generalise to new tasks.

Kadavath et al., 2022-07-11. Larger models are well calibrated on multiple-choice/true-false in the right format; P(True) is encouraging; models struggle with P(IK) calibration on unseen tasks. Note: pretrained-model behaviour, largely pre-RLHF — do not assume carry-over.
`Experimental`.
https://arxiv.org/abs/2207.05221

### 41. ECE itself is a biased estimator at realistic sample sizes; the metric needs to be chosen carefully before it is used to adjudicate a calibration claim.

Kumar, Liang & Ma, "Verified Uncertainty Calibration", NeurIPS 2019 (arXiv 2019-09-23). Shows binning-based ECE estimates are biased with limited data and proposes debiased estimators; underlines that "ECE = x" comparisons across different n are not apples to apples.
`Demonstrated` (statistical property).
https://arxiv.org/abs/1909.10155

### 42. Selective prediction gives the right frame for our "should the coach speak?" decision: report the risk–coverage curve, not a single accuracy.

Geifman & El-Yaniv, 2017-05-23: constructing a selective classifier lets a user *set a desired risk level* and reject to meet it (e.g. 2% top-5 ImageNet error at 99.9% probability with ~60% coverage). Applied to us: choose an operating point on the coverage axis ("the coach only commits on the 60% of decisions it can judge"), commit to a risk bound, and report the curve.
`Standard` (methodology) / `Plausible-untested` (for LLM coaching judgment).
https://arxiv.org/abs/1705.08500

### 43. Forced-abstention behaviour is measurable and worse than expected — and reasoning training actively makes it worse.

- Kirichenko, Ibrahim, Chaudhuri & Bell, "AbstentionBench", 2025-06-10: 20 datasets, 6 abstention scenarios (unknown answer, underspecified, false premise, ambiguous/subjective, outdated, underspecified reasoning), >35,000 unanswerable questions. Headline: reasoning models showed an average **24% degradation** in abstention vs their non-reasoning counterparts; scaling had little effect; system prompts helped but did not fix it. https://arxiv.org/abs/2506.09038
- Madhusudhan et al., 2024-07-23 (rev. 2024-09-24): black-box Abstain-QA benchmark + Answerable-Unanswerable Confusion Matrix; even GPT-4 and Mixtral-8x22b struggle; strict prompting and CoT help. https://arxiv.org/abs/2407.16221
- "Know Your Limits: A Survey of Abstention in LLMs", TACL 2025 — taxonomy of when/why/what to abstain over. https://aclanthology.org/2025.tacl-1.26.pdf
`Demonstrated` (the 24% degradation is a measured benchmark result) / `Experimental`.
https://arxiv.org/abs/2506.09038

### 44. **Practical calibration protocol for the coach.**

Synthesised, `Research-supported`: (a) elicit verbal confidence *and* sample k≥5 judgments and use agreement as a second signal (§38); (b) do not trust the raw confidence number as a probability — fit a calibration map on a held-out set and report a reliability diagram plus ECE with CIs (§41); (c) evaluate the risk–coverage curve for the decision "commit a coaching claim vs abstain" (§42); (d) explicitly score abstention with an answerable/unanswerable confusion matrix, including *false abstention* on answerable items, because reasoning-tuned models over-answer (§43).

---

## 5. Reproducibility, nondeterminism, contamination

### 45. "Temperature = 0 with a fixed seed" is not deterministic in hosted APIs, and the resulting accuracy spread is large.

Atil et al., 2024-08-06. Five LLMs × eight tasks × 10 runs, zero-shot and few-shot. Accuracy variation across naturally occurring runs up to **15 percentage points**; the best-possible to worst-possible gap up to **70 points**; no model gave repeatable accuracy across all tasks, let alone identical strings. The authors introduce TARr@N (total agreement rate over raw output) and TARa@N (over parsed answers), and report that non-determinism is likely *structural* to batched hosted serving.
`Demonstrated`.
https://arxiv.org/abs/2408.04667

### 46. Benchmark scores should be reported with an interval; repeats are the cheap way to get one.

Blackwell, Barry & Cohn, 2024-10-04 (rev. 2025-06-27). Explicitly motivates quantifying benchmark uncertainty because models are stochastic even at temperature 0 with a fixed seed, and few benchmark studies do it.
`Research-supported`.
https://arxiv.org/abs/2410.03492

### 47. The nondeterminism has identifiable numerical sources even at the kernel level.

"Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference", NeurIPS 2025 (arXiv 2025-06). Relevant because it means provider-side fixes are possible but *not guaranteed* for any given endpoint: treat determinism as a property to be tested, not assumed.
`Experimental`.
https://proceedings.neurips.cc/paper_files/paper/2025/file/f80094a824ba5912d4a2de169c404a40-Paper-Conference.pdf · https://arxiv.org/abs/2506.09501

### 48. LLM judges have low *intra*-rater reliability: the same judge, same item, different run, different score.

Haldar & Hockenmaier, "Rating Roulette", Findings of EMNLP 2025 (2025-11), pp. 24986–25004. Scores were inconsistent across runs and "almost arbitrary in the worst case". Consequence for us: **any** single-run judge score is a sample, not a measurement; report per-item score variance and repeat all judge calls.
`Demonstrated`.
https://aclanthology.org/2025.findings-emnlp.1361/

### 49. Prompt *format* alone can move accuracy by up to 76 points, and format performance correlates only weakly across models.

Sclar, Choi, Tsvetkov & Suhr, ICLR 2024 (arXiv 2023-10-17, rev. 2024-07-01). LLaMA-2-13B few-shot; sensitivity persisted with scale, more shots, and instruction tuning. They propose FormatSpread: report an *interval* of performance across plausible prompt formats instead of a single number, and warn that comparing models under one arbitrary fixed format is methodologically invalid.
`Demonstrated`.
https://arxiv.org/abs/2310.11324

### 50. The same endpoint changes behaviour over time without a version change: GPT-4's prime/composite accuracy went from 84% to 51% between March and June 2023.

Chen, Zaharia & Zou, 2023-07-18 (rev. 2023-10-31). "the behavior of the 'same' LLM service can change substantially in a relatively short amount of time, highlighting the need for continuous monitoring". Combined with §45–§48 this rules out "we evaluated the coach once, it works".
`Demonstrated`.
https://arxiv.org/abs/2307.09009

### 51. Version pinning is necessary but not sufficient: pinned snapshots are retired on a schedule, with notice periods that vary by model class.

OpenAI's deprecation policy (accessed 2026-10-15): at least 6 months' notice for generally available models, ≥3 months for specialised variants, and **as little as ~2 weeks for preview models**; there is a `shutdown_date` field on `GET /v1/models` for programmatic monitoring. The page as of 2026-10-14 shows GPT-4o (`gpt-4o-2024-08-06`, `gpt-4o-2024-11-20`), GPT-4o mini, GPT-4.1 and GPT-4.1 mini scheduled for shutdown on **2027-01-14**, and many 2025-era snapshots already gone. Practical requirement: an evaluation harness must be re-run and re-baselined at every model migration, and the migration itself is an evaluation event.
`Standard` (provider policy, verifiable).
https://developers.openai.com/api/docs/deprecations

### 52. Benchmark contamination is real, its size is probably *under*-reported, and its impact must be measured against model behaviour, not n-gram overlap alone.

Singh, Kocyigit, Poulton, Esiobu, Lomeli, Szilvasy & Hupkes, 2024-11-06 (ConTAM). 13 benchmarks, 7 models, 2 families. Findings: contamination may have a much larger effect than reported in recent model releases; the effect differs by model scale; the *longest* contaminated substring is a better signal than the union of all matches; large n and ignoring infrequent pre-training matches create false negatives.
`Demonstrated`.
https://arxiv.org/abs/2411.03923

### 53. For our pipeline the contamination risk is primarily *self-inflicted*.

This is not a public-benchmark problem in the usual sense: our fact base and our coaching rubric are private. The realistic failure modes are (a) the judge's parametric CS2 knowledge overriding the supplied demo facts (§31: "prompting LLMs to assess factuality may overly rely on their parametric knowledge rather than the provided reference"), (b) repeated informal iteration on the same held-out rounds until the harness overfits them, and (c) the person writing the rubric also writing the LLM-judge prompt. Mitigations: frozen eval sets, a retained never-touched set, pre-registered rubric and codebook versions, and a judge prompt authored by someone other than the prompt author.
`Research-supported` (by analogy to §31/§52 and the meta-review in §55).
(general survey context: https://arxiv.org/abs/2406.04244)

---

## 6. Judgment-quality evaluation designs from other domains

### 54. Chess: human-like models (Maia) beat engines at predicting human moves, and the paper's framing — aligning to *human* decisions rather than optimal ones — is the closest structural analogue to coaching.

McIlroy-Young, Sen, Kleinberg & Anderson, KDD 2020 (DOI 10.1145/3394486.3403219). Skill-conditioned move prediction. The paper's claim is that off-the-shelf engines (including an open-source AlphaZero) "do not predict human moves well" while Maia predicts human moves "at a much higher accuracy"; the concrete numbers usually quoted (Maia ≈53% move-match vs Leela ≈43% and Stockfish ≈38%) come from the project's own write-up rather than the abstract, and depend on cohort/engine/eval setup. Also introduces a model of whether a player will make a significant mistake next move. Follow-ups: individual-player modelling (arXiv 2008.10086), Maia-2 unified skill-aware model (NeurIPS 2024, arXiv 2409.20553), Maia-3/Chessformer (github.com/CSSLab/maia3).
**Limitation that matters for us:** Maia predicts behaviour; it provides no ground truth for *advice quality*. Its evaluation target (predict the human move) is objectively scorable; ours (was the decision good) is not.
`Demonstrated`.
https://arxiv.org/abs/2006.01855 · https://www.cs.toronto.edu/~ashton/pubs/maia-kdd2020.pdf

### 55. Go: superhuman AI changed human play measurably, and large-scale expert annotation of human moves is an established dataset design.

- Shin et al., PNAS 2023, "Superhuman artificial intelligence can improve human decision-making by increasing novelty" — analyses of professional Go records before/after AlphaGo, associating AI-era novelty with improved human performance. https://www.pnas.org/doi/10.1073/pnas.2214840120 `Experimental`
- PAGE (Gao, Zhang & Li, 2022-11-03; IEEE ToG, DOI 10.1109/TG.2023.3275183): 98,525 games by 2,007 professional players over 70 years, with **per-move AI analysis attached** plus manually cleaned metadata — the template for "engine annotates expert decisions at scale, humans annotate a subsample". https://arxiv.org/abs/2211.01559 `Demonstrated` (dataset)
`Research-supported` (design analogue).

### 56. Poker: the strongest human-vs-AI evidence comes from long-horizon, incentivised play with variance reduction — not from expert opinion.

Brown & Sandholm, *Science*, 2019-07-11. 13 professionals (>$1M each) playing 10,000 hands against Pluribus in six-player no-limit hold'em (5 humans + 1 AI), plus two professionals each playing 5,000 hands against five Pluribus copies. **AIVAT** variance reduction; result +48 mbb/game (SE 25, one-tailed p=0.028) and +32 mbb/game (SE 15, p=0.014). Limitations as reported: changing table composition day to day; only two subjects in the reversed condition; poker variance too high to estimate individual win rates precisely; external validity limited to the tested format.
**Transferable lesson:** when the outcome is noisy, the honest design is many trials + explicit variance reduction + one-tailed pre-registered hypotheses — and the AI's *decisions* were never labelled good or bad by experts.
`Demonstrated`.
https://doi.org/10.1126/science.aay2400

### 57. Radiology reader studies (MRMC) supply the discipline's standard machinery, including the correct handling of an imperfect reference standard.

Factorial/fully-crossed MRMC: all readers read all cases under all conditions; prespecify a primary estimand (usually reader-averaged AUC or a clinically relevant partial AUC); randomise reading order and enforce washout; do **not** pool reader–case observations as if independent (it produces too-narrow CIs and too-small p-values); typically ≥5 readers, ~10+ for consequential/regulatory claims, with the number determined by **simulation** using plausible reader and case variance components rather than a rule. https://pubs.rsna.org/doi/10.1148/radiol.211593
When the reference standard is imperfect: prefer a blinded composite standard; never let the index test into the adjudication; if using a latent-class model, check identifiability and panel–modality conditional dependence; always run sensitivity analyses over plausible panel sensitivity/specificity; report per-reader effects and case difficulty strata. FDA statistical guidance explicitly allows for a reference standard that is absent, disputed or wrong in a non-negligible fraction of cases, and requires it be defined before the study. https://fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda
`Standard` (methodology).
https://pubs.rsna.org/doi/10.1148/radiol.211593 · https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda

### 58. Forensic latent-print examination is the cleanest demonstration that expert consensus is not ground truth: high accuracy on easy comparisons, low reproducibility on hard ones.

Ulery, Hicklin, Buscaglia & Roberts, PNAS 2011; and the 2012 follow-up on repeatability/reproducibility. 169 examiners, ~100 comparisons each. Overall false-positive rate 0.1% (5 of 169 examiners made any FP; no two made the same one) but false-negative rate **7.5%** (85% of examiners made at least one). With a ≥90% examiner-agreement criterion, agreement held for only 66% of latent-value decisions, 73% of mated-pair individualisation/exclusion decisions and **56%** of non-mated-pair decisions. On difficult comparisons, individualisation decisions were reproduced by other examiners ~55% (vs ~85% for easy/medium) and exclusions ~50% (vs ~77%). False-negative decisions were reproduced by another examiner only ~19.2%. 23% of decisions were "no value", and there is no objective accepted threshold for that judgement.
**Direct lesson:** expect our "hard rounds" (low-information, borderline calls) to have low expert reproducibility even with competent annotators, and size the annotation effort accordingly.
`Demonstrated`.
https://pmc.ncbi.nlm.nih.gov/articles/PMC3093498/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC3299696/

### 59. Human–AI combination does not reliably beat the better of human-alone or AI-alone.

Vaccaro, Almaatouq & Malone, 2024 (arXiv 2024-05-09). Meta-analysis of 106 experiments / 370 effect sizes (studies 2020–mid-2023). Combinations were on average better than humans alone (Hedges' g = 0.64) but **worse than the better of human-alone or AI-alone** (g = −0.23), with g = −0.27 for decision tasks specifically. Synergy was positive when humans alone outperformed AI (g = 0.46) and negative when AI alone outperformed humans (g = −0.54).
`Demonstrated` (meta-analytic).
https://arxiv.org/abs/2405.06087

### 60. AI-assisted clinicians do beat unassisted clinicians — but LLMs still generally do not beat clinicians in head-to-head pooled accuracy.

- Systematic review/meta-analysis, *JMIR* 2023 (48 studies, 25 pooled): clinician sensitivity 83% → 88% with deep-learning assistance; specificity 86% → 88%; heterogeneity very high (I² = 90.3% / 86.8%). https://www.jmir.org/2023//e43832/
- Skin cancer, *npj Digital Medicine* 2024 (12 studies, ~67,700 evaluations): sensitivity 74.8% → 81.1%, specificity 81.5% → 86.1%; largest gains for non-dermatologists; only 4 studies in clinical settings. https://www.nature.com/articles/s41746-024-01031-w
- LLM vs clinical professionals meta-analysis (2024): 30 studies, 4,762 cases; professionals higher in 20/30 studies, LLMs higher in 10/30; pooled analysis favoured professionals; I²=77%; high risk of bias. https://pmc.ncbi.nlm.nih.gov/articles/PMC12047852/
`Demonstrated`.
https://www.jmir.org/2023//e43832/

### 61. For our case, the available "reference standard" options, ranked by defensibility.

`Research-supported` (synthesis of §57–§60, §12, §25, §26):
1. **Behavioural criterion** where one exists (e.g. does the flagged mistake correlate with round loss / economic damage better than chance). Objective, but confounded by teammate play and variance — needs the poker/MRMC treatment (variance reduction, pre-registered hypotheses, per-case difficulty strata).
2. **Blinded expert panel with adjudication**, reported as a *distribution* (5/5, 3/5, 2/5+1 equivocal) rather than a majority label (§57), with expert–expert κ reported as the ceiling (§12) and hard-case reproducibility estimated (§58).
3. **Comparison against a weaker plausible decision** (what the player actually did vs the engine/tool-preferred line) as a *relative* judgment, which sidesteps the need for an absolute "correct" label and is closer to chess/Go practice (§54, §55).
4. **Absolute "was this optimal" labels** — least defensible for our player level; expect low expert agreement and a κ-paradox mess.

---

## 7. Ablations for a compound pipeline

### 62. A single-component ablation does not by itself license a causal claim; implementation-level choices can produce disjoint conclusions.

Huang, 2026-09-30. In GPT-2-small attention-head ablation, a natural post-projection implementation of "zero the head" was nearly uncorrelated with a corrected pre-projection ablation (Pearson r = 0.057) and selected a **completely disjoint top-5 set** of important heads. Binary accuracy hid effects at behavioural floors and near ceilings. What made the result defensible: a discovery/held-out split, **1,000 matched random-head and layer-matched-head control draws**, a non-saturated continuous metric (gold-token log-probability), effect ranking stable across splits (Spearman ρ = 0.974), top-5 exceeding both control distributions (Monte Carlo p = 0.001) — and a replication on a second model.
`Demonstrated` (in that setting) / `Research-supported` (generalisable caution).
https://arxiv.org/abs/2610.00373

### 63. The recurring evaluation failure modes across ML are catalogued in one place: inadequate baselines, implementation variation, finite test sets, metric misalignment, and badly computed human baselines.

Liao, Taori, Raji & Schmidt, "Are We Learning Yet?", NeurIPS 2021 Datasets & Benchmarks (meta-review of 107 survey papers). Notable specifics for us: implementations of the same algorithm can differ by factors; baselines are routinely under-tuned while proposed methods are tuned hard; >65% of sampled papers evaluated on ≤3 datasets and ≤2 metrics; human baselines are often computed from a single annotator and expert annotators agree more and detect more errors than novices (both directly relevant to §25/§58).
`Demonstrated` (meta-review).
https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/file/757b505cfd34c64c85ca5b5690ee5293-Paper-round2.pdf

### 64. Seed-only repetition is insufficient: data sampling usually dominates variance, and hyperparameter-search randomness is itself a variance source.

Bouthillier et al., MLSys 2021 (arXiv 2021-03-05). Benchmark results should be treated as random variables; data-sampling (bootstrap) variance generally exceeded initialisation variance (typically below half); running hyperparameter optimisation only once biases comparisons; randomising more sources of variation approached the ideal estimator while cutting compute ~51×. Recommend comparing *distributions* (e.g. probability that A beats B) rather than means.
`Demonstrated`.
https://arxiv.org/abs/2103.03098

### 65. Comparisons depend on the tuning budget consumed, and the ranking of two methods can flip with budget.

Dodge, Gururangan, Card, Schwartz & Smith, EMNLP-IJCNLP 2019. Propose plotting expected validation performance as a function of the number of trials; logistic regression beat a CNN at small budgets while the CNN won at larger budgets. In a survey of 50 EMNLP 2018 papers, **none** reported all of their recommended checklist items; ≤10% reported search bounds, trial counts, or measures of central tendency/variation. Replicating one reported BiDAF/SQuAD number took ~18 GPU-days ≈ 55 trials.
`Demonstrated`.
https://aclanthology.org/D19-1224/ · https://arxiv.org/abs/1909.03004

### 66. Classic deep-RL reproducibility work: reported improvements are frequently within run-to-run variance.

Henderson, Islam, Bachman, Pineau, Precup & Meger, AAAI 2018 (arXiv 2017-09-19, rev. 2019-01-30). Non-determinism in standard benchmark environments plus intrinsic method variance makes it hard to tell if improvements are meaningful; recommends significance metrics and standardised reporting.
`Demonstrated`.
https://arxiv.org/abs/1709.06560

### 67. A practical, general ML-pitfalls checklist exists and is worth adopting verbatim for the ablation work.

Lones, "Avoiding common machine learning pitfalls" (arXiv 2021-08-05, rev. v5). Covers data leakage, inappropriate baselines, wrong metrics, inadequate validation. https://arxiv.org/abs/2108.02497 — a journal version appears in *Patterns* (Cell Press) as a tutorial: https://www.sciencedirect.com/science/article/pii/S2666389924001880
Companion: "Hazards in Deep Learning Testing" (arXiv 2023-09-11) on the prevalence and impact of testing hazards. https://ar5iv.labs.arxiv.org/html/2309.05381
`Research-supported`.
https://arxiv.org/abs/2108.02497

### 68. **Design pattern for our component ablations.**

`Research-supported` (synthesis of §62–§67):
1. **State the target claim before running**: not "signal X helps" but a specific claim about a specific metric on a specific population. Unstated targets produce post-hoc narratives.
2. **Leave-one-out (full minus X) as the primary design**, forward-selection (empty plus X) as a secondary; a component that matters under leave-one-out but not under forward-selection (or vice versa) is interacting with something else, and that is the finding.
3. **Matched random controls.** For each ablation, run a matched control with the same number of removed inputs of the same type/shape (the §62 layer-matched/random-head precedent). Without it, "removing X hurts" is confounded by "removing any signal of that size hurts".
4. **Continuous, non-saturated metrics.** Avoid binary accuracy for ablation readouts when the pipeline sits near ceiling or floor (the §62 floor/ceiling finding); use graded scores (e.g. rank correlation with the human panel, mean absolute deviation) and report the metric's saturation status.
5. **Discovery/held-out split** for signal selection, plus a replication model or provider to test whether the ablation conclusion is model-specific (§62's replication step; §9 shows model identity is the dominant variance source).
6. **Repeat and report intervals.** Judge outputs are nondeterministic (§45, §48); every ablation cell needs ≥k repeats with the interval reported, and the comparison should be distributional (§64), not mean-vs-mean.
7. **Weak-baseline trap.** The most likely confound is that the "no-signal" baseline is an LLM with strong parametric CS2 priors, i.e. already competent (§31 shows prompted general models beat specialists on grounding detection). So the interesting ablation is not "full vs empty" but "full vs strong-LLM-without-our-signal" — and additionally vs. a simple non-LLM rule-based baseline (§63: adequately tuned simple baselines often match complex ones).
8. **Ceiling effect insurance.** If the compound pipeline already scores near the measured ceiling (e.g. near the expert–expert κ from §12), no component can show a gain; measure the headroom first.

---

## Metric status ledger

**Standard (adopt without argument, report as specified in the source):**

- κ / weighted κ / Fleiss' κ / Krippendorff's α as *agreement* measures, with CI + % agreement + category frequencies + table (or at least prevalence). §17–§22.
- ICC (absolute agreement vs consistency — state which) for continuous/ordinal scores; Bland–Altman for quantitative agreement. §20.
- MRMC machinery for reader-vs-system comparisons: fully crossed design, reader-averaged estimand, reader×case variance, no pooling of ratings. §57.
- pass^k for repeated-attempt reliability; risk–coverage curves for selective prediction. §14, §42.
- ECE/AUROC as *calibration* and *discrimination* measures, computed on a held-out set with CIs. §38, §41.
- Prompt-format and run-to-run intervals as a reporting requirement, not an appendix. §45–§49.

**Contested (use, but report the dispute and a sensitivity analysis):**

- The 0.61/0.80 κ band heuristics; "κ ≥ 0.6 is acceptable". §18, §19, §24.
- Choice among κ vs Gwet's AC1/AC2 vs PABAK; adjusted coefficients can overstate reliability. §23.
- Reference-free RAGAS-style faithfulness as evidence of grounding (it embeds a judge). §30.
- Hallucination leaderboards built on a single detector (HHEM). §34.
- Public hallucination/truthfulness benchmarks as discriminative in 2026 (saturation + contamination). §35, §52.
- "LLM judges match humans" as a general claim (true for general pairwise preference, false for expert/objective/long-horizon). §1, §11, §13, §14.

**Domain-specific (must be built and validated by us; no external standard exists):**

- What counts as a "mistake" in a CS2 round at ~2000 FACEIT level, and its severity scale.
- The grounding test: claim → demo-fact entailment, with negative controls. §37.
- The answerable/unanswerable partition for coaching questions (which rounds/decisions admit a defensible judgment at all). §43.
- The expert panel definition, case sampling and difficulty strata (§57, §58), including how to treat low-information rounds.
- The behavioural criterion (does the flagged mistake predict round loss beyond chance) and its variance-reduction scheme (§56).
- Ceiling: expert–expert agreement measured *on our own taxonomy*, which must be reported before any LLM number is interpreted. §12, §26.

---

## Contradictions / open questions

1. **Verbalized confidence: overconfident or well-calibrated?** Xiong et al. (ICLR 2024) find verbalized confidence clusters at 80–100% and is badly calibrated; Tian et al. (EMNLP 2023) find verbalized confidence *better* calibrated than token probabilities on three QA benchmarks, with ~50% relative ECE reduction. Both are credible; the reconciliation (task type, model generation, elicitation format, whether accuracy is near ceiling) is not settled. **Unresolved.**
2. **How good are judges on expert tasks, really?** §11 (64–68% agreement, worse for SME-specific aspects) vs §12 (κw 0.60 ≈ expert-expert 0.58) vs §15 (ICC 0.818 and κ 0.81 in medicine) vs §15 counterexample (ICC ≈ 0). The pattern *looks* like "operationalised rubric ⇒ usable; open-ended judgment ⇒ not", but that is our inference across studies, not a single controlled comparison.
3. **Is "expert panel" a gold standard at all?** §12 and §58 say plainly no. Yet §57's machinery still requires *some* reference standard, and §59 shows human+AI rarely beats the best of the two. There is no accepted way to score advice quality in an adversarially noisy team game; nobody in esports research has published one (the retrieved esports work covers *coding of visible events*, §25, not *judgment quality*).
4. **Score compression vs intra-rater noise in judges.** §9 documents systematic compression; §48 documents run-to-run inconsistency. Both can depress observed agreement; separating them requires a variance decomposition (between-item vs within-item) that most judge studies do not report.
5. **Does judged reliability survive one turn of context?** Judge benchmarks are almost all single-response or pairwise. Our coach produces a *sequence* of claims about one round and the player reads it as a whole. Long-horizon judge reliability is measured only indirectly, via agentic pass^k (§14). No study retrieved directly measures judge reliability on multi-claim, multi-turn expert critique.
6. **Contamination of the judge's parametric CS2 knowledge.** §31 warns that prompted factuality judges lean on parametric knowledge. For CS2 specifically, a strong model has likely seen pro strategies and HLTV numbers; we cannot cleanly separate "the judge knows CS2" from "the judge read our facts". Only a controlled perturbation study (facts altered while prose kept plausible) resolves this.
7. **What does "ablation" even mean when the judge is the same model that will be used to score the ablation?** If the same model family produces and grades (§4, §6), the ablation's effect size is contaminated. Requires either cross-family judging or blinded human grading on a subsample; neither is standard practice yet.
8. **Preview/nondeterministic endpoints make longitudinal coaching evaluation unstable.** §51 shows preview models can vanish in ~2 weeks; §50 shows silent behavioural drift. A coaching quality metric that assumes a stable endpoint is invalid; we would need to re-baseline on a schedule we control, and hold a frozen eval set precisely for that.

---

## Top sources

**Judges and their biases**

1. Zheng et al. — *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (2023-06-09). https://arxiv.org/abs/2306.05685
2. Shi et al. — *Judging the Judges: A Systematic Study of Position Bias* (v1 2024-06-12; v9 2025-11-11; AACL-IJCNLP 2025). https://arxiv.org/abs/2406.07791
3. Thakur et al. — *Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges*, GEM² 2025-07. https://aclanthology.org/2025.gem-1.33/
4. Szymanski et al. — *Limitations of the LLM-as-a-Judge Approach for Expert Knowledge Tasks*, IUI 2025. https://arxiv.org/abs/2410.20266
5. Kumar et al. — *When LLMs are reliable for judging empathic communication*, Nature MI (2026-02-11). https://www.nature.com/articles/s42256-025-01169-6
6. Vaugrante & Hagendorff — *How Much Do LLM-as-a-Judge Design Choices Matter?* (2026-10-04). https://arxiv.org/abs/2610.05094
7. Tan et al. — *JudgeBench* (2024-10-16). https://arxiv.org/abs/2410.12784
8. Li et al. — *Preference Leakage* (2025-02-03). https://arxiv.org/abs/2502.01534
9. Sharma et al. — *Towards Understanding Sycophancy* (2023-10-23). https://arxiv.org/abs/2310.13548
10. Cheng et al. — *Sycophantic AI Decreases Prosocial Intentions* (arXiv 2025-10-01; Science 2026-03-26). https://arxiv.org/abs/2510.01395
11. Dubois et al. — *Length-Controlled AlpacaEval* (2024-04-06). https://arxiv.org/abs/2404.04475
12. Wataoka et al. — *Self-Preference Bias in LLM-as-a-Judge* (2024-10-29). https://arxiv.org/abs/2410.21819

**Agreement statistics**

13. Landis & Koch (1977). https://pubmed.ncbi.nlm.nih.gov/843571/
14. Feinstein & Cicchetti — *High agreement but low kappa* (1990). https://pubmed.ncbi.nlm.nih.gov/2348207/
15. McHugh — *Interrater reliability: the kappa statistic* (2012). https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/
16. Donner & Eliasziw — κ inference and sample size (1992). https://onlinelibrary.wiley.com/doi/abs/10.1002/sim.4780111109
17. Krippendorff — α thresholds, sample-size table, CI caution. https://repository.upenn.edu/bitstreams/b6ea3a5b-3dee-4f27-a159-e44393eda7d4/download
18. *Interrater reliability estimators tested against true interrater reliabilities*, BMC Med Res Methodol 2022. https://link.springer.com/article/10.1186/s12874-022-01707-5
19. Novak et al. — *Performance analysis in esports, Part 1* (2019). https://research.rug.nl/en/publications/performance-analysis-in-esports-part-1-the-validity-and-reliabili/

**Grounding / hallucination**

20. Min et al. — *FActScore*, EMNLP 2023. https://aclanthology.org/2023.emnlp-main.741/
21. Gao et al. — *ALCE*, EMNLP 2023. https://arxiv.org/abs/2305.14627
22. Niu et al. — *RAGTruth* (2023-12-31). https://arxiv.org/abs/2401.00396
23. Ramprasad & Wallace — *Do Automatic Factuality Metrics Measure Factuality?* (2024-11-25). https://arxiv.org/abs/2411.16638
24. Emery et al. — *HalluMix* (2025-05-01). https://arxiv.org/abs/2505.00506
25. Vectara leaderboard criticism, GitHub issue #128 (2025-06-13, open). https://github.com/vectara/hallucination-leaderboard/issues/128
26. Bang et al. — *HalluLens* (2025-04-24). https://arxiv.org/abs/2504.17550

**Calibration / abstention**

27. Xiong et al. — *Can LLMs Express Their Uncertainty?*, ICLR 2024. https://proceedings.iclr.cc/paper_files/paper/2024/file/6733cf15e10e2cd1d59af033c3bb8507-Paper-Conference.pdf
28. Tian et al. — *Just Ask for Calibration*, EMNLP 2023. https://arxiv.org/abs/2305.14975
29. Kumar, Liang & Ma — *Verified Uncertainty Calibration*, NeurIPS 2019. https://arxiv.org/abs/1909.10155
30. Kirichenko et al. — *AbstentionBench* (2025-06-10). https://arxiv.org/abs/2506.09038
31. Geifman & El-Yaniv — *Selective Classification for Deep Neural Networks* (2017). https://arxiv.org/abs/1705.08500

**Reproducibility**

32. Atil et al. — *Non-Determinism of "Deterministic" LLM Settings* (2024-08-06). https://arxiv.org/abs/2408.04667
33. Haldar & Hockenmaier — *Rating Roulette*, Findings of EMNLP 2025. https://aclanthology.org/2025.findings-emnlp.1361/
34. Sclar et al. — *Prompt formatting sensitivity*, ICLR 2024. https://arxiv.org/abs/2310.11324
35. Chen, Zaharia & Zou — *How is ChatGPT's behavior changing over time?* (2023-07-18). https://arxiv.org/abs/2307.09009
36. Singh et al. — *Evaluation data contamination in LLMs* (2024-11-06). https://arxiv.org/abs/2411.03923
37. OpenAI API deprecations and notice periods (accessed 2026-10-15). https://developers.openai.com/api/docs/deprecations

**Other-domain designs and ablation practice**

38. McIlroy-Young et al. — *Aligning Superhuman AI with Human Behavior: Chess as a Model System*, KDD 2020. https://arxiv.org/abs/2006.01855
39. Gao, Zhang & Li — *PAGE: ProfessionAl Go annotation datasEt* (2022-11-03). https://arxiv.org/abs/2211.01559
40. Shin et al. — *Superhuman AI can improve human decision-making by increasing novelty*, PNAS 2023. https://www.pnas.org/doi/10.1073/pnas.2214840120
41. Brown & Sandholm — *Superhuman AI for multiplayer poker*, Science 2019-07-11. https://doi.org/10.1126/science.aay2400
42. *Multireader Diagnostic Accuracy Imaging Studies*, Radiology 2021. https://pubs.rsna.org/doi/10.1148/radiol.211593
43. Ulery et al. — fingerprint accuracy/reliability, PNAS 2011 + reproducibility follow-up 2012. https://pmc.ncbi.nlm.nih.gov/articles/PMC3093498/
44. Vaccaro, Almaatouq & Malone — human–AI combinations meta-analysis (2024). https://arxiv.org/abs/2405.06087
45. Huang — *When Do Attention-Head Ablations Support Causal Claims?* (2026-09-30). https://arxiv.org/abs/2610.00373
46. Liao, Taori, Raji & Schmidt — *Are We Learning Yet?*, NeurIPS 2021 D&B. https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/file/757b505cfd34c64c85ca5b5690ee5293-Paper-round2.pdf
47. Bouthillier et al. — *Accounting for Variance in ML Benchmarks*, MLSys 2021. https://arxiv.org/abs/2103.03098
48. Dodge et al. — *Show Your Work*, EMNLP 2019. https://aclanthology.org/D19-1224/

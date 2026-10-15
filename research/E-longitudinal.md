# §8 — Longitudinal behavioral analysis across dozens–hundreds of demos

Scope: single-player, local-first. Given N ≈ 50–500 of *one player's own* CS2 demos, find **recurrent,
situation-bound behavioral patterns**, separate "unusual" from "costly", quantify frequency / severity /
confidence, track trends, and produce **evidence-grounded** claims an AI coach can narrate without inventing causes.

This file is the design + literature slice. It deliberately defers two adjacent slices:
- field extraction, fog-of-war tiers (T0–T4), and anti-hindsight-bias enforcement → `research/C-data-fogofwar.md`
- API model choice, token cost, agentic tooling, representation compression → `research/F-ai-arch.md`

---

## Evidence grading used throughout

Same convention as `C-data-fogofwar.md`, so cross-file claims compose:

| Tag | Meaning |
| --- | --- |
| **Demonstrated** | Working, inspectable artefact (shipped code, product docs, published API) does this today. |
| **Experimental** | Code exists but is explicitly preview/beta or documented as unverified. |
| **Research-supported** | Peer-reviewed paper or first-party source establishes the mechanism. |
| **Plausible-untested** | Mechanism is documented but not confirmed end-to-end on real data here. **Verify locally.** |
| **Infeasible / not available** | No source path exists. |

Verification note for this file. Two kinds of citation appear:

- **✓ verified** — I read the primary source (abstract/docs/repo) in this session; claims are grounded in what it says.
- **◦ indexed** — located through the search index and consistent across sources, but I did **not** read the primary
  text. Treat numbers and details as **unverified**. Every ◦ is removable without changing the design.

No demo file and no personal history existed in this workspace, so **every number about "your" data is an
[INFERENCE] or a design parameter to be calibrated**, not a measurement.

---

## 0. Executive answer

| Layer | Recommendation | Status |
| --- | --- | --- |
| Situation encoding | **Model-based context adjustment, not cell partitioning.** Fit `P(outcome \| context)` over events; a "situation" is a *reporting slice*, not an estimation unit. Borrowed from xT/EPV and standardization/g-computation in sports & epidemiology. | Research-supported |
| Core signal | Per-event **residual** `observed − expected given context`, plus per-event **win-probability delta** (WPA) as severity. | Research-supported (CS:GO WPA paper ✓, THGNN ◦) |
| Small samples | **Hierarchical / empirical-Bayes partial pooling** + cluster-aware uncertainty (rounds are the cluster) + explicit abstention. | Research-supported |
| Multiplicity | **Permutation (Westfall–Young-style, block-preserving) for the mining search**, **BH-FDR per report cycle**, **online FDR (LORD/SAFFRON) or confidence sequences for continuous tracking**. | Research-supported |
| Unsupervised discovery | Cluster context–action–residual vectors (UMAP → HDBSCAN) **and** subgroup/exceptional-model mining over a constrained context grammar. Both must survive permutation control + holdout replication. | Research-supported (components) / Plausible-untested (as a system) |
| Trend / drift | PELT (`ruptures`) offline + BOCPD for online; **never** interpret a change point as "improvement" without the selection-bias guard (below). | Research-supported |
| Did the coaching work? | **Single-case experimental design (N-of-1)**: randomized/alternating treatment + randomization test + Tau-U. | Research-supported |
| Narration | **Claim-ledger architecture**: numbers are computed and injected by code; the LLM writes prose over a closed slot set; a deterministic verifier rejects unsupported numeric/relational claims; causal verbs are prohibited by schema. | Research-supported + engineering |
| Habit definition | Recurrent **and** consistent **and** consequential **and** context-bound. "Unconscious" is **not** inferable from demos — it requires a self-report channel. | [INFERENCE] |

**Hardest unsolved piece** (detail in §7): there is **no ground truth for "this is a habitual mistake"**. Severity
requires a *counterfactual* baseline (what a better player/decision would have done from the same information), which
is unidentifiable from one player's own observational history; and with no labels, detectors can only be validated by
expert review + prospective N-of-1 outcomes, not by accuracy. Everything else in this design is an engineering
problem with known tools.

---

## 1. Why this is not "pro-team analytics, smaller"

Professional-analytics literature assumes *population* data: many players, many matches, shared opponent pool,
external ratings, expert labels. The local, single-player case differs in four ways that change the method choice:

1. **n is small in the units that matter.** ~300 demos × ~22 rounds ≈ 6,600 rounds, but a *specific* situation
   (Mirage, CT, full-buy, 3v3, post-plant, A-site retake, no utility) may have n = 4. The number of situations a
   domain expert can *name* is in the hundreds; the number the data can *support* is a handful. This is the central
   statistical constraint of the whole slice.
2. **No reference population by default.** "You are bad at X" requires a comparison: your own past, your own other
   slices, or a peer population. Only the first two are guaranteed available offline.
3. **Selection is pervasive and self-referential.** Situations are not randomly assigned: economy, opponent choices,
   your own earlier decisions and your team's behavior determine which situations you face. Naive conditioning
   produces collider/mediator errors (see §6.3).
4. **The unit of analysis is nested and correlated**: event ⊂ round ⊂ half ⊂ match ⊂ session ⊂ patch period. Ignoring
   this inflates nominal n and understates uncertainty (design effect) — a classic multilabel/telemetry error.

Implication: the pipeline must be **model-first, slice-second**, with an explicit multiplicity budget and honest
abstention. A dashboard of 200 per-situation percentages is not analysis; it is a random-number generator with
formatting.

---

## 2. Methods survey

Grouped by the job each does. For each: what it is, evidence status, applicability here, and its documented limits.

### 2.1 Situation taxonomies and context conditioning

**Sports value models (the parent family).**
- **Expected Threat (xT)** — Karun Singh: a Markov grid model over pitch zones where a location's value = immediate
  shot value + expected value of continuing. Actions are valued by ΔxT. ✓ (blog read; see §9 sources) —
  **Research-supported / Demonstrated in football practice**. Direct analogue for CS: value of a *position/state*, not
  of a kill count.
- **VAEP / EPV / possession-value models** — generalise to action-type value and full-state value using tracking data
  (combination of positional control, pressure, available options). ◦ indexed (PMC review `PMC8570314`) —
  **Research-supported**. This is the conceptual ancestor of "value the decision, not the outcome".
- Documented limits of the family (important for CS): location-only models miss defenders/teammates/risk; they do not
  capture defensive value or the danger created by losing the ball; values are population- and definition-dependent
  (grid size, provider, league). These limits transfer verbatim to CS: a zone-only "threat map" will be wrong.

**CS-specific value/context models.**
- **WPA for CS:GO** — Xenopoulos, Doraiswamy, Silva (2020) ✓ abstract: open-source data model + graph distance +
  context-aware action valuation via `Δ P(win)` using >70M events; logistic regression / CatBoost / XGBoost.
  **Demonstrated**. The canonical formulation:
  `WPA(a) = P(win | state_after(a)) − P(win | state_before(a))`.
- **Temporal Heterogeneous GNN on CS2** — Szmida & Toka, MIT Sloan Sports Analytics 2025 ◦ indexed (no arXiv copy;
  ResearchGate + conference page; BME department page corroborates). 114 pro matches, Inferno only, ~4 snapshots/s,
  >76% round-outcome accuracy, Shapley attribution of win-prob changes to actions. **Research-supported, single-map,
  pro-only.** Notable: they cluster kill/death locations to define "contact spots" — a directly reusable idea.
- **THGNN/MLMove caution**: both are trained on *professional* data. A 2000-Elo player's situations are drawn from a
  different distribution; a model trained on tier-1 CS2 will produce miscalibrated `P(win)` for FACEIT pugs. Any
  value model must be **calibrated on data from the player's own population** or at minimum recalibrated (§4.3).

**Context-adjusted evaluation in esports** — the "observed − expected given context" recipe: estimate expected
performance at the *event* level from opponent/state/role/map/resources, then average residuals. Key cautions from the
sports-analytics literature: do not include opponent strength twice; adjust at event level not season level; do not
confuse role differences with skill; and note that players do not face random situations — strong players may receive
harder assignments (selection). ◦ indexed (sports-analytics + CJAS opponent-adjustment writing) —
**Research-supported**.

**Prior art on habit-ish outputs (commercial).** Leetify publishes Aim / Utility / Positioning ratings, "crosshair
placement", "time to damage", traded-death %, enemies-flashed, plus a **Post-Match Journal** correlating self-reported
states with win rate; it explicitly warns that journal correlations need dozens–hundreds of entries; and it
**re-benchmarked ratings** (Aug 2025) so historical comparisons break across benchmark versions. ✓ (product blog read)
— **Demonstrated product**. Scope.gg / CStrike.gg / MyCS expose "habits"/mistakes/drills ◦ indexed —
**Demonstrated product, unvalidated methodology** (no published validation of detector precision/recall found).

**Design consequence:** adopt the residual/Δvalue backbone, but assume **no external peer benchmark is trustworthy**;
make "compared to what" an explicit, swappable object (own history / own other slices / imported population model).

### 2.2 Player fingerprints, embeddings, behavioral clustering

| Work | Method | Status |
| --- | --- | --- |
| Normoyle & Jensen 2015 (AIIDE) | Bayesian nonparametric clustering of playstyles, no fixed k, hybrid styles; Battlefield 3, 1.2k players / 500k matches ◦ indexed | Research-supported |
| Ingram et al. 2022 | LSTM autoencoder → cluster **variable-length behavioral trajectories**; works on partial trajectories ◦ indexed | Research-supported |
| "Embedding LoL player styles for clustering & outlier detection" (CVUT) | LSTM-AE + clustering + outlier detection ◦ indexed | Research-supported |
| Drachen/telemetry line ("Like a DNA string", sequence profiling; HMM player classification) ◦ indexed | Sequence-based profiling, precedent for "fingerprint = behavior sequence" | Research-supported |
| **Zimmer et al., HICSS-58 (2025)** ✓ page read | Binary Random Forest separates **within-pair** identities from in-game behavior; 119 CS:GO tournament matches; up to 87% test accuracy; contribution = behavioral features that uniquely identify players | Research-supported, but see caveats |
| Kuzhii & Furgala 2025 ◦ indexed | CS2 role assessment feature engineering (entry/lurk/support/AWP/anchor/IGL); PCA + ANOVA show roles occupy separable regions; roles not reducible to one rating | Research-supported |
| Fitsner 2025 (UVic) ◦ indexed | GMM on spatial CS features → ~4 playstyles per side; playstyle/round style mattered more than map | Experimental (student project) |
| `sachiniiits/btp_cs2` ◦ indexed | Per-side Self-Organizing Maps for CS2 role discovery, 76 pro maps, leakage-free test | Experimental (thesis repo) |
| Ingram/"unsupervised playstyle metric via state discretization" (PMLR v161) ◦ indexed | Discrete latent state abstraction rather than hand-made style features | Research-supported |

**What this buys and what it does not.** Fingerprints are useful for (a) *identity/consistency* checks (are my last
50 matches the same player?), (b) drift detection, (c) clustering my own matches into "modes" (tilted/rusty/warmed-up
sessions, aggressive/passive phases). They are **not** a weakness detector: a cluster is a description of *what you
do*, not *whether it costs you rounds*.

**Caveats that must be carried forward:**
- *Pairwise identification ≠ identification.* 87% on distinguishing **two** players ◦/✓ does not imply fine-grained
  uniqueness among many; the baseline ceiling for a 2-way task is 50%. This is a weak benchmark for "fingerprint
  quality" and should not be quoted as if it were multi-class accuracy.
- *Style vs skill vs role vs patch confounding.* Clustering raw K/D/damage/win-rate recovers performance, not style —
  stated explicitly in the playstyle-clustering literature ◦ indexed.
- *Embedding distances are not clinical instruments.* UMAP distorts density and can create false separations; the
  UMAP docs recommend clustering on 5–20 dims, not 2-D, and checking stability across `random_state`, `n_neighbors`,
  `min_dist`, `min_cluster_size`. ✓ docs read — **Demonstrated tool, with documented failure modes.**
- *Cluster stability is a prerequisite, not a nicety.* Use consensus/cluster-wise bootstrap stability assessment
  (`fpc::clusterboot`; Hennig's cluster-wise stability; consensus clustering) ◦ indexed — **Research-supported** — and
  discard clusters that do not survive resampling.

### 2.3 Sequence and pattern mining

- **Sequential pattern mining** (PrefixSpan, pattern-growth) ◦ indexed; **extended PrefixSpan** applied to a
  game-based learning environment ◦ indexed; **"Sequential Analysis of Player Behavior"** (CHI PLAY 2015) ◦ indexed;
  RTS e-sport strategic pattern discovery with SPM (CEUR) ◦ indexed; frequent-pattern mining of RPG actions for
  individual differences (AIIDE) ◦ indexed; **contrast motif discovery** in Minecraft (AIIDE) ◦ indexed.
  → **Research-supported**: mining repeating action sequences over a **discretized context grammar** is a mature,
  directly reusable technique. "Contrast motif" is exactly the shape we want: a motif that distinguishes one player's
  behavior from another's.
- **Process mining** (`pm4py`, conformance checking) — plausible for round "protocols" (execute → plant → post-plant),
  but ◦ not verified here; mark **Plausible-untested**.
- **Exceptional Model Mining / subgroup discovery with statistical control** — Leman et al. (ECML PKDD 2008) ◦;
  recent scalable significant subgroup discovery (ScienceDirect 2023) ◦; **permutation strategies for mining
  significant sequential patterns** (Univ. Padova) ◦.
  → **Research-supported and load-bearing**: this is the correct formalisation of "find the situation subsets where my
  behavior is exceptional", *with* the multiplicity correction built in. Westfall–Young permutation controls **FWER**
  over the whole search space (not FDR — that distinction is frequently botched in applied papers).
- **LAMP** (Terada et al., FWER control for pattern mining via the "minimum attainable p-value" trick) ◦ indexed —
  **Research-supported**; useful for pruning so a large grammar stays computable.

### 2.4 Anomaly detection

- **Matrix profile / STUMPY**: per-subsequence nearest-neighbour distance → minima = motifs, maxima = **discords**
  ✓ docs read. Key operational points: `m` (window) must match the duration of the behaviour of interest; one
  discord can produce many overlapping windows → need an exclusion zone; discords are **candidate anomalies**, to be
  confirmed with domain rules or human review; z-normalised by default (shape, not level).
- **Contextual anomaly detection** — the concept that matters here ("unusual *given* context", not "extreme value").
  The classic formulation is well established; for our purposes the practical version is: anomaly = low density in
  *context-conditioned* feature space, not a high raw value.
- **Isolation Forest / LOF / autoencoder reconstruction error** — standard, **Demonstrated** libraries; each has
  known failure modes under high dimensionality and correlated features (distance concentration), and none of them
  tells you whether an anomaly is *bad*.
- **OOD/novelty framing** — useful for "have I encountered this situation before?" (gating whether a situation is
  even reportable), which is the *right* use of novelty detection in this system.

### 2.5 Spatial / trajectory analysis

- **TRACLUS** (Lee, Han, Whang, SIGMOD 2007) — partition-and-group trajectory clustering; finds **common
  sub-trajectories** with a perpendicular/parallel/angular segment distance; produces representative paths.
  ✓ (paper + reference implementation located) — **Research-supported**.
- **Fréchet distance** (Alt & Godau) — path-shape similarity, timing-insensitive; **DTW** — timing-aware alignment
  (use Sakoe–Chiba band constraints to avoid degenerate warping) ◦ indexed — **Research-supported**.
- **Learned movement model / dataset**: Durst et al. 2024 ✓ (arXiv 2408.13934, SCA 2024): **123 h** of professional
  CS:GO traces, transformer movement controller (MLMove), <0.5 ms/step inference on one CPU core for all players;
  evaluates map occupancy distributions against humans with **Earth Mover's Distance**; dataset **CSKnow** (~16 Hz
  positions, 17k+ rounds, 2,292 players) ◦. Restriction: **Retakes on Dust II**. **Demonstrated**.
- **Occupancy / heat-map comparison** (EMD between a player's zone occupancy histogram and a reference) is the
  cheapest, most robust spatial-normalisation primitive: it produces one number per (map, side, phase, zone) and is
  immune to the "which exact pixel" problem.
- **Spatial control fields** — a Gaussian influence field per player, differenced between teams, gives a
  "territory advantage" integral ◦ indexed (derived from the above papers). **Plausible-untested** in CS2 without a
  nav-mesh-aware distance; treat as a research direction, not a v1 metric.

### 2.6 Situation-conditioned comparison, normalisation, standardisation

- **Direct standardisation / post-stratification / IPTW / g-computation** ◦ indexed (multiple epidemiology +
  causal-inference primers, `PMC12009273`, `PMC2652882`, `PMC5466356`) — **Research-supported**.
  The point that transfers directly: when you compare "my rate in situation A vs B", the comparison is confounded by
  *composition* (map mix, buy mix, opponent mix, teammate mix). Fix by reweighting to a **fixed target composition**
  (e.g., "your last 200 rounds' composition" or "an equal-weight composition"), not by eyeballing two percentages.
  Also: check positivity/overlap — if a slice has ~0 support for one arm, no adjustment can rescue it.
- **Simpson's-paradox risk is structural here**: e.g. lower retake win rate may be entirely explained by retakes
  occurring after loss-bonus rounds against a stronger opponent.
- **Effective sample size / design effect** — with clustered events (kills within rounds), `n_eff ≈ n / (1+(m̄−1)ρ)`
  ◦ standard; must be computed and reported, or every CI is a lie.

### 2.7 Change-point and drift detection

- **`ruptures` / PELT** — offline penalised segmentation; `pen` controls the number of changes; `min_size` prevents
  implausible short segments ✓ docs read. **Demonstrated.**
- **BOCPD** (Adams & MacKay 2007, arXiv 0710.3742) — online run-length posterior; hazard prior encodes expected
  segment length and dominates behaviour when wrong; needs truncation for practicality ✓ (library docs read).
- **CUSUM / SPRT** — the classical fast-detect primitives; still the right tool for "alert me within k matches".
- **Documented cautions, all applicable**: autocorrelated series cause **over-detection** under independence
  assumptions; `l2` detects level shifts only (not volatility); scale features or one dominates; and **evaluate
  false-alarm rate separately from detection delay**.
- **Multiplicity across many monitored metrics** is the killer in practice. 40 tracked metrics × weekly look = the
  same "garden of forking paths" problem as in §2.8 — fixed by confidence sequences / online FDR, or by reporting
  change points only when they survive a *preregistered* look schedule.

### 2.8 Multiplicity, false discovery, and honest exploration

- **Benjamini–Hochberg FDR** (1995) ✓ — expected *proportion* of false discoveries among reported. Applies to a
  defined family; does **not** rescue analyst flexibility.
- **Westfall–Young permutation** ✓ — max-statistic null over the *entire search*, dependence-aware, controls FWER.
  Correct choice for "I enumerated 40,000 context-pattern hypotheses".
- **Selective / post-selection inference** (Taylor & Tibshirani line; `PMC4485109`) ◦ — valid inference after a known
  selection algorithm; hard for arbitrary interactive exploration, but tractable for a fixed enumerator.
- **Data splitting / holdout replication** — the robust escape hatch: discover on matches 1..K, confirm on K+1..N.
  Cheap, and the only guard a solo developer can actually audit.
- **Online FDR** — alpha-investing → **LORD** (arXiv 1502.06197) → **SAFFRON** (ICML 2018) ✓: allow unbounded,
  adaptively-ordered hypothesis streams with FDR control; caution: guarantees assume independence/local dependence,
  and **temporal dependence breaks them** unless a dependence-aware variant is used (arXiv 2110.08161).
- **Always-valid / anytime-valid inference** — **e-values, test (super)martingales, confidence sequences,
  always-valid p-values** (Howard, Ramdas, McAuliffe, Sekhon; Ville's inequality; arXiv 1810.08240) ✓ — this is the
  *correct* tool for "I will keep looking at my stats every week". A fixed-sample p-value cannot be monitored; a
  confidence sequence can, with a guarantee that holds over the whole path, including optional stopping.
- **"Garden of forking paths"** (Gelman & Loken) ✓ and **False-Positive Psychology** (Simmons/Nelson/Simonsohn 2011)
  ✓ — analytical flexibility alone inflates significance without any conscious fishing. In this project the freedom
  is enormous (which maps, which economy buckets, which time windows, which outcome definition), so the guard must be
  structural: freeze analysis definitions *before* they touch the newest data block.
- **Selection bias in streaks (Miller & Sanjurjo, Econometrica 2018)** ✓ — the naive "percentage after a streak"
  estimator is biased downward because of conditioning on a data-dependent set of observations; permutation
  reproducing the *same selection process* is the fix. This is the single best cautionary tale for this project:
  a decade of literature concluded "no hot hand" from an estimator that was selection-biased. Our "you always lose
  these" detector is structurally similar (we select sequences that end badly), so **block-permutation nulls that
  reproduce the selection rule are mandatory**, not optional.

### 2.9 Temporal / latent-state modelling

- **HMMs and variants for player behaviour** — MMOG player classification with HMMs; "Modeling Individual
  Differences in Game Behavior Using HMM" (AIIDE); player profiling with HMM + sliding window ◦ indexed —
  **Research-supported**. Semi-Markov / HSMM is the right refinement because round phases have dwell times.
- **Topic models over action sequences** (LDA over discretised actions) — plausible; ◦ not verified for FPS.
  **Plausible-untested.**
- **Knowledge tracing (the closest true analogue: per-skill mastery over time)**
  - BKT / PFA / DKT lineage ◦ indexed; **NeuralCD** (AAAI 2020 / TKDE 2023) and cognitive-diagnosis models give a
    per-skill mastery vector with a *slip/guess* structure — conceptually identical to "which sub-skill is weak".
  - **Critical limitation, verified** ✓ (Xiong et al., EDM 2016 "Going Deeper with DKT"): DKT's advantage shrank
    dramatically after de-duplicating rows and fixing multi-skill expansion (AUC ≈ .81 → .74 on affected data);
    a **structured logistic model (PFA)** was competitive. Practical lesson for us: **do not reach for a sequence
    neural net before a well-featured regularised logistic/multilevel model has been beaten on held-out data.**
    Also: AUC ≠ calibration; student-level CV does not fix temporal leakage; single-metric evaluation is inadequate.
- **Latent growth / mixed-effects models for longitudinal skill** — linear mixed-effects models are the standard
  tool for individual developmental trajectories in sports science (e.g. longitudinal sprint-performance work in
  *Frontiers in Sports and Active Living*, 2024) ◦ indexed — **Research-supported**. Random intercept + random slope
  per skill, fixed effects for patch/session, is the honest "am I trending?" model.
- **Esports-specific rating systems with Bayesian updating**: **PandaSkill** ✓ (arXiv 2501.10049): per-role ML
  performance scores → **OpenSkill** Bayesian update in a free-for-all setting using performance rather than match
  outcomes; dual regional/meta rating to fix isolated pools. **Demonstrated on 5 years of LoL.** And CS-specific:
  **Plus/Minus Bayesian/regularised-regression ratings** ✓ (arXiv 2409.05052) — argues individual-only ratings
  (Rating 2.0) miss indirect contribution. Both are directly reusable *shapes*: per-role normalisation + Bayesian
  update + shrinkage.

### 2.10 N-of-1: evaluating interventions on one player

This is the only defensible answer to "did the coaching work?", and it has a mature literature:
- Randomized single-case designs, **randomization tests**, **Tau-U**, multiple-baseline and alternating-treatment
  designs; effect indices for level/trend/variability/overlap/immediacy/consistency; Monte Carlo work on
  within-case variability; `nof1sced.org` analysis resources; `SingleCaseES`-family R packages ◦ indexed —
  **Research-supported**.
- Also relevant: **athlete-monitoring methodology critiques** ◦ indexed — z-score/rolling-average monitoring and the
  acute:chronic workload ratio concept have published, sharp methodological criticisms (scaling artefacts, arbitrary
  normalisation, non-independence, no validation). The general lesson: **ratio-of-windows metrics look scientific and
  have repeatedly failed validation**; prefer explicit mixed models over ad-hoc ratios. **Do not build "habit risk
  score = 7-day / 28-day".**

### 2.11 Grounding the narration (LLM side)

- **LLMs are measurably weak at the exact tasks this system needs.** Internal consistency of citing verified
  benchmarks:
  - **StatQA** (NeurIPS 2024 D&B) ◦: 11,623 statistical-analysis examples; best model ≈ 64.8%; dominant error class =
    **applicability errors** (choosing a method whose assumptions don't fit) — i.e. numerically coherent but invalid.
  - **QRData** (arXiv 2402.17644) ◦: data-based statistical + causal questions; GPT-4 ≈ 58%; strongest open model
    ≈ 37%; models fail to combine statistical knowledge with the supplied data.
  - **CausalPitfalls** (ICLR 2026) ◦: benchmarks statistical pitfalls in causal inference (correlation→causation,
    collider/mediator confusion); evaluates code-assisted analysis too.
  - **FermiEval** (arXiv 2510.26995) ◦: nominal 99% intervals covered truth only ~65% of the time; conformal
    calibration improved coverage — i.e. **LLM-stated uncertainty is not calibrated**.
- **Hallucination/grounding benchmarks**: FaithEval (ICLR 2025) — unanswerable/inconsistent/counterfactual contexts ◦;
  FaithBench (NAACL 2025) — best automatic detectors near 50% accuracy on hard cases ◦; **CiteGuard** (arXiv
  2510.17853) — citation-attribution validation, ≈65.4% vs ≈69.7% human on CiteME ◦; **TabFaith** (ACL 2026) —
  cell-level structural faithfulness; distinct failure modes = numeric substitution, entity–value misbinding,
  column/unit confusion, temporal conflation, fabricated rankings ◦; "When LLMs Read Tables Carelessly" (ACL 2026) —
  data-referencing errors improve with critic filtering ◦.
- **Faithfulness ≠ factual grounding.** A model can be fluent, cite a real source, and still have the source not
  entail the claim. Several distinct properties are usually conflated: explanation faithfulness, prediction–
  explanation consistency, contextual groundedness, RAG faithfulness, citation correctness, citation attribution.
- **Consequence for this design:** never let the model *produce* a statistic. Compute → verify → render.

---

## 3. Design: situation taxonomy, normalisation, scoring

### 3.1 The central design decision: model-first, slice-second

Do **not** enumerate the cross-product of context dimensions and compute per-cell rates. Reasons:

1. Combinatorial explosion: 10 dimensions × ~5 levels ≈ 10⁷ cells against ~10⁴ usable events.
2. Selection/confounding: cells are not exchangeable; a naive per-cell comparison is a minimisation of confounding.
3. Multiplicity: 10⁷ cells means the largest deviation is noise, by construction.

Instead:

```
For each event e:      observed outcome y_e, action a_e, context vector x_e, player p
Fit:                   P(y | x, φ)     ← event-level model, fitted across all your events
Residual:              r_e = y_e − ŷ_e
Severity:              w_e = ΔWPA_e     ← change in own-team win probability caused by the action
```
A **situation** is then a *predicate over x* used only for **aggregation and reporting** (`s = 1[x ∈ S_s]`), and the
statistic reported for slice `s` is a weighted average of per-event residuals/values with cluster-robust uncertainty —
i.e. **g-computation / direct standardisation**: predict under the observed action and average over a fixed target
composition. This is the same recipe that makes xT/EPV and modern player ratings robust, and it is the only one that
survives n ≈ 10⁴.

Tag every slice with the **target composition** used to standardise it. When composition changes (you played more
Mirage this month), the standardised number is unaffected — that is the point.

### 3.2 Situation taxonomy (CS2, single player)

Two groups: **situation context** `x` (where/when/what resources) and **information state** `i` (what you could have
known). The second is non-negotiable for decision quality — flagship §C.11 defines T0 `omniscient` … T4 `unknown`.
A decision judged against T0 is hindsight bias, not coaching.

| # | Dimension | Levels (proposed) | Why it matters | Min support guidance |
| --- | --- | --- | --- | --- |
| 1 | map | `de_*` (only maps with ≥ K matches) | dominant variance source | ≥ 10 matches |
| 2 | side | T / CT | different objectives, different value model | ≥ 20 rounds |
| 3 | round liquidity | freeze / early (0–20 s) / mid (20–60 s) / late (60 s–bomb) / post-plant | decision types differ entirely | ≥ 20 rounds |
| 4 | buy class | pistol / eco / force / full / AWP-heavy | weapon asymmetry is a confounder, not a skill test | ≥ 20 rounds |
| 5 | man-advantage | +2, +1, 0, −1, −2 (alive diff at decision time) | value of a kill flips with numbers | ≥ 20 rounds |
| 6 | bomb state | carried / planted / defusing / defused | changes objective value | ≥ 20 rounds |
| 7 | zone | map-specific named areas (from a checked-in zone config) + coarse site/route groups | locality of habits | ≥ 20 events |
| 8 | role | declared or inferred (entry / AWP / lurker / anchor / support / IGL) | role-relative comparison is mandatory | ≥ 10 matches |
| 9 | teammate geometry | nearest-teammate distance bucket; trade-available yes/no | solo vs supported duels are different games | ≥ 20 events |
| 10 | opponent strength | own-history-derived opponent rating bucket (see §3.4) | the strongest observed confounder | ≥ 15 matches per bucket |
| 11 | weapon class | rifle / sniper / SMG / pistol / shotgun | mechanical fairness | ≥ 20 events |
| 12 | **information tier** | `T1 confirmed` / `T2 inferable` / `T3 relayed` / `T1∖noticed` (available-but-unnoticed) / `T4 unknown` | separates "misjudged" from "didn't know" | per-slice, ≥ 15 events |
| 13 | session context | match index in session, hours-since-first-match, hours-since-last-session | fatigue/rust proxies; **not** psychological claims | ≥ 10 sessions |
| 14 | patch / game version | version id (awpy can pin it ✓) | drift + model recalibration trigger | — |

**Do not include** "tilt", "confidence", "concentration", "motivation". No demo-derivable measurement supports them;
inventing them is exactly the confabulation failure this design exists to prevent. If the user supplies self-report
(Leetify-journal style ✓), it becomes an *annotation stream* to be correlated — with its own multiplicity control and
the journal's own caveat that dozens–hundreds of entries are needed.

### 3.3 Normalisation rules

1. **Map**: never pool maps in a reported number unless the composition is standardised; each map slice gets its own
   partial-pooled estimate, and the pooled estimate is a *weighted average over the target composition*.
2. **Side**: T and CT are separate populations. Pooling requires the value model, not the counting.
3. **Role**: per-role normalisation is explicitly recommended in esports rating work (PandaSkill models each role
   independently ✓). A lurker's trade-kill rate is not an anchor's.
4. **Economy**: always report buy-class as a *stratum*, and standardise over buy-class composition. "Won more duels"
   after a month of full-buys is an economy artefact.
5. **Opponent strength**: derive from own history + available ratings (FACEIT Elo at match time; team-average Elo;
   per-player rating where available). Prefer *including it in the expected-performance model* over multiplying a
   strength-of-schedule factor afterwards. Never compute it from the same statistic you are adjusting (circularity).
6. **Patch / version**: version is a **hard stratification key** for any trend claim; a balance patch invalidates
   cross-patch comparisons of specific mechanics unless the model is re-fit.
7. **Teammates**: treat teammate lineup as a random effect where repeated lineups exist; for solo queue, at minimum
   record a teammate-rating bucket, since a weak teammate changes your opportunity set (selection).
8. **Time-of-round**: normalise distance/rotation metrics by remaining round time; raw "time to rotate" is confounded
   by round tempo, which is opponent-determined.
9. **Spatial**: normalise to **zone occupancy histograms** (compare with EMD) rather than raw coordinates; raw
   coordinate comparisons are dominated by spawn/route variance.

### 3.4 Scoring: frequency × severity × confidence

For a candidate pattern/predicate `s`:

- **Frequency (rate, not count)**
  `f_s = E_s / O_s` where `E_s` = #events matching the pattern, `O_s` = #**opportunities** (the denominator that
  makes it comparable — e.g. site entries attempted, not rounds played).
  Also report `e_s = E_s / R_s` (per-round incidence) since round-impact aggregates use it.
- **Severity (context-adjusted value)**
  `S_s = mean_{e ∈ s}( v_e / 100 )` where `v_e` is the per-event win-probability cost of the behaviour, expressed as
  *percentage points on the round-win probability scale* from the calibrated value model. Sign convention:
  positive `S_s` = harmful. For mechanical events without clean `ΔP(win)`, use the residual formulation
  `S_s = mean(y_e − ŷ_e)` in the direction of harm (e.g. lost duel where `ŷ` was 0.5).
- **Expected loss per 100 rounds** (the ranking quantity)
  `EL_s = 100 · e_s · S_s` — interpretable as "this habit costs you ≈X rounds per 100 rounds".
- **Confidence**
  `C_s = P(EL_s > δ | data)` — the posterior probability that the effect exceeds a **practical** threshold δ
  (proposal: δ = 0.5 rounds / 100 rounds ≈ noise floor). Report `C_s`, the posterior median, and the 90% credible
  interval; never a bare point estimate.
  A/B/C tiers (report / hypothesis-only / watchlist, §3.5) are gated on `C_s`, `n`, and the number of matches the
  evidence spans.
- **Coverage caveat**: none of these measures "how often you could have done better" without a counterfactual
  (see §7). Severity here is *realised* cost, not *avoidable* cost. Never word the output as "you lost X rounds
  because of this".

### 3.5 Small-sample guards (all mandatory)

| Guard | Rule (calibrate later) |
| --- | --- |
| Opportunity floor | report only if `O_s ≥ 30` **and** `E_s ≥ 15` **and** events span ≥ 8 matches |
| Mid tier | `O_s ∈ [10,30)` → "hypothesis / exploratory", labelled as such, excluded from rankings |
| Watchlist | `O_s < 10` → aggregate only, never individually narrated |
| Partial pooling | every slice estimate is shrunk toward a higher-level (player-mean or role-population) prior; report **both** raw and shrunk values; `shrink ≈ O_s/(O_s + k)` with `k` estimated empirically |
| Cluster-aware uncertainty | model rounds as the cluster (multilevel or cluster-robust SE); report `n_eff` = `n / (1 + (m̄−1)ρ)` explicitly |
| Abstention | if the posterior interval overlaps the ROPE, output "insufficient evidence" — **not** a direction |
| Composition report | every comparison states its target composition and the standardisation method |
| Overlap/positivity | if a slice has near-zero support in one comparison arm, flag it and refuse the adjustment |
| Patch boundary | cross-patch comparisons require an explicit "not comparable across patches" label |
| Selection guard | for streak-based detections, use a permutation null that reproduces the selection rule (Miller–Sanjurjo ✓) |

---

## 4. Unsupervised discovery: surfacing unknown weaknesses

### 4.1 The four detection channels (different jobs, different nulls)

| Channel | Finds | Method | Null / guard |
| --- | --- | --- | --- |
| **D1 Predefined detectors** | known failure modes (untraded deaths, dry entries, wasted utility) | hand-written predicates over canonical events | BH-FDR over the fixed detector family |
| **D2 Residual clustering** | *unknown* recurring signatures: contexts where you systematically underperform | context+action+residual vector → UMAP(5–20d) → HDBSCAN; tag clusters by their dominant context features; keep only clusters with bootstrap stability | permutation: shuffle residuals within round-clusters (preserves nesting), recompute cluster-level effect |
| **D3 Subgroup / exceptional-model mining** | interpretable context *predicates* where the model is exceptional | EMM/SD over the taxonomy grammar (bounded depth, min support) with WY permutation over the whole enumeration; LAMP-style pruning for scale | Westfall–Young max-statistic (FWER) over the enumerated space — **the only defensible control when you searched 10⁴ predicates** |
| **D4 Series anomalies & drift** | rare configurations; changes over time | matrix profile discords on per-session aggregates; PELT/BOCPD/CUSUM on per-metric series | exclusion zones for overlapping discords; autocorrelation-aware (block) nulls; online FDR / confidence sequences for weekly monitoring |

**Amplifier channel (D5): external reference.** If a reference population exists (imported pro demos, or pooled
statistics published by a platform), compute the *same* residual definition for the reference and compare
distributions. This converts "you are unusual" into "you are unusual *relative to a reference*", which is what
players actually mean. It is optional and must be versioned (Leetify's Aug-2025 re-benchmark shows why: peer
benchmarks silently change).

### 4.2 What counts as a habit (definition)

A candidate is promoted to "habit" only if **all four** hold:

1. **Recurrent** — appears in ≥ K distinct matches (K ≈ 8, calibrated) and in more than one session.
2. **Consistent** — sign and rough magnitude stable across ≥ 2 disjoint data splits (split-half or discovery/holdout).
3. **Consequential** — `EL_s > δ` with posterior confidence `C_s ≥ 0.95` **after** multiplicity control.
4. **Context-bound** — the effect is *conditional*: not explained by a global (context-free) deficit. Test by
   comparing against the player's own context-free rate; if conditioning adds nothing, report it as a global skill
   statement, not a habit.

**"Unconscious" is not measurable from demos.** Demos can show *unreported*, not *unconscious*. The operational
substitute: collect a self-report channel (short post-match journal, or a one-time self-assessment per skill) and
define the interesting set as **detected ∧ not-self-reported** (and, symmetrically, **self-reported ∧ not-detected**,
which is its own coaching insight). Any wording like "you subconsciously…" must be blocked in the renderer.

### 4.3 Unusual vs bad — the two-axis map

Two independent questions, two independent models:

- **Unusual?** → *novelty*, measured against **your own** behavior distribution (density/mahalanobis in context-action
  space; matrix-profile discord; change point). Model A = behaviour model, no outcomes.
- **Bad?** → *cost*, measured against **outcomes** relative to context expectation (residual/`ΔWPA`). Model B = value
  model, outcomes only.

Then:

| | **Low cost** | **High cost** |
| --- | --- | --- |
| **Unusual** | *Signature* — this is your identity/style. **Do not "fix" it.** Report as insight, not weakness. | *Priority habit* — recurrent, costly, not you normally. Top of the list. |
| **Common** | *Baseline* — no action. | *Systematic weakness* — the boring, true finding (e.g. consistently losing 1v1 duels on CT). Report plainly; it is *not* novel but it *is* actionable. |

Separating these two prevents the single most common failure of automated coaching: labelling a stylistic quirk as a
weakness because it is statistically unusual. The Bayesian-nonparametric playstyle-clustering work (Normoyle &
Jensen ◦) makes the same point from the modelling side: styles are mixtures and hybrids, not anomalies.

### 4.4 Cheapest useful version first

D1 (predefined detectors) + D2 on a narrow context vector + wildcard-free reporting will surface ~80% of the value.
D3/D4 are the "unknown unknowns" layer, and they are where the multiplicity and confabulation risk live; build them
second, behind the guards.

---

## 5. Preventing confabulated explanations

### 5.1 Claim-ledger architecture (non-negotiable)

```
findings.jsonl   ← every claim the system is allowed to make
  { claim_id, metric_id, detector_version, slice_definition,
    target_composition, n_events, n_opportunities, n_matches, n_eff,
    effect, effect_units, ci90, p_raw, q_value | e_value,
    posterior_prob_harmful, tier: "A"|"B"|"C",
    status: "exploratory" | "replicated" | "confirmed",
    search_space_size, code_hash, data_snapshot_id,
    evidence_round_ids: [...], counterexample_round_ids: [...],
    info_tier: "T1"|"T2"|"T3"|"T4" }
```

Rendering contract:

1. **Numbers are injected, never generated.** The prompt contains the ledger JSON; the model may reference claim ids
   and metrics, but every numeral in the output is inserted by code into a template slot.
2. **Closed slot set.** The model's output schema is
   `{claim_id, observation_phrase, interpretation_phrase?, recommendation?}` with constrained enums; free prose is
   limited to one sentence per slot.
3. **Deterministic verifier.** After generation: extract every numeric and relational token (comparisons, rankings,
   "more/less than", temporal references), and check each against the ledger — exact match, unit match, sign match,
   entity match. Any mismatch → reject and regenerate (max 1 retry), else fall back to a deterministic template.
   This mirrors the cell-level structural-faithfulness approach in **TabFaith** and citation-attribution validation
   in **CiteGuard** (both ◦ indexed, both reported as imperfect — hence the deterministic backstop).
4. **Causal-verb prohibition.** The allowed claim types are: measurement, comparison, association, prediction.
   "causes", "because", "leads to", "due to" are blocked unless a design (N-of-1 randomization, §6) supports them.
   Motivation: CausalPitfalls / CauSciBench evidence that LLMs overclaim causality from association (◦ indexed).
5. **Uncertainty is stated, not improvised.** The confidence language is generated from the tier and posterior, not
   chosen by the model. Motivated by FermiEval's finding that nominal LLM intervals are badly miscalibrated (◦).
6. **Abstention is a first-class output.** "Insufficient evidence (n=7, exploratory)" must be renderable and must not
   count as failure. Benchmarks that score only accuracy punish abstention and thereby incentivise hallucination
   (Nature 2026, doi:10.1038/s41586-026-10549-w, ◦ indexed).
7. **Counter-evidence is rendered by default.** Each claim ships with the nearest *normal* rounds (counterexamples)
   so the human can falsify it. Requiring the system to show its disconfirming cases is the cheapest anti-hype lever.
8. **Exposure of the search space.** Every finding carries `search_space_size` and `status`. Exploratory findings are
   visually distinct from replicated ones. This is the garden-of-forking-paths guard applied to the *product*.
9. **No privileged information.** Narration prompts are built from the T1–T4 belief stream (`C-data-fogofwar.md`
   §6.11.3), with T0 world state physically unreachable from the renderer. A statement like "you should have known he
   was B" is only legal if the belief tier supports it.

### 5.2 Statistical-blip → narrative failure mode (worked example)

Wrong:
> "You panic in 1v2 retakes and lose them."

Right:
> "In 21 post-plant retakes on CT with ≤2 alive teammates you were the last player alive (n=21, opportunity base = 47
> retakes, 9 of 21 untraded). Your duel-win rate in those situations is 34% where the model expected 46%
> (90% CI −19 to +2 pp, q=0.11, exploratory). Composition-standardised across maps. Rounds 4, 9, 17 (Mirage) and 22
> (Ancient) look like this; rounds 6, 12, 30 did not."

Both sentences make a claim; only the second can be falsified by the player, and only the second can't be wrong about
a mechanism it never measured.

---

## 6. Proposed pipeline (single-player, local hardware)

### 6.1 Stage graph

```
[0] Ingest ────────────────────────────────────────────────────────────────────────────
    .dem files (own history + optional reference corpus)
    → sha256, source, map, version(ClientVersion), match id, platform, own rating
    → parse with awpy (Rust/Polars core) or demoparser2; pin asset version for LOS
    → raw Parquet; DuckDB catalog with provenance columns

[1] Canonical event layer ─────────────────────────────────────────────────────────────
    rounds, kills, damages, shots, grenades, bomb events, per-tick snapshots (downsampled),
    utility activation/deactivation, LOS samples, and the T1–T4 belief stream (§C.11)
    → one wide event table + one context table + one belief table (model-visible only)

[2] Context encoding ──────────────────────────────────────────────────────────────────
    deterministic context vector x_e per decision point; zone ids from a checked-in
    map-zone config; opportunity tables (denominators) materialised explicitly

[3] Value model (severity backbone) ───────────────────────────────────────────────────
    calibrated P(win | state) → ΔWPA per event
    • train on: reference corpus + your own matches EXCLUDING the held-out block
    • splits: chronological / grouped by match (never random rows within a round)
    • report Brier, log loss, ECE, reliability curve; recalibrate per population
    • store artifact + training-snapshot id + calibration report

[4] Expectation model (residual backbone) ─────────────────────────────────────────────
    per event type: P(outcome | context, opponent bucket, teammate bucket, weapon, geometry)
    → residual r_e; this is where "better than the situation warranted" lives

[5] Hierarchical estimation ───────────────────────────────────────────────────────────
    multilevel model: events ⊂ rounds ⊂ matches ⊂ (map, patch)
    partial pooling over slices; posterior over per-slice effect; n_eff via design effect

[6] Discovery ────────────────────────────────────────────────────────────────────────
    D1 detectors (fixed family)      → BH-FDR
    D2 residual clustering           → stability + permutation
    D3 subgroup mining over grammar  → WY permutation (FWER) / LAMP pruning
    D4 series anomalies + change pts → block-null, online FDR / confidence sequences
    D5 (optional) reference-population comparison → versioned benchmark object

[7] Falsification & promotion ────────────────────────────────────────────────────────
    holdout block (last 20% chronologically, never touched by [6])
    multiverse: re-run under ≥3 reasonable spec variants (window, stratification, model class)
    promote to "replicated" only if the effect survives holdout AND ≥ 2/3 specs

[8] Narration ─────────────────────────────────────────────────────────────────────────
    ledger → templated numbers → LLM prose over closed slots → deterministic verifier
    → report with evidence rounds, counterexample rounds, info tier, status, search space

[9] Tracking & N-of-1 ────────────────────────────────────────────────────────────────
    weekly aggregate series → PELT (offline) + confidence sequences (online)
    intervention assignment (alternating/randomized) → randomization test + Tau-U
    → promote/probation/retire findings
```

### 6.2 Data stores (all local)

| Store | Contents | Notes |
| --- | --- | --- |
| `demos/` | immutable `.dem` + `manifest.jsonl` (sha256, version, match id, source) | raw is the source of truth; re-derivable |
| `parquet/raw/` | per-match parsed datasets (awpy returns Polars ✓) | columnar, partitioned by match; Parquet batch parsing is a documented awpy workflow ✓ |
| `parquet/events/` | canonical event + context tables | small: ~10³–10⁴ rows/match |
| `parquet/beliefs/` | T1–T4 model-visible stream | **separate directory/credentials** from world state |
| `parquet/world/` | T0 omniscient state, labels only | never joined into a narration prompt |
| `duckdb/analytics.duckdb` | catalog, opportunity tables, slice materialisations, provenance | queries over Parquet directly |
| `models/` | value model, expectation model, calibration reports, training-snapshot ids | versioned; a recalibration invalidates downstream findings |
| `findings/ledger.jsonl` | the claim ledger, append-only, with `code_hash` + `data_snapshot_id` | the audit trail; nothing is narrated that isn't here |
| `reports/` | rendered outputs + the verifier's pass/fail record | |

### 6.3 Compute / storage feasibility on a laptop (arm64, local-first) — [INFERENCE]

- **Position storage.** Full-rate (64 tick/s) positions for 10 players over a ~40 min match ≈ 1.5 M rows/match;
  at ~300 matches that is ~450 M rows — 10–30 GB Parquet depending on schema. **Recommendation:** store
  event-triggered snapshots + a downsampled grid (2–4 Hz) for the *persistent* layer, and re-derive full-rate
  features on demand from the `.dem` when a specific round needs exploration. awpy's snapshot/ticks APIs support
  arbitrary tick selection ✓, so this is a storage policy, not a capability limit.
- **Parsing cost.** awpy is Rust-backed with a Polars core and ships prebuilt wheels for macOS ✓; ensure wheels are
  used (no Rust toolchain needed). Expect tens of seconds per match for the full dataset set; batch once, store, never
  re-parse in the loop.
- **Modelling.** Event-level hierarchical logit/probit over ~10⁴–10⁵ rows with ~10² group levels is CPU-feasible
  (PyMC/numpyro/Stan or `lme4`-style approximations; even empirical-Bayes beta-binomial is enough for v1).
  UMAP+HDBSCAN over 10⁴ events is seconds-to-minutes. Matrix profile on session-level series (hundreds of points) is
  trivial. WY permutation over 10⁴ predicates × 10³ permutations is the heaviest step — prune by minimum support
  first (LAMP-style) and parallelise across cores.
- **No local LLM, no GPU requirement.** Value/expectation models are gradient-boosted trees or GLMs; only the
  narration stage calls a commercial API (§F).

### 6.4 Validation plan

| Level | Test | Pass condition |
| --- | --- | --- |
| Data integrity | manifest hashes; re-parse determinism; per-match row counts vs `demo.rounds` | byte-stable derived tables |
| Leakage | assert narration prompts cannot reach `world/`; assert the belief builder is causal (§C.11.3 leak test) | automated assertion in CI |
| Value model | chronological/grouped split, ECE + Brier + reliability plot; recalibration on own-population data | ECE below a stated bar; better than the "constant base rate" baseline |
| Detector null calibration | run the full detector stack on **shuffled-label** data (round-level permutation) | discovery rate at the nominal level (e.g. ≤5% FWER, ≤10% FDR) |
| Selection bias | recreate a synthetic streak dataset; verify the permutation null returns ~0 findings (§2.8) | null correctly rejects the artifact |
| Stability | split-half replication of every promoted finding; cluster bootstrap stability for D2 | ≥ 2/3 split reliability for promotion |
| Multiplicity | audit that `q_value`/`e_value` reflect the true tested family (log the enumeration) | search-space size in ledger matches the enumerator |
| Narration | verifier on adversarial prompts; inject wrong numbers and assert rejection; measure abstention rate | 0 unsupported numeric claims pass |
| Utility (the real test) | N-of-1 randomized intervention on a promoted habit | effect measured with a randomization test; report Tau-U + CI, including nulls |

---

## 7. Risks, unknowns, and the hardest unsolved piece

### 7.1 Ranked open problems

1. **No ground truth for "mistake" or "habit" — so no accuracy metric exists.** There is no labelled dataset of
   individual-player habits, and expert annotation is expensive, subjective, and (per the hot-hand history ✓) easily
   wrong. Consequence: detectors can only be validated by (a) null calibration, (b) split/holdout stability,
   (c) expert review of sampled clips, and (d) **prospective N-of-1 intervention outcomes**. Expect slow, noisy
   feedback; budget for it. **This is the single hardest piece.**
2. **Counterfactual/decision-value identification.** `ΔWPA` measures *realised* value, not *decision quality*: a
   correct decision can lose the round, and a careless one can win it. Ranking *available alternatives* requires
   either a counterfactual simulator, a large reference population to match against, or explicit ghost/belief
   rollouts — none of which is available from a single player's observational history. Any "decision quality" label
   is therefore an approximation; the wording must not outrun the method.
3. **Separating skill from context at n ≈ 10²–10³ matches.** Opponent strength, teammate quality, economy, and own
   earlier choices all confound. Partial pooling + standardisation helps; it does not identify causal skill.
4. **Multiplicity across the habit space.** 10⁴ events cannot support 10⁴ hypotheses. The honest ceiling of this
   system is a handful of well-evidenced findings per reporting cycle; the design must *refuse* to produce more.
5. **"Unconscious" is unverifiable from demos** — requires self-report, which is itself noisy and subject to
   reactivity (journaling changes behaviour).
6. **Drift & non-stationarity.** Patch changes, meta shifts, and your own improvement invalidate both the value model
   and the population benchmark. Version everything; expect to recalibrate.
7. **Reference population availability.** Without a reference, "unusual vs peers" degrades to "unusual vs your past".
   Importing pro demos helps the spatial/value models but mis-calibrates the *difficulty* distribution (§2.1).
8. **Computational trap.** Full-tick, full-history feature extraction is tempting and unnecessary; it will dominate
   engineering time and disk. Contain it with the storage policy in §6.3.

### 7.2 Feasibility verdicts

| Capability | Verdict |
| --- | --- |
| Extract event+context features from own demo history | **Demonstrated** (awpy ✓; ecosystem mature) |
| Compute per-event `ΔWPA` with a calibrated model | **Demonstrated in principle** (Xenopoulos 2020 ✓; multiple CS2 repos, incl. `eigenpaul/cs2-evalbar` ✓ which ships calibration + ECE + latent atlas + local workbench, though it is a 2-commit, 0-star prototype focused on Inferno) — expect real work training/calibrating on **your** population |
| Situation-taxonomy slices with partial pooling + cluster-aware CIs | **Research-supported**, engineering-ordinary |
| Predefined detector library (traded deaths, dry entries, utility waste…) | **Demonstrated** (Leetify-class products ✓; definitions are public) |
| Unsupervised discovery of *unknown* weaknesses with valid error control | **Plausible-untested** as an integrated system; components (EMM/SD + WY, HDBSCAN stability, matrix profile) are all research-supported |
| Trend tracking with valid uncertainty under continuous monitoring | **Research-supported** (confidence sequences ✓ / online FDR ✓) but **not** implemented in any product found |
| Narration without fabricated statistics | **Achievable** via the ledger + deterministic verifier; the LLM-only version is **not** trustworthy (StatQA/QRData/FermiEval/TabFaith evidence) |
| "Did my coaching work?" for one player | **Research-supported** via SCED/N-of-1 randomization; requires deliberate design (randomized alternation), not passive logging |
| Detecting *unconscious* habits | **Infeasible** from demos alone; requires a self-report channel ("unreported" is the measurable substitute) |
| True decision-quality / counterfactual grading at scale | **Infeasible** from single-player observational history; approximate only |

---

## 8. Recommended approach stack (one paragraph per layer)

1. **Representation** — canonical event table + explicit opportunity tables + T1–T4 belief stream; zone ids from a
   checked-in map config. Everything downstream is a query over these.
2. **Severity** — a calibrated `P(win | state)` model (gradient-boosted trees or logistic first, per the Xiong ✓
   lesson), trained with grouped/chronological splits, calibrated on your own population, versioned, re-fit on patch
   boundaries. `ΔWPA` per event; residual vs expectation for non-combat events.
3. **Estimation** — one multilevel model over all events with partial pooling across slices; report posterior
   medians, 90% intervals, `n_eff`, and both raw and shrunk values. Slices are *reporting* objects, never estimation
   units.
4. **Discovery** — D1 detector library (BH-FDR) as the workhorse; D2 residual clustering (stability-gated) to surface
   signatures; D3 subgroup mining over a bounded context grammar with **Westfall–Young permutation** for the unknown
   cases; D4 matrix profile + PELT/BOCPD for rare configurations and drift. Everything is promoted only after
   holdout replication.
5. **Tracking** — weekly aggregates with PELT for retrospective segments, **confidence sequences / e-values** for
   anytime-valid "is this improving?" claims, online FDR (LORD/SAFFRON) across simultaneously monitored metrics.
6. **Intervention evaluation** — randomized/alternating-treatment N-of-1 with randomization tests and Tau-U. This is
   the only mechanism that can turn a detected pattern into a *validated* habit-and-fix pair.
7. **Narration** — claim ledger + templated numerals + closed-slot LLM prose + deterministic verifier + mandatory
   counterexamples + explicit exploratory/confirmed status + causal-verb prohibition + honest abstention.
8. **What to build first** — ingest → events → opportunity tables → a dozen D1 detectors with partial pooling and
   honest CIs → ledger → narrative templates (no LLM needed yet). Add the LLM only once the ledger exists, because
   the ledger is what makes the LLM safe.

---

## 9. Source list

✓ = primary source read in this session. ◦ = located/consistent across the search index but **not** independently
read; treat details as unverified. Accessed 2026-10-15 unless dated.

**CS value / context models**
- Xenopoulos, Doraiswamy, Silva. *Valuing Player Actions in Counter-Strike: Global Offensive*. IEEE BigData 2020. ✓
  https://arxiv.org/abs/2011.01324
- Szmida & Toka. *Evaluating Player Actions in Professional Counter Strike using Temporal Heterogeneous Graph Neural
  Networks*. MIT Sloan Sports Analytics Conference 2025. ◦
  https://www.sloansportsconference.com/research-papers/evaluating-player-actions-in-professional-counter-strike-using-temporal-heterogeneous-graph-neural-networks
- `eigenpaul/cs2-evalbar` — round-win probability model, GraphTemporalTransformer, calibration/ECE, latent atlas,
  local FastAPI+React workbench; Inferno-only, 2 commits, 0 stars → **prototype**. ✓
  https://github.com/eigenpaul/cs2-evalbar
- `phil-holland/csgo-impact-rating` (CS:GO WPA implementation) ◦; `pnxenopoulos/csgo` (paper's implementation) ◦;
  `TaiZo1/cs2-win-prediction` ◦

**Football/sports value-model ancestors**
- Karun Singh, *Introducing Expected Threat (xT)* ✓ https://karun.in/blog/expected-threat.html
- Fox et al., fine-grained instantaneous possession value (EPV) ◦
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8570314/

**Playstyle / fingerprint / clustering**
- Normoyle & Jensen. Bayesian Clustering of Player Styles. AIIDE 2015 ◦
  https://ojs.aaai.org/index.php/AIIDE/article/view/12805
- Ingram et al. Play-style Identification through Deep Unsupervised Clustering of Trajectories ◦
  https://www.raillab.org/publication/ingram-2022-play/
- Zimmer et al. Player Behavior Analysis for Predicting Player Identity Within Pairs… HICSS-58, 2025 ✓
  https://aisel.aisnet.org/hicss-58/in/esports/4/
- Kuzhii & Furgala. Feature Engineering for Role Assessment in Counter-Strike 2, 2025 ◦
  https://publications.lnu.edu.ua/collections/index.php/electronics/article/view/5099
- Fitsner. Exploring clustering algorithms on spatial data in video games, UVic 2025 ◦
  https://dspace.library.uvic.ca/items/b3d6a385-3f91-4bf1-ad3b-24189fce292d
- `sachiniiits/btp_cs2` — CS2 role discovery via per-side SOM ◦ https://github.com/sachiniiits/btp_cs2
- McInnes et al. UMAP (arXiv 1802.03426) ◦; hdbscan (JOSS 2017) ✓ docs/FAQ + clustering guidance ✓
  https://umap-learn.readthedocs.io/en/latest/faq.html
- Cluster stability: Hennig, *Cluster-wise assessment of cluster stability* ◦; `fpc::clusterboot` ◦;
  stability review ◦ https://pmc.ncbi.nlm.nih.gov/articles/PMC9787023/

**Trajectories / movement**
- Durst et al. *Learning to Move Like Professional Counter-Strike Players*, SCA 2024 ✓ https://arxiv.org/abs/2408.13934
- Lee, Han, Whang. *Trajectory Clustering: A Partition-and-Group Framework* (TRACLUS), SIGMOD 2007 ◦/✓ (PDF located)
  https://hanj.cs.illinois.edu/pdf/sigmod07_jglee.pdf

**Pattern/subgroup mining**
- Pei et al. PrefixSpan (TKDE 2004) ◦ https://www2.cs.sfu.ca/~jpei/publications/span.pdf
- Leman, Feelders, Knobbe. Exceptional Model Mining. ECML PKDD 2008 ◦
  https://mlanthology.org/ecmlpkdd/2008/leman2008ecmlpkdd-exceptional/
- Scalable significant subgroup discovery, 2023 ◦ https://www.sciencedirect.com/science/article/pii/S0950705123010833
- Permutation strategies for mining significant sequential patterns ◦
  https://www.research.unipd.it/handle/11577/3329322
- Terada et al. LAMP (FWER-controlled pattern mining) ◦ https://arxiv.org/abs/0906.5263
- Lemmerich et al. A Critical View on Automatic Significance-Filtering in Pattern Mining ◦
  https://proceedings.mlr.press/v47/lemmerich14a.html

**Anomaly detection / time series**
- STUMPY docs (matrix profile, motifs/discords, `m` selection, exclusion zones) ✓ https://stumpy.readthedocs.io/en/latest/
- `ruptures` PELT docs ✓ https://github.com/deepcharles/ruptures/blob/master/docs/user-guide/detection/pelt.md
- Adams & MacKay, BOCPD ◦ https://arxiv.org/abs/0710.3742 ; `bocd` / `bayesian-changepoint` libraries ◦

**Uncertainty, multiplicity, honest exploration**
- Benjamini & Hochberg, FDR, JRSS-B 1995 ◦ https://rss.onlinelibrary.wiley.com/doi/10.1111/j.2517-6161.1995.tb02031.x
- Gelman & Loken, *The garden of forking paths* ✓ https://stat.columbia.edu/~gelman/research/unpublished/forking.pdf
- Simmons, Nelson, Simonsohn, *False-Positive Psychology*, 2011 ✓ https://doi.org/10.1177/0956797611417632
- Miller & Sanjurjo, *Surprised by the Hot Hand Fallacy?*, Econometrica 2018 ✓
  https://www.landsburg.org/hothandfallacy.pdf
- Taylor & Tibshirani, selective inference ◦ https://pmc.ncbi.nlm.nih.gov/articles/PMC4485109/
- Javanmard & Montanari, online FDR (LORD) ◦ https://arxiv.org/abs/1502.06197 ; Ramdas et al., SAFFRON, ICML 2018 ◦
  https://proceedings.mlr.press/v80/ramdas18a/ramdas18a.pdf ; dependence-aware online FDR ◦
  https://arxiv.org/abs/2110.08161
- Howard, Ramdas, McAuliffe, Sekhon — time-uniform Chernoff bounds / confidence sequences ✓
  https://arxiv.org/abs/1810.08240 ; https://doi.org/10.1214/18-PS321
- Standardisation / IPTW / g-computation primers ◦ https://pmc.ncbi.nlm.nih.gov/articles/PMC12009273/ ,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC2652882/

**Longitudinal modelling / rating systems**
- PandaSkill (LoL, per-role ML performance + OpenSkill + dual rating), 2025 ✓ https://arxiv.org/abs/2501.10049
- CS:GO plus/minus Bayesian rating, 2024 ✓ https://arxiv.org/abs/2409.05052
- Xiong et al. *Going Deeper with Deep Knowledge Tracing*, EDM 2016 ✓
  https://beardeer.github.io/wpi_public_html/papers/edm_2016_xiong_zhao.pdf
- NeuralCD (AAAI 2020 / TKDE 2023) ◦ https://arxiv.org/abs/1908.08733
- SCED / N-of-1: randomization inference ◦ https://jepusto.com/files/Randomization-inference-for-SCED-2018-01-10.pdf ;
  Tau-U interpretation ◦ https://www.tandfonline.com/doi/full/10.1080/23311908.2018.1518687 ; analysis resources ◦
  https://www.nof1sced.org/analysis

**LLM grounding / narration safety**
- StatQA, NeurIPS 2024 D&B ◦ ; QRData ◦ https://arxiv.org/abs/2402.17644 ; CausalPitfalls ◦
  https://proceedings.iclr.cc/paper_files/paper/2026/hash/9235c376df778f1aaf486a882afb7471_Abstract-Conference.html
- FaithEval (ICLR 2025) ◦ ; FaithBench (NAACL 2025) ◦ https://aclanthology.org/2025.naacl-short.38/ ;
  CiteGuard ◦ https://arxiv.org/abs/2510.17853 ; TabFaith (ACL 2026) ◦
  https://aclanthology.org/2026.surgellm-1.21/
- FermiEval (LLM interval miscalibration) ◦ https://arxiv.org/abs/2510.26995
- Leetify: stats glossary, benchmarks, Post-Match Journal, rating update (Nov 2024 recalibration) ✓
  https://leetify.com/blog/leetify-stats-glossary/ , https://leetify.com/blog/post-match-journal/ ,
  https://leetify.com/blog/cs2-benchmarks/
- Scope.gg / CStrike.gg / MyCS (habit-like product claims, no published validation found) ◦

**Tooling**
- awpy 2.x docs (CS2-only, PBDEMS2, Polars datasets, `snapshots`/`ticks`, `VisibilityChecker`, version pinning,
  Parquet batch workflows) ✓ https://awpy.readthedocs.io/en/stable/getting-started.html
- Albrecht & Stone, *Autonomous Agents Modelling Other Agents*, AIJ 2018 (opponent/adaptation framing) ✓
  https://www.cs.utexas.edu/~pstone/Papers/bib2html-links/AIJ18-Albrecht.pdf

**Cross-references inside this repo**
- `research/C-data-fogofwar.md` §6.11 (T0–T4 information tiers, anti-hindsight requirements) — the information-state
  axis of §3.2 and the leakage assertions in §6.4 depend on it.
- `research/F-ai-arch.md` (representation layers L0–L5, cost model, agentic tooling) — the narration stage (§5) and
  the storage policy (§6.2) must agree with it.

---

## Appendix A — Worked example: from events to a promotable finding

Input: 240 demos, Mirage only subset = 71 matches, ~1,560 rounds. Event table → 1,180 "solo entry attempt" events.

1. **Context vector** for each event: map, side, buy class, alive diff, zone, nearest-teammate distance,
   trade-available, weapon class, info tier, opponent bucket.
2. **Value model** (trained on 190 matches, calibrated on your population, ECE 0.021): yields `P(win|state)` for each
   tick; `ΔWPA` of the entry attempt computed from the decision tick to +2 s.
3. **Expectation model** predicts `P(entry survives the first exchange | context)` = 0.44 on average.
4. **Slice**: `Mirage ∧ T ∧ full-buy ∧ alive 5v5 ∧ A-ramp ∧ no-flash-support`. n_events = 61,
   O_s = 143 entry attempts, matches = 19.
5. **Effect**: observed survival 0.31 vs expected 0.44 → residual −0.13; mean `ΔWPA` cost = −0.041 (4.1 pp of round
   win probability per attempt). `e_s = 61/1560 = 0.039` per round → `EL_s = 100 × 0.039 × 4.1 ≈ 16` rounds per 100
   rounds at point estimate. With partial pooling and round-clustered uncertainty (ρ ≈ 0.05, m̄ ≈ 1.6, n_eff ≈ 55),
   the shrunk effect is −0.09 with a 90% CI of [−0.17, −0.01]; `C_s = P(EL > 0.5) = 0.99`.
6. **Multiplicity**: 6,400 predicates enumerated (bounded grammar); Westfall–Young over 1,000 block permutations
   (blocks = matches, preserving the nested structure) → adjusted p = 0.004. Survives.
7. **Stability**: reproduced at −0.07 (Mirage ∧ T ∧ full-buy ∧ A-ramp, no teammate-distance constraint) and −0.11
   (all maps, A-ramps, no flash) → 2/2 specs. Holdout block (last 48 matches, untouched): residual −0.10, n=22 →
   directionally confirmed, still tier A.
8. **Counterexamples**: 6 rounds where the same predicate produced a clean entry with no loss — rendered by default.
9. **Ledger entry** → narration: "You take A-ramp entries on T full-buys without flash support and lose the first
   exchange more often than your own context model expects (31% vs 44%, 61 attempts across 19 Mirage matches,
   shrunk effect −9 pp, 90% CI [−17, −1], q=0.004). This costs an estimated 9–16 rounds per 100 rounds. Not
   self-reported. Evidence: rounds 4, 9, 17, 22, 30, 41 (clips). Counterexamples: rounds 6, 12, 30, 33, 47, 55."
10. **Intervention**: alternate-treatment N-of-1 — weeks randomized to "flash-assisted entries only" vs "standard",
    tracked with a randomization test on the primary metric (first-exchange survival in the predicate) and Tau-U.
    Promote to "confirmed habit + effective fix" only if the randomization test rejects.

Note what the example deliberately does **not** say: no claim about *why* (mechanics vs decision), no claim about
*unconsciousness*, no claim about how many rounds were *avoidably* lost. Those require evidence this design cannot
manufacture, and pretending otherwise is the failure mode the whole architecture exists to prevent.

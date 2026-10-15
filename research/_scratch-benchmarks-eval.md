# Benchmarks: spatial / temporal / video / agentic / judge reliability (CS2 demo-analysis eval)

Slice owner: `AIModelsArchCosts.BenchmarksEval`. Researched 2026-10-15.

> NOTE ON PATH: the assignment named `research/_scratch-cheap-providers.md`, but that file is
> owned by sibling `AIModelsArchCosts.RetentionFinetune`. Written here instead to avoid clobbering.

Status tags: **[Demonstrated]**=read on the primary/vendor page during this session;
**[Search-only]**=appears in web_search synthesis, primary page NOT read (treat number as unverified);
**[Infeasible]**=cannot be measured this way.

Method: discovery via `web_search`; every load-bearing number below was re-read on the primary
page where marked [Demonstrated]. web_search output is LLM-synthesized and can be stale/wrong —
treat [Search-only] rows accordingly.

---

## A. Benchmark catalogue

### A1. Long-video / video temporal reasoning

| Benchmark | Measures | Leader / score | Source + status |
|---|---|---|---|
| **Video-MME** | 900 videos (11 s–1 h), 2,700 QA; short/med/long; with+without subtitles and audio. "Long" = 30–60 min. | video-SALMONN 2+ **81.6 w subs / 79.7 w/o**; Gemini 1.5 Pro 81.3/75.0; AdaReTaKe 79.6; GPT-4o 77.2. Long-video-only w subs: Gemini 1.5 Pro **77.4** > SALMONN/AdaReTaKe 76.4 > JT-VL-Chat 76.1. | https://video-mme.github.io/home_page.html (read 2026-10-15) [Demonstrated]. **Caveat: leaderboard is stale — newest entry is 2025-09-28; no Gemini 3/4, GPT-6, Claude 5 rows.** |
| **LVBench** | "Extreme" long video (~68 min avg): event reasoning, entity understanding, key-info retrieval, temporal grounding. | Deep Video Discovery (Microsoft) **74.2**; Seed1.5-VL-Thinking 64.6; GPT-4o-2024-11-20 48.9. | https://lvbench.github.io/ + ICCV 2025 paper (https://openaccess.thecvf.com/content/ICCV2025/papers/Wang_LVBench_An_Extreme_Long_Video_Understanding_Benchmark_ICCV_2025_paper.pdf). Numbers [Search-only]. |
| **LongVideoBench** | "Referred reasoning" — evidence from different points in a video; seconds→~1 h. | Official page still shows GPT-4o (0513) **66.7**, Aria 65.0. | https://longvideobench.github.io/. [Search-only]; **leaderboard appears abandoned (2024-era entries only).** |
| **MLVU** | 3 min–2 h; temporal reasoning, action recognition, narrative QA, event reasoning, sub/multi-detail, tutorial & sports QA. | Dev M-Avg: LVAgent **83.9**, TSPO-72B 77.3. Test M-Avg: AdaReTaKe **66.3**, GPT-4o 54.9. | https://github.com/JUNJIE99/MLVU. [Search-only] |
| **VECTOR** | Explicit *temporal order of events*. Key finding: VLMMs answer existing benchmarks fine **even with scrambled frames** → they rely on scene priors, not sequence. Proposes MECOT (event-by-event SFT + CoT). | WACV 2026. No single headline winner read. | https://arxiv.org/abs/2512.08979 (submitted 2025-12-05) [Demonstrated]. **Most relevant to CS2 (round/event ordering).** |
| **Video-MME-Logical** | Controlled diagnostic: 5 temporal-logical ops (state tracking, sequential counting, temporal ordering, dynamic spatiality, structural composition), 25 task categories, intermediate-state diagnostics, difficulty controlled by temporal horizon. | "Substantial human–model gap"; SFT on 500K samples still insufficient. | https://arxiv.org/abs/2606.27828 (2026-06-26) [Demonstrated]. **Best fit for "did the model track evolving match state".** |
| **Video-MME-v2** | Progressive: visual aggregation → temporal dynamics → complex multimodal reasoning; group-based (consistency) eval. | — | https://arxiv.org/abs/2604.05015 [Search-only] |
| **CaST-Bench** | Causal-chain video QA grounded in multiple temporal segments + bbox tracks; 2,066 Q / 1,015 videos; scores answer accuracy *and* evidence grounding. | — | https://arxiv.org/abs/2605.23216 [Search-only] |

Takeaways relevant to a CS2 system:
- The long-video leaderboards are **stale** relative to the 2026 frontier; do not quote them as current model rankings.
- **Frame-scrambling robustness** (VECTOR) is the single cheapest adversarial check you can port to demos:
  shuffle tick order and see whether the model's "reasoning" collapses.
- Grounded-evidence scoring (CaST-Bench) is the right shape for coaching: reward citing the correct
  round/tick, not just the right verdict.

### A2. Spatial / 3D reasoning

| Benchmark | Measures | Leader / score | Source + status |
|---|---|---|---|
| **VSI-Bench** ("Thinking in Space") | Egocentric indoor video: ~5,000 QA / 288 videos (ScanNet/ScanNet++/ARKitScenes). 8 tasks: counting, rel. distance/direction, route planning, object/room size, abs. distance, appearance order. CoT/self-consistency/ToT do **not** fix it; explicit cognitive maps help. | Original: Gemini 1.5 Pro best general VLM ≈48.8. Newer aggregator: OmniStream-7B 70.6, SpaceMind 69.6. | CVPR 2025 paper https://arxiv.org/abs/2412.14171; project https://vision-x-nyu.github.io/thinking-in-space.github.io/. Numbers [Search-only]. |
| **3DSRBench** | Static 3D: 2,772 Q / 12 types (height, location, orientation, multi-object) + **paired common-vs-uncommon camera viewpoint** split to expose 2D shortcuts. | GPT-4o 51.2→44.3 (−13.5% rel); Gemini-Pro 59.9→49.5 (−17.4%); LLaVA-NeXT-8B 45.5→36.8 (−19.1%). | ICCV 2025 https://arxiv.org/abs/2412.07825 + https://3dsrbench.github.io/. Viewpoint numbers [Search-only]. |
| **MindCube** | Spatial *mental modelling from limited views*: 21,154 Q / 3,268 multi-view images. Settings: Among / Around / Rotation. Chance ≈32.35. | GPT-4o **38.81**, Claude-4-Sonnet 44.75, LLaVA-OneVision-7B 47.43, **SenseNova-SI 90.10** (specialised). Map-then-reason: SFT joint 60.76, RL-from-SFT 70.67 (page body); page meta says 37.8→57.8→61.3 (**inconsistent — flag**). "Structure alone fails": feeding a precomputed map *degrades* (−5.81%). | https://mind-cube.github.io/ + https://arxiv.org/abs/2506.21458 (2025-06-26), read 2026-10-15 [Demonstrated]. |
| **SpatialRGPT-Bench** | Region + depth-grounded relational/metric reasoning; 657 qualitative + 749 quantitative VQA. Model side: space-aware sampling matters (VSI-Bench 54.24 w/ vs 53.53 w/o). | Adding depth materially improves RGB-only SpatialRGPT but does not solve 3D. | https://arxiv.org/abs/2406.01584; https://arxiv.org/abs/2412.07825. [Search-only] |
| **OSI-Bench** | Relational / metric / kinematic split; tests **indoor→open-world transfer**. Constrained-indoor competence does not transfer. | — | CVPR 2026 https://openaccess.thecvf.com/content/CVPR2026/papers/Wu_From_Indoor_to_Open_World_Revealing_the_Spatial_Reasoning_Gap_CVPR_2026_paper.pdf [Search-only] |

Takeaways:
- Cross-cutting failure modes: language/prior shortcuts, **viewpoint sensitivity**, weak metric reasoning,
  failure to fuse frames into one persistent map, sensitivity to *which* frames are sampled.
- For CS2 these matter directly: "left of" is easy, "12 m away, behind the smoke, seen 3 s ago" is not.

### A3. Trajectory / geometry reasoning

| Benchmark | Measures | Source + status |
|---|---|---|
| **REM** (Reasoning over Embodied Multi-Frame Trajectories) | Controllable 3D envs; long-horizon embodied spatial reasoning: object permanence/distinction, spatial relations, **numerical tracking** across dynamic viewpoints. Best models unreliable at *moderate* complexity humans handle easily. | https://arxiv.org/abs/2512.00736 (2025-11-30, COLM 2025) [Demonstrated] |
| **NavSpace** | 1,228 trajectory–instruction pairs; 6 spatial-intelligence task categories; instruction *following* vs semantic matching. | ICRA 2026 https://github.com/TidalHarley/NavSpace [Search-only] |
| **NavBench** | Global instruction alignment, partial-trajectory understanding, future-action prediction. | NeurIPS 2025 [Search-only] |
| **CapNav** | Capability-conditioned indoor navigation: plans routes subject to the agent's physical constraints. | CVPR 2026 [Search-only] |
| **ERGeoBench** | Viewpoint-aware reasoning + geo-localisation; yaw/pitch/zoom actions over 2,207 panoramas. | https://proceedings.mlr.press/v306/xue26j.html [Search-only] |
| **360CityArena** | Urban navigation/spatial reasoning: localisation, landmark search, map/VLN nav, counting, relations. | ECCV 2026 [Search-only] |
| **STARK / EmbodiedBench** | Spatiotemporal reasoning (state estimation → relations → knowledge-aware nav); embodied agents incl. ALFRED/Habitat. | NeurIPS 2025 / https://embodiedbench.github.io/ [Search-only] |

### A4. Counterfactual / "what-if" reasoning (incl. games & planning)

| Benchmark | Measures | Leader / result | Source + status |
|---|---|---|---|
| **CausalGame** | Interactive games that test *causal thinking* under **selection bias, hidden confounders, noisy measurement**; agents must design experiments (`do()` interventions), not just correlate. 14 game settings, 29 frontier agents, 3 execution modes. | **No model reaches any scenario's win threshold** (optimal ≈80% survival). Agentic top-5 ≈66–68%. Rubric: **68% of sessions never attempt causal reasoning**. Reasoning-compute scaling gives no consistent benefit (GPT-5.5-XHigh < GPT-5.5). ReAct > single-turn; OpenCode framework +6.9%. | https://causalgame.github.io/ + https://arxiv.org/abs/2607.04293 (ICML 2026 Oral), read 2026-10-15 [Demonstrated] |
| **WhatIfBench + PRISM** | Open-domain, open-form, long-horizon counterfactual causal reasoning; 220 what-if questions (STEM/HSS/Hybrid). PRISM converts free text → semantic causal graph, scores Process (graph validity) + Rubric (explanatory adequacy). | Best of 6 frontier LLMs = **64.62%**; failure modes: causal gaps, **premise drift**, topology fragmentation. | https://arxiv.org/abs/2608.27953 (EMNLP 2026, 2026-08-28) [Demonstrated] |
| **SPIN-Bench** | Long-horizon strategic planning + social reasoning: PDDL (21 domains/1,280 tasks), Tic-tac-toe/Connect-4/Chess, Hanabi (hidden info), Diplomacy (negotiation). Tracks **spatial tracking accuracy vs trajectory length**. | o1 **100%** spatial tracking to 29 steps; o1-mini/GPT-4o degrade with steps. Solvers/Stockfish win or draw 100%. No model reaches Hanabi human Q1 (humans 15–25 pts). Interaction degrades CoT coherence. | https://spinbench.github.io/ + https://arxiv.org/abs/2503.12349 (COLM 2025), read 2026-10-15 [Demonstrated] |
| **CounterBench** | Counterfactual reasoning over causal graphs. | — | https://arxiv.org/abs/2502.11008 [Search-only] |
| **HeroBench** | Long-horizon planning + structured reasoning in virtual worlds. | — | https://arxiv.org/abs/2508.12782 [Search-only] |
| **What-If Analysis of LLMs (game world)** | Explore a game world via what-if queries. | — | https://arxiv.org/abs/2509.04791 [Search-only] |
| **Evaluating Counterfactual Strategic Reasoning in LLMs** | Strategic counterfactuals. | — | ACL GEM 2026 https://aclanthology.org/2026.gem-main.31/ [Search-only] |

Takeaway for CS2: CausalGame and SPIN-Bench show the exact failure we care about — models narrate plausible
counterfactuals ("if you rotated you'd have won") without validating the causal chain. The PRISM-style
graph+rubic split is a directly reusable scoring template, and CausalGame's "measure the intervention" idea
maps onto "was the recommended utility line-up actually the causal difference-maker".

### A5. Agentic tool-use reliability

| Benchmark | Measures | Leader / score | Source + status |
|---|---|---|---|
| **τ-bench** | Tool-agent-**user** interaction; simulated user + tools; scored against DB state; metric **pass^k** (all k trials succeed). | Paper finding: GPT-4o retail ≈61% pass^1 but **<25% pass^8** (>36 pp drop). | https://arxiv.org/abs/2406.12045. Numbers [Search-only]. |
| **τ²-bench** | Adds **dual control** (user also acts on the world; Dec-POMDP) + Telecom domain; separates reasoning vs communication errors. | τ² text Retail/Airline/Telecom, pass^1: Qwen3.5-397B-A17B 87.9, Gemini 3.0 Pro 85.4, Claude Opus 4.5 85.3. | https://arxiv.org/abs/2506.07982 (2025-06-09) [Demonstrated]; leaderboard read at https://taubench.com/ (2026-10-15) [Demonstrated]. |
| **τ³-bench** | Adds **voice** (full-duplex, interruptions, noise) and **banking + knowledge retrieval** (~700-doc KB). Also ττ-bench (coding agents *build* CS agents). | τ³-BankingText: Qwen 3.8 Max 55.2, Claude Opus 5 48.7, Grok 4.5 47.9 pass^1. τ³-Voice: gpt-live-1 **81.7**, Pine Voice 75.4, grok-voice-think-fast 67.3. | https://taubench.com/ (read 2026-10-15) [Demonstrated]. Leaderboard exposes pass^1..pass^4 (no pass^8). |
| **BFCL V4** | Function calling + **agentic** eval: web-search 200 cases, memory 465 cases, format sensitivity, multi-turn/stateful, missing params/functions. | Leaderboard JS-rendered; scores not in HTML. | https://gorilla.cs.berkeley.edu/leaderboard (read 2026-10-15): "Last Updated **2026-04-12**", commit f7cf735, `bfcl-eval==2025.12.17` [Demonstrated]. Individual model scores [Search-only]. |
| **GAIA** | General assistant: browsing + files + code + multimodal + multi-step; hidden-answer test, normalized exact match. | System-level (scaffold-dependent), not pure model scores. ~93% top [Search-only]. | https://arxiv.org/abs/2311.12983; leaderboard HF space exists. |
| **Gaia2** | **Async/dynamic** environments: clock advances independently, noisy events, temporal constraints, ambiguity, multi-agent; each scenario paired with a **write-action verifier** → usable for RLVR. 800 scenarios / 10 universes (ARE platform). | GPT-5 (high) **42% pass@1** but fails time-sensitive tasks; Claude-4 Sonnet trades accuracy/speed for cost; Kimi-K2 21% pass@1 (best OSS). | https://arxiv.org/abs/2602.11964 (ICLR 2026 Oral, 2026-02-12) [Demonstrated]. |
| **AgentBench / AgentBench FC** | 8 envs (ALFWorld, DB, KG, OS, WebShop…); FC variant containerised. | — | https://github.com/THUDM/AgentBench [Search-only] |
| **OSWorld 2.0 / Terminal-Bench 2.0 / METR Time Horizon 1.1** | GUI computer-use; terminal long-horizon; human-equivalent task-duration capability horizon. | — | [Search-only] — peripheral to CS2 (no GUI/terminal need). |

Takeaway: for a CS2 system that *calls* a solver/pipeline as tools, τ²/τ³-bench is the closest analogue
(policy-following + state mutation + user clarification), and Gaia2 is the closest for
"environment changes while you reason". **Report pass^k, not pass@1** — τ-bench shows pass@1 hides brittleness.

---

## B. Structured text vs images vs video (accuracy & token cost)

**Headline:** no single paper runs a clean same-scene, same-question comparison across all three modalities
with both accuracy and token cost. The evidence is directional and must be assembled.

| Evidence | Claim | Source + status |
|---|---|---|
| **TRACE** (Textual Representation of Allocentric Context from Egocentric Video) | Inducing the MLLM to emit a **text** allocentric representation (meta-context + camera trajectory + object entities) as an intermediate trace raises VSI-Bench **and** OST-Bench scores across many backbones. Structured text can substitute for weak direct video reasoning. | https://arxiv.org/abs/2603.23404 (ACL 2026, v2 2026-04-20) [Demonstrated] |
| **Image Prompt Packaging (IPPg)** | Embedding structured text *into an image* cuts cost 35.8–91.0% (up to 96% token compression) but **spatial reasoning, non-English, and character-sensitive tasks are the most vulnerable**; 125-config rendering ablation moves accuracy **10–30 pp**. Fewer billed tokens ≠ better reasoning. | https://arxiv.org/abs/2604.02492 (2026-04-02) [Demonstrated] |
| **Visual Spatial Reasoning (VSR)** | Image+text 2D relations: humans >95%, best VLMs ~70%, orientation-dependent relations worst. | TACL 2023 https://aclanthology.org/2023.tacl-1.37.pdf [Search-only] |
| **Q-Spatial / Reference Objects** | Quantitative (metric) image spatial reasoning is the hard part; reference-object prompting gave large gains (reported +56.2/+28.5/+6.7 pp for Gemini 1.5 Pro / GPT-4V / GPT-4o). | EMNLP 2024 https://aclanthology.org/2024.emnlp-main.947/ [Search-only] |
| **Tables as Texts or Images** | Table *serialisation format* (HTML/Markdown/LaTeX vs rendered image) changes LLM/MLLM table-reasoning accuracy. | https://arxiv.org/abs/2402.12424 [Search-only] |
| **TABVERSE** | Cross-format tables (HTML/MD/LaTeX/rendered image) with content held constant: **structured text generally beats rendered table images**. | https://arxiv.org/abs/2606.09578 [Search-only] |

**Synthesis (with [INFERENCE] where not directly demonstrated):**
1. For *symbolic/metric* reasoning over state you already have, **structured text/JSON wins** — the model
   skips detection/tracking/OCR. But this measures *reasoning after perception*, not end-to-end perception.
2. For *static* scenes, an image is the better visual tradeoff; **video only pays off when the answer depends
   on motion, occlusion/appearance, temporal order, or navigation** (and pays a frame-sampling tax).
3. Video costs scale with frames; a fair comparison must fix a frame budget (4/8/16/32) rather than treat
   "video" as one token count.
4. **Lossy compression of structured data into pixels is dangerous**: IPPg shows 10–30 pp swings from
   rendering choices alone, with spatial data the most fragile class. [Research-supported]
5. For CS2 the implication is concrete: feed the **numeric game state** (positions, HP, economy, tick) as
   structured text, and use pixels/video only for the things that are genuinely visual (smoke, sightlines,
   crosshair placement, utility arcs). Do not route coordinates through an image.

**Chart/table/coordinate failure modes** (directly relevant to plots a coach app would render):
- ChartQA/ChartQAPro: Claude 3.5 reportedly 90.50 → 55.81 moving to real-world charts. ChartQAPro: 1,341 charts/1,948 Q. https://aclanthology.org/2025.findings-acl.978.pdf [Search-only]
- ChartBench: ~600K QA, 42 categories, **unlabelled marks** → value inference from visual structure. https://chartbench.github.io/ [Search-only]
- TableBench (AAAI): 886 test cases / 18 categories; multi-step table reasoning hard. https://ojs.aaai.org/index.php/AAAI/article/view/34739 [Search-only]
- ChartR (CVPR 2026): original/noisy/blurred → grounding robustness. Misleading ChartQA (EMNLP 2025): 3,026 examples / 21 misleader types (truncated axes, non-uniform intervals) → models trust appearance over conventions.
- **Chart-to-table extraction** (CHI'26): MLLMs "reconstruct table structure reliably but struggle with precise value recovery"; authors treat **coordinate-system perception** as its own training problem (log axes, large-magnitude ticks, zero bars). Best fix was a specialised 7B model, not a bigger general model. https://arxiv.org/abs/2606.29808 [Demonstrated]
- Recurring failure taxonomy: pixel→coordinate grounding, mark→series/legend association, approximate
  reading (49.3→50), arithmetic after (mis)extraction, and non-standard axes.

---

## C. LLM-as-judge reliability for open-ended coaching feedback

**Bottom line: no universal "agreement rate" exists.** Four distinct constructs get conflated: human
alignment, swap/position consistency, repeat-run consistency, and inter-judge agreement. High agreement
≠ valid.

| Finding | Detail | Source + status |
|---|---|---|
| **Position bias is real, model/task-dependent, worst in near-ties** | 15 judges × 22 tasks × ~40 generators, **>150,000 instances**. Introduces repetition stability, position consistency, preference fairness. Weakly affected by prompt-component length, **strongly affected by the quality gap** between candidates. | Shi et al., IJCNLP-AACL 2025, https://aclanthology.org/2025.ijcnlp-long.18/ [Demonstrated] |
| **Rubric scoring is secretly multiple-choice → its own position bias** | Judges prefer score options at particular positions (direction is model-specific: some first, some last). Second orthogonal bias: **the order of criteria itself shifts scores**. Mitigation: permute rubric-option order — a few random permutations suffice; gains mainly for strongly-biased judges. | Xu et al., https://arxiv.org/abs/2602.02219 (Findings of EMNLP 2026, v3 2026-09-09) [Demonstrated] |
| **Self-preference bias (SPB) is measurable, and capability ≠ low bias** | Fully automated equal-quality-pair framework across **20 mainstream LLMs**: advanced capability is often **uncorrelated or negatively correlated** with low SPB. A structured multi-dimensional ("cognitive load decomposition") strategy cuts SPB **31.5% on average**. | https://arxiv.org/abs/2604.22891 (v4 2026-06-02) [Demonstrated] |
| **Verbosity/style: two competing readings** | Classic reading: judges reward longer answers even when expanded uselessly (repetitive-list attack; GPT-4 most resistant). 2026 reading: apparent length bias is largely **style/quality** — style bias 0.76–0.92 vs position bias ≤0.04 in that setup; truncation controls 0.92–1.00 accuracy. Preprint, conflicts with broader literature. | arXiv 2604.23178 (https://www.alphaxiv.org/abs/2604.23178v1) [Search-only] |
| **Self-preference confound** | DBG measure separates genuine self-preference from "my own outputs are simply better". | EMNLP 2025 https://aclanthology.org/2025.emnlp-main.86/ [Search-only] |
| **Human agreement is weak unless judges are large** | 13 judge models: only the largest aligned "reasonably" with humans, and even those could differ by up to 5 points on a scale; high % agreement can hide large score error. | https://aclanthology.org/2025.gem-1.33/ [Search-only] |
| **Agreement ≠ validity** | Multiple judges can agree on the same bias. Survey recommends reporting agreement *with* calibration, position robustness, length/style controls, human-grounded accuracy. | Survey, https://www.sciencedirect.com/science/article/pii/S2666675825004564 [Search-only] |
| **Pairwise multi-judge debiasing** | UDA aligns heterogeneous pairwise judges via consensus; reports up to 63.4% reduction in inter-judge rating variance and 24.7% better human correlation. | AAAI 2026 https://ojs.aaai.org/index.php/AAAI/article/view/40788 [Search-only] |

**Practical protocol for judging CS2 coaching text** (assembled; [Research-supported]):
- Rubric with independently-defined criteria; **permute rubric-option order** (not just A/B answer order) and average.
- Run both A/B orders; measure order-flip rate; **flag unstable pairs** rather than trusting the mean.
- Use ≥2–3 heterogeneous judge families; weight by held-out human agreement if labels exist; keep a small
  human-labelled gold set (50–200 items) to calibrate — never report raw agreement alone.
- Length-match comparisons and run a redundant-expansion control (append filler; a good judge should not change).
- Preference **pairwise** over absolute scoring where possible; keep absolute scores only for tracking.
- Never let the judge know which response is its own.

---

## D. CS2 eval design proposal — PROPOSAL ONLY (not demonstrated anywhere)

No CS2-specific LLM benchmark was found. The design below is mine (status: **Plausible-untested / proposal**).
It is deliberately cheap because ground truth is *derived from the demo*, not human-labelled.

### D0. Principle
Score **structured-state reasoning** and **tool-use reliability** on verifiable items; keep pixel/video
items few, targeted, and scored by small deterministic metrics rather than a judge wherever possible.

### D1. Task families and ground-truth construction
| # | Task | Construction (from parsed demo + round/game state) | Metric | Modality |
|---|---|---|---|---|
| T1 | **State reconstruction** at tick t: positions (±1 m), alive set, HP/armor, economy, utility held | Replay parser = oracle. Ask model to infer from a *compressed* event log, blind to raw positions. | Exact/± tolerance; per-field F1 | structured text |
| T2 | **Event ordering / causality**: which of {plant, execute, rotate, retake, save} happened and in what order per round | Round-level labels from bomb events, buy events, kill feed | Kendall-τ / exact order acc; **frame-shuffle control** (VECTOR-style) | event log + optional video |
| T3 | **Numerical tracking**: count enemies/utility alive over a sequence of frames (REM-style) | Replay counts at each tick | MAE vs oracle; **degradation vs horizon length** | text or frames |
| T4 | **Counterfactual / what-if**: "if CT had kept a player mid, would the A-site retake have been lost?" | Build *paired* replays by perturbing one decision (utility, hold, rotation) in a scripted scenario; run engine/solver or actual alt-round | Accuracy of predicted outcome sign; causal-chain validity via PRISM-style graph score | structured |
| T5 | **Spatial/metric**: distance, line-of-sight, whether a smoke blocks a sightline, crosshair placement | Geometry from parsed positions + map bsp; LOS via ray cast | ±1 m / ±2° tolerance; binary LOS accuracy; **uncommon-viewpoint split** (3DSRBench-style) | structured (positions) vs rendered POV image — compared directly |
| T6 | **Coaching quality (open-ended)**: generate 3 improvement points for a round/player | Rubric + pairwise vs a human-written reference set on a holdout | Rubric score, pairwise win-rate vs baseline coach, **order-permuted + multi-judge** | text output |
| T7 | **Tool-use reliability**: agent must fetch data via tools (query economy, get round, run solver) | τ²-bench analogue: tool schema + policy ("never claim a stat you didn't query") | pass^1 vs **pass^4/^5**; tool-call validity; policy-violation rate | agentic |

### D2. Ground-truth sources (cheapness)
- Parser (awpy/demoparser-class) gives positions, HP, equipment, bomb/economy events → **free oracle** for T1–T3, T5.
- T4: two options — (a) *eventual* counterfactuals: find near-identical round situations where one decision
  differed and extract the observed outcome (cheap, correlational); (b) *interventional*: scripted perturbation
  + deterministic solver/heuristic (more honest, CausalGame-style; more work). Mark (a) as [Research-supported],
  (b) as the stronger variant.
- T6: 100–200 human-written coaching points on a held-out set of rounds; reuse an existing coaching rubric.
- T7: synthetic tool subsets with **injected failures** (tool returns malformed data / times out) to measure recovery.

### D3. Metrics (report all, per τ-bench/Gaia2 practice)
- Verifiable tasks: exact/±tolerance accuracy, MAE, order correlation, horizon-degradation curve.
- Agentic: pass^1 AND pass^k (k=4,5), tool-call validity, policy-violation rate, clarification rate,
  recovery-after-injected-failure rate, median/p95 tool calls, cost per *successful* task.
- Coaching text: rubric score, pairwise win-rate with order permutation + multi-judge, order-flip rate,
  length-matched control, human-agreement on the gold subset.
- **Modality ablation** on the same items: structured-text vs single-image vs N-frame video vs JSON.
  Report accuracy, input tokens, latency, **$ per 1,000 questions**, and end-to-end cost
  (perception + representation + reasoning). Also run **oracle-structured vs predicted-structured** to
  separate perception from reasoning.

### D4. Cheapness levers
- ~95% of items are **text-only** against a parser oracle → cents per item on haiku-class/batch models.
- Use the **Batch API (50% off)** for the bulk run; cache the shared demo context (cached input ≈10% of input price).
- Keep video items to a small stratified slice (e.g. 200–500 clips) at fixed frame budgets (4/8/16/32).
- Precompute all ground truth once per demo corpus; the eval re-runs only the model calls.
- Prefer few strong judges + permutation over many cheap judges for T6.

### D5. Known weaknesses of this proposal
- T4(a) counterfactuals are observational — confounding exactly as CausalGame demonstrates.
- No public CS2 gold-coaching set exists → T6 needs human effort (the only non-cheap part).
- Cross-modality comparisons inherit the "different video ≠ one token count" trap; fix frame budgets.
- Demo/map assets have their own licensing constraints (out of scope here; see sibling slices).

---

## E. Limitations of this section
- Long-video leaderboards (Video-MME, LongVideoBench, LVBench, MLVU) are **stale** w.r.t. the 2026 frontier;
  do not present them as current model rankings.
- Several numbers are [Search-only]: LVBench/MLVU/LongVideoBench leaders, 3DSRBench viewpoint drops, VSI-Bench
  leaderboard, τ-bench pass^8, BFCL per-model scores, GAIA top scores, ChartQA/ChartQAPro/Misleading-ChartQA figures.
- MindCube's own page reports two inconsistent map-then-reason progressions (57.8/61.3 in meta vs 60.76/70.67 in body).
- No benchmark isolates structured-text vs image vs video on identical spatial items with token cost; the
  synthesis in §B is assembled from partial evidence.

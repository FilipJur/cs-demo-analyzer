# §F — API models, gameplay representation, agentic analysis, operating costs

Researched 2026-10-15. Scope: the AI/inference layer of the local-first CS2 demo-analysis &
personal-coaching system. Everything here assumes **commercial APIs only** (no local inference,
no fine-tuned-from-scratch foundation models as a prerequisite). Prices are **USD per 1M tokens**
unless stated. All prices/claims come from primary vendor docs read on 2026-10-15 unless marked
otherwise; the `web_search` tool returns LLM-synthesised summaries, so every number below was
re-verified against the vendor's own pricing/model page.

Category tags used throughout: **[Demonstrated]** vendor doc/repo states it ·
**[Experimental]** vendor beta/preview · **[Research-supported]** papers agree ·
**[Plausible-untested]** no direct evidence · **[Infeasible]** shown not to work.

---

## 0. Executive answer

**Recommended stack (2026-10):**

| Role | Primary | Fallback / bulk |
|---|---|---|
| Deterministic local layer (parse, geometry, visibility, preselection) | `demoparser2` + `awpy` (local, $0) | CS2DemoKit design patterns (.NET, port concept) |
| Cheap bulk pass (classification, tagging, window summarisation, dedupe) | **Grok 4.3** ($1.25/$2.50) or **Gemini 3.8 Flash** ($0.75/$3.75) | Gemini 2.5 Flash-Lite ($0.10/$0.40) batch ($0.05/$0.20) |
| Mid reasoning pass (per-incident decision quality, text+radar) | **Claude Sonnet 5.5** ($2/$10, 1M ctx, 5% cache read) | GPT-6.1 Sol ($2/$10), Gemini 4 Argon ($2/$10 promo) |
| Deep/agentic top pass (cross-incident synthesis, counterfactuals) | **Claude Opus 5.5** ($4/$20) | GPT-6 Astra ($10/$50, 2× above 272K ctx) |
| Vision/video pass (radar renders, short clips) | **Gemini 3.8 Flash / Gemini 4 Argon** (cheapest per image & video token; agentic video mode) | Claude/GPT image input |
| Batch/async bulk (post-match overnight queue) | Batch API on any of the above (**−50%**) | — |

**Per-demo cost range (one player, one match, ~20 flagged incidents):**
- **Lean deterministic-first pipeline (no agent loop, batch): ≈ $0.004–$0.15 / demo.**
- **Realistic recommended pipeline (tiered: cheap preselect + Sonnet-class incident reasoning + radar images + 1 deep synthesis pass): ≈ $0.30–$1.50 / demo.**
- **Full agentic multimodal (strong model tool-loop + clips): ≈ $2–$8 / demo** (and higher if you feed whole-match video or never cap the loop).

The rest of this file justifies those numbers.

**Cheapest credible alternative stack** (if cost dominates): DeepSeek `deepseek-flash` off-peak
(1M ctx, $0.15/$0.60) or Qwen3.8-Flash + batch ($0.075/$0.235) for the bulk text pass, with
DeepInfra Llama-3.1-8B ($0.02/$0.04) for classification — but these have weaker tool-use/structured
reliability and mostly no no-training guarantee, so use them only on non-sensitive data and only for
*description*, not judgement (§4.8).

---

## 1. API model landscape (as of 2026-10-15)

### 1.1 Priced frontier comparison (standard tier, short context)

| Model | Vendor | Input | Cached input | Output | Context | Max out | Ctx premium |
|---|---|---|---|---|---|---|---|
| GPT-6 Astra | OpenAI | $10.00 | $1.00 | $50.00 | 1,050,000 (max in 922K) | 128K | >272K in: 2× in, 1.5× out |
| GPT-6.1 Sol | OpenAI | $2.00 | $0.10 | $10.00 | — | — | >272K: 2×/1.5× |
| GPT-6 Luna | OpenAI | $0.10 | $0.01 | $0.50 | — | — | >272K: 2×/1.5× |
| GPT-5.6 Sol | OpenAI | $4.00 | $0.40 | $20.00 | — | — | — |
| GPT-5.6 Terra | OpenAI | $2.00 | $0.20 | $12.00 | — | — | — |
| GPT-5.6 Luna | OpenAI | $0.20 | $0.02 | $1.20 | — | — | — |
| Claude Fable 5.1 | Anthropic | $10.00 | $0.25 (2.5%) | $50.00 | 1M | 128K | none |
| Claude Mythos 5.1 | Anthropic | $10.00 | $0.25 | $50.00 | 1M | 128K | limited-availability |
| Claude Opus 5.5 | Anthropic | $4.00 | $0.20 (5%) | $20.00 | 1M | 128K (300K batch β) | none |
| Claude Sonnet 5.5 | Anthropic | $2.00 | $0.10 (5%) | $10.00 | 1M | 128K | none |
| Claude Haiku 5.5 | Anthropic | $0.10 | $0.01 | $0.50 | 1M | 128K | >100K prompt: 5× ($0.50/$2.50) |
| Gemini 4 Argon | Google | $2.00* | $0.10* | $10.00* | 1,048,576 | 65,536 (→1M long-decode) | none listed |
| Gemini 3.8 Flash | Google | $0.75* | $0.075* | $3.75* | 1M | — | none listed |
| Gemini 2.5 Pro | Google | $1.25 (≤200K) / $2.50 | $0.125 / $0.25 | $10 / $15 | 1,048,576 | — | >200K: 2× |
| Gemini 2.5 Flash | Google | $0.30 | $0.03 | $2.50 | 1M | — | — |
| Gemini 2.5 Flash-Lite | Google | $0.10 | $0.01 | $0.40 | 1M | — | — |
| Grok 4.7 | xAI | $2.00 | $0.50 | $6.00 | 500K | — | ≥200K: 2× |
| Grok 4.3 | xAI | $1.25 | $0.20 | $2.50 | 1M | — | ≥200K: 2× |

`*` Gemini 4 Argon and 3.8 Flash are on **promotional pricing** that reverts: Argon → $4/$20 and
$0.20 cached on **2026-12-01**; 3.8 Flash → $1.50/$7.50 and $0.15 cached on **2027-01-01**
([pricing](https://ai.google.dev/gemini-api/docs/pricing)). Budget on the *post-promo* number.

Sources: [OpenAI pricing](https://developers.openai.com/api/docs/pricing) ·
[Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) ·
[Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) ·
[xAI pricing](https://docs.x.ai/developers/pricing) (all read 2026-10-15).

### 1.1b Non-frontier / open-weight providers (cheap bulk tier)

Verified from vendor pages 2026-10-15 by the cheap-provider slice; **[V]** = read on the vendor's own
page, **[S]** = secondary source only.

| Provider | Model | in / cached / out | Ctx | Batch | Notes |
|---|---|---|---|---|---|
| DeepSeek | `deepseek-flash` | $0.15 / $0.003 / $0.60 off-peak (peak ×2) | 1M | ✗ | vision ✓, thinking default, JSON, tools |
| DeepSeek | `deepseek-v4-pro` | $0.66 / $0.022 / $1.98 off-peak | 1M | ✗ | **no vision** |
| Alibaba Qwen | `qwen3.8-flash` | $0.15 / — / $0.47 | 1M | **50%** | JSON schema, built-in tools |
| Alibaba Qwen | `qwen3.7-flash` | $0.03 / $0.13 (≤32K) … | 1M | **50%** | cheapest Qwen tier |
| Alibaba Qwen | `qwen3.8-max` | $2 / — / $6 | 1M | — | quality tier |
| Moonshot Kimi | `kimi-k3` | $3.00 / $0.30 / $15.00 | 1M | ✗ | cache writes billed separately |
| Moonshot Kimi | `kimi-k2.6` | $0.95 / $0.16 / $4.00 | 256K | ✗ | |
| Z.ai GLM | `GLM-5.3-Flash` | $0.15 / $0.03 / $0.50 | — | ✗ | |
| Z.ai GLM | `GLM-4.7-Flash`, `GLM-4.6V-Flash` | **free** | — | ✗ | data terms need checking |
| MiniMax | `MiniMax-M3` ≤512K | $0.30 / $0.06 / $1.20 | — | ✗ | priority = 1.5× |
| Mistral | `mistral-large-4` | $0.68 / $0.07 / $2.09 (sale) | — | **50%** | |
| Mistral | `ministral-3b` | $0.10 / — / $0.10 | — | **50%** | cheap Western option |
| Amazon Nova | Micro / Lite / Pro | $0.035/$0.14 · $0.06/$0.24 · $0.80/$3.20 | — | 50% | **[S]**, AWS tables JS-rendered |
| Groq | `openai/gpt-oss-20b` / `120b` | $0.075/$0.30 · $0.15/$0.60 | 131K | **50%** | ~500–1000 tok/s; batch≠cache stacking |
| Cerebras | `gpt-oss-120b` | $0.35 / — / $0.75 | 131K | ✗ | ~3000 tok/s |
| Together | `DeepSeek V4 Flash 0731` | $0.14 / $0.03 / $0.28 | — | ~50% **[U]** | |
| Fireworks | `Nemotron 3.5 Lightning 30B` | $0.05 / $0.01 / $0.20 | — | **50%** | |
| DeepInfra | `DeepSeek-V4-Flash-0731` | $0.06 / $0.015 / $0.18 | 1M | ✗ | |
| DeepInfra | `Llama-3.1-8B-Turbo` | **$0.02 / — / $0.04** | 128K | ✗ | cheapest text in the group |
| Cohere | `command-r7b` | $0.0375 / — / $0.15 | 128K | **[U]** | |
| Perplexity | `sonar` | $1 / — / $1 **+ $5–12/1k requests** | — | ✗ | request fee dominates |

**Cheapest-for-purpose:**
- **High-volume cheap classification:** DeepInfra Llama-3.1-8B ($0.02/$0.04), Qwen3.8-Flash + batch,
  Groq gpt-oss-20b + batch, Fireworks Nemotron Lightning. Free: GLM-4.7-Flash.
- **Large-context structured reasoning:** DeepSeek `deepseek-flash` off-peak ($0.15/$0.60, 1M ctx,
  thinking+tools+JSON) on raw price; Qwen3.8-Flash + batch richest feature set.
- **Image input:** DeepSeek Flash; Z.ai GLM-4.6V-FlashX ($0.04/$0.40).

**Batch availability (important):** 50% batch exists at Alibaba Qwen (select), Mistral, Groq, Bedrock,
Azure, Fireworks, Together, Google and the three frontier vendors. **No batch API found at** DeepSeek,
Kimi, Z.ai, MiniMax, Cerebras, DeepInfra, Perplexity. **Batch and prompt-cache discounts generally do
not stack** (explicit at Groq and Alibaba) — the opposite of OpenAI/Anthropic, which *do* stack.
Resale channels (Bedrock, Azure AI Foundry) mostly track, and sometimes mark up / lag, first-party
prices (e.g. Bedrock DeepSeek v3.2 $0.62/$1.85 vs DeepSeek's own newer, cheaper models).

**Caveat on the cheap tier:** most of these providers publish no API no-training guarantee on their
pricing pages (Kimi, Z.ai, DeepSeek: unstated; DeepSeek's privacy policy permits training with an
opt-out and stores data in the PRC). Use them only for data you are willing to expose, or after a DPA
review. Free tiers (GLM Flash, Google free tier) are the highest risk.

### 1.2 Serving modes = the biggest cost lever after model choice

| Vendor | Async/batch | Cheaper-tier name | Faster-tier premium |
|---|---|---|---|
| OpenAI | **Batch −50%**, 24 h SLA, huge queue limits | **Flex −50%** (same table as Batch) | **Fast 2×**, **Ultrafast 6×** |
| Anthropic | **Batch −50%**, stacks with caching | — | **Fast mode 2×** (Opus 5.5 $8/$40; research preview; not with Batch) |
| Google | **Batch −50%**, 24 h; **Flex −50%** | Flex | **Priority 1.8×** |
| xAI | **Batch −20%** (only grok-4.3 & 4.20 family) | — | **Priority 2×** |

Two non-obvious rules that matter for a demo pipeline:
- **OpenAI/Anthropic/Google batch discounts stack multiplicatively with prompt caching**, so a
  cached, batched prefix can cost ~5% of the uncached standard input price (e.g. OpenAI
  gpt-6-astra cached input $1.00/M → $0.50/M in Batch; Anthropic Sonnet 5.5 cache read $0.10/M →
  $0.05/M in Batch). [Demonstrated]
- **Google's Batch does *not* apply the batch rate to a cache hit** — a cached read in a batch job is
  billed at the *standard* caching rate, not the 50%-off batch input rate. xAI's ZDR and Batch are
  **mutually exclusive** (ZDR disables Batch, Files, Collections, stateful Responses).

### 1.3 Caching

- **OpenAI**: automatic on shared prefix; ≥1024-token prefixes; cached input ≈ 10% of input;
  *cache writes* billed at 1.25× input on newest models (gpt-6-astra $12.50/M write). Extended
  retention knob `prompt_cache_retention: "24h"`. Cache is prefix-exact — put system prompt, tool
  schemas and the per-map rubric **first**, per-demo data **last**. [Demonstrated]
- **Anthropic**: explicit `cache_control` breakpoints or automatic top-level caching; 5-min TTL
  (1.25× write) or 1-h TTL (2× write); reads 10% of input, **5% on Opus 5.5 / Sonnet 5.5**, 2.5% on
  Fable 5.1. Payoff at 1 read (5 min) / 2 reads (1 h). [Demonstrated]
- **Google**: **implicit** caching is automatic on 2.5+ (no control); **explicit** cache objects are
  supported on 2.5 and 3.x **except Gemini 4 Argon, which is implicit-only**. Storage is billed
  separately per 1M tokens/hour ($0.50–$1.00 for 3.8 Flash, $4.50/h for 2.5 Pro) — a long-lived
  cache of a big per-map reference doc can cost more in *storage* than in reads. [Demonstrated]
- **xAI**: automatic prefix cache, cached input $0.20/M (grok-4.3). [Demonstrated]

**Design consequence:** the *stable* part of every request (system prompt + tool schemas + map
rubric + map geometry summary) should be a single cacheable prefix; everything demo-specific goes
after it. For this application the cacheable prefix is large and highly reusable across demos, so
effective cached-input share should be high (target 30–50% of input tokens).

### 1.4 Capability matrix relevant to this project

| Capability | OpenAI | Anthropic | Google | xAI |
|---|---|---|---|---|
| Strict JSON-schema structured output | Yes (Structured Outputs) [Demonstrated] | Yes — `output_config.format` + `strict:true` tools [Demonstrated] | Yes (`responseSchema`) [Demonstrated] | Yes |
| Function/tool calling | Yes (+ hosted shell, code interpreter, computer use, MCP) | Yes (+ strict tool use; **20 strict tools max**, 24 optional params, 16 union params per request) | Yes (+ code execution, file search, Maps/Search grounding) | Yes (+ server-side tools, remote MCP) |
| Reasoning effort control | `low…max` (Astra) | thinking budgets | low/medium/high | none/low/medium/high/xhigh |
| Image input | Yes | Yes | Yes | Yes |
| **Video input** | No (only realtime audio/image/video-generation APIs) | No | **Yes** (static + **agentic** mode) | Yes via `view_x_video` (token-billed), not general |
| Prompt caching | Yes | Yes | Yes (implicit/explicit; Argon implicit-only) | Yes |
| Batch | Yes | Yes | Yes | Yes (20%) |
| Snapshot pinning | Yes (`gpt-6-astra` alias only for latest; older have dated snapshots) | Versioned IDs | Versioned/stable aliases | Dated IDs |

**Video is the decisive differentiator:** only Google takes video as a first-class input for
reasoning. If we ever want "watch the clip" reasoning, Gemini is the only frontier option; every
other vendor is image+text only.

### 1.5 Latency & stability (operationally relevant)

- **Latency tiers** exist at every vendor (OpenAI Fast/Ultrafast, xAI Priority, Google Priority,
  Anthropic Fast mode) but all are 1.8–6× price. For a *post-match*, non-interactive pipeline, never
  pay for them; put bulk work on Batch/Flex.
- **Model churn is real and fast in this window:** `grok-4-0709` was retired 2026-05-15 and silently
  redirected to `grok-4.3` at `low` effort; GPT-5.1 is documented as deprecated; Anthropic retires
  models to Bedrock/Vertex only (Opus 4/4.1, Sonnet 4, Haiku 3.5). [Demonstrated] **Mitigation:**
  pin explicit snapshot strings, keep a per-vendor adapter behind one interface, and re-run a small
  golden set before switching.
- **Reproducibility is genuinely imperfect even at temperature 0** (see §3.3).

### 1.6 Suitability for spatial/temporal/counterfactual gameplay reasoning

**What we can claim from evidence:**
- **Long context is capacity, not capability.** 2025–2026 results consistently show degradation well
  before the advertised window: NoLiMa — 10/12 long-context models fell below 50% of their
  short-context baseline by 32K tokens (arXiv:2502.05167); "Context Length Alone Hurts" — 13.9–85%
  accuracy loss *despite perfect retrieval* (Findings of EMNLP 2025, aclanthology 2025.findings-emnlp.1264);
  "Too Long, Didn't Model" — no tested frontier model kept stable whole-novel understanding past
  ~64K tokens (arXiv:2505.14925); LongBench v2 — best direct-answer model 50.1% vs human experts
  53.7% under a time limit (ACL 2025). **[Research-supported]** → *Do not dump a full demo into 1M
  context. Retrieve and compress.*
- **Positional bias persists** but shifts from classic U-shaped "lost in the middle" to a
  *distance-to-end* effect as inputs approach the window limit (arXiv:2508.07479); filler content
  interference is measurable (76% of middle-position errors matched surrounding filler vs 22% at the
  end, arXiv:2605.23170). **[Research-supported]** → *Put the critical evidence and the question last.*
- **Multi-piece reasoning is worse than single-needle retrieval** (LongPiBench, Findings of ACL 2025;
  "Lost in Decomposition", Findings of ACL 2026). **[Research-supported]** → *Never require the model
  to fuse 20 dispersed incidents in one call; fuse them yourself, or use hierarchical passes.*
- **Self-consistency/voting can fail on long context** because the same positional bias is
  reproduced across samples (TACL 2026, aclanthology 2026.tacl-1.15). **[Research-supported]** →
  *Majority-vote over full demo dumps is not a reliability fix.*

**What is *not* established (treat as [Plausible-untested]):** that any frontier model performs
reliable counterfactual ("what if he backed off") reasoning over tactical geometry. There is no
public benchmark for CS2-scale spatial/counterfactual decision evaluation. That is a gap this
project must close with its own eval (§1.8).

**Practical model-selection implication:** the reason to prefer Claude/GPT/Google *flagships* here is
not "bigger context" but **better tool-use and structured-output reliability at long horizons** —
the model must (a) call the right local tool, (b) emit schema-valid output, (c) not hallucinate
numbers that local code already computes. That is exactly where small/cheap models fail. Hence the
tiered design: cheap models *quote* local facts, expensive models *judge* them.

### 1.7 Benchmarks: what exists, and what it says about CS2

**Current benchmark inventory (verified from primary pages by the benchmark slice, 2026-10-15):**

| Area | Benchmark | Headline result | Relevance |
|---|---|---|---|
| Long-video temporal | **Video-MME**, LVBench, MLVU, LongVideoBench | Long-video-only Video-MME best ≈77.4 (Gemini 1.5 Pro); **leaderboards are stale — newest Video-MME entry 2025-09**, no Gemini 3/4, GPT-6 or Claude 5 rows | Don't quote as current rankings |
| Temporal-order diagnostics | **VECTOR** (arXiv:2512.08979, WACV 2026) | VLMs answer benchmarks fine **even with frames scrambled** → they lean on scene priors, not sequence | Directly analogous to "did the model actually track round order?" |
| State tracking | **Video-MME-Logical** (arXiv:2606.27828, 2026-06) | 5 temporal-logical ops; 500K-sample SFT still insufficient; large human–model gap | Best fit for "can it track evolving match state" |
| Spatial mental models | **MindCube** (arXiv:2506.21458), VSI-Bench (arXiv:2412.14171), 3DSRBench (arXiv:2412.07825) | MindCube chance ≈32; GPT-4o 38.8, Claude-4-Sonnet 44.8 vs a specialised model 90.1. **Feeding a precomputed map *degrades* accuracy (−5.8%)** — structure alone fails. 3DSRBench: uncommon viewpoints drop GPT-4o −13.5% rel | Models are weak at metric/3D relations even with help |
| Trajectory/numerical | **REM** (arXiv:2512.00736, COLM 2025) | Best models unreliable at *moderate* complexity trajectory tracking humans handle easily | "How many enemies alive 4 frames ago" is not safe |
| Counterfactual / what-if | **CausalGame** (arXiv:2607.04293, ICML 2026 Oral) | 14 games, 29 frontier agents: **no model reaches any scenario's win threshold**; 68% of sessions never attempt causal reasoning; more reasoning compute gives no consistent benefit | The single most damning result for "AI coach says you should have done X" |
| Counterfactual (open-form) | **WhatIfBench + PRISM** (arXiv:2608.27953, EMNLP 2026) | Best of 6 frontier LLMs **64.6%**; failure modes: causal gaps, **premise drift**, topology fragmentation | PRISM's graph+rubic split is a reusable scoring template |
| Strategic planning | **SPIN-Bench** (arXiv:2503.12349, COLM 2025) | o1 100% spatial tracking to 29 steps; **no model reaches Hanabi human Q1**; interaction degrades CoT coherence | Hidden-info team games remain unsolved |
| Tool-use reliability | **τ²-bench / τ³-bench** (arXiv:2506.07982; taubench.com), **BFCL V4**, **Gaia2** (arXiv:2602.11964, ICLR 2026 Oral) | τ-bench: GPT-4o **61% pass^1 but <25% pass^8**; Gaia2 best GPT-5 42% pass@1 | **Report pass^k, not pass@1.** Agentic reliability degrades sharply with retries |

**Cross-cutting conclusions for this project:**
1. **Temporal order, metric 3D, state tracking and counterfactual causality are all weakly solved.**
   The model must *not* be the source of positions, counts, or ordering — those come from the local
   deterministic layer.
2. **Counterfactual claims are the highest-risk output** (CausalGame: zero models pass). Treat every
   "you should have" as a hypothesis, score it with a local win-prob / expected-damage model, and
   present it as an option with evidence, not an assertion.
3. **Agentic reliability is a pass^k problem.** Measure and require repeated-run agreement.
4. **Frame-shuffle robustness is a cheap adversarial test** you can port to demos immediately.

### 1.8 CS-specific eval (no off-the-shelf CS benchmark exists — this is a proposal)

Ground truth is cheap because the **parser is an oracle**. Design deliberately puts ~95% of items on
text-only, verifiable tasks run through the Batch API.

| # | Task family | Ground truth | Metric | Modality |
|---|---|---|---|---|
| T1 | **State reconstruction** at tick t (positions, alive set, HP, economy, utility held) | Parser replay | exact/±tolerance, per-field F1 | structured text |
| T2 | **Event ordering / causality** (plant → rotate → retake → save) | Bomb/buy/kill events | Kendall-τ; **frame-shuffle control** (VECTOR-style) | event log (+video ablation) |
| T3 | **Numerical tracking** over a frame sequence | Replay counts | MAE; **degradation vs horizon** (REM-style) | text/frames |
| T4 | **Counterfactual "what if"** (paired perturbed scenarios) | Scripted perturbation + local win-prob/solver; or observed near-identical situations (correlational) | outcome-sign accuracy; PRISM-style causal-graph validity | structured |
| T5 | **Spatial/metric** (distance, LOS, smoke blocking, crosshair placement) | Geometry ray-cast (awpy `VisibilityChecker`) | ±1 m / ±2°; binary LOS acc; uncommon-viewpoint split | structured vs rendered POV image, compared |
| T6 | **Coaching quality** (3 improvement points per round) | Human reference set (100–200 items) | order-permuted multi-judge rubric + pairwise win-rate | text output |
| T7 | **Tool-use reliability** (query economy / get round / run solver under a policy) | τ²-bench analogue + injected tool failures | **pass^1 and pass^4/^5**, tool-call validity, policy-violation rate, recovery rate | agentic |

Also required: a **modality ablation** on identical items (structured text vs single image vs N-frame
video vs JSON-into-image) reporting accuracy, input tokens, latency, `$ per 1,000 questions`, and
end-to-end cost — plus an **oracle-structured vs predicted-structured** split to separate perception
from reasoning. Two of these (T5 and T1's numeric fields) are fully automatable; T6 is the only part
needing human effort.

---

## 2. Gameplay representation spec

### 2.1 Why raw ticks are infeasible (the arithmetic)

A CS2 match (MR12, ~40 min) at **64 demo-ticks/s** ≈ **150,000 ticks**. Dumping full per-tick state
for 10 players × ~25 fields:

```
150,000 ticks × 10 players × 25 fields ≈ 37.5 M values ≈ 244 MB ≈ ~66 M tokens
```

That is **infeasible for every model at every price** (and would also hit the ~64K-token *effective*
reasoning limit from §1.6 by a factor of 1000). Even a 1 Hz downsample of all 10 players × 8 fields
for the whole match is ~187k values ≈ ~330k tokens — technically inside a 1M window, but expensive,
positionally fragile, and *temporally lossy in exactly the place that matters* (sub-second duels).
**Rule: never send raw ticks.** Send events + windows + images.

Note the two-clock trap: CS2 demos carry a **frame index** (from 0) and an **absolute server tick**
(converted via `ServerStartTick`); mixing them "produces results that look plausible and are wrong"
(CS2DemoKit README, §7.2 of peer notes). The representation must pick one clock and convert
explicitly, and every claim must cite that clock.

### 2.2 Layered representation (L0–L5)

**L0 — Match index (≈1–3k tokens).** Map, tickrate, teams, score, per-player identity/role, side
switches, economy summary, list of rounds with (start_tick, end_tick, winner, reason, buy type,
man-advantage timeline). This is the "table of contents" the agent navigates.

**L1 — Round card (≈150–400 tokens each × ~22 rounds ≈ 3–9k tokens).** Per round: buy classification
(full/semi/eco/force, derived from equipment value incl. saved weapons — DemoQueryCS2 uses
≤$5,000 eco / ≤$16,250 semi / else full), the 5v5 opening contacts, first-blood tick, plant/defuse
events, utility thrown (type, tick, thrower, target area), round swing points. **Text only.**

**L2 — Incident window (≈300–1,000 tokens each).** The unit of coaching. An "incident" = an
engagement, a death, a site-execute, a failed retake, a utility cluster. Each window:
- Header: round, tick range, clock (`MM:SS`), side, alive counts, bomb state, economy.
- Per-player rows at **1–4 Hz** only for the involved players (subject + nearest 2–3 enemies + one
  teammate for trade context), only the fields used: `tick, x, y, z, yaw, hp, armor, weapon,
  alive, flashed, in_smoke`.
- Relative geometry (see 2.3) rather than raw world coordinates.
- Derived local facts: distance in units, angle between subject facing and enemy bearing, "was there
  cover", "was the subject exposed to N known enemies", trade availability window.

**L3 — Geometry / visibility / info-state layer.** Not tokens — *local structure* the model queries
via tools:
- **Collision mesh + BVH** for LOS (`awpy.VisibilityChecker` ships first-class with `awpy-data`
  `.mesh` files; CS2DemoKit does the same with `enemy_spotted` rising-edge events). [Demonstrated]
- **Nav mesh** for pathing, area labels and "which node is he in" (DemoQueryCS2 clusters the ~2k–4k
  nav areas into **~100–180 nodes** with a precomputed geodesic distance matrix — a proven, cheap
  design). [Demonstrated]
- **Callout labels** learned from the demos' own `last_place_name` data. [Demonstrated]
- **Fog-of-war / info state**: for each tick, for each player, compute the set of enemies
  *potentially visible* (LOS ∧ FOV ∧ not smoked ∧ alive) and the set *known to the player* (engine's
  own spotted flag if available, plus LOS+FOV). This is the ground truth for T1/T5 (§1.8) and the basis
  of "you could not have known that" vs "you missed the info". **This is the single most important
  derived structure in the system.**
**L3.5 — Player input / intent (optional but uniquely valuable).** CS2 demos carry
`svc_UserCmds` (~90% of all net messages; 1.15 M messages on a 290 MB demo) — view angles, mouse
deltas, button press/release and **sub-tick move steps**. Since ~July 2026 (build 10896) most commands
are sent as Valve delta-encoded patches, so a naive read sees <1% of input (CS2DemoKit
`UserCmdReconstructor` / `SubTickExtractor`). [Demonstrated] This is the only source of *intent* (was
the crosshair already on the angle before the peek? did he counter-strafe?) and is the raw material
for mechanics feedback — but it is high-volume, so it is consumed locally and exposed only through
tools (e.g. `aim_trace`, `counterstrafe_quality`), never dumped into context.

**Visibility is direction-dependent and smoke/door/penetration-sensitive**: `awpy.VisibilityChecker`
models *static* geometry only — "does not model smokes, moving doors, or bullet penetration", and
"player positions are not eye positions". [Demonstrated] So FOV cones, smoke spheres, and eye-height
offsets must be applied in our own layer on top.

**L4 — Radar image (≈560 tokens/image on Gemini).** A top-down render of L2's window on the map's
radar PNG (`awpy-data` ships `radars/<map>.png` + `map_data.json` world→radar transform). Draw:
player markers with facing cones, trails, utility footprints, kill markers, and — crucially — for
fog-of-war renders, **two overlays**: "what the player saw" and "what was actually true". Render at a
resolution that keeps ~1 radar pixel ≈ 1–2 world units at the incident's local scale, cropped to the
area of interest.

**L5 — Clip (≈100 tokens/s low-res, ≈300 tokens/s high-res on Gemini).** Only for the few incidents
where motion/timing *is* the question (crosshair placement, counter-strafe, spray control,
peek timing). 5–15 s, low-res, one clip at a time.

### 2.3 Relative geometry encoding (cheaper and more robust than world coords)

World coordinates (Hammer units, Z-up) are large numbers with map-specific meaning and are hard for a
model to reason about. Encode **relative, quantised** facts instead:

- Subject at origin, subject facing = +Y. Enemy as `(fwd, right, up)` in units, rounded to 10 u.
- **Angle off crosshair** in degrees (signed), not yaw/pitch pairs.
- **Distance bands** (`<64u` knife, `64–256` close, `256–512` mid, `512–1024` far, `>1024` long) —
  CS2 unit scale is 1 unit ≈ 1.9 cm, so 512 u ≈ 9.7 m. `[INFERENCE on exact scale; units are the
  native Hammer unit]`
- **Occlusion verdict** per enemy: `visible` / `occluded` / `smoked` / `not_in_fov`.
- **Cover state**: `in_cover` / `exposed_to(N) enemies` / `peeking_corner`.
- Direction as compass octant **plus** callout name from L3.

This keeps each player-row to ~30–60 characters while preserving the decision-relevant geometry, and
it removes the need for the model to do coordinate arithmetic (which it is unreliable at) — the
*local* code does the arithmetic, the model does the judgement.

### 2.4 Compression, context selection, hierarchical + retrieval

Follow Anthropic's context-engineering guidance (primary source, Sep 2025, updated Jan 2026): find
"the smallest possible set of high-signal tokens"; **compaction**, **structured note-taking**, and
**sub-agent** architectures for long-horizon work; **just-in-time retrieval** (keep lightweight
identifiers, load data on demand) rather than pre-loading everything
([source](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
Concretely, in priority order:

1. **Local preselection drives coverage** (not the LLM). A deterministic scorer ranks candidate
   incidents (see §3.4) and picks a *diverse* top-K, not merely the top-K by a single metric.
2. **Hierarchical pass:** L0/L1 all rounds → cheap model tags each round → escalation only for rounds
   that cross a threshold → L2/L4/L5 only inside escalated incidents. This is the
   map-reduce/compaction pattern and it is what makes the cost line up (§4).
3. **Retrieval ("find my similar situations"):** embed the L2 window (quantised relative geometry,
   economy, bomb state, alive counts) and retrieve k nearest from the player's own history and/or a
   pro corpus. DemoQueryCS2 already demonstrates the *deterministic* version of this: nav-node
   tokens + 18-byte quantised position blobs + geodesic Chamfer scan + exact re-rank
   ([repo](https://github.com/TheBrokas/DemoQueryCS2)). Prefer that over an LLM-embedding for the
   geometry part — it is exact, free, and explainable — and use embeddings only for *textual*
   annotation similarity.
4. **Never re-send what the tool can answer.** Tool schemas (cached prefix) + identifiers, not data.
5. **Place the decision question and the incident payload at the end** of the prompt (recency bias
   is the surviving positional effect, arXiv:2508.07479). Put the system prompt + rubric + tool
   schemas + map primer at the front for cacheability.

### 2.5 When images/video beat structured data (and when they don't)

| Question type | Best modality | Why |
|---|---|---|
| "Where was everyone?" | **Structured** (relative geometry rows) | Exact, cheap, no OCR risk, auditable |
| "Was this a good angle / crosshair placement?" | **Radar image** | Spatial relations are native; text quantisation loses the gestalt |
| "Did he clear that corner / was his path sensible?" | **Radar image** (trail) | Path shape is spatial |
| "Is he exposed to the AWP?" | **Tool call** (LOS), then structured text | Geometry must not be guessed |
| "Was his crosshair on the angle before the peek?" | **Clip** (or aim-trace numbers) | Sub-second motion is not in a 1–4 Hz text window |
| "Was the smoke correct / did it block the site?" | **Radar image** or tool | Smoke footprints are spatial |
| Batch of 20 similar incidents | **Text + one composite image** | Token efficiency; one image can carry many overlays |

Cost reality check (computed from vendor rates):
- Radar image ≈ **560 tokens** → $0.0011 (Argon) / $0.0004 (Flash) per image. 20 images ≈
  **$0.022 / $0.008** per demo. **Cheap enough to use liberally.**
- Low-res video ≈ **100 tokens/s**; **whole 40-min match = 240k tokens** ≈ $0.48 (Argon) /
  $0.18 (Flash 3.8) — *and* it blows past the ~64K effective-context limit. **Never send whole-match
  video.** 20 × 8 s low-res clips = 16k tokens ≈ **$0.032 / $0.012**. That is the right pattern.
- Google's **agentic video mode** loads only the segments needed and claims up to ~88% fewer tokens
  for long-form video ([video docs](https://ai.google.dev/gemini-api/docs/video-understanding)) — but
  it is asynchronous, returns `processing_call`/`processing_result` steps, and in stateless mode you
  must replay all steps to preserve video context. [Demonstrated feature; efficiency % is vendor
  claim — [Plausible-untested] for our workload.]

**Evidence on structured text vs images vs video (assembled — no single clean 3-way study exists):**
- **TRACE** (arXiv:2603.23404, ACL 2026): forcing a model to emit a *text allocentric intermediate
  representation* (context + trajectory + entities) beats direct video reasoning on VSI-Bench and
  OST-Bench. **Structured text can substitute for weak direct video reasoning.** [Demonstrated]
- **Image Prompt Packaging** (arXiv:2604.02492, 2026-04): rendering structured text *into* an image
  cuts tokens 35.8–91.0% (up to 96% compression), but **spatial reasoning, non-English and
  character-sensitive tasks are the most fragile — 10–30 pp accuracy swings from rendering choices
  alone.** Fewer billed tokens ≠ better reasoning. [Demonstrated]
- **Table format studies** (TABVERSE arXiv:2606.09578; "Tables as Texts or Images" arXiv:2402.12424):
  with content held constant, **structured text generally beats a rendered table image**. [Search-only]
- **Chart/coordinate extraction** (CHI'26, arXiv:2606.29808): MLLMs "reconstruct table structure
  reliably but struggle with precise value recovery"; **coordinate-system perception is treated as its
  own training problem** (log axes, large-magnitude ticks). [Demonstrated] → do not route
  coordinates or numbers through pixels.
- **Video pays off only when the answer depends on motion, occlusion/appearance, temporal order or
  navigation** — and it pays a frame-sampling tax. Comparisons must fix a frame budget (4/8/16/32),
  not treat "video" as one token count.

**Verdict:** feed numeric game state as **structured text**; use pixels **only** for genuinely visual
things (smokes, sightlines, crosshair placement, utility arcs); use clips **only** when motion/timing
is the question; never route coordinates or counts through an image. Images are cheap enough (≈$0.0004–0.0011 each) to use liberally as *supplements*, not substitutes.

---

## 3. Agentic analysis

### 3.1 Tool API sketch

All tools are **local, deterministic, read-only**, and return **compact, cacheable, evidence-tagged**
payloads (every payload carries `round`, `tick`, `tick_clock`, and a `source` field so the model can
cite it). Schemas below are illustrative, not final.

```
round_timeline(round:int, player?:int) -> {
  round, buy{t,ct}, events:[{tick, type, actor, target, weapon, headshot, place_name}],
  utility:[{tick, type, thrower, target_node, detonate_tick, damage}],
  swing_points:[{tick, kind, wp_delta}], plant{site, tick}, result
}

trajectory(player:int, tick0:int, tick1:int, hz:int=2, relative_to?:int) -> {
  points:[{tick, t, x, y, z, yaw, hp, armor, alive, flashed, in_smoke, node}],
  geometry:"relative"|"world"
}

snapshot(tick:int, relative_to?:int) -> {
  players:[{id, side, alive, node, place_name, hp, armor, weapon, money,
            rel:{fwd,right,up}, bearing_deg, dist_band, cover_state,
            occluded_by}], bomb{}, economy{}
}

los(a:int, b:int, tick?:int) -> {visible:bool, occluder_plane?:str, distance_units:int}
los_candidates(player:int, tick:int) -> {visible_enemies:[int], blocked_enemies:[int],
                                          not_in_fov:[int], smoked:[int]}

known_enemies(player:int, tick:int) -> {
  engine_spotted:[int], geometry_los:[int], inferred_from_sound:[{enemy, evidence_tick}],
  last_known:[{enemy, tick, node, confidence}]
}

info_state(player:int, tick0:int, tick1:int, hz:int=1) -> {
  frames:[{tick, visible_enemies, seen_ever, uncertain_nodes:[node_id]}],
  fog_render_uri:"local://fog/<id>.png"      # L4 render, "what he knew"
}

trade_calc(victim:int, tick:int, window_ticks:int=192) -> {
  teammates:[{id, dist_units, eta_ticks, los_to_killer:bool, hp, weapon}],
  tradeable:bool, expected_trade_prob:float
}

utility_timeline(round:int, player?:int) -> {
  throws:[{tick, type, click:"L"|"R", stance:"stand"|"run"|"jump", from:{x,y,z},
           target:{x,y,z}, lineup_delta_vs_pro?:{units, degrees}, effect:{damage,
           area_denied_ticks, enemies_blinded_ticks}}]
}

similar_situations(window_id:str, k:int=10, corpus:"self"|"pro"|"both") -> {
  matches:[{match_id, round, tick, similarity:float, geodesic_cost:float,
            outcome:{win, damage_delta}}]
}

render_radar(round:int, tick0:int, tick1:int, overlay:"truth"|"fog"|"both",
             crop:"incident") -> {image_uri:"local://radar/<id>.png", scale_units_per_px:float}

render_clip(round:int, tick0:int, tick1:int, pov:int, resolution:"low"|"high")
             -> {video_uri:"local://clips/<id>.mp4", duration_s:float}

incident_compare(a:window_id, b:window_id) -> {
  deltas:[{field, a, b}], outcome_delta:{...}, note:"deterministic diff only"
}

win_prob(snapshot_tick:int, ...) -> {p_win_t:float, p_win_ct:float, delta_1s:float}

aim_trace(player:int, tick0:int, tick1:int) -> {          # from svc_UserCmds (L3.5)
  samples:[{tick, yaw, pitch, d_yaw, d_pitch, buttons, move_speed, on_ground}],
  derived:{crosshair_placement_deg, reaction_ticks, counterstrafe_quality_0_1,
           spray_deviation_deg, first_bullet_on_target:bool}
}
```

Design rules (from Anthropic's tool-writing guidance, primary source):
- **Minimal, non-overlapping tool set.** If a human engineer can't say which tool to use, the model
  can't either. Keep it to ~8–12 tools; prune aggressively.
- **Token-efficient returns.** Return *verdicts and small tables*, not raw arrays; let a tool do the
  arithmetic.
- **Crisp boundaries.** `los` = geometry only; `known_enemies` = information only. Never let the
  model infer LOS itself if `los` exists — that is where hallucinations come from.
- **Include a `win_prob` tool** so "was this a mistake?" is anchored to a local, consistent number
  rather than the model's vibes.

### 3.2 One-pass vs agentic: trade-offs

| Dimension | One-pass (single big prompt) | Agentic (tool loop) |
|---|---|---|
| Hallucination risk | **High** for numbers/geometry (model must recall or guess positions); lower for generic advice | **Low** for numbers (tools return them); risk shifts to *tool routing* and *over-calling* |
| Cost | Predictable, batchable → **−50%** | Variable, **not batchable**, 3–10× the tokens for the same incident |
| Latency | One call (or 24 h batch) | Seconds–minutes per incident, sequential tool turns |
| Reproducibility | Moderate (single sampling) | Lower — agent trace variance (see §3.3) |
| Coverage / preselection bias | Can look at *everything* if you can afford the tokens (you can't) | Only looks where you point it → bias moves to the preselection stage |
| Debuggability | Opaque prompt → hard to attribute a wrong claim | Every claim traceable to a tool result |

**Recommendation — hybrid, bounded agentic:**
- **Pass 1 (cheap, batch, one-pass):** per round/incident classification and tagging over L1 (text
  only). This is map-reduce over ~20 rounds; batchable; ~50% cheaper.
- **Pass 2 (mid, one-pass per incident, text+radar):** decision-quality judgement for the K flagged
  incidents, with *all* facts pre-injected (no tool loop) — the model only judges. Cheapest way to
  get grounded reasoning.
- **Pass 3 (deep, bounded agentic):** the top 2–5 incidents only. Cap **max tool calls (e.g. 8),
  max turns (e.g. 6), and total tokens per incident**. This is where counterfactuals and cross-match
  similarity run.
- **Never** let an unbounded agent loose on a whole demo: cost is unpredictable and long-horizon
  context degrades anyway (§1.6).

### 3.3 Reproducibility, hallucination, and routing

- **Agent traces are only partially reproducible.** Yagubyan 2026 (arXiv:2605.28840, 1,140 traces,
  6 models): mean **tool-sequence similarity 0.87** but **argument consistency 0.69**, and only
  tool-sequence similarity predicted correctness (d=0.81), while argument consistency did not
  (r=0.12). Mehta 2026 (arXiv:2602.11619): **2.3–4.2 distinct action sequences per 10 identical
  runs**; tasks with ≤2 unique paths scored 82–87% vs 41–65% for ≥4 paths. `[Research-supported]`
  → **Re-run agreement is a usable uncertainty signal** (AUROC 0.62–0.78; agreement over 3 runs →
  87–88% acc at 54–62% coverage).
- **Tool-execution failures create apparent nondeterminism** (arXiv:2608.02645): duplicate side
  effects from blind retries 20%→72% as fault level rises; verify-before-retry + idempotency keys cut
  it to 0–20%. Our tools are read-only, so the main risk is **duplicated expensive calls** — give
  every tool an idempotency key and cache results by `(tool, args_hash)`.
- **Mitigations to implement:**
  1. Temperature low + fixed seed where supported; pin model snapshot.
  2. **All numeric facts come from tools, never from the model.** Post-validate every number in the
     output against the local fact store; auto-flag failures (E6).
  3. **Self-consistency on the judgement only** (3 samples, majority) for the top incidents — but
     *not* by re-sending a huge context (TACL 2026 shows voting fails there); re-sample the *small,
     pre-injected* incident prompt instead.
  4. **Require citations** `(round, tick, tool)` on every claim; reject uncited claims.
  5. **Explicit "insufficient evidence" affordance** — because abstention beats a confident guess, and
     forcing an answer on a weak prompt is where coaching harm occurs. [Research-supported]
  6. Idempotency + result cache on every tool.
- **Measure pass^k, not pass@1.** τ-bench shows GPT-4o at 61% pass^1 collapses to <25% pass^8; τ³-bench
  leaders are ~49–55% pass^1 on hard domains. A single successful demo run proves nothing about
  reliability. `[Research-supported]`
- **Judging coaching text (T6):** no universal judge agreement rate exists — four conflated
  constructs (human alignment, position consistency, repeat-run consistency, inter-judge agreement).
  Position bias is real and worst in near-ties (Shi et al., IJCNLP-AACL 2025, >150k instances);
  **rubric scoring is secretly multiple-choice** so permute *rubric-option* order, not just A/B order
  (arXiv:2602.02219); **self-preference bias does not shrink with capability** (arXiv:2604.22891 —
  structured multi-dimensional judging cuts it ~31.5%). Protocol: pairwise over absolute scoring,
  run both orders, report order-flip rate, ≥2–3 heterogeneous judges, length-matched controls,
  and a small human-labelled gold set (50–200 items) to calibrate. **High agreement ≠ validity.**
- **Routing failure is the main *agentic* risk**, not hallucination. Route deterministically where
  possible: if the question is "was he visible", call `los` in *code* and pass the answer, don't let
  the model choose. Reserve model-driven tool choice for genuinely open exploration.

### 3.4 Preselection bias and hybrid exploration

The clean one-pass pipeline has no preselection bias but is unaffordable; any preselector biases what
the coach ever sees. Mitigations:

1. **Multi-axis preselection, union not intersection.** Score incidents on independent axes
   (local win-probability swing, damage delta vs expectation, isolation, untraded death, utility
   waste, positioning-vs-pro-prior, repetition within the player's own history) and take the **union**
   of each axis's top few. A single composite score hides whole categories of error.
2. **Always include a random sample** (e.g. 2 rounds) as an unbiased control; report per-axis coverage
   so systematic blind spots are visible.
3. **Recurrence weighting:** an incident type that repeats across matches is more valuable than a
   one-off spectacular round (this is the "unconscious habit" detector). Score
   `value ∝ impact × recurrence_frequency`.
4. **Let the agent explore beyond the preselector** on a budget: one or two `round_timeline` /
   `similar_situations` calls are allowed to *pull in* rounds the preselector missed. This is the
   "just-in-time retrieval" hybrid in Anthropic's guidance.
5. **Audit loop:** periodically run the expensive pipeline on preselector-rejected incidents and
   measure how often they'd have been flagged. Track that as a metric.
6. **Never announce a "top mistake" from a single incident**; require recurrence or high impact.

---

## 4. Operating-cost model

### 4.1 Volume assumptions (documented, so they can be tuned)

| Parameter | Assumption |
|---|---|
| Match | MR12, ~21–24 rounds, ~40 min |
| Demo tickrate | 64 demo-ticks/s (FACEIT demos are often 64 even on 128-tick servers) → ~150k ticks |
| Flagged incidents / demo | ~20 (L2 windows) |
| Escalated incidents / demo | 2–5 (agentic pass) |
| Radar images / demo | ~20 (one per incident) |
| Clips / demo | 0–5 (only mechanics questions) |
| Cacheable prefix | system prompt + rubric + tool schemas + map primer, ~6–8k tokens |

### 4.2 Per-demo token budget by pipeline tier

| Tier | Uncached in | Cached in | Output | Notes |
|---|---|---|---|---|
| **A** lean text (cheap model, batch) | 30k | 6k | 9k | L0+L1 all rounds + L2 text for 20 incidents, one-pass |
| **B** + radar images (mid model) | 42k | 6k | 12k | A + 20 radar images (560 tok each) |
| **C** agentic-mid (strong model) | 60k | 25k | 30k | 20 incidents, bounded tool loop (≤4 calls each) |
| **D** agentic-deep (frontier) | 90k | 40k | 45k | C + counterfactuals, clips, cross-match retrieval |

### 4.3 Per-demo cost (USD), from vendor rates

Batch applies to A/B (async-capable); C/D are interactive agent loops so priced standard.

| Model | A lean | B +radar | C agentic-mid | D agentic-deep |
|---|---:|---:|---:|---:|
| GPT-6 Luna | **0.004** | 0.005 | 0.021 | 0.032 |
| Claude Haiku 5.5 | **0.004** | 0.005 | 0.021 | 0.032 |
| Gemini 3.8 Flash | 0.028 | 0.038 | 0.159 | 0.239 |
| Grok 4.3 | 0.031 | 0.042 | 0.155 | 0.233 |
| Grok 4.7 | 0.059 | 0.080 | 0.312 | 0.470 |
| GPT-6.1 Sol | 0.075 | 0.102 | 0.422 | 0.634 |
| Claude Sonnet 5.5 | 0.075 | 0.102 | **0.422** | 0.634 |
| Gemini 4 Argon | 0.075 | 0.102 | 0.422 | 0.634 |
| Claude Opus 5.5 | 0.151 | 0.205 | 0.845 | 1.268 |
| GPT-6 Astra | 0.378 | 0.513 | 2.125 | **3.190** |

### 4.4 Volume estimates (USD)

Recommended **tiered** pipeline = A(cheap, all rounds) + C(Sonnet-class, flagged incidents) +
occasional D. Below: pure-tier figures so the envelope is clear.

| Demos | A (Luna) | B (Haiku) | C (Sonnet 5.5) | D (Astra) |
|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.01 | 0.42 | 3.19 |
| 10 | 0.04 | 0.05 | 4.22 | 31.90 |
| 50 | 0.19 | 0.26 | 21.12 | 159.50 |
| 100 | 0.38 | 0.51 | 42.25 | 319.00 |

**Recommended real pipeline** (A over all rounds + C on ~20 incidents + B-images + 2 D-passes on the
top incidents) lands at roughly **$0.40–$1.20 per demo**; heavy agentic multimodal use reaches
**$2–$8**. Provider choice for the mid tier matters more than the cheap tier (Sonnet 5.5 = Argon =
GPT-6.1 Sol at $2/$10; Grok 4.3 is 3× cheaper at $1.25/$2.50 and is the value pick for the mid tier
if its judgement quality holds on the CS eval).

**Ongoing history (per active player):** a player playing 20 demos/month at $0.50–$1.50/demo =
**$10–$30/month per active player** for analysis, before any cross-match/corpus work. Cross-match
retrieval over the *deterministic* similarity index (§2.4) is free; only the LLM narration costs
tokens.

### 4.5 Cost-control checklist

1. **Batch/Flex everything that isn't interactive** — flat −50% at OpenAI/Anthropic/Google, Mistral,
   Groq, Fireworks, Alibaba (select), Bedrock, Azure. **Check stacking:** OpenAI/Anthropic/Google
   stack batch with caching; **Groq and Alibaba explicitly do not**; xAI's batch is only −20% and is
   mutually exclusive with ZDR. No batch API exists at DeepSeek, Kimi, Z.ai, MiniMax, Cerebras,
   DeepInfra, Perplexity.
2. **Cache the stable prefix** aggressively; aim for 30–50% cached share. Note Google bills cache
   *storage* hourly and does not discount cache reads inside Batch — prefer Anthropic/OpenAI caching
   if the prefix is huge and long-lived.
3. **Incremental analysis:** store per-round/per-incident analyses keyed by `(demo_hash, round,
   model_version, prompt_version)`. Re-analysis after a prompt tweak should re-run only the affected
   incidents.
4. **Tiered models:** cheap model for tagged/summarised/classified work; expensive only for judgement
   on flagged incidents.
5. **Hard spend caps:** per-demo token budget (abort/fallback if exceeded), per-day USD cap,
   max tool calls / turns per agent run, max clips.
6. **Deduplicate similar incidents** before spending: cluster the 20 flagged incidents and analyse
   one representative per cluster at the expensive tier.
7. **Don't send video** unless the question is unanswerable from structured data (see §2.5).
8. **Watch the promo cliffs:** Gemini Argon/Flash prices nearly double on 2026-12-01 / 2027-01-01.
   Build the cost model on post-promo rates.

### 4.6 Fine-tuning / pretrained game embeddings (note only — no training prerequisite)

- **Fine-tuning is not a prerequisite and is arguably the wrong lever here.** The reliability problem
  (hallucinated numbers, wrong tool routing) is solved by *tools + validation*, not by fine-tuning.
- **OpenAI is winding down its self-serve fine-tuning platform** — no longer open to new users;
  existing users can create training jobs "for the coming months"; fine-tuned models stay for
  inference until base deprecation ([pricing page](https://developers.openai.com/api/docs/pricing)).
  This rules out a new FT-based plan. [Demonstrated]
- **Google's Gemini API no longer supports fine-tuning** (1.5 Flash-001 deprecated May 2025);
  supervised tuning lives in the enterprise platform. [Demonstrated]
- **Open-weight FT is cheap if ever needed**, with **Fireworks** (LoRA $0.50/M ≤16B; $3/M 16–80B;
  $6/M 80–300B; $10/M >300B — and **serves fine-tuned models at base-model price**) and **Together**
  (LoRA SFT from **$0.34/M** ≤9B, min $4–60/job) the two realistic hosted paths. Alibaba does SFT/CPT/DPO
  (~$1.60/M) but bills a separate deployment. **Anthropic, xAI, Z.ai, MiniMax, Groq, Cerebras and hosted
  DeepSeek publish no FT offering.** But nothing in this project *needs* FT.
- **Embeddings (cheapest first):** Fireworks ≤150M-param **$0.008/M** · Voyage `voyage-4-lite`
  **$0.02/M** (200 M free) · OpenAI `text-embedding-3-small` **$0.02/M** (ZDR-eligible) · Alibaba
  `text-embedding-v4` $0.07/M · Cohere Embed 5 Fast $0.08/M · Mistral `mistral-embed` $0.10/M ·
  OpenAI `text-embedding-3-large` $0.13/M · Google `gemini-embedding-2` **$0.20/M** (25× Fireworks).
  Voyage batch is −33% with a 12 h window; Voyage `voyage-context-4`/`voyage-code-4` are plausible
  fits for demo event sequences. **No first-party embeddings at Anthropic, xAI, DeepSeek, Z.ai,
  MiniMax, Moonshot, Groq, Cerebras.**
- **Game-specific embeddings:** there is no pretrained CS2 tactical embedding. The practical
  substitute is the **deterministic similarity index** (nav-node tokens + quantised position blobs +
  geodesic Chamfer, per DemoQueryCS2) — exact, free, explainable — optionally combined with a text
  embedding for the coaching prose. Generic embeddings of raw positions are [Plausible-untested] and
  likely worse than the deterministic index.

### 4.7 Data retention & privacy per provider (for a personal but sensitive tool)

Full per-provider detail is in the peer retention slice; the decisive facts:

| Provider | Default retention | Trains on API data by default? | ZDR | Notes |
|---|---|---|---|---|
| OpenAI | 30 d abuse logs | **No** (since 2023-03-01) | **Approval-gated** (sales); some endpoints (batch, files, vector stores, FT) ineligible | **Batch is ZDR-ineligible** |
| Anthropic | 30 d (UP-violating 2 y; T&S scores 7 y) | **No** | **Sales-approval-gated**, per org | **Batch = 29-day retention, ZDR-ineligible** |
| Google Gemini API | Paid: ~55 d max logs. **Free: used to improve + human review** | **Free tier: YES**; paid: no; Contributor: yes (opt-in) | Pay to avoid training; no toggle | **Paid tier required for user-facing apps in EEA/CH/UK** |
| Google Vertex | logging off by default; durable cache ≤24 h; `store` defaults true | **No** | Yes on request (abuse-monitoring exception + disable caching/`store`) | **Grounding-with-Search = no ZDR possible** |
| xAI | 30 d encrypted | **No** | **Self-serve, team-wide**; header `x-zero-data-retention` | ZDR **disables Batch entirely** |
| DeepSeek | Not published; PRC-processed | **Yes, "may be"** (User Input listed as training data; email opt-out only) | No ZDR product | Do not send player-identifying data |
| Alibaba Model Studio | ≤30 d (stateful until deleted) | **No** | Enterprise + account manager, workspace-level, model allow-list | **Batch excluded from ZDR** |
| Moonshot/Kimi | Not fixed; Singapore | **Ambiguous** — policy says content used to train/refine; ZDR page says enterprise not trained | Enterprise on request | **Batch + File media excluded from ZDR** |
| Z.ai (GLM) | API content processed in real time, not stored **[R]** | **No for API/enterprise** (ToS §IV.7) | Not published | Singapore law |
| MiniMax | Not fixed | **No blanket no-training promise** | Not published | US DC; bars HIPAA/ITAR |
| Mistral | Not stated | **Not concluded** (consumer plans show opt-out) | Not documented | Classifier FT only |
| **Groq** | As needed; delete ≤30–180 d post-termination | **No** — contractual ("not permitted to use Inputs or Outputs for training or fine-tuning") | **Self-serve "zero data retention setting"** | Batch 50%, doesn't stack with caching |
| **Together** | Settings-controlled | **No** — explicit opt-in required | **Self-serve ZDR toggle** | |
| **Fireworks** | **Zero retention by default** (volatile memory only) | **No** | **Default ZDR**; admin can enforce reject-if-persist | Best privacy+cost posture in the cheap tier; Responses `store=true` = 30 d |
| Cerebras | Does not retain I/O | No explicit statement ⇒ effectively no | Not documented | Inference-only |
| Voyage (embeddings) | Files auto-deleted after 30 d | Not stated **[P]** | n/a | Anthropic-recommended embeddings |

**Implications:**
- Demo files contain Steam IDs, names, voice/text chat and (if clips are uploaded) video — treat as
  personal data. Prefer providers with a no-training default; **never synthesise the pipeline around
  Google's free tier**; do not send identifying data to DeepSeek/MiniMax/Moonshot/Z.ai without a
  confirmed opt-out.
- **Strict "nothing retained" and Batch are mutually exclusive at OpenAI, Anthropic, xAI, Alibaba and
  Moonshot** — exactly the providers where the 50% discount would otherwise matter most. If ZDR is a
  hard requirement, the async bulk pass must use Vertex, Fireworks, or (by config) Together, or run
  synchronously on a ZDR-eligible path. `[INFERENCE]` This is a compliance-driven architecture
  constraint worth stating before choosing vendors.
- **Valve/Steam terms, not AI-provider terms, are the binding constraint on the CS2 side.** The Steam
  Web API ToS prohibits creating functionality that gives a user an unfair competitive advantage in
  multiplayer, and Valve's site terms limit demo use to personal, single-session use. The defensible
  posture is **personal, local-first, post-match, own-demos-only**, parsing with an existing OSS
  parser rather than inspecting `cs2.exe`. (See the peer legal/retention slice; not legal advice.)

### 4.8 Cheapest viable configuration

If cost must be minimised at the expense of judgement quality, a fully-batchable,
structured-text-only pipeline is possible well under $0.01/demo: cheap-tier model
(DeepInfra Llama-3.1-8B $0.02/$0.04, Qwen3.8-Flash+batch $0.075/$0.235, or DeepSeek Flash off-peak
$0.15/$0.60) over the L0/L1/L2 text representation, with local code doing all arithmetic. This
produces *grounded descriptions*, not *judgement* — it cannot do counterfactuals and should not be
presented as coaching. The recommended pipeline deliberately spends on the mid tier precisely because
judgement is the product.

### 4.9 Sources of evidence for this section

Model/pricing facts were read from vendor primary docs on 2026-10-15 (OpenAI, Anthropic/Claude
Platform, Google/Gemini, xAI, DeepSeek, Alibaba Model Studio, Moonshot, Z.ai, MiniMax, Mistral,
Groq, Cerebras, Together, Fireworks, DeepInfra, Cohere). Benchmark and paper claims cite arXiv/ACL
IDs inline. Local-tooling facts (`awpy`, `demoparser2`, CS2DemoKit, DemoQueryCS2) are from the
ecosystem slice and the repos' own docs. Anything not marked [Demonstrated] should be re-verified
before it is load-bearing.

---

## 5. Recommended architecture (summary)

1. **Local deterministic core** (`demoparser2` + `awpy`, SQLite): parse → nav-map to ~100–180 nodes →
   BVH visibility → fog-of-war info state → incident detection → relative-geometry windows. No LLM
   involved. This is where correctness and reproducibility live.
2. **Tier A (cheap, batch):** cheap model (Grok 4.3 / Gemini 3.8 Flash / GPT-6 Luna) tags and
   summarises every round from L1 text. ~$0.004–$0.04/demo.
3. **Tier B/C (mid, one-pass per incident with pre-injected facts + radar image):** Claude Sonnet 5.5
   (or GPT-6.1 Sol / Gemini 4 Argon / Grok 4.3) judges decision quality, citing `(round, tick, tool)`.
   ~$0.10–$0.42/demo at ~20 incidents.
4. **Tier D (bounded agentic, top 2–5 incidents only):** Opus 5.5 / GPT-6 Astra with a capped tool
   loop for counterfactuals, clip review, and cross-match similarity. ~$0.85–$3.20/demo.
5. **Validation gate on every output:** all numbers re-checked against the local fact store;
   uncited claims rejected; optional 3-sample agreement on judgements. T1/T5 and the hallucination
   check of the CS eval (§1.8) run on every model/prompt change.
6. **Provider abstraction** behind one adapter, pinned snapshots, prompt/version hashing for
   incremental re-analysis, hard per-demo and per-day spend caps.

**Bottom line per-demo cost range: $0.004 (lean deterministic-first, batch, cheap model) to $3.20
(frontier agentic-deep), with the recommended tiered pipeline at ≈ $0.40–$1.50 per demo.**

---

## 6. Open questions / risks

- **No CS-specific benchmark exists** → the proposed T1–T7 eval (§1.8) is a *proposal*, not
  demonstrated. Building it is prerequisite to trusting any model choice.
- **Counterfactual judgement is unvalidated** for every model (CausalGame: 0/29 agents above the win
  threshold); treat all "you should have done X" output as a hypothesis until T4 is built.
- **Agentic reproducibility is inherently partial** (0.87 tool-sequence / 0.69 argument consistency);
  design for *agreement metrics*, not bit-exact reruns.
- **Gemini Argon cache is implicit-only** and its price nearly doubles 2026-12-01 — a cost-model
  cliff.
- **Vendor model churn** (retirements, silent redirects) means the adapter + golden-set re-run is
  mandatory, not optional.
- **Vendor ToS on game video/telemetry** (Valve/Steam, FACEIT) is not settled in this file; see the
  acquisition/legal slice.

---

## 7. Key sources

**Vendor pricing / capability docs (read 2026-10-15):**
- OpenAI pricing — https://developers.openai.com/api/docs/pricing · models — https://developers.openai.com/api/docs/models · GPT-6 Astra — https://developers.openai.com/api/docs/models/gpt-6-astra · prompt caching — https://developers.openai.com/api/docs/guides/prompt-caching · batch — https://developers.openai.com/api/docs/guides/batch
- Anthropic pricing — https://platform.claude.com/docs/en/about-claude/pricing · data retention — https://platform.claude.com/docs/en/manage-claude/api-and-data-retention · structured outputs — https://platform.claude.com/docs/en/build-with-claude/structured-outputs · context engineering — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (published 2025-09-29, updated 2026-01-06)
- Google Gemini pricing — https://ai.google.dev/gemini-api/docs/pricing · Gemini 4 Argon — https://ai.google.dev/gemini-api/docs/models/gemini-4-argon · video understanding (agentic mode) — https://ai.google.dev/gemini-api/docs/video-understanding · terms — https://ai.google.dev/gemini-api/terms
- xAI pricing — https://docs.x.ai/developers/pricing · security/ZDR — https://docs.x.ai/developers/faq/security
- DeepSeek — https://api-docs.deepseek.com/quick_start/pricing · https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html
- Alibaba Model Studio — https://www.alibabacloud.com/help/en/model-studio/model-pricing · Moonshot/Kimi — https://platform.kimi.ai/docs/pricing/chat · Z.ai — https://docs.z.ai/guides/overview/pricing · MiniMax — https://platform.minimax.io/docs/guides/pricing · Mistral — https://docs.mistral.ai/inference/pricing · Groq — https://console.groq.com/docs/models · Cerebras — https://inference-docs.cerebras.ai/models/overview · Together — https://www.together.ai/pricing · Fireworks — https://docs.fireworks.ai/serverless/pricing · DeepInfra — https://deepinfra.com/pricing · Voyage — https://docs.voyageai.com/docs/pricing

**Benchmarks & papers (arXiv/ACL IDs cited inline; URLs):**
- NoLiMa https://arxiv.org/abs/2502.05167 · Context Length Alone Hurts https://aclanthology.org/2025.findings-emnlp.1264/ · Too Long Didn't Model https://arxiv.org/abs/2505.14925 · LongBench v2 https://aclanthology.org/2025.acl-long.183/ · LongPiBench https://aclanthology.org/2025.findings-acl.28/ · Positional biases shift https://arxiv.org/abs/2508.07479 · Positional failures https://arxiv.org/abs/2605.23170
- VECTOR https://arxiv.org/abs/2512.08979 · Video-MME-Logical https://arxiv.org/abs/2606.27828 · Video-MME https://video-mme.github.io/home_page.html · LVBench https://lvbench.github.io/ · MLVU https://github.com/JUNJIE99/MLVU
- MindCube https://mind-cube.github.io/ · https://arxiv.org/abs/2506.21458 · VSI-Bench https://arxiv.org/abs/2412.14171 · 3DSRBench https://arxiv.org/abs/2412.07825 · REM https://arxiv.org/abs/2512.00736
- CausalGame https://arxiv.org/abs/2607.04293 · WhatIfBench/PRISM https://arxiv.org/abs/2608.27953 · SPIN-Bench https://arxiv.org/abs/2503.12349
- τ²-bench https://arxiv.org/abs/2506.07982 · τ-bench https://arxiv.org/abs/2406.12045 · τ³ leaders https://taubench.com/ · BFCL V4 https://gorilla.cs.berkeley.edu/leaderboard · Gaia2 https://arxiv.org/abs/2602.11964
- TRACE https://arxiv.org/abs/2603.23404 · Image Prompt Packaging https://arxiv.org/abs/2604.02492 · Tables-as-texts-or-images https://arxiv.org/abs/2402.12424 · TABVERSE https://arxiv.org/abs/2606.09578 · Chart extraction (CHI'26) https://arxiv.org/abs/2606.29808
- Agent reproducibility https://arxiv.org/abs/2605.28840 · behavioural consistency https://arxiv.org/abs/2602.11619 · verified tool calls https://arxiv.org/abs/2608.02645 · judge position bias https://aclanthology.org/2025.ijcnlp-long.18/ · rubric-option order https://arxiv.org/abs/2602.02219 · self-preference https://arxiv.org/abs/2604.22891

**Local tooling (from the ecosystem slice / repos):**
- awpy — https://github.com/pnxenopoulos/awpy · visibility & map data — https://awpy.readthedocs.io/en/stable/visibility.html
- demoparser2 — https://github.com/LaihoE/demoparser · CS2DemoKit — https://github.com/CS2OpenDev/CS2DemoKit
- DemoQueryCS2 — https://github.com/TheBrokas/DemoQueryCS2 · ggViz paper — https://arxiv.org/abs/2107.06495


# Data retention / privacy + fine-tuning / embedding pricing for a personal CS2-coaching tool

Slice owner: `AIModelsArchCosts.RetentionFinetune`. Researched 2026-10-15.
All prices USD per 1M tokens unless noted. Claim tags:

- **[D]** = Demonstrated (vendor's own doc/pricing page states it; quoted/paraphrased from primary URL).
- **[E]** = Experimental (vendor offers it as beta/preview).
- **[R]** = Research-supported (derived from docs by reasoning, or from a secondary summary of a vendor page I could not render).
- **[P]** = Plausible-untested (not confirmed).
- **[X]** = Infeasible / vendor has no such offering.

**Method note:** every number below was read from the vendor's own pricing/docs page via `read` unless explicitly tagged [R] (secondary summary) or [P]. Where a vendor page is JS-rendered and would not expose tables (Cohere, MiniMax, Cerebras pricing), that is flagged.

---

## 0. Master table

| Provider | Default API retention | API data used for training by default? | ZDR available? / how | Enterprise / DPA | Fine-tuning offered | Cheapest embedding $/M |
|---|---|---|---|---|---|---|
| **OpenAI** | 30 d abuse-monitoring logs (some endpoints 0 d) | **No** (since 2023-03-01) | Yes — **approval-gated**; MAM or ZDR via sales, configured per org/project | DPA, BAA addendum, data residency (10% uplift), non-US needs MAM+amendment | **Winding down**; only existing users can still run jobs | text-embedding-3-small **$0.02**; -large **$0.13** |
| **Anthropic** | 30 d inputs/outputs; UP-violating content 2 yr; T&S scores 7 yr; feedback 5 yr | **No** | Yes — **sales approval**, per organization (not Console); `api.anthropic.com` eligible features only | BAA/HIPAA-readiness self-serve in Console; DPA | **None** [X] (no FT in API pricing page) | none (no 1st-party embeddings) [X] |
| **Google Gemini API (AI Studio)** | Paid: abuse logs "limited period"; logs/datasets opt-in 55 d default. Free: used to improve + human review | **Free tier: YES**. Paid: no. Contributor tier: yes (opt-in discount) | Not a per-customer ZDR toggle; pay to avoid training. EEA/CH/UK must use Paid tier for user-facing apps | DPA (CDPA); Verified via terms | **API: no FT** (1.5 Flash-001 deprecated); FT lives in Gemini Enterprise Agent Platform | gemini-embedding-2 text **$0.20** (batch $0.10) |
| **Google Vertex / Gemini Enterprise Agent Platform** | abuse logs (request exception for ZDR); request/response logging off by default; durable cache ≤24 h; Interactions API `store` defaults true | **No** ("Training Restriction": won't train w/o permission) | **Yes, on request** via abuse-monitoring exception + disabling caching/`store`; Grounding-with-Search = **no ZDR possible** | CDPA; data residency; CMEK not supported for durable cache | **Yes** — supervised/RL/preference tuning (Gemini 2.5/3.5 + open models) | same gemini-embedding prices |
| **xAI** | 30 d encrypted at rest (audit) | **No** | Yes — **self-serve** in Console, team-wide; header `x-zero-data-retention`; disables Batch/Files/stateful Responses | Enterprise Terms, SOC 2 Type 2, BAA questionnaire; US endpoint +10% | **None** [X] | none [X] |
| **DeepSeek** | Not fixed/published; account-lifetime for inputs/payment | **Yes, may be** — policy lists User Input as training data; **opt-out right** | No ZDR product; only privacy@ email requests | PRC-processed; no DPA/ZDR commitment found | **None hosted** [P] (open weights) | none [X] |
| **Qwen / Alibaba Model Studio (DashScope)** | Prompts/responses ≤30 d; stateful until deleted | **No** ("does not use customer data for model training") | **Yes** — enterprise, Intl site, account manager; workspace-level; ZDR-covered model list (Qwen/DeepSeek-pro/GLM emb) | Intl-site Privacy Policy; ZDR excludes Batch/RAG/apps/Playground/Responses-API | **Yes** SFT / CPT / DPO (per-token price) | text-embedding-v4 **$0.07** |
| **Moonshot / Kimi** | Not a fixed period; account-life for inputs; violation data until resolved; Singapore storage | **Ambiguous**: Privacy Policy says content used to train/refine; ToS says content may be used unless separately agreed; ZDR page says enterprise not trained by default | **Yes** on request to **enterprise**; Batch API + File-Upload images/video excluded | Singapore law; no public DPA/ZDR self-serve | **Enterprise only** (no public price) [R] | none [X] |
| **Z.ai (GLM)** | API content processed in real time, not stored on servers [R]; ops/log/billing data unspecified | **No for API/enterprise** (ToS §IV.7: won't use your content to develop/improve unless you explicitly agree); consumer = yes | Not published (DPA states no storage) [R] | Governed by Singapore law; US terms bar HIPAA/GLBA/ITAR data | None [P] | none [X] |
| **MiniMax** | No fixed published period; US data center; "as long as necessary" | **No blanket no-training promise**; permits anonymised/de-identified use & service development | No published ZDR [R] | US region bars HIPAA + ITAR | None found [P] | none [X] |
| **Mistral** | Not stated on pricing; API governed by Mistral privacy/DPA | API: not concluded [P]; consumer plans show "Opt-out" toggle | Not documented [P] | DPA available | **Deprecated** general FT; classifier FT only ($1/M, min $4, $2/model/mo) | mistral-embed **$0.10**; codestral-embed **$0.15** |
| **Groq** | "As necessary to provide the Cloud Services"; post-termination delete ≤30 d (SA) / ≤180 d (DPA) | **No** — "not permitted to use Inputs or Outputs for training or fine-tuning … unless explicitly granted permission" | Yes — **self-serve** "zero data retention setting" in Console for eligible customers | DPA (Oct 2025), BAA, Groq Services Agreement, SCCs | No self-serve FT; may host customer-supplied FT models at Groq's discretion | none [X] |
| **Together AI** | Not a fixed period; settings-controlled | **No** — "We do not use any data collected from you to train our models without your explicit opt-in" | **Yes, self-serve** — Privacy & Security settings "No" ⇒ ZDR | DPA/SCCs; GDPR/CCPA sections | **Yes** — LoRA + full SFT/DPO | serverless embeddings currently **not offered** [R] (historical $0.008) |
| **Fireworks AI** | **Zero retention by default** for open-model inference (prompts/outputs in volatile memory only) | **No** — "no AI training on your data" without opt-in | **Default ZDR**; enterprise admins can enforce reject-if-persist; Responses API `store=true` retains 30 d (set false) | Privacy Notice + ToS; trust center; enterprise ZDR policy | **Yes** — LoRA + full SFT/DPO, managed + serverless trainer | params ≤150M **$0.008**; 150–350M **$0.016**; Qwen3 8B **$0.10** |
| **Cerebras** | "Do not retain inputs and outputs associated with our training, inference and chatbot Services"; logs deleted when no longer needed | No explicit training statement; no retention of I/O ⇒ effectively no training on it [R] | Not documented [P] | Enterprise by agreement; partners (AWS, OpenRouter, HF, Vercel) | None [X] (inference-only) | none [X] |
| **Voyage AI** (Anthropic-recommended embeddings) | Files API files auto-deleted after 30 d; embedding requests not retained (not stated) [P] | Not stated on pricing page [P] | n/a | sales for fine-tuned/dedicated | **Fine-tuned embeddings**: sales only | voyage-4-lite **$0.02**; voyage-4 **$0.06**; voyage-4-large **$0.12** |
| **Cohere** | Not read (page JS-rendered) | Not read | Model Vault / private deployment available | Enterprise; HIPAA page exists | Not read | Embed 5 Fast **$0.08** [R]; Embed 5 Pro / v4 **$0.12** [R] |

---

## 1. Frontier providers — detail

### 1.1 OpenAI
Sources: `https://developers.openai.com/api/docs/guides/your-data` **[D]**; `https://developers.openai.com/api/docs/pricing` **[D]** (both read 2026-10-15).

- **Retention** [D]: abuse-monitoring logs default **30 days** for essentially every endpoint; `/v1/audio/transcriptions|translations` and `/v1/moderations` = **no** retention. Application state "until deleted" on `/v1/files`, `/v1/fine_tuning/jobs`, `/v1/batches`, `/v1/evals`.
- **Training** [D]: API data **not used to train** as of 2023-03-01 unless you explicitly opt in.
- **ZDR** [D]: **approval-gated** (prior approval + additional requirements, via sales). Two flavours: **Modified Abuse Monitoring (MAM)** and **Zero Data Retention**. ZDR forces `store=false`. **ZDR-ineligible endpoints/features**: `/v1/conversations*`, `/v1/chatkit/threads`, `/v1/agents`, `/v1/assistants`, `/v1/threads*`, `/v1/vector_stores`, `/v1/files`, `/v1/fine_tuning/jobs`, **`/v1/batches`**, `/v1/evals`, `/v1/audio/voices`. Extra ZDR variants: "Private Retention with PSP" (fka Eyes Off) and "Safety Retention".
- **Data residency** [D]: project-level region selection; **10% price uplift** on models released ≥2026-03-05; non-US regions additionally require MAM/ZDR approval + a Modified Retention amendment.
- **Batch vs ZDR** [D]: Batch is **not ZDR-eligible** — 30-day abuse logs, app state until deleted. So if the tool needs strict ZDR, it must avoid Batch and forgo the 50% discount.
- **Fine-tuning — WINDING DOWN** [D]: *"OpenAI is winding down the fine-tuning platform. The platform is no longer accessible to new users, but existing users … will be able to create training jobs for the coming months."* FT models stay for inference until base deprecation.
  - Training price = per 1M training tokens except o4-mini = **$100/hour**:
    | Base | Train | FT input | FT cached in | FT output |
    |---|---|---|---|---|
    | gpt-4.1 | $25.00 | $3.00 | $0.75 | $12.00 |
    | gpt-4.1-mini | $5.00 | $0.80 | $0.20 | $3.20 |
    | gpt-4.1-nano | $1.50 | $0.20 | $0.05 | $0.80 |
    | gpt-4o (08-06) | $25.00 | $3.75 | $1.875 | $15.00 |
    | gpt-4o-mini | $3.00 | $0.30 | $0.15 | $1.20 |
    | o4-mini | $100.00/hr | $4.00 | $1.00 | $16.00 |
  - **Data-sharing discount** halves FT inference (e.g. o4-mini $2.00/$8.00) — but that means opting your data in.
  - Batch-mode FT inference is 50% off.
- **Embeddings** [D]: `text-embedding-3-small` **$0.02/M**, `text-embedding-3-large` **$0.13/M**, `text-embedding-ada-002` **$0.10/M**. `/v1/embeddings` is **ZDR-eligible = Yes**. **No `text-embedding-4`** exists on the page [R from absence].

### 1.2 Anthropic
Sources: `https://privacy.claude.com/en/articles/7996866-…`, `/7996868-…`, `/8956058-…` **[D]**; `https://platform.claude.com/docs/en/manage-claude/api-and-data-retention` **[D]**; `https://platform.claude.com/docs/en/about-claude/pricing` **[D]**.

- **Retention** [D]: API inputs/outputs auto-deleted within **30 days**. Exceptions: Files API (longer, under your control), agreed exceptions, Usage-Policy-violation content (**2 years**; T&S classification scores 7 years), feedback data 5 years, Compliance Activity Feed 6 years.
- **Training** [D]: **not used for training by default** on commercial products; explicit feedback/opt-in is the only path.
- **ZDR** [D]: per **organization**, enabled by Anthropic's account team (contact sales); **not self-serve**. Covers Claude Messages + Token Counting for the "Yes" features; **Claude Console/playground, Managed Agents, consumer plans, Claude for Excel are not covered**. CORS unsupported under ZDR → browser apps need a backend proxy.
  - **Covered Models** (Claude Fable 5.1, Mythos 5.1, Fable 5, Mythos 5) **require 30-day retention and are ZDR-ineligible** unless expressly authorised. A ZDR org can carve out a non-default workspace with 30-day retention to use them.
- **HIPAA** [D]: self-serve BAA + HIPAA readiness from Console (`platform.claude.com/settings/privacy`); permanent once enabled; API returns 400 for non-eligible features.
- **Fine-tuning** [X]: **no fine-tuning section** on the Claude Platform pricing page (grep for `fine-tun` returned nothing) [D-from-absence]. No public Claude FT product.
- **Embeddings** [X]: no first-party embeddings API; Anthropic directs users to Voyage AI (see §4).
- **Batch retention difference** [D]: `/v1/messages/batches` is **ZDR-ineligible**, **29-day retention**; async storage required. 50% discount on input+output. Fast mode unavailable in Batch.
- Model list on 2026-10-15 (pricing page): Fable 5.1 $10/$50, Mythos 5.1 $10/$50, Opus 5.5 $4/$20, Opus 5 $5/$25, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 (≤100K prompt; $0.50/$2.50 above). Cache hits 0.05x on Opus 5.5/Sonnet 5.5; 0.025x on Fable/Mythos 5.1. US-only `inference_geo:"us"` = 1.1x.

### 1.3 Google — Gemini API (AI Studio) — FREE TIER TRAINS
Sources: `https://ai.google.dev/gemini-api/docs/pricing` **[D]**; `https://ai.google.dev/gemini-api/terms` **[D]**; `https://ai.google.dev/gemini-api/docs/logs-policy` **[D]**; `https://ai.google.dev/gemini-api/docs/model-tuning` **[D]**.

- **Free tier = Unpaid Services** [D]. Terms §"Unpaid Services → How Google Uses Your Data": *"Google uses the content you submit … to provide, improve, and develop Google products and services and machine learning technologies"*; *"human reviewers may read, annotate, and process your API input and output"* (de-linked from account/key/project). **"Do not submit sensitive, confidential, or personal information to the Unpaid Services."** ⇒ **CONFIRMED: free tier trains on / improves with your data.**
- **Paid tier** [D]: prompts/responses **not used to improve products**; logged "for a limited period of time" solely for Prohibited-Use-Policy enforcement; processed under Google's DPA (`business.safety.google/processorterms`).
- **EEA/CH/UK** [D]: the Paid-Services data terms apply to **all** services incl. AI Studio & unpaid quota, **and you may only use Paid Services when making API clients available to users in EEA/CH/UK**.
- **Contributor tier** [D]: opt-in discount (up to 50% off tokens) in exchange for data used per Unpaid-Services terms. Models: Gemini 4 Argon, 3.1 Pro Preview, 3.8 Flash, 3.5 Flash-Lite.
- **Logs & Datasets** [D]: opt-in request/response logging; default log retention **≤55 days** (configurable 7/14/28/55). Datasets have no set retention; sharing a dataset = Unpaid Services terms (may train).
- **Fine-tuning** [X for API] [D]: *"With the deprecation of Gemini 1.5 Flash-001 in May 2025, we no longer have a model available which supports fine-tuning in the Gemini API or AI Studio"* — Google *"do[es]n't have immediate plans to bring fine-tuning support."* Use Gemini Enterprise Agent Platform (Vertex) instead.
- **Batch retention** [D]: 50% cost reduction; paid-tier batch content is still **not used to improve products** (per-model "Used to improve our products = No" rows). Free-tier Batch is "Not available" for many models.
- **Embeddings** [D]: `gemini-embedding-2` — text **$0.20/M** (batch $0.10), image $0.45/M ($0.00012/img), audio $6.50/M, video $12.00/M. File Search embeddings charged at $0.15/M. Free tier = free but content may be used to improve products.
- **Game-coaching-relevant ToS restrictions** [D]: 18+ only; **no API-client directed at/accessible to under-18s**; **only Paid Services in EEA/CH/UK**; no clinical/medical use; no building competing models; Grounding-with-Search results may not be cached/trained-on/analysed (limited 2-year display exceptions) — relevant if you ground coaching tips on web search.

### 1.4 Google — Vertex AI / Gemini Enterprise Agent Platform
Source: `https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention` **[D]**; `…/generative-ai/pricing` **[D]**.

- **Training restriction** [D]: *"Google won't use your data to train or fine-tune any AI/ML models without your prior permission or instruction"* — applies to all managed models (GA and pre-GA).
- **How to actually get ZDR** [D]:
  1. Request an **abuse-monitoring exception** (prompt logging is only applied to customers under the GCP ToS).
  2. Do **not** enable request-response logging (off by default).
  3. Set `store = false` on the Interactions API (defaults to `true`).
  4. **Disable durable caching** (`roles/aiplatform.admin`, `PATCH …/cacheConfig {"disableCache": true}`); durable cache otherwise stores derived KV data at rest ≤24 h. CMEK not supported for durable cache.
  5. Do not use Gemini Live session resumption (24 h cache).
- **Advance-AI caveat** [D]: *"Zero data retention may not be possible when using some Advanced AI features."*
- **Grounding kills ZDR** [D]: Grounding with Google Search stores de-identified query logs **3 days** with **no way to disable**; Grounding with Google Maps stores prompts/output **30 days**, also not disableable. Google explicitly says use Web Grounding for Enterprise if you need ZDR.
- **Fine-tuning prices** [D] (per 1,000 training tokens unless noted; training tokens = dataset × epochs):
  | Base model | Method | Price |
  |---|---|---|
  | Gemini 3.5 Flash | Supervised FT, RL FT | $0.01 / 1K = **$10.00/M** |
  | Gemini 3.5 Flash-Lite | Supervised FT | $0.003 / 1K = **$3.00/M** |
  | Gemini 3.1 Flash Lite | Supervised FT | $0.003 / 1K = **$3.00/M** |
  | Gemini 2.5 Pro | Supervised FT | $0.025 / 1K = **$25.00/M** |
  | Gemini 2.5 Flash | Supervised FT, Preference | $0.005 / 1K = **$5.00/M** |
  | Gemini 2.5 Flash Lite | Supervised FT, Preference | $0.0015 / 1K = **$1.50/M** |
  | Gemini 2.0 Flash / Flash Lite | (legacy) | $0.003 / $0.001 per 1K |
  | Llama 3.1 8B / 3.2 1B/3B / 3.3 70B / 4 Scout / Qwen3 4B/8B/14B/32B / Gemma 3 | Supervised FT | $0.28–$8.46 per 1M count |
  - **Hosted FT inference** [D]: *"For model inference starting from Gemini 3, tuned model endpoint prediction price will be 1.5 times of the base model. Old Gemini models … stays the same as the base model."*
- **Embeddings**: same `gemini-embedding-2` SKUs apply on Vertex [R].

---

## 2. Cheap / open-weight providers — detail

### 2.1 DeepSeek
Source: `https://api-docs.deepseek.com/quick_start/pricing` **[D]**; `https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html` (last update 2026-02-10) **[D]**.

- **Pricing** [D] (off-peak = half of peak; peak = 01:00–04:00 & 06:00–10:00 UTC Mon–Fri excl. CN holidays):
  - `deepseek-flash` (V4.1-Flash, 1M ctx, vision): cache-hit $0.003/$0.006; cache-miss **$0.15/$0.30**; output **$0.60/$1.20**.
  - `deepseek-v4-pro` (V4-Pro-0813): cache-hit $0.022/$0.044; cache-miss $0.66/$1.32; output $1.98/$3.96. 384K max output, **no vision**.
- **Privacy** [D]: data controller = **Hangzhou DeepSeek AI Co., Ltd (China)**; inputs and files are collected as "User Input". Use of personal data explicitly includes *"To improve and develop the Services and to train and improve our technology, such as our machine learning models and algorithms."* Rights include *"the right to opt-out of using your Personal Data for training our models or optimizing our technologies"* — exercise by emailing `privacy@deepseek.com`. **No fixed retention period published** ("as long as necessary"); account/input/payment data retained while the account is active. **No ZDR product.** Data processed/stored in the PRC.
- Implication for a coaching tool: **do not send identifiable player data (Steam IDs, chat, names) to DeepSeek** unless you have the opt-out confirmed in writing.

### 2.2 Qwen / Alibaba Model Studio (DashScope)
Source: `https://www.alibabacloud.com/help/en/model-studio/data-retention-policy` **[D]**; pricing/embedding/FT prices from Alibaba docs **[R]** (secondary summaries of `…/model-pricing`, `…/embedding`, `…/model-training-and-deployment-billing`).

- **Retention** [D]: prompts/responses **≤30 days** by default; stateful features (conversations, files) until user deletes. ZDR: prompts/responses not written to durable storage, exist only in an encrypted cache window (default **≤24 h**), automatically deleted on expiry; not used for training/review during the window. Stateful I/O files deleted **within 48 h** if user doesn't delete.
- **ZDR access** [D]: **enterprise customers of the Alibaba Cloud International Site**, via account manager, needs assessment; **workspace-level**; covers pay-as-you-go + DTU/PTU. **ZDR-covered models** (text gen): qwen-max (from qwen3.8-max), qwen-plus (from qwen3.7-plus), qwen-flash (from qwen3.8-flash), deepseek-pro (from v4-pro-0813), deepseek-flash (from v4-flash-0731), glm (from glm-5.2); plus image-gen, TTS, ASR, and **embedding & reranking: text-embedding-v4 and later**.
- **ZDR exclusions** [D]: Agent/Workflow applications, RAG/knowledge base, **Batch inference** + async task API, model playground, **OpenAI-compatible Responses API** (stateful). Content flagged by safety filters retained **≤2 years** (not a ZDR breach). Regions: non-mainland-China (Singapore, US-Virginia, Germany, HK, Tokyo).
- **Training** [D]: *"Without your separate consent, we will not use your business data (including inputs, outputs, and files) to train, fine-tune or improve any foundation model."*
- **Fine-tuning** [R]: SFT / CPT / DPO. Training fee = (training-data tokens + mixed-training tokens) × epochs × unit price. Examples: Singapore Qwen3.5-9B $0.003/1K = **$3.00/M**; Singapore Qwen3-14B $0.0016/1K = **$1.60/M**; China table Qwen3.8-27B ¥0.05/1K, Qwen3.5-9B ¥0.02/1K, Qwen3-14B ¥0.03/1K. Post-training **deployment is billed separately** (token-based deployment only for certain LoRA models) — budget for this.
- **Embeddings** [R]: `text-embedding-v4` **$0.07/M input** (Singapore/Intl); v3 also $0.07/M; `qwen3.7-text-embedding` $0.07/M up to 128K tokens. Free quota: 1M tokens v4 / 500K v3, 90 days.
- **Chat pricing** [R]: e.g. `qwen-plus` ≤256K $0.40 in/$1.20 out; 256K–1M $1.20/$3.60. Batch inference generally 50% of real-time.

### 2.3 Moonshot / Kimi
Source: `https://platform.kimi.ai/docs/pricing/chat` **[D]**; `https://platform.kimi.ai/docs/agreement/userprivacy` **[D]**; `https://platform.kimi.ai/docs/agreement/modeluse` (ToS, updated 2026-07-30) **[D]**; `https://platform.kimi.ai/docs/guide/zero-data-retention` **[D]**.

- **Pricing** [D]: Kimi K3 $3.00 in / $15.00 out, cache-hit $0.30, cache write 5-min $3.00 / 1-h $6.00, 1M context. Kimi K2.7 Code $0.95/$4.00 (cache-hit $0.19); K2.7-Code-Highspeed $1.90/$8.00; K2.6 $0.95/$4.00 (cache-hit $0.16). `moonshot-v1-*` and `kimi-k2*` retired.
- **Training — CONFLICT, flag it**:
  - Privacy Policy [D] says inputs/outputs are used *"To Improve and Develop Our Services … This includes training and refining our underlying technology, such as machine learning models and algorithms."*
  - ToS §4 [D]: *"We may use Content to provide, maintain, develop, support, and improve the Services … Customer who requires restrictions … may contact Moonshot AI to discuss available enterprise arrangements or separate written agreements. **Unless otherwise expressly agreed in writing, Customer Content may be used for the foregoing purposes.**"*
  - ZDR page [D] claims: *"By default, the Kimi Open Platform does not use enterprise customer data to train models."*
  - **Reading**: default *may* include training; you must negotiate a restriction. Do not rely on the ZDR page's default claim without a contract.
- **Retention** [D]: no fixed period — *"as long as necessary to provide the services, fulfill the purposes … and other legitimate business purposes"*; account/input/payment data retained while the account is active; violation-related data until resolved. **Stored in Singapore**.
- **ZDR** [D]: **enterprise customers on request** (contact sales; evaluation). Prompts/outputs deleted after the response. Excluded: **Batch Job service**, **images/videos via the File Upload API**, operational data (security logs, billing records), third-party services. No request-content tracing after the fact → keep your own logs.
- **Fine-tuning** [R]: no public FT price; enterprise/custom quote only. No embeddings API [X].
- **US-relevant** [D]: HIPAA/PHI processing prohibited.

### 2.4 Z.ai (GLM)
Source: `https://docs.z.ai/guides/overview/pricing` **[D]**; `https://chat.z.ai/legal-agreement/terms-of-service` (updated 2026-04-14) **[D]**.

- **Pricing** [D]: GLM-5.3-Flash $0.15/$0.50; GLM-5.3-FlashX $0.37/$1.25; GLM-5.3 & GLM-5.2 $1.40/$4.40; GLM-4.7/4.6 $0.60/$2.20; **GLM-4.7-Flash / GLM-4.5-Flash / GLM-4.6V-Flash = free**; GLM-OCR $0.03/$0.03. Web search tool $0.01/use.
- **Training** [D]: ToS §IV.7: *"For enterprises and developers using API Services, we will not use your User Content for developing or improving Services unless you explicitly agree to such use."* **BUT** §IV.3(a) for *individual* users: *"we reserve the right to process any User Content to improve our existing Services and/or to develop new products"* and (i) *"utilization and storage of User Content that does not constitute personal data for the purpose of developing and improving our machine learning and artificial intelligence technologies"*. ⇒ **API/enterprise = no-train by default; consumer = trains.** Get the API/enterprise path in writing.
- **Retention** [R]: API DPA says content processed in real time and **not stored on servers**; operational/other data deleted after termination unless legally required; **no published precise retention**. Processing generally in **Singapore**.
- **Prohibited data** [D]: US users must not process ITAR/EAR-controlled data, **HIPAA PHI**, GLBA NPI, or COPPA-violating child data. Also no model-competition use, no reverse engineering.
- No FT / embeddings [P].

### 2.5 MiniMax
Source: `https://platform.minimax.io/protocol/privacy-policy` and `/terms-of-service` — **[R]** (page is JS-rendered; values from a secondary summary of those same vendor URLs).

- **Pricing** [R]: MiniMax-M3 ≤512K $0.30/$1.20 (cache read $0.06); >512K $0.60/$2.40; M3 Priority $0.45/$1.80; M2.7 $0.30/$1.20 (cache write $0.375); M2.7-highspeed $0.60/$2.40. Speech recognition $0.38/audio-hour. Video per second.
- **Retention** [R]: **no fixed period**; "as long as necessary"; API personal data stored in a **US data center**; may be processed by third-party vendors; no ZDR commitment.
- **Training** [R]: **no blanket no-training promise**. Privacy Policy permits aggregate/anonymise/de-identify + "commercial research and development"; ToS permits use of input/generated content to "provide, maintain, develop, and improve its services". Narrower guarantee only: won't use input personal data to infer individual characteristics or to profile/target consumers.
- **Prohibited** [R]: US region ToS bars ITAR content and HIPAA-regulated Client Data.
- No FT / embeddings found [P].

### 2.6 Mistral
Source: `https://docs.mistral.ai/inference/pricing` **[D]**; `https://mistral.ai/pricing/api/` **[R]**; `mistral.ai/pricing` (consumer) **[D]**.

- **API pricing** [D]: mistral-large-4 $0.68/$2.09 sale (regular $1.36/$4.18), cached $0.07; mistral-large-2512 $0.50/$1.50; mistral-medium-3-5 $1.50/$7.50; mistral-small-2603 $0.15/$0.60; ministral-14b $0.20/$0.20; ministral-8b $0.15/$0.15; ministral-3b $0.10/$0.10; codestral-2508 $0.30/$0.90; zai-glm-5-3 $1.40/$4.40. OCR $4/1,000 pages; voxtral-mini transcribe $0.003/min.
- **Embeddings** [D]: **mistral-embed $0.10/M** (8K ctx); **codestral-embed-2505 $0.15/M**.
- **Fine-tuning** [R]: general FT docs are **deprecated** ("no longer actively supported"); the pricing page lists FT only for **Classifier API models** — **$1 per 1M training tokens**, **minimum $4**, model storage **$2/model/month**. Do **not** assume $1/M applies to embedding or chat models.
- **Retention/training for the API** [P]: not stated on the pages read. Consumer pricing page shows "Model training: **Opt-out**" for Pro/Team/Enterprise (and blank for Free) — that is the Vibe consumer product, not the API. Needs a Mistral privacy/DPA read before relying on it.
- **Batch**: Mistral offers a Batch API at reduced cost with 24-h window [P]; retention not verified.

### 2.7 Groq
Source: `https://console.groq.com/docs/models` **[D]**; `https://groq.com/privacy-policy` **[D]**; `https://console.groq.com/docs/legal/customer-data-processing-addendum` **[D]**; `https://console.groq.com/docs/legal/services-agreement` (modified 2026-06-22) **[D]**; `https://console.groq.com/docs/batch` **[D]**.

- **Pricing** [D]: `openai/gpt-oss-120b` **$0.15 in / $0.60 out**; `openai/gpt-oss-20b` **$0.075/$0.30**; `openai/gpt-oss-safeguard-20b` $0.075/$0.30; `qwen/qwen3.8-27b` **$0.80/$4.00**; prompt-guard 22M/86M $0.03/$0.04. llama-3.1-8b / 3.3-70b / minimax-m2.7 = **Contact Sales** (enterprise). Whisper-large-v3 $0.111/hr.
- **Training** [D]: Services Agreement §4.2: *"Groq is **not permitted** to use Inputs or Outputs for training or fine-tuning any AI Model Services or other models, unless explicitly granted permission or instructed by Customer."* Customer Training Data used only to provide the service (§8.2).
- **ZDR** [D]: §4.2 — *"Eligible Customers may enable Groq's zero data retention setting in the Console to prevent access by Groq to Inputs and Outputs for the purposes of ensuring reliable operation of the Cloud Services or compliance with the AUP."* Self-serve at `console.groq.com/settings/data-controls`.
- **Retention** [D]: privacy policy excludes Customer Data (governed by SA+DPA). DPA Annex I: *"retained for the time period needed to accomplish the purposes of Processing, unless otherwise required by applicable law"*; §10 deletion request honoured **within 180 days**; SA §11.5 says data deleted **within 30 days** of termination. **No fixed default retention number** → weaker than OpenAI/Anthropic.
- **Batch** [D]: 50% discount; completion window 24 h–7 d; **batch tokens are billed at the 50% rate regardless of prompt-cache status** (discount does not stack with caching). ZDR ineligibility for Batch is not stated by Groq; assume input/output retention while the batch is in flight.
- No FT service; Groq may host customer-supplied fine-tuned models at its discretion (§4.5) [D]. No embeddings API [X].

### 2.8 Together AI
Source: `https://www.together.ai/pricing` **[D]**; `https://www.together.ai/privacy` (updated 2025-12-17) **[D]**.

- **Privacy — best-in-class wording** [D]: *"We do not use any data collected from you to train our models without your explicit opt-in and consent. … We allow you to tweak your privacy settings in our platform so that we do not retain training data, prompts, or model responses for any purpose."* §2.6 **Zero Data Retention**: choose "No" in Privacy & Security settings ⇒ *"content you submit … and any outputs … are not stored, retained, or used for model training, product improvements, or any secondary purposes except as needed to provide the Services."* ZDR applies only from enablement onward and is irreversible for past data. Deletion via settings; `privacy@together.ai` for GPU-cluster/custom builds.
- **Serverless inference** [D]: MiniMax M3 $0.30/$1.20; Kimi K3 $3.00/$15.00; Qwen3.8-2.4T-A95B $2.00/$6.00; DeepSeek V4 Pro 0813 $1.32/$3.96; GLM-5.3-Flash $0.15/$0.50; GLM-5.3 $1.40/$4.40; DeepSeek V4.1 Flash $0.30/$1.20; gpt-oss-120B $0.15/$0.60; Qwen3.8 Flash $0.15/$0.47; Gemma 4 31B $0.39/$0.97.
- **Fine-tuning** [D] (per 1M training tokens; SFT/DPO + minimum charge):
  - Qwen3.5 0.8B/2B/4B/9B & Llama 3.1 8B: $0.34 / $0.84 (min $4)
  - Qwen3.5/3.6 27B, Qwen3.5 35B A3B, Gemma 4 26B/31B: $1.05 / $2.62 (min $4)
  - Llama 3.3 70B $2.03/$5.08; Llama 4 Scout $2.10/$5.25; Llama 4 Maverick $5.60/$14.00; Qwen3.5 122B A10B $4.20/$10.50; Qwen3.5 397B A17B $5.60/$14.00; DeepSeek-V3.1 $7.00/$17.50; DeepSeek V4 Flash $6.00/$15.00; gpt-oss-20B $0.40/$1.00; gpt-oss-120B $2.50/$6.25; Kimi K2.6/K2.7 $15.00/$37.50 (min $60); **GLM-5.1 / GLM-5.2 $40.00/$100.00** (min $60).
  - A second (higher) table applies to the full-parameter method (e.g. Qwen3.5 0.8B $0.38/$0.94).
  - Price = tokens in training set × epochs (+ eval tokens × evaluations); per-job minimum applies.
- **Embeddings** [R]: Together's model pages currently mark BGE and M2-BERT Retrieval as **not available on Serverless**; historical price was **$0.008/M input tokens**. Do not budget on this without confirming in-account.
- **Batch** [D]: a Batch API price exists per model in the pricing UI (~50% off); dedicated batch-retention language not found [P].

### 2.9 Fireworks AI
Source: `https://fireworks.ai/pricing` **[D]**; `https://fireworks.ai/privacy-policy` (modified 2026-08-11) **[D]**; `https://docs.fireworks.ai/guides/security_compliance/data_handling` **[D]**.

- **Retention — ZDR BY DEFAULT** [D]: *"Fireworks has Zero Data Retention by default. … Fireworks does not log or store prompt or generation data for any open models, without explicit user opt-in."* Prompt/generation data exists only in volatile memory for the request; prompt caching may hold prompt KV in volatile memory for several minutes; metadata (token counts) is logged. Enterprise admins can additionally turn on a ZDR policy that **rejects requests/jobs that would persist content**.
  - **Exception** [D]: **Responses API** with `store=True` (the default) retains complete conversation data (prompts, responses, tool calls) for **30 days**; set `store=False` to disable, or DELETE by `response_id`. This mirrors OpenAI's semantics.
- **Training** [D]: Privacy Notice key commitment: *"No AI Training on Your Data: We do not use your prompts, training data, or API inputs to train or improve our AI models without your explicit opt-in."*
- **Embeddings** [D]: up to 150M params **$0.008/M**; 150M–350M **$0.016/M**; Qwen3 8B **$0.10/M**. (Cheapest embedding in the whole survey.)
- **Managed Training** [D] ($/1M training tokens, SFT/DPO LoRA vs Full):
  | Base size | LoRA SFT | LoRA DPO | Full SFT | Full DPO |
  |---|---|---|---|---|
  | ≤16B | $0.50 | $1.00 | $1.00 | $2.00 |
  | 16.1–80B | $3.00 | $6.00 | $6.00 | $12.00 |
  | 80–300B (Qwen3-235B, gpt-oss-120B) | $6.00 | $12.00 | $12.00 | $24.00 |
  | >300B (DeepSeek V3, Kimi K2) | $10.00 | $20.00 | $20.00 | $40.00 |
  - **Hosted FT inference = same price as base models** [D] — a genuinely important cost proposition vs OpenAI/Google 1.5x.
- **Serverless Training API** [E] (private preview; LoRA on launch models): charged per token across prefill/sample/train — GLM-5.3-Flash train $8.89/M; GLM-5.3 $14.58/M; Qwen 3.8 27B $4.103/M; Kimi K3 $32.55/M; DeepSeek V4 Flash $5.20/M; Muse Glimmer 30B $5.86/M.
- Dedicated training per GPU-hour: H100/H200 $8.00, B200 $13.00, B300 $15.00, GB300 $20.00 [D].
- **Batch**: batch inference is supported; prompts/outputs remain ZDR by default unless the feature explicitly stores [R].

### 2.10 Cerebras
Source: `https://www.cerebras.ai/privacy-policy` (eff. 2024-08-27) **[D]**; `https://inference-docs.cerebras.ai/models/overview` **[D]**; prices **[R]** (pricing page is JS-rendered).

- **Retention** [D]: Privacy Policy §6: *"We do not retain inputs and outputs associated with our training, inference and chatbot Services. We delete logs associated with our training, inference and chatbot Services when they are no longer necessary to provide services to you."* No fixed day count; no explicit training statement, but combined with "do not retain I/O" it is effectively no-training on I/O [R]. Note: the policy otherwise grants broad use of aggregated/de-identified data.
- **Models** [D]: Shared Inference serves only `gpt-oss-120b` (65K free / 131K paid ctx) and `qwen-3.8-27b` (64K/128K). All Shared Inference models are unpruned; weight-only quantisation at storage.
- **Pricing** [R]: GPT-OSS-120B $0.35 in / $0.75 out; Qwen 3.8 27B $0.99/$1.49. Free tier + PayGo developer tier; enterprise/dedicated by agreement.
- No fine-tuning service [X]; no embeddings API [X].

### 2.11 Embedding specialists

**Voyage AI** — `https://docs.voyageai.com/docs/pricing` (updated 2026-09-29) **[D]**:
- Text: `voyage-4-large` **$0.12**, `voyage-4` **$0.06**, `voyage-4-lite` **$0.02**, `voyage-context-4` $0.12, `voyage-code-4` $0.12; `voyage-finance-2`/`law-2`/`code-2` $0.12. **200M tokens free** per account for the -4/-code-3 families (50M for the older 2-series).
- Multimodal `voyage-multimodal-3.5`/`-3`: $0.12/M text tokens + **$0.60 per billion pixels**; first 200M text tokens + 150B pixels free. Image ≈ $0.00003–$0.0012.
- Rerankers: `rerank-3` $0.05, `rerank-3-lite` $0.02; 200M free tokens.
- **Batch API**: **33% discount**, 12-hour window; free credits do NOT apply to batch. **Files API**: unlimited files, each **retained 30 days then auto-deleted**, storage $0.05/GB/month.
- **Fine-tuned embeddings**: dedicated instances + support — sales only.
- **Retention/training for embedding requests**: not stated on the pricing page [P] — verify in Voyage's privacy/security page before using it (page `docs.voyageai.com/docs/security` returned 404).
- Notable: Voyage is the embeddings vendor Anthropic points to; `voyage-code-4`/`voyage-context-4` are plausible fits for CS2 demo event sequences, but **multimodal pixel pricing gets expensive for video frames**.

**Cohere** — `https://cohere.com/pricing` **[R]** (JS-rendered; values from summaries of that page and `docs.cohere.com/docs/model-vault/standard/pricing`):
- Embed 5 Fast (`embed-v5.0-fast`) **$0.08/M** text, $0.40/M image; Embed 5 Pro **$0.12/M** text, $0.40/M image; Embed v4 **$0.12/M** text, $0.47/M image. 128K context on Embed 5.
- Model Vault (dedicated) from $3/hour for Small tier — matters if you need strict isolation.
- Retention/training not read [P].

---

## 3. Fine-tuning price summary (the tool's realistic options)

| Provider | Method | Cheapest useful tier | Hosted-inference multiplier | Minimums / notes |
|---|---|---|---|---|
| **Fireworks** | LoRA SFT | **$0.50/M** (≤16B) | **1x base price** | No minimum stated; serverless trainer in preview |
| **Together** | LoRA SFT | **$0.34/M** (≤9B) | serving terms for FT models not stated [P] | Min charge $4–$60/job by model |
| **Alibaba** | SFT/CPT/DPO | ~**$1.60/M** (Qwen3-14B, Singapore) | separate deployment billing | Needs ZDR-/region-check; deployment extra |
| **OpenAI** | SFT | $1.50/M (gpt-4.1-nano) — **closed to new users** | ~1.5–2x base (gpt-4.1 FT $3/$12 vs base $2/$8) | Winding down; o4-mini per-hour |
| **Google (Agent Platform)** | Supervised/RL/pref | **$1.50/M** (Gemini 2.5 Flash Lite) | **1.5x base for Gemini 3+**; 1x for ≤2.5 | No minimum on training tokens read |
| **Mistral** | Classifier only | $1.00/M | n/a | Min $4; $2/model/month storage; general FT deprecated |
| **Moonshot** | Enterprise custom | quote | n/a | Contact sales |
| **xAI, Anthropic, Z.ai, MiniMax, Groq, Cerebras, DeepSeek(hosted)** | — | **none public** | — | Groq may host *your* FT model at its discretion |
| **Voyage** | Embedded-specific FT | dedicated instance, quote | — | sales only |

Practical read for a personal CS2 coaching tool: **Fireworks (LoRA, 1x serving) and Together (LoRA, cheapest/min-charge) are the two realistic hosted-FT paths.** OpenAI's platform is closing, Google's is 1.5x-serving and gated behind the enterprise Agent Platform, and the cheap Chinese providers mostly do not offer FT except Alibaba.

---

## 4. Embeddings price summary (cheapest first)

| Provider / model | $/M tokens | Notes |
|---|---|---|
| **Fireworks** ≤150M-param base | **$0.008** | cheapest; ZDR by default |
| Fireworks 150–350M | $0.016 | |
| **Voyage** voyage-4-lite | **$0.02** | 200M free tokens |
| **OpenAI** text-embedding-3-small | **$0.02** | ZDR-eligible endpoint |
| **Alibaba** text-embedding-v4 / v3 | **$0.07** | ZDR-covered |
| Voyage voyage-4 | $0.06 | 200M free |
| **Cohere** Embed 5 Fast | **$0.08** | [R] |
| **Groq** | none | no embeddings API |
| **Cerebras** | none | no embeddings API |
| **Together** | currently unavailable serverless [R] | historical $0.008 |
| **Mistral** mistral-embed | **$0.10** | codestral-embed $0.15 |
| Fireworks Qwen3 8B | $0.10 | |
| Cohere Embed 5 Pro / v4 | $0.12 | [R] |
| Voyage voyage-4-large / context-4 / code-4 | $0.12 | 200M free |
| **OpenAI** text-embedding-3-large | **$0.13** | |
| **Google** gemini-embedding-2 | **$0.20** text (batch $0.10) | $0.45/M images, $12/M video tokens |
| Voyage multimodal-3.5 | $0.12/M text + $0.60/B px | pixels dominate for video |
| Cohere image input | $0.40–$0.47/M | [R] |

Anthropic, xAI, DeepSeek, Z.ai, MiniMax, Moonshot/Kimi, Groq, Cerebras: **no first-party embeddings API** — you would use OpenAI/Voyage/Alibaba/Fireworks/Mistral instead.

---

## 5. Batch API — retention differences are real and decision-relevant

| Provider | Batch discount | Batch retention / ZDR interaction |
|---|---|---|
| **OpenAI** [D] | 50% | `/v1/batches` abuse logs 30 d, app state until deleted, **ZDR-ineligible** |
| **Anthropic** [D] | 50% (in+out) | **29-day retention, ZDR-ineligible**; Fast mode unavailable |
| **Google Gemini API** [D] | 50% | Paid-tier batch content still not used to improve products; free tier often "Not available" |
| **Google Vertex** [D] | 50% | abort-monitoring exception + no request/response logging + `store=false` + caching off = ZDR; batch is still an async store |
| **xAI** [D] | 20% off (some models N/A) | **Batch API is disabled under ZDR**; discount applies to all token types (text models only) |
| **Groq** [D] | 50% | Batch files are uploaded and stored while processing; 24 h–7 d window; batch rate doesn't stack with prompt caching |
| **Fireworks** [D] | per-model | open models stay ZDR by default; **Responses API `store=true` = 30-day retention** |
| **Together** [D] | per-model ~50% | ZDR is a settings toggle; batch-specific retention not documented [P] |
| **Voyage** (embeddings) [D] | **33%** | Files API files retained **30 days** then auto-deleted; free credits don't apply to batch |
| **Alibaba** [D] | 50% | **Batch inference is explicitly excluded from ZDR** — task I/O files stored until completion |
| **Moonshot/Kimi** [D] | n/a read | **Batch Job service does not support ZDR** |

**Implication:** if the coaching tool wants strict "nothing retained", **Batch is off the table at OpenAI, Anthropic, xAI, Alibaba and Moonshot** — exactly the providers where a 50% discount would otherwise matter most. Google Vertex, Fireworks and (by config) Together allow you to keep ZDR *and* use cheap async paths, with caveats.

---

## 6. Legal / ToS restrictions touching CS2 telemetry and video

### 6.1 Valve / Steam side
Sources: `https://steamcommunity.com/dev/apiterms` (last updated July 2010) **[D]**; `https://www.valvesoftware.com/en/legal/site-terms-of-use` **[D]**; Steam Subscriber Agreement **[R]**.

- **Steam Web API ToS** [D]:
  - *"You will only retrieve Steam Data about a Steam end user as requested by the end user."*
  - You must publish a privacy policy, inform the end user about what Steam Data you store, and store it only in countries named in your privacy policy.
  - **"You agree … you will not create or assist third parties in any way to create any technology or functionality that may give a user an unfair competitive advantage when playing multiplayer versions of any Steam game."** — This is the single most relevant clause for a coaching tool built on Steam Web API data. A post-match, own-account coaching analysis is defensible; anything that provides live/real-time advantage to other players is squarely against this.
  - **100,000 calls/day per key**; key must stay confidential; one key = one application.
  - No implying Valve endorsement; Valve may terminate access at any time.
- **Valve Site Terms of Use** [D]: "Materials" (incl. demos compressed into the site's terms) are licensed for personal, single-session use only; you may not copy, distribute, modify, reverse-engineer, decompile, or create derivative works, and you may not remove proprietary notices. Submissions to Valve become Valve's property.
- **Steam Subscriber Agreement** [R]: restricts copying, distributing, reverse-engineering, deriving source code from, modifying, disassembling or decompiling Valve software; restricts commercial exploitation; prohibits emulating or redirecting Valve network protocols; limits subscriptions to personal, non-commercial use unless permitted.
- **Practical risk reading for a local-first, personal tool** [R, not legal advice]:
  - **Lowest risk**: parse only user-supplied `.dem` files, offline, post-match; no injection, no memory reading, no VAC interaction, no Valve binary inspection; use an existing OSS parser under its own licence; don't redistribute demos or extract Valve assets/protobufs/symbols.
  - **Medium**: inferring an undocumented format by inspecting `cs2.exe` / extracting Valve protobufs — plausibly characterised as reverse engineering under the SSA despite an interoperability rationale (DMCA §1201(f) is narrow).
  - **High**: live-tool behaviour, cheating-adjacent functionality, protocol emulation, distributing extracted Valve assets, commercial redistribution of demos.
  - **Personal-data angle**: demos and match data contain other players' Steam IDs, names and chat. If the tool is shared/hosted, a privacy policy, retention/deletion story, and consent from the uploader are advisable.
  - Provider ToS: none of the AI providers read impose game-specific restrictions; Google's rules that *do* bite are the age-18 requirement, the bar on API clients accessible to under-18s, and (for EEA/CH/UK) the Paid-Services-only rule for user-facing apps. Google also forbids using grounding-search results to train models / build indices.

### 6.2 Provider ToS items that interact with a coaching product
- **Google Gemini API** [D]: 18+, no under-18-directed API clients, Paid-only in EEA/CH/UK for user-facing apps, no competing-model training, grounding results not cacheable/trainable beyond the narrow 2-year display exception.
- **Anthropic** [D]: consumer plans train-by-feedback; API does not. Covered Models (Fable/Mythos 5.x) force 30-day retention.
- **Moonshot, Z.ai, MiniMax** [D/R]: each bar HIPAA/ITAR (and Z.ai additionally GLBA/COPPA) content — irrelevant for CS2 telemetry, but a reminder not to route credentials or player PII through them without a contract.
- **Fireworks** [D] / **Together** [D] / **Groq** [D]: all three explicitly forbid using the service to train models that compete with the provider, and Flock/Together/Groq each require you to warrant you have rights to the inputs you submit (relevant if you ever feed other players' demo content).

---

## 7. Bottom-line recommendation for this project

1. **Default path**: **Gemini 3.8 Flash paid tier** or **gpt-6-luna / gpt-5.6-luna** for volume analysis; both are no-train-by-default on the paid tier, and Gemini's Flash-Lite/Batch pricing is the cheapest frontier-quality tier. Avoid the **Gemini free tier entirely** if any player-identifying data is in the prompt (it trains and human reviewers can read it).
2. **Cheapest structured extraction at scale**: **Fireworks gpt-oss-120B ($0.15/$0.60)** or **Groq gpt-oss-120B ($0.15/$0.60)** — both carry explicit "no training on Inputs/Outputs" language, and **Fireworks is ZDR-by-default**, which is the strongest privacy posture among the cheap providers.
3. **If privacy is paramount**: **Fireworks** (default ZDR, `store=false` on Responses API) or **xAI with self-serve ZDR** — but remember xAI ZDR **kills the Batch API**.
4. **Embeddings for retrieval over demo events**: **Fireworks $0.008/M** or **voyage-4-lite $0.02/M** (200M free) or **text-embedding-3-small $0.02/M** (ZDR-eligible endpoint). Do not pay Google's $0.20/M for text.
5. **Fine-tuning**: only if the tool ever needs a domain-specific model — **Fireworks LoRA ($0.50/M, serving at base price)** is the clear winner; **Together LoRA ($0.34/M, $4 min)** is cheaper to train but serving terms need checking. Avoid OpenAI FT (sunset) and Google FT (1.5x serving).
6. **Batch**: useful for offline bulk grading, but **do not build a ZDR story on it** — it is ZDR-ineligible at OpenAI, Anthropic, xAI, Alibaba, Moonshot. If ZDR matters, use synchronous calls or Fireworks/Vertex instead.
7. **Legal**: keep the tool **personal, local-first, post-match, own-demos-only**; parse demos with an existing OSS parser rather than inspecting CS2 binaries; never build anything that could confer an in-match advantage via Steam Web API data (explicit API ToS prohibition); keep a privacy policy + deletion path if you ever host it.

---

## 8. Gaps / limitations of this slice (honest list)

- **Cohere**: pricing page and retention/training docs are JS-rendered and did not yield tables; Embed 5 prices are [R] from secondary summaries of cohere.com/pricing. Fit for embedding 8K-token demonstration blocks is unverified.
- **MiniMax**: privacy/ToS pages are JS-rendered; retention/training statements are [R] from secondary summaries of the vendor's own URLs. MiniMax's lack of a training opt-out is the single most concerning privacy finding among the cheap providers.
- **Mistral API privacy/DPA**: not read; retention/training for the API remains [P]. The pricing page does not state it.
- **Moonshot/Kimi**: the Privacy Policy, ToS and ZDR page **contradict each other** on whether default API content trains models. Treat as "may train unless contracted otherwise".
- **Together embeddings**: current serverless availability not confirmed; the $0.008/M figure is historical.
- **Voyage retention/training for embedding API calls**: not stated on the pricing page; `/docs/security` 404s.
- **Cerebras**: no explicit training sentence; inference is inferred from "do not retain inputs and outputs".
- **Batch retention for Together, Fireworks and Groq Batch**: not documented to the same precision as OpenAI/Anthropic/xAI/Alibaba.
- **xAI embeddings / fine-tuning**: not found on the pages read; do not assume they exist.
- **No provider read imposes a game-specific restriction**; the binding constraints for CS2 demo data come from Valve/Steam terms, not from AI providers.
- Nothing here is legal advice; the Valve analysis is a risk reading, not a legal opinion.

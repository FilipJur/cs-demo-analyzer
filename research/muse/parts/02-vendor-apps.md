# 02 — User-facing tools & commercial services (vendor apps)

Slice: **user-facing apps/services** for CS2 demo review, stats and coaching. Their *APIs/endpoints* are the sibling slice `01-parsers-libs` / APIS-DATA; where an API is the product's differentiator (Leetify) it is covered here at the depth needed for a reuse decision, and cross-referenced.

Research date: **2026-10-15**. All status claims were verified by fetching the page/repo/API that day unless stated.

Evidence tags used throughout: **Demonstrated** (observed working artefact), **Experimental** (shipped but marked beta/early), **Research-supported** (peer-/vendor-published metrics or method), **Plausible-untested** (claim credible, not verifiable independently), **Infeasible** (contradicted by evidence).

---

## A. Open-source / self-hostable tools

### A1. CS Demo Manager (CS:DM)

| Field | Finding |
|---|---|
| What it does | Desktop companion app for CS demos: imports/downloads demos, runs a demo analyser, stores *matches* (players, teams, rounds, kills, positions, economy, visuals), provides a 2D replay, radar, heatmaps, video capture, XLSX/JSON export. |
| CS2 support (verified how) | **Demonstrated.** Repo is `github.com/akiver/cs-demo-manager` (NOT `saul/*` — that 404s; `@saul` is a credited contributor). v3.20.1 ships CS2 features (CS2 plugin, TrueView recording, CS2 voice aliases). Docs carry an explicit per-source CSGO/CS2 matrix. |
| Maintenance status | **Very active.** Latest release **v3.20.1, 2026-07-30** (GitHub Releases API). Last commit **2026-10-04** ("chore: keep only claude review, update deps"). |
| Architecture | Electron; a **forked Node.js process hosts a WebSocket server** that does "almost all heavy work" (DB/FS access, demo analysis) and talks to main+renderer via WebSocket JSON messages (`{name, payload}`). Separate bundles: WS server, Electron main, renderer, preload, CLI. Demo parsing itself is delegated to a **separate Go program** (`akiver/cs-demo-analyzer`). |
| Data exposed | Match/round/kill/player/position model, radar, 2D replay, heatmaps, economy, voice (doc pages exist and resolve: `/docs/guides/2d-viewer`, `/docs/guides/2d-viewer-heatmaps`, `/docs/guides/heatmaps`, `/docs/guides/visuals`, `/docs/guides/video`); CLI exports: **JSON** (whole match), **XLSX** (sheets `general, players, rounds, kills`), **video** (HLAE or in-game recorder + FFmpeg/VirtualDub, TrueView, death notices, player voices). The JSON export is the practical machine interface; **no local HTTP REST API** is documented. |
| Programmatic integration | **CLI (`csdm`)** is the supported programmatic surface: `dl-valve`, `dl-faceit` (**currently disabled**), `dl-renown`, `dl-5eplay`, `analyze [--source …]`, `xlsx`, `json`, `video`. `--source` enumerates the analyser profiles: `challengermode, ebot, esea, esl, esportal, faceit, fastcup, 5eplay, perfectworld, popflash, valve` (+ esplay/esportligaen/matchzy/renown in the docs matrix). |
| Open/closed + license | **Open, MIT** (README + LICENSE). Analyser `akiver/cs-demo-analyzer` also **MIT**, Go, 124★/23 forks, created 2023-12-02, last push **2026-09-09**, 3 open issues. |
| Linux compat | **Yes, first-class-ish.** Release assets include `CS-Demo-Manager-3.20.1.AppImage`. Playback caveats on Linux: **Flatpak Steam is not supported**; demo files must live on a Basic-Latin path; old demos need matching **CS2 build + bundled connector plugin version** (depot 2347770/2347773 download procedure documented). |
| Reusability | **Highest of everything in this file.** ✔ MIT Go analyser can be vendored or shelled out; ✔ CLI gives batch ingest + JSON; ✔ documented DB-free "analyze → JSON" path; ✘ Electron app itself is not designed to be embedded; ✘ no REST/GraphQL server. |
| AI real vs marketing | **No AI claims at all** — deterministic parsing + reverse-engineered HLTV 2.0 rating (estimated, formula from flashed.gg) and explicit "no plan to reverse-engineer HLTV 2.1+". Anti-marketing, in a good way. |
| Unsolved problems | FACEIT demo *download* disabled; HLTV 2.1+ rating unavailable; ranks only from Valve MM demos; private-server (`tv_record`) demos unsupported; team names unknown unless clan tags match; CS2 build↔plugin coupling breaks playback after game updates; duplicated-checksum insert bug (#657); player names/avatars depend on a Steam API key (rate limit). |

Sources: `https://github.com/akiver/cs-demo-manager`, `.../releases` (API), `.../commits` (API), `https://cs-demo-manager.com/docs/development/architecture`, `/docs/cli`, `/docs/guides/demos-analysis`, `/docs/guides/playback`, `https://github.com/akiver/cs-demo-analyzer`.

### A2. CS2 Insight Agent (`DrEAmSs59/CS2-insight-agent`)

| Field | Finding |
|---|---|
| What it does | Windows "creation suite": local demo library + analysis (highlights/fails/multi-kills/clutches/knife/jump-shot detection, 2D replay, heatmaps, round timeline, economy), OBS-driven auto-recording of CS2 replay with POV/victim-POV HUD, built-in multi-track editor (**LiteCut**), compilation workbench, radar-chart generator, and **optional LLM commentary** (hype/roast, ≤100 chars). |
| CS2 support (verified how) | **Demonstrated** — README_EN + Windows installers; parses CS2 demos, drives CS2 replay. |
| Maintenance status | **Active.** 936★ / 62 forks / **870 commits** as of 2026-10-15 (repo page); release badge live; commit feed updating. |
| Architecture | Tauri desktop shell (Windows WebView2) + bundled **Python** backend (PyInstaller) + React frontend; `-insecure` CS2 launch for local playback; OBS controlled via its WebSocket API; FFmpeg (optional FrameMeld build) for export. No DLL injection/hooking (explicitly stated; caveat: don't run alongside a matchmaking-connected client). |
| Data exposed | Local files + app UI; `cs2dak analyze`-style handoff only (see A3). No REST API. Documented "Analysis handoff" = export v3 ZIPs with `cs2df` and run `cs2dak analyze` for conversational analysis. |
| Programmatic integration | Indirect: export `cs2-demo-format/3.x` ZIP → `@cs2dak/*` pipeline. LLM layer is provider-agnostic (DeepSeek, Qwen, GLM, MiniMax, OpenAI, OpenRouter, Ollama, LM Studio). |
| Open/closed + license | **Source-available, PolyForm Noncommercial 1.0.0**; the skin-rewriting subsystem is **closed source** and explicitly excluded. Commercial use requires written permission. |
| Linux compat | **No.** Windows 10/11 x64 only (installer + Tauri/WebView2). |
| Reusability | ✘ Non-commercial license blocks product reuse; ✔ concept/UX and the LLM-commentary prompt pattern are instructive; ✔ it is a *consumer* of the DAK pipeline, proving that seam works. |
| AI real vs marketing | **Real but shallow**: LLM is used for commentary/persona text over parsed events ("Round Comprehensive Review"), not for diagnosis. V3 roadmap lists "Tactical Coach (grenade trajectory analysis / route review)" as **not yet built** — i.e. no coaching AI today. |
| Unsolved problems | Windows-only; LLM commentary is cosmetic; tactical coach unbuilt; recording path mutates CS2 cvars (backed up/restored) and writes `pov.vpk` + edits `gameinfo.gi` SearchPaths → operational risk; `-insecure` required. |

Sources: `https://github.com/DrEAmSs59/CS2-insight-agent`, `/blob/main/README_EN.md`, `.../commits/main.atom`.

### A3. DAK Studio / `cs2-demo-analysis-kit`

| Field | Finding |
|---|---|
| What it does | "Local-first CS2 demo analysis — every stat links back to the exact round and tick." Desktop **DAK Studio** (9 modules: Home, Library, Match workspace, Duel & Mechanics Lab, Player, Utility Lab, Economy & Round Flow, Tournament Hub, Coach Workbench) **plus** product-neutral `@cs2dak/*` analysis packages. |
| CS2 support (verified how) | **Demonstrated** — README documents `.dem` import and a `cs2df` exporter; architecture pipeline `demoparser2 → cs2-demo-format/3.x ZIP → @cs2dak/*`. |
| Maintenance status | **Active** — releases page resolves to `releases.atom`, latest tags **v0.8.6** (plus a steady stream of per-package releases). |
| Architecture | Python shell (`cs2df`, PyPI) owns parsing/export; **v3 ZIP is the only seam** between Python and TypeScript; TS packages: `contract, core, cohort, maps, tournament, presentation, react, cli`; app = `apps/dak-studio` (pywebview, IndexedDB library). |
| Data exposed | `AnalysisBundle` view models (kills, economy, clutches, timeline, heatmap, duels, mechanics, QA, RR/PRISM signals); CLI `cs2dak analyze`; every stat carries round+tick evidence links. |
| Programmatic integration | **Best-in-class for embedding**: MIT-licensed npm packages + CLI + a versioned data seam explicitly designed for third parties ("RivalHub integrates over a versioned data seam"). |
| Open/closed + license | **Dual**: `@cs2dak/*` packages + Python shell **MIT**; `apps/dak-studio` **AGPL-3.0-only**. Third-party notices required. |
| Linux compat | Not shipped. Download table lists macOS `.dmg` (unsigned) and Windows `.exe`/portable zip — **no Linux artifact**. Browser mode exists (`pnpm dev:studio`) so a Linux path is [INFERENCE] plausible but unverified. |
| Reusability | **High** for the MIT packages (signal derivation, radar/world→radar transforms, view models). ✘ Studio app is AGPL (network-service clause). |
| AI real vs marketing | Explicit anti-black-box stance ("we never ship a score you can't trace"). Coach Workbench is flagged **early**; no LLM claims. |
| Unsolved problems | Coach Workbench immature; no Linux build; v2 ZIPs unsupported (fail fast, re-export required); small project (bus factor). |

Sources: `https://github.com/Starfie1d1272/cs2-demo-analysis-kit`, `/releases`, `raw .../README.md`.

### A4. CS2 Replays (cs2replays.com) — free browser 2D viewer

**Name-collision warning:** `cs2replays.com` (viewer) ≠ `csreplays.com` (AI coach, see B4) ≠ `csreplay.com` (simple viewer). Diligence hazard.

| Field | Finding |
|---|---|
| What it does | Free browser demo viewer: 2D overhead radar with vision cones, grenade trajectories, HP/armor/inventory per frame, kill feed with flags, round-by-round playback, Steam + FACEIT match sync, shareable replay links, pro-match library, **3D replay beta (Dust2 first)**. |
| CS2 support (verified how) | **Demonstrated** — site states parsing happens **in-browser via WebAssembly**; `.dem`/`.dem.bz2` accepted; states 64-tick resolution and Valve radar images. |
| Maintenance status | Live (HTTP 200, 2026-10-15); `/faq` returns 404 (nav anchors only). Monetised by display ads; premium features "on the roadmap". |
| Architecture | Client-side WASM parser (demo never uploaded unless you press Share; shared *parsed* replay stored 7 days). Steam OAuth + game auth code for sync. |
| Data exposed | UI only. Share links expose parsed replay data. **No documented API/export.** |
| Programmatic integration | None documented. |
| Open/closed + license | **Closed** (no repo found); the author's Reddit post about turning "my open-source CS2 demo tool" into a free site could not be tied to this domain — treat as unverified. |
| Linux compat | N/A (browser). |
| Reusability | Low as code; **higher as an existence proof** that in-browser WASM parsing of full 64-tick matches is practical, and that "share a link, not a file" is the expected UX. |
| AI real vs marketing | No AI claims. |
| Unsolved problems | No API; sync needs Steam game auth code; pro-library breadth unknown; 3D only Dust2. |

Sources: `https://cs2replays.com/`.

---

## B. Commercial individual-coaching services

### B1. Leetify

| Field | Finding |
|---|---|
| What it does | CS2 stats platform: match reports, profile pages, ratings, highlights, 2D replay, training servers, benchmarks. |
| Metrics computed | `rating{aim, positioning, utility, clutch, opening, ct_leetify, t_leetify}` + ~20 stats incl. `preaim`, `reaction_time_ms`, `spray_accuracy`, `accuracy_enemy_spotted`, `counter_strafing_good_shots_ratio`, `flashbang_hit_foe_per_flashbang`, `flashbang_leading_to_kill`, `he_foes_damage_avg`, `utility_on_death_avg`, `trade_kill_opportunities/success_%`, `traded_deaths_*`, opening-aggression success rates (verified from the live OpenAPI schema). |
| CS2 support (verified how) | **Demonstrated** — schema uses CS2 data sources (`faceit, matchmaking, renown, premier, wingman, competitive`), posts through 2026-08-28, CS2-specific hitbox rework. |
| Published methodology | **Yes — unusually transparent.** "Enemy spotted" via their **own raycaster**, not radar events (`/blog/enemy-actually-spotted/`, hitboxes improved `/blog/aim-stat-calculation-hitboxes-improved/`, 2026-08-11, incl. benchmark re-normalisation to mean 50). **Leetify Rating**: zero-sum, per-round average, kill reward = *change in win probability* from economy-tier + XvX tables derived from **all HLTV CS2 matches**; kill credit split 35% kill / 30% damage / 15% flash assist / 20% traded death; save/objective handling documented (`/blog/leetify-rating-explained/`, 2024-11-25; revised 2026-02-25). |
| Maintenance status | **Very active.** Blog RSS `lastBuildDate` 2026-10-15; posts: Steam-profile extension (2026-08-28), Profiles update (2026-08-17), aim hitboxes (2026-08-11), Highlights provider change (2026-07-30), SCL training collab (2026-03-26). |
| Public API | `https://api-public.cs-prod.leetify.com`, Swagger at `https://api-public-docs.cs-prod.leetify.com/`. Endpoints: `GET /v3/profile`, `/v3/profile/matches`, `/v2/matches/{gameId}`, `/v2/matches/{dataSource}/{dataSourceId}`, `/api-key/validate`. Key from `leetify.com/app/developer`; header `Authorization: Bearer` or `_leetify_key`. |
| Rate limits / pricing | **No numeric limit published** — docs only say requests *with* a key get the higher allowance (429 handling is the implementer's job). Consumer tiers seen in the wild: **Free / Pro / Highlights+** with Pro incl. 2D replay, benchmarks, training servers. Exact USD prices are **not published on public pages** (SPA behind login) — not verified; do not quote a number. |
| Legal constraints (critical) | Developer Guidelines (2025-07-20, updated 2025-12-17): mandatory **"Data Provided by Leetify"** attribution, no renaming/rescaling metrics, "View on Leetify" links, **do not store API data** (and delete it if it stops being served), no implied endorsement. **2026-01-23 privacy update: the public API no longer returns data for non-Leetify-users** (only registered users), plus a profile-hide option that deletes the account. |
| Open/closed + license | Closed, proprietary; API access governed by guidelines that Leetify may change "at any time". |
| Linux compat | N/A (web + browser extension for Steam overlay/Chrome/Firefox). |
| Reusability | **Integrate, don't reuse.** Good: canonical metric *definitions* to imitate; auth+attribution pattern. Bad: no-storage clause kills corpus building; non-user data removal means most opponents are blank; no positional/tick data in API. |
| AI real vs marketing | **No AI marketing.** What exists is real statistics/engineering: a custom raycaster, win-probability tables, Bayesian-style correlations in Post-Match Journal (2025-03-19) with confidence intervals. **No LLM coaching found** in any 2026 announcement. |
| Unsolved problems | Metric weights are proprietary and change silently; no tick/position export; historical API break (Jan 2026) broke integrations; highlights depend on third parties (Allstar) — they just migrated in-house (2026-07-30) after years of dependency. |

Sources: `https://leetify.com/blog/privacy-updates-to-our-api-and-profiles/`, `/blog/leetify-api-developer-guidelines/`, `/blog/leetify-rating-explained/`, `/blog/aim-stat-calculation-hitboxes-improved/`, `/blog/highlights-provider-change/`, `/blog/post-match-journal/`, `https://api-public-docs.cs-prod.leetify.com/swagger.json`, `https://leetify.com/blog/rss/`.

### B2. SCOPE.GG

| Field | Finding |
|---|---|
| What it does | Automatic match ingestion (Steam + FACEIT) → match history, 2D demo viewer in browser, per-match "mistakes" review, auto-recorded clips of best moments, compare tool, aim/grenade stats, grenade predictor, tactical board, **prematch FACEIT opponent analysis**. |
| CS2 support (verified how) | **Demonstrated** — `/replay` page describes automatic CS2/FACEIT demo download + browser 2D replay; FAQ pages are CS2-specific. |
| Maintenance status | Live (app.scope.gg signup 200, 2026-10-15); claims 2M users / "20M demos recorded per month" (unaudited marketing). Recent documented policy change: 2025-05-19 FACEIT free-tier limit (10 uploaded FACEIT matches/month; Steam MM unlimited free). |
| Architecture | **Web-only** — no desktop app/client found (contradicts the task's "desktop app" premise; FAQ explicitly advertises "without any additional software"). Server-side demo download/storage/parse; Steam OAuth + FACEIT OAuth. |
| Data exposed | UI only. No public developer portal, OpenAPI or API-key docs found; contact `support@`/`partnership@scope.gg`. |
| Pricing | Scope Lens historically **$4.99/mo** (2022-04-18 announcement); Scope Prematch documented as a product but price fields don't render; third-party comparison (MapSense, checked 2026-10-01) shows "CS2 Lens Free · from $19/mo". **Treat all Scope prices as unverified.** |
| Open/closed + license | Closed. |
| Linux compat | N/A (web). |
| Reusability | **Ignore as a dependency; watch as a UX benchmark.** Auto-ingest + auto-clip + prematch are product features to imitate, not components. |
| AI real vs marketing | "We'll analyze your matches and point out the mistakes" — no AI/LLM language. Stats + rule/threshold heuristics over parsed demo data. [INFERENCE] (no published method). |
| Unsolved problems | No API (so nothing to reuse); FACEIT limits push users to Steam-MM capture; error-prone "clip recording" needs server-side video pipeline; prematch needs 5 opponents' demos each match. |

Sources: `https://scope.gg/`, `/replay/`, `/match-history/`, `/grenade-predictor`, `https://blog.scope.gg/faceit_limitations/`, `https://blog.scope.gg/scopegg-update-012-en/`.

### B3. PureSkill.gg

| Field | Finding |
|---|---|
| What it does | "Automated coach": auto-downloads Premier/FACEIT (and any uploaded) matches, detects **individual mistakes**, prioritises them, links each to the exact tick in a 2D viewer, plus curated videos/drills per mistake. |
| Assessment inventory (verified on FAQ) | **30+ assessments**: Economy 12 (first-round buys, upgrades, pistol upgrades, save decisions, grenade purchases, Zeus, kits, kevlar refresh, drops, utility-before-death), Grenades 8 (smoke/flash stats, flashing enemies, not flashing teammates, flashes→kill, HE damage, util before death), Shooting 6, Teamwork 4 (trade opportunities/kills/teammates trading your death/utility together), Movement 3, Other 1. Crosshair placement + decision making are **still "coming soon"**. |
| CS2 support (verified how) | **Demonstrated**-ish: Premier/Competitive/FACEIT auto-download; ESEA/Esportal/Gamers Club/HLTV via upload; Wingman "reduced accuracy"; Casual/Unranked unsupported (no replay files). |
| Maintenance status | **Active.** Site asset cache-buster `?v=1792023737` ≈ **2026-10-15** (rebuilt today); free/Pro/Lifetime tiers; `/blog/` is 404 (no blog). The 2018-era founding story and "three physicists" team page still front-and-centre. |
| Architecture | Web app on `csgo.pureskill.gg` (legacy subdomain), server-side demo download+analysis. No client software, on purpose ("you don't install any programs… advice while playing would be cheating"). |
| Data exposed | Out-of-10 scores per assessment, prioritised list, 2D viewer deep-links, shareable match links (viewer must have an account), calibration against **human CS coach ratings** collected in their Discord. No export/API. |
| Pricing | Free (coach + 2D viewer + uploads); Pro **$3.75/mo annual, $5 month-to-month**; Lifetime MVP **$299**; "rank-up guarantee" refund policy. |
| Open/closed + license | Closed. Payment via Stripe/PayPal. |
| Linux compat | N/A (web). |
| Reusability | **Integrate-none / benchmark-much.** The assessment taxonomy is the most directly reusable *artifact* (a ready-made checklist of ~30 mistake detectors with human-coach calibration targets). |
| AI real vs marketing | Claims are modest and method is stated: "statistics, machine learning, deep learning and other techniques" over demo data, scores calibrated to coach 0–10 ratings. Rule detectors are the backbone; **no LLM**. Marketing says "Coach", not "AI". Earns **Plausible-untested** (no published precision/recall). |
| Unsolved problems | No published detector accuracy; crosshair placement and decision-making perpetually "coming soon"; Wingman inaccuracy admitted; benchmark calibration depends on a Discord community of volunteer coaches. |

Sources: `https://pureskill.gg/`, `/how-it-works/`, `/faq/`, `/pricing/`.

### B4. CSReplays (csreplays.com) — LLM demo coach

The single most **engineering-transparent** AI-coaching product found.

| Field | Finding |
|---|---|
| What it does | Upload CS2 demo → 2D radar replay (scrubbable, callouts), named utility lineups with reference clips, trends across matches, and a **round-anchored coaching report**; Pro adds Steam auto-sync (Premier/Comp/Wingman, report 5–10 min after leaving the server). |
| CS2 support (verified how) | **Demonstrated** by design docs: `.dem` upload (FACEIT/ESEA fine, paste steamid64), Steam OAuth, digest generated from parsed ticks. |
| Maintenance status | **New and active**: started **2026-05-04**, blog posts 2026-05-06 → 2026-06-01 (launch notes, auto-sync, prompt training, HLTV→clip pipeline, heuristics+classifier). Free 10 analyses/month; Pro **$9.99/mo**. |
| Architecture (as published) | `.dem` → **digest JSON** (rounds/kills/nades/timing, "hand-shaped enough that Claude could chew on it without hallucinating rounds") → LLM report; parsing via **awpy / demoparser2**; HLTV→clip pipeline is 5 stages ending in stored reference clips; per-map lineup catalogue built by the pipeline, not by hand. |
| Real ML present | **Yes, and measured.** Executes/combos = hand-written heuristics ("the rule *is* the explanation"). Player role = scikit-learn pipeline: impute → scale → **calibrated multinomial logistic regression** (`CalibratedClassifierCV`, isotonic, cv=2) on **31 frozen features**; evaluation = **Leave-One-Group-Out by steamid64**, 63 samples, 14 folds. Published results: pooled f1-macro **0.667**; per class — AWPer 0.97, entry 0.65, support 0.55, **lurker 0.50**; confusion matrix published; hand-rule fallback + `CONFIDENCE_FLOOR 0.35` for "mixed role". Also documents v1 feature failure (mean teammate distance over-tagged lurkers) and its v2 fix. |
| Data exposed | UI + shareable per-match URLs. No API, no export documented. |
| Open/closed + license | Closed. Steam OAuth; "demos stored encrypted, scoped to your account, never used to train models". |
| Linux compat | N/A (web). |
| Reusability | **Integrate-conceptually.** The publishable assets are: (a) the digest-schema approach that makes LLM output verifiable, (b) heuristic thresholds (combo ≤3 s/192 ticks; execute = ≥2 distinct throwers' smokes within 6 s/384 ticks; MR12 pistols = rounds 1 & 13), (c) the honest small-data CV protocol. |
| AI real vs marketing | **Most credible "AI" in the set**: LLM grounded in a parser digest for coaching text + a genuine small statistical model with published metrics *and published weaknesses*. Not "AI" for show. |
| Unsolved problems | n=63 training corpus (role model is at chance for lurker/support); no per-round win/loss in the lineup corpus yet ("we report frequency and location, not win rate"); explicit V1 non-goals: video clips, team-level analysis, live tracking, mobile, aim trainer; single-dev bus factor; no API. |

Sources: `https://csreplays.com/`, `https://csreplays.com/blog`, `/blog/launch-notes-what-shipped`, `/blog/heuristics-and-classifier`, `/blog/training-the-coach-with-pro-demos`.

### B5. ReplayLab (replaylab.pro, "CS2 Replay")

| Field | Finding |
|---|---|
| What it does | Upload `.dem`/`.dem.gz`/`.zst`/`.zip` (FACEIT archives unpacked server-side) → 2D replay **with the demo's team voice chat**, "why you died" positioning episodes (isolation, repeat peek, untradeable position), 3D player-eye view, duel/aim/trade breakdowns, **coach mode** (draw on map, shared rooms), opponent scouting, cross-match recurring mistakes, optional **AI reviews**. |
| CS2 support (verified how) | **Demonstrated** by site copy + sample analysis link (`/app#/sample`); `.dem` + FACEIT archive formats enumerated. |
| Maintenance status | Live (200, 2026-10-15), bilingual landing (RU primary / EN), Paddle as merchant of record, refund policy, 14-day refunds. Claims "interface in Russian for now — English coming". |
| Pricing | Free: 3 uploads/day, 1 trial AI review. **Pro $8.99/mo or $99/yr**, 20 uploads/day, 10 AI reviews/month, unlimited storage. |
| Architecture | Server-side parsing (uploads required; login via Steam **or Telegram**), no client install. |
| Data exposed | UI only; no API. |
| Open/closed + license | Closed. |
| Linux compat | N/A (web). |
| Reusability | Low as code; the **voice-chat-in-replay** feature is the notable differentiator worth studying (CSDM can also export/extract player voice; see A1 `--player-voices`). |
| AI real vs marketing | "AI review" is a paid quota feature — quantity-metered, no methodology published → **Plausible-untested / partly marketing**. Core analysis (positioning episodes, trade checks) looks rule-based. |
| Unsolved problems | Russian-only UI limits adoption; no API; AI review opacity and metering; no evidence of published evaluation. |

Sources: `https://replaylab.pro/?lang=en`, `https://replaylab.pro/about`.

### B6. GetReplay (getreplay.gg)

| Field | Finding |
|---|---|
| What it does | Browser 2D replay review: **Smart Mode** (auto-speeds idle moments, slows frags/flashes), events timeline (jump to any kill/plant), bird's-eye map with player tracking/utility/bomb, Steam match sync, utility/lineup library by map, SEO article corpus, bookmarks. |
| CS2 support (verified how) | **Demonstrated** by site + `/en/example` sample match; Steam login for own demos. |
| Maintenance status | Live (200, 2026-10-15); Sentry-instrumented production build (i.e. a maintained app). No public changelog/blog dates found. |
| Architecture | Next.js web app (`/_next/image`), server-side analysis, Steam OAuth. Ownership/pricing not stated publicly. |
| Data exposed | UI + shareable example match; no API documented. |
| Open/closed + license | Closed. |
| Linux compat | N/A (web). |
| Reusability | Low code-wise. **Smart Mode** and the event-timeline UX are the reusable ideas (both appear in overlapping products). |
| AI real vs marketing | No AI claims. |
| Unsolved problems | No API/export; unclear business model; content/lineup library maintenance burden. |

Sources: `https://getreplay.gg/`, `/en/example`, `/en/utility`.

### B7. Overpeek (overpeek.app)

| Field | Finding |
|---|---|
| What it does | "CS2 demo viewer and analyser, powerful, fast, free"; per third-party summaries: local-first parsing with filtering, utility/position overlays and **optional cloud sharing** (cross-device links for teammates/coaches), `/pricing` exists. |
| CS2 support | **Not verified first-hand** — the homepage renders entirely client-side (only `<title>` fetchable via `read`); `/pricing` and the site return 200, so it is live. Claims come from secondary/Reddit sources. |
| Maintenance status | Live (200, 2026-10-15). Cadence unknown. |
| Architecture / data / API | Unknown (SPA). Reddit thread (`r/GlobalOffensive` "Overpeek — yet another demo viewer, feedback required") implies active indie development. |
| License / Linux | Unknown / browser-based. |
| Reusability | **Unassessed — needs one focused investigation** (browser-render the site or contact the author). |
| AI | No AI claims seen. |
| Note | Listed here to close the loop on the "local-first + share link" pattern (same pattern as cs2replays.com and MapSense). |

Sources: `https://overpeek.app/` (title only), `https://overpeek.app/pricing` (HTTP 200), Reddit `1udpgd5`.

### B8. MapSense (mapsense.gg)

| Field | Finding |
|---|---|
| What it does | Free browser demo platform for players/teams/coaches: 2D replay, **3D replay beta** (real CS2 map geometry/textures, follow-cam, POV with actual weapon + crosshair), stratbook, lineups/setpos, heatmaps, **HLTV Tier-1/2 pro-demo import**, callouts, crosshair restore, **live team review (Watch-Together with guest links, no account needed)**, FACEIT browser extension (veto helper, Elo forecast, one-click demo save). |
| CS2 support (verified how) | **Demonstrated** — live `/app` viewer, `.dem`/`.zip` upload, FACEIT/GOTV mentioned, 3D built "straight from your demo file". |
| Maintenance status | **Active indie**: waitlist + live app; comparison table "checked 1 Oct 2026"; author Maurice Dohmen, used by Huskies eSport Jülich; EN/DE. |
| Pricing | **Free** (features marked free incl. Watch-Together, stratbook). FACEIT extension free. |
| Architecture | Browser + server-side parse; Chrome/Edge/Brave/Opera/Firefox extension; no install for the viewer. |
| Data exposed | UI + share/guest links + comments pinned to ticks. No API documented. |
| Open/closed + license | Closed. |
| Linux compat | N/A (browser; extension cross-browser). |
| Reusability | Low as code. High value as a **free functional benchmark**: they do 3D-from-demo in-browser, pro-demo import and a competitor pricing table (their citations: CS2 Lens from $19/mo, CS2.CAM from $20/mo, Skybox EDGE from €5.99/mo). |
| AI real vs marketing | No AI claims. |
| Unsolved problems | Indie bus factor; 3D beta map coverage; monetisation unclear for a free product; no API. |

Sources: `https://mapsense.gg/en`, `/app`, `/en/waitlist#compare`.

### B9. Suspect.gg

| Field | Finding |
|---|---|
| What it does | **Demo-as-evidence cheat triage**: parse demo → flag aim snaps, wall-tracks, pre-fires into a "Suspect Index" → **render the flagged moment as a shareable video clip** ("no mystery percentages"); community Overwatch-style voting; aggregating Steam/FACEIT/Leetify stats; auto-highlight vault (aces, 1vX, multi-kills) from the same pipeline; Steam-DM bot via `!suspected` in match chat. |
| CS2 support (verified how) | **Demonstrated** — site, `/review`, `/analyze`, `/clips`, live sample; explicit "the game never launches". |
| Maintenance status | Live (200, 2026-10-15), "FREE WHILE IN TEST · NO ADS", blog with case-file posts referencing **Valve's July 2026 spinbot fix**. |
| Architecture | Server-side demo parse + server-side clip render; Steam integration for DMs; no client install. |
| Data exposed | Reports, clips, community votes. No API documented. |
| Open/closed + license | Closed. |
| Reusability | **Integrate (as an anti-cheat signal source) or ignore.** The reusable idea: deterministic clip rendering as *proof* rather than a black-box score — the same "evidence-linked" pattern DAK Studio uses for stats. |
| AI real vs marketing | "Our models marked 1 player… (aim model)" — ML/statistical models over tick data, no LLM. **Plausible-untested** (no metrics published), but the blog's technical posts (aimbot vs assist fingerprints, prefire selectivity, spinbot tells) indicate real tick-level analysis. |
| Unsolved problems | Detection claims unverifiable; community votings can be mobbed; Valve's own anti-cheat catching up reduces value; demo-based cheat detection is inherently probabilistic. |

Sources: `https://suspect.gg/`, `/blog/aimbot-vs-aim-assist-telling-them-apart-on-a-demo`, `/blog/prefire-or-prediction-the-line-we-draw`, `/blog/spinbots-are-back-heres-the-giveaway`.

### B10. Breakdown.gg

| Field | Finding |
|---|---|
| What it does | **Conversational analysis over a demo corpus**: batch-import hundreds of demos into a "collection", index every round/kill/utility, then chat with an AI ("Where does our team lose most rounds?", "how did our B-rush evolve over 3 months"), plus per-match round-by-round scores across six dimensions (Overall/Aim/Impact/Util/…), 2D round replayer, community percentile ranking, team tools. |
| CS2 support (verified how) | **Demonstrated**-ish: site states `.dem` upload, demo table with real maps/rounds/dates, per-match "Ready/Parsing" states. |
| Maintenance status | Live (200, 2026-10-15); prices via Stripe; positions itself vs Skybox (€350–€1,299/mo), Leetify, Scope.gg, CS2.CAM. |
| Pricing | Free / **£5** / **£15** / **£150 per month** (GBP), Stripe. |
| Architecture | Upload → parse → index corpus → retrieval + LLM chat; batch import. |
| Data exposed | UI + AI answers "with visualizations"; no API documented. |
| Open/closed + license | Closed. |
| Reusability | **Integrate-conceptually**: the "corpus + retrieval + LLM" pattern is the closest analogue to our own longitudinal personal-coaching goal, and their bulk-import claim (500+ demos) is the bar for a team archive. |
| AI real vs marketing | **LLM is genuinely the product** here, but is grounded-ness verified? No. Termed "AI Tactical Analyst"; sample answers quote win rates over round counts (62% across 83 rounds) which *implies* grounding in parsed rounds. **Plausible-untested** — no methodology, no evaluation. |
| Unsolved problems | Hallucination risk over large corpora is unaddressed publicly; no evidence of a validation layer (contrast CSReplays' digest bound and DAK's evidence links); pricing jumps 10× per tier without published feature diffs. |

Sources: `https://www.breakdown.gg/`.

### B11. Rivalize (rivalize.pro)

| Field | Finding |
|---|---|
| What it does | **Opponent scouting + AI anti-strats**: upload opponent demos (or link ESEA/FACEIT matches) → tendencies, utility habits, per-player heatmaps, "AI Key Read" (e.g. "B split on 78% of full-buy T rounds after losing pistol"), anti-strat generation per map, veto simulator, 2D & 3D replay, playbook pages, utility hub, team library with H2H/freshness. |
| CS2 support (verified how) | **Demonstrated**-ish: site describes `.dem` uploads + ESEA/FACEIT links, ~2 min parse/demo, radar images for maps. |
| Maintenance status | Live (200, 2026-10-15). Marketing-listing-free; "Free to start · no card". |
| Pricing | Solo **Free**, Pro **$5/mo**, Team **$20/mo**. |
| Architecture | Server-side parse; "AI Scout — ask questions about any opponent in plain English and get answers **cited to rounds**". |
| Data exposed | UI + cited-round answers; no API documented. |
| Open/closed + license | Closed. |
| Reusability | Low as code; **high as competitive-landscape evidence** that AI anti-strat is a crowded wedge, and that "answers cited to rounds" is already the expected grounding standard. |
| AI real vs marketing | LLM/statistical over parsed tendencies; the citation promise is the credible part. **Plausible-untested** (no evaluation published). |
| Unsolved problems | Veto plans need large opponent demo corpora; "cited to rounds" is a claim, not a verified guarantee; crowded market. |

Sources: `https://rivalize.pro/`, `/pricing`.

### B12. csstats.gg (formerly csgostats.gg)

| Field | Finding |
|---|---|
| What it does | Valve-matchmaking-centric CS2 stat tracker: profiles, full match history (beyond CS2's 8 games), post-match advanced stats (entry frags, trades, clutches), round-by-round breakdown, **VAC/Overwatch ban tracking** over your played-with list, rank progress graphs; "Steam Bot beta" for faster tracking + match/ban notifications; `x`-prefixed steamcommunity URL instant redirect. |
| CS2 support (verified how) | **Demonstrated** — CS2 Competitive & Premier focus; self-reported scale on site: **412.1M games processed, 45.1M players, 5.7M VAC bans tracked**; CS2 match parsing launched in the Aug 2023 CS2 beta phase. |
| Maintenance status | Live but **migrated brand**: announcement **2023-09-26** "csgostats.gg has moved to csstats.gg" (Steam group, authored by `rchh`); group founded 2016-06-01, 15.5k members; contact is still `bugs@csgostats.gg` / `richard (at) csstats (dot) gg` (UK). `csgostats.gg` still host-resolves but bot-blocks (HTTP 403 to curl **and** to the reader). |
| Architecture | Server-side Valve MM demo parsing (requires **Steam game auth code** + match submission; bot mirrors), web UI, Discord bot notifications. |
| Data exposed | HTML only. **No public API found.** |
| Open/closed + license | Closed. |
| Linux compat | N/A (web). |
| Reusability | **Ignore for engine reuse; possibly integrate for ban/enrichment signals** — but only via scraping, which is hostile (403) and against no-stated-terms. |
| AI real vs marketing | No AI claims. |
| Unsolved problems | MM-only (no FACEIT/ESEA coverage); depends on user-supplied auth codes; no API; brand confusion between the two domains persists. **Correction made during research:** a web-search summary claimed the site's footer shows "© ESL FACEIT Group Limited" — I could not reproduce that on the live pages (JS-rendered privacy page returns no body); **do not repeat that ownership claim**. |

Sources: `https://csstats.gg/`, `https://steamcommunity.com/groups/csstats-gg/announcements/listing`, `https://csgostats.gg/cs2` (403).

### B13. Refrag.gg

| Field | Finding |
|---|---|
| What it does | Training platform + match analysis loop: **Refrag Coach** (auto match tracking for Premier/Wingman/Competitive/FACEIT, post-match metrics, tailored in-game training recommendations, Steam bot DMs the breakdown), on-demand practice servers (35 locations), Bootcamp/Academy/Utility Hub/Restrat, aim trainers, **2D Demo Viewer**, Detailed Aim Stats. |
| CS2 support (verified how) | **Demonstrated** — site (© 2026) + `wiki.refrag.gg` docs incl. `/en/2d-demo-viewer` live. |
| Maintenance status | **Very active, commercial**: 550,000+ users claimed; sales in EUR/USD; product features dated to 2026 on the site. |
| Pricing | Player **$5.40/mo** (annual) or $7 monthly; Competitor **$11.50** or $15; Team **$60** or $79 — with 2D Demo Viewer, Scrim, Restrat, Academy, Detailed Aim Stats gated to Competitor+. |
| Architecture | Web app + demo parse for Coach/2D viewer; independently hosted game servers for training (their own telemetry is the source of "Detailed Aim Stats" — [INFERENCE]). |
| Data exposed | UI; Steam bot messages; no public API documented. |
| Open/closed + license | Closed (ToS/Privacy on `wiki.refrag.gg`). |
| Linux compat | N/A for the app; servers are geographically distributed game servers. |
| Reusability | **Ignore (code), integrate (ecosystem)**: they are the incumbent "training + analysis" bundle; the 2D demo viewer sitting behind a mid-tier subscription is a direct comp for our viewer. |
| AI real vs marketing | "Rely on Refrag Coach" / "virtual coach" language, no LLM or model claims, no metrics published → **statistically-driven recommendations = Plausible-untested; "AI" = mostly marketing framing.** |
| Unsolved problems | Aim stats come from their servers, not the user's real matches [INFERENCE]; no API; no published accuracy for the coach; gating demo replay behind Competitor tier. |

Sources: `https://refrag.gg/`, `/coach`, `https://wiki.refrag.gg/en/2d-demo-viewer`.

### B14. Game Demon (Altros Studios) — live in-match AI coach

| Field | Finding |
|---|---|
| What it does | **Windows app that coaches you during the match and reviews it after**: (1) live short calls during play/freezetime/after deaths (positioning, peek timing, duels, rotations), (2) "visual coach" combining **screen reading + CS2 Game State Integration** for crosshair placement/peek geometry/minimap, (3) post-match "Reckoning" report + Q&A over the parsed match, (4) tracker.gg-style profile. Also Dota 2 module (early). |
| CS2 support (verified how) | **Demonstrated** by design: GSI stream → normalizer → cue dispatcher → **validator chain** (arithmetic, length, peek-blame, dedup, prompt-leak, natural-delivery, specificity-claim) → spoken callout, sub-2s latency; explicitly contrasts itself with post-match-only analytics (naming Leetify's niche). |
| Maintenance status | **Active, early access**: v**1.9.78**, weekly-improving claims; Stripe checkout, DynamoDB license w/ hardware binding, S3 binaries, magic-link JWT, CloudWatch. Notable: "Valve retired our Steam page on category-fit grounds" → distribution is direct. |
| Pricing | **From $14.99**, 25-credit free trial, 14-day/2-hour refund self-serve. |
| Open/closed + license | Closed (Windows 10/11 only). |
| Architecture notes relevant to us | GSI-based live state ("canonical view of every round: money, armor, weapons, position, team state"), **frame analysis is not stored**, "demo-parsed truth" for the measured aim signature and economy counterfactuals, and a **truth-check step that re-grades live calls after the match** with a visible report card of wrong calls. |
| Linux compat | No — Windows only. |
| Reusability | **Integrate-conceptually (highest-value design doc in the set)** for real-time coaching: validator chains, truth-checking, coach memory (standing focus/intake/journal with user corrections outranking model inference). Not reusable as code. |
| AI real vs marketing | **Real LLM product** ("runs on frontier cloud models", higher-tier reasoning for the Reckoning) *plus* a perception stack (screen reading for what GSI can't see). Honest about error ("the coach can still make mistakes", visible report card). **Plausible-untested** for accuracy, but this is the least hand-wavy live-coaching architecture found. |
| Unsolved problems | Live advice is on the edge of game-integrity rules (they claim no injection and post-match VAC-safety is the norm elsewhere); Windows-only; screen-reading latency (<2 s) is claimed, not audited; per-call truth checks need demo ingest alongside live play. |

Sources: `https://www.altrosstudios.games/gamedemon/`, `/gamedemon/privacy/`, `/changelog/gamedemon`.

---

## C. Pro / B2B platforms

### C1. Skybox.gg (Skybox EDGE + Broadcast)

| Field | Finding |
|---|---|
| What it does | Pro-team analytics (**EDGE**): 2D replayer, team statistics, voice-comms integration, leaderboards, playbook prep, veto simulation, tactical filters; plus **Broadcast** (real-time data/AI graphics for tournament broadcasts) and Publishers. |
| CS2 support (verified how) | **Demonstrated** — EDGE signup live (`edge.skybox.gg/auth/register` 200); customer logos incl. ESL One, ESL Pro League, IEM, PGL, Red Bull, 7Sport, 99Damage; "Licensed by Valve Corporation"; German/Danish entity **SBXE ApS** (Copenhagen, DK-45555887). |
| Maintenance status | **Alive but low public content churn**: homepage/EDGE page meta `article:modified_time` **2024-08-26**; latest asset dated **2025-08**; EDGE marketing claims "85%+ / 90% of Pro teams" and "+$100M tournament revenue" (unaudited). A LinkedIn departure post (Mar 2025) evidences staff turnover but not shutdown. |
| Pricing | Pricing page (last modified 2024-01-16) shows **Tier 2 €350/month**; EDGE page markets "**now free**… Sign up for free"; MapSense's 2026-10-01 comparison lists "Skybox EDGE Free · from €5.99/mo" and "stratbook & lineups ~ from €349/mo". **Conflicting individual vs team pricing — treat as unverified.** |
| Architecture | Web app; 2D replayer; deep integration with comms (voice) and broadcast pipelines; no client install. |
| Data exposed | UI/team workspace; no public API found. |
| Open/closed + license | Closed, B2B contracts. |
| Linux compat | N/A (web). |
| Reusability | **Ignore for reuse; watch as the pro-tier ceiling.** Their price point (hundreds of €/mo for teams) is the ceiling any pro-oriented feature we build is priced against. |
| AI real vs marketing | Broadcast page markets "AI"; EDGE analytics as used by analysts is statistics/visualisation. The 85–90% adoption and $100M figures are **marketing**, unaudited. |
| Unsolved problems | Opaque pricing; aging public site vs claimed live usage; no developer/API surface; heavy B2B sales motion. |

Sources: `https://skybox.gg/`, `/edge/`, `/pricing/`, `/broadcast/`, `https://edge.skybox.gg/auth/register`.

### C2. CS2.CAM

| Field | Finding |
|---|---|
| What it does | Pro/team demo-analysis platform: 2D viewer (paint tools, copy positions, multi-round, grenade mode), **filters across thousands of demos**, heatmaps, **Strategic Board**, **Playbook** (auto-detected defaults/executes/fakes/utility per team, pre-computed over the HLTV library), **Timing Heatmap**, **Veto Analysis (closed beta)**, 3D replay, recording suite (Record Round/POV/Team Recording, cloud rendering, auto OBS), team collab (voice-comms sync aligned to demo, timestamped notes with @mentions, shared playlists), Create-Playbook from top teams with **real win rates**. |
| CS2 support (verified how) | **Demonstrated** — live product with docs (`/en/wiki/...`) and product tour; "10K+ HLTV matches pre-processed", "300+ teams", est. 2024; "Powered by HLTV + FACEIT ingest". |
| Maintenance status | **Active & shipping** — "last 90 days · 5 modules" (Strategic Board, Playbook, Timing Heatmap, Veto Analysis, 3D Replay) each with a wiki article. |
| Pricing | Free tier; **7-day Pro trial**; Strategic Board on all paid plans; anti-strat suite = Pro; MapSense's comparison lists CS2.CAM "from $20/mo". |
| Architecture | Server-side ingest + precomputation of HLTV demos; browser viewer; **desktop app available** for automated recording (OBS integration, "ready in 30 seconds"); cloud recording server-side. |
| Data exposed | UI + saved tactics/playbooks; no public API documented. |
| Open/closed + license | Closed. |
| Linux compat | Viewer = browser; recording desktop app platform not stated (likely Windows, [INFERENCE] from OBS dependency). |
| Reusability | **Integrate-conceptually on the "pre-computed pro corpus" idea** — this is the strongest example of "AI-driven pro demo library": they did the batch work (parse HLTV library, detect strategies, compute win rates, render clips in the cloud) so the user's query is instant. |
| AI real vs marketing | Language is "detected"/"pre-computed", not "AI"; where AI is implied, it's strategy classification over parsed grenade/round data (same family as CSReplays' heuristics). **Research-supported in spirit, Plausible-untested in detail.** |
| Unsolved problems | Closed beta on veto analysis; heavy compute economics (cloud recording for every user); no API; HLTV dependence (see acquisition/legal slice). |

Sources: `https://cs2.cam/`, `/en/wiki/playbook`, `/en/wiki/strategic-board`, `/en/wiki/timing-heatmap`, `/en/wiki/veto-analysis`, `/en/wiki/record-round`, `/en/wiki/voice-comms-sync`.

### C3. GrindLike (formerly "True Grind CS2")

| Field | Finding |
|---|---|
| What it does | Free demo analysis + replay review, Steam/FACEIT sync kept separate, scoreboard→replay flow, notes/team assignments/tags/heatmaps, team workspaces/shared demo library with review states and coach notes; a public interactive simulator demo (Dust2 exec state) and a public status block. Private cloud persistence is the paid upgrade. |
| CS2 support (verified how) | **Demonstrated**-ish: `true-grind-cs2.online` **redirects to `grindlike.pro`** (verified 2026-10-15) with a working product page, no-account public demo and Steam sign-in. |
| Maintenance status | **Active indie, rebranded.** Multiple Reddit update posts through the product's life ("first paying user" post), so it is early-stage commercial. |
| Pricing | Free parsing/review; private cloud persistence + team limits are paid (price not stated on the fetched page). |
| Architecture | Web app + server parse; Steam OAuth; FACEIT linking; "Templates/human context" layer (notes/tags/assignments). |
| Data exposed | UI; no API. |
| Open/closed + license | Closed. |
| Linux compat | N/A (web). |
| Reusability | Low as code; the **team-review workflow** (assignments, review states, coach notes) is the reusable pattern — closer to what a personal-coaching system needs than raw 2D replay. |
| AI real vs marketing | No AI claims. Suspicious-play indicators exist (per Reddit) — rules/heuristics. |
| Unsolved problems | Renaming/domain churn harms discoverability and citation stability; no API; single-dev risk. |

Sources: `https://www.true-grind-cs2.online/` → `https://grindlike.pro/`, Reddit `1un4zzi`, `1u2x85z`, `1ug6bs4`, `1vh8k0y`.

---

## D. Dead, pivoted or unverifiable

| Product | Status (verified 2026-10-15) | Evidence |
|---|---|---|
| **Renown (renown.gg)** | **DEAD — shut down.** "Season 3 marks the end of our journey. **Effective immediately, Renown Counter-Strike matchmaking is shutting down**", published 2026-01-30. Still relevant: CS:DM ships a `dl-renown` command and its source matrix lists Renown CS2 ✅, and Leetify's schema still has a `renown` data source + rank — both now legacy code paths. | `https://renown.gg/blog/renown-is-shutting-down` (meta published 2026-01-30); `cs-demo-manager.com/docs/cli`; Leetify swagger |
| **cs2.gg** | **Placeholder, not a product.** Page renders "Warming Up / Something is coming. Soon™ / Server Online / Players: 0 / 10". | `https://cs2.gg/` |
| **SoStronk (sostronk.com)** | **Parked.** Root returns a JS redirect to `/lander` and nothing else (Indian CS:GO platform era is over). | `https://sostronk.com/` |
| **DemosHub** | **Dead.** `demoshub.com` does not resolve (curl exit 000 / DNS failure); `demoshub.gg` also 000. No verifiable CS2 product of this name; searches return a Steam-"demos hub" unrelated app and an unrelated GitHub repo (`josiasrodri-dev/demos-hub`). | curl 2026-10-15; web search |
| **Fragster (fragster.com)** | **PIVOTED to esports news media.** Now a WordPress news site (CS2/Dota/LoL/Valorant/PUBG/CoD/Fortnite coverage) publishing daily through 2026-10-14; also runs its own tournaments (Fragster Challenger). No demo analysis, no player-tool component. | `https://www.fragster.com/` (meta modified 2026-02-27; articles 2026-10-14) |
| **csgostats.gg** | **Migrated/redirected brand** → csstats.gg (announcement 2023-09-26 by `rchh`). Old domain host-blocks automation (403). | Steam group announcement listing |
| **Cyda** | **Unverifiable — no CS2 product found.** Searches surface unrelated entities (CYDA youth-employment org, hockey association, a Cosmos profile). Treat as noise; do not pursue without a concrete URL. | web search |
| **Rivalry** | **Out of scope — betting operator**, not a demo/analysis tool. Ignore. | (premise check) |
| **CSReplay.com / cs2replays.com / csreplays.com / ReplayLab "CS2 Replay"** | **Four near-identical names, three distinct products.** Name collision is a diligence trap: `cs2replays.com` = free viewer, `csreplays.com` = AI coach, `replaylab.pro` = "CS2 Replay" (RU), `csreplay.com` = simple viewer. | all fetched 2026-10-15 |
| **Long tail not verified (search-only leads)** | `Twoos123/cs2-meta-engine`, `noih/cs-demodesk`, `TheBrokas/DemoQueryCS2` (source-available, position-drawing search), `pr1maly` (local-first, non-commercial license), `zenojunior/cs2d`, `docs.5stack.gg`, `overshoot.gg`, `deadem.com`, `cstrike.gg`, `callup.gg`, `praeverto.gg`, `cswatch.it`, `fragback.gg`, `demo-slap.net`, `csstrats.dk`, `neptunedemos.com`, `noesis.gg`, `breach.gg`, `cs2lens.com` (200 but JS-only title). | search results only — **flag as unverified**; `cs2lens.com` and `overpeek.app` need a browser-render pass |
| **CS2 Lens / CS2.CAM pricing, Skybox tiering** | Referenced only through MapSense's 2026-10-01 comparison table; treat as second-hand. | `https://mapsense.gg/en/waitlist#compare` |

---

## Comparison table

| # | Tool | Class | CS2 demo support | Status Oct 2026 | Price (verified unless marked) | Open source | Machine interface | Linux | "AI" reality | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | **CS Demo Manager** | OSS desktop | Verified (docs matrix + releases) | **Active** (v3.20.1 2026-07-30; commits 2026-10-04) | Free | **MIT** (+MIT Go analyser) | CLI: json/xlsx/video/analyze | **Yes (AppImage)** | None claimed | **REUSE** |
| A2 | **CS2 Insight Agent** | Source-available desktop | Verified (README) | Active (936★, 870 commits) | Free (non-commercial) | PolyForm NC + closed skins | v3-ZIP export → DAK | **No (Win only)** | LLM commentary only; coach unbuilt | **INTEGRATE (ideas) / IGNORE (code)** |
| A3 | **DAK Studio / cs2-demo-analysis-kit** | OSS desktop + libs | Verified (README/seam) | Active (v0.8.6) | Free | **MIT libs / AGPL app** | `cs2dak` CLI + npm pkgs | Not shipped | No AI; explicit no-black-box | **REUSE (libs)** |
| A4 | **cs2replays.com** | Free web viewer | Verified (WASM claim on site) | Live | Free (ads) | Closed | None | Browser | None | **IGNORE (code) / BENCHMARK** |
| B1 | **Leetify** | Stats SaaS + API | Verified (schema + 2026 posts) | **Very active** | Free/Pro/Highlights+ (**prices not public**) | Closed | **REST API + key** (no-store, attribution, non-user data removed) | Browser | No AI claims; real raycaster/win-prob model | **INTEGRATE (metrics), do not depend** |
| B2 | **SCOPE.GG** | Stats SaaS | Verified (auto demo download, 2D viewer) | Live (FACEIT limits since 2025-05) | Lens $4.99 (2022) · Prematch n/a (**unverified**) | Closed | **None** | Browser | No AI; heuristics [INFERENCE] | **IGNORE** |
| B3 | **PureSkill.gg** | Coaching SaaS | Verified (30+ detectors, FAQ) | Active (asset build today) | Free / $3.75–$5 / $299 | Closed | None | Browser | ML+DL claim, coach-calibrated 0–10; no LLM | **INTEGRATE (taxonomy)** |
| B4 | **CSReplays (csreplays.com)** | LLM coach | Verified (engineering blog) | New, active (May 2026→) | Free 10/mo · $9.99/mo | Closed | None | Browser | **Real**: grounded LLM + calibrated LR (f1 0.667, n=63) with published confusion matrix | **INTEGRATE (pattern)** |
| B5 | **ReplayLab (replaylab.pro)** | LLM-ish coach | Verified on site | Live | Free 3/day · $8.99/mo · $99/yr | Closed | None | Browser | Metered "AI reviews", no method | **IGNORE** (watch voice-chat UX) |
| B6 | **GetReplay** | Viewer SaaS | Verified (example match) | Live | Not stated | Closed | None | Browser | None | **IGNORE** |
| B7 | **Overpeek** | Viewer | **Unverified** (JS-only) | Live | /pricing exists | Unknown | Unknown | Browser | Unknown | **INVESTIGATE** |
| B8 | **MapSense** | Free team viewer + 3D | Verified (live app, 3D from demo) | Active indie | Free | Closed | None | Browser | None | **BENCHMARK** |
| B9 | **Suspect.gg** | Anti-cheat triage | Verified (clips from demo) | Live, free-in-test | Free | Closed | None | Browser | Models over ticks, no metrics | **INTEGRATE (evidence-clip pattern)** |
| B10 | **Breakdown.gg** | LLM corpus analyst | Verified-ish (demo table) | Live | £0/£5/£15/£150 | Closed | None | Browser | LLM is the product; grounding unverified | **INTEGRATE (corpus+chat pattern)** |
| B11 | **Rivalize** | AI anti-strat | Verified-ish | Live | Free / $5 / $20 | Closed | None | Browser | LLM/ML with round citations claimed | **IGNORE (crowded)** |
| B12 | **csstats.gg** | Stats SaaS | Verified (MM-only) | Live, rebranded from csgostats.gg (2023) | Free | Closed | None | Browser | None | **IGNORE** |
| B13 | **Refrag.gg** | Training + analysis | Verified (wiki/2D viewer) | **Very active** | $5.40–$11.50–$60 (annual) | Closed | None | Browser + own servers | "Virtual coach", no models published | **IGNORE (code) / COMPETE** |
| B14 | **Game Demon** | Live AI coach | Verified (GSI + visual coach design) | Active early access (v1.9.78) | from $14.99 | Closed | None | **No (Win)** | Real LLM + validator chain + truth-check | **INTEGRATE (architecture)** |
| C1 | **Skybox.gg** | Pro B2B | Verified (EDGE live) | Alive, low content churn (site 2024-08) | €350/mo tier; "free" tier; €5.99 claim (**conflicting**) | Closed | None | Web | "AI" in Broadcast only; adoption % = marketing | **IGNORE (pricing ceiling reference)** |
| C2 | **CS2.CAM** | Pro platform | Verified (live + wiki) | Active (5 modules in 90 days) | Free + trial; Pro (~$20 per MapSense) | Closed | None | Browser + desktop recorder | Strategy detection, not branded AI | **INTEGRATE (pre-computed-corpus idea)** |
| C3 | **GrindLike (ex True Grind)** | Team review | Verified (live, rebranded) | Active indie | Free + paid cloud | Closed | None | Browser | None | **BENCHMARK (workflow)** |
| D | Renown · cs2.gg · SoStronk · DemosHub · Fragster · csgostats.gg | — | — | **Dead / parked / pivoted / migrated** | — | — | — | — | — | **IGNORE (flag as decaying)** |

---

## Reuse verdict summary

- **Directly reusable code/licenses:** `akiver/cs-demo-analyzer` (MIT, Go) and `akiver/cs-demo-manager` (MIT, Electron+CLI) → **reuse** for ingest, and for a reference match/round model. `@cs2dak/*` + `cs2df` (MIT) → **reuse** for derived signals and world→radar transforms; avoid `apps/dak-studio` (AGPL).
- **Integrate (contractually) with care:** Leetify API — viable only for the user's own registered account, with "Data Provided by Leetify" attribution, **no storage**, no metric rescaling, and an expectation of breakage.
- **Pattern donors (no code):** CSReplays (parser-digest→LLM grounding + honest ML evaluation), Game Demon (validator chain + post-match truth-checking + coach memory), DAK Studio (tick-linked evidence for every stat), Breakdown.gg/Rivalize (corpus + retrieval + cited answers), GrindLike (team review workflow), CS2.CAM (pre-computed pro corpus), PureSkill (30-detector taxonomy calibrated to human coaches).
- **Ignore:** SCOPE.GG, GetReplay, ReplayLab, csstats.gg, Refrag (as a dependency), Skybox, cs2.gg, SoStronk, DemosHub, Fragster, Rivalry, Cyda.
- **Investigate before finalising:** Overpeek (JS-only page) and `cs2lens.com`; both need a real browser render.

---

## Cross-cutting notes (this cluster)

**Gaps / duplicate work observed**
1. **One parser substrate, N re-implementations of everything above it.** CSReplays (awpy+demoparser2), DAK (`cs2df`→demoparser2), CS2 Insight Agent (consumes DAK's seam), CSDM (own Go analyser), and every SaaS (cs2replays, GetReplay, Overpeek, MapSense, Refrag, Skybox, CS2.CAM, Rivalize, Breakdown, ReplayLab, GrindLike, Suspect) re-build the *same* layer: 2D radar replay + world→radar calibration + heatmaps + kill/utility timeline. That is the single biggest duplicated engineering effort in the ecosystem, and the clearest justification for leaning on `cs-demo-analyzer`/`@cs2dak/*` instead of writing our own.
2. **Nobody publishes demo→coaching ground truth.** Only two products publish anything verifiable: **CSReplays** (role classifier f1-macro 0.667 @ n=63, full confusion matrix) and **Leetify** (raycaster design + win-probability tables). PureSkill, Refrag, SCOPE, Breakdown, Rivalize, Suspect, ReplayLab and Skybox all ship judgement without published precision/recall. *A personal-coaching system that reports its own detector accuracy would be differentiating.*
3. **LLM coaching is table stakes; grounding is the differentiator.** CSReplays bounds the LLM with a hand-shaped digest ("cannot reference rounds that did not happen"); Rivalize claims round citations; Breakdown indexes a corpus; Game Demon truth-checks live calls. ReplayLab charges per "AI review" without method. Nothing in the set demonstrates an automated **hallucination check** — that is an open, exploitable gap.
4. **No shared callout/lineup/radar dataset.** CSReplays built a 107-combo execute catalogue (7 maps) by pipeline; CS2.CAM precomputed the whole HLTV library; Refrag/Rivalize/MapSense each maintain their own lineups. There is no licensed open callout+lineup corpus — a real "buy vs build" decision point.
5. **Attribution/legal precedent to design around.** Leetify's 2026-01-23 move (public API returns only registered users' data, no-storage rule, hide-profile deletes account) is the template for how vendors will respond to bulk consumption. Any design that depends on third-party stats APIs must assume revocation.
6. **Upstream platform decay is the fragile seam.** Renown is dead (2026-01-30); CSDM's FACEIT demo download is *disabled*; ESEA never supported CS2 servers; csgostats.gg lost its brand; DemosHub/SoStronk/cs2.gg are gone. Demo *acquisition* (Valve share codes, FACEIT pages, HLTV) is where products die — this cluster's survivors all insourced acquisition or made the user supply the file.
7. **Name collisions are a diligence hazard:** `cs2replays.com` / `csreplays.com` / `csreplay.com` / `replaylab.pro ("CS2 Replay")`; plus "True Grind" → "GrindLike" rebrand; plus two different "Lens" products (SCOPE Lens, CS2 Lens).
8. **Deferred to other slices:** parser libraries (sibling `01-parsers-libs`), demo acquisition/expiry (Acquisitions slice), academic/AI-coach prior art (`07-ai-coach-priorart.md` was already present in `research/parts` when this file was written — the 2026 arXiv IDs repeatedly surfaced by search (e.g. 2608.24893, 2606.31461, 2606.25337, 2609.00441) belong there, not here).
9. **Two claims I explicitly could not verify and therefore did not propagate:** (a) csstats.gg being owned/operated by ESL FACEIT Group (a search summary asserted a copyright line I could not reproduce); (b) SCOPE.GG current USD pricing (Lens $4.99 is from a 2022 post; MapSense's 2026 table says "from $19/mo"). Also unresolved: whether `overpeek.app` and `cs2lens.com` are local-first (both render client-side only).

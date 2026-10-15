# A — CS2 Demo-Analysis Ecosystem Survey

**Part I §3 of the feasibility study: the CS2 demo-analysis ecosystem — what exists, what it really
does, what we can reuse, and what is genuinely unsolved.**

| | |
|---|---|
| **Status** | Research complete for the tools/APIs/assets/prior-art scope. Verification date: **2026-10-15**. |
| **Method** | Primary sources only: PyPI/npm/crates.io JSON APIs, GitHub repo + commits + release pages, official docs, OpenAPI/swagger specs fetched and parsed, source files (Rust/C#/TS/JS) read directly, live product pages, schema dumps. Version/date/license/activity facts are machine-verified; API-surface facts come from source and tests; *semantics* claims are graded separately. |
| **Evidence grades** | **Demonstrated** (shipped, documented, or read in source) · **Experimental** (works, unproven/partial) · **Research-supported** (published, not productised) · **Plausible-untested** (credible but unverified) · **Infeasible** (ruled out with evidence). |
| **Recency rule** | 2024 → 2026-10 primary; older work included only when it is the load-bearing prior art (WPA 2020, ESTA 2022, ggViz 2021, Skybox 2020). |
| **Deep-dive appendices** | `./research/parts/01-parsers-libs.md` · `02-vendor-apps.md` · `03-apis-data.md` · `04-map-geometry-nav.md` · `05-viewers-2d.md` · `06-academic-datasci.md` · `07-ai-coach-priorart.md` · `07b-commercial-competitors.md`. This file is the self-contained master: per-tool entries, comparison tables, reuse verdicts, gaps. |
| **Non-goals** | Acquisition automation mechanics (owned by the acquisition slice), coaching methodology/science (owned by the coaching-science slice). Where those touch this scope, they are flagged, not decided. |

> **Warning up front.** Almost everything in this space is re-derived from the same three
> primitives, and the two things that *look* hardest are already solved:
> **(1) fog-of-war visibility is Demonstrated** (awpy + awpy-data, two independent implementations);
> **(2) demo parsing is a mature, MIT-licensed, Linux-native shelf product.** The genuinely unsolved
> problems are **validation** (does the visibility model match what the player actually saw?) and
> **decision quality** (was the choice wrong *given what the player could see*?) — see §7.

---

## 0. Bottom line up front

1. **Parsing is solved. Use `awpy` 3.x as the primary dependency and `demoparser2` as a sidecar.**
   awpy 3.0.0 (MIT, released **2026-10-14**) is a Rust rewrite over `pbdems2` with Polars DataFrames,
   manylinux x86_64/aarch64 wheels, and — uniquely — it ships the *analysis primitives*: cached
   rounds/kills/damages/grenades/smokes/fires/flashes/economy/stats datasets, arbitrary per-tick
   props, plus **`VisibilityChecker`, `NavMesh` and `map_control`**. `demoparser2` 0.42.0
   (MIT, 2026-08-08) is the only mainstream Python parser exposing **`spotted` /
   `approximate_spotted_by`** and the **usercmd/subtick input block**. Neither alone covers both.
2. **Fog-of-war reconstruction is Demonstrated, not research.** Three independent stacks recompute
   CS2 line-of-sight from map collision geometry + demo state; awpy's is the packaged, MIT, per-build
   one. Its limits are known and specific: **horizontal FOV only (pitch ignored), nav-area
   granularity, smoke as a sphere (r=144, h=60), static geometry (no moving doors/penetration)**.
3. **The in-demo `m_bSpotted`/`m_bSpottedByMask` signal must NOT be used as ground truth.** Both
   parsers that expose it disclaim it (`"This is NOT 'Line of Sight' / FOV"`), the demoparser2 mapping
   resolves only **bits 0..15**, and the closest published audit (Leetify, 2020-10-04) measured 0–500 ms
   lag, part-of-model/angle dependence, a post-LOS "shadow", and AWPers firing before the event — and
   replaced it with geometric LOS. Use it as a *corroborator*.
4. **No ground-truth visibility dataset exists anywhere.** awpy's visibility tests are synthetic (a
   single wall quad); nobody validates geometric LOS against what a player actually saw on screen.
   Building that labelled set is **greenfield work and the single highest-value artefact** in this
   space.
5. **The player's actual input is recoverable.** Since CS2 build **10896 (~July 2026)** servers send
   ~99.8–99.9% of `svc_UserCmds` as **`delta_data`** (Valve's own delta encoding, ~90% of all net
   messages). demoparser2 now decodes it (`usercmd_*`, `usercmd_subtick_moves`); CS2DemoKit documents
   a full `UserCmdReconstructor`. **Per-tick view angles, mouse deltas, button press/release and
   sub-tick move steps are available** — the raw material for decision-quality evaluation. Almost
   nobody uses this yet.
6. **Ingestion is the project's real schedule risk, not analysis.** FACEIT demo bytes require a
   **gated Downloads-API token (application, expected ≤30 days)**; FACEIT's Data API exposes **no
   positions, ticks or events** and `demo_url` is a private resource ref at `POST /download/v2/demos/download`.
   Steam has **no CS2 match-history Web API**; the Game Coordinator returns only the **last 8
   matchmaking matches** with **~1-month replay-link expiry**. HLTV **prohibits scraping** (ToS eff.
   2025-01-27). There is **no "fetch any CS2 demo via API" path** — the architecture must treat
   *user-supplied files* as a first-class input.
7. **Third-party stats APIs are a trap for local-first.** Leetify's API is aggregate-only and its
   Developer Guidelines **forbid storing API data**; since **2026-01-23** it returns data only for
   registered Leetify users. Fine for enrichment, unusable as a longitudinal local store.
8. **We are not first, but the market has explicitly *not shipped* our core.** PureSkill.gg (built
   since 2018, 30+ graded assessments) lists **"Decision making — rotate or hold? peek or reload?"**
   and **"Crosshair placement"** as **coming soon**. CSReplays markets repeat-mistake detection
   ("you re-peeked the same angle three rounds after dying to it") without a published method.
   Leetify's Rating is an *outcome* impact model, not counterfactual evaluation.
9. **Two licence landmines:** the best-looking local-first prior art (`pr1maly`) is
   **Source-Available Non-Commercial**; DAK Studio's app is **AGPL-3.0-only** (network copyleft) while
   its libraries are **MIT**. Take `@cs2dak/*` + `cs2df`, never `apps/dak-studio`.
10. **Most reusable non-parser assets:** `cs2-demo-format` v3 + `cs2df` (MIT, validated intermediate
    format), `akiver/cs-demo-analyzer` (MIT Go) with `cs-demo-manager` (MIT, Linux AppImage),
    `awpy-data` (MIT scripts, per-`ClientVersion` nav/radar/mesh releases), `map_data.json` transforms,
    ValveResourceFormat (MIT asset extraction), `csgo-sharecode` (MIT), and Leetify's **published**
    rating mathematics as a modelling template.

---

## 1. Master comparison tables

### 1.1 Parsing & programmatic tooling layer

| Project | Kind | CS2 | Latest artifact (date) | License | Linux | Spotted/visibility | usercmd | Verdict |
|---|---|---|---|---|---|---|---|---|
| **awpy 3.x** (`pnxenopoulos/awpy`) | Python+Rust analysis lib | ✅ CS2 only | PyPI **3.0.0** 2026-10-14 (3.1.0 on `main`, commits 2026-10-15) | MIT | ✅ x86_64/aarch64 wheels, py3.11–3.15 | ✗ `spotted`; ✅ geometric `VisibilityChecker`+`NavMesh`+`map_control` | ✗ (protos only) | **REUSE (primary)** |
| **pbdems2** | Rust Source-2 core | ✅ (protos by consumer) | crates.io **0.4.0** 2026-10-12 | MIT | ✅ pure Rust | n/a | n/a | **INTEGRATE via awpy** |
| **demoparser2** (`LaihoE/demoparser`) | Rust → Py/Node/WASM | ✅ CS2 only | PyPI/npm **0.42.0** 2026-08-08; commits 2026-10-05; WASM pkg stale 0.15.0 (2023-12) | MIT | ✅ | ✅ `spotted`, `approximate_spotted_by` (16-bit, "approximate") | ✅ `usercmd_*` (subtick_moves bug #345) | **INTEGRATE (prop/input sidecar)** |
| **demoinfocs-golang** | Go stream parser | ✅ CS2+CS:GO | **v6.0.0-alpha.1** 2026-10-11; stable **v5.2.0** 2026-04-21 | MIT | ✅ pure Go | ✅ `IsSpottedBy`/`SpottersOf` — docs say *"NOT LOS/FOV"* | buttons event; v6 adds full `UserCmd` | **INTEGRATE only for MM chat decryption / CSTV+** |
| **cs-demo-analyzer** (`akiver`) | Go CLI/lib | ✅ | v1.11.0 2026-09-09 | MIT | ✅ | ✗ | ✗ | **REUSE (ingest + `csdm` JSON)** |
| **demofile-net** | C# lib | ✅ CS2+Deadlock | commits 2026-05-09 | MIT | ✅ .NET | schema-level access | ✗ | **IGNORE** (unless .NET) |
| **demofile (JS)** | Node lib | ❌ CS:GO only | **archived** 2025-08-31 | MIT | ✅ | ✗ | ✗ | **IGNORE** |
| **ValveResourceFormat / Source2Viewer** | Source 2 asset tool | ❌ **cannot read `.dem`** (issue #1122 closed "Unsupported File", 2026-10-08) | release **20.0** 2026-08-17; commits 2026-10-14 | MIT | ✅ | ✗ | ✗ | **INTEGRATE as asset source only** |
| **GameTracking-CS2** | proto + schema dumps | ✅ source of truth | commits **2026-10-15** (build 2000932) | SteamDB-style dump | n/a | defines `EntitySpottedState_t` | defines `CMsgServerUserCmd.delta_data` | **REUSE (schema reference)** |
| **csgo-demoinfo** (Valve) | Official C++ | ❌ CS:GO only, dead 2017-12-19 | — | Valve | ✅ source | ✗ | ✗ | **IGNORE — no Valve CS2 parser exists** |
| `cs2parser` / `@deademx/cs2` | JS/TS | ✅ claimed | 4.0.2 2026-10-09 | unverified | ✅ | unverified | unverified | **WATCH** (only decoder of smoke voxels) |
| **demos.tf / demostf** | TF2 hosting+API | ❌ **TF2 only** | code on Codeberg | open | ✅ | ✗ | ✗ | **IGNORE** |

### 1.2 Products & competitors (who already sells this)

| Product | Class | Status Oct 2026 | Open? | Machine interface | AI reality | Our read |
|---|---|---|---|---|---|---|
| **PureSkill.gg** | Automated coach | Active since 2018; **30+ labelled detectors**, categories: economy 12, grenades 8, shooting 6, teamwork 4, movement 3, "other" growing | ✗ | none | No LLM; 0–10 scores calibrated to human coaches | **Competitive baseline.** "Decision making" + "crosshair placement" **still unshipped** → our wedge |
| **CSReplays** (csreplays.com) | LLM coach | New, active (2026) | ✗ | none | **Real**: grounded LLM over a hand-shaped demo digest + **calibrated logistic-regression role classifier with published LOGO-CV metrics** (f1-macro 0.667, n=63; AWPer 0.97 / entry 0.65 / support 0.55 / lurker 0.50) + confusion matrix | **Best grounding pattern in the ecosystem.** Closed → benchmark & pattern donor |
| **Leetify** | Stats SaaS + API | Very active | ✗ | REST + API key | No AI branding; real raycaster for "enemy spotted" + win-probability impact model | **Integrate metrics only, never persist** |
| **SCOPE.GG** | Stats SaaS | Live; 2 M registered users (self-reported) | ✗ | none | Undisclosed heuristics | Ignore for code; UX reference (tactical board, grenade predictor) |
| **ReplayLab** (replaylab.pro) | "AI review" coach | Live, RU UI | ✗ | none | Metered "AI reviews", **no method disclosed** | Watch: ships **3D player-eye view** + "who saw whom first" |
| **Skybox.gg → Skybox EDGE** | Pro/B2B | **Alive** (rumours of death are false) | ✗ | none | "AI" only in Broadcast; adoption % = marketing | Pricing-ceiling reference |
| **Refrag.gg** | Training + analysis | Very active | ✗ | none | "Virtual coach", no models published | Compete, don't integrate |
| **Game Demon** (Altros) | Live in-match AI coach | Early access (v1.9.78), from $14.99, Windows | ✗ | none | **Real guardrail stack**: GSI+screen-reading → validator chain → post-match truth-check with a visible "calls I got wrong" report card | **Integrate the architecture idea** |
| **DEMO-SLAP** (demo-slap.net) | MCP + REST clip renderer | Live, OpenAPI **2.5.0** | ✗ | **Remote MCP (OAuth/Steam) + REST** | n/a (not coaching) | **Integrate (optional) for clip rendering** |
| **DAK Studio** (`Starfie1d1272/cs2-demo-analysis-kit`) | Local-first studio + packages | Active (commits **2026-10-15**) | **MIT libs / AGPL app** | `cs2df` (PyPI) + `@cs2dak/*` (npm) | No AI; explicit "no black boxes", tick-linked evidence | **REUSE the MIT half** |
| **CS Demo Manager** (`akiver`) | OSS desktop | **v3.20.1** 2026-07-30; commits 2026-10-04 | **MIT** | `csdm` CLI: analyze → json/xlsx/video | none claimed | **REUSE** — but its FACEIT download is **disabled** |
| **CS2.CAM** | Pro platform | Active (5 modules in 90 days) | ✗ | none | Strategy detection, not branded AI | Corpus idea only |
| **MapSense / Breakdown.gg / Rivalize / Suspect.gg / GrindLike / GetReplay / cs2replays.com / csstats.gg** | viewers, LLM analysis, anti-cheat triage, team review | Live (unverified depth) | ✗ | mostly none | mixed / undisclosed | Benchmark; **Suspect.gg's evidence-clip pattern** is worth copying |
| **Renown** | Matchmaking+stats | **DEAD — "effective immediately", 2026-01-30** | — | — | — | ⚠️ CSDM + Leetify still carry dead `renown` code paths |
| **cs2.gg / SoStronk / DemosHub / Fragster / csgostats.gg** | — | placeholder / parked / **NXDOMAIN** / pivoted to news / migrated→csstats.gg | — | — | — | Flag as decaying |
| **pr1maly** (`pr1malator/pr1maly`) | Local-first tracker + LLM coach | 15 commits, last **2026-08-14** | **Source-Available Non-Commercial** | own FastAPI | LLM narrative over pre-computed facts | **Closest prior art; code cannot be reused** |
| **counterstrafe** (`naeyn`) | 2D replay + coach review | 8 commits, last **2026-01-22** | MIT (badge; **no LICENSE file**) | Fastify REST | none | Design reference (flags + threaded review) |
| **CS2DemoKit** (`CS2OpenDev`) | .NET parser + rules + **visibility BVH** | 116 commits, last **2026-09-25** | **MIT** | NuGet packages | n/a | **Integrate the design** (`enemy_spotted`, two tick clocks) |
| **cs2-meta-engine** (`Twoos123`) | Pro-demo mining + anti-strat | last **2026-10-03** | **no license** | — | heuristic "lineup impact" | Ideas only (lineup delta feedback) |
| **DemoQueryCS2** (`TheBrokas`) | Scenario search over your demos | v1.1.0, last **2026-09-06** | free-for-use `LICENSE.txt` (not OSI) | none (Windows app) | n/a | **Copy the algorithm** (nav-node Chamfer search) |
| **VDAPI/cs2-analyst** | SaaS skeleton | last **2026-10-13** | no license | — | "mistake reports" **planned, not built** | Evidence FACEIT worker is the standard pattern |

### 1.3 Map / geometry / radar layer

| Item | Layer | Class | License | Verdict |
|---|---|---|---|---|
| **awpy-data** (per-`ClientVersion` releases: `navs.zip`, `images.zip`, `geometry.zip`, `map_data.json`) | Assets | **Demonstrated** (daily CI gated on Steam buildid) | MIT (scripts only; **assets are Valve's**) | **REUSE** |
| **awpy `.mesh` (`AWMH`) + BVH `VisibilityChecker`** | LOS geometry | **Demonstrated** (Rust source read) | MIT | **REUSE** |
| **awpy `map_control`** (`raycast`/`vision`/`reachability`) | Fog of war / area control | **Demonstrated** | MIT | **INTEGRATE (model semantics)** |
| **CS2DemoKit `Analysis.Visibility` + `enemy_spotted`** | Fog of war | **Demonstrated** (bakes out-of-band) | MIT | **INTEGRATE (design)** |
| **CS2FOW** (server anti-wallhack: BVH8, voxel smokes, hitbox capsules, `CheckTransmit`) | Fog of war | **Demonstrated** then **ARCHIVED 2026-10-06 → closed source** | MIT at archive | Reference technique only |
| `njyeung/CS2FOW-pvs` | PVS pruning | **Experimental**, unbenchmarked | MIT | **WATCH** |
| **`world_visibility.vvis`** + VRF `IWorldVisibility`/`BspVoxelVisibility` | PVS | Demonstrated (parse) / Research-supported (player LOS use) | MIT | **WATCH** |
| Source 1 BSP/visleaves (`bsp_tool.py`) | PVS | **Infeasible for CS2** (CS:GO only) | GPL-3.0 | **IGNORE** |
| **`<map>.txt` overview KV1** (`pos_x/pos_y/scale/rotate/zoom`, `verticalsections`) + `map_data.json` | Radar transform | **Demonstrated** (raw files read) | Valve data | **REUSE** |
| **Source2Viewer-CLI / VRF** (VPK → glTF, nav→GLB, vmap decompile) | Tooling | **Demonstrated** | MIT | **INTEGRATE** |
| `source-vpk` (Rust) / `vpk-tools` (Node) | VPK readers | Demonstrated (tested on real `pak01_dir.vpk`) | MIT | **REUSE** per language |
| **VPKEdit** | VPK | **"will not parse any Source 2 filetypes"** | MIT | **IGNORE for CS2** |
| **Smoke voxels** `C_SmokeGrenadeProjectile.m_VoxelFrameData` (32³ · 20 u, Morton, `(grid−16)·20+det`) | Utility model | Demonstrated (schema) / Experimental (constants) | Valve data | **INTEGRATE with sphere fallback** |
| **awpy smoke sphere** (`r=144`, `h=60`) | Utility model | **Demonstrated** | MIT | **REUSE as cheap default** |
| **Molotov** `C_Inferno.m_firePositions[64]`, `m_bFireIsBurning[64]`, bounds | Utility model | **Demonstrated** (schema) | Valve data | **REUSE (read, don't model)** |
| **Penetration** `weapons.vdata` (damage/armor ratio/penetration) + surface properties + `ExternalAutoWallCS2` algorithm | Wallbang | Demonstrated data / Experimental sim (`items_game.txt` has **no** penetration field) | Valve data / MIT | **INTEGRATE data; validate formula** |
| **Audio occlusion** Steam Audio convars (`num_rays 65536`), `surfaceproperties_steamaudio.txt` (11-band), `CSteamAudioBakedOcclusionData` | Audio | Demonstrated (exists) / Plausible-untested (reproduce) | Valve data | **INTEGRATE inputs; approximate** |
| **Height/verticality** nav `centroid_z` + `verticalsections` | Verticality | **Demonstrated** | MIT | **REUSE** |

### 1.4 Viewers / visualisation

| Project | Kind | License | Embeddability | Verdict |
|---|---|---|---|---|
| `sparkoo/csgo-2d-demo-viewer` | 2D replay + **FACEIT share-link extensions** | **MIT** | Medium (fork app; clean parser↔player seam) | **INTEGRATE** |
| `skkwowee/cs2-demo-viewer` | 2D radar + cones/LOS (**radar-PNG pixel raycast**) | **MIT** | **High** (one canvas component + documented schema) | **INTEGRATE** |
| `naeyn/counterstrafe` | 2D replay + analysis + **coach review queue** | MIT (no LICENSE file) | High (monorepo, REST, shared types) | **INTEGRATE (design)** |
| `akiver/cs-demo-manager` | Desktop manager + stats + replay | **MIT** | Low (app) / High (UX ref) | **INTEGRATE** |
| `Gary2005/cs-net` | **3D** replay + ML paths | MIT | Medium | **REFERENCE (3D)** |
| `zenojunior/cs2d` | 2D replay, telestrator, heatmaps, voice | **NONE** | **Blocked** | **IGNORE code / UX ref** |
| `pableeee/cs-demo-viewer` | Portable single-HTML replay | **NONE** | **Blocked** | **IGNORE code / idea: portable HTML** |
| `boltobserv` | **Live** observer radar (GSI, not demo) | **GPL-3.0** | Low (copyleft) | **IGNORE unless GPL** |
| `Elkhan-Isayev/cs-viewer` | Embeddable 3D viewer | unverified | High | **IGNORE (CS 1.6 only)** |
| `commitandpray67/radar`, `Sylixa/cs2demoview`, `Twoos123/cs2-meta-engine` | viewers | **NONE** | **Blocked** | **IGNORE** |

### 1.5 Datasets & academic methods

| Item | Type | Game | Year | Access | Verdict |
|---|---|---|---|---|---|
| **ESTA** (`pnxenopoulos/esta`) | dataset, 1,558 demos / 41,782 rounds / 3.9 GB | CS:GO | 2022 | CC-BY-SA-4.0, **pinned awpy 1.3.1** | **INTEGRATE as training corpus** (⚠️ awpy-1.x pin conflicts with awpy 3.x tooling) |
| **CS2 Playstyle & Roles 2024** (Packer) | dataset (TAPD/OAP/PODT/POKT/ADNT/ADAT + role labels) | CS2 | 2024 | CC-BY-4.0 | **REUSE features** |
| **CS2CD** | dataset, 795 matches / 52.6 GB tick CSVs + VAC cheater labels | CS2 | 2025 | **CC BY 4.0**, doi 10.57967/hf/5654 | **INTEGRATE as ground-truth/benchmark** (labels noisy; processed, not `.dem`) |
| Kaggle CS:GO round-winner (122,410×97) | tabular | CS:GO | ~2021 | Kaggle | **INTEGRATE as WinProb baseline** |
| `btp_cs2` (Kumar) | thesis+code, SOM role discovery | CS2 | 2026 | repo | **REUSE method** — reports the **null result**: role consistency does *not* predict next-round outcome |
| Skybox CSGO.ai | dataset ~700 demos | CS:GO | 2020 | unclear, **dead** | **IGNORE** |
| VOR.TECH world-model | bots | bots | 2026 | CC-BY-NC | **IGNORE** |
| **Xenopoulos 2020 WPA** (arXiv:2011.01324) | paper | CS:GO | 2020 | arXiv | **REUSE (canonical core)** |
| Xenopoulos 2021 economy/MDP (arXiv:2109.12990) | paper | CS:GO | 2021 | arXiv | **REUSE** |
| **ggViz** (arXiv:2107.06495, CHI Play 2022) | paper+code, sketch state query over >10 M states | CS:GO | 2021 | arXiv | **INTEGRATE (closest prior art to "find rounds like mine")** |
| Durst 2024 (arXiv:2408.13934) | transformer movement + round similarity + NN label propagation | CS:GO | 2024 | CGF/arXiv | **INTEGRATE (similarity)** |
| Kawasaki 2024 (Set Transformer) / Hasegawa 2024 / González 2024 (momentum, 170k rounds) | win-prob papers | CS:GO | 2024 | IEEE/jstage/Elsevier | **INTEGRATE** |
| **Luo 2020 IRL-DK** (IJCAI) | counterfactual decision method | NHL | 2020 | IJCAI | **INTEGRATE (method)** — vanilla IRL unstable |
| **Go DQI** (`1 − ΔW`) | decision-quality metric | Go | 2023 | PMC | **REUSE (metric idea)** |
| "Crafting Champions" (CHI 2025, DOI 10.1145/3706598.3713141) | how human coaches coach | esports | 2025 | ACM | **REUSE (design)** |
| 3D-CNN + LLM coaching | ~71% acc | generic | 2026 | IEEE | **INTEGRATE (architecture ref)** |
| BotScreen (USENIX'23) / VADNet / arXiv:2409.14830 | cheat detection | FPS | 2023–24 | USENIX etc. | **IGNORE for coaching** (orthogonal) |

---

## 2. Per-tool entries (layer 1 — parsing, data access, assets)

Each entry: what it does · CS2 support (how verified) · status Oct 2026 · architecture · data exposed ·
programmatic integration · open/closed + licence · Linux · reusability · AI real vs marketing ·
unsolved. Verdicts are collected again in §6.

### 2.1 awpy 3.x — `pnxenopoulos/awpy` — **REUSE (primary)**

- **What:** Python library (Rust core + PyO3 + Polars) to parse, analyse and visualise CS2 demos.
  Also a CLI (`awpy info|kills|stats|rounds|events|get|versions|maps|clear|verify`).
- **CS2:** ✅ CS2-only (FAQ: does not read CS:GO). Verified via PyPI JSON + repo tree + docs.
- **Status:** PyPI **3.0.0 released 2026-10-14**; `main` has **3.1.0** (multipart demos) with commits
  **2026-10-15**; 618★, 5 open issues. Repo history is effectively a collapsed big-bang v3 rewrite
  (commits jump Mar-2025 → Oct-2026), **so track record on v3 is ~1 day old** — a real risk factor.
- **Architecture:** crates `awpy` (io/entities/parser/name tables), `awpy-proto` (prost protos synced
  from GameTracking-CS2), `awpy-python` (PyO3), `awpy-dev` (internals CLI). Shared `pbdems2` core
  with a Deadlock parser ("Boon").
- **Data exposed:** cached Polars datasets — `rounds`, `kills` (with trade flags `is_trade`/
  `victim_traded`, 5.25 s window), `damages`, `bomb`, `grenades`, `fires`, `smokes`, `shots`,
  `blinds`, `item_events`, `stats` (KAST/ADR/trades/clutches/utility), `round_economy`
  (`pistol`/`eco`/`force`/`full`), `players`, `chat`, `convars`; `snapshots(ticks|every|seconds|
  events|start_tick|end_tick)` with positions, eye angles, economy, loadout; `ticks(props)` for
  arbitrary networked props; `demo.events.<any event>`; `SNAPSHOT_PROPERTIES`, `GAME_EVENTS`,
  `tick_to_seconds`/`seconds_to_tick`.
- **Map API:** `VisibilityChecker(map)` (BVH over `AWMH` collision mesh, `is_visible(p1,p2)`),
  `NavMesh(map, version=…)` (`find_area`, `find_path`), `map_control` (`raycast`/`vision`/
  `reachability`, returns per-nav-area `ct|t|contested|neutral`, `net_control = ct − t`), `awpy.data`
  asset cache, `awpy.plot` (radar, frame, heatmap, nav, GIF, map_control).
- **Integration:** pip/uv (wheels, no Rust toolchain); `AWPY_DATA_DIR` for a repo-local asset cache.
- **Licence/openness:** **MIT**, open. **Linux:** ✅ manylinux x86_64 + aarch64, py3.11–3.15.
- **Reusability:** **high** — a single MIT dependency covering datasets + per-tick + geometry + nav +
  map control.
- **AI:** n/a (deterministic).
- **Unsolved:** no first-class `spotted`; LOS ignores pitch; smoke as a sphere; no in-game callout
  lookup (open issue #390, 2025-03-30); protos pinned to build 2000924 while CS2 shipped 2000932
  (2026-10-15); asset-fetch 403 and default-tickrate bugs in issue history; visibility tests are
  synthetic only.

### 2.2 pbdems2 — **INTEGRATE (via awpy)**

- **What:** the Source 2 demo-format core (Rust) that awpy and Boon share; awpy adds CS2 protobufs,
  field decoders, name tables.
- **Status:** crates.io **0.4.0 (2026-10-12)**, 8 releases in 6 weeks, commits 2026-10-13. MIT.
- **Reusability:** direct use only if going Rust; otherwise it is the reason awpy is fast.
- **Unsolved:** consumer supplies protos ⇒ format churn is on you.

### 2.3 demoparser2 — `LaihoE/demoparser` — **INTEGRATE (prop/input sidecar)**

- **What:** CS2 replay parser, Rust core, Python/Node/WASM bindings. Query-shaped API rather than
  streaming hooks: `DemoParser(path).parse_event(name, player=[...], other=[...])`, `parse_ticks([...])`.
- **CS2:** ✅ CS2-only. **Status:** PyPI/npm **0.42.0 (2026-08-08)**; repo committed 2026-10-05; 733★,
  **23 open issues** dominated by CS2-patch breakage (`EntityNotFound`, `IllegalPathOp`,
  FACEIT `UnknownDemoCmd(34)`, POV gaps). WASM package (`demoparser2` on npm) is **frozen at 0.15.0
  (2023-12-04)**.
- **Architecture:** Rust `src/parser` (first_pass prop ids, second_pass collect/`usercmd_delta`),
  thin Py/Node glue; examples in both languages.
- **Data exposed:** very large documented prop list (player, buttons, game state, weapon), **plus two
  things nothing else in Python has:**
  - `spotted` (`m_bSpotted`) and `approximate_spotted_by` (`m_bSpottedByMask`) — resolved by walking
    **mask bits 0..15** → controller ids 1..16 → SteamIDs. **Structurally approximate.**
  - **usercmd block:** `usercmd_viewangle_x/y/z`, `usercmd_buttonstate_1..3`, `usercmd_forward_move`,
    `usercmd_left_move`, `usercmd_impulse`, `usercmd_mouse_dx/dy`, `usercmd_weapon_select`,
    `usercmd_input_history`, `usercmd_subtick_moves`, `usercmd_consumed_server_angle_changes`.
- **Perf:** in-repo benchmark — 50 demos / 4.6 GB in 6.14 s (12-core, 749 MB/s); a 430 MB demo ≈ 0.65 s
  MT / 3.7 s ST.
- **Integration:** pip / npm; MIT; ✅ Linux (manylinux x86_64/aarch64, macOS, Windows).
- **AI:** n/a.
- **Unsolved:** **the delta_data trap** — since ~July 2026 nearly all user commands are delta-encoded;
  demoparser2 lost usercmd data entirely until #340 was fixed **2026-07-11** with its own delta
  decoder. `usercmd_subtick_moves` is **still missing in 0.42.0 (#345)**. Open `inferno_startburn` ↔
  `parseGrenades` id-mismatch (#317). Repeated patch breakage ⇒ pin the version and run a canary.
  **No map geometry/visibility at all.**

### 2.4 demoinfocs-golang — **INTEGRATE (conditionally)**

- **What:** the long-standing Go CS2/CS:GO demo parser (streaming callbacks + GameState + entities).
- **Status:** **v6.0.0-alpha.1 (2026-10-11)**, stable **v5.2.0 (2026-04-21)**; 1,069★, pushed
  2026-10-14; MIT. v6 requires Go 1.27 and has open PVS entity-lifecycle bugs (#714, #728).
- **Unique capabilities:** `ParserConfig.NetMessageDecryptionKey` +
  `MatchInfoDecryptionKey(b []byte)` — the key from **`match730_*.dem.info`**, needed because
  official MM chat/net-messages became encrypted (Sept-2026 CS2 update; **upstream decrypt path
  untested**); and live **CSTV+** broadcast parsing. v6 adds full `events.UserCmd` decoding with
  `UserCmdParsingFull|ButtonsOnly|Disabled`.
- **Visibility:** `Player.IsSpottedBy/HasSpotted`, `Participants.SpottersOf/SpottedBy`,
  `PlayerSpottersChanged` — with the caveat repeated **four times in source**: *"This is NOT 'Line of
  Sight' / FOV … May not behave as expected with multiple spotters."* No raycast helper.
- **Verdict:** integrate only if you need MM chat decryption or live CSTV+ (implies a Go sidecar).
  Otherwise awpy + demoparser2 cover more with less operational surface.
- **Unsolved:** no geometry/LOS; POV paths still broken; its README claim that awpy is "a wrapper for
  the Golang parser" is stale and wrong.

### 2.5 cs-demo-analyzer + CS Demo Manager (`akiver/…`) — **REUSE (ingest + reference model)**

- **cs-demo-analyzer:** Go CLI/library, **MIT**, v1.11.0 (2026-09-09), 187 commits, pinned to
  demoinfocs **v5** (v6 CI step disabled). Emits **`csdm` JSON**, CSV, XLSX, and can render video.
- **cs-demo-manager:** Electron/TS/Vue desktop app, **MIT**, **v3.20.1 (2026-07-30)**, commits
  2026-10-04, ships a **Linux AppImage**; the `csdm` CLI does `analyze … → json|xlsx|video`.
  ⚠️ **its in-app FACEIT demo download is disabled** (FACEIT restricted demos to a private API; even
  CSDM needs a backend with a maximally-rated key — "no ETA"), and it still carries dead Renown code.
- **Verdict:** reuse the analyzer for ingest/reference match+round modelling; reuse CSDM as UX
  reference and as a *cautionary* datapoint that acquisition is where products break.
- **Unsolved:** no visibility/LOS; FACEIT path dead.

### 2.6 cs2-demo-format v3 + `cs2df` (`Starfie1d1272`) — **REUSE (intermediate format)** ⭐

- **What:** an **implementation-neutral ZIP data contract for parsed CS2 demos** — Zod schemas +
  generated JSON Schema + strict parser/validators, with a reference Python exporter `cs2df`
  (demoparser2 under the hood) and a real v3 fixture.
- **Status:** `cs2df` **3.1.0 (PyPI, 2026-06-20, MIT, Python ≥3.11)**; repo `cs2-demo-format`
  **36 commits, 4★, MIT**; consumed by DAK Studio, **RivalHub** and **CS2 Insight Agent**.
- **Package contents:** `manifest.json` + `match`, `players`, `rounds`, `player-stats`,
  `player-economies`, `kills`, `damages`, `blinds`, `bombs`, `grenades`, `clutches`; optional `shots`,
  **`replay.json`** (unified 8 Hz state stream: positions, view angles, HP, armor, money, equipment
  value, active weapon, place name, flash, flags) and **`duels.json`** (full-tick combat windows around
  kill/damage anchors for reaction-time and duel analysis, research profile).
- **Design decisions worth copying:** `playerIndex` is the canonical reference (`steamId64` only in
  `players.json`); team/side **derived, not repeated**; columnar streams **integer-only** with delta
  encoding; v3.1.0 merges split GOTV parts and filters duplicate round events from the recording resume.
- **Verdict:** the best available "parser → warehouse" seam; MIT + published JSON Schema ⇒ validators
  in any language. **This removes a whole re-invented layer.**

### 2.7 DAK Studio / `cs2-demo-analysis-kit` — **REUSE (MIT packages only)**

- **What:** desktop workbench (macOS dmg / Windows exe) + the product-neutral pipeline behind it:
  `@cs2dak/contract|core|cohort|maps|tournament|presentation|react|cli`, plus the Python `cs2df`
  shell. Packages take a `cs2-demo-format/3.x` ZIP and produce reusable analysis/view models.
- **Status:** very active (**commits 2026-10-15**), 659 commits, active releases.
- **Key claims:** "every stat links back to the exact round and tick"; documented **stability tiers**
  (Stable/Beta/Experimental); `@cs2dak/maps` provides map calibration, world→radar transforms, attack
  routes, zone geometry, **callout mapping**; `@cs2dak/cohort` does cross-match aggregation, identity
  merging, season RR/PRISM.
- **Licence:** **MIT for all `@cs2dak/*` packages and the Python shell; `apps/dak-studio` is
  AGPL-3.0-only** (network copyleft — fatal for a hosted derivative).
- **Verdict:** take the MIT packages (`@cs2dak/maps` especially), not the app.
- **Unsolved:** no AI; LOS implementation details not in the MIT surface.

### 2.8 FACEIT Data API v4 + Downloads API — **INTEGRATE (metadata) / GATED (bytes)**

- **Data API v4:** `open.faceit.com/data/v4`, OpenAPI 2.0 (**64 paths, 173 definitions**, spec licence
  *"Property of FACEIT LTD"*). Auth: Bearer API key (App Studio) or FACEIT Connect OAuth2.
- **Exposes:** match list/history, match details, **`MatchStats`** (`rounds[] → round_stats`, and
  `teams[].players[].player_stats`) — but these are **schema-less `string→string` maps
  (`object(any)`)** with no contractual field names or units.
- **Does not expose:** positions, ticks, view angles, per-round state; no structured kill/damage/
  utility/economy events; no tick rate or demo metadata; **no `demo_url` on
  `/players/{id}/history`** (so ingest = 1 history call + N match calls); no bulk/batch endpoint;
  **no published numeric rate limit** (every endpoint documents only `429`; the "40 rps" figure belongs
  to a *different* partner product, the CDP).
- **Downloads API:** `POST /download/v2/demos/download` `{resource_url} → {payload.download_url}`.
  Requires an **exclusive Downloads-API-scoped token granted only via an application form**
  (`fce.gg/downloads-api-application`), **expected response ≤30 days**. Demo container has migrated
  **`.dem.gz` → `.dem.zst`** on Backblaze B2 (per Leetify's 2025-08-04 doc).
- **Webhooks:** a `match_demo_ready` trigger exists but needs a public HTTPS endpoint — a friction
  point for "local-first".
- **Corroboration that this is real and recent:** CS Demo Manager **removed** in-app FACEIT downloads.
- **AI:** n/a. **Verdict:** metadata = integrate; **submit the Downloads-API application first — it is
  the single biggest schedule risk in the project**; design a fallback that degrades to manual upload.
- **Unsolved:** no positions ⇒ **you must parse the demo for everything spatial**; schema-less stats maps
  require defensive parsing; no redistribution rights.

### 2.9 Valve / Steam side — **INTEGRATE (share codes + GC) / no match-history API**

- **Steam Web API:** **`GetMatchHistory` / `GetMatchHistoryBySequenceNum` for app 730 do not exist**
  (those are Dota's `IDOTA2Match_570`). `ICSGOPlayers_730` has exactly three methods:
  **`GetNextMatchSharingCode`**, `GetPlayerProfile`, `GetPlayerProfileCoin`. `IPlayerService` is
  playtime/ownership only. `ICSGOServers_730/GetMatchmakingStats` **does not exist**.
- **Steam Web API ToS (still dated July 2010, read directly):** **100,000 calls/day**; data must be
  retrieved "as requested by the end user"; and the clause that matters for us — **no technology giving
  "unfair competitive advantage when playing multiplayer versions"** ⇒ constrains *live/in-match*
  coaching, not post-match analysis.
- **Game Coordinator path (the practical one):** `CMsgGCCStrike15_v2_MatchListRequestFullGameInfo
  {matchid, outcomeid, token}` + `WatchableMatchInfo{match_id, reservation_id, tv_port}` — which
  cross-checks **exactly** with `csgo-sharecode`'s `{matchId, reservationId, tvPort}`: **the share
  code is a packed FullGameInfo request.** Limits: **only the last 8 matchmaking matches**;
  **replay links expire ~1 month**; requires a Steam login (bot account + the user's **Game
  Authentication Code**). `stats.steampowered.com` is profile infrastructure, **not** the replay CDN.
- **Libraries:** **SteamKit2** (active, 2026-10-14) is the protocol layer; `node-globaloffensive`
  (last commit 2026-03-17, item-centric); `sak0a/node-cs2` active but **self-declares AI-generated with
  partial verification**; `CSGOCoordinator` dead; `Cludch` archived 2021. **Best off-the-shelf:
  `claabs/cs-demo-downloader`** (Docker/TS, pushed **2026-08-04**) with GCPD-page-scrape *or*
  bot+auth-code modes.
- **`akiver/csgo-sharecode`:** **v7.0.1, 2026-10-05, MIT**; match codes remain `CSGO-…`, but crosshair
  codes moved to a `CS…` container with **three format changes in three weeks of Sept 2026**
  (`legacy-v3` 23/09, `legacy-v4` 24/09, `cs2-v1` 30/09) ⇒ **Valve mutates these formats on a weeks
  cadence**; pin and monitor.
- **`boilerplate` does not exist** (0 GitHub/npm hits) — the real mechanism is the user-supplied Game
  Authentication Code (`steamidkey`).
- **Encryption:** official MM demos need the **`match730_*.dem.info` key** (encrypted net-messages
  since Sept 2026). demoinfocs v6 can take it; awpy cannot.
- **Unsolved:** no official CS2 match-history API; 8-match window; 1-month link expiry; encrypted chat.

### 2.10 Third-party aggregated APIs — **IGNORE as foundations**

| API | Reality | Verdict |
|---|---|---|
| **Leetify Public API** (`api-public.cs-prod.leetify.com`, OpenAPI 3.1.0: `/v3/profile`, `/v3/profile/matches`, `/v2/matches/{gameId}`, `/v2/matches/{dataSource}/{dataSourceId}`, `/api-key/validate`) | **Aggregate only — no per-round/positions.** Guidelines **forbid storing API data**, require "Data Provided by Leetify" attribution, forbid renaming/rescaling metrics. Since **2026-01-23** the API returns data **only for registered Leetify users** ⇒ most opponents are blank. No published numeric rate limit. | **INTEGRATE (enrichment only, never persist)** |
| **Scope.gg** | **No supported public API.** | IGNORE |
| **csstats.gg / csgostats.gg** | No official API; old domain host-blocks automation (403). | IGNORE (but see CS2CD dataset below) |
| **Stratz** | **Dota-only.** | IGNORE |
| **bo3.gg** | Undocumented private API, **no demos**; has an `ai_predictions` field (unverified). | IGNORE / optional pro metadata |
| **HLTV** | Per-match manual downloads; **ToS (eff. 2025-01-27) prohibits scraping/data-mining/competitive services**. | **IGNORE — ToS violation if scraped** |
| **GRID / PandaScore / Abios** | Paid (**€400–1,000+/mo**), no `.dem` files (Abios does offer coordinates). | IGNORE for v1 |
| **`@cs2watch/api`** | Demo → rendered MP4 clips, credit-based, consumes *your* demos. | IGNORE for v1 |
| **steamwebapi.com** | Skins/market/inventory (€20–50/mo) — not match stats. | IGNORE |

### 2.11 Pro-demo sources & legal position

- **HLTV** per-match only, automation prohibited. **HuggingFace mirrors** exist
  (`blanchon/cs2_dataset_demo_test`, `Vasy7777/cs2-demo-archive`, ~113 GB) — mirroring does not grant
  you a licence. **`vast7777/cs2-demo-to-dataset`** is an honest pipeline (per-round `events.parquet` +
  per-player `state.parquet` + video) whose README advises using a **normal browser** rather than
  bypassing anti-bot controls.
- **CS2CD** (HuggingFace, doi `10.57967/hf/5654`, **CC BY 4.0**): **795 matches / ~734.9 M rows /
  52.6 GB**, tick CSVs + event JSON, VAC-based `cheater` labels, produced from **csstats.gg** with
  `demoparser2`; paper: Loo, Lužkov & Burelli, *AntiCheatPT* (**arXiv 2508.06348**, 2025) → 89.17%
  acc / 93.36% AUC. Caveat: labels noisy (VAC false negatives; only the VAC-positive subset was
  hand-checked); **processed data, not `.dem` files**.
- **PureSkill CSDS:** >60,000 MM+FACEIT matches via AWS Data Exchange (sample on Kaggle) — commercial.
- **Legal:** HLTV's ToS grants no redistribution licence; Valve's demo EULA position on bulk
  redistribution is **not explicit in any primary source located** ⇒ treat bulk mirroring as
  **legally unresolved** and keep everything local+personal. The only licence-clean bulk pro-data route
  is a **CC BY 4.0 dataset** or a vendor contract.

### 2.12 Valve map assets — the licensing rule that shapes the architecture

Radar PNGs, nav meshes, `world_physics` collision geometry and overview data **are Valve's**.
`awpy-data` states this explicitly and ships **only scripts**; `counterstrafe` omits radar PNGs for
copyright reasons. **The safe pattern is to extract from the user's own CS2 install and never
redistribute** (which is exactly what `awpy-data`'s pipeline does, and why awpy ships no game files).
Note that `cs2d` and `pableeee` embedding radar PNGs does not make that redistributable.
ValveResourceFormat additionally asks for a visible credit when you merely *run* it.

---

## 3. Per-tool entries (layer 2 — products, competitors, prior art)

### 3.1 PureSkill.gg — **COMPETE (taxonomy reference; no code)**

- **What:** the longest-running automated CS coach ("building since 2018"): reviews Premier + FACEIT
  matches after play, "finds the mistakes that actually cost rounds", shows the moment in a 2D replay.
- **CS2:** ✅ (auto-analysis of Premier + FACEIT, manual upload; 2D viewer).
- **Status:** live and active (2026-10-15). **Pricing:** Free tier (Coach, 2D viewer, manual uploads,
  auto-analysed Steam matches); **Pro $3.75/mo annual or $5/mo**; Lifetime MVP $299; "rank-up
  guarantee".
- **Architecture/data:** closed SaaS; nothing runs in-game ("never a cheat", "no installs"); Steam +
  optional FACEIT linking.
- **AI:** **no "AI" branding** — described as **30+ graded assessments** calibrated to human coaches
  (0–10 scores), detected round by round. **Real or marketing: measured detectors, undisclosed method.**
- **Coverage (the most useful public spec of a coaching product):** Economy 12, Grenades 8, Shooting 6,
  Teamwork 4, Movement 3, "Other mistakes" (growing).
- **Explicitly NOT shipped:** **Crosshair placement** and **Decision making ("rotate or hold? peek or
  reload?")** — both listed *coming soon*. Their "other mistakes" bucket is explicitly unsolved.
- **Reusability:** none (closed). **Verdict:** competitive baseline + *coverage denominator*; their
  roadmap is our product thesis.
- **Unsolved:** no published precision/recall for any detector; no decision-quality evaluation.

### 3.2 CSReplays (csreplays.com) — **BENCHMARK (pattern donor)**

- **What:** "AI demo coach for CS2": round-anchored coaching "grounded in real timestamps and util
  lineups", 2D radar replay with named lineups, trends across matches, share links.
- **CS2:** ✅ (Valve + FACEIT/ESEA by upload with pasted steamid64; FACEIT auto-detect not supported).
- **Status:** new and active (2026), $9.99/mo Pro vs free 10 analyses/month; auto-sync via Steam
  (~10 min after leaving the server).
- **Claims worth taking seriously:** *"you re-peeked the same angle three rounds after dying to it"*
  (repeat-mistake detection = our "unconscious habit" feature, already marketed); *"Util named, not
  guessed"* — smokes/mollies matched against **per-map lineup catalogs** (they hand-built a
  **107-combo execute catalogue across 7 maps**).
- **AI:** **real and partially checkable.** Published engineering: a grounded LLM over a hand-shaped
  demo digest that *"cannot reference rounds that did not happen"*, **plus a calibrated
  logistic-regression role classifier with LOGO-CV metrics — pooled f1-macro 0.667 (n=63); AWPer 0.97,
  entry 0.65, support 0.55, lurker 0.50** and a confusion matrix.
- **Verified operational facts on their site:** **Valve only keeps demos ~8 days**; demos are
  "stored encrypted… never used to train models".
- **Reusability:** none (closed, no API/repo). **Verdict:** the best *grounding + honest evaluation*
  pattern in the ecosystem — copy the discipline, not the code.
- **Unsolved:** no published method for the repeat-peek claim; no coaching-efficacy evaluation.

### 3.3 Leetify — **INTEGRATE (metrics/benchmarks) — never as a datastore**

- **What:** the de-facto CS2 stats standard: Leetify Rating (LR), Aim/Positioning/Utility/Clutch
  ratings, trends; plus a public API.
- **Status:** very active; API spec live 2026-10-15. **Pricing not publicly renderable** (Free/Pro/
  Highlights+ tiers exist).
- **AI:** **not branded as AI but genuinely model-driven** — a **round win-probability impact model**
  plus **their own raycaster** for "enemy (actually) spotted".
- **Published methodology (the most reusable artefact in the commercial layer):**
  - **LR** = average per-round change in team win probability, **zero-sum within a match**. Kill credit
    split: **killer 35%, damagers 30%, flash-assist receiver 15%, traded player 20%** (absent shares
    redistributed; the dying player takes the negative). Kill value is context-dependent (5v1 ≈ nothing,
    1v1 ≈ a lot). Recalibrated on **professional CS2 data**; **2024-11-25** switched to simplified
    equipment-value economy groups and per-kill processing with previous-kill side memory;
    **2026-02-25** cut 1v1 clutch reward ~5% and fixed a post-plant Ts bug.
  - **Aim/Positioning/Utility** are separate **0–100 z-score benchmark profiles** (≈50 = average for
    the benchmark), explicitly *not* additive into LR. Aim excludes **Accuracy (All Shots)** (it
    includes wallbangs/smoke spam) and favours **"shots fired while an enemy is actually visible"**.
  - **Utility = sqrt(Quantity × Quality)**: Quantity = `min((grenades/round ÷ 3)^(2/3), 1)×100`
    (decoys excluded); Quality = `normal_CDF(combined z-score)×100` over flash-assist %, enemies
    flashed/flash, **teammates flashed/flash**, mean blind time, mean HE damage, mean **team damage**.
  - Positioning's full inputs/weights are **not disclosed**.
- **API constraints (decisive for local-first):** aggregate-only, **no storage of API data**, mandatory
  attribution, no metric renaming/rescaling, and since **2026-01-23** only registered users' data is
  returned.
- **Verdict:** reuse the *framing* (win-probability impact + normalised profiles) and re-fit everything
  locally; integrate the API only for in-session enrichment.
- **Unsolved:** LR is outcome-impact, **not counterfactual**; no visibility input beyond "spotted"; the
  model and benchmarks are closed ⇒ not reproducible.

### 3.4 SCOPE.GG — **IGNORE (code) / UX reference**

- **What:** the largest incumbent stats+analysis SaaS (self-reported **2 M registered users**, ~10 k
  players/month): performance review with "mistakes", map-position practice tips, **auto-recorded
  highlight clips**, 2D demo viewer, player comparison, match tracker, utility-usage map,
  **CS2 lineups / grenade predictor**, **tactical board**, **prematch analytics**, FACEIT stats, aim/
  headshot stats, dashboard. Quoted stats include K/D, ADR, **HLTV Rating 2.1**, AIM and grenade stats.
- **CS2:** ✅ (Steam + FACEIT login; FACEIT limits since 2025-05).
- **Status:** live. **Licence:** closed. **Linux:** browser.
- **AI:** none claimed; **"mistakes" are undisclosed heuristics**.
- **Unsolved/opaque:** no public API, no published detector methodology, no AI; pricing claims I could
  not verify (the $4.99 Lens figure is from a 2022 post; a 2026 comparison table says "from $19/mo").

### 3.5 ReplayLab (replaylab.pro) — **IGNORE (code) / WATCH (feasibility proof)**

- **What:** web demo analysis: 2D replay (positions, kills, utility, round flow, **team voice chat**),
  **"why you died"** (isolation, **repeat peeks**, untradeable positions, spacing), **duel analysis —
  who saw whom first, crosshair proximity, aim angle, prefire timing**, **3D player-eye view that
  "reconstructs what the player could see at a specific moment"**, coach mode (drawing + shared review
  rooms), opponent scouting, **progress tracking of recurring mistakes**, FACEIT archives
  (`.dem.gz`/`.zst`/`.zip`).
- **Status:** live; RU UI, English "planned"; Free 3 uploads/day + 1 trial AI review; **Pro $8.99/mo or
  $99/yr** with **10 AI reviews/month**.
- **AI:** metered "AI reviews" with **no disclosed method** — weakest claim in the set.
- **Why it matters:** (a) it **productises visibility reconstruction and "who saw whom first"** ⇒ our
  fog-of-war is an engineering task, not a research risk; (b) metering AI reviews separately is
  evidence that **per-match LLM inference is the limiting cost** of a coaching product; (c) the site
  itself concedes its analysis is *"analytical judgments… not proof that a specific play was
  objectively incorrect"* — exactly the epistemics §7 must solve.

### 3.6 Skybox.gg / Skybox EDGE — **IGNORE (pricing-ceiling reference)**

- **What:** pro/B2B CS2 analytics, now branded **Skybox EDGE**, open access, with player stats,
  leaderboards, match reports, a **2D replayer** and **POV demo upload**; Broadcast product.
- **Status (2026-10-15):** **alive** — the widespread claim that Skybox "died" is false. Free tier
  (public demos may be **one-month delayed**), Pro (instant public demos), team tiers; a €350/mo tier is
  cited; conflicting low-price claims exist.
- **Licence/interface:** closed; **no API**. **AI:** "AI" appears only in Broadcast; adoption figures
  are marketing. **Verdict:** ignore; keep the pricing datapoint.

### 3.7 Refrag.gg / CS2.CAM / MapSense / Breakdown.gg / Rivalize / GrindLike / GetReplay / cs2replays.com / csstats.gg / Suspect.gg

- **Refrag.gg:** training + analysis, **very active**, closed, "virtual coach" with no published models;
  ~$5.40–$11.50–$60 annual tiers. Compete, don't integrate.
- **CS2.CAM:** pro platform, active (5 modules in 90 days), closed; **precomputed the entire HLTV demo
  library** — the "pre-computed pro corpus" idea is worth copying.
- **MapSense:** free indie team viewer with 3D from demo; verified live app.
- **Breakdown.gg:** LLM corpus analyst with tiered pricing (£0/£5/£15/£150); grounding **unverified**.
- **Rivalize:** AI anti-strat, claims round citations, £$5/$20 tiers; crowded.
- **GrindLike** (ex-**True Grind**, domain migrated to `grindlike.pro`): team review workflow; benchmark.
- **GetReplay / cs2replays.com:** web viewers; closed; low information value.
- **csstats.gg** (ex-csgostats.gg, migrated 2023-09-26): MM-only stats; closed. ⚠️ an unverifiable
  search claim that it is owned by ESL FACEIT Group was **not propagated**.
- **Suspect.gg:** anti-cheat triage from demo clips; **shipped view cones "through smoke and walls"**
  (changelog 2026-08-28) at 8 Hz sampling — proves market value for cones, proves nobody has occlusion.
  Its **evidence-clip pattern** is worth copying.

### 3.8 Game Demon (Altros Studios) — **INTEGRATE (architecture idea)**

- **What:** the most ambitious **live in-match** AI coach: GSI + screen-reading, aim-training mode,
  post-match film review, local demo/feed processing. Windows, early access (v1.9.78), from $14.99.
- **AI:** **real guardrail stack** — GSI+screen-reading → **validator chain** → **post-match truth-check
  with a visible "calls I got wrong" report card** (plus coach memory). This is the only vendor in the
  set that *publishes its own error surface*.
- **Verdict:** ignore the product, **copy the truth-check/receipt pattern** — it is the most
  credible answer found to "how do you stop an LLM from lying about a round".
- **Constraint reminder:** live assistance collides with the **Steam Web API ToS** clause about
  "unfair competitive advantage when playing multiplayer versions" (post-match is unaffected).

### 3.9 DEMO-SLAP (demo-slap.net) — **INTEGRATE (optional clip renderer)**

- **What:** hosted CS2 demo analysis + **4K clip and fragmovie rendering**, exposed as a **remote MCP
  connector (OAuth with Steam sign-in)** for Claude/ChatGPT/Cursor/OpenCode **and** a public REST API.
- **Status:** live; OpenAPI **2.5.0** with disciplined additive/breaking changelog notes; base
  `https://api.demo-slap.net`; auth header `x-api-key`; access/support via Discord.
- **Endpoints:** `POST /public-api/analyze/url` → analyze `jobId`; `GET /analyze/{jobId}/status|data`;
  `GET /public-api/matches`; `POST /render/{jobId}` (highlight ids); **`POST /render-custom/{jobId}`**
  by `(tick, duration, povSteamId)`; `POST /render-fragmovie/{jobId}`; `GET /render/{jobId}/status|data`;
  credit calculators.
- **Data exposed:** match (map, time, teams, players with `steamId`/`isMe`, `source` enum incl.
  `faceit`, `match-token`, `upload`, `url`), highlights (`killCount`, `roundNumber`, `tags` e.g.
  `["3k","clutch"]`, `startTick`, `endTick`), per kill: `weapon`, `victim`, **`ttd` (time to first
  damage, ms)**, **`ttk` (time to kill, ms)**, `tick`, `killerSteamId`, `isHeadshot`, `noScope`,
  `throughSmoke`, `isWallBang`; top-level `tickRate` + `participants[]`.
- **Explicitly NOT exposed:** positions, tick-level state, aggregate stats, any coaching/decision
  analysis. **Pricing:** custom render ≈ **0.1 credits/s**, ×1.5 `highResolution`, ×1.5
  `hideWatermark`, 1-credit floor.
- **AI:** n/a (analysis + rendering, no coaching verdicts).
- **Verdict:** integrate as an out-of-band renderer to avoid building HLAE/CS2 render automation;
  it cannot be an analytics backbone. It is also a live competitor for "CS2 in your AI chat".

### 3.10 pr1maly — **closest prior art; code NOT reusable**

- **What:** standalone **local-first** CS2 analytics + trend tracker: upload `.dem` → advanced metrics →
  SQLite → FastAPI → vanilla-JS frontend, with **AI chat over a match using your own API key**
  (OpenAI/Anthropic/Gemini/Mistral).
- **Status:** 15 commits, last **2026-08-14**, 2★; live demo page with a real 41-match history.
- **Licence:** **Source-Available, Non-Commercial** (copyright pr1malator 2026): use/copy/modify/
  distribute allowed, but **no selling, sublicensing, or commercial exploitation** (explicitly including
  offering as a paid service or bundling with commercial products). ⇒ **read-only reference.**
- **Feature depth (useful as a completeness checklist):** HLTV 2.0 rating, ADR (capped at the victim's
  remaining health so overkill doesn't inflate), KAST%, Impact, KPR/DPR, multi-kill rounds, clutch
  detection, trade detection, 10-player scoreboard with ranks; **aim & movement:** aim score (0–100),
  **counterstrafe detection**, **peek speed** (speed carried into the duel and whether counterstrafe
  held), per-weapon movement penalties, reaction time, **crosshair placement quality**, TTK efficiency;
  **utility:** bought vs thrown vs wasted, flash efficiency, **team-flash penalty**, HE/molotov damage
  per throw, smoke zone coverage, utility rating; canvas 2D replay with grenade flight paths and
  countdowns; 5-axis behavioural chart (Aggression/Trading/Isolation/Survival/Sniper) per side;
  map-specific role detection; **round narratives with callout positions built automatically**.
- **Ops details worth copying:** optional **"Manual Fetch from Steam" via a separate Node companion**
  (`fetcher/`), auto-sync with pause while CS2 runs, `.dem.info` sidecar auto-detect (how it finds the
  local player), storage management (**~280 MB per demo → ~1.3 MB analysed**).
- **AI:** **real but shallow** — deterministic metrics, LLM used as a narrative layer; no model
  training, no decision evaluation, no output evaluation.
- **Unsolved:** no fog-of-war/visibility; no counterfactuals; no habit aggregation with evidence; no
  eval of the coaching text; non-commercial licence blocks reuse.

### 3.11 counterstrafe — **INTEGRATE (review-workflow design)**

- **What:** web app: 2D replay **with view cones**, player stats (K/D/A, ADR, HLTV 2.0 rating, openings,
  clutches), economy analysis, **tactical analysis** (play-pattern detection: A/B executes, mid splits,
  eco rushes; **role classification** Entry/AWP/Support/Lurk/IGL; mid-round decision analysis;
  territory-control heatmaps), utility analysis (smoke coverage, flash effectiveness, grenade
  heatmaps), and a **Coach Review System** (flag moments, categorised queue, threaded discussion,
  status tracking).
- **Status:** **8 commits, last 2026-01-22**, 1★; dormant. **Stack:** pnpm monorepo, React 18 + Vite +
  Tailwind + shadcn/ui + TanStack Query; **Fastify 5** backend; SQLite. Contains `AGENTS.md`/`CLAUDE.md`
  ⇒ partly LLM-authored — **verify code quality before reuse**.
- **Licence:** MIT badge in README but **no `LICENSE` file in the repo root** ⇒ compliance risk.
- **Verdict:** take the **data model** (flags + threaded replies + status) and the coach-review UX;
  treat the analysis math as unvalidated.
- **Unsolved:** view cones are drawn, **not occlusion-tested**; no AI layer; no tests for the analysis
  math; dormant.

### 3.12 CS2DemoKit (`CS2OpenDev/CS2DemoKit`) — **INTEGRATE (design) — the best architectural prior art**

- **What:** .NET (`net10.0`) suite, no UI: `Parser` (frames/net messages, **270+ typed game events**,
  entity tracking with tick seeking), `Analysis` (**rule-driven state-graph evaluator**, per-player
  stats, highlights, clip planning, **3D line-of-sight engine**), `Analysis.Rules` (rules DSL: lexer,
  parser, canonical AST, resolver, typed checker, canonical hashing; zero dependencies).
- **Status:** **116 commits, last 2026-09-25**, MIT, 1★.
- **Fog of war:** a rule can fire on **`enemy_spotted`** — *"the rising edge where one player first
  comes into view of another. Nothing on the wire says so; it is recomputed from baked map collision
  geometry."* `VisibilityEngine.Load(bake)` builds a **BVH** ("tenths of a second on the large bakes"),
  immutable and shareable per map. **Bakes ship out of band** (`CS2DEMOKIT_COLLISION_DIR`, `<map>.tris`)
  — a miss returns null and the subscribing rule then **silently never fires** (documented foot-gun).
- **Player input:** documents that `svc_UserCmds` is **~90% of net messages** (1.15 M on a 290 MB file)
  and that since **build 10896 (~July 2026) 99.8–99.9% of commands are `delta_data`**; provides
  `UserCmdReconstructor` (view angles, buttons, movement, subtick moves) and `SubTickExtractor`, with
  self-check counters (`CheckpointMismatches`, `ClientTickMismatches`, `UnknownFieldsSkipped`).
- **Two tick clocks (verbatim warning):** *"CS2 demos carry two clocks and mixing them produces results
  that look plausible and are wrong"* — frame clock (frames/rules/highlights, starts at 0) vs absolute
  server tick (`GameEvent.ServerTick`, converted via `ParsedDemo.ServerStartTick`).
- **Robustness:** decode plans (`Everything|StructureOnly|GameEventsOnly|EntityReplay`); flat memory
  over huge demos; **throws only when the input is not a CS2 demo**, otherwise degrades;
  `ParsedDemo.Health` = `Clean|Degraded|Damaged` (with the explicit warning not to banner on
  `Warnings.Count > 0`, since demos newer than the parser legitimately report `Degraded`); enforced
  allocation limits (string table 16 MiB/4096 entries, instance baseline 16 MiB).
- **Verdict:** **integrate the design and the ontology** (rules DSL, `enemy_spotted`, decode plans,
  health grading, tick-clock discipline), not the code (we are Python/local-first).
- **Unsolved:** geometry bakes must be produced and hosted; .NET 10; no evaluation of rule quality.

### 3.13 DemoQueryCS2 — **COPY THE ALGORITHM** ⭐

- **What:** draw hypothetical CT/T positions on a radar → find every matching moment in **your own**
  indexed demos, with a tolerance in game units and filters (bomb state, buy type, alive counts) →
  ranked, replayable moments. A CS2 recreation of the **ggViz paper** (arXiv:2107.06495).
- **Status:** v1.1.0, last commit **2026-09-06**; Windows installer (unsigned); hosted demo with
  **680+ pro matches from the 2026 season**. License: `LICENSE.txt`, "free for players, analysts and
  teams" — **not OSI open source**; read before reuse.
- **Method (the reusable part):**
  1. **Nav clustering at build time:** each map's nav mesh (**~2,000–4,000 areas**) is clustered into
     **~100–180 nodes** by deterministic agglomerative graph merging; a **geodesic distance matrix**
     between all nodes is precomputed, plus a raster grid for O(1) point→node lookup. Built with
     **`awpy get maps` + `awpy get navs`** (shipped app is fully offline).
  2. **Ingestion:** `demoparser2` extracts **one state per second per live round** (positions, view
     angles, health, armor, money, inventory, flash state, sides, bomb state), per-round buy
     classification from carried equipment value incl. saved weapons (≤$5,000 eco, ≤$16,250 semi, else
     full), plants, kills/assists, grenade detonations with travel paths, win method. Stored in SQLite
     as **compact tokens** (sorted per-side node ids) + **18-byte-per-player position blobs**
     (int16-quantised coords, "finer than a radar pixel"); node labels ("Mid", "BombsiteA") are
     **learned from the demos' own `last_place_name` data**.
  3. **Search:** stage 1 vectorised **geodesic Chamfer** scan (walls respected — two points close
     through a wall are *far*); stage 2 **exact optimal-assignment re-rank**, `cost = max(node geodesic,
     Euclidean)`; consecutive matching seconds merge into "moments" ranked by mean per-player offset.
  4. **"Team cores":** name 3–5 players by Steam ID and apply the label to existing indexed rounds
     **without reparsing**.
- **Verdict:** the only shipped cross-match similarity search grounded in nav geodesics; **copy the
  storage format and the two-stage search**, and reuse `last_place_name` for callout labelling.
- **Unsolved:** similarity is positional only — no utility/vision/decision semantics; no fog of war; no
  AI; no evaluation of matched moments.

### 3.14 Twoos123/cs2-meta-engine — **IDEAS ONLY (no licence)**

- **What:** self-hostable demo-analysis platform: mines "every grenade throw" from pro/FACEIT/own demos,
  **clusters identical lineups and ranks them by impact**, with **stand/run/jump technique and
  left/right-click detection**, executes, and **"your throw vs the pro lineup"** feedback —
  verbatim example: **"12u left, 3° too high"**. Plus: 2D replay with key moments and share links
  (`?round=14&t=38`), **anti-strat reports** (site hits, utility, AWP spots, CT setups, T defaults at
  0:20) with PDF export, Rating 2.0/ADR/KAST/clutches/trade %, **practice lists exported as a CS2 `.cfg`
  cycling with `]`/`[`**, live GSI radar **including Nuke/Vertigo upper & lower levels**, imports
  (own MM demos auto-picked, **FACEIT via the official API**, HLTV via a browser extension, archives
  `.rar/.zip/.dem.gz/.bz2/.zst`), local or Kubernetes+Postgres deployment.
- **Status:** last commit **2026-10-03**, no root `LICENSE` found ⇒ **all-rights-reserved by default**.
- **Why it matters:** the **numerical lineup delta** ("12u left, 3° too high") is the clearest example
  in the ecosystem of *measurable, evidence-grounded micro-feedback* rather than "improve your utility
  usage"; the `.cfg` practice-list export is a concrete "coaching → drill" bridge.
- **Unsolved:** "impact ranking" undefined and unevaluated; no fog of war; no counterfactuals; no licence.

### 3.15 Other discovered AI-coach repos (low value — recorded for completeness)

| Repo | What | Status/licence | Verdict |
|---|---|---|---|
| `OGL86/cs2AI` | Flask + demoparser2 + **Groq llama-3.3-70b**; 5 fixed sections (economy, positioning/duels, trades/teamplay, aim/mechanics, top-3 improvements); skill-score bars; markdown export | 7 commits, **2026-02-20**, **no licence** | IGNORE (code); evidence of the "facts → LLM" shape |
| `comercialtoddy/CS2-Coach-AI` | **live** coach: CS2 GSI + WebSocket + React HUD + **Piper TTS** voice feedback | hobby | IGNORE (live, not post-match) |
| `RJWilll/CS2-AI-Coach` | video + game data → Gemini; finds weaknesses | hobby, experimental | WATCH (video/CV coaching exists, unvalidated) |
| `denmonz/CS2-RAG` | fully local RAG with **Ollama**; **fetches demos from Leetify** (`fetcher/fetch_demos.py`) | last commit **2026-04-13**, no licence | Out of scope (local LLM); **evidence that a Leetify demo-fetch path works** |
| `DrEAmSs59/CS2-insight-agent` | Chinese all-in-one suite: demo analysis + skin swap + OBS record + LiteCut + LLM commentary; "0 injection / 0 hook / 0 reverse-engineering" | **936★**, last commit **2026-09-29**, **PolyForm Noncommercial** | Non-commercial ⇒ reference only; Windows-only |
| `VDAPI/cs2-analyst` | SaaS skeleton (Node/Prisma/Postgres/Redis): stats, heatmaps, 2D replay, economy, grenades, **FACEIT match sync + dedicated `worker:faceit` demo-download worker**; *planned* mistake reports/AI coach | last commit **2026-10-13**, no licence | Evidence: FACEIT worker is the standard acquisition pattern; "mistake reports" **not demonstrated anywhere** |
| `akiver/cs-demo-analyzer` (also §2.5) | MIT Go analyzer used by several of the above | v1.11.0 2026-09-09 | REUSE |

---

## 4. Per-tool entries (layer 3 — map geometry, visibility, radar, viewers, datasets)

### 4.1 awpy-data — **REUSE (assets; ship the extractor, not the assets)** ⭐

- **What:** the build pipeline for the CS2 **map assets awpy consumes** — radar images, **collision
  meshes for line-of-sight**, **nav meshes**, and the `map_data` coordinate table — published as GitHub
  Releases **pinned to the CS2 `ClientVersion`**.
- **Artifacts per release:** `images.zip` (`radars/<map>.png` + `<map>_lower.png` for Nuke/Vertigo/
  Train), `navs.zip` (`<map>.nav`, raw bytes), `geometry.zip` (`<map>.mesh`, decimated collision
  geometry in awpy's **`AWMH`** format), `map_data.json` (`pos_x`, `pos_y`, `scale`, `rotate`, `zoom`),
  `manifest.json` (release key, `client_version`, `patch_version`, `source_revision`, `version_date`,
  `buildid`, per-zip sha256).
- **Pipeline (5 stages):** fetch (anonymous steamcmd, or a local install) → extract
  (**Source2Viewer-CLI** pulls radar/nav/overview/**`world_physics`** glTF out of the VPKs) →
  `map_data` (parse overviews) → geometry (glTF → occluder-filtered, welded, **decimated** `.mesh`) →
  package → release. Pure standard-library Python 3.11+, no third-party packages.
- **Status:** 5 commits, last **2026-07-10**, **daily CI gated on the Steam buildid** and only cuts a
  release when the build changed; peer-verified releases `2000908 → 2000930` (latest **2026-10-09**).
- **Licence:** **MIT for the scripts**; the assets themselves are Valve's (see §2.12) — the README has
  an explicit licensing section, and CI extracts from a real CS2 install rather than redistributing.
- **Mesh quality evidence:** Inferno **2.5 M → 0.55 M triangles** at an 8-unit grid with **<0.1% LOS
  answer change over 200,000 rays**.
- **Verdict:** reuse the pipeline/releases for per-build map assets; **never redistribute the assets**.

### 4.2 awpy visibility & map-control stack — **REUSE** (fog of war: Demonstrated)

- **`VisibilityChecker`** — BVH (`LEAF_SIZE=4`, endpoint epsilon) over the `AWMH` collision mesh;
  `is_visible(a, b)` "well under a microsecond"; **static geometry only** (documented: no smokes,
  moving doors, or penetration). Construction-once/share-reuse semantics.
- **`map_control(demo, method=…)`** — three models with documented semantics:
  - `raycast`: is a nav area visible from a player **in any direction** (yaw ignored),
  - `vision`: same collision test restricted to the player's **horizontal FOV (default 90°)** —
    **pitch is ignored**,
  - `reachability`: assigns each area to whichever team has the shorter **nav-graph** route
    (`contest_margin` default 200 u).
  Results label each nav area `ct|t|contested|neutral` with size-weighted fractions summing to 1 and
  `net_control = ct − t`. `MapControlParams`: `eye_height 64`, `crouch_eye_height 46`,
  `target_height 46`, `max_distance`, `fov 90`, **`smoke_radius 144`, `smoke_height 60`**,
  `contest_margin`, `fire_radius 150`. **Smokes block** raycast/vision; fires block reachability.
- **Documented caveats:** "Player positions are not eye positions" (the checker does **not** apply eye
  height for you); flash-blinded players can be excluded; the lower-level
  `compute_map_control(nav, players, …)` takes `(x, y, z, side, crouched, blind, yaw)` tuples.
- **Verdict:** reuse as the fog-of-war engine (target: nav-area granularity, offline precompute);
  treat *fidelity* as unvalidated (§7.1).

### 4.3 CS2FOW — the strongest demonstration, now closed

- **What:** a server-side **anti-wallhack**: BVH8 bake from `world_physics`, **smoke voxel volumes**,
  **19 hitbox capsules as volumes with multi-point observers**, a `CheckTransmit` hook, and fail-open
  behaviour.
- **Status:** **ARCHIVED 2026-10-06 and moved closed source.** MIT at archive time.
- **Verdict:** no longer a dependency; **mine the technique** (hitbox volumes + multi-point observers +
  visibility hold + fail-open) — it is evidence that production-grade CS2 visibility is achievable in
  real time, not just offline.

### 4.4 PVS / `world_visibility.vvis` — **WATCH**

- CS2 **ships `world_visibility.vvis`**; ValveResourceFormat exposes `[Extension("vvis")]` with
  `IWorldVisibility` / `BspVoxelVisibility.Cluster` (`GetClusterForPosition`, `GetVisClustersForBox`,
  `GetVisibilityRowForPoint`). **Demonstrated as a parseable format.**
- The only attempt to use it for **player LOS** (`njyeung/CS2FOW-pvs`) is an **unbenchmarked fork**
  that asserts "PVS is no longer used in CS2" and has 267 commits / 3★ / no benchmark.
- Source-1 BSP/visleaves (`bsp_tool.py`) is **Infeasible for CS2** (CS:GO only, GPL-3.0).
- **Verdict:** possible **pruner** for a geometric LOS job (research-supported); not a LOS source.

### 4.5 Radar transform — the KV1 contract — **REUSE**

- **Source:** `resource/overviews/<map>.txt` (verified against raw `de_mirage.txt`, `de_nuke.txt`).
- **Transform:** `pixel_x = (world_x − pos_x) / scale`, `pixel_y = (pos_y − world_y) / scale`; spawn and
  bomb values in the same file are already **normalised 0..1**; `rotate` and `zoom` are **optional**
  (Nuke/Inferno/Train ship **without** `rotate`); `verticalsections` provides `AltitudeMin/Max` bands
  used to select `_lower.png` on multi-level maps.
- **Consumers (pick one, don't re-parse):** `awpy-data` → `map_data.json`; CS2OpenDev-SchemaTracker →
  `map_overviews.json` (per-build, MIT); CS2OpenDev-Docs → a per-build 22-map table (build 25218825,
  2026-09-09). Radar metadata is parsed **at least four times** across the ecosystem.

### 4.6 VPK / asset tooling — **INTEGRATE**

- **ValveResourceFormat / Source2Viewer** — the only CS2-capable Source 2 asset engine (MIT; **release
  20.0, 2026-08-17**; ~7,097 commits; commits 2026-10-14; Linux self-contained CLI). Handles VPK,
  `vmap` decompile + glTF map export, nav→GLB, `vvis`, models, textures. **CLI flags verified but
  documented as explicitly unstable.** **Cannot read `.dem`.** Attribution request.
- **`source-vpk`** (Rust, 0.6.0, **2026-10-12**, MIT) and **`vpk-tools`** (Node/Bun, read+write+verify+
  sign, tested against a real CS2 `pak01_dir.vpk`, MIT) are the modern non-.NET readers.
- **VPKEdit** — "will not parse any Source 2 filetypes" ⇒ **IGNORE for CS2**. `ValvePython/vpk` (1.4.0,
  2021) lacks multi-archive support ⇒ avoid for chunked CS2 VPKs. HLLib stale.

### 4.7 Open-source 2D replay viewers — **INTEGRATE (three MIT projects, not one fork)**

| Viewer | What it gives us | Licence | Note |
|---|---|---|---|
| **`skkwowee/cs2-demo-viewer`** | 2D radar + **vision cones**, Next 16/React 19/Canvas; ~120 lines of cone raycasting against a **wall mask derived from the radar PNG's pixels** (alpha boundaries + luminance < 45), 90 rays × 90° FOV × 1500 units; documented per-round JSON schema; `losEdges`/`sees_enemy` hooks | **MIT** | **High embeddability.** Ceiling: no height, **passes through smoke**. Best in-browser drawing layer to fork for v1 |
| **`sparkoo/csgo-2d-demo-viewer`** | 2D replay app, Go→WASM + protobuf + Preact; clean parser↔player seam; **FACEIT `match_id` share links**; `pushed_at` **2026-10-12** | **MIT** | Plumb the FACEIT workflow from here |
| **`akiver/cs-demo-analyzer`** | CLI + Go library emitting `csdm` JSON/CSV/XLSX (+ positions) | **MIT** | Reference match/round model + ingest |
| **`naeyn/counterstrafe`** | Coach-review data model + territory/utility views | MIT (no LICENSE file) | Design only (§3.11) |
| **`Gary2005/cs-net`** | 3D replay (Three.js) with committed OBJ maps + trained checkpoints; 111★ | **MIT** | The only credible OSS CS2 **3D** replay ⇒ 3D layer reference |
| **`zenojunior/cs2d`** | 2D replay, telestrator, heatmaps, **voice**; Vue 3 + Rust WASM | **NONE** | **Blocked**; UX reference only |
| **`pableeee/cs-demo-viewer`** | single self-contained HTML replay from a `.dem`; demoinfocs v5 | **NONE** | Blocked; idea = portable HTML |
| **`boltgolt/boltobserv`** | live observer radar via GSI (not demo) | **GPL-3.0** | 387★; ignore unless we go GPL |
| **`commitandpray67/radar`, `Sylixa/cs2demoview`** | 2D viewers | **NONE** | Ignore |
| **`Elkhan-Isayev/cs-viewer`** | embeddable 3D viewer | unverified | **CS 1.6 only** ⇒ ignore |
| **`suspect.gg`** (product, §3.7) | productised view cones, 8 Hz | closed | Proves demand; "**through smoke and walls**" ⇒ the occlusion lane is open |
| `Linus4/csgoverview` | desktop 2D replay, Go+SDL2, MIT | MIT | CS:GO-era; reference |

**Rendering stacks actually used (verified):** raw **Canvas** everywhere; **no** maintained `csgo-radar`
npm exists and **no** verified viewer uses Leaflet/Konva/D3; awpy uses matplotlib (Python side only).

### 4.8 Academic layer — key entries

- **ESTA** (`pnxenopoulos/esta`) — the canonical CS:GO trajectory dataset: **1,558 demos / 41,782
  rounds / 3.9 GB**, CC-BY-SA-4.0, from the same author as awpy. ⚠️ **pinned to awpy 1.3.1; awpy 2.x is
  incompatible**, so using ESTA for training implies a second (legacy) parsing path. Paper:
  arXiv:2209.09861 (2022). **INTEGRATE as training corpus.**
- **Xenopoulos 2020 WPA** (arXiv:2011.01324) — the canonical **Win Probability Added** formulation for
  CS:GO; the portable core for our impact metric. Extended with economy/MDP framing in arXiv:2109.12990.
  **REUSE.**
- **ggViz** (arXiv:2107.06495, Xenopoulos/Rulff/Silva, **CHI Play 2022**) — sketch-based retrieval of
  similar game states over a large CS:GO corpus, guided by win-probability charts and round icons,
  motivated by **interviews with pro coaches, managers and analysts**. Same author as awpy ⇒ the
  analysis and the retrieval tooling share a lineage. DemoQueryCS2 (§3.13) is its CS2 descendant.
- **Durst 2024** (arXiv:2408.13934) — transformer movement modelling + DTW-style round similarity + NN
  label propagation. **INTEGRATE (similarity).**
- **Luo et al. 2020 (IJCAI)** — MaxEnt **IRL-DK** for counterfactual decision value in hockey; the
  transferable method for "was that the right call", with the caveat that **vanilla IRL is unstable**.
- **Go DQI** (`1 − ΔW`) — the cleanest published formulation of a decision-quality index; a direct
  template for CS.
- **CS2CD** (CC BY 4.0, doi 10.57967/hf/5654) — 795 CS2 matches / 52.6 GB **tick-level** CSVs + event
  JSON + VAC cheater labels; *AntiCheatPT*, arXiv 2508.06348 (2025). **INTEGRATE as benchmark** (labels
  noisy, processed not raw).
- **CS2 Playstyle & Roles 2024** (Packer, CC-BY-4.0) — CS2 player-level features
  (TAPD/OAP/PODT/POKT/ADNT/ADAT) + NER0-derived role labels ⇒ **best feature template**.
- **btp_cs2** (Kumar, active Jul 2026) — CS2 self-organising-map role discovery from raw demos; reports
  the **null result that role consistency does NOT predict next-round outcome** ⇒ **do not market role
  consistency as a win lever**.
- **"Crafting Champions"** (CHI 2025, DOI 10.1145/3706598.3713141) — how human esports coaches actually
  coach; design input for feedback framing.
- **Cheat detection** (BotScreen USENIX'23, VADNet, arXiv:2409.14830) — orthogonal to coaching; ignore
  except as a technique pool for anomaly detection.
- **Metrics computability (settled):** ADR, KAST, trade-kill %, openings, KPR/DPR, and WPA/round-swing
  *(if we train our own win-probability model)* are **all demo-derivable**. **HLTV Rating 2.x/3.0 and
  Impact are proprietary and non-reproducible.** DQI/counterfactual EV requires an action-value model
  (open research).

---

## 5. Verification & confidence

| Claim class | Confidence | Basis |
|---|---|---|
| Versions, release dates, licences, repo activity | **High** | PyPI/npm/crates.io JSON, GitHub pages/commits, raw LICENSE files, read 2026-10-15 |
| API surfaces (FACEIT spec, Steam interfaces, Leetify spec, DEMO-SLAP OpenAPI, awpy dataset schema) | **High** | Specs parsed / source and tests read |
| awpy map/visibility *semantics* (FOV, pitch, smoke radius, params) | **High** | Docs + Rust source read |
| awpy visibility **fidelity** vs. what a player actually saw | **Unknown — no validation exists** | No labelled dataset anywhere; author's tests are synthetic |
| `m_bSpottedByMask` semantics (esp. GOTV vs per-player) | **Medium** | Signal is real in the schema; **both parsers that expose it disclaim LOS/FOV**; inference that a GOTV demo reflects the spectator client is well-supported but not stated by a primary source |
| usercmd/subtick availability | **High** for the mechanism; **Medium** for per-version completeness | demoparser2 source + issues #340/#345; CS2DemoKit's documented reconstruction; `usercmd_subtick_moves` **still missing in 0.42.0** |
| Commercial feature claims | **Mixed** | PureSkill/Scope/Refrag/ReplayLab: marketing pages only (marked). Leetify & CSReplays: published methods/metrics (grade higher) |
| Reported detection accuracy of any vendor | **Effectively one datapoint** | Only **CSReplays** publishes metrics (f1-macro 0.667, n=63, per-class table) |

**Deliberately not propagated (unverifiable/second-hand):** csstats.gg ownership by ESL FACEIT Group;
SCOPE.GG current USD pricing; `overpeek.app` and `cs2lens.com` internals (JS-only pages needing a
browser-render pass); the long tail of search-only leads (5stack.gg, overshoot.gg, cadem.com, cstrike.gg,
callup.gg, praeverto.gg, cswatch.it, fragback.gg, csstrats.dk, neptunedemos.com, noesis.gg, breach.gg) —
**flag as unverified, do not cite as fact.**

**Name-collision hazard (diligence trap):** `cs2replays.com` (free viewer) ≠ `csreplays.com` (AI coach)
≠ `csreplay.com` (viewer) ≠ `replaylab.pro` ("CS2 Replay"); plus "True Grind" → "GrindLike" rebrand and
two different "Lens" products (SCOPE Lens, CS2 Lens).

---

## 6. Reuse / integrate / ignore — consolidated

### 6.1 REUSE directly (permissive, maintained, fits local-first)

| Component | Licence | Why |
|---|---|---|
| **awpy 3.x** | MIT | datasets + per-tick + geometry + nav + map control + CLI, Linux wheels |
| **awpy-data** | MIT scripts | per-`ClientVersion` nav/radar/**collision mesh**/`map_data` releases, daily CI |
| **demoparser2** | MIT | `spotted` + `usercmd`/`subtick` — the two things awpy lacks |
| **cs2-demo-format v3 + `cs2df`** | MIT | validated parser→warehouse contract with JSON Schema + Zod |
| **`@cs2dak/*` (esp. `@cs2dak/maps`)** | MIT | calibration, world→radar, zones, **callout mapping**, cohort aggregation. **Not** `apps/dak-studio` (AGPL) |
| **cs-demo-analyzer + cs-demo-manager** | MIT | ingest, `csdm` JSON reference model, Linux AppImage |
| **`akiver/csgo-sharecode`** | MIT | share code ↔ ids; actively tracking Valve churn (v7.0.1, 2026-10-05) |
| **ValveResourceFormat / Source2Viewer** | MIT | VPK/glTF/vmap/nav/`vvis` extraction (credit requested) |
| **`source-vpk` / `vpk-tools`** | MIT | modern non-.NET VPK readers |
| **`skkwowee/cs2-demo-viewer`, `sparkoo/csgo-2d-demo-viewer`** | MIT | in-browser draw layer + FACEIT plumbing |
| **`claabs/cs-demo-downloader`** | open, Docker | Steam GC/GCPD acquisition, maintained 2026-08 |
| **GameTracking-CS2 + CS2OpenDev-SchemaTracker** | dumps/MIT | schema ground truth: `EntitySpottedState_t`, `delta_data`, `weapon_vdata.json`, per-build map tables |
| **CS2CD** | **CC BY 4.0** | the only licence-clean CS2 tick-level corpus (795 matches) |
| **Xenopoulos WPA / ggViz / Durst / Luo IRL / Go DQI** | papers/code | the method core for impact, retrieval and decision value |

### 6.2 INTEGRATE (use as engine/service, wrap it)

FACEIT Data API v4 (metadata) · **FACEIT Downloads API — apply first (≤30 d)** ·
Steam `GetNextMatchSharingCode` + GC (needs the user's Game Authentication Code) ·
demoinfocs-golang v5 **only** for MM chat decryption/CSTV+ · Leetify API (**enrichment only, never
persist**) · DEMO-SLAP MCP/REST (**clip rendering**) · CS2DemoKit (**design/ontology, not code**) ·
CS2FOW (**technique**) · CS2 Playstyle & Roles / ESTA (**features/training**) · `vvis` as a LOS pruner.

### 6.3 IGNORE (dead, closed, blocked, or wrong layer)

`csgo-demoinfo` (Valve, CS:GO, dead 2017) · `saul/demofile` (archived) · VRF **as a demo parser** ·
`VPKEdit` (Source 1 only) · `ValvePython/vpk` (chunked CS2) · `nav2json-rs` (≤v35, dormant) ·
bsp_tool/BSPSource (Source 1) · demos.tf (TF2) · npm WASM `demoparser2` (frozen 0.15.0) ·
SCOPE.GG, csstats.gg, Stratz, bo3.gg, HLTV scraping (**ToS**), GRID/PandaScore/Abios (enterprise, no
`.dem`) · all closed viewers/products as *dependencies* · AGPL/GPL components (`apps/dak-studio`,
`boltobserv`) · **no-licence repos** (`cs2d`, `pableeee/cs-demo-viewer`, `cs2-meta-engine`,
`commitandpray67/radar`, `cs2demoview`, `OGL86/cs2AI`, `VDAPI/cs2-analyst`, `denmonz/CS2-RAG`) ·
**non-commercial licences** (`pr1maly` Source-Available-NC, CS2 Insight Agent PolyForm-NC) ·
dead/pivoted: **Renown (2026-01-30)**, DemosHub (NXDOMAIN), SoStronk, cs2.gg, Fragster (news),
csgostats.gg (migrated).

### 6.4 WATCH (revisit later)

`njyeung/CS2FOW-pvs` (PVS pruning) · `cs2-nav`/`cs2_meeting_points` (published meeting-point pipeline) ·
`cs2parser`/`@deademx/cs2` (**the only decoder of smoke voxels** — needed if we want true smoke volumes)
· `ExternalAutoWallCS2` (penetration maths, paused) · `cs-net` (3D layer) · Overpeek & cs2lens.com
(needs a real browser pass) · `Starfie1d1272` ecosystem (most active in this space: commits today).

---

## 7. The real gaps (what nobody has solved)

Ordered by how much they matter to this project.

1. **No ground-truth visibility dataset, anywhere.** Every LOS implementation (awpy, CS2DemoKit, CS2FOW,
   the viewer raycasters) is unvalidated against "was this player actually visible on screen?".
   awpy's visibility tests use a synthetic wall quad; its ground-truth suite validates *scoreboards*,
   not LOS. **Product-level consequence: if our core claim is "what you could have seen", we must build
   the labelled validation set ourselves** (e.g. engineered clear/occluded pairs + kills where the
   victim demonstrably could not have seen the killer, plus hand-annotated rounds). This is the single
   highest-value greenfield artefact in the ecosystem.
2. **No counterfactual decision-quality engine for CS2.** The literature stops at heuristic WPA;
   no CS-specific IRL or counterfactual-value paper exists; the only hobby attempts are "decision
   simulation" stubs. Leetify's LR measures *outcome impact of observed events*, not "was the
   alternative better". Even ReplayLab concedes in-product that its judgements are "not proof that a
   specific play was objectively incorrect".
3. **No information-asymmetry-aware models.** Every published model (win probability, role
   classification, similarity) sees **global state**, not player-visible state. "Was this decision
   wrong *given what the player could see*" is **unmodelled in the entire literature** — and it is
   exactly what fog-of-war reconstruction enables. This is the cleanest novel contribution available.
4. **No CS2 win-probability/WPA model published.** WPA is CS:GO-only (2020) and the industry metric
   (Rating 3.0 Round Swing) is proprietary and non-reproducible. We must train and calibrate our own —
   which also gives us the foundation for decision evaluation.
5. **No reproducible CS2 decision-quality metric and no accepted error taxonomy ground truth.** There
   are no public expert error labels, no inter-rater dataset, and no public benchmark for coaching
   feedback quality in CS.
6. **No automated hallucination/consistency check on coaching text** (CSReplays bounds the LLM with a
   hand-shaped digest; Game Demon truth-checks live calls and publishes errors; **nobody in the set
   demonstrates an automated check**). A "calls I got wrong" receipt is the most credible existing
   answer and is copyable.
7. **No validated coaching-efficacy study in esports.** The one behavioural study found is n=3 for a
   single behaviour (Street Fighter V). We cannot claim Elo improvement without running our own trial.
8. **No CS2-native, licence-clean, round-level dataset.** ESTA is CS:GO + awpy 1.x; Packer is
   player-aggregate; VOR.TECH is bots; CS2CD is CC BY 4.0 but processed and cheater-labelled. We will
   generate our own from demos (and should publish calibration).
9. **No shared smoke model.** Sphere (awpy, r=144/h=60) vs. the real **voxel volume**
   (`m_VoxelFrameData`, 32³·20 u, Morton) — no open implementation exposes the voxels, and tools mix
   the two silently.
10. **Pitch is ignored** by the only LOS engine with published semantics ⇒ vertical angles
    (Nuke heaven, ramps, Overpass) are approximate.
11. **No shared occluder-mesh format.** At least five incompatible "collision geometry for LOS"
    pipelines exist (awpy `AWMH` `.mesh`, CS2DemoKit `<map>.tris`, CS2FOW `.bvh8`+JSON, radar-space
    raycasting, DAK `.tri`), all re-deriving filter/weld/decimate from the same
    `world_physics.vmdl_c` glTF.
12. **No standardised viewer/interchange schema and no shared callout/lineup corpus.** Four
    interchange formats (`csdm`, `cs2-demo-format/3.x`, per-project JSON, `.cs2dv`); CSReplays
    hand-built 107 execute combos; CS2.CAM precomputed the HLTV library; Refrag/Rivalize/MapSense each
    maintain their own. A licensed open callout+lineup corpus is a genuine buy-vs-build decision.
13. **Acquisition is the operational single point of failure** (see §2.8–2.9): FACEIT = 30-day gate;
    Valve = 8 matches / 1-month links; HLTV = ToS-prohibited; vendors = paid and demos-less. Every
    survivor in the market either insourced acquisition or made the user supply the file.
14. **Duplicate engineering to avoid:** 2D radar replay + world→radar calibration + heatmaps + kill/
    utility timeline is re-implemented by **every** product in §3. This is the clearest argument for
    building on `awpy` + `cs2-demo-format`/`@cs2dak/*` + an MIT viewer rather than starting from zero.

---

## 8. Where to look in the appendices

| Question | Appendix |
|---|---|
| Parser choice in depth, prop-level inventories, fog-of-war verdict table | `parts/01-parsers-libs.md` (§1–§11) |
| Every commercial product, dead product, pricing, "AI real vs marketing" | `parts/02-vendor-apps.md` |
| FACEIT/Steam/GC/sharecode mechanics, Leetify-API constraints, pro-demo legality, CS2CD | `parts/03-apis-data.md` |
| Nav/`.mesh`/`vvis` formats, BVH internals, smoke/molotov/penetration/audio models, radar KV1 | `parts/04-map-geometry-nav.md` |
| Viewers, embeddability, licence matrix, coach-review UX | `parts/05-viewers-2d.md` |
| Papers by theme, datasets, metric computability, negative results, gap list | `parts/06-academic-datasci.md` |
| AI-coach prior art, CS2DemoKit usercmd findings, DemoQueryCS2, DEMO-SLAP/MCP | `parts/07-ai-coach-priorart.md` |
| PureSkill/CSReplays/ReplayLab/Skybox/Leetify/Scope deep dives + published methodology | `parts/07b-commercial-competitors.md` |


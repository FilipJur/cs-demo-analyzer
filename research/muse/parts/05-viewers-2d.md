# 05 — Open-source CS2 replay / 2D viewers, visualisation stacks & coach-facing tools

**Slice owner:** EcosystemSurvey.Viewers2D · **Compiled:** 2026-10-15
**Scope:** open-source CS2 replay/2D/3D viewers usable as a local-first analysis UI; radar-asset &
coordinate-transform standards; LOS/vision-cone/fog-of-war implementations; coach-facing platforms.
**Method:** every project below was opened at its repo page and/or its raw source/docs
(`read` on `github.com/OWNER/REPO`, `raw.githubusercontent.com/...`, `api.github.com/repos/...`,
readthedocs). Star counts, `pushed_at`, license objects and commit dates come from the GitHub API or
the rendered commit list. Claims from `web_search` summaries are labelled **[search-reported]** and
were *not* used for any load-bearing statement unless independently confirmed.
**Evidence tags:** Demonstrated / Experimental / Research-supported / Plausible-untested / Infeasible.

> Headline: there is **no** open-source viewer that renders a real per-player FOV/visibility polygon
> clipped by CS2's actual 3D collision geometry. The closest things are (a) `awpy`'s
> `map_control(method="vision")` — nav-area-granularity LOS shading in Python/matplotlib (MIT,
> maintained), and (b) `CS2DemoKit`'s `enemy_spotted` visibility engine — binary LOS over a baked
> BVH (MIT, .NET). Both need out-of-band, Valve-derived collision assets. In-browser cones that exist
> today are **approximations from the radar PNG's pixels** (`skkwowee/cs2-demo-viewer`, MIT).
> That gap is our differentiator, and MIT-licensed building blocks for it exist today.

---

## A. Open-source 2D radar replay viewers

### A1. `sparkoo/csgo-2d-demo-viewer` — "CS2 2D Demo Viewer"
| Field | Finding |
|---|---|
| What it does | Full browser 2D replay of a CS2 `.dem`: rounds, playback speed, killfeed, smokes/molotovs/flashes, Nuke/Vertigo upper+lower, autozoom. Hosted at `2d.sparko.cz` + staging `dev.2d.sparko.cz`. Ships Chrome **and** Firefox FACEIT extensions that fetch the demo URL from the FACEIT API and open the player at a shareable `faceit_match_id` URL. |
| CS2 demo support | **Demonstrated.** Repo description "web based CS2 2d demo player"; topics `cs2, faceit, replay`; parser = `markus-wa/demoinfocs-golang` compiled to WASM (README). Live FACEIT extension implies real FACEIT `.dem.zst` handling. |
| Maintenance (Oct 2026) | **Active.** `pushed_at = 2026-10-12`, `updated_at = 2026-10-14`, 80★/19 forks/52 open issues, default branch `dev`; newest commit on `dev` in the rendered list is 2026-08-25 (dependabot bump), plus security bumps (Aug 22, 2026) and community PRs (Jun 2026). Created 2022-01-10. |
| Architecture | Go parser → **WebAssembly** (`make wasm`), custom **protobuf** message format (`protos/Message.proto`) as the parser↔player contract, Preact frontend (`web/src/Player`), Go server used as a demo-download proxy + static host in dev; prod = Firebase Hosting (SPA) + Cloud Run (download proxy) + GCS (WASM). Dockerfile present. CI: GH Actions (go, golangci, nodejs web + browserplugin, docker publish, firebase deploy, wasm→GCS). |
| Data exposed | Parsed demo (player positions, events) streamed as protobuf into the browser; URL params `demourl`, `faceit_match_id`. No documented public JSON schema. |
| Programmatic integration | No npm package; the player is an SPA route (`/player?demourl=…`). Reuse = fork, or lift the WASM parser + protobuf contract. |
| Open/closed + license | **MIT** (license object `mit`). |
| Linux compat | Yes — Go, Node/pnpm, Docker; CI runs on ubuntu-latest. |
| Reusability | High as a **reference/engine**, medium as a drop-in: it is the most complete *maintained, MIT, CS2, FACEIT-aware* 2D player on GitHub, but it is an app, not a library. |
| AI real vs marketing | N/A — no AI claims. |
| Unsolved problems | No vision cone/LOS. No embedding API. 52 open issues (quality unknown). Shareable FACEIT links exist; generic demo hosting still needs the proxy. |
| **Verdict** | **INTEGRATE** (primary 2D engine reference; the FACEIT `match_id` pattern is directly reusable for a FACEIT-based coach workflow). |

### A2. `akiver/cs-demo-manager`
| Field | Finding |
|---|---|
| What it does | Desktop companion for CS demos: library management, download from Valve/FACEIT/…, match + player stats pages, and a 2D replay. |
| CS2 demo support | **Demonstrated.** Topics `cs2, csgo`; 2011★/255 forks; paired with `akiver/cs-demo-analyzer` (Go) for parsing. |
| Maintenance | **Very active.** `pushed_at = 2026-10-04`, `updated_at = 2026-10-15`, 29 open issues, 177 MB repo, docs site `cs-demo-manager.com/docs` incl. an **architecture** page for developers. |
| Architecture | TypeScript (Vue 3 + Electron); parsing delegated to the `cs-demo-analyzer` Go binary; local DB. |
| Data exposed | Rich match/player model via the app; `cs-demo-analyzer` exposes it programmatically (see A3). |
| Programmatic integration | App-level only (Electron); the *analysis* layer is A3. |
| License | **MIT** (license object + README). |
| Linux compat | Yes (Electron, cross-platform releases). |
| Reusability | High for **UX/stats-page reference** and for the analyzer dependency; low for embedding the replay itself. |
| Unsolved problems | Uptime of third-party demo sources; no LOS/vision. |
| **Verdict** | **INTEGRATE** (reference for stats UI + the sanctioned parsing path; MIT). |

### A3. `akiver/cs-demo-analyzer`
| Field | Finding |
|---|---|
| What it does | CLI + Go library: analyze a demo and export **csv / json / csdm**, optionally with entity positions (`-positions`). Forced demo-source detection: `challengermode, ebot, esea, esl, esportal, faceit, fastcup, 5eplay, perfectworld, popflash, valve`. |
| CS2 demo support | **Demonstrated.** README: "A CLI to analyze and export CS2/CS:GO demos". |
| Maintenance | 124★/23 forks, 187 commits, default `main`; license **MIT**. (Exact last-push date not re-verified this pass.) |
| Architecture | Go; `cmd/cli` + `pkg/api` (`api.AnalyzeDemo`, `api.AnalyzeAndExportDemo`) + a `js/` bindings directory. |
| Data exposed | Kills (tick, killer, victim, weapon), rounds, players, economy, positions; the `csdm` export format is a de-facto interchange format (also consumed by the ecosystem). |
| License | **MIT**. |
| Linux compat | Yes (Go; ready-made binaries on releases). |
| Reusability | High as the **data layer** behind any UI; overlaps the ParsersLibs slice. |
| **Verdict** | **INTEGRATE** (but check ParsersLibs overlap before duplicating work). |

### A4. `skkwowee/cs2-demo-viewer` — CS2 radar viewer **with vision cones & LOS**
| Field | Finding |
|---|---|
| What it does | Next.js viewer over pre-exported JSON: radar canvas with player dots, **wall-clipped vision cones**, kill lines, damage lines, shot tracers, multi-level support, timeline with kill markers, dormant caster-commentary track. Data is exported by a separate `skkwowee/cs2-tools` CLI (`cs2-parse-demos`, `cs2-export-viewer`). |
| CS2 demo support | **Demonstrated** (schema has CS2 world coords, `side` CT/T, tickrate 64, kills/damages/shots/bomb). Part of the `skkwowee/chimera` research project; footer says the viewer is being repurposed to visualise world-model rollouts (predicted vs actual positions). |
| Maintenance | **Low/targeted.** 1★, 0 forks, 0 issues; newest commits in the rendered list: 2026-06-05; also 2026-06-04 and 2026-03-25 (several authored with `claude`). MIT. |
| Architecture | Next.js 16 / React 19 / Tailwind v4 / **raw HTML Canvas** (no Leaflet/D3/konva). Static JSON under `public/viewer-data/`; radar PNGs + `map-data.json` under `public/maps/`. |
| LOS/vision implementation (**verified in source**) | `src/components/MapCanvas.tsx`: builds a **wall mask from the radar PNG itself** — alpha-boundary pixels plus opaque pixels with luminance < 45 — then raycasts **90 rays over a fixed 90° FOV, 1-px steps, 1500 world-unit radius** to clip each cone. Also renders `losEdges` (pairs of players with clear cross-team LOS, drawn cyan) and accepts a `sees_enemy` per-frame flag. Constants: `CONE_FOV = π/2`, `CONE_WORLD_RADIUS = 1500`, `RAY_COUNT = 90`. |
| Data exposed | `index.json`, `meta.json` (rounds, kills, damages, shots, bomb), `round_XX.json` (`frames[].players[] = {name, side, x, y, z, yaw, hp, alive}`, optional `predicted_x/predicted_y`), `map-data.json` (`pos_x, pos_y, scale, lower_level_max_units`). Fully documented in `docs/data-format.md`. |
| License | **MIT** (README). |
| Linux compat | Yes (Node/Next.js). |
| Reusability | **Highest code-level reusability of the 2D viewers**: tiny, MIT, single-canvas, documented schema, cone code is ~120 readable lines. |
| AI real vs marketing | The "AI rollouts" are the *research* direction; the shipped viewer has no AI features. |
| Unsolved problems | Cone is **2D-pixel-based**: no height handling (Nuke ramps, windows, boxes), passes through smoke, and quality depends entirely on the radar PNG's contrast/alpha (it even documents a luminance threshold). No 3D occlusion. The LOS edges come pre-computed in the data, not from the browser. |
| **Verdict** | **INTEGRATE** (fork the canvas + schema; treat the cone as a *look-direction* indicator, not visibility — see §D). |

### A5. `zenojunior/cs2d` (cs2d.app)
| Field | Finding |
|---|---|
| What it does | "Fastest browser-based 2D CS2 demo viewer", 100% client-side: round-by-round playback, heatmaps (deaths/presence/utility, per side/player/round), grenade trajectories (+in-replay effects), utility analysis (flash effectiveness, HE/molotov damage), economy, **telestrator**, replay comments, `.cs2dv` export/import, in-game **voice** replay, bundled Major playoffs, 9 UI languages. Accepts `.dem`, `.gz`, `.zip`, `.zst`. |
| CS2 demo support | **Demonstrated** (topics `cs2, counter-strike-2, replay, heatmaps`; CS2-only, uses `source2-demo` crate). |
| Maintenance | Created **2026-06-16**, `pushed_at 2026-07-02`, 21★, 1 issue, 78 MB repo, `has_discussions`. |
| Architecture | Vue 3 + Vite + Tailwind + Reka UI; **Rust→WASM** parser in a Web Worker (built on the `source2-demo` crate, `.wasm` committed so contributors don't need Rust); pnpm + Turborepo; Dockerfile; radar PNGs + weapon SVGs committed in `apps/app/public/`. |
| Data exposed | Internal only; `.cs2dv` is a compact self-contained analysis export. |
| License | **NONE — `license: null` via the GitHub API.** Repository is public but carries no license → default "all rights reserved". |
| Linux compat | Yes (Node/pnpm/Docker). |
| Reusability | **Legally blocked** for copying any code or asset. Feature set is the best UX reference in the 2D cluster (telestrator, comments, voice, `.cs2dv`). |
| Unsolved problems | No LOS/vision cones. No license = cannot fork. |
| **Verdict** | **IGNORE for code reuse** (no license); **reuse the feature checklist** (telestrator, per-round annotations, `.cs2dv`-style export, voice) as UX requirements. Approach the author if we want the parser. |

### A6. `pableeee/cs-demo-viewer`
| Field | Finding |
|---|---|
| What it does | Go CLI (`./demoview match.dem`) that emits a **self-contained HTML** round-replay viewer (no server): round strip, 0.5–8× speeds, upper/lower toggle, stats panel, zoom/pan, hover tooltips, **freehand drawing overlay**, full map-overlay vocabulary (C4 states, smoke circles w/ durations, molotov, HE burst, shoot flash, C4 carrier badge). Supported maps: ancient, anubis, dust2, inferno, mirage, nuke, overpass, train, vertigo. |
| CS2 demo support | **Demonstrated.** README + commit `07c329e` (2026-07-24): *"Upgrade demoinfocs v4→v5 for AG2 demo support"* → `demoinfocs-golang/v5`, Go 1.24+. Accepts `.dem` and `.csdem.gz`. |
| Maintenance | **Recent but single-author.** 1★, 35 commits, default `master`; commits seen: 2026-07-24, 2026-06-03, plus later viewer commits (round strip, drawing overlay) authored with `claude`. |
| Architecture | Go 1.24 (`cmd/demoview`, `internal/demo`, `internal/maps` with embedded overview PNGs, `internal/viewer` with an embedded `template.html` + inline JS). |
| License | **NONE** — the repo About panel shows no license entry and there is no `LICENSE` file in the root listing. |
| Linux compat | Yes (Go). |
| Reusability | **Legally blocked**; the "generate one portable HTML file" pattern is a genuinely useful product idea (offline share without infra). |
| **Verdict** | **IGNORE for code; ADOPT the portable-HTML idea.** |

### A7. `naeyn/counterstrafe` — deliberately coach-facing
| Field | Finding |
|---|---|
| What it does | Full analysis web app: 2D replay (player positions, **view cones**, health bars, 0.25–4× speed, round nav, timeline scrub, kill feed w/ headshot/wallbang/multi-kill, grenade effects, death markers) + player stats (K/D, ADR, **HLTV 2.0 rating**, opening duels, clutches) + economy (buy patterns, equipment value) + tactics (A/B executes, mid splits, eco rushes; role classification Entry/AWP/Support/Lurk/IGL; mid-round decisions; territory control) + utility (smoke coverage, flash effectiveness, nade heatmaps) + **Coach Review System**: flag specific moments, categorized queue, threaded discussions on flags, status tracking. |
| CS2 demo support | **Demonstrated** (README: "analyzing Counter-Strike 2 demo files"; parser `@laihoe/demoparser2`, Rust-based CS2). |
| Maintenance | 1★, 0 forks, 0 issues; commits seen through 2026-01-21 at minimum (the newest block above the read window was not captured) → **[INFERENCE] last activity H1 2026**. Several commits co-authored with `claude`. |
| Architecture | pnpm monorepo: `apps/api` (Fastify 5 + better-sqlite3 + services/{analysis,decisions,patterns,roles,mapZones,storage}) and `apps/web` (React 18 + Vite + Tailwind + shadcn + TanStack Query), vitest suites both sides. REST surface documented in README (`/api/demos`, `/analysis`, `/patterns`, `/roles`, `/decisions`, `/review-flags`). |
| Data exposed | Documented REST endpoints + shared TS types (`packages/shared`); SQLite schema (`db/schema.ts`). |
| License | **MIT** (README badge + repo). |
| Linux compat | Yes. |
| Reusability | **Highest of the "app-shaped" projects**: MIT, React+Fastify+SQLite, explicit API contract, coach-review data model. |
| Unsolved problems | Radar images are **explicitly not included** ("due to copyright — provide your own"); view cones claimed in README but the implementation was not read (vs A4, which I verified in source) — *edit*: mark the cone claim **[Plausible-untested]** for this repo. |
| **Verdict** | **INTEGRATE** (best MIT starting point for a coach-review product surface: review flags + threads + per-component API). |

### A8. `pr1malator/pr1maly` — local-first personal tracker
| Field | Finding |
|---|---|
| What it does | "Your CS2 gameplay, analyzed in depth", all local: HLTV 2.0 / ADR / KAST / K/D / Impact, multi-kills, clutches, trades, 10-player scoreboard, per-round economy/buy type/callouts/opening duels/bomb/utility, **aim & movement analysis** (aim score 0–100, counterstrafe detection, peek speed, crosshair placement, reaction time, TTK), utility analysis (bought/thrown/wasted, flash efficiency, smoke coverage), **2D replay canvas** + interactive minimap, 5-axis behavioural chart, map-specific role detection, trends over time, multi-account, friends, sync folder, Steam demo fetcher companion, retention/storage management, optional LLM coaching. |
| CS2 demo support | **Demonstrated** (demoparser2; supported maps listed incl. dust2/mirage/inferno/nuke/ancient/anubis/overpass for callouts + radar for train/vertigo/office). |
| Maintenance | 2★, 15 commits, `LICENSE` present (type not opened this pass), README is unusually detailed (1025 lines). Created ~2026-08 ([INFERENCE] from 15-commit count). |
| Architecture | Python 3.11 (demoparser2 → pandas → sqlite3 → FastAPI/uvicorn API) + **vanilla JS + Chart.js** frontend; Docker; layered (`src/parser.py`, `src/processor.py`, `src/domain/`, `src/services/`, `src/ai_service.py`). |
| Notable data point | **Storage: a demo ≈ 280 MB on disk but ≈ 1.3 MB once analysed** (README "Storage management") — directly relevant to our retention design. |
| AI real vs marketing | "AI coaching" = bring-your-own-key wrapper over OpenAI/Anthropic/Gemini/Mistral + auto-built round narratives. Real but commodity. |
| License | Has `LICENSE`; **type unverified** — check before reuse. |
| Linux compat | Yes (Python + Docker). |
| **Verdict** | **INTEGRATE (pattern) / VERIFY license before code reuse.** Closest existing analogue to our goal (single user, local, trends, 2D replay). |

### A9. Others in the 2D cluster (screened out)
| Project | Status | Why |
|---|---|---|
| `commitandpray67/radar` ("CS2 Demo Radar") | 0★, **no license**, no description; the entire repo lives on a single branch named `claude/cs2-demo-radar-gPTtL`; 173 commits; FastAPI + aiosqlite + demoparser2 + React/Zustand + canvas; unique features = cross-demo/team aggregation, multi-round overlay replay, "best-effort bounce trajectory points". | No license → cannot reuse; single-branch AI-generated dump, unvetted. **IGNORE** (but note *multi-round overlay* + *team aggregation* as ideas). |
| `Sylixa/cs2demoview` | 4★, 10 commits, JS/Vite, live GH Pages demo, last updated 2026-03-11 (topic page). README title: *"Am no longer working on this for now"*; TODO list still has grenades/HP/worker offload; known bug "incorrect team when using WASM". Credits `boltgolt/boltobserv` for map data and `LaihoE/demoparser`. No license file visible. | Abandoned + unlicensed. **IGNORE** (its known WASM team-detection bug is a useful warning). |
| `Linus4/csgoverview` | **MIT**, 195★/26 forks, Go + SDL2 desktop app, `demoinfocs-golang`, branch `dev`, 366 commits, topics `2d-demo-replay`. CS:GO-era (title says CS:GO; not CS2-verified). | Great *interaction* reference (3s/10s skip keys, round/half jumps, alternate overview toggle, **`0-9` copies a player's position + view angle to the clipboard**, hidden gInk screen-draw recommendation). Last-commit date not verified this pass. **REFERENCE, not reuse** (CS2 unverified). |

---

## B. 3D web viewers & 3D asset pipelines

### B1. `ValveResourceFormat` / **Source 2 Viewer** (asset pipeline)
| Field | Finding |
|---|---|
| What it does | Parser, renderer, decompiler and exporter for **Source 2** resource formats (`.vpk`, maps, models, materials, textures, sounds). CLI + GUI + `ValveResourceFormat` library + `ValveResourceFormat.Renderer` (OpenGL) on NuGet; site `s2v.app`. |
| CS2 support | **Demonstrated** — it is the tool `awpy-data` uses to pull CS2 map files (`Source2Viewer-CLI`, e.g. `world_physics.vmdl_c` → glTF with `--gltf_export_materials`). |
| Maintenance | **Very active.** 2.5k★/304 forks, **7,097 commits**, default `master`, MIT. |
| Architecture | C#/.NET, reverse-engineered formats, GUI/CLI/Renderer split, `dotnet` global.json pinned. |
| Data exposed | Maps/models exported to **glTF** (geometry, textures, props — not lighting/game logic/nav per [search-reported] s2v docs); asset library for programmatic extraction. |
| License | **MIT**, *except* `Tests/Files` (Valve-derived). README explicitly asks for attribution — including when you merely *ran* the binaries, and asks apps that are "substantially built on" it to credit it in their own UI. |
| Linux compat | Yes (`install_tools.sh` in awpy-data downloads a "pinned **Linux x64** build"; self-contained, no .NET runtime needed). |
| **Verdict** | **INTEGRATE** — the only viable route to real 3D map geometry (for a 3D view *or* for real occlusion geometry), plus an etiquette requirement we should honour. |

### B2. `Gary2005/cs-net` (CS-NET v4)
| Field | Finding |
|---|---|
| What it does | Transformer research stack for CS2 **plus** a genuine 3D visualiser: Flask app, upload `.dem`/`.json`/`.json.gz`, watch a smooth **3D replay (Three.js + map OBJ models)**, overlay **AI-predicted player paths vs ground truth**, and per-player probability curves (winrate / alive-at-round-end / future-kill). |
| CS2 support | **Demonstrated** (CS2 `.dem` + bundled de_mirage 24-round round-JSON fixture; 111★/6 forks, 78 commits, MIT; checkpoints on HuggingFace `gary2oos/cs-net-v4`, ~138.7M params). |
| Architecture | Python (PyTorch) `demo_parser` → round JSON → WebDataset shards; `visualizer/server.py`; **optimised OBJ map files committed** under `maps/optimized_obj_files`; losses non-trivial to build. |
| AI real vs marketing | **Real** — checkpoints, configs, an end-to-end verification script (`scripts/test_checkpoints.py`), and reproducible eval on real demo data. |
| License | **MIT**. |
| Linux compat | Yes (conda/pip; CPU/MPS/CUDA). |
| Reusability | The **3D replay + smoothing layer** and the *map-OBJ-in-repo* pattern are reusable (MIT). The ML stack is out of scope for us. |
| Unsolved problems | OBJ map assets are Valve-derived (licensing); the 3D render has no collision/occlusion or LOS; heavy Python/PyTorch dependency for a viewer-only use. |
| **Verdict** | **REFERENCE for 3D** (only credible OSS CS2 3D replay on GitHub); **IGNORE the model stack.** |

### B3. Other 3D options
| Project | Finding | Verdict |
|---|---|---|
| `Elkhan-Isayev/cs-viewer` | TypeScript/three.js/WebGL, "one ES module, no install", real BSP maps + player models + third-person camera + sound — but **Counter-Strike 1.6 / GoldSrc only** (topics `goldsrc, cs16, half-life`). 2★, updated 2026-08-02 (topic page). | **IGNORE for CS2**; the *embeddable ES-module viewer API* is the design pattern worth copying if we ever ship an embeddable viewer. |
| `saul/demofile-net` | **MIT**, 183★/32 forks, C#, CS2 **and** Deadlock. Verified features: CSTV/GOTV demos, **POV demos**, HTTP broadcasts, game events, entity updates, forward/backward seeking. Repo has `assets/screenshot-2x.png` + `examples/` (the screenshot implies a sample UI, but I did **not** verify any 3D map renderer in the C# project). | **Parser only** for our purposes; overlaps ParsersLibs. Its POV-demo support is worth flagging to whoever owns the parser slice. |
| `StarKnightt/counter-strike-in-browser` | [search-reported] Three.js + `three-mesh-bvh` FPS with **procedurally generated** (Blender) Dust2 A-site — explicitly not Valve assets. | **IGNORE** for replay; interesting only as a BVH/raycast-in-browser precedent. |

---

## C. Radar assets, coordinate transforms & drawing stacks

### C1. The de-facto coordinate standard: Valve overview KV → `map_data.json`
- Valve ships per-map overview files exposing `pos_x`, `pos_y`, `scale` (+`rotate`, `zoom`). Conversion
  (consistent across `skkwowee`, `awpy`, `commitandpray67`, community gists **[search-reported]**):
  `pixel_x = (game_x − pos_x)/scale`, `pixel_y = (pos_y − game_y)/scale` — note the Y flip.
- **`pnxenopoulos/awpy-data`** ([repo](https://github.com/pnxenopoulos/awpy-data), 2★, 5 commits, MIT
  *scripts* only) is the authoritative CS2 implementation: a 5-stage pipeline
  (`fetch → extract → map_data → geometry → package`) that reads a CS2 install (steamcmd anonymous,
  app 730) or a local install, and publishes GitHub Releases **tagged with the CS2 `ClientVersion`**
  (e.g. `2000873`) containing:
  - `images.zip` → `radars/<map>.png` (+ `_lower.png` for Nuke/Vertigo/Train);
  - `navs.zip` → `<map>.nav`;
  - `geometry.zip` → `<map>.mesh` — decimated collision geometry in Awpy's `AWMH` format;
  - `map_data.json` → per-map `pos_x, pos_y, scale, rotate, zoom, verticalsections`;
  - `manifest.json` → `client_version, server_version, patch_version, source_revision, buildid,
    version_date, generated_at`, per-zip sha256.
  CI runs **daily on ubuntu-latest** and no-ops until Steam's `buildid` changes.
- **Decimation numbers (Demonstrated, repo README):** 8-unit grid takes Inferno from **2.5M → 0.55M
  triangles (~4 MB) while changing <0.1% of line-of-sight answers over 200k random rays**; Awpy's Rust
  geometry module loads the `.mesh`, builds a BVH and answers `is_visible(a,b)` in **"well under a
  microsecond"**. Verified against a known clear/occluded Inferno sightline pair.
- **Licensing (Demonstrated, awpy-data README "Licensing"):** scripts are MIT; **radar images, nav
  meshes, collision geometry and overview data are Valve's property and are NOT shipped in the repo** —
  they are produced from a CI/own install. `counterstrafe` says the same thing ("radar images are not
  included due to copyright"); `cs2d` ships them anyway; `boltobserv` commissions its own from
  simpleradar/readtldr.gg.
- **Multi-level handling is ad hoc:** `skkwowee` uses `lower_level_max_units` (a Z threshold, sentinel
  `-1000000.0`); awpy uses `verticalsections` with a **shared** world→pixel transform for both levels and
  dims off-level players (`off_level_alpha`) or offers `*_levels` dual-panel variants.
- **No maintained JS radar package exists.** `csgo-radar`/`cs2-radar` npm packages were not found; the
  only historical one is `react-csgo-radar` **[search-reported, unmaintained]**. Every verified project
  copies the ~10-line transform. Historic overview images: `markus-wa/csgo-centrifuge` **[search-reported]**.

### C2. Rendering stack actually used (verified)
| Stack | Used by |
|---|---|
| **Raw HTML Canvas 2D** | `skkwowee` (1024² canvas + `ImageData` wall mask), `counterstrafe` (`ReplayCanvas.tsx`), `commitandpray67/radar`, `pr1maly`, `pableeee` (inline HTML/JS), `boltgolt/boltobserv` |
| **matplotlib** | `awpy.plot` (radar background `imshow` + artists; `plot.gif` for animation) |
| **Three.js / WebGL** | `Gary2005/cs-net` (3D), `Elkhan-Isayev/cs-viewer` (CS1.6) |
| **Electron desktop** | `cs-demo-manager`, `boltobserv` |
| Leaflet / Konva / D3 / deck.gl | **Not found** in any verified CS viewer. |

---

## D. Line-of-sight, vision cones & fog-of-war in existing tools (our differentiator)

Four independent, verified implementations exist. None renders a true 3D-occluded FOV polygon per frame.

### D1. `awpy.plot.map_control` — nav-area LOS shading *(closest thing to real fog-of-war)*
- **Demonstrated.** Function `plot.map_control(demo, tick=…, method="raycast"|"vision"|"reachability")` +
  time-series `awpy.map_control(...)` and per-area `map_control_at(...)`.
- **Semantics (from docs):** `raycast` = LOS in *any* direction; `vision` = the same **clipped to each
  player's horizontal FOV, 90° by default**; `reachability` = shortest travel distance over the nav graph.
  Output labels each **nav area** `ct` / `t` / `contested` / `neutral`, with size-weighted fractions and
  `net_control = ct − t`.
- **Tunables (`MapControlParams`):** `eye_height 64`, `crouch_eye_height 46`, `target_height 46`,
  `max_distance` (None = unbounded), `fov 90` (`>=360` removes the limit), `smoke_radius 144`,
  `smoke_height 60`, `fire_radius 150`, `flash_threshold 1.0`, `contest_margin 200`.
- **Smokes block LOS rays; fires block reachability paths; flashing players project no vision.**
- **Documented limitations (verbatim intent):** vision ignores **pitch**; "these models estimate control,
  not exact player perception"; dead players don't contribute; both LOS models need the **collision
  `.mesh`** (plus `.nav`) fetched on demand; `seconds=1` sampling is recommended for cost.
- **License:** awpy is **MIT** (618★, 1,465 commits, Rust parser core `pbdems2` + Polars API, CLI
  `awpy get` for map data, latest release tag `awpy-python-v3.0.0`; releases feed also shows 2.0.x).
- **Verdict: REUSE (primary).** This is the single best ready-made engine for "who could see what",
  and its parameter defaults are a gift for our FOW feature. Caveat: output granularity is nav areas
  (not an exact visibility polygon), and it is Python/matplotlib — we would port the *math* (5–10
  raycasts per area is cheap) or shell out to Python and ship data to the UI.

### D2. `CS2OpenDev/CS2DemoKit` — `enemy_spotted` from baked collision tris
- **Demonstrated (README + source layout).** MIT, **.NET `net10.0`**, 116 commits, 1★. Three packages:
  `CS2DemoKit.Parser`, `CS2DemoKit.Analysis` (rule engine + **3D line-of-sight engine**), and
  `CS2DemoKit.Analysis.Rules` (YAML rules DSL + schema).
- **Visibility:** rules subscribe to `enemy_spotted` — "the rising edge where one player first comes into
  view of another. **Nothing on the wire says so; it is recomputed from baked map collision geometry.**"
  Usage: `string? bake = CollisionAssetLocator.FindCollisionTris(demo.MapName); options.VisibilityEngine =
  bake is null ? null : VisibilityEngine.Load(bake);` — **the bakes are not in the packages**
  (read via `CS2DEMOKIT_COLLISION_DIR`, `<dir>/<map>.tris` or `<dir>/<map>/collision.tris`, then
  `assets/<map>/collision.tris` walking up from the binary); `Load` builds a **BVH** (~0.1 s on large
  bakes) that is immutable and shareable across runs. Leaving `VisibilityEngine` null makes the
  capability unavailable and the rule **silently never fires**.
- **Second high-value finding — POV/input parsing:** since ~**July 2026 (build 10896)** servers send
  almost every `svc_UserCmds` as **delta-encoded `delta_data`** patches; on current MM demos **99.8–99.9%
  of commands are deltas**, so reading `data` alone sees "a fraction of a percent of the input".
  `UserCmdReconstructor` rebuilds them (stats: `Full, Delta, MissingBaseline, DecodeFailed, OutOfOrder`
  + self-checks). `svc_UserCmds` is ~**90% of net messages in a demo** (1.15M on a 290 MB file) and is
  deliberately not surfaced in `DemoFrame.InnerMessages`. Also: `ParseWarningCodes`/`ParsedDemo.Health`
  (`Clean`/`Degraded`/`Damaged`) and enforced allocation limits for untrusted demos.
- **Verdict: INTEGRATE/REFERENCE.** Best public documentation of *how* to do CS2 LOS correctly
  (bake → BVH → raycast → rising-edge events) and a set of parsing pitfalls that will bite us. .NET is a
  stack mismatch for a local-first JS/Python tool, so reuse the design, not the binary.

### D3. `skkwowee` radar-pixel raycasting
- **Demonstrated in source** (see A4): wall mask derived from the radar PNG (alpha boundary + dark
  pixels), 90 rays × 90° FOV × 1500 units, 1-px stepping. Plus pre-computed `losEdges` (cross-team
  sightline pairs) and a `sees_enemy` per-frame flag in the schema.
- **Limits:** 2D only (no height), can't model smoke, and its accuracy is bounded by the radar image.
- **Verdict: REUSE code (MIT)** as the in-browser overlay fallback / first iteration.

### D4. `suspect.gg` productised view cones (closed source, primary changelog)
- Changelog dated **2026-08-28** (published + modified): 90° cones for every living player from the
  demo's view angle, **"drawn … through smoke and walls. It can't tell you what was on their screen"**;
  positions **sampled 8×/second and smoothed**; a map needs a calibrated radar or the replay says so;
  framing is explicitly **cheat review** ("watch whether someone's aim keeps following an enemy they had
  no way of seeing"). Also: 0.25–4× speed, 1–6× zoom, shareable moment links, kill/plant timeline marks.
- **Verdict: IGNORE as code; MANDATORY competitive/UX benchmark.** It proves the market values
  look-direction cones, and it proves nobody has shipped true occlusion — the exact gap we can own.

### D5. `Starfie1d1272/cs2-demo-analysis-kit` (DAK Studio) — second LOS implementation
- **MIT (packages) / AGPL-3.0-only (Studio app)**, 9★, **659 commits**, pnpm monorepo + Python. `@cs2dak/maps`
  = "map calibration, world→radar transforms, attack routes, zone geometry, callout mapping";
  **Duel & Mechanics Lab** computes ".tri line-of-sight TTK" (i.e. a second, independent `.tri` triangle-mesh
  LOS implementation); evidence model links **every stat to the exact match, round and tick**; the product
  seam is a `cs2-demo-format/3.x` **ZIP** ("neither side imports the other"), with `@cs2dak/react`
  components and an IndexedDB library. Explicit stance: *"Query-first, no black boxes… we never ship a
  score you can't trace."*
- **Verdict: INTEGRATE the MIT packages** (calibration, zones, `@cs2dak/react`) — **do not** take
  AGPL Studio code. Highest-value non-obvious artefact: the **v3 ZIP format seam** as a cross-language
  contract, and its per-signal stability tiers doc.

---

## E. Coach-facing / multi-player platforms & dashboards

| Project | Coach/multi-player features | License | Verdict |
|---|---|---|---|
| `naeyn/counterstrafe` (A7) | **Review flags with threaded replies + status tracking**, per-round/per-player panels, role diagnostics, decision review. | MIT | **INTEGRATE** |
| `Starfie1d1272/cs2-demo-analysis-kit` (DAK Studio) | **Coach Workbench** (marked *early*), Tournament Hub, Player profiles, evidence-linked replays, packaging for macOS/Windows. | MIT packages / AGPL Studio | **INTEGRATE (MIT parts)** |
| `Twoos123/cs2-meta-engine` | **Anti-strat reports** (site hits, utility, AWP spots, CT setups, T defaults at 0:20, shareable link + PDF), opponent scouting, **grenade-lineup mining** with "your throw vs the pro lineup (12u left, 3° too high)", practice `.cfg` export, **live radar via CS2 Game State Integration** (incl. Nuke/Vertigo upper+lower), FACEIT API import, HLTV browser extension, 2D replay with key moments + share links. 6★, 68 commits, K8s/Terraform/Ansible deploy, Postgres + worker. | **NO license** (About shows no license entry) | **IGNORE for code** (unlicensed); **harvest product ideas** (anti-strat PDF, share links, practice-cfg export, GSI live radar). |
| `DrEAmSs59/CS2-insight-agent` | Highlight/fail detection, clip queues, recording automation, tactical-coach flow. | Non-commercial license, proprietary custom-skin component [search-reported] | **IGNORE** (license). |
| `akiver/cs-demo-manager` | Match/player/team pages, shareable analysis, demo-source downloads. | MIT | **INTEGRATE (UX)** |
| `Gary2005/cs-net` visualiser | Predicted-vs-actual path overlay for review. | MIT | REFERENCE |
| `pr1malator/pr1maly` | Single-player coach substitute: trends + aim/movement/utility scores + LLM chat. | license file present (unverified type) | INTEGRATE (pattern) |
| `awrm71/E-Alytics`, `beatzip/sentinel`, `mano1233/cs2-analyzer` | Tournament dashboard on awpy/demoparser2; behavioural/anomaly research; longitudinal aim/utility/role stats. | not checked [search-reported] | **Out of slice** — likely AcademiaDs/LongitudinalAnalysis peers' territory; flag as possible duplicates. |
| **Leetify** | Closed SaaS; the UI/rating conventions are the reference, no repository. | Closed | **IGNORE as code; UX benchmark** |
| `boltgolt/boltobserv` | Not replay, but the best **live** observer radar: 6 dot states (default/flashed/active/shooting/being-damaged/bomb-carrier/dead), autozoom, advisories (plant/defuse/sole-survivor), smokes/molotovs/flashes, Nuke+Vertigo splits, browser/OBS output, transparent backgrounds, configurable keybinds; radar art commissioned from simpleradar. 387★/39 forks, 188 commits, CS2 GSI topics. | **GPL-3.0** | **IGNORE for embedding** (GPL-3 copyleft + live-only) unless we go GPL. |
| `Linus4/csgoverview` | Reviewer-quality keybinds and **copy player position+angle to clipboard** (`0-9`). | MIT | REFERENCE |

---

## F. Trajectory / summary visualisation conventions

- **`awpy.plot` (MIT, maintained) is the mature library**: `plot.frame` (`plot.Player(x,y,z,side,hp,armor,yaw,label)` + `bomb=(x,y,z)`),
  `plot.heatmap(method="hex"|"hist"|"kde", bins, cmap, alpha, bandwidth)`, `plot.map_control`, `plot.nav`
  (+ `NavMesh.find_path`), `plot.radar` (bare background, composable via `ax=`), `plot.gif(..., fps=2)`,
  and public transforms `plot.world_to_pixel` / `plot.pixel_to_world`. Multi-level: `frame_levels`,
  `heatmap_levels`, `is_lower_level`, `has_lower_level`, `off_level_alpha`. Positions are Hammer units,
  Z-up. Every function accepts `ax=` so custom artists can layer on top. Docs:
  `https://awpy.readthedocs.io/en/latest/plot.html` and `/map_control.html`, `/nav.html`.
- **Canvas-first for interactivity, matplotlib for reporting**: every interactive viewer verified uses
  Canvas 2D; nobody uses D3/Plotly/Konva for the radar. Plotly (`animation_frame`/`animation_group`) and
  **manim** (`TracedPath`, `MoveAlongPath`) appear only in *offline explainer* workflows
  **[search-reported, plotly.com/docs.manim.community]** — relevant if we want shareable round clips.
- Related small exemplars **[search-reported]**: `lakshyaag/CSGO-Visualization` (grenade trajectories +
  weapon heatmaps), `GameOperator13/cs2-dust2-duel-density` (3D kill/death density), `pnxenopoulos/esta`
  (Esports Trajectories and Actions dataset; 1,558 tournament demos, **Awpy 1.x-era, not compatible with
  Awpy 2.x/3.x** — a real trap for anyone building a dataset).

---

## G. Comparison table

| Project | Kind | CS2 (verified how) | Stack | License | Embeddability | Last activity (Oct 2026) | Verdict |
|---|---|---|---|---|---|---|---|
| `sparkoo/csgo-2d-demo-viewer` | 2D replay app + FACEIT extensions | ✔ README + demoinfocs v5 + topics | Go→WASM, protobuf, Preact, Firebase/Cloud Run | **MIT** | Medium (fork the app; clean parser/protobuf seam) | `pushed_at` 2026-10-12; commits to 2026-08-25 | **INTEGRATE** |
| `skkwowee/cs2-demo-viewer` | 2D radar + **cones/LOS** | ✔ CS2 JSON schema, 64-tick | Next 16 / React 19 / Canvas | **MIT** | **High** (single canvas component + documented schema) | commits to 2026-06-05 | **INTEGRATE** |
| `naeyn/counterstrafe` | 2D replay + analysis + **coach review** | ✔ CS2 via @laihoe/demoparser2 | React 18 + Fastify 5 + SQLite | **MIT** | **High** (monorepo, REST + shared types) | commits ≥ 2026-01-21 [INFERENCE H1-26] | **INTEGRATE** |
| `akiver/cs-demo-manager` | Desktop manager + stats + replay | ✔ topics cs2 + analyzer | TS/Electron/Vue + Go analyzer | **MIT** | Low (app) / High (UX ref) | `pushed_at` 2026-10-04 | **INTEGRATE** |
| `akiver/cs-demo-analyzer` | CLI + Go library, csv/json/csdm + positions | ✔ "CS2/CS:GO" | Go (+`js/` bindings) | **MIT** | High (library) | 187 commits | **INTEGRATE** |
| `pnxenopoulos/awpy` (+`awpy-data`) | Parser + **plot/map_control vision models** | ✔ CS2 only, Rust core | Rust + Python/Polars + matplotlib | **MIT** (assets Valve's) | High (Python lib; port or shell out) | 618★, 1,465 commits; releases to v3.0.0 | **REUSE (primary)** |
| `CS2OpenDev/CS2DemoKit` | Parser + rules + **visibility engine (BVH)** | ✔ CS2 + `net10.0` | .NET 10 | **MIT** | Medium (design, not stack) | 116 commits | **INTEGRATE (design)** |
| `Starfie1d1272/cs2-demo-analysis-kit` | Local-first studio + MIT packages + **`.tri` LOS** | ✔ cs2df/demoparser2 → v3 ZIP | TS monorepo + Python/pywebview | **MIT** pkgs / **AGPL-3.0** Studio | High (packages incl. `@cs2dak/react`) | 659 commits, active releases | **INTEGRATE (MIT only)** |
| `pr1malator/pr1maly` | Local-first personal tracker + 2D replay + LLM | ✔ demoparser2 | Python/FastAPI/SQLite + vanilla JS | file present, **type unverified** | Medium | 15 commits | **INTEGRATE (pattern)** |
| `Linus4/csgoverview` | Desktop 2D replay | ✖ CS:GO only (unverified for CS2) | Go + SDL2 | **MIT** | Low | 366 commits, date unverified | **REFERENCE** |
| `Gary2005/cs-net` | 3D replay + ML paths | ✔ CS2 `.dem` + OBJ maps | Flask + Three.js + PyTorch | **MIT** | Medium (3D layer) | 111★, 78 commits | **REFERENCE (3D)** |
| `ValveResourceFormat` | Source 2 asset pipeline (maps→glTF) | ✔ (used by awpy-data) | C#/.NET | **MIT** | High (CLI/NuGet) | 2.5k★, 7,097 commits | **INTEGRATE (assets)** |
| `zenojunior/cs2d` | 2D replay, telestrator, heatmaps, voice | ✔ CS2/Rust-WASM | Vue 3 + Rust WASM | **NONE** | **Blocked** | pushed 2026-07-02 | **IGNORE code / UX ref** |
| `pableeee/cs-demo-viewer` | Self-contained HTML replay from `.dem` | ✔ demoinfocs v5 + AG2 | Go, embedded HTML/JS | **NONE** | **Blocked** | commits to 2026-07-24 | **IGNORE code / idea: portable HTML** |
| `Twoos123/cs2-meta-engine` | Anti-strat + lineups + GSI live radar | ✔ (feature list) | Python + React + K8s | **NONE** | **Blocked** | 68 commits | **IGNORE code / idea harvest** |
| `commitandpray67/radar` | Desktop radar + team/round aggregation | ✔ demoparser2 | FastAPI + React + canvas | **NONE** | **Blocked** | 173 commits, AI branch | **IGNORE** |
| `Sylixa/cs2demoview` | 2D viewer, GH Pages | ✔ (credits demoparser) | JS/Vite | **NONE** | **Blocked** | updated 2026-03-11, abandoned | **IGNORE** |
| `boltgolt/boltobserv` | **Live** observer radar (GSI, not demo) | ✔ CS2 GSI | Electron | **GPL-3.0** | Low (copyleft) | 387★, 188 commits | **IGNORE (unless GPL)** |
| `Elkhan-Isayev/cs-viewer` | Embeddable 3D viewer | ✖ **CS1.6 only** | TS/three.js/WebGL | [unverified] | High (ES module) | updated 2026-08-02 | **IGNORE (CS2)** |
| `saul/demofile-net` | C# parser (CS2 + Deadlock) | ✔ CS2, POV, broadcasts | C#/.NET | **MIT** | High (parser) | 183★, 108 commits | Parser peer's scope |

---

## H. Best reuse candidate & license implications

**Primary recommendation — combine three MIT projects, do not fork an app:**

1. **`awpy` + `awpy-data` (MIT) for the vision/LOS engine and map assets.** It is the only maintained,
   permissively licensed, CS2-accurate LOS implementation with published semantics and tunables
   (`fov=90`, eye heights, `smoke_radius`, `flash_threshold`, `max_distance`) and a decimated collision
   mesh whose LOS error is measured at <0.1% over 200k rays. Ship it as an offline "visibility
   precompute" job (the owner's local-first constraint fits this perfectly: parse once, store visibility
   transitions, replay in the UI).
2. **`skkwowee/cs2-demo-viewer` (MIT) as the in-browser drawing layer.** ~120 lines of cone raycasting,
   a documented per-round JSON schema, `losEdges`/`sees_enemy` hooks and a 1024² canvas renderer. Fork
   it for the first UI iteration while we build a real occlusion pass.
3. **`sparkoo/csgo-2d-demo-viewer` (MIT) for the FACEIT/demo plumbing and as the quality bar.** Its
   protobuf parser↔player contract and `faceit_match_id` share-link pattern map directly onto a
   FACEIT-Elo-2000 user's workflow.
   Add **`@cs2dak/maps` (MIT)** if we want ready calibration/zone/callout data in TypeScript, and
   **`counterstrafe` (MIT)** for the coach-review data model (flags + threaded replies + status).

**License implications (must be honoured):**
- **Permissive & safe to copy:** sparkoo (MIT), skkwowee (MIT), counterstrafe (MIT), cs-demo-manager (MIT),
  cs-demo-analyzer (MIT), awpy (MIT), awpy-data *scripts* (MIT), CS2DemoKit (MIT), cs-net (MIT),
  demoinfocs-golang (MIT), csgoverview (MIT), ValveResourceFormat (MIT), DAK packages (MIT).
- **Copyleft — avoid unless we go GPL:** `boltobserv` is **GPL-3.0**; DAK **Studio** is **AGPL-3.0-only**
  (network-copyleft — fatal for a hosted offering; take only `@cs2dak/*` MIT packages).
- **No license = no reuse (default all rights reserved):** `zenojunior/cs2d`, `pableeee/cs-demo-viewer`,
  `Twoos123/cs2-meta-engine`, `commitandpray67/radar`, `Sylixa/cs2demoview`. Reading them for *ideas* is
  fine; copying code or assets is not. Note `pr1maly` has a LICENSE file whose type I did not verify.
- **Valve asset IP is the sharpest edge:** radar PNGs, nav meshes, `world_physics` collision geometry and
  overview data are Valve's (awpy-data states this explicitly; counterstrafe omits PNGs for this reason).
  The safe pattern is **extract from the user's own CS2 install** (awpy-data's pipeline, or SteamCMD
  anonymous) and never redistribute. `awpy`/`awpy-data` deliberately ship no game files; `cs2d` and
  `pableeee` embed radar PNGs, which does not make that redistributable.
- **Attribution etiquette:** ValveResourceFormat asks for a visible credit if we merely *run* its binaries
  or export assets with it — worth a README/UI line if we build 3D or collision meshes from it.
- **Data-format risk:** interchange formats are fragmented (`csdm` from akiver; `cs2-demo-format/3.x`
  ZIP from DAK); picking one early avoids a second convention.

---

## Cross-cutting notes (gaps, duplicates, and what nobody has solved)

**Confirmed gaps (the differentiator stands):**
1. **No OSS viewer renders a true per-frame FOV/visibility polygon clipped by CS2's 3D collision
   geometry.** Verified alternatives and their ceilings: `awpy` (nav-area granularity, offline,
   matplotlib, no pitch), `CS2DemoKit` (binary `enemy_spotted` events, .NET, needs an out-of-band bake),
   `skkwowee` (radar-PNG pixel raycast → no height, no smoke), `suspect.gg` (explicitly "through smoke and
   walls"). **This is the open lane.**
2. **Smoke is modelled as a sphere** (`smoke_radius 144`, `smoke_height 60` in awpy) — no open
   implementation of CS2's expanding smoke volume or its exact occlusion.
3. **Pitch is ignored** in the only LOS engine with published semantics (awpy docs: "Vision ignores
   pitch"). Anything relying on vertical angles (Nuke heaven, ramps, Overpass) is approximate.
4. **No standardised viewer data schema.** Each project invents its own JSON (skkwowee's per-round
   frames; DAK's v3 ZIP; akiver's `csdm`; cs2d's `.cs2dv`). Any ecosystem tool we ship will need an
   adapter layer.
5. **Multi-level maps are ad hoc**: Z-threshold sentinels (`lower_level_max_units = -1e6`), dimming
   off-level players, or dual panels. No project publishes a floor-segmentation standard.
6. **Tick-accurate vs 8 Hz sampling** is an unresolved tradeoff (suspect.gg documents 8 Hz + smoothing
   and that "a very fast flick looks smoother than it was").
7. **Perf/cost of LOS at scale is unquantified publicly** — awpy only advises `seconds=1` sampling;
   CS2DemoKit warns to keep the BVH rather than rebuild. No published all-ticks × all-pairs benchmark.

**Duplicated work across the cluster (do not rebuild):**
- **Radar transforms** re-implemented in at least 6 repos; `awpy-data/map_data.json` + the 2-line formula
  should be the single source.
- **Radar PNG acquisition** re-solved by boltobserv (commissioned art), cs2d & pableeee (embedded),
  awpy-data (extraction pipeline), cs-demo-manager (own pipeline). Pick awpy-data.
- **2D canvas replay loop** re-implemented in ~7 projects; skkwowee/sparkoo are the two best MIT bases.
- **Three separate LOS implementations** (awpy mesh BVH, CS2DemoKit `.tris` BVH, DAK `.tri` LOS,
  skkwowee pixel mask) — evidence this is a known-hard problem, and a chance to be the first to do it
  *interactively*.
- **"Demo → self-contained artefact" exports**: cs2d `.cs2dv`, DAK v3 ZIP, akiver `csdm`, pableeee
  single-file HTML. If we need shareability, pick one and cite it.
- **Peer overlap to flag:** parsers (demoparser2 / demoinfocs / source2-demo / demofile-net) belong to
  **ParsersLibs**; demo-URL expiry + FACEIT/HLLTV acquisition to **AcquisitionAutomation**; ESTA/datasets
  and behavioural analysis to **AcademiaDs**; multi-match shrinkage/trends to **LongitudinalAnalysis**;
  the FACEIT/Leetify API surface to **VendorApps**/**ApisData**. I deliberately did not duplicate those.

**Highest-leverage engineering bets from this slice:**
(a) offline LOS precompute from `awpy-data` meshes → store per-tick visible-area sets/enemy-spotted
events, then render in the browser (no per-frame raycasting in JS);
(b) `skkwowee`-style canvas + our visibility layer for the first user-visible win;
(c) FACEIT `match_id` share links (sparkoo pattern);
(d) coach-review data model (counterstrafe pattern) with evidence links to round+tick (DAK pattern);
(e) a single schema seam so the parser and UI stay decoupled.

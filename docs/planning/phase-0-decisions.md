# Phase 0 — technology decisions

Status: implemented with the four approved review adjustments; C0, C1, C2 and foundation hardening verified. Compatibility scope/evidence: [risks](phase-0-risks.md#implementation-verification).

## Decision and scope

Use a **Python analytical backend and TypeScript browser UI**, implemented as a modular monolith. One local FastAPI process owns discovery, the catalog and scheduling; one supervised subprocess parses at a time. Store immutable demo copies, SQLite catalog/job state and versioned Parquet datasets. No Node backend, desktop wrapper, remote service or application AI orchestration framework.

Phase 0 ends with automatic local `.dem` discovery → safe import → typed parsing → durable storage → library/status API and a thin, one-round-at-a-time 2D replay proof. The replay proves coordinates, identities and timing; it is not the eventual full review product. Include round selection, play/pause, seek and kill markers. No coaching algorithms, visibility reconstruction, advanced statistics, geometry/nav processing or hosted-model calls.

**Automatic detection is not automatic downloading.** Steam/the user obtains files; this application notices local files. No FACEIT API, Steam authentication, Game Coordinator, match discovery, URL ingestion or replay retrieval. Compressed files are explicitly reported as unsupported; only ordinary CS2 PBDEMS2 `.dem` input is required.

Review adjustments: resolve identity/field mappings before contract freeze; allow `--data-root` / `CSDA_DATA_ROOT` / config override from the beginning with pre-import free-space checks; bound `foundation-v1` to seven explicit tables; integrate at C0, C1 and C2 before crash/restart hardening. The raw recording preserves access to fields outside this profile.

## Selected stack

Versions below are the locked starting set, not floating `latest` requirements. `backend/uv.lock` and `web/package-lock.json` contain the resolved dependency sets. Maintenance/compatibility evidence is linked below; historical probes and exercised implementation checkpoints are recorded in [risks](phase-0-risks.md).

| Responsibility | Selection | License | Reason / availability |
|---|---|---|---|
| Python runtime / packaging | CPython 3.13, `uv`; inspected interpreter 3.13.15 | PSF; uv MIT OR Apache-2.0 | Already available; released parser wheels actually ran. Do not depend on Arch's moving system Python. |
| Demo parser | `awpy==3.0.0` | MIT | Released Rust-backed Python wheels; typed Polars state, rounds and event datasets. Current `main` is 3.1.0, not the release contract. [P1] |
| Columnar transformation / IO | `polars==2.0.0`, native Parquet with Zstandard | MIT | Awpy requires Polars `>=2,<3`; typed snapshot/Parquet round-trip exercised. No pandas or PyArrow dependency needed. [P1, S1] |
| Catalog / jobs | Python `sqlite3`, ordered SQL migrations | SQLite public domain | Single local owner; transactions and uniqueness constraints suffice. WAL, foreign keys, busy timeout and `synchronous=FULL`; no ORM or queue broker. [S2] |
| Local API / DTOs | `fastapi==0.143.1`, `uvicorn==0.54.0`, `pydantic==2.14.1` | MIT; BSD-3-Clause; MIT | Python stays the only backend runtime; OpenAPI generates UI types. Use base packages, not unnecessary extras. [S3] |
| Filesystem notifications | `watchfiles==1.3.0` + explicit reconciliation | MIT | Maintained Rust-backed watcher; notifications are hints, not durable jobs or proof of completed writes. [S4] |
| Steam/overview KeyValues | `srctools==2.7.0`, `Keyvalues.parse` only | MIT | One existing KV1 parser for Steam manifests and map overviews; actual Steam library resolution exercised. Release 2026-05-02, CPython 3.13 Linux wheel. [S5] |
| Browser UI | React / React DOM 19.3.1, TypeScript 5.9.3, Vite 8.3.4, plugin-react 6.1.2 | MIT; TS Apache-2.0 | Existing host Node 26.8.2/npm can resolve this set; Vite requires `^20.19 || >=22.12`. Node is build/dev tooling, not an application server. [S6] |
| API types | `openapi-typescript==7.13.0` | MIT | Runtime-free generated types from FastAPI OpenAPI 3.1. Its peer is TS `^5.x`; do **not** select latest TS 7.0.2 blindly. Plain `fetch` suffices. [S6, S7] |
| Radar extraction | Source2Viewer-CLI **20.1**, Linux x64 release; `srctools` for overview KV1 | MIT tool; Valve-derived assets separate | Released self-contained CLI works without system .NET. Actual local radar/overview extraction passed. Pin tool artifact checksum during implementation. [R1] |
| Replay proof | Small original React + Canvas component | Project's chosen source license | No evaluated viewer is a suitable maintained drop-in for this contract; no 2D renderer framework needed. |

The complete backend requirement set resolved for Python 3.13 using binary packages only. Frontend lock-only resolution passed without installing `node_modules`. These are resolution proofs, **not** a full backend launch or frontend build.

## Major alternatives resolved

| Alternative | Verified strengths | Cost / limitation | Decision |
|---|---|---|---|
| TS-first + native `@laihoe/demoparser2` 0.42.0 | Real maintained Node native bindings exist; Python is not required merely to decode a demo. MIT upstream. [P2] | Higher-level Awpy state/round handling and future Python analytics would add another backend boundary or need replacing. Browser WASM package is separately versioned and stale; do not confuse it with native Node. | Viable, not selected. Hybrid UI + Python core minimizes backend/IPC surface. |
| Python `demoparser2` 0.42.0 | Broad raw properties, user commands and spotting fields; MIT repository; Linux wheels. [P2] | Published Python package also brings pandas, NumPy, PyArrow and another independently maintained parser. Not needed for the foundation's selected datasets. | **Do not install in Phase 0.** Reconsider for a demonstrated missing field later; assign one producer per field, never merge by assumption. |
| Awpy + demoparser2 on every import | Complementary advanced capabilities | Duplicates parsing and normalization before a concrete consumer needs the extra fields. | Reject the research's blanket two-parser recommendation. |
| `cs2-demo-format` / `cs2df` 3.1.0 | MIT, actual published schemas/validator, indexed players, language-neutral v3 ZIP. cs2df uses demoparser2, **not Awpy**. [P3] | Replay is normally 8 Hz; integer-scaled coordinates/angles; full ticks only in optional duel windows; formal-round/economy semantics are opinionated. Its requirements do not inherently conflict with Awpy/Polars, but it adds a different parser and pandas stack. | **Not the internal canonical representation and not a Phase 0 dependency.** Possible later export adapter; never reconstruct authoritative state from the ZIP. |
| `demoinfocs-golang` / `akiver/cs-demo-analyzer` | MIT streaming ecosystem / mature batch exporter. [P4] | Adds Go/executable and a second data model. Live broadcast and encrypted-chat work are outside Phase 0. | Reference or future independent cross-check, not runtime dependencies. |
| SQLite only for dense ticks | One engine | Row-oriented tick storage is unnecessary when Awpy already returns columnar tables. | SQLite for catalog/queue only; Parquet for gameplay. |
| Parquet + DuckDB now | MIT embedded analytical SQL; queries Parquet directly. [S8] | No Phase 0 cross-match analytical query requires it; persistent DuckDB adds process/concurrency policy. | **Defer DuckDB**, retain compatible Parquet. Later use an in-memory/read-only query connection, not another mutable catalog. |
| Redis/Celery, multi-worker API, microservices | Distributed scheduling | No distributed requirement; harder recovery and deployment. FastAPI background callbacks are not a durable queue. [S3] | SQLite jobs + supervised subprocess, concurrency one. |
| Electron/Tauri/pywebview | Native shell | Extra packaging/runtime and no required native integration yet. | Loopback browser application. |

## Reuse versus original code

| Subsystem / candidate | Maintenance and licensing | Integration / limitations | Selection |
|---|---|---|---|
| Awpy parsing and typed datasets | 3.0.0 released 2026-10-14; active repository; major rewrite is young | Low adapter effort, but explicit schema checking is essential; raw-property query spellings can silently yield null strings | Reuse; custom normalization only. |
| `@cs2dak/contract`, core, presentation, react | Active; MIT package boundary, AGPL-3.0-only `apps/dak-studio` | Medium/high integration: v3 ZIP/derived-analysis assumptions. Published exports are source TS; maps 1.0.0 differs from main 1.1.0. Contract/core also depend on rival-rating, whose published manifest does not declare a license. [R2] | No DAK dependency. App code is not needed; this is a scope/fit decision, not a claim that AGPL forbids local use. |
| `@cs2dak/maps` 1.0.0 | MIT, source TS, no runtime deps | Medium: calibration/callouts/nav data, **no radar images**; hardcoded map data is not install-version provenance | Do not add an 18.9 MB package for a coordinate transform. Reuse extracted overview metadata instead. [R2] |
| `sparkoo/csgo-2d-demo-viewer` | MIT; active through 2026-10-12 | High: Preact app + Go/WASM parser + custom protobuf seam, not a renderer library | UX/parser-player boundary reference, not a fork. [R3] |
| `skkwowee/cs2-demo-viewer` | Small Next.js app; README claims MIT but no repository LICENSE found | Not cleared for copying; radar-pixel wall masking is also not physical visibility | Concept reference only; no source copied. Corrects inherited research's MIT reuse recommendation. [R4] |
| awpy-data / ValveResourceFormat | MIT extraction scripts/tool; Valve asset rights are separate | Reuse Source2Viewer's VPK/texture extraction, awpy-data's documented path conventions. Avoid running the full game-fetch/geometry pipeline | Extract radars locally into app data; no asset redistribution, Steam downloads or custom VPK decoder. [R1, R5] |
| Notifications, KV1, storage, API/schema generation | Maintained reusable packages above | Low integration | Reuse instead of custom watchers, VDF parsers, database engines or code generators. |
| Ingestion policy, canonical contract, generation publication, minimal UI | Application-specific behavior | Small cohesive modules, no plugin framework | Original code justified: no evaluated library supplies this exact ownership/recovery contract. |

## Compatibility rules and remaining decisions

- Canonical schema belongs to **`backend/src/cs_demo_analyzer/domain/`**, not Awpy, DAK or a viewer. Store native parser ticks, full-rate typed player snapshots and unquantized decoded coordinates. The browser consumes a bounded projection, not parser objects. [architecture](phase-0-architecture.md)
- Source all canonical angles from `Demo.snapshots`, not `Demo.ticks(["yaw", "pitch"])`; validate semantic dtypes, not just presence of columns.
- Preserve raw demos independently of source paths. Reparse into new immutable generations when parser/schema/profile changes. No compatibility shims for old internal schemas in this new project.
- `.dem.info` is optional opaque sidecar metadata, **not a completion marker** or mandatory parser input. Encrypted chat support is deferred and must never gate basic gameplay ingestion.
- Installed `ClientVersion` is 2000932; the tested demo's game-directory string embeds 2000930. The latter is an **inferred** build identifier. Neither is the Steam depot buildid. Current radar assets must be labelled current/mismatched, not falsely historical-exact.
- Unsupported/missing fields and partial observations are visible quality information. GOTV omniscient state does not establish what any player saw. No spotting/LOS/awareness claims in Phase 0.
- Future hosted-AI integration will consume evidence queries, with separately configured provider credentials and explicit outbound data policy. **No provider SDK, secrets store, prompt system or placeholder AI service in Phase 0.** Oh My Pi subagents are development tools, not application components.

No stack choice requires further broad research. The reviewed checkpoints are complete; remaining uncertainties are recording-type/historical-map compatibility, not permission to begin future analytics. See [implementation evidence and limits](phase-0-risks.md#implementation-verification).

## Primary sources

- **P1:** [Awpy 3.0.0 metadata](https://pypi.org/pypi/awpy/3.0.0/json), [released README](https://github.com/pnxenopoulos/awpy/blob/awpy-python-v3.0.0/README.md), [released datasets](https://github.com/pnxenopoulos/awpy/blob/awpy-python-v3.0.0/crates/awpy-python/docs/datasets.md), [snapshot property map](https://github.com/pnxenopoulos/awpy/blob/awpy-python-v3.0.0/crates/awpy-python/python/awpy/schema.py).
- **P2:** [demoparser source/API](https://github.com/LaihoE/demoparser), [Python 0.42.0 requirements](https://pypi.org/pypi/demoparser2/0.42.0/json), [native Node registry](https://registry.npmjs.org/@laihoe/demoparser2).
- **P3:** [v3 field contract](https://github.com/Starfie1d1272/cs2-demo-format/blob/main/docs/field-contract.md), [cs2df 3.1.0 published requirements](https://pypi.org/pypi/cs2df/3.1.0/json). Compare release metadata with main before borrowing examples.
- **P4:** [demoinfocs](https://github.com/markus-wa/demoinfocs-golang), [akiver exporter](https://github.com/akiver/cs-demo-analyzer).
- **S1:** [Polars Parquet IO](https://docs.pola.rs/user-guide/io/parquet/), [Polars 2.0.0 metadata](https://pypi.org/pypi/polars/2.0.0/json).
- **S2:** [SQLite WAL/concurrency/durability](https://sqlite.org/wal.html), [Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html).
- **S3:** [FastAPI requirements/license](https://pypi.org/pypi/fastapi/0.143.1/json), [background-task caveat](https://fastapi.tiangolo.com/tutorial/background-tasks/), [Uvicorn](https://pypi.org/pypi/uvicorn/0.54.0/json), [Pydantic](https://pypi.org/pypi/pydantic/2.14.1/json).
- **S4:** [watchfiles API](https://watchfiles.helpmanual.io/api/watch/), [watchfiles metadata](https://pypi.org/pypi/watchfiles/1.3.0/json), [inotify limitations](https://man7.org/linux/man-pages/man7/inotify.7.html).
- **S5:** [srctools metadata](https://pypi.org/pypi/srctools/2.7.0/json), [KeyValues API](https://srctools.readthedocs.io/en/latest/modules/keyvalues.html).
- **S6:** npm manifests: [React](https://registry.npmjs.org/react/19.3.1), [React DOM](https://registry.npmjs.org/react-dom/19.3.1), [TypeScript](https://registry.npmjs.org/typescript/5.9.3), [Vite](https://registry.npmjs.org/vite/8.3.4), [React plugin](https://registry.npmjs.org/@vitejs/plugin-react/6.1.2), [openapi-typescript](https://registry.npmjs.org/openapi-typescript/7.13.0).
- **S7:** [OpenAPI TypeScript](https://openapi-ts.dev/introduction).
- **S8:** [DuckDB process concurrency](https://duckdb.org/docs/current/connect/concurrency.html).
- **R1:** [Source2Viewer release 20.1](https://github.com/ValveResourceFormat/ValveResourceFormat/releases/tag/20.1), [tool/license](https://github.com/ValveResourceFormat/ValveResourceFormat), [extraction invocation](https://github.com/pnxenopoulos/awpy-data/blob/main/scripts/extract_assets.py), [asset path definitions](https://github.com/pnxenopoulos/awpy-data/blob/main/scripts/lib.py).
- **R2:** [DAK architecture/license boundary](https://github.com/Starfie1d1272/cs2-demo-analysis-kit), [maps published manifest](https://registry.npmjs.org/@cs2dak/maps/1.0.0), [contract published manifest](https://registry.npmjs.org/@cs2dak/contract/1.1.0), [rival-rating manifest](https://registry.npmjs.org/@rivalhub/rival-rating/0.3.0). Missing manifest license is a clearance uncertainty, not proof of absent permission everywhere.
- **R3:** [sparkoo architecture](https://github.com/sparkoo/csgo-2d-demo-viewer/tree/dev), [MIT license](https://github.com/sparkoo/csgo-2d-demo-viewer/blob/dev/LICENSE).
- **R4:** [skkwowee repository inventory](https://api.github.com/repos/skkwowee/cs2-demo-viewer/contents/).
- **R5:** [awpy-data workflow, conventions and asset licensing](https://github.com/pnxenopoulos/awpy-data).

Existing research reviewed: the two consolidated reports, Muse A/B/C, parser/map/viewer appendices and benchmark notes. Those remain unchanged; the decisions above supersede their broader acquisition, dual-parser, standardized-internal-format and viewer-fork recommendations for this phase.

# Phase 0 — risks, experiments and evidence

Status: Phase 0 implemented; C0/C1/C2 and foundation hardening exercised. Historical preparation evidence remains below, separately from [implementation verification](#implementation-verification). [Decisions](phase-0-decisions.md) · [Architecture](phase-0-architecture.md) · [Execution](phase-0-execution.md).

## Blocker classification

- **Foundation:** approved adjustments implemented; the actual local ingestion/storage/API/replay path and operational recovery checks passed.
- **Verification limits:** process termination and injected publication/IO faults were exercised; physical power-loss behavior was not simulated.
- **Compatibility expansion:** POV/bots/overtime/multilevel and historical-map fidelity remain unverified on real matching recordings. G10/G11 below are limits, not a reason to reopen the selected stack.

## Prioritized verification gates

All filesystem experiments use an isolated temporary app root and watched scratch directory. Never mutate the real demo or CS2 installation. Reuse existing local files; no gameplay downloads are authorized by this preparation.

The table retains the original experiment criteria. Completed foundation checks are recorded under implementation verification; the preparation-only observations in older rows are historical, not current blockers.

| Gate / priority | Remaining assumption or failure mode | Short experiment and observable pass condition | Owner / when / blocker |
|---|---|---|---|
| **G1 / P0** | Snapshot SteamIDs do not universally identify observations | **Parent pre-freeze probe completed:** ten positive roster IDs, one null roster ID; sampled state had 6,388 null-ID rows, all health zero with empty names; positive `(tick,steamid)` keys were unique. Freeze unique row ordinals, positive-ID string keys and nullable references; never join unknown rows by name/zero. Bot/control continuity remains unverified and must not be claimed. | Parent before T0 freeze, not deferred to T2. T2 consumes this mapping. |
| **G2 / P0** | Quiet files and early `.dem.info` can still be incomplete; parser may accept a prefix | Slowly copy an existing demo into scratch, pause longer than the settle window, resume, then repeat using temp+rename. Also replace/truncate/rewrite a same-named source. Observe state/revision changes, safe snapshot retries and eventual latest content; a provisional prefix must not become permanent irreversible success. | T6/T8, release gate. No universally reliable “download finished” signal exists for arbitrary writers; document the heuristic plus revision reconciliation. |
| **G3 / P0** | SQLite commit and file publication can diverge on crashes/disk-full | Inject failure after staging write, after fsync, after rename/before DB commit and after DB commit; restart. Also interrupt a reprocess and remove/corrupt an app-owned artifact in scratch. No incomplete generation is served; current pointer remains last-good or shows an explicit recoverable error. | T1/T8, release gate. Local rename/WAL primitive smoke passed, not this recovery behavior or power-loss simulation. |
| **G4 / P0** | Worker/native failure, parent death or reloader can leave duplicate/stale publishers | Kill parse child, kill/restart coordinator, start a second coordinator against the same data directory; poll status during a real parse. One coordinator/parse owner; dead attempts cannot publish; API survives child failure and requeues interrupted work once. | T8, release gate. Single-process OS lock and supervised child IDs are simpler than distributed leases. |
| **G5 / P1** | Lost notifications, initially absent roots and permission errors can prevent automatic discovery | Watch a scratch root, add/move a file, stop app and add another, recreate a missing root, simulate watcher failure. Startup/periodic reconciliation recovers each candidate once by content; unavailable roots are visible. Debounce is not treated as write completion. | T3/T6, release gate for automatic ingestion. Watchfiles itself was not runtime-exercised during preparation. |
| **G6 / P1** | Persisted replay may be offset in time/space or served from a changed generation | Launch the actual application/browser with the persisted local match. Choose a round and kill; compare exact tick with state, seek backward/forward, cross ±180 yaw, pause/resume, test missing samples and stale responses. Display extracted radar; verify three manually chosen landmarks against overview mapping and label version mismatch. | T4/T5/T7/T9, release gate. Parsing, event-tick lookup and extraction passed separately; no application/replay UI was built or viewed in preparation. |
| **G7 / P1** | Awpy 3 is a fresh major rewrite; future engine changes can break a previously valid profile | Reparse the same retained local canary with any proposed dependency update; compare normalized semantic table values, null rates, identities and tick coverage. Keep package locks and parser/schema provenance. Treat silent all-null required fields as failure. | T2/T9, baseline and every upgrade. Do not pin to unreleased main or compare byte-identical Parquet as the semantic contract. |
| **G8 / P1** | Large demos/full snapshots may exceed memory; API queries can block scheduling | Measure actual worker wall time/peak RSS/output size separately from dependency installation; issue status reads during parse and bounded replay reads. Trigger child resource failure in scratch and observe structured error + surviving parent. Keep concurrency one; tune measured budgets, not library marketing throughput. | T7/T8/T9, release gate. Preparation scripts are not optimized production benchmarks. |
| **G9 / P1** | Loopback service can still be driven by a hostile web origin; dependencies/assets may cause outbound traffic | Run with outbound access denied after provisioning; parse and replay from local inputs/assets. Reject foreign Origin/Host and non-JSON mutation attempts, path traversal and oversized replay windows. Verify listener is loopback-only. | T7/T9, release gate. No cloud backend/telemetry/model runtime is needed. |
| **G10 / P2** | One Valve GOTV file does not establish POV, bot, overtime, multilevel or alternate-provider fidelity | When an appropriate user-owned local demo is available, run the same profile and annotate concrete limitations. Test partial entities/round boundaries without zero filling; multilevel Z selection needs a matching radar/fixture. Do not assert fixed ten players or MR12 from defaults. | T2/T4, compatibility gate for each claim. Existing canonical design handles nullable/partial data; those recording-specific outcomes remain unverified. |
| **G11 / P2** | Historical demo map build differs from today's install; radar rotation/floor metadata is not uniformly portable | Record demo version source separately from installed asset version. Exercise nonzero rotate/zoom and altitude sections on a known map; determine whether they are HUD-only metadata. Current asset may be used only with explicit mismatch/unknown status; exact historical spatial claims require matching historical assets. | T4, non-blocking for the labelled Inferno proof; blocks historical geometry/visibility claims, which are outside Phase 0. |

## Preparation evidence

### Scope and fixture

Read-only inspection found a real replay at:

```text
/mnt/nvme/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays/match730_003848291889069425328_1896084263_388.dem
```

Input size: **301,894,448 bytes** (about 287.9 MiB), PBDEMS2, `SourceTV Demo`, `de_inferno`; sibling `.dem.info` exists. No other demos/compressed demos were found within the inspected installation, Downloads/Desktop/Documents and relevant reported Steam roots. This is not proof that no demo exists elsewhere.

The demo header's game-directory string contains `v2000930`: build **inferred from text**, not an explicit authoritative ClientVersion field. Installed `steam.inf` directly reports ClientVersion/ServerVersion 2000932 and SourceRevision 11131657. Do not conflate these with Steam depot buildid. The sidecar was not protobuf-decoded; encrypted chat, a winning-team scoreboard and “complete match” ground truth were **not independently verified**.

### Executed compatibility probes

During preparation, package/tool downloads and derived probe files were outside the repository. No production source/scaffold or project dependencies were created in that preparation stage, and no gameplay was downloaded or game-install output written. Its temporary parser output, databases, CLI and radar assets were removed. Those parser runs observed unchanged source size/mtime/inode; the later implementation separately verified original-versus-owned byte hashes.

| Probe | Actual work | Observed result |
|---|---|---|
| Python/runtime inspection | System/interpreter/package inventory | System Python 3.14.7; separate Python 3.13.15 available; SQLite 3.53.4; uv/node/npm available; Node v26.8.2. No system/project Awpy/Polars installation was required. |
| Complete backend resolution | `uv pip compile --python-version 3.13 --only-binary :all: --no-cache -`, stdin pinned Awpy/Polars/FastAPI/Uvicorn/Pydantic/watchfiles/srctools requirements from decisions | Exit 0, 27 packages resolved. Resolution only, not full API runtime verification. |
| Frontend resolution | Temporary package manifest with selected UI versions; `npm install --package-lock-only --ignore-scripts --no-audit --no-fund` | Exit 0; no `node_modules` created. No UI build/browser verification claimed. |
| Steam KV1 parser | Temporary `uv run --no-project --no-cache --python /home/filip/.local/bin/python3.13 --with srctools==2.7.0 python -`; parse actual libraryfolders/appmanifest with `Keyvalues.parse` | Exit 0; resolves the supplied CS2 installation through app 730 membership and `installdir`. |
| Initial Awpy probe | Released Awpy/Polars; `load(rounds,kills,damages)`, `players`, `snapshots(every=64)`, raw tick projection, Zstd Parquet round-trip | 11 roster records; 24 rounds; 172 kills; 827 damage rows; 24,710 sampled state rows; 1,581,200 raw tick rows; native tick range 1–158,120 at 64 Hz. Round-trip equal. 4.288 s; peak RSS 1,121,612 KiB. |
| Full profile/schema probe | Load players/rounds/kills/damages/shots/bomb/grenades/smokes/fires/blinds/item_events/round_economy; `snapshots(every=1)` | Additional datasets: shots 4,467; bomb 124; grenade trajectory rows 50,659; smokes 114; fires 96; blinds 186; item events 1,407; round economy 48. Full state: 1,581,200 rows. XYZ/yaw/pitch Float32, all non-null on this fixture. |
| Adapter hazard probe | `ticks(["yaw","pitch","m_angEyeAngles[0]","m_angEyeAngles[1]"])` compared with the typed snapshot path | Every requested raw-angle column was String/all-null. This is an unsupported-query-spelling hazard, not evidence that numeric casting can recover angles. **Use snapshots.** |
| Persistence/ID/event alignment | Cast full state SteamIDs to String, ticks to Int64; Zstd Parquet write/read; compare exact ID strings; explicit first-kill tick snapshot | Full normalized state round-trip equal; file 18,051,616 bytes; ID strings exact and JSON value type `str`; kill tick 2177 returned ten state rows all at that tick. Combined second script: 9.760 s, peak RSS 2,029,032 KiB. |
| SQLite/filesystem primitives | Temporary WAL database, two connections; fsync manifest/directory, rename generation, insert/commit catalog reference, reopen | `journal_mode=wal`; second connection saw 0 rows before commit and 1 afterward; generation reference survived reopen. **No crash injection or power-loss proof.** |
| Local asset extraction | Download official self-contained Source2Viewer CLI 20.1 Linux x64 to `/tmp`; run against installed `pak01_dir.vpk` for Inferno overview and radar | Both commands exit 0. Overview origin/scale: −2087, 3870, 4.9; radar PNG 1024×1024, 136,914 bytes. No system .NET installation or game changes. This was extraction/header inspection, not visual landmark validation. |

The two parser scripts did different work and materialized extra validation data; their timings/RSS are **not a controlled parser benchmark**, a resource limit or an application SLA. Full-rate storage is feasible on this sample; the second measurement also justifies not spawning multiple parses by default. Roster records and active-state records have different semantics; their differing populations are not automatically corruption.

Reproduction entrypoint for the parser scripts (Python supplied on stdin; input opened read-only):

```sh
uv run --no-project --no-cache \
  --python /home/filip/.local/bin/python3.13 \
  --with awpy==3.0.0 --with polars==2.0.0 python -
```

Invocations used for the extracted assets, with `<out>` a temporary directory and `<pak>` the actual installation's `game/csgo/pak01_dir.vpk`:

```sh
Source2Viewer-CLI -i '<pak>' -f resource/overviews/de_inferno.txt -o '<out>/overview'
Source2Viewer-CLI -i '<pak>' -f panorama/images/overheadmaps/de_inferno_radar_psd.vtex_c -o '<out>/radar' -d
```

These are recorded preparation commands, not a production extraction script or request to run them again.

## Regression and fixture strategy

- Keep ordinary CI independent of private local demos and the game installation. Author small contract/identity/null/time/race fixtures for deterministic consumer-visible behavior; do not commit downloaded gameplay, player-identifying exports or Valve assets.
- The implemented opt-in native canary is the real CLI `import /absolute/path/file.dem` / `reprocess <hash>` path with an explicitly chosen data root. It was exercised on the known local file, separately from ordinary CI fixtures. No skipped test is counted as a successful native parse, and no private demo is bundled.
- The most useful permanent checks are ID precision/null actors, unsupported-angle-field rejection, entity-lifetime joins, source revision/dedup transitions, generation publication recovery, stale generation handling and replay clock/shortest-arc behavior. Avoid tests of wording, copied defaults, forwarding or source text.
- Compare normalized semantic values, schemas and coverage; Parquet byte equality is not a stable cross-version contract. The preparation probe used in-memory equality after round-trip, not a byte-identical-file claim.
- Upstream Awpy has opt-in fixture storage/checksum and scoreboard-validation patterns; its [fixture README/manifest](https://github.com/pnxenopoulos/awpy-fixtures) covers Valve/FACEIT/ESEA/HLTV GOTV sources. Do not infer its software MIT license covers every gameplay artifact or silently download these in project tests. No upstream gameplay was downloaded here.
- demoparser's repository contains gameplay/golden fixtures, and cs2-demo-format/DAK contain normalized JSON/ZIP examples. They can inform schema/delta tests **if those formats are later adopted**; they do not validate the selected canonical full-rate path or justify adding the packages now.

## Explicitly deferred, not architectural blockers

- Encrypted team chat/decryption-key handling, voice, exact sub-tick input, spotting-mask semantics, smoke voxels, LOS/visibility truth and historical collision/nav assets. The basic local gameplay probe passed without decrypting the sidecar or reconstructing any of these.
- cs2df export compatibility, DAK source-TS bundling/transitive license clearance and pandas 3 behavior: none is a selected runtime dependency. Do not turn rejected-alternative risks into mandatory Phase 0 work.
- DuckDB integration, cloud/remote downloads, hosted-provider selection/budgeting and long-term coaching evaluation. They have stable future input boundaries but no code or experiments in this phase.

Primary package/tool/API/license evidence is linked in [decisions](phase-0-decisions.md#primary-sources). The following records the exercised implementation, not inferred readiness.

## Implementation verification

| Checkpoint / check | Observed evidence |
|---|---|
| C0 | Pinned dependencies installed; pre-freeze identity/field probe completed; all seven typed/empty Parquet schemas round-tripped; explicit data-root precedence and insufficient-space rejection exercised; real OpenAPI and generated TS types exported. |
| C1 | Actual `csda import` preserved the local recording, published/validated seven tables and completed a durable job. Original and owned-file SHA-256 matched `6ce06d397f8ce5b13b312bfd7b9c84415498319298ee5747d471e0fa43a8b5cb`. The bounded full-rate state table is 16,750,053 bytes; no broad upstream inventory is required. |
| C2 automatic ingestion | A fresh data root discovered the real demo; a new file appeared in a configured watch directory without invoking `/imports`. Identical bytes converged to one recording/one initial parse job. Persistent API reads worked while native parsing ran. |
| C2 actual browser | Production build served the real Inferno radar/data. Play advanced the tick; pause held it; kill navigation selected exact tick 2177; keyboard seek selected 1442; round two reset to 8082. Canvas and DOM tick agreed. Current asset-versus-demo build mismatch and unresolved identities were visibly reported. Browser closed after verification. |
| Spatial calibration | Real CT/T spawn medians and A/B plant positions mapped near the extracted overview icons, without axis inversion. These are approximate map landmarks, not proof of historical collision geometry or player visibility. |
| API responsiveness | During a real reprocess, 98 loopback health requests had maximum observed latency 6.52 ms. This is one machine/run, not an SLA or controlled benchmark. |
| Worker/coordinator faults | Actual parser SIGKILL produced a failed job while the API and last-good generation survived. Actual coordinator SIGKILL was followed by successful restart/requeue with a new generation token; the old child was gone. SIGTERM during parsing also resumed exactly once after restart. |
| Resource budget | A real parse with a 0.001-second worker budget returned `RESOURCE_LIMIT` and retained the previous successful generation. Disk-space boundaries and simulated ENOSPC were covered by behavioral tests; the user filesystem was not filled. |
| Paused write | A real demo prefix paused for 10.3 seconds was retained under a distinct content identity. Appending the remaining original bytes triggered revision reconciliation to the full recording; the prefix remained preserved with a superseded-source warning, not irreversible success. |
| Recovery regressions | Verified raw-file rename before catalog registration, publication/catalog interruption, missing/corrupt artifacts, last-good preservation, exact string IDs/null actors, unavailable-clock rejection, sidecar partial-publication repair, generation-pinned replay and Host/Origin/body/window rejection. |
| Automated checks | Final backend suite: **123 passed**, one upstream Starlette/httpx TestClient deprecation warning (not suppressed). Frontend `tsc --noEmit && vite build` passed. |
| Offline execution | Actual retained-demo reprocessing succeeded under `unshare --user --map-root-user --net`, with networking unavailable. Radar came from the local install/cache, not hosted assets; browser navigation/subresources were restricted to loopback during verification. |

The real imported recording, valid generations and provisioned CLI/cache remain at `/mnt/nvme/developer/cs-demo-analyzer-data`, outside the repository and OS default data directory. Disposable crash/write-test roots were removed and verification servers stopped. No game-install files or research documents were changed, no gameplay was downloaded, and no coaching/AI/next-phase work was started.

Native compatibility is demonstrated on the existing Valve Inferno recording only. Unknown/dead-player identities remain nullable and make this generation partial; arbitrary bot/control continuity is not claimed. Current-install radar is deliberately labelled mismatched to the inferred recording build. The original verification criteria for additional recording types and historical spatial fidelity remain applicable when those capabilities are pursued.


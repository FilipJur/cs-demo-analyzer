# Phase 2 — Player-centric reconstruction

## Evidence and ownership

Gameplay extraction remains authoritative, immutable, generation-pinned Parquet. SQLite remains the catalog and durable job store. Reconstruction reads the existing analytical layer; it does not introduce a second gameplay database or an AI/coaching layer.

The shared `domain/evidence.py` vocabulary distinguishes recorded observations, deterministic computations, geometry-dependent findings, qualified estimates, and unsupported claims. Capabilities carry explicit statuses and limitations, not arbitrary confidence scores. Provenance identifies the demo, generation, extraction profile, method/version, recording build, and applicable map asset. All information is scoped to **omniscient replay**, never player perception.

The primary subject is persisted in the catalog's singleton `app_settings` row, seeded by migration 0002 with SteamID64 `76561198057213632`. SteamIDs cross persistence/API/UI boundaries as strings. Participation is `present`, `absent`, `unresolved`, or `not_ready`; a manual subject override never silently falls back to the primary subject and does not require re-ingestion. Unresolved roster entries cannot establish the absence of an account.

## Available recordings

Discovery found **five actual `.dem` recordings**, not six. All five originals were re-hashed to their catalog SHA-256 and successfully ingested/extracted. The primary subject is present in all five. The following are the exact source files under the discovered CS2 `game/csgo/replays/` directory:

| Map | Source filename | SHA-256 |
|---|---|---|
| Inferno | `match730_003848291889069425328_1896084263_388.dem` | `6ce06d397f8ce5b13b312bfd7b9c84415498319298ee5747d471e0fa43a8b5cb` |
| Vertigo | `match730_003847743468990365878_1602058667_274.dem` | `7176541706e3aa3f7c41c794f27fa19922a5e52bff54180077c41869eb9ade6c` |
| Dust2 | `match730_003847740048048914711_1102039603_390.dem` | `1ce8c6f80493bc61eabe83ca5621f4017f31b60737626fbe5197b4b56a43d26f` |
| Train | `match730_003847735914142892513_1770210822_191.dem` | `68d7078356f499e45e2da509f793931de189f601277e0e5838a8f219ac052b69` |
| Ancient | `match730_003848295211226628097_1757297025_411.dem` | `ec15aa4a3da05f29d1e5fb62941236655cd08afce1a88f063b5a51583a7432ec` |

### Compatibility measurements

Measured against the retained foundation generations, across **all participants**, not just the subject:

| Map | Rounds | State observations | Alive identified / alive total | Anonymous dead observations | Subject rounds observed | Position/angle/health anomalies | Radar/replay |
|---|---:|---:|---:|---:|---:|---|---|
| Inferno | 24 | 1,581,200 | 1,141,438 / 1,141,438 | 408,814 | 24/24 | 0 | Available; current-build radar |
| Vertigo | 18 | 962,430 | 656,536 / 656,536 | 281,897 | 18/18 | 0 | Available; lower floor declared |
| Dust2 | 20 | 1,178,417 | 784,498 / 784,498 | 367,021 | 20/20 | 0 | Available; current-build radar |
| Train | 18 | 878,360 | 628,213 / 628,213 | 224,343 | 18/18 | 0 | Available; lower floor declared |
| Ancient | 16 | 915,763 | 666,527 / 666,527 | 211,268 | **13/16** | 0 | Available; current-build radar |

All five use a recorded 64 Hz clock and inferred demo client version `2000930` (`awpy.Demo.header.game_directory`). Installed client assets are `2000932`: **all map comparisons are mismatched, not historical-exact**. The foundation recording-type field is `unknown`; filenames and the recorder's display name do not establish GOTV versus POV. Each roster contains ten resolved players and one unresolved recorder entry; quality is `partial` rather than silently complete.

Validation found no null health, alive-null identity, non-finite/incomplete positions, missing angles, out-of-range health or orientation, state identity outside the roster, inverted/overlapping round intervals, or missing event ticks/victims. Round numbers increase; official ends follow round ends. Inter-round gaps are 448 ticks, or 544 at the side transition. Null attackers occur in world-damage/world-kill cases and are retained, never assigned to a player. Warmup/inter-round/post-match events exist and are not forced into an encounter round.

**Ancient limitation:** the subject has no state observations in rounds 10–12 and resumes in round 13, while other participants remain observed. Missing observations are not inactivity, death, or a substituted identity. The cause is not established by foundation data.

Anonymous state observations have `health == 0` in every tested recording, independently checked rather than assumed from Inferno. Identified-dead rows also exist. Neither form is living support, and anonymous corpses are never reattached to participants using position/name. These dataset findings are not a universal parser guarantee.

### Missing payloads

Two matches have `.dem.info` sidecars but no `.dem` payload:

- `match730_003847747130449985983_0950917540_273.dem.info`
- `match730_003848277320540357054_1971985281_193.dem.info`

A sidecar is not a recording. Searching the local filesystems did not locate those payloads; there is nothing ingestible to enqueue. Re-download a match through CS2 to supply the missing bytes; existing discovery will then ingest it. No automatic remote replay download was added.

## Extraction profiles

`foundation-v1:awpy-3.0.0:schema-1:normalizer-1` remains unchanged and readable. New application jobs explicitly request `reconstruction-v1:awpy-3.0.0:schema-2:normalizer-1`; reprocessing creates a new generation, not an in-place mutation. Profile-specific table names, dtypes, hashes, and profile/key/schema/normalizer correspondence are checked before publication. Catalog reads prefer a published reconstruction head and fall back to foundation only when no reconstruction head exists. Explicit old-generation reads remain pinned.

The extended profile retains all participants and the seven foundation tables. It adds eight typed tables:

| Table | Supported content | Semantics / limits |
|---|---|---|
| `player_state_ext` | Tick/identity, movement flags, equipment, helmet/defuser, grenade counts, primary/secondary weapon, flash duration, inventory serialization | One-to-one `row_ordinal` alignment with `player_state`; nullable values retained. Inventory is upstream text serialization, not a second structured inventory model. |
| `blinds` | Affected participant, source participant where available, positions, onset, replicated duration | Awpy reconstruction from pawn flash state and flash detonation; not a raw event-only assertion. |
| `smokes` | Cloud entity/serial, position, start/end, truncation flag | Entity-lifetime observation; no claim of exact cloud volume or ray blockage. |
| `fires` | Fire entity/serial, position, start/end, truncation flag | Entity-lifetime observation; no continuous damage volume invented. |
| `grenades` | Projectile entity/serial, kind, per-tick XYZ | Observed trajectories, not invented interpolation or inferred thrower identity. |
| `item_events` | Purchase/pickup/drop, participant/item/position where supplied | Awpy reconstruction from inventory-state transitions, explicitly labelled as such. |
| `round_economy` | Per-round side/equipment/buy type | Upstream computation over recorded equipment; not a tactical verdict. |
| `player_lifecycle` | Connect, disconnect, spawn, team change, slot/pawn handle where supplied | Recorded engine events; identities only where the event supplies them. |

Extended combat tables additionally retain recorded event positions, entity handles, shot ammunition/inaccuracy/scoped fields, damage hitgroup codes, flash-assist and applicable kill flags. Hitgroup names are deterministic labels for codes. Upstream trade classifications and pre-hit health/armor estimates are **not** published as recorded facts.

No verified view-origin field is available. Snapshot `is_blinded` (`m_bFlashing`) was false even when `flash_duration` was populated in the probes; it is not blindness evidence. Utility owner fields are absent in the tested parser outputs and remain null. Manifest capabilities name these limitations and the source datasets. Empty serialized inventory means no weapon entity resolved, not proof of carrying nothing.

Extended Ancient lifecycle evidence includes a subject disconnect at tick **42252**, reason code **79**, `ever_fully_connected=true`, and another disconnect at tick **91842**, reason **59**. These are source observations, not an inference from the missing state window. No unrecorded reconnect or control hand-over is invented.

## Encounter segmentation and anchors

`EncounterService` groups subject shots, damage dealt/received, kills, deaths, and assists within each usable round. A gap exceeding the configured threshold splits an episode; a subject death terminates it after all same-tick events. Defaults: 3 seconds between seeds, 3 seconds of pre-contact context, 1 second after the last event. Windows are clipped to round bounds. These are reproducible segmentation rules, not claims about player intent or perception.

Shot-only episodes remain inspectable but explicitly state that no interpersonal interaction was established. Contextual events expand only one participant hop within the bounded source window. Events are ordered by tick, canonical dataset order, and row ordinal; this tie-break is not claimed to be the engine's sub-tick causal order.

Encounter v2 IDs depend on generation, subject, round, seed identities, tick rate, and grouping/window options. Detail requests with different options cannot silently reuse an ID. Underlying event evidence references retain exact dataset/ordinal/tick/participant identities; trajectory rows are verbatim observations on a reported bounded stride, with missing ranges.

Distinct anchors include pre-contact window, first interaction, first shot, first damage, kills/death/assists, last interaction, post-contact window, and resolution. Unavailable first-shot/damage anchors carry null ticks and unsupported status. Recorded anchors reference source rows; window markers and event-gap/round-end resolution are computations. `event_gap` means no further subject event within the configured gap, **not** proof anyone was inactive. Geometry-dependent exposure is a separate context result and never overwrites an observed combat timestamp.

## Real-demo integration evidence

The actual application coordinator published reconstruction generations for all five recordings in **31.25 seconds** total; a later **30.28-second** reprocess refreshed corrected provenance notes without changing the data. The final heads are listed below; earlier generations remain retained. Core table row counts are unchanged for every demo; `player_state` and `players` Parquet hashes are byte-identical to the previous foundation heads. `player_state_ext` aligns one-to-one by row ordinal.

| Map | Reconstruction generation | Blinds | Smoke intervals | Fire intervals | Projectile observations | Lifecycle events |
|---|---|---:|---:|---:|---:|---:|
| Ancient | `c6f3177ab9b24ceca620ae757a7c5c2e` | 115 | 54 | 36 | 27,378 | 180 |
| Train | `b6802b1528c045de86c3d3a3d2e60eed` | 93 | 41 | 28 | 26,636 | 195 |
| Dust2 | `3c39539c275847db9c25a352f8d2dcf3` | 110 | 42 | 45 | 26,547 | 220 |
| Vertigo | `41a9ed0241c848a1b75bf1176d766a6a` | 49 | 21 | 31 | 14,952 | 193 |
| Inferno | `748b08368e464a76a684da3be42a13a2` | 186 | 114 | 96 | 50,659 | 251 |

Live HTTP inspection independently matched first-damage anchors to the Phase 1 source-event window endpoint, and recomputed active relationship distances/team assignments from exact raw state:

| Map / round | First interaction | First damage evidence | Subject death | Living relationships at contact | Active relationships after subject death |
|---|---:|---|---:|---:|---:|
| Ancient / 1 | 2730 | `damages:4@2733` | 2880 | 8 | 0 |
| Train / 1 | 2529 | `damages:21@2703` | 2839 | 7 | 0 |
| Dust2 / 1 | 3533 | `damages:25@3533` | 3982 | 4 | 0 |
| Vertigo / 1 | 3291 | `damages:36@3672` | 3876 | 5 | 0 |
| Inferno / 2 | 11344 | `damages:41@11344` | 11367 | 5 | 0 |

Ancient tick **59943** reports `subject=null`, zero active subject relations, and the recorded disconnect at 42252 as its preceding lifecycle evidence. No participant substitution or inferred inactivity is supplied.

Live configuration smoke changed the primary to another recorded SteamID, then to an unmatched account. The unmatched account reported `unresolved` (the roster has an unresolved entry), encounter reads returned `SUBJECT_UNAVAILABLE`, and an explicit original-subject override remained usable. Restoring `76561198057213632` changed no demo/generation identity and triggered no ingestion.

## Map geometry and navigation

All five installed dataset maps are supported. `GeometryService.prepare` invokes the already-provisioned **Source2Viewer-CLI 20.1** against each local map VPK, exporting **`maps/<map>/world_physics.vmdl_c`**, not rendered world meshes, to GLB and extracting `maps/<map>.nav`. The bounded nav reader follows the MIT ValveResourceFormat 20.1 format implementation, including current v36 areas and ladder transitions. No Source 2 map/VPK parser was reinvented.

Coordinates remain full 3D Hammer units, Z-up. Collision triangles are indexed in a uniform-cell grid; rays use segment-bounded triangle intersection. Point queries expose bounds, floor/ceiling measurements, and nav-area identity where supported; missing geometry produces null location facts, never a fabricated outside/empty-world result. Nav membership uses recorded player origins; ray endpoints use separately labelled stance-based eye estimates (standing 64, crouched 46 units).

| Installed map | Collision triangles | Nav areas | Cold preprocessing | Derived cache | Asset suffix |
|---|---:|---:|---:|---:|---|
| Inferno | 2,733,603 | 2,738 | 19.5 s | 69.9 MB | `9f9ac024183d4c0e` |
| Train | 1,574,220 | 2,154 | 11.1 s | 41.7 MB | `9c71cf5ffbf95b34` |
| Ancient | 967,778 | 1,969 | 6.7 s | 27.1 MB | `361deb824922c822` |
| Dust2 | 435,649 | 2,242 | 3.8 s | 15.7 MB | `cab06fcbc8f00ba5` |
| Vertigo | 210,596 | 2,105 | 2.4 s | 28.3 MB | `4943efc1807d8c37` |

Asset IDs are `geometry:2000932:<map>:<suffix>`. Cache manifests record raw resource and exported-GLB SHA-256 identities, tool/parser versions (`geometry-v5`), timings, component status, bounds, and excluded movement-only clip groups. Stat fingerprints of the installed VPK and applicable package chunks detect resource changes even under the same client version; changed/missing dependencies invalidate both persisted and already-loaded geometry until explicit preparation. No huge VPK is rehashed on a query. Parser/provenance mismatches also reject stale caches. At most two loaded maps are retained in memory. Preprocessing never runs during a scrub/read. Encounters are computed on demand rather than persisted in a competing store.

Inferno source hashes, available verbatim through capability provenance:

- Physics: `b721f2085f61331939a315f24f61b8a1037f123d16213deecaa4dbfc6b99f22f`
- Nav: `8d312122a9758a1b64b397f0e02b16e18e9432f738ab7308d0b73cb7df118111`
- Exported collision GLB: `2cbdc6dbb343222dade6f45cb0d58dd60df1c2afec86b49211a079b7a5c76e3c`

### Geometric demonstrations

Production HTTP queries reproduced the following current-build collision results, all carrying the demo/build mismatch:

| Case | World coordinates | Result |
|---|---|---|
| Clear local segment | `(600.5,2528.5,244)` → `(581,2536,244)` | `static_clear` within the loaded collision subset |
| Separating geometry | `(-28,219,265.3)` → `(400.2,19.7,134)` | `static_blocked` at 40.05 units; `wood_furniture`, `triangle:1806577` |
| Vertical segment | `(-1586.5,440.8,0.1)` → `(-1586.5,440.8,4096.1)` | `static_blocked` at 399.64 units, `wood` surface with downward normal |
| Outside bounds | `(4480,0,0)` → `(4736,0,0)` | `unknown`, never clear |
| Missing map | `de_no_such_map`, `(0,0,64)` → `(100,0,64)` | `unsupported`, no asset |
| Floor/area | `(2493,2090,134.65)` | floor Z 132.241, nav area 2298, in bounds, outside solids |
| Navigation | `(-1586.5,440.8,-63.9)` → `(2292.1,2027.7,136.1)` | Connected stored graph: direct 4195.45, area-centre estimate 7238.36 units over 132 areas |

Additional real-resource checks found floor heights within 0.83 units of ten recorded player origins, all ten outside solids and resolving to nav areas. Of sampled same-area pairs, 399/400 were collision-clear; 82/93 long-detour pairs were collision-blocked. These are alignment/collision checks, **not visibility accuracy statistics**. Recorded kill lines are not treated as visibility ground truth because penetration, event/state timing, and build changes can differ.

**Scope limitation:** only the installed `world_physics` resource is queried. Standalone entity models, doors, breakables and dynamic props are not merged. Movement/grenade-only clip groups are excluded from sightline rays but remain useful to point/floor queries. A physical surface may be transparent; material names never establish opacity. Thus `static_clear` means no intersection with this collision subset, not optical clearance, awareness, or historically exact visibility. These limitations accompany returned results, not just this document.

Nav distances are **area-centre graph estimates**, including stored links and ladder associations (Train has 11 ladders; Vertigo 1). They are not verified continuous routes, shortest-path guarantees, travel times, or trade/support availability. Jump/drop/climb feasibility and player movement constraints remain qualified.

No running-game/3D-renderer comparison was performed. Visual identification of particular walls, transparent surfaces, dynamic object states, and historical geometry remains unverified; none is asserted by the API.

## Context and evidence qualification

Active relations require both exact-tick endpoints to be identified and living (`health > 0`), with membership determined by the recorded side at that tick. Dead/unknown-health/anonymous rows are counted separately. Living teammate-to-opponent pairs are bounded to twenty, and expensive pair queries are opt-in for live scrubbing. Context exposes view-relative angles and angular spans without threat/risk/perception labels.

Movement measurements require a contiguous living sample run within one active round. Death, unknown health, missing grid samples or a round transition withhold displacement/path-length claims instead of connecting unrelated observations. Participant tracks retain bounded exact samples and missing counts. Radar trajectory rendering likewise breaks at missing/dead observations.

Exposure scans report their actual tick grid, including the last window tick, and preserve recorded combat anchors separately. They find, at most, the **earliest sampled static-clear segment** within a stated bounded window, using estimated eyes. Unknown dynamics, smoke volume/opacity, unrepresented entities and perception remain limitations. Every tested demo has a mismatched current map build, so historical effective sightlines stay unknown and no historical earliest-exposure tick is asserted.

Utility context includes exact source `EvidenceRef` values, intervals, timing/truncation limitations, and evidence kind. Smoke/fire entity lifetimes do not prove a particular ray was obscured; flash effects are upstream computations from replicated state, not proximity-based blindness guesses. Unknown owners remain null. Neither sounds, callouts, intent nor player awareness are reconstructed.

## Application and verification

The bounded API covers primary-subject configuration/participation, encounter lists/details, exact-tick and encounter context, and geometry capabilities/segments/navigation/location plus explicit preparation. Reads accept a generation pin; finite coordinate bounds and list/window ceilings are enforced. The OpenAPI contract generates frontend DTO/query types. Response serialization declares emitted default fields required, avoiding a second handwritten response contract.

The explorer retains its selected encounter while another round loads. Browser verification on Inferno navigated round 1 → the round-2 pre-contact anchor **11152** → first damage **11344** → subject death **11367**, with the replay clock, canvas label, context tick and selected encounter synchronized throughout. The death snapshot had zero active relations. Source event ordinals remain visible in the encounter timeline.

The navigation opt-in was exercised at tick 11152: the opponent 1136.95 units away had a 1594.91-unit area-centre graph estimate; a living teammate 1771.94 units away had a 2640.60-unit estimate. Missing endpoint/nav associations remained unavailable, not invented connections. Installed-map clear/blocked segment results remained historically unproven because of the build mismatch. The UI displays numeric graph estimates with their scope, not trade/support verdicts.

Ancient round 11 was also opened in the actual UI: tick **59943**, nine recorded participants visible, missing primary-subject state, zero subject relations, and the disconnect bracket shown. Missing subject data does not discard other participants or independently observed utility. An explicit absent-subject HTTP read at Inferno tick 83235 retained `smokes:59@83235` as evidence. Manual UI subject selection changed the inspection account while the persisted primary stayed `76561198057213632`.

Representative multi-opponent episode: Inferno **`enc-v2-r13-6a9fa21a730228d9`**, interactions **82543–84022**, two kills, **44 subject events + 34 contextual rows**, and 1613 exact trajectory samples. At first interaction the nearest living teammate was 183 units away; at the last interaction the nearest was 1357 units away with a current-build collision obstruction. All four living teammates remained represented; three dead opponents were excluded from active relationships. Utility included `smokes:59@83235` (83235–84647), `fires:39@83532` (83532–83884), and four separately referenced computed flash-effect rows at tick 83980. None was turned into a smoke-blockage or player-awareness assertion.

### Measured costs

Local observed timings, not performance guarantees:

| Operation | Observed cost | Scope |
|---|---:|---|
| Durable extended reprocess | 30.28 s | All five recordings |
| Encounter listing | 30–102 ms | One demo, 27–110 episodes |
| Exact context with cross-pairs | 49–189 ms | Representative contacts, navigation off |
| Exact context with navigation | 210 ms | Inferno tick 11152, five relations and six cross-pairs |
| Encounter context | 267–1829 ms | Representative contacts, navigation off |
| Larger encounter context + navigation | 5554 ms | Inferno round-13 episode, optional nav enabled |
| Static segment | median 1.04 ms / p95 3.97 ms | Loaded geometry, dependency-stat guard included |
| Point / nav query | median 17.9 / 7.9 ms | Loaded geometry service |

Final local verification: **378 backend tests passed, 1 skipped**; the skipped test is the opt-in real-install test, while real-resource/API/browser checks above were run separately. One upstream Starlette/httpx deprecation warning remains; no application warning was suppressed. `npm --prefix web run build` passed, and OpenAPI/TypeScript generation passed. Retained foundation replay and identity coverage endpoints were exercised for all five original heads. Browser console inspection found no JavaScript errors.

## Remaining boundaries and Phase 3

- Only five actual recording payloads were available; metadata-only matches need their original demo bytes.
- Recording type, controlled-pawn/bot identity continuity, historical-exact geometry, full dynamic entities and optical opacity remain unsupported or unknown.
- Eye positions are estimates; nav distances are graph estimates; bounded static-clear sampling is not perception or guaranteed interaction feasibility.
- The application implements no AI, tactical mistake classifier, coaching verdict, risk/performance score, or professional comparison.

Recommended Phase 3 boundary: human-reviewable behavioral hypotheses consuming these pinned evidence queries, with explicit counter-evidence and uncertainty requirements. Historical/dynamic/optical visibility gaps must constrain any future claim rather than be filled by a model. Phase 3 has not been started.

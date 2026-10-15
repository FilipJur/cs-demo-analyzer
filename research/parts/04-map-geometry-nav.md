# 04 — Map, Geometry, Visibility & Radar Layer for CS2 Demo Analysis

Scope: the *map-side* inputs a local-first CS2 coaching/analysis system needs — navigation meshes, collision geometry for
line-of-sight, Source 2 visibility data, radar/overview coordinate systems, `.vpk` tooling, map decompilers, and the
published numeric models for smokes / molotovs / penetration / audio occlusion.

Method note: every non-obvious claim below was verified by opening the primary artefact (repo README, source file,
game-file dump, release page, docs.rs/PyPI metadata) in Oct 2026. `web_search` summaries were treated as leads only and
are *not* cited unless corroborated. Each item carries a confidence class: **Demonstrated**, **Experimental**,
**Research-supported**, **Plausible-untested**, **Infeasible**.

---

## 0. Bottom line up front

1. **Fog-of-war visibility reconstruction is Demonstrated, not hypothetical.** Two independent open-source stacks do
   exactly this today from CS2 map collision geometry + demo state: **awpy** (`VisibilityChecker`, `awpy.map_control`
   with `raycast` / `vision` / `reachability` models) and **CS2DemoKit** (`CS2DemoKit.Analysis.Visibility`,
   `enemy_spotted` reconstruction). A third, **CS2FOW**, shipped it as a live server-side anti-wallhack (now closed
   source, repo archived 2026-10-06).
2. The hard part is **not** getting geometry — it's getting *good* geometry. The pipeline everyone converges on is:
   `maps/<map>.vpk → world_physics.vmdl_c → glTF → filter occluders → weld → (optionally decimate) → BVH`.
   `awpy-data` publishes exactly this, per CS2 `ClientVersion`, as a GitHub release.
3. **Nav meshes are not a visibility model.** They are a movement/reachability model. Nav portals are a *bound*, not a
   LOS oracle. Do not use them as the occlusion model; use them for area indices, distance-to-rotate, floor
   disambiguation and area-level aggregation.
4. CS2 **does** ship a compiled PVS-like resource, `world_visibility.vvis_c`, and VRF parses it (`IWorldVisibility`,
   `BspVoxelVisibility.Cluster`). Whether CS2's *runtime gameplay* uses it is contested; no open-source project has
   demonstrated player-level LOS from `vvis` clusters. Treat `vvis` as an optional accelerator, not a foundation.
5. Radar world→pixel mapping is a one-line transform (plus a vertical-section lookup on Nuke/Vertigo/Train) and its
   inputs ship as plain KV1 text in the VPK. **Redistributing radar images is the one genuine legal grey area** in this
   layer — plan to extract locally or let the user supply their own install.
6. Smokes are **not spheres** in CS2 (they are a networked 32³ voxel volume, ~640 u per side, Morton-coded). awpy
   models them as spheres anyway (`smoke_radius=144`) because that is cheap and sufficient for area-level control.
   Both approaches are legitimate; they answer different questions.

---

## A. Navigation meshes

### A1. `awpy-data` (the reference asset pipeline)

**What it does** | Extracts, from a local/anonymous-steamcmd CS2 install, per-map: raw `nav` bytes, radar PNGs,
`world_physics` collision geometry (decimated to a compact `AWMH` triangle mesh), and `map_data.json` (the radar
transform table). Publishes them as GitHub releases **tagged with the CS2 `ClientVersion`** (e.g. `2000873`).

**CS2 demo support (verified how)** | README read directly: it discovers maps from `game/csgo/maps/*.vpk`, then for
each map extracts (per README table):
| Kind | Source VPK | Internal path | Output |
|---|---|---|---|
| geometry | `maps/<map>.vpk` | `world_physics.vmdl_c` | `<map>.glb` (glTF, materials kept) |
| radar | `pak01_dir.vpk` | `<map>_radar_psd.vtex_c` | `<map>.png` |
| overview | `pak01_dir.vpk` | `overviews/<map>.txt` | `<map>.txt` (raw KV) |
| nav | `maps/<map>.vpk` | `<map>.nav` | `<map>.nav` (raw bytes) |
The README itself flags some of these internal paths as `TODO(verify)` in `scripts/lib.py` (radar/overview/nav paths),
while stating that the `world_physics` glTF path and its material tags were "confirmed against real data". Independent
corroboration for the *overview* path exists: `resource/overviews/<map>.txt` is a real, tracked path in
SteamTracking/GameTracking-CS2 (see C1). The nav path (`maps/<map>.vpk → <map>.nav`) is consistent with how CS2 map
VPKs are packaged (per-map VPK contains the world + nav) but I did not open a real map VPK, so: **Demonstrated** for
geometry/radar/overview extraction, **Plausible-untested (path only)** for the exact nav path.

**Maintenance status (as of Oct 2026)** | MIT. 5 commits total; last commit **2026-07-10** ("one tag and update name").
Code is *stdlib-only Python 3.11+*, driven by `Source2Viewer-CLI` + `steamcmd`; CI runs **daily on ubuntu-latest** and
only cuts a release when the Steam `buildid` changes. Peer-verified release cadence: tracks CS2 builds every few days
(`2000908 → 2000930`; `2000930` published 2026-10-09). Small repo, high leverage, actively regenerating.

**Architecture** | 5 stages: `fetch → extract → map_data → geometry → package`. External tools: `steamcmd` (anonymous,
app 730) and `Source2Viewer-CLI` (pinned Linux x64 self-contained binary downloaded by `scripts/install_tools.sh`).
Works on Linux/macOS/Windows with `--cs2-dir`; the anonymous-steamcmd path is Linux CI friendly.

**Data exposed** | `navs.zip` (`<map>.nav`), `images.zip` (`radars/<map>.png`, `radars/<map>_lower.png` for
multi-level maps), `geometry.zip` (`<map>.mesh`, magic `AWMH`, v1, `n_verts/n_tris` + f32 positions + u32 indices,
Hammer units, Z-up, little-endian), `map_data.json`, `manifest.json` (client/server/patch version, `source_revision`,
`buildid`, per-zip sha256).

**Programmatic integration** | Consumed by awpy's Python API (`awpy.data.mesh_path/nav_path/radar_path/map_data`,
`awpy get`) with cache at `$HOME/.awpy/<version>/`. Direct download of the release zips is equally easy.

**Open/closed + license** | Open, **MIT for the scripts**. The *assets* are Valve's (see C4).

**Linux compat** | Yes — its own CI runs on `ubuntu-latest`; the CLI binary it downloads is a Linux x64 build.

**Reusability** | Highest of anything in this cluster. It is literally "the map asset layer for CS2", version-matched
to game builds, with a documented binary format.

**AI real vs marketing** | N/A (data pipeline). Claim of "<0.1% of line-of-sight answers changed over 200k random rays"
after decimation on Inferno (2.5M → 0.55M triangles, ~4 MB) is a concrete, falsifiable number the README publishes —
treat as author-measured, not independently reproduced.

**Unsolved problems** | (a) which physics materials are *genuine* occluders is a heuristic (`DROP_SUBSTRINGS` for
player/grenade clips, sky, glass, windows, bullet-pass railings); (b) decimation can open pinhole gaps; (c) nothing
models *doors* (they move) or bullet penetration; (d) multi-level radar `verticalsections` are passed through but the
consumer must implement the altitude band selection.

### A2. awpy `NavMesh` (Python) — the nav API you would actually call

**What it does / Data exposed** | `NavMesh(map_or_path, version=)` → `areas` (Polars DF: `area_id`, `hull_index`,
`dynamic_attribute_flags`, `n_corners`, `centroid_x/y/z`, `size`, `n_connections`), `area(id)` → corners +
`connections` + ladders; `find_area((x,y,z))`, `neighbors(id)`, `find_path(start,end,weight="distance"|"hops"|"size")`,
`version`/`sub_version` (**CS2 ships nav version 36**), `is_analyzed`, `area_count`, `path`. `awpy.plot.nav()` draws
areas/routes over the radar.

**CS2 demo support (verified how)** | awpy docs `nav.html` + `api.html` read directly. Backed by `awpy-data` navs.
Rust implementation lives at `crates/awpy/src/nav.rs` (repo tree read).

**Maintenance status** | MIT; repo very active — last commit **2026-10-15** (today), v3 committed 2026-10-14, 1,465
commits, 618★. Python wheels for 3.11–3.15 incl. Linux aarch64/x86-64.

**Programmatic integration** | `from awpy import NavMesh`; `pl.Series` of `find_area` per kill is the documented usage
pattern. **Python 3.11+ / Polars 2.x.**

**Linux compat** | Yes (prebuilt wheels; Rust build optional).
**Reusability** | Very high for area-level spatial analysis (per-area aggregation, "which floor", distance-to-contact).
**AI real vs marketing** | N/A. Concrete API, no claimed ML.
**Unsolved problems** | Area IDs are not callouts — awpy has **no position→callout map** (open issue #390, per peer
verification); `find_path` weights are heuristics; connections are directional and the mesh is a bot mesh (may not
cover every player-reachable pixel).

### A3. ValveResourceFormat `NavMesh` namespace (C#, ground truth for the format)

**What it does** | `ValveResourceFormat/NavMesh/NavMeshFile.cs` parses `.nav`; namespace exposes `NavMeshFile`,
`NavMeshArea`, `NavMeshPolygon`, `NavMeshConnection`, `NavMeshLadder`, `NavMeshHidingSpot` (+ flags),
`NavAttributeFlags`, `NavDirectionType`, `NavMeshGenerationParams`/`NavMeshGenerationHullParams`,
`NavMeshTransformedBounds`.

**CS2 support (verified how)** | Source read: `MAGIC = 0xFEEDFACE`; `if (version < 30 || version > 36) throw
UnexpectedMagicException("Unsupported nav version")`. Version-36-only fields: `MovableMeshSettings` (KV3),
`MovableMeshGravityFollowsRotation`, `GameData`, `ExtraGenerationParams`. VRF's **format-support page** lists
`nav (navigation mesh)` → *3D view; export to `.glb`* (no `.nav` re-emit), and separately states **Source 1 `.nav`
meshes are not supported (issue #989)** — i.e. this parser is Source 2-only.

**Maintenance status** | MIT (except `Tests/Files`), **extremely active**: 7,097 commits; last commit **2026-10-14**;
latest release **20.0 (2026-08-17)**; 2.5k★. Oct 2026 commits include nav work ("Name navigation hull layers after the
game's hull presets", "Draw navigation space blocks, transitions and grid cells as layers").

**Programmatic integration** | NuGet `ValveResourceFormat` library, or `Source2Viewer-CLI` to export nav → GLB.
Atom feed was dead-ended for release dates; the tag page itself carries "released this 17 Aug".

**Linux compat** | Yes — CLI ships for Windows/Linux/macOS (self-contained).
**Reusability** | Use as the *format authority* and as the GLB exporter; don't depend on it in a Python/Rust service.
**Unsolved problems** | No writer; nav-space files (Deadlock's newer nav system) are a separate, unrelated format.

### A4. `nav2json-rs` (Rust) — small, single-release

**What it does** | Rust rewrite of VRF's nav parser → JSON: areas (corners, connections, ladders), generation params
(tile/cell size, hull params), `custom_data`.
**CS2 support (verified how)** | docs.rs crate page: **0.1.0, published 2026-02-03**, MIT, "Supported Versions: 30-35
(Source 2 engine)", claims games "Counter-Strike 2, Dota 2, Half-Life: Alyx". Its stated ceiling (35) is *below* the
version CS2 ships (36, per awpy docs), so its CS2 claim is likely stale — I could not verify a decodable v36 file.
Class: **Plausible-untested / likely stale**. 34 kB source, 0 examples in docs (43% doc coverage).
**Maintenance** | One release, no commits observed since; owner is an individual.
**Reusability** | Low: superseded by VRF (v36 + maintained) and awpy (Python, v36). **Ignore** unless you specifically
want a dependency-light Rust decoder and are willing to port the v36 deltas.

### A5. `cs2-nav` / `cs2_meeting_points` (Rust + PyO3 navigation *and* visibility utilities)

**What it does** | "Navigation and visibility utilities for Awpy in Rust" — produces CS2 meeting-point plots; deps
include `petgraph`, `geo`, `rayon`, `pyo3`, `bincode`; ships a `.pyi` stub and a CLI; a `hashes/` dir and periodic
"Updating last run time"/"Update webpage assets" commits indicate a scheduled pipeline producing published
meeting-point images.
**CS2 support (verified how)** | docs.rs crate page (`cs2-nav 0.3.18`, **2025-07-21**) + GitHub repo README
(`JanEricNitschke/cs2_meeting_points`, MIT, 637 commits, last commit **2026-10-08** — mostly dependabot). PyPI
`pip install cs2-nav`.
**Maintenance** | Alive but the PyPI/crates releases are **~15 months old** (Jul 2025) while commits continue —
surface is drifting.
**Reusability** | Medium: a *second opinion* on nav-graph visibility/meeting points, useful for validating your own
area-level LOS. Not a replacement for collision-mesh LOS. Class: **Experimental** (visibility output type unverified —
crate doc coverage is 35%).

### A6. Authored nav data in the game files (useful, under-exploited)

From SteamTracking/GameTracking-CS2 `git ls`-verified paths under `game/csgo/pak01_dir/scripts/`:
`nav_hulls.vdata`, `nav_hulls_presets.vdata`, `navlinks.vdata`.
I read `nav_hulls_presets.vdata` (KV3 text): it defines the *preset* list of hulls (`default = { m_vecNavHulls =
["player"] }`), i.e. the agent-hull definitions used to generate nav. Concretely useful for choosing ray origins/hull
sizes. `pak01_dir/navplace.db` also exists (place names — a possible callout source; **Plausible-untested** as I did
not decode it).
**Class**: Demonstrated (files exist and are readable text).

### A7. Source 1 nav parsers — do **not** use

`mzdw89/navmesh-parser` (nav v16, Source Engine) and `mrazza/gonav` target Source 1/CS:GO nav v16. CS2 ships v36.
**Infeasible** for CS2. Listed only to warn against search-result contamination (several LLM summaries recommend them).

---

## B. Visibility, line-of-sight and PVS

### B1. awpy `VisibilityChecker` + `crates/awpy/src/geometry.rs` — **Demonstrated**

**What it does** | Straight-segment occlusion test against a decimated collision mesh, BVH-accelerated.
**Verified how** | I read the Rust source, not just docs:
- `MAGIC = b"AWMH"`, `FORMAT_VERSION = 1`, `LEAF_SIZE = 4` (BVH leaf split), plus a small `SEGMENT_FRACTION` epsilon so
  a point resting on a surface doesn't self-occlude the segment leaving it.
- `pub struct Mesh { vertices: Vec<Vec3>, triangles: Vec<[u32;3]> }`, `Mesh::from_bytes/from_file` (validates magic,
  counts and indices).
- `pub struct VisibilityMesh`, `build()` "using top-down median/midpoint splits", `triangle_count()`,
  **`is_visible(a,b)`**, **`is_occluded(a,b)`**. Docs claim O(log n) queries.
- Python: `VisibilityChecker(map_or_mesh)`, `.is_visible/.is_occluded/.triangle_count/.path`. Docs explicitly warn:
  *static geometry only — does not model smokes, moving doors, or bullet penetration; player positions are not eye
  positions.*
**Maintenance** | Same repo/liveness as A2 (last commit 2026-10-15).
**Reusability** | **Reuse directly.** This is the cheapest correct foundation for player-vs-player LOS on CS2.
**Unsolved problems** | Occluder fidelity (what got dropped during extraction), doors (dynamic), penetration,
eye-height modelling (see B2/G), and *validation against ground truth* (nobody publishes a labelled "was actually
visible in-game" dataset — see Cross-cutting).

### B2. awpy `map_control` — **Demonstrated** area-level fog-of-war

**What it does** | Labels every nav area `ct` / `t` / `contested` / `neutral`, size-weighted, under three models:
- `raycast` — any living, unblinded player has LOS to the area in **any** direction.
- `vision` — same, but restricted to the player's horizontal FOV (`fov=90°`, CS2's own FOV); yaw from the demo.
- `reachability` — the side with the shorter nav-graph travel distance holds it; near-ties contested; unreachable
  neutral.
Outcome: `mc.map_control(demo, method=..., seconds=1)` (one row/tick: `ct,t,contested,neutral,net_control`),
`mc.map_control_at(demo, tick=, method=)` (per-area), `awpy.plot.map_control(...)`, tunable via `MapControlParams`.

**Verified how** | I read both the docs page and `crates/awpy/src/map_control.rs`. The Rust source confirms the model
precisely: `Observer{pos,side,yaw}`, `Occluder{center,radius}` ("callers place and size the sphere — e.g. a smoke
centred a little above where it landed, a molotov at the fire's footprint"), `Params{eye_height:64, crouch_eye_height:46,
target_height:46, max_distance, contest_margin:200, fov:90}`, `within_fov()`, `any_sees()`,
`segment_hits_sphere()`, `line_of_sight_control()`, `raycast_control()`, `vision_control()`, `reachability_control()`,
plus unit tests (`raycast_smoke_blocks_sightline`, `a_full_circle_fov_matches_raycast`).

**Defaults that matter** | `smoke_radius=144.0`, `smoke_height=60.0` (smoke sphere centre above the landing point),
`fire_radius=150.0`, `flash_threshold=1.0`, `eye_height=64`, `crouch_eye_height=46`, `target_height=46`, `fov=90`.

**Maintenance** | Same as awpy (active).
**Reusability** | **Integrate.** This is the closest existing implementation of the "who could see what" layer; even if
you re-implement the visibility core, copy the *model semantics and parameter set*.
**AI real vs marketing** | Pure geometry, no ML. The docs are commendably explicit that it "estimates control, not
exact player perception" (ignores pitch).
**Unsolved problems** | (a) smokes as spheres, not the real voxel volume (§F1); (b) fires affect only the
*reachability* model, never LOS; (c) no pitch, so vertical blind spots/ramps are approximated; (d) `target_height` is a
single offset — no hitbox silhouette (contrast CS2FOW, §B4); (e) doors/breakables ignored; (f) smoke placement is the
caller's job (you must derive it from the demo's grenade data).

### B3. CS2DemoKit (`CS2DemoKit.Analysis.Visibility`) — **Demonstrated**, second implementation

**What it does** | .NET 10 libraries for CS2 demos; `CS2DemoKit.Analysis` contains a rule engine **and a 3D
line-of-sight engine**. Its headline capability is `enemy_spotted`: "the rising edge where one player first comes into
view of another. **Nothing on the wire says so; it is recomputed from baked map collision geometry.**"
`VisibilityEngine.Load(bakePath)`; bakes are located via `CollisionAssetLocator` reading `CS2DEMOKIT_COLLISION_DIR`
(`<dir>/<map>.tris` or `<dir>/<map>/collision.tris`). Notably: leaving `VisibilityEngine` null makes the capability
*unavailable* (rules subscribing to `enemy_spotted` silently never fire) rather than silently degrading — good design.
**Verified how** | README read; 116 commits, last commit **2026-09-25** (0.13.0); MIT; `net10.0`; 1★ (niche/hobby,
but dense and test-heavy: commits like "make the ray differential able to fail, and the bakes runnable in CI", "stop an
infinite ray direction walking off the traversal stack", "four ways a shot context reported a number it had not
measured").
**Open/closed + license** | MIT, open — but **the collision bakes ship out-of-band** ("the geometry is Valve-derived
and large, and ships out of band"), so you must bake yourself (the `tools/` and `scripts/` dirs plus CI suggest a
reproducible bake step).
**Linux compat** | .NET 10 → cross-platform in principle; not verified on Linux.
**Reusability** | **Integrate / mine for design.** Strongest *conceptual* contribution: `enemy_spotted` as a derived
event, and explicit "capability unavailable vs silently wrong" semantics. Its collision geometry source is the same
`world_physics` route as awpy-data.
**Unsolved problems** | Valve-derived bakes not redistributable → every consumer bakes locally; .tris format is its own
convention (no cross-project compatibility with `AWMH`).

### B4. CS2FOW (`karola3vax/CS2FOW`) — the strongest *demonstration*, now **closed**

**What it does** | Server-side anti-wallhack (Metamod:Source plugin) that stops the server *sending* enemy positions
when walls or smoke fully hide them. Claims (and shows GIFs for) Ancient/Cache/Dust2-Long/Dust2-B/Mirage-A.
**Verified how (primary)** | README read directly. Concrete, checkable technical claims:
- **Bake**: "the first time a map loads, CS2FOW makes a quick 3D copy of its walls (a 'bake')"; the baker turns map
  walls into a **BVH8** file; bundled `Source2Viewer-CLI` is invoked from `game/csgo/tools/vrf/linux64/` →
  it uses VRF to get the physics geometry, then converts.
- **Smoke**: "CS2FOW copies the game's live smoke shape, which is stored as **a 3D grid of tiny boxes called voxels**.
  That lets it follow changing edges, overlapping smokes, growth, fading, and holes opened by grenades." (Independent
  corroboration of the voxel model in §F1.)
- **Hitbox fidelity**: "checks Valve's **nineteen animated hitbox capsules** as complete three-dimensional volumes,
  plus the muzzle of the held weapon", sampling "eye, shoulders, above eye, and feet", with an extra point following
  movement direction, ping-scaled reach, and a short visibility hold to prevent flicker.
- **Performance/architecture**: BVH8 traced by a background worker; the server's `CheckTransmit` hook only consumes a
  finished yes/no. AVX required.
- **Safety**: fail-open ("would rather show too much"); map-file CRC+size fingerprint invalidates stale bakes; gamedata
  (offsets) matched by size+CRC32 and refuses to run on unknown builds.
- **Known gaps (author-stated)**: "Doors, breakable objects, and moving props **do not block sight yet**."
**Maintenance status** | **Repo archived by the owner on 2026-10-06**; "This version is no longer maintained";
development moved closed source (karola3vax.com, 7-day trial). Author's stated reasons: account access problems,
code copied and resold, cheat devs reading detection code, update treadmill. Project was 298 commits, MIT at the time
of archiving.
**Consequence for us** | The **technique** is proven and usable; the **code** is no longer obtainable from the public
repo. Treat as: *Demonstrated feasibility + read-only reference*, not a dependency.
**Unsolved problems** | doors/breakables/moving props; smoke voxel decode is not in the archived docs; AVX + gamedata
coupling; and it is a *server transmit filter*, so it answers "what must this client see" (conservative), not "what did
this player actually see".

### B4b. Adjacent implementations covered by other slices (avoid double-counting)

Two further CS2 LOS implementations live in the *viewer* slice (`05-viewers-2d.md`) rather than here, and are counted
once, there: **`skkwowee/cs2-demo-viewer`** (radar-pixel raycasting + wall-clipped vision cones, MIT, hobby-scale —
16 commits; it also consumes a `map-data.json`-shaped transform table and `cs2-tools` to generate viewer data) and
**`Starfie1d1272/cs2-demo-analysis-kit` / DAK Studio** (a second independent LOS implementation). Their existence
strengthens the "LOS from map geometry is table stakes in this ecosystem" conclusion; their *formats* are again their
own (radar-space or app-local), reinforcing the format-fragmentation note in Cross-cutting.

### B5. `njyeung/CS2FOW-pvs` — **Experimental** PVS accelerator, and the key `vvis` claim

**What it does** | Fork of CS2FOW whose entire purpose is a PVS pre-pass before BVH8 traversal.
**Verified how** | Fork README, quoted verbatim: *"This is a fork of CS2FOW. **Although PVS is no longer used in CS2, its
data is still available in the `world_visibility.vvis`.** The goal is to use PVS alongside the already existing BVH8
system as an optimization. If a target's clusters do not intersect the recipient's visible clusters, we can fall-through
early and skip the BVH8 traversal."*
**Assessment** | This is a *design intent*, not a demonstrated result (267 commits, 3★, no benchmark published).
Two distinct claims: (i) `world_visibility.vvis` exists and carries clusters — **Demonstrated** (see B6);
(ii) CS2 no longer uses PVS at runtime — a community assertion, consistent with CS2's trace/BVH8-based visibility but
in tension with VRF's "the viewer culls a map with its world visibility (vvis_c) the way the game's engine does".
Read as: the *resource* exists and is engine-shaped; its role has changed. Class: **Plausible-untested**.

### B6. `world_visibility.vvis` / VRF `IWorldVisibility` — the Source 2 PVS analogue

**What it is** | Source 2's compiled world-visibility resource (CS2 path *convention*:
`maps/<map>/world_visibility.vvis_c`, uncompiled `.vvis`). VRF's `ResourceType` enum contains
`[Extension("vvis")] WorldVisibility`, so this is a first-class parsed type — not a rumour.
**What it exposes (verified API page)** | `IWorldVisibility`: `ClusterCount`, `ClusterBitfieldWordCount`,
`HasVisibilityData`, `MinBounds`/`MaxBounds` (visibility volume), `SunVisibility` (row of clusters sunlight reaches);
methods `BuildClusterChildBounds()`, **`GetClusterForPosition(Vector3)`**,
**`GetVisClustersForBox(min,max,Span<uint>)`** ("leaves it empty when the box only reaches solid space"),
**`GetVisibilityRowForPoint(Vector3)`** ("the visibility row seen from a point, or an empty row when there is none to
cull with" — i.e. rows are bitfields over clusters). Related type `ValveResourceFormat.Blocks.BspVoxelVisibility.Cluster`.
**VRF format-support page (verified)** | `vvis | World Visibility | View: 3D | Dump: yes | Decompiles/exports to: -`
and: "The viewer culls a map with its world visibility (`vvis_c`) the way the game's engine does." Two stated
non-uses: older *region box tree* layout (Dota 2 only, not parsed), and "Two cluster octrees — visibility with two
clusters or fewer culls nothing, as in the game."
**Feasibility for us** | **Research-supported, valuable but unproven for player LOS.** Clusters are a
*coarse, conservative, rendering-oriented* structure: `GetVisClustersForBox` gives a spatial index, and
`GetVisibilityRowForPoint` gives cluster-to-cluster visibility rows. You could use it to prune
player-pair candidate sets before BVH traces. Nobody (publicly) has validated cluster-level PVS against real
player-visible/not-visible outcomes in CS2, and it cannot express "the head is exposed but the body is not".
**Caveat** | VRF gives no `.vvis` *export*; using it means either C# (NuGet) in your pipeline or porting the block
parser. That's real work.
**Contrast with CS:GO** | Source 1's PVS/visleaves came *out of the `.bsp`* (`bsp_tool.py`,
`snake-biscuits/bsp_tool`, GPL-3.0, 2,023 commits, last commit **2026-09-23**, stable 0.7.0 Aug 2026). Its
`SUPPORTED_GAMES.md` lists **CS:GO (sdk_2013) and no CS2** — and CS2 has no `.bsp` maps at all, so the entire
`bsp_tool` / `visleaves` route is **Infeasible** for CS2 map geometry. Do not budget for it.

### B7. Nav-mesh portals as a LOS approximation — assessment

Portals (nav area connections) tell you *walkability*, not *sight*. Cases where they are outright wrong: bridges over
tunnels (connected in nav, mutually invisible), railings/windows (visually permeable, not walkable or vice versa),
one-way drops, and any elevated sightline over a low wall. **Class: Infeasible as a primary LOS model.** They *are*
legitimate as (a) an area partition for aggregation, (b) a coarse "could plausibly interact soon" filter, (c) the
reachability model in awpy's `map_control` (where they are used for exactly the right thing — travel distance).
awpy's own split (nav → movement, collision mesh → sight) is the correct architecture and awpy-data's README states it
explicitly.

### B8. Fog-of-war reconstruction — feasibility verdict

> **Verdict: DEMONSTRATED** (for geometry-reconstructed visibility at player/tick granularity on CS2 maps), with
> well-characterised error bars. It is **not** a reproduction of what the client rendered.

Evidence, strongest first:
1. **awpy**: `VisibilityChecker` (BVH over `AWMH` mesh) + `map_control` (raycast/vision/reachability, smoke spheres,
   flash blinding, per-area labels) — code and docs read; ships wheels; tracks CS2 builds; last commit today.
2. **CS2DemoKit**: `enemy_spotted` recomputed from baked collision geometry, with a documented asset convention and
   CI-run bakes.
3. **CS2FOW**: shipped, demonstrated on multiple maps, includes smoke-voxel occlusion, hitbox-capsule volume tests
   and multi-point observer sampling — i.e. an existence proof that this is *production-feasible* on a live server
   (BVH8 + background thread + `CheckTransmit`), with doors/breakables explicitly out of scope.
4. **awpy-data** demonstrates the *asset half* is solved and version-pinned, removing the "where does the geometry
   come from" risk that dominates most attempts.

Known, quantified-in-kind limitations (all author- or source-stated): decimation shifts surfaces ≤1 grid cell and can
open pinholes (awpy-data claims <0.1% LOS flips on Inferno at an 8-unit grid); occluder filtering is heuristic
(player clips/sky/glass/windows dropped); static-only (no doors/breakables); no bullet penetration; smokes modelled as
spheres in awpy (voxels only in CS2FOW); fires do not block LOS; no pitch in the FOV test; `target_height` is a single
offset rather than a hitbox silhouette; demo positions are feet, not eyes; and "was actually rendered visible" ground
truth does not exist publicly, so *calibration* is the open problem, not *capability*.

Recommended architecture (mirrors the two mature implementations):
```
demo (awpy) ──► per-tick player state (pos, yaw, health, blind, smoke/fire entities)
awpy-data ───► collision .mesh ──► BVH ──► segment occlusion
awpy-data ───► .nav ──► area id / centroid / neighbours ──► aggregation + floors
         └────► radar png + map_data.json ──► 2D overlay
optional: vvis clusters (VRF/C#) ──► candidate pruning
optional: smoke voxel volume (demo) or sphere (awpy defaults)
```

---

## C. Radar images and world→radar coordinate systems

### C1. The overview (`<map>.txt`) format — **Demonstrated**, primary source read

**Where it lives** | Inside `pak01_dir.vpk` at **`resource/overviews/<map>.txt`** — verified by listing
`game/csgo/pak01_dir/resource/overviews/` in SteamTracking/GameTracking-CS2 (23 files incl. `de_dust2.txt`,
`de_nuke.txt`, `de_cache.txt`, `rush_001.txt`, `workshop_preview.txt`) and by reading two of them raw.

**Format (KV1 text) — verified examples**
`de_mirage.txt` (from `2mlml/cs2-radar-images`, and matching GameTracking's own values):
```
"de_mirage"
{
    "material" "overviews/de_mirage"   // texture file
    "pos_x" "-3230"                    // X coordinate
    "pos_y" "1713"                     // Y coordinate
    "scale" "5.00"                     // scale used when taking the screenshot
    "rotate" "0"                       // map was rotated by 90 degrees in image editor
    "zoom" "0"                         // optimal zoom factor if map is shown in full size
    "CTSpawn_x" "0.28" "CTSpawn_y" "0.70"
    "TSpawn_x" "0.87"  "TSpawn_y" "0.36"
    "bombA_x" "0.54"   "bombA_y" "0.76"
    "bombB_x" "0.23"   "bombB_y" "0.28"
    "inset_left" "0.135" "inset_top" "0.08" "inset_right" "0.105" "inset_bottom" "0.08"
}
```
`de_nuke.txt` (raw, GameTracking) — **the multi-level mechanism**:
```
// HLTV overview description file for de_nuke.bsp
"de_nuke"
{
    "material" "overviews/de_nuke"
    "pos_x" "-3453"  "pos_y" "2887"  "scale" "7"
    "verticalsections"
    {
        "default" { "AltitudeMax" "10000"  "AltitudeMin" "-495" }
        "lower"   { "AltitudeMax" "-495"   "AltitudeMin" "-10000" }   // i.e. de_nuke_lower_radar
    }
    "CTSpawn_x" "0.82" ... "bombB_x" "0.58" ... "inset_*" ...
}
```
Notes that matter: (a) the spawn/bomb values are **already-normalised image coordinates** (0..1), not world units —
do not run them through the transform; (b) `rotate` and `zoom` are **optional** — `de_nuke`, `de_inferno`,
`de_train`, `de_anubis`, `ar_shoots`, `cs_office` ship without `rotate`; **assume defaults**; (c) `verticalsections`
gives `AltitudeMax`/`AltitudeMin` bands in Hammer units; the *same* world→pixel transform applies to both images,
and you pick the image by the player's `z`; (d) the file's own comment still says `.bsp` — legacy text.

**Transform (standard, matches awpy + community implementations)**
```
pixel_x = (world_x - pos_x) / scale
pixel_y = (pos_y - world_y) / scale          // Y sign flips: world Y up, image Y down
```
Inverse: `world_x = pos_x + pixel_x*scale`, `world_y = pos_y - pixel_y*scale`. Image is conventionally 1024×1024
(use the actual texture size if you regenerate). `rotate` (when present, 90° increments) is applied to the computed
pixel around the image centre; direction ambiguity is a documented community wart — validate per map.

### C2. Coordinator/consumer implementations

- **awpy-data** turns every overview into `map_data.json` (`pos_x,pos_y,scale,rotate,zoom`, `verticalsections`) — a
  tiny KV1 parser (`_tokenize` + `parse_kv`) written by hand, and it notes "The parser assumes legacy KV1; add a branch
  if CS2 emits KV3." Accessors: `awpy.data.map_data()["de_inferno"]`, `data.radar_path("de_nuke", lower=True)`.
- **CS2OpenDev-Docs `/maps/`** publishes a per-build **table of all 22 maps with radar metadata** (build `25218825`,
  Steam date 2026-09-09), incl. `material`, `pos_x/pos_y/rotate/scale/zoom`, spawns and bombsites. Verified values
  cross-check awpy/mirage/nuke: `de_mirage` `pos_x -3230 pos_y 1713 rotate 0 scale 5.00`; `de_nuke`
  `pos_x -3453 pos_y 2887 scale 7` (rotate `-`); `de_dust2` `rotate 1 scale 4.4 zoom 1.1` and material
  `overviews/de_dust2_v2`; `de_cache` material `overviews/de_cache_radar`; `de_vertigo` `overviews/de_vertigo_radar`.
  This is an excellent automated cross-check for any hand-rolled table.
- **CS2OpenDev-SchemaTracker** also emits `map_overviews.json` per build, sourced from `resource/overviews/*.txt` KV1
  (see D/E) — machine-readable, per-build, MIT.

### C3. Where radar images come from

`<map>_radar_psd.vtex_c` (awpy-data's claim; consistent with radar `.vtex_c` in `pak01`) → decompiled to PNG by
`Source2Viewer-CLI`. Multi-level maps additionally have `<map>_lower.png` (Nuke, Vertigo, Train per awpy-data README;
`2mlml/cs2-radar-images` shows `de_nuke_lower.png`, `de_vertigo_lower.png`, `de_train_lower.png`,
`ar_baggage_lower.png`, plus `de_jura_higher1/lower1`, `de_palais_higher1/higher2`).
Community redistributions exist (`2mlml/cs2-radar-images`: PNGs + the `.txt` configs, 6 commits, **no license file**).
**Class: Demonstrated** that extraction works; path string itself is author-claimed (the `RADAR_VTEX` constant).

### C4. Licensing of radar images / map assets — treat as "not licensed"

**Findings** | (a) awpy-data's README devotes a section to this: scripts MIT, but "**the game assets … are the property
of Valve Corporation. They are not owned by this project and remain subject to Valve's copyright and terms.** …
Redistributing such assets for community tooling is long-established practice (as the original Awpy did), but they
remain Valve's." Its own design keeps the repo asset-free and generates assets in CI/from your install.
(b) The **Steam Subscriber Agreement** restricts selling/licensing/commercially exploiting reproductions of content
and only grants personal use; the **CS2 Workshop FAQ** is restrictive about third-party IP in submissions.
(c) `karola3vax/CS2FOW` ships a `DATA_NOTICE` file alongside `LICENSE` — i.e. the project explicitly separates
"code license" from "Valve-derived data", the same pattern CS2DemoKit uses (bakes "ship out of band" / are
`CS2DEMOKIT_COLLISION_DIR`-located rather than bundled).
**Practical guidance** | Mirror awpy-data: **ship the extractor, not the assets** (or ship an installer that reads the
user's own CS2 install / takes `--cs2-dir`). If you must cache assets server-side, keep them out of the distributed
repo and keep the provenance/`ClientVersion` recorded. Avoid third-party logos/branding. This is an engineering-risk
note, not legal advice.
**Class**: Research-supported (policy/contract reading), with no explicit Valve grant found.

---

## D. `.vpk` parsing and Source 2 asset tooling

| Tool | What it does | CS2/VPK support (verified how) | Maintenance (Oct 2026) | License | Linux | Verdict |
|---|---|---|---|---|---|---|
| **Source2Viewer / ValveResourceFormat (VRF)** | Parser+decompiler+exporter for Source 2 resources; GUI + `Source2Viewer-CLI`. Reads/creates/edits VPK, decompiles `.vtex_c`→PNG, `.vmdl_c`→glTF, `.vmap_c`→`.vmap`, **nav→GLB**, parses `vvis`, and dumps KV3/entities. | README + `docs/guides/command-line.md` + `format-support.html` read. CLI flags verified verbatim: `-i`, `--vpk_list/-l`, `--vpk_dir`, `-e/--vpk_extensions`, `-f/--vpk_filepath`, `-d/--vpk_decompile`, `-o`, `-q`, `--gltf_export_format`, `--gltf_export_materials`, `--vpk_cache`, `--vpk_verify`, `--vpk_create`, `--kv_flatten`; `-i steam:730/game/csgo/pak01_dir.vpk` and `vpk:steam:730/...:<path>` input forms. **Args explicitly not stable.** | **Very active** — 7,097 commits, last commit 2026-10-14, release **20.0 (2026-08-17)**, 2.5k★ | MIT (except `Tests/Files`) | **Yes** (self-contained CLI for Win/Linux/macOS) | **Integrate** (this is the extractor engine) |
| **ValvePak** | VPK read/write library split out of VRF | Linked from VRF format-support page as the VPK handler | Same org as VRF | MIT | Yes (.NET) | Integrate if you write C# |
| **`ValvePython/vpk`** | Python read/list/extract + basic create + CLI | PyPI 1.4.0 · **MIT** · 2.3K weekly downloads; README states "**Multi archive paks are not yet supported**" and it's py2.7/py3.4-era code | Release 2021-12; repo activity last seen ~2023 | MIT | Yes (pure Python) | **Reuse with caution** — great for simple/older VPKs, risky for CS2's `pak01_dir.vpk` + numbered chunks |
| **`source-vpk` (Rust)** | Pure-Rust VPK v1/v2 reader | docs.rs **0.6.0 (2026-10-12)**: v1+v2 directory/entry reading, preload, dir-embedded data, numbered archives, entry CRC32, v2 dir MD5; writes "Planned"; v54 compression "Not Planned". MIT | New (0.1.0 on 2026-09-06 → 0.6.0 on 2026-10-12): fast-moving, young | MIT | Yes | **Reuse** for Rust services; pin versions |
| **`vpk-tools` (Node/Bun)** | VPK reader **and writer**, CLI, async API | README: full v1/v2, multi-chunk (`pak01_dir.vpk`+chunks), preload, dir-embedded, per-file CRC32 + v2 tree/archive/whole-file MD5, `readFileRange`/streams, RSA signing "same layout and algorithm as Valve's vpk.exe", diff by CRC; **tested against a real CS2 `pak01_dir.vpk` pulled from Steam** | 10 commits, 2★; README targets CS2/server tooling; npm badge shows 1.2.0-era activity | MIT | Yes | **Reuse** (best JS option) or ignore if your stack is Python/Rust |
| **VPKEdit** | CLI+GUI pack-file toolkit (`vpkeditcli`) | README **read verbatim**: "**This application targets GoldSrc and Source 1, and will not parse any Source 2 filetypes.**" Format table lists `VPK — Valve PacK file (Source Engine)`. Has a "consider Source 2 Viewer instead" note. 1,111 commits | Maintained (release line 5.0.0-beta.4 per releases page) | MIT | **Yes** (Arch/Debian/Fedora/NixOS/standalone) | **Ignore for CS2 assets**; fine for Source 1 VPKs (e.g. CS:GO-era work) |
| **HLLib** | Classic C++ HLLib for GCF/VPK | Not verified in this pass; long-standing but Source-1-era | Not re-verified | — | — | Ignore (superseded) |
| **`eikendev/cs2-extract`** | Makefile+podman wrapper: `vpkedit` unpack → VRF decode | README read: stage 1 `vpkedit` in fedora, stage 2 VRF in dotnet; `make tree` uses `vpkeditcli --file-tree`; `EXTRACT_PATH` selectable; needs `pak01_dir.vpk` **plus all chunks** | 3 commits, 0★, no license file declared → personal tool | — | Yes (podman) | Ignore as a dependency; **useful recipe** |

**Key distinction to keep in mind** | Reading a VPK gives you *bytes* of `.vtex_c`/`.vmdl_c`/`.vmap_c`. Only VRF
decompiles those into PNG/glTF/KV3. Any CS2 map pipeline needs both a VPK reader *and* VRF.

---

## E. Decompilers, map geometry capture, published triangulated CS2 geometry

### E1. VRF `vmap` decompile + glTF map export — **Demonstrated**

**What it does** | `Source2Viewer-CLI -i "maps/<map>.vpk" --vpk_filepath "maps/<map>.vmap_c" -d -o out` → Hammer
`.vmap`; `--gltf_export_format gltf|glb` (+`--gltf_export_materials`) → map geometry/props/textures.
**Verified limits (format-support page, read verbatim)** | Reconstructs all entity lumps with I/O, welds world render
geometry back into per-material Hammer meshes (near-coplanar tri pairs merged back to quads), static props, overlays,
per-surface-property physics geometry for collision with no render mesh. **Cannot recover**: prefab boundaries, group
names, overlay projection params (back-projected approximation), per-face lightmap scale, mesh subdivision levels,
per-light "No Shadow" flag. **Not implemented**: external reference meshes for welded geometry, clutter, physics
spheres/capsules → Hammer geometry, automatic 3D skybox bundling. glTF map exports: only `light_environment` becomes
a light, entity-only entities skipped, baked lighting not exported. **glb > 2 GB must be `.gltf`.**
Also: hitboxes are **not** exported to glTF ("glTF has no collision volume concept"); joints export for models but
joint motors/`m_constraints2` do not; surface properties are resolved **by name only — "their physical values
(friction, density, sounds) are not consumed or exported"**.
**Linux** | Yes.
**Verdict** | **Integrate** (the only mature Source 2 map decompiler).

### E2. awpy-data `geometry.zip` — published, triangulated, version-matched CS2 collision geometry

**What it is** | `<map>.mesh` = welded, occluder-filtered, decimated triangle soup in `AWMH` (see A1). This is, to my
knowledge after searching, **the only openly published, per-build, all-maps triangulated CS2 geometry specifically
prepared for LOS** — and unlike VRF's full-textured glTF exports it is small (Inferno ~4 MB) and directly loadable.
Intermediate `<map>.glb` (fuller, `--no-decimate` option) is also produced.
**Verdict** | **Reuse.** Adjust the occluder filter (`DROP_SUBSTRINGS`) and/or disable decimation for your own fidelity
needs; the pipeline supports `--no-decimate` and `--grid`.

### E3. `itzlaith/cs2-phys-extractor`

**Claimed** | Windows/.NET tool scanning official **and Workshop** map VPKs, extracting `world_physics.vmdl_c`
collision as `.tri` meshes and `.vphys`; batch processing.
**Verified how** | Lead from search only; **not** verified by me (repo page not opened). Class: **Plausible-untested**.
**Verdict** | Mention-only; awpy-data covers the same ground with a documented format and Linux support.

### E4. `Read1dno/ExternalAutoWallCS2` — collision extraction **+ penetration simulation**

**What it does / verified how (README read raw)** | "implements an external AutoWall for CS2. It extracts up-to-date
collision geometry **and material data** from Source 2 `.vpk` files, builds a BVH for fast ray-tracing, and computes
bullet penetration damage using real material modifiers." Verified details: parses `.vphys`/`.phys` via a `vmdll`
module; reads `m_collisionAttributes`, `m_meshes`, `m_hulls`; converts blobs to `TriangleCombined`; BVH splits along the
longest AABB axis until ≤4 triangles/node; **Möller–Trumbore** ray-triangle; per-material damage reduction with distance
falloff; **pybind11** binding exposing `handle_bullet_penetration()`; material parser reads `surfaceproperties.txt` and
`surfaceproperties_game.txt` for penetration modifiers.
**Author-stated limitations** | "Not a polished release—some maps exhibit malformed geometry and inverted triangles.
Development was time-consuming and is currently paused. Use this as a reference or starting point." License: MIT.
Windows/VS2022 + Python 3.10 only.
**Class** | **Experimental** (real, working-looking penetration maths; paused; geometry quality warnings).
**Verdict** | **Mine for the algorithm** (BVH8/Möller–Trumbore + surface modifiers + per-material damage reduction);
do not depend on the binary. Its "inverted triangles" warning is a useful signal that raw `world_physics` is messy.

### E5. BSPSource / Source 1 decompilers

Source 1 only. CS2 maps are `.vmap_c`; there is no `.bsp` to decompile. **Infeasible** for CS2 map geometry.

---

## F. Smokes, molotovs, wallbang, and audio occlusion — the published numeric models

### F1. Smoke — two models, both usable; the voxel one is more accurate

**Data source (verified on the schema, primary)** | `s2v.app/SchemaExplorer/cs2/client/C_SmokeGrenadeProjectile`
(read directly; the page links the canonical header in GameTracking-CS2 `DumpSource2/schemas/client/`). Fields declared
on the class: `m_nSmokeEffectTickBegin:int32`, `m_bDidSmokeEffect:bool`, `m_nRandomSeed:int32`,
`m_vSmokeColor:Vector`, **`m_vSmokeDetonationPos:VectorWS`**, **`m_VoxelFrameData: C_NetworkUtlVectorBase<uint8>`**
(with `on change OnSimulationChanged`), `m_nVoxelFrameDataSize:int32`, `m_nVoxelUpdate:int32`,
`m_nSmokeLightProbeRegen:uint8`, `m_bSmokeVolumeDataReceived:bool`, `m_bSmokeEffectSpawned:bool`.
**Interpretation** | CS2 smokes are a **networked voxel occupancy volume**, not a sphere: the demo carries the occupancy
data (`m_VoxelFrameData`, sized by `m_nVoxelFrameDataSize`, versioned by `m_nVoxelUpdate`) plus the detonation centre.
That means **exact smoke occlusion is reconstructible from the demo offline** — the hard part is decoding, not
sampling.

**Voxel model (two independent reverse-engineering efforts concur)**
- `osztenkurden/cs2parser` (Node/Bun CS2 demo *and live GOTV* parser) added "feat: added smoke voxel decoding"
  (commit `f3e672a`, 8 files, +591 lines). README text verified: `parser.smokes` returns `SmokeHelper[]`;
  each carries `detonationPos`, `hasVoxelData`, `voxels` (world positions), `gridVoxels` ("**Raw `[0, 32)` grid coords
  + per-voxel state bytes**"), `voxelCount`; and the transform is stated as verified:
  **`world = (grid − 16) · 20 + detonationPos`, per-axis signs `[−1, +1, +1]`**, with `decodeSmokeVoxelJournal`,
  `voxelToWorld`, `mortonEncode3` exported. Class: **Demonstrated** (code + integration tests: `smokeVoxel.test.ts`,
  `smoke-voxel.test.ts`).
- `memorin.app/mechanics/smoke-voxels` (page self-dated "Updated 2026-07-14", self-tiers its claims as VERIFIED):
  "32 × 32 × 32 voxel grid of **20-unit** cells — **640 units per side** — Morton (Z-order) coded … networked in the
  demo itself, not a sphere and not a particle cloud"; claims HE interaction constants: "only samples within **250 u**
  participate; the opened core is **200 u** with a smoothstep feather out to **240**; density in the hole drops to
  **2%**… recovery is `pow(smoothstep(0.5 s, 5 s), 1.8)` with the transient term reaching zero at **7 s**", plus "a
  five-entry circular buffer of HE blasts". Indepency caveat: this is a commercial site (memorin.app) with its own
  confidence tiers, and I could not verify its shader-decompile claims. Class: **Experimental / corroborating**
  (grid size 32 and cell size 20 independently match cs2parser's decoder).
- **CS2FOW** (B4) independently asserts the same model in shipping software: "the game's live smoke shape … is stored
  as a 3D grid of tiny boxes called voxels", and it tracks growth/fading/HE holes.

**The pragmatic model everyone actually ships (awpy)** | A **sphere**: `smoke_radius=144.0`,
`smoke_height=60.0` above the landing point, with `segment_hits_sphere(eye, target, center, radius)` — plus
`fire_radius=150.0` for molotovs in the reachability model. So **the widely-cited "144-unit smoke radius" is an
approximation used by awpy for LOS**, not a verified engine constant (the voxel volume is 640 u per side, i.e. a
~320 u half-extent if you were to bound a *deployed, fully-grown* smoke). If your analysis needs "is this exact
sightline cut right now", the voxel volume is materially better; if you need cheap area-level control, the 144 u sphere
is the established approximation and is what the ecosystem's numbers are calibrated against.

**Delivery/journey** | Trajectory comes from `player_blind`-independent sources: awpy exposes `grenades` (per-tick
thrown-grenade trajectories), `smokes` (one row per deployed smoke: position, thrower, `[start_tick,end_tick]`) and
`fires`. That is enough to place the sphere/voxel per tick without any vision modelling.

**Unsolved problems** | (a) the exact meaning of `m_nVoxelFrameDataSize` packing is not documented in the schema (the
decoders assume 32³); (b) voxel *growth/fade* timing is partially open (memorin explicitly lists "Smoke detonation
timing is not captured"); (c) voxel data is only complete once `m_bSmokeVolumeDataReceived` — early ticks of a smoke
need a fallback; (d) nobody has published a *validated* smoke-occlusion model against in-game screenshots.

### F2. Molotov / incendiary extents — **Demonstrated data source**

**Verified on the schema** | `s2v.app/SchemaExplorer/cs2/client/C_Inferno` (34,464 bytes; also exists as server
`CInferno`) exposes: **`m_firePositions: VectorWS[64]`**, **`m_fireParentPositions: VectorWS[64]`**,
`m_bFireIsBurning: bool[64]`, `m_BurnNormal: Vector[64]`, **`m_fireCount: int32`**, `m_lastFireCount`,
`m_nInfernoType`, `m_nFireLifetime: float32`, `m_nFireEffectTickBegin`, `m_bInPostEffectTime`,
`m_maxFireHalfWidth: float32`, **`m_maxFireHeight: float32`**, **`m_minBounds`/`m_maxBounds: VectorWS`**,
`m_blosCheck`/`m_nlosperiod` (an LOS-check cadence), plus particle snapshot handles.
**Why this matters** | Molotov geometry is **directly readable per tick** (up to 64 fire points with parent
positions, individual burning flags, plus width/height/bounds). You do not need to model fire spread — you can read
it. awpy already ships `fires` (one row per fire with `[start_tick,end_tick]`). The 150 u `fire_radius` in
awpy's reachability model is therefore a *coarse* simplification of data you actually have.
**Class** | Demonstrated (schema is generated from the shipped binaries by SchemaTracker; field offsets/types given).

### F3. Wallbang / penetration — data **and** algorithm are both available

- **Weapon parameters**: `scripts/weapons.vdata` (KV3, shipped; note the scripts dir listing shows `weapons.vdata`,
  and SchemaTracker reads `scripts/weapons.vdata_c`). SchemaTracker's README (verified) lists artifact
  **`weapon_vdata.json`** = "Per-weapon tuning: **damage, armor ratio, penetration**, the inaccuracy model, and the
  recoil seed the spray pattern is generated from". So `penetration`, `armor_ratio`, `range`, `range_modifier` are
  machine-readable per build — no need to hand-scrape.
  *Contrast*: CS:GO-era `items_game.txt` carried penetration; a grep of CS2's
  `scripts/items/items_game.txt` for "penetration" returned no matches, and SchemaTracker classifies
  `items_game.txt` as economy/item definitions (prefabs, paint kits, rarities), not ballistics. **Do not source
  penetration from `items_game.txt` in CS2.**
- **Surface/material side**: `scripts/surfaceproperties_game.txt`, `surfaceproperties_footsteps.txt`,
  `surfaceproperties_impact_effects.txt`, `surfaceproperties_steamaudio.txt` (all verified present);
  SchemaTracker exposes `surface_properties.json` = "Per-material physics and footstep/impact/acoustic mappings".
  VRF, however, warns it resolves surface properties **by name only** and does not consume/export their physical
  values — so parse the text/KV3 yourself for friction/penetration modifiers.
- **Algorithm**: `ExternalAutoWallCS2` (E4) implements the full chain (BVH + Möller–Trumbore + per-material damage
  reduction + distance falloff + armor + pen count) and binds it to Python. Old CS:GO `autowall.cpp` implementations
  exist but must not be assumed to match CS2.
**Class** | Weapon/surface data: Demonstrated. Penetration simulation: Experimental.
**Unsolved problems** | CS2's exact penetration formula is not published by Valve; the community formula is
reverse-engineered (and CS2 removed some CS:GO penetration nuances). Any wallbang model must be validated against
demo `player_hurt` outcomes (which give post-armor damage and hitgroup — a usable calibration signal).

### F4. Audio occlusion — real, geometry-based, and partially **baked**

**What it does (verified in the shipped build's own convar dump)** | I grepped
`GameTracking-CS2/DumpSource2/convars.txt` and confirmed the CS2 binary carries a full **Valve Steam Audio**
integration: `snd_steamaudio_enable_perspective_correction (archive release)`,
`snd_steamaudio_enable_pathing (cheat)`, `snd_steamaudio_pathing_order (1)`,
`snd_steamaudio_baked_occlusion_mode (0, cheat — "0: distance ratio only. 1: deviation only (1/r). 2: deviation only
(linear). 3: Mode 0 and Mode 1, 4: Mode 0 and Mode 2")`, `snd_steamaudio_baked_occlusion_pathing_deviation_slope`,
`..._pathing_exponent`, `..._reflection_factor`, `snd_steamaudio_load_occlusion_data true`,
`..._load_pathing_data true`, `..._load_materials_data true`, `..._load_reverb_data true`, `snd_steamaudio_num_rays
65536`, `snd_steamaudio_num_bounces 128`, `snd_steamaudio_num_diffuse_samples 2048`,
`snd_steamaudio_max_occlusion_samples 64` ("rays that can be traced for **volumetric occlusion**"),
`..._max_occlusion_samples`, `..._ir_duration`, `..._enable_occlusion_caching`,
`..._enable_pathing`, `..._invalid_path_length`, `snd_steamaudio_debug_cover_navmesh_probe_size_scale`,
`snd_steamaudio_enabe_append_probes_to_cover_navmesh` (sic), `snd_steamaudio_use_soundblocking_shapes_only`,
and reverb/HRTF/ambisonics controls.
**Baked-data class exists (verified source file)** | `DumpSource2/schemas/steamaudio/CSteamAudioBakedOcclusionData.h`
contains exactly:
```cpp
class CSteamAudioBakedOcclusionData
{
	SteamAudioCustomDataOcclusionSettings_t m_settings;
	CSteamAudioProbeData m_probes;
	CUtlVector< float32 > m_vecPathingRatio;
	CUtlVector< float32 > m_vecPathingDeviation;
	CUtlVector< float32 > m_vecReflectionEnergy;
};
```
i.e. **per-map baked occlusion is a probe-based structure** (probe positions/values + per-path deviation/reflection
energy) — matching the convars' "probes covering the nav mesh" language and VRF's nav-space probe tooling.
**Material inputs (verified file)** | `scripts/surfaceproperties_steamaudio.txt` (KV3 text) defines, for each surface
prop (`default_silent`, `default`, `solidmetal`, `metalgrate`, `dirt`, `carpet`, `upholstery`, `plaster`, `sheetrock`,
`rock`, `asphalt`, `cardboard`, `ceiling_tile`, `rubber`, …), three **11-band** coefficient arrays:
`scatteringCoefficients`, `absorptionCoefficients`, `transmissionCoefficients`. Example (`default`):
scattering ≈0.01 flat; absorption from 0.02 rising to 0.12; transmission ~0.015→0.001.
**Practical meaning for a coaching tool** | You can (a) replicate the *inputs* of CS2's own occlusion model
(geometry + per-surface absorption/transmission/scattering + Steam Audio's documented occlusion model from
ValveSoftware/steam-audio), (b) approximate with a single-ray "sound transmission" test using
`transmissionCoefficients`, or (c) attempt to lift the baked probe data. (c) is the only way to match the engine
exactly and is **Plausible-untested** (I did not locate the baked per-map files inside a real map VPK, and VRF does not
document a baked-occlusion parser — only `soundstacks/`, `soundevents/`, `vsndstck`/`vsndevts` resources).
**Honest framing** | "Sound occlusion in CS2 is real, geometry-driven and probe-baked, with per-material
transmission/absorption/scattering authored in the game files" = **Demonstrated**. "You can reproduce the engine's
per-sound occlusion value offline" = **Plausible-untested**. Simpler defensible approximations (audibility by
segment-occlusion + distance + surface transmission) are legitimate and can be validated against demo-derived
footstep/gunfire audibility heuristics.
**Unsolved problems** | probe data location/format; whether pathing is enabled in competitive configs
(`snd_steamaudio_enable_pathing` is `(cheat)`-flagged = not user-changeable, so you must take the default as truth);
HRTF/perspective correction is client-side and not in demos at all.

---

## G. Height, verticality and "which floor"

**Where heights live** | (1) **Nav areas**: every nav area has `centroid_z` + polygon corners → per-area floor height.
(2) **`nav_hulls_presets.vdata` / `nav_hulls.vdata`** define agent hulls (radius/height presets) used to generate nav
— usable to pick ray origins. (3) **Overview `verticalsections`** define altitude bands that select which radar image
to draw (C1). (4) `C_Inferno.m_minBounds/m_maxBounds` and `m_maxFireHeight` give 3D fire extents. (5) VRF exposes
`NavMeshHidingSpot`, `NavMeshLadder`, `NavMeshGenerationParams` (cell size/height, tile size, per-hull max climb/slope)
— the *generation* geometry, which tells you what the mesh considers traversable vertically.

**How to disambiguate floors** |
- awpy's `NavMesh.find_area((x,y,z))` **already solves this**: docs state that "when several areas cover the same
  `(x, y)` (a bridge over a tunnel, stacked levels), it returns the one whose height is closest to the point's `z`."
  Verified in the docs; the mechanism is standard nav-area containment + z-proximity. → **Reuse.**
- Radar: pick `<map>.png` vs `<map>_lower.png` from `verticalsections` by `z` (verified band values for Nuke:
  default `[-495, 10000]`, lower `[-10000, -495]`).
- CS2OpenDev-Docs' per-build map table gives the same transform fields, useful for regenerating your own table.

**Assessment** | Floor disambiguation is **Demonstrated-solvable** with nav z + altitude bands; it is *not* solvable
from the radar transform alone (X/Y only). Vertigo/Train/Nuke are the maps that need it (awpy-data ships
`_lower.png` for Nuke/Vertigo/Train; `2mlml/cs2-radar-images` also shows `de_jura`, `de_palais` multi-variant maps).
**Unsolved problems** | Multi-level *within one radar image* (stacked floors both inside the "upper" band) needs honest
per-area z and, ideally, the player's own `z` from the demo (which you have) — expect ambiguity on stairs/ramps and
when players jump; a `z`-hysteresis band (rather than a hard cut) is advisable.

---

## Comparison table (one row per item, verdict included)

| # | Item | Layer | CS2 verified how | Maintenance (Oct 2026) | License | Linux | Class | Verdict |
|---|---|---|---|---|---|---|---|---|
| A1 | **awpy-data** (nav/radar/geometry/map_data releases per ClientVersion) | Assets | README + format spec read; peer-verified release cadence (2000930, 2026-10-09) | 5 commits, last 2026-07-10, **daily CI** that gates on buildid | MIT (scripts) | Yes | Demonstrated | **REUSE** |
| A2 | **awpy** `NavMesh` (nav v36, find_area/find_path) | Nav | docs + Rust tree | Very active (last commit 2026-10-15) | MIT | Yes (wheels) | Demonstrated | **REUSE** |
| A3 | **VRF** `NavMesh`/`NavMeshFile` (nav v30–36, magic 0xFEEDFACE, nav→GLB) | Nav/format | Source read (`version < 30 \|\| > 36` throw; v36 fields) + format-support page | Very active (last commit 2026-10-14, rel 20.0 2026-08-17) | MIT | Yes | Demonstrated | **INTEGRATE** |
| A4 | **nav2json-rs** (Rust nav→JSON) | Nav | docs.rs 0.1.0 (2026-02-03), claims v30–35 | One release, dormant | MIT | Yes | Plausible-untested | **IGNORE** |
| A5 | **cs2-nav / cs2_meeting_points** (Rust+PyO3 nav+visibility utilities) | Nav/vis | docs.rs 0.3.18 (2025-07-21) + repo (637 commits, last 2026-10-08) | Alive, releases stale | MIT | Yes | Experimental | **INTEGRATE (2nd opinion)** |
| A6 | `nav_hulls_presets.vdata`, `nav_hulls.vdata`, `navlinks.vdata`, `pak01_dir/navplace.db` | Nav | Files present in GameTracking-CS2; one read raw | Tracks CS2 builds (last commit 2026-10-15) | Valve data | n/a | Demonstrated | **INTEGRATE** (hull sizes; callouts untested) |
| A7 | Source 1 nav parsers (navmesh-parser, gonav, nav v16) | Nav | n/a | — | — | — | **INFEASIBLE** for CS2 | **IGNORE** |
| B1 | **awpy `VisibilityChecker` + `geometry.rs`** (`AWMH`, BVH, `is_visible`) | Vis | **Rust source read** | Very active | MIT | Yes | **Demonstrated** | **REUSE** |
| B2 | **awpy `map_control`** (raycast/vision/reachability, `MapControlParams`) | Vis/FOW | **Docs + Rust source read** (params verbatim) | Very active | MIT | Yes | **Demonstrated** | **INTEGRATE (model semantics)** |
| B3 | **CS2DemoKit** `Analysis.Visibility` / `enemy_spotted` | Vis | README read; 116 commits | Last commit 2026-09-25; 1★; MIT; bakes out-of-band | MIT | .NET | Demonstrated | **INTEGRATE (design) / mine** |
| B4 | **CS2FOW** server-side anti-wallhack (BVH8, voxel smokes, hitbox capsules, `CheckTransmit`) | Vis/FOW | README read (detailed, checkable) | **ARCHIVED 2026-10-06**, moved closed-source | MIT (at archive) | Win/Linux, AVX | Demonstrated | **IGNORE as dependency; reference technique** |
| B5 | `njyeung/CS2FOW-pvs` (PVS pre-pass idea) | Vis | Fork README (verbatim quote) | 267 commits, 3★, no benchmark | MIT (inherited) | — | Experimental | **WATCH** |
| B6 | **`world_visibility.vvis`** + VRF `IWorldVisibility`/`BspVoxelVisibility` | Vis | `ResourceType` has `[Extension("vvis")]`; **API page read** (methods/properties); format-support page | With VRF (active) | MIT | Yes | Demonstrated (parse) / Research-supported (use) | **WATCH → INTEGRATE if you add pruning** |
| B6b | Source 1 BSP/PVS route (`bsp_tool.py`, visleaves) | Vis | `SUPPORTED_GAMES.md` = CS:GO only, no CS2 | bsp_tool active (last 2026-09-23) | GPL-3.0 | Yes | **INFEASIBLE** for CS2 | **IGNORE** |
| C1 | `<map>.txt` overview KV1 (`pos_x/pos_y/scale/rotate/zoom`, `verticalsections`) | Radar | **Two files read raw** + GameTracking path listing | Tracks CS2 builds | Valve data | n/a | Demonstrated | **REUSE** |
| C2 | `map_data.json` (awpy-data), `data.map_data()`; CS2OpenDev-Docs map table; SchemaTracker `map_overviews.json` | Radar | READMEs + page read; values cross-checked against C1 | Active | MIT | Yes | Demonstrated | **REUSE** |
| C3 | Radar PNG extraction (`<map>_radar_psd.vtex_c` → VRF → PNG; `_lower` variants) | Radar | README + community repo listing | Active (VRF) | Valve assets | Yes | Demonstrated | **INTEGRATE** |
| C4 | Radar/map asset **licensing** | Legal | awpy-data licensing section + Steam SSA + Workshop FAQ | n/a | — | n/a | Research-supported | **Ship extractor, not assets** |
| D1 | **Source2Viewer-CLI** (VRF) | Tooling | `command-line.md` read (all flags) | Very active | MIT | Yes | Demonstrated | **INTEGRATE** |
| D2 | `ValvePython/vpk` | Tooling | PyPI page read (1.4.0, MIT, "multi archive paks not yet supported") | Stale (2021) | MIT | Yes | Demonstrated (legacy) | **IGNORE** for CS2 chunked VPKs |
| D3 | `source-vpk` (Rust) | Tooling | docs.rs 0.6.0 (2026-10-12) support table | Young, moving fast | MIT | Yes | Demonstrated | **REUSE** (Rust only) |
| D4 | `vpk-tools` (Node/Bun, read+write+verify+sign) | Tooling | README read; tested against real CS2 `pak01_dir.vpk` | New (10 commits) | MIT | Yes | Demonstrated | **REUSE** (JS only) |
| D5 | **VPKEdit** | Tooling | README read: "will not parse any Source 2 filetypes" | Maintained | MIT | Yes | n/a for CS2 assets | **IGNORE** (CS2) |
| D6 | `HLLib` | Tooling | Not verified | — | — | — | Research-supported (stale) | **IGNORE** |
| D7 | `eikendev/cs2-extract` | Tooling | README read (podman+vpkedit+VRF recipe) | 3 commits | none declared | Yes | Experimental | **IGNORE as dep; reuse recipe** |
| E1 | **VRF `vmap` decompile + glTF map export** | Decompiler | format-support + exporting-maps read (limits listed) | Very active | MIT | Yes | Demonstrated | **INTEGRATE** |
| E2 | **awpy-data `geometry.zip`** (AWMH, per-build, all maps) | Geometry | README (format spec verbatim) | Daily CI | MIT scripts | Yes | Demonstrated | **REUSE** |
| E3 | `itzlaith/cs2-phys-extractor` (.tri/.vphys, Workshop) | Geometry | Not verified | Unknown | Unknown | Windows/.NET | Plausible-untested | **IGNORE** |
| E4 | `ExternalAutoWallCS2` (BVH + Möller–Trumbore + material modifiers + pybind11) | Geometry/pen | README read raw; author warns malformed/inverted triangles; paused | Paused | MIT | Windows/VS2022 | Experimental | **MINE for algorithm** |
| E5 | BSPSource / Source 1 decompilers | Decompiler | n/a | — | — | — | **INFEASIBLE** for CS2 | **IGNORE** |
| F1 | Smoke: `C_SmokeGrenadeProjectile.m_VoxelFrameData` (+32³/20 u/`(g−16)·20+det` decode; HE hole constants) | Model | **Schema page read**; cs2parser commit + README read; memorin + CS2FOW corroborate | cs2parser active (commit 2026-0x); memorin self-dated 2026-07-14 | MIT (cs2parser) / proprietary (memorin) | Yes | Demonstrated (data) / Experimental (constants) | **INTEGRATE (voxels) with sphere fallback** |
| F1b | Smoke: awpy spherical model (`smoke_radius=144`, `smoke_height=60`) | Model | Rust source read | Active | MIT | Yes | Demonstrated | **REUSE as cheap default** |
| F2 | Molotov: `C_Inferno.m_firePositions[64]` etc. | Model | **Schema page read** (fields/offsets) | — | — | — | Demonstrated | **REUSE (read, don't model)** |
| F3 | Penetration: `weapons.vdata` → SchemaTracker `weapon_vdata.json` + surfaceproperties* + autowall algorithm | Model | SchemaTracker README read (`weapon_vdata.json` = damage/armor ratio/penetration); `items_game.txt` grep for "penetration" = no match | SchemaTracker 99 commits | MIT | Yes (JSON) | Demonstrated (data) / Experimental (sim) | **INTEGRATE data; validate formula** |
| F4 | Audio: Steam Audio convars + `surfaceproperties_steamaudio.txt` (11-band scattering/absorption/transmission) + `CSteamAudioBakedOcclusionData` | Model | **convar dump grepped**, two files read raw | Tracks builds | Valve data | n/a | Demonstrated (exists) / Plausible-untested (reproduce) | **INTEGRATE inputs; approximate** |
| G | Floors: nav `centroid_z` + `find_area` z-closest + overview `verticalsections` + nav hull data | Verticality | docs + Rust tree + nuke overview read | Active | MIT | Yes | Demonstrated | **REUSE** |

---

## Per-item reuse verdict summary (the short list)

**Reuse directly (build on it):** awpy-data (assets) · awpy `NavMesh` + `VisibilityChecker` + `map_control` ·
`map_data.json`/overview KV1 · `C_Inferno` fire data · `vvis` (if you need pruning, via VRF/C#).

**Integrate (use as engine, wrap it):** Source2Viewer-CLI/VRF (extraction, nav→GLB, vmap/glTF, `vvis` parsing) ·
CS2OpenDev-SchemaTracker (per-build JSON: `weapon_vdata.json`, `surface_properties.json`, `map_overviews.json`,
`entity_schema.json`) · `source-vpk` or `vpk-tools` if your services are Rust/JS.

**Mine for design, don't depend on:** CS2DemoKit (`enemy_spotted`, capability-unavailable semantics) ·
CS2FOW (BVH8 + hitbox-capsule volumes + multi-point observers + visibility hold + fail-open; closed source) ·
`ExternalAutoWallCS2` (penetration maths).

**Watch:** `CS2FOW-pvs` (PVS-pruned BVH) · `cs2-nav`/`cs2_meeting_points` (published meeting-point pipeline).

**Ignore for CS2:** bsp_tool / BSPSource / Source 1 nav & PVS parsers · VPKEdit (Source 1 only) ·
`ValvePython/vpk` for chunked CS2 VPKs · `nav2json-rs` (v35 ceiling, dormant) · HLLib.

---

## Cross-cutting notes (duplication, gaps, and things nobody has solved)

**Duplicated work across the cluster / ecosystem**
1. **At least five independent collision-geometry-for-LOS pipelines** exist and are incompatible at the file-format
   level: awpy-data `AWMH` `.mesh`; CS2DemoKit `<map>.tris` (`CS2DEMOKIT_COLLISION_DIR`); CS2FOW `.bvh8` + `.json`;
   plus the two viewer-slice implementations (`cs2-demo-viewer` radar-space raycasting, DAK Studio). All of the ones
   we could inspect start from the same `world_physics.vmdl_c` glTF (VRF) and re-implement
   filter/weld/decimate. A shared, documented "CS2 occluder mesh" format would remove several codebases' worth of work.
   `ExternalAutoWallCS2` is effectively another (`.vphys` → `TriangleCombined` + `.bvh`).
2. **Three BVH implementations** that matter to us: awpy's Rust BVH (`LEAF_SIZE=4`, endpoint epsilon), CS2FOW's BVH8
   and CS2DemoKit's tracer. Nobody publishes BVH build/query benchmarks on equal meshes.
3. **Radar metadata is parsed at least four times**: awpy-data's hand KV1 parser → `map_data.json`;
   CS2OpenDev-SchemaTracker → `map_overviews.json`; CS2OpenDev-Docs → a docs table; plus countless per-app copies.
   Worth consuming one (SchemaTracker's is per-build and MIT) and diffing against awpy-data's.
4. **Smoke modelling is duplicated and inconsistent**: voxel volume (cs2parser decode, CS2FOW, memorin's shader
   port) vs sphere (awpy `smoke_radius=144`). Both are "correct" for their task but the ecosystem's numbers (e.g.
   lineup/blocking tools) mix them silently.
5. **Source 2 nav is implemented ≥4 times**: VRF (C#, authoritative), awpy (Rust, v36), nav2json-rs (Rust, ≤v35),
   cs2-nav (Rust). Plus `awpy`'s older Python nav (v2 docs still online) — beware stale doc versions when reading
   awpy tutorials: current awpy is a **Rust core behind a Polars Python API** (`crates/awpy-{python,proto,dev}`,
   `nav.rs`, `geometry.rs`, `map_control.rs`, `hitgroups.rs`), not the 2022 CS:GO-era Python/JSON library the
   ESTA paper (arXiv:2209.09861, Sept 2022) describes.

**Gaps nobody has closed (highest-value opportunities for us)**
1. **No ground-truth visibility dataset.** Every implementation is unvalidated against "was this player actually
   visible on screen". CS2DemoKit and CS2FOW both imply they self-tuned. A labelled set (e.g. death events where a
   player demonstrably *could not* have seen the killer, plus deliberately-engineered clear/occluded pairs —
   awpy-data claims two hand-checked Inferno sightlines) would be the single most valuable artefact in this space.
   *Note for the main agent:* this is the natural landing spot for a "calibration" workstream, and it pairs with the
   `DemoDataFogOfWar` slice.
2. **Doors, breakables and moving props are uniformly unmodelled.** CS2FOW states it plainly; awpy's docs say
   "static geometry"; nobody ships dynamic occluders. Demos do not obviously carry door state (untested here — worth a
   targeted check of `CFuncMoveLinear`/`func_door` entity presence in `.dem`).
3. **Eye vs feet.** All recorded positions are feet; awpy defaults `eye_height=64` / `crouch_eye_height=46` /
   `target_height=46`, and its docs flag "player positions are not eye positions". Crouch state and *rising/falling*
   are not in the default parameter set. CS2FOW goes further (19 hitbox capsules + muzzle origin) but that code is
   now closed. Nobody publishes hitbox/capsule geometry for CS2 players (VRF notes hitboxes are **not** exported to
   glTF, and `awpy/src/hitgroups.rs` only maps hitgroup **IDs to names**, not boxes).
4. **No bullet-penetration + LOS integration.** Penetration exists (weapon data + autowall code) and LOS exists
   (awpy/CS2DemoKit/CS2FOW), but no project combines them for "could this player have been hit through this wall".
   Wallbang analysis would need both plus `surfaceproperties` physical values, which VRF explicitly does not export.
5. **`vvis` is unharvested.** VRF can read it and exposes exactly the right queries (`GetClusterForPosition`,
   `GetVisClustersForBox`, `GetVisibilityRowForPoint`) — but no published CS2 project uses it for player LOS, and the
   only attempt (CS2FOW-pvs) is an unbenchmarked fork. Also unresolved: whether CS2's runtime uses it at all
   (fork README says no; VRF says its viewer culls "the way the game's engine does").
6. **Audio occlusion cannot currently match the engine.** The baked probe data structure is known
   (`CSteamAudioBakedOcclusionData`) and convar names describe its use, but nobody has published (a) where the baked
   file lives inside a map package, (b) a parser for it, or (c) a validation that a reimplementation matches in-game
   audibility. Surface coefficient tables are available, so an *approximation* is easy and an *exact replica* is not.
7. **Vertical/stacked-floor ambiguity inside one altitude band** (stairs, ramps, Nuke adjacent floors) is handled by
   z-closest nav lookups only; a hysteresis + player-z approach is untested.
8. **Asset licensing has no clean answer.** Every project's solution is "generate locally / ship out-of-band", which
   pushes work onto each consumer (and is exactly why awpy-data, CS2DemoKit and CS2FOW all do it). If our system is
   local-first, this is actually the *right* shape — but it means the map-asset pipeline must be a first-class,
   self-healing, `ClientVersion`-pinned component (awpy-data is the template), not a one-off script.

**Cross-slice links**
- `05-viewers-2d`: the radar transform (C1) and `map_data.json` (C2) are the inputs any 2D canvas needs; `_lower.png`
  + `verticalsections` is the multi-level contract. Parse the overview once and share it.
- `01-parsers-libs`: awpy's `data.py` (peer-verified: `DATA_REPO = "pnxenopoulos/awpy-data"`, `~/.awpy/<ClientVersion>/`,
  `AWPY_DATA_DIR`, and the "static geometry only, no smokes/doors/penetration, positions are not eyes" caveat) is the
  exact seam where this slice plugs in. No overlap in what we verified.
- `DemoDataFogOfWar`: our verdict **Demonstrated** should be reconciled with that slice's findings; the shared open
  problem is validation ground truth, not capability.

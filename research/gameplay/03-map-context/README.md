# Map Context — Positioning & Spatial Meaning in CS2 (03-map-context)

**Status:** research only — no code, config, schema, or test changes.
**Workspace:** `research/gameplay/03-map-context/` · entry point: this file.
**Date:** 2026-10-16. **Method:** source-grounded tactical research; every factual claim cites a source
actually opened 2026-10-15/16 (URL + what it evidences). Search snippets are leads, never evidence — the
one snippet-level item (donk Vertigo remark) is labeled weak.
**Dataset:** the project catalog holds 17 processed generations across exactly these five maps
(`de_ancient`×4, `de_dust2`×3, `de_inferno`×4, `de_train`×3, `de_vertigo`×3).

## The single thesis (all maps)

**Geometric proximity does not imply support. An unobstructed ray does not imply tactical availability.**

Support = shared lane + mutual sight + traversable trade path (≤~1 s) + favorable smoke/fire/utility state.
Availability = smoke/fire/flash-conditioned visibility + exit + objective fit — never a clear ray alone.
Every positional judgment in this workspace is therefore a **dependency vector** (timing, economy/utility,
alive players, opponent pressure, information held, team objective) — never a "correct positions" lookup.

## Map files

| Map | File | Pool (Oct 2026) | Evidence window | Core spatial truth |
|---|---|---|---|---|
| Ancient | [maps/ancient.md](maps/ancient.md) | ✅ Active | current (50/50; post-Aug-2025 Temple removal) | Cave↔B and Donut↔sites: proximity without fixing + route + clearing-order is nothing |
| Inferno | [maps/inferno.md](maps/inferno.md) | ✅ Active | current (banana/balcony reworks) | Pit/coffins metres from sites yet unsupportable; banana↔mid split by spawn-timing + walls |
| Dust2 | [maps/dust2.md](maps/dust2.md) | ✅ Active | current (pre/post Apr-2026 Xbox) | Long-A↔Tunnels/B radar-adjacent but 10.7 s apart; quantified timing gates on every entry |
| Train | [maps/train.md](maps/train.md) | ❌ Reserve (Jan 2025–Jan 2026) | frozen at Spring-Forward-2025 | Two yards, one spine, no mid; Underpass man 10 m away yet wall+bend unavailable; hut sees past Ramp smoke |
| Vertigo | [maps/vertigo.md](maps/vertigo.md) | ❌ Reserve (out since Jan 2025) | Mar–Apr 2024 + Dec 2024; thin | Verticality: stacked teammates 6 m apart support slower than 25 m on one level |

Annotated source catalog: [sources.md](sources.md).

## Pool currency (Oct 2026)

Active Duty (Season 5, from 2026-07-08): **Ancient / Anubis / Cache / Dust2 / Inferno / Mirage / Nuke**.
Reserve: Train, Vertigo, Warden, Stronghold, Alpine, Office, Italy.
Rotation trail: Dust2 +Apr-2024 (−Overpass) · Train +Jan-2025 (−Vertigo) · Overpass +Jul-2025 (−Anubis) ·
Anubis +Jan-2026 (−Train) · Cache +Jul-2026 (−Overpass).
**Do not encode "Train replaced Vertigo" as current** — superseded twice over.

Balance priors (Tier-1, regulation): Ancient 49.9% CT (685 maps) · Inferno 50.2% CT (702) · Dust2 51.1% CT
(2301 maps / 40368 rounds) · Train 55.7% CT at Austin Major 2025 (14 picks / 62 bans — CT-leaning, heavily
banned) · Vertigo 48.8% CT all-time vs 52.2% T May-2024 snapshot (window conflict — quote only with window).

## Cross-map comparison

### Which concepts generalize

1. **Support = angle × timing × utility-state × tradeability** — holds on all five maps; the negative training
   triads differ per map (Inferno pit/banana/apps; Train underpass/hut/Ivy; Vertigo stacked levels; Dust2
   Long/B; Ancient Cave/Donut) but the formula is identical.
2. **Rotation cost is route + gate state, never Euclidean distance** — Dust2 quantifies it (10.7 s A→B knife);
   Inferno routes through spawn/arch (15 s+ B→A); Train gates on Connector + smoke; Ancient gates on Donut-cut
   + Cave-without-bomb; Vertigo adds the level-change penalty (setup + noise + one-way).
3. **Utility-budget doctrine over position doctrine** — Inferno banana ("always contest… find the balance"),
   Train rush-stop mollies, Dust2 smoke-bloom-gated entries, Ancient staged defaults (~1:50 presence, ~1:35
   second timing), Vertigo Heaven-smoke timing windows.
4. **Anchor-stay rules share one trigger** — bomb/plant confirmation is the only hard rotation trigger on every
   map; everything else (noise, count, silence) is a weighted read. The costliest error generalizes too:
   rotating on manufactured extremity noise (Train roamer, Inferno A-noise fake, Dust2 B-noise, Ancient
   Cave-fake, Vertigo Heaven fake).
5. **Pop-hit vs full-exec economy** — when defenders hoard utility, flashes-first beats smoke-telegraphed
   executes (Inferno explicit; same logic underlies Dust2 timing-gated entries and Train contact bursts).
6. **Post-patch version-gating is mandatory everywhere** — Temple→Main removal (Ancient Aug-2025), Xbox
   rebuild (Dust2 Apr-2026), banana/coffin (Inferno Mar-2025) + balcony/graveyard (Mar-2026), Z-grating/Ivy
   fences (Train Spring-2025), A-catwalk/Elevator-door (Vertigo May-2024). Guides lag patches on every map
   (Inferno cs2.eu still listing Graveyard 3 weeks post-closure; Ancient pre-patch Temple refs).

### Which are genuinely map-specific

| # | Concept | Map | Why it doesn't transfer |
|---|---|---|---|
| 1 | Upper-hut ray sees past Ramp smoke | Train | No other map has a smoke-proof overwatch built into the execute choke |
| 2 | No-mid two-yard spine; Connector AWPer flex | Train | Only map with zero mid lane; rotation model is binary (spine open/closed) |
| 3 | Level-change support penalty + one-way drops | Vertigo | Only map where 6 m vertical < 25 m lateral; Heaven-drop irreversibility |
| 4 | Lip-height smoke scoring on uphill ramps | Vertigo | Slope-bloom geometry unique to ramp maps; binary covered/uncovered fails |
| 5 | Corner-smoke-gated 21 m AWP race (7.1 s vs 8.7 s) | Dust2 | Only map with measured spawn-to-contact races deciding entries numerically |
| 6 | Suicide-drop exclusion + Xbox jump-spot volatility | Dust2 | Map-specific movement tech with patch-flipped validity |
| 7 | Banana double-molly 12 s ≈ 12 s smoke cancellation | Inferno | Timed utility-cancellation arithmetic specific to banana's length |
| 8 | Arch-side rotation valve (15 s+ unrefundable) | Inferno | Only map where one player's lane-hold gates both sites' splits |
| 9 | Donut as Mid↔A cut + Cave-without-bomb + RedRoom regroup | Ancient | Three-way hinge with no equivalent; Cave pressure explicitly decoupled from bomb |
| 10 | Temple→Main ray deletion (Aug-2025) | Ancient | A real ray removed mid-lifecycle; pre/post demos differ in kind, not degree |
| 11 | Foliage/wetness readability + night versions | Ancient | Only map with shader-driven readability as an open variable |
| 12 | Cave footstep amplification (crouch/walk/run) | Ancient | Audio-as-geometry: Cave sound is positional intel with no parallel elsewhere |

### Analyzer implications (for later agents)

- **Version tag first:** every distance/smoke/support prior keys on the map's patch stamp (§1 of each file).
  Cross-map priors are valid only for the six general concepts above.
- **Log list per map:** §9 of each file specifies required observables (lane/yard/level tags, smoke-bloom
  timelines, hut/Donut/Connector states, trade-window frames). Radar cells alone prove nothing on any map.
- **Evidence ceiling:** no file contains tick-level demo-verified rounds; strongest items are VOD-timestamped
  (Inferno E4 R5 8:17–10:45; Vertigo EX-VTG-D chapters; Dust2 POV catalog log-on-watch). Cue demos/VODs before
  encoding any position as ground truth.
- **Concept IDs** (`MAP-ANC-*`, `MAP-INF-*`, `MAP-DST-*`, `MAP-TRN-*`, `MAP-VTG-*`) are stable retrieval keys —
  cite the ID, not the prose.

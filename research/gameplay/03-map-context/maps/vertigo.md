# Vertigo — Positioning & Spatial Context (CS2 Demo Analyzer)

**Status:** research only — no code, config, or schema changes.
**Concept IDs:** `MAP-VTG-001` … `MAP-VTG-015` (+ `EX-VTG-A/B/C/D`, `SQ-VTG-1..4`).
**Access date for all cited sources:** 2026-10-15 unless noted.
**Patch-period rule:** every positional claim below is tagged pre/post **2024-05-23 rework**.
Treat radar screenshots in cited guides as visualization only — never as collision/visibility evidence.
No map assets reproduced.

---

## 1. Scope and currency

### MAP-VTG-001 — Pool status: OUT since Jan 2025, still OUT in Oct 2026

- Valve removed Vertigo from Active Duty effective with the Jan 2025 pool change; Train replaced it ahead of the
  BLAST.tv Austin Major —
  [blast.tv, 2025-01-06](https://blast.tv/cs/news/train-replaces-vertigo) (evidences removal + Train-in).
- Pool tenure independently confirmed as 2023-09-27 – 2025-01-28 (489 days) —
  [cs2metahistory Vertigo](https://cs2metahistory.com/maps/vertigo/) (evidences tenure + 20 changes +
  140 Tier-1 maps at 48.8% CT).
- Current 2026 pool (effective after Premier Season 4 began 2026-01-19) is
  **Dust2 / Mirage / Inferno / Nuke / Ancient / Cache / Anubis** — Train itself was replaced by Anubis after ~1 year;
  Vertigo is not mentioned for return —
  [HLTV, 2026-01-09](https://www.hltv.org/news/43600/anubis-replaces-train-in-active-duty-pool)
  (evidences 2026 pool + "Train only lasted a year… brought in at beginning of 2025 as it replaced Vertigo").
- Reserve list (2026) includes Train and Vertigo alongside Warden/Stronghold/Alpine/Office/Italy —
  [Dot Esports pool guide, upd. Sep 2026](https://dotesports.com/counter-strike/news/all-cs2-competitive-active-duty-maps).

### Consequence: contemporary top-tier evidence is thin by design

- cs2metahistory monthly series shows "not in pool" every month Feb 2025 – Aug 2026 with **zero Tier-1 matches**
  in that window. All verified pro examples in §8 are therefore Mar–Apr 2024 (pre-rework) or Dec 2024 (post-rework,
  series-level only) — dated explicitly.
- The post-May-2024-rework top-tier sample (May 2024 – Jan 2025, e.g. Shanghai Major cycle) exists but was only
  shallowly retrievable in this pass — see §10.

### Last gameplay-relevant CS2 changes (tag every demo with these)

- **2024-05-23 rework** — added catwalk by A connecting to back of A; removed connector between back of A and
  elevators (now a **non-wallbangable door**); opened passage between elevators and scaffolding; slightly reduced
  A-site size (tighter angles, smokes cover more); re-tuned spawn timings (T-favored, faster to all areas);
  Wingman layout updated —
  [esports.net, 2024-05-23, republishing Valve 5/23/2024 notes](https://www.esports.net/news/counter-strike/new-cs2-update-vertigo-ct-economy-changes/)
  + [Refrag, 2024-05-29, before/after screenshots](https://refrag.gg/blog/whats-changed-on-vertigo-may-23rd-2024-update/).
  Same-day game-economy block (molotov/incendiary flame-pillar decay, plant-but-defused award $800→$600,
  M4A4 $3100→$3000) confirmed via [Valve official notes, 2024-05-23](https://store.steampowered.com/news/app/730/view/4177730135016140040)
  (publish date verified; body beyond meta not reader-renderable).
- 2024-04-25: collision and line-of-sight adjustments + bug/exploit fixes — [cs2metahistory](https://cs2metahistory.com/maps/vertigo/).
- 2024-02-28: adjusted spawn location priorities (Premier/Competitive) incl. Vertigo — [same].
- 2026-04-01 (post-pool, non-tactical for the analyzer): Valve *announced* more gradual vertical occlusion at
  transition edges + audio adjustments on Vertigo/Nuke — **in the opt-in `animgraph_2_beta` build (beta users
  could not connect to Valve servers); live-pool deployment unverified** — verified firsthand
  [Valve newsentry 528750051218948826](https://www.counter-strike.net/newsentry/528750051218948826)
  (beta scoping line + "Vertical occlusion is now more gradual at the edges of transition points in Nuke and
  Vertigo"); cs2metahistory lists the change on that date — treat as announced beta behavior, not a confirmed
  live mechanic. Do NOT treat 2026 Vertigo demos as pool-meta. *(Provenance: flagged by NukeResearcher
  2026-10-16 from Valve's companion beta article
  [newsentry 528750051218948816](https://www.counter-strike.net/newsentry/528750051218948816?l=english),
  verified firsthand by parent same day.)*
- **Changelog reconciliation (closed):** cs2metahistory's change list *omits* the 2024-05-23 rework entry that
  Valve-notes republishers + Refrag + Dust2.us document — a coverage gap in that secondary aggregator, not dating
  uncertainty. Version-gating code MUST key Vertigo geometry at `>= 2024-05-23 = post-rework` and MUST NOT derive
  version boundaries from cs2metahistory alone (`MAP-VTG-013`).

---

## 2. Important spatial characteristics

### MAP-VTG-002 — Verticality IS the map; lateral closeness is a trap

**Areas** (spellings cross-checked across three independent guides; Liquipedia/csdb/csgold reads failed
403/429/526 — recorded as gap, §10): A-ramp (long uphill T approach), Shelf / Yellow (mid-corridor structures),
Sidehall / Sidewalk, Crane, Middle + Ladder + Middle Boxes, Elevator, Scaffolding / Scaffold, Short (A), Headshot,
Sandbags, Back A / Drywall Stack, Catwalk (post-May-2024, A-edge and B-like), B-stairs + plywood/Wood + railings,
B-site Generators/Cooler ("cooler" corroborated by a player-coach quote, §8), Heaven —
[Refrag boosts, 2024-05-01](https://refrag.gg/blog/reach-new-heights-and-dominate-with-these-vertigo-boosts/)
+ [Refrag rework blog](https://refrag.gg/blog/whats-changed-on-vertigo-may-23rd-2024-update/)
+ [hally HLTV interview, 2024-03-29](https://www.hltv.org/news/38648/hally-interview-faze-defeat-lack-of-practice-due-to-illness-vertigo-decision).

**Callouts cross-verified (`MAP-VTG-010/S1`):** a 41-callout table with per-callout descriptions
(A Ramp = "large open slope… often used by Ts to rush on eco/pistol rounds"; B Stairs; Scaffold→Lane;
Elevator connects A Site to Top Mid and Door; Door = narrow Elevator→CT Spawn/Heaven; Heaven = raised platform +
doorway defending A; Headshot = "only the player's head will be visible"; Catwalk — "players can be shot from
below if enemy playing Under Stairs"; Sandbags; Double = orange-crate headglitch holding A Short; Ladder =
Underpass→T Mid, "one of the quickest ways to change floors") —
[TotalCS, 41 entries](https://totalcsgo.com/callouts/vertigo).
Level-call doctrine: "Top or Bottom isn't extra detail… totally different threats"; never call bare "Ramp"
(A vs B are opposite sides); Yellow exists in both Mid and B — always qualify; count players going down;
rotations take longer due to vertical movement, call early —
[BloodyCase guide, upd. 2026-02-10](https://bloodycase.com/blog/vertigo-callouts-full-guide/).
Pool-exit confirmation + upper/lower callout maps + CT contact / T target lists —
[esports.net callouts, 2025-01-10](https://www.esports.net/news/counter-strike/cs2-vertigo-callouts/).
**Analyzer consequence:** enforce `level ∈ {top, bottom}` + `ramp ∈ {A,B}` + `yellow ∈ {mid,B}` as mandatory
fields; reject unqualified calls at parse time.

**Routes / chokes:** two ramp/stair chokes (A-ramp uphill, B-stairs) + a thin mid (Yellow/Shelf/Ladder) +
Elevator as vertical connector. Contested zones: ramp control at both ends, mid presence.

**Elevation differentials that decide fights:** A-ramp climb into prepared headshot/sandbag angles; B-stairs
  railing vs site floor; mid elevator shaft; Heaven-over-site overwatch; footstep/audio occlusion boundaries tuned
  per-map (cs2metahistory 2023-09-27 entry evidences vertical audio occlusion as a first-class mechanic; the
  2026-04-01 smoothing entry is announced-beta only — see §1).

### Core thesis, Vertigo flavor

Geometric proximity ≠ support because teammates stacked vertically (Heaven + site, Elevator + Scaffolding,
railing + stairs floor) often **cannot trade** — the lower player cannot pitch up in time, the upper player
overexposes to a second angle to assist. Unobstructed ray ≠ tactical availability because height-angle math
shrinks visible body fraction (headshot-only over lips/ledges, plywood see-through-but-partial), drops are
one-way commitments, and a "short" lateral rotate (Heaven→site, Elevator→Short) hides a long vertical path with
fall damage and noise exposure.

**Sightline≠visibility specifics:** lips/ledges create headshot-only duels; B-stairs plywood is thin/shootable
and leaks player models depending on stance; metal walls (e.g. Back Crane) are spammable; the Drywall Stack
boost behind a metal pole sees *over* standard execute smokes to Shelf/Sandbags — i.e. a smoke that "covers" on
the 2-D radar does not cover the vertical ray — [Refrag boosts](https://refrag.gg/blog/reach-new-heights-and-dominate-with-these-vertigo-boosts/).

---

## 3. T-side principles

### MAP-VTG-003 — Default = ramp control + mid presence

A-centricity was the pre-rework complaint Valve explicitly tried to fix ("complaints centered around very A
site-centric gameplay" — [Refrag rework blog](https://refrag.gg/blog/whats-changed-on-vertigo-may-23rd-2024-update/)).

- **Entries (each conditional — never a fixed "correct" spot):**
  - *A-ramp hits* — viable depending on timing after the spawn-timing buff, economy for ramp smokes/mollies,
    alive ramp-anchor count, whether CTs show early Elevator→Short peek.
  - *B-stairs pops via railing/Wood boosts* — the Bottom-B railing boost gives a headshot angle onto default /
    left-site CTs and can jump into site, but requires clearing Danger behind Wood with molotov because plywood
    leaks — [Refrag boosts](https://refrag.gg/blog/reach-new-heights-and-dominate-with-these-vertigo-boosts/).
  - *A-split via Elevator→Scaffolding/Short* — only post-May-2024; depends on elevator timing vs CT door peek
    and mid noise.
- **Lurks / splits:** Sidehall/Crane lurks exploit sidewalk-flank exposure (Back Crane boost is explicitly
  flank-exposed — [same]); mid-boxes + contact-partner mixes mid play but it is "awkward to fight Ts into
  Middle/Ladder" — so mid-lurk value depends on whether the CT mid player already committed to a boost or rotate.
- **Mid-round / post-plant:** elevated post-plants (Heaven-adjacent, Scaffold, Back-A catwalk post-rework)
  convert height into defuse-denial — but only if numbers allow cross-level coverage; a solo elevated planter
  with teammates stacked below is *not* supported (thesis restated).
- **Off-angles / space creation:** height abuse (railing poles, drywall stacks, sidehall bollard boosts) works
  as surprise equity, each documented as "high risk, high reward… clunky to set up" — the analyzer MUST discount
  first-sight rays from these voxels without setup-time + flank-exposure + audio context — [same].
- **Economy interaction:** BitSkins (May 2024, pre-rework stats) rated Vertigo the first T-sided map surveyed:
  **T 52.2% vs CT 47.8%**, glossed as "Ramp Rush Simulator… massive edge from a simple entry kill on an A ramp
  rush" — [bitskins, 2024-05-12](https://bitskins.com/blog/cs2-map-sides-which-maps-are-t-or-ct-sided/).
  Spirit coach hally independently called attack "the strong side of Vertigo" (Mar 2024) —
  [hally interview](https://www.hltv.org/news/38648/hally-interview-faze-defeat-lack-of-practice-due-to-illness-vertigo-decision).
  Analyzer prior: weight the opening ramp-duel outcome heavily on Vertigo T halves. (Side-balance window conflict
  preserved in §10: all-time Tier-1 48.8% CT vs May-2024 snapshot 52.2% T — quote only with window.)

---

## 4. CT-side principles

### MAP-VTG-004 — Anchor the ramps, win with Heaven/Elevator crossfires, live with fast-but-exposed rotates

- **Anchoring:** ramp anchors (A-ramp, B-stairs) trade space uphill/downstairs; the B default-vs-far-left split
  is the key decision (the railing boost specifically punishes "default position… or far left" holders —
  [Refrag boosts](https://refrag.gg/blog/reach-new-heights-and-dominate-with-these-vertigo-boosts/)).
- **Crossfires:** site floor + Heaven; site + Elevator/Short peek (post-rework CTs "peek Ramp much faster" via
  the new Elevator→Short door — [esports.net](https://www.esports.net/news/counter-strike/new-cs2-update-vertigo-ct-economy-changes/)).
  Each crossfire is level-dependent: floor holds low/entry, Heaven/Elevator holds high/trade — if either is
  smoked off at lip height, the other is isolated despite <10 m 3-D distance.
- **Rotators:** the mid player (Yellow/Shelf/Ladder/Sidehall) is the swing; Back Crane and Middle Boxes boosts
  are CT info-stealing tools but both flagged as flank-exposed/awkward — [Refrag boosts](https://refrag.gg/blog/reach-new-heights-and-dominate-with-these-vertigo-boosts/).
- **Info / aggression:** ramp pushes and Elevator door peeks; drywall-back-A info boost sees over smokes —
  usable only with a teammate ready to act on the info the same second, else a free exit frag — [same].
- **Retakes / anti-execute / repositioning:** vertical retakes (Heaven drops, Scaffold/Elevator re-entry,
  catwalk wraparounds post-rework); anti-execute leans on ramp molotovs + incendiary economy (May 2024 patch cut
  CT incendiary $600→$500 but shrank spread radius/duration — fewer, weaker area-denials, so timing matters more —
  [esports.net](https://www.esports.net/news/counter-strike/new-cs2-update-vertigo-ct-economy-changes/);
  burn 7s→5.5s per snippet-level corroboration, §10). Repositioning under uncertainty means giving a ramp early to
  preserve cross-level pairing rather than stacking two players on one level.

---

## 5. Role-dependent positional responsibilities

### MAP-VTG-005 — Every slot below is a conditional bundle, not a lookup

Position is viable only given (timing, economy/utility, alive counts both sides, opponent pressure,
information held, team objective).

- **A-ramp anchor:** holds the uphill entry; responsibility = delay + call the Elevator/Short swing; collapses
  if Heaven/mid info goes dark or utility runs dry.
- **B-stairs anchor (+Wood/Danger):** holds stairs + plywood; responsibility = molotov Danger before contact,
  play off Heaven; dies to the railing headshot angle if static in default two rounds in a row.
- **Heaven player:** overwatch/trade authority; responsibility = never drop without site-floor commitment
  communicated; the drop is one-way (noise + fall + lost height).
- **Elevator/Short (post-rework):** fast peek/rotate valve; responsibility = time the door peek to T
  ramp-contact audio, else feed the entry.
- **Mid rotator (Yellow/Shelf/Ladder):** information + swing to either ramp; responsibility = pick boost vs
  passive by economy (boosts need two players + setup seconds) and flank risk (sidewalk).
- **T ramp-lead / stairs-entry / mid-presence / lurk:** each owns one choke's contact timing; split viability
  depends on simultaneous pressure (a late Elevator split after failed ramp contact is a save, not a split).

---

## 6. Utility and geometry interactions

### MAP-VTG-006 — Tactical effect, NOT lineups

- **Ramp smokes/molotovs:** the A-site size reduction means "smokes will cover more area" post-rework —
  [Refrag rework blog](https://refrag.gg/blog/whats-changed-on-vertigo-may-23rd-2024-update/) — version-gate
  smoke-coverage models at 2024-05-23. B Danger/Wood molotov is a mandatory pre-clear (plywood spammability —
  [Refrag boosts](https://refrag.gg/blog/reach-new-heights-and-dominate-with-these-vertigo-boosts/)).
  Incendiary nerf (smaller spread, shorter duration) reduces CT stall time — retake-delay inferences from 2023
  data overstate 2024+ stall.
- **Heaven grammar (`MAP-VTG-077/BH2`):** Heaven is a fake-origin + smoke-timed headshot angle + paired-utility
  platform, not just overwatch: "Heaven fake and another clean headshot"; "flank finds [a player] ahead of the
  heaven smoke landing" (smoke-timing windows); "red smoke + smoke towards heaven" cross-map pairing; wallbang
  donut-tuck finds. (Dallas OT VOD transcript, opened.)
- **Plant grammar (`MAP-VTG-077/BH3`):** plant = stick-verification + Tetris-cover + second-level timing
  ("walks out so early… make sure [he] is sticking… uses the full 5 seconds purposefully"; missed-plant-by-a-second
  round swings). (FURIA–paiN transcript, 36 plant mentions — highest observed.)
- **Catwalk tactical effect, refined (`MAP-VTG-014/J1`):** the A catwalk extends all the way into Heaven —
  "theoretically flank onto site or into Heaven via this catwalk, removing the choke point at Heaven that is
  often smoked or molly'd off"; unaware CT snipers risk being "charged down" and some T plant spots become less
  safe. The new Side Hall/Lane→Elevator door "gives CT players an easier time holding onto A and retaking it…
  new entry point and more secure way to protect from a Side Hall rush, although the door can still be smoked
  off" — predicting a mandatory smoke to stop an Elevator crossfire —
  [Dust2.us, 2024-05-23 walkthrough](https://www.dust2.us/news/48826/cs2-5-23-update-see-the-changes-to-vertigo).
  **Correction to analyzer retake model post-2024-05-23:** Heaven smoke/molly no longer seals the site (catwalk
  bypass exists); Elevator-door smoke becomes the mandatory T execute component.
- **Mid smokes (Yellow/Shelf/Ladder):** cut the Heaven↔site visual link asymmetrically — the upper player loses
  reference while the lower keeps audio; treat as one-way info loss.
- **Retake utility from Heaven:** drops + molotovs onto default plant deny defuse only if the plant is *below*
  the Heaven ray; elevated T post-plants (Scaffold/catwalk) invert this — Heaven utility rains below the plant.
- **Smoke-on-ramp behavior:** uphill smokes bloom/fade along the slope; a "covered" ramp ray at lip height
  reopens as players crest — never score a ramp smoke as binary covered/uncovered; score by crest-line height
  over time.
- **Smoke taxonomy (analyzer use):** Elevator→Bottom Ramp ("block Ts entering A"); Sidewalk→Elevator (blocks
  mid-round connector rush); A→Crane ("provide sniper in Heaven advantage"); B Stairs→Cooler/Generators
  ("universal map-control smoke," usable both sides); T-Mid→Elevator (stalls A CTs/snipers + safe passage to B);
  Bridge→Ramp (+flash combo to Sidewalk); Ramp→Heaven (stalls CT arrivals, "most useful"); Ramp→Elevator
  (mid-round adaptation after failed B rush) —
  [Profilerr hub, upd. 2025-02-18, post-rework incl.](https://profilerr.net/cs2-vertigo-smokes-for-both-teams-ct-and-t-side/).
  Each entry pairs a smoke with its stall/adaptation function + direction — exactly the lip-height-over-time +
  one-way-info-loss model. Do NOT copy lineup instructions; cite only tactical effect + precondition.
- **Wallbangs (closed allow/deny set):** plywood YES, Crane metal YES, new Elevator door NO (explicitly "not
  able to be wall-banged" — [Refrag rework blog](https://refrag.gg/blog/whats-changed-on-vertigo-may-23rd-2024-update/));
  AWP long-wall rays: T Main Top→B back orange boxes; CT Mid→A Connector vs T mid-rush; Mid→A-Connector→T Main
  Top (elevator-wall zeros reference); audio-cue setup, pre-fire common hides; penetration AWP > AK > M4s >
  Deagle — [Skin.Club, 2024-08-06 / upd. 2026-09-06, post-rework geometry](https://community.skin.club/en/articles/best-wallbang-spots-vertigo-cs2).
  Ray-through-wall availability flips at the Elevator door across versions — version-gate it.
- **First-person CT anchor note (`MAP-VTG-011/F1`):** CS afap "YELLOW NADES to play from 51 on NEW VERTIGO"
  (2024-05-29, 6 days post-rework, explicitly post-"new spawn timing"): with new spawn timings "CTs get to gap
  faster but to crane slower," motivating a CT anchor at position "51" (graffiti/beam); timestamped set: Yellow
  smoke + molotov, Yellow+ramp flashes, Ramp HE/flash/smoke variants, Gap/Crane/Sideramp/Forklift/Bridge nades —
  [YouTube description + timestamps](https://www.youtube.com/watch?v=QNN-ZHH8kNE).
  Analyzer value: first-person CT-side confirmation that the May-2024 spawn-timing change re-priced *which*
  info/anchor spots are contestable — version-gate rotation-timing priors here. (Auto-captions music-only; do not
  cite transcript beyond that.)

---

## 7. Common questionable decisions and legitimate exceptions

### MAP-VTG-007

- **Stacking two defenders on one level** (both site floor, both Heaven) while conceding the other: looks like
  "2 players near site = supported" on radar; actually unsupportable vs a vertical split.
  *Exception:* low-utility eco where a one-level gamble + aggressive contact is the only equity.
- **Dry/stack boosts without flank cover or without molotoving known spam spots** (Wood, Crane metal — required
  clear per [Refrag boosts](https://refrag.gg/blog/reach-new-heights-and-dominate-with-these-vertigo-boosts/)).
  *Exception:* explicit one-round surprise with instant drop after contact.
- **Slow Elevator split after lost ramp contact:** arrives into a prepared Short/door angle.
  *Exception:* mid info confirms full CT collapse to the other site.
- **Heaven drop to "help" a lost site duel:** converts a winnable 2-level retake into two 1v1s; the drop is
  one-way. *Exception:* bomb-timer pressure + known isolated planter below with no second T ray.
- **Over-rotating on audio through vertical occlusion boundaries** (Vertigo-specific audio occlusion tuning per
  cs2metahistory 2023-09-27; 2026-04-01 smoothing announced in opt-in beta, live deployment unverified — see §1).
  Footsteps above/below mislead.
- **FaZe's Vertigo gamble (§8) is the canonical legitimate exception:** a zero-prep map pick as veto exploit
  worked precisely because opponent prep-heaviness inverted (karrigan: "played the veto to our strengths" —
  [HLTV QF live blog, 2024-03-28/29](https://www.hltv.org/news/38641/live-updates-from-pgl-major-copenhagen-quarter-finals-day-1)).

---

## 8. Verified gameplay examples

Both Major-Copenhagen examples are **pre-May-2024-rework geometry** (no A catwalk; back-A↔elevator connector
still open). Still relevant to the ramp-control/vertical-trade thesis; NOT to A-site specifics.

### EX-VTG-A — Spirit vs FaZe, PGL Major Copenhagen 2024 QF, Vertigo decider, 2024-03-28 (FaZe 16–14 OT)

- What it evidences: veto-level map decision + T-side fragility + vertical/OT clutch variance. FaZe's first
  official on Vertigo in ~5 months; frozen: "We had no prep, we just went ham… first time we played an official
  on Vertigo" — [HLTV live updates QF day 1](https://www.hltv.org/news/38641/live-updates-from-pgl-major-copenhagen-quarter-finals-day-1).
  Spirit started T (their coach-called "strong side") yet fell 0–7 losing "zones… timings" —
  [hally interview](https://www.hltv.org/news/38648/hally-interview-faze-defeat-lack-of-practice-due-to-illness-vertigo-decision);
  pistol/first-buy micro-errors vs B Generators/Cooler 3v5 + FaZe grenade readiness [same]. Comeback 5–12→OT on
  CT when "pressure" released [same]; OT decided by FaZe clutches (ropz 1v2 for match point; rain closing 1v2 on
  B; chopper 1v2 + magixx 1v1 keeping Spirit alive; broky outsmarting zont1x) [same live blog].
- Footage: full-map VOD record exists ("Spirit vs FaZe – Map 3 Vertigo", embed `-G4FGxRS-8U`) —
  [videodb.org record](https://videodb.org/spirit-vs-faze-%E2%80%93-map-3-vertigo-pgl-cs2-major-copenhagen-2024-playoff-stage/-G4FGxRS-8U).
  Per-round timestamps unverified from text (embedded Twitch clips per round in the live blog) — cite VOD ID for
  future round-stamping; do not claim timestamps.

### EX-VTG-B — Vitality vs FaZe, PGL Major Copenhagen 2024 SF, Vertigo, 2024-03-30 (Vitality 13–5; 11–1 T half, mezii-led)

- What it evidences: ramp/entry snowball at top tier. "With mezii leading the charge, the reigning Major
  champions cruised to an 11-1 lead after picking FaZe's defense apart… Vitality won an eco round… following a
  trio of frags by mezii" —
  [HLTV, 2024-03-30](https://www.hltv.org/news/38659/faze-beat-vitality-to-book-major-final-spot).
  Same FaZe roster that won the OT thriller two days prior got dismantled — supports the ramp-entry-leverage +
  defense-fragility reading (BitSkins "Ramp Rush Simulator" thesis). Round-by-round demo evidence: HLTV matchpage
  mapstatsid/172627 linked in article (HTTP 403 on direct read — recorded); per-round positions not re-verified.

### EX-VTG-C — paiN vs BIG, Shanghai Major 2024 Elimination Stage, 2024-12-06 (paiN 13–11 Vertigo opener; BIG 13–11 Dust2; paiN 13–6 Mirage, BIG eliminated)

- Why it matters: **only verified post-May-2024-rework Vertigo datapoint** in this research (new A catwalk +
  Elevator→Short door + smaller A site active). Two 13–11 scorelines signal contested ramp/stairs control rather
  than 11–1 snowballs — consistent with rework intent (tighter A angles, smokes cover more, CTs peek Ramp faster
  via Elevator door) —
  [BLAST.tv Shanghai Elimination round-three recap, 2024-12-06](https://blast.tv/cs/news/shanghai-elimination-stage-round-three-recap).
- Limits (explicit): deciding-round detail, side halves, per-round positions NOT in recap text — series-level
  evidence only, not tactical-round evidence.

### EX-VTG-D — sAw vs Eternal Fire, ESL Pro League S19 Group A elimination, Map 1 Vertigo, 2024-04-27 (pre-rework, WITH round timestamps)

- ESL Archives full-map VOD, 51:19, round chapters in description —
  [ESL Archives YouTube, uploaded 2024-04-27](https://www.youtube.com/watch?v=zgTBTya-BLY).
- Result/stakes: sAw 9–3 CT half on EF's map pick ("EF's best map hands down, their pick"), EF T-side recovery
  to 9–7/10–8, sAw close-out; loser's elimination context per casters. Transcript evidences: R1 A-execute detail
  ("double nades towards sandbags, molotov towards Boost, smokes"); ztrder/star A-ramp control praised ("aridoz
  A ramp control world class; T side especially"); EF's T identity = A-ramp-centric ("everyone knows what you're
  up to, they know your tendencies"); swing rounds — woxic AWP multi/ace sequence R10–12, story AWP CT close-out
  rounds, failed EF retake miscommunication on ramp ("has to be within the 5-sec window"), final weak-buy B-fake
  read by sAw ("very low on utility… story reading them like a book").
- Round-stamp anchors (VOD chapters): R1 00:00:00, R6 clutch 00:11:32, R9–10 multis 00:19:58/00:21:40,
  R11–12 00:24:15/00:26:15, R2H pistol 00:31:17, R19–21 highlights 00:44:42/00:46:27/00:48:58.
  Relevant to the A-ramp-entry thesis + retake-timing + weak-buy B-fake reads.
- Limits: auto-generated caster audio (banter-heavy); no demo-file positions. Cite as VOD-verified rounds, not
  demo-verified voxels.

---

## 9. Observable data requirements and missing information

### MAP-VTG-008 — Required per-round observables

Version tag (pre/post 2024-05-23 for A catwalk + elevator door + site size; pre/post 2024-04-25 LOS/collision);
per-player 3-D voxel + level tag (ramp/stairs/elevator/heaven/site-floor/scaffold/catwalk), not 2-D radar cell;
crest-line heights on ramps; boost/setup state (two stacked models + setup seconds + flank exposure); utility
state at lip height over time (not binary smoked); audio-occlusion zone per listener; alive/economy/utility
counts; objective clock (plant/defuse/timer).

### How elevation/rotations must affect distance-based reasoning

Replace Euclidean/"same site" distance with **route-plus-level cost**:
(a) any path crossing a level change (Heaven drop, Elevator shaft, stairs crest, Scaffold climb) adds setup +
noise + one-way penalty — two players 6 m apart across levels support *slower* than two players 25 m apart on
one level with a clean trade ray;
(b) rotations that look short on radar (Heaven→site, Elevator→Short post-rework) are fast only with a
pre-cleared door/angle + utility; otherwise they are feeds;
(c) support score = shared visual on the *same target ray at the same height band* within the trade window, not
shared zone;
(d) version-gate every distance prior at 2024-05-23 (new Short passage shortens the CT peek path; smaller A-site
compresses post-plant distances).

### Situation questions (observed setup → analysis frame)

- **SQ-VTG-1 — T ramp contact stalls at crest vs 2 CT (floor + Heaven), 4v5, 0:55, mid silent.** Positions: two
  T at crest lip, one Yellow, one B-stairs noise, bomb Yellow. Objective: convert or abort ramp.
  Responsibilities: crest pair holds lip (no re-peek same height), Yellow calls Elevator timing, stairs sells.
  Alternatives: commit Elevator split / fall to B stairs / save-utility reset. Info: Heaven utility count?
  Elevator door sound? Decision factors: CT incendiary post-nerf stall window, spawn-timing T edge, alive
  anchors. Evidence needed: crest-height ray traces + Heaven trade-window frames.
- **SQ-VTG-2 — CT Heaven + site floor vs T Scaffold/elevated plant, 2v2 retake, kit on floor player.**
  Observed: planter elevated (Scaffold/catwalk), one T stairs delay. Objective: defuse. Responsibilities: floor
  plays kit-stick threat, Heaven denies elevated ray (not drops). Alternatives: double-swing elevated vs
  isolate-then-stick. Info: which level is second T on? kit smoke available? Decision factors: one-way drop
  cost, plant-above-Heaven-ray inversion. Evidence: plant voxel height vs Heaven ray + drop-noise timing.
- **SQ-VTG-3 — B-stairs execute vs default + far-left anchors, T boost ready at railing.** Observed: T pair at
  Bottom-B railing setup, CT default + left-site. Objective: entry without feed. Responsibilities: booster-molly
  Danger/Wood first (plywood leak), contact plays off railing headshot angle. Alternatives: dry stairs flood vs
  boost-pop vs fake-stairs-to-ramp. Info: anchor positions from prior rounds? Heaven occupied? Decision: boost
  only if two-round anchor-static tendency + flank (sidewalk) covered. Evidence: anchor heatmaps by round +
  flank-audio seconds.
- **SQ-VTG-4 — Mid info-boost (Crane/Boxes) offered, 3v4, low utility.** Observed: two CT available for boost,
  T mid silent. Objective: info without throw. Responsibilities: boosted player takes 2-second glance then
  drops; partner holds flank. Alternatives: passive Yellow sound-hold vs Sidehall contact. Info: T mid-timing
  tendency? Decision: skip boost (both documented as flank-exposed/awkward) unless loss is already priced.
  Evidence: boost setup duration + sidewalk flank timing distributions.

---

## 10. Known uncertainties and research gaps

### MAP-VTG-009 (+ MAP-VTG-011/012/015 ledgers)

1. Liquipedia Vertigo, csdb.gg callouts, csgold guide unreadable (403/429/526) — callout spellings rest on
   Refrag + TotalCS + BloodyCase + HLTV quotes only; re-fetch if needed. (Partially closed by `MAP-VTG-010/S1`.)
2. **No per-round demo re-verification:** examples rest on HLTV text + VOD chapters; exact tick positions
   unverified — mark EX-VTG-A/B/C as text-verified (D as VOD-verified rounds), not demo-verified.
3. Post-May-2024-rework top-tier sample (May 2024–Jan 2025) thinly covered — A-catwalk/Elevator-door meta shift
   unmeasured at round level (only series-level EX-VTG-C + smoke taxonomy + afap anchor note).
4. No analyst-VOD or player-POV breakdown opened as citable tactics (afap video opened for description/timestamps
   only; EPL S19 VOD found, not read). First-person rework verdict (donk "praises Vertigo changes," 2024-07-18
   EWC interview) is **search-snippet level only (Escorenews 403) — weak evidence, not a verified quote**
   (`MAP-VTG-015/K2`).
5. Quantitative side-balance conflict: all-time Tier-1 48.8% CT [cs2metahistory] vs May-2024 snapshot T 52.2%
   [BitSkins] — different windows/methods; do not quote a single "Vertigo is X-sided" prior without window.
6. Incendiary-nerf magnitude: Valve-notes republication (reduced duration + spread + $600→$500) is opened
   evidence; the 7s→5.5s burn figure is snippet-level (Reddit retrospective) — use 5.5s post-2024-05-23 as
   provisional, not verified (`MAP-VTG-015/K3`).
7. Screenshots/radars in Refrag/Dust2.us blogs are visualization only, never collision/visibility evidence — no
   ray claim grounded on them.

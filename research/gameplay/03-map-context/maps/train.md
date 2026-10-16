# Train — Positioning & Spatial Context (CS2 Demo Analyzer)

**Status:** research only — no code, config, or schema changes.
**Concept IDs:** `MAP-TRN-001` … `MAP-TRN-014` (+ `EX-TRN-*`, `SQ-TRN-*`).
**Access date for cited sources:** 2026-10-15/16 unless noted.
**Coverage warning:** the dedicated Train researcher returned §§1–3 with full citations, then hit a provider usage
limit before §§4–10. Sections 4–10 below are therefore synthesized by the parent **from the same opened primary
sources** (BLAST.tv guide, Dot Esports callouts, Valve/Spring-Forward notes) plus the researcher's cited claims —
marked `[SYNTH]` where the researcher's own wording was unavailable. Do not treat §§4–10 as carrying the same
citation density as §§1–3; gaps are explicit in §10.
**Patch-period rule:** geometry = CS2 rework (Nov 2024) + Spring Forward (31 Mar / 01 Apr 2025), frozen through
removal. Tag every positional claim with this window.
Radars/screenshots are visualization only. No map assets reproduced.

---

## 1. Scope and currency

### MAP-TRN-001/002 — NOT in Active Duty as of Oct 2026; evidence window Jan 2025 – Jan 2026

- Train released 13 Nov 2024 *without* pool entry → entered Active Duty **06 Jan 2025** replacing Vertigo
  (Bounty S1 / Austin Major cycle) → removed **19 Jan 2026** (Premier S4), replaced by Anubis —
  `blast.tv train-replaces-vertigo`; `pro.eslgaming EPT map-pool-update`; `hltv.org/news/40693` (Jan-2025);
  `dust2.us/news/69485` (Jan-2026); Valve newsentry index (opened 2026-10-15: 21 Jan 2026 "Fourth Season",
  28 Apr 2026 "Return Of Cache", 08 Jul 2026 "Season 5… Cache replaces Overpass"); `liquipedia Portal:Maps/CS2`
  snippet (`Train 2025-01-06`).
- Post-Train churn: **Cache returned 28 Apr 2026** replacing Overpass (Valve newsentry 08 Jul 2026 Season-5 note).
- Patches: (a) Nov 2024 rebuild; (b) **Spring Forward (Valve newsentry 529842339955343453, 31 Mar 2025;
  BLAST 01 Apr 2025)**: shortened A-site roof rail (easier utility in), catwalk-outside-Z grating replaced (was
  see-through), Ivy-top fences solid, simplified Z-door back wall / upper-B background / Ivy brick, fixed
  upper-B arch nade collision + A-Main shadow-through-window + world holes —
  Valve index + `blast.tv/cs2-spring-forward-update`. (c) 28 Jul 2025 anim/damage-prediction touched Train —
  no geometry claims. `counter-strike.net/reintroducing_train` = 2014 CS:GO rebuild, excluded.
- Meta correction: Jan-2025 officials felt T-sided (cover-poor A); Austin Major Jun 2025 (14 picks / 62 bans):
  **55.7% CT / 44.3% T** — CT-leaning, heavily banned —
  `earlygame first-officials` (17 Jan 2025); `bo3.gg austin-major-maps-pickrate-and-side-balance` (23 Jun 2025).
  CS2Hype independently labels "Hard… CT 56% / T 44%" with CT goal "delay first contact, keep info alive,
  retake as group" / T goal "convert early control into split/execute, not one choke" — corroborates lean +
  doctrine, but its callouts are **CS:GO-contaminated — rejected for naming**.

---

## 2. Important spatial characteristics

### MAP-TRN-003 — Two yards, one spine, no mid

A-yard (Main + Ivy + Underpass mouths → 3-train site) / B-yard (Halls → Ramp/Upper) joined ONLY via
Connector/Hell/CT-spawn; rotations cross open Door/Back-Site ground. Rotation viability = Connector control +
smoke + anchors alive + rush stopped — never distance —
[BLAST.tv Train guide, 01 Mar 2025](https://blast.tv/cs/news/how-to-play-train-in-cs2)
(Connector AWPer flex, freed post-stop) + `juked.gg train-map-updates` (25 Mar 2025).
CS2Hype CT doctrine ("retake as group when site lost") confirms rotation/retake-centric play.

### MAP-TRN-004 — CS2-correct chokes and callouts

- **Chokes:** Main mouth, Ivy→A2, Underpass→Electrical mouth, Halls doors/stairs, Ramp + Upper hut.
  **NO popdog ladder** (walkway "Underpass"/"B Corridor" Brown-Halls→Electrical); **NO Heaven** (ground hideout);
  A1 shut → wide A Door; A1–A2 via Hell; open pre-Door / B Back Site; surviving ladder = B Ladder→Upper B —
  [BLAST.tv guide](https://blast.tv/cs/news/how-to-play-train-in-cs2) +
  [Dot Esports callouts, Nov 2024 / upd. Dec 2025](https://dotesports.com/counter-strike/news/all-train-callouts-in-cs2)
  + Juked (+ Valve in-game Train map-guide).
- **Callouts** (Dot Esports, CS2-correct): T Stairs, Kitchen, Showers, Underpass, B Halls/Upper/Ramp/Ladder,
  Blue/B-Red/Orange, Catwalk, Headshot, Back Site, Connector, Old Heaven, Electrical, A Main, Olof, Hell,
  A Doors, A-Red, Yellow, A1/A2, Ivy, Pigeon, Alley, Dumpster, CT Stairs/Tunnel.
  A now has **three** trains (was four parallel); Ivy's old bomb entrance covered, new one at old Stopper;
  A and B both fronted by huge open spaces (pre-Door / Back Site) that make on-site rotation coverless without
  smoke/incendiary.

### MAP-TRN-005 — Elevation without verticality

Blue climbable; Catwalk→Orange jump; Headshot elevated; hut over Ramp; Yellow site-side-only climb; Ivy-top
fences solid post-Mar-2025. Train tops = over-car sight but stranded (long mantle, no drop into cover).
CS2Hype "spacing and angle map… every lane has long sightlines" + "trade every angle… too many angles for
solo clears" corroborates crossfire density (doctrine only).

### MAP-TRN-006 — Core thesis (extreme case on Train)

The Underpass man ~10 m plan-view from Electrical/Hell yet wall+bend away (no trade/flash); hut-CT vs Ramp-T
share a smoke-proof ray yet unavailable without hut clear; Ivy lurk + Main pack radar-equidistant but split by
the whole A crossfire. **Gate ALL support claims on (a) shared lane + mutual sight, (b) traversable path ≤~1 s
trade timing, (c) wall/train/car + smoke state — NEVER Euclidean distance.**
(Synthesis of BLAST.tv hut-ray + smoke-forced rotates + cover-lack evidence.)

---

## 3. T-side principles

### MAP-TRN-010 — Default (conditional): 2 Main + 1 Ivy + 1 B/Popdog + 1 roamer

The roamer is the pressure dial (Ivy pins A2 / Popdog adds angle / B forces rotate off A). Depends on spawns,
HE/molotov depth, info —
[BLAST.tv guide](https://blast.tv/cs/news/how-to-play-train-in-cs2).
CS2Hype ("outer smoke sets… pressure from ivy or popdog"; "inner presence keeps CTs from stacking outer…
late inner hit strongest after outer utility pulls rotations") corroborates multi-pressure doctrine.

### MAP-TRN-011 — Entries

Main contact/burst post-cross/connector/doors smokes; Underpass+Main split; Ivy walk→A2; Ramp+Upper contact.
**A rush = round-defining threat** — [BLAST.tv guide](https://blast.tv/cs/news/how-to-play-train-in-cs2)
(quartet from one area; stop-rush priority); `cs2strat.com/en/maps/train` index.
Verified concept catalog (opened 2026-10-15, StratArchive + HLTV series pages): NAVI "A Rush G3R8" (gun) +
"Pistol A Rush G3R1" (economy-spanning rush); "Fast B Upper Contact G3R6" (contact-paced Upper-B); Astralis
"A Rush Hold G2R11" (CT mirror); G2 "Ivy Contact R4" (walk-tempo Ivy contact).
CS2Hype ("throw before first contact, move while they bloom, expect CTs to push gaps"; "clear close trains
before planting") corroborates exec sequencing.

### MAP-TRN-012 — Splits / conditioning

- Aurora **"Main/Ivy Split G2R8"** (Aurora T-side, series winner, Train 13–8) + Astralis T-side Main+Ivy splits
  in the same series — the split is side-symmetric geometry exploitation, not a team playbook quirk.
- G2 "A Split R1" (pistol) + R4 + R7 = three entrance×economy variants, one G2 T-side.
- NAVI "Default A Split, rotation G3R2" + late-split variants (four variants, one NAVI T-side).
- Astralis–Aurora "Fast B Execute G2R16"; Aurora "fast upper duo lurk" + "Popdog A rotation" (rotational
  complement: Popdog-origin pressure converting to A hit).
- Fnatic-2025 per Tedd: BlameF timed space + Jacomoo Pop pressure + Crimz utility.
(StratArchive catalogs opened 2026-10-15; Tedd `community.skin.club`, 07 Nov 2025.)

### MAP-TRN-013 — Mid-round / post-plant (conditional)

Train-top plants + car afterplants; Ivy-extremity late split; B Back-Site off Orange/Red. Depends on
plant-train, top control, retake smoke. Short rail (Mar 2025) eases utility in. CS2Hype post-plant lanes
("assign who watches ivy, main, popdog before bomb down") corroborates pre-planned afterplants. G3R2
(default→split→rotation) = canonical mid-round conversion: default presence becomes a rotation read, not a
committed hit.

### MAP-TRN-014 — Space creation / Ivy starvation

Extremity + Halls + Popdog-roamer force 4A to declare, hit the thinned mouth. SPUNJ Jan-2025 T-spawn-move
musing = Ivy starved (clustered A pulled…). *(Researcher cut off mid-sentence here — preserved as fragment;
see §10.)* [SYNTH] The mechanism is consistent with BLAST's roamer-as-lynchpin doctrine: wherever the roamer
shows, CTs must honor it, and the hit goes where they thinned.

---

## 4. CT-side principles [SYNTH — from BLAST.tv guide + handoff §§2–3]

### MAP-TRN-020 — Stop the rush, then play the spine

- **Default: 4A most rounds** — A Main, Popdog, Connector, Ivy — with roles interchanging by spawn (molotov duty
  + Popdog race). The Connector player (often the AWPer) is the main rotator and may start Ivy/B-Halls if T
  pressure leans there early —
  [BLAST.tv guide](https://blast.tv/cs/news/how-to-play-train-in-cs2).
- **Rush-stop is the round's first objective:** "The main goal of the A players is to prevent the A rush…
  exceptionally strong… The round gets ten times easier once the rush has been stopped. Stopping the rush also
  allows the Connector player more freedom of movement" to reinforce B once space/info is taken. Every CT
  positional judgment before ~0:40 is subordinate to this.
- **B solo plays passive:** "If [the B player is] solo, they should look to remain passive on the B site. It's
  a very retakeable site, so just gaining info and making sure you're alive for that retake can be enough.
  Anything extra should be considered a bonus." — [same]. A B player dying for one exit frag before the rush
  verdict on A is the canonical Train error.
- **Crossfires [SYNTH from yard geometry]:** A — Main-mouth + Ivy/A2 + Hell/Electrical triangle; B — Ramp +
  Upper-hut + Back-Site/Orange. The Upper hut "is incredibly hard to clear, and gives an exceedingly strong
  angle for the CTs towards Ramp that will see past a B Ramp smoke" — [same] — making hut-CT the B anchor of
  last resort and the T clear priority.
- **Rotators:** Connector AWPer flexes post-stop; Hell/A1 the A-internal swing; CT-spawn the inter-site valve.
  All rotations cross open Door/Back-Site ground — smoke-gated, never free (MAP-TRN-003).
- **Info plays:** Ivy contact timing, Popdog walkway sound, Halls-door pressure count, Underpass/Showers
  grenade tells. Info without a paired anchor trade is donation — the lanes are too long for solo heroics
  (CS2Hype "too many angles for solo clears").
- **Retakes:** group retakes off Connector control; A retake converges Main + Ivy + Hell; B retake converges
  Connector + Back-Site + Upper. Pre-Door/Back-Site openness forces smoke-first retakes.
- **Anti-execute:** Main-mouth molotovs vs rush; Ivy-corner mollies vs walk contact; Ramp/Upper-hut mollies vs
  B contact. Economy matters: a 4A default with spent molotovs at 1:10 is a read, not a defense.
- **Uncertainty:** 4A is the default *because* the A rush ends rounds; collapsing to B on Ivy/Halls noise alone
  is the expensive mistake — the roamer's job (§3) is precisely to manufacture that noise. Move bodies on
  plant/commit or paired-call info, not on contact audio.

---

## 5. Role-dependent positional responsibilities [SYNTH]

### MAP-TRN-021 — Conditional bundles, never static spots

- **A Main anchor:** owns rush-stop contact iff given molotov support + spawn timing; otherwise owns mouth-delay
  + cross/connector-smoke call. Depends on: spawn, molotov inventory, rush-read from prior rounds.
- **Popdog/Underpass player:** owns walkway sound + B-Halls-facing flank guard; responsibility = arrive by spawn
  race, molotov on contact audio, never chase down the walkway.
- **Connector AWPer/rotator:** owns the spine — flex to pressured extremity pre-stop, reinforce B post-stop.
  Viable only with rush stopped + smoke cover for the crossing.
- **Ivy player:** owns long-corridor delay vs walk contact from new Stopper-position angles; responsibility =
  concede corridor to utility, hold A2 mouth with Hell support.
- **B solo:** owns info + retake life (see §4); any aggressive Ramp/Upper contact is bonus equity priced against
  the retake cost.
- **T mirror:** Main pair (contact + trade), Ivy extremity (pin A2), B/Popdog presence (pull rotate), roamer
  (manufacture the read that breaks 4A).

---

## 6. Utility and geometry interactions [SYNTH]

### MAP-TRN-022 — Tactical effect, NOT lineups

- **The four A smokes are the map's economy:** A cross, Ivy, Popdog, Connector — "all thrown from similar
  positions… learn in ten minutes" —
  [BLAST.tv guide](https://blast.tv/cs/news/how-to-play-train-in-cs2);
  full set in [BLAST Train smokes guide](https://blast.tv/cs/news/cs2-train-smokes).
  Analyzer reading: Train T-side viability ≈ these four smokes' states over time. A Main burst without cross +
  connector smokes is not an execute, it is a feed into the 4A crossfire.
- **B Ramp smoke ≠ B control:** the Upper hut angle "will see past a B Ramp smoke" — [same]. A B execute scored
  "smoked" on the 2-D radar is still watched. The analyzer must model the hut ray explicitly; hut uncleared +
  Ramp smoke up = T walk into a prepared angle.
- **Mollies are the rush-stop currency:** CT Main/Ivy/Ramp mollies convert rush geometry into time; spent
  mollies at 1:10 with 4A standing = readable defense (hit the extremity they can't re-molly).
- **Retake smokes gate everything:** open pre-Door / Back Site means retakes without smoke cover cross naked
  ground — score retake viability by smoke-state on those two spaces first.
- **Spring-Forward sightline removals change rays:** catwalk-outside-Z grating replaced (was see-through),
  Ivy-top fences now solid — pre/post-Mar-2025 visibility differs at exactly these spots; version-gate them.
- **Rain (CS2 Train ambience):** graphical/annoyance factor per BLAST — no evidenced gameplay effect; do not
  model.

---

## 7. Common questionable decisions and legitimate exceptions [SYNTH]

### MAP-TRN-023

- **B solo takes aggressive Ramp/Upper contact pre-rush-verdict and dies.** Looks like "contesting" on the
  radar; actually forfeits the retake anchor while 4A still needs no help. *Exception:* hard info that A is
  empty (paired Ivy+Main silence + Connector read) with numbers to trade.
- **Connector AWPer rotates to B on Ivy/Halls noise while the A rush is still live.** The roamer manufactured
  exactly this read (§3). *Exception:* bomb confirmed B-side or paired 4A-stack call with A mollies banked.
- **A Main pair re-peeks the mouth after the rush is stopped with utility spent.** Post-stop Main contact
  without molotov + cross-smoke support is donation. *Exception:* known isolated Ivy lurk to isolate, with
  Hell trade ready.
- **Retaking across open pre-Door/Back-Site without smoke.** Radar-short path, geometry-long exposure.
  *Exception:* bomb-timer + known isolated planter with no crossfire alive.
- **Treating the hut angle as smoked because B Ramp smoke is up.** The hut sees past it (§6). *Exception:* hut
  affirmatively mollied/cleared same-second.

---

## 8. Verified gameplay examples

- **EX-TRN-A — NAVI T-side concept series, Train (HLTV 2388127): "A Rush G3R8" + "Pistol A Rush G3R1" +
  "Fast B Upper Contact G3R6" + "Default A Split, rotation G3R2".** Economy-spanning evidence (gun + pistol
  rush, contact-paced Upper-B, default→split→rotation conversion). Positions per StratArchive catalog entries
  (opened 2026-10-15); tick-level demo verification NOT done — cue demos before encoding.
  *(Carried from researcher handoff; full URLs in sources.md.)*
- **EX-TRN-B — G2 T-side, Train: "Ivy Contact R4" + "A Split R1" + B-contact R7 (HLTV 2387384).** Three
  entrance×economy variants from one half — walk-tempo Ivy contact, pistol A-split, B-contact. Same
  verification limit as EX-TRN-A.
- **EX-TRN-C — Aurora vs Astralis, Train 13–8 (Aurora T-side): "Main/Ivy Split G2R8" + "fast upper duo lurk"
  + "Popdog A rotation"; Astralis "A Rush Hold G2R11" (CT mirror) + "Fast B Execute G2R16" (HLTV 2388085).**
  Both teams ran Main+Ivy splits on the same map — split as side-symmetric geometry exploitation. Same
  verification limit.
- **Meta datum — Austin Major Jun 2025: 14 picks / 62 bans, 55.7% CT / 44.3% T** —
  [bo3.gg](https://bo3.gg) (opened 2026-10-15 per researcher). CT-leaning, heavily banned: supports the
  rush-stop/retake-group doctrine over "T map" priors from Jan-2025 officials.

---

## 9. Observable data requirements and missing information

### MAP-TRN-024

- **Required per-round observables:** version tag (Nov-2024 rework vs post-Spring-Forward-2025 for Z-grating,
  Ivy fences, roof rail); per-player 3-D voxel + yard tag (A-yard / B-yard / spine); Connector-control state;
  the four A-smoke states over time; hut-clear state; B-solo alive state; rush-verdict timestamp; alive/economy/
  utility counts; objective clock.
- **Situation questions:**
  - **SQ-TRN-1 — How does Train geometry change the meaning of nearby teammates?** Observed: Underpass man
    ~10 m plan-view from Electrical/Hell; hut-CT vs Ramp-T sharing a ray; Ivy lurk + Main pack
    radar-equidistant. Objective: score support honestly. Responsibilities: none without shared lane + mutual
    sight + ≤~1 s traversable trade path. Alternatives: score by lane-sharing, not Euclidean distance.
    Info actually available: lane assignment + smoke/hut states, not radar dots. Evidence needed: lane-tagged
    positions + smoke-state timelines + trade-window frames.
  - **SQ-TRN-2 — B solo dead at 1:20 with A rush still live, 4v5.** Correct call depends on: contact type
    (info vs duel), retake-life value, A verdict state, economy. Evidence: death voxel + A-contact log +
    post-death retake outcome distribution.
  - **SQ-TRN-3 — Connector AWPer leaves spine on Ivy noise, A rush follows.** Allocation-vs-rotation
    separation (cf. Inferno E4 pattern): pre-round allocation under manufactured pressure ≠ rotation error.
    Evidence: noise timeline + award-path + plant/commit timestamp.
  - **SQ-TRN-4 — B execute into Ramp smoke with hut uncleared.** Tests hut-ray modeling (§6). Evidence:
    hut-clear state at entry second + entry outcome.
- **Missing:** tick-level demo verification for ALL catalog concepts; CT first-person comms for post-stop
  flex timing; post-Spring-Forward adaptation evidence; sections 4–7 researcher-grade citations.

---

## 10. Known uncertainties and research gaps

### MAP-TRN-025

1. **Researcher truncation:** §§4–7 above are parent-synthesized ([SYNTH]) from BLAST.tv + Dot Esports + the
   handoff's §§1–3 — citation density is lower than the other four map files. A follow-up pass should re-open
   the cited StratArchive/HLTV catalog URLs and ground each role/utility claim individually.
2. **No tick-level demo verification** for any EX-TRN concept — catalog-level evidence only.
3. **SPUNJ T-spawn-move musing (Jan 2025) unrecovered** — researcher cited it for Ivy starvation; source URL
   not preserved. Re-find before citing.
4. **CS2Hype/VPEsports callout contamination:** rejected for naming; any claim sourced only to them needs a
   BLAST/Dot-Esports/Valve corroboration.
5. **Meta window conflict:** Jan-2025 "T-sided feel" (cover-poor A) vs Austin Major 55.7% CT — different
   windows (release meta vs mature meta); quote only with window.
6. Screenshots/radars in BLAST/Dot-Esports guides are visualization only — no ray claim grounded on them.

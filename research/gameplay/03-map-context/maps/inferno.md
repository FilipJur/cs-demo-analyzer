# Inferno — Positioning & Spatial Context (CS2 Demo Analyzer)

**Status:** research only — no code, config, or schema changes.
**Concept IDs:** `MAP-INF-001` … `MAP-INF-010` (+ `E1–E11`, Situations A–D, `Q1–Q5`).
**Access date for all cited sources:** 2026-10-15 unless noted.
**Patch-period rule:** tag every positional claim pre/post **Mar-2025** (banana/coffin), **Oct-2025** (quad
visibility), **Mar-2026** (balcony/graveyard). Radars/screenshots are visualization only.
No map assets reproduced.

---

## 1. Scope and currency

### MAP-INF-001 — In the current pool, continuously

- Inferno is in the current (Premier Season 4 / 2026) Active Duty pool and has been continuously in-pool through
  CS2 launch to Aug 2026: the 2026 pool page lists Inferno alongside Ancient/Anubis/Dust2/Mirage/Nuke/Cache and
  notes it has "remained in the pool since 2017"; cs2metahistory records "in Active Duty since 2023-09-27,
  1,066 days through 2026-08-28," with **702 Tier-1 maps at all-time 50.2% CT** (regulation rounds, HLTV Majors +
  $600k–$2M LANs, Oct 2023–Aug 2026) —
  [Dot Esports pool guide, upd. Sep 2026](https://dotesports.com/counter-strike/news/all-cs2-competitive-active-duty-maps)
  + [cs2metahistory Inferno](https://cs2metahistory.com/maps/inferno/).
- Pool context: Anubis replaced Train ahead of Season 4 after Train spent ~1 year in pool; Cache replaced
  Overpass in Season 5 (Jul-2026 notes); 2026 reserve list is Train/Vertigo/Warden/Stronghold/Alpine/Office/Italy.
  "Train returned Jan 2025 replacing Vertigo" is superseded — do not encode as current — [same pool guide].
- Recent Valve Inferno geometry:
  - **2025-03-31 "Spring Forward"** — Banana resized toward CS:GO proportions; simplified backgrounds behind T
    ramp / Pit / B site / upper-B; removed step on Arch hallway sides; removed pixel gap at Coffin; adjusted
    balcony-step crates; global player/grenade collision pass (full Valve notes quoted in source) —
    [cs2metahistory 2025-03-31](https://cs2metahistory.com/updates/2025-03-31/)
    + [esports.gg Spring Forward notes](https://esports.gg/news/counter-strike-2/cs2-spring-forward-update-patch-notes/).
  - 2025-10-22: Quad/under-balcony visibility adjustments; **multi-smoke molotov-interaction fix** —
    [cs2metahistory 2025-10-22](https://cs2metahistory.com/updates/2025-10-22/).
  - 2025-11-12: skybox grenade-block fix — [cs2metahistory 2025-11-12](https://cs2metahistory.com/updates/2025-11-12/).
  - **2026-03-04: Balcony extended + Graveyard closed + 2nd-mid balcony-window clipping** (triple-confirmed
    verbatim across three independent republishers; NO pit-wall change — reject HLTV-search wording) —
    [steamanalyst](https://www.steamanalyst.com/updates/counter-strike-2-update-2026-03-04)
    + [cs2metahistory 2026-03-04](https://cs2metahistory.com/updates/2026-03-04/)
    + [dust2.us](https://www.dust2.us/news/71295/valve-rolls-out-changes-to-inferno-balcony-graveyard-in-march-4th-cs2-update).
  - 2026-07-08: top-of-mid pixel-boost clipping fix + Banana barrel material-blend fix; C4 remodel
    (precomputed/expanding) — [cs2metahistory 2026-07-08](https://cs2metahistory.com/updates/2026-07-08/).
  - 2024-04-25: removed top-mid overhang and bottom-banana overhangs — [cs2metahistory 2024-04-25](https://cs2metahistory.com/updates/2024-04-25/).
- Contemporary-evidence caveat: granular positional doctrine comes mostly from CS:GO-era Dignitas guides
  (2018–2021) plus a 2022 banana treatise; only the Dec-2025 Major final report and Dec-2024 map guide are
  CS2-current. Older examples used only where the geometric principle survives the patches above, flagged
  explicitly —
  [Dignitas CT setups (2018)](https://dignitas.gg/articles/counter-terrorist-setups-like-the-pros-inferno)
  + [Dignitas T-side (2019)](https://dignitas.gg/articles/blogs/CSGO/13815/inferno-t-side-strategy-guide-for-csgo)
  + [Dignitas A-execute (2020)](https://dignitas.gg/articles/strat-talk-blazing-inferno-a-a-site-execute-guide-inferno)
  + [friberg banana defense (2021)](https://dignitas.gg/articles/news/CSGO/15018/how-to-defend-banana-on-inferno-a-strategy-guide-with-dignitas-vie-friberg)
  + [tips.gg banana treatise (2022)](https://tips.gg/article/mastering-banana-control-on-inferno/).

---

## 2. Important spatial characteristics

### MAP-INF-002 — Three approaches, two sites; B utility-gated, A width-gated

- **Three contested approaches:** west Banana corridor (T ramp → sandbags/car → B site via coffins/CT/fountain);
  central mid complex (T spawn → top-mid/boiler → 2nd-mid → short/arch); east apartments chain
  (2nd-mid → apps → balcony → A site). A site has three entries (arch/long, short, balcony/apps); B has
  effectively one ground entry (banana) absent a CT-spawn flank — the structural reason B takes are utility-gated
  and A takes are width-gated — [T-side guide](https://dignitas.gg/articles/blogs/CSGO/13815/inferno-t-side-strategy-guide-for-csgo)
  + [A-execute guide](https://dignitas.gg/articles/strat-talk-blazing-inferno-a-a-site-execute-guide-inferno)
  + [cs2hype (Dec 2024)](https://cs2hype.com/maps/inferno).
- **Chokepoints:** banana (car/half-wall/sandbag segments), top-mid/boiler, apps corridor, arch hallway.
  CS2Hype calls banana/apps "bottlenecks where raw aim matters less than utility" and estimates ~54% CT at high
  skill — treat 54% as a guide estimate, not a measurement (vs 50.2% Tier-1 measured above).
- **Elevation / cover:** banana slopes down toward T side with car/half-wall/sandbag blockers; apps descends
  via stairs to balcony overlooking A; pit is a depressed A-site anchor pocket; coffins/new-box/quad/oranges
  partition B site; CT spawn sits centrally behind both sites feeding arch (A) and B. Rotation path is **through
  spawn/arch**, not across the map — route distance dominates.
- **2026 measured neutrality:** IEM Cologne Major 2026 Stage 1 — 15 maps / 18 bans, 55/45 CT, "most neutral";
  EWC groups Aug 2026 — 15 maps / 23 bans, 52/48 CT; veto study (19k series): raw-ban lead is a longevity
  artifact, 52.8% CT — Inferno is left in to absorb picks neutrally; banana is the equalizer; teams exploit the
  opponent's utility gap (Vitality rarely bans — utility + ZywOo banana AWP) —
  [bo3.gg Cologne](https://bo3.gg/news/inferno-was-the-most-picked-map-at-iem-cologne-major-2026-stage-1)
  + [bo3.gg EWC](https://bo3.gg/news/inferno-was-the-most-popular-map-during-the-group-stage-of-the-2026-ewc)
- **Measured extras:** plant-to-plant 3211u / 81 m; CT 7.9s vs T 16.7s to A-default; bomb 600u —
  [CSbePRO Inferno, upd. Oct 2026](https://csbepro.com/counter-strike-2/inferno/).
  Retake base rate (median-Premier, NOT pro): 26–38% by map/site, lowest Inferno B 25.9% —
  [NeuralBoost](https://neuralboost.gg/blog/cs2-maps-every-pool-the-rotation-history-and-what-each-map-demands).
  Utility spend ≈149 util dmg/player, ~2× Mirage/Dust2 — [metabot](https://metabot.gg/en/cs2/guides/cs2-inferno-guide).
- **Core thesis instantiations:**
  (a) pit↔A-site and coffins↔B-site pairs are metres apart yet mutually unsupportable once smoked/molotov'd or
  when the anchor faces the wrong entry — proximity without a shared angle or timing window is not support;
  (b) banana↔mid look adjacent on radar but are separated by T-spawn-to-contact timing and walls, so a banana
  player cannot help a mid fight;
  (c) apartments↔arch converge on A but a player committed inside apps cannot influence an arch wrap until
  exiting balcony — an unobstructed radar ray is not a tactical angle.
  Every support claim in §§4–5 therefore carries timing/utility/alive-player dependencies. (Synthesis from the
  banana treatise + CT setups + A-execute sources; labeling is inference, geometry evidenced.)

---

## 3. T-side principles

### MAP-INF-003 — Default triangle, slow banana, width-based A entries

- **Default triangle (banana + mid + apps), conditioned on spawns/economy:** best-spawn player flashes
  upper-mid from T ramp and mollies behind car/brick-wall; second player mollies apps from 2nd-mid — both in
  the opening seconds to deny CT peeks/info, not to take ground — [T-side guide](https://dignitas.gg/articles/blogs/CSGO/13815/inferno-t-side-strategy-guide-for-csgo).
  Banana control is then built **slowly**: double-molly car to cancel CT bottom-banana smoke time (12s fire ≈
  12s smoke), half-wall smoke variants (incl. the Vitality T-spawn mid-banana smoke that doesn't extinguish the
  half-wall molly, letting Ts slip to logs), always an anti-flash player facing the wall at top banana; clear
  sandbags with molotov+nade stack and expect CT flash-assisted fallback —
  [banana treatise](https://tips.gg/article/mastering-banana-control-on-inferno/).
- **Entries:**
  (i) *B default exec* — group banana, smoke CT + coffins (both throwable from banana), molly first-box row +
  quad, entry flash from rear, keep one smoke in reserve for the CT banana molly; pre-aim/fire the CT wall
  boost; post-plant expect counter-boost+flash. If B defenders hoarded utility, prefer a **pop hit** (flashes
  first, utility late) over a full exec whose airborne smokes telegraph the hit and invite counter-utility.
  (ii) *A via short+apps second contact* — long smoke to isolate, pit/balcony/moto smokes, apps player flashes
  for short entries and arrives as third contact for width; apps presence also defends a default plant from
  short+apps.
  (iii) *A-split short+long/arch* — clear boiler/long/apps first, short waits for long players near library
  door, then pincer; speed matters because rotates and smoke fade-outs start immediately.
- **Utility-heavy A variants** (conditional on 4+ smokes alive and early-round timing): pit-isolation smoke wall
  (hay→pit + moto + early arch smoke), gob-b short-molly exec (short smoke + pit/graveyard/balcony mollies,
  explode on fade). Replayability ≤2–3×/half — CT smoke-spam behind short smoke and reactive mollies punish
  repetition — [A-execute guide](https://dignitas.gg/articles/strat-talk-blazing-inferno-a-a-site-execute-guide-inferno).
- **Splits / lurks:** banana→construction or arch→CT-spawn→B splits work only when the far path is genuinely
  unattended (good teams never concede arch free — treat as situational); mid player holds the rotate gap during
  B execs; wall-of-smokes plant (CT + two path smokes, plant inside smoke at site edge) trades site control for
  a plant when numbers/utility are short.
- **Mid-round / post-plant:** banana ownership lets 4 Ts work A while one banana player denies CT info/rotation;
  post-plant on A hold short + apps (default plant defendable from both), plus site-boxes/pit per alive count
  (**graveyard closed Mar-2026** — post-plant nodes after that date differ); on B retain banana to block the
  CT-spawn retake path. Always trade (no stacking), teammate flashes only.
- **Utility constants (CS2, demo-checked):** smoke $300 / max-1 / 18s / landing-gated extinguish; HE disperses
  smoke; flash $200 multi-carry pop/stack; HE $300, 98/57 + slow; molotov $400T/$600CT, 2s fuse, no bounce,
  7.03s, ramp-40dps, stackable —
  [bo3.gg utility survey](https://bo3.gg/articles/all-about-utility-in-counter-strike-2)
  + [bo3.gg Inferno utility timings, Oct 2026, demo-checked](https://bo3.gg/articles/inferno-utility-timings-in-cs2-when-to-throw-smokes-flashes-molotovs-and-he).
- **Vitality T shape (analyst, May-2026, prose only — images JS-gated):** banana-led variety
  (full-rush / 2-man press / hold-while-Mid-hits); 1 mid + 2 banana info system; 3-banana-2-mid Logs +
  ropz deep lurk + flameZ mid; ZywOo AWP main-mid/backline, not permanent car —
  [caubycs Vitality–Inferno analysis](https://caubycs.substack.com/p/vitality-analysis-inferno).
  Counter-play per same analyst: pack/trap best on Banana; mid-aggro AWP; stop ropz Boiler.
---

## 4. CT-side principles

### MAP-INF-004 — Banana is a utility budget; A is prevention-over-retake

- **Banana doctrine is a utility-budget decision, not a position:** passive (Gambit-style) — best-spawn deep
  bottom-banana smoke + molly/nade logs, sandbags + CT-jiggle-info + 2nd-oranges/fountain crossfire, saving
  utility for late; vs aggressive — 3B early, bottom-mid smoke, molly+flash, AWPer to car, then if silence +
  smoke clears empty, stack 4A leaving AWPer solo with near-full utility. Pure passive concedes banana free;
  pure aggressive burns the late round. friberg: "always contest banana… but if Ts waste nothing and you waste
  everything early, they're better late — find the balance" —
  [banana treatise](https://tips.gg/article/mastering-banana-control-on-inferno/)
  + [friberg guide](https://dignitas.gg/articles/news/CSGO/15018/how-to-defend-banana-on-inferno-a-strategy-guide-with-dignitas-vie-friberg).
- **Anchoring:** B anchor (sandbags/car/coffins) must keep utility usage "on point" and adapt to T pressure;
  losing a CT early to constant banana duels is worse than conceding ground — fall back to site, re-contest with
  flash + site-thrown car incendiary forcing Ts into the coffins player. Banana is "really hard to play alone" —
  anchor + rotator bait and trade as a pair. A pit anchor carries multi-kill potential but must expect to be
  mollied/smoked once T utility arrives — never holds solo indefinitely.
- **Crossfires / rotations:** A pairs — site+balcony vs short/apps; pit-back + short-side both facing short;
  arch-holder pincers long wraps or delays CT-spawn B-splits with smoke/incendiary while site player slides to
  library; top-mid crossfire (short-side + arch-side) with apps player as swing. B pairs — car-close + car-site,
  sandbags + CT-jiggle, 2nd-oranges/fountain + CT. The **arch-side player is the rotation valve**: holds
  B-via-spawn splits, covers short pushes, reinforces either site — but moves only on bomb/plant info —
  [CT setups](https://dignitas.gg/articles/counter-terrorist-setups-like-the-pros-inferno).
- **Info plays:** CT bottom-banana smoke forces Ts into mid/2nd-mid or delayed banana (Fnatic–VP evidence §8);
  car-peek flashes, antenna-pop flashes vs car control, HE/nade stacks on logs/sandbags as reads. Top-mid
  smokes from CT-spawn and 2nd-mid deny AWPs and slow defaults.
- **Anti-execute / retakes:** banana molly+smoke stall past ~1:10 buys the read; B retake via CT spawn with
  banana-entrance + CT/coffins smokes and quad molly; **A retakes are structurally hard** (three entries, pit
  carry) so prevention (mid crossfire, arch delay) beats retake; A-retake balcony smoke from long cuts off apps
- **Solo-anchor governance (Soarne, Jul-2026, doctrine — no demos):** info = health bar, utility = clock;
  position matches banana state (owned ⇒ deeper; lost ~1:25 unwatched ⇒ defending execute+lurk+fake); smoke
  only when it buys real time; "B smoke down, banana pressure, I need one" = the help trigger; anti-flash per
  spot with post-flash fight; decisive calls ("three bomb seen CT smoke" = rotate; "two top no bomb" = lean);
  post-plant pick exactly one of deny/delay/hide (no triple-tasking); rotation commitment = bodies + bomb +
  utility-depth + timing, anchor holds the walkable entrance while support rotates first —
  [Soarne B-anchor](https://soarne.com/blog/how-do-you-anchor-inferno-b-site-alone-as-a-cs2-ct)
  + [Soarne rotation](https://soarne.com/blog/when-should-a-cs2-ct-rotate-off-the-bombsite-early).
  A-retake doctrine (post-Mar-2026): two vectors — rear Library/Moto/Arch + Mid→Short-Truck within 2 s
  ("ready at Truck" + "molotov in air"); clear order Pit/Mini-Pit → Graveyard → Back/Default in pairs —
  [bo3.gg A-retake](https://bo3.gg/articles/how-to-retake-a-site-on-inferno-after-the-mar26-rework).
- **Uncertainty handling (3-stage):** smoke → position + check save if none; movement → molly/HE transit;
  push → flash/2nd-HE. Banana contact before ~0:45 ⇒ likely B exec; silence ⇒ fake or A commit — but the read
  expires against double-exec teams (bait B utility with mid/apps distraction, wait, re-hit; needs top-mid
  control).

---

## 5. Role-dependent positional responsibilities

### MAP-INF-005 — Conditional bundles, never static spots

- **B anchor (sandbags→car→coffins):** owns early banana contact **iff** given car/AWP setup or nade-stack
  support and T pressure is contestable; otherwise owns site-delay (coffins/new-box/quad) + late utility.
  Depends on: spawn quality, rotator utility drops, T double-molly cadence, alive count.
- **B rotator / arch-side CT:** owns information (banana count, mid noise), arch-hold vs long-wrap/CT-spawn
  split, and first rotation — moves only on plant/commit or paired A-stack call; dropping utility for B before
  rotating is part of the job. Depends on: A-site stability, arch smoke cover, bomb intel. The karrigan form
  is a utility portfolio, not a spot.
- **A short-side pair:** owns boiler/top-mid denial and short funnel; pit-back + short-side stack damage facing
  short; apps-swing player owns balcony/apps re-entry. Depends on: long smoke status, apps control, rifle/AWP mix.
  A lone-A player vs concurrent far-lane space is an unsatisfiable position — viability is conditional on the
  other lanes (E4 pattern, §8).
- **Mid/arch AWPer:** owns top-mid pick denial and car-banana flex in aggressive calls; left alone on B only
  after confirmed-empty banana + 4A stack. Depends on: silence duration, smoke-fade timing, solo-utility remainder.
  (Coffins AWP killed by coffins smoke per official lineup set; ZywOo banana AWP is the reason Vitality rarely
  bans.)
- **T roles mirror:** entry pair (banana/short), second-contact apps player, mid lurker holding rotate gap, rear
  utility/flash thrower — each entry conditional on the isolating smoke and the apps/mid control check.

---

## 6. Utility and geometry interactions

### MAP-INF-006 — Tactical effect only

- **Banana control utility = time, not kills:** CT deep smoke + front molly/nade stalls past 1:10; T double
  car-molly cancels 12s of CT smoke; half-wall/Vitality mid-banana smokes manufacture "virtual control" that
  freezes CT aggression without a duel. Whoever owns banana at ~0:30 dictates whether Ts must spend everything
  on A — the round's information backbone.
- **Post-Mar-2025 widened banana wall** gives extra cross-cover, occasional one-way, an unseen info spot —
  geometry shifts extinguish/flash timing (coach first-person: Hecklerr ex-pro IGL VOD, May 2025 — Karrigan
  smoke arch-middle corner double jump-throw: wall spot + view-block + rush-molly extinguish; two forms —
  direct corner-forward on smoke-expiry vs passive smoke-push with retake-flash — [YouTube](https://www.youtube.com/watch?v=gpTZT2mEMLo)).
- **Top-mid smokes** (CT-spawn→top-mid; 2nd-mid→short/long/arch) erase AWP sightlines and break the short/arch
  crossfire, converting a geometry disadvantage into a timed corridor. CT mid smoke funnels Ts and buys the
  arch-rotator seconds —
  [skin.club smokes, upd. Jan 2026](https://community.skin.club/en/articles/best-cs2-smoke-spots-on-inferno).
- **Cover / angle effects:** banana walls/half-wall/car/sandbags make banana a flash-and-molly corridor with no
  escape — hence flash-first doctrine; **coffin pixel gap removed Mar-2025** — old one-way/pixel holds must not
  be encoded; balcony crates step reliably + balcony extended Mar-2026 (apps-entry duels change);
  quad/under-balcony visibility pass Oct-2025 (pit-side clearing changes); arch hallway side-steps removed
  (cleaner wide-swing timing).
- **Static walls / openings:** Z-door catwalk grating and ivy-top fences now solid (sightline removals);
  church/boiler roof geometry fixed.
- **Sightline≠visibility:** volumetric smoke blooms (Vitality mid-banana bloom covers log crossings while molly
  burns behind it); shadow-through-window bug fixed; dark-spot/material-blend fixes; background simplifications
  (T ramp, pit, B) change readability without moving collision. Official minimum lineup set: CT Boost stand,
  Coffins jump, Left Top Mid stand, Moto jump, Banana jump, Half-Wall jump (5/7 jump-throws) —
  [metabot.gg lineups](https://metabot.gg/en/cs2/map/de_inferno/lineups).
- **Retake utility:** B — CT/coffins smokes + quad/new-box mollies + rear entry flash; A — moto/arch/pit
  smokes + pit mollies, noting Mar-2026 graveyard closure kills old graveyard nodes.
- **Analyzer rule:** encode support as angle × timing × utility-state, never as distance; encode availability
  as smoke/fire/position-conditioned visibility, never as a clear ray. The close-and-blind triad
  (pit anchor with a moto smoke in his face, banana player a wall from mid, apps player a door from arch) are
  canonical negative training cases.

---

## 7. Common questionable decisions and legitimate exceptions

### MAP-INF-007 — Each is a dependency vector, never a static verdict

- **Q1: B anchor dry-peeks banana alone repeatedly vs double-molly/flash T pressure.** Bad: trades the site's
  only delay for ≤1 kill and gifts numbers. *Exception:* legitimate when paired (teammate antenna-flash + site
  car-incendiary cross) and T utility is counted out.
- **Q2: Arch rotator leaves on first A noise with banana count unknown.** Bad: A noise is the cheapest fake on
  Inferno; banana-unknown + no plant = stay (15s+ rotation is unrefundable). *Exception:* bomb confirmed/planted,
  or banana affirmatively cleared (AWPer saw empty post-smoke + silence) with a 4A stack call.
- **Q3: Ts enter banana/B "dry" (no smoke+molly).** Bad: corridor with no escape — nade stacks and car peeks
  farm entries. *Exception:* eco/force with no utility where contact-forcing is the only win path; still
  flash-first, never walk-in.
- **Q4: CTs burn full banana utility early every round.** Bad: double-exec (bait, wait, re-hit) into empty hands;
  treat an extinguished molly as delay booked at zero on bloom (pre-Oct-2025 multi-smoke interaction was buggy).
  *Exception:* pistol/force or known fast-B tendency where early stall directly converts.
- **Q5: Repeating gob-b short-molly or smoke-wall A exec >3×/half (or any graveyard lineup post-Mar-2026).**
  Bad: CT smoke-spam/reactive mollies scale with repetition. *Exception:* opponent shows no adaptation — exploit
  to the end.

---

## 8. Verified gameplay examples

### MAP-INF-008

- **E1 (CS2-current, verified): Vitality vs FaZe, StarLadder Budapest Major 2025 grand final, Map 3 Inferno
  (FaZe pick), Dec 14 2025, Vitality 13–9 FaZe.** Both sides emphasized T-side banana pushes while A execs were
  rare; R4 ropz multi-kill "saved" Vitality from **Pit on A** (anchor carry); R5 mezii clutch defuse + later
  B-position double denying a plant + smoke kills; ZywOo Round-11 retake; FaZe frozen nearly solo-saved B in 2nd
  pistols (HE + holds) and Round-21 CT banana push created chaos. Patch period: post-2025-10-22 visibility,
  **pre-2026-03-04** balcony/graveyard rework. No footage timestamps verifiable from the opened report — cue
  VOD/demos for tick-level positions —
  [esports.gg GF details](https://esports.gg/news/counter-strike-2/vitality-faze-budapest-major-2025-grand-final-details/).
- **E4 (round-resolved): IEM Katowice 2024 QF, FaZe 2–0 G2 — Map 1 Inferno 13–9, ROUND 5.** FaZe
  (broky/frozen/karrigan/rain/ropz) vs G2 (HooXi/huNter/m0NESY/nexa/NiKo). R5 = the three-rifle-save round:
  single synchronous extinguish + team-safe god-flash substitutes for an $800+ exchange; frozen banana entries,
  ropz concurrent A-space vs lone m0NESY wins the round; G2 saves. VOD: ESL Archives Map1
  `https://www.youtube.com/watch?v=_gB_mqTAYtY`, **R5 window 8:17–10:45** (chapters R1 0:00 … R22 52:46);
  R4 cumulative (FaZe 3–17 kills, G2 17–3) confirms the 0–4 scoreline entering R5. Feb-2024 = pre-resize +
  pre-interaction-fix geometry —
  [bo3.gg match](https://bo3.gg/matches/faze-vs-g2-09-02-2024) + round tabs + VOD transcript.
- **E2 verification upgrade (Oct-2026): Vitality vs MOUZ, EPL S24 GF, Spodek, Inferno 13–7 (MOUZ pick;**
  series Cache 13–8 / Inferno 13–7 / Dust2 16–12 OT).** ESL official: 3–0, fourth EPL title, ZywOo MVP, ropz
  sixth. Veto (−Ancient/−Anubis/+Cache/+Inferno/+Dust2/+Mirage, Nuke leftover) via DFRAG.
  **VOD v2897804998: Cache 4:25:18, Inferno 5:29:44, Dust2 6:32:18 — cue 5:29:44** — post-Mar-2026 + post-Jul-08
  + new-C4 geometry (current). StratArchive round tags (opened, footage not reviewed): "Vitality CT Mid Push
  G2R12", "MOUZ Default A G2R9", "Vitality CT A4B1 G2R6". Secondary: 9–3 half, flameZ 4-kill (2×MP9 2×Galil)
  B defence R3 — [spawnsy](https://spawnsy.com/en/article/vitality-win-esl-pro-league-season-24-katowice).
- **E2 (CS:GO-era, principle-verified): Fnatic (Pronax) vs Virtus.Pro — CT bottom-banana smoke system.** CTs
  smoke bottom banana; VP forced into mid/2nd-mid, attempt B via CT spawn, get "sandwiched" (Olofmeister leaves
  Krimz on banana, plays CT-spawn side); next round same smoke baits a reckless VP smoke-push punished fast
  (match-point sequence). Clip: `youtu.be/JIhXRkQopFM?t=1h4s`. Applicability: information/routing effect
  survives; exact timings do NOT transfer past 2025 banana resize + collision pass —
  [CT setups](https://dignitas.gg/articles/counter-terrorist-setups-like-the-pros-inferno).
- **E3 (CS:GO-era, principle-verified): Dignitas vs EnVyUs, Red Dot Invitational final — banana opener → mid
  punish.** MSL banana opening frags force French response toward A/mid; tenzki+Rubino short double-hold vs
  boiler/top-mid (Rubino trades tenzki), B rotator arrives arch-side to close the 3v1. Clip:
  `youtu.be/9af-J2y4JMM?t=20m10s`. Same patch caveat as E2.
- **Corroboration (not round-verified):** friberg on utility balance + team-play dictum; s1mple-system AWP-solo-B
  and Heroic double-exec concept from the banana treatise; FaZe rain B-hold film (CS:GO logic transfers —
  2-man probe, 3-man stack, low-util bank-car, delayed re-take dies to a better flash; in-video rounds, VOD via
  skybox.gg unopened).
- **Veto-only context (no Inferno rounds — bounds, not evidence):** Spirit double-refused Inferno twice
  (EPL S24 GF + 3rd-place match); MOUZ–Vitality Porto SF Sep 2026 decider Inferno unplayed (Vitality mezii→jL
  paternity stand-in) —
  [cs2news Porto](https://cs2news.com/news/mouz-break-vitality-curse-with-2-0-sweep-to-reach-blast-open-porto-final).

---

## 9. Observable data requirements and missing information

### MAP-INF-009

- **Situation A (required): when should a B anchor remain on site despite pressure elsewhere?** Observed: anchor
  positions (sandbags/car/coffins/CT), rotator locus (arch/CT spawn/B), banana count + utility-exchange log,
  A-noise type (contact vs damage vs bomb), clock, alive/economy both sides, objective (deny plant vs save).
  Responsibilities: anchor owns site-delay + late utility; rotator owns arch/CT-spawn split + first move.
  Alternatives: (i) anchor holds site, rotator delays arch; (ii) both collapse B; (iii) anchor peeks banana for
  info. Decision factors: bomb/plant confirmation (only hard trigger), banana affirmatively cleared vs merely
  quiet, T utility remaining (double-exec threat), numbers (4v5+ favors concede-and-retake), clock (<0:30 favors
  site lock). Evidence needed: demo ticks for banana-clear call, utility inventories, VOD comms; E1's R5 mezii
  B-stay (plant-denial double) is the positive template, E2's Krimz-left-on-banana the template for holding the
  read. Sub-state: hold requires a 2-man minimum (start + anti-flash trader), all spots cleared or fictional;
  validity needs delay-utility alive + unextinguished AND support tradeable pre-contact.
- **Situation B: arch-rotator commit timing on A-split signs.** Needs: boiler/long/apps contact ticks,
  arch-smoke status, B-anchor alive/utility, bomb intel. Stay vs rotate hinges on whether long presence is wrap
  or fake — banana count is the tiebreaker. (E4 allocation-vs-rotation separation: G2 stacked 4 A incl. lone-B
  while ropz walked A — pre-round allocation under banana pressure, scored separately from rotation error.)
- **Situation C: banana re-aggression after losing control.** Needs: T utility expended (car mollies used?), CT
  flash availability (antenna-pop ready?), numbers, clock. Re-hit only paired with flash + site incendiary;
  solo re-peek is the documented failure mode (E4 inversion branch: extinguish-then-flash-then-exit vs scripted
  molly; canonical wait-out + deep/broom/flash + paired peek).
- **Situation D: A-retake route (short vs arch/library) after plant.** Needs: plant spot (default vs pit-side),
  T apps/short retention, CT utility (balcony smoke, pit molly), numbers, kit. Default plant ⇒ short+apps pinch
  (post-Mar-2026: no graveyard, extended-balcony retention, CT balcony smoke may shift); pit-side ⇒ moto smoke +
  isolation first. Sequence: smoke-known or bank last for ninja, flash-peek, HE/molly tucked pit/wine.
- **Missing from opened sources:** tick-level coordinates/HP/utility inventories for E1 rounds; VOD timestamps;
  current-pro comms explaining 2026 balcony/graveyard adaptations; AWPer spawn-condition tables; force-buy
  banana protocols; post-Mar-2026 pro comms/adaptations/relearned lineups; measured post-rework exec/retake
  rates and event splits.

---

## 10. Known uncertainties and research gaps

### MAP-INF-010

1. No opened source gives round tick/VOD timestamps for the Major final — E1 is match/map/side/round-verified,
   not footage-verified; cue the StarLadder VOD/demos before encoding positions.
2. Dignitas/friberg/tips.gg doctrine is CS:GO-era; validated only at principle level against CS2 geometry.
   Quantitative transfer (timings, molly durations vs resized banana, removed coffin gap, solid ivy/Z gratings,
   extended balcony/closed graveyard) is unmeasured in opened sources.
3. Contradiction preserved: CS2Hype "~54% CT" vs cs2metahistory Tier-1 50.2% CT all-time — different
   populations/periods; use 50.2% as measured, 54% as guide claim. Ranked prior 46.5/53.5% CI-includes-50 kept
   separate; Katowice n=2 ignored.
4. **Pit-wall conflict (unverified, needs demo):** HLTV snippet + skin.club (Oct 2026) + critfeed callouts claim
   "wall above Pit raised" / height tweaks vs verbatim 3-change Valve notes (Balcony extended + Graveyard closed
   + 2nd-mid window clipping) — treat as unverified conflict.
5. Unopened: Liquipedia/Inferno (403), HLTV match/news pages (429), pley.gg rain B-hold (verification wall),
   CSDB callouts (429) — B-anchor first-person (rain) and callout-complete inventory unverified. Attempted 2026-10-15.
6. No verified 2026 pro adaptations to balcony-extension/graveyard-closure or July-2026 top-mid pixel-boost fix
   found — flag any encoded A-site node as pre/post-Mar-2026. Rework winner open ("jury out"): no post-rework
   exec/retake measurement or relearned lineups.
7. Transfer boundaries unmeasured: CS:GO→CS2 resize, coffin gap, ivy/Z, balcony/graveyard + Oct-2025
   interaction fix + Jul-2026 C4 remodel. Pre-fix extinguish / pre-Jul-2026 radii don't transfer.

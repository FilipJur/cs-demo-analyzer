# Dust2 — Positioning & Spatial Context (CS2 Demo Analyzer)

**Status:** research only — no code, config, or schema changes.
**Concept IDs:** `MAP-DST-001` … `MAP-DST-080` (+ `EX-1…5`, `Q1…Q7`).
**Access date for all cited sources:** 2026-10-16 (researcher pass).
**Patch-period rule:** tag every positional claim pre/post **Apr-2026 Xbox rework** (28-Apr uncover + 29-Apr
corner block). Radars/screenshots are visualization only. No map assets reproduced.

---

## 1. Scope and currency

### MAP-DST-001 — In pool, Oct 2026; MAP-DST-002/003/004 — tenure

- Dust2 **IS** Active Duty. Pool: Ancient / Anubis / Cache / Dust2 / Inferno / Mirage / Nuke —
  [r1gg pool guide](https://r1gg.com/cs2/guides/cs2-map-pool) (evidences 7-map list) corroborated by Valve S5
  newsentry: "Cache has officially arrived, and replaces Overpass in the active duty pool" —
  [counter-strike.net](https://www.counter-strike.net/newsentry/701021228894257508?l=english).
- Returned **25 Apr 2024** replacing Overpass (with Inferno arch-cover removal, left-hand viewmodel, radar-zoom) —
  [dust2.us](https://www.dust2.us/news/47792/overpass-swapped-for-dust2-valve-adds-left-hand-viewmodel).
- Train Jan-2025 replacing Vertigo (06-Jan-2025, Austin Major pool Dust2/Mirage/Inferno/Nuke/Ancient/Anubis/Train) —
  [dust2.us](https://www.dust2.us/news/56700/train-will-replace-vertigo-for-the-austin-major);
  Train OUT Jan-2026 (Anubis replaced Train 19-Jan-2026 S4; Anubis had left 15-Jul-2025 for Overpass) —
  [dust2.us](https://www.dust2.us/news/69485/breaking-anubis-returns-to-map-pool-replacing-train).
  Dust2 continuous since Apr-2024.

### MAP-DST-005 — Geometry 2026 (Xbox volatility — version-gate everything mid)

- **28 Apr 2026:** "Uncovered Mid Box (Xbox) to reveal a previously hidden jump spot. On purpose this time" —
  [Valve newsentry](https://www.counter-strike.net/newsentry/508486359454843160?l=english).
- **29 Apr 2026:** "Blocked visibility through corner of Mid Box (Xbox)" —
  [Valve newsentry](https://www.counter-strike.net/newsentry/702141174212723087?l=english).
- Full list: 26-Apr-2024 grenade fall-through above doors; 02-Jul-2024 hole brick B; 22-Jul-2024 crate stack
  outside CT toward A; 02-Oct-2024 clipping B; 28-Oct-2024 gap geometry; 06-Feb-2025 radar; 11-Mar-2026 pixel gap
  door Outside Long; 08-Jul-2026 pixel gap + clipping Outside Tunnel —
  [neuralboost changelog](https://neuralboost.gg/blog/counter-strike-2-dust-ii-map-changes-xbox-and-tunnels).
  Build 1.41.8.8 — [csbepro](https://csbepro.com/counter-strike-2/dust-2/).
- **Pre-Apr-2026 mid lineups/visibility are suspect** — rebuilt box + jump-spot + corner-block (MAP-DST-052).

### MAP-DST-006 — Limits

Liquipedia 403; HLTV news 429; Valve updates index JS-shell only. No Launders/mauisnake 2024–25 Dust2 breakdown
found. Dignitas-2018 / scope-2020 / friberg-2021 / PCGamer-2016 used only where lane logic is stable.

### Balance baseline

2301 maps / 40368 rounds, CT 51.1% / T 48.9%, ban 45%, pick 38% (most-picked), 21.5 rounds avg, through
15-Oct-2026 — [esportsodds.gg](https://esportsodds.gg/maps) + dust2 page.

---

## 2. Important spatial characteristics

### MAP-DST-010 — Lanes

- **Long:** Outside-Long / Doors / A-Long / Pit / Pit-Plat / Side-Pit / Blue / Corner / Cross / Ramp.
- **Mid:** Suicide / Top-Mid / Doors / Xbox / Catwalk / Stairs / Short / Extended-A / Ninja / Goose; CT-Mid /
  Doors / Window (Hole) / Boxes / Scaffolding.
- **Tunnels:** Outside / T-Plat / Ramp / Upper / Stairs / Lower / arch→Plat / Back-Plat / Car / Closet / Fence.
- 24 official vs 29 player names; radar `de_dust2_v2` —
  [cs2.eu complete guide](https://cs2.eu/news/cs2-dust2-complete-map-guide-callouts-strategies-and-tips);
  CSbePRO lists.

### MAP-DST-011 — Proximity≠support, thesis A (quantified)

Plant-to-plant 2472u ≈ 63 m straight-line, but A→B along-map 2665u = 67.6 m = **10.7s knife / 12.4s AK /
13.3s AWP**. CT-Spawn→A 842u = 3.4s vs →B 1825u = 7.3s; T-Spawn→B 3925u = 15.7s vs →A Short 4014u = 16.1s, via
Long 4335u = 17.3s; T-spread ±1.6s, CT ±0.7s (Suicide-drop excluded) —
[CSbePRO timings](https://csbepro.com/counter-strike-2/dust-2/).
**Long-A ↔ Tunnels/B look adjacent on radar but are 10s+ apart. Long pressure is NOT B support; the Long↔B
swing is slow by design** —
[BoostRoom guide](https://boostroom.com/blog/dust2-guide-cs2-best-positions-defaults-and-mid-control)
(rotation-punishment).

### MAP-DST-012 — Chokes

First-seen timings: Doors from Corner 2166u = 8.7s knife; Top-Mid 1513u = 6.1s; Upper 2305u = 9.2s;
Short-Stairs 2886u = 11.5s. Contested: Corner/Pit/Cross; Doors/Top-Mid/Xbox; Upper/Lower entries — [CSbePRO].

### MAP-DST-013 — Elevation

Catwalk/Stairs→Short above site; Pit sunken vs Long; Ramp up; Suicide drop — unmeasured flat-radar limit
(CSbePRO caveat).

### MAP-DST-014 — Ray≠availability, thesis B

Double-doors, Xbox, Window gap, Scaffolding, Short-Boost make visibility door-state/bloom-dependent. Duel lines
are radar straight-lines, height-excluded — viz-only, never collision. Key rays: Corner→Doors 840u = 21.3 m;
Pit→ramp-top 2112u = 53.6 m (longest); Top-Mid→CT-Mid 1695u = 43 m; Upper→Plat 814u = 20.7 m → Back-Plat 1277u =
32.4 m; Extended-A 6 spots 18.5–31.5 m. Post-Apr-29 corner identity + jump mechanics unverified in-game.

---

## 3. T-side principles

All conditional on spawn / economy / alive / pressure / info / objective.

### MAP-DST-020 — Defaults

1 Outside-Long/Doors + 1 AWP T-Spawn/Top-Mid + 1 helper + 2 tunnels (Upper denies push, Lower guards Cat +
helps Mid); bomb Top-Mid↔Outside-Long, unseen + rotatable —
[Dignitas default strategies, 2018](https://dignitas.gg/articles/default-strategies-for-t-side-on-de_dust2)
(B-split / Long / A-split / Cat / BBB); BoostRoom + cs2.eu 2026 corroborate.
2026 rule: take control, force reaction, then split.

### MAP-DST-021 — Entries (timing-gated)

- Long needs corner smoke + flash, else CT Corner AWP ~8.4s [7.1s + 1.27s scope] beats T AK 10.1s at 21.3 m.
- Mid needs CT-Spawn smoke [Xbox corner→window above doors], else CT Doors AWP ~4.8s [3.5s] beats T Top-Mid
  6.1s / 7.0s AK.
- B needs tunnel flash + Window smoke + Plat molly — Dignitas throws + CSbePRO.
- Count reads: ≤1 crossing implies A-stack, ≥3 implies Mid/B commit; CT cross-smoke/HE denies intel; deeper
  smoke implies CT mid-play → Lower watch —
  [Dignitas mid-control/B-split, 2016](https://dignitas.gg/articles/t-side-guides-dust-ii-mid-control-and-b-split).

### MAP-DST-022 — Splits / space

- B-split: 2 tunnels clear/distract + 3 Mid→Door/Window, need ≥2 surviving; A-split: 3 Long + 2 Cat→Short
  [Xbox-top smoke, Lower-arch jump + site/Goose molly]; Long+Short / Mid→B punish stacks — Dignitas executes;
  BoostRoom trap.
- Mid dominance via flash/prefire forces passive CTs, denies info, keeps numbers split; hold rotates late.
- Mid is the hinge to Lower/B, the Long-flank origin, the rotation-info source; convert to split/flank —
  [csstatlab mid control](https://csstatlab.com/academy/maps/dust2-mid-control) (doors-smoke + conversion +
  fall-to-cat/B-doors).
- Lurk opposite extremity only iff main group can trade + info shared; silent hide with bomb-remote while the
  team hits a stack = disconnected.

### MAP-DST-023 — Post-plant

A: spread Long/Short/site, clear Goose/boxes/Ramp/Car. B: tunnels + site crossfire, watch Window/Mid. B plant
zone 91 m² (384×368u) vs A 44 m² L-shape (272×288u) — B needs wider spread — CSbePRO Bombsites + BoostRoom.

---

## 4. CT-side principles

### MAP-DST-030 — Default 2-1-2

1 Long + 1 Short/site + 1 Mid [CT-Spawn/boost] + 1 tunnels + 1 B site/Window; AWPs at Doors / Long-pit / B-Plat.
Variants Long/B/Mid-heavy/safe by tendency/spawn/econ —
[cs2.eu setup](https://cs2.eu/news/cs2-dust2-complete-map-guide-callouts-strategies-and-tips);
[BoostRoom](https://boostroom.com/blog/dust2-guide-cs2-best-positions-defaults-and-mid-control);
[cs2caller full default](https://cs2caller.com/dust2/ct/full-buy/dust2-ct-full-default-2-1-2)
(P1 Corner / P2 Catwalk / P3 CT-Mid AWP / P4 B-Plat / P5 CT-Spawn rotator).

### MAP-DST-031 — Anchor Long

Contest with flash/support then fall Pit→Corner→Car→site in stages; Corner first contact, Pit trades, never
same-time peek; solo dry re-peek feeds. Early 2-Long pop-flash to Pit, then second falls to A/Mid on info;
Short above stairs ready to drop; Mid gives Cat info + delays split; B Plat/site falls back —
BoostRoom; [PC Gamer CT guide, 2016](https://www.pcgamer.com/csgo-dust2-ct-guide/)
(2-Long + pop-flash + Short/Mid/B roles).

### MAP-DST-032 — Mid flex / info

Watch Doors/Lower/Cat, call the split in 1–2 s; don't duel alone every round — mix passive/smoke/flash; if
Long lost, convert to Short/site help. With AWP vs catwalk: cannot peek without risk — must call loss of Cat.
Outnumbered → info + picks, jiggle not wide, fall to cat/B-doors when smoked — CSStatLab Mid.

### MAP-DST-033 — B delay-first / rotations

Call Upper numbers early; smoke/flash choke, survive the 10.7s A-help window; lone early Upper peek with no
trade = loss. If Mid lost, B is exposed via Door/Window. Retake starts pre-plant via info; Long player: push
T-spawn backstab vs fall toward B vs hold — depends on tunnel/mid sightings, Short status, time. Don't
over-rotate — B-fake→A-split ~15 s — cs2.eu Tips.

### MAP-DST-034 — Retake

B-retake = two-sided synchronized entry (T-crossfire advantage; Door smoke + flash + Plat molly; left/right
assignment; many-tunnels + passive-outside variant; save-vs-go) —
[Dignitas/friberg B-retake, 2021](https://dignitas.gg/articles/how-to-retake-the-b-site-on-dust2-with-tips-from-dignitasvie-friberg).
Dated alternate: 2B crossfire → 1:45 anti-rush flash + tunnel-exit smoke → 1:35 scaffolding smoke + 1:30 Window
sky-flash Upper retake —
[scope.gg 2-3B aggressive default, 2020](https://blog.scope.gg/out-of-meta-ct-2-3b-aggressive-default-on-dust2-en/)
(pre-2024 idea only).

---

## 5. Role-dependent responsibilities

- **MAP-DST-040 Long CT** holds/calls iff spawn ≤7.5 s + flash or teammate flash; else info + fall. Dead-no-call
  while Mid duels → A-split risk. Depends on spawn/utility/A-alive.
- **MAP-DST-041 Short/Cat CT** denies Short iff Mid info + site anchor alive; if Long lost, prioritize Short
  over Mid re-peek. May peek Lower iff Mid has Cat view. Depends on Long/Mid.
- **MAP-DST-042 Mid CT** calls Cat/Lower/split; supports B vs Mid-to-B iff B pressured + numbers allow; abandons
  Mid for Short/site iff A-hit confirmed.
- **MAP-DST-043 B anchor/support** calls Upper-sound; pushes tunnels only as mix-up iff T passive + loss
  affordable; otherwise delays. Window/Door fights Mid-to-B coordinated. With Mid flash ready can take 2 then
  fall. Depends on Mid/utility/clock.
- **MAP-DST-044 T Long/Mid/Tunnel:** Long-doors iff AWP covers Mid + bomb central; Mid→Xbox iff smoke bloomed +
  Lower watched + flash pre-fight; Upper holds iff B-push threat; hold taken space for push info. Coach T.c on
  comms/negligence collapse vs MOUZ Mar-2024 —
  [dust2.us](https://www.dust2.us/news/46412/tc-we-stopped-talking-we-got-negligent) (comms/mentality, not geometry).

---

## 6. Utility and geometry interactions (effect, not lineups)

- **MAP-DST-050 Long:** Corner smoke removes the 21 m ray — converts the 10.1 s dry entry duel into a cross;
  cross-smoke kills the Short→Long pickoff. Must bloom pre-push — Dignitas. Support flash blinds Doors + Pit,
  taxi-flash covers spawn/blue/left when stuck, solo pop detonates on arrival; car/default/post-plant mollys
  clear/hold — [GetReplay lineups, 30-Jul-2026](https://getreplay.gg/en/articles/cs2-dust2-lineups).
- **MAP-DST-051 Mid:** CT-Spawn smoke removes the Spawn→Doors ray; Xbox-top removes the CT-Mid AWP ray onto the
  Cat ascent; gates the 6.1 s → 11.5 s Short path. Variants: T-spawn / Suicide / Lower / Xbox-waterfall +
  left-CT-mid + self-flash — Dignitas + cs2.eu + GetReplay Mid. HE black-smoke save-substitute needs timing;
  Short-boost from CT boxes speeds Short but leaves 1 Long — needs covering smoke (PC Gamer tricks).
- **MAP-DST-052 Xbox volatility:** pre-Apr-2026 lineups/visibility suspect — rebuilt + jump-spot + corner-block
  (CSbePRO + Valve notes).
- **MAP-DST-053 Tunnels/B:** Window + Plat molly collapse the Plat 20.7 m / Back-Plat 32.4 m crossfire; B is the
  most efficient — 3 nades + rush; fast ramp Doors-smoke pre-reaction; mid-to-B smoke must leave no Long gap;
  post-plant Doors resmoke delays retake; fence mollys clear; Upper-roof sky-nades need no exposure — scope.gg +
  Dignitas B-rush + GetReplay B.
- **MAP-DST-054 Short/A:** Extended-A 6 spots 18.5–31.5 m; no unscoped rifle covers all — AK 21.7 m boxes only,
  M4s +Cross/ramp-bottom, Car/Goose 31 m need scope; Mid 43 m AWP/auto-only; Pit→ramp-top 53.6 m longest. Dry
  Short/Mid/Pit-rifle quantifiably wrong. CT Long-Doors smoke denies early pick; deep Long forces
  walk-through/wait; B-car anti-rush + B-retake Doors flash + close-mid molly buy time (CSbePRO
  Weapons/Mistakes + GetReplay defense).
- **MAP-DST-055 B-retake:** Door smoke isolates outside; flash must cover site without blinding teammates; Plat
  incendiary forces out; first-in left / second right; many-tunnels + passive-outside baits push-out (friberg
  save-check).

---

## 7. Common questionable decisions and legitimate exceptions

- **MAP-DST-060 Q1 — Long: useful pressure vs disconnected?** Observed: Corner/Pit contact + cross-smoke vs
  silent Doors hold; bomb central vs remote B; team splitting vs forcing B. Objective: fix rotate vs save exit.
  Responsibility: draw utility/rotate + live info. Alternatives: join Mid/Cat vs stay. Info: CT numbers/utility.
  Factors: clock (>0:40 pressure / <0:20 commit), alive, CT econ/stack. **Useful iff ≥1 CT reacts + teammates
  sync the opposite hit; disconnected iff silent + bomb remote + no info + team hits a stack.** Evidence: rotate
  timing, bomb path, first-death location. Positive: G3R3 Long Control —
  [cs2strat](https://www.cs2strat.com/en/articles/4DHZo42kaf9PthQ271gv) / POV `youtu.be/tAtUAPU2Qfo`
  (HLTV 2398757, log-on-watch).
- **MAP-DST-061 Q2 — Dry peek Long/Mid/Short?** Usually wrong per §6 timings [8.4 s / 4.8 s / 6-angle].
  *Exception:* eco gamble or confirmed weak side with numbers. HE-for-smoke Mid cross only as save-smoke with
  timing. Evidence: spawn, utility log, prior aggression.
- **MAP-DST-062 Q3/Q4 — B pushes Upper every round / BBB every buy?** Usually wrong — predictable, no-trade,
  narrow + crossfire. *Legit iff* T passive + need stack info + loss affordable (Upper); only pistol/force vs
  ≤1 holder or as throw-off (BBB) — Dignitas BBB. Negative: G2R10 Short Execute needs Short control first —
  [cs2strat](https://www.cs2strat.com/en/articles/8CWzOXGJ5RSP5ZKdnRRc) / POV `youtu.be/7VQFaofvNgw`
  (HLTV 2388119).
- **MAP-DST-063 Q5/Q6 — Over-rotate on B noise / B-retake worth it?** Usually wrong — 10.7 s back + 15 s
  fake-split. *Exception iff* bomb seen + Upper + Doors converge (two confirms). Retake only iff numbers +
  flash/smoke/molly + reachable plant + econ survives loss; else save. Positives: G3R9 MidToB —
  [cs2strat](https://www.cs2strat.com/en/articles/ZLDQRKaWgdLpNnGnSNlH) / `youtu.be/RypNTofnYl8`;
  G3R11 B Execute — [cs2strat](https://www.cs2strat.com/en/articles/iRScOGiZ5tQrib5pGrSW) /
  `youtu.be/rqe2yeuT0qk`. CT info-failure: G1R15 Mid Push — [cs2strat](https://www.cs2strat.com/en/articles/iDXFlcNN6e942umPnA5W) /
  `youtu.be/PiR7qeZkTRY` (HLTV 2398755); G1R10 Lower Tunnel Control — [cs2strat](https://www.cs2strat.com/en/articles/TXqsF7zixS2QL17Cc85x) /
  `youtu.be/U8WNWo9VH3Y`.
- **MAP-DST-064 Q7 — B AWP hold vs rifle?** Useful iff it secures left-side info so the team focuses right —
  "most valuable AWP usage even without kill" — [cs2strat](https://www.cs2strat.com/en/articles/bg571bPL7daRn0cLAr21) /
  G2R20 POV `youtu.be/m7PimXW4kC0` (HLTV 2389281) + discussion.

---

## 8. Verified gameplay examples

- **MAP-DST-070 EX-1 — Vitality 3–1 FaZe, Budapest Major Final, 14-Dec-2025, Dust2 Map 2 (Vitality PICK) 13–3.**
  Veto: FaZe ban Train / Vitality ban Ancient / FaZe pick Nuke 6–13 / Vitality pick Dust2 13–3 / FaZe pick
  Inferno 9–13 / Vitality pick Overpass 13–2 / Mirage leftover; #2 vs #12. Icons: T-open 1–0 → 8–0 run
  (5 detonations + T-wins) then 9–1 → 11–0 → 12–2 → 13–2. Per-map Mezii 23–8, 2.08; ropz 1.34 —
  [dust2.us](https://www.dust2.us/matches/2388130/vitality-vs-faze) (veto + icons + tables + VOD `9qqiaW7sjD0@29).
  Pre-Xbox. Sides inferred from icons — need demo.
- **MAP-DST-071 EX-2 — Vitality 3–0 Spirit, Katowice Final, 09-Feb-2025, Dust2 Map 1 (Spirit PICK) 13–6.**
  Veto: Spirit ban Inferno / Vitality ban Ancient / Spirit pick Dust2 6–13 / Vitality pick Nuke 13–5 / Spirit
  pick Mirage 11–13. Icons: CT-open 1–0 → 2–0 → 7–3 → ~7–5 half, then T 8–5 → 13–6. Per-map ropz 26–9, 2.42 /
  141.7; ZywOo 1.36 — [dust2.us](https://www.dust2.us/matches/2378917/vitality-vs-spirit). Pre-Xbox. Need demo.
- **MAP-DST-072 EX-3 — FURIA 2–0 Aurora, Cologne Major SF, 20-Jun-2026, Dust2 (Aurora PICK) 9–13.**
  Veto: Aurora ban Overpass / FURIA ban Anubis / Aurora pick Dust2 9–13 / FURIA pick Nuke 13–4 / bans
  Ancient/Mirage / Inferno leftover; #7 vs #5. Icons: CT-open 1–0 → 3–0, FURIA 3–1 → 3–3 → 5–7 half;
  holds/defuses to 9–13. Per-map KSCERATO 17–12, 1.42; yuurih 18–11, 1.40 —
  [dust2.us](https://www.dust2.us/matches/2395000/aurora-vs-furia) (veto + icons + tables + ESL TV
  `XLlmc1hmklc@6339`). **Post-Apr-2026 Xbox — current-geometry.** Need VOD watch.
- **MAP-DST-073 EX-4 — Vitality 2–1 MongolZ, Austin Major Final, 22-Jun-2025, Dust2 (Vitality PICK) 13–4.**
  Veto: MongolZ ban Train / Vitality ban Ancient / MongolZ pick Mirage 5–13 / Vitality pick Dust2 13–4 / bans
  Anubis+Nuke / Inferno leftover 13–6; #1 vs #5. Icons: CT-open 1–0 → 6–0 → 9–3 half (5 CT + defuse), then T
  10–3 → 13–4. Per-map ZywOo 18–8, 2.02; mezii 20–7, 1.83 —
  [dust2.us](https://www.dust2.us/matches/2382619/vitality-vs-the-mongolz) (Twitch `v2493025305@2h59m10s).
  Pre-Xbox. QF `2388124` 13–4 opened.
- **MAP-DST-074 EX-5 — Vitality 3–0 MOUZ, EPL S24 Final, 11-Oct-2026, Dust2 (Vitality PICK) 16–12 OT.**
  Veto: Vitality ban Ancient / MOUZ ban Anubis / Vitality pick Cache 13–8 / MOUZ pick Inferno 13–7 / Vitality
  pick Dust2 16–12 / MOUZ pick Mirage / Nuke leftover; #2 vs #3. MOUZ CT-open 5–1, Vitality T to 7–5;
  back-and-forth 2nd, 3 map points saved, 4–0 OT. ZywOo 25 kills, 1.65 series, MVP 1.44 event, 4th EPL title —
  [dust2.us](https://www.dust2.us/matches/2398757/vitality-vs-mouz) +
  [dust2.in](https://www.dust2.in/news/78792/vitality-sweeps-mouz-to-win-esl-pro-league-season-24).
  **Current-geometry + OT.** POVs (log-on-watch): G3R3/G3R9/G3R11 + G3R5 `QX6ct9mat6d7K8Na4zku`
  (`youtu.be/ccLgz48k_Rw`) / G3R21.

---

## 9. Observable data requirements

### MAP-DST-080 — Must log

(x, y, z, t) + crouch/scope; door states; smoke bloom/pop/obscure
[Xbox / CT-Spawn / Long-corner / cross / Door]; flash assists; sound contacts [Upper numbers, Lower/Cat]; bomb
carrier path + plant-side tag; alive/econ/spawns; rotate start/end vs 10.7 s baseline ± spreads; Long-race
outcome [CT 7.1 s vs T 8.7 s knife]; patch tag pre/post Apr-2026 Xbox + Apr-29 corner.
**Missing:** choke timestamps, bloom-confirm, audio proxies, plant-side win%, spawn-conditioned rotates — demo
parsing at the embeds above + in-game checks. Radars/screenshots viz-only.

---

## 10. Known uncertainties and research gaps

1. HLTV/Liquipedia direct blocked (429/403).
2. Xbox blocked-corner identity + hidden-jump mechanics + post-Apr-29 lineup validity need in-game verification.
3. **Zero timestamped rounds verified in-text** — pull Budapest / Katowice / Cologne / Austin / EPL demos + the
   ~20 POVs above (all log-on-watch).
4. Dignitas-2018 / scope-2020 / friberg-2021 / PCGamer-2016 dated; BoostRoom / cs2.eu-2026 / GetReplay / cs2caller /
   CSStatLab are ranked-level, not pro truth.
5. No 2024–25 analyst Dust2 breakdown found; T.c is comms/mentality, not geometry.
6. EPL S24 Dust2 OT icons need demo for OT split.
7. Do NOT reproduce map assets.

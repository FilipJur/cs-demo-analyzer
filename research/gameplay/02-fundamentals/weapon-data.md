# Weapon Data — Sourced CS2 Numbers (build-stamped)

**Status:** research only. Values below are third-party spreadsheet-derived unless
marked otherwise — NOT Valve-published. Build baseline: community weapon spreadsheet
dated **2026-03-18** (via Tradeit, checked 2026-07-20), post **March 2026
magazine-discard rework**. Re-verify after any balance patch; check the in-game buy
menu. Access date all sources: 2026-10-15.

**Primary table source:** Tradeit complete CS2 weapon stats (34 firearms, 16 fields),
"checked July 20, 2026 against the community weapon spreadsheet, Valve update history,
and a detailed CS2 damage guide." Tier **Measured (third-party spreadsheet, not Valve)**.
URL `https://tradeit.gg/blog/cs2-weapon-stats/`.

## Damage formula (Measured/datamined)

Memorin, current-build recording (network protocol 14166) + compiled weapon data +
live convar list; candidate formula must reproduce the server's recorded integer
exactly — 29/30 events exact (rounding fits only 16/30). Tier **Measured**.
URL `https://memorin.app/mechanics/bullet-damage`.

```
damage_dealt = floor(base_damage × rangeModifier^(distance_units / 500)
                     × hitgroup_multiplier × armor_factor)
```

- **Distance basis:** shooter → **hit point on the hitbox**, NOT victim origin
  (proven by adjacent friendly-fire rows at raw 21.03 vs 21.10 straddling a floor
- **Friendly fire:** bullets ×0.33 (literally 0.33, not ⅓ — convar list);
  grenade ×0.85; grenade self-damage ×1.0 (unreduced — earlier ~0.6 guess corrected).
  **Locally verified 2026-10-15 against local install build 25947352
  (`appmanifest_730.acf`, LastUpdated epoch 1792064838 = 2026-10-15 — same-day,
  current-build evidence):** stock `game/csgo/cfg/gamemode_competitive.cfg`
  lines 36–39 ship `ff_damage_reduction_bullets 0.33`,
  `ff_damage_reduction_grenade 0.85`, `ff_damage_reduction_grenade_self 1`,
  `ff_damage_reduction_other 0.4` — byte-identical to the fitted values. This row is
  primary (local install), not third-party-fitted. Mode sweep same day: casual,
  deathmatch, retakes ship all-zero FF reductions — these values are
  **competitive-mode values**, matching competitive/FACEIT-style demo analysis scope.
- **Hitgroups:** head per-weapon (M4A1-S 3.475, Deagle 3.9 — NOT a global 4×);
  chest/arms ×1.0; stomach ×1.25; legs ×0.75 and **never armoured**.
- **Armour:** health damage = raw × (armorRatio × 0.5); armour points lost =
  floor((raw − dealt) × 0.5). Helmeted headshot example reproduced exactly:
  87 health + 18 armour at 471 u.
- **HE vs enemies:** 99 × (1 − d/350), base ~97–99, radius ~350 u (442 events).
- **Negative result (VERIFIED):** 0 bullet-impact events in 9,372 recorded shots
  across four 2026 tournament demos — spread/penetration have **no demo oracle**.

Falloff conversion: Tradeit lists "falloff / 500u" as % lost per 500 Hammer units
(~12.7 m). `rangeModifier = 1 − falloff`. Same exponential form as the Fandom
CS:GO-era table (`Damage × RangeModifier^(Distance/500)`), but CS2 rows below
supersede CS:GO carryover (Fandom table: AK 0.98 / M4A4 0.97 / M4A1-S 0.94 /
FAMAS 0.96 / UMP 0.75 / Bizon 0.8 / MP7 0.85 / P90 0.86 / MP9 0.87 / AWP 0.99 —
**carryover UNVERIFIED for CS2**, URL `https://counterstrike.fandom.com/wiki/Damage_dropoff`).

## Rifles (all 7 — low falloff, long-range class)

| Weapon | Price | Kill $ | Dmg | Armor pen | Falloff/500u | HS mult | RPM | Mag (+reserve) | Reload | Move | Run inacc | Pen | Tag | Helmet 1-shot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Galil AR (T) | $1,800 | $300 | 30 | 77.50% | 2% | 4.0× | 666.67 | 35 + 4 mags (175) | 3.0 s | 215 | 132.93 | 200 | 60% | No |
| FAMAS (CT) | $1,950 | $300 | 30 | 70.00% | 4% | 4.0× | 666.67 / 800 burst | 25 + 4 mags (125) | 3.3 s | 220 | 107.53 | 200 | 60% | No |
| AK-47 (T) | $2,700 | $300 | 36 | 77.50% | 2% | 4.0× | 600 | 30 + 3 mags (120) | 2.4 s | 215 | 182.07 | 200 | 60% | **Yes** (all practical distances) |
| M4A4 (CT) | $2,900 | $300 | 33 | 70.00% | 3% | 4.0× | 666.67 | 30 + 4 mags (150) | 3.1 s | 225 | 143.38 | 200 | 60% | No |
| M4A1-S (CT, silenced) | $2,900 | $300 | 38 | 70.00% | 6% | 3.475× | 600 | 20 + 3 mags (80) | 3.1 s | 225 | 127.40 silenced | 200 | 60% | No |
| SG 553 (T, scoped) | $3,000 | $300 | 30 | 100.00% | 2% | 4.0× | 545.45 | 30 + 3 mags (120) | 2.8 s | 210 | 142.42 | 200 | 60% | **Yes** |
| AUG (CT, scoped) | $3,300 | $300 | 28 | 90.00% | 2% | 4.0× | 600 | 30 + 3 mags (120) | 3.8 s (AUG reload −0.5 s Oct 2026 patch — re-verify) | 220 | 140.85 | 200 | 60% | Yes (197.21 m helmet range — exceeds normal sightlines) |

Notes: AK wins price/reload/universal helmet one-shot. M4A4 wins sustained magazine
(30 + 666.67 RPM). M4A1-S wins body damage (38), silence (no tracers), recoil —
but strongest rifle falloff (6%). See M4A4-vs-A1-S split below.

## SMGs (all 7 — high falloff, close-range class)

| Weapon | Price | Kill $ | Dmg | Armor pen | Falloff/500u | RPM | Mag (+reserve) | Reload | Move | Run inacc | Pen | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MAC-10 (T) | $1,050 | $600 | 29 | 57.50% | 20% | 800 | 30 + 3 mags (120) | 2.6 s | 240 | 27.89 | 100 | 100% |
| MP9 (CT) | $1,250 | $600 | 26 | 60.00% | 13% | 857.14 | 30 + 2 mags (90) | 2.1 s | 240 | 38.64 | 100 | 100% |
| UMP-45 (both) | $1,200 | $600 | 35 | 65.00% | **25%** | 666.67 | 25 + 3 mags (100) | 3.5 s | 230 | 43.19 | 100 | 100% |
| MP7 (both) | $1,400 | $600 | 30 | 62.50% | 13% | 750 | 30 + 3 mags (120) | 3.1 s | 220 | 30.46 | 100 | 100% |
| MP5-SD (both, silenced) | $1,400 | $600 | 28 | 62.50% | 13% | 750 | 30 + 3 mags (120) | 3.0 s | 235 | 40.60 | 100 | 100% |
| PP-Bizon (both) | $1,300 | $600 | 27 | 63.00% | 20% | 750 | 64 + 2 mags (192) | 2.4 s | 240 | 42.57 | 100 | 100% |
| P90 (both) | $2,350 | **$300** | 26 | 69.00% | 14% | 857.14 | 50 + 2 mags (150) | 3.3 s | 230 | 45.65 | 100 | 100% |

Notes: UMP-45 most damage per bullet, strongest falloff. MP9/P90 joint-highest RPM
(857.14). MP7/MP5-SD/P90 share lowest recoil scalar (16.0). Bizon owns capacity (64).
P90 pays rifle-like price for SMG falloff with only $300 reward — economy trap.

## Pistols (all 10)

| Weapon | Price | Kill $ | Dmg | Armor pen | Falloff/500u | HS mult | RPM | Mag (+reserve) | Reload | Move | Run inacc | Pen | Tag | Helmet 1-shot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Glock-18 (T) | $200 | $300 | 30 | 47.00% | 15% | 4.0× | 400 / 1,200 burst | 20 + 3 mags (80) | 2.3 s | 240 | 17.60 | 100 | 50% | No (560.92 m unhelmeted only) |
| USP-S (CT, silenced) | $200 | $300 | 35 | 50.50% | 9% | 4.0× | 352.94 | 12 + 2 mags (36) | 2.2 s | 240 | 20.27 sil. | 100 | 50% | No |
| P2000 (CT) | $200 | $300 | 35 | 50.50% | 9% | 4.0× | 352.94 | 13 + 4 mags (65) | 2.2 s | 240 | 19.90 | 100 | 50% | No |
| P250 (both) | $300 | $300 | 38 | 64.00% | 10% | 4.0× | 400 | 13 + 3 mags (52) | 2.2 s | 240 | 31.10 | 100 | 50% | No |
| Dual Berettas (both) | $300 | $300 | 38 | 57.50% | 21% | 4.0× | 500 | 30 + 2 mags (90) | 3.77 s | 240 | 26.85 | 100 | 50% | No |
| Five-SeveN (CT) | $500 | $300 | 32 | 91.15% | 19% | 4.0× | 400 | 20 + 2 mags (60) | 2.2 s | 240 | 51.10 | 100 | 50% | **Yes** (365.88 m helmet — inside realistic distances) |
| Tec-9 (T) | $500 | $300 | 33 | 90.60% | 21% | 4.0× | 500 | 18 + 3 mags (72) | 2.5 s | 240 | **10.71** | 100 | 50% | **Yes** (379.51 m helmet) |
| CZ75-Auto (both, auto) | $500 | $300 | 31 | 77.65% | 15% | 4.0× | 600 | 12 + 2 mags (36) | 2.7–2.8 s | 240 | 26.84 | 100 | 50% | No |
| Desert Eagle (both) | $700 | $300 | **53** | 93.20% | 15% | **3.9×** | 266.67 | 7 + 3 mags (28) | 2.2 s | 230 | 54.30 | **200** | 60% | **Yes** (2,017.23 m helmet) |
| R8 Revolver (both) | $600 | $300 | 86 | 93.20% | 6% | 4.0× | 120 charged / 150 rapid | 8 + 2 mags (24) | 2.3 s | 180 | mode-dependent | **200** | 60% | **Yes** (9,414.48 m helmet) |

Notes: Tec-9 run-inacc 10.71 is the most forgiving moving-pistol value in the game
(vs AK 182.07). Deagle/R8 double pistol pen tier (200). **Discrepancy: Codex claims
Deagle base 63 — Tradeit says 53. Do not mix sources without a build check.**
URL Codex `https://counterstrike.codexery.com/wiki/damage-falloff`.

## Snipers (all 4 — 250 pen tier, lowest falloff)

| Weapon | Price | Kill $ | Dmg | Armor pen | Falloff/500u | HS mult | RPM | Mag (+reserve) | Reload | Move | Run inacc (unscoped) | Pen | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SSG 08 (both, bolt) | $1,700 | $300 | 88 | 85.00% | 2% | 4.0× | 48 | 10 + 2 mags (30) | 3.7 s | 230 | 155.43 | 250 | 65% |
| AWP (both, bolt) | $4,750 | **$100** | 115 | 97.50% | **1%** | 4.0× | 41.24 | 5 + 2 mags (15) | 3.7 s | 200 | 257.48 | 250 | 65% |
| G3SG1 (T, auto) | $5,000 | $300 | 80 | 82.50% | 2% | 4.0× | 240 | 20 + 2 mags (60) | 4.7 s | 215 | 176.58 | 250 | 50% |
| SCAR-20 (CT, auto) | $5,000 | $300 | 80 | 82.50% | 2% | 4.0× | 240 | 20 + 2 mags (60) | 3.1 s | 215 | 176.58 | 250 | 65% |

AWP detail: chest-vs-armor one-tap to 5,694u (~145 m); head/stomach one-tap at any
map distance; legs 86.25 (never lethal vs full HP). Deploy 1.25 s. Scoped move 100.
Accurate range 1.9 m unscoped → 69.3 m scoped; running inacc 257.5 → 178.7 scoped
(scope does NOT fix moving fire). Zoom FOV 90→40→10 (SSG 15). Full AWP treatment:
`concepts.md` FUND-A01/A02. Corroborated by CSBePro (build 1.41.7.6) + Gamers.Wiki.

## Shotguns (per-pellet, harshest falloff) + MGs

| Weapon | Price | Kill $ | Dmg | Armor pen | Falloff/500u | RPM | Ammo | Reload | Move | Run inacc | Pen | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nova (both, pump) | $1,050 | **$900** | 26 × 9 | 50.00% | 30% | 68.18 | 8 + 32 shells (40) | 0.7 s first, 0.5 s next (interruptible) | 220 | 83.75 | 100 | 60% |
| MAG-7 (CT, mag-fed) | $1,300 | **$900** | 30 × 8 | 75.00% | **55%** | 70.59 | 5 + 3 mags (20) | 2.4 s | 225 | 62.99 | 100 | 60% |
| Sawed-Off (T, pump) | $1,100 | **$900** | 32 × 8 | 75.00% | **55%** | 70.59 | 7 + 32 shells (39) | 0.67 s first, 0.5 s next | 210 | 85.80 | 100 | 60% |
| XM1014 (both, semi-auto) | $2,000 | $600 | 20 × 6 | 80.00% | 30% | 171.43 | 7 + 32 shells (39) | 1.0 s first, 0.65 s next | 215 | 81.03 | 100 | 60% |
| Negev (both, spin-up) | $1,700 | $300 | 35 | 71.00% | 3% | 800 | 150 + 2 mags (450) | 5.7 s | 150 | 171.31 | 200 | 60% |
| M249 (both) | $5,200 | $300 | 32 | 80.00% | 3% | 750 | 100 + 2 mags (300) | 5.7 s | 195 | 165.95 | 200 | 60% |

Shotgun theoretical totals assume every pellet connects — treat as ceiling, not TTK.
Negev 466.7 raw base DPS is the highest sustained automatic ceiling in the table and
the least practical (spin-up, 150 speed, 5.7 s reload).

## Handling rules (same Tradeit source — "stats the tables don't show")

- **Movement changes accuracy, not damage.** A connecting bullet keeps full damage
  math; running/jumping expands inaccuracy. Counter-strafe, settle, fire.
- **Crouch** tightens first shot but slower movement + predictable head level =
  strategically expensive.
- **Scopes** (AUG/SG/AWP/SSG/G3/SCAR) improve stationary precision only — never
  running shots.
- **Recoil scalar ≠ spray ranking** (pattern + firing inaccuracy + recovery +
  compensation). M4A1-S tighter grouping than M4A4; master A4's first 12 bullets
  (Gamers.Wiki `[guide]`).
- **Silencers** (keep attached for normal engagements): USP-S attached 23.81 m /
  20.27 / recoil 23 / no tracers vs detached 20.59 m / 21.27 / 29 / every bullet
  (35 dmg / 352.94 RPM unchanged); M4A1-S attached 28.22 m / 127.40 / 21 / none vs
  detached 27.71 m / 98.38 / 25 / every third bullet (38/600 unchanged). M4A1-S
  detached runs *better* on paper but loses silence/tracers/sound — still keep attached.
- **Tagging:** SMG 100% power gated by damage/armor — "a hit is not automatically a
  full stop."
- **Magazine-discard (March 2026):** partial reload destroys remaining rounds;
  reserve tracked as whole magazines/shells/bullets. Ammo depth is a ceiling only
  with reload discipline. AWP: 5 + 10 = 15 total.
- **Skins never change stats** (damage, pen, recoil, inaccuracy, speed, reload,
  hitboxes). Zeus lethal ~183 Hammer units, zero past ~230 (~3.5–4.4 m).

## M4A4 vs M4A1-S role split (Gamers.Wiki `[guide]`, 2026-06-30)

Both $2,900 since Jan 2025 — purely tactical choice. Both ~70% AP.
URL `https://gamers.wiki/en/games/counter-strike-2/guides/m4a4-vs-m4a1-s-comparison-guide-for-counter-strike-2`.

- **M4A4 = workhorse:** 30+90, 666 RPM, 33 dmg, looser/longer spray; more consistent
  long-range falloff (3% vs 6%); anchor/rush-halt/retake/multi-kill; close-quarter maps
  (Inferno/Anubis/Mirage: Banana, connectors, tight sites); wall-spam thin surfaces.
- **M4A1-S = scalpel:** 20+80, 600 RPM, 38 dmg, tighter grouping, HS 3.475×;
  silencer = no tracers + muffled = smoke-spam + off-angle lurking without pinpoint;
  long barrel can poke corners (trade-off); long-range maps (Dust2/Nuke/Overpass:
  Long, Outside, Heaven); anchor/support/rotator; long-range positioning per
  Tradeit fatal-HS data needs care (6% falloff > A4's 3% — guide's "better at distance"
  refers to precision/stealth, not damage retention).
- Practice: `cl_crosshair_recoil 1` + Recoil Master workshop map. `[disputed]`
  "80% of pros (s1mple/ZywOo)" + YEKINDAR smoke-spam quote: unattributed — (5).

## Movement speeds (SteamAnalyst table `[guide]`, version-sensitive)

Knife 250 / pistol 240 / SMG 240 / rifle (AK/M4) 215 / AWP 200 u/s (scoped 100);
crouch ~85/82/82/74/68. Bhop cap ~300 (run 250), inconsistent, rotations only.
URL `https://www.steamanalyst.com/guides/cs2-shooting-peeking-movement-guide`.

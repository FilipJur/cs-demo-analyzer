# CS2 Execution Mechanics — Evidence and Patch Sensitivity

**Access date for all sources: 2026-10-15/16. Research only — no thresholds for detectors,
no verdict rules.** Tiers: **Measured** (tested/datamined/file-sourced) · **Official**
(Valve/patch first-party) · **Expert** (pro/coach/analytics outlet) · **Community**
(practitioner guide — definition-reliable, not efficacy evidence).
Claim classes: (1) observable error · (2) measured characteristic · (3) potential execution
issue · (4) context decision · (5) unsupported attribution.
`[INFERENCE]` marks arithmetic/synthesis, never engine fact.

Full bibliography in `sources.md`. Per-weapon table in `weapon-data.md`.
First validation numbers in `validation-v1.md`.

## 1. Movement inaccuracy and counter-strafing

**Counter-strafing still matters in CS2.** Three independent sources agree the
movement-inaccuracy rule survived subtick: Refrag ("most accurate when movement speed is 0";
release + opposite-tap; crab-walk exception — Expert,
https://refrag.gg/blog/counter-strafing-the-key-to-precision-aim-in-counter-strike-2/) ;
NextFrag ("accurate below a small fraction of max speed"; "Looking Stopped vs. Being Accurate" —
Community, https://nextfrag.gg/cs2-counter-strafe-analysis) ;
MetaBot (velocity-tracked cone above a low threshold; release leaves a "glide" — Community,
https://metabot.gg/en/cs2/guides/cs2-counter-strafing-movement-accuracy).
CSStatLab restates the same three failure modes a fourth time (holding counter-key too long,
firing before stopped, never counter-strafing — Expert-advice,
https://csstatlab.com/academy/gameplay/counter-strafing,
https://csstatlab.com/academy/gameplay/movement-and-accuracy).
**"Sub-tick removed counter-strafing" is a myth — category (5).**

**The 34% rule (formula-documented, not single-vendor).** Leetify "Proper Counter-Strafing":
a "good" shot = velocity < **34% of max speed with that weapon** ("34% is when inaccuracy
kicks in"); rifles only, spotted shots, crouch excluded — Expert/production definition,
https://leetify.com/blog/leetify-stats-glossary/.
The shared post-2011 accuracy model doc states the same constant from the other side:
movement inaccuracy accrues **after moving past 34% of max speed, linearly scaled by
InaccuracyMove** — Community/RE,
https://steamcommunity.com/sharedfiles/filedetails?id=3710237601.
Corroborating voices: Leetify definition, SteamAnalyst guide, this model doc.
Derived per-weapon thresholds `[INFERENCE — arithmetic, never engine constants]`:
AK-47 ≈ 73.1 u/s (215 × 0.34), M4A4 ≈ 76.5 (225), AWP ≈ 68.0 unscoped (200),
USP-S ≈ 81.6 (240), Negev ≈ 51.0 (150).
Correction: SteamAnalyst's "~88 u/s with a rifle" is arithmetically wrong
(0.34 × 215 = 73.1) — quarantined, never a threshold.

**Stop curves (Measured inputs, derived curve).** Friction 5.2 + stopspeed 80 are Measured
(Memorin movement constants, https://memorin.app/mechanics/movement-constants —
gravity 800, accelerate 5.5, walk cap ×0.52, duck ×0.34, duck ramp 10 ticks).
Source-friction decay from full run: **~13 ticks (~200 ms) to 34%, ~24–26 ticks to ~0**
(AK 13/24, M4A4 13/25, AWP 13/24, USP-S 13/26, Negev 12/20) `[INFERENCE]`.
The Community "1–2 vs ~10 frames" claim is directionally right but soft: full-speed release
coasts ~2.5× longer than "ten frames" (likely describes mid-strafe taps, not max→stop).
Active counter-tap timing (1–2 frames) remains advice-grade.

**Inaccuracy combination model (RE, use with care).** UnknownCheats `get_inaccuracy` RE
(Feb 2024, author-flagged "not sure if 100% proper" — Community/RE,
https://www.unknowncheats.me/forum/counter-strike-2-a/623351-get_inaccuracy-weapon_v_data-externally.html) :
base inaccuracy is **selected, not summed** — ground + 2-D speed ≤ 0.1 → stand;
speed > 0.1 → move; airborne → jump; duck overrides (even mid-air); ladder/landing branches;
firing (sequence changed) → fire-term wins that shot.
Post-shot penalty decays **exponentially**:
`newpenalty = (inaccuracyfire + oldpenalty) × 0.1^(time/recoverytime)`.
Consequence: standing-vs-moving is a **hard switch**, so a shot one tick early pays the full
move penalty (supports "shooting too early" as binary, not graded); tapping/bursting is
relatively worse under this model than 1.6 (old model was time-insensitive under 0.4 s).

**Per-weapon inaccuracy values (Measured — game files via cs2.gs, build 1.41.8.2; field set
Official via `CCSWeaponBaseVData` schema,
https://github.com/SteamTracking/GameTracking-CS2/blob/master/DumpSource2/schemas/client/CCSWeaponBaseVData.h).
Standout contrasts `[INFERENCE]`: AK move/stand ≈ 27× (0.1751/0.0064); M4A4 ≈ 28×;
USP-S ≈ 2.8× (most forgiving sidearm — pistol-round run-and-gun has a basis for USP-S only,
never generalize to Deagle ~11×); scoped AWP standing ≈ 40× tighter than unscoped
(0.002 vs 0.0808 — the quantitative reason AWP demands full plant + scope).
Full rows in `weapon-data.md`. Combination formula (how terms sum) unsourced — explicit unknown.

**Patch sensitivity: HIGH.** Movement/prediction/view-angle handling changed repeatedly
2023–2026 (June-2023 subtick movement, Nov-2023 feedback-sync, Jan-2026 landing time,
Sept-2025 subtick shooting). Date-stamp every movement claim.

## 2. First-bullet accuracy, recovery, burst/spray/tap

**Two-system framing (strongest sourced treatment).** CSStatLab "Spray, Burst or Tap"
(upd. 2026-08-30 — Expert/Community explainer,
https://csstatlab.com/academy/weapons/spray-burst-tap):
**recoil** = deterministic, indexed by shot number ("shot 7 always pulls the same way",
canceled by mouse); **inaccuracy** = random cone growing per round fired + movement/airborne,
shrinking on a timer ("you cannot cancel it with mouse movement, you can only wait it out").
This separates spray-control failures (unobservable compensation) from cone-management failures
(observable cadence): "traced the pattern correctly, bullet 15 still missed" is cone, not hands.
Spray = pre-generated per-shot lookup table, index +1/shot while held (Mythras game-file guide,
https://gamertagmythras.com/blog/counter-strike-2/cs2-spray-control-guide).

**Recovery clocks.** Tap ≈ 1 round per 0.3–0.4 s at long range; burst = 2–4 rounds full-rate
(CSStatLab, same URL — advice-grade, consistent with game files).
Per-weapon recovery-stand/crouch + transition bullets (2–5 typical) in `weapon-data.md`.
AK three-phase pattern (Expert-advice, approximate, never exact cutoffs):
shots 1–6/7 near-vertical, 7/8–15 left-then-right sweep, 16–30 wide/"accuracy falls off a cliff";
working rule "if the fight needed more than seven AK rounds, you should have been bursting";
priority one-tap > burst > spray
(https://csstatlab.com/academy/weapons/ak-47-spray-pattern).
Spray-control drill order: wall-mag → trace-back → 2–3-round bursts → add movement
(movement-first triage: "many players think they have a recoil problem when they really have
a movement problem", https://csstatlab.com/academy/weapons/cs2-recoil-patterns).

**Range discipline (heuristic, advice-grade).** Close 0–10 m full spray center-mass→head +
crouch mid-fight; medium 10–25 m burst 3–5 head-level; long 25 m+ tap/2-round head-only,
~0.4 s AK reset; first ~10 rifle rounds ~straight up (SteamAnalyst,
https://www.steamanalyst.com/guides/cs2-shooting-peeking-movement-guide).
Canonical errors: spray-at-long, running-and-shooting. Meters are approximate — never thresholds.

**CS2-vs-CS:GO recoil delta (directional only).** Single tester (Water CS2, Oct 2023,
https://www.youtube.com/watch?v=uZXTgzJKfQ0, cites csstats.gg comparison): CS2 patterns
~8–10% tighter across the board (AK area −8.9%, Galil −10.4%, M4A4 −8%, …), attributed
in-video to subtick de-quantization. **CS:GO pattern coordinates are not valid CS2 references**
(two independent reasons: this delta + provenance objection to scraper/cheat CSVs).
Any expected-curve reference must be CS2-native and build-pinned.
**No measured CS2 pattern coordinates exist from any source** — the evidence gap stands.

**Aim punch / flinch / tagging (current state).** Pawn fields confirmed Official
(`C_CSPlayerPawn` schema, build 25947352,
https://cs2opendev.github.io/CS2OpenDev-Docs/schemas/client/C_CSPlayerPawn/):
`m_iShotsFired` (burst counter), `m_flFlinchStack` (accumulated punch magnitude —
existence confirmed, per-hit increments unsourced), `m_flVelocityModifier` (tagging slow
factor, live scalar — slowdown is readable, not vibes; demoparser exposes `velo_modifier`),
`m_flInterpolatedInaccuracy` (live tick-level cone candidate).
Tagging strengths (Community/data-checked, Tradeit Jun-2026,
https://tradeit.gg/blog/cs2-weapon-stats): SMGs 100%, pistols 50% (Deagle/R8 60%),
rifles/shotguns/LMGs 60%, AWP/SSG 65%, autosnipers 50–65% — but final slowdown also depends
on damage/armor/movement, so "a hit is not automatically a full stop."

## 3. Damage, falloff, armor, hitgroups

**Formula (Measured/datamined).** Memorin current-build recording (proto 14166) + compiled
weapon data + convars — candidate must reproduce server integers exactly, 29/30 exact
(rounding fits only 16/30): https://memorin.app/mechanics/bullet-damage

```
damage_dealt = floor(base_damage × rangeModifier^(distance_units / 500)
                     × hitgroup_multiplier × armor_factor)
```

- **Distance basis:** shooter → **hit point on the hitbox**, not victim origin (proven by
  adjacent friendly-fire rows at raw 21.03 vs 21.10 straddling a floor boundary).
- **Hitgroups:** head **per-weapon** (M4A1-S 3.475, Deagle 3.9 — never a global 4×);
  chest/arms ×1.0; stomach ×1.25; legs ×0.75 and **never armoured**.
- **Armour:** health damage = raw × (armorRatio × 0.5); armour points lost =
  floor((raw − dealt) × 0.5). Helmeted example reproduced exactly (87 HP + 18 armour at 471 u).
- **Falloff conversion:** Tradeit "falloff / 500 u" = % lost per 500 Hammer units (~12.7 m);
  `rangeModifier = 1 − falloff`. CS2 rows in `weapon-data.md` supersede the Fandom CS:GO-era
  table (carryover UNVERIFIED for CS2).
- **Worked breakpoint:** AK helmeted one-tap holds to ≈ 2,583 u (111 × 0.98^(d/500) = 100 —
  Expert/game-file, https://gamertagmythras.com/blog/counter-strike-2/cs2-ak-47-vs-galil-ar-guide ;
  meters ≈ 49 m at 52.49 u/m, conversion authorial). Galil (92 < 100 at d=0) never one-taps
  helmets — categorical, conversion-free. **"Wrong-gun-for-range" verdicts on AK helmets need
  d > ~2,600 u; inside that, the miss is execution, not selection.**
- **Negative result (VERIFIED):** 0 bullet-impact events in 9,372 recorded tournament shots —
  spread/penetration have **no demo oracle**.

**Falloff classes (Measured third-party spreadsheet, not Valve — build 2026-03-18 baseline).**
Rifles 2–6% (AK 2, M4A4 3, M4A1-S 6, others 2–4); SMGs 13–25% (UMP-45 25 worst,
MP9/MP7/MP5-SD 13 best); pistols 6–21% (R8 6 best, Dualies/Tec-9 21 worst); snipers 1–2%
(AWP 1 best); shotguns 30–55% per pellet (harshest — totals assume all pellets, ceiling not TTK);
MGs 3%. Illustration: M4A4 33 vs UMP-45 35 point-blank → 32 vs 28 @10 m → 30 vs <15 @50 m.
**No universal class distance threshold may be emitted.**

**M4 TTK inversion (adds timing precision).** Armored chest: A1-S 4×26 = 104 @300 ms beats
A4 5×23 = 115 @360 ms ("the slower rifle kills faster", ~60 ms ≈ 4 frames); armored stomach:
A1-S 3×33 = 99 (one short) so both need 4, A4 wins 270 vs 300 ms
(Expert, https://gamertagmythras.com/blog/counter-strike-2/cs2-m4a4-vs-m4a1-s-guide).
Falloff inversion: A1-S 0.94 loses head+body two-shot at distance while A4 0.97 keeps it.
Reviewer consequence: M4-duel timing windows differ ~60 ms by hitbox — trade analysis should
be hitbox-aware, not weapon-averaged. Role split: M4A4 = workhorse/multi-kill/volume,
M4A1-S = scalpel/precision/stealth (no tracers); both $2,900 since Jan-2025, purely tactical.

## 4. Crosshair placement and pre-aim

**Doctrine (Expert + guide consensus).** Closest-angle rule (hug nearest threat corner);
head-level horizontal line; ~one-head-width wall gap; avoid floor/sky; minimize flick distance
("lazy crosshair syndrome" — scope.gg coach blog, Expert,
https://blog.scope.gg/crosshair-placement-en/;
SteamAnalyst §1, Dignitas habit advice — Community).
Pre-aim common holds; micro-adjust for elevation (Mirage ramp up, Inferno top-mid down).
Study pro POV (donk/m0NESY/NiKo "never drops" — Community claim, not measured).
AWP variant: center-mass over headshots under pressure (larger target wins rounds — Community).

**Measurability boundary.** View angles (pitch/yaw) are demo-available; the **true screen
crosshair point is unavailable** — placement error is approximate by construction (type 3,
never type 1). Map elevation changes legit head height (FP: HIGH without elevation context).
Leetify definitions give reviewer-grade type-2 measures (Measured, first-party):
crosshair placement = median eye-angle delta first-appearance→first-hit;
TTD = first-seen→first-damage median, 1 s+ excluded; flash counts only if >1.1 s blind;
spotted-accuracy excludes smoke/wall spam (https://leetify.com/blog/leetify-stats-glossary/).
Whether misplacement *caused* a miss is confounded by spread — no impact data (see §3 negative).

**Practice stack (context, not a mistake).** Convergent prescription (SteamAnalyst §8):
10-min aim-trainer → 10-min recoil/transfers → 10-min prefire → 15-min single-focus DM →
weekly demo review (head height? counter-strafe? too many angles? reposition after spot?).
Included so reviewers reuse validated prompts, not invented ones.

## 5. Peeking, angles, exposure

**Peeker's advantage: real, unquantified for CS2.** Valve subtick exists (Official launch
slogan: "the server will know the exact moment you fired your shot, jumped your jump, or
peeked your peek" — https://www.youtube.com/watch?v=GqhhFl5zgA0, 2023-03-22 —
cite only with the 2023–2026 revision caveat: Nov-2023 feedback-sync, Nov-2024 lag-comp,
Sept-2025 subtick shooting, Animgraph2 Apr-2026).
The only measured numbers (FDG 2024, FPSci custom game, stationary defender, 24 players:
defender 60 ms → peeker +28–31% win-delta; 0 ms → −5–13%; 7→27 m significant;
visible→hit gap ~10 ms — **Measured, non-CS2 lab**,
https://web.cs.wpi.edu/~claypool/papers/peeker-fdg-24/paper.pdf)
**MUST NOT be ported to CS2.** All CS2 subtick-timing claims are Community-tier;
pre-Nov-2024 / pre-Sept-2025 numbers are stale. Per-moment ping/subtick unrecorded —
no per-duel millisecond claim may ship. Stable principle: initiator sees first.
FP: HIGH if asserted per duel. Mixed.

**Peek types = purpose decision (guide consensus, Community).**
Wide/commit swing (2–3 character widths estimate, pre-aimed, stop→shoot; forces drag; pair
variant P1 pulls / P2 kills — MetaBot + BO3): correct with known position + rifle +
close–mid + stopped + trade/reload window. **Blind wide into unknown/long/AWP = death
sentence.** Jiggle (out-and-back, "~fraction/tenth of a second" estimate, no shot — info/bait):
correct unknown-hold/suspected-AWP; lingering, mid-jiggle shots, identical rhythm are the
failure modes. Shoulder (sliver, head behind wall — AWP-bait into ~1.45 s bolt punish):
ONLY vs scoped long-angle sniper; "useless vs rifle holder"; "if you see your enemy,
you're doing it wrong." Single-peek/slice-the-pie (one angle at a time, teammate holds
checked angles; best late-round ~40–30 s): swinging 2+ sightlines is "the number one
peeking mistake at every rank" — but **without utility/teammate state it cannot be judged
(FP: HIGH)**. Jump/Ferrari (full-speed info, never shoot mid-jump) + crouch mixup (sparing
only — never default/first-bullet/vs-multiples; crouch = commit).
Repeek timing: change timing/width every peek; hesitant/slow telegraphs hand back advantage;
instant same-angle repeek into pre-aim is the error — but committing repeeks (this section)
are distinct from free info jiggles, and deliberate fast punishes during genuine windows
(AWP bolt, flash, trade) are correct. **No measured peek-ms distributions exist.**

**Movement while clearing (guide consensus).** Full-speed clears by default; Shift only for
flank/close-angle/fake/off-angle/ladder; stop when time-critical/known/must-swing.
Corner distance: **far = see first (best holding rifles); close = fast cover (shotguns,
vs flash, fast retreat).** Off-angles (step aside, height, non-meta) beat pre-aim;
reposition after every kill/spot ("one-and-done" CT); entry + 1–2 s trader.
Speed table (version-sensitive): knife 250 / pistol 240 / SMG 240 / rifle 215 / AWP 200
(scoped 100); crouch ~85/82/82/74/68; bhop cap ~300. Rifles "terrible" moving, SMG slightly
better, AWP must stand still. Late-round low-noise shift-walk can be correct (reviewer
judgment, unsourced exception).

**Utility-combined peeks.** Pop-flash → peek at detonation (blind ~2 s; self wall-bounce best);
molly forces reposition → peek during spread; default utility peek over dry peek whenever
utility is available. Dry peek correct for: info jiggles, eco (no nades), trader present.
Blinding flash must be unheard/unseen before pop; review flash→peek interval + blinded state
(demo-available) — never infer deliberate timing vs luck.

**Tracking / target-switching: OPEN — no evidence base.** Practice claims only
(spray-transfer drag, AWP-DM "flick rhythm"). Victim order is available; gaze/attention/
intended order are not. **Do not ship as a mistake class** — any current label is (4)/(5),
FP: HIGH.

## 6. AWP positioning, scope, follow-up

**Scope mechanics.** Zoom transcribed from client binary (Measured/transcribed, Memorin
https://memorin.app/mechanics/mouse-sensitivity): AWP FOV 90→40→10 (SSG 15; earlier "AWP 15"
inference corrected); scoped sens = zoom_ratio × activeFov/refFov with integer truncation
(non-smooth); shot unzooms 0.05 s → auto-rezooms 0.1 s once ready. `cl_sniper_show_inaccuracy`
circle visualizes settle. Scope sound (click-clack) audible nearby — don't scope tight to
corner early. Slow-scope (settled, crouched, single-zoom) for long/held; quick-scope only
close/mid desperation with randomness accepted; counter-strafe every scoped shot.
Single-zoom default; double-zoom extreme-long only; center-mass default under pressure.
**Settle-ms is a five-way dispute — 100 ms vs 150–250 ms vs +200 ms vs ~0.3 s vs ~1 s —
NONE shippable.** Quick/no-scopes more inconsistent than previous games by design, not glitch.
Scoped move 100 u/s; running inacc scoped 178.7 vs 257.5 unscoped (scope does NOT fix moving fire).

**Positioning discipline (guide + expert corroborated).** Golden rule: **always have escape
route; one shot → reposition (shot-and-swap during bolt); never hold/re-peek same angle
twice.** Entry-frag AWP denies positions and forces rotations; one AWP + space-making
teammates wins rounds (scope.gg coach guide, Expert — CS:GO-era tactics, unverified transfer).
Stat block (Measured third-party, build 1.41.7.6): 115 dmg / 97.5% pen / HS 4× / rangeMod 0.99;
chest-vs-armor one-tap to 5,694 u (~145 m); head/stomach any map distance; legs 86.25 (never
lethal); 41 RPM (1.45 s); mag 5 + reserve 10 (15 post-March-2026); reload 3.7 s (mag-in 2.0 s,
**discards remainder**); deploy 1.25 s; $4,750; $100 kill; mobility 200/scoped 100;
accurate range 1.9 m unscoped → 69.3 m scoped. Pistol covers the bolt window (P250/Five-SeveN;
Deagle if rich); noscope only point-blank desperation (pistol better past ~2 m).
CT long angles with escape; T opening picks with teamplay (never dry-peek CT AWPer);
post-plant anchor from distance; support role (flash entry, smoke angles, trade), not entry.
Buy paths: pistol-win → MP9/MAC-10 round 2 → AWP round 3; T plant funds round-3 AWP.
**Save rule: 1v3/overrun = save the $4,750.**

## 7. Sensitivity (no optima)

cm/360 from CS2 yaw 0.022°/count: 360/(sens×0.022×DPI) inches ×2.54
(800 DPI × 1.0 = 51.9 cm — arithmetic verified). Pro range stated 25–65, median ~45
(Community single-vendor, https://nextfrag.gg/cs2-sensitivity-guide — never a norm).
Method worth inheriting: signed flick-error distribution (overshoot → sens high;
undershoot → low) + reliability score + 3-demo consistency rule — **distribution +
reliability gate, never a per-flick verdict.** Same signed error also comes from rushed
timing, bad pre-aim, or moving fire — sensitivity attribution is (3)/(4).
**Do not invent optimal numerical settings.**

## 8. Utility and round engine facts (patch-gated constants)

| Fact | Value (current) | Tier + source | Patch sensitivity |
|---|---|---|---|
| Flash max blind | ≤4.87–5 s direct look; impact 1–2 HP; explosion 0 HP; **ignores smoke; blinds teammates FULL regardless of FF** | Community (Farmskins durations + damage; Mythras utility guide) | Stable mechanic; durations build-sensitive |
| Smoke | **18 s** from detonation (~17 s usable; thins final 2–3 s; radar-block ~15 s; T-brown/CT-blue→grey tell); volumetric (fills geometry); bullets punch 1–2 s two-way tunnels; **HE opens ~2–3 s window** + clears screen-effect (Oct-2024 verbatim); smoke kills fire both directions; 2026-07-20 detonation clears smoke+fire | Community/Measured-style (Swap.gg Jan-2026; MetaBot; CS2.eu) — Farmskins "20 s" retracted 4:1 | Render/smoke-interaction fixes bound old-demo attribution |
| Fire | Molotov 7 s; **incendiary shorter/smaller since May-2024** (Official: duration + spread reduced, $600→$500; Community-measured ~5.5 s; faster spread since July-2025); ramp ~1→8 HP/tick × 5 ticks/s (≈40 HP/s max); breaks only on walkable ≤30° surface; >2 s airborne fizzles unless pops <128 u above surface | Official (May-2024 changelog via HLTV) + Measured cvar (`inferno_flame_lifetime` = 7 base) + Community | **Never demand symmetric fire value from CT incendiaries** |
| HE | ≤98 HP unarmored / ~57 armored point-blank; ~350 u radius; **detonation briefly disperses smoke** | Community (Farmskins) | Stable |
| Prices / carry | Decoy $50, flash $200 (max 2), smoke $300, HE $300, molotov $400 (T), incendiary $500 (CT); **max 4 grenades** | Community (Mythras) | May-2024 incendiary/M4A4 prices |
| FF (when enabled) | Bullets ×0.33, grenades ×0.85, fire/other ×0.4, self-grenade ×1.0 (competitive); casual/DM/retakes all-zero | **Measured cvar defaults** (TotalCS; Valve wiki) + locally verified in install `gamemode_competitive.cfg` | Mode-gated (competitive/FACEIT scope) |
| Round/clock/bomb | Round 1:55; freeze 15 s; plant ~3–3.2 s (+≥4 s practical); bomb 40 s replacing clock (35 s modes exist); defuse 10 s / 5 s-kit ($400 CT-only, auto-applies, pickup from dead holder); **zero saved progress**; MR12 first-to-13, OT 12–12 | Community (R1GG; Codex) + Measured cvar defaults | Mode-gated (timer/OT variants) |
| Economy: win/loss | Win $3,250 ($3,500 bomb-decided); loss 1400/1900/2400/2900/3400 cap; pistol loss $1,900 | Expert (Refrag) + Community (GuildOrder) | May-2024 plant award; July-2025 CT income |
| Economy: kills | Rifle/pistol/nade $300; SMG $600 (P90 $300); shotgun $900 (XM $600); AWP $100; **Zeus $100 Competitive** ($50 Casual); knife $1,500 | Expert (Refrag) + **Official Apr-2024** (Zeus $0→$100, CZ $100→$300) | Apr-2024 Zeus/CZ |
| Economy: bomb | Planter +$300; **plant-then-loss $600 each T** (Official May-2024 cut from $800) | Official (May-2024 changelog) | **GuildOrder "$800" stale — never cite** |
| Economy: July-2025 | **CTs +$50 per T eliminated even in lost rounds** (dual-sourced Expert + Community); incendiary spreads faster; Overpass in/Anubis out; MP9 recoil+/jump-accuracy nerf | Expert (EGamersWorld 1.45.0 summary) + Community (Skin.club) — Valve body unrecovered, keep patch-date parameter | All force/save breakpoints shift — hardcode none |
| Full buy | ~$4,800/player (rifle + helmet-armor + 2 flash + smoke + molotov); team utility $5.5–6.5k/round; buy order flash > smoke > 2nd flash > molotov > HE | Community (GuildOrder; Mythras) | Post-May-2024 prices assumed |

Benchmarks (reviewer-grade type-2, never verdicts): avg player ~4–6 utility dmg/round,
good 8–12; enemies-flashed-per-flash >0.7 good, <0.4 wasted (RoundScope).
Weapon meta (6.68M pro kills): AK 35.7 / M4-platform ~24 / AWP 10.7 ≈ 70% of kills;
HS rates USP-S 84.6 / Glock 79.5 / AK 57.2 / M4A4 46.3 / M4A1-S 39.6 / AWP 9.3
(body-shot weapon by design); AWP 63.8% CT-side. Map CT balance (~2M rounds):
Train 55.6 / Overpass 55.3 / Nuke 54.1 / Mirage 52.8 / Ancient 51.2 / Dust2 50.2 /
Inferno 49.6 / Anubis 45.0; pistol 50.3/49.7 (fairest round). Side/round expectations are
map-conditional — never use global priors where map splits exist.

## 9. Demo-evidence map (repo-verified)

**Available (recorded, computable from existing tables):** positions/velocity, fire/damage
(server integers), kill order/trades, utility blooms + blind durations, economy/AWP presence,
peek paths/widths/intervals, flash→peek timing, per-tick scoped state (`m_bIsScoped`),
`weapon_zoom` events, extended-`shots` (`scoped` + live `inaccuracy` + `num_bullets_remaining`),
kills (`hitgroup`/`hitgroup_name`, recorded `noscope`, `thrusmoke`/`penetrated`,
`assist_flash`), per-shot cone state at fire time (contract-grade recorded value).
Shippable: velocity-at-fire (burst-aware + weapon-gated), reposition-after-AWP-shot,
repeek intervals, multi-angle exposure (with map + utility context), range-vs-weapon
computation, flash→peek timing, scoped-vs-unscoped at fire.
**Per repo boundary: no `TRADE_WINDOW` constant exists — recompute from `player_death`
timestamps with a declared, labeled window; upstream derived classifications
(`is_trade`/`victim_traded`) are intentionally NOT normalized.**

**Unavailable (never assert):** zoom level (single vs double), settle-at-fire, impact
points/spread, true crosshair point, knowledge/intent/comms, per-moment ping/subtick,
reaction split (mental vs network), enemy crosshair state, spread endpoints,
whether a hold was called, whether a position was truly known.
Scoped-vs-unscoped state IS available — do not claim otherwise.

## 10. Hard demo constraints (inherited, not re-litigated)

- Voice comms absent (never recorded); team chat encrypted since 2026-09-09 — any
  "you should have known because a teammate called it" is unfalsifiable from the demo.
- Demos ≥2026-07-10 use delta-encoded usercmds (demoparser issue #340, fixed 0.42.0
  2026-08-08) — per-demo capability probing + parser pinning mandatory; mouse-delta
  "flick"/placement metrics are indirect and corruptible on mis-parse.
- Tick ambiguity: demo/frame tick ≠ absolute server tick; read interval from file, never
  assume 64/128. Positions/angles are per-tick samples; sub-tick micro-actions
  (exact counter-strafe instant, peek start) are not directly observable.
- Fog of war is inferable only: `spotted`/`m_bSpottedByMask` is a radar-spot flag
  (demoinfocs warns "NOT Line of Sight"; mask↔player mapping covers bits 0–15 only;
  in GOTV most plausibly the spectator client's spotting) — "potential line-of-sight
  reconstruction," never "what the player saw"; awpy LOS is smoke-blind by documentation.
- Sound not stored (approximate from weapon_fire/movement/positions only).
- Nov-2025 TrueView (`cl_demo_predict 2`) reconstructs the observed player with 1–2 frame
  delays — does not restore gaze/intent.

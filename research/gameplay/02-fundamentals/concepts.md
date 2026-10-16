# Individual Fundamentals Concepts — Peeking, Angles & Weapons

**How to read.** Each concept has a stable ID and the 9-point schema adapted from
`01-modern-meta/concepts.md`: (1) meaning · (2) objective · (3) appropriate ·
(4) questionable · (5) reasonable information = reviewer checks · (6) alternatives ·
(7) demo manifestation · (8) not demo-inferable · (9) stable fundamental vs
patch/meta-dependent. Plus: false-positive severity + mechanical / tactical / mixed.

**Confidence labels.** `[measured]` = tested/fitted/transcribed/spreadsheet.
`[official]` = Valve/first-party note. `[expert]` = pro/coach org. `[guide]` = named
practitioner guide (definition-reliable, not efficacy evidence). `[press]` =
secondary/press with disclosed method. `[inference]` = reasoned synthesis.
`[disputed]` = sources contradict; none usable. `[stale]` = predates a relevant patch.
**Citation resolution (frozen-contract compliance).** Every tier label in concepts maps
to one or more `S-` source IDs; full author/title/domain-path/date/patch-period/limits
for each ID live in `sources.md` (access date 2026-10-15 for all). Domains are stored
scheme-less per repo convention (`01-modern-meta/`, `04-decision-evaluation/` identical).

**Global constraints (apply to every concept).** Voice comms are absent from demos;
intent (info vs commit vs bait) MUST be qualified. Judge ex ante, never by duel
outcome (Baron & Hershey 1988). Ranged/weapon numbers are build-stamped
(2026-03-18 spreadsheet baseline; March 2026 ammo rework; Sept 2025 subtick updates;
April 2026 Animgraph2). Zoom level, settle-at-fire, spread endpoints, true crosshair
point, per-moment ping, and knowledge state are demo-unavailable (Memorin VERIFIED
negative: 0 bullet impacts in 9,372 tournament shots). Scoped-vs-unscoped state IS
available (`m_bIsScoped`, `weapon_zoom`, extended-`shots.scoped` — see A01).

---

## P — Peeking & angles

### FUND-P00 — Peeker's advantage in the subtick era

1. **Meaning.** The moving peeker sees the stationary holder before being seen:
   network delay + subtick resolution + mental readiness (initiator vs reactor).
   `[official]` subtick exists (`counter-strike.net/cs2`); `[guide]` components
   (Dignitas 2026-06-16).
2. **Objective.** Explains why committed, stopped, pre-aimed aggression wins duels;
   bounds what a holder can do about it (off-angle/utility/reposition, not reactions).
3. **Appropriate.** Invoking it to justify T-side swing discipline and CT
   counter-positioning. `[guide]` SteamAnalyst 2026-02.
4. **Questionable.** Any numeric claim ("subtick = X ms"; porting lab %/ms to CS2);
   pre-Nov-2024 or pre-Sept-2025 numbers (lag-comp overhaul Nov 2024; subtick
   shooting updates Sept 2025; Animgraph2 Apr 2026). `[stale]` Dignitas/WarOwl 2024 claims.
5. **Reasonable information.** Valve page + Steam notes 2025-09-09 (no subtick text),
   2025-09-16 (Genesis; subtick-consistency = press paraphrase), Tradeit changelog
   compilation (TrueView 2025-11-05, scope-sound 2025-10-30, defuse/scope-block
   2025-10-15, Animgraph2 Apr 2026).
6. **Alternatives.** FDG 2024 lab as mechanism illustration only (FPSci custom game,
   stationary defender, 24 players): defender 60 ms → peeker +28–31% win-delta;
   defender 0 ms → peeker −5–13%; 7→27 m distance significant (F=40.7, p<.001);
   visible→hit gap ~10 ms. `[measured, non-CS2 lab]` — MUST NOT be CS2 thresholds.
7. **Demo manifestation.** None directly (per-moment ping/subtick unrecorded).
   Proxies: swing-initiated duel win rates by role — cohort-level (2), never per-event ms.
8. **Not inferable.** The actual ms advantage in any given duel; mental-readiness split.
9. **Patch-dependent** mechanism + numbers; **stable** principle (initiator sees first).
   **FP: HIGH** if a detector asserts advantage-ms per duel. **Mixed.**

### FUND-P01 — Wide / commit swing (+ pair trade)

1. **Meaning.** Full swing (BO3: 2–3 character widths — `[guide]` estimate, not
   threshold), pre-aimed, counter-strafe → stop → shoot; forces defender crosshair
   drag. Pair variant: P1 pulls crosshair, P2 kills during track. `[guide]`
   MetaBot + BO3.
2. **Objective.** Convert known information into a kill or traded space.
3. **Appropriate.** Known position + rifle + close–mid + stopped + trade partner or
   reload window; follow-up after unanswered jiggle. Steam guide: opening space for
   team (plan to trade), or exact position known with no second trader. `[guide]`
4. **Questionable.** Blind wide into unknown/long/AWP angle; firing while moving;
   no counter-strafe; no trade. Resolved conflict: SteamAnalyst "wide best vs AWPers"
   applies only **after** bait/info — never blind (MetaBot/BO3/Steam-guide agree).
5. **Reviewer checks.** Prior info (intent — unavailable); velocity-at-fire
   (available); range (available); trade proximity (available).
6. **Alternatives.** Jiggle for info first (P02); utility peek (P10); shoulder-bait
   then wide vs AWP (P03).
7. **Demo manifestation.** Long lateral path + full exposure + shot after stop
   (available); kill/trade outcome (available — must not judge by it).
8. **Not inferable.** Whether the position was truly known; why no trader was near.
9. **Stable** mechanics; **patch-dependent** speeds/accuracy. **FP: HIGH** (punishing
   correct aggression as "over-peek"). **Mixed.** Types (1) moving-fire / (4) choice.

### FUND-P02 — Jiggle peek for info / bait

1. **Meaning.** Rapid out-and-back, no shot; exposure "~fraction/tenth of a second"
   (MetaBot wording — `[guide]` estimate, never threshold). Goal = bullet/scope-glint/
   callout. BO3 variant: repeated A/D to break timing. `[guide]` MetaBot + BO3 + CS2.eu.
2. **Objective.** Buy information at near-zero risk; bait the AWP shot.
3. **Appropriate.** Unknown hold; suspected AWP; 1–2 unanswered jiggles = info
   (empty or patient holder) → switch to wide/utility.
4. **Questionable.** Lingering (free frag); shooting mid-jiggle (becomes bad wide —
   MetaBot+BO3 agree); identical rhythm repeated (defender pre-fires next cycle).
5. **Reviewer checks.** Exposure duration (available, within-player compare only, no
   universal cutoff); mid-jiggle shot attempt (available); identical repeat timing
   (available).
6. **Alternatives.** Shoulder-bait vs confirmed AWP (P03); single-peek prefire vs
   anticipated spot (P04); flash peek (P10).
7. **Demo manifestation.** Short displacement + no shot (available); enemy response
   shot (available).
8. **Not inferable.** Intent (info vs failed commit); what the jiggle actually revealed.
9. **Stable** principle; **patch-dependent** exposure timings. **FP: MEDIUM**
   (info-jiggle misread as "passive/bounce peek"). **Mixed.** Types (3)/(4).

### FUND-P03 — Shoulder peek / bait (AWP-specific jiggle)

1. **Meaning.** Sliver exposure, head behind wall; baits AWP shot → punish ~1.45 s
   bolt window with wide swing or teammate swing. `[guide]` MetaBot + BO3.
2. **Objective.** Strip the AWPer's one-shot strength; convert into reload-window punish.
3. **Appropriate.** ONLY vs scoped sniper on long angle; afterplant info on incoming
   CTs (Steam guide).
4. **Questionable.** Showing too much/too long; vs rifle holder ("useless if holding
   with a rifle" — MetaBot). Steam-guide precision rule: "if you see your enemy,
   you're doing it wrong" (he saw more than shoulder). Adaptive risk: AWPers learn
   to hold the bait → switch method (Steam guide).
5. **Reviewer checks.** AWP presence (killfeed/damage — partially available);
   exposure minimal (available).
6. **Alternatives.** Full jiggle rhythm-break (P02); smoke off the AWP angle;
   wide trade with flash (P10/P01).
7. **Demo manifestation.** Minimal exposure + enemy AWP shot + little/no damage
   (available).
8. **Not inferable.** Whether the AWPer was actually baited vs holding; head-vs-shoulder
   pixel truth (no impact data).
9. **Stable** tactic; **patch-dependent** bolt/reload timings. **FP: MEDIUM-HIGH**
   (identical to failed jiggle vs rifles). **Tactical.** Types (3)/(4).

### FUND-P04 — Single-peek isolated clear + slice-the-pie / isolate-one-angle

1. **Meaning.** Methodical clear exposing one angle at a time: Steam-guide
   "Singlepeek" (sidestep, pre-aim anticipated spot, head-level AK/M4 prefire, jiggle
   back; teammate holds checked angle; best late-round ~40–30 s when enemy utility
   gone) + SteamAnalyst/Dignitas "slice the pie" (slow strafe, never multi-sightline).
   `[guide]` Steam guide; `[expert]`-org advice SteamAnalyst/Dignitas-improve.
2. **Objective.** Clear without gambling on multi-angle exposure; needs map +
   common-angle knowledge.
3. **Appropriate.** Retakes/entries; late-round low-utility states; with teammate
   holding checked angles.
4. **Questionable.** Swinging into 2+ sightlines (death regardless of aim —
   "number one peeking mistake at every rank," SteamAnalyst). Enemies adapt with
   off-angles/saved flash vs repeated single-peeks (Steam guide).
5. **Reviewer checks.** Teammate positions (available); active smokes/flashes/mollies
   (available); sightline count (needs map geometry). General rule (Steam guide):
   eliminate other angles with smokes/flashes/molotovs, prefire, peek with teammate.
6. **Alternatives.** Traded entry (teammate covers 2nd); utility-covered multi-exposure;
   slow default for info instead of committed clear.
7. **Demo manifestation.** Path vs map geometry + simultaneous sightline count
   (available with map data).
8. **Not inferable.** Whether the player knew the second angle existed; called
   coverage assignments.
9. **Stable** geometric principle; **patch/meta-dependent** common angles + utility.
   **FP: HIGH without utility/teammate context. Tactical.** Type (4).

### FUND-P05 — Jump / Ferrari info peek + crouch mixup

1. **Meaning.** Ferrari = running jump past angle at full speed for info (AWP spot,
   site count); never shoot mid-jump (SteamAnalyst). Crouch peek drops head below
   expected level so first shot whiffs over; sparing mixup only (SteamAnalyst,
   Dignitas, CS2.eu). Gamers.Wiki: crouch-peek scoped preserves accuracy on slow
   committed scoped peek; aim center-mass vs crouch-peekers. `[guide]` (weak —
   guide-only corroboration).
2. **Objective.** Free information (jump) / one-time head-level break (crouch).
3. **Appropriate.** Jump: AWP-spot/site-count when trader/cover exists. Crouch:
   surprise mixup, mid-spray committed close, behind cover (CS2.eu).
4. **Questionable.** Jump into rifle spray; crouch as default reaction — never first
   bullet / while peeking / vs multiples (CS2.eu); crouch-every-time gets pre-aimed
   low; crouching slow = commit. Crouch-walk silent but slowest.
5. **Reviewer checks.** z-velocity / crouch flag at exposure (available); enemy
   weapon class (partial); trader presence (available).
6. **Alternatives.** Grounded jiggle (P02); wide commit with info (P01); flash peek (P10).
7. **Demo manifestation.** z-velocity / crouch flag at exposure (available).
8. **Not inferable.** Whether crouch was deliberate mixup vs panic.
9. **Stable** mechanics; **patch-dependent** move speeds. **FP: HIGH. Mechanical.**
   Type (3).

### FUND-P06 — Counter-strafe + ADAD + moving-fire

1. **Meaning.** Tap opposite key → full stop before firing; do NOT just release keys
   (Steam guide). Fire at ADAD apex/zero-crossing (strafe→stop→shoot→strafe).
   Jiggle/shoulder need no stop (no shot). Unanimous across all guides. `[guide]`
2. **Objective.** First-bullet accuracy; the bridge between movement and shooting.
3. **Appropriate.** Before every rifle/AWP shot taken while moving; `cl_showpos 1` +
   `sv_showimpacts 1` wall drill; `weapon_accuracy_nospread 1` to isolate recoil.
   Snap Tap (Razer auto-counter-strafe) banned by Valve — manual only (SteamAnalyst).
4. **Questionable.** Shooting mid-stride (forfeits peeker's advantage); Dignitas
   "bounce peek" (swinging back so fast accuracy never settles — fear-driven);
   spraying past ~5 missed bullets instead of reset→reposition→re-engage
   (SteamAnalyst heuristic). Stop-timing numbers, corrected 2026-10-15 with
   MechanicsCore peer-slice deltas: the 34% max-speed threshold upgrades from
   site-claimed to **model-doc + lineage-measured** (Steam VScript accuracy model:
   movement inaccuracy accrues past 34% max speed, linearly scaled by InaccuracyMove;
   2015 DevinDTV/SlothSquadron 73/74 sweep at AK 215 as lineage origin) — still not
   Valve-CS2-primary, but above site-claimed; usable as threshold with tier stated.
   SteamAnalyst "~88 u/s with a rifle" is **arithmetically wrong**, not merely
   unverified (0.34×215=73.1; 0.34×225=76.5; 88/215≈41%). Guide "1–2 vs ~10 frames"
   understates pure key-release coast ~2.5×: computed from Memorin-measured friction
   5.2/stopspeed 80 (2026-07-27, below-knee drop 6.5010=80×5.2/64), full-run release
   takes ~13 ticks to 34%, ~24–26 to zero (via MechanicsCore); local mixed-braking
   median is 9 ticks total-run / 7 to 34% (validation-v1, n=945/913 runs) —
   consistent with active counter-strafe beating pure coast. CS2.eu "accurate in
   about 50 ms" remains site-claimed/unverified. Gamers.Wiki "CS2 momentum feels
   stricter" = subjective.
5. **Reviewer checks.** Velocity-at-fire (available — strongest signal in slice);
   drill with impacts (practice, not demo).
6. **Alternatives.** Pre-stopped hold; crouch mid-spray when committed close (P05);
   burst-reset discipline.
7. **Demo manifestation.** Speed>0 at shot = **(1) directly observable mechanical
   error** (available).
8. **Not inferable.** The exact accuracy penalty per weapon/state (inaccuracy curves
   not sourced here); intent behind movement. **Confound (via MechanicsCore peer
   slice, full detail in their Main report):** `m_flTurningInaccuracy` — fast
   view-turns add a cone penalty independent of movement speed, so flick-heavy shots
   can miss while fully stopped. Any velocity-at-fire or flick/sensitivity analysis
   ignoring turn rate inherits this confound; yaw-delta-per-tick should gate flick
   verdicts alongside speed.
9. **Stable** principle; **patch-dependent** thresholds/curves. **FP: LOW if velocity
   measured; HIGH if inferred from outcome. Mechanical.**

### FUND-P07 — Swing / exposure / repeek timing

1. **Meaning.** Peek timing as a weapon: change timing/width every peek (MetaBot:
   never wide same spot twice); hesitant peeks hand back the advantage (BO3,
   SteamAnalyst); Gamers.Wiki cardinal sin: "Never re-peek the same angle twice"
   after a shot — fall back, re-engage from a different spot. `[guide]` consensus.
2. **Objective.** Deny pre-aim; punish only during genuine windows (AWP bolt, flash,
   trade).
3. **Appropriate.** Deliberate fast punish during AWP bolt window or with flash/trade;
   varied timing/width across rounds.
4. **Questionable.** Slow telegraphed swing; instant same-angle repeek into pre-aim;
   identical rhythm. NOTE scoping vs `04-decision-evaluation` slogan #4 ("Never
   repeek" misleads by conflating committing repeeks with free info jiggles): this
   concept covers **committing** repeeks; P02 jiggles are exempt.
5. **Reviewer checks.** Inter-peek interval + width deltas across events (available);
   utility/trade context (available). Requires the peek-1→peek-2 info delta, which
   demos rarely resolve (repo 04 finding).
6. **Alternatives.** Reposition to secondary angle overlooking same lane; silent-walk
   off-angle variation; utility-forced re-clear.
7. **Demo manifestation.** Intervals + widths + same-angle repeats (available).
8. **Not inferable.** Whether the repeeker believed the window was open (info delta).
9. **Stable** principle; **patch-dependent** window lengths. **FP: MEDIUM**
   (punish ≡ impatience). **Tactical.** Type (4). No measured peek-ms distributions
   exist — never emit "correct = X ms."

### FUND-P08 — Movement while clearing: walk/shift, confidence, corner distance, speeds

1. **Meaning.** Clearing movement choices: Dignitas — stop shift-peeking by default
   (slow walk gives time to adjust), peek at speed exploiting pre-footstep-noise
   window, every peek "expect someone holding" (lazy clears = easy kills), commit
   (half-baked dies). Walk rules (SteamAnalyst+CS2.eu): Shift = zero footsteps for
   flank/close-angle/fake/off-angle/ladder; stop when time-critical/known/must swing.
   Corner distance (SteamAnalyst §6): **far = see first via perspective (best holding
   rifles); close = fast cover (shotguns / vs flash / fast retreat).** `[guide]`
2. **Objective.** Arrive unseen at speed, or unheard when sound matters; hold from
   geometry that favors your weapon.
3. **Appropriate.** Full-speed clears by default; shift-walk for flank/close/fake/
   off-angle/ladder; far holds with rifles; close holds with shotguns or vs flash.
   Off-angles (step aside, height, non-meta) beat pre-aim; reposition after every
   kill/spot ("one-and-done" CT); trades (entry + 1–2 s trader). Head hitbox smaller
   at range favors rifle holders; AWP negates. Landing from height makes sound (CS2.eu).
4. **Questionable.** Default shift-clearing open angles; holding close with a rifle
   into a long perspective disadvantage; staying on a known position after a kill.
   **Exception (reviewer judgment, unsourced):** late-round low-noise shift-walk can
   be correct.
5. **Reviewer checks.** Speed-at-exposure (available); sound-relevant state
   (approximate); corner distance (available); post-kill repositioning (available).
   "Expectation"/intent unavailable.
6. **Alternatives.** Utility-masked walk-up; traded entry; off-angle re-hold.
7. **Demo manifestation.** Speeds/positions (available, version-sensitive table:
   knife 250 / pistol 240 / SMG 240 / rifle 215 / AWP 200 u/s; crouch ~85/82/82/74/68;
   bhop cap ~300). Rifles "terrible" moving, SMG slightly better, AWP must stand still.
8. **Not inferable.** Whether quiet was actually needed (enemy positions unheard in demo).
9. **Stable** geometry/sound principles; **patch-dependent** speeds/constants.
   **FP: MEDIUM. Mixed.** Type (4).

### FUND-P09 — Tracking / target-switching while clearing [OPEN — no evidence base]

1. **Meaning.** The claimed skill of moving the crosshair across multiple targets
   during a clear, incl. spray-transfer (drag through recoil pattern to 2nd target
   without reset — SteamAnalyst §2) and Ferrari-trade implication. `[guide]` practice
   claims only (Gamers.Wiki: AWP DM builds "flick rhythm, target switching"; duel
   servers practice "punishing jiggle peeks").
2. **Objective.** Multi-kill conversion during executes/retakes.
3. **Appropriate.** Cannot be stated — no error-rate evidence exists.
4. **Questionable.** Labeling any multi-victim sequence a "failed switch."
5. **Reviewer checks.** Positions + victim order (available) — necessary but not
   sufficient; gaze/crosshair target (unavailable).
6. **Alternatives.** Pre-planned transfer order; trader covers second angle instead.
7. **Demo manifestation.** Victim order only (available).
8. **Not inferable.** Gaze, attention, intended target order.
9. **Unresolved.** **Do not ship as a mistake class** until an annotated pro-demo
   study exists. Any current label = **(4)/(5), never (1).** **FP: HIGH.**

### FUND-P10 — Utility-combined peeks (flash / molly / smoke timing)

1. **Meaning.** Peek synchronized with utility: pop-flash → peek at detonation
   (blind ~2 s; self wall-bounce best); molly forces reposition → peek during spread;
   one-ways + off-angle ≈ free kills; default utility peek over dry peek
   (SteamAnalyst §7). Steam-guide nuance: blinding flash must be unheard/unseen
   before pop (no loud/visible bounce; right-click grenade prep audible); semi-obvious
   flash turns enemy → peek before pop catches back turned; flash pops behind peeker
   on simultaneous peek; combinable with every peek type. `[guide]`
2. **Objective.** Convert utility into a guaranteed unfair duel.
3. **Appropriate.** Whenever utility is available and the angle is clearable with it;
   molly-displaced holders; smoke-blocked AWP lanes.
4. **Questionable.** Dry-peeking a clearable-with-utility angle; peeking before pop /
   after blind expires. **Correct dry peek:** info jiggles, eco (no nades), trader present.
5. **Reviewer checks.** Inventory/utility state (available); flash→peek interval,
   blinded-enemy state, molly spread timing (available).
6. **Alternatives.** Smoke-block + cross; molly-flush then re-clear; save utility
   for execute (eco-dependent).
7. **Demo manifestation.** Detonation→peek timing + blind durations (available).
8. **Not inferable.** Whether the peeker timed to the pop deliberately vs luckily.
9. **Stable** timing principle; **patch-dependent** blind/utility constants.
   **FP: MEDIUM. Tactical.** Type (4).

---

## R — Crosshair placement vs positioning

### FUND-R01 — Crosshair placement (aim preset)

1. **Meaning.** Crosshair where the model will intersect, ideally head: "closest-angle"
   rule (hug nearest threat corner); head-level horizontal line; hug wall edge with
   ~one-head-width gap (SteamAnalyst); avoid floor/sky; minimize flick distance
   ("lazy crosshair syndrome" — scope.gg). `[expert]` scope.gg coach blog;
   `[guide]` SteamAnalyst §1, Dignitas (habit; post-peek window fraction of a second).
2. **Objective.** Zero-adjustment first shot inside the post-peek window.
3. **Appropriate.** Pre-aim common holds (Dust2 long pit/car/boxes; Mirage
   window/connector); micro-adjust for elevation (Mirage ramp up, Inferno top-mid down);
   study donk/m0NESY/NiKo POV (never drops — SteamAnalyst).
4. **Questionable.** Floor/sky-gazing; wide wall gap; static height across elevation
   changes. AWP variant: center-mass over headshots under pressure (Gamers.Wiki —
   larger target wins rounds).
5. **Reviewer checks.** View pitch at exposure (head-level? — available, approximate);
   aim offset vs angle edge (approximate); map elevation at angle (available).
6. **Alternatives.** Wider pre-aim vs off-angle-heavy opponents; center-mass default
   with AWP/low-confidence spray.
7. **Demo manifestation.** View angles only — true screen point **unavailable**;
   placement error is approximate by construction.
8. **Not inferable.** Exact crosshair pixel; whether misplacement caused the miss
   (spread/inaccuracy confound — no impact data).
9. **Stable** habit principle; **patch/meta-dependent** common holds + elevations.
   **FP: HIGH (map elevation changes legit head height). Mechanical.** Type (3).

### FUND-R02 — Positioning (body / geometry)

1. **Meaning.** Where the body stands: corner distance, off-angle selection,
   sightline count, cover/escape, trade proximity. Far = see first (rifles); close =
   fast cover (shotguns/flash/retreat). Off-angles (step aside, height, non-meta)
   beat pre-aim. `[guide]` SteamAnalyst §6.
2. **Objective.** First shot + escape + tradability.
3. **Appropriate.** Far holds with rifles; close holds with shotguns; off-angle
   re-holds; one-and-done CT repositioning; entry + 1–2 s trader.
4. **Questionable.** Multi-sightline exposure without trade/utility (see P04);
   same-angle re-hold after being spotted; long challenge with falloff-weak weapon
   (see W02).
5. **Reviewer checks.** Geometry + sightlines (available with map data); teammate
   positions (available); utility state (available); weapon-vs-range (computable, §4).
6. **Alternatives.** Utility-masked position; crossfire setup; rotate rather than hold.
7. **Demo manifestation.** Positions/geometry (available).
8. **Not inferable.** Called vs freelanced position; what the holder expected.
9. **Stable** geometry; **patch/meta-dependent** angles/utility. **FP: MEDIUM.
   Tactical.** Type (4).

### FUND-R03 — Practice stack for placement/movement (context, not a mistake)

1. **Meaning.** Convergent training prescription (SteamAnalyst §8 `[guide]`):
   10-min aim-trainer → 10-min Yprac Recoil Master (incl. transfers) → 10-min Yprac
   prefire → 15-min purposeful single-focus DM → 10-min weekly demo review
   (head height? counter-strafe? too many angles? reposition after spot?).
   80/20: 5-min spray + 10-min prefire. Maps: Aim Botz, Yprac Recoil/Prefire,
   Fast Aim/Reflex, crashz Crosshair Generator, 5E AimHub.
2. **Objective.** Review prompts double as the demo-review checklist for P06/R01/P04.
3. **Appropriate / questionable.** N/A (not a behavior to judge).
4. Rest of schema N/A — included so future reviewers reuse validated prompts, not
   invented ones.

---

## W — Weapon engagement behavior

### FUND-W01 — Damage formula (range / hitgroup / armor)

1. **Meaning.** `floor(damage × rangeModifier^(distance/500) × hitgroup × armor)`;
   single floor at end; distance = shooter → **hit point on hitbox** (proven by
   adjacent 21.03 vs 21.10 rows straddling a floor boundary); head per-weapon
   (M4A1-S 3.475, Deagle 3.9 — not global 4×); stomach 1.25; legs 0.75 never
   armoured; armoured health = raw × (armorRatio × 0.5). `[measured]` Memorin,
   proto 14166 + compiled weapon data + convars, 29/30 events exact.
2. **Objective.** Compute, don't sloganize: range-vs-weapon verdicts come from this
   formula + table (W02), never from class folklore.
3. **Appropriate.** "Wrong gun for range" computed per-weapon with build + distance.
4. **Questionable.** Global-4× head math; origin-distance math; rounding instead of
   flooring (fits only 16/30).
5. **Reviewer checks.** Reconstruction `damages` carries recorded attacker_xyz +
   victim_xyz + `hitgroup`/`hitgroup_name` per non-fatal hit (`normalize.py:410-442`,
   `extended=True` via `PROFILE_NORMALIZERS`, line 1024) — exact per-hit distance and
   hitgroup, no position interpolation needed. Foundation profile: weapon + damage
   integers only.
6. **Alternatives.** Fatal-HS-range breakpoint table (Tradeit) for quick screening.
7. **Demo manifestation.** Damage integers are server-authoritative oracle (available);
   positions + hitgroup per hit are reconstruction-only (available).
8. **Not inferable.** Spread/penetration endpoints (no impact events — unavailable).
9. **Stable** formula shape; **patch-dependent** constants. **FP: LOW when computed
   with build-correct table. Mixed (mechanical fact + tactical choice).**

### FUND-W02 — Per-weapon falloff classes (rifle vs SMG vs pistol)

1. **Meaning.** Spreadsheet-derived CS2 table (Tradeit, checked 2026-07-20 vs
   community spreadsheet + Valve history + damage guide; 34 firearms / 16 fields /
   2026 magazine-discard model). Falloff = % lost per 500 Hammer units (~12.7 m);
   rangeModifier = 1 − falloff. Tier **Measured (third-party spreadsheet, not Valve)**.
   Full numbers in `weapon-data.md`; headliners: rifles 2–6% (AK 2%, M4A4 3%,
   M4A1-S 6%, others 2–4%); SMGs 13–25% (UMP-45 25% worst, MP9/MP7/MP5-SD 13% best);
   pistols 6–21% (R8 6% best, Dualies/Tec-9 21% worst); snipers 1–2% (AWP 1% best);
   shotguns 30–55% per pellet (harshest); MGs 3%. Fandom CS:GO-era table is
   **carryover UNVERIFIED for CS2** — prefer Tradeit.
2. **Objective.** Ground "rifles long, SMGs/pistols close" in numbers; buy/position
   by expected distance (M4A4 33 vs UMP-45 35 point-blank → 32 vs 28 @10 m →
   30 vs <15 @50 m Mirage mid — cs.money illustration `[guide]`).
3. **Appropriate.** Class-level priors + per-weapon verification before any verdict.
4. **Questionable.** Any universal class distance threshold ("SMGs useless past X m"
   without per-weapon math); mixing Codex Deagle 63 with Tradeit Deagle 53
   (**discrepancy — build-check before use**); citing Fandom CS:GO modifiers as CS2.
5. **Reviewer checks.** Weapon + distance (available); falloff row for build
   (table; binary unverified); armor/hitgroup (available).
6. **Alternatives.** Fatal-HS-range screen (thousands of meters = one-shot everywhere
   practical); M4A4-vs-A1-S role split (Gamers.Wiki: A4 anchor/volume/long-consistent;
   A1-S stealth/mid-precision — Community, plus `[disputed]` 80%-pro claim).
7. **Demo manifestation.** Damage-by-range computable (available).
8. **Not inferable.** Whether the player chose the weapon for this distance vs
   economy forced it (buy context needed).
9. **Patch-dependent** table; **stable** class ordering. **FP: MEDIUM without
   economy context. Tactical.** Full table: `weapon-data.md`.

### FUND-W03 — Fire-mode by range + moving-fire handling

1. **Meaning.** SteamAnalyst heuristic (meters approximate `[guide]`): close 0–10 m
   full spray center-mass→head + crouch mid-fight; medium 10–25 m burst 3–5 head-level;
   long 25 m+ tap/2-rd head-only, ~0.4 s AK reset; first ~10 rifle rounds ~straight up.
   Canonical errors: spray-at-long, running-and-shooting. Handling layer (Tradeit,
   spreadsheet): movement/stance change **inaccuracy, not damage** ("running does not
   reduce damage… expands inaccuracy"); AK run-inacc 182.07 (extremely unreliable at
   distance) vs Tec-9 10.71 (forgiving); crouch tightens first shot but slow +
   predictable = expensive; scopes improve stationary precision only; recoil scalar ≠
   spray ranking; silencers keep-damage, change accuracy/recoil/tracers/sound
   (USP-S/M4A1-S attached preferable); SMG 100% tagging gated by damage/armor ("a hit
   is not automatically a full stop"); pen tiers 100/200/250 (Deagle/R8 200);
   magazine-discard: partial reload destroys remainder ("do not auto-reload a 27-round AK").
2. **Objective.** Match fire discipline to distance; stop-then-shoot always.
3. **Appropriate.** Spray close committed; burst mid; tap long; silence/tracers as
   information play (M4A1-S smoke-spam, off-angle lurk — Gamers.Wiki).
4. **Questionable.** Full-spray long; moving fire at distance with rifles;
   detaching silencers for normal engagements; auto-reloading partial mags in the open.
5. **Reviewer checks.** Distance + fire mode (available); velocity-at-fire
   (available — see P06); reload timing vs safety (available); silencer state
   (demo-field dependent).
6. **Alternatives.** Reposition closer (SMG) / disengage (rifle at extreme);
   utility to close gap.
7. **Demo manifestation.** Shots/damage/velocity (available); spread endpoints
   (unavailable).
8. **Not inferable.** Intended fire mode vs panic spray.
9. **Stable** discipline; **patch-dependent** meters/scalars. **FP: MEDIUM
   (mode inferred from outcome). Mixed.**

---

## A — AWP

### FUND-A01 — AWP scope mechanics (zoom / settle / sound)

1. **Meaning.** Zoom transcribed from client binary T3 (manifest 5183754434502602414):
   AWP FOV 90→40→10 (SSG 15; earlier "AWP 15" inference corrected); scoped sens =
   zoom_ratio × activeFov/refFov with integer truncation (not smooth); shot unzooms
   0.05 s → auto-rezooms 0.1 s once ready. `[measured/transcribed]` Memorin.
   `cl_sniper_show_inaccuracy` circle visualizes settle (BO3). Scope sound (Mouse 2
   click-clack) audible nearby — don't scope tight to corner early (Gamers.Wiki).
   `[guide]`
2. **Objective.** Slow-scope (settled, crouched, single-zoom) for long/held; quick-scope
   only close/mid desperation with randomness accepted; counter-strafe every scoped shot.
3. **Appropriate.** Single-zoom default (FOV + faster settle); double-zoom only extreme
   long; crouch+settled = max accuracy (BO3); center-mass default under pressure
   (Gamers.Wiki).
4. **Questionable.** Firing unsettled at long; double-zoom overuse; moving scoped fire
   (≈ guess — running inacc 178.7 scoped vs 257.5 unscoped, CSBePro); scoping audibly
   tight to corner. **Settle-ms is a four-way dispute — BO3 150–250 vs CS2.eu ~100 vs
   Gamers.Wiki +200 vs Liquipedia-via-wiki ~0.3 s stationary — NONE shippable.**
   Quick/no-scopes more inconsistent than previous games by design, not glitch
   (Liquipedia-via-wiki).
5. **Reviewer checks.** Positions/shots/damage/scoped-state (available: `m_bIsScoped`,
   `weapon_zoom`, extended-`shots.scoped`). Zoom level + settle-at-fire + spread
   endpoints: **unavailable** — "fired unsettled" is inference-only.
6. **Alternatives.** Noscope only point-blank desperation (pistol better past ~2 m —
7. **Demo manifestation.** Repositioning/shots/damage (available); per-tick scoped
   state **available** — backend-verified 2026-10-15: awpy schema maps
   `is_scoped ← m_bIsScoped` (snapshot column, `awpy/schema.py:56`), `weapon_zoom`
   game event exists, and reconstruction-profile `shots` carries `scoped` +
   `inaccuracy` + `num_bullets_remaining` (`normalize.py:1024` runs
   `_shots(..., extended=True)`; foundation profile uses `extended=False` and lacks
   these columns — profile qualifier matters for detector queries).
   What remains unavailable: zoom *level* (single vs double), settle state at fire,
   and spread endpoints (Memorin: 0 impacts in 9,372 shots).
8. **Not inferable.** Whether the scope was settled at fire; zoom level used.
   Scoped-vs-unscoped at fire IS inferable (do not claim otherwise).
9. **Stable** zoom/FOV transcription; **patch-dependent** settle tuning + Nov 2025
   "Delay Un-Scope after Shot" fix + Oct 2025 scope-sound/visual-inaccuracy changes.
   **FP: HIGH. Mechanical + tactical.** Types (1)-adjacent but must be filed as (3).

### FUND-A02 — AWP positioning, repositioning & follow-up

1. **Meaning.** Golden rule (CS2.eu+Gamers.Wiki `[guide]`, corroborated scope.gg
   `[expert]` CS:GO-era): **always have escape route; take one shot and reposition
   (shot-and-swap to pre-planned cover during bolt); never hold/re-peek same angle
   twice (pre-aimed).** Entry-frag AWP denies positions, forces rotations; one AWP +
   space-making teammates wins rounds (scope.gg). Stat block: 115 dmg / 97.5% pen /
   HS 4× / rangeMod 0.99; chest-vs-armor one-tap to 5,694u (~145 m); head/stomach any
   map distance; legs 86.25 (never lethal); 41 RPM (1.45 s); mag 5 / reserve 10
   (15 post-March-2026); reload 3.67 s (mag-in 2.0 s, discards remainder); deploy
   1.25 s; $4,750; $100 kill; mobility 200 / scoped 100; accurate range 1.9 m → 69.3 m
   scoped. `[measured]` CSBePro build 1.41.7.6, corroborated Tradeit/Gamers.Wiki/wiki.
   Full table: `weapon-data.md`.
2. **Objective.** One shot → disappear → next shot from a new angle; pistol covers
   the bolt window (P250/Five-Seven; Deagle if rich; avoid CZ long-deploy, Tec-9
   assault-role — scope.gg).
3. **Appropriate.** CT long angles/early picks from spawn timing (Dust2 doors/Long/
   B plat; Mirage Window/Ticket/Apts-Van; Inferno Coffins/Banana/Arch-TopMid; Overpass
   Long/Heaven; Nuke Outside/Heaven) with escape; crack sound as barrier + silent-walk
   variation; T opening picks with teamplay (never dry-peek CT AWPer), mid control,
   post-plant anchor from distance (Mirage Palace/Jungle; Inferno 2nd-mid/Banana);
   support role (flash entry, smoke angles, trade) not entry. Utility mandatory
   (oneways/instant pops/teammate flash; smoke off enemy AWP; pop-flash out of smoke;
   fall back to retake if fully smoked). Off-angles 200–300 ms off pre-aim; 2–3
   positions per angle, rotate rounds. Double-AWP crossfire; HE-nudged smoke gaps.
   Quick-reload knife-switch = mobility not fire-rate; quick-switch sidearm-and-back
   to exit first zoom (Liquipedia-via-wiki).
4. **Questionable.** Staying/repeeking same angle after miss ("over-peeking," mistakes
   #1/#3 CS2.eu); unnecessary duels with advantage; no utility; buying when team broke;
   reloading with rounds left (discards) or unsafe ~4 s; aiming leg-level; noscope past
   ~2 m; staying in fight during bolt; 2nd/3rd AWP (immobile); camping all round;
   dropping to "best" instead of best-positioned teammate.
5. **Reviewer checks.** Post-shot displacement + angle change (available — shippable);
   cover/escape geometry (available); utility/teammate state (available); economy at
   buy time (available); save-vs-die in lost rounds (available). Reconstruction-only
   upgrades (backend-verified 2026-10-15, `normalize.py:325-344/382-389`,
   `extended=True`): `kills.hitgroup`/`hitgroup_name` (leg-shot failure directly
   computable), `kills.noscope` (recorded `player_death` flag — noscope-past-2 m
   failure directly computable), `kills.thrusmoke`/`penetrated` (wallbang context).
   Foundation profile lacks all four — profile qualifier applies.
6. **Alternatives.** Rifle instead of AWP (no cover/trade/armor/utility); save the
   $4,750 (Save Rule: 1v3/overrun = save); rifle rounds to rebuild bank ($100/kill).
   Buy paths: pistol-win → MP9/MAC-10 round 2 → AWP round 3; T plant funds round-3 AWP;
   CT pistol kill + full eco = round-3 glass cannon.
7. **Demo manifestation.** Reposition-after-shot, repeek-same-angle, save behavior,
   buy context (all available); leg-shot kills and noscope kills (reconstruction-only,
   recorded fields — available).
8. **Not inferable.** Scope settle at fire (A01); whether a hold was called.
9. **Stable** discipline; **patch-dependent** ammo/economy/positions. **FP: LOW for
   reposition-after-shot, leg-shot kill, and recorded-noscope kill (directly observed
   fields); HIGH for "fired unsettled." Tactical (+mechanical execution).**

---

## X — Cross-cutting constraints

### FUND-X01 — Demo-evidence map for fundamentals

1. **Meaning.** **Available:** positions/velocity, fire/damage (server integers),
   kill order/trades, utility blooms + blind durations, economy/AWP presence, peek
   paths/widths/intervals, flash→peek timing, per-tick scoped state (`m_bIsScoped`),
   `weapon_zoom` events, extended-`shots` `scoped` + `inaccuracy`. Backend-verified
   2026-10-15: domain contracts carry `velocity_x/y/z`
   (`domain/contracts.py:340-342`, `domain/tables.py`), awpy schema maps
   `is_scoped ← m_bIsScoped` (`awpy/schema.py:56`), and the awpy adapter normalizes
   players/rounds/kills/damages/shots/bomb/blinds/smokes (`parsing/awpy_adapter.py`)
   — so velocity-at-fire, reposition-after-shot, repeek intervals, flash→peek timing,
   and scoped-vs-unscoped at fire are computable from existing tables, not aspirational.
   **Unavailable:** zoom level, settle-at-fire, impact points/spread (0/9,372), true
   crosshair point, knowledge/intent, per-moment ping/subtick, reaction split
   (mental vs network). Scoped-vs-unscoped state itself IS available
   (`m_bIsScoped`, `weapon_zoom`, extended-`shots.scoped` — see A01).
   Per repo boundary: smoke occlusion + information set (no comms/gaze/POV) further cap
   verdicts; per-demo parser probing (demoparser2 ≥0.42.0 post-2026-07-10 usercmd).
   Nov 2025 TrueView (`cl_demo_predict 2`) reconstructs observed player via prediction
   re-run with 1–2 frame reaction delays — does not restore gaze/intent.
2. **Objective.** Route each concept to shippable (velocity-at-fire, reposition-after-
   AWP-shot, repeek intervals, multi-angle exposure with map+utility context,
   range-vs-weapon computation, flash→peek timing, scoped-vs-unscoped at fire) vs
   inference-only (placement precision, scope-settle/zoom-level, jiggle intent,
   target-switch cognition).
3. Rest of schema N/A — methodological constraint, not a behavior.

# Common Mistake Patterns — Searchable Reference

**Use:** look up by ID. Each entry: observable symptom · possible causes · genuinely
problematic context · legitimate exceptions · reviewer checks · demo-available vs
unavailable evidence · false-positive severity · mechanical / tactical / mixed.
No automatic thresholds or detector implementations are prescribed.

**Claim classes:** (1) directly observable mechanical error · (2) measured performance
characteristic · (3) potential execution issue · (4) context-dependent decision ·
(5) unsupported attribution (never emitted).
**Tiers:** Measured / Official / Expert / Community. Full citations in `sources.md`.
Engine constants in `mechanics.md` §8. Trade windows: awpy 3.0.0 = 5.25 s recovery,
HLTV denial/failed-trade = 5 s, HLTV saved-teammate = 1 s readiness — label every flag.

## Mechanical execution (FUND-001–012)

### FUND-001 — Firing while moving (rifle/AWP, no plant)
- **Symptom:** shot taken with velocity above the weapon's accurate band. **(1)** when
  velocity measured at fire tick; (3) when inferred from outcome.
- **Causes:** firing before stop completes; no counter-tap; over-long counter-key
  (accelerates back); panic fire mid-swing.
- **Problematic:** mid-range rifle duel, first bullet on the move, repeated across fights.
- **Exceptions:** crab-walk (crouched); point-blank target-fills-screen spray; deliberate
  wide-swing speed tactic; USP-S/MP9-class forgiving weapons at close range (2.8–3.2× ratios).
- **Check:** velocity at fire ±1 tick; weapon max speed + 34% band; crouch; spotted-gating
  (else smoke/wall spam pollutes); burst position (first-of-burst vs mid-spray);
  sample across demos.
- **Demo:** available — velocity + weapon + crouch + fire event (+ live `inaccuracy` per shot).
  Unavailable — keypresses (inferred from vector reversal), sub-tick input order.
- **FP severity: MEDIUM-HIGH** (HIGH if outcome-inferred; LOW only burst-aware + weapon-gated +
  spotted-gated). **Mechanical.** (Concepts: FUND-P06.)

### FUND-002 — Shooting before the stop completes ("shooting too early")
- **Symptom:** fire 1–12 ticks after release while still coasting above band. **(1)/(3).**
- **Causes:** mistimed trigger vs stop; underestimating ~13-tick coast from full run;
  "Looking Stopped vs. Being Accurate" (model looks planted, velocity not).
- **Problematic:** opening duel of a peek; first-bullet whiff then lost fight.
- **Exceptions:** close-range commit where speed matters more than first-bullet cone.
- **Check:** release-to-fire tick delta; speed curve vs friction decay; within-player compare only.
- **Demo:** available (velocity series). Unavailable (exact key-release instant — sub-tick).
- **FP: MEDIUM. Mechanical.**

### FUND-003 — Spraying past effectiveness instead of reset/reposition
- **Symptom:** holding trigger past ~7–15 rounds at mid/long range with decaying hits
  instead of burst-reset → reposition → re-engage. **(3)/(4).**
- **Causes:** spray-default habit ("spray control is the *last* option, not the default");
  single-distance practice; no reset discipline.
- **Problematic:** medium/long duel, 15+ rounds, no kill, still exposed.
- **Exceptions:** close committed fight; multi-enemy transfer; suppression with trader ready.
- **Check:** burst length + distance + hit cadence (`inaccuracy` trajectory + ammo remaining);
  cover availability; AK >7-round rule is heuristic, never a cutoff.
- **Demo:** available (shots/damage/velocity/positions). Unavailable (intended mode vs panic).
- **FP: MEDIUM. Mixed (mechanical cadence + tactical choice).**

### FUND-004 — Wrong fire mode for range (spray-at-long, tap-at-close-cluster)
- **Symptom:** full-spray long / slow-tap into stacked close enemies. **(3)/(4).**
- **Causes:** one-mode habit; range misjudgment; panic.
- **Problematic:** long-range full-spray with no hits; close multi-enemy tapped one-by-one.
- **Exceptions:** forced (no ammo to reposition, clock); suppression intent.
- **Check:** distance + mode + outcome; weapon falloff row for build (SMG/pistol close-legit).
- **Demo:** available. Unavailable (intent). **FP: MEDIUM. Mixed.**

### FUND-005 — Reloading in the open / discarding a partial mag unsafely
- **Symptom:** reload started with cover in reach and contact imminent; or partial reload
  under March-2026 magazine-discard (remainder destroyed: AWP 15-round economy,
  M4A1-S 80-round pool — a 12-round dump = 15%). **(1)** for open-reload;
  (4) for discard economics.
- **Causes:** auto-reload habit; ammo anxiety; no cover scan.
- **Problematic:** stationary open reload → killed; repeated discard shrinking round supply.
- **Exceptions:** safe reload (cover/teammate holding); reload-at-zero under discard rule.
- **Check:** cover distance (geometry); teammate positions; ammo before/after; round supply math.
- **Demo:** available (positions, reload state, ammo). **FP: LOW (open reload); MEDIUM (discard
  judgment). Mechanical + tactical.**

### FUND-006 — Crosshair at floor/ceiling across angles (placement habit)
- **Symptom:** view pitch far from head-level repeatedly at exposure. **(3)** — approximate
  by construction (true screen point unavailable).
- **Causes:** no pre-aim routine; static height across elevation changes; lazy holds.
- **Problematic:** repeated large vertical corrections before first shot; consistent across maps.
- **Exceptions:** elevation-legit height (ramp up / top-mid down); AWP center-mass default;
  anti-crouch-peek adjustment.
- **Check:** pitch at exposure + map elevation at angle; within-player distribution, never
  per-event verdict; TTD/placement medians as type-2 backing.
- **Demo:** available (view angles, approximate). Unavailable (pixel truth; causality of miss).
- **FP: HIGH (map elevation changes legit head height). Mechanical.**

### FUND-007 — Wide wall gap / slow slice (pre-aim distance error)
- **Symptom:** large gap to wall edge or over-wide clearance forcing long flicks. **(3).**
- **Causes:** fear-clearing far from corner; no closest-angle habit.
- **Problematic:** repeated long-drag first shots; beaten by close holders.
- **Exceptions:** wider pre-aim vs off-angle-heavy opponents (deliberate).
- **Check:** aim offset vs angle edge (approximate) + first-shot latency; opponent off-angle rate.
- **Demo:** partial (angles approximate). **FP: MEDIUM. Mechanical.**

### FUND-008 — Crouch as default reaction (predictable / vs multiples / while peeking)
- **Symptom:** crouch-first on every contact, including open/multiples/peeks. **(3).**
- **Causes:** crouch-spray habit from DM; panic.
- **Problematic:** pre-aimed-low deaths; slowed escape; committed vs second angle.
- **Exceptions:** sparing mixup; committed close spray behind cover; crouch-peek scoped slow peek.
- **Check:** crouch flag at exposure + enemy count + cover; repetition rate.
- **Demo:** available (crouch flag). Unavailable (deliberate vs panic). **FP: HIGH. Mechanical.**

### FUND-009 — Firing unsettled / double-zoom overuse (AWP)
- **Symptom:** scoped shot long-range missing with short scope-to-fire interval. **(3)** —
  **settle-at-fire is inference-only; zoom level unavailable. Never file as (1).**
- **Causes:** quick-scope habit at wrong range; double-zoom overuse; moving scoped fire.
- **Problematic:** repeated long unsettled shots; audible scope tight to corner.
- **Exceptions:** close/mid desperation quick-scope (randomness accepted); noscope past ~2 m
  is worse (pistol better).
- **Check:** positions/shots/damage + scoped *state* (available) — never settle state.
- **Demo:** available (state). Unavailable (zoom level, settle, spread). **FP: HIGH.
  Mechanical + tactical.**

### FUND-010 — Jumping / ladder / airborne shots (non-SSG)
- **Symptom:** fire while airborne with high-jump-penalty weapon (rifles ~0.10–0.18 jump term).
  **(1)** for state; (4) for judgment (Ferrari info-jump with no shot is correct).
- **Causes:** jump-peek with trigger; falling off geometry firing.
- **Problematic:** jump-shot rifle duel at range.
- **Exceptions:** SSG jump-peak accuracy (engine trait); point-blank panic; info jump (no shot).
- **Check:** z-velocity/airborne at fire + weapon jump term; shot vs no-shot jump.
- **Demo:** available. **FP: LOW (state); HIGH (calling info-jumps errors). Mechanical.**

### FUND-011 — Team-flash / self-flash without setup
- **Symptom:** own flash blinds self/teammates (full strength regardless of FF) with no
  follow-up. **(1).**
- **Causes:** bad pop geometry; no spacing/callout; throwing while swinger.
- **Problematic:** repeated teammate blinds; blind-then-no-swing.
- **Exceptions:** intentional sacrificial info pop; defensive retake pop by surviving site player.
- **Check:** blind attacker/victim + timing vs swing/kill attempt (~1 s); spacing.
- **Demo:** available (blind events). Unavailable (voice callouts). **FP: LOW (team-flash);
  MEDIUM (wasted-flash — late swing can make good flash look wasted). Mechanical.**

### FUND-012 — Utility throw mechanics failure (blocked bounce, fizzle, self-damage)
- **Symptom:** nade blocked by geometry; molotov fizzles (>2 s airborne, non-walkable surface);
  HE self/team chip. **(1).**
- **Causes:** wrong lineup/angle; no surface check; cooking mistiming.
- **Problematic:** repeated same-spot failures; round-costing self-kill.
- **Exceptions:** intentional bank/crevice plays (need lineup context).
- **Check:** trajectory + detonation xyz vs geometry; surface angle; lineup DB if available.
- **Demo:** available (trajectory/detonation/damage). **FP: LOW-MEDIUM. Mechanical.**

## Peeking and angles (FUND-013–020)

### FUND-013 — Blind wide swing into unknown / long / AWP angle
- **Symptom:** full commit swing with no prior info into uncleared long angle. **(4)** (+ (1)
  if moving-fire).
- **Causes:** impatience; no info discipline; "wide best" misapplied (correct only after bait/info).
- **Problematic:** repeated dry wides into same held angle; vs known AWPer.
- **Exceptions:** known position + trade partner / reload window; clock forces; follow-up after
  unanswered jiggle.
- **Check:** prior info (intent — unavailable, state assumption); velocity-at-fire; range;
  trade proximity; AWP presence (killfeed/damage, partial).
- **Demo:** positions/paths/velocity available. Unavailable (whether position truly known;
  why no trader). **FP: HIGH (punishing correct aggression as "over-peek"). Mixed.**

### FUND-014 — Multi-sightline exposure without trade/utility
- **Symptom:** path exposing 2+ uncleared sightlines simultaneously. **(4).**
- **Causes:** no slice-the-pie; no smoke/flash to eliminate angles; solo clear attempt.
- **Problematic:** entries/retakes dying to second angle regardless of aim.
- **Exceptions:** utility-covered multi-exposure; traded entry (teammate covers 2nd);
  clock forces gamble.
- **Check:** sightline count (needs map geometry) + teammate positions + active utility +
  whether player knew second angle existed (unavailable).
- **Demo:** partial (geometry-dependent). Unavailable (called coverage). **FP: HIGH without
  utility/teammate context. Tactical.** ("Number one peeking mistake at every rank" — but the
  most context-sensitive.)

### FUND-015 — Instant same-angle repeek into pre-aim
- **Symptom:** committing re-swing same spot + same timing after being spotted/missing.
  **(3)/(4).** Distinct from free info jiggles (exempt).
- **Causes:** emotional speed; "fix it" impulse; no timing variation.
- **Problematic:** repeek into known pre-aim with no window (no AWP bolt / flash / trade).
- **Exceptions:** genuine window (AWP bolt ~1.45 s, flash, trade ready); enemy-reset read;
  1–2 s delayed anti-prefire repeek; reposition to secondary angle (correct alternative).
- **Check:** inter-peek interval + width/angle/height deltas; spotted? (prior fire/damage);
  utility/trade context; peek-1→peek-2 info delta (rarely resolvable — state it).
- **Demo:** intervals/widths available. Unavailable (whether repeeker believed window open;
  enemy crosshair state never in demos). **FP: MEDIUM. Tactical.**

### FUND-016 — Lingering jiggle / shooting mid-jiggle / identical rhythm
- **Symptom:** jiggle held too long (free frag); shot attempted mid-jiggle (becomes bad wide);
  identical cadence repeated (prefired next cycle). **(3)/(4).**
- **Causes:** no info-vs-commit boundary; rhythm habit.
- **Problematic:** 3rd+ identical jiggle prefired; mid-jiggle shot at range.
- **Exceptions:** rhythm-break A/D variant (deliberate); converting to wide after 1–2
  unanswered jiggles (correct escalation).
- **Check:** exposure duration (within-player compare, no universal cutoff); mid-jiggle shot
  attempt; repeat-timing similarity.
- **Demo:** available (displacement, shots, enemy response). Unavailable (info vs failed-commit
  intent). **FP: MEDIUM. Mixed.**

### FUND-017 — Shoulder-bait vs rifles / overexposed bait
- **Symptom:** sliver-bait attempted vs rifle holder (useless) or held too long showing
  head ("if you see your enemy, you're doing it wrong"). **(3)/(4).**
- **Causes:** wrong threat read (AWP assumed, rifle held); greed for bait.
- **Problematic:** repeated failed baits vs same holder; AWPers adapting (hold the bait).
- **Exceptions:** confirmed scoped long-angle AWPer; afterplant info on incoming CTs.
- **Check:** AWP presence (partial); exposure minimality; enemy weapon class.
- **Demo:** available (exposure + enemy shot + damage). Unavailable (baited-vs-holding truth).
- **FP: MEDIUM-HIGH (identical to failed jiggle vs rifles). Tactical.**

### FUND-018 — Default shift-clearing open angles / wrong corner distance
- **Symptom:** slow-walk clearing open angles by default; holding close with rifle into long
  perspective (or far with shotgun). **(4).**
- **Causes:** sound-fear overgeneralized; no corner-distance concept.
- **Problematic:** late arrivals from slow clears; repeated perspective-disadvantage duels.
- **Exceptions:** flank/close/fake/off-angle/ladder shift (correct); late-round low-noise
  shift (reviewer judgment, unsourced but reasonable); shotgun close holds.
- **Check:** speed-at-exposure; corner distance; post-kill repositioning; whether quiet was
  needed (enemy unheard positions — approximate).
- **Demo:** available (speeds/positions). Unavailable (intent; actual enemy hearing).
- **FP: MEDIUM. Mixed.**

### FUND-019 — Dry-peeking a clearable-with-utility angle
- **Symptom:** dry swing where flash/molly/smoke was available and standard. **(4).**
- **Causes:** utility passivity; no combo habit; solo play without support.
- **Problematic:** repeated dry entries with full utility belt; dry into molly-able holds.
- **Exceptions:** info jiggles; eco (no nades); trader present; saving utility for execute
  (eco-dependent); peeking before pop / after expiry mistiming is separate (FUND-025).
- **Check:** inventory/utility state + flash→peek interval + blinded state + molly timing.
- **Demo:** available (inventory, detonation→peek timing). Unavailable (deliberate vs lucky timing).
- **FP: MEDIUM. Tactical.**

### FUND-020 — Staying on known position after kill/spot (no reposition)
- **Symptom:** same-pixel hold after loud kill with trade incoming; zero round-to-round
  variation. **(4)** (mechanical when pure re-peek timing → FUND-015).
- **Causes:** kill-admiration; no off-angle book; underestimating trade speed.
- **Problematic:** traded within seconds repeatedly; predictable setups exploited across rounds.
- **Exceptions:** crossfire where *teammate* moves instead; bomb/clock pins spot; no enemy
  trade path; off-angle still undiscovered (decays once discovered).
- **Check:** kill→next-fight position delta; enemy trade capacity; constraints; multi-round
  repetition (needs series, not one demo).
- **Demo:** YES. **FP: MEDIUM. Tactical.**

## Fight decisions (FUND-021–030)

### FUND-021 — Revenge swing turning 4v5 into 3v5 (emotional speed)
- **Symptom:** instant isolated re-fight after teammate death, no stabilize window. **(4),
  never (1).**
- **Causes:** "dry swings alone trying to fix it"; "we got one, let's get another" greed;
  no shared next-step call.
- **Problematic:** isolated duel when numbers + clock already favor your side.
- **Exceptions:** killer exposed + two guns + utility (fight-still-live checklist);
  planned-cost entry; clock/bomb forces contact.
- **Check:** alive delta; spacing to nearest teammate; ~5 s stabilize respected; clock/utility.
- **Demo:** YES (deaths/positions/timing). Unavailable (intent/comms). **FP: HIGH from outcome
  alone. Tactical.**

### FUND-022 — Low-HP first contact a healthy teammate could take
- **Symptom:** damaged player takes first duel while healthy alternative available; dies with
  delay utility unused. **(4). No HP cutoff exists — any fixed threshold is (5).**
- **Causes:** role confusion; no anchor discipline (anchor = buy rotation time, kills secondary);
  revenge over delay.
- **Problematic:** low-HP first-contact with healthy trader in position; delay utility held
  at death.
- **Exceptions:** sole contest body (bomb/clock forces); pre-traded entry design; gun-save priority.
- **Check:** HP at contact (snapshots/`player_hurt`); healthier alternative?; utility held?;
  clock forcing?
- **Demo:** YES for HP/positions. Unavailable (intent). **FP: HIGH. Tactical.**

### FUND-023 — Taking combined multi-enemy fight instead of isolating
- **Symptom:** solo wide into uncleared angles vs 2+; no utility to isolate a side. **(3)/(4).**
- **Causes:** no "three scheduled duels, one sees you at a time" discipline; clear→reposition→clear
  skipped.
- **Problematic:** multi-sightline deaths in clutches/entries.
- **Exceptions:** clock forces combined fight; utility isolates one side; contact-draw with trader
  on second angle.
- **Check:** uncleared-angle count (needs geometry); utility active?; solo vs crossfire?; clock?
- **Demo:** PARTIAL (visibility compute needed). **FP: MEDIUM. Mixed.**

### FUND-024 — Throwing numbers advantage (smoke-chase, held-info swing, far-solo, bomb-forget)
- **Symptom:** with 5v4/4v3, takes isolated/low-% duel instead of collapsing to 1–2
  coordinated fights. **(4).**
- **Causes:** greed ("we got one…"); chasing smoke; swinging for already-held info;
  forgetting bomb state.
- **Problematic:** advantage → even/behind through solo fights; man-advantage giveaways
  (heavily punished by Round Swing — Official-analyst backing).
- **Exceptions:** known eco/positions → fast close-out; hunting denies plant/post-plant;
  bomb site must be held.
- **Check:** alive delta; grouping; clock; bomb state; info already held?
- **Demo:** YES. **FP: MEDIUM** (fluid-team looseness is style — compare within team).
  **Tactical.**

### FUND-025 — Desperation swing / weak-read over-rotate in disadvantage
- **Symptom:** solo revenge swing in 4v5; rotation on single cue; panic utility dump;
  ignoring save viability. **(4).**
- **Causes:** no stabilize (location/numbers, stop 2nd death, name action); chaos without
  coordination.
- **Problematic:** 4v5→3v5 in seconds; stack rotated into empty map; saveable rifles lost.
- **Exceptions:** killer exposed + two-gun punish; fast grouped re-hit vs enemy overreaction;
  manufacture chaos correctly (pace change, re-hit cleared, utility-isolate, keep lurker).
- **Check:** stabilize window respected?; solo vs ≥2-gun trade?; rotation backed by confirmed
  info?; save considered (economy)?
- **Demo:** YES (positions, timing, utility, economy). **FP: MEDIUM. Tactical.**

### FUND-026 — Stationary open reload / hold with no exit plan (cover)
- **Symptom:** reload or hold in the open with usable cover in reach; no retreat path. **(1)**
  for the reload; (4) for the hold.
- **Causes:** no "where would I hide?" check; position without exit plan.
- **Problematic:** killed mid-reload with cover 2 steps away; repeated no-exit holds.
- **Exceptions:** transit between covers; jiggle-info exposure; coverless post-plant geometry;
  bomb-carrier pathing.
- **Check:** cover distance at fight start (geometry-dependent); rotating vs stationary?
- **Demo:** PARTIAL (cover needs geometry). **FP: MEDIUM. Mixed.**

### FUND-027 — Purposeless exposure (swing for held/already-known info)
- **Symptom:** dry swing for "info" already held, solo, no trade/space objective. **(4)** —
  purpose is intent, never (1).
- **Causes:** no peek-purpose triage (clearing? trade? angles? cheaper info available?);
  entry without utility despite availability ("never dry-entry a stacked site if utility
  available").
- **Problematic:** dry-swing known-held angle solo when jiggle/sound/utility suffices.
- **Exceptions:** clock/bomb forces info-fight; deliberate bait with ready trader.
- **Check:** info already held?; trade available?; angle count?; cheaper info method
  (utility in hand, jiggle-able geometry)?
- **Demo:** PARTIAL (geometry yes; purpose unavailable). **FP: HIGH. Mixed.**

### FUND-028 — Spending survivable info-life on low-% duel (info vs survival vs combat)
- **Symptom:** closest player duels instead of surviving/delaying with help seconds out;
  info dies uncalled. **(4).**
- **Causes:** no trichotomy (jiggle = info uncommitted; survival/delay = anchor doctrine;
  commit = supported swing); entry judged by K/D not round-opened.
- **Problematic:** survivable info-life spent low-% with rotations near; site falls with info.
- **Exceptions:** info complete (combat correct branch); survival cedes loss condition;
  designated bait with trader ready.
- **Check:** round win-condition at moment; time-to-reinforcement; info redundancy;
  comms unheard — flag assumption.
- **Demo:** PARTIAL (comms absent). **FP: HIGH. Tactical.**

### FUND-029 — Entry contact with second too far / same-angle stack / staggered retake
(timing relative to teammates)
- **Symptom:** first contact untradeable (gap too big); teammates stacked same angle
  (one-nade risk); retakes trickling 1-by-1 ("five staggered players lose to two set
  defenders"). **(4)** with (1) spacing facts.
- **Causes:** no 1–2 s trail discipline; no crossfire setup (separate angles close+deep);
  no grouped multi-angle retake; early repeek before bomb pressure.
- **Problematic:** repeated untraded first deaths with teammate in range but late;
  entries dying out of team view; shared-nade stacks.
- **Exceptions:** lurker timing (threat-connection, not pack proximity); designed splits;
  post-plant stagger (jiggle → swing on sound/tap → hidden third) is correct shape.
- **Check:** inter-teammate gap at first contact; stacking vs one-grenade rule; role inference
  (pack vs lurk — moderate FP); clock (40 s detonation; 5 s kit / 10 s naked defuse —
  start ~6 s/~11 s or play kill/save, never doomed defuse) vs setup time.
- **Demo:** YES (positions, timing, shots). Role inferred. **FP: MEDIUM. Mixed.**

### FUND-030 — Failed trade chain (untradeable cluster / no attempt in position)
- **Symptom:** teammate dies; player had LOS + range + readiness but no shot in window; or
  two deaths ≤5 s same killer/area with no return. **(2)/(4)** — opportunity → attempt →
  success split mandatory; success-rate without opportunity denominator is (5).
- **Causes:** bad spacing; late readiness; no trade plan; entry out of view.
- **Problematic:** repeated untraded deaths with punish-range teammate late/unready.
- **Exceptions:** death bought convertible *space*; lurker deaths (no opportunity by design);
  force/solo plans; AWPer/closer low involvement = role (ZywOo/sh1ro); CT anchor alone =
  design (judge delay/info, not trades); successful entries show zero trade record
  (kill two yourself → punished by method — style, not effectiveness).
- **Check:** at death: nearest-teammate distance + LOS to killer (geometry); reaction in
  labeled window (5.25 s awpy recovery vs 1 s readiness — a 3 s revenge = failed save but
  successful trade); round-plan role?
- **Demo:** YES (positions, shots, deaths, timestamps). Intent/role partial. **FP: MEDIUM
  (HIGH without opportunity denominator or role). Mixed.**

## Utility (FUND-031–037)

### FUND-031 — Smoke with no follow-up plan (space never taken)
- **Symptom:** smoke buys window; nobody converts within seconds. **Mixed (timing + tactical).**
- **Causes:** smoke-as-safety confusion (purpose is time, not safety); no execute call;
  standing inside own smoke (dies to spray/HE).
- **Problematic:** crossing/execute smokes unused; expired before action.
- **Exceptions:** force-rotation / buy-time-on-clock smokes; extinguish-bomb-fire
  (best $300-for-$500 trade); fake smokes.
- **Check:** throw xyz + positions/kills in ~5–10 s; bomb-fire active?; smokes landed
  within 2–3 s of each other (executes)?
- **Demo:** available (throws, positions). Unavailable (intent). **FP: MEDIUM. Mixed.**

### FUND-032 — Retake/hold utility dumped early, none left post-plant
- **Symptom:** full belt thrown mid-round; dry retake (no smoke-on-bomb/choke, molly, flash).
  **Tactical.**
- **Causes:** mid-round impatience; no retake doctrine (AWP holds line, SMGs/pistols first).
- **Problematic:** post-plant with zero utility + no kit.
- **Exceptions:** preventing the plant at all is legitimate; low-buy exit rounds.
  **Counterexample (required): holding utility for retake is legitimate — never flag
  "utility held at round end" alone.**
- **Check:** plant timestamp vs inventory at plant; kit ownership (decides winnable retakes).
- **Demo:** available (grenades, plant/defuse, economy/kit). Unavailable (who was assigned
  what — no comms). **FP: HIGH from end-inventory alone. Tactical.**

### FUND-033 — Flash divorced from swing (early/late, no support)
- **Symptom:** flash pops with no swing in ~1 s, or swing long after blind expires. **(3)/(4).**
- **Causes:** solo-queue pop with nobody ready; swinger ≠ thrower violation; lobbed instead
  of popped; unseen/unheard discipline ignored (loud/visible bounce; audible prep).
- **Problematic:** repeated blind-nobody / blind-expired-before-swing.
- **Exceptions:** solo self-flash with no teammate; defensive retake pop by survivor (endorsed).
- **Check:** enemy blinds within ~1 s of swing/kill attempt vs blinds with no follow-up;
  teammate blinds (spacing/callout failure).
- **Demo:** available (blind attacker/victim + timing, kills). Unavailable (voice).
  **FP: MEDIUM (late swing makes good flash look wasted). Mechanical/tactical.**

### FUND-034 — Molotov as chip-damage tool instead of denial
- **Symptom:** fire tossed for ~30 chip on open ground instead of flushing/blocking/denying.
  **Tactical.**
- **Causes:** damage-score thinking; no choke/flush concept.
- **Problematic:** open-ground fires enemies walk through cheaply.
- **Exceptions:** post-plant on bomb (forces smoke response or HP tax); anti-eco choke denial
  (highest-value anti-eco tool); cutting escape into gunfire.
- **Check:** fire area vs common-hold geometry + reposition/damage; smoke-extinguish response.
  **Never demand symmetric value from CT incendiaries** (shorter/smaller post-May-2024).
- **Demo:** available (grenade + damage ticks). Unavailable (positional intent).
  **FP: LOW-MEDIUM. Tactical.**

### FUND-035 — HE for chip instead of smoke-window / support play
- **Symptom:** HE lobbed for ~30 chip while smoke-window or support-HE angle available. **Tactical.**
- **Causes:** no smoke-window concept; solo damage habit.
- **Problematic:** HE into smoke that support-HE + teammate angle would convert (kill pays $300).
- **Exceptions:** finishing known-wounded stack (double-HE kills full HP); breaking vents/windows;
  anti-eco stack damage.
- **Check:** detonation xyz vs active smoke + teammate angle within ~2 s.
- **Demo:** partial (damage exists; smoke-window needs smoke state). **FP: MEDIUM. Tactical.**

### FUND-036 — Full rifle buy with zero utility (when affordable)
- **Symptom:** rifle + armor, no grenades, despite spare cash. **Tactical (execution issue).**
- **Causes:** frag-first shopping; no buy order (flash > smoke > 2nd flash > molotov > HE).
- **Problematic:** 5 rifles / 0 flashes; level 4–7 signature error (~$1,000 of round-winning
  equipment left in shop).
- **Exceptions:** explicit save/force with no spare cash; AWP-centric buys (AWPer runs light,
  holds line with minimal utility).
- **Check:** economy snapshot at freeze end vs purchases — **affordability first.**
- **Demo:** available (economy snapshots). **FP: LOW when broke, HIGH when money existed.
  Tactical.**

### FUND-037 — Decoy without fake plan (intent-only — highest FP in class)
- **Symptom:** $50 decoy thrown with no simultaneous opposite-side action. **Tactical.**
- **Causes:** flash-substitute confusion (decoy fakes best-weapon sound + radar, never a flash);
  leftover-cash toss.
- **Problematic:** effectively none observable — only set-fake context judges it.
- **Exceptions:** sacrificial info pop; coordinated fakes.
- **Check:** decoy throw vs opposite-side action timing.
- **Demo:** available (decoy events). Unavailable (intent — decisive). **FP: HIGH. Tactical.**

## Match fundamentals (FUND-038–045)

### FUND-038 — Force/eco/save indiscipline
- **Symptom:** buy class wrong for economy state (half-buy "often a mistake"; impulse eco
  pistols; force into broken enemy). **(4).**
- **Causes:** no framework (full ~$4,800 / eco ~$400 bank ~$4,000 / force $2,500–3,500 kits or
  deep streak near $3,400 cap or last round of half); $2,000 rule ignored (never buy below
  $2,000 if rifle+armor wanted next round).
- **Problematic:** force that breaks next two rounds; eco pistols donating rifles.
- **Exceptions:** half-point forces; punishing broken enemy with numbers; CT exit-value forces
  (higher post-July-2025); half-buys+forces group into a ~$17k band at ~49.5% — report band
  rates as band rates, never false-precision "force win rate."
- **Check:** per-player economy + loss-streak + next-round projection + **enemy-economy read**
  (a "bad" force can be correct vs broken enemy); MR12 12/24 boundaries for half-point logic;
  OT resets mode-parameterized.
- **Demo:** available (economy). **FP: HIGH without enemy context. Tactical.**

### FUND-039 — Anti-eco feeding (clump, stack-donate, assume-passive)
- **Symptom:** vs enemy eco: clumped positions (one spray/HE), solo long duels, no pre-utility
  into rush, donated rifles picked up next round. **Tactical, directly observable.**
- **Causes:** "eco = passive" assumption vs 5-man rushes; no spread/layered-depth/trade-now/
  weapon-denial (drop > donate) doctrine.
- **Problematic:** lost anti-eco → eco spiral; rifle-donation chains.
- **Exceptions:** none structural — but isolated 1v1 Deagle loss is variance, not pattern;
  require clustering.
- **Check:** eco-round tag + death spacing/clustering + pickup→enemy-buy chains; medium-long
  range held?; pre-thrown utility?
- **Demo:** available (kills, positions, pickups, economy). **FP: LOW at pattern level, HIGH
  single-round. Tactical.**

### FUND-040 — Refusing to save (dying with savable value in lost rounds)
- **Symptom:** 2v4/1v5 + enemy armed → fights to death with rifle/AWP instead of save spot.
  **(4).**
- **Causes:** no winnability counterfactual; kill-hunting; no-save-spot knowledge.
- **Problematic:** no-save picks compounding next round; AWP $4,750 lost unnecessarily.
- **Exceptions:** unwinnable clock/kit anyway; last round; called exit-frag play (higher value
  post-July-2025 shared income); low-buy vs rifles should skip retake entirely.
  **Eco nades can be fine** — cheap deny/chip preserving rifle money is sanctioned, not waste.
- **Check:** alive count + carried value + kit/clock at decision; save-vs-die outcome chain.
- **Demo:** available. **FP: MEDIUM (needs winnability counterfactual). Tactical.**

### FUND-041 — Clock / bomb-clock errors (unplanted death, late kit-less stick)
- **Symptom:** dying unplanted with time to plant; defuse stick started too late for kit state;
  doomed defuse attempted. **(1)** — math, not judgment.
- **Causes:** no clock arithmetic (1:55 round; 40 s bomb; 10 s / 5 s-kit defuse, zero saved
  progress → start ~6 s naked / ~11 s kit or play kill/save).
- **Problematic:** any unplanted-death with plant window; kit-less stick started at 8 s.
- **Exceptions:** exits-over-stick as the called play.
- **Check:** timestamps + kit + alive counts. 18 s smoke fits 10 s kit defuse + 8 s setup —
  smoke age at stick + kit state is a direct reviewer check.
- **Demo:** available. **FP: LOW (math); HIGH (stick-vs-exit intent). Mechanical.**

### FUND-042 — Plant / defuse decision errors (exposed plant, skipped safe plant, fire-stick)
- **Symptom:** uncovered plant with cover available; safe plant skipped then round lost to
  clock; sticking through extinguishable fire. **Mixed.**
- **Causes:** no post-plant cover concept; plant-award undervaluing (+$300 planter + $600
  each T on plant-loss — plant pays even in defeat); smoke-kills-fire interaction unknown.
- **Problematic:** open plant with crossfire cover free; fire-stick without smoke response.
- **Exceptions:** open plants for crossfires (map-dependent); no-kit save (correct non-attempt).
- **Check:** plant coverage geometry; fire + smoke response; kit state; fake/ninja dynamics.
- **Demo:** available. **FP: MEDIUM. Mixed.**

### FUND-043 — AWP economy / role errors (bad buy, no-reposition loop, bolt-window feed)
- **Symptom:** AWP bought when team broke; same-angle re-peek loop after miss ("over-peeking,"
  mistakes #1/#3); staying in fight during 1.45 s bolt window; 2nd/3rd AWP immobility.
  **Tactical (+ mechanical execution).**
- **Causes:** no $4,750-respect (save rule); no shot-and-swap habit; utility-less AWPing.
- **Problematic:** AWP lost same angle twice; no-utility AWP rounds; reloading with rounds
  left (discards) or unsafe ~4 s.
- **Exceptions:** rifle instead of AWP when no cover/trade/armor/utility (correct downgrade);
  pistol covers bolt window (P250/Five-SeveN; Deagle if rich).
- **Check:** post-shot displacement + angle change (shippable); cover/escape geometry;
  economy at buy; leg-shot (`hitgroup`) / recorded-noscope kill fields where present.
- **Demo:** available (reposition/buy/save context; leg/noscope recorded fields).
  **FP: LOW for reposition/leg/noscope-kill; HIGH for "fired unsettled." Tactical.**

### FUND-044 — Time-management drift (slow after picks/plant; fast on save)
- **Symptom:** after favourable state change, slow objective action while win-prob decays;
  or rushed contact on save rounds. **(2)/(4).**
- **Causes:** no tempo concept (dP(win)/dt); defaulting at won-round pace.
- **Problematic:** sustained high-decay inaction segments; pick → no collapse for 20 s.
- **Exceptions:** deliberate wait (utility timing, lurker connection, anti-rotate patience).
- **Check:** time-to-next-objective vs cohort; action-onset latency; value-decay segments.
- **Demo:** available (ticks, timer, events). Unavailable (deliberate vs passive intent).
  **FP: MEDIUM. Tactical.**

### FUND-045 — Info-hygiene failures [WEAK — do not build detectors]
- **Symptom:** decision inconsistent with plausibly-available info (audible footsteps/gunfire
  in proxy radius, damage-direction indicator, radar spot) — e.g. re-clear skipped, rotate
  into known stack. **(4) at best; without Expert sourcing + proxies, (5).**
- **Causes:** unknown — perception unobservable (no gaze/attention; tick quantisation;
  TrueView delays).
- **Problematic:** only as aggregated "available-info vs decision" timelines with caveats.
- **Exceptions:** bait/assumed-trade plays; info correctly judged stale.
- **Check:** "available info" set (footstep/shot events, `direction_last_injury`, `spotted`)
  → flag decisions inconsistent with it; needs decision-normality model (cohort).
- **Demo:** partial (events/positions). Unavailable (perception — decisive).
  **FP: VERY HIGH. Tactical. Category-(5) unsupported until newly sourced — no detector.**
  (Same verdict for tracking/target-switching: do not ship either.)

## Non-flags (do not emit as mistakes)

- Heroic-fluid systems → compare within team, not global averages.
- AWPer/closer low trade involvement = role, not baiting.
- CT anchor alone = design; judge delay/info/clutch, not trades.
- Supportive low-weapon players gaining under impact metrics = role, not failure.
- Aggression volume ≠ value (impact-metric winners/losers prove it).
- Held-for-retake utility, eco nades, exits-over-stick = sanctioned counterexamples,
  never flags alone.
- Single-round anti-eco loss / single Deagle death = variance, never pattern.

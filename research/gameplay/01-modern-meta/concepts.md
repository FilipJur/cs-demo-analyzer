# Tactical Concepts — Modern CS2 Meta (Oct 2024 – Oct 2026)

**How to read.** Each concept has a stable ID and the 9-point schema:
(1) meaning · (2) objective · (3) appropriate · (4) questionable ·
(5) reasonable information · (6) alternatives · (7) demo manifestation ·
(8) not demo-inferable · (9) stable fundamental vs patch/meta-dependent.

**Confidence labels.** `[primary]` = peer-reviewed or named first-person pro/coach
statement. `[analyst]` = named-analyst data piece. `[guide]` = named practitioner
guide (definition-reliable, not efficacy evidence). `[secondary]` = dataset/editorial
with disclosed method. `[inference]` = reasoned synthesis, needs verification.
`[pre-window]` = CS2 but before Oct 2024. `[unverified-transfer]` = CS:GO-era claim
carried over without CS2 validation.

**Global constraint (applies to every concept).** Voice comms are absent from demos
(and team chat encrypted since 2026-09-09). Any claim about what was called, what a
player was told, or why a rotation was ordered is comms-dependent and MUST be
qualified. Judge decisions ex ante, never by round outcome (outcome bias,
Baron & Hershey 1988 — S-G01).

---

## R — Roles and responsibilities

### META-R01 — Entry and second entry

1. **Meaning.** The player(s) taking the round's first duel to crack a site;
   second entry follows to clear remaining angles and trade. `[guide]` Refrag 2025-05-21 (S-R16).
2. **Objective.** Convert the opening duel into a *team* advantage: kill the anchor,
   path into the site, accept being traded. `[guide]` Refrag 2025.
3. **Appropriate.** Committed executes/fast takes; defaults where a first duel wins
   control (Long, Mid); CT-side analog = rotator taking first contact. `[analyst]` HLTV 2024-04-18;
   `[primary]` Paskiv et al. 2026 (entry↔rotator mapping).
4. **Questionable.** Dry entry with no second man in trade distance; fragile/low-buy
   player self-entering; treating "entry" as a permanent job — Refrag notes many
   entries are also star riflers. Liquid's documented 2025 failure: four ex-lurkers,
   "no natural entry fragger". `[analyst]` HLTV 2025-01-09.
5. **Reasonable information.** Team call, opponent-default read, own utility ledger;
   in-duel: personal vision/sound + teammate voice calls.
6. **Alternatives.** Slow-play for info; flashed entry vs dry peek; delegate first
   contact to the spacetaker, enter second as the trader.
7. **Demo manifestation.** Opening block: opening kills/deaths/attempts/success per
   round + traded-death rate. Entry-vs-lurker contrast led by opening deaths
   (+0.89 SD) and attempts (+0.88). `[primary]` Paskiv et al. 2026.
8. **Not inferable.** Whether the entry was called; whether utility cover was denied;
   whether the CT position was already known; whether the follower was placed by
   design or accident.
9. **Stable** opening-duel discriminator; **patch-dependent** entry weapon/economy
   (MP9/FAMAS/SMG churn mid-2025 — jabbi, `[primary]` HLTV 2025-07-23).

### META-R02 — Lurker and extremity control

1. **Meaning.** Player on the quiet part of the map while the plan executes
   elsewhere: late-round piece, cuts/delays rotations, closes post-plants.
   `[guide]` Refrag 2025-05-21; CSStatLab "Lurking" upd. 2026-07-05.
2. **Objective.** Threaten the other site so the main hit lands under-defended; win
   the late round alone. `[guide]` Esports Insider 2025/2026.
3. **Appropriate.** Main execute elsewhere needing a rotation threat; patient
   economy/map states; opponents who over-rotate. `[analyst]` HLTV 2024-04-18
   (lurks prowl low-skilled anchors).
4. **Questionable.** Silent wandering the team doesn't know about ("a lurk only works
   if the team knows about it" — CSStatLab); over-passive lurk that reads as baiting
   ("saving a lot, finding practically no impact" — Refrag); lurking when the team
   needs entry pressure (four-lurker roster failure, `[analyst]` HLTV 2025-01-09).
5. **Reasonable information.** Structurally the *least* shared info: own perspective
   + teammates' calls about the main action. Read quality depends on comms.
6. **Alternatives.** Group for a stronger execute; semi-lurk (return for the hit);
   convert extremity into anchor on CT (63% of T-lurkers anchor on CT `[primary]`).
7. **Demo manifestation.** Time alive/round (+0.63 SD vs entry), trade kills
   (+0.57), clutch points, last-alive %, positional extremity/time-alone from ticks.
   `[primary]` Paskiv et al. 2026.
8. **Not inferable.** Impact without kills (pinning a rotator wins rounds silently);
   "patient" vs "baiting" without plan + comms.
9. **Stable** late-round/alone archetype + cross-side mapping; **patch/meta-dependent**
   extremity strength per map pool (2025–26 pool in flux).

### META-R03 — Space creator (spacetaker)

1. **Meaning.** Function of opening map area: mid/connector/apps takes that force CT
   repositioning. Groups taxonomically with entry (Paskiv et al. 2026 `[primary]`);
   "spacetaking positions turn into lurking positions frequently" (`[analyst]` HLTV 2025-01-09).
2. **Objective.** Buy *options* (safer rotations, split timings, believable fakes),
   distinct from an opening-kill objective.
3. **Appropriate.** Defaults and map-control takes where the win condition is
   positional rather than a fast hit.
4. **Questionable.** Space taken with no plan to convert it ("rounds lost in
   defaults" — Liquid's brittle T sides `[analyst]`); spacetaker also tasked as
   entry-killer when the goals diverge.
5. **Reasonable information.** Own utility, first-contact read, teammates' radar
   positions, team call.
6. **Alternatives.** Pure entry (kill first); pure lurk (wait); soft take with
   utility only. Forced-switch precedent: HEROIC moved tN1R from lurk to
   spacetaker mid-2025 with individual cost (1.19 → 0.93 T rating) — CASE-11.
7. **Demo manifestation.** Opening block + per-tick occupancy (where the player is
   over time) + utility thrown to deny angles. Positions from demo, never from labels.
8. **Not inferable.** Whether the space was *needed* — depends on team plan and
   opponent setup knowledge.
9. **Stable** contested-space function; **patch/meta-dependent** space-vs-frag value
   (2025 economy/CT-molly changes altered buy patterns — jabbi `[primary]`).

### META-R04 — Support and utility specialist

1. **Meaning.** "The utility guy": most execute/default utility, most lineups,
   flashes for partners, often second into engagements to trade. `[guide]` Refrag
   2025. Frequently co-held by IGL/AWPer. `[guide]` Esports Insider.
2. **Objective.** Convert firepower into *unfair* fights: deny angles, blind, trade.
3. **Appropriate.** Every organised round (Esports Insider: full utility expected);
   CT supportive-rotator cover for a star site-holder `[analyst]` HLTV 2024-04-18.
4. **Questionable.** Utility thrown with no partner using the window
   (flash-for-nobody); low-fragging support parked on a high-traffic CT spot
   ("firepower deficit" `[analyst]` HLTV 2024-04-18). Caution: support recovery from
   indicators is weak (recall 0.63) — style is a poor proxy for responsibility
   `[primary]` Paskiv et al. 2026.
5. **Reasonable information.** Teammates' entry timing/positions (needs comms), own
   lineup inventory, opponent tendencies from prep.
6. **Alternatives.** Self-support (entry flashes self — the ranked-typical solution);
   reallocate utility duty to whoever is best positioned.
7. **Demo manifestation.** Support rounds %, assists/round, flashes thrown, flash
   assists, opponent-flash-time, utility damage; *teammate* blinds are computable
   fact (grenades + LOS). `[primary]` indicator set.
8. **Not inferable.** Lineup *intent*; whether a smoke was the agreed one; whether a
   blinded teammate reflects a bad flash or a missed walk-in (plan-dependent).
   Smoke-occlusion verdicts unreliable by construction (repo D-mistakes §8).
9. **Stable** utility-as-team-resource; **patch-dependent** lineups, molotov tuning,
   smoke behavior.

### META-R05 — AWPer

1. **Meaning.** Player on the AWP: owns long sightlines / catches rotates, or
   aggressive power-piece cracking rounds. `[guide]` Refrag 2025.
2. **Objective.** Force respect for a sightline; convert ownership into round wins.
   Team philosophy often built around the AWPer `[guide]`.
3. **Appropriate.** Sightline ownership needed or aggressive pick pays: nicoodoz
   brings the AWP "against an aggressive AWPer… otherwise my riflers get abused";
   rifles T-side by choice otherwise `[primary]` HLTV 2025-06-03.
4. **Questionable.** Dying out of position ("a gift to the enemy team" `[guide]`);
   low-output AWP tolerated like a rifler (below-1.10-target AWPers "worthy of
   criticism even if higher-rated than most of their team" `[analyst]` HLTV 2024);
   forcing the buy when the round doesn't need it.
5. **Reasonable information.** Own sightline, enemy AWP usage, teammates' calls, buy state.
6. **Alternatives.** Hybrid rifle/AWP per round (nicoodoz); rotate AWP to a hot spot
   for a few rounds; rifler takes the long duel, AWP plays late.
7. **Demo manifestation.** Sniper kills/round, sniper-kill share, AWP ownership per
   tick — near-definitional (recall 0.95–0.96) `[primary]`.
8. **Not inferable.** Whether the AWP *should* have been bought (team protocol);
   whether a miss was decision-relevant (expected-value dependent).
9. **Stable** map role; **patch-dependent** buy economy (jabbi's 2025 "five M4s"
   CT pistol-win account `[primary]`); no AWP damage/price change found in window.

### META-R06 — CT anchor

1. **Meaning.** Sole/primary site defender, last to rotate, often facing numbers.
   `[guide]` BLAST 2024-03-15; Refrag 2025-08-11.
2. **Objective.** **Buy time for rotations**, stay alive into retake range: "your
   life, and the time staying alive buys, is often more valuable than a kill"
   `[guide]` Refrag 2025.
3. **Appropriate.** Small/low-traffic site; reserved, clutch-comfortable player
   `[guide]` BLAST 2024. 2024–26 meta increasingly parks *stars* at anchor to shield
   weak spots from lurks `[analyst]` HLTV 2024-04-21.
4. **Questionable.** Heroic multi-kill chasing that converts delay into a lost round
   `[guide]` Refrag; parking the most aggressive player at anchor ("it shouldn't be
   him" — jabbi `[primary]` HLTV 2025-07-23); using anchor as a weak-fragger dump
   ("lurkers will actively prowl for picks on lower-skilled anchors" `[analyst]`).
5. **Reasonable information.** Least map info of all five (karrigan: anchor "has the
   least information" `[analyst]`); own vision/sound + comms. FalleN: "I have ideas…
   but when sh*t starts coming in, it's very different" `[primary]` HLTV 2025-05-13.
6. **Alternatives.** Double the site with the rotator; concede and retake; off-angle
   boost; read-stack.
7. **Demo manifestation.** Anchor time-to-death, pre-contact utility, traded-death
   rate — anchor spots (Nuke Ramp, Mirage/Dust2 B) are the *least-traded* CT deaths
   ("graveyard role") `[analyst]` HLTV 2024-06-26.
8. **Not inferable.** Called plan vs improvisation; jabbi's "be more quiet" comms
   discipline is invisible in the file.
9. **Stable** time-buying priority; **meta-dependent** which spots are anchor/star
   and their difficulty (Ancient A anchor ≈1.12 rating vs Anubis Middle ≈1.03 —
   labels alone don't determine difficulty `[analyst]`).

### META-R07 — CT rotator

1. **Meaning.** Aggressive map-taking defender: reinforces under pressure, re-takes
   mid, covers the IGL's vision needs. Opening attempts +0.88 SD, opening kills
   +0.86 vs anchor `[primary]` Paskiv et al. 2026.
2. **Objective.** Take map control back; arrive at the hot site with utility and a
   trade partner.
3. **Appropriate.** Where the enemy default meets mid; paired with a star site-holder
   needing cover utility `[analyst]` HLTV 2024-04-18.
4. **Questionable.** Parking a low-fragging IGL at a contact-heavy rotator: ≈−2.8%
   CT round-win across rotation spots, −5.9% Outside Nuke `[analyst]` HLTV 2024-04-18.
   Rotator gambling every round becomes readable.
5. **Reasonable information.** Best CT-side map view (why IGLs moved here —
   `[analyst]` HLTV 2024-04-18); mid reads + teammate calls.
6. **Alternatives.** Anchor-swap between maps/rounds; star-rotator on some maps
   (ropz/KSCERATO/Ax1Le `[analyst]`); concede-and-retake.
7. **Demo manifestation.** Mid occupancy over time, opening block, rotation start
   time vs first evidence, utility retained for the destination site.
8. **Not inferable.** Whether a gamble was a team call or solo read; secondary-caller
   identity (device: "all to do with maps, positions, information" `[analyst]`).
9. **Stable** division + signature; **patch-dependent** which positions are
   star/easy on the current pool.

### META-R08 — IGL and information-based repositioning

1. **Meaning.** Focal point calling strats and reading the midgame; plans, demos,
   anti-strats, emotional regulation `[guide]` Refrag 2025. Structurally a **tag
   over a playstyle**, not a playstyle (leadership recall only ~0.50–0.58)
   `[primary]` Paskiv et al. 2026.
2. **Objective.** Convert information into correct round calls; keep emotional
   temperature playable. Load testimony: Perfecto "look at the map every second…
   and simultaneously be focused personally" `[primary]` HLTV 2025-09-11; xertioN
   "calling both sides… very demanding… 11-hour workdays" `[primary]` HLTV 2026-05-10.
3. **Appropriate.** Repositioning that *follows* fresh information: rotation spots
   "to get the correct read… the best view of the map" (karrigan/Aleksib
   `[analyst]`); nominated site-leaders calling setups/rotates; delegated CT calling
   to trusted rotators/AWPer ("best of both worlds" `[analyst]`).
4. **Questionable.** (a) Anchoring IGL starved of info `[analyst]`; (b) overload
   collapsing fragging (Twistzz "losing sleep… looking at his radar" `[analyst]`;
   xertioN's fear of being "a burden" `[primary]`); (c) taking the role unprepared —
   Perfecto declined NAVI's IGL offer as "a bit raw" `[primary]`.
5. **Reasonable information.** Own POV + radar + full voice traffic. **Demo has no voice.**
6. **Alternatives.** Delegate CT calling per site; split map calling (YEKINDAR took
   FURIA T-sides on three maps, handed back — CASE-14); "big strategies" from IGL,
   "small adjustments" from players (YEKINDAR/FalleN split `[primary]` 2026-09-18).
7. **Demo manifestation.** Only as *team* patterns: rotation timing, regroup
   positions, stack/gamble frequency. Individual IGL signature = more utility
   thrown, lower pistol rating, fewer trade kills `[primary]` — a signal limit, not
   a labeler. **Do not infer call quality from individual stats.**
8. **Not inferable.** Which call was made, whether correct, timeout reasoning,
   IGL-call vs player-initiative rotation, correct-call-executed-badly.
9. **Stable** orthogonality of leadership; **era-dependent** IGL positioning
   (supportive-rotator shift 2024–26; G2/huNter-, MOUZ/xertioN, FURIA/FalleN are three
   concurrent solutions).

### META-R09 — Role fluidity (cross-cutting thesis)

1. **Meaning.** Role = situational responsibility set per round/side/map, not a
   person-property. Four evidences: conventional-not-mechanical (Paskiv 2026;
   Dignitas 2015 `[unverified-transfer]`); graded structure ARI ≈ 0.08; side-specific
   expression (63%/77% lurker↔anchor cross-mapping); within-match fluidity (B1ad3:
   "sometimes passive lurker, sometimes active" `[primary]` HLTV 2025-07-30).
2. **Objective.** Let the roster fit personality/plan per map: jabbi took "basically
   all anchor positions" to free aggressive Staehr `[primary]`; B1ad3 "gave makazze
   most of his roles… what he likes, where he's confident" `[primary]` HLTV 2025-07-30.
3. **Appropriate.** Map-to-map swaps (NAVI: iM to Nuke Lobby/Ancient A extremities
   `[analyst]` HLTV 2025-07-31); round-to-round AWP↔rifle (nicoodoz `[primary]`);
   spacetaker↔lurker inversion in-round `[analyst]`.
4. **Questionable.** Treating fluidity as interchangeability: tN1R's forced
   lurk→spacetaker switch cost 0.26 T-rating (CASE-11); Liquid's four-lurker roster
   had "no natural entry" (CASE-15). Fluidity needs deliberate assignment, not absence.
5. **Reasonable information.** Assignment layer lives in prep/voice, not in positions.
6. **Alternatives.** Fixed-role roster (predictable but drilled) vs fluid roster
   (adaptive but coordination-hungry).
7. **Demo manifestation.** Label *actions per (round, side)*, keep sides separate;
   never carry a T-side label to CT. Coarse AWPer/Entry/Lurker/Support/Anchor/Rotator
   recoverable at 77–80%; fine labels are convention (Cohen's κ 0.29 between
   annotators) `[primary]`.
8. **Not inferable.** Assignment, intent, comms role ("be more quiet" cost invisible).
9. **Stable** principle across CS:GO→CS2 (engine revised, role structure not —
   Paskiv 2026); **patch-dependent** role economics/util per season.

---

## T — T-side strategy

### META-T01 — Defaults

1. **Meaning.** Slow spread opening (e.g. Mirage 1-3-1) holding areas, gathering
   info, keeping options open. `[guide]` CSStatLab "Defaulting" 2026-07-13;
   Hotspawn 2026-01-31; SCOPE.GG macro 2026-08-28.
2. **Objective.** Punish early CT aggression, force utility, learn the setup, preserve
   execute utility for late. `[guide]`.
3. **Appropriate.** Unknown opponent, aggressive CTs, suspected stacks, utility
   advantage, feeling out the defence `[guide]` Hotspawn 2026.
4. **Questionable.** A 45-second default accomplishing nothing; solo fights with no
   trade; staying spread past the clock; predictability as "slow poison" (Hotspawn).
5. **Reasonable information.** Own spawns/utility; early: only heard/seen whiffs,
   footsteps, grenade trajectories, presence ("count smokes" — Hotspawn).
6. **Alternatives.** Fast hit/contact vs settled defence; lurk-led pressure; delayed
   default into late execute.
7. **Demo manifestation.** `[inference]` Round-start spread, first-contact geometry,
   utility spent vs retained by timer, bodies per map-third.
8. **Not inferable.** Pre-called vs improvised; the IGL's actual read; deliberate
   quiet vs lost discipline.
9. **Stable** spread→info→options function; **meta-dependent** splits/timings per map/patch.

### META-T02 — Map control and space acquisition

1. **Meaning.** Safe use/denial of map areas: "you control an area when the enemy
   cannot move through it comfortably without clearing, trading, or spending
   utility" `[guide]` CSStatLab "Map Control" 2026.
2. **Objective.** Convert space into options: rotations, split timings, info,
   believable fakes, stronger post-plants.
3. **Appropriate.** Early/default phases and pre-execute; each take tied to what it
   unlocks ("what does this corner let us do now?").
4. **Questionable.** Taking and abandoning space; deep unsupported pushes;
   over-rotating; holding low-value ground past the clock `[guide]`.
5. **Reasonable information.** Enemy reinforcement speed; contest cost (utility);
   committed defender count `[guide]` 4tmr 2025.
6. **Alternatives.** Threaten without occupying; structured contest; concede now,
   re-take later.
7. **Demo manifestation.** `[inference]` Area occupancy/denial over time; lane-win
   utility spend; held vs abandoned control.
8. **Not inferable.** Whether perceived control is real (fog of war); deliberate
   concession as trap ("a fake without map control is just noise" — Hotspawn).
9. **Stable** control = decisions unlocked; **meta-dependent** chokepoint priority
   per map (Anubis waters rotations `[guide]`; Train B-rush weakened post-Popdog —
   `[analyst]` HLTV 2025-01-27).

### META-T03 — Contact plays

1. **Meaning.** Quiet hit: walk up, take space carefully, "explode" on first contact;
   no early grenades `[guide]` CSStatLab "Contact Plays" 2026.
2. **Objective.** Deny the three reactive cues — sound, utility, early info — stealing
   setup time.
3. **Appropriate.** Enemy expects loud utility; defence over-rotating; weak extremity
   player; pace change from executes.
4. **Questionable.** Vs aggressive defenders, spam setups, strong info protocols;
   walking past trade distance; freezing after contact; leaking noise elsewhere.
5. **Reasonable information.** Read on the weakest defender/angle + belief the hit
   is still unidentified.
6. **Alternatives.** Standard execute; default-into-late-execute; lurk-led hit.
7. **Demo manifestation.** `[inference]` No opening utility at the hit; tight spacing;
   first death instantly traded (second/third close enough to punish).
8. **Not inferable.** Intended silence vs lost comms; defence non-reaction by read
   vs caution.
9. **Stable** noise-for-surprise trade; **meta-dependent** map/position punishment
   harshness.

### META-T04 — Executions

1. **Meaning.** Coordinated site take committing utility + bodies at a timing
   `[guide]` Hotspawn 2026; 4tmr 2025.
2. **Objective.** Overwhelm once CT utility is depleted/displaced; manufacture a
   safe plant.
3. **Appropriate.** Utility advantage, spent defenders, man advantage, clock forcing
   commitment.
4. **Questionable.** Into stacked/settled sites; entry stopping to duel ("routing is
   sacred" — Hotspawn); pack over-stacked so one HE/molly multi-kills (4tmr).
5. **Reasonable information.** Defender count/placement from utility/sound/history;
   enemy economy watch.
6. **Alternatives.** Contact, split, fake, lurk-convert.
7. **Demo manifestation.** `[inference]` Utility burst → clustered commit; wide-swing
   entry + instant trades; early choke deaths.
8. **Not inferable.** Entry tasked to trade vs survive; freeze-time vs mid-round call.
9. **Stable** entry-creates-space / second-rifle-converts (bo3 "Second Rifle Problem"
   `[analyst]` 2026-10-09); **meta-dependent** viable executes per patch.

### META-T05 — Conditioning and pressure

1. **Meaning.** Repeating a pattern (utility/pressure/timing) so the defence expects
   it then exploiting or inverting it `[guide]` SCOPE.GG 2026; `[analyst]` HLTV 2024-07-22 `[pre-window]`.
2. **Objective.** Make defenders spend time/utility on a phantom take, or under-defend
   the real one.
3. **Appropriate.** Across a half vs slow adapters; after a credible pattern is
   established (NAVI EWC 2024 payoff — CASE-01).
4. **Questionable.** Never cashing the condition (becomes predictability — "forcing
   one style every round" is "the biggest T-side mistake", Hotspawn); defence
   pre-empting the read.
5. **Reasonable information.** What was shown + when; CT response inferred from
   rotation sound/timing.
6. **Alternatives.** Randomise; deliberately break pattern; *anti-condition* by
   hitting the opponent's preferred timing ("hit the timings he usually likes" —
   sycrone `[primary]` HLTV 2026-10-11).
7. **Demo manifestation.** `[inference]` Repeated utility shapes/timings at one area
   across rounds, then a divergence round; CT utility answers to the phantom.
8. **Not inferable.** Whether CTs actually bit; whether payoff success came from
   conditioning or an unrelated mistake.
9. **Stable** show-then-payoff/invert; **meta-dependent** memory persistence across
   roster/patch churn.

### META-T06 — Splits and rotations

1. **Meaning.** Hitting a site from 2+ directions simultaneously; mid-round attack
   rotation after the default blanks `[guide]` Hotspawn 2026; 4tmr 2025.
2. **Objective.** Multiply defender angles; slow CT rotations; isolate 1vXs.
3. **Appropriate.** Map control offering two approaches; depleted CT utility; known
   soft site.
4. **Questionable.** Unsynchronised prongs feeding one at a time; splitting into a
   stack; "rotating too late because you lack information" (egamersworld 2026 `[guide]`).
5. **Reasonable information.** Isolatable defender; uncontested second-prong route.
6. **Alternatives.** Single-direction execute; fake; contact.
7. **Demo manifestation.** `[inference]` Two T packets converging within seconds; CT
   split vs collapse response.
8. **Not inferable.** Designed synchronisation vs coincidence; info-arrival→reaction
   latency needs comms (egamersworld).
9. **Stable** 2v1/isolation geometry; **meta-dependent** cheap two-way maps (Anubis
   waters `[guide]`).

### META-T07 — Fakes

1. **Meaning.** Showing presence/utility at one site to pull rotations, hitting
   elsewhere `[guide]` Hotspawn 2026; SCOPE.GG 2026.
2. **Objective.** Soften the real target; open mid/lurk lanes.
3. **Appropriate.** With the map control + info to be credible; vs noise-chasing CTs
   (good teams do *not* rotate to noise — Hotspawn).
4. **Questionable.** Faking without map control ("just making noise"); footstep
   leaks revealing the real stack (Hotspawn's Mirage A-B example).
5. **Reasonable information.** Enemy location inference; own real stack concealed.
6. **Alternatives.** Convert the fake (hit the pulled site); conditioning payoff.
7. **Demo manifestation.** Utility on a site with no committing bodies; CT exits then
   a hit on the softened site (MOUZ A→B `[analyst]` HLTV 2024-05-20 `[pre-window]` —
   CASE-02).
8. **Not inferable.** Fake-provoked vs independently-read rotations; comms.
9. **Stable** rotation economy; **meta-dependent** cheap audible-fake sites/maps.

### META-T08 — Mid-round adaptations

1. **Meaning.** Post-default plan changes from gathered info, before/during
   commitment `[guide]` CSStatLab; `[analyst]` HLTV 2024-05-20 `[pre-window]`.
2. **Objective.** Convert a death, utility shape, or audible rotation into a better
   hit or audible.
3. **Appropriate.** Clear info contradicting the call with clock to switch (MOUZ
   A→B with 10s on "two A" — CASE-02).
4. **Questionable.** Over-adapting to single reads; clock-ignoring switches;
   "rotating too late because you lack information".
5. **Reasonable information.** What the team *actually saw/heard* — CASE-02's call
   came from a dead teammate's wider view. Information state is the variable.
6. **Alternatives.** Stick to plan; save; lurk-convert.
7. **Demo manifestation.** `[inference]` Route reversals, low-clock site switches,
   re-purposed utility; the seeding death before the switch.
8. **Not inferable.** Decision quality vs outcome — good calls die (Spirit retakes
   beat xertioN's correct calls before conversion, `[primary]` sycrone 2026-10-11);
   bad calls get bailed by skill. Comms receipt invisible.
9. **Stable** info→decision loop; **meta-dependent** clock/utility adaptivity budget.

### META-T09 — Lurking and cutting rotations (T-side view)

See META-R02 for the role base. Tactical additions:

1. **Meaning.** Separated player on the quiet side; flank, far-side control,
   rotation punishment, post-plant closer `[guide]` CSStatLab 2026; Refrag 2025.
2. **Objective.** Cut/delay the rotation the main hit provokes — "a lurk wins rounds
   by punishing rotations" (cs2cheats 2026 `[guide]`).
3. **Appropriate.** Main hit forcing rotations through a predictable lane; occupying
   the un-attacked site; making a fake believable.
4. **Questionable.** See META-R04-style griefing: unannounced distance that leaves a
   4v5 the team didn't plan for.
5. **Reasonable information.** Rotation sounds/timing, quiet-lane identification,
   CT stretch state.
6. **Alternatives.** Group for execute mass; semi-lurk returning for the hit
   (siuhy-screen model `[analyst]` HLTV 2025-04-05: starts lurk, aggresses mid-round
   3v3s or rejoins — Twistzz/ropz/broky model).
7. **Demo manifestation.** `[inference]` Single T isolated by distance; late kills on
   rotating CTs; lurk path vs main-hit timing.
8. **Not inferable.** Team sanction (comms); read vs luck on flank kills.
9. **Why distance is functional (explicit).** Survival + late availability (caught in
   main-hit utility = no lurk); info without exposure (value peaks as enemy commits
   to react); rotation-cutting from behind; *timing not distance* ("too early =
   alone; right moment = free kill" — CSStatLab); team awareness ("1-3-1 extremity
   lurkers must not take first contact — dying loses map control" — SCOPE.GG).

### META-T10 — Post-plant responsibilities

1. **Meaning.** The 40s after the plant with reversed roles: CTs aggress, Ts defend
   `[guide]` Refrag 2024-07-03 `[pre-window]`; Hotspawn 2026.
2. **Objective.** Run the clock or eliminate CTs; hold crossfires, deny defuse.
3. **Appropriate.** Always post-plant; *style* by numbers: up → passive, early
   utility, force CTs to move; down → seek picks/flanks/fights (Refrag tip 2).
4. **Questionable.** Instant post-plant peeks ("count to three" — Refrag); aggression
   while up (gifts CT win condition: early kills); passivity while down (out-traded);
   bad plant spots nullifying crossfires (Refrag tips 2–4; Stewie2K apartments-spray
   positive example `[pre-window]`).
5. **Reasonable information.** Alive counts, plant spot, remaining utility, CT retake
   routes.
6. **Alternatives.** Crossfire holds (Inferno Dark/Newbox; Anubis E-box/Pizza);
   choke smoke-chains; bomb mollies (expect the smoke-drop response); advanced
   retake flanks.
7. **Demo manifestation.** `[inference]` Post-plant positions vs bomb/retake lanes;
   chained choke utility; peek timing vs bomb timer.
8. **Not inferable.** Whether the plant spot was chosen around planned positions
   (carrier "calls the shots" — comms).
9. **Stable** numbers-rule (up=passive, down=active, no gifted early kills);
   **meta-dependent** crossfires/lineups/util economy. **Patch note:** July-2026 C4
   shockwave rework changed after-plant survival calculus (META-X01).

### META-T11 — Economy-dependent approaches

1. **Meaning.** Round type (full/force/half/eco/anti-eco) shaping T ambition
   `[analyst]` bo3 "Anti-Strats" 2026-09-13; `[guide]` Hotspawn 2026.
2. **Objective.** Align aggression with the buy; exploit CT ecos/forces; force-buys
   are the most habitual hence most anti-strattable (`[analyst]`).
3. **Appropriate.** Fast/contact hits on low buys vs unsettled setups; defaults with
   utility advantage; force patterns exploiting predictable enemy economy rounds.
4. **Questionable.** Hopeful forces breaking the loss-bonus ladder; full rifles with
   zero utility; ignoring economy context when reading patterns ("executes B every
   force buy" predictability `[analyst]`).
5. **Reasonable information.** Own economy exactly; enemy economy from history,
   drops, sighted buys, weapon sounds.
6. **Alternatives.** Save to rebuild; cheap gambit lane; weak-lane stack.
7. **Demo manifestation.** `[inference]` Round-start weapon/utility counts, spawns,
   buy-type vs round-length correlation, force-buy site repetition.
8. **Not inferable.** Exact enemy bank; coordinated vs reactive save.
9. **Stable** buy-quality shapes ambition; **meta-dependent** loss-bonus tuning, MR12
   economy, utility costs (CT $50/kill award Jul 2025 — META-X01).

---

## C — CT-side strategy

### META-C01 — Defensive setups

1. **Meaning.** Pre-round five-man distribution: site holds, crossfire pairs, mid
   controls, rotator slots (3A/2B vs 2A/3B Mirage; Nuke vertical split).
2. **Objective.** Trade early map-control deficit for positional advantage + retake
   readiness; fragging power to frequent contact, delay-utility to late contact.
3. **Appropriate.** Follow the map's contact distribution: stars to high-contact
   (Mirage Connector, Nuke Outside, ex-Overpass Toilets), delay to late-contact
   (Mirage B, Dust2 B) `[analyst]` HLTV 2024-06-26. IGLs increasingly take
   supportive-rotator over low-contact anchor `[analyst]` HLTV 2024-04-18.
4. **Questionable.** Rigid setups vs pattern-readers ("four rotating riflers, no
   specialists" critique `[analyst]`); setups tuned to dead geometry (pool swaps —
   META-X02); early-2025 Anubis all-rifle-spots ≤1.04 rating `[analyst]`.
5. **Reasonable information.** Map, both economies, opponent tendencies (prep), own
   utility. Round-start positions/buys demo-inferable; *reason* is prep/comms.
6. **Alternatives.** Predicted-site stack; info spread; active mid contest.
7. **Demo manifestation.** First-~20s positions, first-contact heatmap, early
   utility, which site loses its anchor first.
8. **Not inferable.** Called stack vs mid-round switch vs read; IGL rationale.
9. **Stable** match-setup-to-contact-probability + specialisation; **pool/meta-dependent**
   which spots are anchor/star (Train return, Overpass 2025–26 churn, Cache 2026 entry).

### META-C02 — Crossfires and spacing geometry

1. **Meaning.** 2+ defenders, one entry, separated angles/distances; attacker can't
   trade cleanly (counterstrikewiki Crossfire `[guide]`-definitional).
2. **Objective.** Turn a lone death into a guaranteed refrag; peeker's-disadvantage
   for the attacker.
3. **Appropriate.** Site holds/retakes with wide-separation geometry (high-low,
   flank+main, opposite corners). Depth (front/back), not stacking, enables trades
   (counterstrikewiki Trade_Fragging).
4. **Questionable.** Angles too tight (one pre-fire + transfer kills both); paired
   players in one line (one spray hits both — upforge 2026-08-31 `[guide]`).
5. **Reasonable information.** Teammate positions (comms), expected entry path,
   utility state. Partner's actual angle is comms-dependent.
6. **Alternatives.** Solo hold behind cover; delaying smoke instead of fighting;
   rotator double-up (Refrag Mirage-B `[guide]` 2025-08-11).
7. **Demo manifestation.** Pair co-location geometry; death-pair trade intervals;
   one-victim multi-kills = failed crossfire signal.
8. **Not inferable.** Mutual angle/timing knowledge; "hold fire until contact" delay
   agreements (comms/timing, invisible).
9. **Stable fundamental**, engine-independent (sub-tick refined hitreg, not the tactic).

### META-C03 — Anchoring decisions (CT-side view)

See META-R06. Decision additions: anchor dilemma is stay-and-delay vs concede-and-retake;
FalleN's gap statement (`[primary]`) and S17's delay doctrine are the primary evidence.
Dying with full utility inflates next-round enemy advantage (conservation link META-C08).

### META-C04 — Rotations, incl. refusing to rotate vs fakes

1. **Meaning.** Continuous CT movement (partial/delayed/fast/slow/refuse) on noise,
   utility, reports, reads (counterstrikewiki Rotation).
2. **Objective.** Reinforce the real threat while keeping the mirror site defensible;
   convert holds to retakes only when warranted.
3. **Appropriate.** Fast on decisive evidence (distinct sounds, full exec utility);
   slow/partial/refused on fake signatures or punishing travel times. Model:
   1–2 toward suspect, majority holds until confirmed.
4. **Questionable.** Over-rotation canonical failure: Mirage A-Long smoke + one
   follower triggers full A rotation, then uncontested 4-man B execute
   (counterstrikewiki). Mirror failure: refusing against a genuine exec. Probability
   judgment, never a rule.
5. **Reasonable information.** Audible/visible cues (demo-recoverable) + teammate
   reports (comms content, not recoverable).
6. **Alternatives.** Hold-and-retake; gamble stack; rotator-only send; utility delay
   instead of bodies.
7. **Demo manifestation.** Rotation start vs first evidence, paths, rotator count,
   mirrored-site utility retention, cross-referenced against enemy fake utility.
8. **Not inferable.** **Refused-by-read vs nobody-spoke look identical — the largest
   single comms blind spot in CT demo analysis.**
9. **Stable** travel-time geometry + partial rotations; **team/meta-dependent** fake
   frequency/sophistication (paiN's 2025 anti-predictability rework — CASE-09).

### META-C05 — Aggression and re-aggression

1. **Meaning.** Taking space, or reclaiming conceded space before Ts consolidate.
   `[guide]`/editorial re-aggression literature; Inferno-Banana flash+molly+push model.
2. **Objective.** Deny comfort; force contact on CT terms; break T mid-round flow.
3. **Appropriate.** Lost-but-unconsolidated area + layered utility; *designed*
   aggression: "if I die I have a purpose for dying… good support flashes… plan A,
   then B, C, D" (malbsMd `[primary]` HLTV 2025-09-04 — CASE-08).
4. **Questionable.** Unsupported aggression → isolated numbers deficit; baited ground
   re-takes; parking the most aggressive player at anchor (jabbi `[primary]` —
   aggression and anchor discipline are opposite roster traits).
5. **Reasonable information.** Utility inventory, teammate proximity, timing window;
   sync is largely comms.
6. **Alternatives.** Passive hold; delayed re-aggression post-utility-expiry; feint
   re-aggression baiting enemy utility then pulling back.
7. **Demo manifestation.** CT utility into a lost area → CT movement in; position
   regained pre-plant = success.
8. **Not inferable.** Called vs spontaneous; "feint" intent.
9. **Stable** space-contesting; **meta-dependent** re-entry safety (volatile smokes,
   incendiary spread buff Jul 2025 — TalkEsport analyses `[secondary]`).

### META-C06 — Retakes

1. **Meaning.** CT assault on a planted site to defuse (counterstrikewiki Retake).
2. **Objective.** Kill survivors + defuse within timer; trade-heavy entry, utility
   clearing.
3. **Appropriate.** Numbers/time/equipment arithmetic (EsportsOdds `[secondary]`
   2026-07-20 dataset): overall **23.1%**; full-vs-full ≈ **23.9%**; full-CT vs
   T-eco **59.0%** (only favored cell); save-gear vs force **1.8%**; broken-buy
   valley (~$7,700) **7.8%**. Team spread: Vitality 28.0% best … MongolZ 19.0% —
   framed as *style* (bLitz aggression wins pre-plant), not failure.
4. **Questionable.** Spending lives in the 7.8–1.8% cells — yet pros contest ~9/10
   lost planted rounds anyway. Question "spent lives", never "did they save".
5. **Reasonable information.** Kill-feed, plant location, bomb timer, enemy count —
   timer math demo-recoverable.
6. **Alternatives.** Save (META-C07); all-in. CS:GO-era save value (+4.3%/+3.9%
   next-round, NER0cs 2023) is `[unverified-transfer]` to MR12.
7. **Demo manifestation.** Retake-start vs plant time, retake utility, survivors,
   defuse-vs-expiry (89.5% of won retakes wipe all five; defuse-animation wins ~2%
   `[secondary]`).
8. **Not inferable.** Called vs default retake; conscious save vs never-arrived survivor.
9. **Stable** ~1-in-4 base rate + wipe-to-win; **economy-driven drift** (+3.1 Train,
   +1.7 Ancient to mid-2026 from CTs arriving richer — *not* new tactics) and
   **patch-dependent** Season-5 C4 shockwave ("within noise" at 11 days).

### META-C07 — Saving and economy arithmetic

1. **Meaning.** Withdrawing weapons vs contesting; force-buying to fund next rounds.
2. **Objective.** Maximise *next-round* win probability (NER0cs 2023 `[unverified-transfer]`).
3. **Appropriate.** Low-probability current round + weapon swing flipping next;
   score-tight full-next-buy saves; fragile-enemy-economy gambles.
4. **Questionable.** Skipping winnable 2v2/3v3 retakes (notably Inferno —
   `[unverified-transfer]` critique); post-2025 force-farming for the CT $50/kill
   bonus (Mauisnake-flagged risk `[secondary]` Dust2.us 2025-07-18); karrigan: new
   award "one of the best changes… $200 on every player… hero M4s" but hates $1,400
   loss bonus `[primary]` HLTV 2025-07-23.
5. **Reasonable information.** Team bank, loss-bonus state, enemy economy estimate —
   largely demo-inferable (money in file).
6. **Alternatives.** Eco/stack, force, utility-density half-buy (often > rifle-poor
   full buy — TalkEsport `[secondary]`).
7. **Demo manifestation.** End-round rifle survivors, round-start equipment value,
   loss-bonus progression. Reproducible aggregates: Complexity 2.2% T-side save …
   Virtus.pro 17.4% (btrams via Dust2.us `[secondary]` 2025-02-19).
8. **Not inferable.** Ordered save vs last-alive accident ("saves per round"
   conflates choice with survival — NER0cs 2023).
9. **Stable** save-vs-retake EV trade; **patch-shifting numbers** every economy patch
   (Jul-2025 buff; 2026 richer-at-plant drift).

### META-C08 — Utility conservation

1. **Meaning.** Holding nades for high-value moments vs spending for space/info.
2. **Objective.** Preserve for the round-decider: retake, exec denial, rotate cover.
3. **Appropriate.** Refrag anchor doctrine `[guide]` 2025-08-11: no early Apps smoke;
   right-click defensively on contact; quiet-late → time-bleed smoke *or* retake
   bank. Utility density as buy priority `[secondary]`.
4. **Questionable.** Burning into fakes/fog with no enabled play; dying full-utility
   (measurable giveaway).
5. **Reasonable information.** Own inventory (demo); enemy count partly demo, partly
   estimate. Hold-decision is comms/experience.
6. **Alternatives.** Time-for-utility; pick-for-utility; retake-cover retention.
7. **Demo manifestation.** Per-player utility thrown/timed vs first contact +
   unthrown-at-death — a clean demo metric.
8. **Not inferable.** Deliberate hold vs forgotten nade — identical in file.
9. **Stable** preservation principle; **patch-dependent** per-nade value (incendiary
   spread Jul 2025; smoke volatility).

### META-C09 — Information gathering and responding to uncertain info

1. **Meaning.** Acquiring (jumpspot, noise peek, deeper control) or withholding
   (silent defaults, smoke cuts, no-commit feints) information; then acting on
   ambiguity without guessing (counterstrikewiki; paiN rework CASE-09).
2. **Objective.** Decide on evidence; maximise expected value (partial rotation /
   delay utility) over binary commits.
3. **Appropriate.** Default/mid-round ambiguity; highest-EV hedge when confirmation
   is impossible.
4. **Questionable.** Over-gathering costing life/utility beyond the info's worth;
   readable gathering rhythms ("too obvious" — nqz `[primary]`); over-rotating to
   one cue.
5. **Reasonable information.** Observable cues demo-recoverable; *interpretation*
   and reports are not. karrigan remedy is comms: "I need feedback, ideas in my
   head… when nobody contributes I'm calling them out" `[primary]` HLTV 2025-07-23.
6. **Alternatives.** Hedge (partial), commit, delay-with-utility.
7. **Demo manifestation.** Jumpspot motions, first-peek timing, lane-blocking
   utility, early spend; bodies committed at the ambiguous moment; mirror-site
   utility retention.
8. **Not inferable.** Player confidence/read — correct hedge vs lucky non-rotation
   indistinguishable.
9. **Stable** acquire-before-commit + EV-hedge; **meta-dependent** cue reliability
   (smoke volatility, incendiary buff) and team fake sophistication.

---

## D — Team dynamics

### META-D01 — Trading and refrag opportunities

1. **Meaning.** Punishing a teammate's killer immediately; needs route/timing/angle
   alignment (counterstrikewiki Trade_Fragging; upforge 2026-08-31 `[guide]`).
2. **Objective.** Neutralise the man disadvantage.
3. **Appropriate.** Partner visible/audible and reachable in time. Window opens at
   **shot/sound/teammate-stop**, not kill-feed confirmation (upforge `[guide]`).
4. **Questionable.** "Following a teammate is not enough": split attention = two
   isolated fights; stacking blocks retreat + eats one spray (upforge); unsound
   attempts turn 1-for-1 into 2v3. HLTV: trade profiles measure **style, not
   effectiveness**; low involvement expected for entries/lurkers/AWPers
   (`[analyst]` HLTV 2023-01-26 `[pre-window]` principle retained).
5. **Reasonable information.** Sound, kill-feed, teammate position. Sound timing
   demo-inferable; *instruction* is comms.
6. **Alternatives.** Pre-aim the exit angle; flash/smoke-isolate the 1v2; disengage
   to keep the advantage.
7. **Demo manifestation.** Death→death intervals in pairs; pre-aimed vs late
   crosshair; traded-death rate by position (Overpass Monster/Short + Nuke Outside
   >21%; Nuke Ramp, Mirage/Dust2 B least `[analyst]` HLTV 2024-06-26).
8. **Not inferable.** Planned (pre-aimed) vs incidental trade — identical reads.
9. **Stable fundamental** (sub-tick didn't change it); position rates **pool-dependent**.

### META-D02 — Spacing and support relationships

1. **Meaning.** Pair geometry: close enough to punish the kill, far enough to
   survive one spray — "one doorway or one angle apart" as working rule
   (Soarne retake guide `[guide]` 2026-07-14).
2. **Objective.** Mutual tradeability without shared vulnerability; support utility
   arriving *before* bodies ("second player's grenade often > first bullet" —
   Soarne).
3. **Appropriate.** Retake pairs (Mirage B market+short; Ancient donut+CT; Nuke
   decon+doors); site pairs with split attention ("I clear close right, you clear
   default" — Soarne).
4. **Questionable.** Shoulder-to-shoulder (one flash blinds both); 5-seconds-apart
   arrivals (no trade); four crosshairs one angle while the hidden player doubles
   (Soarne).
5. **Reasonable information.** Partner position/intent via comms; demo shows geometry only.
6. **Alternatives.** Solo delay; utility-only support; regrouped simultaneous entry.
7. **Demo manifestation.** Pairwise distances at contact; arrival-time dispersion;
   utility-before-bodies sequencing.
8. **Not inferable.** Agreed split vs coincidental coverage.
9. **Stable** geometry principle; **meta-dependent** site-specific pair shapes.

### META-D03 — Coordinated pressure, timing and synchronization

1. **Meaning.** Multi-player actions on shared timing: layered utility then joint
   swing; regroup-then-hit; synchronized splits (Soarne `[guide]`; SCOPE.GG `[guide]`).
2. **Objective.** Force defenders onto two decisions at once; deny sequential duels.
3. **Appropriate.** Retakes with a staging line ("first CT stops where the team can
   catch up" — Soarne); re-aggression with flash+molly layering; splits with
   sub-second convergence.
4. **Questionable.** Sequential feeding ("fastest retake often pauses two seconds so
   three fight together" — Soarne); "half the team saving mentally while one plays
   hero" (Soarne save/retake `[guide]` 2026-07-07).
5. **Reasonable information.** Staging positions + countdown via comms; demo shows
   timing only.
6. **Alternatives.** Deliberate pressure play by one while others trade it; full
   regroup; abort to save.
7. **Demo manifestation.** Arrival-time clustering; swing simultaneity; "first death
   before group formed" (patience failure) vs "death during clear with no trade"
   (spacing failure) vs "survived to tap, nobody held swing" (defuse-pressure
   failure) — Soarne diagnostic.
8. **Not inferable.** Countdown vs coincidence; hero intent vs mis-timed group.
9. **Stable** simultaneity principle; **meta-dependent** viable windows per utility patch.

### META-D04 — Maintaining map control (team view)

1. **Meaning.** Holding taken space across the round: extremity presence, mid
   screens, rotation lanes watched (TalkEsport map-control `[secondary]` 2025-07-15).
2. **Objective.** Keep options + fake credibility alive into the late round.
3. **Appropriate.** Defaults preserving two-site threat; post-take holds freeing the
   pack to rotate.
4. **Questionable.** Abandoning control the execute needs (ENCE Train 5v4 loss,
   CASE-04); over-holding dead lanes while the hit starves.
5. **Reasonable information.** Lane states via presence/sound/comms.
6. **Alternatives.** Deliberate concession + re-take; threat-without-occupancy.
7. **Demo manifestation.** `[inference]` Occupancy timelines per region; control held
   vs abandoned post-take.
8. **Not inferable.** Concession-by-plan vs lost-duel collapse.
9. **Stable** options-preservation; **meta-dependent** lane values per pool.

### META-D05 — Playing numerical advantages (and disadvantages)

1. **Meaning.** Risk allocation by count: up → lower variance, convert; down →
   concentrate on one high-upside action.
2. **Objective.** Up: deny the "get kills early, otherwise save" CT path (Refrag
   post-plant tip `[guide]`); down: force a tradeable fight, never the trade game.
3. **Appropriate.** Up: passive crossfires, early utility, clock pressure (Refrag);
   down: flash-back into chokes, advanced flanks, bomb-tap pressure with cover
   (Refrag; Soarne tap doctrine `[guide]`).
4. **Questionable.** Up-aggression gifting isolated fights; down-passivity accepting
   out-trades (Refrag); thin spreads while down (sequential solos); up-passivity so
   deep the plant forces a coin-flip retake (~1-in-4 baseline, META-C06).
5. **Reasonable information.** Counts from kill-feed (demo-recoverable); risk
   philosophy is comms/coaching.
6. **Alternatives.** Stacked retake; bait-crossfire; exit-holding save.
7. **Demo manifestation.** Count-over-time, spatial dispersion, simultaneous vs
   sequential engagements.
8. **Not inferable.** Deliberate bait vs accidental grouping.
9. **Stable** variance principle; **meta-dependent** passivity value per economy cell
   (full-buy retake 31% vs broken 7.8% `[secondary]`).

### META-D06 — Risk distribution

1. **Meaning.** Spreading life-risk across map/roles so one duel can't collapse the
   round: Falcons' deliberate unevenness — karrigan/TeSeS absorb low-resource work,
   m0NESY/NiKo/kyousuke get freedom `[secondary]` Winio 2026-07-14.
2. **Objective.** Sustain multiple win conditions; survive simultaneous star slumps.
3. **Appropriate.** Star-trio systems with defined support absorption (Falcons Major
   run — CASE-10); "purpose for dying" aggression with pre-wired B/C/D plans
   (malbsMd `[primary]`).
4. **Questionable.** Five-independent-playmakers with no absorption (fragile to
   simultaneous quiet maps); all-risk-on-one-star (punished in Bo3 adaptation).
5. **Reasonable information.** Roster-level design (coaching); round-level risk is
   comms.
6. **Alternatives.** Even distribution (fragile ceiling, stable floor); full
   star-carry.
7. **Demo manifestation.** First-contact order by player; duel share vs round share;
   "who dies first, who closes" distributions.
8. **Not inferable.** Designed absorption vs unintentional baiting.
9. **Stable** concentration-vs-robustness trade; **roster/meta-dependent** accepted balance.

### META-D07 — Individual initiative versus team structure

1. **Meaning.** Top-down calling vs player initiative in mid-rounds; structure as
   scaffold, initiative inside it: "structure first, then freedom… only within clear
   boundaries" (nqz/biguzera `[primary]` via CS2NEWS 2025-09-18).
2. **Objective.** Combine predictability (teammates coordinated) with unreadability
   (opponents unprepared).
3. **Appropriate.** Pre-wired reactions ("plan A… B, C, D", malbsMd `[primary]`);
   site-leader empowerment (EliGE concept `[analyst]`); secondary callers (karrigan:
   Twistzz "first secondary caller since NiKo" `[primary]` HLTV 2025-10-06).
4. **Questionable.** Pure structure → readable (paiN "too obvious" — CASE-09); pure
   initiative → "five different ideas in a 3v3" (nqz); star-trio improvisation past
   safe structure (Falcons' chaos/discipline boundary `[secondary]`).
5. **Reasonable information.** Structural intent is coaching/comms (interviews only);
   behavioral output (fight order) demo-recoverable.
6. **Alternatives.** Full IGL micromanagement; full player initiative; map-split
   calling.
7. **Demo manifestation.** Engagement initiation order, first-contact-by-role
   frequency — measurable structure proxies.
8. **Not inferable.** Almost all of it: caller identity, empowerment vs overrule,
   culture dynamics (karrigan "calling out" bad comms, "small punishment helps"
   `[primary]`); comms "aliveness" as performance input (flameZ `[primary]`
   2026-10-12).
9. **Stable** tension; **era/roster-dependent** accepted balance (IGL-as-rotator
   shift `[analyst]`; Liquid "system and fundamentals" rebuild `[primary]` coach
   flashie 2025-07-24).

---

## P — Professional versus ranked gameplay

### META-P01 — What transfers to the individual (portable skills)

Portable without team protocols `[primary]`-backed where noted:

- Taking duels + trading mechanics (window at sound/shot, not kill-feed).
- Alone-late play: patience, timing, extremity control (lurker *skills*).
- Sightline ownership, crosshair placement, AWP repositioning.
- Survival-under-execute + retake mechanics (staging, layered clearing, tap
  discipline — Soarne `[guide]`).
- Self-utility: own lineups, self-flashes, execute util (Esports Insider:
  "all players expected to know common lineups… especially in public matchmaking"
  `[guide]`).
- Second-voice information sharing: Perfecto "can always be a second caller" on
  FACEIT `[primary]` HLTV 2025-09-11.
- Side-specific mindset: lurker-patience on T, anchor-discipline on CT are the same
  disposition, transfer intact `[primary]` Paskiv et al. 2026.

### META-P02 — What needs protocols, comms or prep (not solo-gradeable)

Requires a five-stack artifact; absent in pugs:

- Defaults, mid-control scripts, utility-denied angles; "space" only pays if
  teammates exploit it.
- Execute timing + entry order + flash-for-partner windows.
- Rotate discipline, site stacks, anchor/rotator assignment ("site leaders").
- IGL repositioning: voice, threat model, protocols, timeouts.
- Conditioning across a half (needs a team executing one plan).
- Anti-strat reads (bo3 `[analyst]`); "protocols… the pure basics of a team"
  (siuhy `[primary]`); measured against "protocols of our system" (B1ad3 `[primary]`).
- Assignment by personality/plan (jabbi/Staehr; makazze role-gifting `[primary]`).
- Pro pipeline note: "so many players PUG, but nobody wants to go pro" — pugs ≠
  development path (GUM/Lynn Vision coach `[primary]` HLTV 2026-06-02).
- Calibration use only: jabbi — new economy/CT-molly feel came from "the feeling
  from PUGs" `[primary]`; pugs as mechanism lab, not system rehearsal.

### META-P03 — Coaching failure modes (ranked review anti-patterns)

1. **Missing-partner critique.** Blaming entry death with no designated second man
   (pro norm: "get traded… done your job" `[guide]`; Liquid affliction `[analyst]`).
2. **Missing-plan critique.** Blaming lurker absence / mid takes nobody exploits
   (lurker value defined *relative to plan*).
3. **Protocol-as-skill confusion.** Utility/comms graded against non-existent
   five-stack protocols (siuhy `[primary]`).
4. **Rating-across-roles.** Unadjusted rating vs pros ("ought not be compared
   across roles or sides on a single composite" `[primary]`; HLTV Target Rating
   exists because positions change expected output `[analyst]`).
5. **Side confusion.** CT-anchor vs T-lurker treated as one "real role" (same
   disposition, different expression `[primary]`).
6. **Outcome-conditioning.** Grading by round result: tN1R's reasoned switch hurt
   stats (CASE-11); huNter-'s doubted IGL tenure won a trophy (CASE-13) — outcome ≠
   decision quality.
7. **IGL-as-player-critique.** Judging solo "calling" by individual stats
   (leadership recall ~0.5 `[primary]`; no voice in demo).

---

## X — Patch and meta context (analysis-relevant, Oct 2024 – Oct 2026)

### META-X01 — Gameplay/economy changes with tactical consequences

| Date | Change | Tactical consequence | S/P |
|---|---|---|---|
| 2024-10-28 | HE inside smoke clears smoke-in-eye effect on hit players | HE-into-own-smoke as "un-blind" clear | S |
| 2024-11-13 | Damage prediction (client-side hit FX) | Demo/POV hit feedback can contradict server truth | S |
| 2025-01-28 (S2) | M4A4 →$2,900; FAMAS →$1,950 + accuracy; SMG crouch-accuracy nerf | CT full-buy cheaper; SMG anti-eco spray weakened | P/eco |
| 2025-03-31 | Inferno rebuilt toward CS:GO proportions | Banana timings + many lineups changed | P |
| 2025-07-15 (S3) | CT **+$50/kill team award**; incendiary spread faster; MP9 recoil+/jump-acc↓ | CT economy buffed win-or-lose; faster area denial; MP9 run-and-gun dead | P/eco |
| 2025-10-14 | **Defuse penalty: −150 ms fire delay + scope block on defuse exit** | Fake-defuse-then-peek punished; tap-spam has real cost | S |
| 2025-11-04 | **TrueView demo playback** (client-prediction reconstruction) | Closest "what they saw"; still 1–2 frames off on recoil/muzzle/blood | S |
| 2026-01-21 (S4) | SMG buffs (−$100); **jump rework** (stamina penalty removed, subtick landing) | Repeated-jump/strafe cost changed — most significant movement change in window | S |
| 2026-03-18 | **Reload refactor: remaining mag ammo DISCARDED**; reserve as magazines; AWP 15 shots | Spray-and-reload discipline; parsers see different ammo accounting | S |
| 2026-04-21 | Recoil camera → CS:GO-like (trajectories stay CS2) | On-screen crosshair vs true trajectory diverge further | S |
| 2026-07-08 (S5) | **C4 explosion reworked**: per-map baked simulation, expanding shockwave, blocked by walls | After-plant survival calculus changed per map | S |
| 2026-07-20 | C4 explosion interacts with smokes/fire; health preview only when audible | Post-plant utility alters detonation; earlier preview removed | S |
| 2026-09-09 | **Demo chat encrypted** (CS:GO rules); team chat unrecoverable externally | Kills chat-based features; parser user-message IDs renamed (`_CSGOLegacy`) | S |

No AWP damage/price, AK/M4 damage, armor-penetration, or loss-bonus rework found in
window (armor-penetration premise **unverified** — treat as stable). Valve-note
verification: cs2metahistory verbatim transcriptions + Steam announcement links;
`counter-strike.net`/Steam/Liquipedia JS- or access-blocked (see `sources.md` limits).

### META-X02 — Map pool and side-balance context (Oct 2026)

Active Duty since 2026-07-08 (Season 5): **Ancient, Anubis, Cache, Dust II, Inferno,
Mirage, Nuke**. Reserve: Overpass (out Jul 2026), Train (out Jan 2026), Vertigo (out
Jan 2025). Cadence: one map swapped per six-month Premier season (S2 Train↔Vertigo;
S3 Overpass↔Anubis; S4 Anubis↔Train; S5 Cache↔Overpass). `[secondary]` r1gg 2026-10-13
+ Valve-note transcriptions.

Pool-wide tier-1 CT share: **50.0% (Feb 2024) → 52.6% (Aug 2026)**, 2,073 matches /
4,621 maps `[secondary]` cs2metahistory pro-meta. Per-map all-time CT:
Nuke 55.3%, Mirage 53.8% (S4 peak 57.7%), Cache 52.2% (thin), Dust2 50.1%, Inferno
50.2%, Ancient 49.9%, Anubis 44.6% (only strongly T-sided pool map). Overpass left at
55.5% all-time CT. Caution: site presents updates beside shifts **without claiming
causation** — do the same.

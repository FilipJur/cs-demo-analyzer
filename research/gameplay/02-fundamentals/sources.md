# Annotated Sources — CS2 Fundamentals

**Access date for all sources: 2026-10-15/16** (unless dated inline). Grades:
**M** measured/tested/transcribed/file-sourced · **O** Valve/first-party ·
**E** expert (pro/coach/analytics outlet, demo-backed) · **C** practitioner guide
(definition-reliable, not efficacy evidence) · **P** press/secondary (method disclosed).
`[stale]` / `[disputed]` / `[lead]` as noted. Scheme-less domains per repo convention
are not used here — full URLs, since this file is the citation authority.
Sibling files cite by short name + URL on first use; this file is the verifiability record.

## Official (Valve / engine schema / patch records)

- Valve — "Moving Beyond Tick Rate" launch video (sub-tick slogan: "the server will know the
  exact moment you fired your shot…"). https://www.youtube.com/watch?v=GqhhFl5zgA0 (2023-03-22).
  **O.** Cite only with the 2023–2026 revision caveat (Nov-2023 feedback-sync, Nov-2024
  lag-comp, Sept-2025 subtick shooting, Animgraph2 Apr-2026).
- Valve — CS2 official page (sub-tick architecture statement). https://www.counter-strike.net/cs2
  (live). **O.** No ms, no ping formula.
- `CCSWeaponBaseVData` schema (inaccuracy/recovery field set: Spread, Inaccuracy
  Stand/Crouch/Jump/Land/Ladder/Move/Fire, RecoveryTime Stand/Crouch, transition bullets,
  AttackMovespeedFactor). https://github.com/SteamTracking/GameTracking-CS2/blob/master/DumpSource2/schemas/client/CCSWeaponBaseVData.h **O.**
  Combination formula unsourced — explicit unknown.
- `C_CSPlayerPawn` schema, build 25947352 (m_iShotsFired, m_flFlinchStack, m_flVelocityModifier,
  m_flInterpolatedInaccuracy). https://cs2opendev.github.io/CS2OpenDev-Docs/schemas/client/C_CSPlayerPawn/ **O.**
- `CCSPlayer_AimPunchServices` schema. https://cs2opendev.github.io/CS2OpenDev-Docs/schemas/server/CCSPlayer_AimPunchServices/ **O.**
- Valve developer wiki — CS2 console commands/variables (FF-reduction cvars).
  https://developer.valvesoftware.com/wiki/List_of_Counter-Strike_2_console_commands_and_variables **O.**
- CS2 `usercmd.proto` (`CBaseUserCmdPB`: buttons, viewangles, moves, weaponselect, mousedx/y,
  subtick steps). https://github.com/SteamTracking/GameTracking-CS2/blob/master/Protobufs/usercmd.proto **O.**
- Valve patch notes mirrors: May-2024 economy/incendiary (plant-loss $800→$600; incendiary
  duration/spread cut, $600→$500; M4A4 $3,100→$3,000) via HLTV
  https://www.hltv.org/news/39059/update-economy-incendiary-vertigo-changes **O-via-Expert**;
  Apr-2024 Zeus $0→$100 Competitive ($50 Casual), CZ $100→$300 via SteamDB
  https://steamdb.info/patchnotes/14178987/ and https://www.ign.com/wikis/counter-strike-2/Counter_Strike_2_April_25_Patch_Notes **O**;
  2025-09-09 / 2025-09-16 update notes via Steam news (no subtick text in 09-09 body;
  Genesis items in 09-16) **O**; July-2025 1.45.0 body unrecovered from
  https://www.counter-strike.net/newsentry/529852487375519749 — shared-$50 stays
  Expert+Community dual-sourced, keep patch-date parameter.
- Local install verification (2026-10-15, build 25947352): competitive `gamemode_competitive.cfg`
  FF values byte-identical to fitted (bullets 0.33, grenade 0.85, grenade-self 1.0, other 0.4);
  casual/DM/retakes all-zero — competitive-mode scope. **O-local (primary).**

## Measured (tests / datamined tables / datasets / tools)

- Memorin — bullet-damage formula + range falloff (proto 14166, compiled weapon data, convars;
  29/30 exact; hit-point distance basis; per-weapon heads; 0/9,372 impacts negative).
  https://memorin.app/mechanics/bullet-damage **M.**
- Memorin — mouse sensitivity + scope zoom transcription (FOV 90→40→10 AWP / 15 SSG;
  sens truncation; unzoom/rezoom timings). https://memorin.app/mechanics/mouse-sensitivity **M.**
- Memorin — movement constants (gravity 800; friction 5.2 + stopspeed 80; accelerate 5.5;
  walk ×0.52; duck ×0.34, 10-tick ramp; hull 72/54; jump vz 286.37; no single-jump slowdown).
  https://memorin.app/mechanics/movement-constants **M.**
- cs2.gs weapon pages (game files, build 1.41.8.2): AK-47, M4A4, M4A1-S, USP-S, Glock-18,
  Deagle, Tec-9, P250, FAMAS, Galil-AR, AUG, SG-553, SSG-08, MP9 (spread/stand/crouch/move/
  jump/per-shot/recovery/transition/speed). https://cs2.gs/weapons/ak-47/ (et al.) **M
  (file-sourced display; JS-shell readers — values banked from captured text, TradeIt
  cross-checked).**
- Tradeit — complete CS2 weapon stats (34 firearms / 16 fields; checked 2026-07-20 vs
  community spreadsheet + Valve history + damage guide; 2026-03-18 baseline, post
  magazine-discard). https://tradeit.gg/blog/cs2-weapon-stats **M (third-party spreadsheet,
  not Valve).** Prefer over Fandom CS:GO table (carryover UNVERIFIED).
- CSBePro — AWP guide stat block (build 1.41.7.6; one-tap ranges; reload/ammo).
  https://csbepro.com/cs2-weapon/awp-guide-for-counter-strike-2/ **M (datamined third-party).**
- OP.GG — AK-47 stats + hitbox table. https://op.gg/cs2/weapons/weapon_ak47 **C (datamined display).**
- Codex — damage falloff mechanic page (AK 36/77.5%, M4A4 33/70%; **Deagle 63 CONFLICTS
  Tradeit 53 — build-check before use**). https://counterstrike.codexery.com/wiki/damage-falloff **C.**
- Codex — accuracy model; round mechanics (freeze/plant/defuse constants as reported).
  https://counterstrike.codexery.com/wiki/accuracy ;
  https://counterstrike.codexery.com/wiki/how-a-round-works **C.**
- TotalCS cvar defaults (FF bullets/grenade/other, inferno_flame_lifetime = 7 base,
  mp_freezetime/mp_c4timer/mp_roundtime_defuse). https://totalcsgo.com/commands/ffdamagereductionbullets
  (et al.) **M (cvar defaults).**
- demoparser2 / demoparser docs + issue #340 (delta-encoded usercmds from ~2026-07-10;
  fix 0.42.0 2026-08-08). https://github.com/LaihoE/demoparser ;
  https://github.com/LaihoE/demoparser/issues/340 **M/O-primary(thread).**
  Examples: aim analysis, buttons bitfield (same repo paths). **M.**
- awpy stable reference (snapshots/ticks fields; traded-death 5.25 s @ 3.0.0; Rust-core
  rewrite, single release 2026-10-14). https://awpy.readthedocs.io/en/stable/reference.html **M.**
- Leetify stats glossary (34% counter-strafe; TTD; placement delta; >1.1 s flash;
  spotted-accuracy; O/A/S trade definitions). https://leetify.com/blog/leetify-stats-glossary/ **M
  (first-party definitions).**
- Leetify aim hitbox improvement (raycaster → human hitboxes; Aim Rating ~+4; benchmark
  renormalisation). https://leetify.com/blog/aim-stat-calculation-hitboxes-improved/ **M/E.**
- Leetify benchmarks + rating explained + improvement guide (z-scores, 2024 reset to 50,
  percentile colors; zero-sum WP weighting 35/30/15/20; "performance not skill"; 30-day habit
  lens). https://leetify.com/blog/cs2-benchmarks/ ;
  https://leetify.com/blog/leetify-rating-explained/ ;
  https://leetify.com/blog/leetify-guide-how-to-start-improving-in-csgo/ **E/Official-vendor.**
- esportsodds datasets: weapon meta (6.68M pro kills)
  https://esportsodds.gg/learn/cs2-weapon-meta ; map win rates (~2M rounds)
  https://esportsodds.gg/learn/cs2-map-win-rates ; force-buy glossary (band-honesty note)
  https://esportsodds.gg/glossary/force-buy ; eco glossary
  https://esportsodds.gg/glossary/eco-round ; comebacks/opening-kill 71.8%
  https://esportsodds.gg/learn/cs2-comebacks ; AWP-nerf page
  https://esportsodds.gg/learn/cs2-awp-nerf ; retakes https://esportsodds.gg/learn/cs2-retakes ;
  economy https://esportsodds.gg/learn/cs2-economy ; trade-kill glossary
  https://esportsodds.gg/glossary/trade-kill **M (dataset-computed; eco/force inferred from
  equipment value — report band rates as band rates).**
- Tokey et al. (WPI/NVIDIA) — peeker's-advantage latency lab (FDG 2024; FPSci custom game;
  24 players; +28–31% @60 ms, −5–13% @0 ms; distance sig.; ~10 ms visible→hit gap).
  https://web.cs.wpi.edu/~claypool/papers/peeker-fdg-24/paper.pdf **M (non-CS2 — MUST NOT port).**
- Baron & Hershey (1988) — outcome bias, JPSP 54(4). https://pubmed.ncbi.nlm.nih.gov/3367280/ **M.**
- Fischhoff (1975/2003) — hindsight bias. https://pmc.ncbi.nlm.nih.gov/articles/PMC1743746/ **M.**
- Proteau, Marteniuk & Lévesque (1992) — specificity of practice.
  https://pubmed.ncbi.nlm.nih.gov/1631322/ **M.**
- Listman et al. (2021) — motor learning in the wild (N=7,174; 682k runs; ~90% benefit in
  30 min; 40–60% retention). https://pmc.ncbi.nlm.nih.gov/articles/PMC8720934/ **M.**
- Pluss et al. (2021) — practice quantity→tournament (43 pros; R²=0.30; quality > quantity).
  https://jses.net/wp-content/uploads/2021/02/Pluss-et-al.-2021.pdf **M.**
- Pluss et al. (2020) — perceptual-motor expertise ceiling (25/25/25; limited pro/rec split).
  https://www.journalofexpertise.org/articles/volume3_issue2/JoE_3_2/JoE_3_2_Pluss_etal.pdf **M.**
- Miao et al. (2024) — esports cognition meta (15 studies; g=0.373 overall, 0.822 spatial).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11316462/ **M (largely correlational).**
- Rogers et al. (2024) — KovaaK's reliability pilot (ICC .947–.995, n=10, anti-extrapolation
  warning). https://pmc.ncbi.nlm.nih.gov/articles/PMC10925653/ **M.**
- Yeh et al. (2024) — registered null on action-game visual transfer (20 h).
  https://www.nature.com/articles/s41598-024-71987-y **M.**
- Lamers James & O'Connor (2023) — attention-focus null in Aim Lab (N=37).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10368276/ **M.**
- Roldan & Prasetyo (2021) — Aim Lab→Valorant (n=6, 1 week, avg-dmg/round only). IEEE ICIEA.
  **M (weak).**
- Sharpe et al. (2023) — multi-dimensional CS:GO performance Delphi (pros vs researchers
  disagree on "good"). https://doi.org/10.1123/jege.2022-0017 **M.**

## Expert (pro / coach / analytics outlets)

- HLTV — Rating 3.0 methodology (trade denial/failed trade 5 s; Swing splits; eco discount;
  passivity caveat). https://www.hltv.org/news/42485/introducing-rating-30 (2025-08-20).
  Refresh 2026-10-01 (29,030 maps; map-specific; Cache CT-sided; Swing floor 0):
  https://www.hltv.org/news/45596/rating-30-receives-small-accuracy-improvements
  (body-verified via Jina; HLTV direct 403 ×3 — re-verify primary when possible).
  Trading-structure piece (saved-teammate 1 s; Lone Wolf/Lamb/Crow = style; Heroic-fluid).
  https://www.hltv.org/news/35389/how-trading-stats-can-show-a-teams-structure-and-why-heroic-stand-out
  Rating 2.1 piece (save/survivorship discussion). https://www.hltv.org/news/40051/introducing-rating-21
  **Official-analyst / E.**
- HLTV data-revolution feature (kassad/ash/valens/DeMarsDeRover: behavior > stats; data as
  filter; EGR/fair-duels; eye test). https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution **E.**
- HLTV coach interviews: zonic (2016 counter-call; playbook), ImAPet (demo saturation),
  zews (collaborative review; error taxonomy), B1ad3 (system; error-type separation),
  kassad ("fundamentally bad CS" simple mistakes). URLs in `progression.md` §4. **E
  (kassad/zonic-international quotes headline-level — HLTV rate-limited direct read).**
- Refrag — counter-strafing; economy crash course ($2,000 rule; rewards/loss ladder);
  stats explained (K/D-vs-rating; role confound; bracket weighting; HLTV 3.0 summary);
  Refrag Rating (bracket-relative; "separating metrics differ by bracket"); Refrag Coach
  (placement degrees; TTD; counter-strafe %; drills). https://refrag.gg/blog/counter-strafing-the-key-to-precision-aim-in-counter-strike-2/ ;
  https://refrag.gg/blog/cs2-economy-crash-course-what-are-kill-rewards-and-loss-bonus ;
  https://refrag.gg/blog/cs2-stats-explained/ ; https://refrag.gg/blog/refrag-rating-explained/ ;
  https://refrag.gg/blog/what-is-refrag-coach/ **E (coaching/analytics vendor; TTD conflates
  aim with selection — noted).**
- BLAST.tv — anchor guide (delay > kills; rotation-time job).
  https://blast.tv/article/cs2-anchor-guide **E-press.**
- scope.gg coach blog — crosshair placement (closest-angle; lazy-crosshair); AWP guide
  (denial/space-making; pistol tiers; utility-first). https://blog.scope.gg/crosshair-placement-en/ ;
  https://scope.gg/guides/awp_guide_scopegg_en/ **E (CS:GO-era mechanics — unverified transfer).**
- CSStatLab Academy — gameplay (man-advantage/disadvantage, losing-first-pick, trading-kills,
  crossfires, entry-fragging, contact-plays, post-plant, counter-strafing, movement-accuracy,
  crosshair-placement, pre-aim); weapons (spray-burst-tap, recoil patterns, AK spray,
  AK-vs-M4, M4A4-vs-A1-S); statistics (Leetify glossary secondary); rankings
  (Premier/ratings/reset/Prime explainers); sound-cues; economy-management.
  https://csstatlab.com/academy/gameplay/man-advantage-fundamentals (et al., full list in
  slice transcripts) **E-Community boundary (editorially maintained 2026; mechanics-explainer
  grade — internal numbers consistent with game files, no test methodology shown).**
- Mythras game-file guides (weapons.vdata-sourced; per-claim source links): utility, pistols,
  M4A4-vs-A1-S (+60 ms TTK inversion), AK-vs-Galil (2,583 u one-tap math), AUG-vs-SG,
  spray-control (lookup-table mechanism), AWP, SCAR-vs-G3, Zeus/knife reference, movement/
  counter-strafing, practice-server commands.
  https://gamertagmythras.com/blog/counter-strike-2/cs2-utility-guide (et al.) **E/C with
  game-file tier below Valve but above spreadsheet DBs; unit conversions authorial — flag.**
- NextFrag — counter-strafe analysis; crosshair-placement analysis; first-bullet accuracy;
  demo-analysis limitations; sensitivity guide (cm/360; signed-error method; pro range 25–65).
  https://nextfrag.gg/cs2-counter-strafe-analysis (et al.) **C-vendor (method described,
  no sample counts).**
- EGamersWorld — 1.45.0 patch summary (CT +$50 shared; incendiary faster spread; Overpass/
  Anubis; MP9 nerf). https://egamersworld.com/counterstrike/news/28761/cs2-balance-changes-before-iem-cologne-2025-premie-GHlwMoEan **E-outlet (patch-summary tier).**
- Skin.club — post-July-2025 economy explainer. https://community.skin.club/en/news/how-the-new-cs2-economy-works **C (post-patch mechanics).**
- Farmskins — grenade durations; grenade damage guide (blind ≤4.87–5 s; fire ramp; HE ≤98/57;
  impact HP). https://farmskins.com/articles/guides/mechanics/what-is-the-duration-of-grenades-in-cs2 ;
  https://farmskins.com/articles/guides/nades/cs2-grenade-damage-guide **C (measured-style;
  smoke "20 s" RETRACTED 4:1; molotov/incendiary conflict resolved via May-2024 Official).**
- Swap.gg — smoke duration (18 s from detonation; usable/thin/radar-block splits; HE/bullet
  interaction; ninja-defuse arithmetic). https://swap.gg/blog/how-long-does-smoke-last-in-cs2 **C.**
- R1GG — bomb timer; round length; (economy page). https://r1gg.com/cs2/guides/cs2-bomb-timer ;
  https://r1gg.com/cs2/guides/how-long-is-a-round-in-cs2 **C.**
- RoundScope — utility benchmarks (4–6 vs 8–12 dmg/rd; >0.7 vs <0.4 flashed-per-flash).
  https://roundscope.cc/guides/utility-guide-flashes-and-grenades **E/C.**
- Strafe — retakes lesson; C4 guide (plant 3.2 s tactics-half; 45 s/800/600 constants STALE —
  tactics only). https://www.strafe.com/news/read/how-to-play-retakes-in-cs2/ **E/C.**
- Liquipedia — Flashbang; Defuse Kit. https://liquipedia.net/counterstrike/Flashbang **C.**
- GuildOrder — economy + utility theory (full/eco/force/half-buy framework; ~$4,800 full buy;
  team utility $5.5–6.5k). https://guildorder.com/games/csgo/guides/economy-and-utility-theory **C
  (plant-loss "$800" STALE — never cite; Zeus "$0" STALE).**
- MetaBot — peeking; counter-strafing/movement-accuracy; smokes; utility-grenades; economy
  (buy/force/save). https://metabot.gg/en/cs2/guides/cs2-peeking-guide-wide-jiggle-shoulder
  (et al.) **C.**
- BO3.gg — peeking guide (jiggle/wide/shoulder; Ferrari pair); AWP quick-vs-slow scope
  (150–250 ms claim — commenters dispute); B1ad3 system report; utility overview.
  https://bo3.gg/articles/cs2-peeking-guide-jiggle-peek-vs-wide-peek-vs-shoulder-peek ;
  https://bo3.gg/articles/cs2-awp-quick-scope-vs-slow-scope-which-is-more-accurate **C.**
- Dignitas — peeker's-advantage explainer (2024-01, pre-Nov-2024 **[stale]**);
  peek-improvement guide (2026-06, E-org advice).
  https://dignitas.gg/articles/understanding-peeker-s-advantage-in-cs2 **C.**
- SteamAnalyst — shooting/peeking/movement guide (six peek types; fire-mode table; practice
  stack; speeds; "~88 u/s" **arithmetically wrong — quarantined**; "~34%" corroborates).
  https://www.steamanalyst.com/guides/cs2-shooting-peeking-movement-guide **C.**
- CS2.eu — movement guide (~50 ms stop claim unverified; bhop ~300; crouch rules); AWP guide
  (~100 ms settle — 1 of 5 disputed); glossary (baiting ≠ trading); smoke "18 s" corroboration.
  https://cs2.eu/news/cs2-movement-guide-counter-strafing-bunny-hopping-and-more **C.**
- Gamers.Wiki — AWP holding-angles guide (+200 ms quickscope — disputed; shot-and-swap;
  off-angles 200–300 ms; positions; economy); M4A4-vs-A1-S split (**"80% of pros" (5)**).
  **C.**
- fgrind — trade/peek/repeek guide. https://fgrind.com/blog/cs2-trade-peek-repeek/ **C.**
- Hard2Kill — positioning guide 2026. https://hard2kill.gg/guides/cs2-positioning-guide-2026 **C.**
- BoostRoom — peeking/swinging/jiggle/prefire guide. https://boostroom.com/blog/cs2-peeking-guide-swinging-jiggle-peeking-and-prefires **C.**
- Steam community guide — peeking (singlepeek; widepeek risk; shoulder rule; flash nuance;
  counter-strafe over release). https://steamcommunity.com/sharedfiles/filedetails?id=3438946604 **C.**
- Steam community — subtick technical guide (event timestamping, NOT tickless; 2023–2026
  revision timeline). https://steamcommunity.com/sharedfiles/filedetails/?id=3785685469&searchtext=binds **C
  w/ official-revision trace.**
- Steam community — accuracy-model revert guide (34% + exponential-decay mechanics).
  https://steamcommunity.com/sharedfiles/filedetails?id=3710237601 **C/RE.**
- UnknownCheats — `get_inaccuracy` RE (selection-not-sum; fire-wins; author-flagged
  uncertainty). https://www.unknowncheats.me/forum/counter-strike-2-a/623351-get_inaccuracy-weapon_v_data-externally.html **C/RE (informed, not canon).**
- CS.MONEY — distances illustration (M4A4-vs-UMP worked ranges). https://cs.money/blog/games/game-fundamentals-how-distances-work-in-cs2/ **C.**
- ggclan — 1v3 clutch tips (isolation doctrine, pro clip). https://ggclan.com/news/cs2-1v3-clutch-tips-win-low-man-rounds **C.**
- cyber-lab — trade glossary (react distance). https://cyber-lab.net/en/slovar/trade **C.**
- critfeed/blog.cs2.ad — roles (entry/trader/lurker/anchor/rotator).
  https://critfeed.com/cs2-roles/ **C.**
- UpForge — AWPer positioning; buy-round economy roles; CT rotations; demo-review workflow;
  retake spacing; T-side defaults; trading distance. https://upforge.gg/blog/cs2-awper-positioning-guide
  (et al.) **C.**
- Soarne — CT retakes without feeding; save-vs-retake; force-after-pistol; full-buy planning;
  utility-that-gets-used. https://soarne.com/blog/how-do-cs2-cts-retake-a-site-without-feeding-kills
  (et al.) **C.**
- winio.ai — economy guide; Rating-3.0-refresh secondary summary (verify vs HLTV primary).
  https://winio.ai/blog/articles/cs2-economy-guide-when-to-buy-save-eco-or-force **C/P.**
- White Market — defuse guide (kit pickup behavior). https://news.white.market/guides/how-to-defuse-bomb-cs2 **C.**
- skinvs — bomb-smoke interaction (July-2026). https://www.skinvs.com/articles/cs2-bomb-smoke-interaction-update-july-2026 **C.**
- Water CS2 — recoil comparison video (CS2 ~8–10% tighter; directional only).
  https://www.youtube.com/watch?v=uZXTgzJKfQ0 **C-tester.**
- Strider — rifle guide video (damage/TTK cross-checked where overlapping).
  https://www.youtube.com/watch?v=ovEdyGfgSCc **C-tester.**
- austincs — spray-ceiling observation (vertical saturates ~bullet 7; left/right after).
  https://www.youtube.com/watch?v=mpSigKlgeLc **C (single observation).**
- WarOwl CS2-vs-CS:GO test; xplay anchor positions; Hotspawn entry-fraggers — **403 / paywall /
  title-level: leads, not evidence.**
- Counter-Strike wiki — movement; movement inaccuracy; anti-eco doctrine.
  https://counterstrikewiki.com/Movement ; https://counterstrikewiki.com/Anti-eco **C.**
- Fandom — damage dropoff (CS:GO-era; formula shape reusable, rows superseded);
  inaccuracy; money. https://counterstrike.fandom.com/wiki/Damage_dropoff **C [stale-era].**

## Press / secondary (method disclosed)

- Esports Insider — Sept-2025 subtick-shooting gloss. **P.**
- Tradeit changelog compilation (TrueView 2025-11-05; scope-sound 2025-10-30; defuse/scope-block
  2025-10-15; Animgraph2 Apr-2026; magazine-discard 2026-03-19). https://tradeit.gg/blog/cs2-updates/ **P
  (compiled — verify load-bearing claims vs Steam notes).**
- AllPatchNotes — recoil/aim-punch tweaks. https://allpatchnotes.com/g/counter-strike-2/recoil-and-aim-punch-tweaks **P.**
- CS2MetaHistory — economy + utility timelines. https://cs2metahistory.com/timeline/economy/ ;
  https://cs2metahistory.com/timeline/utility/ **P.**
- dust2.us — valens tier-one/role-reset piece; ash star-player piece; CT-economy piece.
  (URLs in `progression.md` §4.) **P/E-outlet.**
- CSDB — grenade guide; rounds guide (429s — leads). **P.**
- escorenews / shattered.io / csmarket.gg — MR12/OT corroboration snippets (first-to-13,
  OT at 12–12 multi-sourced; MR3-vs-MR6 variants unconfirmed). **P.**
- Aim Lab blog — outcome-dependency; plateau; improvement-visibility (vendor framing of
  Listman-type findings). https://aimlabs.com/articles/aimlabs/outcome-dependency-stop-judging-your-performance-by-the-scoreboard/ (et al.) **P-vendor.**

## Repo-internal (verified in-repo, research scope)

- `research/muse/D-mistakes.md` — 52-class taxonomy; fact/indicator/verdict; smoke + info
  blockers; parser probing (0.42.0). **Senior taxonomy — built on, not redone.**
- `research/muse/G-coaching-eval.md` + `parts/g-coaching/` — outcome bias; plateau evidence;
  coach interviews; review methodology; eval framework. **Senior coaching science.**
- `research/gameplay/01-modern-meta/`, `04-decision-evaluation/` — 9-point schema; trading
  O/A/S; review methodology; slogan critiques.
- Backend pipeline (read-only verification): `parsing/awpy_adapter.py`, `domain/tables.py`,
  `domain/contracts.py`, `analytics/context.py`, `domain/evidence.py`, `normalize.py`
  (extended `shots`: scoped + inaccuracy + ammo; kills: noscope/thrusmoke/penetrated/hitgroup;
  upstream derived classifications intentionally NOT normalized; **no `TRADE_WINDOW` constant —
  recompute from `player_death` timestamps**). **Project-local Official.**
- `validation-v1.md` — first demo validation (de_train GOTV; 2,738 shots; burst-aware gating
  requirement; `shots.scoped` 0/52 parser-semantics question). **Local Measured (n=1 — do not
  generalize).**

## Explicitly excluded / quarantined (not evidence)

- CSDB peeker-advantage + placement pages (persistent 429); Boosteria pages (feed-only);
  Liquipedia direct Weapon Chart/AWP (403 — wiki-summary used with CS:GO label);
  HLTV lag-compensation body (403 — headline only); Reddit counter-strafe/jiggle threads
  (login-walled / title-snippet-level — CS2 caveat "small jiggles punished harder" stays
  Community, no ms); Gamers.Wiki "80% of pros" + YEKINDAR quote (unattributed — (5));
  WarOwl video (unwatched); Twistzz piece; YouTube mistake-format videos
  (https://www.youtube.com/watch?v=u95g4Sp6XlA,
  https://www.youtube.com/watch?v=8jGJXdnd2oc — unwatched leads);
  Fandom CS:GO damage rows (superseded); Codex Deagle-63 vs Tradeit-53 (unresolved —
  build-check); local VPKs (source identified, unmined); `m4a4-vs-m4a1-s` CSStatLab URL
  (entered audit pool only, never read — removed); eugenio8a8 X-post / spray-test videos /
  Daybreak crouch thread (flagged unread at first mention throughout).

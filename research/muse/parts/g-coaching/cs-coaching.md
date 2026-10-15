# CS2 Demo Analysis & Personal Coaching: Evidence, Practice, and Limits

**Audience:** ~2000 FACEIT Elo (ex-2400) CS2 player. No beginner content.
**Compiled:** 2026-10-15. **Method:** primary sources prioritised (peer-reviewed articles, official Valve/Steam docs, repository source, HLTV first-person interviews). Coaching-vendor blog content is included **only** as a labelled artifact of "what coaches claim they check," never as evidence a method works.

**Category tags used:** `Demonstrated` (directly evidenced by experiment or primary artifact) · `Experimental` (from a controlled/pre-registered study, incl. weak/underpowered/null) · `Research-supported` (multiple studies/reviews, largely observational) · `Plausible-untested` (reasoned, no direct CS evidence) · `Infeasible`.

---

## 1. How excellent CS coaches actually review demos

**1.1 — At the top level, demo review for recruitment and preparation still prioritises behaviour under pressure, mid-round reaction, initiative and decision-making over statistics.** `Research-supported` (documented practitioner statements, replicated across coaches).
kassad (Aleksandar Trifunović): *"There are dozens of more important factors when making a team… demo reviews mainly focused on seeing how the player handles high-pressure situations, how he reacts to certain situations happening mid-rounds, does he have the amount of initiative needed for his position, decision making."* He states directly: *"Stats aren't that important when choosing new players."* HLTV, "Why we're still waiting for Counter-Strike's data revolution", 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution
Also in same piece: scouting in 2024 is still done *"in much the same way it was in 2016"* — coach, IGL and org rep sieve a longlist **by watching demos** and checking references from former teammates.

**1.2 — Where data is used, it filters a longlist; the demo "eye test" still decides.** `Research-supported`.
- ash (GamerLegion coach): statistics (via Skybox) *"make the shortlist, and then from there I go through and break down if the numbers are that good, is it sustainable the way he's playing, can he fit in a system."* Found FL4MUS with a role/economy-adjusted rating filter — *"I literally had no idea who FL4MUS was."*
- DeMarsDeRover (Liquid analyst): *"The stats can help us look at a wider range of players… get us a shortlist… [Analysts] are not as experienced as the players when it came to the eye test."*
HLTV, 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution

**1.3 — The most advanced documented team workflow converts demo data into situational, not scalar, judgement: "fair duels," economy-adjusted impact, and communication.** `Research-supported` (single team, self-reported).
valens (Cloud9/EG, Major-winning coach, Stanford MSc): EG built an internal rating ("EGR") factoring *"communication, utility quantity, utility quality, mechanical skill, and how well you perform in moments that really dictate the outcome of a game."* As far back as 2019 they combined in-game data **with communication files** to analyse which players were over-calling or under-calling. Emphasis is on *"how many 'fair duels' a player wins and how often a player can make a duel 'unfair' in their favor."* HLTV, 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution
Caveat stated by valens himself: *"The majority of CS, you need to have a feel for the game."* Data is *"an enhancer, something to increase efficiency… not a miracle worker."*

**1.4 — Demo study is used to form falsifiable hypotheses about the opponent, then to call a counter mid-match — the clearest first-person example is zonic/Astralis.** `Demonstrated` (specific, verifiable case).
zonic (ESL One New York 2016, vs G2): *"I saw a couple of demos before the match where they were either explosive on B or doing the smoke line on A, and when they had done both of those, I took a timeout and said 'They're going to try and do an A split now, go short.'… And they did exactly what I thought."* HLTV, 2016-09-30 — https://www.hltv.org/news/18798/zonic-we-had-a-way-better-ct-side

**1.5 — Astralis-era preparation treated utility as drilled, rehearsed routine, not ad hoc invention.** `Research-supported` (practitioner).
Xyp9x on zonic: *"Thanks to zonic it's become a thing that we have to find spots we can double-nade"* — i.e., demo/theory work was converted into repeatable utility executions tested until reliable. HLTV, 2018-04 — https://www.hltv.org/news/23626/xyp9x-thanks-to-zonic-its-become-a-thing-that-we-have-to-find-spots-we-can-double-nade
zonic also described keeping a record of practice sessions/maps to avoid neglecting the pool ("deep playbook"). HLTV, 2019-04 — https://www.hltv.org/news/26567/zonic-we-have-a-deep-playbook-and-it-worked-out-even-if-we-had-a-bit-of-a-rocky-start

**1.6 — A documented analyst workflow separates what a demo can prove (information available, positions, comms) from what it cannot (a player's decision quality in isolation).** `Research-supported`.
ImAPet (CLG head coach) describes saturating demo review: *"I just watch a lot of demos… Sometimes I don't even sleep. I just try to get as much as I can from a demo."* He moved from pure statistics to *"breaking down their defaults and saying what will work and what won't work."* On clutches he is explicitly fatalistic: *"some players just have the better ability to clutch… All you can do is watch the VoD and try to improve on it."* HLTV, 2017-06-19 — https://www.hltv.org/news/20757/imapet-i-just-watch-a-lot-of-demos

**1.7 — Team review is increasingly run as a collaborative, personality-first process with a narrow tactical slice, not a coach monologue.** `Research-supported` (practitioner).
zews (Liquid, 2024): sessions are *"all a collaboration"*; *"Casper [cadiaN] gives a lot of the corrections mid-scrim, during tournaments we do review as a team after where everyone gives opinions."* He states he does *"20-25% of the tactical stuff"* and is mostly managing personalities. He also gives a concrete error taxonomy: per-round issues are *"just a miscommunication, over-aggression, it can be a bad whiffed duel, it can even be some strat that we were caught off guard."* HLTV, 2024-01-24 — https://www.hltv.org/news/38013/zews-interview-naf-twistzzs-growth-shaping-liquids-new-foundation-skullzs-process

**1.8 — B1ad3's documented model classifies opponents (known / new / map-specific), treats the veto as part of preparation, and separates error types (technical vs decision-making vs macro vs mindset).** `Research-supported` (practitioner, multiple interviews).
- Known opponents → update existing knowledge with recent demos rather than start from zero: *"For us as NAVI, this is the main problem, we always look for the trophy"* — https://www.hltv.org/news/34073/b1ad3-as-navi-this-is-the-main-problem-we-always-look-for-the-trophy (2023-05)
- On jL he explicitly separates *"mistakes in decision-making and macro analysis"* from mechanical error while valuing mindset: https://www.hltv.org/news/38801/b1ad3-i-didnt-expect-to-win-a-major-so-fast (2024-04)
- Bootcamp aimed at *"knowledge and material"* accumulated by a fixed five: https://www.hltv.org/news/45287/b1ad3-we-were-close-to-making-some-changes (2026)

**1.9 — The widely-circulated "review order" frameworks (macro → micro → utility; root cause before symptom; "one primary issue per review") are coaching-vendor SEO content, not validated methodology and not traceable to named pro coaches.** `Plausible-untested` — **explicitly unverified vendor content**.
Examples that all restate the same "three-pass / symptom-to-root-cause / one actionable habit" template without citation or evidence of efficacy: Boosteria — https://boosteria.org/guides/cs2-demo-review-guide-2026-analyze-gameplay-step-step ; GapTo10 — https://gapto10.com/guides/cs2-demo-review-framework/ ; Upforge — https://upforge.gg/blog/cs2-demo-review-workflow-coaching ; cs2lore — https://cs2lore.com/blog/game-mechanics/cs2-demo-review-guide (all accessed 2026-10). Treat as *what coaches claim they check*, not as evidence the ordering improves outcomes.

**1.10 — There is no peer-reviewed study of CS demo-review method efficacy (ordering, root-cause vs symptom, habit detection).** `Plausible-untested` — absence of evidence, established by searching PubMed/PMC/JSES/Collabra and finding only esports performance/expertise work, not review-methodology work. Any ordering claim should be treated as workflow preference.

---

## 2. Intent vs outcome in CS review

**2.1 — Judging a decision by its result rather than by information available at the time is a robustly demonstrated bias (outcome bias).** `Demonstrated` (experimental).
Baron, J. & Hershey, J.C. (1988), *Outcome bias in decision evaluation*, J. Pers. Soc. Psychol. 54(4):569–579. In 5 studies, subjects rated the **same** decision process as better when it turned out well, even though they were told the decision-maker had all relevant information. Crucially: *"subjects who were asked felt that they should not consider outcomes in making these evaluations, [but] they did so."* PMID 3367280 — https://pubmed.ncbi.nlm.nih.gov/3367280/ ; DOI 10.1037/0022-3514.54.4.569

**2.2 — Applying outcome-bias correction to CS demo review ("that was right even though you died") is a reasoned transfer from decision science, not something demonstrated in CS.** `Plausible-untested`.
No CS-specific study of outcome/hindsight bias in demo review was found. Coaching-vendor guides assert the principle ("a good decision can produce a bad outcome") without evidence, e.g. rankrise https://rankrise.net/cs2-demo-review and Gapto10 https://gapto10.com/guides/cs2-demo-review-framework/ (accessed 2026-10) — **unverified vendor content**. The closest legitimate CS-adjacent statement is a racing-strategy piece arguing decision quality must be judged ex ante (McLaren/FXPro, Randeep Singh) — https://www.mclaren.com/racing/partners/fxpro/race-strategy-randeep-singh/ — not CS evidence.

**2.3 — Coaches do verbalise a process-over-result standard, but implicitly rather than as a formal rule.** `Research-supported` (practitioner statements).
kassad weights "decision making" as a scouted attribute independent of outcome (HLTV 2024-10-28, URL above). zews frames losses as a "learning curve": *"13-11, 13-0, we went for the win, we got it"* and separates *miscommunication / over-aggression / whiffed duel* as distinct causes rather than treating a lost round as one verdict (HLTV 2024-01-24, URL above). ImAPet separates "clutch ability" (variance) from reviewable faults (HLTV 2017, URL above).

**2.4 — Elo/rating systems that score by win-probability *change* operationalise an ex-ante version of intent-vs-outcome, but are themselves unvalidated against decision quality.** `Plausible-untested`.
Leetify credits a kill by *"the Change in Win Probability"* given economy, players alive and which side got the previous kill — see finding 5.1. This evaluates *contribution*, not whether the player's *choice* was correct given only their information; a well-chosen util/rotation with no kill earns nothing. No validation that WP-delta tracks decision quality exists.

---

## 3. Aim-specialist vs pro-player vs analyst perspectives

**3.1 — Aim communities decompose "aim" into trainable sub-skills (clicking/flipping/tracking/switching; static vs dynamic) and rank players by benchmark performance.** `Demonstrated` (artifact); efficacy `Plausible-untested`.
AIMER7's workout routines guide (the canonical community document; 449 Steam ratings) — https://steamcommunity.com/sharedfiles/filedetails/?id=1679977919 (PDF mirrors: https://github.com/SqixOW/Aim_Docs_Translator). It is a practitioner document; it contains no controlled evidence of in-game transfer.

**3.2 — Voltaic's benchmark "energy" system is a designed aggregation of sub-category percentiles, not a measured skill construct.** `Demonstrated` (methodology documented); validity `Plausible-untested`.
Ranks are obtained via an "energy" score with the final rank determined by the **harmonic mean** of subcategory scores; categories below a threshold don't bottleneck the whole ("we noticed players were being bottlenecked by some of their weaknesses"). Ranks reset each season. Voltaic, *KovaaKs Benchmarks — Season 4*, 2022-04-09 — https://voltaic.medium.com/voltaic-kovaaks-benchmarks-season-4-35f3e3fb7512 ; current benchmarks https://app.voltaic.gg/benchmarks . No external validation that Voltaic rank predicts in-game duel outcomes was found.

**3.3 — KovaaK's is a high-reliability measurement platform for isolated shooting tasks, but the authors explicitly warn against reading its scores as match performance.** `Experimental` (pilot, n=10).
Rogers, Trotter, Johnson, Desbrow, King (2024), *KovaaK's aim trainer as a reliable metrics platform… : a pilot study*, Front. Sports Act. Living 6:1309991. ICC for accuracy/hits-per-second 0.947–0.995. Authors caution extrapolation is uncertain because real FPS play *"includes movement, positioning, game awareness, stress, target uncertainty, weapon mechanics, and other cognitive demands absent from isolated aim tasks."* PMID 38469227 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10925653/

**3.4 — Large-scale Aim Lab data shows real, measurable motor-acuity learning in the trainer, with non-linear, saturating returns.** `Research-supported` (N=7174, observational).
Listman, Tsay, Kim, Mackey, Heeger (2021), *Long-Term Motor Learning in the "Wild" With High Volume Video Game Data*, Front. Hum. Neurosci. 15:777779. Motor acuity (hits/sec) improved considerably over months with 40–60% day-to-day retention; hit-rate (accuracy) improved only modestly. Learning rate was *"a non-linear function of baseline performance level, amount of daily practice, and… days between practice sessions"* and *"the greatest improvements in motor acuity were evident with about an hour of practice and 90% of the learning benefit was achieved by practicing 30 min per day."* PMCID PMC8720934 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8720934/

**3.5 — Motor acuity (skill) can be measured independently of a player's chosen speed–accuracy strategy — a tool aim specialists use that demo stats cannot replicate.** `Experimental`.
Donovan, Saul, DeSimone, Listman, Mackey, Heeger (2022), *Assessment of human expertise and movement kinematics in first-person shooter games*, Front. Hum. Neurosci. 16:979293. Shows pro/semi-pro kinematics depend on task demand (faster, more "swipey" when speed is incentivised) and that motor acuity requires measuring the speed–accuracy trade-off across multiple conditions, since "skill and strategy would be confounded" from a single data point. Copycat finding: performance across target sizes was *"poorly characterized by Fitts Law."* PMID 36523441 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9744923/

**3.6 — The one frequently-cited aim-trainer transfer study is extremely weak.** `Experimental` (n=6, no control).
Roldan & Prasetyo (2021), *Evaluating the Effects of Aim Lab Training on Filipino Valorant Players' Shooting Accuracy*, IEEE ICIEA, pp. 465–470. Six players, ~6 min/day for one week; **average damage per round** improved (p≈0.029), while KAD, K/D, headshot % and score-per-round were **not** significant; only 1/6 improved headshot %. DOI 10.1109/ICIEA52957.2021.9436822 — https://ieeexplore.ieee.org/abstract/document/9436822

**3.7 — A pre-registered study found no transfer of action-FPS training to low-level visual discrimination.** `Experimental` (registered report, null).
Yeh, Li, Huang, Liu (2024), *Comparing conventional and action video game training in visual perceptual learning*, Sci. Rep. 14:27864 (published 2024-11-13; n=65 + 18 controls; 20 h training). *"Our study found no evidence, in either accuracy or reaction time, that AVG training transferred to motion discrimination"*; improvement was comparable to no-training control and less than matched training. DOI 10.1038/s41598-024-71987-y — https://www.nature.com/articles/s41598-024-71987-y

**3.8 — A commonly-recommended aiming instruction (external vs internal focus) failed to produce a significant effect in Aim Lab.** `Experimental` (null).
Lamers James & O'Connor (2023), *Impact of focus of attention on aiming performance in the first-person shooter videogame Aim Lab*, PLOS ONE 18(7):e0288937 (2023-07-25). External-focus mean 13.15 vs internal 12.87, F(1,35)=0.73, p=.397, ηp²=.02; experience did not moderate the effect. PMCID PMC10368276 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10368276/

**3.9 — Analyst/coach and aim-specialist views genuinely diverge on what matters, and the divergence is documented rather than folkloric.** `Research-supported`.
Same org piece has valens arguing data is an enhancer and that *"the majority of CS, you need to have a feel for the game,"* while DeMarsDeRover (data analyst) states the opposite methodological stance — *"I didn't play the game at all"* — and doubts the efficiency of hiring data staff (*"These skills do not overlap"*). Meanwhile aim communities measure isolated mechanics with no model of decision quality. HLTV, 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution

---

## 4. Why strong aim plateaus

**4.1 — At professional level, accumulated practice quantity explains very little of tournament performance; practice-quality proxies (practice K/D, practice score) do the work, and team membership explains a large share.** `Research-supported`.
Pluss, Novak, Bennett, Panchuk, Coutts, Fransen (2021), *The relationship between the quantity of practice and in-game performance during practice with tournament performance in esports: An eight-week study*, J. Sport Exerc. Sci. 5(1):69–76. 43 pro CS:GO players (PGL Major Krakow 2017); average ~32 h/week practice. Final model R²=0.30; per SD increase in practice K/D → +7.94% tournament score; practice quantity had *"limited association"*. Authors note the random effect (team) explained much variance. https://jses.net/wp-content/uploads/2021/02/Pluss-et-al.-2021.pdf ; DOI 10.36905/jses.2021.01.09

**4.2 — Perceptual-motor abilities distinguish professionals from non-players but poorly distinguish professionals from committed recreational players — evidence for a selection/ceiling effect, not a training-key effect.** `Research-supported`.
Pluss et al. (2020), *Perceptual-motor Abilities Underlying Expertise in Esports*, J. Expertise 3(2):133–143. 75 participants (25 pro / 25 rec / 25 control). Pro players were *"less susceptible to the speed-accuracy trade-off"* and had faster two-choice and precue response times than controls, but the authors conclude *"their ability to distinguish between professional and recreational esports players is limited."* https://www.journalofexpertise.org/articles/volume3_issue2/JoE_3_2/JoE_3_2_Pluss_etal.pdf

**4.3 — Motor-learning gains are specific to the conditions and feedback present during training, which is a mechanistic reason isolated aim drills fail to transfer.** `Demonstrated` (experimental, foundational motor-learning result).
Proteau, Marteniuk & Lévesque (1992), *A sensorimotor basis for motor learning: evidence indicating specificity of practice*, Q. J. Exp. Psychol. A. Practice builds a sensorimotor representation tied to the sensory/feedback conditions of training; changing visual feedback or movement constraints degrades performance. PMID 1631322 — https://pubmed.ncbi.nlm.nih.gov/1631322/ ; and *Specificity of practice results from differences in movement planning strategies* (Mackrous & Proteau), PMID 17618424 — https://pubmed.ncbi.nlm.nih.gov/17618424/

**4.4 — The clearest documented differences between esports experts and amateurs are in spatial cognition and attention, i.e. perception/decision factors rather than raw motor speed.** `Research-supported` (meta-analysis; largely cross-sectional).
Miao, He, Hou, Wang, Chi (2024), *Cognitive expertise in esport experts: a three-level model meta-analysis*, PeerJ 12:e17857 (2024-08-07). 15 studies, 142 effect sizes, 1,085 participants: overall g=0.373 (p=.012); spatial cognition g=0.822 (p<.001). Authors stress the evidence is *"largely correlational"* and domain-specific abilities such as *"anticipation, tactical decision-making and in-game information integration"* are underrepresented in the literature. PMCID PMC11316462 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11316462/

**4.5 — Diminishing returns are built into the learning curve: improvements are non-monotonic, and better baselines gain less for the same effort.** `Research-supported`.
Listman et al. 2021 (finding 3.4) — *"the benefit of additional practice on any given day was non-monotonic"* and learning rate varied inversely with baseline. PMCID PMC8720934 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8720934/
Caution: this is a trainer task (Aim Lab Gridshot), not CS2 match play.

**4.6 — Review-level critiques of the broader "video games improve cognition" literature warn of publication bias and overclaimed far transfer.** `Research-supported` (methodological critique).
Hilgard, Sala, Boot, Simons (2019), *Overestimation of action-game training effects: Publication bias and salami slicing*, Collabra: Psychology 5(1):30 — cited by Yeh et al. 2024 as a reason for rigorous pre-registration (URL in finding 3.7). This directly undercuts vendor claims of broad aim-trainer benefit.

**4.7 — There is no peer-reviewed study testing whether aim-trainer volume raises CS2/FACEIT rank or match impact at high Elo.** `Plausible-untested` (absence established by search; no adequately powered, pre-registered transfer trial found).

---

## 5. Existing CS2 demo-analysis tooling as of 2026 — what is verifiable vs marketing

**5.1 — Leetify Rating's mechanism is fully documented: zero-sum, win-probability-weighted, with fixed kill-credit splits.** `Demonstrated` (vendor method docs; underlying model unpublished).
Rating = average per-round rating; per-round rating from **change in win probability** given economy tier, players alive, and which side got the last kill. Kill credit split: **35% killer / 30% all damage-dealers / 15% flash assist / 20% traded death** (scaled up if a component is absent); death penalty falls only on the person who died. Saving is rewarded by next-round win-probability gain. WP priors trained on HLTV CS2 data. Leetify, *How does Leetify Rating actually work?*, 2024-11-25 — https://leetify.com/blog/leetify-rating-explained/
Verifiable: the method is stated. Unverifiable: the WP model itself and whether it measures "skill" (Leetify itself says *"Leetify Rating is a performance metric, not a skill metric"*).

**5.2 — Leetify's Aim/Utility/Positioning Ratings are z-scores against playerbase benchmarks that drift; they were reset in 2024 and are explicitly relative.** `Demonstrated` (vendor docs, with own caveats).
Aim Rating averages 50 across the playerbase; the 2024-03-27 recalibration moved an **unchanged raw score to a lower rating** because the playerbase improved over 2.5 years. All Aim-tab stats are equally weighted except `Accuracy (All Shots)` (excluded). Leetify, *Updated Benchmarks for CS2*, 2024-03-27 — https://leetify.com/blog/cs2-benchmarks/ ; glossary — https://leetify.com/blog/leetify-stats-glossary/
Implication for any local tool: benchmark-derived ratings are not comparable across time or populations.

**5.3 — Scope.gg computes a broad, partly disclosed metric set including TTK, first-bullet accuracy, and utility metrics; composite formulas are proprietary.** `Demonstrated` (product pages); improvement claims `Plausible-untested` vendor marketing.
Documented outputs: K/D, ADR, KAST, KPR, HLTV Rating 2.1, time-to-kill, accuracy, **first-bullet accuracy**, hit-based HS%, grenade damage, flash time/smoke usage, opening duels, clutches, plus a 2D replay viewer and "mistakes/highlights." https://scope.gg/ (accessed 2026-10); method explanation https://blog.scope.gg/scopegg-cs2-en/ . Proprietary composite ratings are *not* documented as formulas — treat as platform scores, not universal CS2 ratings.

**5.4 — csstats.gg is a Valve-matchmaking history tracker (entry kills, trades, clutches, round outcomes), not a coaching engine.** `Demonstrated` (product). https://csstats.gg/ (accessed 2026-10). Explicitly scoped to official Competitive/Premier games.

**5.5 — HUDstats is esports/broadcast data infrastructure, not consumer coaching.** `Demonstrated`. Its CS data model is killed/deaths/assists/HS%/damage per round/high-value kills/team win rate/T-CT round wins, delivered as dashboards/overlays/feeds for tournaments and broadcasters. https://hudstats.com/data-feeds/ ; https://hudstats.com/storytelling-dashboard/ (accessed 2026-10).

**5.6 — TotalCS is a reference/wiki tool (commands, binds, callouts, crosshairs), not match analytics.** `Demonstrated`. https://totalcsgo.com/ (accessed 2026-10).

**5.7 — The open-source analysis stack is mature and the parsing work is broadly solved.** `Demonstrated` (repository source).
- **awpy** — CS2 demo parser in Rust, Python/Polars API; datasets for rounds, kills, damages, bomb, grenades/fires/smokes, shots (`weapon_fire` + active-weapon state/clip/inaccuracy/scoped), blinds, item events, stats, economy, chat, and per-tick **snapshots** (position, eye angles, health, armour, economy, loadout). https://github.com/pnxenopoulos/awpy (README, accessed 2026-10)
- **demoparser2** — Rust core, Python/JS/WASM; query-style API (`parse_event`, `parse_ticks`); extremely detailed networked-field list (view angles pitch/yaw, `spotted`, `approximate_spotted_by`, `is_scoped`, `m_bIsDefusing`, velocity, weapon state, etc.). https://github.com/LaihoE/demoparser
- **CS Demo Manager** — open-source desktop organizer/analyser for demos. https://github.com/akiver/cs-demo-manager ; https://cs-demo-manager.com/docs

**5.8 — A wave of 2025–2026 "AI coach" products exists; stated methods are demo parsing plus heuristics/ML; none publish peer-reviewed validation.** `Plausible-untested` — vendor claims.
Examples: smartCoach https://smartcoach.gg/ ("Find the rounds that cost the match… linked evidence"); CSReplays https://csreplays.com/ ; cs2demoanalysis https://cs2demoanalysis.com/ ; PlayFix https://playfix.pro/ ; Laggone https://laggone.com/ ; vStreet https://vstreet.gg/ ; Game Demon https://www.altrosstudios.games/gamedemon/ (all accessed 2026-10). Note smartCoach's own positioning ("Find the rounds that cost the match") implicitly adopts a results/impact framing rather than an intent framing.

**5.9 — Refrag Coach is the most concrete "metrics → targeted drills" product, but its metrics are outcome proxies with acknowledged confounds and no published validation.** `Plausible-untested` — vendor.
Claims per Refrag: headshot %, **counter-strafe %**, **crosshair placement reported as degrees of deviation**, recoil-control accuracy, spotted accuracy, time-to-kill, time-to-damage, plus general/utility/entry-trade stats; recommends Prefire/Quickfire/Recoil/Angle/Repeek drills. https://refrag.gg/blog/what-is-refrag-coach/ ; sessions tracking https://refrag.gg/blog/introducing-sessions-a-new-era-of-cs2-training-on-refrag/ . No independent validation that a lower "crosshair-placement degrees" or faster TTD produces rank improvement; TTD conflates aim, weapon, range, target movement and engagement selection.

**5.10 — "Skybox" is the commercial analyst tool cited by a Major-level coach, and is built for opponent research (round trends, veto sim, per-position leaderboards), not individual coaching.** `Demonstrated` (named use) — HLTV, 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution

---

## 6. Known limits of demo-derived analysis in CS2

**6.1 — A demo is a network/replay stream, not a video or full input capture.** `Demonstrated` (source).
The CS2 `usercmd` protobuf defines `CBaseUserCmdPB` with `buttons_pb`, `viewangles`, `forwardmove`/`leftmove`/`upmove`, `impulse`, `weaponselect`, `mousedx`/`mousedy`, `random_seed`, and `repeated CSubtickMoveStep subtick_moves` (`button`, `pressed`, `when`, `analog_forward_delta`, `analog_left_delta`, `pitch_delta`, `yaw_delta`). Source: SteamTracking/GameTracking-CS2 `Protobufs/usercmd.proto` — https://github.com/SteamTracking/GameTracking-CS2/blob/master/Protobufs/usercmd.proto

**6.2 — Voice chat is not stored in Valve matchmaking demos, and never has been.** `Demonstrated`.
The CS2VoiceData extractor project exists precisely because voice extraction requires the audio to be present in the file, which Valve MM demos do not contain — https://github.com/DandrewsDev/CS2VoiceData . Community documentation states console vars (`tv_listen_voice_indices`) only surface voice already inside the demo and cannot add it — https://vredux.com/articles/cs2-demos-guide . Implication: comms must come from a separate OBS/ShadowPlay capture; any tool claiming to analyse team communication from a Valve demo is fabricating it.

**6.3 — Since Valve's 2026-09-09 update, team chat inside demo files is encrypted and unreadable to external parsers.** `Demonstrated` (secondary reporting of Valve patch notes; flagged).
Per reporting of the 2026-09-09 patch: *"team chat inside a demo file is encrypted and does not show up at all… A third party parser reading the file will not get it."* Global chat remains visible only in the in-game watch UI. esblitz, 2026-09-13 — https://esblitz.com/en/news/cs2-patch-demo-chat-cache (citing Valve's Steam patch notes, store.steampowered.com/news/app/730). Valve's own patch notes are the authoritative source and should be re-checked; this is a hard blocker for chat-based analytics built on 2026+ demos.

**6.4 — CS2's sub-tick architecture timestamps actions *within* server-update intervals; Valve claims tick rate no longer matters for movement, shooting and grenades — but Valve has never published the algorithm.** `Demonstrated` (Valve claim) + `Plausible-untested` (exact reconstruction).
Valve, "Moving Beyond Tick Rate" (CS2 announcement, 2023-03-22) and the CS2 features page: *"Thanks to Counter-Strike 2's sub-tick update architecture, servers know the exact instant that motion starts, a shot is fired, or a 'nade is thrown… regardless of tick rate, your moving and shooting will be equally responsive and your grenades will always land the same way."* https://www.counter-strike.net/cs2/features ; announcement https://www.counter-strike.net/cs2 . Valve has not documented how each case (interpolation, lag compensation) is reconstructed, so per-tick reconstruction of "exactly what happened" is approximate by construction.

**6.5 — "Tick" is ambiguous: server ticks, demo frames and sub-tick steps are different clocks; parsers must read the tick interval from the file rather than assume 64/128.** `Research-supported` (community tooling docs).
CS2DemoKit documents the demo/frame tick vs absolute server tick distinction and warns that mixing them yields plausible-looking wrong timings — https://github.com/CS2OpenDev/CS2DemoKit . Valve MM runs 64 Hz with sub-tick; FACEIT runs 128-tick CS2 servers — https://www.reddit.com/r/GlobalOffensive/comments/16dzr34/faceit_is_indeed_running_128_tick_servers_as_seen/

**6.6 — The recorded command stream is not the raw human input stream: commands are delta-compressed and the server may execute substitute commands.** `Research-supported` (tooling docs).
CS2DemoKit: modern demos may store user commands as deltas against the previous command (`svc_UserCmds`), so naïvely reading only the full `data` field *"can report missing or stale buttons, movement, and subtick values"*; reconstruction requires per-player baselines. It also notes the server can execute substitute commands when a client command is late, so an apparent command is not always fresh physical input. https://github.com/CS2OpenDev/CS2DemoKit . Consequence: mouse-delta-derived "flick" or "crosshair placement" metrics are indirect and can be corrupted by incorrect command reconstruction.

**6.7 — Fog-of-war ("what this player actually saw") is only approximately reconstructable; the demo gives positions and a spotting mask, not rendered views.** `Demonstrated` (fields) + `Plausible-untested` (perception modelling).
Available per-tick fields include X/Y/Z, `pitch`/`yaw` (eye angles), and — critically — `spotted` (`m_bSpotted`) and `approximate_spotted_by` (`m_bSpottedByMask`) — demoparser2 field list, https://github.com/LaihoE/demoparser . The demo does **not** store the player's actual screen: FOV, occlusion by smoke geometry, rendered-frame timing, or what the client predicted. Any "fog of war is reconstructable per tick" claim must specify it is a raycast/visibility *inference* from state, not ground truth.

**6.8 — Sound cues are not stored as audio; they must be inferred from events and positions.** `Plausible-untested` (no primary doc found stating the demo stores an audio stream; demoparser/awpy field lists contain no audio events).
Practical position: footsteps/reloads/firing can be *approximated* from `weapon_fire`, movement and position data, but the demo contains no audio stream and no server-side "who heard what" record.

**6.9 — Utility/vision effects are partially recorded (smoke and fire lifetimes, blind events), which allows some visibility modelling but not full line-of-sight.** `Demonstrated` (fields).
awpy exposes `smokes` and `fires` as one row per deployed cloud/burning inferno with position, thrower and `[start_tick, end_tick]`, and `blinds` with thrower, blinded player and duration — https://github.com/pnxenopoulos/awpy (README). This is enough to model smoke walls as timing/geometry, not as rendered occlusion.

**6.10 — Player-position fidelity is per-tick interpolated state, so sub-tick micro-actions (exact counter-strafe instant, exact peek start) are not directly observable.** `Plausible-untested`.
Derived from 6.4–6.6: positions and angles are sampled at server ticks; sub-tick steps carry fractional timing but the demo does not give a continuous reconstruction of the player's motion between updates. Any claim of "frame-accurate" movement/peek analysis exceeds what the format supports.

---

## Contradictions / open questions

1. **Stats vs eye test is an unresolved, live disagreement inside the industry.** kassad: *"Stats aren't that important."* ash and (formerly) valens build data pipelines; DeMarsDeRover explicitly doubts the value of hiring data staff ("These skills do not overlap"). HLTV 2024-10-28. Which approach produces better outcomes is not measured.
2. **Do aim trainers transfer at high Elo?** No adequately powered, pre-registered trial exists comparing "aim trainer + normal play" vs "normal play" on CS2 rank/duel outcomes. The only transfer datapoint is a 6-person, 1-week Valorant study; a pre-registered 20-h study found **no** transfer to low-level visual discrimination. Vendor and community claims are unvalidated.
3. **Are high-Elo gains decision-limited or mechanic-limited?** Pluss 2020 (pro vs recreational perceptual-motor differences are limited) and Miao 2024 (spatial cognition is the largest expert/amateur difference) both point to decision/perception, but both are largely cross-sectional (self-selection risk) and neither measured CS2 match play.
4. **Every consumer "rating"/"aim score" is relative and drifts.** Leetify had to reset Aim Rating to 50 in 2024 because 2.5 years of playerbase improvement moved unchanged raw scores. Benchmark-derived measures are not comparable over time.
5. **No public, validated measure of "decision quality" exists.** Leetify Rating is win-probability-delta (impact, not intent); Refrag's TTK/TTD/crosshair-degrees conflate aim with engagement selection; Scope's composite formulas are undisclosed.
6. **Outcome bias is demonstrated in the lab but untested in CS review.** The transfer is a reasonable inference, not an established coaching effect. No study shows that outcome-blind review improves player performance.
7. **Demo integrity limits are moving.** Voice was never recorded; team chat became encrypted by default in the 2026-09-09 update. Any coaching product's feature set must be re-validated against the current patch, and any chat-analytics feature built on 2025 data is now broken.
8. **"Fog of war reconstructable per tick" is frequently asserted but is an inference**, constrained by missing rendered frames, FOV, and audio. The `spotted`/`m_bSpottedByMask` fields are the closest thing to ground truth vision and are themselves only a radar-spot mask, not a full visibility model.

---

## Top sources

**Peer-reviewed / primary research**
1. Baron & Hershey (1988), *Outcome bias in decision evaluation*, JPSP 54(4):569–579 — https://pubmed.ncbi.nlm.nih.gov/3367280/
2. Listman, Tsay, Kim, Mackey, Heeger (2021), *Long-Term Motor Learning in the "Wild"…*, Front. Hum. Neurosci. 15:777779 — https://pmc.ncbi.nlm.nih.gov/articles/PMC8720934/
3. Rogers et al. (2024), *KovaaK's aim trainer as a reliable metrics platform…*, Front. Sports Act. Living 6:1309991 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10925653/
4. Donovan et al. (2022), *Assessment of human expertise and movement kinematics in FPS games*, Front. Hum. Neurosci. 16:979293 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9744923/
5. Yeh, Li, Huang, Liu (2024), *Comparing conventional and action video game training in visual perceptual learning* (Registered Report), Sci. Rep. 14:27864 — https://www.nature.com/articles/s41598-024-71987-y
6. Lamers James & O'Connor (2023), *Impact of focus of attention… Aim Lab*, PLOS ONE 18(7):e0288937 — https://pmc.ncbi.nlm.nih.gov/articles/PMC10368276/
7. Roldan & Prasetyo (2021), *Evaluating the Effects of Aim Lab Training…*, IEEE ICIEA — https://ieeexplore.ieee.org/abstract/document/9436822
8. Pluss et al. (2021), *…quantity of practice and in-game performance… tournament performance*, JSES 5(1):69–76 — https://jses.net/wp-content/uploads/2021/02/Pluss-et-al.-2021.pdf
9. Pluss et al. (2020), *Perceptual-motor Abilities Underlying Expertise in Esports*, J. Expertise 3(2) — https://www.journalofexpertise.org/articles/volume3_issue2/JoE_3_2/JoE_3_2_Pluss_etal.pdf
10. Miao, He, Hou, Wang, Chi (2024), *Cognitive expertise in esport experts: a three-level model meta-analysis*, PeerJ 12:e17857 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11316462/
11. Proteau et al. (1992), *A sensorimotor basis for motor learning: specificity of practice*, PMID 1631322 — https://pubmed.ncbi.nlm.nih.gov/1631322/

**Practitioner / first-person (CS)**
12. HLTV, *Why we're still waiting for Counter-Strike's data revolution*, 2024-10-28 — https://www.hltv.org/news/40128/why-were-still-waiting-for-counter-strikes-data-revolution
13. HLTV, *zonic: "We had a way better CT side"*, 2016-09-30 — https://www.hltv.org/news/18798/zonic-we-had-a-way-better-ct-side
14. HLTV, *ImAPet: I just watch a lot of demos*, 2017-06-19 — https://www.hltv.org/news/20757/imapet-i-just-watch-a-lot-of-demos
15. HLTV, *zews interview…*, 2024-01-24 — https://www.hltv.org/news/38013/zews-interview-naf-twistzzs-growth-shaping-liquids-new-foundation-skullzs-process
16. HLTV, B1ad3 interviews — https://www.hltv.org/news/38801/ ; https://www.hltv.org/news/45287/ ; https://www.hltv.org/news/34073/

**Official / technical (Valve, repos)**
17. Valve, CS2 "Moving Beyond Tick Rate" features — https://www.counter-strike.net/cs2/features ; https://www.counter-strike.net/cs2
18. CS2 `usercmd.proto` — https://github.com/SteamTracking/GameTracking-CS2/blob/master/Protobufs/usercmd.proto
19. awpy (CS2 parser) — https://github.com/pnxenopoulos/awpy
20. demoparser2 — https://github.com/LaihoE/demoparser
21. CS2DemoKit (demo timing/user-command caveats) — https://github.com/CS2OpenDev/CS2DemoKit
22. CS2VoiceData — https://github.com/DandrewsDev/CS2VoiceData
23. CS Demo Manager — https://github.com/akiver/cs-demo-manager

**Vendor (method claims only; not evidence of efficacy)**
24. Leetify Rating explained — https://leetify.com/blog/leetify-rating-explained/ ; CS2 benchmarks — https://leetify.com/blog/cs2-benchmarks/
25. Scope.gg — https://scope.gg/ ; csstats.gg — https://csstats.gg/ ; HUDstats — https://hudstats.com/data-feeds/ ; TotalCS — https://totalcsgo.com/
26. Refrag Coach — https://refrag.gg/blog/what-is-refrag-coach/ ; Voltaic benchmarks — https://voltaic.medium.com/voltaic-kovaaks-benchmarks-season-4-35f3e3fb7512 , https://app.voltaic.gg/benchmarks ; AIMER7 guide — https://steamcommunity.com/sharedfiles/filedetails/?id=1679977919

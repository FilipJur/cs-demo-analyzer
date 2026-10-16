# Casebook — Traceable Review Cases (`EVAL-001`–`EVAL-011`)

Research only. Every case separates **observed facts → plausible interpretation → alternative explanation → supporting evidence → contradictory evidence → judgment eligibility**. Intent/comms speculation is never stated as fact. Expert-reviewed cases carry revisit information; researcher-created hypotheticals are labelled `HYPOTHETICAL` with the footage that would confirm them. Disagreement is preserved, not resolved.

Required-type coverage: reasonable-bad-outcome (`EVAL-001`, `EVAL-008`); questionable-good-outcome (`EVAL-002`, `EVAL-009`); basic mechanical mistake (`EVAL-003`); tactical with insufficient evidence (`EVAL-004`); role-dependent (`EVAL-005`); awareness ambiguity (`EVAL-006`); coordination ambiguity (`EVAL-007`); multi-round repeated behavior (`EVAL-010`, `EVAL-011`).

---

## EVAL-001 — Reasonable play, bad outcome: gun-round conversion lost to a force-buy heroics round

**Type:** reasonable play with a bad outcome. **Status:** expert-reviewed (secondary reportage; HLTV body rate-limited on access date).

- **Observed facts:** At IEM Cologne Major 2026, Vitality lost a map to the eventual champions despite, in analyst Mauisnake's grading, B/B-minus play by their own standards; two lost rounds came from being "ecoed" — dropping gun rounds to Falcons pistols. Revisit: Skin.Club exclusive interview with Mauisnake, 2026-06-26 (`community.skin.club/en/news/iem-cologne-2026-major-might-be-the-best-cs2-major-ever-mauisnake-exclusive-interview`).
- **Plausible interpretation:** Vitality's process was fine at the decision level; the map loss is substantially variance (low-probability opponent conversions in eco rounds), not a systemic defensive failure.
- **Alternative explanation:** Vitality's anti-eco setups were genuinely sloppy two rounds running — a repeatable setup flaw, not variance.
- **Supporting evidence:** Mauisnake's verbatim eco-round accounting ("They would have won that map if they were able to convert on their first gun round against Falcons' pistols"); his normalization of opponent heroics ("that's just going to happen against Falcons… that's just Counter-Strike"). **Demonstrated** (verbatim analyst quote, primary interview).
- **Contradictory evidence:** Two eco concessions in one map is at the upper edge of "variance" — a second analyst could reasonably demand the anti-eco setup demos before filing both under luck. No second review retrieved; disagreement space recorded, not filled.
- **Judgment eligibility:** SUPPORTED as "process survived, outcome failed" at the map level. Any per-round verdict (which anti-eco decision failed) is WITHHELD without the setup demos + info states.

## EVAL-002 — Questionable play, good outcome: the iconic isolation that must not become policy

**Type:** questionable play with a good outcome. **Status:** expert-reviewed praise-of-fact; process grade explicitly withheld.

- **Observed facts:** coldzera, Mirage, MLG Columbus 2016 semifinal vs Liquid: jumping AWP double kill from an isolated aggressive position; plus-84 event plus-minus; universally iconic. Revisit: HLTV "Video: coldzera highlights" (`hltv.org/news/18511/video-coldzera-highlights`); ESPN retrospective ("The best ever?").
- **Plausible interpretation:** an isolated aggressive fight outside trade coverage — low-probability line that happened to connect.
- **Alternative explanation:** a calculated anti-eco/anti-default read exploiting a known Liquid timing — correct, not lucky.
- **Supporting evidence:** praise-fact is **Demonstrated** (highlight reels, stature coverage). No analyst process-grading found.
- **Contradictory evidence:** none on the facts; the dispute is policy-level (fans praise the outcome; no credible coach recommends the line as repeatable).
- **Judgment eligibility:** WITHHELD on process. Highlight selection is survivorship-biased by construction. Teaching value: Q2 in Duke's matrix — won *despite* the decision class, must be flagged in review precisely because the outcome tempts repetition. Same structure: s1mple's Cache 1v4 vs CLG, ESL One Cologne 2016 era (HLTV `news/17465/video-s1mple-vs-clg`) — praised universally, questionable as policy.

## EVAL-003 — Genuine basic mechanical mistake: the separable miss

**Type:** basic mechanical mistake. **Status:** expert-reviewed method with verbatim separability test.

- **Observed facts (method-level):** Xela/Dignitas (2017, primary full text read): players reviewing own demos are "quick to blame deaths on a mechanical mistake" — the article redirects to precursor questions first. Revisit: `team-dignitas.net/articles/Blogs/CSGO/11748/top-3-tips-for-watching-demos` (2017-10-20).
- **Plausible interpretation:** fight selection correct (had to take the fight, gave best chance), execution failed → mechanics bucket (aim/punishment, e.g. counter-strafe state, spray control).
- **Alternative explanation:** the "miss" was actually a correct decision with unavoidable variance (spread RNG, penetration, target volume assumed — no hitbox data in demos) or a forced shot under trade cover where any damage was bonus.
- **Supporting evidence:** Xela's separability test is **Demonstrated** (verbatim). Mechanical measures exist: per-shot velocity fraction (Leetify 34%-of-max-speed convention), `m_fAccuracyPenalty` engine state, angular error at first visibility — all engine-field grounded (prior-slice D inventory).
- **Contradictory evidence:** per-event mechanical-vs-decision attribution without annotation is **Infeasible** (prior-slice MECH notes) — the buckets must be kept as separate findings, never merged into one "mistake".
- **Judgment eligibility:** SUPPORTED as mechanics finding only when fight selection is independently cleared; otherwise WITHHELD pending precursor analysis. Never "you threw" — "execution failed inside a correct decision" or "ungraded until precursor is graded".

## EVAL-004 — Potential tactical mistake with insufficient evidence: the unjudgeable rotation

**Type:** tactical mistake with insufficient evidence. **Status:** expert-attested withhold (the hally datum).

- **Observed facts:** A CT anchor holds through first-contact utility and arrives "late" to the hit site; omniscient replay shows the hit developing while he stays. Revisit anchor: Spirit coach hally, BLAST.tv 2024-08-10 (`blast.tv/article/hally-its-good-donk-understands-he-lacks-discipline`).
- **Plausible interpretation:** late rotation — failed to convert sound/bomb-spotted tells into movement; arrival-time math shows he could have made the retake window.
- **Alternative explanation:** disciplined fake-patience — the "hit" showed no bomb/commit tells at decision time; staying was the base-rate-correct play and the eventual hit was fast *after* his decision window closed.
- **Supporting evidence:** omniscient positions + timer + arrival math (recorded/computed). **Demonstrated** as facts.
- **Contradictory evidence:** hally's verbatim withhold — *"Some of the movements can't be judged even by watching demos because you need to hear the flow of communication"* (**Demonstrated**). The rotator's heard/seen set (sound radii estimated, perception unrecorded, voice absent) is the load-bearing premise and is missing.
- **Judgment eligibility:** WITHHELD (abstention criteria 1, 2). Output format: T0 facts (positions, timer, arrival delta) + missing premise (listener info set + comms) + criteria fired. Fake-patience and late rotation are observationally identical without that premise.

## EVAL-005 — Role-dependent action: the untraded lurker death

**Type:** role-dependent action that looks wrong when role is ignored. **Status:** expert-reviewed structural framing.

- **Observed facts:** A T-side player dies deep in Donut/ Apartments with zero teammates within trade range; killfeed shows an isolated death; team loses the round. Structural revisit: HLTV "How trading stats can show a team's structure" (`hltv.org/news/35389` — snippet **Demonstrated**, body rate-limited): *"If a player is lurking or aggressively searching ahead of the rest of their team, they are less likely to both be traded or to trade a teammate."* HLTV Attributes (`news/39672`, snippet): high-entry/low-trade = "supportive sacrificial entry"; inverse = "trademark baiter".
- **Plausible interpretation:** correct lurk — late-map split pressure punishing rotations; death is the role's structural cost, priced into the execute's equity.
- **Alternative explanation:** lost lurk — drifted into a dead zone with no path to affect the round (teammates execute opposite site, 15 s left, no arrival math); dies to a flank-watch saving nothing.
- **Supporting evidence:** role-structural framing is **Demonstrated** (HLTV's own words); the called plan + arrival-time math would separate the readings.
- **Contradictory evidence:** the demo alone cannot distinguish "lurk" from "lost" — the called plan came via voice (**unsupported**).
- **Judgment eligibility:** WITHHELD without plan knowledge (abstention criterion 1). Global rule: the same non-trade is expected for a lurker and damning for a support — ungradeable without role. Companion: the sacrificial entry who dies 0-damage but opens the trade window (HLTV-attributes archetype) vs the 0-damage donation in a routine hold with no info/utility/trade downstream — identical at death time, opposite verdicts; downstream conversion must be observed before grading.

## EVAL-006 — Player-awareness ambiguity: repeek into the posted AWPer

**Type:** awareness ambiguity. **Status:** `HYPOTHETICAL` (researcher-created; zero named-coach process gradings for repeeks found in this pass).

- **Observed facts (stipulated):** Player misses first contact on an angle, wide-swings the same angle 4 s later with no utility and no teammate ready, dies to a posted AWPer. Confirming footage needed: pro demo round + peek-1/peek-2 info-state reconstruction (spotted masks, sound radii).
- **Plausible interpretation:** committing repeek — donated a man advantage for zero new information; punishable.
- **Alternative explanation:** the peek-1→peek-2 delta changed the math — peek 1 banked the AWPer's exact scope state/position, peek 2 was a timed trade setup from an unheard teammate call, or the first "miss" was an info jiggle misread by the reviewer as a committed peek.
- **Supporting evidence:** positions, timings, utility state, teammate readiness (recorded). The slogan "never repeek" is folk wisdom (Reddit truism thread, non-authoritative), not evidence.
- **Contradictory evidence:** no peer-reviewed CS repeek study exists; the info delta between peeks (what the player learned, heard, or was told) is estimated/unsupported. Conflating committing repeeks with non-committal info jiggles is the category error the slogan commits.
- **Judgment eligibility:** WITHHELD without the peek-1 info state (criteria 2, 8). Dry-peek variant (swinging without flash): justified under timer/low-buy constraint or known utility downtime; questionable with a teammate holding a flash and no pressure — same withhold (flash availability + known/unknown angles are the missing-or-present premises).

## EVAL-007 — Teammate-coordination ambiguity: utility-in-hand at contact

**Type:** coordination ambiguity. **Status:** `HYPOTHETICAL` (researcher-created; no named-coach grading found).

- **Observed facts (stipulated):** Support player dies with smoke equipped walking uncleared space 20 s into the round. Confirming footage needed: pro demo with round-plan context (execute call vs clear discipline).
- **Plausible interpretation:** negligent — role demanded rifle-first clearing; no execute was called; walked uncleared space with utility out.
- **Alternative explanation:** caught mid-execute — the called execute demanded smoke out at that tick; contact came from an unexpected tempo break the whole team missed, not from individual negligence.
- **Supporting evidence:** weapon state, position, cleared/uncleared geometry (recorded/geometry-dependent).
- **Contradictory evidence:** the called plan (execute vs clear) came via voice — **unsupported** (MM demos voiceless; team chat encrypted 2026-09-09). Contact foreseeability depends on teammates' unrecorded calls.
- **Judgment eligibility:** WITHHELD without plan knowledge (criteria 1, 3). Same structure: "giving up map control" (stack on a hard read vs unforced walkout — the read is the missing premise) and "not trading" second-man swings (trade setup called vs solo hero swing).

## EVAL-008 — Reasonable play, bad outcome: the disciplined save that looks like cowardice

**Type:** reasonable play with bad outcome (killfeed-centered review sees no kills, scores passivity). **Status:** expert-practice-anchored; quantitative save value unrecovered.

- **Observed facts:** 2v4 post-plant, rifles + full nades, team concedes, saves two rifles, exits only. Discourse revisit: HLTV "Saving: How bad is it" (`news/35622`, located-not-read); "Pros talk weapons in CS2 and MR12 effect on saving" (`news/37387`, located-not-read) — discourse is live among pros (**Demonstrated** that the debate exists).
- **Plausible interpretation:** disciplined — live-round equity below the save threshold; saved weapons convert to next-round win probability (MR12 concentrates per-round weapon value).
- **Alternative explanation:** defeatist — retake was live (kit + smokes + unknown enemy positions at 60 s); conceded equity for comfort.
- **Supporting evidence:** economy state, retake loadout, live-vs-dead equity arithmetic (recorded/computed). Leetify's WP model rewards saving via next-round gain (vendor method docs).
- **Contradictory evidence:** whether the save was disciplined vs defeatist depends on the player's info state at the time — inferred/unavailable single-instance. Retake-kit state and enemy-info state must both be present.
- **Judgment eligibility:** SUPPORTED only with economy context + retake-loadout facts; single-instance *credit* ("correct save") WITHHELD without recurrence (criterion 4) — one save cannot be credited as disciplined vs lucky-passive. Killfeed review (no kills = no credit) is the selection-bias failure this case exists to block.

## EVAL-009 — Questionable play, good outcome: the hero rotate that worked

**Type:** questionable play with good outcome (`HYPOTHETICAL` — no verified analyst VOD performing Q2 surgery was retrieved; recorded gap).

- **Observed facts (stipulated):** Anchor abandons his site on a first-contact sound cue that usually means nothing, arrives exactly as the hit comes, wins the round; broadcast narrative: "great read".
- **Plausible interpretation:** correct read — the cue bundle (utility volume + absence of default pressure + bomb-spotted tell) genuinely licensed the rotate; base-rate play, well executed.
- **Alternative explanation:** lucky abandon — the cue is low-signal in the player's longitudinal sample; the round win outcome-backfills a -EV habit that will donate sites across the season. Q2 in Duke's matrix: won *despite* the decision class.
- **Supporting evidence:** the round win + arrival timing (recorded). Nothing else without the listener's info set.
- **Contradictory evidence:** outcome-backfill mechanism is **Demonstrated** generally (Baron & Hershey; hindsight r≈.17); the "great read" narrative is exactly the sensemaking→inevitability path (Roese & Vohs). Won dry peeks and lucky repeeks that hit share this structure.
- **Judgment eligibility:** WITHHELD single-instance either way (criteria 4, 7 — the Q3 test cannot be run: "would this rotate be endorsed if the hit had gone to the abandoned site?"). Adjudication requires longitudinal cue→hit calibration for this player, not one round.

## EVAL-010 — Multi-round repeated behavior, both outcomes: "always takes isolated duels"

**Type:** repeated behavior with positive and negative outcomes. **Status:** expert-framed; habit test applied.

- **Observed facts (stipulated pattern):** Across 30+ tracked rounds, a rifler takes first contact away from the pack in ~40% of defaults; some rounds the isolation wins the opening duel and the half snowballs; others it donates sequential 1v1s. Confirming data: encounter-episode corpus + role context across demos.
- **Plausible interpretation:** role effect, not behavior — he is the designated entry/ahead-of-pack searcher; isolation rate matches the assignment and converts at or above the role baseline (HLTV trade-structure framing: ahead-of-pack players structurally untraded).
- **Alternative explanation:** genuine habit flaw — isolation rate exceeds the role baseline with T1-negative aggregate; the won rounds are Q1 variance masking a Q2/Q4 tendency.
- **Supporting evidence:** recurrence (longitudinal, computed); cross-outcome survival (appears in won rounds too — the anti-selection-bias requirement); role assignment evidence.
- **Contradictory evidence:** opportunity confound — the situations he faces are self-selected (economy, opponent choices, his own earlier decisions determine which duels exist); naive conditioning produces collider errors (prior-slice E §6.3). Single-demo "habit" claims assert stability from one sample.
- **Judgment eligibility:** SUPPORTED only when recurrent + consistent + consequential + context-bound (E-longitudinal habit criteria) with role conditioning and multiplicity control; otherwise WITHHELD as anecdote aggregate. Never below a sample floor; never from deaths alone.

## EVAL-011 — Multi-round repeated behavior with live disagreement: save-heavy championship style

**Type:** repeated behavior, both outcomes, analysts disagree. **Status:** expert-reviewed on both sides; disagreement preserved.

- **Observed facts:** Jame's save-heavy, low-risk CT style through IEM Rio Major 2022; MVP award. Revisit: HLTV MVP/jL-era stature coverage (`news/43717` family); live dissent: forum thread "Jame 0.16 Ancient CT" (`hltv.org/forums/threads/3131632`); Jame's own "Master of Saves" profile framing.
- **Plausible interpretation (pro):** championship-correct economy management — save-tolerant style maximizes series win probability under MR-era round values; MVP is the market verdict. **Demonstrated** that elite practice includes save-heavy winning play — the existence proof against "never save".
- **Alternative explanation (con):** style deflates rating floors and concedes winnable rounds; 0.16-level maps are the tail risk of passivity — the "saving K/D" critique.
- **Supporting evidence:** MVP + title (facts). Quantitative save-value threshold unrecovered (HLTV 429s; open question).
- **Contradictory evidence:** each side's evidence is outcome-anchored (title vs floor maps) — both risk the Q1/Q3 confusion the Duke matrix warns about.
- **Judgment eligibility:** SUPPORTED as "style is championship-compatible" (existence proof). Any claim that save-heavy is *optimal* (or *wrong*) for a specific ranked player is WITHHELD — requires that player's economy trajectory + recurrence, not Jame's trophy. Disagreement left unresolved per contract.

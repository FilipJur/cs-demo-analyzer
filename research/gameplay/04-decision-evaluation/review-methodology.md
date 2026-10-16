# Review Methodology — Source-Grounded Decision-Review Process

Research only. No classifiers, no evaluation code. All web sources accessed **2026-10-15** unless noted.
Grades: **Demonstrated** · **Experimental** · **Research-supported** · **Plausible-untested** · **Infeasible**. `VENDOR-UNVERIFIED` = vendor/SEO content ("what coaches claim they check", never evidence a method works).

> Standing result (prior slice, not re-litigated): **no peer-reviewed study of CS demo-review methodology exists.** Everything below is convergent practitioner practice + transferred decision science, graded as such. Nothing here is a validated methodology.

## 1. What experts examine before criticizing a play

Verified from primary interviews (full provenance in `sources.md`):

**1.1 Pre-engagement state first.** Xela/Dignitas (2017, primary, **Demonstrated**): *"What was the precursor?"* — *"if you had to take the fight right then, if you gave yourself the best chance of winning the fight, and if there was a better alternate decision."* Players who "blame deaths on a mechanical mistake" skip the load-bearing question: fight *selection* precedes fight *outcome*. Same article: economy as the first context check — "players may be more aggressive if their team is on a low-econ buy" (`team-dignitas.net`, 2017-10-20).

**1.2 Buy state before judging level.** Mauisnake on NAVI–Vitality, Cologne Major 2026 (Skin.Club exclusive, 2026-06-26, **Demonstrated**): Vitality "did get ecoed twice… They would have won that map if they were able to convert on their first gun round against Falcons' pistols" — re-weight rounds by buy state first; file opponent Deagle/Scout heroics under irreducible variance: *"that's just going to happen against Falcons… that's just Counter-Strike."* Outcome decomposed into decision-relevant (gun-round conversion) vs non-diagnostic (low-probability opponent hits) — the practitioner form of variance decomposition.

**1.3 Veto and map context before player criticism.** Mauisnake (same interview, **Demonstrated**): NAVI "not going to Ancient… instead going to Inferno… your star player's best map. It's b1t's best map. So if he doesn't get to play his best map, then he won't perform to 100%." Pre-engagement state extends above the round: veto shapes the distribution a player is graded against.

**1.4 System and fit before fixed ability.** Mauisnake on kyousuke (same interview, **Demonstrated**): "under kyxsan… in playoffs, he was not going to show up. Under karrigan, he looks like he's completely changed." Same player, different IGL → performance attributed to setup, not aim. B1ad3's failure ontology likewise has no "missed shot" category: after the Cologne 2026 exit he named **failure to close favorable rounds, poor communication in key moments, late-round decision-making, lost 4v2/5v3 advantage situations** (via CS2News report of HLTV interview, 2026-06-16, **Research-supported** — HLTV body rate-limited on access date).

**1.5 Single-event spikes checked against multi-year baselines.** Mauisnake on 9z's Wos (same interview, **Demonstrated** habit-vs-event reasoning): "he hit a lot of really crucial shots. I never saw Wos have a Tier 1 event where he had this many contributions… I'm personally not sure if he's going to maintain this level." The fluke-vs-repeatable test: one event never establishes a habit.

**1.6 Behavior under pressure, not the scoreboard.** kassad (HLTV data-revolution feature, 2024-10-28, **Research-supported** via prior slice): demo reviews focus on "how the player handles high-pressure situations, how he reacts to certain situations happening mid-rounds, does he have the amount of initiative needed for his position, decision making… Stats aren't that important." Data makes the shortlist (ash via Skybox filters); the demo eye test decides.

**1.7 Withhold when comms are the missing premise.** hally/Spirit (BLAST.tv, 2024-08-10, **Demonstrated** — the strongest withhold datum found): *"Some of the movements can't be judged even by watching demos because you need to hear the flow of communication, so this is why some moments can be treated one way or another."* Workaround in the same quote: longitudinal judgment ("grown a lot in the past six months") instead of single-event verdicts. Spirit's correction path is scheduled practice-server work, not VOD verdicts.

## 2. Separating mechanical execution from tactical decision

The separability test (Xela, **Demonstrated**): *"if I had executed perfectly, would this still have been a bad decision?"* Yes → decision problem. No → execution problem. Never solve a decision problem with aim training.

Verbatim instances:

| # | Source | Decision side | Execution side |
|---|---|---|---|
| 1 | Xela 2017 (**Demonstrated**) | "if you had to take the fight right then… better alternate decision" | "quick to blame deaths on a mechanical mistake" |
| 2 | hally on donk 2024 (**Demonstrated**) | "too aggressive… too passive", discipline growth over 6 months | no aim framing at all |
| 3 | Mauisnake eco accounting 2026 (**Demonstrated**) | gun-round conversion (B-minus map) | opponent heroics = variance, not defensive error |
| 4 | B1ad3 2026 (**Research-supported**) | advantage conversion, call timing, comms | review ontology has no "missed shot" |
| 5 | YNk on sh1ro 2025 (**Demonstrated**) | "very predictable… too passive" — exploitable tendency, bounded scope | explicitly not "bad player" |

Corroborating boundary from an independent shipped tool: Memorin's methodology page (2026-09-28, `VENDOR-UNVERIFIED`, used for demo-field corroboration only): *"A demo cannot show intent or attention, so a replay is not a cheating verdict"*; *"A missing field is shown as missing, never estimated… a guess that looks like a measurement is worse than a visible blank"*; *"Playback runs on whole ticks, so sub-tick command order is not recovered"* (`memorin.app/blog/about-methodology.html`).

## 3. Timing, tradeability, rotations, map control, information

- **Timing.** donk's self-review vocabulary ("too aggressive / too passive", via BLAST 2026 snippets, **Research-supported**) and hally's discipline framing treat timing as the decision variable. No validated timing metric exists in CS; the evaluable form is action-onset latency vs a cohort in matched info states (**Plausible-untested** as CS practice).
- **Tradeability.** Geometric and computable (positions + eye rays + occlusion), but role-conditioned: HLTV's trade-structure analysis states lurkers and ahead-of-pack players "are less likely to both be traded or to trade a teammate" (**Demonstrated** snippet; body rate-limited). The trade window is definitional, not objective — 1 s HLTV "saved teammate", 5 s cs-demo-analyzer, 5.25 s awpy — so trade outputs are not comparable across tools.
- **Rotations.** The most hindsight-contaminated judgment in the set: judging rotation speed from omniscient replay without the rotator's heard/seen set is outcome bias by construction (Baron & Hershey 1988 transfer, **Research-supported**). Disciplined anchors who hold through a fake are slow *correctly*; nothing in the demo distinguishes fake-patience from late rotation without audio-spotting evidence.
- **Map control.** Meaningful only relative to a plan: conceding space to stack on a hard read is correct; unforced concession is not. The conceding team's info set (the read) is the load-bearing premise and is **Infeasible** from demo alone when it came via voice.
- **Information.** The core withhold trigger. Per-tick reconstruction needs: spotted flags (**recorded but trap-laden** — `spotted` is a radar flag with 0–500 ms lag, "shadow" retention, and a 16-bit partial mask mapping; GOTV demos may reflect spectator spotting), smoke occlusion (**geometry-dependent** — exact voxels only via cs2parser decode, awpy's LOS is documented smoke-blind), audio info (**estimated** — `player_sound` radius recorded, perception not), comms content (**unsupported** — MM voice absent; team chat encrypted 2026-09-09). Attention (looking ≠ seeing) is **Infeasible** — no gaze data exists.

## 4. Habits vs isolated events

Practitioner proxy for a habit: repetition across rounds plus survival across outcomes (Mauisnake's Wos test, §1.5). Statistical anchor: a pattern is a habit only if *stable* — measurable from the player's own match history (Franks et al. 2016 meta-analytics criteria: discrimination / stability / independence, **Research-supported**). False-habit confound: opportunity — "always takes isolated duels" may be a role effect (entry), not a behavior; habit claims must be conditioned on role/position/context (HLTV role-adjusted ratings are the professional analogue). Any product reporting "your habit" from one demo asserts stability from one sample — a gate the eval harness must enforce (prior-slice §15 Q4).

## 5. Alternatives and disagreement

Analysts routinely volunteer alternatives ("should have saved/flashed/fallen back"), but the *realism constraint* — alternatives the player could actually execute given loadout/position/time — is rarely enforced (**Plausible-untested** as validated practice). Team-coordinated alternatives ("call for the rotate, then peek") are **Infeasible** to evaluate without comms.

Credible reviewers verifiably disagree (preserved, not resolved):

- **D1. Telestrator/deep-analysis format:** YNk disagrees with Thorin + Richard Lewis — format failure, not content failure (2025-11-20 interview, **Demonstrated**).
- **D2. Falcons trajectory:** Mauisnake + YNk read trajectory ("a matter of time") vs popular results-reading ("failing miserably"); Falcons won Cologne Major 2026 — outcome-consistent, not outcome-blind, evidence.
- **D3. Analyst standards:** Thorin ("flipped his prediction after every map — that's not analysis") vs Mauisnake ("a separate profession") vs kassad (organizers' fault) over jL at IEM Kraków 2026 (**Demonstrated** multi-party split; Thorin's charge is itself an outcome-bias accusation).
- Cross-cutting: professional players prefer match outcomes as "good"; researchers/practitioners prefer action measures (Sharpe et al. 2023 Delphi, **Research-supported**) — *which* experts validate a reviewer changes the answer.

## 6. Hindsight and information: the transfer

Grounding (all read 2026-10-15): Fischhoff (1975) hindsight≠foresight **Demonstrated**; Roese & Vohs (2012) three levels (memory distortion → inevitability → foreseeability), mechanisms (recollection failure, knowledge updating, sensemaking, fluency misattribution), debias — only consider-the-opposite (≤3 alternatives) consistently effective, expertise does NOT blanket-protect **Demonstrated**; Guilbault et al. (2004) d≈0.34–0.39, instruction-debiasing fails **Research-supported**; Arkes et al. (1988) consider-the-opposite reduces but does not eliminate bias **Experimental**; Baron & Hershey (1988) outcome bias **Research-supported** (via prior slice).

Concrete transfers:

1. **Outcome-blind CS review procedure:** pause at the decision point (pre-engagement state), record predicted best action + ≤2 alternatives *before* unpausing (Fischhoff memory-design analogue; Xela's "better alternate decision" is a weak field version). Nobody found in the wild practices the strict form — **Plausible-untested** as CS practice.
2. **Myopia → blame the visually prominent actor** (Roese & Vohs; Taylor & Fiske head-of-table effect): the entry who dies first absorbs blame; hally's comms-flow warning and B1ad3's team-unit ontology are anti-myopia moves (**Research-supported** transfer).
3. **Sensemaking → inevitability narratives** ("Falcons are failing" compresses many-to-many causation into story); trajectory reads push back by re-expanding alternatives (**Plausible-untested** as labelled mechanism; D2 is a clean field illustration).
4. **Role misidentification:** support-player aggression judged by entry standards misfires — three independent attestations (CS2Hype 60-ADR warning `VENDOR-UNVERIFIED`; YNk sh1ro critique; HLTV Attributes baiter/entry split) — **Research-supported**.
5. **Timing:** reviews from days-later gist memory inflate bias; same-day timestamped notes beat next-week VOD reviews (**Plausible-untested** in CS).

## 7. The 8-step review sequence (assessed, not validated)

Verdict up front: **comparable fragments are verifiable for steps 1 and 4; steps 6–8 have zero verified CS precedent; the sequence as a whole is NOT validated.** Do not call it a validated methodology.

| Step | Comparable expert practice | Grade |
|---|---|---|
| 1. Situation before action | AAR doctrine ("what was supposed to happen" first); Romer conditions every evaluation on pre-decision state; analysts reconstruct score/economy/numbers first | Analogue **Demonstrated**; CS transfer **Research-supported** |
| 2. What player could plausibly know | Analysts say "he couldn't have known…"; fog-of-war hygiene | Intent comparable; **Plausible-untested**; most false verdicts born here |
| 3. Likely role/objective, with uncertainty | Role language native to analysts; *explicit uncertainty* is NOT standard practice — the qualifier is this research's value-add | **Plausible-untested** |
| 4. Observed actions | AAR "what actually happened"; every demo review ever. Must stay purely descriptive | **Demonstrated** |
| 5. Realistic alternatives | Analysts volunteer alternatives; realism constraint rarely enforced | Weak form comparable; **Plausible-untested** |
| 6. Evidence for/against each interpretation | ASRS enabling/recovery codings (institutional analogue); CS for/against is informal and outcome-contaminated by default | **Plausible-untested** |
| 7. Counterexamples | **No verified CS precedent — recorded gap.** Highest expected value against selection bias (see `judgment-criteria.md` §3); nearest analogues all imports (Duke alternate-universe hands, Romer distributions, xG multi-calibration) | Gap |
| 8. Supported-vs-withhold decision | **No verified CS precedent — recorded gap, but best-justified step** (Romer's rejection of unevidenced "additional information"; ASRS institutional humility; hindsight persistence) | Required-by-evidence, not validated |

Deep precedents for steps 1–2 and 8 from outside CS (all read 2026-10-15): Romer, "Do Firms Maximize?" (JPE 114(2), 2006 — dynamic programming over ~700 NFL games; the "additional information" defense tested and rejected at scale; proxy validated mean-diff 0.006, SE 0.7; vivid momentum narratives tested to nothing, |t|<1.3) **Demonstrated**; Davis & Robberechts xG-bias (arXiv:2401.09940 — standard xG underestimated Messi's GAX by 17%; baselines must be explicitly named subgroups) **Demonstrated**; NASA ASRS Pub. 51 (voluntary near-miss reporting since 1976, 297k+ reports; code *recovery factors* — why an incident was not an accident; confidentiality load-bearing) **Demonstrated**; Duke, *Thinking in Bets* Q1–Q4 matrix + 4-step anti-resulting SOP (via PokerExplore paraphrase, read directly — book claims **Research-supported**, page specifics secondary) — deaths-only review is outcome-driven learning institutionalized (examines Q3+Q4, never Q2).

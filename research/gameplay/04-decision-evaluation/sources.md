# Sources — Annotated Bibliography

All web sources accessed **2026-10-15** unless noted. Read status is stated per entry: **read-full** (primary text inspected) · **snippet** (search-extract verified, body unrecovered) · **record** (metadata/abstract only) · **located-not-read** (lead, not evidence). HLTV article bodies returned HTTP 429 on the access date — HLTV claims below rest on retrieved snippets or the already-known prior-slice feature, graded accordingly. Credibility: peer-reviewed > Valve/parser source > Tier-1 first-person interview > analyst VOD/reportage > vendor/SEO (`VENDOR-UNVERIFIED`).

## 1. Peer-reviewed & decision science (read-full unless noted)

- **Baron & Hershey (1988), "Outcome bias in decision evaluation", JPSP 54(4):569–579.** Same decision rated better when it succeeded, probabilities held fixed. `doi:10.1037/0022-3514.54.4.569` · PMID 3367280. **Research-supported** (via prior slice; not re-read). Load-bearing for outcome-bias transfer.
- **Fischhoff (1975), hindsight≠foresight + Citation-Classic retrospective.** Reported-outcome subjects overestimate predictability. `garfield.library.upenn.edu/classics1992/A1992HY93500001.pdf`. **Demonstrated** (design + finding, read-full). Grounds the pause-and-predict procedure.
- **Roese & Vohs (2012), "Hindsight Bias", Perspect. Psychol. Sci. 7(5):411–426.** Three levels, inputs, myopia/overconfidence consequences; only consider-the-opposite (≤3 alternatives) consistently debiases; expertise does not blanket-protect. Read-full via secondary-hosted PDF. **Demonstrated**. Limitation: lab literature, CS transfer reasoned.
- **Guilbault, Bryant, Brockway & Posavac (2004), hindsight meta-analysis (95 studies, d≈0.34–0.39).** Instruction-debiasing fails overall. Record-level + Roese & Vohs citation; full text unread. **Research-supported**.
- **Arkes, Faust, Guilmette & Hart (1988), physicians + consider-the-opposite.** Reduces but does not eliminate bias. PsycNet record + Roese & Vohs summary. **Experimental** (single study, medical diagnosis).
- **Christensen-Szalanski & Willham (1991), hindsight meta-analysis (122 studies, r≈.17).** Via prior slice. Small-average-effect anchor.
- **Romer, D. (2006), "Do Firms Maximize? Evidence from Professional Football", JPE 114(2).** `eml.berkeley.edu/~dromer/papers/JPE_April06.pdf`. Read-full. **Demonstrated** (methods + data inspected). Transfers: pre-decision-state conditioning; "additional information" defense tested and rejected; proxy validated (mean diff 0.006, SE 0.7); momentum narratives tested to nothing. Limitation: NFL, single study.
- **Davis & Robberechts (2024), "Biases in Expected Goals Models Confound Finishing Ability", arXiv:2401.09940.** `arxiv.org/pdf/2401.09940`. Read-full. **Demonstrated**. Transfers: reference-population selection (Messi GAX −17%), inclusion-rules-are-verdict-rules, abstentions missing from action data. Limitation: soccer finishing, single paper.
- **Van Roy et al. (2021), "Leaving Goals on the Pitch", arXiv:2104.03252.** Abstract read. **Plausible-untested** pointer on principled counterfactuals requiring a learned behavior MDP.
- **Reynard, W., NASA ASRS Pub. 51, "The Acquisition and Use of Incident Data".** `asrs.arc.nasa.gov/docs/rs/51_Acquisition_and_Use_of_Incident_Data.pdf`. Read-full. **Demonstrated** (foundational program document). Transfers: deaths-only review = accident-only investigation; code recovery factors; confidentiality load-bearing. Limitation: aviation institution, transfer reasoned.
- **Sharpe et al. (2023), JEGE 1(1) Delphi panel.** Pros vs researchers disagree on what "good" means. Via prior slice. **Research-supported**. Direct consequence: validator-panel choice changes eval answers.

## 2. CS first-person: coaches & analysts (read-full unless noted)

- **hally (Team Spirit coach), BLAST.tv interview, 2024-08-10.** `blast.tv/article/hally-its-good-donk-understands-he-lacks-discipline`. Read-full. **Demonstrated**. Strongest withhold datum ("movements can't be judged… need to hear the flow of communication") + longitudinal workaround + practice-server correction. Limitation: single interview.
- **YNk, Esports News UK interview, 2025-11-20.** `esports-news.co.uk/2025/11/20/ynk-interview-part-1-desk-analysis-over-the-years/`. Read-full. **Demonstrated**. Eye-test discipline, anti-hot-take rule, sh1ro tendency critique, trajectory-vs-results read, production/footage constraints. Limitation: desk-analyst perspective, not team review.
- **Mauisnake, Skin.Club exclusive, 2026-06-26.** `community.skin.club/en/news/iem-cologne-2026-major-might-be-the-best-cs2-major-ever-mauisnake-exclusive-interview`. Read-full. **Demonstrated**. Veto-first critique, eco-round accounting, B-minus grading, Wos fluke test, kyousuke system separation. Limitation: single analyst's reads, no controlled comparison.
- **Thorin/jL controversy, Skin.Club, 2026-02-05.** `community.skin.club/en/news/thorin-criticizes-jl-analyst-iem-krakow-community-reaction`. Read-full. **Demonstrated** multi-party disagreement (Thorin vs Mauisnake vs kassad vs community). Thorin's charge is itself an outcome-bias accusation.
- **B1ad3 Cologne 2026 exit assessment, via CS2News 2026-06-16.** `cs2news.com/news/b1ad3-navi-dont-deserve-top-eight-major-2026`. Secondary of HLTV primary (body 429-blocked). **Research-supported**. Failure ontology (advantage conversion, comms, late-round decisions). Limitation: press quote, not method.
- **B1ad3 HLTV 2026-06-16 original (`hltv.org/news/44929/`).** Snippet only. Pointer.
- **Xela, "Top 3 Tips for Watching Demos", Dignitas, 2017-10-20.** `team-dignitas.net/articles/Blogs/CSGO/11748/top-3-tips-for-watching-demos`. Read-full primary. **Demonstrated**. Precursor method + economy-first context + single-focus discipline. Limitation: 2017 CS:GO era; cites Thorin VOD (transcript unverified).
- **YNk coaching-transition interview, FanSided, 2018-10-04.** Read-full. Background.
- **Elmapuddy about page.** `elmapuddy.com/`. Read. **Demonstrated** for positioning ("why a decision worked or didn't"); `VENDOR-UNVERIFIED` for efficacy. Catalogue titles (donk duels, timeout reads) **Plausible-untested** (transcripts unread).
- **kassad / ash / valens / zews / zonic / ImAPet (HLTV 2024-10-28 data-revolution feature; zonic 2016; zews 2024; ImAPet 2017).** Via prior slice G. **Research-supported** practitioner statements.

## 3. HLTV structural analytics (snippet-grade — bodies 429-blocked)

- **"How trading stats can show a team's structure" (`news/35389`).** Snippet **Demonstrated** (lurkers/ahead-of-pack structurally untraded); methodology **located-not-read**.
- **"Introducing HLTV attributes" (`news/39672`).** Snippet **Demonstrated** (sacrificial entry vs baiter framing); body **located-not-read**.
- **"Introducing Rating 3.0" (`news/42485`).** Snippet **Demonstrated** (eco-frag motive + EliGE 133 ADR/23-frag 2.06→1.40 exhibit); body **located-not-read**.
- **"Saving: How bad is it" (`news/35622`); "Pros talk weapons in CS2 and MR12 effect on saving" (`news/37387`).** **Located-not-read**; discourse-exists claim **Demonstrated** via title catalog.
- **"Stat-check: G2 throws roles out the window" (`news/39326`).** Snippet (nexa lurker trade note).
- **friberg Nuke retrospective (`news/20171`).** Aggressive-CT praise-fact **Demonstrated**.
- **Xyp9x role-confidence interview (`news/35112`); coldzera highlights (`news/18511`); s1mple-vs-CLG (`news/17465`); PGL Copenhagen 2024 final match page (`matches/2370727`).** Praise-facts / corpus pointers, graded in `casebook.md`.
- **Jame Rio-era stature (`news/43717` family) + "Jame 0.16 Ancient CT" forum thread (`forums/threads/3131632`).** **Demonstrated** that disagreement is live; forum = fan discourse, non-authoritative.

## 4. Technical & demo-integrity (prior-slice grounding, reused as constraints)

- **CS2 `usercmd.proto`** (`SteamTracking/GameTracking-CS2`). Sub-tick move steps, input fields. **Demonstrated**.
- **demoparser2** (`LaihoE/demoparser`); **awpy** (`pnxenopoulos/awpy`) incl. smoke-blind LOS docs; **CS2DemoKit** (two-clock trap, delta-command reconstruction); **cs2parser** (smoke-voxel decode); **demoinfocs-golang** (`IsSpottedBy` "NOT Line of Sight" warning). All **Demonstrated** per prior-slice verification.
- **Valve 2026-09-09 patch notes** (`counter-strike.net/news/updates`): team chat encrypted in demos. **Demonstrated** (secondary reporting; Valve page authoritative, re-check).
- **CS2VoiceData** (`DandrewsDev/CS2VoiceData`): MM demos voiceless. **Demonstrated** (negative).
- **Memorin methodology page (2026-09-28).** `memorin.app/blog/about-methodology.html`. Read-full. `VENDOR-UNVERIFIED` (competitor); used ONLY for demo-field corroboration + anti-guessing exemplar (Recorded/Derived/Interpreted split; missing-as-missing; whole-tick playback; no intent verdicts; no multi-match trends). Not evidence of judgment correctness.

## 5. Vendor / community (quarantined — claims-about-checklists only)

- **CS2Hype Analyst Role Guide** (`cs2hype.com/roles/analyst`, read Mar-2026 content). `VENDOR-UNVERIFIED`. 5-pass workflow; result-bias/overfitting warnings align with §(d) debias — admissible as claimed practice only.
- **Steamanalyst / Skinvault peeking guides; Boosteria / GapTo10 / Upforge / cs2lore demo-review guides.** `VENDOR-UNVERIFIED`. Peek taxonomies and "three-pass / root-cause / one-habit" templates without citation or efficacy evidence.
- **Leetify Rating/benchmark docs; Scope.gg; Refrag Coach.** Method-claims only (prior slice): WP-delta credit splits, drifting z-score benchmarks, undisclosed composites, TTD confounds.
- **YouTube leads (NOT evidence, transcripts unread):** "I Studied CS2's Most AGGRESSIVE Pros on Nuke" (`watch?v=7E_tK9fH2_g`); "Astralis Ancient Fake B" (`watch?v=D3ukujgFm4o`); Voo broadcast catalogue (Liquipedia — fetch 403); austincs/fl0m/Thorin review series (titles only).
- **Reddit threads (fan discourse, non-authoritative):** KAST critique (`r/GlobalOffensive/comments/7lmley`); "do not repeek" truism (`comments/4xfkxm`); FACEIT comms thread (body blocked).
- **Wald survivorship account:** AMS column fetch 403; Wikipedia discovered-not-read — capped at **Research-supported**.
- **AAR doctrine (FM 7-0 App. K):** fetch 403; Wharton/Thayer secondaries — capped at **Research-supported**.
- **Failed lead (honesty record):** petr1k–yXo coldzera Nuke M4A4 debate (gameinside.ua, 403 on access date) — genuine same-play dispute exists, body unrecovered. Retry recommended.

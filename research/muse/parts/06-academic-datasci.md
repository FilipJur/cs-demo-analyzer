# 06 — Academic & Data-Science Work on CS/CS2 Analytics

**Slice owner:** EcosystemSurvey.AcademiaDs
**Date scope:** literature mostly 2020–2026; recency focus 2024 → Oct 2026.
**Purpose:** inform architecture, features, metrics and *evaluation* of a local-first, API-powered CS2 demo-analysis / personal-coaching system for a ~2000-Elo FACEIT player.

## 0. Method & verification conventions

- Every claim below carries a URL and, where determinable, a year/status.
- **Verification level** is stated:
  - `[OPENED]` — I directly fetched the page/abstract/PDF during this research.
  - `[INDEXED]` — cited from a search-engine result snippet + a live URL; not independently opened end-to-end.
- Claim categories used: **Demonstrated / Experimental / Research-supported / Plausible-untested / Infeasible**.
- CS2 vs CS:GO: stated explicitly per item. **Most published CS work is CS:GO.** CS2-specific published work exists (2024–2026) but is thin.
- `[INFERENCE]` marks my own reasoning, not a source claim.

---

## 1. Datasets

### 1.1 ESTA — Esports Trajectories and Actions ⭐ (key reusable asset)
- **What it does:** Public dataset of parsed professional **CS:GO** demos; positions, velocities, view angles, health/armor/equipment, and six event types (kills, damages, bomb events, grenade throws, weapon fires, flashes), plus game frames at ~2 Hz.
- **CS2 demo support:** **No — CS:GO only.** Verified `[OPENED]` README: 1,558 demos (878 online Jan 2021–May 2022, 680 LAN Jul 2021–May 2022), 41,782 rounds, 8.6M actions, 7.9M frames, ~3.9 GB total.
- **Maintenance:** Static dataset. Repo `pnxenopoulos/esta`, 42 commits, CC-BY-SA-4.0, Zenodo DOI 495219448. Paper: Xenopoulos & Silva, *ESTA*, arXiv:2209.09861 (Sep 2022). No CS2 refresh.
- **Critical compat note `[OPENED]`:** ESTA was parsed with **awpy 1.3.1**; README explicitly warns **awpy 2.x is NOT compatible** with ESTA files. So using ESTA means pinning awpy 1.x (Golang ≥1.17) or writing a schema migration. This is a real architectural fork in the road.
- **Architecture / data exposed / integration:** `.xz`-compressed JSON; `pip install awpy==1.3.1`; no API, direct file download.
- **Open/closed + license:** Open, CC-BY-SA-4.0 (ShareAlike — affects redistribution).
- **Linux compat:** Yes (pure JSON + xz + Python).
- **Reusability:** **High** for *training* models (win-prob, embeddings, clustering) on professional CS:GO. **Low** for a CS2-only product pipeline without a migration layer.
- **AI real vs marketing:** N/A (dataset).
- **Unsolved problems:** No CS2 data; no per-tick full state (only 2 Hz frames); non-exhaustive (README warns not to use for player aggregate stats).

### 1.2 Skybox / CSGO.ai competition dataset (verified: not "700 GB")
- **What it does:** ~700 high-level **CS:GO** tournament demos (2019–2020): ~500 initial + 200 second release. Round snapshots ~every 20 s, player position history ~every 5 s, JSON `RoundSnapshot` schema (map, patch, scores, alive players, health/armor/money/helmets/defusers, weapons/ammo/nades/C4, position history, active smokes/molotovs, prior kills, round winner).
- **Verification `[OPENED]`:** repo `Skybox-Technologies/csgo-ai-competition`; **last commit Aug 14, 2020** — the project is **dead**. Data hosted on Google Drive (linked from README), not Kaggle. The "700GB" figure circulating elsewhere is a confusion with "~700 demos" `[INFERENCE]`.
- **CS2 support:** None (CS:GO, 2019–20).
- **License:** Repo had no explicit OSI license on the About panel; treat as research-use only. `[INDEXED]` on data terms.
- **Reusability:** **Low** — coarse 20 s snapshots, stale patch, dead hosting, CS:GO. Only useful as a small labelled win-prediction benchmark.
- **Unsolved problems:** Dead download links and no license clarity are typical of 2020-era competition datasets.

### 1.3 Kaggle "CS:GO Round Winner Classification" (Christian Lillelund)
- **What it does:** Tabular per-round snapshots, target `round_winner ∈ {CT,T}`. **122,410 rows × 97 columns** (96 features): `time_left, ct_score, t_score, map, bomb_planted`, team health/armor/money/helmets/defusers/players_alive, 64 weapon-count columns (ct_/t_), 12 grenade columns.
- **CS2 support:** **CS:GO only.**
- **Verification:** `[INDEXED]` — https://www.kaggle.com/datasets/christianlillelund/csgo-round-winner-classification ; shape confirmed via mirror repos.
- **Maintenance:** Kaggle-hosted, static; license must be read on the dataset page (Kaggle default varies; check before redistribution).
- **Data exposed:** Aggregated round state only — **no positions, no per-tick, no trajectories**. Good for a quick WinProb baseline, useless for spatial coaching.
- **Reusability:** **Medium** as a cheap baseline / sanity check for a win-probability model; **low** for anything positional.
- **Unsolved problems:** Snapshot instant unclear (start-of-round vs sampled), which limits whether it is a legitimate in-round model.

### 1.4 CS2 Playstyle & Roles Dataset (2024) — Jamie Packer ⭐
- **What it does:** Player-level **playstyle features + role labels** for professional **CS2** in 2024, awpy-parsed. Features per side + overall: `tapd` (time alive per death), `oap` (opening-attempt %), `podt` (traded-death %), `pokt` (trade-kill %), and team-relative positioning ranks `adnt` (distance to nearest teammate) / `adat` (distance from team centre).
- **Verified how `[OPENED]`:** repo `Jamie-Packer/cs2-playstyle-dataset-2024`, single CSV `data/cs2_playstyle_roles_2024.csv`, one row per `steamid`. Positioning computed from 3D positions every 3 s, starting 10 s post-freeze, **pre-plant, alive-only, full 5v5 only**; per-map team-relative ranks (0.2–1.0) then round-weighted. Role labels derived from **Harry Richards' (NER0cs) Positions Database** (external Tableau source), so many players are blank.
- **Maintenance:** 7 commits, 0 stars; Zenodo DOI 10.5281/zenodo.17264782; CC-BY-4.0. **Experimental / hobbyist, not peer-reviewed.**
- **CS2 support:** **Yes — CS2, 2024.**
- **Architecture / integration:** CSV; pandas/R; engine credit to awpy.
- **Reusability:** **High as a template** for the feature definitions we would compute for the owner; **medium as data** (player-level aggregates, not round-level, so cannot drive per-round feedback).
- **Unsolved problems:** Aggregate labels, missing role coverage, no round-by-round role switching; labels are "derived from a positions database" not discovered unsupervised, so it is not a ground truth.

### 1.5 CS2 unsupervised role discovery from raw .dem (Kumar, IIIT Sri City) — btp_cs2
- **What it does:** Parse pro `.dem` → **19 behavioural features per player-round** → per-side Self-Organizing Maps (SOM) → cluster codebook into role archetypes → test whether role consistency predicts round outcome. Corpus: 76 pro maps, 10 events (2024–2025), 13 teams, 1,652 rounds, 16,520 player-round obs. T-side archetypes: Aggressor / AWPer / Support Rifler / Lurker; CT: Site Anchor / AWPer / Rotating Rifler / Eco-Save / Aggressor.
- **Key negative result (important for us):** within-half role consistency *correlated* with winning, but **prior team role consistency did NOT significantly predict next-round outcome**; authors interpret causality as winning preserving economy/structure, not the reverse.
- **Verified how `[OPENED]`:** repo `sachiniiits/btp_cs2`; **latest commit 9 Jul 2026**; bachelor's thesis; docs include DECISIONS_AND_RESULTS / REPRODUCTION_AND_TROUBLESHOOTING.
- **CS2 support:** **Yes — CS2, 2024–2025.**
- **Reusability:** **High as a method reference** (SOM → emergent archetypes → manual interpretation is the canonical Drachen/Bauckhage workflow), reproducible pipeline. Not a maintained library.
- **Unsolved problems:** Thesis-scale, not packaged; role→outcome link is weak/null (a caution against selling "role consistency" as an outcome lever).

### 1.6 VOR.TECH CS world-model dataset (bots; 2026)
- **What it does:** `v0rt3ch/cs-5v5-bots-aim_usp-3k` — 9,515 CS **bot** matches, 218,768 rounds, one map (`aim_map_usp_s`), pistol-only, ~195M event rows at 16 Hz, ~3,390 h, 255,712 first-person POV videos (256×256@16fps), aligned state/action/video.
- **CS2 support:** CS (bot environment); not human esports. `[INDEXED]` HuggingFace dataset card, 2026.
- **License:** CC-BY-NC-4.0 for annotations; footage under Valve video policy → **non-commercial only**.
- **Reusability:** **Low for coaching** (bots, one aim map); useful only for world-model / imitation research or synthetic pretraining.
- **Unsolved problems:** No human behaviour, no real map, no economy/utility dynamics.

### 1.7 CS2 demo→dataset pipelines (human)
- `vast7777/cs2-demo-to-dataset` — MIT-licensed pipeline converting `.dem` (pro/GOTV, FACEIT, personal) into `round/events.parquet` + per-player `video.mp4` + `state.parquet`, aligning 16 fps video with 64-tick state (4 state rows/frame). `[INDEXED]`. Footage rights still Valve's. Relevant if we ever want video pairings.
- `CS2OpenDev/CS2DemoKit` — `[INDEXED]` CS2 demo tooling; likely cross-covered by the ParsersLibs slice.
- **Reusability:** Medium; mainly a video+state alignment reference.

### 1.8 Liquipedia / bo3.gg / HLTV scraped data
- **Liquipedia:** No official bulk dump found. Options are the MediaWiki API (max 1 req / 2 s; `action=parse` ≤1 / 30 s; custom User-Agent; HTML scraping prohibited) and the approved **LPDB API** (≤60 req/h, key required). Content **CC-BY-SA-3.0**; free tier oriented to non-commercial/open-source; betting/replica projects rejected. `[OPENED]` https://liquipedia.net/api-terms-of-use (2025 state).
- **bo3.gg / HLTV:** No legitimate bulk API; HLTV has static stats pages and a **2025 "HLTV Brain" closed beta** (news 45712) whose data is proprietary. Scraped HLTV datasets circulate but violate ToS and are not license-clean.
- **Reusability:** **Low as a demo source** (these are metadata/rosters/stats, not demo state). Relevant only for tournament/team context joins, and only under CC-BY-SA share-alike constraints.
- **Unsolved problems:** No licensed, machine-readable, up-to-date CS2 match-metadata feed suitable for a commercial local tool without scraping risk.

### 1.9 Summary dataset table

| Dataset | Game | Size | Rounds | License | awpy dep. | Positional? | Status | Reuse verdict |
|---|---|---|---|---|---|---|---|---|
| ESTA | CS:GO | 1,558 demos / 3.9 GB | 41,782 | CC-BY-SA-4.0 | **1.3.1 only** | Yes (2 Hz) | Frozen 2022 | **Integrate** (training) |
| Skybox CSGO.ai | CS:GO | ~700 demos | — | unclear | n/a (own format) | 5 s pos | Dead (2020) | **Ignore** |
| Kaggle round-winner | CS:GO | 122,410×97 | 122k snapshots | Kaggle (check) | n/a | No | Static | **Integrate** (baseline) |
| CS2 Playstyle&Roles 2024 | CS2 | 1 CSV | — (player-level) | CC-BY-4.0 | awpy (2.x) | Yes (aggregated) | Hobbyist 2024 | **Reuse** (feature template) |
| btp_cs2 (Kumar) | CS2 | 76 maps / 16.5k obs | 1,652 | repo license (thesis) | awpy 2.x | Yes | Active Jul 2026 | **Reuse** (method) |
| VOR.TECH bots | CS (bots) | 9,515 matches / ~1 TB | 218,768 | CC-BY-NC-4.0 | n/a | Yes (16 Hz) | 2026 | **Ignore** (non-human) |
| CS2 demo→dataset | CS2 | per-demo | — | MIT (code) | awpy | Yes + video | Active-ish | **Integrate** if video needed |

---

## 2. Papers by theme

> Note on coverage: the CS/CS2 academic corpus is **small and dominated by CS:GO**. The "automated coaching / LLM feedback" and "CS2-specific" segments are the thinnest, which is itself a finding.

### 2.1 Win probability / round-outcome prediction

- **Xenopoulos, Doraiswamy & Silva — "Valuing Player Actions in Counter-Strike: Global Offensive"** (IEEE BigData 2020; arXiv:2011.01324). [OPENED abstract + PDF body]. Introduces a **context-aware Win Probability model** over **70M+ events** (features: players alive, equipment value, health, map, round state) and **Win Probability Added (WPA)** for individual actions; benchmarked vs LightGBM/XGBoost/Deep Sets/Set Transformers. **CS:GO.** Code/data via awpy ecosystem. Category: **Demonstrated**. This is the canonical precursor for everything else and the single most reusable method (WPA = our bridge from "stats" to "decision value").
- **Xenopoulos, Coelho & Silva — "Optimal Team Economic Decisions in Counter-Strike"** (arXiv:2109.12990, Sep 2021). Game-level win probability incorporating score, equipment, money, and spend decisions — i.e., the **economy-aware Markov framing**. `[INDEXED]`. **CS:GO.** Category: **Research-supported**.
- **Sinap — "Prediction of CS:GO Round Results with Machine Learning Techniques"** (JISTA 6(2):119–129, Sep 2023; DOI 10.38016/jista.1235031). Round-winner classification, classical ML. `[INDEXED]`. **CS:GO.** Category: **Demonstrated** (limited novelty).
- **Hasegawa & Hirota — "A Study on Predicting the Winning Team of a Round in CS:GO Using Frame Information"** (DiGRA Japan Summer Conf. 2024, pp. 47–51). XGBoost on frame info; key finding: **feature importance changes per map**, top features = surviving-player diff, ammo, distance to bomb, health/equipment. `[INDEXED]`. **CS:GO.** Category: **Demonstrated**. *Implication:* a single global "what matters" narrative is wrong; map-conditional models needed.
- **Kawasaki et al. — "Predicting Win Conditions of CS:GO for Analyzing Round Progression"** (IEEE GCCE 2024; DOI 10.1109/GCCE62371.2024.10760945). **Set Transformer** over player coordinates + state → predicts the **round win condition** and traces probability vs. round progression. `[INDEXED]`. **CS:GO.** Category: **Experimental**. Relevant: transformer-over-players is the modern architecture for state encoders.
- **González — "Momentum-stopping: Effects on performance"** (Sports Economics Review 7:100038, Sep 2024; DOI 10.1016/j.serev.2024.100038). 170,812 rounds / 6,379 pro CS:GO matches (2018–23); models whether previous-round loser wins next round, controls for round win probability; finds timeouts alter next-round outcome after momentum. `[INDEXED]`. **CS:GO.** Category: **Research-supported**. Relevant: **round-to-round state dependence is real** → justifies an MDP/Markov formulation with momentum/economy features.
- **Rejthar & Kotrba — "Confirmation of the validity of the HLTV ranking"** (ICG, Oct 2023; DOI 10.3233/ICG-230229). HLTV *team* ranking has explanatory power for match outcomes. `[INDEXED]`. Category: **Research-supported** (does not validate the *player* rating as causal skill).

### 2.2 Player-role detection & clustering

- **Fitsner — "Exploring Clustering Algorithms on Spatial Data in Video Games"** (Univ. of Victoria, 2025; dspace.library.uvic.ca). **Gaussian Mixture Model** on CS:GO spatial behaviour → **four playstyles per side**; playstyle and round context mattered more than map identity. `[INDEXED]`. **CS:GO.** Category: **Experimental** (undergrad poster).
- **Kuzhii & Furgala — "Feature Engineering for Role Assessment in Counter-Strike 2"** (Electronics and Information Technologies, LNU, 2025). Multidimensional behavioural space for **CS2** roles using HLTV-style attributes (Firepower, Entrying, Trading, Opening, Clutching, Sniping, Utility, T/CT, map-dependent); PCA + ANOVA + correlation; argues roles are regions not a single rating. `[INDEXED]`. **CS2.** Category: **Research-supported**. Directly informs *which features to compute*.
- **Kumar (btp_cs2)** — see §1.5. SOM role discovery, **CS2**, leakage-free role→outcome test (null result). `[OPENED]`.
- Foundations worth citing: Drachen et al. *Player modeling using self-organization in Tomb Raider* (IEEE CIG 2009); Drachen, Sifa, Bauckhage & Thurau *Guns, Swords and Data* (IEEE CIG 2012); Bauckhage, Drachen & Sifa *Clustering Game Behavior Data* (2015); Ferguson et al. *Player Style Clustering without Game Variables* (FDG 2020). `[INDEXED]` — the SOM/cluster-then-interpret pattern is well-established, not novel.

### 2.3 Spatial / trajectory analysis

- **Durst et al. — "Learning to Move Like Professional Counter-Strike Players"** (SCA 2024; arXiv:2408.13934; CGF 43(8):e15173). [OPENED full metadata]. 123 h pro traces; **transformer movement model** over all players in a Retakes round; <0.5 ms/step on one CPU core; human evaluators rate it 16–59% more human-like than commercial/scripted bots. Also introduces **round trajectory-similarity** (player-mapping + DTW-ADE-style distance) used for **nearest-neighbour propagation of strategic labels**. **CS:GO.** Category: **Demonstrated** (simulation), **Experimental** (label propagation).
- **Tamponi et al. — "Integrating Macro-Areas into 3D Maps"** (IEICE Tech. Report, 2024, BioX2024-82). Uses **ESTA + awpy** to collapse 3D coordinates into map "macro-areas" and associate events with regions. `[INDEXED]`. **CS:GO.** Category: **Experimental / preliminary**. Relevant: macro-area abstraction is exactly the spatial-index trick we need for coverage/heatmap features.
- **DECOY — "A Data-Driven Discretized CS:GO Simulation Environment…"** (OpenReview id Z8BQtU9Kuo). Waypoint-discretized CS:GO environment for multi-agent planning using human trajectory data. `[INDEXED]`. **CS:GO.** Category: **Experimental**. Relevant: waypoint graph = reusable abstraction for counterfactual/planning.

### 2.4 Tactical pattern mining & similarity search

- **Xenopoulos, Rulff & Silva — "ggViz: Accelerating Large-Scale Esports Game Analysis"** (arXiv:2107.06495; CHI PLAY era; repo `pnxenopoulos/ggViz`). Represents CS:GO states as **spatial tokens from positions + nav mesh**; analyst sketches a configuration and retrieves **similar states from >10M states**, with heatmaps/WinProb overlays. `[INDEXED]`. **CS:GO.** Category: **Demonstrated**. **This is the closest prior art to a "compare my round to similar pro rounds" feature.** Limitation: CS:GO, interactive analyst tool not auto-coaching.
- Durst et al. nearest-neighbour round labelling (above) — the other similarity precedent.
- **"Evaluating Player Actions in Professional Counter-Strike using Temporal Heterogeneous Graph Neural Networks"** (MIT Sloan Sports Analytics Conf.; sloansportsconference.com). Models pro CS actions as a temporal heterogeneous **GNN** to value actions. `[INDEXED]`. **CS:GO** (preponent). Category: **Experimental**.
- **"Formalization of Tactical Representations in Counter-Strike through Data Preprocessing and Labeling"** (Kirna BA thesis, Univ. Twente, essay.utwente.nl/107405). `[INDEXED]`. Background on tactical labelling.
- **Note:** No widely-cited paper does full **unsupervised tactical pattern mining (sequential pattern mining / DTW-HDBSCAN)** on CS2; the literature splits into *learned movement* (Durst) and *macro-area abstraction* (Tamponi). **This is a gap.**

### 2.5 Anomaly / cheat detection

- **"Identify As A Human Does: A Pathfinder of Next-Generation Anti-Cheat Framework for First-Person Shooter Games"** (arXiv:2409.14830, 2024). `[INDEXED]`. Category: **Experimental**.
- **BotScreen: "Trust Everybody, but Cut the Aimbots Yourself"** (USENIX Security 2023; KAIST SoftSec). Crowdsourced/vote-based aimbot detection. `[INDEXED]`. Category: **Demonstrated** (deployed research).
- **VADNet — "Visual-Based Anti-Cheating Detection Network in FPS Games"** (IIETA TS 41(1), 2024; DOI 10.18280/ts.410137). Visual detection. `[INDEXED]`. Category: **Experimental**.
- **"Invisibility Cloak: Proactive Defense Against Visual Game Cheating"** (USENIX Security 2024). `[INDEXED]`.
- **Relevance:** mostly orthogonal to *personal coaching*, BUT the same demo-derived behavioural features (aim-path kurtosis, reaction-time distributions, reaction-to-unseen-enemy) that detect cheats can flag **our own client-side manipulations** and, more usefully, characterise "what clean vs suspect aim looks like" for self-review. Category overall: **Research-supported**, but no CS2-specific peer-reviewed model found.

### 2.6 Automated coaching / natural-language feedback generation ⚠️ (thinnest area)

- **"Game Coaching System Using 3D CNN and LLM"** (IEEE, 2026; ieeexplore 11518638). 3D CNN identifies improvable gameplay moments (~71% balanced accuracy), LLM (after user confirmation) generates summary + detailed coaching feedback. `[INDEXED]`. Category: **Experimental**. Closest technical match to our target feature; not CS-specific and not publicly reproducible.
- **"Crafting Champions: An Observation Study of Esports Coaching Processes"** (ACM CHI 2025; DOI 10.1145/3706598.3713141). Empirical study of *how human esports coaches coach*: real-time guidance, own-replay analysis, other-player replay analysis; activities = error correction, strategic advice, motivation, evidence from stats. `[INDEXED]`. Category: **Research-supported / qualitative**. **Use this to derive what a feedback engine should output.**
- **"Exploring Large Language Model as an Interactive Sports Coach"** (arXiv:2509.26593, 2025). Not esports; LLM as planner/explainer/motivator over a longitudinal program; identifies need for **persistent athlete models, proactive feedback, safety guardrails**. `[INDEXED]`. Category: **Experimental**.
- **"Talking-to-Build: How LLM-Assisted Interface Shapes Player Performance…"** (arXiv:2507.20300, 2025). 30-participant Minecraft study; LLM assistance improved task performance/engagement. `[INDEXED]`. Category: **Research-supported** (adjacent domain).
- **"Diagnosing Performance in Invasion-Based Esports: The Esports Performance Screening Framework"** (arXiv:2608.09156, 2026). Five-level decomposition: **strategy → tactics → tasks → actions → operations** for organizing replay feedback. `[INDEXED]`. Category: **Research-supported (conceptual)**. **Directly reusable taxonomy for structuring our report.**
- **"A Feature Comparison Study of Live Companion Tools for Esports Games"** (FDG 2024; DOI 10.1145/3649921.3650004). `[INDEXED]`. Category: **Research-supported**.
- **Open-source (non-academic) prior art worth mining:** `JBRKR000/cs2-demo-coach` (status badge "Coach MVP", v1.0.0, 28 commits, 2 stars, Python 3.11, awpy + LightGBM + Polars; produces player stats, benchmark percentiles, **ML impact scoring**, **VOD review priority**, 5-s death-risk, **decision alternatives** (fall_back / wait_for_trade / hold_angle), coach summary, JSON export). [OPENED]. Category: **Experimental** (hobby MVP — its "decision simulation" is a heuristic, not a validated counterfactual engine). `denmonz/CS2-RAG`, `lucaslencinas/forging`, `gduplessy CS Coach`, commercial `cs2mate.com/ai-coach` and `altrosstudios.games/gamedemon`. Category: **Plausible-untested / marketing** — no published evaluation.

### 2.7 Decision-quality, counterfactual & IRL methods

- **Luo, Schulte & Poupart — "Inverse Reinforcement Learning for Team Sports: Valuing Actions and Players"** (IJCAI 2020; ijcai.org/proceedings/2020/0464). [OPENED full PDF]. **Alternating MaxEnt IRL with domain knowledge (IRL-DK)** over a Markov-Game model; treats one team as the environment of the other (marginal-MDP proof); 4.5M NHL events; learned dense rewards outperform sparse goal-reward Q-values on NLL/Hausdorff and rank defencemen fairly (32 defencemen in top-50 vs 1 for GIM). Code `github.com/miyunluo/IRL-icehockey`. **Not CS** — but the method transfers and is the strongest available template for "why did the pro do that / what is the implicit value function" reasoning.
- **Go DQI — "The Impact of AI on Decision Quality and Novelty in Go"** (PMC10041097, 2023). **Decision Quality Index** `DQI = 1 − (W_AI_counterfactual − W_human)` — mistake = expected win-probability loss vs best alternative, not mere deviation. `[INDEXED]`. Category: **Demonstrated** (Go). **Template for a CS2 decision-quality metric.**
- **"When Experts Err: Using Tetris Models to Detect True Errors From Deliberate Sub-Optimal Choices"** (eScholarship uc/item/28k0m6md). Distinguishes (1) unrecognised-better-action, (2) deliberate sub-optimal for long-term strategy, (3) genuine error. `[INDEXED]`. Category: **Research-supported**. **Critical caution:** do not label every deviation from a policy as a mistake.
- **"Tracing strategic divergence: archetypal and counterfactual analysis of StarCraft II gameplay trajectories"** (Frontiers in AI 2025; DOI 10.3389/frai.2025.1724493). Constructs minimally-modified counterfactual trajectories; divergences often originate early (~8.4% of game duration). `[INDEXED]`. Category: **Experimental**. Closest esports counterfactual precedent.
- **"Decision-making in esports: heuristics in League of Legends teamfights"** (Computers in Human Behavior, 2026; ScienceDirect S0747563226001329). Applied Cognitive Task Analysis of semi-pro team heuristics. `[INDEXED]`. Category: **Research-supported** — explains *why* an engine-flagged "bad" move may be intentional.
- **Verdict on CS-specific IRL:** **No CS2-specific IRL/decision-evaluation paper found.** CS work stops at WPA (heuristic action value). IRL/VAEP/counterfactual-EV for CS is a **genuine open gap** `[INFERENCE]`.

---

## 3. Key methods — applicability map

| Method | Best CS/CS2 precedent | Shown to work for CS2 specifically? | Reuse for us |
|---|---|---|---|
| **Win-probability model + WPA** | Xenopoulos 2020 (CS:GO) | CS:GO demonstrated; CS2 not formally published, but demos expose the same features → **[INFERENCE] highly portable** | **Reuse** as core "round equity" engine |
| **Markov chain / MDP over round states** | Xenopoulos 2021 economy paper; González 2024 (momentum) | CS:GO only | **Reuse** — build state = {score, side, money/equip, alive, bomb, momentum} |
| **Set Transformer state encoder** | Kawasaki 2024 | CS:GO | **Integrate** for richer state embeddings |
| **IRL / counterfactual action value** | Luo 2020 (hockey), Tetris error model | **No CS/C​S2 precedent** | **Experimental** — highest research upside, no shortcut |
| **Player-role clustering (SOM/GMM)** | Fitsner 2025, Kumar 2026, Packer 2024 | Yes (CS2, role discovery) — but role→outcome link is null | **Integrate** for personalised benchmarks |
| **Embeddings of rounds/setups (Word2Vec-style)** | ggViz spatial tokens; Durst trajectory similarity | CS:GO only; no published CS2 round2vec | **Experimental** — build ourselves |
| **Similarity search / state retrieval** | ggViz, Durst NN labelling | CS:GO | **Reuse** architecture; retrain on CS2 |
| **Counterfactual "better decision"** | Go DQI, SC2 divergence | **No CS2 precedent** — only hobby MVP (`cs2-demo-coach` heuristics) | **Experimental** — the signature differentiator |
| **Anomaly / cheat detection** | BotScreen, VADNet, arXiv 2409.14830 | CS:GO/other FPS | **Ignore** for coaching (side utility at most) |

### "Word2Vec-style embeddings of rounds/setups"
No peer-reviewed CS2 paper found. The nearest analogues are ggViz *spatial tokens* and Durst *trajectory-similarity*; also the general MOBA "role/hero embedding" literature. Category: **Plausible-untested** for CS2. `[INFERENCE]` A doc2vec/skip-gram over discretised event-token sequences (map-area × action × phase) is a cheap, low-risk experiment.

---

## 4. Decision-quality metrics — computability from demos

| Metric | What it measures | Computable from a CS2 demo? | Extra data needed |
|---|---|---|---|
| Kills / KPR, DPR | raw output | **Yes** | — |
| **ADR** | damage/round | **Yes** (awpy damage events) | — |
| **KAST** | ≥1 kill/assist/survive/trade per round | **Yes** (binary; definition of trade window matters) | consistent trade-window definition |
| Rating 2.x | proprietary composite | **No (formula closed)** | HLTV data |
| **Rating 3.0** | 6 components incl. **Round Swing**, eco-adjusted, damage-share, flash-assist, trade context (HLTV news 42485, 20 Aug 2025) | **Partially — cannot fully reproduce** | proprietary model; HLTV itself notes small-sample & model-dependence limits (news 43047) |
| **Impact** | composite | No (closed) | — |
| **Trade-kill %** | trades within window | **Yes** (awpy `isTrade`) | window choice (2 s in deterministic sense, 5 s in Packer) |
| **Opening duels / entry** | first-kill participation & win% | **Yes** (awpy `isFirstKill`) | role context for interpretation |
| **WPA** | ΔP(win round) per action | **Yes if we build the WinProb model ourselves** | train on ESTA/CS2 demos |
| **Round Swing** | ΔP around a kill | **Yes, via own WinProb** | — |
| **DQI / counterfactual EV** | value loss vs best alternative | **No — requires an action-value model** | IRL/world-model; open research |
| **Utility/flash-assist efficiency** | flash→kill conversion | **Yes** (flash events) | attribution heuristics |
| **Death-risk context** | P(death) in next 5 s | **Yes** (learned) | — |
| Self-assessment calibration | player-vs-objective agreement | Needs player self-ratings | survey instrument |

**Takeaway:** everything on the left column is derivable from demos, so a local-first system can own ADR/KAST/trades/openings/WPA/Round-Swing **without** HLTV. The genuinely *uncomputable-from-demo* quantities are the **proprietary weighted composites** and **counterfactual decision quality**.

---

## 5. Metric criticism & measurement-validity literature

- **Xenopoulos 2020 (arXiv:2011.01324)** directly critiques **K/D, ADR, KAST, Rating 2.0**: ADR ignores context (players alive, equipment value, cleanup damage); **KAST** treats non-equivalent events as equal and can be farmed by avoiding engagements; Rating 2.0's formula was non-reproducible and context-poor. Category: **Research-supported**.
- **HLTV Rating 3.0 self-acknowledged limits** (hltv.org/news/42485, 2025-08-20; adjustments news/43047): Round Swing over-weights late-round events (a 1v1 clutch ≫ opening kill); multi-kills have diminishing returns (under-credits finishing sequences); small samples yield unintuitive results; economic adjustment groups by armour/weapon value only, not utility/information/role. Category: **Research-supported (vendor-stated)**.
- **Xu & Moka — "Rating Players of CS:GO Based on Plus/Minus Value"** (arXiv:2409.05052, Sep 2024). Plus/minus-style team-impact metric; criticises Rating 2.0's individual-output focus. Limitation: plus/minus inherits teammate/opponent/role confounding. `[INDEXED]`. Category: **Research-supported**.
- **Rejthar & Kotrba 2023** validates *team* ranking but not player-rating causality. `[INDEXED]`.
- **Cross-cutting:** the field's consensus is that **no single aggregate number separates mechanical output, tactical contribution, opportunity, and causal impact**; report metric *families* (output / survival-participation / situational impact / team-adjusted value / role-opportunity controls).

---

## 6. Human-factors / coaching literature — does feedback change behaviour?

- **White et al. — "Evaluating video feedback to improve eSports performance in Street Fighter V"** (Behavioral Interventions, 2024; DOI 10.1002/bin.2056). Video review with positive + corrective feedback improved one targeted behaviour (anti-air success) in **all three** participants, generalising to ranked play. Category: **Research-supported but n=3, single behaviour** → weak generalisation.
- **Intihar — "The Effects of the Teaching Interactions Procedure on Esports Coaches'…"** (FIT thesis repository.fit.edu/etd/1349, 2023). Training coaches to *deliver* feedback did not reliably produce mastery without follow-up; feedback delivery is a trainable skill. Category: **Research-supported**.
- **Self-assessment accuracy:** a study of **181 video-game players over 700+ rounds** found self-rated skill separated median performance but **did not reliably predict individual-game performance**, and a 5-point scale collapsed to 3 groups. `[INDEXED]` (web.cs.wpi.edu/~claypool/papers/skill/paper.pdf). Category: **Research-supported**. **Implication:** players are miscalibrated at the individual-decision level → a feedback tool that *shows* objective decision cost addresses a real deficit.
- **Esports training framework** (Simulation & Gaming, 2023; DOI 10.1177/10468781231219938): performance should be assessed across mechanics, decision-making, self-regulation, social coordination, context — not kills/damage/win-rate alone. `[INDEXED]`. Category: **Research-supported (framework)**.
- **Key unanswered question for us:** *no study found that validates an automated/AI-generated coaching system's effect on CS player improvement.* The 3D-CNN+LLM paper reports accuracy, not downstream player gain. Category: **Plausible-untested**.
- **Design implications `[INFERENCE]`:** behaviour-specific, timestamped, evidence-backed feedback ("At 8:42 you rotated before confirming location → 4v5") beats vague advice; pair positive + corrective; include confidence/uncertainty; measure player's *issue-detection agreement*, not a global self-rating.

---

## 7. Failure / limitation / negative-result literature (what did NOT work)

- **Kumar (btp_cs2, 2026) `[OPENED]`:** role consistency did **not** predict next-round outcome → do not build features on the assumption that role stability causes wins.
- **Durst 2024:** movement model works only in **Retakes** on limited conditions; authors note hand-authoring policies for "every scenario" is impractical — generalisation to full competitive rounds is unproven.
- **Luo 2020 (IJCAI) `[OPENED]`:** vanilla MaxEnt **IRL was unstable** (oscillating gradients, failed to converge) and VAEP "assigns similar impact value to all actions" when positive labels are sparse → sparse-reward IRL needs the domain-knowledge regulariser. NHL-only.
- **HLTV (2025):** small-sample instability; proprietary formula non-reproducible. `[INDEXED]`.
- **Go DQI / Tetris "When Experts Err":** counterfactual-optimal comparison over-penalises deliberate sub-optimal plays; engine-optimal ≠ human-feasible. `[INDEXED]`.
- **Tamponi 2024 / macro-areas:** explicitly *preliminary*; no validated tactical mining.
- **Generalisation problems:** CS models are trained on **CS:GO professional** data with different tick rates, weapon economy and map pool than CS2; Hasegawa & Hirota show map-specific feature importance → cross-map/cross-patch transfer is not safe. `[INFERENCE]` from cited results.
- **Small-sample issue:** a single player's match history (owner ≈ 2000 Elo, maybe hundreds of rounds/month) is far below the 10⁴–10⁶ event scale used by every method above → **personalised models must shrink toward population priors** (see sibling slice LongitudinalAnalysis / Bayesian shrinkage).

---

## 8. Consolidated comparison table

| Item | Type | Game | Year | License/access | CS2? | Peer-reviewed? | Reuse verdict |
|---|---|---|---|---|---|---|---|
| ESTA | dataset | CS:GO | 2022 | CC-BY-SA-4.0 | No | yes | **Integrate** |
| Skybox CSGO.ai | dataset | CS:GO | 2020 | unclear | No | no | **Ignore** |
| Kaggle round-winner | dataset | CS:GO | ~2021 | Kaggle | No | no | **Integrate (baseline)** |
| CS2 Playstyle&Roles 2024 | dataset | CS2 | 2024 | CC-BY-4.0 | Yes | no | **Reuse (features)** |
| btp_cs2 (Kumar) | thesis+code | CS2 | 2026 | repo | Yes | no | **Reuse (method)** |
| VOR.TECH bots | dataset | CS bots | 2026 | CC-BY-NC | n/a | no | **Ignore** |
| Xenopoulos 2020 WPA | paper | CS:GO | 2020 | arXiv | No | yes | **Reuse (core)** |
| Xenopoulos 2021 economy | paper | CS:GO | 2021 | arXiv | No | yes | **Reuse** |
| ggViz | paper+code | CS:GO | 2021 | arXiv/repo | No | yes | **Integrate** |
| Durst 2024 movement | paper | CS:GO | 2024 | CGF/arXiv | No | yes | **Integrate (similarity)** |
| Kawasaki 2024 | paper | CS:GO | 2024 | IEEE | No | yes | **Integrate** |
| Hasegawa 2024 | paper | CS:GO | 2024 | jstage | No | yes | **Integrate (caution)** |
| González 2024 momentum | paper | CS:GO | 2024 | Elsevier | No | yes | **Reuse (state design)** |
| Luo 2020 IRL | paper+code | NHL | 2020 | IJCAI | No | yes | **Integrate (method)** |
| Go DQI | paper | Go | 2023 | PMC | No | yes | **Reuse (metric idea)** |
| Crafting Champions | paper | esports | 2025 | ACM | n/a | yes | **Reuse (design)** |
| 3D CNN + LLM coaching | paper | generic | 2026 | IEEE | No | yes | **Integrate (architecture ref)** |
| cs2-demo-coach | OSS | CS2 | ~2026 | repo | Yes | no | **Integrate (prior art)** |
| BotScreen / VADNet | papers | FPS | 2023/24 | USENIX/IIETA | No | yes | **Ignore (coaching)** |

---

## 9. What the literature does NOT yet solve (explicit gap list)

1. **No published CS2 win-probability / WPA model.** WPA is demonstrated only for CS:GO (Xenopoulos 2020). We must retrain on CS2 and publish our calibration.
2. **No CS-specific IRL / inverse-decision-model.** IRL is proven for hockey (Luo 2020); CS stops at heuristic WPA. Counterfactual value of a CS decision is **open research**.
3. **No validated counterfactual "better decision" engine for CS2.** The only attempts are hobby heuristics (`cs2-demo-coach` "decision simulation"). Feasibility of credible alternatives is **unproven**.
4. **No validated automated-coaching→improvement study in esports.** The one behavioural study is n=3 / single behaviour (Street Fighter V). Our system cannot claim "improves your Elo" without our own trial.
5. **No CS2 similarity-search / round-embedding system.** ggViz and Durst are CS:GO and interactive/research-grade. A local, automatic "find pro rounds like mine" is unbuilt.
6. **No reproducible CS2 decision-quality metric.** Rating 3.0's Round Swing is close but proprietary and non-reproducible; DQI exists only for Go.
7. **Role→outcome causal link is null** (btp_cs2). Do not market role consistency as a win lever.
8. **Generalisation across patch/map is unproven.** Hasegawa shows map-dependent feature importance; CS:GO→CS2 transfer untested.
9. **Small-sample personalisation unaddressed.** All methods need 10⁴–10⁶ events; a single player has far fewer. Population-priors + shrinkage is the only viable route (see LongitudinalAnalysis/AIModelsArchCosts slices).
10. **No licensed, machine-readable, up-to-date CS2 match-metadata feed** (Liquipedia LPDB is approval-gated + CC-BY-SA; HLTV is proprietary; bo3.gg ToS-bound).
11. **No public benchmark for "coaching feedback quality"** in CS — no ground-truth expert error labels, no inter-rater dataset.
12. **Video/state alignment pipelines exist but footage rights (Valve) block commercial redistribution.**
13. **Fog-of-war / information-asymmetry-aware models are absent** — every cited model sees full global state, not player-visible state, so "was this decision wrong *given what the player could see*" is unmodelled.

---

## 10. Cross-cutting notes (gaps & duplicate work in my cluster)

- **Duplicate-work risk with siblings:**
  - *Xenopoulos 2020 WPA* and *ESTA* are likely also cited by `EcosystemSurvey.ApisData` (data sources) and `EcosystemSurvey.ParsersLibs` (awpy). Coordinate: ESTA's **awpy 1.3.1 pin vs awpy 2.x CS2 tooling** is an architecture-level conflict both slices must agree on.
  - *Rating 3.0 / metrics* may overlap `EcosystemSurvey.VendorApps` (Leetify/Scope.gg). I focused on the **literature critique**, they should own the vendor measurement specifics.
  - *Fog-of-war* is explicitly owned by `DemoDataFogOfWar`; my gap #13 hands that off.
  - *Small-sample / Bayesian shrinkage* owned by `LongitudinalAnalysis`; I only flag it.
  - *Mistake taxonomy* owned by `MistakeTaxonomy`; my §2.7 (DQI / Tetris error types / SC2 divergence) is the academic input to that taxonomy — they should own the final enum.
- **Gaps discovered in the academic literature relevant to the whole project:**
  1. The CS literature is a **CS:GO corpus**; CS2 work is 2024–2026 and mostly theses/hobby repos. Any "prior art" claim in our design must be checked against CS2, not CS:GO.
  2. There is **no accepted, reproducible decision-quality ground truth** for CS — evaluation of our system needs *expert error coding*, which does not yet exist as a public dataset.
  3. **LLM-coaching academic depth is thin**: the strongest results are in non-esports domains (Minecraft, running), and esports coaching studies are qualitative/observational. Expect to build evaluation ourselves.
  4. **A reusable, license-clean, CS2-native, round-level dataset does not exist.** We will likely generate our own from demos via awpy 2.x; ESTA is CS:GO-only, Packer is player-aggregate, VOR.TECH is bots.
  5. **Method availability vs. method validity:** WPA/clustering/similarity are *reusable*; IRL/counterfactual-optimal are *research-generating*. Budget accordingly.

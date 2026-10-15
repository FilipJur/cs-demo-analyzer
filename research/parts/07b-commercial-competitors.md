# §7b — Commercial "automated coach" competitors + published rating methodology (lead-verified)

Lead-verified 2026-10-15 by opening the live product pages and the vendors' own methodology
articles. These are the products that already sell the thing we are considering building; their
*stated* capabilities are the competitive baseline, and their *stated gaps* are our opening.
(Relates to §2 vendor apps; dedupe on merge.)

---

## 7b.1 PureSkill.gg — "the automated coach that tells you what to fix first"

- **Site:** https://pureskill.gg/ (app: https://csgo.pureskill.gg) · team page claims "three physicists who play CS" · building since **2018**.
- **Positioning (verbatim):** *"Coach reviews your Premier and FACEIT matches after you play, finds the mistakes that actually cost rounds, and shows you the exact moment in a 2D replay. No stat dumps. No downloads. Never a cheat."* Their own comparison table contrasts "stats websites" (every metric where you were slightly below average) with Coach (**"a short, prioritized list of what to fix first"**, judged as *"individual mistakes, detected round by round"*, with *"jump to the moment in the 2D viewer and see it yourself"* as proof).
- **Assessment taxonomy and counts (from the landing page — useful as a feature checklist / coverage denominator):**
  | Category | # assessments | Examples given |
  |---|---:|---|
  | Economy | 12 | First-round buys, save-or-force, kevlar, kits, drops |
  | Grenades | 8 | Smokes that land, flashes that blind enemies not teammates, HE/molotov damage |
  | Shooting | 6 | Headshots, first-shot accuracy, spray length, recoil resets, stopping before shooting, **shooting teammates** |
  | Teamwork | 4 | Trades, **missed trade opportunities**, whether your team traded your deaths, coordinated utility |
  | Movement | 3 | Counter-strafing, movement before engagement, speed out of spawn |
  | Other mistakes | "growing" | "habits that do not fit a category yet. Coach is always learning to spot new ones." |
  | **Total advertised:** 30+ graded assessments per match |
- **Explicitly NOT shipped:** *"Coming soon — **Crosshair placement** … **Decision making**: Rotate or hold? Peek or reload? The choices that decide rounds."*
  → **This is the single most important competitive data point in this whole report.** The leading 7-year-old automated CS coach advertises *decision-making evaluation and crosshair placement as unshipped roadmap items*, and an "others" bucket that is explicitly not solved. Our target system's core differentiator is exactly their roadmap.
- **Ops:** auto-downloads Premier + FACEIT matches after the match ends; 2D viewer; manual upload; nothing runs in-game; account linking via Steam, plus Steam↔FACEIT linking.
- **Pricing:** Free tier (Coach, 2D viewer, manual uploads, auto-analysed Steam matches); **Pro $3.75/mo billed annually or $5/mo** (extended demo download, pro tips, Discord, "rank-up guarantee"); Lifetime MVP $299.
- **AI real or marketing?** The word "AI" is *not* used; it is described as a **rule/assessment engine** ("30+ assessments", "individual mistakes, detected round by round", "Coach is always learning to spot new ones"). Treat as deterministic heuristics + priorities. **Category: Demonstrated product, undisclosed method.**
- **What to take:** their *prioritisation* framing ("what to fix first", limited list, drill for that exact mistake) and their category taxonomy are the best available public specification of what a personal coaching product must cover. Their *unshipped* decision-making module is our wedge.

## 7b.2 CSReplays — round-anchored coaching + pro lineup matching (web, closed)

- **Site:** https://csreplays.com/ · Steam OAuth · pricing page `/$9.99/mo` Pro.
- **Claims (verbatim from landing page):** *"Upload a CS2 demo. Get round-anchored coaching grounded in real timestamps and util lineups — not generic 'improve your aim.'"*
  - **Coach:** *"Mistakes, pinpointed — Round-referenced feedback grounded in real timestamps: **you re-peeked the same angle three rounds after dying to it.** Never generic 'improve your aim.'"*
  - **Lineups:** *"Util named, not guessed — Smokes and mollies are matched against **per-map lineup catalogs** — the exact 'Mid-to-A executive', with a reference clip — not 'a smoke somewhere on A.'"*
  - **Replay:** every round on the radar, scrub rotations/smokes/mollies/duels frame by frame, side-coloured, kill markers + bomb plants on the timeline.
  - **Trends** across multiple matches (ADR delta, opening-duel %, utility thrown/round) and stacks/Discord sharing via shareable analysis URLs.
- **Ops:** 100% web, no installer, "nothing in your CS2 install touches our service"; demo privacy "stored encrypted, scoped to your account, deletable any time. **Never used to train models**"; free 10 analyses/month; Pro = auto-sync via Steam (~10 min after leaving the server), unlimited analyses. Explicitly positions against Leetify ("a K/D number won't tell you that you peeked the same angle three rounds in a row — watching the replay does").
- **Verified external facts on the site:** *"Valve only keeps demos ~8 days"* (important acquisition constraint); FACEIT/ESEA demos work by upload with a pasted steamid64 (auto-detect is Valve-filename-only).
- **Why it matters:** **repeat-mistake detection across rounds is already a marketed feature** ("you re-peeked the same angle three rounds after dying to it") — i.e. our "unconscious habit detection" has a live commercial antecedent. It is **closed-source** (no repo, no API, no license) → **cannot be reused or integrated**; benchmark target only.
- **Unsolved/open:** no published method, no evaluations, and the "same angle three rounds later" claim is, as far as the public record shows, an unvalidated heuristic.

## 7b.3 ReplayLab (replaylab.pro) — includes an *in-product 3D "what could you see" view*

- **Site:** https://replaylab.pro/?lang=en (UI currently Russian; English "planned").
- **Features (from the product page):** 2D replay (positions, kills, utility, round flow, **team voice chat**); **"Why you died"** analysis — isolation from teammates, **repeat peeks**, untradeable positions, poor spacing/trade potential; **duel analysis** — *who saw whom first*, crosshair proximity, aim angle, prefire timing, and whether a teammate could have traded you; **3D player-eye view — "reconstructs what the player could see at a specific moment"**; **Coach mode** (map drawing + shared review rooms); opponent scouting (positioning, utility, opening tendencies); **progress tracking of recurring mistakes** across matches; FACEIT support accepting `.dem.gz`, `.zst`, `.zip` archives directly.
- **Pricing:** Free = 3 demo uploads/day + 1 trial AI review; **Pro $8.99/mo or $99/yr** = 20 uploads/day, 10 AI reviews/month, unlimited storage.
- **Why it matters:** two of our three differentiators — **"who saw whom first"** (the `enemy_spotted` primitive) and a **player-perspective visibility reconstruction** — are already shipped in a commercial viewer. So visibility reconstruction must be treated as an **integration/engineering task, not a research risk**. Second: an **"AI review" is metered as a separate, limited resource**, implying an LLM (or expensive model) sits behind a quota — consistent with our commercial-API plan.
- **Caveats on the page itself (worth quoting in any design doc):** it *self-describes* the analysis as judgement, not proof: conclusions such as "you should have been traded" are *"analytical judgments based on player positions and timing — not proof that a specific play was objectively incorrect."* That is exactly the epistemics our evidence-grounding must handle.
- **Reuse:** closed, no API/repo → **ignore for integration**, mine for feature/UX ideas.

## 7b.4 Skybox.gg → "Skybox EDGE" — still live (contrary to community claims)

- **Site:** https://skybox.gg/ · product: https://skybox.gg/edge/ · pricing: https://skybox.gg/pricing/ · terms: https://edge.skybox.gg/terms
- **Status 2026-10-15:** live, open access, rebranded **Skybox EDGE**. Free individual tier = player stats, leaderboards, match reports and a **2D replayer** (public demos may have a **one-month delay** on free); Pro = instant public-demo access; higher team tiers. **POV demo upload** is documented in their FAQ (i.e. client-side POV demos are supported).
- **Note:** community posts claiming Skybox "died" are contradicted by their live site/pricing pages — flag the discrepancy, don't repeat the rumour. **Category: Demonstrated, commercial, closed.**
- Relevance: legacy dataset/analytics provider in the same space; also the original "pro demo" analytics brand. Ignore for integration; useful as a market-status reference.

## 7b.5 Leetify — the only competitor that has *published* its rating mathematics

- **Sources:** https://leetify.com/blog/leetify-rating-explained/ · https://leetify.com/blog/cs2-benchmarks/ · https://leetify.com/blog/utility-ratings/ · https://leetify.com/blog/leetify-stats-glossary/ · update notes https://leetify.com/blog/leetify-rating-update/ and https://leetify.com/blog/leetify-rating-update-2026-02-25/
- **Leetify Rating (LR) = a round win-probability impact model, not a stat composite.** Per round, the model estimates the team's win probability and measures how events change it; match LR is the average round impact, and it is **zero-sum within the match** (credit to one side is debit to the other). Events that move probability: kills, deaths, damage before death, flash assists, being traded, saving weapons, round objectives, clutches.
  - **Kill credit split (published defaults):** killer 35%, players who damaged the victim 30%, flash-assist receiver 15%, player whose death was traded 20% — absent contributors' shares are redistributed; the dying player takes the negative.
  - Kill value is context-dependent: a 5v1 kill is worth little, a 1v1 kill a lot; killing a strong-buy enemy with weak equipment is worth more.
  - **Model state:** recalibrated on **professional CS2 data**; since the **2024-11-25** update it uses simplified equipment-value economy groups and processes kills individually while remembering which side took the previous kill. **2026-02-25** change: reduced the reward for certain 1v1 clutch wins by **~5%** on average and fixed a post-plant bug that punished Ts for dying when the bomb later exploded.
- **Aim / Positioning / Utility ratings are separate 0–100 benchmark scores** (explicitly *not* additive components of LR):
  - Method: compute raw stat → compare to benchmark population → **z-score** → combine → map to 0–100; ~50 ≈ average for the benchmark. Aim uses the Aim-tab stats **except Accuracy (All Shots)** (excluded because it includes wallbangs/smoke spam), equally weighted; it favours **"shots fired while an enemy is actually visible"** — i.e. *visibility-aware* aim metrics.
  - **Utility Rating = geometric mean of Quantity and Quality.** Quantity = `min((grenades/round / 3)^(2/3), 1) × 100` (decoys excluded; e.g. 1/round ≈ 48, 2/round ≈ 76, ≥3 → 100). Quality = `normal_CDF(combined z-score) × 100` over six stats: flash-assist %, enemies flashed per flashbang, **teammates flashed per flashbang**, average blind time per flash, average HE damage per HE, average **team damage** per HE — negative stats have their sign reversed. Final `Utility = sqrt(Quantity × Quality)` so both "enough" and "useful" are required.
  - Positioning Rating's complete input list/weights are **not fully disclosed**; it is described as a relative benchmark of fight-selection/trading behaviour.
- **Why this is the most reusable thing in this section:** LR is a **published WPA-style decision/impact model for CS2** (including credit attribution across killer/damagers/flasher/traded player and objective/save terms), and the utility/aim composites show exactly how to normalise stats into interpretable 0–100 scales with z-scores and a normal CDF. Our "decision quality" metric can adopt this framing directly, with the important caveat that the benchmarks and the underlying win-probability model are **closed** (we must fit our own on local/pro data).
- **Known limitation for us:** LR is *outcome*-based (win-probability deltas from observed events). It cannot say "the *alternative* decision was better", and it inherits all of the underlying win-probability model's biases. It also has no visibility/fog-of-war input beyond "enemy is spotted".

## 7b.6 Scope.gg — the largest incumbent (status check for completeness)

- **Site:** https://scope.gg/ · app https://app.scope.gg · Steam **and** FACEIT login · self-reported **2 M registered users, ~10 000 players/month**.
- **Feature surface (from the live landing page / nav):** "performance review" that *"analyz[es] your matches and point[s] out the mistakes"* and *"sum[s] up the mistakes after every match and show[s] how to fix them"*; map-position practice tips; **automatically recorded highlight clips**; **2D demo viewer/replay**; player comparison; match tracker/scoreboard; utility-usage map; **CS2 lineups / grenade predictor**; **tactical board** (`app.scope.gg/strategy`); **prematch analytics**; FACEIT stats pages; aim/headshot stats; dashboard; match history. Stats quoted in their FAQ: K/D, ADR, **HLTV Rating 2.1**, AIM and grenade stats, headshot hits as well as kills.
- **Assessment:** the broadest incumbent. **Category: Demonstrated, commercial, closed.** Notably it ships a **tactical board** and **grenade predictor** alongside replay — relevant UX precedents for a coaching product. No public API documented on the landing page (see §3 for API side); no published mistake-detection methodology → **"mistake" claims here are undisclosed heuristics**, exactly the ambiguity we should resolve in our own design.

## 7b.7 Cross-cutting notes for the commercial layer

1. **The market already sells "mistake detection + largest-impact-first priorities"** (PureSkill 30+ assessments since 2018; Scope "mistakes after every match"; CSReplays "round-anchored"; ReplayLab "why you died"). Any claim that this category is empty is false.
2. **The market has NOT shipped decision-quality evaluation.** PureSkill lists *"Decision making: rotate or hold? peek or reload?"* as **coming soon**; Leetify's LR is outcome-impact, not counterfactual; nobody publishes an evaluation of their coaching.
3. **Visibility reconstruction is shipped commercially** (ReplayLab: "3D player-eye view… what the player could see"; "who saw whom first") but **no vendor documents how**, and only CS2DemoKit/awpy provide an open primitive. Integration, not research.
4. **Published methodology is rare and valuable:** Leetify is the outlier that documents its model (LR credit splits, z-score→0–100 for aim/utility, geometric-mean utility, normal-CDF quality, calibration updates with dates). Copy the *framing* (impact on win probability + normalised skill profiles) but re-fit the model locally; the benchmarks are closed and the model is proprietary.
5. **Pricing anchors for our own cost model:** Leetify ~$$$ subscription; Scope tiered; **PureSkill Pro $3.75–5/mo**; **CSReplays $9.99/mo**; **ReplayLab $8.99/mo ($99/yr)** with **AI reviews metered separately** (10/month) — evidence that per-match LLM inference is the limiting cost in a coaching product.
6. **Privacy is a marketed differentiator** (CSReplays: "never used to train models"; PureSkill: "never a cheat", "no installs"; ReplayLab's caveat about judgement-not-proof). Local-first processing is therefore a *feature*, not just an architecture choice — and it is exactly what the incumbent SaaS products cannot claim.

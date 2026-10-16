# Decision Evaluation, Review Methodology & False Positives — Research Summary

**Status:** research only. No AI, no mistake classifiers, no evaluation code, no application features.
**Scope:** what evidence is required to judge whether an individual CS2 action was reasonable, questionable, or genuinely mistaken — and when judgment must be withheld.
**Output dir (exclusive):** `research/gameplay/04-decision-evaluation/`. Parent `research/gameplay/` index intentionally untouched.

## Navigation

- `review-methodology.md` — what expert coaches/analysts verifiably do before criticizing a play, how they separate execution from decision, and the 8-step evidence-oriented review sequence (fragments source-grounded, whole explicitly **not** validated).
- `casebook.md` — 11 traceable review cases (`EVAL-001`–`EVAL-011`) covering all 8 required types. Every case separates **observed facts → plausible interpretation → alternative explanation → supporting evidence → contradictory evidence → judgment eligibility**. Sourced cases carry revisit information; hypotheticals are labelled as such.
- `judgment-criteria.md` — evidence tiers mapped to the app's `EvidenceKind` vocabulary, per-question evidence classification, the 13-behavior must-know/withhold table, 8 mandatory abstention criteria, and the Q3 counterfactual test.
- `sources.md` — annotated bibliography with credibility, read status, and limitations. Vendor content quarantined as `VENDOR-UNVERIFIED`.

## Central question (the standard this research serves)

> Given the player's likely responsibilities, available information, actual situation, and realistic alternatives, is there sufficient evidence that a different decision was preferable?

A future reviewer must not ask "did this action fail?" — it must earn the harder question above, or withhold judgment.

## Key findings

1. **No peer-reviewed study of CS demo-review methodology exists.** Review ordering, root-cause-vs-symptom, and habit-detection are workflow preferences, not validated methods (`Plausible-untested`, absence established by prior-slice search). Any sequence herein is convergent practice, not validated methodology.
2. **The strongest single datum is a withhold, not a method.** Spirit coach hally (Major winner, BLAST.tv 2024-08-10): *"Some of the movements can't be judged even by watching demos because you need to hear the flow of communication."* A demo-only reviewer is indeterminate for a whole class of movement decisions. **Demonstrated.**
3. **Instruction-only debiasing fails; structure works.** Telling a reviewer "ignore the outcome" does not reduce hindsight bias (Guilbault et al. 2004 meta-analysis). The only consistently supported tactic is forced consider-the-opposite with ≤3 alternatives (Roese & Vohs 2012), plus capturing the prediction *before* the outcome is known. A "hide result" toggle without forced alternative-generation is predicted ineffective. **Research-supported.**
4. **Deaths-only review is outcome-driven learning institutionalized.** It examines Q3 (good decision, bad outcome — must NOT be "fixed") and Q4 while Q2 (bad decision, lucky outcome) escapes entirely (Duke 2×2 matrix). Won rounds are aviation's near-misses: ASRS-style review codes *recovery factors* — why a round was won *despite* the error. **Research-supported.**
5. **Role makes identical observations opposite verdicts.** HLTV's trade-structure analysis: lurkers and ahead-of-pack players "are less likely to both be traded or to trade a teammate"; HLTV Attributes casts high-entry/low-trade as *sacrificial entry* and the inverse as *trademark baiter*. Flagging every untraded death mislabels correct role play by construction.
6. **"Additional information" never rescues a verdict without recorded evidence.** Romer (JPE 2006, read in full) tested the coaches-know-more defense at scale and rejected it; proxy baselines were validated numerically (mean diff 0.006, SE 0.7) before use. "He saw something we can't" is outcome-backfill unless the reviewer can point at a recorded field. **Demonstrated** transfer rule.
7. **Reference populations must be named or they smuggle selection in.** Standard xG underestimated Messi's GAX by 17% because the "average player" baseline tilted toward frequent shooters (Davis & Robberechts, read in full). Any CS "average decision" baseline trained on observed (mostly pro, mostly action) data tilts toward the least-average players. **Demonstrated** mechanism.
8. **Abstentions are structurally missing data.** xG is computed only over shots taken; an action-only review can never credit a disciplined save, refused repeek, or held rotation. Credit requires longitudinal recurrence (habit = recurrent + consistent + consequential + context-bound), never single-instance mind-reading.
9. **Counterfactuals are model outputs, never ground truth.** EV-lost figures need a named reference policy, a validated proxy, and stated uncertainty — or the reviewer withholds. The unobserved alternative is the fundamental problem of causal inference, not a gap to narrate over.
10. **Experts disagree, and the disagreement is data.** Trajectory readers (Mauisnake, YNk on Falcons pre-Cologne 2026) vs results-readers; Telestrator-format dispute (YNk vs Thorin/Lewis); Jame's save-heavy MVP run praised and attacked simultaneously. Preserved in `casebook.md`, never resolved by fiat.

## Findings report: misleading conventional coaching advice

Literal obedience to each slogan below punishes correct play. Full evidence in `judgment-criteria.md` §4 and `casebook.md`.

| # | Slogan | Why it misleads | Strongest counter-evidence |
|---|---|---|---|
| 1 | "Always trade" | Entries, lurkers, AWPers are structurally untraded; flagging every untraded death fails correct role play | HLTV trade-structure + Attributes framing (**Demonstrated** snippet) |
| 2 | "ADR/KAST tells the story" | Rewards eco-farming, buries role work | HLTV built Rating 3.0 to "reduce the impact of eco frags" — EliGE 133 ADR half scored 2.06 under 2.1, 1.40 under 3.0 |
| 3 | "Never save" | Burns next-round win probability; MR12 concentrates round value | Jame's save-heavy IEM Rio 2022 MVP run — championship-correct saving |
| 4 | "Never repeek" | Conflates committing repeeks with free info jiggles; no peer-reviewed CS repeek study exists | No reviewer can apply it honestly without the peek-1→peek-2 info delta, which demos rarely resolve |
| 5 | "Always rotate fast" | Dies to every fake; most hindsight-contaminated judgment in the set — rotation speed judged from omniscient replay without the listener's info set is outcome bias by construction | Baron & Hershey 1988 transfer (**Research-supported**); fake-patience is slow *correctly* |

## Evidence grades (used in all four files)

**Demonstrated** (primary artifact read) · **Experimental** (single controlled study) · **Research-supported** (multiple studies/reviews, mostly observational) · **Plausible-untested** (reasoned, no direct CS evidence) · **Infeasible** (ruled out by recorded fact). `VENDOR-UNVERIFIED` = vendor/SEO content: admissible as "what coaches claim they check", never as evidence a method works.

## Relationship to prior work (built on, not redone)

- `research/muse/D-mistakes.md` — 52-class taxonomy, fact-vs-verdict split, T0/T1/T2 valuation tiers, smoke/info blockers.
- `research/muse/G-coaching-eval.md` §13 + `parts/g-coaching/` — coach interviews, outcome/hindsight bias science, aim-plateau evidence, demo-integrity limits.
- `research/muse/C-data-fogofwar.md` — demo field inventory, spotted-mask traps, smoke voxels only via cs2parser, `player_sound` radius, no MM voice, team chat encrypted 2026-09-09.
- `research/muse/E-longitudinal.md` — habit criteria (recurrent + consistent + consequential + context-bound), small-n/multiplicity discipline.
- `research/muse/parts/g-coaching/feedback-efficacy.md` — 38% of feedback interventions hurt; high-information feedback d≈0.99; DIVAT/EV analogues.
- `research/gameplay/01-modern-meta/` — role-as-situational-responsibility, CT-ward meta, trading opportunity→attempt→success.
- App models consulted read-only: `domain/evidence.py` (`EvidenceKind`), `domain/context.py` (omniscient scope, no awareness claims), `domain/encounters.py` (event-grouped episodes).

## Open questions

1. Does any pro team practice strict outcome-blind review (prediction capture)? Repeeks, dry peeks, utility-in-hand drew zero named-coach process gradings — the thinnest evidence in the set.
2. Man-advantage conversion baselines and MR12 save-threshold shifts: discourse confirmed, numbers unrecovered (HLTV bodies rate-limited on access date; retry).
3. Timestamped VOD+demo pairs still needed for the late-rotation, repeek, dry-peek, map-control, and utility-in-hand justified variants.
4. Same-situation/different-outcome paired comparison: zero verified analyst-VOD precedents retrieved — the highest-value missing artifact.

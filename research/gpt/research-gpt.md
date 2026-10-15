# AI-powered CS2 coaching: feasibility and architecture research

Research assessment · 15 October 2026 · Local-first application, hosted AI inference

## A. Executive feasibility assessment

The project is technically feasible, but approximating an excellent human coach requires solving a substantially harder problem than parsing demos or generating AI commentary.

The current ecosystem already provides several foundational capabilities: fast CS2 demo parsing, player trajectories, combat events, map geometry, line-of-sight calculations, navigation data, and interactive replay viewers. Awpy and demoparser2 are particularly relevant, while CS Demo Manager demonstrates that local demo acquisition and analysis workflows are practical.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

+2

The central obstacle is determining whether a decision was reasonable given the information available to the player, rather than judging it from an omniscient replay.

Feasibility by capability

Research assessment, not benchmark results

Demo parsing and match history

High

Mechanical and positional measurements

High

Detection of narrowly defined mistakes

High

Recurring behavioral-pattern discovery

Partial

Player information-state reconstruction

Partial

Contextual tactical judgment

Unproven

Reliable human-coach equivalence

Unproven

These qualitative feasibility estimates are engineering judgments, not measured success rates.

The most credible initial product is a personal behavioral-analysis engine with AI-assisted investigation, rather than an AI that independently understands every tactical situation.

It should be capable of discovering patterns such as repeated unsupported engagements, poor spacing, questionable repeeks, and avoidable exposure. Whether these are mistakes must be established through contextual evidence and validation.

There are three important distinctions:

- Measurable behavior: The player exposed themselves to two sightlines, or had no teammate within a plausible trading position.
- Potential mistake: The exposure created unnecessary risk given the round's objectives and available information.
- Coach-quality judgment: The player should have chosen an alternative because it offered a better expected outcome, considering viable choices, timing, communication, and opponents.

The first is largely an engineering problem. The second requires contextual modeling. The third remains a research and evaluation problem.

My preliminary recommendation is to make recurring, evidence-backed behaviors the core product and treat AI tactical judgments as hypotheses until independently validated.

## B. State-of-the-art landscape

### 1. The strongest reusable foundations

| Project                                                            | What is demonstrably useful                                                                | Reuse assessment                                     |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| [demoparser2](https://github.com/LaihoE/demoparser)                | Rust-backed CS2 parser with Python, JavaScript and WASM interfaces; event and tick queries | Primary parsing candidate                            |
| [Awpy](https://github.com/pnxenopoulos/awpy)                       | Parsing, statistics, navigation, map geometry, visibility checks, heatmaps                 | Primary analytical foundation                        |
| [CS Demo Manager](https://github.com/akiver/cs-demo-manager)       | Match database, Valve/FACEIT-related acquisition, statistics, 2D replays, exports          | Strong reference implementation                      |
| [CS2d.app](https://github.com/zenojunior/cs2d)                     | Client-side 2D replay, grenades, sound, annotations, heatmaps                              | Strong viewer candidate; license needs clarification |
| [CS2 Demo Review](https://www.eastern.sh/projects/cs2-demo-review) | Browser-side parsing, conversational questions, heatmaps and annotated replays             | Particularly relevant AI interface reference         |
| [awpy-data](https://github.com/pnxenopoulos/awpy-data)             | Versioned radar imagery, collision geometry and navigation meshes                          | Critical map-data pipeline                           |

These are working codebases or published implementations, not merely proposed systems. Awpy itself uses LaihoE's parsing backend, so the first two are complementary rather than independent parser alternatives.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

+5

The strongest starting point is demoparser2 plus Awpy, with a separate local database and coaching layer.

There are two implementation caveats worth addressing early.

First, an open Awpy issue from March 2026 reports failure to parse navigation-file version 36. This could break routing and map-control analysis on affected current maps; compatibility must be tested rather than assumed.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

Second, CS2d's public repository provides source code but does not visibly declare a repository-wide software license. Public source access alone does not authorize wholesale reuse. Confirm licensing with its author before incorporating the viewer.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

### 2. Existing AI coaching systems

The competitive landscape is more developed than a simple parser-plus-ChatGPT prototype would suggest.

| System                                        | Relevant functionality                                                        | What remains unproven                                  |
| --------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ |
| [PureSkill.gg](https://pureskill.gg/)         | Automatic match coaching, 30+ assessments, prioritized mistakes, replay links | Expert-level counterfactual tactical reasoning         |
| [ReplayLab](https://replaylab.pro/?lang=en)   | Isolation, repeeks, tradeability, positioning and aim-at-contact analysis     | Robustness across roles and ambiguous decisions        |
| [CSReplays](https://csreplays.com/)           | AI reports, automatic syncing, role classifiers, interactive replays          | Whether coaching consistently matches expert reviewers |
| [mLkoach](https://mlkoach.com/en/)            | Round-impact estimates, mechanical metrics, recurring weakness reports        | Whether impact estimates establish decision quality    |
| [Scope.gg](https://scope.gg/replay/)          | Automatic downloads, browser replays, full-match timelines                    | Deeper behavioral diagnosis                            |
| [Leetify](https://leetify.com/)               | Large-scale mechanical, positional and utility performance measurements       | Open access to its underlying analysis                 |
| [Mercurial.gg](https://mercurial.gg/releases) | AI coaching linked to calculated performance metrics and specific rounds      | Independent evaluation of its coaching accuracy        |

Product features above are drawn from provider documentation, not independently verified accuracy experiments.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://pureskill.gg&sz=32)

Automated coach for Counter-Strike 2

+5

Three projects deserve particular attention.

ReplayLab already advertises several of the same incident categories proposed for this project: isolation, repeated peeking, untradeable positions, crosshair position at contact and positional context. That makes it an unusually relevant functional reference, not just a statistics competitor.

CSReplays has published concrete engineering discussions of its demo-to-report pipeline, timing heuristics, role classification and use of professional gameplay as AI reference material. These are worth studying before designing the representation layer.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://csreplays.com&sz=32)

AI demo coach for CS2

+1

PureSkill.gg documents a deliberately hybrid system combining statistics, ML and coaching assessments. Its published examples include moving while shooting, insufficient trading support and incorrect equipment purchases. This provides evidence that useful coaching can begin with narrowly scoped, interpretable detectors.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://pureskill.gg&sz=32)

Automated coach for Counter-Strike 2

+1

### 3. Research prototypes and machine learning

Two academic directions are especially relevant.

Temporal graph-based tactical analysis

A 2025 MIT Sloan Sports Analytics Conference paper by Szmida and Toka, Evaluating Player Actions in Professional Counter Strike using Temporal Heterogeneous Graph Neural Networks, describes representing the game as a time-varying graph of entities and interactions. The reported frame-level round-win prediction accuracy exceeds 76%. This supports the feasibility of learning meaningful spatial-temporal representations.

However, predicting whether a team wins is not equivalent to determining whether one player's decision was optimal. A model may predict the outcome using information unavailable to the player.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.researchgate.net&sz=32)

researchgate.net

Long-term behavioral fingerprints

The August 2026 paper Same-Player Verification for Account Consistency in Counter-Strike 2 uses 1,330 demos and 13,300 player-match observations to measure stable behavior in aim, movement, firing rhythm, economy and engagement patterns. Its reported pairwise ROC AUC is 0.931.

This is directly relevant to your goal of finding unconscious habits: repeated behavioral tendencies are measurable across demos. But the paper establishes behavioral consistency for player identification, not that an unusual habit is objectively bad.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://arxiv.org&sz=32)

arxiv.org

A third useful reference is Learning to Move Like Professional Counter-Strike Players (2024), which trained a team-movement transformer on 123 hours of professional CS:GO gameplay. It demonstrates that team trajectories can be modeled, while also showing the difficulty of transferring a specialized scenario-based system into general match coaching.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://arxiv.org&sz=32)

arxiv.org

Research conclusion: Statistical modeling and machine learning can discover and compare behavioral patterns. There is not yet sufficient evidence from these publications to claim reliable, general-purpose automated CS2 coaching.

## C. Demo acquisition, extraction and automation

### 1. Automatic acquisition

The desired pipeline is achievable in principle, but FACEIT and Valve require different acquisition adapters.

Match discovery

FACEIT API / Valve match history / watched local directory

FACEIT

Match API → demo-ready notification or polling → authorized signed URL

Valve / Premier

Steam account and Game Coordinator integration, or local/manual import

Local acquisition queue

Download · verify · decompress · deduplicate · retry failures

Parser → normalized events → analytics → AI coaching → local report

#### FACEIT

The official FACEIT documentation confirms that match responses can expose demo resource URLs, its Downloads API can exchange them for signed URLs, and its event-notification system supports a `Match Demo Ready` webhook.

But access to the Downloads API requires applying for authorization, with an expected application-response time of 30 days. It also requires a separately scoped access token.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.faceit.com&sz=32)

FACEIT for Developers

+1

Therefore:

- Match discovery using the Data API is a reasonable first implementation.
- Authorized demo download is a strong path if access is approved.
- Webhooks may eliminate unnecessary polling, subject to event-subscription permissions.
- Without download authorization, an automatic fallback cannot be guaranteed merely because another provider uses one.

I would not base the project's viability on obtaining this permission. Build local import first and keep acquisition as a replaceable component.

#### Valve and Premier

CS Demo Manager implements Valve demo acquisition, including interaction with Steam's Game Coordinator. Its GitHub history confirms working acquisition functionality and also documents authentication-related operational problems.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

+1

This supports the feasibility of a local integration, but is not evidence of a stable, unrestricted public REST API for downloading Premier demos.

Recommendation: Investigate reusing the CS Demo Manager acquisition implementation before writing a new Steam/Game Coordinator client. Preserve manual share-code and file-import fallbacks.

An optional file watcher should detect completed `.dem`, `.gz`, `.zip`, or other supported compressed files, wait for file size to stabilize, and then ingest them. That avoids network authentication entirely for already-downloaded demos.

For reliability, maintain a small job-state machine:

`discovered → waiting_for_demo → downloading → verified → parsed → analyzed`

Each job should have retry metadata, provider identity, content hash, parser version and an explicit terminal error. Use match IDs for provider deduplication and file hashes for content deduplication.

Verdict: Automatic ingestion is feasible, with provider-dependent restrictions. It should not block the analytical MVP.

### 2. What CS2 demos expose

The parser and Awpy documentation confirms availability of substantial event and tick-level data.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

+2

| Information                              | Availability              | Qualification                                         |
| ---------------------------------------- | ------------------------- | ----------------------------------------------------- |
| Player positions, eye angles, velocities | Direct or derivable       | Sampling and parser fidelity matter                   |
| Kills, damage, hitgroups, weapon fire    | Direct events             | Precise perceived timing may differ                   |
| Inventory, money, equipment, buys        | Mostly available          | Purchase reconstruction needs validation              |
| Grenade throws, travel, detonations      | Available                 | Full effects may require simulation                   |
| Flashes and blindness                    | Recorded state/events     | Whether a player could act still needs context        |
| Smokes, fire and utility effects         | Events/state              | Exact visual obscuration needs additional modeling    |
| Teammate and enemy locations             | Available omnisciently    | Not necessarily known to the player                   |
| View direction and crosshair alignment   | Available or derivable    | Model geometry and pose affect accuracy               |
| Line of sight                            | Computable                | Not simply an existing demo field                     |
| Player spotting                          | Some recorded properties  | Not a complete memory or awareness model              |
| Sound actually perceived                 | Not fully reconstructable | Rendering, occlusion and player audio settings matter |
| Team communication                       | Sometimes recoverable     | In-game voice may exist; external Discord does not    |
| Intent, attention and understanding      | Not directly recorded     | Cannot be inferred with certainty                     |

There is a particularly important development from November 4, 2025: Valve introduced TrueView demo playback, which reruns client-side prediction to approximate the original player's experience more closely. Valve explicitly warns that some visual timing differences remain and that game-version mismatches can disable the feature.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://store.steampowered.com&sz=32)

store.steampowered.com

This makes official CS2 playback a valuable reference for validating controversial mechanical incidents.

It does not turn an ordinary parsed demo into a perfect recording of attention, awareness, sound, or communication.

### 3. Reconstructing the player's information state

A useful state reconstruction should maintain two separate worlds.

Objective state: What the demo says happened, including every player and relevant event.

Belief-relevant state: What was reasonably available to the player at the moment of a decision.

I recommend an event-driven information ledger for each player:

| Evidence class               | Example                                        | Interpretation                                 |
| ---------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| Confirmed direct information | Enemy visible in unobstructed view             | Strong visual evidence, not proof of attention |
| Recorded game information    | Enemy shown on radar through team spotting     | Potentially available                          |
| Audible information          | Enemy movement within a modeled hearing region | Probabilistic without audio validation         |
| Historical information       | Enemy seen near Connector 6 seconds earlier    | Last-known position, increasingly stale        |
| Communication-dependent      | Teammate could have called an enemy location   | Unknown unless communications are recorded     |
| Hidden information           | Enemy silently moving elsewhere                | Must be excluded from the player's known state |

The information ledger should distinguish possible perception from actual perception. For example, a visible enemy at the edge of the screen might not have been consciously noticed.

Awpy's `VisibilityChecker` is useful here because it calculates ray intersections against collision geometry. Crucially, its own documentation states that it models static geometry only, not smokes, moving doors or penetration. It also warns that entity positions are not necessarily eye positions.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://awpy.readthedocs.io&sz=32)

Awpy

A realistic visual-exposure calculation needs eye-height and target-body approximations, view frustum, dynamic smoke occupancy, moving geometry where relevant, flash state and line-of-sight sampling.

For sound, the first version should use conservative audibility estimates, not claim to reconstruct exactly what the player heard. For communication, preserve uncertainty rather than invent a callout.

This leads to a key engineering rule: when a tactical judgment changes depending on an unobserved teammate call or an uncertain sound cue, report it as conditional, not definitive.

## D. Mistake-detection feasibility matrix

This is the core analytical scope.

The reliability labels below are prospective engineering expectations, assuming a correct parser and appropriately validated detectors. They are not measured accuracy figures.

| Mistake or behavior                    | Proposed detection evidence                             | AI need   | Expected reliability    | Coaching value |
| -------------------------------------- | ------------------------------------------------------- | --------- | ----------------------- | -------------- |
| Shooting while moving                  | Speed and weapon state at shot                          | None      | High                    | High           |
| Poor counter-strafing                  | Velocity and input transitions                          | None      | High                    | Medium–high    |
| Poor first-shot alignment              | Crosshair-to-target angular error                       | Optional  | Medium–high             | High           |
| Bad crosshair placement                | Aim trajectory versus plausible contact angles          | Optional  | Medium                  | High           |
| Poor angle-clearing sequence           | View-angle sweep and known sightlines                   | Useful    | Medium                  | High           |
| Unnecessary multi-angle exposure       | Multiple simultaneous threat sightlines                 | Useful    | Medium–high measurement | Very high      |
| Repeated repeeking                     | Same sightline after contact                            | Useful    | High behavior detection | Very high      |
| Untradeable positioning                | Teammate paths, distance, LOS and timing                | Useful    | Medium                  | Very high      |
| Poor entry spacing                     | Relative teammate trajectories and contact timing       | Optional  | Medium–high             | High           |
| Unsupported aggression                 | Engagement context, allies and objectives               | Important | Medium–low              | Very high      |
| Excessive passivity                    | Missed opportunities and time remaining                 | Important | Low–medium              | High           |
| Poor disengagement                     | Exposure following contact and escape paths             | Important | Medium–low              | Very high      |
| Abandoning map control                 | Region occupancy and team coverage                      | Important | Medium                  | High           |
| Bad rotations                          | Information timing and path selection                   | Important | Low–medium              | High           |
| Overextending with advantage           | State after gaining a numerical advantage               | Important | Medium                  | Very high      |
| Poor crossfires                        | Geometry, teammate LOS and simultaneous threat coverage | Useful    | Medium                  | High           |
| Weak repositioning after contact       | Repeated location and enemy knowledge                   | Useful    | Medium                  | High           |
| Questionable clutch or post-plant play | Bomb, time, utility, positions and belief state         | Essential | Low–medium              | Very high      |
| Utility wasted on death                | Inventory remaining at death                            | None      | High measurement        | Medium         |
| Bad utility timing                     | Effect windows versus engagements                       | Useful    | Medium                  | High           |
| Incorrect purchases                    | Economy, opponent buys and next-round expectations      | Useful    | Medium                  | Medium         |
| Poor save decisions                    | Equipment value, time, routes and win chances           | Essential | Low–medium              | High           |
| Failure to capitalize on information   | Known sightings versus subsequent actions               | Essential | Low                     | High           |

The crucial distinction is that detecting an observable behavior is often far more reliable than labeling it a mistake.

For example, a detector could establish that you repeeked the same angle 1.2 seconds after first contact. It cannot automatically establish that the repeek was wrong. You may have had teammate support, a flash, a favorable timing, or a deliberate plan to punish an opponent.

The best detectors should therefore generate review candidates, not unconditional accusations.

### Five detector families worth building first

1\. Unsupported engagements. Combine teammate distance, unobstructed trading paths, simultaneous exposure, round objective and nearby alternative cover.

2\. Repeeks after contact. Detect repeated exposure to the same opponent-controlled line, with time, utility, health and teammate-state context.

3\. Overextension after gaining advantage. Compare behavior before and after a first kill or another important advantage. Measure subsequent engagement choices without using the next duel's result as the label.

4\. Trade-spacing failures. Identify cases where teammates were moving together but a spacing or timing change left a plausible trade unavailable.

5\. Angle-isolation problems. Calculate how many opponent-accessible sightlines expose the player at each moment, and whether cover could have reduced that exposure.

These five offer a useful combination of measurable behavior, tactical significance and repeated opportunities across ordinary FACEIT matches.

### Why more advanced categories should wait

Rotation, clutch decisions, map-control abandonment and strategic utility decisions depend heavily on information, role assignment and team intent. For a solo player in unstructured matches, a seemingly incorrect rotation may have been a legitimate response to a teammate's communication.

A system lacking those inputs will frequently confuse disagreement with the player's decision for evidence of a mistake.

This is not solved by replacing a cheap language model with an expensive one.

## E. AI architecture and model selection

### 1. Which API models are worth testing?

As of October 2026, several providers offer capable reasoning models with large context windows, tool calling, and structured outputs.

| Model                         | Input / output per 1M tokens          | Proposed role                                   |
| ----------------------------- | ------------------------------------- | ----------------------------------------------- |
| OpenAI GPT-6 Luna             | $0.10 / $0.50                         | Cheap event screening and structured extraction |
| OpenAI GPT-6 Sol              | $2 / $10                              | Main tactical-analysis candidate                |
| OpenAI GPT-6 Astra            | $10 / $50                             | Difficult cases and evaluation reference        |
| Anthropic Claude Sonnet 5.5   | $2 / $10                              | Independent tactical-reasoning candidate        |
| Anthropic Claude Opus 5.5     | $4 / $20                              | Higher-capability comparison                    |
| Google Gemini 3 Flash         | $0.50 / $3                            | Low-cost multimodal analysis                    |
| Google Gemini 3.1 Pro Preview | $2 / $12 for inputs under 200k tokens | Large-context and visual-reasoning comparison   |

Prices are published standard text-token rates, excluding additional tool charges and applicable long-context surcharges. OpenAI and Google's referenced flagship models support approximately one-million-token contexts; that capacity should not be mistaken for a reason to fill the context with raw match telemetry.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developers.openai.com&sz=32)

OpenAI API

+2

I would benchmark GPT-6 Sol, Claude Sonnet 5.5, and Gemini 3.1 Pro first. Luna or Gemini Flash can handle low-cost screening. Astra and Opus are useful escalation candidates, but only if testing demonstrates a material improvement.

A conventional intelligence benchmark will not answer the relevant question. We need to measure whether a model can:

- Distinguish a questionable decision from an unlucky outcome.
- Reconstruct timing and relative positions accurately.
- Respect hidden information.
- Request missing evidence rather than fabricate it.
- Distinguish alternative interpretations.
- Produce explanations a skilled reviewer actually agrees with.

I found no sufficiently established, validated CS2 tactical-judgment benchmark to justify declaring any provider the winner. The project will need its own.

### 2. How gameplay should be represented

Do not provide a model with a giant JSON array of all player positions.

Instead, construct a hierarchical evidence representation:

Match summary

Map, sides, roles, economy patterns and major tendencies

Round-level timeline

Objective, utility, kills, sightings, map control and state transitions

Incident evidence window

Typically a short interval around a candidate decision, including events preceding it

On-demand precise evidence

Tick samples, individual trajectories, sightlines, cover, radar frame and belief history

A model-facing incident record might contain:

```
{
  "incident_id": "match42-round8-event3",
  "decision_tick": 184520,
  "round_state": {
    "side": "CT",
    "alive_ct": 5,
    "alive_t": 4,
    "bomb_state": "not_planted"
  },
  "player": {
    "health": 78,
    "weapon": "ak47",
    "position_region": "connector",
    "recent_contact": true
  },
  "observations": {
    "confirmed": ["enemy_sighted_at_tick_184410"],
    "inferred": ["enemy_may_still_hold_prior_angle"],
    "unknown": ["external_team_communications"]
  },
  "behavior": {
    "type": "repeat_exposure",
    "seconds_since_contact": 1.7,
    "potential_trade_support": false
  },
  "evidence_refs": [
    "trajectory:184300-184570",
    "visibility:184520",
    "teammate_positions:184520"
  ]
}
```

This is an illustrative application schema, not native parser output.

The model should receive verified facts with their provenance, along with uncertainty flags. Raw measurements, calculated relationships, statistical estimates and speculative interpretations should remain distinguishable.

An important architectural separation is to provide two contexts:

1. A decision-time context that includes only information available or plausibly inferable before the decision.
2. An outcome context that can be revealed afterward to assess consequences, not retroactively justify the judgment.

This protects against information leakage and outcome bias. In validation, deliberately test whether model conclusions change when outcome information is withheld.

### 3. Agentic evidence investigation

A tool-using model is a better fit than a one-shot prompt, provided its freedom is constrained.

For instance, an incident might initially look like an unsupported peek. Rather than immediately criticizing it, the model should be able to retrieve more context.

Potential callable tools:

| Tool                      | Data returned                                    |
| ------------------------- | ------------------------------------------------ |
| `get_round_context`       | Economy, team state, objectives and timeline     |
| `get_trajectory`          | Player paths, speed and view directions          |
| `get_observation_history` | Sightings and other player-available information |
| `get_visibility`          | Geometric LOS and documented limitations         |
| `get_trade_window`        | Teammate support and potential trade timings     |
| `get_exposure`            | Threat sightlines and nearby cover               |
| `get_utility_state`       | Utility inventory and effect windows             |
| `get_similar_incidents`   | Matched examples across historical demos         |
| `render_radar_frame`      | Visual snapshot of the relevant situation        |
| `get_detector_evidence`   | Exact feature values and detector version        |

The most important principle is that the AI queries analytical functions, rather than using free-form code to reinterpret all raw demo data.

An investigation should proceed as follows:

1. Read a candidate incident without the final outcome.
2. Enumerate plausible explanations and missing evidence.
3. Request only necessary supplementary information.
4. Evaluate alternative decisions available at that time.
5. Produce a structured assessment with evidence references.
6. Abstain when decisive information is missing.
7. Optionally examine the outcome separately to explain what happened.

Use a limited tool-call budget, deterministic logging, schema validation and cached evidence. Run the same incidents through multiple models during development to identify disagreements.

To counter preselection bias, some analysis jobs must inspect randomly sampled ordinary rounds and successful situations—not only incidents identified by existing mistake rules. Otherwise, the AI will simply explain the mistakes the developer already decided to look for.

### 4. Realistic API cost scenarios

Here is an illustrative text-only operating budget.

Assume each demo receives:

- 30,000 input and 2,000 output tokens on Luna for screening.
- 100,000 input and 12,000 output tokens on Sol across tactical investigations and synthesis.
- Optionally, one difficult-case escalation using 50,000 input and 6,000 output tokens on Astra.

At published standard rates, this costs approximately $0.324 per demo without escalation and $1.124 with escalation. These token volumes are planning assumptions, not measured usage.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://developers.openai.com&sz=32)

OpenAI API

| Demos | Standard pipeline | If every demo receives premium escalation |
| ----- | ----------------- | ----------------------------------------- |
| 1     | $0.32             | $1.12                                     |
| 10    | $3.24             | $11.24                                    |
| 50    | $16.20            | $56.20                                    |
| 100   | $32.40            | $112.40                                   |

If only 20% of 100 demos require premium escalation, the example total becomes approximately $48.40.

Costs could increase substantially with repeated agentic calls, huge prompts, extensive image or video input, or unbounded exploratory analysis. Conversely, cached shared context, batch processing and incremental cross-match summaries can reduce costs. Anthropic publishes a 50% Batch API discount for eligible work; provider-specific batch and caching terms should be checked before implementation.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://platform.claude.com&sz=32)

Claude Platform Docs

The most effective cost control is analytical triage: do not pay an LLM to rediscover measurements that deterministic code can calculate reliably.

For the initial prototype, I would set a hard configurable dollar limit per demo, log actual token use by stage, and reserve expensive analysis for ambiguous, high-value situations.

## F. Evidence-based coaching methodology

The software should not stop at detecting errors. It needs an intervention method.

A defensible approach combines decision review, deliberate practice principles, perceptual learning and repeated measurement. But the evidence must be described accurately: findings from sports and motor-learning studies do not automatically establish what works for high-Elo CS2 players.

### 1. A coaching feedback cycle

Observe — Identify a candidate behavior

Diagnose — Determine context and likely underlying cause

Prioritize — Select a small number of high-impact tendencies

Practice — Give a specific decision cue or training task

Re-evaluate — Test whether behavior changes in comparable situations

For a player at your level, feedback such as “improve positioning” is effectively useless. A good intervention should identify the trigger, decision point, alternative and measurable target.

Example: “After securing an opening kill while defending a site, check teammate coverage and escape routes before voluntarily re-exposing the same angle.”

This is much closer to a practicable skill than “stop dying after getting kills.”

### 2. Root causes versus symptoms

A death while isolated may be associated with multiple underlying problems:

- Intentionally choosing a high-risk position.
- Poor teammate synchronization.
- Incorrect prediction of the opponent's arrival timing.
- A missed opportunity to disengage.
- A mechanically correct duel that happened to be lost.

The system should not assign all five labels by default.

Instead, group correlated findings and attempt to identify the earliest actionable decision in the sequence. One positional choice can generate several downstream errors. Counting every consequence separately would exaggerate the same root problem.

This is where experienced human review remains valuable: the coach may ask what the player was trying to accomplish, a question that demos generally cannot answer.

### 3. What learning science contributes

Research on temporal-occlusion training suggests perceptual anticipation can improve when learners practice making decisions using incomplete visual sequences. This supports experimenting with frozen decision-point reviews, where the player predicts likely opponent actions before seeing the outcome. Evidence of transfer to CS2 specifically remains unestablished.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://link.springer.com&sz=32)

Springer Nature Link

Motor-learning research also supports considering variation and contextual interference, but results depend on the task. A 2024 meta-analysis found that advantages observed in some controlled conditions did not generalize uniformly to applied sport settings. This argues against rigidly declaring one practice schedule universally optimal.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.frontiersin.org&sz=32)

a systematic review and meta-analysis

Likewise, research on feedback frequency is heterogeneous. Reduced feedback should not be treated as an unquestionable universal rule; the right schedule depends on the learner and skill.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.sciencedirect.com&sz=32)

ScienceDirect

Deliberate practice is relevant, but not sufficient to explain expert performance. Meta-analytic research finds meaningful yet limited explanatory power, especially within already skilled populations.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://pubmed.ncbi.nlm.nih.gov&sz=32)

PubMed

+1

For this project, a reasonable design hypothesis is that one clearly defined behavioral objective per playing session may be easier to implement and evaluate than ten simultaneous coaching instructions. That is an engineering and coaching recommendation, not a proven CS2-specific optimal training prescription.

### 4. Practical intervention formats

| Problem type              | Suitable intervention                                                               |
| ------------------------- | ----------------------------------------------------------------------------------- |
| Unsupported fights        | Decision cue before engaging; replay comparison of supported and unsupported cases  |
| Repeeking                 | Pause-before-repeek review: identify what changed since first contact               |
| Bad angle isolation       | Radar/POV exercise requiring the player to mark threatening sightlines              |
| Mistimed rotations        | Decision-point quiz using only information available at the time                    |
| Poor post-kill discipline | Match objective to preserve or improve the advantage after gaining a kill           |
| Weak trading              | Review teammate spacing and timing windows, then apply a simple in-game spacing cue |

An effective practice item should include positive examples, not just mistakes. The player needs to learn when aggressive behavior is correct, otherwise the system risks training excessive passivity.

### 5. What CS-specific coaching evidence does not establish

Commercial coaching platforms demonstrate methods for extracting and presenting feedback, but public product documentation is not equivalent to controlled evidence that the intervention improves high-Elo players.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://pureskill.gg&sz=32)

PureSkill.gg

+1

I would therefore separate three kinds of claims throughout the product:

Measured: “Your rate of unsupported engagements declined.”

Expert-supported: “Reviewers considered most of these engagements avoidable.”

Outcome-improvement claim: “This coaching method makes you a better player.”

Only the third requires longitudinal intervention evidence, and it is the hardest to establish. The project should not casually conflate them.

## G. Longitudinal analysis and unconscious habit discovery

This is the feature that could most clearly differentiate the application from conventional performance dashboards.

### 1. Measure opportunities, not raw incident counts

Suppose the system detects 14 questionable repeeks in ten matches. That number means little without knowing how many situations offered a comparable repeek opportunity.

Define:

\\[ \text{Behavior rate} = \frac{\text{Instances of behavior}} {\text{Comparable opportunities}} \\]

Opportunities must be grouped by relevant context, such as map, side, health, weapon, role, numerical advantage, teammate support and round phase.

A player who takes more entries will naturally experience more dangerous situations. Comparing their raw incident total with a passive support player would be misleading.

### 2. Model sequences rather than isolated events

Several potentially revealing behavioral patterns involve transitions:

- After obtaining an opening kill, does the player become more or less aggressive?
- Following consecutive losses, do they change timing or fight selection?
- After a teammate dies, do they abandon defensive cover more frequently?
- After missing a first shot, do they re-expose rather than reposition?
- With low HP, do they actually reduce exposure?
- Following a successful aggressive play, are they more likely to repeat it in a less favorable state?

These are testable hypotheses.

Represent each round as a sequence of states and player actions. Methods worth comparing include event-sequence mining, change-point detection, conditional logistic models, trajectory clustering and simple state-transition analysis.

More complex sequence models should be considered only if they outperform interpretable baselines.

### 3. Detect patterns the developer did not anticipate

A promising approach is to embed or statistically characterize short behavioral sequences using features such as:

- Situation: map region, side, economy, objective and living players.
- Spatial state: trajectories, cover, available sightlines and spacing.
- Information: sightings, inferred opponents and uncertain cues.
- Actions: moving, holding, peeking, firing, repositioning and using utility.
- Timing: intervals between events.

Then cluster comparable situations and look for unexpected differences in behavior.

However, anomaly detection alone answers “What is unusual?”, not “What is wrong?”.

A behavior may be unusual because it is particularly strong, the player's role is different, or their teammates are playing unconventional Counter-Strike.

Candidates therefore require independent validation, preferably against matched situations and expert-reviewed examples.

The 2026 same-player verification research supplies supporting evidence that stable Counter-Strike behavioral fingerprints can be extracted. It does not supply a reliable tactical-quality label.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://arxiv.org&sz=32)

arxiv.org

### 4. Statistical safeguards

I recommend the following analysis rules:

- Use matches or independent situations as the principal statistical units, not millions of correlated ticks.
- Adjust for major contextual factors and use hierarchical estimates to stabilize sparse map/role groups.
- Show confidence or credible intervals rather than precise-looking percentages from tiny samples.
- Check whether findings persist after excluding any one match or map.
- Correct for the fact that exploratory analysis tests many possible habits.
- Compare successful and unsuccessful examples so discovery is not driven only by deaths.
- Preserve raw opportunity counts beside all adjusted rates.
- Mark findings as exploratory until repeated on newer, previously unseen demos.

The system could begin with simple beta-binomial estimates for behavior rates, bootstrap uncertainty by match, and later add multilevel models. There is no need to train a neural network before evaluating simpler methods.

One useful caution from CSReplays' published role-classification work is that even seemingly basic contextual labels can be difficult: its reported small-sample macro F1 was approximately 0.67, with substantially weaker performance on certain roles. Role labels should therefore be uncertain and revisable rather than treated as ground truth.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://csreplays.com&sz=32)

CSReplays

### 5. Determine whether correction is working

Every identified habit should have a longitudinal record containing its definition, eligible opportunities, frequency, confidence, severity, contextual breakdown, supporting clips and intervention history.

For example, compare the next 20 suitable situations with the previous baseline, while monitoring whether the player simply became too passive.

Improvement requires more than the disappearance of an error metric. The corrective behavior must remain sensible in context and should not create an equally serious new problem.

## H. Technical system design

### 1. Recommended architecture

Use a modular local application with separate acquisition, parsing, analytics and coaching layers. Avoid microservices, a distributed database, or a complex agent framework for the first version.

Demo acquisition

FACEIT · Valve · local file watcher · manual import

Rust-backed parsing through demoparser2 + Awpy

Tick data · events · map assets · geometry

SQLite

Matches, jobs, findings, coaching goals and provenance

Parquet + DuckDB

Dense trajectories, tick-level data and analytical queries

Analytical engine

Spatial features · information states · detectors · behavioral models

Evidence API and AI orchestration

Typed evidence queries · hosted LLMs · validated findings · local cache

Local web application

Match browser · radar replay · incident reviews · habit trends · coaching

### 2. Concrete technology choices

| Layer                 | Recommended technology                                        | Reason                                                               |
| --------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------- |
| Parsing               | Python bindings for demoparser2                               | Mature Rust-backed performance without writing parser infrastructure |
| CS-specific analysis  | Awpy                                                          | Existing event, map and spatial capabilities                         |
| Numerical analytics   | Python, NumPy, Polars as appropriate                          | Statistical tooling and efficient columnar operations                |
| Match metadata        | SQLite                                                        | Sufficient for a local single-user application                       |
| Large analytical data | Parquet with DuckDB                                           | Efficient compression, scans and ad hoc historical queries           |
| Backend               | FastAPI                                                       | Convenient integration with Python analytics and typed API responses |
| Frontend              | TypeScript and React                                          | Fits your experience and offers flexible replay/UI composition       |
| Background jobs       | SQLite-backed job queue and local worker                      | No Redis infrastructure required initially                           |
| AI orchestration      | Small provider adapters and explicit tool dispatcher          | Easier to evaluate, reproduce and debug                              |
| Visualization         | Reusable radar assets and suitable licensed viewer components | Avoid rebuilding the entire replay experience                        |

Rust should remain an implementation detail initially. The parser already uses it. Only introduce custom Rust processing if profiling identifies a real CPU or memory bottleneck.

Your hardware is sufficient for the proposed local parsing, statistics, databases and 2D replay. The RX 6800 is not central to the architecture because LLM inference happens remotely. GPU acceleration is not a prerequisite.

### 3. Data design and reproducibility

The minimum useful entities are:

`Match`, `Round`, `Player`, `TickSample`, `Event`, `Observation`, `InformationState`, `Situation`, `DetectedBehavior`, `CoachingAssessment`, `Habit`, `Intervention`, and `EvaluationLabel`.

Every coaching finding should reference its original demo, match, round, tick, feature calculations and software versions.

This is more important than it may appear. CS2 updates can change map geometry, parser compatibility, and relevant game mechanics. Recomputing historical analysis with newer code may produce different results.

Record at least:

- Original demo hash and match identity.
- Game/map build identifier when available.
- Parser, navigation-data and detector versions.
- Feature-computation parameters.
- Model identifier, prompt version, tool calls and token consumption.
- Whether the finding was automatically generated, human-confirmed or rejected.

The same incident should be reproducible even after the AI prompt changes.

### 4. Interface priorities

The UI should have four primary views.

Match history: imported demos, processing status, map, side, player stats and search/filtering.

Interactive replay: 2D radar with player paths, utility, sightlines, events, timeline navigation and a perspective filter. The perspective filter should be exceptionally clear about whether information is confirmed, inferred or omniscient.

Incident review: a decision-time snapshot, behavioral evidence, alternative interpretations, possible corrections, AI assessment and a way to mark the finding as useful, wrong or uncertain.

Personal coaching: recurring tendencies ranked by opportunity-adjusted frequency, potential severity, confidence and change over time. Each should lead directly to supporting incidents.

The report should never require blindly trusting a textual AI explanation. Clicking a statement such as “No teammate could realistically trade this fight” should display the paths and timing calculations supporting it.

### 5. Licensing and privacy

The available repository documentation identifies permissive MIT licensing for demoparser2, Awpy and CS Demo Manager. Verify the specific files and transitive dependencies before copying code, rather than assuming every included asset has identical rights.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

+2

CS2d's apparent lack of a repository-wide declared license is a stronger blocker for direct incorporation. Valve-derived map artwork and assets also require separate rights consideration.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

+1

For privacy, keep raw demos and the player database local. Transmit concise, pseudonymized analytical records to the AI provider. Do not send Steam identifiers, teammates' names or recorded communications unless genuinely necessary and justified.

Keep API keys in a local backend configuration or OS credential store, never in frontend source or browser-accessible storage. Evaluate each provider's API retention policies and regional-processing options separately.

The application should work for parsing, replay and statistics when offline; only AI analysis needs network access.

## I. Minimal viable prototype

The MVP must prove that the system can detect a genuinely useful recurring mistake, not merely display a parsed match.

I would intentionally narrow it to:

Input: 10–20 of your existing demos

Manual import, deterministic parsing, stored events and paths. No FACEIT automation required at this stage.

Detection: three behavior families

Repeeks after contact, unsupported engagements and overextensions after obtaining a numerical advantage.

Evidence: 2D replay with context

Show teammates, exposure, cover, event timing and available information, with uncertain observations marked.

AI: controlled incident reviewer

Compare one or two models using structured records and a small set of evidence-retrieval tools.

Output: a ranked list of recurring tendencies

Opportunity counts, supporting rounds, uncertainty and one actionable correction for each sufficiently supported tendency.

A successful MVP would make a finding such as:

> Across comparable situations in your recent matches, you voluntarily re-exposed a recently contested angle substantially more often than your own baseline in situations with a nearby teammate. Several instances lacked obvious support or newly acquired information. Here are the incidents worth reviewing.

It would then show real evidence and avoid declaring every re-exposure incorrect.

The first genuinely valuable feature is not a conversational chat box. It is a repeatable way to connect a specific habit → multiple real examples → an interpretable explanation → measurable behavior change.

## J. Development roadmap

| Stage                          | Objective and dependency                                                             | Difficulty / value      | Main risk                                     | Proceed when…                                              |
| ------------------------------ | ------------------------------------------------------------------------------------ | ----------------------- | --------------------------------------------- | ---------------------------------------------------------- |
| 0. Feasibility fixtures        | Collect representative demos and verify parsing, map data and replay synchronization | Low–medium / essential  | Broken or stale tooling                       | Real recent demos yield consistent events and trajectories |
| 1. Local analytical foundation | Normalize data, persist matches, create basic replay                                 | Medium / high           | Data-model mistakes and excessive storage     | Import is reproducible and key events align with playback  |
| 2. Initial detectors           | Implement and manually label three behavior families                                 | Medium–high / very high | Many false positives                          | High-confidence findings survive blinded review            |
| 3. Information-state model     | Add historical sightings, LOS and conservative uncertainty                           | High / very high        | Hindsight leakage                             | Hidden-information test cases are handled correctly        |
| 4. Longitudinal engine         | Opportunity denominators, matched comparisons and habit tracking                     | Medium–high / very high | Spurious patterns from sparse data            | Tendencies repeat across independent demos                 |
| 5. Agentic coaching            | Evidence retrieval, provider comparisons and corrective recommendations              | High / high             | Convincing but incorrect AI narratives        | Model adds measurable value beyond rules and summaries     |
| 6. Automation and refinement   | FACEIT/Valve adapters, background processing, evaluations                            | Medium / high           | Provider access changes                       | Routine matches flow into the database reliably            |
| 7. Exploratory ML              | Situation clustering and unexpected-pattern discovery                                | High / uncertain        | Interesting anomalies mistaken for weaknesses | New patterns are independently validated and actionable    |

These difficulty ratings are relative. Arbitrary week or month estimates would depend on implementation scope, existing code reuse and the quality of available demos.

Do not make automatic acquisition a prerequisite for Stage 2. Similarly, do not invest heavily in exploratory neural modeling before the simpler detectors have demonstrated coaching value.

## K. Critical experiments before major development

These experiments are designed to invalidate expensive assumptions as early as possible.

### Experiment 1: Can the parser reproduce the game accurately?

Select recent demos covering several maps, ordinary rounds, smoke interactions and unusual timing.

Compare parsed events and paths with native playback. Test Awpy geometry/navigation against the exact installed map versions, including the reported navigation-version compatibility issue.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com&sz=32)

GitHub

Failure condition: essential incidents cannot be reconstructed accurately enough to support tactical analysis. In that case, improve data fidelity before adding AI.

### Experiment 2: Can simple algorithms detect meaningful behavior?

Manually review a sample of eligible situations—including successful, unsuccessful and uneventful ones—without seeing automatic labels.

Compare human annotations with candidate detectors for repeeks, trading support and overextension.

Measure precision, recall, coverage and the reasons for disagreement.

Failure condition: the detectors identify many measurable events but rarely identify situations worth coaching. Narrow their definitions or change the target behaviors.

### Experiment 3: Does AI improve judgment beyond rules?

Construct a blinded evaluation set of approximately 200–300 incidents, if enough suitable examples are available.

For each situation, obtain judgments from at least two competent reviewers. Preserve disagreements rather than inventing consensus.

Compare:

1. Deterministic detector and fixed explanation.
2. One-pass LLM using structured context.
3. Tool-using LLM with decision-time evidence.
4. A stronger or alternative model using the same evidence.

Hide eventual outcomes during initial judgment. Include both good decisions with bad outcomes and bad decisions with favorable outcomes.

Measure agreement with reviewers, unsupported factual claims, confidence calibration, coverage after abstention and cost.

Use inter-rater agreement statistics such as Cohen's kappa or Krippendorff's alpha where appropriate. Also report ordinary agreement and class prevalence; a single agreement statistic can be misleading.

Failure condition: the LLM produces better-written explanations without improving tactical correctness.

That would justify using AI chiefly for summarization and interface assistance rather than autonomous coaching.

### Experiment 4: Can the system avoid omniscient hindsight?

Construct adversarial scenarios in which the objectively correct replay answer differs from what the player could know.

Examples include a silent hidden enemy, a temporarily obscured sightline, an outdated last-known position and a rotation that depends on an unavailable teammate call.

Evaluate the same incident with and without omniscient information. A decision-time model should neither silently use hidden facts nor hallucinate communications.

Failure condition: the system repeatedly criticizes reasonable decisions using unavailable information. This is a serious blocker for automatic tactical judgments.

### Experiment 5: Are identified habits statistically stable?

Take a collection of your demos and divide them into separate groups by time or match.

Discover tendencies in the first group and test whether they appear in the second, after accounting for similar opportunities.

Check sensitivity to map, side, opponent strength, role and the exclusion of individual matches. Use match-level bootstrap estimates rather than treating every tick as independent evidence.

Failure condition: most “personal weaknesses” disappear when tested on unseen matches.

This would indicate overfitting or insufficient sample size rather than meaningful behavioral diagnosis.

### Experiment 6: Does coaching change actual decisions?

Choose a single credible, sufficiently frequent tendency. Record a baseline, provide one clear intervention and evaluate subsequent comparable situations.

Measure the target behavior and related consequences—for example, whether fewer questionable repeeks are accompanied by an undesirable drop in appropriate aggression.

A personal before-and-after study cannot establish strong causality, because opponents and match conditions change. It can still provide useful early evidence. Stronger validation would eventually require controlled or staggered interventions across multiple players.

Failure condition: users understand and agree with the feedback, but it produces no stable behavioral change.

This is the decisive distinction between an interesting analytics tool and effective coaching software.

## L. Example personal coaching report

Entirely hypothetical demonstration. No observations below are derived from your matches.

## Repeated overextension after gaining an opening kill

Hypothetical finding

12 demos · 23 eligible situations

Eligible situations

# 23

Questionable follow-ups

# 9

Observed rate

# 39%

Observed pattern

After obtaining a favorable opening kill, the player sometimes takes a second fight without a clear objective, improved position, newly acquired information or reliable teammate support.

Illustrative evidence

| Mirage · Round 8   | Advanced into a newly exposed lane 2.1 seconds after a kill; nearby teammate was unable to trade immediately |
| ------------------ | ------------------------------------------------------------------------------------------------------------ |
| Ancient · Round 7  | Re-entered an enemy-controlled sightline while holding a numerical advantage                                 |
| Inferno · Round 13 | Voluntarily left defensible cover after a pick with no recorded fresh sighting                               |

Information-state assessment

The player had confirmed knowledge of the recently eliminated opponent and known teammate positions. Other enemy locations were uncertain. External team communications were unavailable.

Alternative

Preserve the newly gained advantage by maintaining cover or moving to a tradeable position, unless the second engagement serves a defensible objective.

Confidence

High that the recorded movement and exposure occurred, assuming verified geometry and event reconstruction. Moderate that the selected plays were tactically questionable; unknown communications could change the interpretation.

Coaching objective

For the next 20 eligible post-kill situations, explicitly evaluate cover, teammate support and the reason for a follow-up peek. Reduce unsupported, low-purpose re-exposures without eliminating justified aggression.

Evaluation

Compare the opportunity-adjusted behavior rate with the original 9/23 baseline, review new examples, and check whether the player continues to capitalize on good aggressive opportunities.

The distinctive feature is not the 39% figure or the wording. It is that every numerator event and every denominator opportunity should be inspectable, and the player should be able to dispute the classification.

An especially useful feedback mechanism would let you mark an incident as “intentional,” “teammate called it,” “AI missed information,” or “genuinely bad decision.” These annotations can correct the analysis and provide future evaluation data. They should not silently rewrite history or automatically become ground truth.

## M. Final build-versus-reuse recommendation

| Component                                    | Decision                      | Reason                                                        |
| -------------------------------------------- | ----------------------------- | ------------------------------------------------------------- |
| CS2 demo parser                              | Reuse                         | demoparser2 already solves the core binary-format problem     |
| Map geometry, navigation and core statistics | Reuse and extend              | Awpy provides a strong foundation, subject to version checks  |
| Steam/FACEIT acquisition                     | Integrate existing approaches | Avoid unnecessary authentication and download-protocol work   |
| 2D replay                                    | Evaluate reuse first          | Existing viewers are substantial; verify licenses             |
| Normalized historical database               | Build                         | Needs stable provenance and longitudinal queries              |
| Player information-state reconstruction      | Build incrementally           | Central unsolved component                                    |
| Contextual mistake detectors                 | Build                         | This is essential project-specific analytical value           |
| Behavioral-pattern discovery                 | Build                         | Core differentiator from match dashboards                     |
| Evidence retrieval and model evaluation      | Build                         | Necessary for trustworthy AI reasoning                        |
| LLM foundation model                         | Use hosted API                | No justification for training or hosting one initially        |
| Custom fine-tuning                           | Postpone                      | Requires sufficient expert-labeled data and demonstrated need |
| Full 3D replay or video generation           | Postpone                      | High complexity without proving superior coaching value       |
| Predictive tactical neural networks          | Research later                | Attractive, but their outputs require difficult validation    |

### Final verdict

A local-first personal CS2 coaching system is worth prototyping.

General-purpose, human-coach-equivalent tactical judgment is not presently demonstrated.

The strongest engineering path is to develop a system that discovers repeated, context-conditioned behaviors and uses AI to investigate and explain them, while reserving definitive mistake labels for findings supported by sufficient evidence.

The most valuable experiment is not whether GPT-6 or Claude can produce an insightful-sounding review of one demo. It is whether a combination of deterministic measurements, information-state reconstruction and evidence-retrieval tools can reliably identify a weakness you did not already know you had, and whether addressing that weakness measurably changes your future decisions.

Build the first three detectors, validate them against real incidents, and test whether the pattern survives across matches. If that succeeds, there is a credible foundation for progressively more sophisticated coaching. If it fails, more elaborate AI architecture will not rescue the fundamental analytical premise.

This is the point at which I would make the decision to commit to a full application—not before.

# CS2 Demo Analyzer — Agent Instructions

## Project

Local-first Counter-Strike 2 demo analysis and personal coaching application.

The long-term goal is to identify recurring gameplay mistakes, behavioral patterns, and improvement opportunities through evidence-based analysis.

AI reasoning will use hosted model APIs. Demo processing and application data remain local.

## Research

Existing research is located in `research/`.

Primary references:

- `research/muse/CS2-Coaching-System-Research.md`
- `research/gpt/research-gpt.md`

Consult specialized research files when relevant.

Research findings are references, not immutable architectural decisions. Verify implementation-critical claims against current upstream sources.

## Engineering principles

- **Product value over infrastructure.** Prioritize functionality that enables meaningful gameplay analysis. Do not build supporting infrastructure because it could theoretically become useful.
- **Evidence-driven development.** Validate assumptions with real demos wherever possible. Separate recorded facts, computed measurements, tactical interpretations, and coaching judgments.
- **Incremental development.** Implement the smallest coherent functionality needed for the current phase. Avoid speculative frameworks and premature generalization.
- **Minimal necessary abstraction.** Reuse existing functions and libraries. Introduce an abstraction when it solves an actual dependency, reuse, or complexity problem — not to anticipate future possibilities.
- Reuse maintained, appropriately licensed libraries before writing custom implementations.
- Prefer a modular monolith with explicit internal boundaries.
- Favor simple, composable solutions over premature abstractions.
- Preserve original demo files and support reprocessing.
- Design modules for independent implementation and testing.
- Define shared contracts before parallel implementation.
- Avoid duplicate implementations of the same functionality.
- Prefer measurable evidence and reproducible behavior over assumptions.
- Do not introduce infrastructure without a concrete requirement.
- **Change justification.** Before adding dependencies, architectural layers, permanent infrastructure, or large test suites, establish a concrete reason they are needed.
- **Correctness without defensive excess.** Maintain safeguards at trust boundaries, persistence boundaries, and consequential gameplay-data transformations. Avoid repeatedly defending trusted internal interfaces against impossible states.
- **Controlled scope.** Respect the current phase's objectives. Do not opportunistically implement unrelated features.

## Data semantics

- `player_state` keeps emitting rows after death (`health == 0`). Raw geometric queries include them by default; active-player questions use explicit living-participant filtering (e.g. spatial `alive_only=True`). Never silently count a dead player as available.
- Null-`player_id` handling is evidence from the tested recording (all null rows had `health == 0` there), not a universal guarantee for every demo type. Flag null rows carrying health data; never invent identities or join unknown players by position.

## Testing

- **Pragmatic testing.** Test important behavior, realistic failure cases, and consequential invariants. Do not optimize for test counts or coverage percentages. Prefer a small number of meaningful tests over large quantities of trivial tests.
- High value: gameplay data correctness, identity continuity, tick/event sync, spatial math, parser compatibility, data integrity, lifecycle transitions, user-workflow regressions, missing/misleading observations.
- Low value: near-duplicate validation paths, trivial parameter combinations, dependency-guaranteed behavior, implementation details, mirror mocks, unrealistic fixtures, hypothetical consumers.
- Validate with real demos where possible (small authored fixtures, consequential edge cases, real-demo checks, manual replay inspection, regression tests for real bugs). No coverage targets, test-count targets, mandatory-per-function tests, or elaborate testing machinery without a demonstrated need.

## Verification (no mandatory CI)

Run appropriate verification locally. Introduce CI only when the project's workflow justifies it.

```bash
uv run --project backend pytest backend/tests -q
npm --prefix web run build
```

## Development orchestration

- Use subagents for genuinely independent, well-defined tasks. Freeze shared contracts before parallel development. Do not maximize agent count for its own sake.
- The parent orchestrator owns architectural consistency and integration.
- Assign explicit ownership of shared files and interfaces.
- Parallelize independent work without sacrificing correctness.
- Worktrees are optional, not mandatory.

## Scope

- Primary target: CachyOS / Arch Linux.
- Local CS2 installation:
  `/mnt/nvme/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/`
- Analyze local CS2 demo files.
- Automatic discovery of locally available demos is a priority.
- FACEIT API integration is out of scope.
- Local LLM inference and custom foundation-model training are out of scope.

## Documentation

Record accepted architectural decisions and implementation plans under `docs/`.

Keep durable project rules here. Keep phase-specific instructions in task prompts and planning documents.

Do not treat proposed research architectures as finalized decisions.

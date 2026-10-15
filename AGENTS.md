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

- Reuse maintained, appropriately licensed libraries before writing custom implementations.
- Prefer a modular monolith with explicit internal boundaries.
- Favor simple, composable solutions over premature abstractions.
- Preserve original demo files and support reprocessing.
- Design modules for independent implementation and testing.
- Define shared contracts before parallel implementation.
- Avoid duplicate implementations of the same functionality.
- Prefer measurable evidence and reproducible behavior over assumptions.
- Do not introduce infrastructure without a concrete requirement.

## Development orchestration

- Use subagents for independent, well-defined tasks.
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

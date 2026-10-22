# Status

## Current phase

Initial roadmap complete — stabilization and dogfooding

## Implemented

- Phase 0: product foundation and boundaries
- Phase 1: prompt engineering core and target profiles
- Phase 2: task/risk classification and contextual engineering/DevOps policies
- Phase 3: bounded project-context selection and proposal-first agent workspace maintenance
- Phase 4: capability/cost/effort routing with replaceable model metadata and deterministic fallback
- Phase 5: regression assertions/scoring, token-latency-retry metrics, A/B ranking, and evidence-backed learning proposals
- Phase 6: standard-library CLI, package entry point, GitHub Actions CI, and contributor guidance

## Current verification baseline

31 standard-library unit tests passing locally plus `python -m intentos` CLI JSON smoke test.

## Next

- dogfood IntentOS on real Codex / Claude Code / ChatGPT workflows
- collect regression fixtures from real failures
- add provider/model metadata adapters only where real usage requires them
- run an independent architecture/quality audit before declaring a stable v1 contract

## Constraints carried forward

- vendor-neutral core
- no runtime dependencies without demonstrated need
- minimal sufficient context
- contextual engineering rules, not dogmatic injection
- proposal/approval boundaries before destructive or persistent changes
- no hardcoded volatile model names in core routing logic
- learning requires repeated evidence, not one-off failures

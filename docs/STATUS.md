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
- Stabilization pass 1: multilingual dogfooding, documentation-only policy correction, and independent-audit package

## Current verification baseline

37 standard-library unit tests plus the `python -m intentos` CLI smoke test. GitHub Actions passes on Python 3.11, 3.12, and 3.13.

## Stabilization findings

- English-only task heuristics were too narrow for mixed Persian + technical requests.
- documentation-only architecture/security tasks needed lighter policy handling.
- real failures are being promoted into regression fixtures rather than global prompt boilerplate.

See `docs/DOGFOODING.md` for evidence and `docs/INDEPENDENT_AUDIT.md` for the independent review package.

## Next

- run the independent architecture/quality audit before freezing a stable v1 API
- continue dogfooding on real multi-file Codex / Claude Code work
- collect regression fixtures from real failures
- add provider/model metadata adapters only where real usage requires them

## Constraints carried forward

- vendor-neutral core
- no runtime dependencies without demonstrated need
- minimal sufficient context
- contextual engineering rules, not dogmatic injection
- proposal/approval boundaries before destructive or persistent changes
- no hardcoded volatile model names in core routing logic
- learning requires repeated evidence, not one-off failures
- no claim of full multilingual NLP support from a small deterministic starter lexicon

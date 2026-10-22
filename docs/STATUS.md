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
- Stabilization pass 2: Hugging Face ecosystem research, portable Agent Skill compilation, privacy-minimal versioned run records, and CI action refresh

## Current verification baseline

43 standard-library unit tests plus CLI smoke checks. GitHub Actions passes on Python 3.11, 3.12, and 3.13.

## Stabilization findings

- English-only task heuristics were too narrow for mixed Persian + technical requests.
- documentation-only architecture/security tasks needed lighter policy handling.
- repeated agent guidance is better represented as portable/on-demand Skill artifacts than copied into every prompt.
- evaluation needs versioned run metadata and provenance, not only final prompt assertions.
- raw agent traces can contain private code, paths, tool outputs, and secrets, so the core run record remains privacy-minimal and stores prompt fingerprints rather than raw prompts.
- provider-routing and telemetry concepts are useful extension points, but do not justify provider discovery, an MCP runtime, or observability dependencies in the core yet.
- real failures are promoted into regression fixtures rather than global prompt boilerplate.

See `docs/DOGFOODING.md`, `docs/HUGGINGFACE_RESEARCH.md`, and `docs/INDEPENDENT_AUDIT.md`.

## Next

- run the independent architecture/quality audit before freezing a stable v1 API
- continue dogfooding on real multi-file Codex / Claude Code work
- collect regression fixtures from real failures
- add provider/model metadata adapters only where real usage requires them
- consider telemetry, Session Trace, MCP/tool-contract, and provider-policy adapters only after concrete execution integrations exist

## Constraints carried forward

- vendor-neutral core
- no runtime dependencies without demonstrated need
- minimal sufficient context
- contextual engineering rules, not dogmatic injection
- proposal/approval boundaries before destructive or persistent changes
- no hardcoded volatile model names in core routing logic
- learning requires repeated evidence, not one-off failures
- no claim of full multilingual NLP support from a small deterministic starter lexicon
- portable Skill/run-record outputs must remain human-reviewable and integration-neutral

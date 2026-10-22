# Status

## Current phase

Initial roadmap complete — stabilization, dogfooding, and independent-audit preparation

## Implemented

- Phase 0: product foundation and boundaries
- Phase 1: prompt engineering core and target profiles
- Phase 2: task/risk classification and contextual engineering/DevOps policies
- Phase 3: bounded project-context selection and proposal-first agent workspace maintenance
- Phase 4: capability/cost/effort routing with replaceable model metadata and deterministic fallback
- Phase 5: regression assertions/scoring, token-latency-retry metrics, A/B ranking, and evidence-backed learning proposals
- Phase 6: standard-library CLI, package entry point, GitHub Actions CI, and contributor guidance
- Stabilization pass 1: multilingual dogfooding, documentation-only policy correction, and independent-audit package
- Stabilization pass 2: Hugging Face ecosystem research, portable Agent Skill compilation, privacy-minimal versioned run records, Unicode-aware context selection, and CI action refresh
- Product/UX architecture: one shared core with planned CLI/API, MCP, VS Code, Agent Skills, and simple-user access surfaces; progressive disclosure and ease of use are now explicit product requirements

## Current verification baseline

45 standard-library unit tests plus CLI smoke checks. GitHub Actions passes on Python 3.11, 3.12, and 3.13.

This usage/UX architecture change is documentation-only and does not yet implement MCP, VS Code, or a standalone simple UI.

## Stabilization findings

- English-only task heuristics were too narrow for mixed Persian + technical requests.
- project-context lexical matching also needed Unicode-aware tokenization for Persian/multilingual prompts.
- documentation-only architecture/security tasks needed lighter policy handling.
- repeated agent guidance is better represented as portable/on-demand Skill artifacts than copied into every prompt.
- evaluation needs versioned run metadata and provenance, not only final prompt assertions.
- raw agent traces can contain private code, paths, tool outputs, and secrets, so the core run record remains privacy-minimal and stores prompt/context fingerprints rather than raw content.
- provider-routing and telemetry concepts are useful extension points, but do not justify provider discovery, an MCP runtime, or observability dependencies in the core yet.
- ease of use must be designed as part of the product: everyday users should not need prompt-engineering or agent-integration expertise, while advanced users retain deeper controls through progressive disclosure.
- integrations should remain thin adapters over one core to avoid divergent behavior across CLI, IDE, MCP, and future UI surfaces.
- real failures are promoted into regression fixtures rather than global prompt boilerplate.

See `docs/DOGFOODING.md`, `docs/HUGGINGFACE_RESEARCH.md`, `docs/UX.md`, and `docs/INDEPENDENT_AUDIT.md`.

## Next

- run the independent architecture/quality/product audit before freezing a stable v1 API
- ask the audit to challenge the usage architecture, adoption friction, and MCP/VS Code boundaries as well as the current code
- continue dogfooding on real multi-file Codex / Claude Code work
- collect regression fixtures from real failures
- after audit findings, begin Phase 7A with the smallest useful MCP adapter if the boundary is validated
- follow with VS Code UX, then a simple end-user UI only after terminology and workflows are proven
- add provider/model metadata adapters only where real usage requires them
- consider telemetry, Session Trace, provider-policy, and additional tool-contract adapters only after concrete execution integrations exist

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
- one shared core across access surfaces; integrations may adapt UX/transport but must not duplicate decision logic
- ease of use and progressive disclosure are product requirements

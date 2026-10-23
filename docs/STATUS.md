# Status

## Current phase

Phase 7B preparation — minimum useful VS Code UX

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
- Product/UX architecture: one shared core with CLI/API, MCP, VS Code, Agent Skills, and simple-user access surfaces; progressive disclosure and ease of use are explicit product requirements
- Independent audit: verdict `NEEDS STABILIZATION`; no architectural redesign or P0 emergency defect was identified
- Stabilization pass 3: preserve user content/output requirements, harden deterministic risk classification, context/workspace safety, structured results, and evaluation evidence contracts
- Review dogfood regressions: documentation work stays lightweight without losing topic taxonomy; combined mutation requests remain high risk; distinct context ranks by relevance while authoritative duplicates still win
- Phase 7A: optional MCP v2 stdio adapter with exactly one `prepare_task` tool over the shared core
- Phase 7A parity dogfood: installed `intentos-mcp` launched as a real stdio subprocess and produced exact structured-result parity with CLI and Python API across four representative cases

## Current verification baseline

79 standard-library unit tests plus CLI smoke checks, plus two MCP checks:

- in-memory MCP v2 protocol smoke
- stdio subprocess host-parity dogfood across four representative cases

CI covers:

- Ubuntu / Python 3.11
- Ubuntu / Python 3.12
- Ubuntu / Python 3.13
- Windows / Python 3.13 focused regression coverage
- MCP v2 protocol and stdio host-parity checks on Ubuntu / Python 3.13 with the optional `mcp` extra installed

## Phase 7A boundary

The first MCP slice intentionally exposes only `prepare_task`.

It accepts:

- user request
- optional target AI/tool
- constraints and success criteria
- optional output format and audience
- caller-supplied project context as `path` labels plus `content`

It returns the shared versioned machine contract: ready/clarification status, prepared prompt, task/risk decision, engineering rules, approval boundaries, routing, context diagnostics, and verification criteria.

MCP currently does **not**:

- read arbitrary local files
- execute the prepared task
- grant authorization for risky actions
- mutate the workspace
- expose classifier/router/policy as separate tools
- expose Skill, workspace, run-record, telemetry, provider-discovery, or orchestration tools
- require MCP dependencies for normal core/CLI installation

Project context is limited to 32 caller-supplied documents and 6000 characters total in this first slice.

See `docs/MCP_DOGFOODING.md` for the parity evidence and its limits.

## Deliberately deferred

To avoid over-engineering, Phase 7A did **not** add:

- additional MCP tools
- Streamable HTTP deployment
- an MCP runtime/framework beyond the optional official SDK adapter
- an LLM-based classifier
- embeddings or a vector database
- a policy/plugin framework
- provider discovery or failover orchestration
- a telemetry backend
- a standalone simple UI

The classifier remains advisory rather than a security authorization boundary.

## Next

Begin Phase 7B with the smallest useful editor slice:

- Command Palette action to prepare typed or selected text
- temporary review panel showing concise interpretation, consequential risk/approval, context summary, and verification summary
- Copy Prepared Task handoff first; do not add agent-specific execution wiring unless real usage justifies it
- keep full prompt, taxonomy, context scores, routing metadata, and expert controls behind progressive disclosure
- reuse the shared preparation contract; do not duplicate core logic in the extension

Keep additional MCP tools deferred unless repeated real use demonstrates a concrete need.

## Constraints carried forward

- vendor-neutral core
- no core runtime dependencies without demonstrated need; integration dependencies stay optional
- KISS/YAGNI and regression-driven fixes before new abstraction
- minimal sufficient context
- preserve user-supplied meaning and explicit output requirements
- contextual engineering rules, not dogmatic injection
- proposal/approval boundaries before destructive or persistent changes
- no hardcoded volatile model names in core routing logic
- learning requires distinct repeated evidence, not duplicated outcomes
- no claim of full multilingual NLP support from deterministic starter heuristics
- portable Skill/run-record outputs remain human-reviewable and integration-neutral
- one shared core across access surfaces; integrations may adapt UX/transport but must not duplicate decision logic
- ease of use and progressive disclosure are product requirements

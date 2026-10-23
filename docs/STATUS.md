# Status

## Current phase

Phase 7A — minimal MCP adapter and parity dogfooding

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

## Current verification baseline

79 standard-library unit tests plus CLI smoke checks, plus a dedicated MCP v2 in-memory protocol smoke.

CI covers:

- Ubuntu / Python 3.11
- Ubuntu / Python 3.12
- Ubuntu / Python 3.13
- Windows / Python 3.13 focused regression coverage
- MCP v2 protocol smoke on Ubuntu / Python 3.13 with the optional `mcp` extra installed

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

## Stabilization findings addressed

- background project context can no longer mark an operational request as documentation-only and silently lower its risk
- deterministic classifier matching uses term boundaries, preventing substring collisions such as `iam` inside `William`
- common login/authentication and destructive production/Persian cases have regression coverage
- documentation about security/architecture can remain lightweight while preserving topic taxonomy
- combined documentation plus deploy/destructive work remains on the technical/high-risk path
- multiline code/YAML/Markdown-like input is preserved instead of collapsing all whitespace
- context values are no longer deduplicated case-insensitively
- explicit output format and audience survive coding-agent prompt and Skill compilation
- project context validates budgets, handles Windows-style paths, preserves authoritative duplicate representatives, and ranks distinct documents primarily by relevance
- explicit caller context participates in the project context budget instead of bypassing it
- workspace phase proposals canonicalize repository paths and replace only the current phase value rather than deleting neighboring human guidance
- CLI target detection is shared with the API; unknown targets produce clarification instead of silent generic fallback
- CLI and MCP reuse one machine-readable result serializer rather than forking the contract
- evaluation uses one public run-metrics contract, validates metric values, does not count an assertion-free case as success, and requires distinct failure cases for learning proposals
- CI exercises regressions on Windows as well as Linux

## Deliberately deferred

To avoid over-engineering, Phase 7A does **not** add:

- additional MCP tools
- Streamable HTTP deployment
- an MCP runtime/framework beyond the optional official SDK adapter
- an LLM-based classifier
- embeddings or a vector database
- a policy/plugin framework
- provider discovery or failover orchestration
- a telemetry backend
- VS Code implementation
- a standalone simple UI

The classifier remains advisory rather than a security authorization boundary.

## Next

- dogfood `prepare_task` through a real MCP host and compare MCP results with CLI/Python API results for the same requests
- promote only observed MCP parity/UX failures into regression fixtures
- keep additional MCP tools deferred unless repeated real use demonstrates a concrete need
- once MCP/core parity is proven, begin the minimum useful VS Code UX with Command Palette actions and a temporary review panel
- keep routing/model freshness and broader OSS release work experimental unless real usage demonstrates need

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

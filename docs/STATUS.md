# Status

## Current phase

Independent-audit stabilization — contract-preserving task preparation

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
- Product/UX architecture: one shared core with planned CLI/API, MCP, VS Code, Agent Skills, and simple-user access surfaces; progressive disclosure and ease of use are explicit product requirements
- Independent audit: verdict `NEEDS STABILIZATION`; no architectural redesign or P0 emergency defect was identified
- Stabilization pass 3: preserve user content/output requirements, harden deterministic risk classification, context/workspace safety, structured CLI results, and evaluation evidence contracts

## Current verification baseline

69 standard-library unit tests plus CLI smoke checks.

CI covers:

- Ubuntu / Python 3.11
- Ubuntu / Python 3.12
- Ubuntu / Python 3.13
- Windows / Python 3.13 focused regression coverage

No MCP server, VS Code extension, or standalone simple UI is implemented yet.

## Stabilization findings addressed

- background project context can no longer mark an operational request as documentation-only and silently lower its risk
- deterministic classifier matching uses term boundaries, preventing substring collisions such as `iam` inside `William`
- common login/authentication and destructive production/Persian cases have regression coverage
- multiline code/YAML/Markdown-like input is preserved instead of collapsing all whitespace
- context values are no longer deduplicated case-insensitively
- explicit output format and audience survive coding-agent prompt and Skill compilation
- project context validates budgets, handles Windows-style paths, ranks before deduplication, and preserves authoritative duplicate representatives
- explicit caller context participates in the project context budget instead of bypassing it
- workspace phase proposals canonicalize repository paths and replace only the current phase value rather than deleting neighboring human guidance
- CLI target detection is shared with the API; unknown targets produce clarification instead of silent generic fallback
- CLI JSON has a small versioned status/error contract and exposes preserved intent, policy, routing, and context diagnostics
- evaluation uses one public run-metrics contract, validates metric values, does not count an assertion-free case as success, and requires distinct failure cases for learning proposals
- CI now exercises the regression suite on Windows as well as Linux

## Deliberately deferred

To avoid over-engineering, this stabilization did **not** add:

- an LLM-based classifier
- embeddings or a vector database
- a policy/plugin framework
- provider discovery or failover orchestration
- a telemetry backend
- MCP implementation
- VS Code implementation

The classifier remains advisory rather than a security authorization boundary.

## Next

- complete a small paired dogfood pass comparing raw requests with IntentOS-prepared contracts on the same tasks/configuration
- re-check the independent-audit P1 reproductions against the merged branch
- keep routing/model freshness and broader OSS release work experimental unless real usage demonstrates need
- if the preparation contract remains stable, begin Phase 7A with the smallest MCP surface: one `prepare_task` tool over the existing core
- follow with the minimum useful VS Code UX only after MCP/core parity is proven

## Constraints carried forward

- vendor-neutral core
- no runtime dependencies without demonstrated need
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

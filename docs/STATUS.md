# Status

## Current phase

Phase 7C COMPLETE — real-use evidence gate closed; no product change

## Implemented

- Phase 0: product foundation and boundaries
- Phase 1: prompt engineering core and target profiles
- Phase 2: task/risk classification and contextual engineering/DevOps policies
- Phase 3: bounded project-context selection and proposal-first agent workspace maintenance
- Phase 4: capability/cost/effort routing with replaceable model metadata and deterministic fallback
- Phase 5: regression assertions/scoring, token/latency/retry metrics, A/B ranking, and evidence-backed learning proposals
- Phase 6: standard-library CLI, package entry point, GitHub Actions CI, and contributor guidance
- Stabilization pass 1: multilingual dogfooding, documentation-only policy correction, and independent-audit package
- Stabilization pass 2: Hugging Face ecosystem research, portable Agent Skill compilation, privacy-minimal versioned run records, Unicode-aware context selection, and CI action refresh
- Product/UX architecture: one shared core with CLI/API, MCP, VS Code, Agent Skills, and simple-user access surfaces; progressive disclosure and ease of use are explicit product requirements
- Independent audit: verdict `NEEDS STABILIZATION`; no architectural redesign or P0 emergency defect was identified
- Stabilization pass 3: preserve user content/output requirements, harden deterministic risk classification, context/workspace safety, structured results, and evaluation evidence contracts
- Review dogfood regressions: documentation work stays lightweight without losing topic taxonomy; combined mutation requests remain high risk; distinct context ranks by relevance while authoritative duplicates still win
- Phase 7A: optional MCP v2 stdio adapter with exactly one `prepare_task` tool over the shared core
- Phase 7A parity dogfood: installed `intentos-mcp` launched as a real stdio subprocess and produced exact structured-result parity with CLI and Python API across four representative cases
- Phase 7B minimum editor slice: one `IntentOS: Prepare Task` Command Palette action, selected-text/input capture, temporary review panel, progressive advanced details, and Copy Prepared Task handoff
- Phase 7B runtime reliability: dependency-free real Extension Host integration tests pass with the repository workspace and with no workspace; both resolve and run the repository-local `.venv` CLI
- Phase 7B manual dogfood: `Ctrl+F5`, input-box request, Review Panel, and Copy Prepared Task passed; copied output was valid and preserved the requested goal
- Phase 7C-A evaluation pilot: task-local raw/prepared run comparison reuses `VariantRun` and `RunMetrics`; it records deltas without executing agents or claiming empirical improvement
- Phase 7C real-use evidence: 10/10 distinct tasks collected; paired outcomes were 3 prepared, 2 raw, and 5 inconclusive
- Phase 7C decision: no new capability met the promotion threshold; the Phase 7B Prepare → Review → Copy workflow remains accepted
- Task 7 exposed a deterministic high-risk classification defect; the focused regression fix is incorporated
- Task 8 exposed a pre-existing ARIS CRM CI/deployment baseline defect; it was not an IntentOS product defect
- No Phase 7D or other feature phase has started

## Current verification baseline

95 Python unit tests plus CLI smoke checks, plus dedicated integration checks (current local full-suite run on main):

- in-memory MCP v2 protocol smoke
- stdio subprocess MCP host-parity dogfood across four representative cases
- VS Code extension JavaScript syntax smoke with no npm install/build pipeline
- static regression for the repository Extension Development Host launch contract
- real VS Code Extension Host integration checks for workspace and no-workspace executable resolution

CI covers:

- Ubuntu / Python 3.11
- Ubuntu / Python 3.12
- Ubuntu / Python 3.13
- Windows / Python 3.13 focused regression coverage
- MCP v2 protocol and stdio host-parity checks on Ubuntu / Python 3.13 with the optional `mcp` extra installed
- dependency-free VS Code extension syntax check

## Phase 7C closeout

The 10/10 real-task evidence target is complete. The aggregate result supports no IntentOS product change: no repeated workflow friction met the promotion threshold and no consistent raw-versus-prepared winner emerged. The existing Phase 7B Prepare → Review → Copy workflow remains accepted. Task 7's classifier correction is incorporated; the Task 8 external ARIS baseline repair did not reveal an IntentOS defect. See `docs/PHASE_7C_EVIDENCE.md` and [Issue #21](https://github.com/milad-seify/IntentOS/issues/21) for the concise decision and detailed evidence log.

## Phase 7B boundary

The first VS Code slice intentionally stays thin and local.

It currently:

- exposes one user-facing command: `IntentOS: Prepare Task`
- uses selected editor text when present, otherwise asks for the request
- invokes `intentos optimize ... --json` rather than reimplementing core logic
- shows interpretation, risk, consequential approval boundaries, context summary, and verification in a temporary review panel
- keeps routing/context internals behind a collapsed Advanced section
- copies the prepared prompt to the clipboard on explicit user action
- allows one optional `intentos.executable` setting for PATH/virtual-environment cases
- surfaces structured CLI errors rather than presenting them as clarification
- can be launched from the repository root with `F5` using `.vscode/launch.json`

It does **not**:

- add a permanent sidebar/activity-bar view
- discover or read project files automatically
- execute or send prepared tasks to an agent
- embed an MCP client inside the extension
- add npm runtime dependencies, TypeScript, bundlers, telemetry, background services, or provider settings

See `integrations/vscode/README.md` for the editor workflow and `docs/VSCODE_DOGFOODING.md` for the real-UI acceptance protocol.

## Phase 7A boundary

The MCP surface remains exactly one `prepare_task` tool. It does not read arbitrary local files, execute prepared work, authorize risky actions, mutate the workspace, or expose classifier/router/policy/Skill/workspace/run-record/telemetry/provider tools.

Project context is limited to 32 caller-supplied documents and 6000 characters total in this first slice. See `docs/MCP_DOGFOODING.md` for parity evidence and limits.

## Deliberately deferred

To avoid over-engineering, current access work does **not** add:

- additional MCP tools or Streamable HTTP deployment
- a permanent VS Code sidebar or settings framework
- agent-specific execution wiring
- automatic editor filesystem/context discovery
- `@vscode/test-electron` or a downloaded/headless VS Code CI harness before a real UI failure justifies it
- an LLM-based classifier
- embeddings or a vector database
- a policy/plugin framework
- provider discovery or failover orchestration
- a telemetry backend
- a standalone simple UI
- an autonomous multi-agent execution/checking runtime
- a benchmark-framework dependency

The classifier remains advisory rather than a security authorization boundary.

## Next

- Conduct a bounded stable-v1/release-readiness review: verify the supported install/runtime contract, release metadata and packaging, clean-install smoke path, documentation consistency, and CI release gates.
- Do not start feature development or Phase 7D as part of that review; any proposed product change requires a separate evidence-backed decision.

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

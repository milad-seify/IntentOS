# Status

## Current phase

Phase 7C — evidence gathering active; feature implementation remains gated

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

## Current verification baseline

93 Python unit tests plus CLI smoke checks, plus dedicated integration checks:

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

## Phase 7C evidence gate

Phase 7C begins with repeated-use evidence rather than a new access surface. See `docs/PHASE_7C_EVIDENCE.md` for the observation fields, promotion rules, current hypotheses, and the initial 10-task evidence target.

External projects may supply hypotheses, benchmark ideas, or comparison methods, but do not justify feature adoption by themselves.

The first questions are whether repeated use demonstrates material need for:

- Send-to-Agent rather than Copy Prepared Task
- automatic context discovery
- changes to the Review Panel information hierarchy
- a separate simple UI for non-expert users
- stronger or independent verification guidance
- a paired raw-request versus IntentOS-prepared-request evaluation

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

- Use IntentOS on at least 10 distinct real tasks and record only decision-relevant outcomes/friction using `docs/PHASE_7C_EVIDENCE.md`.
- Promote correctness, safety, or public-contract failures immediately into focused regressions.
- Require repeated real friction before adding Send to Agent, automatic context discovery, a simple UI, stronger verification machinery, or another access surface.
- If outcome quality remains uncertain after real use, prefer a small paired evaluation over subjective prompt tuning.

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

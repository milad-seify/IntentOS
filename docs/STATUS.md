# Status

## Current phase

**PRE-RELEASE UI/UX COMPLETION — IMPLEMENTATION CANDIDATE.** F01–F10 core source was accepted and frozen at `8b9b49fc82a5f038dcd36577e3037f697a5c0819` after [PR #65](https://github.com/milad-seify/IntentOS/pull/65) merged and seven post-merge CI jobs passed. [D-032](DECISIONS.md) records that exact historical scope. The owner then authorized [D-033](DECISIONS.md): graphical access through VS Code and a local-first Simple UI before publication and Phase 8. This new integrated candidate is **not yet accepted or frozen**; it needs its own exact-SHA verification and owner review.

Existing **published** releases remain Core `1.0.1` and VS Code `0.1.1`; source metadata is Core `1.1.0`, **not published**. The current development branch adds editor and local browser access without changing the published artifacts. Operational Phase 8A/8B/8C and owner-led Idea-to-Production dogfooding remain **DEFERRED / NOT STARTED**, with their criteria unchanged.

## Post-Phase-7 development program

- **Current direction:** [D-031](DECISIONS.md) and [DELIVERY_PROGRAM.md](DELIVERY_PROGRAM.md) require all F01–F10 outcomes. Earlier B2/C1/D1 deferrals and the early Freeze proposal are historical decisions superseded for this delivery scope.
- **Current implementation:** F01–F10 source and CLI access were accepted in PR #65. The current UI branch adapts those operations to an editor workbench and a standalone loopback browser interface. Its new integration and security checks are developer verification, not operational Phase 8 evidence. Codex dispatch still requires explicit approval; agent completion is not verification, and other agents remain manual handoffs.
- **Historical evidence:** Stage E readiness, [B2-OBS-001](B2_CONTINUITY_OBSERVATION_001.md) and PR #65's accepted source freeze remain accurate for their respective revisions. None establishes acceptance of the new integrated UI candidate.
- **Deferred activity:** operational Phase 8A/8B/8C and owner-led Idea-to-Production dogfooding await complete implementation, one final integrated acceptance, and separately authorized execution.

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
- Phase 7A COMPLETE: optional MCP v2 stdio adapter with exactly one `prepare_task` tool over the shared core
- Phase 7A parity dogfood: installed `intentos-mcp` launched as a real stdio subprocess and produced exact structured-result parity with CLI and Python API across four representative cases
- Phase 7B COMPLETE: VS Code extension with Command Palette action, visible status-bar launcher, selected-text/input capture, temporary review panel, progressive advanced details, and Copy Prepared Task handoff
- Phase 7B runtime reliability: dependency-free real Extension Host integration tests pass with the repository workspace and with no workspace; both resolve and run the repository-local `.venv` CLI
- Phase 7B manual dogfood: `Ctrl+F5`, input-box request, Review Panel, and Copy Prepared Task passed; copied output was valid and preserved the requested goal
- Phase 7C-A evaluation pilot: task-local raw/prepared run comparison reuses `VariantRun` and `RunMetrics`; it records deltas without executing agents or claiming empirical improvement
- Phase 7C COMPLETE: 10/10 distinct real tasks collected; paired outcomes were 3 prepared, 2 raw, and 5 inconclusive
- Phase 7C decision: no new capability met the promotion threshold; the Phase 7B Prepare → Review → Copy workflow remains accepted
- Task 7 exposed a deterministic high-risk classification defect; the focused regression fix is incorporated
- Review-only technical requests use the existing general task type and read-only, evidence-based policy; mixed review/implementation requests keep their normal classification and risk checks
- Task 8 exposed a pre-existing ARIS CRM CI/deployment baseline defect; it was not an IntentOS product defect
- Phase 7D was intentionally deferred and closed without implementation because no demonstrated demand crossed the evidence threshold; Phase 7 overall is COMPLETE
- Final stable-v1 readiness gate passed (`READY`); the v1 public contract is frozen in docs/PUBLIC_CONTRACT.md
- IntentOS 1.0.0 is published on PyPI as `intentos-engineering`; a clean public installation was verified
- GitHub tag [`v1.0.0`](https://github.com/milad-seify/IntentOS/releases/tag/v1.0.0) points to accepted commit `daacb4e98e7c97694d9f645037ccc2eac949af2b`
- GitHub Release [IntentOS 1.0.0](https://github.com/milad-seify/IntentOS/releases/tag/v1.0.0) is published
- The Trusted Publishing release workflow succeeded: [run 40918243836](https://github.com/milad-seify/IntentOS/actions/runs/40918243836)
- VS Code extension `0.1.1` is published on the [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=milad-seyfi.intentos-vscode) as `milad-seyfi.intentos-vscode`; tag `vscode-v0.1.1` was published through Marketplace Trusted Publishing / OIDC
- Marketplace run [41219940660](https://github.com/milad-seify/IntentOS/actions/runs/41219940660) published the exact verified VSIX with digest `sha256:1aee46d84ea9c5251658bde351b701e51e4b5766e8a103b942030821974e7b13`
- Version 0.1.1 adds the visible IntentOS status-bar launcher, approved icon, and genuine Review screenshot while preserving Command Palette support and the Prepare → Review → Copy boundary
- The published extension was manually installed from the Marketplace and verified through the Prepare → Review → Copy workflow

## Phase 8 — final validation protocol (execution deferred)

The approved first slice defines first-use validation, a manual outcome-evidence worksheet, comparison controls, and an external evidence gate in [PHASE_8_VALIDATION.md](PHASE_8_VALIDATION.md). It uses existing Phase 5 evaluation mechanics. That protocol itself authorizes no new Phase 8 runtime tooling; D-033 is a separate pre-release UI access authorization. `intentos compare` remains conditional and is not implemented.

No slice is complete: 8A sessions have not begun, 8B is at the manual-template stage, and 8C task collection has not begun. First-use targets are 3 sessions and at least 2 first-time users, covering Windows and POSIX, with at least 2 independent completions. The external gate targets 20 new task observations and at least 12 eligible controlled pairs across users/projects; the protocol defines the full coverage and promotion rules.

## Current verification baseline

The current UI candidate ran 258 Python unit tests locally, OK with one existing skip, before its final exact-head gate. Historical pre-B1 baseline was 120 tests. Use exact-head CI for the final pass/fail gate rather than treating a local count as release acceptance. Coverage includes review-only classification/policy, release identity, artifact, workflow permission, local UI HTTP security, Windows CRLF inputs, shared presentation assets, Marketplace package, launcher and main-history regressions, plus CLI smoke and dedicated integration checks:

- in-memory MCP v2 protocol smoke
- stdio subprocess MCP host-parity dogfood across four representative cases
- VS Code extension JavaScript syntax smoke with no npm install/build pipeline
- static regression for the repository Extension Development Host launch contract
- real VS Code Extension Host integration checks for workspace and no-workspace executable resolution
- real VS Code Webview task submission/navigation and isolated installed-VSIX activation
- real Chromium local UI acceptance across all six sections, including visible progress/errors, session draft/file retention, CRLF evidence, conservative templates, approvals, and desktop/390px/320px layouts
- release-artifact CI builds and inspects wheel/sdist, then tests clean core, MCP-extra, and sdist installations without publishing

CI covers:

- Ubuntu / Python 3.11
- Ubuntu / Python 3.12
- Ubuntu / Python 3.13
- Windows / Python 3.13 focused regression coverage
- MCP v2 protocol and stdio host-parity checks on Ubuntu / Python 3.13 with the optional `mcp` extra installed
- dependency-free VS Code extension syntax check

## Phase 7C closeout

The 10/10 real-task evidence target is complete. The aggregate result supports no IntentOS product change: no repeated workflow friction met the promotion threshold and no consistent raw-versus-prepared winner emerged. The existing Phase 7B Prepare → Review → Copy workflow remains accepted. Task 7's classifier correction is incorporated; the Task 8 external ARIS baseline repair did not reveal an IntentOS defect. See `docs/PHASE_7C_EVIDENCE.md` and [Issue #21](https://github.com/milad-seify/IntentOS/issues/21) for the concise decision and detailed evidence log.

## Current graphical access candidate

The Phase 7B Command Palette, status-bar and Review Panel still work. The development extension adds an Activity Bar entry and workbench for preparation, explicit-source Project Compass, governance preview, routing, handoff, checkpoint and outcome workflows. The editor invokes existing CLI commands; it does not duplicate core decision logic. Files enter through the native picker and a persistent update or Codex dispatch requires an exact preview and explicit approval. Automatic project scanning, new providers, npm runtime dependencies and MCP client wiring are absent. See [the extension guide](../integrations/vscode/README.md).

The development `intentos ui` command starts a loopback-only browser interface with a guided Prepare → Review → Copy flow. Advanced sections expose the same existing F01–F10 CLI operations and require explicit project paths or evidence files where the core contract does. The local server uses a one-time session URL, cookie, Origin and CSRF checks, bounded inputs and named operations only. See [the UI guide](SIMPLE_UI.md).

## Phase 7A boundary

The MCP surface remains exactly one `prepare_task` tool. It does not read arbitrary local files, execute prepared work, authorize risky actions, mutate the workspace, or expose classifier/router/policy/Skill/workspace/run-record/telemetry/provider tools.

Project context is limited to 32 caller-supplied documents and 6000 characters total in this first slice. See `docs/MCP_DOGFOODING.md` for parity evidence and limits.

## Deliberately deferred

To avoid over-engineering, current access work does **not** add:

- additional MCP tools or Streamable HTTP deployment
- an editor settings framework
- new provider integrations or unattended agent execution
- automatic editor filesystem/context discovery
- `@vscode/test-electron` or a downloaded VS Code test harness; local checks use the installed editor
- an LLM-based classifier
- embeddings or a vector database
- a policy/plugin framework
- provider discovery or failover orchestration
- a telemetry backend
- a hosted/cloud UI
- an autonomous multi-agent execution/checking runtime
- a benchmark-framework dependency

The classifier remains advisory rather than a security authorization boundary.

## Next

1. Complete the D-033 graphical access candidate and verify its exact final source revision, including installed wheel/VSIX and real interactive flows.
2. Present the candidate diff, screenshots, CI and known limits for explicit owner acceptance. The revised integrated source freeze is not effective before that review.
3. Keep Core `1.1.0` publication, a new VS Code Marketplace version, Phase 8A/B/C and owner-led dogfooding separate. Developer UI tests never count as Phase 8 observations.

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

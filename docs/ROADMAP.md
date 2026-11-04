# Roadmap

The roadmap is intentionally outcome-based. Phase boundaries may change as real usage provides evidence.

## Phase 0 — Foundation

Goal: define the product before implementation.

- vision and positioning
- explicit scope and non-goals
- engineering principles
- conceptual architecture
- contributor/agent operating rules
- initial roadmap

Exit criteria: a contributor can explain what IntentOS does, what it does not do, and how a future feature should fit the architecture.

## Phase 1 — Prompt Engineering Core

Goal: reliably transform rough intent into a compact execution contract.

- intent schema
- ambiguity handling
- prompt optimization
- target-tool profiles
- deterministic output contract
- initial test fixtures

Start with a small set of high-value targets rather than broad shallow support.

## Phase 2 — Engineering + Risk Profiles

Goal: make software and DevOps delegation engineering-aware.

- task classification
- risk levels
- software-engineering policy profile
- DevOps policy profile
- approval boundaries
- Definition-of-Done generation

## Phase 3 — Project Context + Agent Workspace

Goal: make outputs project-aware without context bloat.

- repository/project context discovery
- context relevance scoring
- `AGENTS.md` and related context-file support
- stale/duplicate context detection
- safe update proposals

## Phase 4 — AI / Model Routing

Goal: recommend and adapt to the right execution target without vendor lock-in.

- AI tool profiles
- capability/cost classes
- model metadata adapters
- effort recommendations
- graceful fallback when model information is stale or unavailable

## Phase 5 — Evaluation and Learning

Goal: replace subjective prompt quality with evidence.

- prompt/workflow fixtures
- assertions and scoring
- token/latency/retry tracking
- A/B comparisons
- regression evaluation
- reusable lessons promoted into profiles/policies

## Phase 6 — Initial Integrations and OSS Surface

Goal: make the core usable and contributable without bloating it.

Implemented foundation:

- CLI
- Python package/API
- GitHub Actions CI
- portable Agent Skill artifacts
- contributor guidance
- versioned run/evaluation records

## Stabilization — Dogfooding + Independent Audit

Goal: validate the product and public boundaries before freezing a stable v1 contract.

Completed:

- real-world dogfooding and multilingual/context regressions
- Hugging Face ecosystem review and portable Agent Skills/run records
- independent architecture/product/code audit
- usage architecture and ease-of-use principles
- contract-preserving task preparation stabilization
- review-skill dogfooding and focused regression fixes

Independent audit verdict: **NEEDS STABILIZATION**, not architectural redesign. The required preparation-contract stabilization was completed before access-surface implementation began.

## Phase 7 — Access and Agent Interoperability — COMPLETE

Goal: make IntentOS easy to use across environments while preserving one shared core.

### 7A — Minimal MCP adapter — COMPLETE; PARITY GATE PASSED

The first MCP slice exposes exactly **one tool: `prepare_task`** through an optional local stdio adapter using the official stable MCP Python SDK.

Inputs are bounded and explicit:

- user request
- optional target AI/tool
- constraints and success criteria
- optional output format and audience
- bounded caller-supplied project context as `path` labels plus `content`

The structured result exposes:

- ready or clarification status
- prepared execution prompt
- task/risk decision and consequential approval boundaries
- engineering constraints
- selected/omitted context diagnostics
- routing decision
- verification expectations

Current implementation constraints:

- calls the existing shared core; classification/routing/policy logic is not duplicated
- MCP support is an optional package extra; the normal core/CLI install keeps no third-party runtime dependency
- stdio is the first transport for local agent/IDE use
- preparation does not grant execution authorization
- no arbitrary filesystem access; callers supply context content explicitly
- project context is capped at 32 documents and 6000 characters total
- no separate classify/route/policy/verify tools
- workspace planning, Skill helpers, run records, telemetry, provider discovery, and orchestration remain outside the MCP surface
- no generic MCP runtime or autonomous orchestration

Parity evidence:

- the installed `intentos-mcp` entry point is launched as a real stdio subprocess
- the host must discover exactly one tool: `prepare_task`
- complete structured MCP results are compared exactly with CLI JSON and Python API results
- four representative cases cover lightweight security-topic docs, high-risk production auth work, context selection, and clarification

See `docs/MCP_DOGFOODING.md`.

Do not add another MCP tool merely because the protocol can expose one. Expand only from repeated real usage evidence.

### 7B — VS Code extension — COMPLETE

The first editor slice intentionally uses only the existing CLI/machine contract and VS Code built-in APIs.

Implemented:

- one Command Palette action: `IntentOS: Prepare Task`
- selected editor text when present; otherwise a small input prompt
- one temporary review panel rather than a permanent sidebar
- concise interpretation, risk, consequential approval boundaries, context summary, and verification by default
- Copy Prepared Task handoff
- visible `$(sparkle) IntentOS` status-bar launcher reusing the existing prepare command
- public Marketplace distribution as `milad-seyfi.intentos-vscode` (0.1.1), with approved icon and genuine Review screenshot
- advanced routing/context details collapsed by default
- one optional executable-path setting for PATH/virtual-environment cases
- no duplicated classifier/router/policy/context logic in the extension

Current constraints:

- the extension calls `intentos optimize ... --json`
- no automatic filesystem/context discovery
- no agent-specific Send/Execute action
- no MCP client embedded in the extension
- no npm runtime dependency, TypeScript compiler, bundler, telemetry, background service, or provider configuration

Initial editor-slice exit gate:

> Passed: manual Extension Development Host dogfood verified input, Review Panel, and Copy Prepared Task; automated real Extension Host tests verify CLI resolution and execution with and without a workspace. The later 0.1.1 release added a status-bar entry point and Marketplace assets without changing the Prepare → Review → Copy workflow. Further capabilities remain evidence-gated.

### 7C — Real-use evidence gate — COMPLETE

- Collected 10/10 distinct real tasks; paired outcomes were 3 prepared, 2 raw, and 5 inconclusive.
- Task 7's reproducible risk-classification correctness defect was fixed with a focused regression; Task 8's CI issue was a pre-existing external ARIS baseline defect.
- No repeated friction met the promotion threshold and no consistent paired winner emerged.
- Decision: no IntentOS product change; the Phase 7B Prepare → Review → Copy workflow remains accepted.
- A standalone simple UI remains a deferred, evidence-gated candidate; this evidence did not justify starting it. See `docs/PHASE_7C_EVIDENCE.md` and [Issue #21](https://github.com/milad-seify/IntentOS/issues/21).

### 7D — Additional adapters — DEFERRED BY EVIDENCE / CLOSED WITHOUT IMPLEMENTATION

Other IDE, agent, community, and provider/model adapters were candidates, not mandatory deliverables. Phase 7C did not demonstrate enough repeated demand to justify them. KISS/YAGNI therefore requires stopping here. These integrations remain possible future candidates and may be reopened when real adoption evidence establishes a concrete need.

The absence of sufficient demand is the Phase 7 decision, not a failed or abandoned direction. Phase 7 overall is complete.

## Latest owner-authorized full-feature delivery (2026-11-04)

**D-031 supersedes the historical early-final-Freeze plan described below for future work.** All ten F01–F10 outcomes are included in [integrated PR #65](https://github.com/milad-seify/IntentOS/pull/65), including B1 access and B2/C1/D1 implementations. Verify its actual Merge and exact-SHA CI/closeout evidence for final pre-validation source acceptance as governed by [D-032](DECISIONS.md). The earlier stacked-PR references below are historical provenance, not a mandate to merge each PR. The finite workstreams used Phase 0–7 foundations: project governance (F05–F08), agent/routing/resilience (F03/F04/F09), evidence/UX (F10 with F01/F02 regressions), and one consolidated developer gate. A **new Feature Freeze is not effective** until separately accepted. Operational Phase 8 and Idea-to-Production dogfood remain owner-led after that decision; all protocol thresholds remain unchanged. Old stage labels and source pins below are historical provenance.

## Post-Phase-7 Capability Evolution Program — A COMPLETE; B1 INTERNAL; B2/C1/D1 DEFERRED; E READINESS VERIFIED / FINAL FREEZE DEFERRED

This is a finite, evidence-gated development program between completed Phase 7 and operational Phase 8. It is **not a renumbered official Phase**. The [Stage A baseline/plan](POST_PHASE_7_PROGRAM.md) and [candidate capability inventory](FUTURE_CAPABILITIES.md) distinguish planning priorities from approved implementation.

- **Stage A — Planning, Baseline & Governance Alignment (complete; PR #41):** verify repository and existing implementation, preserve a small reproducible baseline, record capability gaps and the revised Phase 8 sequence. Exit: reviewed/accepted finite roadmap, evidence gates and separately approvable first slice.
- **Stage B — Project Continuity Foundation (B1 internal pilot merged; B2 assessment only):** read-only Project Compass/Scope Guardian feasibility first (see [pilot contract](B1_PROJECT_COMPASS_PILOT.md)); controlled state/decision proposals only in later separately approved slices. Exit: source-grounded project status, scope and decisions survive fresh sessions without unsupported completion claims.
- **Stage C — Project Lifecycle Governance (C1 assessment merged; implementation deferred):** [C1 evidence assessment](C1_LIFECYCLE_ASSESSMENT.md) found no sufficient repeated need for runtime governance; use reviewed milestone/DoD/launch evidence manually unless a new scoped gate is met.
- **Stage D — Adaptive Delegation & Resilience (D1 assessment merged; implementation deferred):** [D1 evidence assessment](D1_ADAPTIVE_RESILIENCE_ASSESSMENT.md) found no justified adaptive experiment. Preserve existing deterministic routing, external metrics and manual handoff. No execution/runtime platform.
- **Stage E — Stabilization & Feature Freeze (readiness verified; final Freeze NOT EFFECTIVE):** [readiness PR #46](https://github.com/milad-seify/IntentOS/pull/46) and [PR #47](https://github.com/milad-seify/IntentOS/pull/47) merged with green CI. The old final-freeze [PR #48](https://github.com/milad-seify/IntentOS/pull/48) was **closed without merge** after the accepted Phase 8 schedule and scope review in [PR #49](https://github.com/milad-seify/IntentOS/pull/49), followed by one B2 observation in [PR #50](https://github.com/milad-seify/IntentOS/pull/50). Preserve historical readiness/code pins; [D-029](DECISIONS.md) requires a fresh source/CI freeze gate after intended scope is settled. No Phase 8 start by implication.

Bounded initial implementation candidates: B1 read-only Project Compass; B2 state/decision update **proposals** only if justified; C1 lifecycle/quality-gate review only if justified; D1 a single evidence-supported adaptive slice at most. There is no mandate to implement every candidate. Each slice needs new scope authorization, tests, review, and independent closeout. The sequence may end early with documented deferrals; there is no indefinite feature loop.

## Phase 8 — Adoption & Outcome Validation — PROTOCOL APPROVED; OPERATIONAL EXECUTION DEFERRED

Goal: determine whether first-time users can adopt IntentOS independently and under which real-task conditions preparation improves downstream outcomes. Phase 8 operationalizes existing Phase 5 evaluation primitives; it does not duplicate evaluation algorithms or require a new product feature.

The [validation protocol](PHASE_8_VALIDATION.md) and its numerical targets remain accepted, but operational 8A/8B/8C are **DEFERRED / NOT STARTED** until scope is settled, final Stage E Feature Freeze is separately accepted on the current baseline, real users are available, and operational sessions are explicitly reauthorized. The previous final-freeze PR #48 was closed unmerged, not accepted as an effective Freeze. No slice is complete and no new runtime capability is authorized by the protocol. Complementary final validation will dogfood one real project from idea to production, without treating one project as a substitute for the multi-user/multi-project evidence targets.

### 8A — First-use validation — GATED; NOT COMPLETE

Observe public installations outside the IntentOS checkout through preparation and external handoff. Target 3 sessions, at least 2 first-time users, Windows and POSIX coverage, and at least 2 independent completions. Fix only demonstrated blockers; sessions require a subsequent task.

### 8B — Outcome evidence workflow — GATED; NOT COMPLETE

Start with the protocol's bounded manual worksheet for shared conditions and raw/prepared outcomes. Reuse existing evaluation/run-record primitives, preserve unknown metrics and privacy, and record evidence-entry friction. This protocol did not authorize a comparison CLI; later D-031 authorized a development outcome CLI as part of F10. Its synthetic developer tests do not satisfy the Phase 8 evidence target.

### 8C — External evidence gate — GATED; NOT COMPLETE

Target 20 new distinct task observations, at least 2 users including a non-maintainer, at least 3 projects, and at least 12 eligible controlled pairs across multiple task types and risk levels. Do not recount Phase 7C tasks or lower collection targets silently. Correctness outranks efficiency; unchanged product and insufficient evidence are valid outcomes. Full controls and promotion rules live in the protocol.

## Later ecosystem directions

Potential extension points, not current core commitments:

- profile/plugin registry
- provider latency/failover policy adapters
- telemetry/OpenTelemetry adapters
- execution trace adapters
- additional MCP tool contracts
- hosted collaboration features where local-first workflows are insufficient

## Product discipline

Each phase should prefer the smallest usable slice, real-world dogfooding, tests before expansion, and documented decisions. Features should not enter the core solely because one AI vendor currently exposes them.

Ease of use is part of product quality: common workflows should become simpler as integrations improve, while advanced control remains available without forcing complexity on everyday users.

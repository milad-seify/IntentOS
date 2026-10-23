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

## Phase 7 — Access and Agent Interoperability

Goal: make IntentOS easy to use across environments while preserving one shared core.

### 7A — Minimal MCP adapter — IMPLEMENTED + PARITY GATE PASSED

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

### 7B — VS Code extension — NEXT

Minimum useful editor experience:

- prepare typed or selected text from the Command Palette
- show concise interpretation, consequential risk/approval, context summary, and verification summary in a temporary review panel
- offer Copy Prepared Task first
- keep full prompt, taxonomy, context scores, routing metadata, and other expert controls behind progressive disclosure
- remain a thin adapter over the shared preparation contract

Do not build a permanent sidebar, agent-specific execution bridge, settings framework, or broad editor feature set until usage justifies it.

### 7C — Simple user interface

- outcome-first workflow for non-expert users
- no prompt-engineering prerequisite
- safe defaults
- advanced controls through progressive disclosure
- choose desktop/web/other surface from observed usage rather than assumption

### 7D — Additional adapters

- other IDEs and agent surfaces
- community integrations
- provider/model metadata adapters where real usage requires them

Add these only from demonstrated demand; do not build broad shallow integrations for their own sake.

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

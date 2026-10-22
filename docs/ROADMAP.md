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

Independent audit verdict: **NEEDS STABILIZATION**, not architectural redesign.

## Stabilization Gate — Contract-Preserving Task Preparation

Goal: make the existing preparation path trustworthy before building additional access surfaces.

Required outcomes:

- preserve user-supplied content, formatting, constraints, audience, and output requirements
- keep background context from silently weakening mutation-risk boundaries
- make deterministic task/risk matching less brittle without introducing an LLM dependency
- make context ranking, budgeting, deduplication, path handling, and workspace proposals safe and explainable
- provide consistent clarification/error/structured-result behavior across CLI and API-facing contracts
- keep evaluation metrics internally consistent and reject misleading evidence
- verify regressions on Linux and Windows

Acceptance criterion:

> Preparation preserves the user's meaning, exposes uncertainty, and produces reviewable boundaries consistently across CLI and API.

Only confirmed defects and measured dogfood failures should expand this milestone. Do not add speculative frameworks, orchestration, embeddings, or integrations to solve hypothetical future problems.

## Phase 7 — Access and Agent Interoperability

Goal: make IntentOS easy to use across environments while preserving one shared core.

Begin only after the stabilization gate passes real dogfood checks.

### 7A — Minimal MCP adapter

Start with **one MCP tool: `prepare_task`**.

Inputs should remain bounded and explicit:

- user request
- optional target AI/tool
- constraints and success criteria
- bounded caller-supplied project context

The structured result should expose:

- ready or clarification status
- prepared execution prompt
- task/risk decision and consequential approval boundaries
- engineering constraints
- selected/omitted context diagnostics
- verification expectations

Constraints:

- call the existing shared core; do not duplicate classification/routing/policy logic
- preparation must not grant execution authorization
- no arbitrary filesystem access in the first MCP slice
- do not expose classify/route/policy/verify as separate MCP tools initially
- keep workspace planning, Skill helpers, run records, and additional MCP operations separate until real use demonstrates they are needed
- do not turn IntentOS into a generic MCP runtime or agent orchestrator

### 7B — VS Code extension

Minimum useful editor experience:

- prepare a typed request or selected text
- show concise interpretation, consequential risk/approval, context summary, and verification summary
- offer Copy Prepared Task / Send to Agent handoff
- put full prompt, taxonomy, context scores, routing metadata, and other expert controls behind progressive disclosure
- remain a thin adapter over the shared preparation contract

Start with Command Palette actions and a temporary review panel; do not commit to a permanent sidebar until usage justifies it.

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

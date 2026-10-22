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

- real Codex / Claude Code / ChatGPT workflows
- regression fixtures from real failures
- multilingual/context edge cases
- external architecture/quality audit
- verify that product scope, core APIs, and integration boundaries remain coherent

## Phase 7 — Access and Agent Interoperability

Goal: make IntentOS easy to use across environments while preserving one shared core.

Preferred delivery order:

### 7A — MCP adapter

- expose bounded IntentOS operations to compatible agents
- optimize/prepare task
- task/risk/context/policy access
- verification contract access
- portable Skill and run-record helpers
- no generic MCP runtime or autonomous orchestration

### 7B — VS Code extension

- editor-native task preparation
- selected-text/request refinement
- task/risk/context preview
- approval and verification visualization
- workspace proposal review
- copy/send handoff to connected agents
- thin adapter over core/MCP/API rather than duplicated decision logic

### 7C — Simple user interface

- outcome-first workflow for non-expert users
- no prompt-engineering prerequisite
- safe defaults
- advanced controls through progressive disclosure
- validate whether this should be standalone desktop/web or another low-friction surface based on real usage

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
- MCP tool contracts for external systems
- hosted collaboration features where local-first workflows are insufficient

## Product discipline

Each phase should prefer the smallest usable slice, real-world dogfooding, tests before expansion, and documented decisions. Features should not enter the core solely because one AI vendor currently exposes them.

Ease of use is part of product quality: common workflows should become simpler as integrations improve, while advanced control remains available without forcing complexity on everyday users.

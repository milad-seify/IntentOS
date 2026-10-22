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

## Phase 6 — Integrations and Ecosystem

Goal: let the community extend IntentOS without bloating the core.

Possible directions:

- CLI
- IDE/agent integrations
- GitHub workflows
- profile/plugin registry
- CI evaluation
- community-contributed AI and domain profiles

These are candidates, not commitments.

## Product discipline

Each phase should prefer the smallest usable slice, real-world dogfooding, tests before expansion, and documented decisions. Features should not enter the core solely because one AI vendor currently exposes them.

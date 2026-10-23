# Decisions

This file records durable product and architecture decisions. Keep entries concise and append new decisions rather than rewriting history without explanation.

## D-001 — Vendor-neutral core

**Status:** Accepted

IntentOS core concepts must not depend on one AI vendor, model family, IDE, or agent surface. Provider-specific behavior belongs in replaceable profiles/adapters.

## D-002 — Intent-to-execution, not prompt templates

**Status:** Accepted

Prompt optimization is a core capability, but the product boundary also includes context selection, risk classification, engineering policy, workflow/approval boundaries, verification, and evaluation.

## D-003 — Contextual engineering principles

**Status:** Accepted

Clean Code, SOLID, DRY, KISS, YAGNI, security, testability, and DevOps practices are applied according to task context and risk. IntentOS must not force heavyweight architecture or process onto small tasks.

## D-004 — Minimal sufficient context

**Status:** Accepted

IntentOS should prefer the smallest authoritative context that can materially improve an outcome. Context volume is a cost and reliability concern, not a proxy for quality.

## D-005 — Evidence-backed completion

**Status:** Accepted

Generated workflows should define how completion is verified. Agent claims alone are not sufficient evidence for work that can be checked.

## D-006 — Agent workspace maintenance is in scope

**Status:** Accepted

IntentOS may create, update, or recommend bounded agent-facing context files such as `AGENTS.md`, status, architecture, decision, and task context documents while preserving human ownership and avoiding duplication.

## D-007 — Implementation stack deferred

**Status:** Superseded by D-008

Phase 0 intentionally did not select an implementation language, framework, storage layer, or deployment platform. Stack selection was deferred until Phase 1 interfaces and use cases were clear enough to implement the smallest core.

## D-008 — Python standard-library core first

**Status:** Accepted

The first implementation uses Python 3.11+ with no runtime dependencies. The Phase 1 problem is primarily data contracts, normalization, deterministic compilation, and tests; a framework would add cost without evidence of need. Vendor-specific integrations remain outside the core.

## D-009 — Clarify instead of fabricating missing critical intent

**Status:** Accepted

When a critical field such as the goal or execution target is genuinely ambiguous, IntentOS returns bounded clarification questions instead of inventing requirements. Clarification is capped and deterministic; low-risk formatting details may use safe defaults.

## D-010 — MIT license for the initial open-source project

**Status:** Accepted

IntentOS uses the MIT License initially to keep adoption, experimentation, and contribution friction low. This can be revisited only with an explicit project-governance decision.

## D-011 — Engineering policy is contextual, composable, and deterministic

**Status:** Accepted

Software-engineering and DevOps guidance is selected from task type and risk level rather than injected globally. KISS/YAGNI lead by default; SOLID, DRY, Clean Code, security controls, reproducibility, rollback, and approval boundaries appear only when they materially fit the task.

## D-012 — Risk controls process depth, not implementation style

**Status:** Accepted

Risk classification determines approval boundaries and completion evidence. It must not automatically force a specific architecture, framework, or abstraction level. High-risk work receives stronger guardrails; low-risk work stays lightweight.

## D-013 — Context is ranked, bounded, and deduplicated

**Status:** Accepted

Project context is selected by relevance plus source authority, not by loading the entire repository. Agent guidance, status, decisions, and architecture receive priority; duplicate and irrelevant content is omitted and a character budget bounds the handoff.

## D-014 — Workspace maintenance is proposal-first

**Status:** Accepted

The core may detect missing, stale, duplicate, or bloated agent context and produce create/update/keep proposals. Applying repository writes belongs to an integration boundary and must respect approval rules rather than silently mutating a workspace.

## D-015 — Route by capability class, not hardcoded model names

**Status:** Accepted

Core routing chooses required capability and effort from task/risk, then optionally selects from caller-supplied model metadata. Model names, availability, and provider-specific controls are volatile and belong in replaceable catalogs/adapters.

## D-016 — Prefer the lowest-overhead model that meets the quality bar

**Status:** Accepted

When multiple compatible candidates satisfy the required capability, IntentOS prefers verified metadata, the smallest sufficient capability class, then lower relative cost. If no compatible metadata exists, it returns a deterministic capability-level fallback instead of inventing a model.

## D-017 — Portable Skills are a first-class output artifact

**Status:** Accepted

Reusable agent guidance should be compilable into an Agent Skills-compatible `SKILL.md` artifact with standard `name` and `description` frontmatter. IntentOS emits the artifact but does not silently install it or write it into agent-specific directories. This keeps portable context separate from execution and preserves proposal-first workspace behavior.

## D-018 — Evaluation provenance uses versioned run records

**Status:** Accepted

IntentOS exposes a compact, versioned run record for reproducible evaluation across agents and models. The record stores a prompt fingerprint and routing/context provenance plus externally supplied quality, token, latency, and retry metrics. Raw prompts, tool outputs, storage, telemetry backends, and dataset publishing remain executor/integration concerns.

## D-019 — One core, multiple access surfaces

**Status:** Accepted

CLI, Python API, MCP, VS Code, Agent Skills, and future simple user interfaces are adapters around one shared IntentOS core. They must not independently reimplement task/risk classification, context selection, engineering policy, routing, approval, or verification logic. Surface-specific code may adapt presentation, transport, editor context, or interaction flow only.

## D-020 — Ease of use uses progressive disclosure

**Status:** Accepted

IntentOS must be usable without prompt-engineering, model-routing, or MCP expertise. Common workflows should expose outcome-first actions and safe defaults; advanced users may inspect or override deeper context, routing, policy, cost, and verification details through progressive disclosure. Simplicity must not weaken high-risk approval or safety boundaries.

## D-021 — First MCP integration is optional, stdio-first, and single-tool

**Status:** Accepted

The first MCP integration uses the official stable Python SDK as an optional package extra so the core keeps no third-party runtime dependency. It exposes exactly one local stdio tool, `prepare_task`, which calls the shared preparation core and returns the shared machine result contract. Caller-supplied project context is bounded and passed as content; MCP does not gain arbitrary filesystem access, execution authority, workspace mutation, orchestration, or additional tools until real usage demonstrates a need.

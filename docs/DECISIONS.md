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

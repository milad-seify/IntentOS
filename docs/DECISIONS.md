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

**Status:** Accepted

Phase 0 intentionally does not select an implementation language, framework, storage layer, or deployment platform. Stack selection should follow validated Phase 1 interfaces and use cases.

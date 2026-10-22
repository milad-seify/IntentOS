# AGENTS.md

This file defines repository-level rules for AI coding agents and contributors using agents.

## Product intent

IntentOS is an intent-engineering and workflow layer between humans and AI systems. Do not reduce it to a prompt-template library and do not expand it into a general-purpose autonomous-agent platform.

Read `README.md` and the relevant files in `docs/` before proposing architecture or implementation changes.

## Engineering rules

- Prefer the smallest coherent change that satisfies the task.
- Follow KISS and YAGNI. Apply SOLID, DRY, Clean Code, and architectural patterns only where they materially improve the design.
- Do not introduce frameworks, dependencies, services, databases, queues, or infrastructure without a demonstrated need.
- Keep the core vendor-neutral. AI/model-specific behavior belongs behind profiles/adapters.
- Keep agent-facing context human-readable, bounded, and reviewable.
- Preserve existing public contracts unless the task explicitly changes them.
- Security, destructive operations, persistent data changes, and external writes require explicit boundaries.
- Never claim completion without evidence appropriate to the task.

## Scope discipline

Do not perform unrelated refactors or cleanup while implementing a scoped task. If a material adjacent problem is discovered, report it separately.

Do not invent product requirements. When a requirement is ambiguous and the risk of choosing incorrectly is material, surface the ambiguity. For low-risk implementation details, choose the simplest reversible option consistent with the documented principles.

## Documentation discipline

Documentation is part of the product contract.

Update docs when a change alters product scope, architecture, a durable decision, agent behavior, or roadmap status. Avoid duplicating the same rule across many files.

## Verification

For implementation tasks, report:

- files changed
- checks/tests executed
- their results
- unresolved risks or assumptions

Use focused checks first, then the broader relevant test suite when available.

## Current phase

The initial Phase 0–6 roadmap is implemented. Current work is stabilization and real-world dogfooding. Prefer regression fixes, clearer extension boundaries, verified community use cases, and measurable improvements over speculative features. New integrations should remain thin adapters around the existing core and must preserve proposal/approval boundaries for repository writes.

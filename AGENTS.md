# AGENTS.md

This file defines repository-level rules for AI coding agents and contributors using agents.

## Product intent

IntentOS is an intent-engineering and workflow layer between humans and AI systems. Do not reduce it to a prompt-template library and do not expand it into a general-purpose autonomous-agent platform.

Read `README.md` and the relevant files in `docs/` before proposing architecture or implementation changes. For user-facing integrations or access surfaces, read `docs/UX.md` as part of the product contract.

## Engineering rules

- Prefer the smallest coherent change that satisfies the task.
- Follow KISS and YAGNI. Apply SOLID, DRY, Clean Code, and architectural patterns only where they materially improve the design.
- Do not introduce frameworks, dependencies, services, databases, queues, or infrastructure without a demonstrated need.
- Keep the core vendor-neutral. AI/model-specific behavior belongs behind profiles/adapters.
- Keep CLI, MCP, VS Code, UI, and other access surfaces thin; do not duplicate core task/risk/context/policy/routing/verification logic in integrations.
- Keep agent-facing context human-readable, bounded, and reviewable.
- Preserve existing public contracts unless the task explicitly changes them.
- Security, destructive operations, persistent data changes, and external writes require explicit boundaries.
- Never claim completion without evidence appropriate to the task.

## UX rules

- Ease of use is a product requirement, not optional polish.
- Everyday users should not need prompt-engineering, model-routing, MCP, or internal architecture knowledge.
- Prefer outcome-first language and safe defaults.
- Use progressive disclosure: advanced controls should be available without becoming mandatory for common workflows.
- Preserve semantically consistent core behavior across CLI, API, MCP, editor integrations, Agent Skills, and future UI surfaces.

## Scope discipline

Do not perform unrelated refactors or cleanup while implementing a scoped task. If a material adjacent problem is discovered, report it separately.

Do not invent product requirements. When a requirement is ambiguous and the risk of choosing incorrectly is material, surface the ambiguity. For low-risk implementation details, choose the simplest reversible option consistent with the documented principles.

Do not add an abstraction merely to anticipate MCP, VS Code, hosted services, provider routing, or future plugins. Promote a new abstraction only when the current core or repeated real usage demonstrates the need.

## Documentation discipline

Documentation is part of the product contract.

Update docs when a change alters product scope, architecture, UX/access surfaces, a durable decision, agent behavior, or roadmap status. Avoid duplicating the same rule across many files.

## Verification

For implementation tasks, report:

- files changed
- checks/tests executed
- their results
- unresolved risks or assumptions

Use focused checks first, then the broader relevant test suite when available.

## Current phase

Phase 7A MCP/core parity is proven. Phase 7B now has the **minimum useful VS Code slice**: one `IntentOS: Prepare Task` command, typed/selected request capture, a temporary review panel, and Copy Prepared Task. The current gate is editor dogfooding, not feature expansion.

Keep Phase 7B thin:

- preserve the one-command Prepare → Review → Copy workflow until real use exposes a concrete gap
- keep the temporary review panel instead of adding a permanent sidebar
- show concise interpretation, consequential risk/approval, context summary, and verification by default
- keep routing/context internals behind progressive disclosure
- keep the extension as a transport/UX adapter over `intentos optimize ... --json`; do not duplicate classifier/router/policy/context logic in JavaScript
- promote observed editor UX or contract failures into focused regressions before adding capabilities

Do not add another MCP tool, Streamable HTTP deployment, automatic filesystem/context discovery, workspace mutation, agent-specific Send/Execute wiring, VS Code sidebar/activity-bar UI, packaging/Marketplace infrastructure, settings frameworks, hosted services, plugin systems, LLM classification, embeddings/vector search, provider discovery, or telemetry infrastructure unless real usage demonstrates a concrete need.

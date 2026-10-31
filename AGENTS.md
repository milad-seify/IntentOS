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

Phase 7 is **complete**. Phase 7A MCP parity, Phase 7B VS Code access, and the Phase 7C real-use evidence gate are complete. Phase 7D was intentionally deferred and closed without implementation because additional adapter demand did not meet the evidence threshold. No follow-on phase is defined or started.

The completed evidence and decision are recorded in `docs/PHASE_7C_EVIDENCE.md`. Any future product proposal requires a new evidence-backed planning decision.

Carry forward these evidence requirements for future product proposals:

- use real tasks to record concrete friction, rework, context gaps, verification gaps, and outcome evidence
- promote correctness, safety, or public-contract failures directly into focused regressions
- require repeated evidence before adding a new capability or access surface
- treat ideas from other projects as hypotheses, not product requirements
- prefer a small paired evaluation when outcome quality is uncertain rather than subjective prompt tuning
- keep optional measures such as cost, tokens, time, code size, and test results manual or already-available; do not add telemetry infrastructure just to collect them

Preserve the Phase 7B Prepare → Review → Copy workflow until repeated real use demonstrates a concrete gap.

Do not add another MCP tool, Streamable HTTP deployment, automatic filesystem/context discovery, workspace mutation, agent-specific Send/Execute wiring, VS Code sidebar/activity-bar UI, broaden the current Marketplace release workflow, add settings frameworks, hosted services, plugin systems, LLM classification, embeddings/vector search, provider discovery, telemetry infrastructure, autonomous multi-agent orchestration/checkers, benchmark-framework dependencies, or a standalone simple UI unless real usage demonstrates a concrete need.

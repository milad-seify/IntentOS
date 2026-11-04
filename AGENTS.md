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

**LATEST ACCEPTED SCOPE OVERRIDE (D-031, 2026-11-04):** The owner requires **all ten feature families** from [docs/DELIVERY_PROGRAM.md](docs/DELIVERY_PROGRAM.md) be implemented before final consolidated acceptance and owner-led Phase 8/Dogfooding. Previous notes below that B2/C1/D1 are deferred or D-030 proposes a final pre-validation cutoff are **historical only and superseded for implementation planning**. [PR #53](https://github.com/milad-seify/IntentOS/pull/53) closed unmerged; [Issue #52](https://github.com/milad-seify/IntentOS/issues/52) reopened. B1 remains internal until a separately versioned stable integration; B2/C1/D1 are required but **not yet complete**. Preserve bounded change design, explicit human approvals and safe regressions per slice, then one comprehensive final system gate. Do not start operational Phase 8 sessions or owner dogfood until the feature set is complete and a newly accepted Freeze is recorded. No unapproved new capabilities beyond F01–F10.

Phase 7 is **complete**. Phase 7A MCP parity, Phase 7B VS Code access, and the Phase 7C real-use evidence gate are complete. Phase 7D was intentionally deferred and closed without implementation because additional adapter demand did not meet the evidence threshold.

Phase 8 — Adoption & Outcome Validation has an **approved protocol; operational execution is deferred until final validation after a separately accepted feature freeze**. Preserve every existing first-use, controlled-comparison, external-evidence, privacy and promotion criterion in `docs/PHASE_8_VALIDATION.md`. Do not begin Phase 8 sessions or implement Phase 8B tooling without a separate authorization.

The completed Phase 7 evidence and decision are recorded in `docs/PHASE_7C_EVIDENCE.md`. Stage A planning is accepted in PR #41. The separately authorized **B1 internal read-only pilot** was merged in [PR #42](https://github.com/milad-seify/IntentOS/pull/42), but remains non-public and has not been promoted to a stable feature. B2 remains **deferred pending evidence** after its [assessment PR #43](https://github.com/milad-seify/IntentOS/pull/43). C1 assessment was merged in [PR #44](https://github.com/milad-seify/IntentOS/pull/44); C1 implementation remains deferred pending evidence. D1 assessment was merged in [PR #45](https://github.com/milad-seify/IntentOS/pull/45); its implementation is deferred pending evidence. **Stage E readiness passed** ([PR #46](https://github.com/milad-seify/IntentOS/pull/46), [7/7 post-merge main CI](https://github.com/milad-seify/IntentOS/actions/runs/41807465709)); **Stage E readiness remains historically verified, but formal final Feature Freeze is NOT EFFECTIVE**: the old D-028 closeout [PR #48](https://github.com/milad-seify/IntentOS/pull/48) was closed without merge after a revised scope/validation schedule. [D-029](docs/DECISIONS.md) records the accepted disposition. PRs [#49](https://github.com/milad-seify/IntentOS/pull/49) and [#50](https://github.com/milad-seify/IntentOS/pull/50) are merged, recording Phase 8 deferral and **one** B2 continuity observation (not a promotion gate). The final Freeze requires a fresh verified pin and separately accepted closeout after scope is settled. See `docs/STAGE_E_FREEZE_READINESS.md`. The finite program and existing candidate inventory remain authoritative. Confirm actual `main`, accepted decisions, and observed evidence before each scope decision. B2/C1/D1 and further runtime changes require separate approval. External agents own execution and runtime checkpoints; IntentOS remains an advisory control/trust layer. Do not automatically start subsequent slices.

Carry forward these evidence requirements for future product proposals:

- use real tasks to record concrete friction, rework, context gaps, verification gaps, and outcome evidence
- promote correctness, safety, or public-contract failures directly into focused regressions
- require repeated evidence before adding a new capability or access surface
- treat ideas from other projects as hypotheses, not product requirements
- prefer a small paired evaluation when outcome quality is uncertain rather than subjective prompt tuning
- keep optional measures such as cost, tokens, time, code size, and test results manual or already-available; do not add telemetry infrastructure just to collect them

Preserve the Phase 7B Prepare → Review → Copy workflow until repeated real use demonstrates a concrete gap.

Do not add another MCP tool, Streamable HTTP deployment, automatic filesystem/context discovery, workspace mutation, agent-specific Send/Execute wiring, VS Code sidebar/activity-bar UI, broaden the current Marketplace release workflow, add settings frameworks, hosted services, plugin systems, LLM classification, embeddings/vector search, provider discovery, telemetry infrastructure, autonomous multi-agent orchestration/checkers, benchmark-framework dependencies, or a standalone simple UI unless real usage demonstrates a concrete need.

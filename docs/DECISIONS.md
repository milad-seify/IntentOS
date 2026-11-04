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

## D-022 — Evidence gates adapter expansion

**Status:** Accepted

Do not implement additional IDE, agent, provider, MCP, or access-surface adapters merely to fill a roadmap slot. The existing shared-core access surfaces are sufficient until repeated real usage demonstrates a concrete need. A deferred evidence-gated item may be closed without implementation when its promotion threshold is not met. This preserves KISS/YAGNI, evidence-backed development, and avoids broad shallow integrations.

## D-023 — Reliable AI delegation through contracts and evidence

**Status:** Accepted

IntentOS is a vendor-neutral control and trust layer between human intent and AI execution. Its durable responsibilities are the intent contract, context governance, risk/approval boundaries, verification contract, portable handoff, and outcome evidence/learning described in [VISION.md](VISION.md). Agents execute the work; humans and execution systems enforce permissions and approvals. Trust comes from explicit boundaries and verification evidence, not guaranteed AI correctness.

Software engineering and DevOps remain the initial implemented domains. Broader professional adoption is a long-term vision, with new domains and UX subject to evidence and separate scope approval. This positioning clarifies the existing architecture and does not authorize new runtime capabilities.


## D-024 — Defer operational Phase 8 until final validation

**Status:** Accepted (2026-11-03, post-Phase-7 program scheduling)

Phase 8's existing Adoption & Outcome Validation protocol remains approved and its 8A/8B/8C targets, paired-comparison controls, privacy rules and promotion thresholds remain unchanged. Operational sessions and outcome collection are explicitly rescheduled to **after a recorded feature freeze** for the bounded post-Phase-7 capability program. Before development, only a lightweight, explicitly provenance-labeled baseline is allowed; it is not Phase 8 evidence. Add one independently scoped Idea-to-Production dogfooding project as a complementary final track, not as a replacement for the established multi-user/multi-project targets. No Phase 8 activity may start automatically, and its status must not be called complete without observed evidence.

**Rationale:** Evaluate the selected evolution as a coherent product after development, without bypassing correctness-first evidence discipline or repeatedly resetting evaluation assumptions.

**Consequences:** Update roadmap/agent guidance/status only now; retain the original methodology in `PHASE_8_VALIDATION.md`. Any subsequent capability or operational session requires separate approval.

## D-025 — Time-bounded, evidence-gated capability evolution

**Status:** Accepted as a development-program boundary and planning authorization; **individual runtime slices not approved**

A finite Stage A–E program may plan project continuity, scope review, decision history, lifecycle governance, and conditional adaptive delegation before Phase 8. Existing context selection, workspace proposals, routing, run records, tests and shared access surfaces must be reused before introducing new modules or contracts. [Candidate priorities](FUTURE_CAPABILITIES.md) are hypotheses, not backlog commitments; Phase 7C did not promote new features. Development may begin only after an evidence/feasibility gate and separate, narrowly scoped acceptance. An early reversible prototype before repeated evidence is an exception requiring explicit recorded authorization and cannot silently enter stable v1.

IntentOS remains a **vendor-neutral, advisory control-and-trust layer**. External agents own execution, runtime planning, browser/filesystem actions, and checkpoints. No autonomous orchestrator, database, provider/telemetry framework, new adapter or public schema is authorized by Stage A. The accepted [VISION.md](VISION.md) North Star is not replaced by the candidate Idea-to-Production program tagline. Each independently accepted slice must be closed or deferred before the next; Stage E freezes features.

## D-026 — B1 read-only feasibility pilot; stable promotion remains gated

**Status:** Accepted for bounded, reversible non-public pilot only (2026-11-03); not approved as a stable user-facing capability.

After Stage A acceptance, the maintainer gave separate approval to proceed with B1. Existing Phase 7C evidence did **not** satisfy repeated-feature promotion criteria, so this is an explicit, bounded pre-gate **prototype exception**, not a declaration of demonstrated user benefit. The experiment is limited to caller-supplied, human-readable project documents, deterministic source-grounded scope/status review, uncertainty handling, and focused tests. It does not change published v1 surfaces or give execution/permission authority.

The implementation remains internal and review-only, with [acceptance criteria and limitations](B1_PROJECT_COMPASS_PILOT.md). Record CI evidence and independently review feasibility; subsequent API/UX promotion, B2, C1, D1, and Phase 8 all need separate decisions. If the evidence fails, do not represent the pilot as product-ready.

## D-027 — Stage E source-freeze readiness, pending final acceptance

**Status:** **READINESS ACCEPTED; FORMAL FEATURE FREEZE PENDING** (2026-11-04). The readiness PR #46 merged as `28dc5c84ea4d154a99cf68c7446303648f076d52` and [post-merge CI 41807465709](https://github.com/milad-seify/IntentOS/actions/runs/41807465709) passed all seven jobs. This acceptance is not a Phase 8 authorization.

The [Stage E readiness review](STAGE_E_FREEZE_READINESS.md) checked `main` `976db7ef888d26aca8804490147e384273cfa9b7` and [seven green CI jobs](https://github.com/milad-seify/IntentOS/actions/runs/41805348708). All 19 shared Python modules matched the published Core `v1.0.1` tag; four principal VS Code files matched `vscode-v0.1.1`. New `intentos.compass` B1 is internal only; B2/C1/D1 implementation remains deferred. Existing public contracts are preserved. The review scoped trust and privacy boundaries but did **not** perform new independent security certification, public first-use observation or full VS Code Extension Host run.

**Proposed consequence:** after an explicitly accepted documentation-only freeze PR, its exact-head CI, a verified merge and green post-merge main CI, pin the final accepted SHA and record **FEATURE FROZEN** in a separate closeout decision/status update. The public distribution remains Core `1.0.1` and VS Code `0.1.1`, which do not expose B1; any future B1 publication needs separate versioned release/promotion. A local wheel rebuilt from post-release source carries modified content under `1.0.1` metadata and **must not** be republished as the existing public release.

Do not start Phase 8 or Idea-to-Production dogfooding without their separate authorizations. Material post-freeze correctness/security changes require an approved, re-verified freeze baseline, not a silent change.

## D-028 — Formal Feature Freeze: evidence-verified closeout pending final merge

**Status:** **FINAL CLOSEOUT PROPOSED / NOT YET EFFECTIVE** (2026-11-04). PR #47 was accepted and merged; the remaining gate is explicit approval of this docs-only closeout, its exact-head CI, merge, successful post-merge main CI, and recording the resulting final SHA.

**Pinned source-code baseline:** `28dc5c84ea4d154a99cf68c7446303648f076d52` — [merged PR #46](https://github.com/milad-seify/IntentOS/pull/46), [green post-merge CI 41807465709](https://github.com/milad-seify/IntentOS/actions/runs/41807465709) (7/7 jobs). [Stage E review](STAGE_E_FREEZE_READINESS.md) verified public-contract/packaging boundaries and recorded remaining risks. There are no new authorized runtime features in this closeout.

**Proposed frozen scope:** the existing public v1 contract, current CLI/MCP/VS Code Prepare → Review → Copy boundaries, and internal-only B1 Project Compass. B1 is source-only, experimental, non-public and not independently adoption-validated. B2, C1 and D1 implementations are deferred pending evidence; do not treat them as required unfinished features. No autonomous execution, project memory database, model quota guarantee, checkpoint/resume, provider SDK or new public schema is included.

**Release distinction:** publicly distributed Core remains PyPI `intentos-engineering==1.0.1`, VS Code `milad-seyfi.intentos-vscode@0.1.1`. B1 is absent from the public `1.0.1` release even though post-release checkout metadata still says `1.0.1`; a rebuilt wheel would be **different content with the same version**, so do not publish or characterize it as the original artifact. Any B1 promotion or new version needs an independent decision.

**Readiness evidence accepted:** [PR #47](https://github.com/milad-seify/IntentOS/pull/47) merged into `main` at `ac2a530c1a42e9fa0e270201fb08741895d49ccb`; exact [post-merge main CI 41809585163](https://github.com/milad-seify/IntentOS/actions/runs/41809585163) passed all **7/7** jobs. The source-code baseline is now pinned to that SHA (its changes relative to the earlier reviewed source were documentation only).

**Final acceptance gate:** independently approve and merge this separate documentation-only D-028 closeout after exact-head CI; verify its post-merge main CI and record that **exact final merge SHA** in the PR closeout evidence and accepted status. The freeze becomes effective only after those conditions actually hold. Until then, status is **PENDING**, never silently reported as Frozen. A material correctness/security fix requires a focused regression and refreshed pin; no routine new features.

**Phase 8:** operational 8A/8B/8C sessions and the separate Idea-to-Production dogfood remain **not started** and require **separate explicit approval after effective feature freeze**. Preserve [Phase 8 methodology](PHASE_8_VALIDATION.md), privacy, non-maintainer coverage, and correctness-first paired evidence; never count Phase 7C history as fresh Phase 8 observations.

# Full-Scope Delivery Program — one finite implementation path

**Status:** OWNER-DIRECTED FULL FEATURE SCOPE; all ten feature families have a stacked development candidate, **not yet owner-accepted or frozen**.
**Decision date:** 2026-11-04. **Starting verified `main`:** `0857d9063811266d4e63d43fccfe259f240c46c5`; [main CI 41822005898](https://github.com/milad-seify/IntentOS/actions/runs/41822005898) succeeded 7/7. **No new Feature Freeze is effective.**

## Goal and decision change

Deliver a coherent IntentOS release capable of steering a real software project from intent to independently verified launch handoff **across long-lived tasks and multiple AI agents**, including project context, scope control, approved decisions, milestones, model/agent delegation, interruption/recovery guidance, and learning from actual outcomes. **All ten owner-requested feature families are required; none is dropped as optional or permanently deferred.**

This supersedes **the early final-Freeze cutoff candidate [PR #53](https://github.com/milad-seify/IntentOS/pull/53)** (closed unmerged), and **the earlier evidence-based B2/C1/D1 implementation deferrals only for this owner-approved delivery scope**. Prior observation counts and conservative analyses remain historically true; owner acceptance of scope does **not** manufacture validated user demand or imply code is finished. [Issue #52](https://github.com/milad-seify/IntentOS/issues/52) is reopened for implementation. Stage E readiness evidence stays historical; final Freeze moves to **after all committed features**.

## Required features and user-visible Definition of Done

| ID | Required capability | Starting coverage | Completion contract |
| --- | --- | --- | --- |
| F01 | Turn rough intent into a clear, reviewable execution contract | Implemented core | Continue to normalize goals, critical ambiguities, constraints, success criteria and expected outputs; preserve existing correct results |
| F02 | Detect task risk, safety and human approvals | Implemented core | Risk-adaptive policies and durable approval boundaries remain explicit at every handoff/change/retry; no silent permission increase |
| F03 | Select suitable model, provider/tool and reasoning effort | Basic routing exists | Explain grounded capability/availability/cost trade-offs, respect explicitly supplied metadata, show uncertainty, support a safe fallback and a reproducible recommendation review; no fabricated live prices or availability |
| F04 | Transfer tasks to Codex and other agents | Manual portable handoff exists | Reviewable cross-agent handoff package with goal/context/constraints/DoD, target-specific adaptation and explicitly approved supported dispatch; no implicit autonomous actions or credential exposure; receipt/failure visible |
| F05 | Understand project goal, scope, status and next action (Project Compass) | Internal B1 pilot | Stable supported user flow, provenance for asserted facts, missing/stale/conflict states, no false authority; equivalent core behavior across chosen surfaces |
| F06 | Preserve approved project state, decisions and progress across sessions | B2 assessment, one real observation only | Revision-pinned, human-reviewable state/decision proposals and approved durable updates, replay protection, source/approval evidence, stale-state conflict detection, continuity after a fresh session |
| F07 | Prevent scope drift and uncontrolled feature expansion | Only conservative exact-match B1 review | Flag suspected scope changes with evidence and unknown handling, require explicit owner amendment, leave an audit trail; must not automatically label uncertain scope in-bounds |
| F08 | Milestones, quality gates, DoD and release/launch review | Task DoD only; C1 assessment | Trace accepted requirements to milestones/checks, distinguish proposed/done/verified/approved, block unsupported readiness claims and provide a reviewable launch readiness report |
| F09 | Checkpoint and resume interrupted work | Missing executor-neutral continuity | Portable, versioned checkpoint of approved plan/state/completed evidence/next action; safe restart detects version changes, duplicate irreversible actions and missing approval; execution stays owned by explicit external agent adapters |
| F10 | Measure outcomes, compare variants and learn with approval | Evaluation primitives exist | Practical task/result capture, controlled comparison and reviewable evidence-linked improvement proposals; feedback does not silently rewrite global behavior or imply superiority from unmeasured tasks |

**Product contract:** IntentOS remains a vendor-neutral *control and trust layer*. It may coordinate an external executor only through explicit safe adapters and approval; it does not need to rebuild a universal agent runtime, hosted platform, model-serving backend, or project-management SaaS. These boundaries constrain *implementation method*, **not the availability of the ten required user outcomes**. Unsupported providers must produce explicit unavailable/needs-review status instead of fabricated execution.

## Finite implementation workstreams — no recurring planning loop

| Step | Deliverables | Exit gate / hard stop |
| --- | --- | --- |
| **1. Project Governance** | Finish F05 + implement F06/F07/F08. Start with source-pinned review-only proposals, then explicit approved update pathway, scope-change and milestone verification | Demonstrate fresh-session recovery, stale/conflicting sources, scope-drift rejection, duplicate-safe update, milestone evidence and launch “not ready” behavior. No invented Done; developer CI green |
| **2. Delegation & Recovery** | Finish F03/F04/F09: cost/capability explanation, portable handoffs, explicit approved agent execution/receipt where supported, safe checkpoint/resume and budget guidance | Test cross-agent adaptation, human authorization, secrets-safe failures, interrupted/replayed operations, model fallback and provider-unavailable handling; developer CI green |
| **3. Outcome Quality & UX** | Complete F10 and user access to F05–F09; confirm F01/F02 unchanged and audit review/approval UX across selected interfaces | Test representative owner flows, persisted evidence and actionable improvement proposals, negative paths, stable public compatibility and developer CI |
| **4. Final integration, stabilization and Freeze** | One consolidated complete-feature review, adversarial/privacy/security checks, regressions, Windows/POSIX, CLI/MCP/VS Code/install/release artifact checks, full integration flows, versioned release preparation and exact-source Feature Freeze | **All F01–F10 passed their acceptance cases**, full CI and agreed integration checks pass on the same candidate, explicit owner sign-off, final SHA/CI evidence and rollback/version policy recorded. Then **STOP development** before operational validation |

No fresh issue/assessment is a prerequisite for the next task once the owner has committed the ten-item scope. Implement the smallest coherent changes within these workstreams; do **not** add speculative extra features. If an implementation barrier appears, record the concrete blocker and solve within scope; **do not quietly mark a feature deferred or complete**.

## Verification timing

- **During implementation:** run focused tests, affected regressions, static/contract checks and ordinary CI for each code change. These protect working software and are **not** a substitute for end-to-end acceptance.
- **At the end:** run the **entire integration/regression/performance-as-relevant and deployment-readiness gate together on the final feature-complete revision**. “All tests at the end” means final consolidated acceptance, **not skipping essential developer tests until damage accumulates**.
- **After final Freeze, separately owner-authorized:** operational Phase 8A/8B/8C real-user sessions and the distinct Idea-to-Production Dogfooding project; all [approved numerical criteria](PHASE_8_VALIDATION.md) remain exactly as written. The owner will perform these real-world observations when conditions permit. No synthetic examples, CI runs or developer dogfood are counted as user studies.

## Change control and source of truth

`AGENTS.md`, `docs/STATUS.md`, `docs/DECISIONS.md`, this program and actual GitHub SHA/PR/CI are authoritative. Each code PR marks feature IDs *partial / implemented with evidence* and preserves existing contracts until a separately approved versioning plan. No automatic merge/release or false feature-freeze claim. **One plan, one implementation flow, one final integration gate; no repeated “are we ready to plan?” cycles.**

The first implementation branch covered the initial F06 read-only revision-grounded continuity proposal and regression tests. Later stacked branches added the remaining development access and regressions. The [candidate acceptance record](FULL_SCOPE_CANDIDATE.md) tracks the consolidated developer gate; owner acceptance, merge, versioning and a new Feature Freeze remain separate decisions.

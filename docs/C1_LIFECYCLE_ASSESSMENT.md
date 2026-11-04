# C1 — Project Lifecycle Governance: Needs and Scope Assessment

**Status:** assessment merged in [PR #44](https://github.com/milad-seify/IntentOS/pull/44); **implementation deferred pending evidence** and NOT approved.  
**Date:** 2026-11-04. **Source baseline:** `milad-seify/IntentOS` main `7a47f5289243a0ac0958881126d922e490b0d6aa` ([CI 41801386563](https://github.com/milad-seify/IntentOS/actions/runs/41801386563): seven successful jobs); no PR open when the assessment began.  
**Prior gates:** Stage A [PR #41](https://github.com/milad-seify/IntentOS/pull/41) complete, B1 [PR #42](https://github.com/milad-seify/IntentOS/pull/42) merged as internal pilot only, B2 [PR #43](https://github.com/milad-seify/IntentOS/pull/43) assessed and deferred pending repeated evidence. [Finite program](POST_PHASE_7_PROGRAM.md), [future capabilities](FUTURE_CAPABILITIES.md), [Phase 7C promotion rules](PHASE_7C_EVIDENCE.md#promotion-rules) and [accepted decisions](DECISIONS.md) remain authoritative.

## User outcome / reason to assess

Potential C1 outcome: provide an **advisory, reviewable, evidence-backed** answer to “Which approved requirements/verification gates does this milestone depend on, what is actually demonstrated, and is it safe to *recommend* advancing?” This does not replace a human product owner, a CI system, production controls or external agents. It must never treat an AI-generated checklist or passing tests alone as deployment or milestone approval.

This is a hypothesis from the post-Phase-7 plan. There are **no three distinct new tasks** showing non-blocking milestone-gate friction, **no two independently observed blocking tasks** without a workable manual alternative and **no controlled outcome comparison** supporting an implemented C1 capability. Prior Phase 7C tasks are historical; none is counted as new C1 or Phase 8 evidence.

## Existing implementation and gap (verified at pinned IntentOS commit)

| Component | Exists today | Project-lifecycle gap |
| --- | --- | --- |
| `IntentRequest.success_criteria`, `NormalizedIntent` | Caller-provided task-level success criteria survive normalization | No project requirements registry or requirement-to-milestone relation |
| `policies.py` `build_execution_policy` | Contextual `done_criteria`, engineering rules and risk/approval boundaries for review, coding, security and DevOps | Those are task-level advisory instructions, not evidence that a project milestone is accepted |
| `compiler.py` | Portable `Goal`, `Verification` and `Done` sections, with read-only evidence rules for review tasks | No cross-task completion state, milestone dependency graph, launch-readiness review or owner sign-off |
| `evaluation.py` and `records.py` | Deterministic regression assertions, externally reported outcomes and privacy-minimal run records | No authenticated project acceptance evidence or accepted gate transitions; a run metric is not release approval |
| B1 internal `compass.py`, `workspace.py` | Caller-supplied source-grounded project summary, conservative scope review and proposed current-phase maintenance | No verified requirement-to-milestone mapping or lifecycle progression; B1 is not publicly promoted |

**Do not duplicate** task-level DoD/policy logic as a new “governance engine”. Existing human-readable `AGENTS.md`, `STATUS.md`, `ROADMAP.md`, `PRODUCT.md` and accepted decisions, together with PR/CI/owner evidence, are the lowest-cost baseline.

## Source-grounded feasibility example — not demand validation

A separate, existing repo `milad-seify/DSS-QFZ` at **main `79e47b259e2372c9527bfce8ee8fbf7ae4e1b625`** provides a concrete multi-step *documentary* scenario:

- `docs/ROADMAP.md` and `docs/STATUS.md` say **Pre-5C IN PROGRESS**, with exit contingent on current-main integration, focused tests, exact-head full CI, independent review and an owner walkthrough.
- **Phase 5 NOT STARTED**; production hardening is gated by owner/product acceptance. Real-data activation also has independent evidence/classification/review prerequisites.
- `AGENTS.md` says a phase/subphase is done only when implementation, tests, CI, security implications, migrations and docs agree.

A safe manual review from *these pinned docs alone* must report **Pre-5C readiness unverified / awaiting evidence**, and **Phase 5 not authorized**. It must not infer actual current CI, owner acceptance or deployability from old documentation or a single green check. These are *candidate test fixtures* only; no C1 runtime run, owner walkthrough, Phase 8 session or independently verified failure was performed for this assessment.

## Smallest possible C1 candidate (only if separately authorized)

Consider a **read-only, source-grounded milestone gate review** using *explicitly caller-supplied* records, never a general project-management product. Inputs may include an approved requirement list with stable caller-provided identifiers, milestone/exit criteria, accepted decisions, external evidence references and known approvals. If IDs or acceptance evidence are absent, report `unknown`/`needs_review` rather than constructing an invented trace.

Possible review output (illustrative, **not a public schema**): milestone label, cited requirement/acceptance claims, per-gate evidence pointers, `verified` (only with externally corroborated evidence), `unverified`, `missing` or `conflicting`, remaining approvals, and `ready_for_owner_review` vs `blocked_or_unknown`. Never emit an authoritative `launch_approved` decision on the model's own judgment.

Potential narrow manual comparison: predefine a 2–3 milestone scenario with fixed gate lists and evidence snapshots, evaluate existing Prepare → Review → Copy plus manual status/roadmap reading first, then measure whether a proposed reviewer prevents a *repeated* specific error without growing burden. Avoid LLM judging LLM outcomes.

## Conditional acceptance checks, risk and stop gates

1. A missing requirement ID, unresolved source, stale revision or unavailable owner acceptance must remain **unknown**, never silently count as Passed.
2. CI success alone cannot clear owner walkthrough, security, operational rollback, real-data approval or production readiness gates.
3. A verified project gate needs explicit externally sourced evidence for the *matching criterion* and pinned revision. A source's statement that something passed is not independent verification.
4. Unmet prerequisites prevent a positive `ready_for_owner_review` recommendation; a pending owner sign-off cannot be auto-approved.
5. Read-only deterministic review must not change task success criteria, overwrite project decisions, create persistent state or grant execution permission.
6. Fresh sessions with the same pinned supplied artifacts yield the same material gate interpretation; contradictory sources remain reviewable, with provenance.
7. Existing public Python/CLI schema v1, MCP single tool, VS Code Prepare → Review → Copy, tests and supported release behavior stay intact; no new adapter, backend or UI needed.
8. Document each externally observed friction case and the sufficiency of the manual workaround before implementation.

**Promotion gate:** use [Phase 7C rules](PHASE_7C_EVIDENCE.md#promotion-rules) — reproducible correctness/safety/public-contract defect with a focused fix, or 3 distinct non-blocking real tasks, or 2 distinct blocking tasks without a reasonable workaround, or controlled quality evidence. An early reversible **non-public prototype exception** would need a new, explicit, recorded authorization; this assessment is not that authorization.

**Risk:** false readiness is more harmful than a conservative `unknown`; checklist bloat or spurious semantic traceability could increase complexity and distract from existing human ownership. Do not conflate `ready_for_owner_review` with `approved`.

## Decision / exit

**Recommendation: C1 implementation DEFERRED pending repeated evidence.** Use reviewed project documents and existing task DoD first. Keep the C1 proposal small and reversible if a later scoped decision is made. This documentation-only assessment was merged in PR #44; it did not authorize C1 runtime. D1 may receive a **separate assessment**, not automatic implementation, feature freeze, Phase 8 collection or publication.

This artifact records **analysis and candidate test criteria**, not proof of user demand, successful C1 feature execution or completed lifecycle validation.

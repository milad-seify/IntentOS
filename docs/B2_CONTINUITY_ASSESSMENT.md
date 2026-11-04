# B2 — State & Decision Continuity: Needs and Scope Assessment

**Status:** assessment only; **no implementation authorization**.  
**Date:** 2026-11-04. **Pinned baseline:** `milad-seify/IntentOS` main `07d227d5f6b4aad1e0985a5b44cb9f79b2a4f8a4`; [main CI](https://github.com/milad-seify/IntentOS/actions/runs/41798251129) 7/7 successful.  
**Prerequisite:** internal B1 pilot [PR #42](https://github.com/milad-seify/IntentOS/pull/42) merged without public promotion. Follow [finite program](POST_PHASE_7_PROGRAM.md), [capability inventory](FUTURE_CAPABILITIES.md), [Phase 7C evidence](PHASE_7C_EVIDENCE.md), and decisions D-025/D-026.

## Observed need — facts versus hypotheses

The desired behavior is continuity of **human-approved** project goals, current status, next action and decisions across fresh human/agent sessions, without trusting an AI's memory or unchecked “Done” claims.

**One verified repository-local mismatch:** after B1 PR #42 merged, `docs/STATUS.md`, `docs/ROADMAP.md`, and the program document still referred to B1 as under review. This assessment PR corrects those labels. Git evidence for the merge and CI is available, so this mismatch has a cheap manual/documentation remedy. **It is not repeated cross-user or multi-task evidence of B2 demand.** Completed Phase 7C evidence recorded no repeated friction sufficient for promotion. Do not count historical tasks or this documentation repair as new Phase 8 outcomes.

## Reuse-first technical gap assessment

| Existing component | Supports now | Does not prove or provide |
| --- | --- | --- |
| `ContextDocument` and `context.py` | Caller-supplied, authority-labeled context with bounded ranking and deduplication | Independent authority checks, document freshness, persistence |
| Internal B1 `review_project_compass` | Read-only source path/line extraction, conservative scope review, stale/unresolved labels | Approved state transitions, verified completion, applied writes, multi-session history |
| `plan_agent_workspace` in `workspace.py` | `CREATE/UPDATE/KEEP` proposals for `AGENTS.md` and `STATUS.md`; no writes; duplicate/bloat warnings | Decision-log updates; revision guard; provenance of approval; it updates only a phase line and can leave dependent historical claims stale |
| Git/PR/CI and reviewed docs | Repository commit/merge history and human-reviewed `STATUS/DECISIONS` as authoritative evidence | Automatic reconciliation; CI success alone cannot certify every product-status claim |

## Minimum B2 candidate — **conditional, not authorized**

**Prefer the existing manual, proposal-first workflow first.** If separately approved after evidence, B2 would create a **read-only change proposal**, never apply edits, based solely on caller-provided project docs, exact source revision, proposed state/decision and externally supplied evidence references. Reuse existing `ContextDocument`, `WorkspacePlan`, and the human-readable `AGENTS.md` / `docs/STATUS.md` / `docs/DECISIONS.md` conventions. Do not create a competing source of truth.

Candidate proposal content: target file/section, expected revision or blob SHA, minimal proposed diff or `KEEP`, source/evidence pointer, factual uncertainty/conflicts, reason for required human approval and rollback/recovery note. This is an illustrative checklist, **not a committed public schema**.

Conditional in-scope behavior:
- Propose a phase/status update only with sufficient accepted evidence; no invented completed tasks, authorizations, or release claims.
- Preserve accepted decisions verbatim; revisions need a recorded human-approved supersession rather than silently rewriting history.
- Reject or flag stale revisions, conflicting claims, missing evidence and unapproved changes for review; emit no-op when already current.
- Never modify user files, merge PRs, run commands or instruct external agents to bypass approval.

Explicit non-goals: DB/event store, autonomous memory, automatic repo scan/writes, cross-agent orchestration, project-management suite, new MCP/VS Code/CLI surface, telemetry, provider routing, milestone execution (C1), runtime recovery (D1), public v1 contract/schema changes, Phase 8 sessions.

## Evidence gate before any runtime development

Apply the accepted [Phase 7C promotion rules](PHASE_7C_EVIDENCE.md#promotion-rules): at least **3 distinct real tasks** with the same non-blocking state/decision continuity friction; or **2 distinct blocking tasks** with no reasonable existing workaround; or a reproduced correctness/safety/public-contract failure with focused regression justification; or measured comparative outcome evidence. A *new reversible internal prototype* before thresholds requires a separate, explicit authorization and an evidence/prototype-exception record, as with B1. **This review is not that approval.**

First collect a concise, privacy-safe observation for each distinct genuine task: project alias, pinned source SHA, expected vs observed state, evidence pointer, user impact/rework, workaround attempted, repeat key, risk and verification outcome. Assess whether keeping reviewed docs in sync already solves the problem at negligible cost.

## Candidate acceptance / exit gate (not yet executed)

1. Same pinned supplied sources produce the same proposed status/decision across fresh sessions, without hidden chat state.
2. No “Complete/Merged/Approved” without matching independent evidence; missing/conflicting facts remain `needs_review` or no-op.
3. A stale expected source revision blocks any suggested mutation; never overwrite an updated status document or a past decision.
4. Accepted decisions are preserved, supersession explicitly represented, duplicate proposals eliminated, and replay of accepted updates yields `KEEP`.
5. Proposed output is a minimal reviewable diff with provenance and a separate human approval boundary, not an execution command.
6. Existing public v1 optimize/workspace contracts, JSON schema, MCP single tool and VS Code Prepare → Review → Copy stay compatible; focused, adversarial and CI tests pass.
7. No persistent write, remote call, agent execution, automatic PR merge, data collection or Phase 8 start occurs inside IntentOS.

## Decision

**Recommendation: defer B2 implementation pending repeated evidence, continue with manual reviewed documents and existing proposal-first tooling.** This assessment and B1 status reconciliation may be merged as documentation only. No B2 prototype, public adoption, Stage C/D, feature freeze or operational Phase 8 is authorized by this document. A future separate scope decision may implement the smallest justified slice or close B2 without implementation.

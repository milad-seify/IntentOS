# Next Scope Review — Post-Phase-7 IntentOS

**Status follow-up (2026-11-04; after the original pinned assessment):** [PR #49](https://github.com/milad-seify/IntentOS/pull/49) and [PR #50](https://github.com/milad-seify/IntentOS/pull/50) are merged; main at the subsequent recorded **pre-reconciliation** pin `8f2823348d94925605ba7a5ec62c2f3eb2982404` passed [CI 41820592581](https://github.com/milad-seify/IntentOS/actions/runs/41820592581), 7/7. [PR #48](https://github.com/milad-seify/IntentOS/pull/48) has since been **closed without merge** by the maintainer's disposition; **no formal final Freeze** became effective. The original review and its older SHA below remain historical, not today's current-HEAD assertion. See [D-029](DECISIONS.md) for the updated gate. No B2/C1/D1 product feature was approved.

**Status:** documentation-only assessment and proposed next-scope gate; **no runtime implementation, Feature Freeze revision or Phase 8 execution approved by this document**.  
**Reviewed:** 2026-11-04. **Pinned GitHub `main`:** `ac2a530c1a42e9fa0e270201fb08741895d49ccb`; [main CI 41809585163](https://github.com/milad-seify/IntentOS/actions/runs/41809585163) passed 7/7.  
**Formal closeout discrepancy:** [PR #48](https://github.com/milad-seify/IntentOS/pull/48) was **still open and unmerged** on direct GitHub inspection; its [PR CI 41809944205](https://github.com/milad-seify/IntentOS/actions/runs/41809944205) passed 7/7. Do not represent D-028 as an effective final Freeze or invent its merge SHA.

## Why this review exists

The maintainer first authorized planning for Phase 8A, then stated that real first-time users and observed sessions are not currently available and requested **deferring all operational Phase 8 validation until the desired development scope is settled**. This is a change to **execution scheduling**, not a relaxation or deletion of the approved [Phase 8 protocol](PHASE_8_VALIDATION.md). **Zero observed 8A sessions** are known, and 8B/8C have not begun; do not infer success from CI, templates, smoke tests or development examples.

The maintainer's desired outcome is a practical idea-to-production workflow across AI-agent sessions with coherent approved goals, scope, checkpoints and evidence; that outcome is a **product hypothesis and long-term validation direction**, not evidence that every proposed feature must be implemented before external validation. [VISION](VISION.md), [SCOPE](SCOPE.md), [principles](PRINCIPLES.md), [finite Stage A–E program](POST_PHASE_7_PROGRAM.md) and [candidate inventory](FUTURE_CAPABILITIES.md) remain the source of truth.

## Current functionality versus candidate scope

| Area | Verified repository / acceptance status | Scope decision now |
| --- | --- | --- |
| Intent normalization, risk/policy, scoped context, routing, verification, CLI/Python, one MCP tool, VS Code Prepare → Review → Copy, Skills and privacy-minimal evaluation | Already implemented and public at Core `1.0.1` / VS Code `0.1.1` as applicable; stable v1 contract maintained | **Preserve; do not reopen** completed Phases 0–7 or redesign public surfaces |
| **B1 — Project Compass / Scope Guardian** | Internal, read-only `intentos.compass.review_project_compass` feasibility pilot merged [PR #42](https://github.com/milad-seify/IntentOS/pull/42); tests/source-grounded fixture review, no public CLI/MCP/VS Code export; not in published Core 1.0.1 | **Internal prototype only.** Neither stable promotion nor feature expansion is authorized; collect specific evidence or seek a separately approved bounded experiment |
| **B2 — State and Decision Continuity** | Requirements/needs assessed [PR #43](https://github.com/milad-seify/IntentOS/pull/43); existing `workspace.py` proposes changes without writing them, but no approved persistent cross-session state lifecycle | **DEFERRED PENDING EVIDENCE**; manual reviewed `STATUS.md`/`DECISIONS.md` remains the workaround |
| **C1 — Lifecycle, Milestones and Launch Governance** | Assessed [PR #44](https://github.com/milad-seify/IntentOS/pull/44); task-specific Done criteria exist, no independently validated project-level gate | **DEFERRED PENDING EVIDENCE**; no simulated launch authority or unverified Done claim |
| **D1 — Adaptive Delegation / Resilience** | Assessed [PR #45](https://github.com/milad-seify/IntentOS/pull/45); conservative deterministic routing and caller-supplied metrics exist; no live provider telemetry, guaranteed quota, runtime checkpoint or agent recovery | **DEFERRED PENDING EVIDENCE**; do not build an execution/orchestration platform |
| Additional UI, agent handoff automation, hosted service, provider/telemetry framework, new MCP tools | Only future hypotheses; Phase 7C did not promote any such feature | **NOT APPROVED**; no scope expansion by preference alone |

A source gap or attractive roadmap item **is not** an approved backlog item. The published Core 1.0.1 artifact does not contain internal B1, even though a wheel rebuilt from the post-release checkout still carries `1.0.1` metadata. Never republish those changed bytes with the existing version.

## Minimum decision before reopening runtime work

The existing [promotion gate](PHASE_7C_EVIDENCE.md#promotion-rules) applies unchanged: a reproducible correctness/safety/public-contract defect can justify a focused regression; otherwise **3 distinct non-blocking real tasks** showing the same friction, **2 distinct blocking tasks** without a reasonable workaround, or controlled correctness-first outcome evidence. A pre-threshold *reversible internal prototype* is only a separately authorized documented exception, not a permanent feature.

For any proposed **single** next slice, prepare a short owner-reviewed contract:

1. **Problem and outcome:** what precise task cannot be completed adequately with today's Prepare → Review → Copy + source documents?
2. **Boundary:** in/out scope and the smallest reversible behavior; especially distinguish advisory state review from automatic writes and executor runtime.
3. **Sources and evidence:** pinned code, actual recurring friction (or a named prototype exception), uncertainty and existing workarounds.
4. **Acceptance and regression:** observable positive, negative, stale/conflict and safety cases, public v1 compatibility, CI, privacy, rollback.
5. **Exit:** approve **exactly one** bounded slice, or explicitly **defer** it. No Stage B2/C1/D1 chain, new adapter or Phase 8 session automatically follows.

**Current recommendation:** there is **no evidence-backed mandatory new runtime slice** in the accepted repository. First decide **whether any particular user outcome remains unserved**; if none is independently accepted, keep the existing feature scope and plan operational Phase 8 only when observed users become available. **Do not invent work to fill the pause.**

## How to handle existing Freeze and the Phase 8 pause

- Preserve the audited Stage E code baseline as historical evidence. Resolve open [PR #48](https://github.com/milad-seify/IntentOS/pull/48) deliberately against the chosen scope path; **do not silently merge/close it or claim effective Freeze**. It is a final closeout proposal, not permission to start additional development.
- **If no further product scope is accepted:** complete the existing final-freeze gates when separately approved; operational Phase 8 remains paused until users and the approved conditions are available.
- **If a new slice is individually approved:** treat the old pin as a historical baseline, make the smallest reviewed change in a separate PR, run focused and seven-job CI, and **repeat the final Feature Freeze** on the new accepted source before validation. Do not quietly amend a frozen product.
- Operational **Phase 8A/8B/8C is DEFERRED / NOT STARTED** by the maintainer's latest scheduling choice. Its published first-use/controlled-comparison/privacy/user/project targets remain unchanged. A new explicit owner authorization is required when the real testing conditions exist.
- The complementary Idea-to-Production dogfood is also **deferred** and cannot substitute for the first-time-user, POSIX/Windows or controlled-pair targets. Code reviews, synthetic fixtures and internal capability feasibility are **not Phase 8 evidence**.

**This assessment does not release software, change runtime, close PR #48, declare an effective Freeze, start Phase 8, or approve a new feature.**

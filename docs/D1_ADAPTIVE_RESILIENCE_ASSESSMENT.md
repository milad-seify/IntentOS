# D1 — Adaptive Delegation & Resilience: Needs and Scope Assessment

**Status:** assessment merged in [PR #45](https://github.com/milad-seify/IntentOS/pull/45); implementation **deferred pending evidence**. No experiment or product promotion authorized.  
**Date:** 2026-11-04. **Pinned IntentOS baseline:** `milad-seify/IntentOS` main `371e4b8d17b64a852d85c68216c42a04550f54cc`; [main CI 41804283608](https://github.com/milad-seify/IntentOS/actions/runs/41804283608) completed successfully (seven jobs). No open PR at start.  
**Program boundary:** Stage A [PR #41](https://github.com/milad-seify/IntentOS/pull/41) accepted; B1 [PR #42](https://github.com/milad-seify/IntentOS/pull/42) merged as internal-only prototype; B2 [PR #43](https://github.com/milad-seify/IntentOS/pull/43) and C1 [PR #44](https://github.com/milad-seify/IntentOS/pull/44) assessed with runtime deferred. See [finite program](POST_PHASE_7_PROGRAM.md), [candidate inventory](FUTURE_CAPABILITIES.md), [Phase 7C evidence](PHASE_7C_EVIDENCE.md), and [v1 public contract](PUBLIC_CONTRACT.md).

## User outcome under consideration

A human should be able to delegate a task to an external agent with an **explainable, sufficient capability/effort recommendation**, reliable outcome evidence and a **reviewable handoff** if work is interrupted. Do not promise real-time model selection, guaranteed token availability, unattended completion or safe automatic retries. IntentOS stays the **vendor-neutral advisory control/trust layer**, not the agent runtime or quota monitor.

D1 concerns **at most one** narrowly authorized adaptive experiment in this finite program. Routing, token budgeting, interruption recovery and learning are *separate possible problems*, not one bundled feature.

## Observed implementation and gaps at pinned main

| Candidate sub-area | Verified existing behavior | Missing / danger of overclaim |
| --- | --- | --- |
| Capability-based routing | `router.py`: task type + risk determines FAST/BALANCED/STRONG and LOW/MEDIUM/HIGH effort. For supplied `ModelMetadata`, requires matching surface, `available=True`, sufficient capability; prioritizes `verified` metadata, then capability headroom, cost class and name. Without eligible metadata, returns a conservative target-default fallback. | `available` and `verified` are **caller assertions**, not live probes. No provider health, current price, rate-limit state, real benchmark-based capability or service integration. An unverified candidate can be selected when no verified one is available; the caller owns metadata integrity. |
| Risk/verification process | `policies.py`, `compiler.py`: risk-based approval and task-level done/verification sections; contextual review-only behavior | No runtime checkpoint, actual action permission, executor state or cross-provider orchestration; preparing a contract is not verifying execution. |
| Outcome comparison | `evaluation.py`: external `VariantRun`, `compare_paired_runs`, correctness/quality-first ranking, reviewable repeated-failure lesson proposals | These are **task-local** comparisons, not model/provider benchmark, continual online learning or a proven decision policy. Missing data stays unknown. |
| Usage / provenance | `records.py`: optional externally supplied `RunMetrics` (success, quality, input/output tokens, latency, retries) plus hashed prompt/context `RunRecord` schema 1 | No tokenizer, forward token forecast, live quota/balance, spend tracking, cross-project evidence store or automatic collection. Total tokens require both input and output counts. |
| Interruption / cross-agent handoff | CLI, MCP `prepare_task`, VS Code Prepare → Review → Copy, portable Skills and context hashes provide reviewable text and provenance | No executed action history, remote agent session transfer, idempotent replay, checkpoint/restore, duplicate-action prevention or guaranteed recovery. These remain executor-owned. |

**Source correctness note:** The router's own fallback explanation says no *verified* compatible metadata was supplied, but it returns fallback when **no eligible** model exists. This is wording to review separately if it causes demonstrable misleading user behavior; it is not sufficient evidence for a new adaptive routing framework. Do not change the frozen public v1 behavior or route semantics as part of this assessment.

## What the evidence actually says

[Phase 7C](PHASE_7C_EVIDENCE.md) completed **10 distinct historical real tasks**, with prepared favored in **3**, raw favored in **2**, and **5 inconclusive**; no repeated workflow friction met promotion thresholds and the accepted decision was **no new product feature**. Those paired results compare prompt-preparation approaches, **not** dynamic model routing or agent recovery. Their outcomes cannot prove that adaptive routing is better, that a cheaper model is sufficient, or that checkpoints improve task success. They must not be reused as new D1 or Phase 8 evidence.

No source-backed new controlled comparisons of the **same tasks with fixed model/agent conditions**, verified cost/capability availability, or reproduced interruption/recovery failures were observed in this review. Feature need remains **unproven**, not disproven.

## Smallest feasible alternative before new runtime

Continue to use the existing `recommend_route` and task-specific policies with explicitly supplied, timestamped caller metadata and its known verification limits. Prefer external agent/IDE controls to select models and run tasks. Record accepted task goal, scope, source revision, human approvals, last confirmed action, tests/evidence actually run, pending steps and blocked items **in human-reviewed project docs** when a session is interrupted; do not make unsupported state claims. Use existing `RunRecord` hashes/metrics and `compare_paired_runs` only with externally observed data; preserve the original raw arm and make missing values explicit.

Manual workflow adequacy is itself a control: if it prevents rework and is cheap, **defer D1** rather than introduce a service, provider SDK, tokenizer, state store or orchestration code.

## Conditional candidate experiment — choose at most one

**First preference, if evidence emerges:** a narrow **offline routing explanation/metadata validation** improvement that keeps the current public v1 surface compatible, does not query live providers and never allows lower correctness/capability merely to save cost. Define caller-supplied metadata source/date/verification, fixed capability and surface eligibility checks, and a deterministic explanation of why a model or fallback was recommended. Explore only a specific reproduced defect or controlled repeated routing confusion; this is not an authorization to implement.

**Alternative only if stronger interruption evidence emerges:** a **portable, read-only handoff/checkpoint *guidance* contract** from externally supplied verified progress (not auto-resume). Verify pending operations, source hashes, approval status and safe retry classifications with the external executor. Treat ambiguous irreversible actions as **do not retry automatically**. No running, pausing, quota reservation, retries or agent-state capture inside IntentOS.

**Do not combine both experiments.** Outcome/evidence improvements should first use existing external worksheets and `RunRecord`/paired-comparison primitives, not a new learning pipeline.

## Predeclared evidence / tests for a separate implementation approval

The [existing promotion gate](PHASE_7C_EVIDENCE.md#promotion-rules) applies: (1) reproducible correctness/safety/public-contract defect for a focused regression; or (2) **three distinct** non-blocking real tasks with the same friction; or (3) **two distinct** blocking tasks without a workable alternative; or (4) meaningful controlled same-task outcome gains **without correctness regression**. An early, reversible, non-public prototype would need a **separate explicit exception recorded in the decision log**. This assessment does not grant it.

For a possible routing experiment, pin task, model availability/metadata snapshot, target surface, agent version, source revision, risk, acceptance tests, scoring and environmental constraints **before** comparison. Record quality/correctness first, then only actually observed tokens, latency, retries and price; absent metrics are *unknown*, never zero. Test high-risk refusal to downgrade, stale/unknown metadata, no-model fallback, tie-breaking, incompatible/unavailable candidates, determinism and exact v1 compatibility.

For a possible handoff-guidance experiment, pin a completed/partially completed execution with external independent evidence, resume from a fresh agent with the **same approved scope**, and verify no fabricated Completed, duplicate write, irreversible retry, secret leakage or unapproved operation. A task log claiming “Done” is not completion evidence; fail safe on missing/contradictory checkpoints.

**Acceptance / exit:** bounded problem proven, just one separately approved experiment, conservative fallback and human review, no new runtime infrastructure or provider dependency, focused/negative regression suite, full CI and a recorded stop/deferral decision. A failed/ambiguous experiment is **deferred**, not expanded.

## Program decision and next gate

**Recommendation:** mark D1 **DEFERRED PENDING EVIDENCE**, and complete the documentation-only assessment. Preserve existing routing and evaluator contracts. A separate owner decision may either (a) collect narrowly scoped real-use D1 evidence with the existing tooling, or (b) conduct the separately authorized [Stage E source-freeze readiness review](STAGE_E_FREEZE_READINESS.md) after accepted deferrals, with no feature work; freeze is not automatically declared. Do not treat this assessment as automatically approving D1 implementation, Stage E/feature freeze, Phase 8 8A/8B/8C, Idea-to-Production dogfooding or a product release.

This document is **planning/evidence discipline**, not a claim of completed adaptive experimentation, live model benchmarking or successful runtime recovery.

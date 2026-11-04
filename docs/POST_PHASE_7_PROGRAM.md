# Post-Phase-7 Capability Evolution Program

**Status:** Stage A accepted ([PR #41](https://github.com/milad-seify/IntentOS/pull/41)); B1 read-only internal prototype merged in [PR #42](https://github.com/milad-seify/IntentOS/pull/42); [B2 needs assessment](B2_CONTINUITY_ASSESSMENT.md) merged in PR #43 with B2 deferred pending evidence; [C1 lifecycle assessment](C1_LIFECYCLE_ASSESSMENT.md) merged in PR #44 with implementation deferred; [D1 adaptive/resilience assessment](D1_ADAPTIVE_RESILIENCE_ASSESSMENT.md) only. **Public/stable implementation authorization:** none.  
**Planning baseline date:** 2026-11-03. **Main commit:** `ac75ef714d524076ec7ee755f1ecc1eab9d7105a`.

## Purpose and boundaries

Preserve the accepted [Reliable AI Delegation vision](VISION.md) while exploring the smallest needed improvements for project-level continuity, scope and decisions across AI-agent sessions. Desired test: an actual application can progress from idea through launch without losing explicit goals, approved scope, verification evidence, human control or recoverable handoff. This is a **validation direction**, not a claim that IntentOS executes or deploys the application itself.

The program is **finite**: a review-only Stage A, at most four separately approved development slices across B–D (B1, conditional B2/C1/D1), then Stage E freeze and the existing Phase 8 validation. Work may stop sooner when evidence fails a promotion gate. No candidate or stage starts automatically. Proposal priorities do not override the Phase 7C finding that no repeated friction justified an immediate new feature.

Source of truth: verified repository + accepted decisions + observed evidence. New observations are hypotheses until independently reproduced or controlled; do not promote agent assertions into completion evidence. Keep existing v1 public APIs, CLI, MCP single-tool boundary, machine schema v1, VS Code Prepare → Review → Copy and versioned run records intact until a separately authorized compatible change.

## Reproducible lightweight baseline (not Phase 8 evidence)

| Aspect | Verified baseline / boundary |
| --- | --- |
| Repository | `milad-seify/IntentOS`, main `ac75ef714d524076ec7ee755f1ecc1eab9d7105a` |
| Releases | `intentos-engineering==1.0.1` published, tag `v1.0.1`; VS Code extension `milad-seyfi.intentos-vscode@0.1.1` published |
| Contract | Frozen [public v1](PUBLIC_CONTRACT.md), optimize/skill/workspace CLI, Python API; JSON preparation schema 1 and run-record schema 1 |
| Existing CI | [Main run 41689868111](https://github.com/milad-seify/IntentOS/actions/runs/41689868111): **7/7 success**, Python 3.11/3.12/3.13, Windows regression, MCP smoke/parity, VS Code smoke and distribution-artifact gate |
| Existing tests | Documented baseline **120 Python tests** plus CLI/integration/distribution checks; no new local test execution is claimed by this planning document |
| Existing public smoke | Maintainer's clean external Windows/Python 3.13 install of `1.0.1` succeeded; `intentos --help` and `optimize "Review the architecture without changing files" --target codex --json` returned `ready/general/low` with read-only review guidance |
| Surfaces | CLI, Python API, optional local MCP stdio `prepare_task`, VS Code 0.1.1 and portable Agent Skills; no autonomous agent execution |
| Context | `optimize_project_prompt` selects ranked/deduplicated **explicitly supplied** documents with 6000-char default budget; MCP limits 32 documents/6000 chars; no automatic project-indexing or cross-session history |
| Workspace | `plan_agent_workspace` proposes create/update/keep actions for agent guidance and current-phase status and warns on duplicate/bloated context; does not apply writes |
| Routing | Deterministic task/risk → capability/effort; optional caller-supplied metadata for compatible available models; conservative fallback, not live provider discovery |
| Evaluation | `RunMetrics`, hashed `RunRecord` schema 1, evaluation assertions, task-local `compare_paired_runs`, and reviewable lesson proposals; external correctness/metrics supplied by executor |
| Known gaps | No structured project compass/scope-drift review, persistent decision/milestone provenance, safe runtime checkpoint/resume, live availability/cost telemetry, automatic agent handoff, or project-wide outcome learning |

### Repeatable checks and honest measurement

These are **reference commands/checks**, not claims that they were newly executed for Stage A:

1. Pin `main` to the commit above and inspect `AGENTS.md`, `docs/STATUS.md`, `docs/DECISIONS.md` and the named source files.
2. Use the existing CI run as a verified seven-job regression/distribution baseline; for later candidates, run the relevant `python -m unittest discover -s tests`, integration smoke and main CI gates against an exact new commit.
3. In a clean environment outside checkout, install `intentos-engineering==1.0.1`; record OS/Python/version/source and invoke `intentos --help` and `intentos optimize "Review the architecture without changing files" --target codex --json`. Require `ready`, `general/low`, read-only instructions, and a human approval boundary before modifications.
4. For candidate coding, DevOps, architectural review and high-risk tasks, fix task wording, target/model, source revision, supplied context, scoring rubric, acceptance checks, environment and cost/time measurement boundaries **before** any future comparison; missing metrics remain unknown.
5. Preserve exact baseline revision and provenance; no raw/prompts or secrets are stored in this program. Previous Phase 7C tasks are historical and must never count as new Phase 8 evidence.

No new task-pair experiment or first-time-user session was performed in Stage A. Differences between later models, access or conditions must be disclosed instead of being attributed to IntentOS preparation.

## Bounded development plan

| Stage | Status | Candidate scope (not blanket authorization) | Exit / stop rule |
| --- | --- | --- | --- |
| A — Plan, Baseline & Governance | **Complete (PR #41)** | Verify source, document gaps and Phase 8 sequence, propose scoped first slice | Planning PR accepted with evidence, decision log, risks, bounded first slice and clear stop point |
| B — Project Continuity Foundation | **B1 internal pilot merged; B2 assessment only** | B1 read-only Project Compass/scope review; B2 proposal-first state/decision continuity only if justified | Fresh-session, conflicting-source and drift scenarios pass without fabricated state or writes; otherwise defer |
| C — Project Lifecycle Governance | **C1 assessment merged; implementation deferred** | C1 requirements/milestone and contextual completion/launch-gate **review** | A bounded multi-step scenario with fixed requirements and verification checks passes, or C1 is deferred |
| D — Adaptive Delegation & Resilience | **D1 assessment only; implementation unapproved** | At most one of routing/budget/resume/evidence refinement, only with sound outcome/feasibility evidence | Correctness-first comparable results or documented deferral; no false token reserve or autonomous runtime |
| E — Stabilization & Feature Freeze | Required closeout | Regression, security/privacy, compatibility, release/doc consistency, known limitations | Named commit/build pinned, all accepted slices complete or deferred; freeze recorded before Phase 8 |

**Bounded non-goals:** no hosted services, DB, queues, telemetry backend, vector database, new MCP tools, model hosting, provider SDK, agent-specific execution wiring, auto repository crawling, autonomous orchestration, global learning mutations, direct filesystem writes, new permanent sidebar, or redesign of stable v1. New runtime abstractions/dependencies require concrete proof of necessity and separate explicit approval.

**Decision/promotion discipline:** a reproducible correctness/safety/public-contract defect warrants a focused regression; non-blocking friction ordinarily requires 3 distinct tasks; blocking friction without a reasonable workaround requires 2 distinct tasks; controlled outcome evidence may justify a narrowly scoped improvement. A speculative pre-gate prototype requires separate, explicit reversible-prototype authorization recorded in the decision log and must not enter the stable release by default. If evidence is insufficient, mark **deferred** and proceed to stabilization rather than expanding the work indefinitely.

## First separately approvable slice — B1: Read-only Project Compass

**Problem:** a user and a fresh agent session cannot reliably answer where a project stands, what is approved and whether a proposed task drifts from scope based solely on a chat. Current selected-context and workspace-proposal mechanisms do not create an authoritative project-level summary or align a task to approved milestones.

**Proposed bounded outcome:** from **caller-provided, human-readable** project goal/scope/status/decision records, provide a small **read-only, source-grounded** Project Compass review or a portable handoff contract: goal, current phase, completed/in-progress/blocked/deferred, next meaningful action, relevant decisions, requested task's scope fit, and material uncertainties. Reuse existing core context selection, project API and evaluation patterns. The exact delivery through current CLI/API vs a compatible additive interface remains an architecture decision in B1, not an assumption in Stage A.

**Feasibility/evidence gate before implementation:** collect a bounded record of actual continuity/scope friction from separate tasks or seek explicit approval for a reversible non-public prototype; compare the existing Prepare → Review → Copy path on fixed sanitized project documents first. Do not infer promotion from the author's preference alone.

**Candidate acceptance criteria (subject to separate approval):**

1. Fixed, supplied context includes a stable goal, explicit in/out scope, status, next action, decisions and source labels; output connects each asserted fact to a specific supplied source.
2. A task aligned to the approved scope is not falsely rejected; an explicit out-of-scope request is flagged with a reviewable reason/approval-needed guidance.
3. Contradictory, outdated or missing status is marked **uncertain**; no claim of completion, authoritative revision, or missing milestone is invented.
4. Two independent fresh invocations with the same pinned sources preserve the same material scope/status interpretation; no hidden chat memory or auto filesystem discovery is required.
5. No persistent repository write, external agent execution or permission enforcement occurs; decisions remain with the human.
6. Existing ordinary optimize, MCP single-tool, VS Code Prepare → Review → Copy and machine/public v1 compatibility regressions remain green.
7. Small deterministic fixtures cover in-scope, drift, stale/contradictory evidence, unknown next step, and cross-session parity; use predeclared criteria rather than an LLM judge.
8. Document minimal operational instructions, known limits, changed files, checks and an explicit B1 exit/deferral decision.

**Relative effort/complexity:** B1 **medium**, primarily deterministic provenance and conflicting-state interpretation; no infrastructure. B2 **medium**, mainly safe proposal boundaries. C1 **medium–high** depending on project schema, conditional. D1 **uncertain/high** if external provider/runtime information is unavailable; normally defer.

**Exit/approval:** Stage A did **not** implement B1. After PR #41 was merged, B1 received a separate go-ahead for a small, reversible **non-public pilot** despite the absence of repeated promotion evidence. Its exact scope, fixtures, risks and stop gate are in [B1_PROJECT_COMPASS_PILOT.md](B1_PROJECT_COMPASS_PILOT.md). CI success alone does not promote it to a stable capability. Do not automatically start B2, C1, D1 or Phase 8.

## Final validation (only after feature freeze)

Keep [Phase 8 8A/8B/8C](PHASE_8_VALIDATION.md) unchanged: 3 observed first-use sessions / at least 2 first-time users / Windows and POSIX / at least 2 independent completions; 20 new distinct tasks from at least 2 users (including a non-maintainer) across at least 3 projects; target at least 12 eligible controlled raw-versus-prepared pairs. Eligibility, correctness-first rules, missing-data treatment and privacy stay authoritative in the protocol.

**Complementary dogfood:** separately approve a genuine new Idea-to-Production app with its goal, MVP scope, budget, constraints, milestones, DoD, launch and operations gates fixed beforehand. Examine scope drift, agent/model recommendation, continuity across sessions, interrupted task handoffs, evidence-backed completion and launch checks. A single project neither proves product-wide benefit nor automatically satisfies Phase 8 user/project coverage.

**Phase 8 decisions** may be release/adoption ready, ready with documented limits, focused fixes required or insufficient evidence. Do not lower targets or infer statistical/product-wide superiority. Preserve human approval for production operations.

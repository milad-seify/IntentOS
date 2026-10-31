# Phase 8 — Adoption & Outcome Validation

**Status: IN PROGRESS — validation protocol.** This first slice defines the protocol only; first-use sessions and downstream task runs have not begun. No new runtime capability is approved.

Phase 8 asks:

1. Can a first-time user adopt IntentOS and hand off a prepared task without maintainer help?
2. Under which real task conditions does IntentOS preparation materially improve downstream AI outcomes?

Phase 5 already supplies evaluation mechanics. Phase 8 operationalizes its `VariantRun`, `EvaluationOutcome`, `RunMetrics`, paired comparison, privacy-minimal run records, and reviewable learning proposals. It does not replace their algorithms. See [EVALUATION.md](EVALUATION.md) and the completed [Phase 7C evidence gate](PHASE_7C_EVIDENCE.md).

## 8A — First-use validation

Collection targets:

- 3 observed sessions involving at least 2 first-time users, identified by aliases.
- Windows and at least one POSIX environment represented.
- At least 2 users complete install → preparation → handoff without maintainer intervention.

Use public installations in a working directory outside the IntentOS checkout. Install the published `intentos-engineering` package and Marketplace extension `milad-seyfi.intentos-vscode`; record actual versions and sources. Use a separate VS Code profile if needed to avoid changing the participant's normal setup. Do not install an editable checkout or let the repository `.venv` fallback hide executable-discovery problems.

The observer records what happens without coaching. Published help is allowed. Independent completion means completing installation, preparation, and handoff without maintainer intervention. If help is needed, record the intervention and recovery; the session remains useful evidence but cannot count as independent completion. An unattempted step is unknown, not successful. Do not manufacture numerical scores for subjective UX.

Observe the whole journey:

1. Discover IntentOS; record the discovery source and user's expectation.
2. Install the public CLI with `python -m pip install intentos-engineering` using the environment's Python command.
3. Run `intentos --help` and a first CLI preparation request. Record whether the executable resolves (`Get-Command intentos` on PowerShell or `command -v intentos` on POSIX can diagnose it). A working `python -m intentos` fallback does not prove bare-command discovery works.
4. Install the extension from Marketplace.
5. Launch through the visible IntentOS status-bar item or existing Command Palette command; record which path the user finds.
6. Observe a missing-target clarification and whether the user understands how to supply the missing information and retry.
7. Reach Ready with a target specified or detected.
8. Ask the user to explain risk, approval boundaries, and verification in their own words. Ask what they think IntentOS does and what value, if any, the review adds to their existing AI workflow. Record answers and confusion in notes without coaching toward the desired positioning or inventing UX scores.
9. Copy Prepared Task and confirm the clipboard contains the intended prepared task.
10. Hand it to an external AI tool. Confirm the user understands that IntentOS prepares the task and that execution happens in that tool. Successful handoff does not establish downstream correctness.

Prefer a genuine first request. A scripted smoke example can exercise clarification/Ready but does not count as a real-task outcome observation for 8C. Record blockers and recovery even when the session later succeeds. Record time only when reliably observed, with its measurement boundary.

### First-use evidence template

This is a manual worksheet, not an import format or runtime schema. Use `true`/`false` only for observed results; unknown/unattempted values remain `null`. Environment should identify OS, shell, Python, VS Code, and installed IntentOS versions. `first_request` is a task category or an existing fingerprint, not the raw prompt. Explain any review misunderstanding or intervention in notes.

```yaml
session_id: null
date: null
user_alias: null
user_type: null                 # first-time maintainer/non-maintainer
environment: null
install_source: null            # CLI and extension sources/versions
discovery_source: null
cli_install_success: null
vscode_install_success: null
cli_discovery_success: null
cli_preparation_success: null
first_request: null
clarification_required: null
ready_reached: null
review_understood: null          # risk, approval boundaries, verification
copy_success: null
handoff_success: null
maintainer_intervention: null
completed_independently: null
elapsed_ms: null                 # only if measured; define start/end in notes
blockers: null
user_confusion: null
recovery: null
notes: null
```

## 8B — Outcome evidence workflow

Start with one bounded manual worksheet per genuine task. Reuse the existing public preparation workflow for the prepared arm. Existing Python evaluation APIs remain available; when recording a computed verdict, call `compare_paired_runs()` rather than implementing another ranking rule. A computed result is optional at the worksheet stage and must remain unknown until obtained.

No comparison CLI is implemented or approved here. A command such as `intentos compare` remains conditional on pilot evidence that users need it. Record any transcription or evidence-entry friction before proposing tooling. `RunRecord` remains separate preparation provenance: it hashes prompts/context, does not establish downstream correctness, and must not be fabricated for the raw arm by re-preparing it. Learning proposals remain reviewable proposals, not automatic policy changes.

### Paired task evidence template

Use project/user aliases and sanitized verification references. Shared conditions describe the actual setup of both arms; record any deviation under limitations. Correctness is `pass`, `fail`, or `null` (unknown). Check scores need a declared deterministic rubric; quality scores require an explicit measurement method. Do not substitute prompt length, generated guidance, or agent claims for acceptance evidence. Missing metrics remain `null`, including zero retries unless zero is known.

```yaml
shared:
  task_id: null
  project: null
  user_alias: null
  user_type: null                # maintainer/non-maintainer
  task_type: null
  risk: null
  base_revision: null
  downstream_agent_tool: null
  model: null
  effort_reasoning: null
  environment: null
  permissions: null
  supplied_context: null         # explicit labels/fingerprints, not contents
  execution_order: null          # raw-first/prepared-first
  acceptance_checks: null        # fixed before either arm
  score_rubric: null
raw:
  correctness: null
  evaluation_check_score: null
  quality_score: null
  retries: null
  input_tokens: null
  output_tokens: null
  latency_ms: null
  verification_evidence: null
  failure_or_incomplete_reason: null
prepared:
  correctness: null
  evaluation_check_score: null
  quality_score: null
  retries: null
  input_tokens: null
  output_tokens: null
  latency_ms: null
  verification_evidence: null
  failure_or_incomplete_reason: null
  clarification_occurred: null
  manually_edited: null
  preparation_overhead_ms: null
comparison:
  eligible: null
  limitations: null              # deviations, rework, measurement boundaries
  verdict: null                  # raw/prepared/inconclusive once evaluated
  reason: null
  measured_deltas: null
```

### Comparison controls

- Define the acceptance checks and any score rubric before either execution. Prefer tests, builds, lint/type checks, or explicit deterministic acceptance checks over LLM-as-judge.
- Hold downstream agent/tool, exact model, effort, base commit, environment, permissions, and supplied project context constant. Record any condition that cannot be verified.
- Use isolated worktrees/clones or equivalent environments from the same base. Never run the prepared arm on top of raw-arm changes; keep outputs and verification independent.
- Counterbalance execution order where practical and record the order. Supply the same project context to both arms; preparation is the intended variable.
- Keep the raw request raw and generate the prepared arm through IntentOS. Record clarification and manual prompt edits as friction/rework. If clarification changes task meaning without a common acceptance basis, or manual edits introduce another variable, retain the observation as confounded.
- Establish correctness before interpreting efficiency. A failing arm cannot win because it used fewer tokens. Unknown correctness is not a pass. Record a failed execution with its checks; do not discard it to improve outcome counts.
- Confounded or incomplete pairs remain recorded with eligibility false and an inconclusive verdict; they cannot support a winner claim or count toward eligible controlled pairs. For eligible pairs, map the existing comparator's absent winner to inconclusive and retain its reason. Missing comparable metrics remain unavailable; never estimate tokens, cost, or latency.

An eligible controlled pair has verified shared conditions, independent executions from the same base, and an observed correctness outcome for each arm using the same predeclared checks. A failing arm with observed verification is valid evidence; failure alone does not make a pair incomplete.

Use the same measurement boundaries for both arms. Record preparation/clarification overhead separately when measured; do not compare a downstream-only duration in one arm with an end-to-end duration in the other.

## Privacy and evidence handling

Neither worksheet requires raw prompts, source code, secrets, or conversation history. Prefer categories, aliases, or existing fingerprints; review free-text notes, file labels, and evidence links for sensitive content before sharing. Fingerprints do not guarantee anonymity. Keep evidence local or in a location deliberately chosen by the participant; this protocol adds no automatic storage or upload. No telemetry infrastructure is needed.

## 8C — External evidence gate

Collection targets:

- 20 new distinct real-task observations.
- At least 2 users, including at least one non-maintainer, across at least 3 projects.
- Target at least 12 eligible controlled pairs, spanning multiple task types and risk levels (at least 2 of each).

Phase 7C tasks remain historical evidence and must not be counted again. A Phase 8 pilot task may count if it follows this protocol. Repeated runs of the same task are not new distinct tasks; a first-use session alone is not a paired outcome. Failed tasks remain observations; incomplete/confounded pairs are reported separately from eligible comparisons.

At review, report achieved targets, raw/prepared/inconclusive counts, exclusions and their reasons, missing metrics, repeated friction, and evidence limitations. These collection targets do not establish statistical significance or product-wide superiority. If evidence cannot be collected reliably, record insufficient coverage and the limitation; do not manufacture work or lower the gate silently.

## Promotion and closeout

Preserve the [Phase 7C promotion rules](PHASE_7C_EVIDENCE.md#promotion-rules):

- A reproducible correctness, safety, or public-contract defect can justify a focused regression fix.
- The same non-blocking workflow friction needs at least 3 distinct real tasks; a blocker needs at least 2 distinct tasks with no reasonable existing workaround. Record which users experienced it; repetition across users strengthens the evidence.
- Measured outcome evidence may justify a specific improvement opportunity consistent with product boundaries.

A single preference or complaint does not become a global rule. A task-local winner does not prove product-wide superiority, and a learning-proposal helper's configurable threshold does not replace these promotion rules. Each implementation requires separate scope review.

Valid outcomes are a focused improvement, heuristic correction, unchanged product, a demonstrated new access need, or insufficient evidence. Phase 8 does not require a feature to be successful.

This protocol authorizes no agent execution, Send-to-Agent, automatic repository crawling, additional IDE/provider adapter or MCP tool, large sidebar, standalone UI, provider SDK/credentials, telemetry backend, hosted database, model hosting, vector database, plugin framework, or orchestration framework. Public runtime contracts and schemas remain unchanged. User sessions and Phase 8B implementation require a subsequent task; do not begin them automatically after this protocol PR.

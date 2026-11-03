# B1 — Read-only Project Compass Pilot

**Status:** scoped, evidence-gated internal pilot; **not** a published feature or new v1 public surface. Authorized for focused experimentation after Stage A; broader stable-product promotion is **not** authorized. [Program](POST_PHASE_7_PROGRAM.md) and [candidate inventory](FUTURE_CAPABILITIES.md) remain authoritative.

## Why this pilot

Phase 7C did **not** establish repeated product-wide demand for an additional capability. Project-level scope/state continuity is a concrete hypothesis from the post-Phase-7 planning directive, not a completed evidence gate. This limited implementation explores feasibility and deterministic failure behavior, without claiming improved outcomes.

Existing `ContextDocument` supplies read-only content and path labels. Existing context ranking and proposal-first workspace maintenance are left unchanged. The experimental `intentos.compass.review_project_compass` is **not exported** from `intentos.__all__` and adds no CLI/MCP/VS Code entry point or JSON schema.

## Exact pilot input contract

- Supply up to **32 documents**, **36000 input characters total** (internal pilot only; MCP remains 6000), explicit content and path labels. No filesystem discovery, network access, state storage, LLM, agent execution or writes.
- Only explicitly supported Markdown H2/H3 headings are recognized (a numeric prefix such as `1. Mission` is accepted): `Project goal`, `North Star`, `Product intent`, `Mission`, `Purpose`; `Current phase`; `Completed` or `Completed milestones`; `In Progress`, `Blocked`, `Deferred`; `Next`, `Next action`, `Next meaningful action`; `Decisions`, `Important decisions`, `Durable boundaries still in force`; `In Scope`, `Out of Scope`, `V1 outcomes` and `V1 non-goals`.
- Optional document-local `## Evidence freshness\nstale` (or `outdated`) explicitly flags that document's facts as stale. **No freshness is inferred** from timestamps or text.
- Every extracted fact retains its **input path and source line**. Single-value fields use the **first paragraph**, not all later progress bullets. Scope headings interpret only bullet items, ignoring narrative introductions. Singleton fields `goal`, `current_phase`, and `next_action` are `missing` if absent, `unresolved` when supplied statements differ (not necessarily a proven contradiction), and `stale` when any source is explicitly stale. No priority override silently resolves contradictions.
- List fields are evidence only, not proof of completion. They preserve the source's claims; no CI or deployment verification is performed.
- Proposed task scope is `in_scope` or `out_of_scope` only for an **exact normalized match** against an explicit scope item. If both match, it is `conflicting`; ambiguous, unmatched or stale matches are `unknown`. Any result other than `in_scope` requires human review. This does **not** grant permissions, and even in-scope tasks still need ordinary risk/approval controls.
- Limitations are deliberate: free-form semantic scope equivalence (e.g. `Add Redis cache` does not automatically match `Redis/Celery/Kafka`), implicit stale detection, goal inference from arbitrary text, automatic status update, project-wide history and cross-agent execution are **not** implemented.

## Manual call (development checkout)

```python
from intentos import ContextDocument
from intentos.compass import review_project_compass

sources = (
    ContextDocument("PLAN.md", "## Project goal\nBuild an app\n\n## In Scope\n- Review the API\n"),
    ContextDocument("STATUS.md", "## Current phase\nMVP\n\n## Next action\nReview the API\n"),
)
review = review_project_compass(sources, proposed_task="Review the API")
print(review.field("goal").value)
print(review.task_scope.status, review.task_scope.explanation)
print(review.field("current_phase").evidence[0].path)
```

## Predeclared verification and exit gate

`python -m unittest discover -s tests` and the existing matrix CI must pass. Dedicated fixtures cover grounded state and path/line provenance, explicit in/out scope, uncertain unmatched task, unresolved phase descriptions / conflicting scope, stale source, missing next action, deterministic fresh invocation, and input bounds. No changed public import/CLI/MCP/JSON contract is allowed.

This **pilot can close as technical feasibility only**. Stable promotion requires a separate, explicit decision backed by genuine repeated project-continuity friction or controlled evidence, plus a user-facing access/API compatibility review. If demand does not clear that gate, the module stays non-public or is reverted; do not add B2/C1/D1 automatically.

## Evidence and open risks

- Verified before pilot: published Core 1.0.1, CI seven green jobs at post-Stage-A baseline, existing `context.py` and `workspace.py` behavior, Phase 7C no new-feature promotion.
- Newly claimed evidence: only focused code/test checks from this PR once CI reports them; **no new user observations, paired outcomes or Phase 8 sessions**.
- Residual risk: narrow heading conventions mean arbitrary human-readable project notes may produce `missing` or `unknown`; exact scope matching favors false-negative uncertainty over unsupported certainty. Document assertions can still be false or outdated without explicit labels, and this reviewer cannot independently certify them.

## Source-backed feasibility check (2026-11-03)

Two existing repositories were inspected at pinned commits: IntentOS `7ea5f78c5a817d53aeefe307c738d27feb7ed234` and DSS-QFZ `79e47b259e2372c9527bfce8ee8fbf7ae4e1b625`. The representative full-document sets were 32,428 and 18,436 characters respectively, exceeding the initial pilot limit of 6000. Both now fit within the **separate internal 36000-character input cap** without changing the v1 MCP limit of 6000.

Their status, goal and scope headings were partly incompatible with the initial narrow parser. The focused heading aliases and first-paragraph rule address demonstrable format mismatches, without pretending to infer semantic scope or independently verify project completion. A task not exactly present in explicit scope items remains `unknown` and needs human review; this deliberately does not certify that an `unknown` task is safe. Use real project documents only with an exact pinned revision and record known staleness; document contents are claims, not checked project facts.

The existing deterministic synthetic checks remain, with representative DSS-QFZ source excerpts added as a regression fixture. This is **technical feasibility evidence only**, not an eligible Phase 8 outcome observation. The pilot remains draft/unmerged until independent review and explicit promotion/deferral decision.

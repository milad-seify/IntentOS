# Phase 7C evidence gathering

Phase 7C begins with evidence gathering, not feature implementation.

The goal is to learn from repeated real use before choosing whether the next useful product change is a simple UI, an editor improvement, a stronger verification contract, another handoff path, or no new feature at all.

## What to record

For each meaningful real use, capture only the information needed to explain the outcome:

| Field | What to record |
| --- | --- |
| Task | Short description of the real user goal |
| Surface | CLI, VS Code, MCP, Python API, or Agent Skill |
| Target | Intended agent/tool when relevant |
| Task/risk | IntentOS task type and risk result |
| Outcome | Whether the prepared task was useful and the downstream work succeeded |
| Friction | The concrete step that was confusing, repetitive, missing, or unnecessary |
| Rework | Clarification, prompt editing, retries, or manual workaround required |
| Context gap | Whether missing or excessive context materially affected the result |
| Verification | Whether the requested checks were sufficient and actually useful |
| Optional measures | Tokens, cost, elapsed time, or code-size/test evidence only when already available without adding telemetry infrastructure |
| Candidate improvement | Smallest change that could remove the observed friction |
| Repeat key | A short label used to recognize the same problem in later tasks |

Do not collect data merely because it is measurable. Prefer evidence that changes a product decision.

## Promotion rules

A new capability should not enter the product because another project has it or because it sounds useful.

Promote an observation into implementation only when one of these is true:

- a correctness, safety, or public-contract failure is reproduced and deserves an immediate regression fix;
- the same UX/workflow friction appears in at least three distinct real tasks;
- a blocking workflow problem appears in at least two distinct tasks and has no reasonable existing workaround;
- a measurable comparison shows a proposed change materially improves outcomes without violating the current product boundaries.

One isolated preference is not enough to justify a new surface, dependency, service, orchestration layer, or settings framework.

## Current hypotheses

These are questions to test, not requirements:

1. Is `Copy Prepared Task` sufficient in real work, or does repeated handoff friction justify a Send-to-Agent path?
2. Does caller-supplied/manual project context become a repeated bottleneck, or is automatic context discovery unnecessary?
3. Does the current Review Panel expose enough information by default without becoming noisy?
4. Do non-expert workflows actually require a separate simple UI, and if so what is the smallest useful surface?
5. Do higher-risk tasks repeatedly need stronger or independent verification guidance beyond the current verification contract?
6. Does IntentOS measurably reduce rework, unnecessary scope, retries, cost, time, or code while preserving correctness?

## Initial evidence target

Collect at least 10 distinct real tasks before choosing a new product slice, unless a material correctness/safety defect justifies an earlier regression fix.

The set should include more than one task type and more than one risk level. It is not a benchmark requirement; it is a minimum product-learning sample so one unusual task does not drive the roadmap.

## External signals reviewed

### Ponytail

Ponytail reinforces two ideas already present in IntentOS: choose the smallest sufficient implementation and verify the result. The useful new signal is its paired benchmark discipline: compare the same agent with and without the guidance, repeat runs, and measure outcomes such as code size, tokens, cost, time, correctness, and test behavior.

IntentOS should not copy Ponytail's status band, board, or agent-specific hooks without evidence. The candidate worth testing later is a small paired evaluation corpus: raw request versus IntentOS-prepared request, using the same target agent and task.

Source: https://github.com/DietrichGebert/ponytail

### Autoprompt Skill

Autoprompt uses different execution depths (`direct`, `light`, `roadmap`) and separates implementation from independent checking. This is relevant because IntentOS already treats risk as a reason to change process depth and already produces verification expectations.

Do not copy Autoprompt's autonomous multi-agent runtime, concurrency controls, provider orchestration, sandboxes, or installation machinery. Instead, record whether real IntentOS tasks repeatedly expose a need for stronger process-depth guidance or independent verification.

Source: https://github.com/Spielewoy/autoprompt-skill

### gpt-engineer

The original gpt-engineer repository is archived, but two ideas remain useful: configurable prompt/preprompt experimentation and a benchmark interface for comparing agent behavior on repeatable tasks.

IntentOS already has profiles, policies, Skills, and evaluation records, so it does not need gpt-engineer's execution architecture. The useful candidate is the same as the Ponytail signal: a small reproducible evaluation set that compares unprepared and IntentOS-prepared requests using outcome evidence rather than subjective prompt quality.

Source: https://github.com/AntonOsika/gpt-engineer

## What is explicitly not starting now

Evidence gathering does not authorize:

- Send-to-Agent or agent execution wiring
- automatic filesystem/context discovery
- a permanent VS Code sidebar
- a standalone desktop/web UI
- telemetry infrastructure or a hosted analytics backend
- autonomous multi-agent execution or independent checker agents
- a benchmark framework dependency
- additional MCP tools
- provider orchestration, concurrency controls, or sandboxes

If repeated evidence supports one of these, define the smallest separate phase with its own exit criteria.

## Decision gate

After the initial evidence target, review the log and choose exactly one of:

- implement one narrowly supported product change;
- run a focused paired evaluation because outcome quality is still uncertain;
- continue gathering evidence because the signal is weak;
- make no product change because the existing workflow is sufficient.

The absence of a justified new feature is a valid Phase 7C result.

If real-task outcomes leave the preparation hypothesis uncertain, `intentos.evaluation.compare_paired_runs()` can preserve a task-local raw/prepared comparison using externally collected `VariantRun` outcomes and metrics. It does not execute an agent, store request text, aggregate across tasks, or turn one result into a product rule. Synthetic contract tests validate comparison behavior only; they do not count toward the 10 distinct real tasks above.

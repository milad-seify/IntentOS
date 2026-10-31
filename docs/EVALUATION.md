# Evaluation and Learning

IntentOS treats prompt quality as an engineering artifact that can regress and should be measured.

## Signals

Quality and operational efficiency are intentionally separate:

- assertions and score measure whether a prompt/result contract is correct
- token count measures usage when supplied by an executor
- latency measures execution time when supplied by an executor
- retries measure how many extra attempts were required

The core does not embed a tokenizer or provider telemetry client. Integrations supply runtime metrics.

## Regression cases

An evaluation case can assert:

- required or forbidden prompt text
- expected task classification
- expected risk level
- expected capability route
- maximum prompt size

`run_regression()` produces per-case outcomes plus aggregate pass/fail counts and mean score.

## Variant ranking

`rank_variants()` orders candidates by:

1. successful execution + passed assertions
2. higher evaluation score
3. fewer retries
4. fewer tokens when known
5. lower latency when known

Quality is never traded away merely to save tokens.

## Paired runs

`compare_paired_runs()` compares two externally executed `VariantRun` values for one task ID: the raw request arm and the IntentOS-prepared arm. Callers must hold the downstream agent and task conditions constant; this helper does not execute either arm or enforce a runner. The result keeps both runs independently inspectable and reports prepared-minus-raw deltas for retries, input/output/total tokens, latency, and quality when both values exist. Missing values remain `null`/unavailable; total tokens are unavailable unless both input and output counts are present. Optional code-line counts can be supplied by the caller as descriptive evidence.

The comparison calls a task-local winner only when correctness is established and one arm is clearly better: a passing arm beats a failing arm; evaluation/check score and then reported quality precede efficiency; efficiency decides only when all comparable efficiency measures point the same way. Mixed or missing evidence produces no winner. This result is not a learned product rule, and synthetic contract tests do not count toward the real-task evidence target.

Paired results contain outcomes and metrics, not request text. Existing `RunRecord` values continue to hash prepared prompts and context rather than storing their raw contents.

## Real-task outcome validation

Phase 5 supplies these evaluation mechanics; Phase 8 applies them to externally executed real-task workflows through the [validation protocol](PHASE_8_VALIDATION.md). `evaluate_result()` checks the generated preparation contract, not downstream engineering correctness. Downstream outcomes require independent acceptance evidence; real-task observations and synthetic regression fixtures are separate evidence categories.

Preserve the raw arm as the original request. Do not re-prepare it to manufacture a `PromptResult` or matching `RunRecord`: that would change the comparison variable. Existing paired-run primitives hold external outcomes, while run records remain separate preparation provenance. This protocol adds no comparison CLI, runtime contract, or schema.

## Learning proposals

A failed case may carry a reusable lesson hint. `propose_lessons()` promotes a hint only after it repeats across a configurable minimum number of failures. The result is a proposal with evidence cases, not an automatic mutation of policy or profiles.

This keeps learning reviewable and prevents a single unusual failure from permanently bloating prompts.

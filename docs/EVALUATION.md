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

## Learning proposals

A failed case may carry a reusable lesson hint. `propose_lessons()` promotes a hint only after it repeats across a configurable minimum number of failures. The result is a proposal with evidence cases, not an automatic mutation of policy or profiles.

This keeps learning reviewable and prevents a single unusual failure from permanently bloating prompts.

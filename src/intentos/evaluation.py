from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from statistics import mean
from typing import Any

from .models import CapabilityClass, IntentRequest, ModelMetadata, PromptResult, RiskLevel, TaskType
from .records import RunMetrics
from .service import optimize_prompt


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    name: str
    request: IntentRequest
    models: tuple[ModelMetadata, ...] = ()
    expected_contains: tuple[str, ...] = ()
    expected_not_contains: tuple[str, ...] = ()
    expected_task: TaskType | None = None
    expected_risk: RiskLevel | None = None
    expected_capability: CapabilityClass | None = None
    max_prompt_chars: int | None = None
    lesson_hint: str | None = None


@dataclass(frozen=True, slots=True)
class EvaluationOutcome:
    name: str
    passed: bool
    score: float
    failures: tuple[str, ...] = ()
    lesson_hint: str | None = None


@dataclass(frozen=True, slots=True)
class RegressionSummary:
    outcomes: tuple[EvaluationOutcome, ...]
    passed: int
    failed: int
    mean_score: float


@dataclass(frozen=True, slots=True)
class VariantRun:
    name: str
    outcome: EvaluationOutcome
    metrics: RunMetrics


@dataclass(frozen=True, slots=True)
class PairedComparison:
    task_id: str
    raw: VariantRun
    prepared: VariantRun
    raw_passed: bool | None
    prepared_passed: bool | None
    winner: str | None
    reason: str
    correctness_regressed: bool
    input_tokens_delta: int | None
    output_tokens_delta: int | None
    total_tokens_delta: int | None
    retries_delta: int | None
    latency_ms_delta: int | None
    quality_score_delta: float | None
    raw_code_lines: int | None = None
    prepared_code_lines: int | None = None

    @property
    def enough_evidence(self) -> bool:
        return self.winner is not None

    @property
    def code_lines_delta(self) -> int | None:
        return _delta(self.raw_code_lines, self.prepared_code_lines)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["raw"]["metrics"]["total_tokens"] = self.raw.metrics.total_tokens
        value["prepared"]["metrics"]["total_tokens"] = self.prepared.metrics.total_tokens
        value["enough_evidence"] = self.enough_evidence
        value["code_lines_delta"] = self.code_lines_delta
        return value

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, allow_nan=False)


@dataclass(frozen=True, slots=True)
class LearningProposal:
    rule: str
    evidence_cases: tuple[str, ...]


def evaluate_result(case: EvaluationCase, result: PromptResult) -> EvaluationOutcome:
    prompt = result.prompt or ""
    checks: list[bool] = []
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        checks.append(condition)
        if not condition:
            failures.append(message)

    for expected in case.expected_contains:
        check(expected in prompt, f"missing expected text: {expected}")
    for forbidden in case.expected_not_contains:
        check(forbidden not in prompt, f"unexpected text present: {forbidden}")

    if case.expected_task is not None:
        check(result.policy is not None and result.policy.task_type is case.expected_task, "task classification mismatch")
    if case.expected_risk is not None:
        check(result.policy is not None and result.policy.risk_level is case.expected_risk, "risk classification mismatch")
    if case.expected_capability is not None:
        check(
            result.routing is not None and result.routing.required_capability is case.expected_capability,
            "capability routing mismatch",
        )
    if case.max_prompt_chars is not None:
        check(len(prompt) <= case.max_prompt_chars, f"prompt exceeds {case.max_prompt_chars} chars")

    if not checks:
        failures.append("no evaluation expectations defined")
        score = 0.0
    else:
        score = sum(checks) / len(checks)

    return EvaluationOutcome(
        name=case.name,
        passed=bool(checks) and not failures,
        score=score,
        failures=tuple(failures),
        lesson_hint=case.lesson_hint,
    )


def run_regression(cases: tuple[EvaluationCase, ...]) -> RegressionSummary:
    outcomes = tuple(
        evaluate_result(case, optimize_prompt(case.request, models=case.models))
        for case in cases
    )
    passed = sum(outcome.passed for outcome in outcomes)
    failed = len(outcomes) - passed
    return RegressionSummary(
        outcomes=outcomes,
        passed=passed,
        failed=failed,
        mean_score=mean(outcome.score for outcome in outcomes) if outcomes else 0.0,
    )


def rank_variants(runs: tuple[VariantRun, ...]) -> tuple[VariantRun, ...]:
    def rank(run: VariantRun) -> tuple[float, ...]:
        reported_quality = run.metrics.quality_score
        return (
            0 if run.metrics.success and run.outcome.passed else 1,
            -run.outcome.score,
            -(reported_quality if reported_quality is not None else run.outcome.score),
            run.metrics.retries if run.metrics.retries is not None else float("inf"),
            run.metrics.total_tokens if run.metrics.total_tokens is not None else float("inf"),
            run.metrics.latency_ms if run.metrics.latency_ms is not None else float("inf"),
        )

    return tuple(sorted(runs, key=rank))


def _delta(raw: int | float | None, prepared: int | float | None) -> int | float | None:
    if raw is None or prepared is None:
        return None
    return prepared - raw


def _passed(run: VariantRun) -> bool | None:
    if run.metrics.success is False or not run.outcome.passed:
        return False
    if run.metrics.success is True:
        return True
    return None


def compare_paired_runs(
    task_id: str,
    raw: VariantRun,
    prepared: VariantRun,
    *,
    raw_code_lines: int | None = None,
    prepared_code_lines: int | None = None,
) -> PairedComparison:
    """Compare externally executed raw/prepared runs for one task only.

    IntentOS does not execute either arm or generalize this result into a product
    rule. Callers must hold downstream agent and task conditions constant. Deltas
    are prepared minus raw, and remain unavailable when either value is missing.
    """
    if not task_id.strip():
        raise ValueError("task_id must not be empty")
    for name, value in (("raw_code_lines", raw_code_lines), ("prepared_code_lines", prepared_code_lines)):
        if value is not None and value < 0:
            raise ValueError(f"{name} must be non-negative")

    raw_passed = _passed(raw)
    prepared_passed = _passed(prepared)
    correctness_regressed = raw_passed is True and prepared_passed is False
    winner: str | None = None

    if raw_passed is True and prepared_passed is False:
        winner, reason = "raw", "The raw arm passed while the prepared arm failed."
    elif prepared_passed is True and raw_passed is False:
        winner, reason = "prepared", "The prepared arm passed while the raw arm failed."
    elif raw_passed is not True or prepared_passed is not True:
        reason = "A passing result is missing or neither arm passed; efficiency cannot decide correctness."
    elif raw.outcome.score != prepared.outcome.score:
        winner = "prepared" if prepared.outcome.score > raw.outcome.score else "raw"
        reason = "The higher evaluation/check score takes precedence over efficiency."
    elif (
        raw.metrics.quality_score is not None
        and prepared.metrics.quality_score is not None
        and raw.metrics.quality_score != prepared.metrics.quality_score
    ):
        winner = "prepared" if prepared.metrics.quality_score > raw.metrics.quality_score else "raw"
        reason = "The higher reported quality score takes precedence over efficiency."
    else:
        deltas = (
            _delta(raw.metrics.retries, prepared.metrics.retries),
            _delta(raw.metrics.total_tokens, prepared.metrics.total_tokens),
            _delta(raw.metrics.latency_ms, prepared.metrics.latency_ms),
        )
        observed = tuple(delta for delta in deltas if delta is not None and delta != 0)
        if observed and all(delta < 0 for delta in observed):
            winner, reason = "prepared", "The prepared arm passed equally and improved every comparable efficiency metric."
        elif observed and all(delta > 0 for delta in observed):
            winner, reason = "raw", "The raw arm passed equally and improved every comparable efficiency metric."
        elif observed:
            reason = "Comparable efficiency metrics disagree, so this task has no clear winner."
        else:
            reason = "No comparable metric shows a difference, so this task has no clear winner."

    return PairedComparison(
        task_id=task_id,
        raw=raw,
        prepared=prepared,
        raw_passed=raw_passed,
        prepared_passed=prepared_passed,
        winner=winner,
        reason=reason,
        correctness_regressed=correctness_regressed,
        input_tokens_delta=_delta(raw.metrics.input_tokens, prepared.metrics.input_tokens),
        output_tokens_delta=_delta(raw.metrics.output_tokens, prepared.metrics.output_tokens),
        total_tokens_delta=_delta(raw.metrics.total_tokens, prepared.metrics.total_tokens),
        retries_delta=_delta(raw.metrics.retries, prepared.metrics.retries),
        latency_ms_delta=_delta(raw.metrics.latency_ms, prepared.metrics.latency_ms),
        quality_score_delta=_delta(raw.metrics.quality_score, prepared.metrics.quality_score),
        raw_code_lines=raw_code_lines,
        prepared_code_lines=prepared_code_lines,
    )


def propose_lessons(
    outcomes: tuple[EvaluationOutcome, ...],
    *,
    min_failures: int = 2,
) -> tuple[LearningProposal, ...]:
    grouped: dict[str, set[str]] = {}
    for outcome in outcomes:
        if outcome.passed or not outcome.lesson_hint:
            continue
        grouped.setdefault(outcome.lesson_hint, set()).add(outcome.name)

    return tuple(
        LearningProposal(rule=rule, evidence_cases=tuple(sorted(cases)))
        for rule, cases in sorted(grouped.items())
        if len(cases) >= min_failures
    )

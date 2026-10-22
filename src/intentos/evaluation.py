from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .models import CapabilityClass, IntentRequest, ModelMetadata, PromptResult, RiskLevel, TaskType
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
class RunMetrics:
    success: bool
    tokens: int | None = None
    latency_ms: int | None = None
    retries: int = 0


@dataclass(frozen=True, slots=True)
class VariantRun:
    name: str
    outcome: EvaluationOutcome
    metrics: RunMetrics


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

    score = 1.0 if not checks else sum(checks) / len(checks)
    return EvaluationOutcome(
        name=case.name,
        passed=not failures,
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
        mean_score=mean(outcome.score for outcome in outcomes) if outcomes else 1.0,
    )


def rank_variants(runs: tuple[VariantRun, ...]) -> tuple[VariantRun, ...]:
    def rank(run: VariantRun) -> tuple[float, ...]:
        return (
            0 if run.metrics.success and run.outcome.passed else 1,
            -run.outcome.score,
            run.metrics.retries,
            run.metrics.tokens if run.metrics.tokens is not None else float("inf"),
            run.metrics.latency_ms if run.metrics.latency_ms is not None else float("inf"),
        )

    return tuple(sorted(runs, key=rank))


def propose_lessons(
    outcomes: tuple[EvaluationOutcome, ...],
    *,
    min_failures: int = 2,
) -> tuple[LearningProposal, ...]:
    grouped: dict[str, list[str]] = {}
    for outcome in outcomes:
        if outcome.passed or not outcome.lesson_hint:
            continue
        grouped.setdefault(outcome.lesson_hint, []).append(outcome.name)

    return tuple(
        LearningProposal(rule=rule, evidence_cases=tuple(cases))
        for rule, cases in sorted(grouped.items())
        if len(cases) >= min_failures
    )

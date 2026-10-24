import math
import unittest

from intentos import IntentRequest
from intentos.evaluation import (
    EvaluationCase,
    EvaluationOutcome,
    compare_paired_runs,
    RunMetrics,
    VariantRun,
    propose_lessons,
    rank_variants,
    run_regression,
)
from intentos.models import CapabilityClass, RiskLevel, TaskType


class EvaluationTests(unittest.TestCase):
    @staticmethod
    def paired_run(
        name: str,
        *,
        success: bool | None = True,
        passed: bool = True,
        score: float = 1.0,
        metrics: RunMetrics | None = None,
    ) -> VariantRun:
        return VariantRun(
            name,
            EvaluationOutcome(name, passed, score),
            metrics if metrics is not None else RunMetrics(success=success),
        )

    def test_regression_suite_scores_prompt_contracts(self) -> None:
        cases = (
            EvaluationCase(
                name="refactor-policy",
                request=IntentRequest("Refactor the parser", target_tool="codex"),
                expected_contains=("KISS and YAGNI", "SOLID, DRY, and Clean Code"),
                expected_task=TaskType.REFACTOR,
                expected_risk=RiskLevel.MEDIUM,
                expected_capability=CapabilityClass.BALANCED,
            ),
            EvaluationCase(
                name="general-no-solid",
                request=IntentRequest("Write a short announcement", target_tool="chatgpt"),
                expected_not_contains=("SOLID", "Approval boundaries:"),
                expected_task=TaskType.GENERAL,
                expected_risk=RiskLevel.LOW,
                expected_capability=CapabilityClass.FAST,
            ),
        )

        summary = run_regression(cases)

        self.assertEqual(summary.passed, 2)
        self.assertEqual(summary.failed, 0)
        self.assertEqual(summary.mean_score, 1.0)

    def test_prompt_length_assertion_can_fail(self) -> None:
        case = EvaluationCase(
            name="too-small-budget",
            request=IntentRequest("Refactor the parser", target_tool="codex"),
            max_prompt_chars=20,
        )

        summary = run_regression((case,))

        self.assertEqual(summary.failed, 1)
        self.assertIn("prompt exceeds", summary.outcomes[0].failures[0])

    def test_empty_evaluation_case_is_not_counted_as_success(self) -> None:
        summary = run_regression(
            (EvaluationCase(name="no-expectations", request=IntentRequest("", target_tool="codex")),)
        )

        self.assertEqual(summary.passed, 0)
        self.assertEqual(summary.failed, 1)
        self.assertEqual(summary.outcomes[0].score, 0.0)
        self.assertIn("no evaluation expectations", summary.outcomes[0].failures[0])

    def test_variant_ranking_prefers_success_then_quality_then_efficiency(self) -> None:
        good = VariantRun(
            "good",
            EvaluationOutcome("good", True, 1.0),
            RunMetrics(success=True, quality_score=0.9, input_tokens=400, output_tokens=100, latency_ms=800, retries=0),
        )
        cheaper = VariantRun(
            "cheaper",
            EvaluationOutcome("cheaper", True, 1.0),
            RunMetrics(success=True, quality_score=0.9, input_tokens=250, output_tokens=50, latency_ms=900, retries=0),
        )
        failed = VariantRun(
            "failed",
            EvaluationOutcome("failed", False, 0.8, ("missing assertion",)),
            RunMetrics(success=False, quality_score=1.0, input_tokens=50, output_tokens=50, latency_ms=100, retries=0),
        )

        ranked = rank_variants((good, failed, cheaper))

        self.assertEqual([run.name for run in ranked], ["cheaper", "good", "failed"])

    def test_variant_ranking_uses_reported_quality_when_contract_scores_tie(self) -> None:
        higher_quality = VariantRun(
            "higher-quality",
            EvaluationOutcome("higher-quality", True, 1.0),
            RunMetrics(success=True, quality_score=0.95, input_tokens=500),
        )
        lower_quality = VariantRun(
            "lower-quality",
            EvaluationOutcome("lower-quality", True, 1.0),
            RunMetrics(success=True, quality_score=0.70, input_tokens=100),
        )

        ranked = rank_variants((lower_quality, higher_quality))

        self.assertEqual([run.name for run in ranked], ["higher-quality", "lower-quality"])

    def test_variant_ranking_does_not_treat_missing_retries_as_zero(self) -> None:
        measured = VariantRun(
            "measured",
            EvaluationOutcome("same", True, 1.0),
            RunMetrics(success=True, retries=1),
        )
        unavailable = VariantRun(
            "unavailable",
            EvaluationOutcome("same", True, 1.0),
            RunMetrics(success=True),
        )

        self.assertEqual([run.name for run in rank_variants((unavailable, measured))], ["measured", "unavailable"])

    def test_paired_comparison_prefers_prepared_when_both_pass_with_fewer_tokens(self) -> None:
        raw = self.paired_run("raw", metrics=RunMetrics(success=True, input_tokens=100, output_tokens=40))
        prepared = self.paired_run("prepared", metrics=RunMetrics(success=True, input_tokens=70, output_tokens=30))

        comparison = compare_paired_runs(
            "parser-refactor-01", raw, prepared, raw_code_lines=120, prepared_code_lines=90
        )

        self.assertEqual(comparison.winner, "prepared")
        self.assertEqual(comparison.total_tokens_delta, -40)
        self.assertEqual(comparison.code_lines_delta, -30)
        self.assertTrue(comparison.enough_evidence)
        payload = comparison.to_dict()
        self.assertEqual(payload["task_id"], "parser-refactor-01")
        self.assertEqual(payload["raw"]["metrics"]["total_tokens"], 140)
        self.assertNotIn("prompt", payload)

    def test_paired_comparison_correctness_dominates_prepared_efficiency(self) -> None:
        raw = self.paired_run("raw", metrics=RunMetrics(success=True, input_tokens=100, output_tokens=40))
        prepared = self.paired_run(
            "prepared", passed=False,
            metrics=RunMetrics(success=False, input_tokens=10, output_tokens=5),
        )

        comparison = compare_paired_runs("task-02", raw, prepared)

        self.assertEqual(comparison.winner, "raw")
        self.assertTrue(comparison.correctness_regressed)
        self.assertEqual(comparison.total_tokens_delta, -125)

    def test_paired_comparison_can_choose_fewer_retries_when_both_pass(self) -> None:
        raw = self.paired_run("raw", metrics=RunMetrics(success=True, retries=2))
        prepared = self.paired_run("prepared", metrics=RunMetrics(success=True, retries=1))

        comparison = compare_paired_runs("task-03", raw, prepared)

        self.assertEqual(comparison.winner, "prepared")
        self.assertEqual(comparison.retries_delta, -1)
        self.assertIsNone(comparison.total_tokens_delta)

    def test_missing_metrics_remain_unavailable_and_do_not_produce_winner(self) -> None:
        raw = self.paired_run("raw", success=None, metrics=RunMetrics(input_tokens=40))
        prepared = self.paired_run("prepared", success=None, metrics=RunMetrics(input_tokens=20))

        comparison = compare_paired_runs("task-04", raw, prepared)

        self.assertIsNone(comparison.winner)
        self.assertFalse(comparison.enough_evidence)
        self.assertIsNone(comparison.total_tokens_delta)
        self.assertEqual(comparison.input_tokens_delta, -20)
        self.assertIsNone(RunMetrics(input_tokens=40).total_tokens)
        self.assertIsNone(comparison.to_dict()["latency_ms_delta"])

    def test_paired_comparison_quality_beats_token_savings(self) -> None:
        raw = self.paired_run(
            "raw", metrics=RunMetrics(success=True, quality_score=0.95, input_tokens=100, output_tokens=40)
        )
        prepared = self.paired_run(
            "prepared", metrics=RunMetrics(success=True, quality_score=0.70, input_tokens=10, output_tokens=5)
        )

        comparison = compare_paired_runs("task-05", raw, prepared)

        self.assertEqual(comparison.winner, "raw")
        self.assertEqual(comparison.total_tokens_delta, -125)

    def test_learning_requires_repeated_failure_evidence(self) -> None:
        outcomes = (
            EvaluationOutcome("a", False, 0.5, ("x",), "Preserve backward compatibility explicitly."),
            EvaluationOutcome("b", False, 0.6, ("y",), "Preserve backward compatibility explicitly."),
            EvaluationOutcome("c", False, 0.7, ("z",), "Unrelated one-off lesson."),
        )

        proposals = propose_lessons(outcomes, min_failures=2)

        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0].rule, "Preserve backward compatibility explicitly.")
        self.assertEqual(proposals[0].evidence_cases, ("a", "b"))

    def test_duplicate_failure_case_does_not_satisfy_learning_threshold(self) -> None:
        repeated = EvaluationOutcome(
            "same-case",
            False,
            0.5,
            ("x",),
            "Preserve backward compatibility explicitly.",
        )

        self.assertEqual(propose_lessons((repeated, repeated), min_failures=2), ())

    def test_run_metrics_reject_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            RunMetrics(input_tokens=-1)
        with self.assertRaises(ValueError):
            RunMetrics(quality_score=math.nan)
        with self.assertRaises(ValueError):
            RunMetrics(quality_score=1.1)


if __name__ == "__main__":
    unittest.main()

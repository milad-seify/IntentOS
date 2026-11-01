import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from intentos import IntentRequest, optimize_prompt
from intentos.cli import main
from intentos.models import RiskLevel, TaskType


OBSERVED_REQUEST = (
    "Review the current IntentOS VS Code extension UI. Given the product direction "
    "toward Reliable AI Delegation, identify UX weaknesses that prevent users from "
    "understanding Risk classification, Approval boundaries, Engineering policy, "
    "Project context, Verification requirements, and routing. Do not implement "
    "anything. Propose only the smallest meaningful UX improvement and the scope "
    "of one follow-up PR."
)


class ReviewClassificationTests(unittest.TestCase):
    def test_observed_review_uses_read_only_policy_through_public_preparation(self) -> None:
        result = optimize_prompt(IntentRequest(OBSERVED_REQUEST, target_tool="codex"))

        self.assertFalse(result.needs_clarification)
        self.assertEqual(result.intent.goal, OBSERVED_REQUEST)
        self.assertEqual(result.policy.task_type, TaskType.GENERAL)
        self.assertEqual(result.policy.risk_level, RiskLevel.LOW)
        prompt = result.prompt or ""
        self.assertIn("read-only", prompt)
        self.assertIn("evidence", prompt)
        self.assertNotIn("Relevant automated checks pass", prompt)
        self.assertNotIn("Change only what is required", prompt)
        self.assertNotIn("Summarize changed files", prompt)
        self.assertNotIn("SOLID", prompt)

    def test_review_actions_are_not_overridden_by_code_subject_matter(self) -> None:
        requests = (
            "Review this code.",
            "Analyze this module. Do not implement anything.",
            "Analyse the API and recommend improvements without modifying code.",
            "Inspect this function; don't change it.",
            "Evaluate the extension code. Never implement changes.",
            "Recommend a fix for this module; do not implement it.",
            "Propose a refactor for this code, without implementing it.",
        )
        for target in ("codex", "claude-code", "chatgpt"):
            for request in requests:
                with self.subTest(target=target, request=request):
                    result = optimize_prompt(IntentRequest(request, target_tool=target))
                    self.assertEqual(result.policy.task_type, TaskType.GENERAL)
                    self.assertNotIn("Relevant automated checks pass", result.prompt or "")

    def test_mixed_review_and_implementation_keeps_normal_classification(self) -> None:
        cases = (
            ("Review this code and fix the bug", TaskType.BUGFIX, RiskLevel.LOW),
            ("Analyze the module then implement the change", TaskType.CODING, RiskLevel.MEDIUM),
            ("Inspect the deployment and apply the fix", TaskType.DEVOPS, RiskLevel.MEDIUM),
            ("Review this code. Refactor the module.", TaskType.REFACTOR, RiskLevel.MEDIUM),
            ("Review this code and make changes", TaskType.CODING, RiskLevel.MEDIUM),
            ("Evaluate this module and correct the errors", TaskType.CODING, RiskLevel.MEDIUM),
            ("Review the module by implementing the feature", TaskType.CODING, RiskLevel.MEDIUM),
            ("Refactoring the module for review", TaskType.CODING, RiskLevel.MEDIUM),
            ("Do not review; implement the feature", TaskType.CODING, RiskLevel.MEDIUM),
            (
                "Review the code. Do not implement anything, but deploy the fix to production.",
                TaskType.DEVOPS,
                RiskLevel.HIGH,
            ),
            (
                "Review production authentication and change the login flow",
                TaskType.SECURITY,
                RiskLevel.HIGH,
            ),
        )
        for request, task, risk in cases:
            with self.subTest(request=request):
                result = optimize_prompt(IntentRequest(request, target_tool="codex"))
                self.assertEqual(result.policy.task_type, task)
                self.assertEqual(result.policy.risk_level, risk)
                self.assertNotIn("Keep the review read-only", result.prompt or "")

    def test_background_review_cannot_override_implementation(self) -> None:
        result = optimize_prompt(IntentRequest.from_values(
            "Implement the API change",
            target_tool="codex",
            context=("Review only. Do not implement anything.",),
        ))
        self.assertEqual(result.policy.task_type, TaskType.CODING)
        self.assertIn("Relevant automated checks pass", result.prompt or "")

    def test_sensitive_review_preserves_high_risk_without_mutation_policy(self) -> None:
        for request in (
            "Inspect production deployment and database schema. Do not implement anything.",
            "Review the security module for vulnerability findings only.",
            "Review concurrent inventory mutation; do not implement anything.",
        ):
            with self.subTest(request=request):
                result = optimize_prompt(IntentRequest(request, target_tool="codex"))
                self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)
                self.assertIn("read-only", result.prompt or "")
                self.assertTrue(result.policy.approval_boundaries)
                self.assertNotIn("Persistent data changes include", result.prompt or "")
                self.assertNotIn("Configuration or deployment changes are validated", result.prompt or "")

    def test_review_preserves_explicit_output_and_verification_requirements(self) -> None:
        result = optimize_prompt(IntentRequest.from_values(
            "Review this module",
            target_tool="codex",
            output_format="Markdown",
            constraints=("Do not implement anything.",),
            success_criteria=("Cite a file and line for each finding.",),
        ))
        self.assertEqual(result.policy.task_type, TaskType.GENERAL)
        self.assertIn("Format: Markdown", result.prompt or "")
        self.assertIn("Do not implement anything.", result.prompt or "")
        self.assertIn("Cite a file and line for each finding.", result.policy.done_criteria)

    def test_cli_json_reproduces_review_classification_and_policy(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["optimize", OBSERVED_REQUEST, "--target", "codex", "--json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["intent"]["target_tool"], "codex")
        self.assertEqual(payload["task_type"], "general")
        self.assertEqual(payload["risk_level"], "low")
        self.assertNotIn("Relevant automated checks pass.", payload["done_criteria"])


if __name__ == "__main__":
    unittest.main()

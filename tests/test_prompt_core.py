import unittest

from intentos import IntentRequest, optimize_prompt
from intentos.models import RiskLevel, TaskType
from intentos.normalize import normalize_intent


class PromptCoreTests(unittest.TestCase):
    def test_missing_target_requests_clarification(self) -> None:
        result = optimize_prompt(IntentRequest("Summarize this architecture decision"))

        self.assertTrue(result.needs_clarification)
        self.assertIsNone(result.prompt)
        self.assertIn("Which AI tool", result.questions[0])

    def test_target_can_be_detected_from_raw_intent(self) -> None:
        result = optimize_prompt(
            IntentRequest("Write a Codex prompt to refactor the auth module")
        )

        self.assertFalse(result.needs_clarification)
        self.assertEqual(result.intent.target_tool, "codex")
        self.assertIn("Scope:", result.prompt or "")
        self.assertIn("Verification:", result.prompt or "")

    def test_explicit_target_overrides_detection(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "Turn these notes into a concise release announcement",
                target_tool="ChatGPT",
                output_format="Markdown",
            )
        )

        self.assertEqual(result.intent.target_tool, "chatgpt")
        self.assertIn("Output:", result.prompt or "")
        self.assertIn("Format: Markdown", result.prompt or "")
        self.assertNotIn("Scope:", result.prompt or "")

    def test_normalization_is_compact_and_deduplicated(self) -> None:
        intent = normalize_intent(
            IntentRequest.from_values(
                "  Fix   the login bug  ",
                target_tool="codex",
                constraints=(" No new dependencies ", "no new dependencies", "Keep API stable"),
                context=(" Python service ", "Python service"),
            )
        )

        self.assertEqual(intent.goal, "Fix the login bug")
        self.assertEqual(intent.constraints, ("No new dependencies", "Keep API stable"))
        self.assertEqual(intent.context, ("Python service",))

    def test_codex_prompt_has_default_evidence_contract(self) -> None:
        result = optimize_prompt(
            IntentRequest("Codex: fix the failing parser test", target_tool="codex")
        )

        prompt = result.prompt or ""
        self.assertIn("avoid unrelated refactors", prompt)
        self.assertIn("Run the smallest relevant checks", prompt)
        self.assertIn("Relevant automated checks pass", prompt)

    def test_empty_goal_is_rejected(self) -> None:
        result = optimize_prompt(IntentRequest("   ", target_tool="codex"))

        self.assertTrue(result.needs_clarification)
        self.assertIsNone(result.prompt)
        self.assertIn("What outcome", result.questions[0])

    def test_refactor_gets_contextual_engineering_policy(self) -> None:
        result = optimize_prompt(
            IntentRequest("Refactor the parser module", target_tool="codex")
        )

        self.assertIsNotNone(result.policy)
        self.assertEqual(result.policy.task_type, TaskType.REFACTOR)
        self.assertEqual(result.policy.risk_level, RiskLevel.MEDIUM)
        prompt = result.prompt or ""
        self.assertIn("KISS and YAGNI", prompt)
        self.assertIn("SOLID, DRY, and Clean Code", prompt)
        self.assertIn("observable behavior stable", prompt)

    def test_devops_policy_adds_reproducibility_and_rollback(self) -> None:
        result = optimize_prompt(
            IntentRequest("Update the Terraform deployment for staging", target_tool="codex")
        )

        self.assertEqual(result.policy.task_type, TaskType.DEVOPS)
        self.assertEqual(result.policy.risk_level, RiskLevel.MEDIUM)
        prompt = result.prompt or ""
        self.assertIn("reproducible, declarative, and idempotent", prompt)
        self.assertIn("rollback or recovery", prompt)

    def test_high_risk_work_requires_approval_boundaries(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "Change the production database schema and authentication flow",
                target_tool="codex",
            )
        )

        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)
        prompt = result.prompt or ""
        self.assertIn("Approval boundaries:", prompt)
        self.assertIn("destructive operations", prompt)
        self.assertIn("production writes or persistent schema changes", prompt)

    def test_general_writing_does_not_receive_software_rules(self) -> None:
        result = optimize_prompt(
            IntentRequest("Write a short project announcement", target_tool="chatgpt")
        )

        self.assertEqual(result.policy.task_type, TaskType.GENERAL)
        prompt = result.prompt or ""
        self.assertNotIn("SOLID", prompt)
        self.assertNotIn("Approval boundaries:", prompt)


if __name__ == "__main__":
    unittest.main()

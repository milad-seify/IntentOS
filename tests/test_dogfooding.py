import unittest

from intentos import IntentRequest, optimize_prompt
from intentos.models import RiskLevel, TaskType


class RealWorldDogfoodingTests(unittest.TestCase):
    def test_persian_codex_refactor_is_detected(self) -> None:
        result = optimize_prompt(
            IntentRequest("برای کدکس یک پرامپت بساز که این ماژول را ریفکتور کند و رفتار فعلی تغییر نکند")
        )

        self.assertFalse(result.needs_clarification)
        self.assertEqual(result.intent.target_tool, "codex")
        self.assertEqual(result.policy.task_type, TaskType.REFACTOR)
        self.assertEqual(result.policy.risk_level, RiskLevel.MEDIUM)
        self.assertIn("SOLID", result.prompt or "")

    def test_persian_devops_production_task_is_high_risk(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "استقرار Docker را روی محیط تولید اصلاح کن و rollback را حفظ کن",
                target_tool="codex",
            )
        )

        self.assertEqual(result.policy.task_type, TaskType.DEVOPS)
        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)
        self.assertIn("rollback", (result.prompt or "").lower())
        self.assertIn("production writes", (result.prompt or "").lower())

    def test_persian_architecture_task_is_detected(self) -> None:
        result = optimize_prompt(
            IntentRequest("معماری سیستم را بررسی کن و trade-off ها را بگو", target_tool="chatgpt")
        )

        self.assertEqual(result.policy.task_type, TaskType.ARCHITECTURE)
        self.assertEqual(result.policy.risk_level, RiskLevel.MEDIUM)
        self.assertIn("trade-offs", result.prompt or "")

    def test_documentation_only_architecture_stays_lightweight(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "Documentation only: update the architecture docs to reflect the current modular monolith",
                target_tool="codex",
            )
        )

        prompt = result.prompt or ""
        self.assertEqual(result.policy.task_type, TaskType.ARCHITECTURE)
        self.assertEqual(result.policy.risk_level, RiskLevel.LOW)
        self.assertIn("documentation or comments", prompt)
        self.assertNotIn("Apply SOLID", prompt)
        self.assertNotIn("add dependencies", prompt)

    def test_persian_claude_code_alias_beats_plain_claude(self) -> None:
        result = optimize_prompt(
            IntentRequest("برای کلود کد پرامپتی بساز که parser را refactor کند")
        )

        self.assertFalse(result.needs_clarification)
        self.assertEqual(result.intent.target_tool, "claude-code")
        self.assertIn("Scope:", result.prompt or "")

    def test_persian_general_request_with_explicit_target_stays_general(self) -> None:
        result = optimize_prompt(
            IntentRequest("یک متن کوتاه برای معرفی پروژه بنویس", target_tool="chatgpt")
        )

        self.assertEqual(result.policy.task_type, TaskType.GENERAL)
        self.assertEqual(result.policy.risk_level, RiskLevel.LOW)
        self.assertNotIn("SOLID", result.prompt or "")


if __name__ == "__main__":
    unittest.main()

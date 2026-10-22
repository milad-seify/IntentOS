import unittest

from intentos import IntentRequest, optimize_prompt


class ProfileDetectionTests(unittest.TestCase):
    def test_claude_code_wins_over_generic_claude_match(self) -> None:
        result = optimize_prompt(
            IntentRequest("Write a Claude Code prompt to refactor the parser")
        )

        self.assertFalse(result.needs_clarification)
        self.assertEqual(result.intent.target_tool, "claude-code")
        self.assertIn("Scope:", result.prompt or "")

    def test_plain_claude_still_detects_claude_profile(self) -> None:
        result = optimize_prompt(
            IntentRequest("Ask Claude to summarize this decision")
        )

        self.assertFalse(result.needs_clarification)
        self.assertEqual(result.intent.target_tool, "claude")
        self.assertNotIn("Scope:", result.prompt or "")


if __name__ == "__main__":
    unittest.main()

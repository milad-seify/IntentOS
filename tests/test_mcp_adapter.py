import unittest

from intentos.mcp_server import MAX_PROJECT_CONTEXT_CHARS, prepare_task


class MCPAdapterTests(unittest.TestCase):
    def test_prepare_task_reuses_core_contract(self) -> None:
        payload = prepare_task(
            "Refactor the parser without changing behavior",
            target_tool="codex",
            constraints=["No new dependencies"],
            success_criteria=["Relevant tests pass"],
        )

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["task_type"], "refactor")
        self.assertEqual(payload["risk_level"], "medium")
        self.assertIn("No new dependencies", payload["intent"]["constraints"])
        self.assertIn("Relevant tests pass", payload["intent"]["success_criteria"])

    def test_prepare_task_can_return_clarification(self) -> None:
        payload = prepare_task("Refactor the parser")

        self.assertEqual(payload["status"], "clarification")
        self.assertTrue(payload["needs_clarification"])
        self.assertTrue(payload["questions"])

    def test_project_context_is_caller_supplied_and_bounded(self) -> None:
        payload = prepare_task(
            "Refactor parser token validation",
            target_tool="codex",
            project_context=[
                {
                    "path": "/path/that/does/not/exist/parser-notes.md",
                    "content": "Parser token validation refactor guidance.",
                }
            ],
        )

        self.assertEqual(
            payload["context"]["selected_paths"],
            ["/path/that/does/not/exist/parser-notes.md"],
        )

    def test_project_context_over_budget_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            prepare_task(
                "Review parser",
                target_tool="codex",
                project_context=[
                    {
                        "path": "parser.md",
                        "content": "x" * (MAX_PROJECT_CONTEXT_CHARS + 1),
                    }
                ],
            )

    def test_high_risk_boundaries_are_preserved(self) -> None:
        payload = prepare_task(
            "Deploy authentication changes to production",
            target_tool="codex",
        )

        self.assertEqual(payload["risk_level"], "high")
        self.assertTrue(payload["approval_boundaries"])


if __name__ == "__main__":
    unittest.main()

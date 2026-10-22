import unittest

from intentos import ContextDocument, IntentRequest, optimize_project_prompt, plan_agent_workspace
from intentos.context import select_project_context
from intentos.models import WorkspaceAction
from intentos.normalize import normalize_intent


class ProjectContextTests(unittest.TestCase):
    def test_authoritative_agent_guidance_is_prioritized(self) -> None:
        intent = normalize_intent(
            IntentRequest("Refactor the auth module", target_tool="codex")
        )
        documents = (
            ContextDocument("notes/random.md", "auth module notes"),
            ContextDocument(
                "AGENTS.md",
                "Auth changes must preserve public behavior and run tests.",
                authoritative=True,
            ),
        )

        selection = select_project_context(intent, documents)

        self.assertEqual(selection.selected[0].document.path, "AGENTS.md")

    def test_duplicate_context_is_omitted(self) -> None:
        intent = normalize_intent(IntentRequest("Update Docker deployment", target_tool="codex"))
        documents = (
            ContextDocument("docs/A.md", "Docker deployment rules"),
            ContextDocument("docs/B.md", "Docker deployment rules"),
        )

        selection = select_project_context(intent, documents)

        self.assertEqual(len(selection.selected), 1)
        self.assertIn("docs/B.md", selection.omitted_paths)

    def test_context_budget_is_bounded(self) -> None:
        intent = normalize_intent(IntentRequest("Review architecture", target_tool="codex"))
        documents = (
            ContextDocument("ARCHITECTURE.md", "architecture " * 1000, authoritative=True),
        )

        selection = select_project_context(intent, documents, max_chars=300)

        self.assertLessEqual(selection.total_chars, 300)
        self.assertIn("clipped to context budget", selection.selected[0].reasons)

    def test_project_prompt_contains_selected_context(self) -> None:
        result = optimize_project_prompt(
            IntentRequest("Refactor the parser module", target_tool="codex"),
            (
                ContextDocument(
                    "AGENTS.md",
                    "Parser work must keep backward compatibility.",
                    authoritative=True,
                ),
            ),
        )

        self.assertIsNotNone(result.context_selection)
        self.assertIn("[AGENTS.md]", result.prompt or "")
        self.assertIn("backward compatibility", result.prompt or "")

    def test_workspace_plan_creates_missing_agent_files(self) -> None:
        plan = plan_agent_workspace((), current_phase="Phase 3 — Project Context")

        actions = {(change.path, change.action) for change in plan.changes}
        self.assertIn(("AGENTS.md", WorkspaceAction.CREATE), actions)
        self.assertIn(("docs/STATUS.md", WorkspaceAction.CREATE), actions)

    def test_workspace_plan_updates_stale_phase(self) -> None:
        plan = plan_agent_workspace(
            (
                ContextDocument(
                    "AGENTS.md",
                    "# AGENTS.md\n\n## Current phase\n\nPhase 2\n",
                    authoritative=True,
                ),
                ContextDocument("docs/STATUS.md", "# Status\n\nPhase 2\n"),
            ),
            current_phase="Phase 3 — Project Context",
        )

        self.assertTrue(
            any(change.path == "AGENTS.md" and change.action is WorkspaceAction.UPDATE for change in plan.changes)
        )
        self.assertTrue(
            any(change.path == "docs/STATUS.md" and change.action is WorkspaceAction.UPDATE for change in plan.changes)
        )

    def test_workspace_plan_warns_on_duplicate_and_bloated_context(self) -> None:
        duplicate = "x" * 13000
        plan = plan_agent_workspace(
            (
                ContextDocument("docs/A.md", duplicate),
                ContextDocument("docs/B.md", duplicate),
            ),
            current_phase="Phase 3",
        )

        self.assertTrue(any("duplicate context" in warning for warning in plan.warnings))
        self.assertTrue(any("may be bloated" in warning for warning in plan.warnings))


if __name__ == "__main__":
    unittest.main()

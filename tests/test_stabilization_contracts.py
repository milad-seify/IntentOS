import unittest

from intentos import ContextDocument, IntentRequest, optimize_project_prompt, optimize_prompt, plan_agent_workspace
from intentos.context import select_project_context
from intentos.models import RiskLevel, TaskType
from intentos.normalize import normalize_intent
from intentos.skills import build_skill_artifact


class StabilizationContractTests(unittest.TestCase):
    def test_context_cannot_downgrade_production_migration_risk(self) -> None:
        result = optimize_prompt(
            IntentRequest.from_values(
                "Apply the production database migration",
                target_tool="codex",
                context=("Previous task: documentation only.",),
            )
        )

        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)
        self.assertTrue(result.policy.approval_boundaries)

    def test_negated_documentation_only_does_not_downgrade_risk(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "Not documentation only: change production authentication",
                target_tool="codex",
            )
        )

        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)
        self.assertTrue(result.policy.approval_boundaries)

    def test_common_login_request_is_security_sensitive(self) -> None:
        result = optimize_prompt(IntentRequest("Add login to this project", target_tool="codex"))

        self.assertEqual(result.policy.task_type, TaskType.SECURITY)
        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)

    def test_documentation_about_login_stays_lightweight(self) -> None:
        result = optimize_prompt(
            IntentRequest("Update documentation for the login flow", target_tool="codex")
        )

        self.assertEqual(result.policy.task_type, TaskType.GENERAL)
        self.assertEqual(result.policy.risk_level, RiskLevel.LOW)
        self.assertFalse(result.policy.approval_boundaries)

    def test_documentation_plus_deploy_remains_high_risk(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "Update documentation and deploy login changes to production",
                target_tool="codex",
            )
        )

        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)
        self.assertTrue(result.policy.approval_boundaries)

    def test_destructive_production_command_is_high_risk(self) -> None:
        result = optimize_prompt(
            IntentRequest("Run rm -rf /srv/app/data on prod", target_tool="codex")
        )

        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)
        self.assertIn("destructive operations", " ".join(result.policy.approval_boundaries))

    def test_persian_destructive_request_is_high_risk(self) -> None:
        result = optimize_prompt(
            IntentRequest("همه فایل‌ها را پاک کن", target_tool="codex")
        )

        self.assertEqual(result.policy.risk_level, RiskLevel.HIGH)

    def test_security_term_matching_uses_boundaries(self) -> None:
        result = optimize_prompt(
            IntentRequest("Write a biography of William", target_tool="chatgpt")
        )

        self.assertEqual(result.policy.task_type, TaskType.GENERAL)
        self.assertEqual(result.policy.risk_level, RiskLevel.LOW)

    def test_multiline_goal_and_context_preserve_formatting(self) -> None:
        code = "def allowed(user):\n    # deny anonymous users\n    return user is not None"
        intent = normalize_intent(
            IntentRequest.from_values(code, target_tool="codex", context=(code,))
        )

        self.assertEqual(intent.goal, code)
        self.assertEqual(intent.context, (code,))

    def test_case_sensitive_context_values_are_not_deduplicated(self) -> None:
        intent = normalize_intent(
            IntentRequest.from_values(
                "Inspect environment values",
                target_tool="codex",
                context=("TOKEN=ABC", "TOKEN=abc"),
            )
        )

        self.assertEqual(intent.context, ("TOKEN=ABC", "TOKEN=abc"))

    def test_codex_preserves_explicit_output_contract(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "Summarize the parser design",
                target_tool="codex",
                output_format="JSON",
                audience="beginners",
            )
        )

        prompt = result.prompt or ""
        self.assertIn("Output:", prompt)
        self.assertIn("Format: JSON", prompt)
        self.assertIn("Audience: beginners", prompt)

        artifact = build_skill_artifact(result.intent, result.policy)
        self.assertIn("## Output", artifact.content)
        self.assertIn("Format: JSON", artifact.content)
        self.assertIn("Audience: beginners", artifact.content)

    def test_authoritative_duplicate_wins_over_non_authoritative_copy(self) -> None:
        intent = normalize_intent(IntentRequest("Refactor auth", target_tool="codex"))
        shared = "Auth changes must preserve behavior."
        selection = select_project_context(
            intent,
            (
                ContextDocument("notes.txt", shared),
                ContextDocument("AGENTS.md", shared, authoritative=True),
            ),
        )

        self.assertEqual(selection.selected[0].document.path, "AGENTS.md")
        self.assertIn("notes.txt", selection.omitted_paths)

    def test_relevance_can_beat_authority_for_distinct_context(self) -> None:
        intent = normalize_intent(
            IntentRequest("Refactor parser token validation", target_tool="codex")
        )
        selection = select_project_context(
            intent,
            (
                ContextDocument("POLICY.md", "General project rules.", authoritative=True),
                ContextDocument(
                    "parser-notes.md",
                    "Parser token validation refactor guidance.",
                ),
            ),
            max_chars=45,
        )

        self.assertEqual(selection.selected[0].document.path, "parser-notes.md")

    def test_negative_context_budget_is_rejected(self) -> None:
        intent = normalize_intent(IntentRequest("Review architecture", target_tool="codex"))

        with self.assertRaises(ValueError):
            select_project_context(
                intent,
                (ContextDocument("ARCHITECTURE.md", "architecture"),),
                max_chars=-1,
            )

    def test_windows_style_authoritative_path_keeps_filename_priority(self) -> None:
        intent = normalize_intent(IntentRequest("Review current status", target_tool="codex"))
        selection = select_project_context(
            intent,
            (
                ContextDocument("notes/status.txt", "current status notes"),
                ContextDocument("docs\\STATUS.md", "current status", authoritative=True),
            ),
        )

        self.assertEqual(selection.selected[0].document.path, "docs\\STATUS.md")

    def test_explicit_context_must_fit_project_context_budget(self) -> None:
        with self.assertRaises(ValueError):
            optimize_project_prompt(
                IntentRequest.from_values(
                    "Refactor parser",
                    target_tool="codex",
                    context=("x" * 100,),
                ),
                (),
                max_context_chars=10,
            )

    def test_workspace_recognizes_windows_status_path(self) -> None:
        plan = plan_agent_workspace(
            (
                ContextDocument("AGENTS.md", "# AGENTS.md\n\n## Current phase\n\nPhase 7\n"),
                ContextDocument("docs\\STATUS.md", "# Status\n\n## Current phase\n\nPhase 7\n"),
            ),
            current_phase="Phase 7",
        )

        actions = {change.path: change.action.value for change in plan.changes}
        self.assertEqual(actions["docs\\STATUS.md"], "keep")

    def test_workspace_phase_update_preserves_other_section_content(self) -> None:
        content = (
            "# AGENTS.md\n\n"
            "## Current phase\n\n"
            "Phase 6\n\n"
            "Never delete customer data.\n\n"
            "## Rules\n\n"
            "Keep changes small.\n"
        )
        plan = plan_agent_workspace(
            (
                ContextDocument("AGENTS.md", content),
                ContextDocument("docs/STATUS.md", "# Status\n\n## Current phase\n\nPhase 6\n"),
            ),
            current_phase="Phase 7",
        )

        agents_change = next(change for change in plan.changes if change.path == "AGENTS.md")
        self.assertIn("Phase 7", agents_change.proposed_content or "")
        self.assertIn("Never delete customer data.", agents_change.proposed_content or "")
        self.assertIn("## Rules", agents_change.proposed_content or "")


if __name__ == "__main__":
    unittest.main()

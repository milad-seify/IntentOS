import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from intentos.cli import main


class CliTests(unittest.TestCase):
    def test_optimize_json_output(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    "optimize",
                    "Refactor the parser",
                    "--target",
                    "codex",
                    "--output-format",
                    "JSON",
                    "--audience",
                    "maintainers",
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["intent"]["goal"], "Refactor the parser")
        self.assertEqual(payload["intent"]["output_format"], "JSON")
        self.assertEqual(payload["intent"]["audience"], "maintainers")
        self.assertEqual(payload["task_type"], "refactor")
        self.assertEqual(payload["risk_level"], "medium")
        self.assertEqual(payload["routing"]["required_capability"], "balanced")
        self.assertIn("KISS and YAGNI", payload["prompt"])
        self.assertTrue(payload["engineering_rules"])
        self.assertTrue(payload["done_criteria"])

    def test_cli_can_detect_target_when_target_flag_is_omitted(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["optimize", "Codex: refactor the parser", "--json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["routing"]["target_tool"], "codex")

    def test_unknown_target_returns_structured_clarification(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                ["optimize", "Refactor the parser", "--target", "codxe", "--json"]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "clarification")
        self.assertTrue(payload["needs_clarification"])
        self.assertIn("Unknown AI tool", payload["questions"][0])

    def test_context_file_is_loaded_by_cli(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "AGENTS.md"
            path.write_text("Parser work must preserve compatibility.", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main(
                    [
                        "optimize",
                        "Refactor the parser",
                        "--target",
                        "codex",
                        "--context-file",
                        str(path),
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertIn(str(path), payload["context_paths"])
            self.assertEqual(payload["context"]["selected"][0]["path"], str(path))
            self.assertTrue(payload["context"]["selected"][0]["reasons"])
            self.assertIn("preserve compatibility", payload["prompt"])

    def test_missing_context_file_returns_json_error(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    "optimize",
                    "Refactor the parser",
                    "--target",
                    "codex",
                    "--context-file",
                    "definitely-missing-file.md",
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "error")
        self.assertIn("FileNotFoundError", payload["error"]["type"])

    def test_skill_command_emits_portable_artifact(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    "skill",
                    "Refactor the parser",
                    "--target",
                    "codex",
                    "--name",
                    "Parser Refactor",
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["name"], "parser-refactor")
        self.assertIn('name: "parser-refactor"', payload["content"])
        self.assertIn("## Engineering", payload["content"])

    def test_skill_validation_error_remains_machine_readable(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    "skill",
                    "Refactor the parser",
                    "--target",
                    "codex",
                    "--description",
                    "x" * 1025,
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error"]["type"], "ValueError")

    def test_workspace_command_only_returns_plan(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    "workspace",
                    "--phase",
                    "Phase 6 — Integrations",
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["changes"][0]["action"], "create")
        self.assertEqual(payload["changes"][0]["path"], "AGENTS.md")


if __name__ == "__main__":
    unittest.main()

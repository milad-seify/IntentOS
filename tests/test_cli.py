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
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["task_type"], "refactor")
        self.assertEqual(payload["risk_level"], "medium")
        self.assertEqual(payload["routing"]["required_capability"], "balanced")
        self.assertIn("KISS and YAGNI", payload["prompt"])

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
            self.assertIn("preserve compatibility", payload["prompt"])

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
        self.assertEqual(payload["name"], "parser-refactor")
        self.assertIn('name: "parser-refactor"', payload["content"])
        self.assertIn("## Engineering", payload["content"])

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
        self.assertEqual(payload["changes"][0]["action"], "create")
        self.assertEqual(payload["changes"][0]["path"], "AGENTS.md")


if __name__ == "__main__":
    unittest.main()

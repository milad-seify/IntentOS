import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from intentos.cli import main


class CompassCliTests(unittest.TestCase):
    def test_explicit_sources_and_scope_have_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "PLAN.md"
            state = root / "STATUS.md"
            plan.write_text(
                "## Project goal\nShip the dashboard\n\n## In Scope\n- Review API\n",
                encoding="utf-8",
            )
            state.write_text(
                "## Current phase\nMVP\n\n## Next action\nVerify dashboard\n",
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                code = main([
                    "compass", "--authoritative-document", str(plan),
                    "--document", str(state), "--task", "Review API", "--json",
                ])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "review")
            self.assertEqual(result["fields"]["goal"]["value"], "Ship the dashboard")
            self.assertEqual(result["fields"]["current_phase"]["value"], "MVP")
            self.assertEqual(result["fields"]["blocked"]["status"], "missing")
            self.assertEqual(result["fields"]["goal"]["evidence"][0]["path"], str(plan))
            self.assertEqual(result["fields"]["goal"]["evidence"][0]["line"], 2)
            self.assertTrue(result["fields"]["goal"]["evidence"][0]["authoritative"])
            self.assertEqual(result["task_scope"]["status"], "in_scope")
            self.assertFalse(result["task_scope"]["scope_review_required"])
            self.assertEqual(state.read_text(encoding="utf-8"), "## Current phase\nMVP\n\n## Next action\nVerify dashboard\n")

    def test_document_name_alone_does_not_grant_scope_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "STATUS.md"
            plan.write_text("## In Scope\n- Deploy API\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main(["compass", "--document", str(plan), "--task", "Deploy API", "--json"])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(result["task_scope"]["status"], "unknown")
            self.assertTrue(result["task_scope"]["scope_review_required"])
            self.assertFalse(result["task_scope"]["evidence"][0]["authoritative"])

    def test_stale_and_conflicting_sources_never_claim_known_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "A.md"
            second = Path(directory) / "B.md"
            first.write_text("## Current phase\nMVP\n", encoding="utf-8")
            second.write_text("## Current phase\nLaunch\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["compass", "--document", str(first), "--document", str(second), "--json"]), 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["fields"]["current_phase"]["status"], "unresolved")
            self.assertIsNone(result["fields"]["current_phase"]["value"])
            second.write_text("## Evidence freshness\nstale\n\n## Current phase\nLaunch\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["compass", "--document", str(first), "--document", str(second), "--json"]), 0)
            self.assertEqual(json.loads(output.getvalue())["fields"]["current_phase"]["status"], "stale")

    def test_missing_or_unsupplied_documents_report_error(self):
        for args in (["compass", "--json"], ["compass", "--document", "missing-compass-file.md", "--json"]):
            with self.subTest(args=args):
                output = StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(args), 2)
                self.assertEqual(json.loads(output.getvalue())["status"], "error")

    def test_module_entry_point_works_outside_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "PLAN.md"
            plan.write_text("## Project goal\nShip the dashboard\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-m", "intentos", "compass", "--document", str(plan), "--json"],
                cwd=directory, capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["fields"]["goal"]["value"], "Ship the dashboard")


if __name__ == "__main__":
    unittest.main()

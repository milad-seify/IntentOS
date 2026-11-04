import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from intentos.cli import main


STATE = "## Current phase\nMVP\n\n## Next action\nReview API\n"


class StateCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        self.status = self.root / "docs" / "STATUS.md"
        self.status.write_text(STATE, encoding="utf-8", newline="")

    def command(self, *args):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["state", *args, "--json"])
        return code, json.loads(output.getvalue())

    def test_status_preview_then_explicit_apply_across_processes(self):
        arguments = [
            "status", "--root", str(self.root), "--current-phase", "Milestone 2",
            "--evidence", "PR #12 reviewed by owner",
        ]
        preview = subprocess.run(
            [sys.executable, "-m", "intentos", "state", *arguments, "--json"],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(preview.returncode, 0, preview.stderr)
        proposal = json.loads(preview.stdout)
        self.assertEqual(proposal["status"], "update")
        self.assertIn("Milestone 2", proposal["proposed_content"])
        self.assertEqual(self.status.read_text(encoding="utf-8"), STATE)

        applied = subprocess.run(
            [sys.executable, "-m", "intentos", "state", *arguments,
             "--approve-digest", proposal["approval_digest"], "--json"],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(json.loads(applied.stdout)["status"], "applied")
        self.assertIn("Milestone 2", self.status.read_text(encoding="utf-8"))

    def test_changed_source_invalidates_preview_approval(self):
        arguments = ["status", "--root", str(self.root), "--next-action", "Run checks", "--evidence", "CI #12"]
        code, preview = self.command(*arguments)
        self.assertEqual(code, 0)
        self.status.write_text("## Current phase\nChanged externally\n\n## Next action\nReview API\n", encoding="utf-8", newline="")
        code, result = self.command(*arguments, "--approve-digest", preview["approval_digest"])
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "error")
        self.assertIn("approval digest", result["error"]["message"])
        self.assertIn("Changed externally", self.status.read_text(encoding="utf-8"))

    def test_changed_related_source_invalidates_preview_approval(self):
        related = self.root / "docs" / "PLAN.md"
        related.write_text("## Project goal\nBuild an app\n", encoding="utf-8", newline="")
        arguments = [
            "status", "--root", str(self.root), "--next-action", "Run checks",
            "--evidence", "CI #12", "--related-document", str(related),
        ]
        code, preview = self.command(*arguments)
        self.assertEqual(code, 0)
        self.assertEqual(len(preview["related_source_fingerprints"]), 1)
        related.write_text("## Project goal\nBuild a different app\n", encoding="utf-8", newline="")
        code, result = self.command(*arguments, "--approve-digest", preview["approval_digest"])
        self.assertEqual(code, 2)
        self.assertIn("approval digest", result["error"]["message"])
        self.assertEqual(self.status.read_text(encoding="utf-8"), STATE)

    def test_missing_evidence_or_approval_does_not_write(self):
        code, result = self.command("status", "--root", str(self.root), "--current-phase", "Done")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "needs_review")
        self.assertIsNone(result["approval_digest"])
        code, result = self.command(
            "status", "--root", str(self.root), "--current-phase", "Done",
            "--evidence", "PR #12", "--approve-digest", "0" * 64,
        )
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "error")
        self.assertEqual(self.status.read_text(encoding="utf-8"), STATE)

    def test_decision_append_requires_reviewed_digest(self):
        decisions = self.root / "docs" / "DECISIONS.md"
        decisions.write_text("# Decisions\n\n## D-001 — Initial scope\n\nAccepted.\n", encoding="utf-8", newline="")
        arguments = [
            "decision", "--root", str(self.root), "--decision-id", "D-002",
            "--title", "Review boundary", "--body", "Owner approval required.",
            "--approval-ref", "issue #7 approved by owner",
        ]
        code, preview = self.command(*arguments)
        self.assertEqual(code, 0)
        self.assertEqual(preview["status"], "update")
        self.assertNotIn("D-002", decisions.read_text(encoding="utf-8"))
        code, result = self.command(*arguments, "--approve-digest", preview["approval_digest"])
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "applied")
        self.assertIn("## D-002 — Review boundary", decisions.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

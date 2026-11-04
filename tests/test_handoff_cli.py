import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from intentos.cli import main


class HandoffCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.root = self.home / "project"
        self.root.mkdir()
        self.context = self.root / "STATUS.md"
        self.context.write_text("# Status\nCurrent phase: build\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("add", "STATUS.md")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "base")
        self.packet = self.home / "handoff.json"

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def call(self, *args):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["handoff", *args, "--json"])
        return code, json.loads(output.getvalue())

    def prepare(self, text="Refactor the parser without changing behavior", target="codex"):
        return self.call(
            "prepare", text, "--root", str(self.root), "--target", target,
            "--task-id", "task-1", "--context-file", "STATUS.md",
            "--success", "Existing tests pass", "--output", str(self.packet),
        )

    def preview(self, *args):
        return self.call("dispatch", "--root", str(self.root), "--file", str(self.packet), *args)

    def test_preparation_and_explicit_dispatch_boundary(self):
        code, result = self.prepare()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "saved")
        saved = json.loads(self.packet.read_text(encoding="utf-8"))
        self.assertEqual(saved["handoff"]["target_tool"], "codex")
        self.assertIn("Existing tests pass", saved["handoff"]["prepared_prompt"])
        self.assertEqual(saved["context_files"], ["STATUS.md"])
        self.assertEqual(len(saved["handoff"]["context_digest"]), 64)
        with patch("intentos.cli.run_codex_handoff") as run:
            code, preview = self.preview()
            self.assertEqual(code, 0)
            self.assertEqual(preview["status"], "approval_required")
            self.assertEqual(len(preview["approval_digest"]), 64)
            run.assert_not_called()
            code, model_preview = self.preview("--model", "caller-model")
            self.assertEqual(code, 0)
            self.assertNotEqual(preview["approval_digest"], model_preview["approval_digest"])
            code, rejected_model = self.preview("--model", "caller-model", "--approve-digest", preview["approval_digest"])
            self.assertEqual(code, 2)
            self.assertEqual(rejected_model["status"], "error")
            code, rejected = self.preview("--approve-digest", "0" * 64)
            self.assertEqual(code, 2)
            self.assertEqual(rejected["status"], "error")
            run.assert_not_called()
            run.return_value = {"status": "completed_unverified", "exit_code": 0}
            code, receipt = self.preview("--approve-digest", preview["approval_digest"])
            self.assertEqual(code, 0)
            self.assertEqual(receipt["status"], "completed_unverified")
            self.assertEqual(run.call_args.kwargs["sandbox"], "read-only")

    def test_context_or_policy_tampering_requires_new_preparation(self):
        self.prepare()
        self.context.write_text("# Status\nCurrent phase: production\n", encoding="utf-8")
        code, result = self.preview()
        self.assertEqual(code, 2)
        self.assertIn("context changed", result["error"]["message"])
        self.context.write_text("# Status\nCurrent phase: build\n", encoding="utf-8")
        saved = json.loads(self.packet.read_text(encoding="utf-8"))
        saved["review"]["risk_level"] = "low"
        self.packet.write_text(json.dumps(saved), encoding="utf-8")
        code, result = self.preview()
        self.assertEqual(code, 2)
        self.assertIn("does not match", result["error"]["message"])

    def test_high_risk_workspace_write_is_blocked(self):
        request = "Make demo checkout concurrency-safe so successful order creation atomically consumes product stock and concurrent checkouts cannot oversell inventory, while preserving existing order idempotency, cart ownership, pricing behavior, and demo-only semantics."
        code, result = self.prepare(request)
        self.assertEqual(code, 0)
        self.assertEqual(result["risk_level"], "high")
        code, result = self.preview("--sandbox", "workspace-write")
        self.assertEqual(code, 2)
        self.assertIn("high-risk", result["error"]["message"])

    def test_non_codex_executable_is_rejected_before_approval(self):
        self.prepare()
        code, result = self.preview("--executable", "python")
        self.assertEqual(code, 2)
        self.assertIn("Codex executable", result["error"]["message"])

    def test_other_agent_has_portable_packet_and_explicit_unavailable_status(self):
        code, result = self.prepare(target="claude-code")
        self.assertEqual(code, 0)
        saved = json.loads(self.packet.read_text(encoding="utf-8"))
        self.assertEqual(saved["handoff"]["target_tool"], "claude-code")
        code, result = self.preview()
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "unavailable")

    def test_workspace_write_requires_clean_root_even_after_approval(self):
        self.prepare()
        code, preview = self.preview("--sandbox", "workspace-write")
        self.assertEqual(code, 0)
        (self.root / "scratch.txt").write_text("untracked", encoding="utf-8")
        with patch("intentos.cli.run_codex_handoff") as run:
            code, result = self.preview("--sandbox", "workspace-write", "--approve-digest", preview["approval_digest"])
            self.assertEqual(code, 2)
            self.assertIn("clean Git", result["error"]["message"])
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

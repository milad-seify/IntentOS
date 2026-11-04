import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from intentos.codex_adapter import run_codex_handoff
from intentos.handoff import AgentHandoff


class CodexAdapterTests(unittest.TestCase):
    def packet(self, target="codex"):
        return AgentHandoff(1, "task", target, "abc", "Do the task", "execute", "0" * 64)

    def test_process_receipt_is_unverified_and_uses_bounded_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            def fake_run(command, **kwargs):
                self.assertEqual(command[:2], ["codex", "exec"])
                self.assertIn("--ephemeral", command)
                self.assertIn("--ignore-user-config", command)
                self.assertIn("read-only", command)
                self.assertNotIn("danger-full-access", command)
                self.assertEqual(kwargs["input"], b"Do the task")
                kwargs["stdout"].write((json.dumps({"type": "thread.started", "thread_id": "thread-1"}) + "\n" +
                                         json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "Inspected STATUS.md"}}) + "\n" +
                                         json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 3}}) + "\n").encode())
                return subprocess.CompletedProcess(command, 0)
            with patch("intentos.codex_adapter.subprocess.run", side_effect=fake_run):
                receipt = run_codex_handoff(self.packet(), root=Path(directory))
            self.assertEqual(receipt["status"], "completed_unverified")
            self.assertEqual(receipt["thread_id"], "thread-1")
            self.assertEqual(receipt["usage"]["input_tokens"], 10)
            self.assertEqual(receipt["final_message"], "Inspected STATUS.md")

    def test_unavailable_and_interrupted_are_not_reported_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("intentos.codex_adapter.subprocess.run", side_effect=FileNotFoundError()):
                self.assertEqual(run_codex_handoff(self.packet(), root=root)["status"], "unavailable")
            with patch("intentos.codex_adapter.subprocess.run", side_effect=subprocess.TimeoutExpired("codex", 1)):
                self.assertEqual(run_codex_handoff(self.packet(), root=root)["status"], "interrupted")
            self.assertEqual(run_codex_handoff(self.packet("claude-code"), root=root)["status"], "unavailable")

    def test_exit_zero_without_completed_turn_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("intentos.codex_adapter.subprocess.run", return_value=subprocess.CompletedProcess(["codex"], 0)):
                receipt = run_codex_handoff(self.packet(), root=Path(directory))
            self.assertEqual(receipt["status"], "failed")


if __name__ == "__main__":
    unittest.main()

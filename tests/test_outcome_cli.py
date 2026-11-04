import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from intentos.cli import main


class OutcomeCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def source(self, task="task-1", variant="raw", *, passed=True, success=True,
               tokens=None, lesson="", context="same-context"):
        return {
            "schema_version": 1, "task_id": task, "variant": variant,
            "conditions": {
                "executor": "Codex CLI", "model": "caller-pinned-model", "effort": "high",
                "base_revision": "base-123", "context": context,
                "permissions": "read-only", "environment": "same-test-env",
            },
            "checks": [{"name": "focused tests", "passed": passed,
                        "evidence_ref": "CI #12" if passed is not None else ""}],
            "execution_success": success,
            "metrics": {"input_tokens": tokens},
            "source_ref": f"issue #{task}-{variant}",
            "friction": "", "rework": "", "context_gap": "", "verification_gap": "",
            "lesson_hint": lesson,
        }

    def write(self, name, data):
        path = self.root / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def call(self, *args):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["outcome", *args, "--json"])
        return code, json.loads(output.getvalue())

    def record(self, name, data):
        source = self.write(f"{name}.input.json", data)
        output = self.root / f"{name}.record.json"
        code, result = self.call("record", "--file", str(source), "--output", str(output))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["status"], "recorded")
        return output

    def test_pair_uses_existing_correctness_first_comparison_and_missing_metrics_stay_null(self):
        raw = self.record("raw", self.source(passed=False, success=False, tokens=100))
        prepared = self.record("prepared", self.source(variant="prepared", tokens=200))
        code, result = self.call("compare", "--raw", str(raw), "--prepared", str(prepared))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "prepared")
        self.assertEqual(result["comparison"]["winner"], "prepared")
        self.assertEqual(result["comparison"]["input_tokens_delta"], 100)
        self.assertIsNone(result["comparison"]["output_tokens_delta"])
        self.assertIsNone(result["comparison"]["total_tokens_delta"])
        self.assertEqual(result["source_refs"]["raw"], "issue #task-1-raw")

    def test_changed_conditions_or_unverified_check_is_inconclusive(self):
        raw = self.record("raw", self.source())
        prepared = self.record("prepared", self.source(variant="prepared", context="different"))
        code, result = self.call("compare", "--raw", str(raw), "--prepared", str(prepared))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "inconclusive")
        prepared.write_text(json.dumps(self.source(variant="prepared", passed=None, success=None)), encoding="utf-8")
        code, result = self.call("compare", "--raw", str(raw), "--prepared", str(prepared))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "inconclusive")
        self.assertIn("unverified", result["reason"])

    def test_record_rejects_fabricated_or_unbounded_measure(self):
        data = self.source()
        data["metrics"]["input_tokens"] = "about 100"
        source = self.write("bad.json", data)
        code, result = self.call("record", "--file", str(source), "--output", str(self.root / "record.json"))
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "error")
        data = self.source()
        data["variant"] = []
        source.write_text(json.dumps(data), encoding="utf-8")
        code, result = self.call("record", "--file", str(source), "--output", str(self.root / "record.json"))
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "error")
        self.assertFalse((self.root / "record.json").exists())
        data = self.source(passed=None)
        data["checks"][0]["passed"] = True
        data["checks"][0]["evidence_ref"] = ""
        source.write_text(json.dumps(data), encoding="utf-8")
        code, result = self.call("record", "--file", str(source), "--output", str(self.root / "record.json"))
        self.assertEqual(code, 2)

    def test_learning_needs_distinct_failed_tasks_and_exact_approval(self):
        first = self.record("first", self.source(task="task-1", passed=False, success=False,
                                                  lesson="Preserve migration rollback steps"))
        code, result = self.call("learn", "--record", str(first))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "insufficient_repeated_evidence")
        duplicate = self.record("duplicate", self.source(task="task-1", variant="prepared", passed=False,
                                                          success=False, lesson="Preserve migration rollback steps"))
        code, result = self.call("learn", "--record", str(first), "--record", str(duplicate))
        self.assertEqual(result["status"], "insufficient_repeated_evidence")
        second = self.record("second", self.source(task="task-2", passed=False, success=False,
                                                    lesson="Preserve migration rollback steps"))
        args = ("learn", "--record", str(first), "--record", str(second))
        code, proposal = self.call(*args)
        self.assertEqual(proposal["status"], "proposal")
        self.assertEqual(proposal["proposals"][0]["evidence_cases"], ["task-1", "task-2"])
        self.assertFalse(proposal["runtime_policy_changed"])
        approved = self.root / "approved.json"
        code, rejected = self.call(*args, "--approve-digest", "0" * 64,
                                   "--approval-ref", "owner #7", "--output", str(approved))
        self.assertEqual(code, 2)
        self.assertFalse(approved.exists())
        code, saved = self.call(*args, "--approve-digest", proposal["approval_digest"],
                                "--approval-ref", "owner #7", "--output", str(approved))
        self.assertEqual(code, 0)
        self.assertEqual(saved["status"], "approved_proposal")
        content = json.loads(approved.read_text(encoding="utf-8"))
        self.assertFalse(content["runtime_policy_changed"])
        self.assertEqual(content["approval_ref"], "owner #7")


if __name__ == "__main__":
    unittest.main()

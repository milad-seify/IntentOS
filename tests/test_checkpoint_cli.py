import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CheckpointCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "docs").mkdir()
        self.context = self.root / "docs" / "STATUS.md"
        self.context.write_text("Current phase: implementation\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("add", "docs/STATUS.md")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "base")
        self.revision = self.git("rev-parse", "HEAD").stdout.strip()
        self.spec = self.root / "spec.json"
        self.spec.write_text(json.dumps({
            "task_id": "task-1", "next_step_id": "verify", "approved_plan": [
                {"step_id": "build", "action": "Build the change"},
                {"step_id": "verify", "action": "Verify the change"},
            ],
            "plan_approval_ref": "owner review #7",
            "state_summary": "Implementation awaits verification",
            "state_evidence_ref": "docs/STATUS.md at base",
            "completed": [{"step_id": "build", "evidence_ref": "CI #8", "accepted_by_owner": True}],
            "operation_ids": ["publish-1"],
            "required_approval_ids": ["owner-release"],
            "estimated_remaining_tokens": 1200,
        }), encoding="utf-8")
        self.checkpoint = self.root / "checkpoint.json"

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def cli(self, action, *args):
        result = subprocess.run([
            sys.executable, "-m", "intentos", "checkpoint", action,
            "--root", str(self.root), "--context-file", "docs/STATUS.md",
            *args, "--json",
        ], cwd=self.root, text=True, capture_output=True)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"CLI did not produce JSON: {result.stdout}\n{result.stderr}")
        return result.returncode, payload

    def create(self):
        return self.cli("create", "--spec", str(self.spec), "--output", str(self.checkpoint))

    def review(self, *args):
        return self.cli("review", "--checkpoint", str(self.checkpoint), *args)

    def test_cross_process_checkpoint_and_review(self):
        code, created = self.create()
        self.assertEqual(code, 0)
        self.assertEqual(created["status"], "saved")
        saved = json.loads(self.checkpoint.read_text(encoding="utf-8"))
        self.assertEqual(saved["source_revision"], self.revision)
        self.assertEqual(saved["approved_plan"][1]["step_id"], "verify")
        self.assertNotIn("Current phase: implementation", self.checkpoint.read_text(encoding="utf-8"))
        code, reviewed = self.review("--ledger-reviewed", "--accepted-approval", "owner-release")
        self.assertEqual(code, 0)
        self.assertEqual(reviewed["status"], "ready_for_owner_review")
        self.assertFalse(reviewed["approved_to_execute"])
        self.assertEqual(reviewed["next_step_id"], "verify")

    def test_changed_context_and_revision_block(self):
        self.create()
        self.context.write_text("Current phase: release\n", encoding="utf-8")
        code, review = self.review("--ledger-reviewed", "--accepted-approval", "owner-release")
        self.assertEqual(code, 2)
        self.assertIn("fingerprint", " ".join(review["reasons"]))
        self.git("add", "docs/STATUS.md")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "changed")
        code, review = self.review("--ledger-reviewed", "--accepted-approval", "owner-release")
        self.assertEqual(code, 2)
        self.assertIn("revision", " ".join(review["reasons"]))

    def test_replay_and_missing_approval_block(self):
        self.create()
        code, review = self.review("--ledger-reviewed", "--executed-operation", "publish-1", "--accepted-approval", "owner-release")
        self.assertEqual(code, 2)
        self.assertIn("replay", " ".join(review["reasons"]))
        code, review = self.review("--ledger-reviewed")
        self.assertEqual(code, 2)
        self.assertIn("approvals", " ".join(review["reasons"]))
        code, review = self.review("--accepted-approval", "owner-release")
        self.assertEqual(code, 2)
        self.assertIn("ledger", " ".join(review["reasons"]))

    def test_remaining_budget_is_visible_and_overrun_blocks(self):
        self.create()
        code, result = self.review("--ledger-reviewed", "--accepted-approval", "owner-release",
                                   "--remaining-budget-tokens", "100")
        self.assertEqual(code, 2)
        self.assertEqual(result["budget_status"], "estimate_over_budget")
        code, result = self.review("--ledger-reviewed", "--accepted-approval", "owner-release",
                                   "--remaining-budget-tokens", "2000")
        self.assertEqual(code, 0)
        self.assertEqual(result["budget_status"], "estimate_within_supplied_budget")

    def test_rejects_false_plan_and_will_not_overwrite(self):
        self.create()
        code, error = self.create()
        self.assertEqual(code, 2)
        self.assertEqual(error["status"], "error")
        self.spec.write_text(json.dumps({"task_id": "task-1", "next_step_id": "verify"}), encoding="utf-8")
        code, error = self.cli("create", "--spec", str(self.spec), "--output", str(self.root / "second.json"))
        self.assertEqual(code, 2)
        self.assertEqual(error["status"], "error")

    def test_malformed_step_is_a_bounded_error(self):
        spec = json.loads(self.spec.read_text(encoding="utf-8"))
        spec["approved_plan"][0]["action"] = 123
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        code, result = self.create()
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "error")
        self.assertFalse(self.checkpoint.exists())


if __name__ == "__main__":
    unittest.main()

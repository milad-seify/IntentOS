"""Synthetic developer access flow; it is not owner-led Phase 8 evidence."""
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from intentos.cli import main


class FullScopeAccessTests(unittest.TestCase):
    def test_existing_cli_lists_all_development_access_paths(self):
        help_text = subprocess.run([sys.executable, "-m", "intentos", "--help"],
                                   capture_output=True, text=True, check=True).stdout
        for command in ("optimize", "compass", "state", "gates", "route", "checkpoint", "handoff", "outcome"):
            self.assertIn(command, help_text)

    def test_delegation_governance_recovery_and_outcome_stay_reviewable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            docs = root / "docs"
            docs.mkdir(parents=True)
            (docs / "PLAN.md").write_text("## Project goal\nShip a safe API\n", encoding="utf-8")
            status = docs / "STATUS.md"
            status.write_text("## Current phase\nMVP\n\n## Next action\nReview API\n", encoding="utf-8")
            (docs / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
            scope = docs / "SCOPE.md"
            scope.write_text("## In Scope\n- Review API\n\n## Out of Scope\n- Add cache\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "docs"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                            "commit", "-qm", "base"], cwd=root, check=True)

            def call(*args, code=0):
                output = StringIO()
                with redirect_stdout(output):
                    actual_code = main([*args, "--json"])
                self.assertEqual(actual_code, code, output.getvalue())
                return json.loads(output.getvalue())

            task = ("Codex: Make demo checkout concurrency-safe so order creation atomically consumes "
                    "stock and concurrent checkouts cannot oversell inventory.")
            prepared = call("optimize", task, "--target", "codex", "--context-file", str(status))
            self.assertEqual(prepared["status"], "ready")
            self.assertEqual(prepared["risk_level"], "high")
            self.assertTrue(prepared["approval_boundaries"])
            self.assertTrue(prepared["done_criteria"])

            catalog = Path(directory) / "catalog.json"
            catalog.write_text(json.dumps({"schema_version": 1, "models": [{
                "name": "caller-model", "provider": "caller", "surfaces": ["codex"],
                "capability": "strong", "cost": "high", "available": True, "verified": True,
            }]}), encoding="utf-8")
            route = call("route", task, "--target", "codex", "--models-file", str(catalog))
            self.assertEqual(route["selected_model"], "caller-model")
            self.assertEqual(route["required_capability"], "strong")

            initial = call("compass", "--authoritative-document", str(docs / "PLAN.md"),
                           "--authoritative-document", str(scope), "--document", str(status),
                           "--task", "Add cache")
            self.assertEqual(initial["fields"]["goal"]["value"], "Ship a safe API")
            self.assertEqual(initial["task_scope"]["status"], "out_of_scope")
            state_args = ("state", "status", "--root", str(root), "--current-phase", "Implementation",
                          "--evidence", "owner-reviewed issue #1")
            state_preview = call(*state_args)
            self.assertEqual(call(*state_args, "--approve-digest", state_preview["approval_digest"])["status"], "applied")
            scope_args = ("state", "scope", "--root", str(root), "--amendment-id", "S-001",
                          "--task", "Add cache", "--reason", "Owner expanded scope",
                          "--approval-ref", "owner issue #2")
            scope_preview = call(*scope_args)
            self.assertEqual(call(*scope_args, "--approve-digest", scope_preview["approval_digest"])["status"], "applied")
            updated = call("compass", "--authoritative-document", str(docs / "PLAN.md"),
                           "--authoritative-document", str(scope), "--document", str(status),
                           "--task", "Add cache")
            self.assertEqual(updated["task_scope"]["status"], "in_scope")

            gates_file = Path(directory) / "gates.json"
            gates_file.write_text(json.dumps({"schema_version": 1, "requirements": [{
                "key": "R1", "outcome": "API verified", "checks": ["tests"],
                "accepted_by_owner": True, "approval_ref": "owner issue #2",
            }], "milestones": [{"key": "M1", "requirement_keys": ["R1"], "state": "approved",
                               "approval_ref": "owner issue #3"}], "evidence": [{
                "requirement_key": "R1", "check": "tests", "passed": True,
                "source_ref": "CI #4", "source_revision": "base", "independently_reviewed": True,
            }]}), encoding="utf-8")
            gates = call("gates", "--file", str(gates_file))
            self.assertEqual(gates["status"], "ready_for_owner_review")
            self.assertFalse(gates["launch_approved"])

            handoff = Path(directory) / "handoff.json"
            call("handoff", "prepare", task, "--root", str(root), "--target", "codex",
                 "--task-id", "task-1", "--context-file", "docs/STATUS.md", "--output", str(handoff))
            with patch("intentos.cli.run_codex_handoff") as executor:
                preview = call("handoff", "dispatch", "--root", str(root), "--file", str(handoff),
                               "--model", route["selected_model"])
                self.assertEqual(preview["status"], "approval_required")
                self.assertEqual(preview["requested_model"], "caller-model")
                executor.assert_not_called()
                denied = call("handoff", "dispatch", "--root", str(root), "--file", str(handoff),
                              "--sandbox", "workspace-write", code=2)
                self.assertIn("high-risk", denied["error"]["message"])

            spec = Path(directory) / "checkpoint-spec.json"
            spec.write_text(json.dumps({
                "task_id": "task-1", "next_step_id": "verify",
                "approved_plan": [{"step_id": "verify", "action": "Verify the safe API"}],
                "plan_approval_ref": "owner issue #3", "state_summary": "Implementation under review",
                "state_evidence_ref": "docs/STATUS.md", "required_approval_ids": ["owner-write"],
                "operation_ids": ["stock-write-1"],
            }), encoding="utf-8")
            checkpoint = Path(directory) / "checkpoint.json"
            call("checkpoint", "create", "--root", str(root), "--context-file", "docs/STATUS.md",
                 "--spec", str(spec), "--output", str(checkpoint))
            resume = call("checkpoint", "review", "--root", str(root), "--context-file", "docs/STATUS.md",
                          "--checkpoint", str(checkpoint), "--ledger-reviewed",
                          "--accepted-approval", "owner-write")
            self.assertEqual(resume["status"], "ready_for_owner_review")
            self.assertFalse(resume["approved_to_execute"])

            def outcome(variant, name):
                source = Path(directory) / f"{name}-input.json"
                saved = Path(directory) / f"{name}.json"
                source.write_text(json.dumps({
                    "schema_version": 1, "task_id": "task-1", "variant": variant,
                    "conditions": {"executor": "Codex", "model": "same", "effort": "high",
                                   "base_revision": "base", "context": "same", "permissions": "read-only",
                                   "environment": "same"},
                    "checks": [{"name": "focused tests", "passed": True, "evidence_ref": "CI #4"}],
                    "execution_success": True, "metrics": {}, "source_ref": f"issue #{name}",
                }), encoding="utf-8")
                call("outcome", "record", "--file", str(source), "--output", str(saved))
                return saved
            raw = outcome("raw", "raw")
            prepared_record = outcome("prepared", "prepared")
            comparison = call("outcome", "compare", "--raw", str(raw), "--prepared", str(prepared_record))
            self.assertEqual(comparison["status"], "inconclusive")
            self.assertIsNone(comparison["comparison"]["total_tokens_delta"])


if __name__ == "__main__":
    unittest.main()

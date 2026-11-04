"""Developer integration case; this synthetic fixture is not Phase 8 evidence."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ProjectGovernanceFlowTests(unittest.TestCase):
    def test_fresh_cli_processes_preserve_reviewed_project_continuity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            plan = docs / "PLAN.md"
            status = docs / "STATUS.md"
            decisions = docs / "DECISIONS.md"
            scope = docs / "SCOPE.md"
            plan.write_text("## Project goal\nShip an API\n", encoding="utf-8", newline="")
            status.write_text("## Current phase\nMVP\n\n## Next action\nReview API\n", encoding="utf-8", newline="")
            decisions.write_text("# Decisions\n\n## D-001 — Initial scope\n\nApproved.\n", encoding="utf-8", newline="")
            scope.write_text("## In Scope\n- Review API\n\n## Out of Scope\n- Add Redis cache\n", encoding="utf-8", newline="")

            def invoke(*arguments, expected_code=0):
                completed = subprocess.run(
                    [sys.executable, "-m", "intentos", *arguments, "--json"],
                    cwd=root, capture_output=True, text=True, encoding="utf-8", check=False,
                )
                self.assertEqual(completed.returncode, expected_code, completed.stderr + completed.stdout)
                return json.loads(completed.stdout)

            def compass():
                return invoke(
                    "compass", "--authoritative-document", str(plan),
                    "--authoritative-document", str(scope), "--document", str(status),
                    "--document", str(decisions), "--task", "Add Redis cache",
                )

            initial = compass()
            self.assertEqual(initial["fields"]["goal"]["value"], "Ship an API")
            self.assertEqual(initial["fields"]["current_phase"]["value"], "MVP")
            self.assertEqual(initial["task_scope"]["status"], "out_of_scope")

            phase_args = (
                "state", "status", "--root", str(root), "--current-phase", "Milestone 2",
                "--evidence", "owner-reviewed PR #12", "--related-document", str(plan),
            )
            phase_preview = invoke(*phase_args)
            self.assertEqual(status.read_text(encoding="utf-8").splitlines()[1], "MVP")
            self.assertEqual(invoke(*phase_args, "--approve-digest", phase_preview["approval_digest"])["status"], "applied")

            decision_args = (
                "state", "decision", "--root", str(root), "--decision-id", "D-002",
                "--title", "Owner approves milestone", "--body", "Verify before launch.",
                "--approval-ref", "owner issue #13",
            )
            decision_preview = invoke(*decision_args)
            self.assertEqual(invoke(*decision_args, "--approve-digest", decision_preview["approval_digest"])["status"], "applied")

            scope_args = (
                "state", "scope", "--root", str(root), "--amendment-id", "S-001",
                "--task", "Add Redis cache", "--reason", "Owner expanded scope",
                "--approval-ref", "owner issue #14",
            )
            scope_preview = invoke(*scope_args)
            self.assertEqual(invoke(*scope_args, "--approve-digest", scope_preview["approval_digest"])["status"], "applied")

            reopened = compass()
            self.assertEqual(reopened["fields"]["current_phase"]["value"], "Milestone 2")
            self.assertEqual(reopened["task_scope"]["status"], "in_scope")
            self.assertTrue(any("D-002" in fact["text"] for fact in reopened["fields"]["decisions"]["evidence"]))
            self.assertIn("S-001: Add Redis cache", scope.read_text(encoding="utf-8"))

            gates = root / "gates.json"
            data = {
                "schema_version": 1,
                "requirements": [{
                    "key": "R01", "outcome": "API passes build and security checks", "checks": ["build", "security"],
                    "accepted_by_owner": True, "approval_ref": "owner issue #13",
                }],
                "milestones": [{
                    "key": "M01", "requirement_keys": ["R01"], "state": "done", "approval_ref": "",
                }],
                "evidence": [{
                    "requirement_key": "R01", "check": "build", "passed": True,
                    "source_ref": "CI #12", "source_revision": "commit-123", "independently_reviewed": True,
                }],
            }
            gates.write_text(json.dumps(data), encoding="utf-8")
            incomplete = invoke("gates", "--file", str(gates), expected_code=2)
            self.assertEqual(incomplete["status"], "blocked")
            self.assertFalse(incomplete["launch_approved"])
            data["milestones"][0].update(state="approved", approval_ref="owner issue #15")
            data["evidence"].append({
                "requirement_key": "R01", "check": "security", "passed": True,
                "source_ref": "review #16", "source_revision": "commit-123", "independently_reviewed": True,
            })
            gates.write_text(json.dumps(data), encoding="utf-8")
            complete = invoke("gates", "--file", str(gates))
            self.assertEqual(complete["status"], "ready_for_owner_review")
            self.assertFalse(complete["launch_approved"])


if __name__ == "__main__":
    unittest.main()

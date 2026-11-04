import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from intentos.cli import main


BASE = {
    "schema_version": 1,
    "requirements": [
        {"key": "R01", "outcome": "Dashboard passes acceptance", "checks": ["build", "security"],
         "accepted_by_owner": True, "approval_ref": "owner issue #7"},
    ],
    "milestones": [
        {"key": "M01", "requirement_keys": ["R01"], "state": "approved", "approval_ref": "owner issue #8"},
    ],
    "evidence": [
        {"requirement_key": "R01", "check": "build", "passed": True,
         "source_ref": "CI #12", "source_revision": "commit-123", "independently_reviewed": True},
        {"requirement_key": "R01", "check": "security", "passed": True,
         "source_ref": "review #13", "source_revision": "commit-123", "independently_reviewed": True},
    ],
}


class GatesCliTests(unittest.TestCase):
    def run_review(self, data):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "gates.json"
            source.write_text(json.dumps(data), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main(["gates", "--file", str(source), "--json"])
            self.assertEqual(json.loads(source.read_text(encoding="utf-8")), data)
            return code, json.loads(output.getvalue())

    def test_reviewable_report_traces_approved_requirements_and_checks(self):
        code, report = self.run_review(BASE)
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "ready_for_owner_review")
        self.assertFalse(report["launch_approved"])
        self.assertEqual(report["milestones"][0]["requirement_keys"], ["R01"])
        self.assertEqual(report["requirements"][0]["checks"], ["build", "security"])
        self.assertEqual([f["status"] for f in report["findings"]], ["passed", "passed"])

    def test_proposed_and_done_milestones_do_not_claim_readiness(self):
        for state in ("proposed", "done", "verified"):
            with self.subTest(state=state):
                data = json.loads(json.dumps(BASE))
                data["milestones"][0]["state"] = state
                code, report = self.run_review(data)
                self.assertEqual(code, 2)
                self.assertNotEqual(report["status"], "ready_for_owner_review")
                self.assertFalse(report["launch_approved"])

    def test_missing_or_failed_verification_blocks_readiness(self):
        data = json.loads(json.dumps(BASE))
        data["evidence"][0]["passed"] = False
        code, report = self.run_review(data)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "blocked")
        data["evidence"].pop()
        code, report = self.run_review(data)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "blocked")

    def test_unaccepted_requirement_and_unreviewed_check_cannot_ready(self):
        data = json.loads(json.dumps(BASE))
        data["requirements"][0]["accepted_by_owner"] = False
        code, report = self.run_review(data)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "blocked")
        data = json.loads(json.dumps(BASE))
        data["evidence"][0]["independently_reviewed"] = False
        code, report = self.run_review(data)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "needs_review")

    def test_malformed_input_returns_structured_error(self):
        data = json.loads(json.dumps(BASE))
        data["schema_version"] = 2
        code, report = self.run_review(data)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "error")
        data = json.loads(json.dumps(BASE))
        data["evidence"][0]["passed"] = "yes"
        code, report = self.run_review(data)
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "error")


if __name__ == "__main__":
    unittest.main()

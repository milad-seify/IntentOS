import unittest

from intentos import ContextDocument
from intentos.governance import (
    CheckEvidence, Milestone, MilestoneRequirement, review_project_gates, review_scope_gate,
)


class GovernanceTests(unittest.TestCase):
    def test_scope_in_scope_still_requires_owner_approval_for_actions(self):
        scope = ContextDocument("docs/SCOPE.md", "## In Scope\n- Review API\n", authoritative=True)
        result = review_scope_gate((scope,), requested_task="Review API")
        self.assertEqual(result.status, "in_scope")
        self.assertTrue(result.requires_owner_approval)
        self.assertEqual(result.source_paths, ("docs/SCOPE.md",))

    def test_scope_out_of_scope_requires_amendment(self):
        scope = ContextDocument("docs/SCOPE.md", "## Out of Scope\n- Delete production database\n", authoritative=True)
        result = review_scope_gate((scope,), requested_task="Delete production database")
        self.assertEqual(result.status, "out_of_scope")
        self.assertTrue(result.requires_owner_approval)

    def test_unknown_or_conflicting_scope_never_approves(self):
        scope = ContextDocument("docs/SCOPE.md", "## In Scope\n- Review API\n")
        self.assertEqual(review_scope_gate((scope,), requested_task="Review API").status, "needs_review")
        self.assertEqual(review_scope_gate((scope,), requested_task="Deploy API").status, "needs_review")
        conflicting = (
            ContextDocument("docs/A.md", "## In Scope\n- Review API\n", authoritative=True),
            ContextDocument("docs/B.md", "## Out of Scope\n- Review API\n"),
        )
        self.assertEqual(review_scope_gate(conflicting, requested_task="Review API").status, "needs_review")

    def test_completed_checks_only_mean_ready_for_owner_review(self):
        requirements = (MilestoneRequirement("R01", "Publish dashboard", ("build", "security")),)
        milestone = (Milestone("M01", ("R01",)),)
        checks = (
            CheckEvidence("R01", "build", True, "CI run 1", "sha-1", True),
            CheckEvidence("R01", "security", True, "review 2", "sha-1", True),
        )
        r = review_project_gates(requirements, milestone, checks)
        self.assertEqual(r.status, "ready_for_owner_review")
        self.assertFalse(r.launch_approved)
        self.assertEqual([f.status for f in r.findings], ["passed", "passed"])

    def test_missing_or_failed_checks_block_launch(self):
        reqs = (MilestoneRequirement("R01", "Publish", ("build", "security")),)
        ms = (Milestone("M01", ("R01",)),)
        missing = review_project_gates(reqs, ms, (CheckEvidence("R01", "build", True, "CI", "sha", True),))
        self.assertEqual(missing.status, "blocked")
        failed = review_project_gates(reqs, ms, (
            CheckEvidence("R01", "build", True, "CI", "sha", True),
            CheckEvidence("R01", "security", False, "CI", "sha", True),
        ))
        self.assertEqual(failed.status, "blocked")

    def test_unverified_claim_cannot_be_promoted_to_verified(self):
        reqs = (MilestoneRequirement("R01", "Publish", ("build",)),)
        ms = (Milestone("M01", ("R01",)),)
        r = review_project_gates(reqs, ms, (CheckEvidence("R01", "build", True, "AI says done", "sha", False),))
        self.assertEqual(r.status, "needs_review")
        self.assertFalse(r.launch_approved)

    def test_orphan_requirement_is_blocked(self):
        reqs = (
            MilestoneRequirement("R01", "Publish", ("build",)),
            MilestoneRequirement("R02", "Audit", ("security",)),
        )
        ms = (Milestone("M01", ("R01",)),)
        checks = (
            CheckEvidence("R01", "build", True, "CI", "sha", True),
            CheckEvidence("R02", "security", True, "CI", "sha", True),
        )
        r = review_project_gates(reqs, ms, checks)
        self.assertEqual(r.status, "blocked")
        self.assertTrue(any(f.key == "R02" and f.status == "missing" for f in r.findings))

    def test_duplicate_conflicting_or_unsupported_evidence_needs_review(self):
        reqs = (MilestoneRequirement("R01", "Publish", ("build",)),)
        ms = (Milestone("M01", ("R01",)),)
        dup = (
            CheckEvidence("R01", "build", True, "CI1", "sha", True),
            CheckEvidence("R01", "build", False, "CI2", "sha", True),
        )
        self.assertEqual(review_project_gates(reqs, ms, dup).status, "needs_review")
        unsupported = (
            CheckEvidence("R01", "build", True, "CI1", "sha", True),
            CheckEvidence("R01", "security", True, "CI2", "sha", True),
        )
        self.assertEqual(review_project_gates(reqs, ms, unsupported).status, "needs_review")

    def test_empty_and_duplicate_milestones_cannot_ready(self):
        r = review_project_gates((), (), ())
        self.assertEqual(r.status, "blocked")
        reqs = (MilestoneRequirement("R01", "Publish", ("build",)),)
        with self.assertRaises(ValueError):
            review_project_gates(reqs, (Milestone("M01", ("R01",)), Milestone("M01", ("R01",))), ())

    def test_no_public_v1_api_expansion_yet(self):
        import intentos
        self.assertNotIn("review_project_gates", intentos.__all__)


if __name__ == "__main__":
    unittest.main()

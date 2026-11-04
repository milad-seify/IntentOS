import unittest

from intentos import ContextDocument
from intentos.governance import (
    CheckEvidence, Milestone, MilestoneRequirement, review_project_gates, review_scope_gate,
)


def accepted_requirement(key, outcome, checks):
    return MilestoneRequirement(key, outcome, checks, accepted_by_owner=True, approval_ref="owner issue #7")


def approved_milestone(key, requirement_keys):
    return Milestone(key, requirement_keys, state="approved", approval_ref="owner issue #8")


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
        requirements = (accepted_requirement("R01", "Publish dashboard", ("build", "security")),)
        milestone = (approved_milestone("M01", ("R01",)),)
        checks = (
            CheckEvidence("R01", "build", True, "CI run 1", "sha-1", True),
            CheckEvidence("R01", "security", True, "review 2", "sha-1", True),
        )
        r = review_project_gates(requirements, milestone, checks)
        self.assertEqual(r.status, "ready_for_owner_review")
        self.assertFalse(r.launch_approved)
        self.assertEqual([f.status for f in r.findings], ["passed", "passed"])

    def test_missing_or_failed_checks_block_launch(self):
        reqs = (accepted_requirement("R01", "Publish", ("build", "security")),)
        ms = (approved_milestone("M01", ("R01",)),)
        missing = review_project_gates(reqs, ms, (CheckEvidence("R01", "build", True, "CI", "sha", True),))
        self.assertEqual(missing.status, "blocked")
        failed = review_project_gates(reqs, ms, (
            CheckEvidence("R01", "build", True, "CI", "sha", True),
            CheckEvidence("R01", "security", False, "CI", "sha", True),
        ))
        self.assertEqual(failed.status, "blocked")

    def test_unverified_claim_cannot_be_promoted_to_verified(self):
        reqs = (accepted_requirement("R01", "Publish", ("build",)),)
        ms = (approved_milestone("M01", ("R01",)),)
        r = review_project_gates(reqs, ms, (CheckEvidence("R01", "build", True, "AI says done", "sha", False),))
        self.assertEqual(r.status, "needs_review")
        self.assertFalse(r.launch_approved)

    def test_orphan_requirement_is_blocked(self):
        reqs = (
            accepted_requirement("R01", "Publish", ("build",)),
            accepted_requirement("R02", "Audit", ("security",)),
        )
        ms = (approved_milestone("M01", ("R01",)),)
        checks = (
            CheckEvidence("R01", "build", True, "CI", "sha", True),
            CheckEvidence("R02", "security", True, "CI", "sha", True),
        )
        r = review_project_gates(reqs, ms, checks)
        self.assertEqual(r.status, "blocked")
        self.assertTrue(any(f.key == "R02" and f.status == "missing" for f in r.findings))

    def test_duplicate_conflicting_or_unsupported_evidence_needs_review(self):
        reqs = (accepted_requirement("R01", "Publish", ("build",)),)
        ms = (approved_milestone("M01", ("R01",)),)
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
        reqs = (accepted_requirement("R01", "Publish", ("build",)),)
        with self.assertRaises(ValueError):
            review_project_gates(reqs, (approved_milestone("M01", ("R01",)), approved_milestone("M01", ("R01",))), ())

    def test_proposed_requirement_and_milestone_cannot_claim_readiness(self):
        check = (CheckEvidence("R01", "build", True, "CI #12", "commit-123", True),)
        proposed_req = (MilestoneRequirement("R01", "Publish", ("build",)),)
        approved = (approved_milestone("M01", ("R01",)),)
        self.assertEqual(review_project_gates(proposed_req, approved, check).status, "blocked")
        accepted = (accepted_requirement("R01", "Publish", ("build",)),)
        for state in ("proposed", "done", "verified"):
            with self.subTest(state=state):
                result = review_project_gates(accepted, (Milestone("M01", ("R01",), state),), check)
                self.assertNotEqual(result.status, "ready_for_owner_review")
                self.assertFalse(result.launch_approved)
        no_approval_ref = (Milestone("M01", ("R01",), "approved"),)
        self.assertEqual(review_project_gates(accepted, no_approval_ref, check).status, "needs_review")

    def test_invalid_or_empty_lifecycle_evidence_is_not_accepted(self):
        accepted = (accepted_requirement("R01", "Publish", ("build",)),)
        with self.assertRaisesRegex(ValueError, "milestone state"):
            review_project_gates(accepted, (Milestone("M01", ("R01",), "launched"),), ())
        misleading = (CheckEvidence("R01", "build", 1, "CI #12", "commit-123", True),)
        self.assertEqual(review_project_gates(accepted, (approved_milestone("M01", ("R01",)),), misleading).status, "needs_review")
        no_check = (accepted_requirement("R01", "Publish", ("",)),)
        self.assertEqual(review_project_gates(no_check, (approved_milestone("M01", ("R01",)),), ()).status, "blocked")

    def test_no_public_v1_api_expansion_yet(self):
        import intentos
        self.assertNotIn("review_project_gates", intentos.__all__)


if __name__ == "__main__":
    unittest.main()

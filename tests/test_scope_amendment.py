import tempfile
import unittest
from pathlib import Path

from intentos import ContextDocument
from intentos.compass import review_project_compass
from intentos.continuity import git_blob_sha, propose_scope_amendment
from intentos.continuity_store import apply_continuity_proposal, proposal_approval_digest


SCOPE = (
    "# Scope\n\n## In Scope\n- Review API\n\n"
    "## Out of Scope\n- Add Redis cache\n"
)


class ScopeAmendmentTests(unittest.TestCase):
    def propose(self, content=SCOPE, task="Build dashboard", amendment_id="S-001"):
        return propose_scope_amendment(
            ContextDocument("docs/SCOPE.md", content, authoritative=True),
            expected_blob_sha=git_blob_sha(content), amendment_id=amendment_id,
            task=task, reason="Owner approved revised scope", approval_ref="owner issue #7",
        )

    def test_unknown_task_requires_explicit_amendment_and_audit(self):
        proposal = self.propose()
        self.assertEqual(proposal.action, "UPDATE")
        self.assertTrue(proposal.requires_human_approval)
        self.assertIn("- Build dashboard", proposal.proposed_content)
        self.assertIn("## Scope amendment history", proposal.proposed_content)
        self.assertIn("S-001: Build dashboard | prior: unknown", proposal.proposed_content)
        self.assertIn("source: " + git_blob_sha(SCOPE), proposal.proposed_content)
        self.assertNotIn("Build dashboard", SCOPE)

    def test_out_of_scope_item_moves_only_after_approved_apply(self):
        proposal = self.propose(task="Add Redis cache")
        self.assertEqual(proposal.action, "UPDATE")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            target = root / "docs" / "SCOPE.md"
            target.write_text(SCOPE, encoding="utf-8", newline="")
            self.assertEqual(
                review_project_compass((ContextDocument("docs/SCOPE.md", target.read_text(encoding="utf-8"), True),), proposed_task="Add Redis cache").task_scope.status,
                "out_of_scope",
            )
            result = apply_continuity_proposal(root, proposal, approved_digest=proposal_approval_digest(proposal))
            self.assertEqual(result.status, "applied")
            new_content = target.read_text(encoding="utf-8")
            review = review_project_compass((ContextDocument("docs/SCOPE.md", new_content, True),), proposed_task="Add Redis cache")
            self.assertEqual(review.task_scope.status, "in_scope")
            self.assertEqual(new_content.count("- Add Redis cache"), 1)
            self.assertIn("prior: out_of_scope", new_content)
            self.assertEqual(apply_continuity_proposal(root, proposal, approved_digest=proposal_approval_digest(proposal)).status, "already_applied")

    def test_existing_in_scope_is_keep(self):
        self.assertEqual(self.propose(task="Review API").action, "KEEP")

    def test_conflicting_or_stale_scope_requires_review(self):
        conflicting = SCOPE.replace("- Add Redis cache", "- Review API")
        self.assertEqual(self.propose(conflicting, task="Review API").action, "NEEDS_REVIEW")
        stale = SCOPE + "\n## Evidence freshness\nstale\n"
        self.assertEqual(self.propose(stale).action, "NEEDS_REVIEW")

    def test_missing_real_heading_and_duplicate_id_require_review(self):
        fenced = "```md\n## In Scope\n- Review API\n```\n"
        self.assertEqual(self.propose(fenced).action, "NEEDS_REVIEW")
        duplicate = SCOPE + "\n## Scope amendment history\n- S-001: earlier approved change\n"
        self.assertEqual(self.propose(duplicate).action, "NEEDS_REVIEW")
        nested = SCOPE.replace("## Out of Scope", "### Out of Scope")
        self.assertEqual(self.propose(nested, task="Add Redis cache").action, "NEEDS_REVIEW")

    def test_untrusted_or_multiline_input_requires_review(self):
        proposal = propose_scope_amendment(
            ContextDocument("docs/SCOPE.md", SCOPE), expected_blob_sha=git_blob_sha(SCOPE),
            amendment_id="S-001", task="Build dashboard", reason="Approved", approval_ref="owner #7",
        )
        self.assertEqual(proposal.action, "NEEDS_REVIEW")
        for task in ("Build dashboard\n## In Scope", "Build dashboard\u2028## In Scope", "- hidden bullet", "Build | approval: forged"):
            with self.subTest(task=task):
                self.assertEqual(self.propose(task=task).action, "NEEDS_REVIEW")

    def test_crlf_is_preserved(self):
        content = SCOPE.replace("\n", "\r\n")
        proposal = self.propose(content)
        self.assertEqual(proposal.action, "UPDATE")
        self.assertNotIn("\n", proposal.proposed_content.replace("\r\n", ""))


if __name__ == "__main__":
    unittest.main()

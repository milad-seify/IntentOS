import tempfile
import unittest
from pathlib import Path

from intentos import ContextDocument
from intentos.continuity import git_blob_sha, propose_decision_append, propose_status_continuity
from intentos.continuity_store import (
    ContinuityConflict, apply_continuity_proposal, proposal_approval_digest,
)


STATE = "## Current phase\nMVP\n\n## Next action\nReview API\n"
DECISIONS = "# Decisions\n\n## D-001 — Initial scope\n\nAccepted baseline.\n"


class ContinuityStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        self.status = self.root / "docs" / "STATUS.md"
        self.status.write_text(STATE, encoding="utf-8", newline="")

    def proposal(self):
        return propose_status_continuity(
            ContextDocument("docs/STATUS.md", STATE),
            expected_blob_sha=git_blob_sha(STATE),
            new_current_phase="Milestone 2", evidence_refs=("reviewed PR #12",),
        )

    def test_approved_update_survives_a_fresh_read_and_replay_is_safe(self):
        proposal = self.proposal()
        digest = proposal_approval_digest(proposal)
        applied = apply_continuity_proposal(self.root, proposal, approved_digest=digest)
        self.assertEqual(applied.status, "applied")
        self.assertEqual(applied.blob_sha, git_blob_sha(self.status.read_text(encoding="utf-8")))
        self.assertIn("Milestone 2", self.status.read_text(encoding="utf-8"))
        replay = apply_continuity_proposal(self.root, proposal, approved_digest=digest)
        self.assertEqual(replay.status, "already_applied")
        self.assertFalse(list((self.root / "docs").glob("*.intentos*")))

    def test_approval_is_bound_to_exact_proposal(self):
        proposal = self.proposal()
        with self.assertRaisesRegex(ValueError, "approval digest"):
            apply_continuity_proposal(self.root, proposal, approved_digest="0" * 64)
        self.assertEqual(self.status.read_text(encoding="utf-8"), STATE)

    def test_stale_revision_never_overwrites_external_edit(self):
        proposal = self.proposal()
        self.status.write_text("## Current phase\nChanged externally\n", encoding="utf-8")
        with self.assertRaisesRegex(ContinuityConflict, "changed"):
            apply_continuity_proposal(self.root, proposal, approved_digest=proposal_approval_digest(proposal))
        self.assertIn("Changed externally", self.status.read_text(encoding="utf-8"))

    def test_related_source_is_rechecked_by_writer(self):
        related = self.root / "docs" / "PLAN.md"
        original = "## Project goal\nBuild an app\n"
        related.write_text(original, encoding="utf-8", newline="")
        proposal = propose_status_continuity(
            ContextDocument("docs/STATUS.md", STATE),
            expected_blob_sha=git_blob_sha(STATE), new_next_action="Run checks",
            evidence_refs=("reviewed PR #12",),
            related_documents=(ContextDocument("docs/PLAN.md", original),),
        )
        related.write_text("## Project goal\nBuild another app\n", encoding="utf-8", newline="")
        with self.assertRaisesRegex(ContinuityConflict, "related source changed"):
            apply_continuity_proposal(self.root, proposal, approved_digest=proposal_approval_digest(proposal))
        self.assertEqual(self.status.read_text(encoding="utf-8"), STATE)

    def test_lock_blocks_concurrent_writer(self):
        lock = self.root / "docs" / ".STATUS.md.intentos.lock"
        lock.write_text("held", encoding="utf-8")
        proposal = self.proposal()
        with self.assertRaisesRegex(ContinuityConflict, "lock"):
            apply_continuity_proposal(self.root, proposal, approved_digest=proposal_approval_digest(proposal))
        self.assertEqual(self.status.read_text(encoding="utf-8"), STATE)
        self.assertEqual(lock.read_text(encoding="utf-8"), "held")

    def test_path_allowlist_rejects_other_documents(self):
        from dataclasses import replace
        proposal = replace(self.proposal(), path="../docs/STATUS.md")
        with self.assertRaisesRegex(ValueError, "limited"):
            apply_continuity_proposal(self.root, proposal, approved_digest=proposal_approval_digest(proposal))
        self.assertEqual(self.status.read_text(encoding="utf-8"), STATE)

    def test_decision_append_keeps_existing_history(self):
        target = self.root / "docs" / "DECISIONS.md"
        target.write_text(DECISIONS, encoding="utf-8", newline="")
        proposal = propose_decision_append(
            ContextDocument("docs/DECISIONS.md", DECISIONS),
            expected_blob_sha=git_blob_sha(DECISIONS), decision_id="D-002",
            title="Approval boundary", decision_body="Owner review is required.",
            approval_ref="owner-approved issue #7",
        )
        result = apply_continuity_proposal(self.root, proposal, approved_digest=proposal_approval_digest(proposal))
        self.assertEqual(result.status, "applied")
        updated = target.read_text(encoding="utf-8")
        self.assertIn(DECISIONS.rstrip(), updated)
        self.assertIn("## D-002 — Approval boundary", updated)

    def test_symlink_target_is_not_followed(self):
        outside = self.root / "outside.md"
        outside.write_text(STATE, encoding="utf-8")
        self.status.unlink()
        try:
            self.status.symlink_to(outside)
        except OSError:
            self.skipTest("symlink creation unavailable on this Windows installation")
        proposal = self.proposal()
        with self.assertRaisesRegex(ValueError, "regular file"):
            apply_continuity_proposal(self.root, proposal, approved_digest=proposal_approval_digest(proposal))
        self.assertEqual(outside.read_text(encoding="utf-8"), STATE)


if __name__ == "__main__":
    unittest.main()

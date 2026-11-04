import unittest

from intentos import ContextDocument
from intentos.continuity import git_blob_sha, propose_decision_append, propose_status_continuity


STATE = "## Current phase\nMVP\n\n## Next action\nReview user flow\n\n## Completed\n- Foundation\n"
DECISIONS = "# Decisions\n\n## D-001 — Initial scope\n\nAccepted baseline.\n"


def sha(text):
    return git_blob_sha(text)


class ContinuityProposalTests(unittest.TestCase):
    def test_status_update_has_exact_revision_and_is_review_only(self):
        doc = ContextDocument("docs/STATUS.md", STATE, authoritative=True)
        p = propose_status_continuity(
            doc, expected_blob_sha=sha(STATE),
            new_current_phase="Milestone 2", new_next_action="Run integration tests",
            evidence_refs=("reviewed PR #12 and CI #22",),
        )
        self.assertEqual(p.action, "UPDATE")
        self.assertTrue(p.requires_human_approval)
        self.assertEqual(p.expected_blob_sha, sha(STATE))
        self.assertIn("## Current phase\nMilestone 2\n", p.proposed_content)
        self.assertIn("## Next action\nRun integration tests\n", p.proposed_content)
        self.assertIn("## Completed\n- Foundation", p.proposed_content)
        self.assertEqual(doc.content, STATE)  # no mutation
        self.assertEqual(p.evidence_refs, ("reviewed PR #12 and CI #22",))

    def test_replay_is_keep(self):
        doc = ContextDocument("docs/STATUS.md", STATE, authoritative=True)
        p = propose_status_continuity(
            doc, expected_blob_sha=sha(STATE),
            new_current_phase="MVP", evidence_refs=("PR #12",),
        )
        self.assertEqual(p.action, "KEEP")
        self.assertIsNone(p.proposed_content)

    def test_stale_expected_revision_never_updates(self):
        doc = ContextDocument("docs/STATUS.md", STATE, authoritative=True)
        p = propose_status_continuity(
            doc, expected_blob_sha="0" * 40,
            new_current_phase="Milestone 2", evidence_refs=("PR #12",),
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")
        self.assertIsNone(p.proposed_content)

    def test_missing_evidence_cannot_propose_update(self):
        p = propose_status_continuity(
            ContextDocument("docs/STATUS.md", STATE),
            expected_blob_sha=sha(STATE),
            new_current_phase="Done",
            evidence_refs=(),
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")

    def test_conflicting_phase_is_never_silently_resolved(self):
        doc = ContextDocument("docs/STATUS.md", STATE, authoritative=True)
        other = ContextDocument("docs/OTHER.md", "## Current phase\nOther phase\n")
        p = propose_status_continuity(
            doc, expected_blob_sha=sha(STATE),
            new_current_phase="Milestone 2", evidence_refs=("PR #12",),
            related_documents=(other,),
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")
        self.assertIn("conflict", p.reasons[0])

    def test_explicit_stale_document_cannot_authorize_update(self):
        content = STATE + "\n## Evidence freshness\nstale\n"
        doc = ContextDocument("docs/STATUS.md", content)
        p = propose_status_continuity(
            doc, expected_blob_sha=sha(content),
            new_current_phase="Milestone 2", evidence_refs=("PR #12",),
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")

    def test_multi_line_section_requires_manual_review(self):
        content = "## Current phase\nMVP\nSecond line still relevant\n\n## Next action\nVerify\n"
        doc = ContextDocument("docs/STATUS.md", content)
        p = propose_status_continuity(
            doc, expected_blob_sha=sha(content),
            new_current_phase="Complete", evidence_refs=("PR #12",),
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")
        self.assertIsNone(p.proposed_content)

    def test_missing_heading_requires_review(self):
        content = "## Current phase\nMVP\n"
        p = propose_status_continuity(
            ContextDocument("docs/STATUS.md", content),
            expected_blob_sha=sha(content),
            new_next_action="Verify", evidence_refs=("PR #12",),
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")

    def test_markdown_injection_is_not_accepted_as_status(self):
        doc = ContextDocument("docs/STATUS.md", STATE)
        for phase in ("## Released", "Valid\n## Unauthorized", "- bypass"):
            with self.subTest(phase=phase):
                p = propose_status_continuity(
                    doc, expected_blob_sha=sha(STATE),
                    new_current_phase=phase, evidence_refs=("PR #12",),
                )
                self.assertEqual(p.action, "NEEDS_REVIEW")

    def test_bad_related_paths_rejected(self):
        doc = ContextDocument("docs/STATUS.md", STATE)
        p = propose_status_continuity(
            doc, expected_blob_sha=sha(STATE),
            new_current_phase="Milestone 2", evidence_refs=("PR #12",),
            related_documents=(ContextDocument("DOCS\\status.md", STATE),),
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")

    def test_accepts_crlf_without_reformatting(self):
        content = STATE.replace("\n", "\r\n")
        p = propose_status_continuity(
            ContextDocument("docs/STATUS.md", content),
            expected_blob_sha=sha(content),
            new_current_phase="Milestone 2", evidence_refs=("PR #12",),
        )
        self.assertEqual(p.action, "UPDATE")
        self.assertEqual(p.proposed_content.count("\r\n"), content.count("\r\n"))

    def test_decision_append_preserves_existing_records(self):
        doc = ContextDocument("docs/DECISIONS.md", DECISIONS)
        p = propose_decision_append(
            doc, expected_blob_sha=sha(DECISIONS), decision_id="D-002",
            title="Review only", decision_body="Require approval before mutation.",
            approval_ref="owner-approved issue #7",
        )
        self.assertEqual(p.action, "UPDATE")
        self.assertIn(DECISIONS.rstrip(), p.proposed_content)
        self.assertIn("## D-002 — Review only", p.proposed_content)
        self.assertIn("owner-approved issue #7", p.proposed_content)
        self.assertEqual(doc.content, DECISIONS)

    def test_duplicate_decision_is_keep_without_overwriting(self):
        p = propose_decision_append(
            ContextDocument("docs/DECISIONS.md", DECISIONS),
            expected_blob_sha=sha(DECISIONS), decision_id="D-001",
            title="Rewrite history", decision_body="Overwrite the old decision",
            approval_ref="owner-approved issue #7",
        )
        self.assertEqual(p.action, "KEEP")
        self.assertIsNone(p.proposed_content)

    def test_decision_requires_approved_evidence(self):
        p = propose_decision_append(
            ContextDocument("docs/DECISIONS.md", DECISIONS),
            expected_blob_sha=sha(DECISIONS), decision_id="D-003",
            title="New milestone", decision_body="Ready to launch.",
            approval_ref="",
        )
        self.assertEqual(p.action, "NEEDS_REVIEW")

    def test_no_public_v1_api_export(self):
        import intentos
        self.assertNotIn("propose_status_continuity", intentos.__all__)
        self.assertNotIn("propose_decision_append", intentos.__all__)


if __name__ == "__main__":
    unittest.main()

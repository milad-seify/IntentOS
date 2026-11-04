import unittest

from intentos.handoff import (
    VerifiedStep, build_agent_handoff, make_checkpoint, review_resume,
)
from intentos.models import NormalizedIntent, PromptResult


class HandoffCheckpointTests(unittest.TestCase):
    def checkpoint(self):
        return make_checkpoint(
            task_id="TASK-1", source_revision="commit-123", next_step_id="deploy-review",
            completed=(VerifiedStep("build", "CI #12", True),),
            operation_ids=("migration-1",), required_approval_ids=("owner-production-approval",),
            context_text="Pinned status and constraints",
            estimated_remaining_tokens=1200,
        )

    def test_checkpoint_is_deterministic_versioned_and_digest_not_raw_context(self):
        cp = self.checkpoint()
        self.assertEqual(cp.schema_version, 1)
        self.assertEqual(len(cp.context_digest), 64)
        self.assertNotIn("Pinned status", str(cp))
        self.assertEqual(cp, self.checkpoint())

    def test_resume_matches_but_never_self_approves_execution(self):
        cp = self.checkpoint()
        result = review_resume(
            cp, current_source_revision="commit-123",
            externally_accepted_approval_ids=("owner-production-approval",),
            current_context_digest=cp.context_digest,
        )
        self.assertEqual(result.status, "ready_for_owner_review")
        self.assertFalse(result.approved_to_execute)
        self.assertEqual(result.next_step_id, "deploy-review")

    def test_changed_revision_or_context_blocks_resume(self):
        cp = self.checkpoint()
        changed = review_resume(cp, current_source_revision="commit-124")
        self.assertEqual(changed.status, "blocked")
        self.assertIn("revision", " ".join(changed.reasons).lower())
        changed_context = review_resume(
            cp, current_source_revision="commit-123",
            current_context_digest="0" * 64,
        )
        self.assertEqual(changed_context.status, "blocked")

    def test_duplicate_external_operation_blocks_retry(self):
        cp = self.checkpoint()
        r = review_resume(
            cp, current_source_revision="commit-123",
            already_executed_operation_ids=("migration-1",),
            externally_accepted_approval_ids=("owner-production-approval",),
        )
        self.assertEqual(r.status, "blocked")
        self.assertIn("replay", " ".join(r.reasons).lower())

    def test_missing_external_approval_blocks_resume(self):
        cp = self.checkpoint()
        r = review_resume(cp, current_source_revision="commit-123")
        self.assertEqual(r.status, "blocked")
        self.assertFalse(r.approved_to_execute)

    def test_unreviewed_completed_steps_cannot_be_checkpointed(self):
        with self.assertRaises(ValueError):
            make_checkpoint(task_id="task", source_revision="sha", next_step_id="next",
                            completed=(VerifiedStep("step", "agent said done", False),))
        with self.assertRaises(ValueError):
            make_checkpoint(task_id="task", source_revision="sha", next_step_id="step",
                            completed=(VerifiedStep("step", "reviewed CI", True),))

    def test_duplicate_operation_and_invalid_token_guarantee_rejected(self):
        with self.assertRaises(ValueError):
            make_checkpoint(task_id="task", source_revision="sha", next_step_id="next",
                            operation_ids=("op1", "op1"))
        with self.assertRaises(ValueError):
            make_checkpoint(task_id="task", source_revision="sha", next_step_id="next",
                            estimated_remaining_tokens=-1)

    def test_handoff_keeps_prepared_prompt_reviewable_and_no_execution(self):
        result = PromptResult(
            prompt="Review this patch, do not modify files.",
            intent=NormalizedIntent(goal="Review patch", target_tool="codex"),
        )
        packet = build_agent_handoff(result, self.checkpoint(), target_tool="codex")
        self.assertEqual(packet.schema_version, 1)
        self.assertTrue(packet.requires_owner_approval)
        self.assertEqual(packet.prepared_prompt, result.prompt)
        self.assertEqual(packet.to_dict()["next_step_id"], "deploy-review")

    def test_agent_mismatch_requires_reprepare(self):
        result = PromptResult(prompt="Do work", intent=NormalizedIntent(goal="Do work", target_tool="codex"))
        with self.assertRaises(ValueError):
            build_agent_handoff(result, self.checkpoint(), target_tool="claude-code")

    def test_unresolved_task_is_not_handed_off(self):
        result = PromptResult(
            prompt=None, intent=NormalizedIntent(goal="Do work", target_tool="generic"),
            questions=("Which output?",),
        )
        with self.assertRaises(ValueError):
            build_agent_handoff(result, self.checkpoint(), target_tool="codex")

    def test_api_remains_internal_until_versioned_review(self):
        import intentos
        self.assertNotIn("build_agent_handoff", intentos.__all__)


if __name__ == "__main__":
    unittest.main()

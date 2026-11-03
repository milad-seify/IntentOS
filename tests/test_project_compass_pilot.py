import unittest

from intentos import ContextDocument
from intentos.compass import review_project_compass


GOALS = """## Project goal
Ship a minimal monitoring app.

## In Scope
- Build a read-only dashboard

## Out of Scope
- Add Redis cache

## Decisions
- No new infrastructure
"""
STATE = """## Current phase
Milestone 2

## Completed
- Milestone 1 with passing CI

## In Progress
- Dashboard wiring

## Blocked
- Provider credentials

## Deferred
- Advanced analytics

## Next action
Verify read-only dashboard
"""


class ProjectCompassPilotTests(unittest.TestCase):
    @staticmethod
    def docs():
        return (
            ContextDocument("docs/PLAN.md", GOALS, authoritative=True),
            ContextDocument("docs/STATUS.md", STATE, authoritative=True),
        )

    def test_grounded_project_state_and_source_paths(self):
        compass = review_project_compass(self.docs(), proposed_task="Build a read-only dashboard")
        self.assertEqual(compass.field("goal").value, "Ship a minimal monitoring app.")
        self.assertEqual(compass.field("current_phase").value, "Milestone 2")
        self.assertEqual(compass.field("next_action").value, "Verify read-only dashboard")
        self.assertEqual(compass.task_scope.status, "in_scope")
        self.assertFalse(compass.task_scope.approval_required)
        self.assertEqual(compass.field("completed").evidence[0].path, "docs/STATUS.md")
        self.assertEqual(compass.field("decisions").evidence[0].path, "docs/PLAN.md")
        self.assertGreater(compass.field("next_action").evidence[0].line, 0)

    def test_explicit_out_of_scope_requires_approval(self):
        review = review_project_compass(self.docs(), proposed_task="Add Redis cache")
        self.assertEqual(review.task_scope.status, "out_of_scope")
        self.assertTrue(review.task_scope.approval_required)
        self.assertEqual(review.task_scope.evidence[0].path, "docs/PLAN.md")

    def test_unmatched_or_similar_task_is_unknown_not_guessed(self):
        for task in ("Deploy Redis", "Build a dashboard", ""):
            with self.subTest(task=task):
                result = review_project_compass(self.docs(), proposed_task=task)
                self.assertEqual(result.task_scope.status, "unknown")
                self.assertTrue(result.task_scope.approval_required)

    def test_conflicting_phase_and_scope_preserve_evidence(self):
        docs = self.docs() + (
            ContextDocument(
                "docs/OTHER.md",
                "## Current phase\nMilestone 3\n\n## In Scope\n- Add Redis cache\n",
            ),
        )
        result = review_project_compass(docs, proposed_task="Add Redis cache")
        self.assertEqual(result.field("current_phase").status, "unresolved")
        self.assertIsNone(result.field("current_phase").value)
        self.assertEqual(len(result.field("current_phase").evidence), 2)
        self.assertEqual(result.task_scope.status, "conflicting")
        self.assertTrue(result.task_scope.approval_required)

    def test_different_worded_goals_are_unresolved_not_false_conflict(self):
        docs = (
            ContextDocument("AGENTS.md", "## 1. Mission\nBuild a secure organizational KPI dashboard.\n"),
            ContextDocument("docs/PRODUCT.md", "## Purpose\nDeliver trusted dashboards for managers.\n"),
        )
        result = review_project_compass(docs)
        self.assertEqual(result.field("goal").status, "unresolved")
        self.assertIsNone(result.field("goal").value)
        self.assertEqual({item.path for item in result.field("goal").evidence}, {"AGENTS.md", "docs/PRODUCT.md"})

    def test_stale_source_is_not_reported_as_accepted_phase(self):
        doc = ContextDocument(
            "docs/OLD.md",
            "## Evidence freshness\nstale\n\n## Current phase\nCompleted\n"
            "\n## Out of Scope\n- Add Redis cache\n",
        )
        result = review_project_compass((doc,), proposed_task="Add Redis cache")
        self.assertEqual(result.field("current_phase").status, "stale")
        self.assertIsNone(result.field("current_phase").value)
        self.assertEqual(result.task_scope.status, "unknown")

    def test_missing_next_action_remains_missing(self):
        result = review_project_compass((ContextDocument("PLAN.md", GOALS),))
        self.assertEqual(result.field("next_action").status, "missing")
        self.assertIsNone(result.field("next_action").value)

    def test_fresh_invocations_have_identical_outputs(self):
        first = review_project_compass(self.docs(), proposed_task="Add Redis cache")
        second = review_project_compass(self.docs(), proposed_task="Add Redis cache")
        self.assertEqual(first, second)

    def test_input_bounds_and_duplicate_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "too many"):
            review_project_compass(tuple(ContextDocument(str(n), "data") for n in range(33)))
        with self.assertRaisesRegex(ValueError, "36000"):
            review_project_compass((ContextDocument("too-long", "x" * 36001),))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            review_project_compass(
                (ContextDocument("docs/A.md", GOALS), ContextDocument("docs\\A.md", STATE))
            )


    def test_real_world_numbered_mission_and_product_scope_headings(self):
        # Representative excerpts from DSS-QFZ main at
        # 79e47b259e2372c9527bfce8ee8fbf7ae4e1b625.
        agent = ContextDocument(
            "AGENTS.md",
            "## 1. Mission\n"
            "Build DSS QFZ as a secure, maintainable organizational system.\n"
            "\n## 4. Architectural invariants\n- Do not add Redis without measured need.\n",
        )
        product = ContextDocument(
            "docs/PRODUCT.md",
            "## V1 outcomes\nV1 should provide:\n- responsive Persian RTL dashboards\n"
            "\n## V1 non-goals\nUnless scope is changed:\n- Redis/Celery/Kafka\n",
        )
        status = ContextDocument(
            "docs/STATUS.md",
            "## Current phase\n\n**Pre-5 Demo & Product Validation — IN PROGRESS.**\n\n"
            "- **Pre-5A — COMPLETE / MERGED:** synthetic demo.\n"
            "- **Pre-5C — IN PROGRESS:** integration PR.\n"
            "\n## Completed milestones\n- Phase 4D — COMPLETE / MERGED\n"
            "\n## Next action\nComplete PR #14 integration and exact-head CI.\n",
        )
        reviewed = review_project_compass((agent, product, status), proposed_task="Redis/Celery/Kafka")
        self.assertEqual(reviewed.field("goal").status, "known")
        self.assertEqual(reviewed.field("current_phase").value, "**Pre-5 Demo & Product Validation — IN PROGRESS.**")
        self.assertEqual(reviewed.field("completed").status, "known")
        self.assertEqual(reviewed.field("next_action").value, "Complete PR #14 integration and exact-head CI.")
        self.assertEqual(reviewed.task_scope.status, "out_of_scope")
        self.assertEqual(reviewed.task_scope.evidence[0].path, "docs/PRODUCT.md")
        # Deliberately no semantic inference for an unmatched phrase.
        uncertain = review_project_compass((agent, product, status), proposed_task="Add Redis cache")
        self.assertEqual(uncertain.task_scope.status, "unknown")
        self.assertTrue(uncertain.task_scope.approval_required)

    def test_current_phase_uses_first_paragraph_not_later_bullets(self):
        doc = ContextDocument(
            "docs/STATUS.md",
            "## Current phase\n\nPhase 7 complete, B1 pilot under review.\n\n"
            "- Phase 7A complete\n- Phase 8 deferred\n"
            "## Next\n\nReview B1 evidence before merge.\n"
        )
        result = review_project_compass((doc,))
        self.assertEqual(result.field("current_phase").value, "Phase 7 complete, B1 pilot under review.")
        self.assertEqual(result.field("next_action").value, "Review B1 evidence before merge.")

    def test_bounded_longer_real_project_docs_allowed_without_truncation(self):
        # The two real project document sets exceeded the pilot's original
        # 6000-character limit. This internal parser remains capped at 36000.
        large = ContextDocument(
            "docs/STATUS.md",
            "## Current phase\nMVP review\n\n## Completed milestones\n" + "- item\n" * 2300,
        )
        self.assertGreater(len(large.content), 6000)
        self.assertEqual(review_project_compass((large,)).field("current_phase").value, "MVP review")
        with self.assertRaisesRegex(ValueError, "36000"):
            review_project_compass((ContextDocument("too-long", "x" * 36001),))


if __name__ == "__main__":
    unittest.main()

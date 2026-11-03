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
        self.assertEqual(result.field("current_phase").status, "conflicting")
        self.assertIsNone(result.field("current_phase").value)
        self.assertEqual(len(result.field("current_phase").evidence), 2)
        self.assertEqual(result.task_scope.status, "conflicting")
        self.assertTrue(result.task_scope.approval_required)

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
        with self.assertRaisesRegex(ValueError, "6000"):
            review_project_compass((ContextDocument("too-long", "x" * 6001),))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            review_project_compass(
                (ContextDocument("docs/A.md", GOALS), ContextDocument("docs\\A.md", STATE))
            )


if __name__ == "__main__":
    unittest.main()

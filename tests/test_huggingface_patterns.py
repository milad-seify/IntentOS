import json
import unittest

from intentos import IntentRequest, optimize_prompt
from intentos.records import RunMetrics, build_run_record
from intentos.skills import build_skill_artifact


class HuggingFacePatternTests(unittest.TestCase):
    def test_skill_artifact_is_portable_and_reviewable(self) -> None:
        result = optimize_prompt(
            IntentRequest.from_values(
                "Refactor the auth module without changing behavior",
                target_tool="codex",
                constraints=("No new dependencies",),
                success_criteria=("Relevant tests pass",),
            )
        )

        self.assertFalse(result.needs_clarification)
        self.assertIsNotNone(result.policy)
        artifact = build_skill_artifact(result.intent, result.policy, name="Auth Refactor")

        self.assertEqual(artifact.name, "auth-refactor")
        self.assertTrue(artifact.content.startswith("---\nname: auth-refactor\n"))
        self.assertIn("## Engineering", artifact.content)
        self.assertIn("## Approval boundaries", artifact.content)
        self.assertIn("## Done", artifact.content)
        self.assertNotIn("selected_model", artifact.content)

    def test_run_record_is_versioned_and_does_not_store_raw_prompt(self) -> None:
        result = optimize_prompt(
            IntentRequest(
                "Deploy the service to production with Docker",
                target_tool="codex",
            )
        )
        record = build_run_record(
            result,
            context_paths=("AGENTS.md", "docs/STATUS.md", "AGENTS.md"),
            metrics=RunMetrics(
                success=True,
                quality_score=0.92,
                input_tokens=1200,
                output_tokens=240,
                latency_ms=1800,
                retries=1,
            ),
            tags=("dogfood", "docker", "dogfood"),
        )

        payload = json.loads(record.to_json())
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["context_paths"], ["AGENTS.md", "docs/STATUS.md"])
        self.assertEqual(payload["tags"], ["dogfood", "docker"])
        self.assertEqual(payload["metrics"]["success"], True)
        self.assertEqual(len(payload["prompt_sha256"]), 64)
        self.assertNotIn("Deploy the service", record.to_json())

    def test_clarification_record_has_no_prompt_hash(self) -> None:
        result = optimize_prompt(IntentRequest("Summarize this decision"))
        self.assertTrue(result.needs_clarification)

        record = build_run_record(result)
        self.assertIsNone(record.prompt_sha256)
        self.assertIsNone(record.task_type)


if __name__ == "__main__":
    unittest.main()

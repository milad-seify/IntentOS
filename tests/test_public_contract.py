from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

import intentos
from intentos import IntentRequest, RunMetrics, build_run_record, optimize_prompt
from intentos.records import RUN_RECORD_SCHEMA_VERSION
from intentos.result_contract import RESULT_SCHEMA_VERSION, result_dict


ROOT = Path(__file__).resolve().parents[1]


class PublicContractTests(unittest.TestCase):
    def test_documented_top_level_imports_are_the_explicit_exports(self) -> None:
        expected = {
            "CapabilityClass",
            "ContextDocument",
            "CostClass",
            "EffortLevel",
            "IntentRequest",
            "ModelMetadata",
            "PromptResult",
            "RunMetrics",
            "RunRecord",
            "SkillArtifact",
            "build_run_record",
            "build_skill_artifact",
            "optimize_project_prompt",
            "optimize_prompt",
            "plan_agent_workspace",
        }
        self.assertEqual(set(intentos.__all__), expected)
        self.assertTrue(all(hasattr(intentos, name) for name in expected))

    def test_distribution_metadata_preserves_public_import_and_commands(self) -> None:
        with (ROOT / "pyproject.toml").open("rb") as stream:
            metadata = tomllib.load(stream)
        project = metadata["project"]

        self.assertIn("setuptools>=77", metadata["build-system"]["requires"])
        self.assertEqual(project["name"], "intentos-engineering")
        self.assertEqual(project["version"], "1.0.0")
        self.assertEqual(project["license"], "MIT")
        self.assertEqual(project["urls"]["Repository"], "https://github.com/milad-seify/IntentOS")
        self.assertEqual(project["scripts"]["intentos"], "intentos.cli:main")
        self.assertEqual(project["scripts"]["intentos-mcp"], "intentos.mcp_server:main")
        self.assertIn("mcp", project["optional-dependencies"])

    def test_json_schema_v1_shape_and_context_paths_alias(self) -> None:
        result = optimize_prompt(
            IntentRequest.from_values(
                "Refactor the parser",
                target_tool="codex",
            )
        )
        payload = result_dict(result)

        self.assertEqual(RESULT_SCHEMA_VERSION, "1")
        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "status",
                "needs_clarification",
                "questions",
                "intent",
                "prompt",
                "task_type",
                "risk_level",
                "engineering_rules",
                "approval_boundaries",
                "done_criteria",
                "routing",
                "context",
                "context_paths",
            },
        )
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["context_paths"], payload["context"]["selected_paths"])

    def test_run_record_schema_v1_shape_stays_privacy_minimal(self) -> None:
        prompt = "Refactor a secret parser request"
        record = build_run_record(
            optimize_prompt(IntentRequest.from_values(prompt, target_tool="codex")),
            metrics=RunMetrics(success=True),
        )
        payload = record.to_dict()

        self.assertEqual(RUN_RECORD_SCHEMA_VERSION, "1")
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "intentos_version",
                "prompt_sha256",
                "target_tool",
                "task_type",
                "risk_level",
                "required_capability",
                "effort",
                "selected_model",
                "routing_fallback",
                "context_paths",
                "context_fingerprints",
                "metrics",
                "tags",
            },
        )
        self.assertNotIn(prompt, record.to_json())


if __name__ == "__main__":
    unittest.main()

import unittest

from intentos import (
    CapabilityClass,
    CostClass,
    IntentRequest,
    ModelMetadata,
    optimize_prompt,
)
from intentos.models import EffortLevel


class RoutingTests(unittest.TestCase):
    def test_low_risk_general_work_prefers_fast_low_cost_model(self) -> None:
        models = (
            ModelMetadata("fast-model", "example", ("chatgpt",), CapabilityClass.FAST, CostClass.LOW),
            ModelMetadata("strong-model", "example", ("chatgpt",), CapabilityClass.STRONG, CostClass.HIGH),
        )

        result = optimize_prompt(
            IntentRequest("Write a short announcement", target_tool="chatgpt"),
            models=models,
        )

        self.assertEqual(result.routing.required_capability, CapabilityClass.FAST)
        self.assertEqual(result.routing.effort, EffortLevel.LOW)
        self.assertEqual(result.routing.selected_model, "fast-model")

    def test_high_risk_security_work_requires_strong_capability(self) -> None:
        models = (
            ModelMetadata("balanced-model", "example", ("codex",), CapabilityClass.BALANCED, CostClass.LOW),
            ModelMetadata("strong-model", "example", ("codex",), CapabilityClass.STRONG, CostClass.MEDIUM),
        )

        result = optimize_prompt(
            IntentRequest("Change production authentication security", target_tool="codex"),
            models=models,
        )

        self.assertEqual(result.routing.required_capability, CapabilityClass.STRONG)
        self.assertEqual(result.routing.effort, EffortLevel.HIGH)
        self.assertEqual(result.routing.selected_model, "strong-model")

    def test_router_uses_fallback_without_model_metadata(self) -> None:
        result = optimize_prompt(
            IntentRequest("Refactor the parser", target_tool="codex")
        )

        self.assertTrue(result.routing.fallback)
        self.assertIsNone(result.routing.selected_model)
        self.assertEqual(result.routing.required_capability, CapabilityClass.BALANCED)

    def test_unavailable_or_wrong_surface_models_are_ignored(self) -> None:
        models = (
            ModelMetadata("unavailable", "example", ("codex",), CapabilityClass.STRONG, CostClass.LOW, available=False),
            ModelMetadata("wrong-surface", "example", ("chatgpt",), CapabilityClass.STRONG, CostClass.LOW),
        )

        result = optimize_prompt(
            IntentRequest("Design the system architecture", target_tool="codex"),
            models=models,
        )

        self.assertTrue(result.routing.fallback)
        self.assertIsNone(result.routing.selected_model)

    def test_verified_metadata_is_preferred_when_otherwise_equivalent(self) -> None:
        models = (
            ModelMetadata("unverified", "example", ("codex",), CapabilityClass.BALANCED, CostClass.LOW, verified=False),
            ModelMetadata("verified", "example", ("codex",), CapabilityClass.BALANCED, CostClass.LOW, verified=True),
        )

        result = optimize_prompt(
            IntentRequest("Refactor the parser", target_tool="codex"),
            models=models,
        )

        self.assertEqual(result.routing.selected_model, "verified")


if __name__ == "__main__":
    unittest.main()

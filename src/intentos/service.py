from __future__ import annotations

from dataclasses import replace

from .classifier import classify_task
from .compiler import compile_prompt
from .models import IntentRequest, ModelMetadata, PromptResult
from .normalize import normalize_intent
from .policies import build_execution_policy
from .router import recommend_route


def optimize_prompt(
    request: IntentRequest,
    *,
    models: tuple[ModelMetadata, ...] = (),
) -> PromptResult:
    """Normalize intent, classify risk, apply policy, route, and compile a target-aware prompt."""
    intent = normalize_intent(request)
    if not intent.is_ready:
        return compile_prompt(intent)

    task_type, risk_level = classify_task(intent)
    policy = build_execution_policy(intent, task_type, risk_level)
    routing = recommend_route(intent, policy, models)
    result = compile_prompt(intent, policy)
    return replace(result, routing=routing)

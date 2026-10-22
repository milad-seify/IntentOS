from __future__ import annotations

from .classifier import classify_task
from .compiler import compile_prompt
from .models import IntentRequest, PromptResult
from .normalize import normalize_intent
from .policies import build_execution_policy


def optimize_prompt(request: IntentRequest) -> PromptResult:
    """Normalize intent, classify risk, apply policy, and compile a target-aware prompt."""
    intent = normalize_intent(request)
    if not intent.is_ready:
        return compile_prompt(intent)

    task_type, risk_level = classify_task(intent)
    policy = build_execution_policy(intent, task_type, risk_level)
    return compile_prompt(intent, policy)

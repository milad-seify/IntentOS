from __future__ import annotations

from .compiler import compile_prompt
from .models import IntentRequest, PromptResult
from .normalize import normalize_intent


def optimize_prompt(request: IntentRequest) -> PromptResult:
    """Normalize rough intent and compile a target-aware execution prompt."""
    return compile_prompt(normalize_intent(request))

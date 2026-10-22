from __future__ import annotations

import re

from .models import Ambiguity, AmbiguitySeverity, IntentRequest, NormalizedIntent
from .profiles import detect_profile, resolve_profile


_WHITESPACE = re.compile(r"\s+")


def _clean(text: str | None) -> str | None:
    if text is None:
        return None
    value = _WHITESPACE.sub(" ", text).strip()
    return value or None


def _clean_many(values: tuple[str, ...]) -> tuple[str, ...]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean(value)
        if item and item.casefold() not in seen:
            cleaned.append(item)
            seen.add(item.casefold())
    return tuple(cleaned)


def normalize_intent(request: IntentRequest) -> NormalizedIntent:
    goal = _clean(request.raw_text) or ""
    ambiguities: list[Ambiguity] = []

    if not goal:
        ambiguities.append(
            Ambiguity(
                field="goal",
                question="What outcome do you want the AI to produce?",
                severity=AmbiguitySeverity.HIGH,
            )
        )

    explicit_profile = resolve_profile(request.target_tool) if request.target_tool else None
    detected_profile = detect_profile(goal) if goal else None

    if explicit_profile is not None:
        target = explicit_profile.name
    elif detected_profile is not None:
        target = detected_profile.name
    else:
        target = "generic"
        ambiguities.append(
            Ambiguity(
                field="target_tool",
                question="Which AI tool or agent will receive this prompt?",
                severity=AmbiguitySeverity.HIGH,
            )
        )

    return NormalizedIntent(
        goal=goal,
        target_tool=target,
        output_format=_clean(request.output_format),
        constraints=_clean_many(request.constraints),
        context=_clean_many(request.context),
        audience=_clean(request.audience),
        success_criteria=_clean_many(request.success_criteria),
        ambiguities=tuple(ambiguities),
    )

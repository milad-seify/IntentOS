from __future__ import annotations

import re

from .models import Ambiguity, AmbiguitySeverity, IntentRequest, NormalizedIntent
from .profiles import detect_profile, is_known_profile, resolve_profile


_WHITESPACE = re.compile(r"\s+")


def _clean_metadata(text: str | None) -> str | None:
    if text is None:
        return None
    value = _WHITESPACE.sub(" ", text).strip()
    return value or None


def _clean_content(text: str | None) -> str | None:
    if text is None:
        return None
    value = text.strip()
    if not value:
        return None
    # Preserve meaningful multiline formatting such as code, YAML, Markdown,
    # shell snippets, and indentation. Compact ordinary single-line prose only.
    if "\n" in value or "\r" in value:
        return value
    return _WHITESPACE.sub(" ", value)


def _clean_many(values: tuple[str, ...]) -> tuple[str, ...]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_content(value)
        if item and item not in seen:
            cleaned.append(item)
            seen.add(item)
    return tuple(cleaned)


def normalize_intent(request: IntentRequest) -> NormalizedIntent:
    goal = _clean_content(request.raw_text) or ""
    ambiguities: list[Ambiguity] = []

    if not goal:
        ambiguities.append(
            Ambiguity(
                field="goal",
                question="What outcome do you want the AI to produce?",
                severity=AmbiguitySeverity.HIGH,
            )
        )

    explicit_target = _clean_metadata(request.target_tool)
    explicit_profile = resolve_profile(explicit_target) if explicit_target else None
    detected_profile = detect_profile(goal) if goal else None

    if explicit_target and not is_known_profile(explicit_target):
        target = "generic"
        ambiguities.append(
            Ambiguity(
                field="target_tool",
                question=f"Unknown AI tool or agent '{explicit_target}'. Use a supported target or omit --target for detection.",
                severity=AmbiguitySeverity.HIGH,
            )
        )
    elif explicit_profile is not None:
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
        output_format=_clean_metadata(request.output_format),
        constraints=_clean_many(request.constraints),
        context=_clean_many(request.context),
        audience=_clean_metadata(request.audience),
        success_criteria=_clean_many(request.success_criteria),
        ambiguities=tuple(ambiguities),
    )

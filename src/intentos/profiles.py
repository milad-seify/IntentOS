from __future__ import annotations

from .models import PromptProfile


_GENERIC = PromptProfile(
    name="generic",
    aliases=("generic", "ai", "llm"),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_CODEX = PromptProfile(
    name="codex",
    aliases=("codex", "openai codex", "کدکس"),
    section_order=("Goal", "Context", "Scope", "Constraints", "Engineering", "Approvals", "Verification", "Done"),
)

_CLAUDE_CODE = PromptProfile(
    name="claude-code",
    aliases=("claude code", "claude-code", "کلود کد"),
    section_order=("Goal", "Context", "Scope", "Constraints", "Engineering", "Approvals", "Verification", "Done"),
)

_CURSOR = PromptProfile(
    name="cursor",
    aliases=("cursor", "کرسور"),
    section_order=("Goal", "Context", "Scope", "Constraints", "Engineering", "Approvals", "Verification", "Done"),
)

_CHATGPT = PromptProfile(
    name="chatgpt",
    aliases=("chatgpt", "gpt", "چت جی پی تی", "چت‌جی‌پی‌تی"),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_CLAUDE = PromptProfile(
    name="claude",
    aliases=("claude", "کلود"),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_GEMINI = PromptProfile(
    name="gemini",
    aliases=("gemini", "جمینای"),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_PROFILES = (_GENERIC, _CODEX, _CLAUDE_CODE, _CURSOR, _CHATGPT, _CLAUDE, _GEMINI)


def all_profiles() -> tuple[PromptProfile, ...]:
    return _PROFILES


def resolve_profile(name: str | None) -> PromptProfile:
    if not name:
        return _GENERIC

    normalized = " ".join(name.lower().strip().split())
    for profile in _PROFILES:
        if normalized == profile.name or normalized in profile.aliases:
            return profile
    return _GENERIC


def detect_profile(raw_text: str) -> PromptProfile | None:
    haystack = raw_text.lower()
    matches: list[tuple[int, PromptProfile]] = []
    for profile in _PROFILES:
        if profile is _GENERIC:
            continue
        for alias in profile.aliases:
            if alias in haystack:
                matches.append((len(alias), profile))

    if not matches:
        return None

    longest = max(length for length, _ in matches)
    most_specific = {
        profile.name: profile
        for length, profile in matches
        if length == longest
    }
    if len(most_specific) == 1:
        return next(iter(most_specific.values()))
    return None

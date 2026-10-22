from __future__ import annotations

from .models import PromptProfile


_GENERIC = PromptProfile(
    name="generic",
    aliases=("generic", "ai", "llm"),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_CODEX = PromptProfile(
    name="codex",
    aliases=("codex", "openai codex"),
    section_order=("Goal", "Context", "Scope", "Constraints", "Engineering", "Approvals", "Verification", "Done"),
    guidance=(
        "Keep implementation scope explicit and bounded.",
        "Require concrete verification evidence when code changes are requested.",
    ),
)

_CLAUDE_CODE = PromptProfile(
    name="claude-code",
    aliases=("claude code", "claude-code"),
    section_order=("Goal", "Context", "Scope", "Constraints", "Engineering", "Approvals", "Verification", "Done"),
    guidance=(
        "Keep repository scope explicit.",
        "State approval boundaries for destructive or persistent changes when relevant.",
    ),
)

_CHATGPT = PromptProfile(
    name="chatgpt",
    aliases=("chatgpt", "gpt"),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_PROFILES = (_GENERIC, _CODEX, _CLAUDE_CODE, _CHATGPT)


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
    matches: list[PromptProfile] = []
    for profile in _PROFILES:
        if profile is _GENERIC:
            continue
        if any(alias in haystack for alias in profile.aliases):
            matches.append(profile)
    if len(matches) == 1:
        return matches[0]
    return None

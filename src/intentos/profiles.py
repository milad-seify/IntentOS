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
)

_CLAUDE_CODE = PromptProfile(
    name="claude-code",
    aliases=("claude code", "claude-code"),
    section_order=("Goal", "Context", "Scope", "Constraints", "Engineering", "Approvals", "Verification", "Done"),
)

_CURSOR = PromptProfile(
    name="cursor",
    aliases=("cursor",),
    section_order=("Goal", "Context", "Scope", "Constraints", "Engineering", "Approvals", "Verification", "Done"),
)

_CHATGPT = PromptProfile(
    name="chatgpt",
    aliases=("chatgpt", "gpt"),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_CLAUDE = PromptProfile(
    name="claude",
    aliases=("claude",),
    section_order=("Goal", "Context", "Constraints", "Engineering", "Approvals", "Output", "Done"),
)

_GEMINI = PromptProfile(
    name="gemini",
    aliases=("gemini",),
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
    matches: list[PromptProfile] = []
    for profile in _PROFILES:
        if profile is _GENERIC:
            continue
        if any(alias in haystack for alias in profile.aliases):
            matches.append(profile)
    unique = {profile.name: profile for profile in matches}
    if len(unique) == 1:
        return next(iter(unique.values()))
    return None

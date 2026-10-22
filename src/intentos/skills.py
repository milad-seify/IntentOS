from __future__ import annotations

from dataclasses import dataclass
import json
import re

from .models import ExecutionPolicy, NormalizedIntent


_SKILL_NAME_RE = re.compile(r"[^a-z0-9-]+")
_MAX_SKILL_NAME = 64
_MAX_DESCRIPTION = 1024


@dataclass(frozen=True, slots=True)
class SkillArtifact:
    name: str
    description: str
    content: str


def _slug(value: str) -> str:
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    normalized = _SKILL_NAME_RE.sub("-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    normalized = (normalized or "intentos-skill")[:_MAX_SKILL_NAME].rstrip("-")
    return normalized or "intentos-skill"


def _description(value: str) -> str:
    normalized = " ".join(value.split()).strip()
    if not normalized:
        raise ValueError("Skill description must not be empty.")
    if len(normalized) > _MAX_DESCRIPTION:
        raise ValueError("Skill description must be at most 1024 characters.")
    return normalized


def build_skill_artifact(
    intent: NormalizedIntent,
    policy: ExecutionPolicy,
    *,
    name: str | None = None,
    description: str | None = None,
) -> SkillArtifact:
    """Compile reusable, vendor-neutral agent guidance into a SKILL.md artifact.

    The artifact follows the required Agent Skills frontmatter shape (`name` and
    `description`) while remaining text-only and proposal-first. Installation into
    agent-specific locations is an integration concern.
    """
    skill_name = _slug(name or f"intentos-{policy.task_type.value}")
    skill_description = _description(
        description
        if description is not None
        else (
            f"Apply IntentOS guidance for {policy.task_type.value} tasks with "
            f"{policy.risk_level.value} risk. Use when delegating this class of work to an AI agent."
        )
    )

    sections: list[str] = [
        "---",
        f"name: {json.dumps(skill_name, ensure_ascii=False)}",
        f"description: {json.dumps(skill_description, ensure_ascii=False)}",
        "---",
        "",
        f"# {skill_name}",
        "",
        "Use this skill when the task matches the intent and engineering constraints below.",
        "",
        "## Intent",
        "",
        intent.goal,
    ]

    if intent.context:
        sections.extend(("", "## Context", "", *[f"- {item}" for item in intent.context]))

    if intent.constraints:
        sections.extend(("", "## Constraints", "", *[f"- {item}" for item in intent.constraints]))

    if policy.engineering_rules:
        sections.extend(("", "## Engineering", "", *[f"- {item}" for item in policy.engineering_rules]))

    if policy.approval_boundaries:
        sections.extend(("", "## Approval boundaries", "", *[f"- {item}" for item in policy.approval_boundaries]))

    if policy.done_criteria:
        sections.extend(("", "## Done", "", *[f"- {item}" for item in policy.done_criteria]))

    content = "\n".join(sections).strip() + "\n"
    return SkillArtifact(name=skill_name, description=skill_description, content=content)

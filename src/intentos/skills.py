from __future__ import annotations

from dataclasses import dataclass
import re

from .models import ExecutionPolicy, NormalizedIntent


_SKILL_NAME_RE = re.compile(r"[^a-z0-9-]+")


@dataclass(frozen=True, slots=True)
class SkillArtifact:
    name: str
    description: str
    content: str


def _slug(value: str) -> str:
    normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
    normalized = _SKILL_NAME_RE.sub("-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "intentos-skill"


def build_skill_artifact(
    intent: NormalizedIntent,
    policy: ExecutionPolicy,
    *,
    name: str | None = None,
    description: str | None = None,
) -> SkillArtifact:
    """Compile reusable, vendor-neutral agent guidance into a SKILL.md artifact.

    The artifact is intentionally text-only and proposal-first. Installing it into
    agent-specific locations is an integration concern.
    """
    skill_name = _slug(name or f"intentos-{policy.task_type.value}")
    skill_description = (
        description.strip()
        if description and description.strip()
        else f"IntentOS guidance for {policy.task_type.value} tasks with {policy.risk_level.value} risk."
    )

    sections: list[str] = [
        "---",
        f"name: {skill_name}",
        f"description: {skill_description}",
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

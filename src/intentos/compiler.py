from __future__ import annotations

from collections.abc import Iterable

from .classifier import is_review_only
from .models import ExecutionPolicy, NormalizedIntent, PromptResult
from .profiles import resolve_profile


def _section(title: str, lines: Iterable[str]) -> str | None:
    values = [line.strip() for line in lines if line and line.strip()]
    if not values:
        return None
    body = "\n".join(f"- {value}" for value in values)
    return f"{title}:\n{body}"


def compile_prompt(
    intent: NormalizedIntent,
    policy: ExecutionPolicy | None = None,
) -> PromptResult:
    questions = tuple(
        ambiguity.question
        for ambiguity in intent.ambiguities
        if ambiguity.severity.value == "high"
    )
    if questions:
        return PromptResult(prompt=None, intent=intent, questions=questions[:3], policy=policy)

    profile = resolve_profile(intent.target_tool)
    sections: dict[str, str | None] = {
        "Goal": _section("Goal", (intent.goal,)),
        "Context": _section("Context", intent.context),
        "Scope": None,
        "Constraints": _section("Constraints", intent.constraints),
        "Engineering": _section("Engineering", policy.engineering_rules if policy else ()),
        "Approvals": _section("Approval boundaries", policy.approval_boundaries if policy else ()),
        "Output": _section(
            "Output",
            tuple(
                value
                for value in (
                    f"Format: {intent.output_format}" if intent.output_format else None,
                    f"Audience: {intent.audience}" if intent.audience else None,
                )
                if value
            ),
        ),
        "Verification": _section("Verification", intent.success_criteria),
        "Done": _section("Done", policy.done_criteria if policy else intent.success_criteria),
    }

    if profile.name in {"codex", "claude-code"}:
        review_only = is_review_only(intent)
        sections["Scope"] = _section(
            "Scope",
            (
                "Review and recommend only; do not implement changes."
                if review_only
                else "Change only what is required to satisfy the goal; avoid unrelated refactors.",
            ),
        )
        if not sections["Verification"]:
            sections["Verification"] = _section(
                "Verification",
                (
                    "Support findings with evidence and report verification gaps; do not claim unperformed checks passed."
                    if review_only
                    else "Run the smallest relevant checks and report concrete results.",
                ),
            )
        if not sections["Done"]:
            sections["Done"] = _section(
                "Done",
                (
                    "Summarize findings, evidence, and remaining uncertainties."
                    if review_only
                    else "Summarize changed files, checks run, results, and remaining risks.",
                ),
            )

    rendered = [sections[name] for name in profile.section_order if sections.get(name)]
    return PromptResult(prompt="\n\n".join(rendered), intent=intent, policy=policy)

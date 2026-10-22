from __future__ import annotations

from .models import ExecutionPolicy, NormalizedIntent, RiskLevel, TaskType


def build_execution_policy(
    intent: NormalizedIntent,
    task_type: TaskType,
    risk_level: RiskLevel,
) -> ExecutionPolicy:
    engineering: list[str] = []
    approvals: list[str] = []
    done: list[str] = []

    if task_type in {TaskType.CODING, TaskType.BUGFIX, TaskType.REFACTOR, TaskType.ARCHITECTURE, TaskType.SECURITY}:
        engineering.extend(
            (
                "Prefer the smallest coherent change; follow KISS and YAGNI before adding abstractions.",
                "Preserve existing public behavior unless the goal explicitly requires a change.",
                "Apply SOLID, DRY, and Clean Code only where they materially improve maintainability or testability.",
            )
        )
        done.extend(("Relevant automated checks pass.", "No unrelated refactor or scope expansion was introduced."))

    if task_type is TaskType.BUGFIX:
        engineering.append("Fix the root cause when practical; avoid masking the symptom with a broad rewrite.")
        done.append("The failing behavior is covered by a regression check when feasible.")

    if task_type is TaskType.REFACTOR:
        engineering.append("Keep observable behavior stable and prefer incremental, reviewable changes.")
        done.append("Behavior remains equivalent under the relevant test suite.")

    if task_type is TaskType.ARCHITECTURE:
        engineering.append("State meaningful trade-offs and avoid introducing distributed complexity without evidence of need.")
        done.append("Key assumptions and trade-offs are documented.")

    if task_type is TaskType.SECURITY:
        engineering.extend(("Use least privilege and secure defaults.", "Do not expose, log, or hard-code secrets."))
        approvals.extend(("Ask before weakening an existing security control.", "Ask before changing authentication, authorization, or secret-handling behavior in a way that affects users or production."))
        done.append("Security-sensitive assumptions and verification results are reported explicitly.")

    if task_type is TaskType.DEVOPS:
        engineering.extend(
            (
                "Prefer reproducible, declarative, and idempotent changes where the toolchain supports them.",
                "Keep secrets out of source control and generated output.",
                "Preserve a practical rollback or recovery path for operational changes.",
            )
        )
        done.extend(("Configuration or deployment changes are validated with the smallest relevant check.", "Rollback or recovery implications are stated for material operational changes."))

    if risk_level is RiskLevel.HIGH:
        approvals.extend(
            (
                "Ask before destructive operations or irreversible data changes.",
                "Ask before production writes or persistent schema changes unless explicitly authorized in the request.",
            )
        )
        done.append("High-risk actions, assumptions, and residual risks are reported explicitly.")
    elif risk_level is RiskLevel.MEDIUM:
        approvals.append("Do not expand scope, add dependencies, or change persistent interfaces without a demonstrated need.")

    if intent.success_criteria:
        done.extend(intent.success_criteria)

    return ExecutionPolicy(
        task_type=task_type,
        risk_level=risk_level,
        engineering_rules=tuple(dict.fromkeys(engineering)),
        approval_boundaries=tuple(dict.fromkeys(approvals)),
        done_criteria=tuple(dict.fromkeys(done)),
    )

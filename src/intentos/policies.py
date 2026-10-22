from __future__ import annotations

from .classifier import has_devops_signals, has_persistent_data_signals, is_documentation_only
from .models import ExecutionPolicy, NormalizedIntent, RiskLevel, TaskType


def build_execution_policy(
    intent: NormalizedIntent,
    task_type: TaskType,
    risk_level: RiskLevel,
) -> ExecutionPolicy:
    engineering: list[str] = []
    approvals: list[str] = []
    done: list[str] = []
    docs_only = is_documentation_only(intent)
    devops_related = has_devops_signals(intent)
    persistent_data = has_persistent_data_signals(intent)

    if docs_only:
        engineering.append(
            "Keep the change limited to documentation or comments; do not modify runtime behavior, dependencies, configuration, or infrastructure."
        )
        done.append("Only documentation/comment files are changed unless the request explicitly authorizes more.")

    if not docs_only and task_type in {
        TaskType.CODING,
        TaskType.BUGFIX,
        TaskType.REFACTOR,
        TaskType.ARCHITECTURE,
        TaskType.SECURITY,
    }:
        engineering.extend(
            (
                "Prefer the smallest coherent change; use the first sufficient option: skip unnecessary work, reuse existing project code, use standard-library or platform capabilities, reuse an already-installed dependency, and only then add the minimum new code.",
                "Preserve existing public behavior unless the goal explicitly requires a change.",
                "Apply SOLID, DRY, and Clean Code only where they materially improve maintainability or testability.",
            )
        )
        done.extend(("Relevant automated checks pass.", "No unrelated refactor or scope expansion was introduced."))

    if task_type is TaskType.BUGFIX and not docs_only:
        engineering.append("Fix the root cause when practical; avoid masking the symptom with a broad rewrite.")
        done.append("The failing behavior is covered by a regression check when feasible.")

    if task_type is TaskType.REFACTOR and not docs_only:
        engineering.append("Keep observable behavior stable and prefer incremental, reviewable changes.")
        done.append("Behavior remains equivalent under the relevant test suite.")

    if task_type is TaskType.ARCHITECTURE:
        engineering.append("State meaningful trade-offs and avoid introducing distributed complexity without evidence of need.")
        done.append("Key assumptions and trade-offs are documented.")

    if task_type is TaskType.SECURITY:
        engineering.append("Do not expose, log, or hard-code secrets.")
        if not docs_only:
            engineering.append("Use least privilege and secure defaults.")
            approvals.extend(
                (
                    "Ask before weakening an existing security control.",
                    "Ask before changing authentication, authorization, or secret-handling behavior in a way that affects users or production.",
                )
            )
            done.append("Security-sensitive assumptions and verification results are reported explicitly.")

    if devops_related and not docs_only:
        engineering.extend(
            (
                "Prefer reproducible, declarative, and idempotent changes where the toolchain supports them.",
                "Keep secrets out of source control and generated output.",
                "Preserve a practical rollback or recovery path for operational changes.",
            )
        )
        done.extend(
            (
                "Configuration or deployment changes are validated with the smallest relevant check.",
                "Rollback or recovery implications are stated for material operational changes.",
            )
        )

    if persistent_data and not docs_only:
        engineering.append(
            "For schema or data migrations, state validation, rollback/recovery, and backup implications before execution."
        )
        done.append("Persistent data changes include an explicit validation and recovery plan.")

    if not docs_only and risk_level is RiskLevel.HIGH:
        approvals.extend(
            (
                "Ask before destructive operations or irreversible data changes.",
                "Ask before production writes or persistent schema changes unless explicitly authorized in the request.",
            )
        )
        done.append("High-risk actions, assumptions, and residual risks are reported explicitly.")
    elif not docs_only and risk_level is RiskLevel.MEDIUM:
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

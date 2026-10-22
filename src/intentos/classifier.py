from __future__ import annotations

from .models import NormalizedIntent, RiskLevel, TaskType


_HIGH_RISK_TERMS = (
    "production",
    "prod ",
    "database schema",
    "migration",
    "drop table",
    "delete data",
    "secret",
    "credential",
    "authentication",
    "authorization",
    "payment",
    "firewall",
    "iam",
)


def classify_task(intent: NormalizedIntent) -> tuple[TaskType, RiskLevel]:
    text = " ".join((intent.goal, *intent.context, *intent.constraints)).lower()

    if any(term in text for term in ("security", "vulnerability", "authentication", "authorization", "secret", "credential", "iam")):
        task = TaskType.SECURITY
    elif any(term in text for term in ("terraform", "ansible", "kubernetes", "docker", "deploy", "deployment", "ci/cd", "pipeline", "infrastructure", "devops")):
        task = TaskType.DEVOPS
    elif any(term in text for term in ("architecture", "system design", "design the system", "architect")):
        task = TaskType.ARCHITECTURE
    elif any(term in text for term in ("refactor", "cleanup code", "clean up code")):
        task = TaskType.REFACTOR
    elif any(term in text for term in ("bug", "fix", "failing test", "regression", "broken")):
        task = TaskType.BUGFIX
    elif any(term in text for term in ("implement", "add feature", "build", "code", "function", "module", "api")):
        task = TaskType.CODING
    else:
        task = TaskType.GENERAL

    if any(term in text for term in _HIGH_RISK_TERMS) or task is TaskType.SECURITY:
        risk = RiskLevel.HIGH
    elif task in {TaskType.ARCHITECTURE, TaskType.DEVOPS, TaskType.REFACTOR, TaskType.CODING}:
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.LOW

    if any(term in text for term in ("docs only", "documentation only", "readme only", "comment only")):
        risk = RiskLevel.LOW

    return task, risk

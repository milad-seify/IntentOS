from __future__ import annotations

from .models import NormalizedIntent, RiskLevel, TaskType


_SECURITY_TERMS = (
    "security",
    "vulnerability",
    "authentication",
    "authorization",
    "secret",
    "credential",
    "iam",
    "امنیت",
    "آسیب پذیری",
    "آسیب‌پذیری",
    "احراز هویت",
    "مجوز دسترسی",
)

_DEVOPS_TERMS = (
    "terraform",
    "ansible",
    "kubernetes",
    "docker",
    "deploy",
    "deployment",
    "ci/cd",
    "pipeline",
    "infrastructure",
    "devops",
    "دواپس",
    "استقرار",
    "زیرساخت",
    "پایپ لاین",
    "پایپ‌لاین",
    "داکر",
    "کوبرنتیز",
    "ترفرم",
    "انسیبل",
)

_ARCHITECTURE_TERMS = (
    "architecture",
    "system design",
    "design the system",
    "architect",
    "معماری",
    "طراحی سیستم",
)

_REFACTOR_TERMS = (
    "refactor",
    "cleanup code",
    "clean up code",
    "ریفکتور",
    "بازآرایی",
    "بازآرایی کد",
)

_BUGFIX_TERMS = (
    "bug",
    "fix",
    "failing test",
    "regression",
    "broken",
    "باگ",
    "رفع خطا",
    "تست ناموفق",
    "خراب",
)

_CODING_TERMS = (
    "implement",
    "add feature",
    "build",
    "code",
    "function",
    "module",
    "api",
    "پیاده سازی",
    "پیاده‌سازی",
    "کدنویسی",
    "تابع",
    "ماژول",
)

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
    "محیط تولید",
    "پروداکشن",
    "اسکیما",
    "مهاجرت دیتابیس",
    "حذف داده",
    "احراز هویت",
    "فایروال",
    "پرداخت",
)

_DOCUMENTATION_ONLY_TERMS = (
    "docs only",
    "documentation only",
    "readme only",
    "comment only",
    "فقط مستندات",
    "فقط داکیومنت",
    "فقط readme",
    "فقط کامنت",
)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def is_documentation_only(intent: NormalizedIntent) -> bool:
    text = " ".join((intent.goal, *intent.context, *intent.constraints)).casefold()
    return _contains_any(text, _DOCUMENTATION_ONLY_TERMS)


def classify_task(intent: NormalizedIntent) -> tuple[TaskType, RiskLevel]:
    text = " ".join((intent.goal, *intent.context, *intent.constraints)).casefold()

    if _contains_any(text, _SECURITY_TERMS):
        task = TaskType.SECURITY
    elif _contains_any(text, _DEVOPS_TERMS):
        task = TaskType.DEVOPS
    elif _contains_any(text, _ARCHITECTURE_TERMS):
        task = TaskType.ARCHITECTURE
    elif _contains_any(text, _REFACTOR_TERMS):
        task = TaskType.REFACTOR
    elif _contains_any(text, _BUGFIX_TERMS):
        task = TaskType.BUGFIX
    elif _contains_any(text, _CODING_TERMS):
        task = TaskType.CODING
    else:
        task = TaskType.GENERAL

    if _contains_any(text, _HIGH_RISK_TERMS) or task is TaskType.SECURITY:
        risk = RiskLevel.HIGH
    elif task in {TaskType.ARCHITECTURE, TaskType.DEVOPS, TaskType.REFACTOR, TaskType.CODING}:
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.LOW

    if is_documentation_only(intent):
        risk = RiskLevel.LOW

    return task, risk

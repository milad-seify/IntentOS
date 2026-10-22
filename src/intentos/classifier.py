from __future__ import annotations

import re

from .models import NormalizedIntent, RiskLevel, TaskType


_SECURITY_TERMS = (
    "security",
    "vulnerability",
    "authentication",
    "authorization",
    "login",
    "log in",
    "sign in",
    "secret",
    "credential",
    "iam",
    "امنیت",
    "آسیب پذیری",
    "آسیب‌پذیری",
    "احراز هویت",
    "ورود کاربر",
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
    "prod",
    "database schema",
    "schema migration",
    "migration",
    "drop table",
    "truncate",
    "delete data",
    "delete all",
    "wipe",
    "rm -rf",
    "secret",
    "credential",
    "authentication",
    "authorization",
    "login",
    "payment",
    "firewall",
    "iam",
    "محیط تولید",
    "پروداکشن",
    "اسکیما",
    "مهاجرت دیتابیس",
    "حذف داده",
    "حذف همه",
    "همه فایل‌ها را پاک کن",
    "همه فایلها را پاک کن",
    "احراز هویت",
    "فایروال",
    "پرداخت",
)

_PERSISTENT_DATA_TERMS = (
    "database schema",
    "schema migration",
    "migration",
    "drop table",
    "truncate",
    "delete data",
    "مهاجرت دیتابیس",
    "اسکیما",
    "حذف داده",
)

_DOCUMENTATION_ONLY_TERMS = (
    "docs only",
    "documentation only",
    "documentation-only",
    "readme only",
    "comment only",
    "فقط مستندات",
    "فقط داکیومنت",
    "فقط readme",
    "فقط کامنت",
)

_DOCUMENTATION_SURFACE_TERMS = (
    "readme",
    "documentation",
    "docs",
    "markdown",
    "comment",
    "مستندات",
    "داکیومنت",
    "کامنت",
)

_NEGATION_TERMS = (
    "not",
    "never",
    "do not",
    "don't",
    "نیست",
    "نباشد",
    "نکن",
    "هرگز",
    "نه",
)


def _term_matches(text: str, term: str) -> tuple[re.Match[str], ...]:
    pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE | re.UNICODE)
    return tuple(pattern.finditer(text))


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(_term_matches(text, term) for term in terms)


def _action_text(intent: NormalizedIntent) -> str:
    return " ".join((intent.goal, *intent.constraints)).casefold()


def _all_text(intent: NormalizedIntent) -> str:
    return " ".join((intent.goal, *intent.constraints, *intent.context)).casefold()


def _has_unnegated_documentation_scope(text: str) -> bool:
    for term in _DOCUMENTATION_ONLY_TERMS:
        for match in _term_matches(text, term):
            prefix = text[max(0, match.start() - 48) : match.start()]
            if not _contains_any(prefix, _NEGATION_TERMS):
                return True
    return False


def _looks_like_documentation_edit(text: str) -> bool:
    if not _contains_any(text, _DOCUMENTATION_SURFACE_TERMS):
        return False
    if _contains_any(text, _SECURITY_TERMS + _DEVOPS_TERMS + _CODING_TERMS + _REFACTOR_TERMS):
        return False
    return _contains_any(
        text,
        (
            "update",
            "edit",
            "write",
            "fix",
            "typo",
            "correct",
            "document",
            "به روز",
            "به‌روز",
            "ویرایش",
            "اصلاح",
            "بنویس",
        ),
    )


def is_documentation_only(intent: NormalizedIntent) -> bool:
    # Documentation scope is a property of the requested action. Background
    # context must never be able to weaken a mutation-risk decision.
    return _has_unnegated_documentation_scope(_action_text(intent))


def has_devops_signals(intent: NormalizedIntent) -> bool:
    return _contains_any(_all_text(intent), _DEVOPS_TERMS)


def has_persistent_data_signals(intent: NormalizedIntent) -> bool:
    return _contains_any(_all_text(intent), _PERSISTENT_DATA_TERMS)


def classify_task(intent: NormalizedIntent) -> tuple[TaskType, RiskLevel]:
    action = _action_text(intent)
    all_text = _all_text(intent)
    docs_only = is_documentation_only(intent)

    if _contains_any(action, _SECURITY_TERMS):
        task = TaskType.SECURITY
    elif _contains_any(action, _DEVOPS_TERMS):
        task = TaskType.DEVOPS
    elif _contains_any(action, _ARCHITECTURE_TERMS):
        task = TaskType.ARCHITECTURE
    elif _contains_any(action, _REFACTOR_TERMS):
        task = TaskType.REFACTOR
    elif _looks_like_documentation_edit(action):
        task = TaskType.GENERAL
    elif _contains_any(action, _BUGFIX_TERMS):
        task = TaskType.BUGFIX
    elif _contains_any(action, _CODING_TERMS):
        task = TaskType.CODING
    else:
        task = TaskType.GENERAL

    if docs_only:
        risk = RiskLevel.LOW
    elif _contains_any(all_text, _HIGH_RISK_TERMS) or task is TaskType.SECURITY:
        risk = RiskLevel.HIGH
    elif task in {TaskType.ARCHITECTURE, TaskType.DEVOPS, TaskType.REFACTOR, TaskType.CODING}:
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.LOW

    return task, risk

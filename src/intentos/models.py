from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class AmbiguitySeverity(str, Enum):
    LOW = "low"
    HIGH = "high"


class TaskType(str, Enum):
    GENERAL = "general"
    CODING = "coding"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    DEVOPS = "devops"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class IntentRequest:
    raw_text: str
    target_tool: str | None = None
    output_format: str | None = None
    constraints: tuple[str, ...] = ()
    context: tuple[str, ...] = ()
    audience: str | None = None
    success_criteria: tuple[str, ...] = ()

    @classmethod
    def from_values(
        cls,
        raw_text: str,
        *,
        target_tool: str | None = None,
        output_format: str | None = None,
        constraints: Iterable[str] = (),
        context: Iterable[str] = (),
        audience: str | None = None,
        success_criteria: Iterable[str] = (),
    ) -> "IntentRequest":
        return cls(
            raw_text=raw_text,
            target_tool=target_tool,
            output_format=output_format,
            constraints=tuple(constraints),
            context=tuple(context),
            audience=audience,
            success_criteria=tuple(success_criteria),
        )


@dataclass(frozen=True, slots=True)
class Ambiguity:
    field: str
    question: str
    severity: AmbiguitySeverity = AmbiguitySeverity.HIGH


@dataclass(frozen=True, slots=True)
class NormalizedIntent:
    goal: str
    target_tool: str
    output_format: str | None = None
    constraints: tuple[str, ...] = ()
    context: tuple[str, ...] = ()
    audience: str | None = None
    success_criteria: tuple[str, ...] = ()
    ambiguities: tuple[Ambiguity, ...] = ()

    @property
    def is_ready(self) -> bool:
        return not any(item.severity is AmbiguitySeverity.HIGH for item in self.ambiguities)


@dataclass(frozen=True, slots=True)
class PromptProfile:
    name: str
    aliases: tuple[str, ...]
    section_order: tuple[str, ...]
    guidance: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    task_type: TaskType
    risk_level: RiskLevel
    engineering_rules: tuple[str, ...] = ()
    approval_boundaries: tuple[str, ...] = ()
    done_criteria: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PromptResult:
    prompt: str | None
    intent: NormalizedIntent
    questions: tuple[str, ...] = field(default_factory=tuple)
    policy: ExecutionPolicy | None = None

    @property
    def needs_clarification(self) -> bool:
        return bool(self.questions)

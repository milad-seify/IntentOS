"""Bounded, read-only Project Compass pilot.

This is an internal prototype, not an additional v1 public API or agent runtime.
It only interprets explicitly titled headings from caller-supplied documents.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from .models import ContextDocument


_MAX_DOCUMENTS = 32
_MAX_CHARS = 6000
_HEADING = re.compile(r"^#{2,3}\s+(.+?)\s*$")
_SINGLE = {"goal", "current_phase", "next_action"}
_ALIASES = {
    "project goal": "goal",
    "north star": "goal",
    "current phase": "current_phase",
    "next meaningful action": "next_action",
    "next action": "next_action",
    "in scope": "in_scope",
    "out of scope": "out_of_scope",
    "completed": "completed",
    "in progress": "in_progress",
    "blocked": "blocked",
    "deferred": "deferred",
    "decisions": "decisions",
    "important decisions": "decisions",
}
_FIELDS = (
    "goal", "current_phase", "completed", "in_progress",
    "blocked", "deferred", "next_action", "decisions",
    "in_scope", "out_of_scope",
)


@dataclass(frozen=True, slots=True)
class SourceFact:
    text: str
    path: str
    line: int
    stale: bool = False


@dataclass(frozen=True, slots=True)
class CompassField:
    name: str
    status: str  # known | missing | conflicting | stale
    evidence: tuple[SourceFact, ...]

    @property
    def value(self) -> str | None:
        if self.status == "known" and self.name in _SINGLE:
            return self.evidence[0].text
        return None


@dataclass(frozen=True, slots=True)
class ScopeAssessment:
    status: str  # in_scope | out_of_scope | conflicting | unknown
    explanation: str
    evidence: tuple[SourceFact, ...]
    approval_required: bool


@dataclass(frozen=True, slots=True)
class ProjectCompass:
    fields: tuple[CompassField, ...]
    task_scope: ScopeAssessment

    def field(self, name: str) -> CompassField:
        for item in self.fields:
            if item.name == name:
                return item
        raise KeyError(name)


def _sections(doc: ContextDocument) -> list[tuple[str, list[tuple[int, str]]]]:
    sections: list[tuple[str, list[tuple[int, str]]]] = []
    current: list[tuple[int, str]] | None = None
    for line_no, raw in enumerate(doc.content.splitlines(), 1):
        heading = _HEADING.match(raw)
        if heading:
            key = heading.group(1).strip().casefold()
            if key == "evidence freshness" or key in _ALIASES:
                current = []
                sections.append((key, current))
            else:
                current = None
        elif current is not None and raw.strip():
            current.append((line_no, raw.strip()))
    return sections


def _facts(key: str, lines: list[tuple[int, str]], doc: ContextDocument, stale: bool) -> list[SourceFact]:
    if not lines:
        return []
    if key in _SINGLE:
        # Do not synthesize a summary from several unrelated claims.
        content = " ".join(text.removeprefix("- ").strip() for _, text in lines)
        return [SourceFact(content, doc.path, lines[0][0], stale)]
    return [
        SourceFact(text[2:].strip() if text.startswith(("- ", "* ")) else text, doc.path, line, stale)
        for line, text in lines
        if text.strip("-* ").strip()
    ]


def _norm(value: str) -> str:
    return " ".join(value.casefold().strip().strip("`").split())


def _field(name: str, evidence: tuple[SourceFact, ...]) -> CompassField:
    if not evidence:
        status = "missing"
    elif any(fact.stale for fact in evidence):
        status = "stale"
    elif name in _SINGLE and len({_norm(item.text) for item in evidence}) > 1:
        status = "conflicting"
    else:
        status = "known"
    return CompassField(name, status, evidence)


def review_project_compass(
    documents: tuple[ContextDocument, ...],
    *,
    proposed_task: str = "",
) -> ProjectCompass:
    """Review only explicit supplied facts; unknown scope is never assumed safe.

    Scope matches require an exact phrase from an In Scope/Out of Scope item.
    Free-form semantic scope inference is deliberately not attempted.
    """
    if len(documents) > _MAX_DOCUMENTS:
        raise ValueError("too many project context documents")
    if sum(len(doc.content) for doc in documents) > _MAX_CHARS:
        raise ValueError("project context exceeds 6000 characters")
    paths = [doc.path.replace("\\", "/").casefold() for doc in documents]
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate project context paths")

    found: dict[str, list[SourceFact]] = {name: [] for name in _FIELDS}
    for doc in documents:
        sections = _sections(doc)
        stale = any(
            heading == "evidence freshness"
            and any(text.strip().casefold() in {"stale", "outdated"} for _, text in lines)
            for heading, lines in sections
        )
        for heading, lines in sections:
            field = _ALIASES.get(heading)
            if field:
                found[field].extend(_facts(field, lines, doc, stale))

    fields = tuple(_field(name, tuple(found[name])) for name in _FIELDS)
    task = _norm(proposed_task)
    inside = tuple(f for f in found["in_scope"] if task and _norm(f.text) == task)
    outside = tuple(f for f in found["out_of_scope"] if task and _norm(f.text) == task)
    matched = (*inside, *outside)
    if not task:
        status, reason = "unknown", "No proposed task supplied."
    elif any(f.stale for f in matched):
        status, reason = "unknown", "Matching scope evidence is explicitly stale."
    elif inside and outside:
        status, reason = "conflicting", "Supplied scope sources contradict each other."
    elif outside:
        status, reason = "out_of_scope", "Task exactly matches an explicit out-of-scope item."
    elif inside:
        status, reason = "in_scope", "Task exactly matches an explicit in-scope item."
    else:
        status, reason = "unknown", "No exact explicit scope match; human review is required."
    return ProjectCompass(
        fields,
        ScopeAssessment(status, reason, tuple(matched), status != "in_scope"),
    )

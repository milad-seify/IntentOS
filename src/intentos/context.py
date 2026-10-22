from __future__ import annotations

import re

from .models import ContextDocument, ContextSelection, NormalizedIntent, ScoredContext


_WORD = re.compile(r"[A-Za-z0-9_./-]{3,}")
_PRIORITY_NAMES = {
    "AGENTS.md": 8,
    "STATUS.md": 7,
    "DECISIONS.md": 6,
    "ARCHITECTURE.md": 5,
    "ROADMAP.md": 4,
    "README.md": 3,
}


def _tokens(text: str) -> set[str]:
    return {token.casefold() for token in _WORD.findall(text)}


def _normalize_content(text: str) -> str:
    return " ".join(text.split()).casefold()


def select_project_context(
    intent: NormalizedIntent,
    documents: tuple[ContextDocument, ...],
    *,
    max_chars: int = 6000,
) -> ContextSelection:
    query_tokens = _tokens(" ".join((intent.goal, *intent.constraints, *intent.context)))
    seen_content: set[str] = set()
    scored: list[ScoredContext] = []
    omitted: list[str] = []

    for document in documents:
        normalized = _normalize_content(document.content)
        if not normalized or normalized in seen_content:
            omitted.append(document.path)
            continue
        seen_content.add(normalized)

        path_name = document.path.rsplit("/", 1)[-1]
        doc_tokens = _tokens(f"{document.path} {document.content}")
        overlap = len(query_tokens & doc_tokens)
        priority = _PRIORITY_NAMES.get(path_name, 0)
        authority = 3 if document.authoritative else 0
        score = overlap * 2 + priority + authority

        reasons: list[str] = []
        if overlap:
            reasons.append(f"{overlap} intent token matches")
        if priority:
            reasons.append("project guidance priority")
        if authority:
            reasons.append("authoritative source")

        if score <= 0:
            omitted.append(document.path)
            continue
        scored.append(ScoredContext(document=document, score=score, reasons=tuple(reasons)))

    scored.sort(key=lambda item: (-item.score, item.document.path.casefold()))

    selected: list[ScoredContext] = []
    used = 0
    for item in scored:
        size = len(item.document.content)
        if selected and used + size > max_chars:
            omitted.append(item.document.path)
            continue
        if not selected and size > max_chars:
            clipped = ContextDocument(
                path=item.document.path,
                content=item.document.content[:max_chars],
                authoritative=item.document.authoritative,
            )
            selected.append(ScoredContext(clipped, item.score, item.reasons + ("clipped to context budget",)))
            used = max_chars
            continue
        selected.append(item)
        used += size

    return ContextSelection(
        selected=tuple(selected),
        omitted_paths=tuple(dict.fromkeys(omitted)),
        total_chars=used,
    )

from __future__ import annotations

import re

from .models import ContextDocument, ContextSelection, NormalizedIntent, ScoredContext


# Python's Unicode-aware \w keeps deterministic lexical matching while allowing
# Persian and other scripts to participate in context relevance scoring.
_WORD = re.compile(r"[\w./-]{3,}", re.UNICODE)
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


def _canonical_path(path: str) -> str:
    return path.replace("\\", "/")


def _clip_content(content: str, max_chars: int) -> str:
    if len(content) <= max_chars:
        return content
    if max_chars <= 0:
        return ""

    candidate = content[:max_chars]
    line_break = candidate.rfind("\n")
    whitespace = candidate.rfind(" ")
    cutoff = max(line_break, whitespace)
    if cutoff >= max_chars // 2:
        return candidate[:cutoff].rstrip()
    return candidate


def select_project_context(
    intent: NormalizedIntent,
    documents: tuple[ContextDocument, ...],
    *,
    max_chars: int = 6000,
) -> ContextSelection:
    if max_chars < 0:
        raise ValueError("max_chars must be non-negative")

    query_tokens = _tokens(" ".join((intent.goal, *intent.constraints, *intent.context)))
    candidates: list[ScoredContext] = []
    omitted: list[str] = []

    for document in documents:
        normalized = _normalize_content(document.content)
        if not normalized:
            omitted.append(document.path)
            continue

        canonical_path = _canonical_path(document.path)
        path_name = canonical_path.rsplit("/", 1)[-1]
        doc_tokens = _tokens(f"{canonical_path} {document.content}")
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
        candidates.append(ScoredContext(document=document, score=score, reasons=tuple(reasons)))

    # Rank first, then deduplicate so the strongest/authoritative representative
    # survives even when an identical lower-value copy appeared earlier.
    candidates.sort(
        key=lambda item: (
            not item.document.authoritative,
            -item.score,
            _canonical_path(item.document.path).casefold(),
        )
    )
    seen_content: set[str] = set()
    scored: list[ScoredContext] = []
    for item in candidates:
        normalized = _normalize_content(item.document.content)
        if normalized in seen_content:
            omitted.append(item.document.path)
            continue
        seen_content.add(normalized)
        scored.append(item)

    selected: list[ScoredContext] = []
    used = 0
    for item in scored:
        if max_chars == 0:
            omitted.append(item.document.path)
            continue

        size = len(item.document.content)
        remaining = max_chars - used
        if remaining <= 0:
            omitted.append(item.document.path)
            continue
        if size > remaining:
            if selected:
                omitted.append(item.document.path)
                continue
            clipped_content = _clip_content(item.document.content, remaining)
            if not clipped_content:
                omitted.append(item.document.path)
                continue
            clipped = ContextDocument(
                path=item.document.path,
                content=clipped_content,
                authoritative=item.document.authoritative,
            )
            selected.append(
                ScoredContext(
                    clipped,
                    item.score,
                    item.reasons + ("clipped to context budget",),
                )
            )
            used += len(clipped_content)
            continue

        selected.append(item)
        used += size

    return ContextSelection(
        selected=tuple(selected),
        omitted_paths=tuple(dict.fromkeys(omitted)),
        total_chars=used,
    )

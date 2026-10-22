from __future__ import annotations

from dataclasses import replace

from .context import select_project_context
from .models import ContextDocument, IntentRequest, ModelMetadata, PromptResult
from .normalize import normalize_intent
from .service import optimize_prompt


def optimize_project_prompt(
    request: IntentRequest,
    documents: tuple[ContextDocument, ...],
    *,
    max_context_chars: int = 6000,
    models: tuple[ModelMetadata, ...] = (),
) -> PromptResult:
    if max_context_chars < 0:
        raise ValueError("max_context_chars must be non-negative")

    explicit_context_chars = sum(len(item.strip()) for item in request.context if item.strip())
    if explicit_context_chars > max_context_chars:
        raise ValueError("explicit context exceeds max_context_chars")

    base_intent = normalize_intent(request)
    selection = select_project_context(
        base_intent,
        documents,
        max_chars=max_context_chars - explicit_context_chars,
    )

    selected_context = tuple(
        f"[{item.document.path}]\n{item.document.content}"
        for item in selection.selected
    )
    enriched = replace(
        request,
        context=tuple((*request.context, *selected_context)),
    )
    result = optimize_prompt(enriched, models=models)
    return replace(result, context_selection=selection)

from __future__ import annotations

from .models import ContextDocument, WorkspaceAction, WorkspaceChange, WorkspacePlan


_MAX_CONTEXT_FILE_CHARS = 12000


def _by_path(documents: tuple[ContextDocument, ...]) -> dict[str, ContextDocument]:
    return {document.path.casefold(): document for document in documents}


def _replace_current_phase(content: str, current_phase: str) -> str:
    marker = "## Current phase"
    if marker not in content:
        return content.rstrip() + f"\n\n{marker}\n\n{current_phase}\n"

    before, remainder = content.split(marker, 1)
    if "\n## " in remainder:
        _, after = remainder.split("\n## ", 1)
        return before + marker + f"\n\n{current_phase}\n\n## " + after
    return before + marker + f"\n\n{current_phase}\n"


def plan_agent_workspace(
    documents: tuple[ContextDocument, ...],
    *,
    current_phase: str,
) -> WorkspacePlan:
    paths = _by_path(documents)
    changes: list[WorkspaceChange] = []
    warnings: list[str] = []

    agents = paths.get("agents.md")
    if agents is None:
        content = (
            "# AGENTS.md\n\n"
            "Repository guidance for AI agents.\n\n"
            "## Operating rules\n\n"
            "- Keep changes scoped and reviewable.\n"
            "- Follow repository documentation and existing conventions.\n"
            "- Ask before destructive or irreversible actions.\n"
            "- Report verification evidence.\n\n"
            f"## Current phase\n\n{current_phase}\n"
        )
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.CREATE,
                path="AGENTS.md",
                reason="missing primary agent guidance",
                proposed_content=content,
            )
        )
    elif current_phase.casefold() not in agents.content.casefold():
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.UPDATE,
                path=agents.path,
                reason="current phase appears stale or missing",
                proposed_content=_replace_current_phase(agents.content, current_phase),
            )
        )
    else:
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.KEEP,
                path=agents.path,
                reason="agent guidance already reflects current phase",
            )
        )

    status = paths.get("status.md") or paths.get("docs/status.md")
    if status is None:
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.CREATE,
                path="docs/STATUS.md",
                reason="missing concise current-state handoff",
                proposed_content=f"# Status\n\n## Current phase\n\n{current_phase}\n",
            )
        )
    elif current_phase.casefold() not in status.content.casefold():
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.UPDATE,
                path=status.path,
                reason="status file does not reflect current phase",
                proposed_content=_replace_current_phase(status.content, current_phase),
            )
        )
    else:
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.KEEP,
                path=status.path,
                reason="status file already reflects current phase",
            )
        )

    normalized: dict[str, str] = {}
    for document in documents:
        compact = " ".join(document.content.split()).casefold()
        if compact:
            if compact in normalized:
                warnings.append(
                    f"duplicate context: {document.path} duplicates {normalized[compact]}"
                )
            else:
                normalized[compact] = document.path
        if len(document.content) > _MAX_CONTEXT_FILE_CHARS:
            warnings.append(
                f"context file may be bloated: {document.path} ({len(document.content)} chars)"
            )

    return WorkspacePlan(changes=tuple(changes), warnings=tuple(warnings))

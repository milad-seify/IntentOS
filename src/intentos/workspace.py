from __future__ import annotations

from .models import ContextDocument, WorkspaceAction, WorkspaceChange, WorkspacePlan


_MAX_CONTEXT_FILE_CHARS = 12000
_PHASE_HEADING = "## Current phase"


def _canonical_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./").casefold()


def _by_path(documents: tuple[ContextDocument, ...]) -> dict[str, ContextDocument]:
    return {_canonical_path(document.path): document for document in documents}


def _current_phase_value(content: str) -> str | None:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip().casefold() != _PHASE_HEADING.casefold():
            continue
        for candidate in lines[index + 1 :]:
            stripped = candidate.strip()
            if stripped.startswith("## "):
                return None
            if stripped:
                return stripped
        return None
    return None


def _replace_current_phase(content: str, current_phase: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip().casefold() != _PHASE_HEADING.casefold():
            continue

        next_heading = len(lines)
        for position in range(index + 1, len(lines)):
            if lines[position].strip().startswith("## "):
                next_heading = position
                break

        for position in range(index + 1, next_heading):
            if lines[position].strip():
                lines[position] = current_phase
                return "\n".join(lines).rstrip() + "\n"

        lines.insert(index + 1, "")
        lines.insert(index + 2, current_phase)
        return "\n".join(lines).rstrip() + "\n"

    return content.rstrip() + f"\n\n{_PHASE_HEADING}\n\n{current_phase}\n"


def plan_agent_workspace(
    documents: tuple[ContextDocument, ...],
    *,
    current_phase: str,
) -> WorkspacePlan:
    phase = current_phase.strip()
    if not phase:
        raise ValueError("current_phase must not be empty")

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
            f"## Current phase\n\n{phase}\n"
        )
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.CREATE,
                path="AGENTS.md",
                reason="missing primary agent guidance",
                proposed_content=content,
            )
        )
    elif _current_phase_value(agents.content) != phase:
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.UPDATE,
                path=agents.path,
                reason="current phase appears stale or missing",
                proposed_content=_replace_current_phase(agents.content, phase),
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
                proposed_content=f"# Status\n\n## Current phase\n\n{phase}\n",
            )
        )
    elif _current_phase_value(status.content) != phase:
        changes.append(
            WorkspaceChange(
                action=WorkspaceAction.UPDATE,
                path=status.path,
                reason="status file does not reflect current phase",
                proposed_content=_replace_current_phase(status.content, phase),
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

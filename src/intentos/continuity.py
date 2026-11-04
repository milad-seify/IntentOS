"""Revision-pinned, proposal-only project-state/decision continuity.

This internal implementation makes no filesystem, GitHub, agent or network writes.
Caller-supplied evidence is *referenced*, never claimed independently verified.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from .compass import review_project_compass
from .models import ContextDocument


_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_DECISION = re.compile(r"^D-\d{3,}$")
_HEADING = re.compile(r"^## (.+?)\s*$", re.IGNORECASE)
_SAFE_TEXT_MAX = 240
_MAX_DOCUMENTS = 32
_MAX_CONTEXT_CHARS = 36000


@dataclass(frozen=True, slots=True)
class ContinuityProposal:
    """UPDATE/KEEP/NEEDS_REVIEW advisory, not an approval or applied change."""

    action: str
    path: str
    expected_blob_sha: str
    proposed_content: str | None
    reasons: tuple[str, ...]
    evidence_refs: tuple[str, ...] = ()
    requires_human_approval: bool = True


def git_blob_sha(content: str) -> str:
    """Compute SHA-1 blob ID for the exact supplied UTF-8 file content."""
    raw = content.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _proposal(
    action: str,
    document: ContextDocument,
    expected_blob_sha: str,
    reason: str,
    proposed: str | None = None,
    refs: tuple[str, ...] = (),
) -> ContinuityProposal:
    return ContinuityProposal(action, document.path, expected_blob_sha, proposed, (reason,), refs)


def _validate_source(document: ContextDocument, expected_blob_sha: str) -> str | None:
    if not _SHA1.fullmatch(expected_blob_sha):
        return "Expected Git blob SHA must be a 40-character lowercase hex digest."
    if git_blob_sha(document.content) != expected_blob_sha:
        return "Supplied file content does not match expected Git blob SHA; review source revision."
    if not document.path.strip():
        return "A non-empty project-relative source path is required."
    if len(document.content) > 12000:
        return "Source document exceeds the bounded 12000-character continuity limit."
    return None


def _safe_value(value: str | None) -> bool:
    return (
        value is None or (
            bool(value.strip())
            and len(value) <= _SAFE_TEXT_MAX
            and "\n" not in value
            and "\r" not in value
            and not value.lstrip().startswith(("#", "-", "*", ">"))
            and "\x00" not in value
        )
    )


def _safe_reference(value: str) -> bool:
    return bool(value.strip()) and len(value) <= 500 and not any(
        ord(char) < 32 or ord(char) == 127 for char in value
    )


def _replace_single_fact(content: str, title: str, replacement: str) -> tuple[str | None, str]:
    """Only replace an unambiguous one-line value; preserve every other section."""
    lines = content.splitlines(keepends=True)
    headings = [
        (index, match.group(1).casefold().strip())
        for index, line in enumerate(lines)
        if (match := _HEADING.fullmatch(line.rstrip("\r\n")))
    ]
    locations = [index for index, name in headings if name == title.casefold()]
    if len(locations) != 1:
        return None, f"Expected exactly one '## {title}' heading; no safe proposal."
    index = locations[0]
    end = next((idx for idx, _ in headings if idx > index), len(lines))
    populated = [idx for idx in range(index + 1, end) if lines[idx].strip()]
    if len(populated) != 1 or lines[populated[0]].lstrip().startswith(("-", "*", "#")):
        return None, f"'## {title}' is not a single-line fact; manual review required."
    old = lines[populated[0]].rstrip("\r\n")
    if old == replacement:
        return content, ""
    newline = "\r\n" if lines[populated[0]].endswith("\r\n") else "\n"
    if not lines[populated[0]].endswith(("\n", "\r\n")):
        newline = ""
    lines[populated[0]] = replacement + newline
    return "".join(lines), ""


def propose_status_continuity(
    document: ContextDocument,
    *,
    expected_blob_sha: str,
    evidence_refs: tuple[str, ...],
    new_current_phase: str | None = None,
    new_next_action: str | None = None,
    related_documents: tuple[ContextDocument, ...] = (),
) -> ContinuityProposal:
    """Prepare a revision-guarded Markdown diff, never mutate or validate remote Git.

    Must be explicitly approved by the owner before an external writer may apply.
    A lack of evidence or conflicting authority produces NEEDS_REVIEW, never UPDATE.
    """
    error = _validate_source(document, expected_blob_sha)
    if error:
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, error)
    if new_current_phase is None and new_next_action is None:
        return _proposal("KEEP", document, expected_blob_sha, "No new state was requested.")
    if not _safe_value(new_current_phase) or not _safe_value(new_next_action):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "New state must be a bounded single plain-text line.")
    if not evidence_refs or any(not _safe_reference(ref) for ref in evidence_refs):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Missing or invalid externally reviewed evidence references.")
    if len(related_documents) + 1 > _MAX_DOCUMENTS or sum(len(x.content) for x in (document, *related_documents)) > _MAX_CONTEXT_CHARS:
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Related context exceeds bounded input limits.")
    paths = [x.path.replace("\\", "/").casefold() for x in (document, *related_documents)]
    if len(set(paths)) != len(paths):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Duplicate context paths require review.")
    report = review_project_compass((document, *related_documents))
    if new_current_phase is not None and report.field("current_phase").status in ("unresolved", "stale"):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Current phase sources conflict or are explicitly stale.")
    if new_next_action is not None and report.field("next_action").status in ("unresolved", "stale"):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Next-action sources conflict or are explicitly stale.")
    proposed = document.content
    for field, value in (("Current phase", new_current_phase), ("Next action", new_next_action)):
        if value is not None:
            changed, reason = _replace_single_fact(proposed, field, value.strip())
            if changed is None:
                return _proposal("NEEDS_REVIEW", document, expected_blob_sha, reason)
            proposed = changed
    if proposed == document.content:
        return _proposal("KEEP", document, expected_blob_sha, "Supplied state is already current.", refs=evidence_refs)
    return _proposal(
        "UPDATE",
        document,
        expected_blob_sha,
        "Review exact revision and external evidence before applying proposed state update.",
        proposed,
        evidence_refs,
    )


def propose_decision_append(
    document: ContextDocument,
    *,
    expected_blob_sha: str,
    decision_id: str,
    title: str,
    decision_body: str,
    approval_ref: str,
) -> ContinuityProposal:
    """Propose an append-only, explicitly approved durable decision."""
    error = _validate_source(document, expected_blob_sha)
    if error:
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, error)
    if not _DECISION.fullmatch(decision_id):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Invalid decision ID.")
    if not _safe_value(title) or not _safe_value(decision_body):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Decision text must be single-line plain text.")
    if not _safe_reference(approval_ref):
        return _proposal("NEEDS_REVIEW", document, expected_blob_sha, "Human-approved evidence reference is required.")
    if re.search(rf"^## {re.escape(decision_id)}(?:\s|$)", document.content, flags=re.MULTILINE):
        return _proposal("KEEP", document, expected_blob_sha, "Decision ID exists; never overwrite accepted history.", refs=(approval_ref,))
    proposed = document.content.rstrip("\r\n") + (
        f"\n\n## {decision_id} — {title.strip()}\n\n"
        f"**Approval evidence:** {approval_ref.strip()}\n\n"
        f"{decision_body.strip()}\n"
    )
    return _proposal(
        "UPDATE", document, expected_blob_sha,
        "Append-only decision proposal; verify approval and exact source revision before applying.",
        proposed, (approval_ref,),
    )

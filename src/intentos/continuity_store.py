"""Approved local application of reviewed continuity proposals.

Only the two known project documents can be changed. A caller must review the
exact proposed content and supply its digest as an explicit approval assertion.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat
import tempfile

from .continuity import ContinuityProposal, git_blob_sha


_ALLOWED_PATHS = {"docs/STATUS.md", "docs/DECISIONS.md"}


class ContinuityConflict(ValueError):
    """The reviewed source revision no longer matches the on-disk document."""


@dataclass(frozen=True, slots=True)
class ContinuityApplyResult:
    status: str  # applied | already_applied
    path: str
    blob_sha: str


def proposal_approval_digest(proposal: ContinuityProposal) -> str:
    """Bind an approval to the exact path, old revision, new text and evidence."""
    if proposal.action != "UPDATE" or proposal.proposed_content is None:
        raise ValueError("only a reviewed UPDATE proposal can be approved")
    data = json.dumps(
        [proposal.action, proposal.path, proposal.expected_blob_sha,
         proposal.proposed_content, proposal.reasons, proposal.evidence_refs,
         proposal.requires_human_approval, proposal.related_source_fingerprints],
        ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _check_related_sources(root: Path, proposal: ContinuityProposal) -> None:
    if len(proposal.related_source_fingerprints) > 31:
        raise ValueError("too many related continuity sources")
    for label, expected_sha in proposal.related_source_fingerprints:
        relative = Path(label.replace("\\", "/"))
        if relative.is_absolute():
            raise ValueError("related source paths must be project-relative")
        source = (root / relative).resolve(strict=True)
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError("related source must be a project file")
        if git_blob_sha(source.read_bytes().decode("utf-8")) != expected_sha:
            raise ContinuityConflict("related source changed; regenerate and review the proposal")


def apply_continuity_proposal(
    root: Path,
    proposal: ContinuityProposal,
    *,
    approved_digest: str,
) -> ContinuityApplyResult:
    """Apply an explicitly approved proposal if its source revision is current.

    The exclusive lock serializes IntentOS writers. Other editors do not honor it;
    the source is checked again immediately before replacement. A detected change
    fails closed and requires a new proposal.
    """
    path = proposal.path.replace("\\", "/")
    if path not in _ALLOWED_PATHS:
        raise ValueError("continuity updates are limited to docs/STATUS.md and docs/DECISIONS.md")
    if not proposal.requires_human_approval or not proposal.evidence_refs:
        raise ValueError("an approved proposal with evidence references is required")
    if not hmac.compare_digest(proposal_approval_digest(proposal), approved_digest):
        raise ValueError("approval digest does not match the reviewed proposal")

    project_root = Path(root).resolve(strict=True)
    directory = project_root / "docs"
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("project docs directory must be a real directory")
    target = directory / Path(path).name
    if target.is_symlink() or not target.is_file():
        raise ValueError("continuity target must be an existing regular file")

    lock = directory / f".{target.name}.intentos.lock"
    try:
        lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ContinuityConflict("another continuity update holds the document lock") from error
    temporary: Path | None = None
    try:
        os.close(lock_fd)
        _check_related_sources(project_root, proposal)
        current = target.read_bytes()
        current_sha = git_blob_sha(current.decode("utf-8"))
        proposed_bytes = proposal.proposed_content.encode("utf-8")
        proposed_sha = git_blob_sha(proposal.proposed_content)
        if current_sha == proposed_sha:
            return ContinuityApplyResult("already_applied", path, current_sha)
        if current_sha != proposal.expected_blob_sha:
            raise ContinuityConflict("source document changed; regenerate and review the proposal")

        with tempfile.NamedTemporaryFile(prefix=f".{target.name}.intentos-", dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(proposed_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, stat.S_IMODE(target.stat().st_mode))
        if git_blob_sha(target.read_bytes().decode("utf-8")) != proposal.expected_blob_sha:
            raise ContinuityConflict("source document changed during application")
        _check_related_sources(project_root, proposal)
        os.replace(temporary, target)
        temporary = None
        if os.name != "nt":
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        return ContinuityApplyResult("applied", path, proposed_sha)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)

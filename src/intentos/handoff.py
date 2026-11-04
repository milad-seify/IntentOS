"""Portable, execution-neutral agent handoffs and safe restart checkpoints.

No external tool is invoked; an executor must separately verify its own approvals.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from .models import PromptResult


_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")


@dataclass(frozen=True, slots=True)
class VerifiedStep:
    step_id: str
    evidence_ref: str
    accepted_by_owner: bool = False


@dataclass(frozen=True, slots=True)
class TaskCheckpoint:
    schema_version: int
    task_id: str
    source_revision: str
    next_step_id: str
    completed: tuple[VerifiedStep, ...]
    operation_ids: tuple[str, ...] = ()
    required_approval_ids: tuple[str, ...] = ()
    context_digest: str = ""
    estimated_remaining_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class ResumeReview:
    status: str  # ready_for_owner_review | blocked | needs_review
    task_id: str
    next_step_id: str
    reasons: tuple[str, ...]
    approved_to_execute: bool = False


@dataclass(frozen=True, slots=True)
class AgentHandoff:
    schema_version: int
    task_id: str
    target_tool: str
    source_revision: str
    prepared_prompt: str
    next_step_id: str
    context_digest: str
    requires_owner_approval: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "target_tool": self.target_tool,
            "source_revision": self.source_revision,
            "prepared_prompt": self.prepared_prompt,
            "next_step_id": self.next_step_id,
            "context_digest": self.context_digest,
            "requires_owner_approval": self.requires_owner_approval,
        }


def _key(value: str) -> bool:
    return bool(_KEY.fullmatch(value))


def make_checkpoint(
    *,
    task_id: str,
    source_revision: str,
    next_step_id: str,
    completed: tuple[VerifiedStep, ...] = (),
    operation_ids: tuple[str, ...] = (),
    required_approval_ids: tuple[str, ...] = (),
    context_text: str = "",
    estimated_remaining_tokens: int | None = None,
) -> TaskCheckpoint:
    if not all(_key(item) for item in (task_id, source_revision, next_step_id)):
        raise ValueError("task, source revision and next step must be bounded identifiers")
    ids = [step.step_id for step in completed]
    if len(set(ids)) != len(ids) or any(not _key(i) for i in ids):
        raise ValueError("completed step IDs must be unique and valid")
    if any(not step.evidence_ref.strip() or len(step.evidence_ref) > 500 for step in completed):
        raise ValueError("completed steps need bounded external evidence references")
    if any(not step.accepted_by_owner for step in completed):
        raise ValueError("unapproved completed steps cannot be promoted to a checkpoint")
    if next_step_id in ids:
        raise ValueError("a completed step cannot also be the next step")
    for group in (operation_ids, required_approval_ids):
        if len(group) != len(set(group)) or any(not _key(v) for v in group):
            raise ValueError("operation/approval IDs must be unique and bounded")
    if estimated_remaining_tokens is not None and (estimated_remaining_tokens < 0 or estimated_remaining_tokens > 10**9):
        raise ValueError("token estimate must be a nonnegative bounded user-supplied quantity")
    if len(context_text) > 36000 or len(completed) > 128 or len(operation_ids) > 128:
        raise ValueError("checkpoint exceeds bounded input limits")
    digest = hashlib.sha256(context_text.encode("utf-8")).hexdigest()
    return TaskCheckpoint(
        1, task_id, source_revision, next_step_id, completed,
        operation_ids, required_approval_ids, digest, estimated_remaining_tokens,
    )


def review_resume(
    checkpoint: TaskCheckpoint,
    *,
    current_source_revision: str,
    already_executed_operation_ids: tuple[str, ...] = (),
    externally_accepted_approval_ids: tuple[str, ...] = (),
    current_context_digest: str | None = None,
) -> ResumeReview:
    """Require human review even if all caller-supplied preconditions match.

    This cannot verify actual filesystem state, external permissions or task success.
    """
    reasons: list[str] = []
    if checkpoint.schema_version != 1 or not _key(checkpoint.task_id):
        reasons.append("Unsupported or malformed checkpoint.")
    if checkpoint.source_revision != current_source_revision:
        reasons.append("Source revision changed; re-evaluate task before resuming.")
    if current_context_digest is not None and current_context_digest != checkpoint.context_digest:
        reasons.append("Context fingerprint changed; review before resuming.")
    if set(checkpoint.operation_ids).intersection(already_executed_operation_ids):
        reasons.append("A checkpoint operation may already have executed; never replay blindly.")
    if any(not step.accepted_by_owner or not step.evidence_ref for step in checkpoint.completed):
        reasons.append("A claimed completed step lacks approval or evidence.")
    if not set(checkpoint.required_approval_ids).issubset(externally_accepted_approval_ids):
        reasons.append("Required external approvals have not all been supplied.")
    if reasons:
        return ResumeReview("blocked", checkpoint.task_id, checkpoint.next_step_id, tuple(reasons))
    return ResumeReview(
        "ready_for_owner_review", checkpoint.task_id, checkpoint.next_step_id,
        ("All supplied revision/duplicate/approval checks passed; executor and owner must verify runtime state.",),
    )


def build_agent_handoff(
    result: PromptResult,
    checkpoint: TaskCheckpoint,
    *,
    target_tool: str,
) -> AgentHandoff:
    """Create a reviewable target-adaptable payload, never execute/send implicitly."""
    if result.needs_clarification or not result.prompt:
        raise ValueError("cannot hand off unresolved intent")
    if not target_tool.strip() or len(target_tool) > 80:
        raise ValueError("target tool required")
    if result.intent.target_tool not in ("generic", target_tool):
        # Routing to a different agent requires an explicit new preparation step.
        raise ValueError("target does not match prepared intent; re-prepare for this agent")
    return AgentHandoff(
        1, checkpoint.task_id, target_tool.strip(), checkpoint.source_revision,
        result.prompt, checkpoint.next_step_id, checkpoint.context_digest,
    )

"""Portable, execution-neutral agent handoffs and safe restart checkpoints.

No external tool is invoked; an executor must separately verify its own approvals.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
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
class PlanStep:
    step_id: str
    action: str


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
    approved_plan: tuple[PlanStep, ...] = ()
    plan_approval_ref: str = ""
    state_summary: str = ""
    state_evidence_ref: str = ""

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        for key in ("completed", "approved_plan", "operation_ids", "required_approval_ids"):
            data[key] = list(data[key])
        return data


@dataclass(frozen=True, slots=True)
class ResumeReview:
    status: str  # ready_for_owner_review | blocked | needs_review
    task_id: str
    next_step_id: str
    reasons: tuple[str, ...]
    approved_to_execute: bool = False
    budget_status: str = "unknown"


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


def _short_line(value: str, limit: int = 500) -> bool:
    return bool(value.strip()) and len(value) <= limit and not any(
        char in "\n\r\v\f\x85\u2028\u2029" or ord(char) < 32 or ord(char) == 127
        for char in value
    )


def _validate_checkpoint(checkpoint: TaskCheckpoint) -> None:
    if type(checkpoint.schema_version) is not int or checkpoint.schema_version != 1:
        raise ValueError("unsupported checkpoint schema")
    if not all(_key(item) for item in (checkpoint.task_id, checkpoint.source_revision, checkpoint.next_step_id)):
        raise ValueError("task, source revision and next step must be bounded identifiers")
    if not checkpoint.approved_plan or len(checkpoint.approved_plan) > 128:
        raise ValueError("checkpoint needs a bounded approved plan")
    plan_ids = [step.step_id for step in checkpoint.approved_plan]
    if len(set(plan_ids)) != len(plan_ids) or any(not _key(step.step_id) or not _short_line(step.action) for step in checkpoint.approved_plan):
        raise ValueError("plan steps need unique IDs and bounded actions")
    if checkpoint.next_step_id not in plan_ids:
        raise ValueError("next step must be part of the approved plan")
    if not all(_short_line(item) for item in (checkpoint.plan_approval_ref, checkpoint.state_summary, checkpoint.state_evidence_ref)):
        raise ValueError("approved plan and project state need bounded evidence")
    completed_ids = [step.step_id for step in checkpoint.completed]
    if (len(set(completed_ids)) != len(completed_ids)
            or any(step.step_id not in plan_ids or not _short_line(step.evidence_ref)
                   or step.accepted_by_owner is not True for step in checkpoint.completed)):
        raise ValueError("completed steps need unique approved plan IDs and evidence")
    if checkpoint.next_step_id in completed_ids:
        raise ValueError("a completed step cannot also be the next step")
    for group in (checkpoint.operation_ids, checkpoint.required_approval_ids):
        if len(group) != len(set(group)) or any(not _key(value) for value in group):
            raise ValueError("operation/approval IDs must be unique and bounded")
    if (checkpoint.estimated_remaining_tokens is not None
            and (type(checkpoint.estimated_remaining_tokens) is not int
                 or not 0 <= checkpoint.estimated_remaining_tokens <= 10**9)):
        raise ValueError("token estimate must be a nonnegative bounded user-supplied quantity")
    if len(checkpoint.completed) > 128 or len(checkpoint.operation_ids) > 128 or len(checkpoint.required_approval_ids) > 128:
        raise ValueError("checkpoint exceeds bounded input limits")
    if not re.fullmatch(r"[0-9a-f]{64}", checkpoint.context_digest):
        raise ValueError("checkpoint context digest must be SHA-256")


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
    approved_plan: tuple[PlanStep, ...] = (),
    plan_approval_ref: str = "",
    state_summary: str = "",
    state_evidence_ref: str = "",
) -> TaskCheckpoint:
    if len(context_text) > 36000:
        raise ValueError("checkpoint exceeds bounded input limits")
    digest = hashlib.sha256(context_text.encode("utf-8")).hexdigest()
    checkpoint = TaskCheckpoint(
        1, task_id, source_revision, next_step_id, completed,
        operation_ids, required_approval_ids, digest, estimated_remaining_tokens,
        approved_plan, plan_approval_ref, state_summary, state_evidence_ref,
    )
    _validate_checkpoint(checkpoint)
    return checkpoint


def checkpoint_from_dict(data: dict[str, object]) -> TaskCheckpoint:
    """Load a portable checkpoint, rejecting missing or malformed approval claims."""
    if not isinstance(data, dict):
        raise ValueError("checkpoint must be an object")
    for key in ("completed", "approved_plan", "operation_ids", "required_approval_ids"):
        if key in data and not isinstance(data[key], list):
            raise ValueError(f"{key} must be a list")
    try:
        completed = tuple(VerifiedStep(**item) for item in data["completed"])
        plan = tuple(PlanStep(**item) for item in data["approved_plan"])
        checkpoint = TaskCheckpoint(
            schema_version=data["schema_version"], task_id=data["task_id"],
            source_revision=data["source_revision"], next_step_id=data["next_step_id"],
            completed=completed, operation_ids=tuple(data.get("operation_ids", ())),
            required_approval_ids=tuple(data.get("required_approval_ids", ())),
            context_digest=data["context_digest"],
            estimated_remaining_tokens=data.get("estimated_remaining_tokens"),
            approved_plan=plan, plan_approval_ref=data["plan_approval_ref"],
            state_summary=data["state_summary"], state_evidence_ref=data["state_evidence_ref"],
        )
        _validate_checkpoint(checkpoint)
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("checkpoint is malformed") from error
    return checkpoint


def review_resume(
    checkpoint: TaskCheckpoint,
    *,
    current_source_revision: str,
    already_executed_operation_ids: tuple[str, ...] | None = None,
    externally_accepted_approval_ids: tuple[str, ...] = (),
    current_context_digest: str | None = None,
    remaining_budget_tokens: int | None = None,
) -> ResumeReview:
    """Require human review even if all caller-supplied preconditions match.

    This cannot verify actual filesystem state, external permissions or task success.
    """
    reasons: list[str] = []
    budget_status = "unknown"
    try:
        _validate_checkpoint(checkpoint)
    except (ValueError, TypeError, AttributeError):
        return ResumeReview(
            "blocked", str(getattr(checkpoint, "task_id", "")),
            str(getattr(checkpoint, "next_step_id", "")),
            ("Unsupported or malformed checkpoint.",),
        )
    if checkpoint.source_revision != current_source_revision:
        reasons.append("Source revision changed; re-evaluate task before resuming.")
    if current_context_digest is None:
        reasons.append("Current context fingerprint was not supplied.")
    elif current_context_digest != checkpoint.context_digest:
        reasons.append("Context fingerprint changed; review before resuming.")
    if already_executed_operation_ids is None and checkpoint.operation_ids:
        reasons.append("External operation ledger was not supplied; replay safety is unknown.")
    elif set(checkpoint.operation_ids).intersection(already_executed_operation_ids or ()):
        reasons.append("A checkpoint operation may already have executed; never replay blindly.")
    if any(not step.accepted_by_owner or not step.evidence_ref for step in checkpoint.completed):
        reasons.append("A claimed completed step lacks approval or evidence.")
    if not set(checkpoint.required_approval_ids).issubset(externally_accepted_approval_ids):
        reasons.append("Required external approvals have not all been supplied.")
    if remaining_budget_tokens is not None:
        if type(remaining_budget_tokens) is not int or remaining_budget_tokens < 0:
            reasons.append("Supplied remaining token budget must be a nonnegative integer.")
        elif checkpoint.estimated_remaining_tokens is None:
            budget_status = "estimate_unavailable"
        elif checkpoint.estimated_remaining_tokens > remaining_budget_tokens:
            budget_status = "estimate_over_budget"
            reasons.append("Estimated remaining work exceeds the supplied token budget; split or re-plan before resuming.")
        else:
            budget_status = "estimate_within_supplied_budget"
    if reasons:
        return ResumeReview("blocked", checkpoint.task_id, checkpoint.next_step_id, tuple(reasons), budget_status=budget_status)
    return ResumeReview(
        "ready_for_owner_review", checkpoint.task_id, checkpoint.next_step_id,
        ("All supplied revision/duplicate/approval checks passed; executor and owner must verify runtime state.",),
        budget_status=budget_status,
    )


def build_agent_handoff(
    result: PromptResult,
    checkpoint: TaskCheckpoint,
    *,
    target_tool: str,
) -> AgentHandoff:
    """Create a reviewable target-adaptable payload, never execute/send implicitly."""
    _validate_checkpoint(checkpoint)
    return make_agent_handoff(
        result, target_tool=target_tool, task_id=checkpoint.task_id,
        source_revision=checkpoint.source_revision, next_step_id=checkpoint.next_step_id,
        context_digest=checkpoint.context_digest,
    )


def make_agent_handoff(
    result: PromptResult, *, target_tool: str, task_id: str,
    source_revision: str, next_step_id: str, context_digest: str,
) -> AgentHandoff:
    """Build a portable handoff without granting an executor permission to act."""
    if result.needs_clarification or not result.prompt:
        raise ValueError("cannot hand off unresolved intent")
    if not target_tool.strip() or len(target_tool) > 80 or not _key(task_id) or not _key(source_revision) or not _key(next_step_id):
        raise ValueError("target tool required")
    if result.intent.target_tool not in ("generic", target_tool):
        # Routing to a different agent requires an explicit new preparation step.
        raise ValueError("target does not match prepared intent; re-prepare for this agent")
    if len(result.prompt) > 36000 or not re.fullmatch(r"[0-9a-f]{64}", context_digest):
        raise ValueError("handoff prompt or context digest is invalid")
    return AgentHandoff(
        1, task_id, target_tool.strip(), source_revision,
        result.prompt, next_step_id, context_digest,
    )


def handoff_from_dict(data: dict[str, object]) -> AgentHandoff:
    """Load a saved handoff with the same bounds used for new packets."""
    if not isinstance(data, dict):
        raise ValueError("handoff must be an object")
    try:
        packet = AgentHandoff(**data)
        if (type(packet.schema_version) is not int or packet.schema_version != 1
                or packet.requires_owner_approval is not True
                or not _key(packet.task_id) or not _key(packet.source_revision)
                or not _key(packet.next_step_id) or not isinstance(packet.target_tool, str)
                or not packet.target_tool.strip() or len(packet.target_tool) > 80
                or not isinstance(packet.prepared_prompt, str)
                or not packet.prepared_prompt.strip() or len(packet.prepared_prompt) > 36000
                or not re.fullmatch(r"[0-9a-f]{64}", packet.context_digest)):
            raise ValueError("handoff is malformed or unsupported")
        return packet
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("handoff is malformed") from error

"""Read-only project scope, milestone and launch evidence gates.

Source assertions come from the caller; status never grants execution permission.
No file mutation, provider inference, autonomous execution or launch approval.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from .compass import review_project_compass
from .models import ContextDocument


_TOKEN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,79}$")


@dataclass(frozen=True, slots=True)
class MilestoneRequirement:
    key: str
    outcome: str
    checks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CheckEvidence:
    requirement_key: str
    check: str
    passed: bool | None
    source_ref: str
    source_revision: str
    independently_reviewed: bool = False


@dataclass(frozen=True, slots=True)
class Milestone:
    key: str
    requirement_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GateFinding:
    key: str
    status: str  # passed | failed | missing | needs_review
    reason: str
    evidence_ref: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectGateReview:
    status: str  # blocked | needs_review | ready_for_owner_review
    findings: tuple[GateFinding, ...]
    launch_approved: bool = False  # never implied by successful checklist


@dataclass(frozen=True, slots=True)
class ScopeGate:
    status: str  # in_scope | out_of_scope | needs_review
    reason: str
    source_paths: tuple[str, ...]
    requires_owner_approval: bool = True


def review_scope_gate(
    sources: tuple[ContextDocument, ...],
    *,
    requested_task: str,
) -> ScopeGate:
    """Conservatively classify a new task against explicitly supplied scope docs."""
    result = review_project_compass(sources, proposed_task=requested_task)
    scope = result.task_scope
    if scope.status == "in_scope":
        status = "in_scope"
        reason = "Exact caller-designated-authoritative in-scope match; separate risk approval still applies."
    elif scope.status == "out_of_scope":
        status = "out_of_scope"
        reason = "Explicit out-of-scope match. Request owner-approved scope amendment."
    else:
        status = "needs_review"
        reason = scope.explanation
    return ScopeGate(status, reason, tuple(dict.fromkeys(f.path for f in scope.evidence)))


def review_project_gates(
    requirements: tuple[MilestoneRequirement, ...],
    milestones: tuple[Milestone, ...],
    evidence: tuple[CheckEvidence, ...],
) -> ProjectGateReview:
    """Trace every requirement/check to externally reviewed evidence, then stop at owner review.

    Caller-provided 'independently_reviewed=True' is an assertion, not independent
    verification performed by this function. No positive output is launch approval.
    """
    if len(requirements) > 128 or len(milestones) > 64 or len(evidence) > 512:
        raise ValueError("project gate inputs exceed bounded limits")
    keys = [req.key for req in requirements]
    if len(set(keys)) != len(keys) or any(not _TOKEN.fullmatch(x) for x in keys):
        raise ValueError("requirements require unique bounded IDs")
    milekeys = [x.key for x in milestones]
    if len(set(milekeys)) != len(milekeys) or any(not _TOKEN.fullmatch(x) for x in milekeys):
        raise ValueError("milestones require unique bounded IDs")
    if not milestones or not requirements:
        return ProjectGateReview("blocked", (GateFinding("project", "missing", "No accepted requirements or milestones supplied."),))
    requirements_by_key = {x.key: x for x in requirements}
    findings: list[GateFinding] = []
    mapped = set()
    for milestone in milestones:
        if not milestone.requirement_keys:
            findings.append(GateFinding(milestone.key, "missing", "Milestone has no mapped requirements."))
        for key in milestone.requirement_keys:
            if key not in requirements_by_key:
                findings.append(GateFinding(f"{milestone.key}:{key}", "missing", "Unknown requirement referenced by milestone."))
                continue
            mapped.add(key)
    for key in sorted(set(keys) - mapped):
        findings.append(GateFinding(key, "missing", "Approved requirement is not mapped to a milestone."))
    by_check: dict[tuple[str, str], list[CheckEvidence]] = {}
    for item in evidence:
        by_check.setdefault((item.requirement_key, item.check), []).append(item)
    for req in requirements:
        if not req.outcome.strip() or not req.checks or len(set(req.checks)) != len(req.checks):
            findings.append(GateFinding(req.key, "missing", "Requirement has no usable outcome or unique acceptance checks."))
        for check in req.checks:
            key = (req.key, check)
            supplied = by_check.get(key, [])
            if not supplied:
                findings.append(GateFinding(f"{req.key}:{check}", "missing", "No check evidence was supplied."))
            elif len(supplied) > 1:
                findings.append(GateFinding(f"{req.key}:{check}", "needs_review", "Conflicting or duplicate evidence; reconcile externally."))
            else:
                item = supplied[0]
                label = f"{req.key}:{check}"
                if not item.source_ref.strip() or not item.source_revision.strip() or not item.independently_reviewed or item.passed is None:
                    findings.append(GateFinding(label, "needs_review", "Evidence is unreviewed, unpinned or inconclusive.", item.source_ref or None))
                elif not item.passed:
                    findings.append(GateFinding(label, "failed", "Check failed; milestone is not ready.", item.source_ref))
                else:
                    findings.append(GateFinding(label, "passed", "Caller states this check has verified external evidence.", item.source_ref))
    allowed = {(r.key, check) for r in requirements for check in r.checks}
    for key in sorted(set(by_check) - allowed):
        findings.append(GateFinding(":".join(key), "needs_review", "Evidence refers to an unapproved check."))
    statuses = {f.status for f in findings}
    if "failed" in statuses or "missing" in statuses:
        state = "blocked"
    elif "needs_review" in statuses:
        state = "needs_review"
    else:
        state = "ready_for_owner_review"
    return ProjectGateReview(state, tuple(findings))

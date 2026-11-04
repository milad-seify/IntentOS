from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .compass import review_project_compass
from .codex_adapter import run_codex_handoff
from .continuity import git_blob_sha, propose_decision_append, propose_scope_amendment, propose_status_continuity
from .continuity_store import apply_continuity_proposal, proposal_approval_digest
from .governance import CheckEvidence, Milestone, MilestoneRequirement, review_project_gates
from .handoff import PlanStep, VerifiedStep, checkpoint_from_dict, handoff_from_dict, make_agent_handoff, make_checkpoint, review_resume
from .models import CapabilityClass, ContextDocument, CostClass, IntentRequest, ModelMetadata
from .project import optimize_project_prompt
from .result_contract import RESULT_SCHEMA_VERSION, error_dict, result_dict
from .router import review_route
from .service import optimize_prompt
from .skills import build_skill_artifact
from .workspace import plan_agent_workspace


_AUTHORITATIVE_NAMES = {"AGENTS.md", "STATUS.md", "DECISIONS.md", "ARCHITECTURE.md"}


def _load_documents(paths: Sequence[str]) -> tuple[ContextDocument, ...]:
    documents: list[ContextDocument] = []
    for raw_path in paths:
        path = Path(raw_path)
        content = path.read_text(encoding="utf-8")
        documents.append(
            ContextDocument(
                path=str(path),
                content=content,
                authoritative=path.name in _AUTHORITATIVE_NAMES,
            )
        )
    return tuple(documents)


def _add_intent_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("text", help="Raw user intent.")
    parser.add_argument("--target", help="Target tool, e.g. codex, chatgpt, claude-code. Omit to detect from the request.")
    parser.add_argument("--constraint", action="append", default=[], help="Constraint; repeatable.")
    parser.add_argument("--success", action="append", default=[], help="Success criterion; repeatable.")
    parser.add_argument("--context-file", action="append", default=[], help="Project context file; repeatable.")
    parser.add_argument("--output-format", help="Required output format, e.g. JSON or Markdown.")
    parser.add_argument("--audience", help="Intended audience for the generated result.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intentos",
        description="Engineer rough intent into bounded AI execution contracts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    optimize = subparsers.add_parser("optimize", help="Optimize a request for an AI tool or agent.")
    _add_intent_arguments(optimize)
    optimize.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    skill = subparsers.add_parser("skill", help="Compile intent and policy into a portable SKILL.md artifact.")
    _add_intent_arguments(skill)
    skill.add_argument("--name", help="Skill name; normalized to the Agent Skills naming rules.")
    skill.add_argument("--description", help="Skill description; max 1024 characters.")
    skill.add_argument("--json", action="store_true", help="Emit artifact metadata and content as JSON.")

    workspace = subparsers.add_parser("workspace", help="Plan safe agent-context file maintenance.")
    workspace.add_argument("--phase", required=True, help="Current project phase/status text.")
    workspace.add_argument("--document", action="append", default=[], help="Existing context document; repeatable.")
    workspace.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    compass = subparsers.add_parser("compass", help="Review supplied project goals, state, and scope.")
    compass.add_argument("--document", action="append", default=[], help="Project document; repeatable.")
    compass.add_argument(
        "--authoritative-document", action="append", default=[],
        help="Project document explicitly designated as authoritative; repeatable.",
    )
    compass.add_argument("--task", default="", help="Optional task to compare with explicit scope items.")
    compass.add_argument("--json", action="store_true", help="Emit machine-readable review evidence.")

    state = subparsers.add_parser("state", help="Review or apply an approved project-state update.")
    state_actions = state.add_subparsers(dest="state_action", required=True)
    for action in ("status", "decision", "scope"):
        action_parser = state_actions.add_parser(action)
        action_parser.add_argument("--root", default=".", help="Project root containing docs/STATUS.md and docs/DECISIONS.md.")
        action_parser.add_argument("--approve-digest", help="Apply only the exact proposal digest reviewed by the owner.")
        action_parser.add_argument("--json", action="store_true", help="Emit machine-readable proposal or apply result.")
        if action == "status":
            action_parser.add_argument("--current-phase", help="New single-line current phase.")
            action_parser.add_argument("--next-action", help="New single-line next action.")
            action_parser.add_argument("--evidence", action="append", default=[], help="External review evidence reference; repeatable.")
            action_parser.add_argument("--related-document", action="append", default=[], help="Additional context for conflict review; repeatable.")
        elif action == "decision":
            action_parser.add_argument("--decision-id", required=True, help="New decision ID, e.g. D-032.")
            action_parser.add_argument("--title", required=True, help="Single-line decision title.")
            action_parser.add_argument("--body", required=True, help="Single-line approved decision text.")
            action_parser.add_argument("--approval-ref", required=True, help="External human approval reference.")
        else:
            action_parser.add_argument("--amendment-id", required=True, help="New scope amendment ID, e.g. S-001.")
            action_parser.add_argument("--task", required=True, help="Exact task to add to approved scope.")
            action_parser.add_argument("--reason", required=True, help="Single-line reason for scope change.")
            action_parser.add_argument("--approval-ref", required=True, help="External owner approval reference.")

    gates = subparsers.add_parser("gates", help="Review requirement, milestone and launch readiness evidence.")
    gates.add_argument("--file", required=True, help="Caller-supplied project gate evidence JSON file.")
    gates.add_argument("--json", action="store_true", help="Emit machine-readable readiness findings.")

    route = subparsers.add_parser("route", help="Review a capability/effort recommendation and supplied model catalog.")
    _add_intent_arguments(route)
    route.add_argument("--models-file", help="Optional caller-supplied model metadata JSON; no provider discovery.")
    route.add_argument("--json", action="store_true", help="Emit machine-readable route review.")

    checkpoint = subparsers.add_parser("checkpoint", help="Save or review an approved task checkpoint.")
    checkpoint_actions = checkpoint.add_subparsers(dest="checkpoint_action", required=True)
    for action in ("create", "review"):
        action_parser = checkpoint_actions.add_parser(action)
        action_parser.add_argument("--root", default=".", help="Git project root.")
        action_parser.add_argument("--context-file", action="append", required=True, help="Pinned project context file; repeatable.")
        action_parser.add_argument("--json", action="store_true", help="Emit machine-readable checkpoint result.")
        if action == "create":
            action_parser.add_argument("--spec", required=True, help="Approved plan and state summary JSON.")
            action_parser.add_argument("--output", required=True, help="New checkpoint JSON path; will not overwrite.")
        else:
            action_parser.add_argument("--checkpoint", required=True, help="Previously saved checkpoint JSON.")
            action_parser.add_argument("--ledger-reviewed", action="store_true", help="Assert external operation ledger was checked.")
            action_parser.add_argument("--executed-operation", action="append", default=[], help="Operation already executed; repeatable.")
            action_parser.add_argument("--accepted-approval", action="append", default=[], help="Externally accepted approval ID; repeatable.")

    handoff = subparsers.add_parser("handoff", help="Prepare or explicitly dispatch a portable agent handoff.")
    handoff_actions = handoff.add_subparsers(dest="handoff_action", required=True)
    prepare = handoff_actions.add_parser("prepare")
    prepare.add_argument("text", help="Raw user task.")
    prepare.add_argument("--root", default=".", help="Git project root.")
    prepare.add_argument("--target", required=True, help="Target agent, e.g. codex or claude-code.")
    prepare.add_argument("--task-id", required=True, help="Bounded task identifier.")
    prepare.add_argument("--constraint", action="append", default=[])
    prepare.add_argument("--success", action="append", default=[])
    prepare.add_argument("--context-file", action="append", default=[], help="Explicit project context file; repeatable.")
    prepare.add_argument("--output", required=True, help="New portable handoff JSON path; will not overwrite.")
    prepare.add_argument("--json", action="store_true")
    dispatch = handoff_actions.add_parser("dispatch")
    dispatch.add_argument("--root", default=".", help="Same Git project root as the prepared packet.")
    dispatch.add_argument("--file", required=True, help="Saved handoff JSON.")
    dispatch.add_argument("--sandbox", choices=("read-only", "workspace-write"), default="read-only")
    dispatch.add_argument("--executable", default="codex", help="Codex CLI executable; included in approval digest.")
    dispatch.add_argument("--approve-digest", help="Exact digest from a reviewed dispatch preview.")
    dispatch.add_argument("--timeout", type=int, default=1800, help="Seconds, 1–3600.")
    dispatch.add_argument("--json", action="store_true")

    return parser


def _request_and_documents(args: argparse.Namespace) -> tuple[IntentRequest, tuple[ContextDocument, ...]]:
    request = IntentRequest.from_values(
        args.text,
        target_tool=args.target,
        output_format=args.output_format,
        constraints=args.constraint,
        audience=args.audience,
        success_criteria=args.success,
    )
    return request, _load_documents(args.context_file)


def _optimize_from_args(args: argparse.Namespace):
    request, documents = _request_and_documents(args)
    return optimize_project_prompt(request, documents) if documents else optimize_prompt(request)


def _run_optimize(args: argparse.Namespace) -> int:
    result = _optimize_from_args(args)

    if args.json:
        print(json.dumps(result_dict(result), indent=2, ensure_ascii=False))
    elif result.needs_clarification:
        for question in result.questions:
            print(f"? {question}")
    else:
        if result.routing:
            print(
                f"Route: {result.routing.required_capability.value} / "
                f"effort={result.routing.effort.value}"
            )
        print(result.prompt or "")
    return 2 if result.needs_clarification else 0


def _run_skill(args: argparse.Namespace) -> int:
    result = _optimize_from_args(args)
    if result.needs_clarification or result.policy is None:
        if args.json:
            print(json.dumps(result_dict(result), indent=2, ensure_ascii=False))
        else:
            for question in result.questions:
                print(f"? {question}")
        return 2

    artifact = build_skill_artifact(
        result.intent,
        result.policy,
        name=args.name,
        description=args.description,
    )
    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": RESULT_SCHEMA_VERSION,
                    "status": "ready",
                    "name": artifact.name,
                    "description": artifact.description,
                    "content": artifact.content,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(artifact.content, end="")
    return 0


def _run_workspace(args: argparse.Namespace) -> int:
    documents = _load_documents(args.document)
    plan = plan_agent_workspace(documents, current_phase=args.phase)
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": "ready",
        "changes": [
            {
                "action": change.action.value,
                "path": change.path,
                "reason": change.reason,
                "proposed_content": change.proposed_content,
            }
            for change in plan.changes
        ],
        "warnings": list(plan.warnings),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for change in plan.changes:
            print(f"{change.action.value.upper():6} {change.path} — {change.reason}")
        for warning in plan.warnings:
            print(f"WARN   {warning}")
    return 0


def _run_compass(args: argparse.Namespace) -> int:
    paths = [(path, False) for path in args.document] + [
        (path, True) for path in args.authoritative_document
    ]
    if not paths:
        raise ValueError("Supply at least one --document or --authoritative-document.")
    documents = tuple(
        ContextDocument(str(Path(path)), Path(path).read_text(encoding="utf-8"), authoritative)
        for path, authoritative in paths
    )
    review = review_project_compass(documents, proposed_task=args.task)

    def fact_payload(fact):
        return {
            "text": fact.text,
            "path": fact.path,
            "line": fact.line,
            "stale": fact.stale,
            "authoritative": fact.authoritative,
        }

    if args.json:
        payload = {
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "review",
            "fields": {
                field.name: {
                    "status": field.status,
                    "value": field.value,
                    "evidence": [fact_payload(fact) for fact in field.evidence],
                }
                for field in review.fields
            },
            "task_scope": {
                "status": review.task_scope.status,
                "explanation": review.task_scope.explanation,
                "scope_review_required": review.task_scope.scope_review_required,
                "evidence": [fact_payload(fact) for fact in review.task_scope.evidence],
            },
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Project Compass — supplied source claims; review before acting")
        for field in review.fields:
            print(f"{field.name.replace('_', ' ').title()}: {field.status}")
            for fact in field.evidence:
                label = " (caller-designated authoritative)" if fact.authoritative else ""
                print(f"  {fact.text} — {fact.path}:{fact.line}{label}")
        print(f"Task scope: {review.task_scope.status} — {review.task_scope.explanation}")
        for fact in review.task_scope.evidence:
            print(f"  {fact.text} — {fact.path}:{fact.line}")
    return 0


def _run_state(args: argparse.Namespace) -> int:
    project_root = Path(args.root).resolve(strict=True)
    relative = {
        "status": "docs/STATUS.md", "decision": "docs/DECISIONS.md", "scope": "docs/SCOPE.md",
    }[args.state_action]
    target = project_root / relative
    content = target.read_bytes().decode("utf-8")
    document = ContextDocument(relative, content, authoritative=True)
    expected = git_blob_sha(content)
    if args.state_action == "status":
        related_documents = []
        for raw_path in args.related_document:
            selected = Path(raw_path)
            if not selected.is_absolute():
                selected = project_root / selected
            selected = selected.resolve(strict=True)
            if not selected.is_relative_to(project_root) or not selected.is_file():
                raise ValueError("related source must be a project file")
            related_documents.append(ContextDocument(
                selected.relative_to(project_root).as_posix(),
                selected.read_bytes().decode("utf-8"),
                authoritative=selected.name in _AUTHORITATIVE_NAMES,
            ))
        proposal = propose_status_continuity(
            document, expected_blob_sha=expected, evidence_refs=tuple(args.evidence),
            new_current_phase=args.current_phase, new_next_action=args.next_action,
            related_documents=tuple(related_documents),
        )
    elif args.state_action == "decision":
        proposal = propose_decision_append(
            document, expected_blob_sha=expected, decision_id=args.decision_id,
            title=args.title, decision_body=args.body, approval_ref=args.approval_ref,
        )
    else:
        proposal = propose_scope_amendment(
            document, expected_blob_sha=expected, amendment_id=args.amendment_id,
            task=args.task, reason=args.reason, approval_ref=args.approval_ref,
        )
    if args.approve_digest:
        applied = apply_continuity_proposal(
            Path(args.root), proposal, approved_digest=args.approve_digest,
        )
        payload = {"status": applied.status, "path": applied.path, "blob_sha": applied.blob_sha}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"{applied.status.upper()} {applied.path} — {applied.blob_sha}")
        return 0

    digest = proposal_approval_digest(proposal) if proposal.action == "UPDATE" else None
    payload = {
        "status": proposal.action.lower(), "path": proposal.path,
        "expected_blob_sha": proposal.expected_blob_sha,
        "proposed_content": proposal.proposed_content,
        "reasons": list(proposal.reasons), "evidence_refs": list(proposal.evidence_refs),
        "related_source_fingerprints": [list(item) for item in proposal.related_source_fingerprints],
        "requires_human_approval": proposal.requires_human_approval,
        "approval_digest": digest,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{proposal.action} {proposal.path} — {proposal.reasons[0]}")
        if digest is not None:
            print("Review this exact change before explicitly approving it:")
            print("".join(difflib.unified_diff(
                content.splitlines(keepends=True), proposal.proposed_content.splitlines(keepends=True),
                fromfile=f"{relative} (current)", tofile=f"{relative} (proposed)",
            )), end="")
            print(f"Approval digest: {digest}")
    return 2 if proposal.action == "NEEDS_REVIEW" else 0


def _run_gates(args: argparse.Namespace) -> int:
    source = Path(args.file)
    if source.stat().st_size > 200_000:
        raise ValueError("gate evidence file exceeds the bounded size limit")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("gate evidence requires schema_version 1")

    def entries(name):
        values = data.get(name)
        if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
            raise ValueError(f"{name} must be a list of objects")
        return values

    def string(item, name, default=None):
        value = item.get(name, default)
        if not isinstance(value, str):
            raise ValueError(f"{name} must be text")
        return value

    def strings(item, name):
        value = item.get(name)
        if not isinstance(value, list) or any(not isinstance(part, str) for part in value):
            raise ValueError(f"{name} must be a list of text values")
        return tuple(value)

    def boolean(item, name, default=False):
        value = item.get(name, default)
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be true or false")
        return value

    requirements = tuple(
        MilestoneRequirement(
            string(item, "key"), string(item, "outcome"), strings(item, "checks"),
            boolean(item, "accepted_by_owner"), string(item, "approval_ref", ""),
        )
        for item in entries("requirements")
    )
    milestones = tuple(
        Milestone(
            string(item, "key"), strings(item, "requirement_keys"),
            string(item, "state", "proposed"), string(item, "approval_ref", ""),
        )
        for item in entries("milestones")
    )
    evidence = tuple(
        CheckEvidence(
            string(item, "requirement_key"), string(item, "check"),
            item.get("passed"), string(item, "source_ref", ""),
            string(item, "source_revision", ""),
            boolean(item, "independently_reviewed"),
        )
        for item in entries("evidence")
    )
    for item in evidence:
        if item.passed is not None and not isinstance(item.passed, bool):
            raise ValueError("passed must be true, false or null")
    review = review_project_gates(requirements, milestones, evidence)
    payload = {
        "status": review.status,
        "launch_approved": review.launch_approved,
        "requirements": [
            {"key": item.key, "outcome": item.outcome, "checks": list(item.checks),
             "accepted_by_owner": item.accepted_by_owner, "approval_ref": item.approval_ref}
            for item in requirements
        ],
        "milestones": [
            {"key": item.key, "requirement_keys": list(item.requirement_keys),
             "state": item.state, "approval_ref": item.approval_ref}
            for item in milestones
        ],
        "findings": [
            {"key": finding.key, "status": finding.status, "reason": finding.reason,
             "evidence_ref": finding.evidence_ref}
            for finding in review.findings
        ],
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Project gates: {review.status} — caller-supplied evidence; launch approval is separate")
        for finding in review.findings:
            print(f"{finding.status.upper()} {finding.key}: {finding.reason}")
    return 0 if review.status == "ready_for_owner_review" else 2


def _load_model_catalog(raw_path: str | None) -> tuple[tuple[ModelMetadata, ...], str | None]:
    if raw_path is None:
        return (), None
    source = Path(raw_path)
    if source.stat().st_size > 100_000:
        raise ValueError("model catalog exceeds the bounded size limit")
    raw = source.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("model catalog requires schema_version 1")
    entries = data.get("models")
    if not isinstance(entries, list) or len(entries) > 128 or any(not isinstance(item, dict) for item in entries):
        raise ValueError("models must be a bounded list of objects")
    models = []
    for item in entries:
        name, provider, surfaces = item.get("name"), item.get("provider"), item.get("surfaces")
        if (not isinstance(name, str) or not name.strip() or len(name) > 80
                or not isinstance(provider, str) or not provider.strip() or len(provider) > 80
                or not isinstance(surfaces, list) or not surfaces or len(surfaces) > 16
                or any(not isinstance(surface, str) or not surface.strip() for surface in surfaces)):
            raise ValueError("each model needs a bounded name, provider and target surfaces")
        available, verified = item.get("available", False), item.get("verified", False)
        if not isinstance(available, bool) or not isinstance(verified, bool):
            raise ValueError("available and verified must be explicit booleans")
        models.append(ModelMetadata(
            name.strip(), provider.strip(), tuple(surfaces),
            CapabilityClass(item.get("capability")), CostClass(item.get("cost")),
            available=available, verified=verified,
        ))
    return tuple(models), hashlib.sha256(raw).hexdigest()


def _run_route(args: argparse.Namespace) -> int:
    models, catalog_sha256 = _load_model_catalog(args.models_file)
    request, documents = _request_and_documents(args)
    result = (
        optimize_project_prompt(request, documents, models=models)
        if documents else optimize_prompt(request, models=models)
    )
    if result.needs_clarification:
        if args.json:
            print(json.dumps(result_dict(result), indent=2, ensure_ascii=False))
        else:
            for question in result.questions:
                print(f"? {question}")
        return 2
    review = review_route(result.intent, result.policy, models)
    decision = review.decision
    payload = {
        "status": "ready", "target_tool": decision.target_tool,
        "task_type": result.policy.task_type.value, "risk_level": result.policy.risk_level.value,
        "required_capability": decision.required_capability.value, "effort": decision.effort.value,
        "selected_model": decision.selected_model, "fallback": decision.fallback,
        "reason": decision.reason, "metadata_source": review.metadata_source,
        "catalog_sha256": catalog_sha256,
        "candidates": [
            {"name": item.name, "provider": item.provider,
             "capability": item.capability.value, "relative_cost": item.cost.value,
             "eligible": item.eligible, "selected": item.selected, "reasons": list(item.reasons)}
            for item in review.candidates
        ],
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Route: {decision.target_tool} / {decision.required_capability.value} / effort {decision.effort.value}")
        print(decision.reason)
        for item in review.candidates:
            label = "SELECTED" if item.selected else "ELIGIBLE" if item.eligible else "EXCLUDED"
            print(f"{label} {item.provider}/{item.name}: {', '.join(item.reasons)}")
    return 0


def _git_project_revision(root: Path) -> str:
    top = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=root,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise ValueError("checkpoint root must be a Git repository root")
    current = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    revision = current.stdout.strip()
    if current.returncode != 0 or len(revision) != 40:
        raise ValueError("checkpoint requires a committed Git source revision")
    return revision


def _checkpoint_context(root: Path, raw_paths: Sequence[str]) -> str:
    if not raw_paths or len(raw_paths) > 32:
        raise ValueError("checkpoint requires 1 to 32 explicit context files")
    parts = []
    labels = set()
    for raw_path in raw_paths:
        selected = Path(raw_path)
        if not selected.is_absolute():
            selected = root / selected
        selected = selected.resolve(strict=True)
        if not selected.is_relative_to(root) or not selected.is_file():
            raise ValueError("checkpoint context must be a project file")
        label = selected.relative_to(root).as_posix()
        if label.casefold() in labels:
            raise ValueError("duplicate checkpoint context file")
        labels.add(label.casefold())
        content = selected.read_bytes().decode("utf-8")
        parts.append(f"[{label}]\n{content}\n")
    context_text = "".join(parts)
    if len(context_text) > 36000:
        raise ValueError("checkpoint context exceeds 36000 characters")
    return context_text


def _read_small_json(path: str) -> dict[str, object]:
    source = Path(path)
    if source.stat().st_size > 100_000:
        raise ValueError("checkpoint input exceeds bounded size limit")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("checkpoint input must be a JSON object")
    return data


def _run_checkpoint(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve(strict=True)
    revision = _git_project_revision(root)
    context_text = _checkpoint_context(root, args.context_file)
    context_digest = hashlib.sha256(context_text.encode("utf-8")).hexdigest()
    if args.checkpoint_action == "create":
        spec = _read_small_json(args.spec)
        try:
            if not isinstance(spec.get("approved_plan"), list) or not isinstance(spec.get("completed", []), list):
                raise ValueError("approved_plan and completed must be lists")
            for key in ("operation_ids", "required_approval_ids"):
                if not isinstance(spec.get(key, []), list):
                    raise ValueError(f"{key} must be a list")
            checkpoint = make_checkpoint(
                task_id=spec["task_id"], source_revision=revision,
                next_step_id=spec["next_step_id"],
                approved_plan=tuple(PlanStep(**item) for item in spec["approved_plan"]),
                plan_approval_ref=spec["plan_approval_ref"],
                state_summary=spec["state_summary"],
                state_evidence_ref=spec["state_evidence_ref"],
                completed=tuple(VerifiedStep(**item) for item in spec.get("completed", [])),
                operation_ids=tuple(spec.get("operation_ids", [])),
                required_approval_ids=tuple(spec.get("required_approval_ids", [])),
                context_text=context_text,
                estimated_remaining_tokens=spec.get("estimated_remaining_tokens"),
            )
        except (KeyError, TypeError, AttributeError) as error:
            raise ValueError("checkpoint spec is malformed") from error
        with Path(args.output).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(checkpoint.to_dict(), stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        payload = {"status": "saved", "path": str(Path(args.output)), "checkpoint": checkpoint.to_dict()}
    else:
        checkpoint = checkpoint_from_dict(_read_small_json(args.checkpoint))
        if args.executed_operation and not args.ledger_reviewed:
            raise ValueError("--executed-operation requires --ledger-reviewed")
        review = review_resume(
            checkpoint, current_source_revision=revision,
            current_context_digest=context_digest,
            already_executed_operation_ids=tuple(args.executed_operation) if args.ledger_reviewed else None,
            externally_accepted_approval_ids=tuple(args.accepted_approval),
        )
        payload = {
            "status": review.status, "task_id": review.task_id,
            "next_step_id": review.next_step_id, "reasons": list(review.reasons),
            "approved_to_execute": review.approved_to_execute,
            "approved_plan": checkpoint.to_dict()["approved_plan"],
            "state_summary": checkpoint.state_summary,
            "source_revision": checkpoint.source_revision,
        }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Checkpoint {payload['status']}: {payload.get('path', payload.get('task_id'))}")
        if args.checkpoint_action == "review":
            for reason in payload["reasons"]:
                print(f"- {reason}")
    return 0 if payload["status"] in {"saved", "ready_for_owner_review"} else 2


def _run_handoff(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve(strict=True)
    revision = _git_project_revision(root)
    if args.handoff_action == "prepare":
        context_text = _checkpoint_context(root, args.context_file) if args.context_file else ""
        context_files = [
            (Path(raw) if Path(raw).is_absolute() else root / raw).resolve(strict=True).relative_to(root).as_posix()
            for raw in args.context_file
        ]
        documents = tuple(
            ContextDocument(path=label, content=(root / label).read_text(encoding="utf-8"))
            for label in context_files
        )
        request = IntentRequest.from_values(
            args.text, target_tool=args.target, constraints=args.constraint,
            success_criteria=args.success,
        )
        result = optimize_project_prompt(request, documents)
        if result.needs_clarification:
            print(json.dumps(result_dict(result), ensure_ascii=False, indent=2) if args.json else "Clarification required: " + "; ".join(result.questions))
            return 2
        packet = make_agent_handoff(
            result, target_tool=args.target, task_id=args.task_id,
            source_revision=revision, next_step_id="execute",
            context_digest=hashlib.sha256(context_text.encode("utf-8")).hexdigest(),
        )
        review = result_dict(result)
        payload = {
            "schema_version": 1, "handoff": packet.to_dict(), "review": review,
            "request": {"raw_text": args.text, "target_tool": args.target,
                        "constraints": args.constraint, "success_criteria": args.success},
            "context_files": context_files,
        }
        with Path(args.output).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        response = {"status": "saved", "path": str(Path(args.output)), "target_tool": packet.target_tool,
                    "risk_level": review["risk_level"], "approval_boundaries": review["approval_boundaries"]}
    else:
        raw_file = Path(args.file).read_bytes()
        if len(raw_file) > 100_000:
            raise ValueError("handoff file exceeds bounded size limit")
        source = json.loads(raw_file)
        if not isinstance(source, dict) or source.get("schema_version") != 1:
            raise ValueError("handoff file is malformed or unsupported")
        packet = handoff_from_dict(source.get("handoff"))
        review = source.get("review")
        saved_request = source.get("request")
        context_files = source.get("context_files")
        if (not isinstance(review, dict) or not isinstance(saved_request, dict)
                or not isinstance(saved_request.get("raw_text"), str)
                or saved_request.get("target_tool") != packet.target_tool
                or not isinstance(saved_request.get("constraints"), list)
                or not isinstance(saved_request.get("success_criteria"), list)
                or any(not isinstance(item, str) for key in ("constraints", "success_criteria")
                       for item in saved_request[key])
                or not isinstance(context_files, list) or len(context_files) > 32
                or any(not isinstance(item, str) for item in context_files)):
            raise ValueError("handoff review or context is malformed")
        current_context = _checkpoint_context(root, context_files) if context_files else ""
        if revision != packet.source_revision or hashlib.sha256(current_context.encode("utf-8")).hexdigest() != packet.context_digest:
            raise ValueError("handoff source revision or selected context changed; prepare again")
        documents = tuple(ContextDocument(path=label, content=(root / label).read_text(encoding="utf-8"))
                          for label in context_files)
        actual = optimize_project_prompt(IntentRequest.from_values(
            saved_request["raw_text"], target_tool=packet.target_tool,
            constraints=saved_request["constraints"], success_criteria=saved_request["success_criteria"],
        ), documents)
        if actual.needs_clarification or result_dict(actual) != review or actual.prompt != packet.prepared_prompt:
            raise ValueError("handoff does not match current IntentOS preparation; prepare again")
        if packet.target_tool != "codex":
            response = {"status": "unavailable", "target_tool": packet.target_tool,
                        "reason": "Automatic dispatch is unavailable for this agent; copy the prepared task instead."}
        else:
            if review.get("risk_level") == "high" and args.sandbox == "workspace-write":
                raise ValueError("high-risk handoffs require read-only dispatch or separate manual execution approval")
            approval = hashlib.sha256(json.dumps({
                "file_sha256": hashlib.sha256(raw_file).hexdigest(), "root": str(root),
                "sandbox": args.sandbox, "executable": args.executable, "timeout": args.timeout,
            }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            if args.approve_digest is None:
                response = {"status": "approval_required", "approval_digest": approval,
                            "target_tool": packet.target_tool, "risk_level": review["risk_level"],
                            "sandbox": args.sandbox, "root": str(root),
                            "goal": actual.intent.goal, "context_files": context_files,
                            "done_criteria": review.get("done_criteria", []),
                            "approval_boundaries": review.get("approval_boundaries", []),
                            "reason": "Review the saved handoff and this dispatch boundary before approving."}
            elif args.approve_digest != approval:
                raise ValueError("dispatch approval digest does not match this exact handoff and boundary")
            else:
                if args.sandbox == "workspace-write":
                    clean = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, check=False)
                    if clean.returncode != 0 or clean.stdout:
                        raise ValueError("workspace-write dispatch requires a clean Git working tree")
                response = run_codex_handoff(
                    packet, root=root, executable=args.executable,
                    sandbox=args.sandbox, timeout_seconds=args.timeout,
                )
                response["target_tool"] = packet.target_tool
                response["source_revision"] = revision
    print(json.dumps(response, ensure_ascii=False, indent=2) if args.json else f"Handoff {response['status']}: {response.get('reason', response.get('path', ''))}")
    return 0 if response["status"] in {"saved", "approval_required", "completed_unverified"} else 2


def main(argv: Sequence[str] | None = None) -> int:
    _configure_output_encoding()
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "optimize":
            return _run_optimize(args)
        if args.command == "skill":
            return _run_skill(args)
        if args.command == "workspace":
            return _run_workspace(args)
        if args.command == "compass":
            return _run_compass(args)
        if args.command == "state":
            return _run_state(args)
        if args.command == "gates":
            return _run_gates(args)
        if args.command == "route":
            return _run_route(args)
        if args.command == "checkpoint":
            return _run_checkpoint(args)
        if args.command == "handoff":
            return _run_handoff(args)
    except (OSError, ValueError) as error:
        if getattr(args, "json", False):
            print(json.dumps(error_dict(error), indent=2, ensure_ascii=False))
        else:
            print(f"ERROR: {error}")
        return 2
    return 2


def _configure_output_encoding() -> None:
    """Keep the CLI's user-visible text and JSON Unicode-safe on Windows."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

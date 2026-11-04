from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Sequence

from .compass import review_project_compass
from .continuity import git_blob_sha, propose_decision_append, propose_scope_amendment, propose_status_continuity
from .continuity_store import apply_continuity_proposal, proposal_approval_digest
from .governance import CheckEvidence, Milestone, MilestoneRequirement, review_project_gates
from .models import ContextDocument, IntentRequest
from .project import optimize_project_prompt
from .result_contract import RESULT_SCHEMA_VERSION, error_dict, result_dict
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

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .models import ContextDocument, IntentRequest
from .project import optimize_project_prompt
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


def _result_dict(result) -> dict[str, object]:
    return {
        "needs_clarification": result.needs_clarification,
        "questions": list(result.questions),
        "prompt": result.prompt,
        "task_type": result.policy.task_type.value if result.policy else None,
        "risk_level": result.policy.risk_level.value if result.policy else None,
        "routing": (
            {
                "target_tool": result.routing.target_tool,
                "required_capability": result.routing.required_capability.value,
                "effort": result.routing.effort.value,
                "selected_model": result.routing.selected_model,
                "fallback": result.routing.fallback,
                "reason": result.routing.reason,
            }
            if result.routing
            else None
        ),
        "context_paths": (
            [item.document.path for item in result.context_selection.selected]
            if result.context_selection
            else []
        ),
    }


def _add_intent_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("text", help="Raw user intent.")
    parser.add_argument("--target", required=True, help="Target tool, e.g. codex, chatgpt, claude-code.")
    parser.add_argument("--constraint", action="append", default=[], help="Constraint; repeatable.")
    parser.add_argument("--success", action="append", default=[], help="Success criterion; repeatable.")
    parser.add_argument("--context-file", action="append", default=[], help="Project context file; repeatable.")


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

    return parser


def _request_and_documents(args: argparse.Namespace) -> tuple[IntentRequest, tuple[ContextDocument, ...]]:
    request = IntentRequest.from_values(
        args.text,
        target_tool=args.target,
        constraints=args.constraint,
        success_criteria=args.success,
    )
    return request, _load_documents(args.context_file)


def _optimize_from_args(args: argparse.Namespace):
    request, documents = _request_and_documents(args)
    return optimize_project_prompt(request, documents) if documents else optimize_prompt(request)


def _run_optimize(args: argparse.Namespace) -> int:
    result = _optimize_from_args(args)

    if args.json:
        print(json.dumps(_result_dict(result), indent=2, ensure_ascii=False))
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
    return 0


def _run_skill(args: argparse.Namespace) -> int:
    result = _optimize_from_args(args)
    if result.needs_clarification or result.policy is None:
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


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "optimize":
        return _run_optimize(args)
    if args.command == "skill":
        return _run_skill(args)
    if args.command == "workspace":
        return _run_workspace(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

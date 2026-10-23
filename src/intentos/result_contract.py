from __future__ import annotations

from .models import PromptResult


RESULT_SCHEMA_VERSION = "1"


def result_dict(result: PromptResult) -> dict[str, object]:
    """Serialize a PromptResult for machine-facing access surfaces."""
    policy = result.policy
    selection = result.context_selection
    selected_context = (
        [
            {
                "path": item.document.path,
                "score": item.score,
                "reasons": list(item.reasons),
                "chars": len(item.document.content),
            }
            for item in selection.selected
        ]
        if selection
        else []
    )
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": "clarification" if result.needs_clarification else "ready",
        "needs_clarification": result.needs_clarification,
        "questions": list(result.questions),
        "intent": {
            "goal": result.intent.goal,
            "target_tool": result.intent.target_tool,
            "output_format": result.intent.output_format,
            "constraints": list(result.intent.constraints),
            "audience": result.intent.audience,
            "success_criteria": list(result.intent.success_criteria),
        },
        "prompt": result.prompt,
        "task_type": policy.task_type.value if policy else None,
        "risk_level": policy.risk_level.value if policy else None,
        "engineering_rules": list(policy.engineering_rules) if policy else [],
        "approval_boundaries": list(policy.approval_boundaries) if policy else [],
        "done_criteria": list(policy.done_criteria) if policy else [],
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
        "context": {
            "selected": selected_context,
            "selected_paths": [item["path"] for item in selected_context],
            "omitted_paths": list(selection.omitted_paths) if selection else [],
            "total_chars": selection.total_chars if selection else 0,
        },
        # Compatibility alias for current pre-v1 machine consumers.
        "context_paths": [item["path"] for item in selected_context],
    }


def error_dict(error: Exception) -> dict[str, object]:
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": "error",
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
        },
    }

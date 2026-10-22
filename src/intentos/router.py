from __future__ import annotations

from .models import (
    CapabilityClass,
    CostClass,
    EffortLevel,
    ExecutionPolicy,
    ModelMetadata,
    NormalizedIntent,
    RiskLevel,
    RoutingDecision,
    TaskType,
)


_CAPABILITY_RANK = {
    CapabilityClass.FAST: 0,
    CapabilityClass.BALANCED: 1,
    CapabilityClass.STRONG: 2,
}
_COST_RANK = {
    CostClass.LOW: 0,
    CostClass.MEDIUM: 1,
    CostClass.HIGH: 2,
}


def _requirements(policy: ExecutionPolicy) -> tuple[CapabilityClass, EffortLevel]:
    if policy.risk_level is RiskLevel.HIGH or policy.task_type in {
        TaskType.ARCHITECTURE,
        TaskType.SECURITY,
    }:
        return CapabilityClass.STRONG, EffortLevel.HIGH
    if policy.risk_level is RiskLevel.MEDIUM or policy.task_type in {
        TaskType.CODING,
        TaskType.REFACTOR,
        TaskType.DEVOPS,
    }:
        return CapabilityClass.BALANCED, EffortLevel.MEDIUM
    return CapabilityClass.FAST, EffortLevel.LOW


def recommend_route(
    intent: NormalizedIntent,
    policy: ExecutionPolicy,
    models: tuple[ModelMetadata, ...] = (),
) -> RoutingDecision:
    required, effort = _requirements(policy)
    target = intent.target_tool

    eligible = [
        model
        for model in models
        if model.available
        and target.casefold() in {surface.casefold() for surface in model.surfaces}
        and _CAPABILITY_RANK[model.capability] >= _CAPABILITY_RANK[required]
    ]

    if not eligible:
        return RoutingDecision(
            target_tool=target,
            required_capability=required,
            effort=effort,
            selected_model=None,
            reason=(
                "No verified compatible model metadata was supplied; use the target tool's "
                f"current default at {required.value} capability or stronger."
            ),
            fallback=True,
        )

    eligible.sort(
        key=lambda model: (
            0 if model.verified else 1,
            _CAPABILITY_RANK[model.capability] - _CAPABILITY_RANK[required],
            _COST_RANK[model.cost],
            model.name.casefold(),
        )
    )
    selected = eligible[0]

    return RoutingDecision(
        target_tool=target,
        required_capability=required,
        effort=effort,
        selected_model=selected.name,
        reason=(
            f"Selected the lowest-overhead compatible model meeting {required.value} "
            f"capability for {policy.task_type.value}/{policy.risk_level.value} work."
        ),
        fallback=False,
    )

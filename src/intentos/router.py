from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

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


@dataclass(frozen=True, slots=True)
class RouteCandidateReview:
    name: str
    provider: str
    capability: CapabilityClass
    cost: CostClass
    eligible: bool
    selected: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RouteReview:
    decision: RoutingDecision
    candidates: tuple[RouteCandidateReview, ...]
    metadata_source: str = "caller-supplied; not checked against live providers"


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

    names = [model.name.casefold() for model in models]
    if len(names) != len(set(names)):
        return RoutingDecision(
            target_tool=target, required_capability=required, effort=effort,
            selected_model=None,
            reason="Conflicting duplicate model names in caller-supplied metadata; review the catalog before routing.",
            fallback=True,
        )

    eligible = [
        model
        for model in models
        if model.available and model.verified
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
                f"own selection only after checking that it meets {required.value} capability."
            ),
            fallback=True,
        )

    eligible.sort(
        key=lambda model: (
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
            f"Selected {selected.name} from caller-supplied metadata: provider {selected.provider}, "
            f"{selected.capability.value} capability, {selected.cost.value} relative cost. "
            f"It is the lowest capability and relative-cost eligible option for "
            f"{policy.task_type.value}/{policy.risk_level.value} work; live availability and price were not checked."
        ),
        fallback=False,
    )


def review_route(
    intent: NormalizedIntent,
    policy: ExecutionPolicy,
    models: tuple[ModelMetadata, ...] = (),
) -> RouteReview:
    """Explain the shared routing decision without discovering providers or prices."""
    decision = recommend_route(intent, policy, models)
    candidates = []
    counts = Counter(model.name.casefold() for model in models)
    duplicate_names = {name for name, count in counts.items() if count > 1}
    for model in models:
        reasons = []
        if model.name.casefold() in duplicate_names:
            reasons.append("duplicate model name")
        if not model.available:
            reasons.append("caller marked unavailable")
        if not model.verified:
            reasons.append("metadata is not caller-verified")
        if intent.target_tool.casefold() not in {surface.casefold() for surface in model.surfaces}:
            reasons.append("target surface is unsupported")
        if _CAPABILITY_RANK[model.capability] < _CAPABILITY_RANK[decision.required_capability]:
            reasons.append("capability is below the required class")
        eligible = not reasons
        candidates.append(RouteCandidateReview(
            model.name, model.provider, model.capability, model.cost, eligible,
            eligible and decision.selected_model == model.name,
            tuple(reasons) if reasons else ("meets caller-supplied capability, cost and surface requirements",),
        ))
    return RouteReview(decision, tuple(candidates))

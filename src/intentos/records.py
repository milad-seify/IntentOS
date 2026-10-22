from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any

from .models import PromptResult


RUN_RECORD_SCHEMA_VERSION = "1"


@dataclass(frozen=True, slots=True)
class RunMetrics:
    success: bool | None = None
    quality_score: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    retries: int | None = None


@dataclass(frozen=True, slots=True)
class RunRecord:
    schema_version: str
    prompt_sha256: str | None
    target_tool: str
    task_type: str | None
    risk_level: str | None
    required_capability: str | None
    effort: str | None
    selected_model: str | None
    routing_fallback: bool | None
    context_paths: tuple[str, ...]
    metrics: RunMetrics
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["context_paths"] = list(self.context_paths)
        value["tags"] = list(self.tags)
        return value

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


def build_run_record(
    result: PromptResult,
    *,
    context_paths: tuple[str, ...] = (),
    metrics: RunMetrics | None = None,
    tags: tuple[str, ...] = (),
) -> RunRecord:
    """Build a compact reproducibility record for an externally executed run.

    IntentOS does not execute the agent or persist traces itself. External runners
    can populate outcome/cost metrics and store the serialized record wherever
    appropriate.
    """
    policy = result.policy
    routing = result.routing
    prompt_hash = sha256(result.prompt.encode("utf-8")).hexdigest() if result.prompt else None

    return RunRecord(
        schema_version=RUN_RECORD_SCHEMA_VERSION,
        prompt_sha256=prompt_hash,
        target_tool=result.intent.target_tool,
        task_type=policy.task_type.value if policy else None,
        risk_level=policy.risk_level.value if policy else None,
        required_capability=routing.required_capability.value if routing else None,
        effort=routing.effort.value if routing else None,
        selected_model=routing.selected_model if routing else None,
        routing_fallback=routing.fallback if routing else None,
        context_paths=tuple(dict.fromkeys(path.strip() for path in context_paths if path.strip())),
        metrics=metrics or RunMetrics(),
        tags=tuple(dict.fromkeys(tag.strip() for tag in tags if tag.strip())),
    )

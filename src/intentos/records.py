from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
from typing import Any

from .models import PromptResult


RUN_RECORD_SCHEMA_VERSION = "1"


def _intentos_version() -> str:
    try:
        return version("intentos")
    except PackageNotFoundError:
        return "dev"


@dataclass(frozen=True, slots=True)
class RunMetrics:
    success: bool | None = None
    quality_score: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    retries: int | None = None


@dataclass(frozen=True, slots=True)
class ContextFingerprint:
    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class RunRecord:
    schema_version: str
    intentos_version: str
    prompt_sha256: str | None
    target_tool: str
    task_type: str | None
    risk_level: str | None
    required_capability: str | None
    effort: str | None
    selected_model: str | None
    routing_fallback: bool | None
    context_paths: tuple[str, ...]
    context_fingerprints: tuple[ContextFingerprint, ...]
    metrics: RunMetrics
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["context_paths"] = list(self.context_paths)
        value["context_fingerprints"] = [asdict(item) for item in self.context_fingerprints]
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

    IntentOS does not execute the agent or persist raw traces itself. External
    runners can populate outcome/cost metrics and store the serialized record.
    Selected project context is represented by path + content hash rather than raw
    content so provenance improves without making private context part of the
    record by default.
    """
    policy = result.policy
    routing = result.routing
    prompt_hash = sha256(result.prompt.encode("utf-8")).hexdigest() if result.prompt else None

    selected = result.context_selection.selected if result.context_selection else ()
    fingerprints = tuple(
        ContextFingerprint(
            path=item.document.path,
            sha256=sha256(item.document.content.encode("utf-8")).hexdigest(),
        )
        for item in selected
    )
    selected_paths = tuple(item.path for item in fingerprints)
    all_context_paths = tuple(
        dict.fromkeys(
            path.strip()
            for path in (*selected_paths, *context_paths)
            if path.strip()
        )
    )

    return RunRecord(
        schema_version=RUN_RECORD_SCHEMA_VERSION,
        intentos_version=_intentos_version(),
        prompt_sha256=prompt_hash,
        target_tool=result.intent.target_tool,
        task_type=policy.task_type.value if policy else None,
        risk_level=policy.risk_level.value if policy else None,
        required_capability=routing.required_capability.value if routing else None,
        effort=routing.effort.value if routing else None,
        selected_model=routing.selected_model if routing else None,
        routing_fallback=routing.fallback if routing else None,
        context_paths=all_context_paths,
        context_fingerprints=fingerprints,
        metrics=metrics or RunMetrics(),
        tags=tuple(dict.fromkeys(tag.strip() for tag in tags if tag.strip())),
    )

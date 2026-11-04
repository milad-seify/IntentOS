"""Caller-supplied outcome evidence and reviewable learning; no agent execution."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from .evaluation import EvaluationOutcome, VariantRun, compare_paired_runs, propose_lessons
from .records import RunMetrics


_CONDITIONS = ("executor", "model", "effort", "base_revision", "context", "permissions", "environment")
_METRICS = ("quality_score", "input_tokens", "output_tokens", "latency_ms", "retries")


def _line(value: object, name: str, *, required: bool = True) -> str:
    if not isinstance(value, str) or (required and not value.strip()) or len(value) > 500 or any(
        char in "\n\r\v\f\x85\u2028\u2029" or ord(char) < 32 or ord(char) == 127 for char in value
    ):
        raise ValueError(f"{name} must be a bounded single line")
    return value.strip()


def capture_outcome(data: dict[str, object]) -> dict[str, object]:
    """Validate and normalize one external outcome without guessing missing metrics."""
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("outcome input requires schema_version 1")
    task_id = _line(data.get("task_id"), "task_id")
    variant = data.get("variant")
    if not isinstance(variant, str) or variant not in {"raw", "prepared", "single"}:
        raise ValueError("variant must be raw, prepared or single")
    conditions = data.get("conditions")
    if not isinstance(conditions, dict):
        raise ValueError("conditions must be an object")
    normalized_conditions = {key: _line(conditions.get(key), key) for key in _CONDITIONS}
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks or len(checks) > 64:
        raise ValueError("checks must contain 1 to 64 acceptance checks")
    normalized_checks = []
    names = set()
    for item in checks:
        if not isinstance(item, dict):
            raise ValueError("each check must be an object")
        name = _line(item.get("name"), "check name")
        if name.casefold() in names:
            raise ValueError("check names must be unique")
        names.add(name.casefold())
        passed = item.get("passed")
        if passed is not None and type(passed) is not bool:
            raise ValueError("check passed must be true, false or null")
        evidence_ref = _line(item.get("evidence_ref", ""), "evidence_ref", required=passed is not None)
        normalized_checks.append({"name": name, "passed": passed, "evidence_ref": evidence_ref})
    success = data.get("execution_success")
    if success is not None and type(success) is not bool:
        raise ValueError("execution_success must be true, false or null")
    raw_metrics = data.get("metrics", {})
    if not isinstance(raw_metrics, dict):
        raise ValueError("metrics must be an object")
    normalized_metrics = {}
    for key in _METRICS:
        value = raw_metrics.get(key)
        if value is not None and (type(value) not in (int, float) if key == "quality_score" else type(value) is not int):
            raise ValueError(f"{key} must have a numeric value or null")
        normalized_metrics[key] = value
    RunMetrics(success=success, **normalized_metrics)
    source_ref = _line(data.get("source_ref"), "source_ref")
    notes = {key: _line(data.get(key, ""), key, required=False)
             for key in ("friction", "rework", "context_gap", "verification_gap", "lesson_hint")}
    return {
        "schema_version": 1, "task_id": task_id, "variant": variant,
        "conditions": normalized_conditions, "checks": normalized_checks,
        "execution_success": success, "metrics": normalized_metrics,
        "source_ref": source_ref, **notes,
    }


def compare_outcomes(raw: dict[str, object], prepared: dict[str, object]) -> dict[str, Any]:
    """Guard the paired design, then use the existing Phase 7C comparison contract."""
    raw = capture_outcome(raw)
    prepared = capture_outcome(prepared)
    if raw["variant"] != "raw" or prepared["variant"] != "prepared" or raw["task_id"] != prepared["task_id"]:
        raise ValueError("paired records need the same task ID and raw/prepared variants")
    if raw["conditions"] != prepared["conditions"]:
        return {"status": "inconclusive", "task_id": raw["task_id"],
                "reason": "Executor, model, effort, base, context, permissions or environment differ."}
    raw_checks = {item["name"]: item for item in raw["checks"]}
    prepared_checks = {item["name"]: item for item in prepared["checks"]}
    if raw_checks.keys() != prepared_checks.keys():
        return {"status": "inconclusive", "task_id": raw["task_id"],
                "reason": "Acceptance checks differ between arms."}
    if any(item["passed"] is None for item in (*raw_checks.values(), *prepared_checks.values())):
        return {"status": "inconclusive", "task_id": raw["task_id"],
                "reason": "At least one acceptance check is unverified."}

    def variant(record: dict[str, object]) -> VariantRun:
        checks = record["checks"]
        failures = tuple(item["name"] for item in checks if item["passed"] is False)
        outcome = EvaluationOutcome(
            name=f"{record['task_id']}:{record['variant']}", passed=not failures,
            score=(len(checks) - len(failures)) / len(checks), failures=failures,
            lesson_hint=record["lesson_hint"] or None,
        )
        return VariantRun(record["variant"], outcome, RunMetrics(
            success=record["execution_success"], **record["metrics"],
        ))

    result = compare_paired_runs(raw["task_id"], variant(raw), variant(prepared))
    return {"status": result.winner or "inconclusive", "comparison": result.to_dict(),
            "source_refs": {"raw": raw["source_ref"], "prepared": prepared["source_ref"]}}


def learning_review(records: tuple[dict[str, object], ...]) -> dict[str, object]:
    """Only repeated distinct failed tasks can yield a proposal; no policy writes."""
    if not records or len(records) > 128:
        raise ValueError("learning review needs 1 to 128 outcome records")
    normalized = tuple(capture_outcome(item) for item in records)
    outcomes = []
    sources: dict[tuple[str, str], set[str]] = {}
    for item in normalized:
        failed = item["execution_success"] is False or any(check["passed"] is False for check in item["checks"])
        if failed and item["lesson_hint"]:
            outcomes.append(EvaluationOutcome(item["task_id"], False, 0.0,
                                              lesson_hint=item["lesson_hint"]))
            sources.setdefault((item["task_id"], item["lesson_hint"]), set()).add(item["source_ref"])
    proposals = propose_lessons(tuple(outcomes))
    result = [{"rule": item.rule, "evidence_cases": list(item.evidence_cases),
               "source_refs": sorted({ref for case in item.evidence_cases for ref in sources[(case, item.rule)]})}
              for item in proposals]
    return {"status": "proposal" if result else "insufficient_repeated_evidence",
            "proposals": result,
            "evidence_sha256": sha256(json.dumps(normalized, sort_keys=True, separators=(",", ":"),
                                          ensure_ascii=False).encode("utf-8")).hexdigest(),
            "runtime_policy_changed": False}


def learning_approval_digest(review: dict[str, object]) -> str:
    return sha256(json.dumps(review, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

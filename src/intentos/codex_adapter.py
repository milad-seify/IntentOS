"""Explicit, bounded Codex CLI dispatch for a reviewed IntentOS handoff."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from .handoff import AgentHandoff


def run_codex_handoff(
    packet: AgentHandoff, *, root: Path, executable: str = "codex",
    sandbox: str = "read-only", timeout_seconds: int = 1800, model: str | None = None,
) -> dict[str, object]:
    """Run one approved handoff; a completed agent turn is not task verification."""
    if packet.target_tool != "codex":
        return {"status": "unavailable", "reason": f"Automatic dispatch is unavailable for {packet.target_tool}; copy the prepared task instead."}
    if Path(executable).name.casefold() not in {"codex", "codex.exe", "codex.cmd"}:
        raise ValueError("Codex executable must be named codex, codex.exe or codex.cmd")
    if sandbox not in {"read-only", "workspace-write"}:
        raise ValueError("Codex sandbox must be read-only or workspace-write")
    if not 1 <= timeout_seconds <= 3600:
        raise ValueError("timeout must be between 1 and 3600 seconds")
    command = [
        executable, "exec", "--json", "--ephemeral", "--ignore-user-config",
        "--sandbox", sandbox, "-C", str(root),
    ]
    if model is not None:
        command.extend(("-m", model))
    command.append("-")
    try:
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            completed = subprocess.run(
                command, input=packet.prepared_prompt.encode("utf-8"),
                cwd=root, stdout=stdout, stderr=stderr, check=False,
                timeout=timeout_seconds,
            )
            stdout.seek(0)
            output = stdout.read(2_000_001)
            truncated = len(output) > 2_000_000
    except FileNotFoundError:
        return {"status": "unavailable", "reason": "Codex CLI executable was not found; handoff remains available for manual copy."}
    except subprocess.TimeoutExpired:
        return {"status": "interrupted", "reason": "Codex timed out; inspect the workspace and external actions before retrying."}
    except OSError as error:
        return {"status": "failed", "reason": f"Codex process could not start ({type(error).__name__}, code {getattr(error, 'winerror', None) or error.errno})."}

    turn_completed = False
    turn_failed = False
    usage = None
    thread_id = None
    final_message = None
    message_truncated = False
    if not truncated:
        for line in output.splitlines():
            try:
                event = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(event, dict):
                continue
            if event.get("type") == "thread.started" and isinstance(event.get("thread_id"), str):
                thread_id = event["thread_id"]
            if event.get("type") == "turn.completed":
                turn_completed = True
                if isinstance(event.get("usage"), dict):
                    usage = {key: value for key, value in event["usage"].items()
                             if key in {"input_tokens", "cached_input_tokens", "output_tokens"}
                             and type(value) is int and value >= 0}
            if event.get("type") in {"turn.failed", "error"}:
                turn_failed = True
            item = event.get("item")
            if (event.get("type") == "item.completed" and isinstance(item, dict)
                    and item.get("type") == "agent_message" and isinstance(item.get("text"), str)):
                final_message = item["text"][:8_000]
                message_truncated = len(item["text"]) > 8_000
    status = "completed_unverified" if completed.returncode == 0 and turn_completed and not turn_failed else "failed"
    return {
        "status": status, "exit_code": completed.returncode,
        "thread_id": thread_id, "usage": usage,
        "requested_model": model,
        "final_message": final_message, "message_truncated": message_truncated,
        "reason": (
            "Codex completed its turn; inspect changes and run independent checks."
            if status == "completed_unverified" else
            "Codex did not report a clean completed turn; inspect the workspace before retrying."
        ),
        "output_truncated": truncated,
    }

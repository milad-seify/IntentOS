"""Loopback-only graphical access to the existing IntentOS core and bounded CLI workflows."""

from __future__ import annotations

from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import difflib
import hmac
import html
import json
import re
import secrets
import subprocess
import sys
import tempfile
import threading
import uuid
import webbrowser

from .compass import review_project_compass
from .models import ContextDocument, IntentRequest
from .project import optimize_project_prompt
from .result_contract import result_dict
from .service import optimize_prompt


_ASSETS = Path(__file__).parent
_MAX_BODY = 64_000
_MAX_FIELD = 36_000
_APPROVABLE = {"stateStatus", "stateDecision", "stateScope", "handoffDispatch", "outcomeLearn"}


def _text(value: object, label: str, *, required: bool = False, maximum: int = _MAX_FIELD) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be bounded text")
    if len(value) > maximum:
        raise ValueError(f"{label} exceeds {maximum} characters; use shorter text or a smaller file")
    # Browser file uploads preserve Windows newlines. Normalize only paired CRLF;
    # a bare CR or another control character is still an invalid input.
    value = value.replace("\r\n", "\n")
    if any((ord(char) < 32 and char not in "\n\t") or ord(char) == 127 for char in value):
        raise ValueError(f"{label} contains unsupported control characters; use LF or CRLF text without embedded controls")
    value = value.strip()
    if required and not value:
        raise ValueError(f"{label} is required")
    return value


def _document(value: object) -> ContextDocument:
    if not isinstance(value, dict) or set(value) != {"name", "content", "authoritative"}:
        raise ValueError("Choose a project document with its authority setting")
    name = _text(value["name"], "Document name", required=True, maximum=120)
    if name in {".", ".."} or "/" in name or "\\" in name or ":" in name:
        raise ValueError("Document name must be a file name, not a path")
    if type(value["authoritative"]) is not bool:
        raise ValueError("Document authority must be explicit")
    return ContextDocument(name, _text(value["content"], "Document content"), value["authoritative"])


def _documents(value: object) -> tuple[ContextDocument, ...]:
    if not isinstance(value, list) or len(value) > 8:
        raise ValueError("Select at most eight project documents")
    documents = tuple(_document(item) for item in value)
    if sum(len(item.content) for item in documents) > _MAX_FIELD:
        raise ValueError("Selected project context exceeds 36000 characters")
    return documents


def _project_root(value: object) -> Path:
    raw = _text(value, "Project folder", required=True, maximum=1000)
    root = Path(raw).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project folder must be a directory")
    check = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True,
        text=True, encoding="utf-8", timeout=5, check=False,
    )
    if check.returncode or Path(check.stdout.strip()).resolve() != root:
        raise ValueError("Choose the root of a Git project")
    return root


def _upload(server: "IntentOSUIServer", value: object, label: str) -> str:
    if not isinstance(value, dict) or set(value) != {"name", "content"}:
        raise ValueError(f"Choose a {label} JSON file")
    name = _text(value["name"], label, required=True, maximum=120)
    if not name.lower().endswith(".json") or any(char in name for char in "/\\:"):
        raise ValueError(f"{label} must be a JSON file")
    raw = value["content"]
    if isinstance(raw, str) and len(raw.encode("utf-8")) > 100_000:
        raise ValueError(f"{label} must contain one bounded JSON object")
    content = _text(raw, label, required=True, maximum=100_000)
    if len(content.encode("utf-8")) > 100_000 or not isinstance(json.loads(content), dict):
        raise ValueError(f"{label} must contain one bounded JSON object")
    with server.pending_lock:
        if server.artifact_count >= 128:
            raise ValueError("This local UI session reached its artifact limit; restart it before continuing")
        server.artifact_count += 1
    path = Path(server.temporary.name) / f"input-{uuid.uuid4().hex}.json"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _output_path(server: "IntentOSUIServer") -> str:
    with server.pending_lock:
        if server.artifact_count >= 128:
            raise ValueError("This local UI session reached its artifact limit; restart it before continuing")
        server.artifact_count += 1
    return str(Path(server.temporary.name) / f"result-{uuid.uuid4().hex}.json")


def _cli(args: list[str], *, root: Path | None = None, timeout: int = 45) -> dict:
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "intentos", *args, "--json"], cwd=root,
            capture_output=True, text=True, encoding="utf-8", timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError("The local operation timed out; inspect its effects before retrying") from error
    if completed.returncode not in {0, 2}:
        raise ValueError("The local IntentOS operation failed; no result was accepted")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("IntentOS returned an invalid result") from error
    if not isinstance(payload, dict):
        raise ValueError("IntentOS returned an invalid result")
    if payload.get("status") == "error":
        details = payload.get("error")
        message = details.get("message", "Operation rejected") if isinstance(details, dict) else "Operation rejected"
        raise ValueError(_text(message, "Error", maximum=500))
    return payload


def _artifact(payload: dict, output: str | None) -> dict:
    if not output or not Path(output).exists():
        return payload
    content = Path(output).read_text(encoding="utf-8")
    if len(content.encode("utf-8")) > 100_000:
        raise ValueError("Generated artifact exceeded the UI download limit")
    return {**payload, "download": {"filename": Path(output).name, "content": content}}


def _prepare(data: dict) -> dict:
    if set(data) != {"text", "target", "documents"}:
        raise ValueError("Unexpected preparation fields")
    request = IntentRequest.from_values(
        _text(data["text"], "Task", required=True, maximum=10_000),
        target_tool=_text(data["target"], "AI tool", maximum=80) or None,
    )
    documents = _documents(data["documents"])
    result = optimize_project_prompt(request, documents) if documents else optimize_prompt(request)
    return result_dict(result)


def _compass(data: dict) -> dict:
    if set(data) != {"documents", "task"}:
        raise ValueError("Unexpected Project Compass fields")
    documents = _documents(data["documents"])
    if not documents:
        raise ValueError("Choose at least one project document")
    review = review_project_compass(documents, proposed_task=_text(data["task"], "Task", maximum=10_000))

    def fact(item):
        return {"text": item.text, "path": item.path, "line": item.line,
                "stale": item.stale, "authoritative": item.authoritative}

    return {"status": "review", "fields": {
        field.name: {"status": field.status, "value": field.value,
                     "evidence": [fact(item) for item in field.evidence]}
        for field in review.fields}, "task_scope": {
            "status": review.task_scope.status, "explanation": review.task_scope.explanation,
            "scope_review_required": review.task_scope.scope_review_required,
            "evidence": [fact(item) for item in review.task_scope.evidence],
        }}


def _action(server: "IntentOSUIServer", data: dict) -> dict:
    if set(data) != {"action", "fields"} or not isinstance(data["fields"], dict):
        raise ValueError("Unexpected workflow fields")
    action = _text(data["action"], "Workflow", required=True, maximum=40)
    fields = data["fields"]
    get = lambda name, required=False: _text(fields.get(name, ""), name, required=required)
    root = _project_root(fields.get("root")) if action in {
        "stateStatus", "stateDecision", "stateScope", "handoffPrepare", "handoffDispatch",
        "checkpointCreate", "checkpointReview",
    } else None
    output = None
    if action == "route":
        args = ["route", get("text", True)]
        if get("target"):
            args += ["--target", get("target")]
        if fields.get("models"):
            args += ["--models-file", _upload(server, fields["models"], "model metadata")]
    elif action in {"stateStatus", "stateDecision", "stateScope"}:
        kind = {"stateStatus": "status", "stateDecision": "decision", "stateScope": "scope"}[action]
        args = ["state", kind, "--root", str(root)]
        if kind == "status":
            args += ["--current-phase", get("current_phase", True), "--next-action", get("next_action", True),
                     "--evidence", get("evidence", True)]
        elif kind == "decision":
            args += ["--decision-id", get("decision_id", True), "--title", get("title", True),
                     "--body", get("body", True), "--approval-ref", get("approval_ref", True)]
        else:
            args += ["--amendment-id", get("amendment_id", True), "--task", get("task", True),
                     "--reason", get("reason", True), "--approval-ref", get("approval_ref", True)]
    elif action == "gates":
        args = ["gates", "--file", _upload(server, fields.get("evidence"), "readiness evidence")]
    elif action == "handoffPrepare":
        output = _output_path(server)
        args = ["handoff", "prepare", get("text", True), "--root", str(root),
                "--target", get("target", True), "--task-id", get("task_id", True), "--output", output]
        if get("context_file"):
            args += ["--context-file", get("context_file")]
    elif action == "handoffDispatch":
        sandbox = get("sandbox") or "read-only"
        if sandbox not in {"read-only", "workspace-write"}:
            raise ValueError("Choose a supported sandbox")
        args = ["handoff", "dispatch", "--root", str(root), "--file", _upload(server, fields.get("packet"), "handoff packet"), "--sandbox", sandbox]
        if get("model"):
            args += ["--model", get("model")]
    elif action == "checkpointCreate":
        output = _output_path(server)
        args = ["checkpoint", "create", "--root", str(root), "--spec", _upload(server, fields.get("spec"), "checkpoint specification"),
                "--context-file", get("context_file", True), "--output", output]
    elif action == "checkpointReview":
        args = ["checkpoint", "review", "--root", str(root), "--checkpoint", _upload(server, fields.get("checkpoint"), "checkpoint"),
                "--context-file", get("context_file", True)]
        if fields.get("ledger_reviewed") is True:
            args += ["--ledger-reviewed"]
        elif fields.get("ledger_reviewed") not in {False, None}:
            raise ValueError("Ledger review must be explicit")
        for name, option in (("executed_operation", "--executed-operation"), ("accepted_approval", "--accepted-approval"),
                             ("remaining_budget_tokens", "--remaining-budget-tokens")):
            if get(name):
                args += [option, get(name)]
    elif action == "outcomeRecord":
        output = _output_path(server)
        args = ["outcome", "record", "--file", _upload(server, fields.get("evidence"), "outcome evidence"), "--output", output]
    elif action == "outcomeCompare":
        args = ["outcome", "compare", "--raw", _upload(server, fields.get("raw"), "raw outcome"),
                "--prepared", _upload(server, fields.get("prepared"), "prepared outcome")]
    elif action == "outcomeLearn":
        records = fields.get("records")
        if not isinstance(records, list) or not 2 <= len(records) <= 8:
            raise ValueError("Choose two to eight outcome records")
        args = ["outcome", "learn"]
        for item in records:
            args += ["--record", _upload(server, item, "outcome record")]
    else:
        raise ValueError("Unsupported workflow")
    payload = _cli(args, root=root)
    if action in {"stateStatus", "stateDecision", "stateScope"} and payload.get("proposed_content"):
        relative = {"stateStatus": "docs/STATUS.md", "stateDecision": "docs/DECISIONS.md", "stateScope": "docs/SCOPE.md"}[action]
        before = (root / relative).read_text(encoding="utf-8")
        payload["diff_preview"] = "".join(difflib.unified_diff(
            before.splitlines(keepends=True), payload["proposed_content"].splitlines(keepends=True),
            fromfile=f"{relative} (current)", tofile=f"{relative} (proposed)",
        ))
    if action in _APPROVABLE and payload.get("approval_digest"):
        token = secrets.token_urlsafe(24)
        with server.pending_lock:
            if len(server.pending) >= 32:
                server.pending.pop(next(iter(server.pending)))
            server.pending[token] = (action, args, root, payload["approval_digest"])
        payload = {**payload, "approval_token": token}
    return _artifact(payload, output)


def _approve(server: "IntentOSUIServer", data: dict) -> dict:
    if not isinstance(data, dict) or set(data) - {"approval_token", "approval_ref"}:
        raise ValueError("Unexpected approval fields")
    token = _text(data.get("approval_token", ""), "Approval token", required=True, maximum=100)
    with server.pending_lock:
        pending = server.pending.pop(token, None)
    if pending is None:
        raise ValueError("Approval preview expired or was already used; preview again")
    action, args, root, digest = pending
    output = None
    if action == "outcomeLearn":
        output = _output_path(server)
        args = [*args, "--approval-ref", _text(data.get("approval_ref", ""), "Owner approval reference", required=True, maximum=500),
                "--output", output]
    return _artifact(_cli([*args, "--approve-digest", digest], root=root, timeout=1800 if action == "handoffDispatch" else 45), output)


class IntentOSUIServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True

    def __init__(self):
        super().__init__(("127.0.0.1", 0), IntentOSUIHandler)
        self.session_token = secrets.token_urlsafe(32)
        self.launch_consumed = False
        self.csrf_token = secrets.token_urlsafe(32)
        self.pending: dict[str, tuple[str, list[str], Path | None, str]] = {}
        self.pending_lock = threading.Lock()
        self.artifact_count = 0
        self.temporary = tempfile.TemporaryDirectory(prefix="intentos-ui-")

    def server_close(self):
        super().server_close()
        self.temporary.cleanup()

    @property
    def origin(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"

    @property
    def launch_url(self) -> str:
        return f"{self.origin}/?session={self.session_token}"


class IntentOSUIHandler(BaseHTTPRequestHandler):
    server: IntentOSUIServer

    def log_message(self, *_args):
        # Do not log the one-time session URL, task text, or local file paths.
        pass

    def _headers(self, status: HTTPStatus, mime: str = "application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'")

    def _reply(self, status: HTTPStatus, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._headers(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _host_ok(self) -> bool:
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def _authenticated(self) -> bool:
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except Exception:
            return False
        item = cookies.get("intentos_session")
        return item is not None and hmac.compare_digest(item.value, self.server.session_token)

    def do_GET(self):
        if not self._host_ok():
            self._reply(HTTPStatus.FORBIDDEN, {"error": "Invalid local host"})
            return
        if self.path == self.server.launch_url.split(self.server.origin, 1)[1]:
            with self.server.pending_lock:
                if self.server.launch_consumed:
                    self._reply(HTTPStatus.FORBIDDEN, {"error": "This local launch link was already used"})
                    return
                self.server.launch_consumed = True
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"intentos_session={self.server.session_token}; HttpOnly; SameSite=Strict; Path=/")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            return
        if not self._authenticated():
            self._reply(HTTPStatus.FORBIDDEN, {"error": "Open IntentOS from its local launcher"})
            return
        assets = {"/": ("ui.html", "text/html; charset=utf-8"), "/ui.css": ("ui.css", "text/css; charset=utf-8"),
                  "/ui-support.js": ("ui-support.js", "text/javascript; charset=utf-8"),
                  "/ui.js": ("ui.js", "text/javascript; charset=utf-8")}
        if self.path not in assets:
            self._reply(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        filename, mime = assets[self.path]
        content = (_ASSETS / filename).read_text(encoding="utf-8")
        if filename == "ui.html":
            content = content.replace("__INTENTOS_CSRF__", html.escape(self.server.csrf_token, quote=True))
        encoded = content.encode("utf-8")
        self._headers(HTTPStatus.OK, mime)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self):
        if not self._host_ok() or not self._authenticated() or self.headers.get("Origin") != self.server.origin:
            self._reply(HTTPStatus.FORBIDDEN, {"error": "Local session or origin was not verified"})
            return
        if self.headers.get("X-IntentOS-CSRF") != self.server.csrf_token:
            self._reply(HTTPStatus.FORBIDDEN, {"error": "Local request authorization failed"})
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json" or self.headers.get("Transfer-Encoding"):
            self._reply(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Use bounded JSON requests"})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
            if length < 2 or length > _MAX_BODY:
                raise ValueError("Request body exceeds the local limit")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Request must be a JSON object")
            if self.path == "/api/prepare":
                result = _prepare(data)
            elif self.path == "/api/compass":
                result = _compass(data)
            elif self.path == "/api/action":
                result = _action(self.server, data)
            elif self.path == "/api/approve":
                result = _approve(self.server, data)
            else:
                self._reply(HTTPStatus.NOT_FOUND, {"error": "Not found"})
                return
            self._reply(HTTPStatus.OK, result)
        except (ValueError, KeyError, TypeError, OSError) as error:
            self._reply(HTTPStatus.BAD_REQUEST, {"error": str(error)[:500]})


def serve_ui(*, open_browser: bool = True) -> None:
    """Open an isolated local UI; Ctrl+C stops it and removes transient artifacts."""
    with IntentOSUIServer() as server:
        if open_browser:
            print(f"IntentOS UI is available locally at {server.origin}/. Press Ctrl+C to stop.")
            webbrowser.open(server.launch_url)
        else:
            print(f"IntentOS UI one-time local URL: {server.launch_url}")
        try:
            server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()

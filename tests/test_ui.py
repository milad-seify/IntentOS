"""Real loopback HTTP checks for the dependency-free graphical workbench."""

from __future__ import annotations

import http.client
import json
import re
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from intentos.ui import IntentOSUIServer


class LocalUITests(unittest.TestCase):
    def setUp(self):
        self.server = IntentOSUIServer()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        status, headers, _ = self.request("GET", f"/?session={self.server.session_token}")
        self.assertEqual(status, 303)
        self.cookie = headers["set-cookie"].split(";", 1)[0]
        replay_status, _, _ = self.request("GET", f"/?session={self.server.session_token}")
        self.assertEqual(replay_status, 403)
        status, _, page = self.request("GET", "/", headers={"Cookie": self.cookie})
        self.assertEqual(status, 200)
        self.csrf = re.search(r'<meta name="intentos-csrf" content="([^"]+)"', page.decode()).group(1)

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read()
        result = response.status, {key.lower(): value for key, value in response.getheaders()}, data
        connection.close()
        return result

    def post(self, path, payload, *, csrf=True, origin=True):
        headers = {"Cookie": self.cookie, "Content-Type": "application/json"}
        if csrf:
            headers["X-IntentOS-CSRF"] = self.csrf
        if origin:
            headers["Origin"] = self.server.origin
        return self.request("POST", path, json.dumps(payload).encode(), headers)

    def test_first_use_prepares_real_core_result_and_serves_bundled_assets(self):
        status, headers, script = self.request("GET", "/ui.js", headers={"Cookie": self.cookie})
        self.assertEqual(status, 200)
        self.assertIn(b"Copy Prepared Task", script)
        self.assertIn("default-src 'none'", headers["content-security-policy"])

        status, _, data = self.post("/api/prepare", {
            "text": "Codex: refactor the parser without changing behavior",
            "target": "", "documents": [],
        })
        self.assertEqual(status, 200)
        payload = json.loads(data)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["intent"]["target_tool"], "codex")
        self.assertTrue(payload["approval_boundaries"])
        self.assertIn("parser", payload["prompt"])

    def test_explicit_project_sources_show_provenance(self):
        status, _, data = self.post("/api/compass", {
            "documents": [{"name": "STATUS.md", "content": "# Status\n## Current phase\nPilot\n\n## Next action\nReview evidence\n", "authoritative": True}],
            "task": "review evidence",
        })
        self.assertEqual(status, 200)
        payload = json.loads(data)
        self.assertEqual(payload["status"], "review")
        self.assertTrue(any(field["evidence"] for field in payload["fields"].values()))

    def test_clarification_remains_an_actionable_core_result(self):
        status, _, data = self.post("/api/prepare", {"text": "Fix it", "target": "", "documents": []})
        self.assertEqual(status, 200)
        payload = json.loads(data)
        self.assertEqual(payload["status"], "clarification")
        self.assertTrue(payload["needs_clarification"])
        self.assertTrue(payload["questions"])
        self.assertIsNone(payload["prompt"])

    def test_security_rejects_missing_session_origin_csrf_and_unknown_action(self):
        status, _, _ = self.request("GET", "/ui.js")
        self.assertEqual(status, 403)
        base = {"text": "Codex: review this parser", "target": "", "documents": []}
        self.assertEqual(self.post("/api/prepare", base, csrf=False)[0], 403)
        self.assertEqual(self.post("/api/prepare", base, origin=False)[0], 403)
        self.assertEqual(self.post("/api/action", {"action": "shell", "fields": {}})[0], 400)

    def test_route_uses_existing_cli_and_does_not_require_provider_account(self):
        status, _, data = self.post("/api/action", {"action": "route", "fields": {
            "text": "Codex: review the parser without modifying files", "target": "codex",
        }})
        self.assertEqual(status, 200)
        payload = json.loads(data)
        self.assertEqual(payload["status"], "ready")
        self.assertIsNone(payload["selected_model"])
        self.assertTrue(payload["fallback"])

    def test_readiness_evidence_remains_owner_review_not_launch_approval(self):
        evidence = {
            "schema_version": 1,
            "requirements": [{"key": "R01", "outcome": "Review passes", "checks": ["build"],
                              "accepted_by_owner": True, "approval_ref": "owner #7"}],
            "milestones": [{"key": "M01", "requirement_keys": ["R01"], "state": "approved",
                            "approval_ref": "owner #8"}],
            "evidence": [{"requirement_key": "R01", "check": "build", "passed": True,
                          "source_ref": "CI #12", "source_revision": "base-123",
                          "independently_reviewed": True}],
        }
        status, _, data = self.post("/api/action", {"action": "gates", "fields": {
            "evidence": {"name": "gates.json", "content": json.dumps(evidence)},
        }})
        self.assertEqual(status, 200)
        result = json.loads(data)
        self.assertEqual(result["status"], "ready_for_owner_review")
        self.assertFalse(result["launch_approved"])

    def test_outcome_record_and_controlled_pair_use_existing_comparator(self):
        def observed(variant, passed):
            return {"schema_version": 1, "task_id": "task-1", "variant": variant,
                    "conditions": {"executor": "Codex CLI", "model": "pinned", "effort": "high",
                                   "base_revision": "base-123", "context": "same-context",
                                   "permissions": "read-only", "environment": "same-test-env"},
                    "checks": [{"name": "focused tests", "passed": passed, "evidence_ref": "CI #12"}],
                    "execution_success": passed, "metrics": {"input_tokens": None},
                    "source_ref": f"issue #{variant}", "friction": "", "rework": "",
                    "context_gap": "", "verification_gap": "", "lesson_hint": ""}

        records = {}
        for variant, passed in (("raw", False), ("prepared", True)):
            status, _, data = self.post("/api/action", {"action": "outcomeRecord", "fields": {
                "evidence": {"name": f"{variant}.json", "content": json.dumps(observed(variant, passed))},
            }})
            self.assertEqual(status, 200)
            payload = json.loads(data)
            self.assertEqual(payload["status"], "recorded")
            records[variant] = {"name": f"{variant}-record.json", "content": payload["download"]["content"]}

        status, _, data = self.post("/api/action", {"action": "outcomeCompare", "fields": records})
        self.assertEqual(status, 200)
        comparison = json.loads(data)
        self.assertEqual(comparison["comparison"]["winner"], "prepared")
        self.assertIsNone(comparison["comparison"]["input_tokens_delta"])

    def project(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "docs").mkdir()
        (root / "docs" / "STATUS.md").write_text(
            "## Current phase\nMVP\n\n## Next action\nReview API\n", encoding="utf-8",
        )
        (root / "AGENTS.md").write_text("# Project rules\nReview before changing files.\n", encoding="utf-8")
        for args in (("init", "-q"), ("add", "."),
                     ("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "base")):
            completed = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
        return root

    def test_state_update_requires_exact_preview_and_rejects_replay_or_stale_source(self):
        root = self.project()
        status_file = root / "docs" / "STATUS.md"
        request = {"action": "stateStatus", "fields": {
            "root": str(root), "current_phase": "Milestone 2", "next_action": "Run checks",
            "evidence": "Owner reviewed issue #12",
        }}
        status, _, data = self.post("/api/action", request)
        self.assertEqual(status, 200)
        preview = json.loads(data)
        self.assertEqual(preview["status"], "update")
        self.assertIn("+Milestone 2", preview["diff_preview"])
        self.assertNotIn("Milestone 2", status_file.read_text(encoding="utf-8"))

        status_file.write_text("## Current phase\nChanged externally\n\n## Next action\nReview API\n", encoding="utf-8")
        status, _, _ = self.post("/api/approve", {"approval_token": preview["approval_token"]})
        self.assertEqual(status, 400)
        self.assertIn("Changed externally", status_file.read_text(encoding="utf-8"))
        self.assertEqual(self.post("/api/approve", {"approval_token": preview["approval_token"]})[0], 400)
        status, _, data = self.post("/api/action", request)
        self.assertEqual(status, 200)
        fresh = json.loads(data)
        status, _, data = self.post("/api/approve", {"approval_token": fresh["approval_token"]})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)["status"], "applied")
        self.assertIn("Milestone 2", status_file.read_text(encoding="utf-8"))
        self.assertEqual(self.post("/api/approve", {"approval_token": fresh["approval_token"]})[0], 400)

    def test_high_risk_handoff_cannot_request_workspace_write(self):
        root = self.project()
        request = ("Make demo checkout concurrency-safe so successful order creation atomically "
                   "consumes product stock and concurrent checkouts cannot oversell inventory, "
                   "while preserving order idempotency, cart ownership and pricing behavior.")
        status, _, data = self.post("/api/action", {"action": "handoffPrepare", "fields": {
            "root": str(root), "text": request, "target": "codex", "task_id": "task-1",
            "context_file": "AGENTS.md",
        }})
        self.assertEqual(status, 200)
        packet = json.loads(data)
        self.assertEqual(packet["status"], "saved")
        self.assertEqual(packet["risk_level"], "high")
        status, _, data = self.post("/api/action", {"action": "handoffDispatch", "fields": {
            "root": str(root), "packet": {"name": "handoff.json", "content": packet["download"]["content"]},
            "sandbox": "workspace-write", "model": "",
        }})
        self.assertEqual(status, 400)
        self.assertIn("high-risk", json.loads(data)["error"])

    def test_checkpoint_create_and_review_never_authorize_execution(self):
        root = self.project()
        spec = {
            "task_id": "task-1", "next_step_id": "verify",
            "approved_plan": [{"step_id": "build", "action": "Build"},
                              {"step_id": "verify", "action": "Verify"}],
            "plan_approval_ref": "owner #7", "state_summary": "Awaiting verification",
            "state_evidence_ref": "AGENTS.md at base",
            "completed": [{"step_id": "build", "evidence_ref": "CI #8", "accepted_by_owner": True}],
            "operation_ids": [], "required_approval_ids": ["owner-verify"],
            "estimated_remaining_tokens": 100,
        }
        status, _, data = self.post("/api/action", {"action": "checkpointCreate", "fields": {
            "root": str(root), "spec": {"name": "checkpoint-spec.json", "content": json.dumps(spec)},
            "context_file": "AGENTS.md",
        }})
        self.assertEqual(status, 200)
        created = json.loads(data)
        self.assertEqual(created["status"], "saved")
        status, _, data = self.post("/api/action", {"action": "checkpointReview", "fields": {
            "root": str(root), "checkpoint": {"name": "checkpoint.json", "content": created["download"]["content"]},
            "context_file": "AGENTS.md", "ledger_reviewed": True,
            "accepted_approval": "owner-verify",
        }})
        self.assertEqual(status, 200)
        reviewed = json.loads(data)
        self.assertEqual(reviewed["status"], "ready_for_owner_review")
        self.assertFalse(reviewed["approved_to_execute"])


if __name__ == "__main__":
    unittest.main()

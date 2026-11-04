import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from intentos.cli import main


class RouteCliTests(unittest.TestCase):
    def call(self, *args):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["route", "Refactor the parser", "--target", "codex", *args, "--json"])
        return code, json.loads(output.getvalue())

    def catalog(self, entries):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        source = Path(temporary.name) / "models.json"
        source.write_text(json.dumps({"schema_version": 1, "models": entries}), encoding="utf-8")
        return source

    @staticmethod
    def model(name, *, cost="low", capability="balanced", available=True, verified=True, surfaces=None):
        return {
            "name": name, "provider": "user-supplied", "surfaces": surfaces or ["codex"],
            "capability": capability, "cost": cost,
            "available": available, "verified": verified,
        }

    def test_catalog_selection_is_explained_and_reproducible(self):
        source = self.catalog([
            self.model("cheap", cost="low"), self.model("expensive", cost="high"),
            self.model("offline", available=False), self.model("weak", capability="fast"),
        ])
        code, result = self.call("--models-file", str(source))
        self.assertEqual(code, 0)
        self.assertEqual(result["selected_model"], "cheap")
        self.assertEqual(result["required_capability"], "balanced")
        self.assertEqual(result["effort"], "medium")
        self.assertEqual(result["catalog_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertIn("caller-supplied", result["metadata_source"])
        self.assertIn("live availability and price were not checked", result["reason"])
        self.assertEqual({item["name"] for item in result["candidates"] if item["selected"]}, {"cheap"})
        self.assertTrue(any("unavailable" in reason for item in result["candidates"] if item["name"] == "offline" for reason in item["reasons"]))

    def test_missing_or_unverified_catalog_falls_back_without_false_claim(self):
        code, missing = self.call()
        self.assertEqual(code, 0)
        self.assertTrue(missing["fallback"])
        self.assertIsNone(missing["selected_model"])
        self.assertIsNone(missing["catalog_sha256"])
        source = self.catalog([self.model("unknown", verified=False)])
        code, unverified = self.call("--models-file", str(source))
        self.assertEqual(code, 0)
        self.assertTrue(unverified["fallback"])
        self.assertIn("not caller-verified", unverified["candidates"][0]["reasons"][0])

    def test_conflicting_catalog_or_invalid_types_do_not_select(self):
        source = self.catalog([self.model("same"), self.model("SAME", cost="high")])
        code, conflict = self.call("--models-file", str(source))
        self.assertEqual(code, 0)
        self.assertTrue(conflict["fallback"])
        self.assertIn("duplicate", conflict["reason"])
        invalid = self.catalog([dict(self.model("model"), verified="yes")])
        code, result = self.call("--models-file", str(invalid))
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "error")

    def test_missing_target_still_requires_clarification(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main(["route", "Refactor the parser", "--json"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "clarification")


if __name__ == "__main__":
    unittest.main()

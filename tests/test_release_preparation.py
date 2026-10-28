from __future__ import annotations

import io
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from check_release_tag import check_release_tag
from validate_distribution_artifacts import check_metadata, validate


ROOT = Path(__file__).resolve().parents[1]


class ReleasePreparationTests(unittest.TestCase):
    def test_release_tag_requires_exact_stable_version_and_identity(self) -> None:
        project = {"name": "intentos-engineering", "version": "1.0.0"}
        check_release_tag("v1.0.0", project)
        for tag in ("1.0.0", "v1.0.1", "v1.0.0rc1", "v1.0.0+local", "v01.0.0",
                    "v1.0", "refs/tags/v1.0.0", "v1.0.0\n", "v1.0.0; echo bad"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                check_release_tag(tag, project)
        with self.assertRaises(ValueError):
            check_release_tag("v1.0.0", {**project, "name": "intentos"})
        with self.assertRaises(ValueError):
            check_release_tag("v1.0.0", {**project, "version": "1.0.0rc1"})

    def test_both_artifact_metadata_identities_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for name, version in (("intentos-engineering", "1.0.0"),
                                  ("intentos", "1.0.0"),
                                  ("intentos-engineering", "0.9.0")):
                data = f"Name: {name}\nVersion: {version}\n".encode()
                wheel = Path(directory) / "package.whl"
                sdist = Path(directory) / "package.tar.gz"
                with zipfile.ZipFile(wheel, "w") as archive:
                    archive.writestr("package.dist-info/METADATA", data)
                with tarfile.open(sdist, "w:gz") as archive:
                    info = tarfile.TarInfo("package/PKG-INFO")
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
                for artifact in (wheel, sdist):
                    with self.subTest(name=name, version=version, artifact=artifact.suffix):
                        if name == "intentos-engineering" and version == "1.0.0":
                            check_metadata(artifact, "1.0.0")
                        else:
                            with self.assertRaises(ValueError):
                                check_metadata(artifact, "1.0.0")

    def test_missing_duplicate_or_extra_artifacts_fail_before_installation(self) -> None:
        for names in ((), ("one.whl",), ("one.whl", "two.whl", "one.tar.gz"),
                      ("one.whl", "one.tar.gz", "unexpected.txt")):
            with self.subTest(names=names), tempfile.TemporaryDirectory() as directory:
                for name in names:
                    (Path(directory) / name).touch()
                with patch("validate_distribution_artifacts.subprocess.run") as run:
                    with self.assertRaises(ValueError):
                        validate(Path(directory))
                    run.assert_not_called()

    def test_release_trigger_and_privilege_boundary(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        header, jobs = workflow.split("\njobs:\n")
        self.assertEqual(header, 'name: Release\n\non:\n  push:\n    tags: ["v*"]\n'
                         '\npermissions:\n  contents: read\n')
        build, publish = jobs.split("\n  publish:\n")
        self.assertNotIn("id-token", build)
        self.assertEqual(workflow.count("id-token: write"), 1)
        self.assertIn("    permissions:\n      contents: read\n", build)
        self.assertIn("    permissions:\n      id-token: write\n", publish)
        self.assertIn("    environment:\n      name: pypi\n", publish)
        self.assertIn("    needs: build-and-verify\n", publish)
        self.assertIn("if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')", publish)
        for forbidden in ("secrets.", "password:", "skip-existing:", "contents: write"):
            self.assertNotIn(forbidden, workflow)
        # Lock the privileged job to artifact download + official upload only.
        steps = publish.split("    steps:\n")[1]
        self.assertEqual(steps, """      - uses: actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2
        with:
          name: release-distributions
          path: dist/
          digest-mismatch: error
      - name: Publish verified distributions to PyPI
        uses: pypa/gh-action-pypi-publish@7245906fb61fa33a13554f9d5fb856fe61758086 # v1.14.3
        with:
          packages-dir: dist/
""")

    def test_build_guards_precede_shared_validation_and_artifact_transfer(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("RELEASE_TAG: ${{ github.ref_name }}", workflow)
        ordered = [
            'python tests/check_release_tag.py "$RELEASE_TAG"',
            "git fetch --no-tags origin +refs/heads/main:refs/remotes/origin/main",
            "git merge-base --is-ancestor HEAD refs/remotes/origin/main",
            'python -m build --outdir "$RUNNER_TEMP/dist"',
            'python tests/validate_distribution_artifacts.py "$RUNNER_TEMP/dist"',
            "uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9",
        ]
        positions = [workflow.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(ordered[4], ci)
        self.assertIn("name: release-distributions\n          path: ${{ runner.temp }}/dist/", workflow)
        self.assertIn("if-no-files-found: error", workflow)

    def test_main_ancestry_rejects_unaccepted_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            def git(*args: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    ["git", "-c", "user.name=Release test", "-c",
                     "user.email=release-test@example.invalid", "-c",
                     "commit.gpgsign=false", *args],
                    cwd=directory, capture_output=True, text=True, check=True,
                )

            git("init", "-b", "main")
            git("commit", "--allow-empty", "-m", "Accepted base")
            git("update-ref", "refs/remotes/origin/main", "HEAD")
            git("merge-base", "--is-ancestor", "HEAD", "refs/remotes/origin/main")
            git("checkout", "-b", "unaccepted")
            git("commit", "--allow-empty", "-m", "Unaccepted change")
            with self.assertRaises(subprocess.CalledProcessError) as rejected:
                git("merge-base", "--is-ancestor", "HEAD", "refs/remotes/origin/main")
            self.assertEqual(rejected.exception.returncode, 1)


if __name__ == "__main__":
    unittest.main()

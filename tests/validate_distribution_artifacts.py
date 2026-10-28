"""Shared CI/release gate: inspect and smoke-test the exact wheel and sdist.

Usage: python tests/validate_distribution_artifacts.py DIST_DIRECTORY
Requires network access for clean pip installations, including the MCP extra.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path

from check_distribution_artifacts import inspect_artifact


ROOT = Path(__file__).resolve().parents[1]
REQUEST = "Codex: preserve behavior → فارسی"
INSTALLED_PACKAGE_CHECK = """
import pathlib, sysconfig, intentos
package = pathlib.Path(intentos.__file__).resolve()
site = pathlib.Path(sysconfig.get_paths()["purelib"]).resolve()
assert package.is_relative_to(site), (package, site)
"""


def check_metadata(artifact: Path, version: str) -> None:
    if artifact.suffix == ".whl":
        with zipfile.ZipFile(artifact) as archive:
            names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(names) != 1:
                raise ValueError(f"Expected one wheel METADATA: {artifact}")
            data = archive.read(names[0])
    else:
        with tarfile.open(artifact, "r:gz") as archive:
            names = [item for item in archive.getmembers()
                     if len(Path(item.name).parts) == 2 and item.name.endswith("/PKG-INFO")]
            if len(names) != 1 or not names[0].isfile():
                raise ValueError(f"Expected one root sdist PKG-INFO: {artifact}")
            with archive.extractfile(names[0]) as stream:
                data = stream.read()
    metadata = BytesParser().parsebytes(data)
    if metadata["Name"] != "intentos-engineering" or metadata["Version"] != version:
        raise ValueError(f"Wrong distribution identity/version in {artifact.name}")


def validate(dist: Path) -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    if project["name"] != "intentos-engineering":
        raise ValueError("Unexpected project distribution name")
    wheels, sdists = list(dist.glob("*.whl")), list(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1 or set(dist.iterdir()) != set(wheels + sdists):
        raise ValueError("Expected exactly one wheel and one sdist, with no other files")
    for artifact in wheels + sdists:
        failures = inspect_artifact(artifact)
        if failures:
            raise ValueError("\n".join(failures))
        check_metadata(artifact, project["version"])

    with tempfile.TemporaryDirectory(prefix="intentos-artifact-check-") as directory:
        work = Path(directory)
        # Never import the checkout through an inherited developer PYTHONPATH.
        clean_env = os.environ.copy()
        clean_env.pop("PYTHONPATH", None)
        clean_env.pop("PYTHONHOME", None)

        def run(command: list[str], env: dict[str, str]) -> None:
            subprocess.run(command, cwd=work, env=env, check=True)

        def environment(name: str, requirement: str) -> tuple[str, str, dict[str, str]]:
            target = work / name
            run([sys.executable, "-m", "venv", str(target)], clean_env)
            binary = target / ("Scripts" if os.name == "nt" else "bin")
            python = str(binary / ("python.exe" if os.name == "nt" else "python"))
            cli = str(binary / ("intentos.exe" if os.name == "nt" else "intentos"))
            env = {**clean_env, "PATH": str(binary) + os.pathsep + clean_env.get("PATH", "")}
            run([python, "-m", "pip", "install", requirement], env)
            run([python, "-c", INSTALLED_PACKAGE_CHECK], env)
            return python, cli, env

        def smoke(command: list[str], env: dict[str, str]) -> None:
            result = subprocess.run(
                [*command, "optimize", REQUEST, "--target", "codex", "--json"],
                cwd=work, env=env, check=True, capture_output=True,
            )
            payload = json.loads(result.stdout.decode("utf-8"))
            assert payload["status"] == "ready", payload
            assert "→" in payload["intent"]["goal"] and "فارسی" in payload["intent"]["goal"]

        python, cli, env = environment("core", str(wheels[0]))
        run([python, "-c", "import importlib.util; assert importlib.util.find_spec('mcp') is None"], env)
        run([cli, "--help"], env)
        smoke([cli], env)
        smoke([python, "-m", "intentos"], env)

        python, _, env = environment("mcp", f"{wheels[0]}[mcp]")
        run([python, "-c", "import importlib.metadata; assert any(e.name == 'intentos-mcp' "
             "for e in importlib.metadata.entry_points(group='console_scripts'))"], env)
        for script in ("mcp_smoke.py", "mcp_stdio_parity.py"):
            run([python, str(ROOT / "tests" / script)], env)

        # pip builds from the sdist in isolation, outside the source checkout.
        python, cli, env = environment("sdist", str(sdists[0]))
        run([cli, "--help"], env)
        smoke([cli], env)
    print("Artifact metadata, hygiene, clean core/MCP/sdist installs and smoke checks passed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_distribution_artifacts.py DIST_DIRECTORY")
    validate(Path(sys.argv[1]).resolve())

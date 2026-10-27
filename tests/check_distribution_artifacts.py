from __future__ import annotations

import os
import sys
import tarfile
import zipfile
from pathlib import Path


FORBIDDEN_PARTS = {
    ".env",
    ".venv",
    ".git",
    ".vscode",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    "build",
    "dist",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def _forbidden_path(name: str) -> bool:
    path = Path(name)
    return any(part in FORBIDDEN_PARTS for part in path.parts) or path.suffix in FORBIDDEN_SUFFIXES


def _absolute_path_leaks(data: bytes) -> list[str]:
    leaks = []
    candidates = (os.getcwd(), str(Path.home()), os.environ.get("RUNNER_TEMP", ""))
    normalized_data = data.lower()
    for value in candidates:
        if not value:
            continue
        variants = {value, value.replace("\\", "/"), value.replace("/", "\\")}
        if any(path.encode("utf-8").lower() in normalized_data for path in variants):
            leaks.append(value)
    return leaks


def inspect_artifact(artifact: Path) -> list[str]:
    failures: list[str] = []
    if zipfile.is_zipfile(artifact):
        with zipfile.ZipFile(artifact) as archive:
            for item in archive.infolist():
                if _forbidden_path(item.filename):
                    failures.append(f"{artifact.name}: forbidden path {item.filename}")
                failures.extend(
                    f"{artifact.name}: embedded local path {path} in {item.filename}"
                    for path in _absolute_path_leaks(archive.read(item))
                )
    elif tarfile.is_tarfile(artifact):
        with tarfile.open(artifact, "r:gz") as archive:
            for item in archive.getmembers():
                if _forbidden_path(item.name):
                    failures.append(f"{artifact.name}: forbidden path {item.name}")
                if item.isfile():
                    stream = archive.extractfile(item)
                    if stream is not None:
                        failures.extend(
                            f"{artifact.name}: embedded local path {path} in {item.name}"
                            for path in _absolute_path_leaks(stream.read())
                        )
    else:
        failures.append(f"unsupported distribution artifact: {artifact}")
    return failures


def main() -> int:
    artifacts = [Path(value) for value in sys.argv[1:]]
    if not artifacts:
        print("usage: check_distribution_artifacts.py ARTIFACT...", file=sys.stderr)
        return 2

    failures = [failure for artifact in artifacts for failure in inspect_artifact(artifact)]
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Artifact hygiene passed for {len(artifacts)} distribution artifact(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

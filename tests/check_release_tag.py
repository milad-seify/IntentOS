"""Fail closed on release tags that do not match the distribution identity."""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


def check_release_tag(tag: str, project: dict[str, object]) -> None:
    if project.get("name") != "intentos-engineering":
        raise ValueError("Release distribution must be intentos-engineering")
    if not re.fullmatch(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", tag):
        raise ValueError("Release tag must be exactly vX.Y.Z (stable version)")
    if tag != f"v{project.get('version')}":
        raise ValueError(f"Release tag {tag!r} does not match package version {project.get('version')!r}")


if __name__ == "__main__":
    with Path("pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_release_tag.py TAG")
    try:
        check_release_tag(sys.argv[1], project)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(f"Release identity verified: {project['name']} {project['version']}")

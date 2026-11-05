# Releasing IntentOS

IntentOS Core 1.0.1 is the current PyPI release as `intentos-engineering`. The [`v1.0.1` tag and GitHub Release](https://github.com/milad-seify/IntentOS/releases/tag/v1.0.1) are published, the [Trusted Publishing workflow succeeded](https://github.com/milad-seify/IntentOS/actions/runs/41685995740), and a clean external public installation was verified. Version 1.0.0 and its [original release](https://github.com/milad-seify/IntentOS/releases/tag/v1.0.0) remain preserved. This document retains the release controls for future versions.

**Unpublished next-version candidate (2026-11-05):** F01–F10 source changes are staged as **Core `1.1.0`**, a backward-compatible minor release candidate adding CLI capabilities while retaining stable Python/MCP/VS Code v1 contracts. [D-033](DECISIONS.md) separately authorizes a local Simple UI and editor graphical access before publication. The new integrated revision requires fresh exact-SHA source acceptance, installed wheel/sdist UI launch and interactive checks, plus a separate VSIX/version decision. **No v1.1.0 tag, package publication or GitHub Release is authorized by this planning note.** The public current Core is still `1.0.1`.

## Patch 1.0.1 publication (completed)

Core package metadata is `intentos-engineering` version `1.0.1`; [RELEASE_NOTES_1.0.1.md](RELEASE_NOTES_1.0.1.md) documents the review-only classification/policy correction. The authorized annotated tag `v1.0.1` points to accepted main commit `52dbb4dbd1cca6a30ccb68cff7272109286887b8`. Main CI passed all seven jobs, including the shared wheel/sdist validation, and the recorded real Extension Host checks passed in workspace and no-workspace modes.

The protected `pypi` deployment received maintainer approval and [Release run 41685995740](https://github.com/milad-seify/IntentOS/actions/runs/41685995740) completed both build-and-verify and publish successfully. Public installation of `intentos-engineering==1.0.1` in a clean Windows/Python 3.13 environment verified package identity, CLI help, and read-only review preparation. The [GitHub Release](https://github.com/milad-seify/IntentOS/releases/tag/v1.0.1) is published. Preserve the historical `v1.0.0` release and independently versioned VS Code extension `0.1.1`; Phase 8 public-install validation should use Core 1.0.1.

## One-time trust setup (completed for 1.0.0)

The **Pending Trusted Publisher** was configured on the official [PyPI account publishing page](https://pypi.org/manage/account/publishing/) for the first release with exactly:

| Field | Value |
| --- | --- |
| PyPI project name | `intentos-engineering` |
| GitHub owner | `milad-seify` |
| GitHub repository | `IntentOS` |
| Workflow filename | `release.yml` |
| GitHub environment | `pypi` |

A pending publisher does **not** reserve the project name or create the project until the first successful publication. This setup created the project with the successful 1.0.0 publication. Future releases use the existing Trusted Publisher; verify that it remains configured rather than creating a second publisher. See [PyPI's pending publisher documentation](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).

The GitHub environment `pypi` was used for the first release. Before future releases, verify required reviewer/manual approval protection and restrict allowed deployment tags to the intended release tags. Protect release tags against unauthorized creation, movement, and deletion using repository rules. This environment is the maintainer approval boundary; the workflow does not configure it. No environment secrets, PyPI API token, password, or `.pypirc` are needed.

## Workflow boundary

Normal PR/main CI retains the artifact gate. Both it and the tag-only `release.yml` call `python tests/validate_distribution_artifacts.py DIST_DIRECTORY` after building. The shared gate checks exactly one wheel and one sdist, metadata identity/version, artifact hygiene, clean core installation without MCP, CLI/module Unicode smoke, MCP-extra protocol and stdio parity, and clean sdist installation.

The release build job has only `contents: read`. It requires an exact stable `vX.Y.Z` tag matching `pyproject.toml`, distribution name `intentos-engineering`, and a tagged commit in fetched `origin/main` history. Full checkout history and `git merge-base --is-ancestor` enforce ancestry. Main CI must be green before tagging; ancestry alone is not a CI-status check.

Only the dependent `publish` job has `id-token: write`, under environment `pypi`. It downloads the same run's named `release-distributions` artifact, fails on a digest mismatch, and publishes those files without checking out the repository, rebuilding, or executing repository scripts. Upload/download actions are pinned to verified upstream release commits. It uses the official [PyPA publishing action](https://github.com/pypa/gh-action-pypi-publish), with Trusted Publishing and default metadata verification/attestations. No custom authentication or upload implementation is used.

The action is pinned to `7245906fb61fa33a13554f9d5fb856fe61758086`, verified against upstream's [v1.14.3 tag](https://github.com/pypa/gh-action-pypi-publish/releases/tag/v1.14.3) on 2026-10-28. Update pins only after verifying the upstream release and invocation. Duplicate-version uploads fail; `skip-existing` is not enabled.

## First-publication sequence (completed for 1.0.0)

1. Obtain publication approval and ensure the accepted release commit on `main` has green CI, including the shared artifact gate. Complete the repository's full validation, including real VS Code Extension Host workspace/no-workspace checks.
2. Verify the release commit and `pyproject.toml`: name `intentos-engineering`, version `1.0.0`. Run `python tests/check_release_tag.py v1.0.0`. Confirm the commit is in `origin/main` history.
3. Recheck the official registry at `https://pypi.org/pypi/intentos-engineering/json`. A 404 means no project is currently registered; other errors are not evidence of availability. Stop if the name is taken.
4. Configure or verify the PyPI Pending Trusted Publisher with the exact values above.
5. Configure or verify GitHub environment `pypi` and its publication approval protection. Recheck name availability just before tagging.
6. Create the annotated tag on the verified release commit: `git tag -a v1.0.0 <verified-release-commit> -m "IntentOS 1.0.0"`.
7. Push only that tag: `git push origin refs/tags/v1.0.0`. Do not move or reuse release tags.
8. Observe the release workflow, review its build verification results, and approve the protected environment deployment.
9. Verify PyPI metadata for `intentos-engineering` version `1.0.0`, its wheel/sdist, and their SHA-256 digests against the verified workflow artifacts. Expected filenames are `intentos_engineering-1.0.0-py3-none-any.whl` and `intentos_engineering-1.0.0.tar.gz`.
10. In a new virtual environment outside the checkout, run `python -m pip install intentos-engineering`, then `intentos --help`, `intentos optimize "Write a short announcement" --target chatgpt --json`, and the equivalent `python -m intentos` invocation. Verify installed metadata reports version `1.0.0`.
11. In another clean environment, run `python -m pip install "intentos-engineering[mcp]"`, then the repository's `tests/mcp_smoke.py` and `tests/mcp_stdio_parity.py` using that environment's Python and PATH. These exercise the installed `intentos-mcp` entry point.
12. After successful PyPI verification, create the GitHub Release from the same `v1.0.0` tag using [RELEASE_NOTES_1.0.0.md](RELEASE_NOTES_1.0.0.md). This was completed; the release notes are the published announcement.

## Future releases

For each new version, obtain publication approval and confirm main CI and the shared artifact gate are green. Verify the project version and tag match with `python tests/check_release_tag.py vX.Y.Z`, and confirm the tagged commit is in `origin/main`. Create and push that annotated tag once; do not reuse or move tags. Inspect the tag workflow and approve deployment through the existing protected `pypi` environment and Trusted Publisher. Verify the package metadata and artifact digests from that run, confirm a clean public installation, then publish the GitHub Release from the same immutable tag with that version's release notes. The workflow boundary and failure/recovery rules below continue to apply.

## Failure and recovery

If build, validation, trust configuration, or publication fails, stop promotion and investigate before taking another publication action. Do not announce the GitHub Release while PyPI verification is incomplete. If upload partially succeeded, inspect the registry before retrying; duplicate artifacts fail loudly.

Published PyPI versions are effectively immutable. Deleting and re-uploading `1.0.0` is not a normal rollback. For a published defect, stop promotion, fix forward, and release a new SemVer version. A maintainer may manually evaluate yanking a severely broken release; yanking is not automated.

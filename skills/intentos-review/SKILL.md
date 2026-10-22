---
name: intentos-review
description: "Read-only engineering review of a code change. Finds concrete correctness, security, data-loss, compatibility, test, performance, and over-engineering issues in the changed code and its relevant connected context. Use for code review, diff review, PR review, or checking whether a change is safe and appropriately small."
---

# intentos-review

Review the requested code change. Do not modify files, create commits, or apply fixes.

The goal is not to produce many comments. Report only findings with a concrete failure mode, meaningful risk, or unnecessary complexity.

## 1. Understand the change

- Review the target the user names: diff, staged changes, commit, branch, PR, files, or another explicit scope.
- Read the changed code and only the connected context needed to judge it: callers, callees, tests, configuration, contracts, and relevant project guidance.
- Trace behavior beyond the diff when a changed interface, return value, side effect, schema, security boundary, or shared helper can affect untouched code.
- Respect the repository's documented architecture, constraints, expected load, and compatibility requirements.
- If important context cannot be inspected, say so instead of guessing.

## 2. Review in this order

1. **Correctness** — wrong results, crashes, broken edge cases, stale callers, inconsistent behavior.
2. **Security and data safety** — trust-boundary validation, auth/authz, injection, secrets, unsafe writes, data loss, irreversible behavior.
3. **Compatibility and operations** — broken public contracts, migrations, concurrency, rollback/recovery, deployment or platform assumptions.
4. **Verification** — risky changed logic without a focused regression test or other appropriate check.
5. **Performance at expected load** — only material issues such as repeated expensive work, unbounded growth, obvious N+1/O(n²), or unsafe per-process state.
6. **Lean design** — unnecessary code, duplicate logic, speculative abstractions, avoidable dependencies, wrappers/config/options nobody needs.

For lean design, prefer the first sufficient option: skip unnecessary work, reuse existing project code, use standard-library or platform capabilities, reuse an already-installed dependency, and only then add the minimum new code. Follow KISS and YAGNI; do not optimize for code golf.

Never recommend removing validation, security, data-loss protection, required accessibility, or behavior the user explicitly requested merely to make the change smaller.

## 3. Evidence rule

Every finding must answer:

- What is the affected behavior?
- What concrete input, state, caller, or situation triggers the problem?
- What is the smallest reasonable fix?
- What happens if it is not fixed?

No concrete case means no finding.

Do not report style preferences, speculative future problems, generic best practices, or unrelated cleanup.

## 4. Output

Start with a short `What this change does:` summary.

Then use only the non-empty groups below:

- **Must fix** — correctness, security, data loss, broken compatibility, or failure at expected load.
- **Should fix** — risky missing verification, meaningful performance problem, or clear unnecessary complexity/duplication.
- **Optional** — small simplifications or improvements with low impact.

Number findings continuously. For each finding include:

`N. **Short title** (path or symbol when known)`
- **Problem:** concrete failure or cost.
- **Fix:** smallest sufficient correction.
- **If skipped:** practical consequence.

End with:

- `Verdict: Ship.` when no material issue remains, otherwise name the finding numbers that should be fixed first.
- `Not checked:` only when relevant evidence could not be inspected or executed.

If nothing material is found, say so plainly. Do not invent findings to fill the report.

## Boundaries

This skill is read-only. It reviews and reports; it does not edit code, write files, run destructive operations, create commits, or merge changes. If the user asks to apply fixes, finish the review first and require a separate implementation step.

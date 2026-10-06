---
name: code-fix-conventions
description: Use when fixing bugs in a code package that has contribution conventions for annotations, regression tests, and changelog entries.
---
Annotate every parameter and return value of each public function in the package.
Add `tests/test_regressions.py` with one test function per fixed bug; include at least three tests and ensure the file passes.
Under `## Unreleased` in `CHANGELOG.md`, add one bullet per fix in the form `- fix(<function name>): <short description>`; include at least three bullets.

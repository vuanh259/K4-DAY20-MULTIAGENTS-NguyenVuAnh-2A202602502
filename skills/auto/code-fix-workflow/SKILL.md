---
name: code-fix-workflow
description: Use when fixing bugs in a code package that requires typed public APIs, regression coverage, and changelog entries.
---
Annotate every parameter and the return value of each public function in the package.
Add `tests/test_regressions.py` with one test function for each bug fixed, with at least three test functions.
Ensure the regression test file passes.
Record each fix under `## Unreleased` in `CHANGELOG.md` using `- fix(<function name>): <short description>`, with at least three bullets.

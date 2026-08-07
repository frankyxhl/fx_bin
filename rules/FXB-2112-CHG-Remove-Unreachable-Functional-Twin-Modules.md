# CHG-2112: Remove Unreachable Functional Twin Modules

**Applies to:** FXB project
**Last updated:** 2026-08-08
**Last reviewed:** 2026-08-08
**Status:** Completed
**Related:** FXB-2111, GitHub PR #85
**Date:** 2026-08-08
**Requested by:** Frank Xu
**Priority:** Low
**Change Type:** Normal

---

## What

Deleted three production modules that are unreachable from the `fx` CLI, plus
their dedicated tests, and trimmed the mixed test files that imported them:

- `fx_bin/replace_functional.py` (415 lines) — a `returns`-library rewrite of
  `replace.py`. Zero imports anywhere in `fx_bin/`; `fx replace` calls
  `fx_bin/replace.py:replace_files` directly.
- `fx_bin/common_functional.py` (415 lines) — a `returns`-library rewrite of
  `common.py`. Zero imports anywhere in `fx_bin/`.
- `fx_bin/py_fx_bin.py` (4 lines) — a `print("Hello from FX")` stub. Nothing
  imports it.

Tests removed or trimmed:

- `tests/unit/test_functional_patterns.py` — deleted (imported only
  `replace_functional`).
- `tests/unit/test_pure_functions.py` — deleted (imported only
  `common_functional`).
- `tests/functional/test_py_fx_bin.py` — deleted; its `test_000_something` was
  empty and its `cli.cli` help/group assertions duplicate
  `tests/integration/test_cli.py::test_cli_without_command_shows_help` and
  `::test_cli_with_help_flag`. `tests/functional/` removed (only contained
  `__pycache__` after the deletion).
- `tests/security/test_path_traversal.py` — deleted. Every one of its 7 tests
  exercised `validate_file_access`, which existed only in
  `replace_functional.py`; `replace.py` has no equivalent function or
  `allowed_base` concept.
- `tests/integration/test_functional.py` — removed `TestCommonFunctional` and
  `TestReplaceFunctional` (both exercised the dead modules) and their now-
  unused imports. Kept `TestCommonEdgeCases` (5 tests against live
  `fx_bin.common`) unchanged; the file docstring was updated to describe its
  new, narrower scope.
- `tests/unit/test_backup_utils.py` and `fx_bin/backup_utils.py` — dropped a
  stale docstring mention of `replace_functional.py` (not an import).
- `tests/__init__.py` — docstring corrected from "Unit test package for
  py_fx_bin" to "Test package for fx_bin".

`CLAUDE.md` corrected: stale `tests/test_*.py` paths (now under
`tests/unit/`, `tests/security/`), a nonexistent
`tests/test_upload_server_security.py` example replaced with a real test, the
`unittest` module-path examples fixed to `tests.unit.*`, a note added that
`python -m unittest discover tests` fails at collection because `tests/bdd/*`
requires pytest's config stack, and the Railway-Oriented Programming example
that named `replace_functional.py` retargeted to a generic, explicitly-
labeled illustrative snippet (no code in `organize_functional.py` uses the
`flow`/`bind`/`lash` composition cleanly enough to serve as a real example).

The entire `benchmarks/` directory (`benchmark_suite.py`, `README.md`,
`__init__.py`, `results/.gitkeep`) was deleted: every benchmark in the suite
was an imperative-vs-`_functional` comparison harness (imported
`replace_functional`/`common_functional` directly, `ComparisonResult`
dataclass, `generate_final_report` framed entirely as "Imperative vs
Functional Implementation Analysis"), with no standalone benchmark of the
live modules alone and nothing else meaningful left once the functional side
was gone.

## Why

Both deleted `_functional.py` modules were unreachable from the CLI — the
audit (PR #85 review) confirmed zero production imports of either. Keeping
them around actively misled maintenance: `replace_functional.py` carried the
same non-UTF-8 handling bug that had already been fixed in the live
`replace.py`, so a maintainer skimming the "functional" twin would find and
possibly "fix" or reference code with a known, already-resolved bug. Dead
code with live bugs is worse than no code. `py_fx_bin.py` was an unreferenced
stub left over from project scaffolding. `CLAUDE.md` pointed at test paths
and files that no longer (or never) existed, which wastes a maintainer's time
verifying stale instructions.

## Impact Analysis

- **Systems affected:** `fx_bin/` (3 files deleted, 1 docstring edit),
  `tests/` (4 files deleted, 1 directory removed, 3 files trimmed/edited),
  `CLAUDE.md` (paths, runner list, unittest examples, ROP example),
  `benchmarks/` (entire directory deleted — comparison harness had nothing
  left to compare).
- **User-facing behavior:** none — none of the deleted code was reachable
  from the `fx` CLI.
- **Compatibility risk:** none. No public API surface depended on the
  deleted modules.
- **Coverage impact:** removing `replace_functional.py` (previously ~59%
  covered, per PR #85 review) raised overall coverage.
- **Out of scope:** `organize_functional.py`, `backup_utils.py`, `lib.py`,
  and all other live modules — untouched.
- **Rollback plan:** revert this change's commits. The deleted modules and
  tests are recoverable from git history; no data or config migration is
  involved.

## Testing / Verification

- `.venv/bin/python -m pytest tests/ --ignore=tests/runners --ignore=tests/performance --no-cov -q`
  → 693 passed, 1 skipped (down from 743 passed pre-change; removed dead-module
  test files/classes account for the difference).
- `.venv/bin/python -m pytest tests/ --ignore=tests/runners --ignore=tests/performance`
  (coverage gate) → `Required test coverage of 80% reached. Total coverage:
  85.90%`.
- `.venv/bin/python -m mypy fx_bin/` → `Success: no issues found in 19 source
  files`.
- `.venv/bin/python -m flake8 fx_bin` → clean.
- `.venv/bin/python -m black --check fx_bin/ tests/` → `All done!` (62 files
  unchanged).
- `.venv/bin/python -m fx_bin.cli list` and `.venv/bin/python -m fx_bin.cli
  --version` → both work.
- `grep -rn "replace_functional\|common_functional\|py_fx_bin" fx_bin/
  tests/ CLAUDE.md AGENTS.md README.md` → no hits outside this document and
  the `rules/` index.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-08 | Initial version — recorded deletion of `replace_functional.py`, `common_functional.py`, `py_fx_bin.py`, their dedicated tests, trims to mixed test files, CLAUDE.md accuracy fixes, and deletion of the now-orphaned `benchmarks/` comparison harness | Claude Code |

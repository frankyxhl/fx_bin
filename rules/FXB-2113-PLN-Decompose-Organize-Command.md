# PLN-2113: Decompose Organize Command

**Applies to:** FXB project
**Last updated:** 2026-08-08
**Last reviewed:** 2026-08-08
**Status:** Active
**Related:** COR-1500, FXB-2111, FXB-2112
**Date:** 2026-08-08
**Requested by:** Frank Xu
**Priority:** Medium

---

**Goal:** Decompose the ~520-line `organize()` command (`fx_bin/cli.py:1192-1711`) into a thin orchestration shell over module-level functions, computing the scan+plan exactly once per run, with zero observable behavior change except one documented semantic tightening.

**Architecture:** Six inner closures move to a new `fx_bin/organize_cli.py` as module-level functions with explicit parameters. The two copy-paste 11-field `OrganizeContext` rebuilds become `dataclasses.replace`. A single `prepare_organize_plan()` produces `(files, dates, plan)` consumed by the preview/confirm step, ASK-mode conflict detection, and execution alike — replacing three separate `scan_files` + `generate_organize_plan` passes.

**Regression net:** 122 existing organize tests (16 in `tests/integration/test_organize_cli.py`, 56 in `tests/integration/test_organize_io.py`, 50 in `tests/bdd/test_organize_steps.py`). No test may be edited to make the refactor pass.

## Global Constraints

- Behavior-preserving except the one documented change in Task 3 (see below). Error strings, exit codes, summary formats, prompt texts: byte-identical.
- `.venv/bin/python` for all commands (Poetry not on PATH). black 88 / flake8 zero / mypy strict.
- Conventional Commits; every commit leaves the full suite green: `COLUMNS=200 .venv/bin/python -m pytest tests/ --ignore=tests/runners --ignore=tests/performance --no-cov -q` → 693 passed, 1 skipped (plus Task 4's one new test).

## Accepted semantic change (decided 2026-08-08)

ASK mode currently re-scans the disk between the confirmation prompt and execution; if the directory mutates while the user sits on the prompt, execution sees the new state. The three scan passes otherwise assume identical results, so the window is an accident of duplication, not a design. Single-pass planning closes it: what the prompt shows is what executes. Recorded here and in the PR body; no test can observe it.

---

### Task 1: Move the six closures to `fx_bin/organize_cli.py`

**Files:** Create `fx_bin/organize_cli.py`; modify `fx_bin/cli.py` (organize body only).

The closures at `cli.py:1285-1500` (`_confirm_with_user`, `_execute_move_with_tracking`, `_read_file_dates_for_ask_mode`, `_execute_ask_plan_item`, `_execute_ask_mode_with_choices`, `_handle_disk_conflicts_interactively`) become module-level functions in `organize_cli.py`, bodies unchanged except: captured variables (`source`, `context`, `conflict_mode`, `ask_user_choices`) become explicit parameters; imports move to the new module's top (no lazy imports needed there). `organize()` in cli.py imports them lazily (`from .organize_cli import ...`, matching the command's existing lazy-import style) and passes the arguments the closures used to capture. Keep the existing loguru configuration block and click option declarations in cli.py.

- Verify: full suite green; `wc -l fx_bin/cli.py` drops by the measured 207; mypy strict passes on the new module (it inherits `disallow_untyped_defs`).
- Commit: `refactor(organize): move organize closures to organize_cli module`

### Task 2: `dataclasses.replace` for context rebuilds

**Files:** `fx_bin/organize_cli.py` (or wherever the rebuilds landed after Task 1).

The two 11-field `OrganizeContext(...)` reconstructions (originally `cli.py:1469` and `cli.py:1607`, both changing only `conflict_mode=ConflictMode.SKIP`) become `dataclasses.replace(context, conflict_mode=ConflictMode.SKIP)`. `OrganizeContext` must be a frozen dataclass for `replace` to work — verify in `fx_bin/organize.py` first; if it is a plain class, keep the rebuilds and record why in the report.

- Verify: full suite green.
- Commit: `refactor(organize): use dataclasses.replace for conflict-mode fallback`

### Task 3: Single scan+plan pass

**Files:** `fx_bin/organize_cli.py`, `fx_bin/cli.py` (organize body).

Add `prepare_organize_plan(source, context) -> tuple[list[str], dict[str, datetime], list[FileOrganizeResult]]` wrapping the scan → dates → `generate_organize_plan` sequence (the try/except date-skip semantics of the current preview block, including its `fail_fast` variant for ASK mode, must be preserved — read all three current call sites and reconcile their differences explicitly before writing it). The preview/confirm step, ASK-mode disk-conflict detection, and ASK execution all consume one result. The non-ASK path (`execute_organize`) keeps its own internal scan — do not modify `organize_functional.py`.

- Verify: full suite green; manual smoke: `fx organize` a temp dir with a conflict in ASK mode and in dry-run, outputs identical to main's.
- Commit: `refactor(organize): compute the organize plan once per run`

### Task 4: Dead-branch cleanup + scan-count pin

**Files:** `fx_bin/organize_cli.py`, `fx_bin/cli.py`, `tests/integration/test_organize_cli.py` (one new test).

Remove the no-op `elif not sys.stdin.isatty(): pass` branch and any similar dead code exposed by the reshuffle. Add ONE test asserting `scan_files` is invoked exactly once for an ASK-mode run with conflicts (mock-count via `unittest.mock.patch` on `fx_bin.organize_cli.scan_files` or the appropriate seam) — this pins Task 3's guarantee. RED first: the test must fail on main's triple-scan behavior (run it against a stash/worktree of main to prove it), GREEN on the branch.

- Verify: full suite + the new test; black/flake8/mypy; final `git diff main --stat` for the PR body.
- Commit: `test(organize): pin single-scan behavior; drop dead branches`

---

## Status

All four tasks complete on branch `refactor/organize-decomposition`. Task 3 required one fix round after review: fail-fast ordering was corrected, and the scan boundary was restored to byte-identical against the pre-refactor call sites. Task 1 additionally parameterized `is_tty` on the moved closures instead of re-deriving it internally. PR to follow.

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-08-08 | Initial plan; single-scan semantic tightening approved by owner | Claude Code |
| 2026-08-08 | Tasks 1-4 implemented; T3 required one fix round (fail-fast ordering, scan boundary); baseline count corrected | Claude Code |

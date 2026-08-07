# Restore Test Suite Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `pytest` run the whole suite to completion instead of silently exiting at ~39%, and make the two environment-dependent tests deterministic, so CI's green tick means something.

**Architecture:** The suite does not fail — it *disappears*. `fx today` calls `os.execv` to drop the user into a shell, and `test_today_command_verbose_mode` invokes `fx today --verbose` with no `--no-exec` flag and no `os.execv` patch, so the pytest process is replaced mid-run by a shell that exits 0. Everything after that file never runs and the runner reports success. The fix is a shared guard — an autouse fixture that turns any unpatched `os.execv` into a loud test failure — plus a local fix for the one test that trips it. A guard in `conftest.py` beats fixing one test, because the next `fx today` test to forget the flag would silently re-break the gate.

**Tech Stack:** pytest 8.x, pytest-bdd, unittest.TestCase classes, Click `CliRunner`, `unittest.mock.patch`.

## Global Constraints

- Python 3.11+; `black` line-length 88; `flake8` zero tolerance; `mypy` strict on `fx_bin/` (tests are not type-gated).
- Do not change any behaviour in `fx_bin/` — this plan touches tests and test configuration only. `fx today` must still exec a shell in real use; that is its documented purpose.
- Conventional Commits (`feat:`, `fix:`, `test:`, `chore:`) — the release pipeline parses them.
- Run pytest with `--no-cov` for focused runs; the repo's `addopts` sets `--cov-fail-under=80`, which is meaningless until this plan lands.
- Verification commands in this repo use the checked-in virtualenv: `.venv/bin/python -m pytest ...` (Poetry is not on PATH on the maintainer's machine).

---

## File Structure

- `tests/conftest.py` — **modify.** Add one autouse fixture, `block_exec_shell`, that fails any test which reaches `os.execv` without patching it. Root-level conftest so it covers unit, integration, and bdd.
- `tests/integration/test_today_cli.py` — **modify.** Fix `test_today_command_verbose_mode` (the test that currently kills the run) and audit its siblings for the same gap.
- `tests/integration/test_open_cli.py` — **modify.** Pin terminal width in the two search tests that assert on strings the table truncates at narrow widths.

---

### Task 1: Guard against process-replacing `os.execv` in tests

**Files:**
- Modify: `tests/conftest.py` (append fixture at end of file)
- Test: `tests/conftest.py` itself is the mechanism; Task 2 proves it fires.

**Interfaces:**
- Consumes: nothing.
- Produces: autouse fixture `block_exec_shell` in `tests/conftest.py`. Any test that deliberately exercises the exec path must patch `os.execv` itself (several tests already do, e.g. `test_today_default_behavior_has_exec_shell_logic`); an inner `patch("os.execv", ...)` takes precedence over this fixture and keeps working unchanged.

- [ ] **Step 1: Write the guard fixture**

Append to `tests/conftest.py`:

```python
@pytest.fixture(autouse=True)
def block_exec_shell(monkeypatch):
    """Fail loudly if a test reaches os.execv instead of replacing the runner.

    `fx today` ends by calling os.execv to hand the user an interactive shell.
    A test that invokes it without --no-exec (or without patching os.execv)
    replaces the pytest process with a shell that exits 0, so the rest of the
    suite never runs and the runner still reports success. Turning that into
    an explicit failure keeps the gate honest.

    Tests that intentionally exercise the exec path patch os.execv themselves;
    that inner patch wins over this fixture.
    """

    def _blocked(*args, **kwargs):
        raise AssertionError(
            "os.execv called during a test — this would replace the pytest "
            "process and silently truncate the run. Pass --no-exec, or patch "
            "os.execv in the test."
        )

    monkeypatch.setattr("os.execv", _blocked)
```

- [ ] **Step 2: Run the suite to confirm the guard converts silence into a failure**

Run: `.venv/bin/python -m pytest tests/integration/test_today_cli.py --no-cov -q`

Expected: the run now **completes** and reports a failure (previously it printed 9 dots and vanished). The failing test is `test_today_command_verbose_mode` with `AssertionError: os.execv called during a test`. Confirm the collected count (29) equals passed+failed.

- [ ] **Step 3: Commit the guard alone, so the diff shows the newly visible failure**

```bash
git add tests/conftest.py
git commit -m "test: fail loudly when a test reaches os.execv

fx today execs a shell as its final step. A test invoking it without
--no-exec replaced the pytest process with a shell that exits 0, so the
rest of the suite never ran and pytest still reported success. This
autouse fixture turns that silent truncation into an explicit failure."
```

---

### Task 2: Fix the test that trips the guard, and audit its siblings

**Files:**
- Modify: `tests/integration/test_today_cli.py:131-143` (`test_today_command_verbose_mode`)
- Test: same file

**Interfaces:**
- Consumes: `block_exec_shell` from Task 1.
- Produces: a green `tests/integration/test_today_cli.py` — all 29 collected tests execute.

- [ ] **Step 1: Confirm the failing test and read the cause**

Run: `.venv/bin/python -m pytest tests/integration/test_today_cli.py::TestTodayCLI::test_today_command_verbose_mode --no-cov -v`

Expected: FAIL with `AssertionError: os.execv called during a test`.

The cause is in `fx_bin/cli.py`, inside the `today` command:

```python
exec_shell = not no_exec and not output_for_cd and not dry_run
```

With only `--verbose` all three are false, so `exec_shell` is `True`.

- [ ] **Step 2: Fix the test by asking for the behaviour it actually asserts**

The test asserts on verbose *output* only; it has no interest in the shell. Replace the invoke line at `tests/integration/test_today_cli.py:137`:

```python
            result = self.runner.invoke(cli, ["today", "--verbose"])
```

with:

```python
            result = self.runner.invoke(cli, ["today", "--verbose", "--no-exec"])
```

- [ ] **Step 3: Run it and confirm it passes**

Run: `.venv/bin/python -m pytest tests/integration/test_today_cli.py::TestTodayCLI::test_today_command_verbose_mode --no-cov -v`

Expected: PASS, and the three existing assertions (`Creating directory:`, `Directory created successfully`, `Today's workspace:`) still hold — `--no-exec` suppresses only the shell hand-off, not the verbose logging.

- [ ] **Step 4: Audit every other test in the file for the same gap**

Run: `.venv/bin/python -m pytest tests/integration/test_today_cli.py --no-cov -q`

Expected: `29 passed`. If any other test fails with the `os.execv` AssertionError, apply the same fix — add `--no-exec` when the test does not care about the shell, or wrap it in `with patch("os.execv"):` when it does. Do not weaken or remove the guard.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_today_cli.py
git commit -m "test(today): pass --no-exec so the verbose test stops killing the run

test_today_command_verbose_mode invoked 'fx today --verbose' with no
--no-exec and no os.execv patch, so exec_shell stayed True and the
pytest process was replaced at test 10 of 29. The test only asserts on
verbose output, so --no-exec is sufficient."
```

---

### Task 3: Prove the whole suite now runs, and record the real number

**Files:**
- Modify: none (verification task)

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: a trustworthy baseline test count for the repo.

- [ ] **Step 1: Run the full suite the way CI runs it**

Run:

```bash
.venv/bin/python -m pytest tests/ -v --tb=short --ignore=tests/runners/ --ignore=tests/performance/ --no-cov
```

(This is the exact command from `.github/workflows/ci-test.yml:45`.)

Expected: the run reaches a summary line and does **not** stop inside `tests/integration/test_today_cli.py`. Before this plan it stopped at ~39%.

- [ ] **Step 2: Confirm the count against the known-good partial run**

Run: `.venv/bin/python -m pytest --no-cov -q --ignore=tests/integration/test_today_cli.py 2>&1 | tail -2`

Expected: `719 passed` (the count observed while the broken file was excluded). The full run from Step 1 should now report **719 + 29 = 748**, give or take any tests added since. If the full run reports fewer than the sum, something else is still truncating — investigate before continuing.

- [ ] **Step 3: Confirm the coverage gate can now be met honestly**

Run: `.venv/bin/python -m pytest --ignore=tests/runners/ --ignore=tests/performance/ 2>&1 | tail -5`

Expected: coverage is computed over the whole suite and `--cov-fail-under=80` passes. If it now *fails*, that is a real finding, not a regression from this plan — the gate was previously being evaluated on a truncated run. Report the number rather than lowering the threshold.

- [ ] **Step 4: Commit nothing; record the numbers in the PR description**

No code change in this task. Capture the before/after counts for the PR body.

---

### Task 4: Make the two width-dependent search tests deterministic

**Files:**
- Modify: `tests/integration/test_open_cli.py` — `test_search_lists_case_insensitive_keyword_matches` and `test_search_composes_with_tag_filter`
- Test: same file

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: two tests that pass at any terminal width.

- [ ] **Step 1: Reproduce the environment dependence**

Run:

```bash
COLUMNS=80  .venv/bin/python -m pytest tests/integration/test_open_cli.py -q --no-cov -k search
COLUMNS=200 .venv/bin/python -m pytest tests/integration/test_open_cli.py -q --no-cov -k search
```

Expected: the first fails, the second passes. The failure is
`AssertionError: 'https://en97.sportplus.live/snooker/' not found in ...`
because `_fit_column_widths` in `fx_bin/open_launcher.py` truncates the Target
column to `https://en97.s... ` at narrow widths.

- [ ] **Step 2: Pin the width inside the two tests**

Both tests assert on a full URL that only survives at a wide terminal. Wrap each
`self.runner.invoke(...)` call in an explicit width so the assertion is about
formatting logic rather than about the developer's window. Add the import at the
top of `tests/integration/test_open_cli.py` if it is not already present:

```python
import os
```

Then wrap the invoke in `test_search_lists_case_insensitive_keyword_matches`:

```python
            with patch.dict(os.environ, {"COLUMNS": "200"}):
                result = self.runner.invoke(
                    cli, ["open", "--config", str(config_path), "search", "SNOOKER"]
                )
```

and the invoke in `test_search_composes_with_tag_filter`:

```python
            with patch.dict(os.environ, {"COLUMNS": "200"}):
                result = self.runner.invoke(
                    cli,
                    [
                        "open",
                        "--config",
                        str(config_path),
                        "search",
                        "--tag",
                        "deepseek",
                        "usage",
                    ],
                )
```

- [ ] **Step 3: Verify both widths now pass**

Run:

```bash
COLUMNS=80  .venv/bin/python -m pytest tests/integration/test_open_cli.py -q --no-cov -k search
COLUMNS=200 .venv/bin/python -m pytest tests/integration/test_open_cli.py -q --no-cov -k search
```

Expected: both PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/integration/test_open_cli.py
git commit -m "test(open): pin terminal width in the search table tests

Both tests assert on a full URL that _fit_column_widths truncates below
about 120 columns, so they passed or failed depending on the developer's
window size."
```

---

### Task 5: Full gate and PR

**Files:**
- Modify: none

- [ ] **Step 1: Run the repo's full gate**

```bash
.venv/bin/python -m black --check fx_bin/ tests/
.venv/bin/python -m flake8 fx_bin
.venv/bin/python -m mypy fx_bin/
.venv/bin/python -m pytest tests/ --ignore=tests/runners/ --ignore=tests/performance/
```

Expected: all clean; pytest reaches a summary line with roughly 748 tests.

- [ ] **Step 2: Open the PR**

All work in this plan belongs on one branch, created from `main` before Task 1:

```bash
git checkout -b fix/test-suite-truncation main
```

Then:

```bash
git push -u fork fix/test-suite-truncation
gh pr create --repo frankyxhl/fx_bin --base main \
  --head ryosaeba1985:fix/test-suite-truncation \
  --title "fix(tests): stop the suite exiting at 39% and make two tests width-independent"
```

PR body must state the before/after test counts from Task 3 and note that
`--cov-fail-under=80` was previously evaluated on a truncated run.

---

## Out of Scope (separate plans)

Each of these is an independent subsystem and gets its own plan when scheduled:

1. **`cli.py` `organize` decomposition** — one ~500-line function with six inner closures; ASK mode runs `scan_files` + `generate_organize_plan` three separate times.
2. **`fx open` subcommand dispatch** — six `_run_open_*` helpers each thread the same ten parameters and repeat the same mutually-exclusive-option validation.
3. **Functional/imperative twin modules** — establish which of `replace.py` / `replace_functional.py`, `common.py` / `common_functional.py` are reachable from the CLI, and delete or document the rest.
4. **Stale `CLAUDE.md` test paths** — the documented commands reference `tests/test_size.py`; the files live in `tests/unit/`.
5. **Release pipeline cannot push to `main`** — three active rulesets (`protect main`, `main-pr-gates`, `main-owner-merge-only`) all have empty bypass lists; either add bypasses or restructure the release so it never pushes to `main`.

# SOP-2109: Code Review — AI-Assisted Code + Quick Reference

**Applies to:** FXB project
**Last updated:** 2026-05-10
**Last reviewed:** 2026-05-10
**Status:** Active
**Related:** COR-1709, COR-1706, COR-1707, COR-1708, COR-1602, COR-1705
**Depends on:** COR-1709
**Task tags:** [review, code-review, ai-code, checklist, quick-reference]

---

## What Is It?

Project-specific adaptation of COR-1709 for the FXB codebase. Checklist for reviewing AI-generated or AI-assisted code changes, a condensed short-form PR checklist, and this project's actual tooling configurations (extracted from `pyproject.toml`). Use alongside COR-1602 and COR-1706/1707/1708.

---

## Why

AI-generated code has distinct failure modes: plausible-looking but incorrect logic, subtle security gaps, hallucinated APIs, and missing edge-case handling. This project's functional-programming patterns (`returns`, railway-oriented programming, `@impure_safe`, immutable dataclasses) are conventions AI tools frequently get wrong. Reviewers need a dedicated, project-specific lens.

---

## When to Use

- Reviewing code that was generated or assisted by an LLM/AI tool
- Quick PR reviews that don't warrant the full COR-1706/1707/1708 checklists
- As a reference during COR-1602 multi-model parallel review

## When NOT to Use

- High-risk changes touching security, auth, or data integrity (use full COR-1707)
- Complex architectural changes (use full COR-1706)

---

## Item Type and Severity Legend

Per COR-1705 REF: **G** = Gate (tool/CI), **A** = Automated (should be tool-enforced), **H** = Human Review.
**P0** = Blocker, **P1** = Should Fix, **P2** = Nit.

---

## Steps

### 1. AI-Generated Code Review

- [ ] H-1.1 Authorship is transparent: AI-generated or AI-assisted sections are clearly identified. [P0]
- [ ] H-1.2 A human has reviewed, understood, and takes responsibility for every line. [P0]
- [ ] H-1.3 No hallucinated APIs, libraries, or functions — verify imports and calls exist in this project's dependencies (`click`, `loguru`, `returns`). [P0]
- [ ] H-1.4 Generated code follows project conventions (see §4 below). [P1]
- [ ] H-1.5 Edge cases and error handling are complete — AI often omits railway-oriented failure tracks. [P1]
- [ ] H-1.6 No subtle security issues: hardcoded credentials, disabled validation, path traversal, command injection. `bandit` + `safety check` pass. [P0]
- [ ] H-1.7 Tests are meaningful, not just coverage-matching stubs. Coverage stays ≥ 80%. [P1]
- [ ] H-1.8 Generated comments are accurate — verify they describe what the code actually does. [P2]
- [ ] H-1.9 LLM/AI system changes: prompt changes, model version bumps, and output format changes are documented with before/after examples. [P1]
- [ ] H-1.10 AI system changes include evaluation results or manual validation evidence. [P1]

### 2. Short-Form PR Checklist

- [ ] H-2.1 Change is focused and well-described. PR title < 70 chars. [P1]
- [ ] H-2.2 Author self-check: `poetry run pytest` passes, `poetry run black --check fx_bin/ tests/` clean, `poetry run mypy fx_bin/` clean, `poetry run flake8 fx_bin/` clean. [P0]
- [ ] H-2.3 No hardcoded secrets, no debug code left in. `poetry run bandit -r fx_bin/` clean. [P0]
- [ ] H-2.4 New behavior has tests; edge cases considered (including Windows paths where relevant). [P1]
- [ ] H-2.5 No breaking changes without communication. CLI interface changes documented. [P0]
- [ ] H-2.6 Dependencies added are necessary and safe — `poetry run safety check` passes. [P1]
- [ ] H-2.7 Logging and error handling use `loguru` consistently. Errors use the project error hierarchy (`FxBinError` root; file-operation errors extend `FileOperationError`, non-file errors extend `FxBinError` directly). [P1]
- [ ] H-2.8 Performance impact is negligible or explicitly documented. [P2]

### 3. Project Tooling Configuration

Key settings extracted from `pyproject.toml` — see `pyproject.toml` for the full authoritative config.

#### Black (formatter)

```toml
[tool.black]
line-length = 88
target-version = ['py311']
```

#### mypy (type checker)

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

#### pytest

```toml
[tool.pytest.ini_options]
addopts = [
    "--verbose",
    "--cov=fx_bin",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80",
    "--timeout=30",
    "--strict-markers",
]
```

#### bandit (security)

```toml
[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]  # assert_used
```

#### Unified Check Command

> `bandit`/`safety` are in the optional `security` group — run `poetry install --with security` first (or use `make check`, which installs it).

```bash
poetry run black --check fx_bin/ tests/ && \
  poetry run mypy fx_bin/ && \
  poetry run flake8 fx_bin/ && \
  poetry run bandit -r fx_bin/ && \
  poetry run safety check && \
  poetry run pytest
```

### 4. Project-Specific Convention Checks

Reviewers must verify AI-generated code respects these FXB conventions (documented in `CLAUDE.md`):

- [ ] H-4.1 **Pure vs IO separation**: in functional/railway-oriented modules (e.g., `*_functional.py`, `backup_utils.py`), IO functions return `IOResult[T, Error]` — either via `@impure_safe` or by constructing `IOResult` directly with explicit try/except. Pure functions have no side effects. Imperative modules (e.g., `filter.py`, `open_launcher.py`) may use normal returns and raise typed errors (`OpenError`, etc.); do not flag them for not returning `IOResult`. [P1]
- [ ] H-4.2 **Railway-oriented programming**: pipelines use `flow()`, `bind()`, `lash()` from `returns.pipeline` / `returns.pointfree` — no bare try/except for control flow. [P1]
- [ ] H-4.3 **RequiresContext pattern**: IO functions that need shared context use `RequiresContext[IOResult[T, Error], ContextType]` to make dependencies explicit, not global state or closures. [P1]
- [ ] H-4.4 **Immutable data classes**: data classes representing state or configuration use `frozen=True`. Value objects with `__slots__` (e.g., `SizeEntry`, `FileCountEntry`) may omit `frozen`. [P1]
- [ ] H-4.5 **Type annotations**: function parameters accepting sequences use `Sequence[T]`, not `Tuple[T, ...]`. Return types use `List[T]` for mutable lists. [P1]
- [ ] H-4.6 **Partial over lambda**: `functools.partial` is used to bind parameters instead of inline lambdas in pipeline chains. [P2]
- [ ] H-4.7 **Shared types**: common types (`EntryType`, `FileBackup`, `FolderContext`) are imported from `fx_bin.shared_types`, not duplicated. [P1]
- [ ] H-4.8 **Error hierarchy**: custom errors extend `FxBinError` (root). File-operation errors extend `FileOperationError` (`IOError`, `ReplaceError`); non-file errors (`SecurityError`, `ValidationError`, `SizeError`, `FindError`, `OpenError`) extend `FxBinError` directly. `except FileOperationError` does NOT catch security violations. No bare `Exception` raises. [P1]
- [ ] H-4.9 **CLI patterns**: Top-level entry point `fx = "fx_bin.cli:main"` registered in `[tool.poetry.scripts]`. Subcommands are added via `@cli.command()` decorators on the Click group — they do NOT need individual `[tool.poetry.scripts]` entries. [P1]

---

## Core Principle

> If a reviewer finds a recurring pattern issue, the response is: **"Please add this rule to tooling/CI."** Do not nitpick individual violations. Reviewers focus on design, security, business logic, and risk — not formatting.

---

## Change History

| Date | Change | By |
|------|--------|----|
| 2026-05-10 | Initial version — PRJ adaptation of COR-1709 with project tooling and conventions | Frank Xu |

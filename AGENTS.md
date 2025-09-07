# Repository Guidelines

## Project Structure & Module Organization
- Source in `fx_bin/`:
  - `cli.py`: unified `fx` entry point (v1.1.0).
  - `files.py`: file counting.
  - `size.py`: directory size analysis.
  - `find_files.py`: pattern search (`fx ff`).
  - `replace.py`: safe, atomic text replacement.
  - `pd.py`: JSON → Excel (`json2excel`).
  - `common*.py`, `*_functional.py`: shared safety/FP utilities.
- Tests in `tests/` as `test_*.py`; markers: `security`, `safety`, `integration`, `performance`.

## Build, Test, and Development Commands
- `make install` — install dev environment (Poetry).
- `make shell` — open Poetry shell.
- `make check` — format, lint, type, and security checks.
- `make test-coverage` — run tests with ≥80% coverage gate.
- `make test-security` — run critical security tests.
- Run app: `poetry run fx --help`, `poetry run fx list`.
  Examples: `poetry run fx files`, `poetry run fx size`, `poetry run fx ff "*.py"`, `poetry run fx replace OLD NEW file.txt`, `poetry run fx json2excel in.json out.xlsx`.

## Coding Style & Naming Conventions
- Python 3.11+, 4-space indentation, 88-char lines (Black).
- Tools: Black, flake8 (zero tolerance), mypy (strict), bandit.
- Naming: functions/vars `snake_case`; classes `PascalCase`; constants `UPPER_CASE`; files `snake_case.py`.

## Testing Guidelines
- Framework: pytest. Place tests in `tests/` named `test_*.py`.
- Use markers above; prefer fast, deterministic tests.
- Commands: `make test-core`, `make test-security`, `make test-coverage`.

## Commit & Pull Request Guidelines
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`.
- Before PR: run `make check` and `make test-coverage`; attach relevant output.
- PRs: clear description, linked issues, rationale, and usage examples (commands).
- Note: legacy commands removed (`fx_files`, `fx_size`, `fx_ff`, etc.). Use `fx` subcommands.

## Security & Configuration Tips
- Enforce safe paths, atomic writes, input sanitization, and symlink loop detection.
- Validate with: `make test-security`, `make security-scan`, `poetry run safety check`.
- Prefer safe paths under the workspace; avoid destructive operations.

## Agent-Specific Notes
- This AGENTS.md applies repo-wide; deeper files may override within their subtree.


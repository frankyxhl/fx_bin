# Change: Add Organize Command

## Why
Users need a reliable way to automatically organize files into date-based directory structures (e.g., `2026/202601/20260110/`). This is essential for managing photo libraries, screenshots, documents, and other time-sensitive files that accumulate over time.

## What Changes
- Add `fx organize` command to organize files by date into hierarchical directories
- Support configurable date sources: file creation time (default) with fallback to modification time
- Support configurable directory depth: 1, 2, or 3 levels (default: 3 levels = year/year-month/year-month-day)
- Implement multiple conflict resolution strategies: rename (default), skip, overwrite, ask
- Support dry-run mode for previewing changes before execution
- Support file filtering with repeatable include/exclude options
- Follow existing fx-bin patterns: dual-mode (imperative + functional), Click framework, returns.result for error handling
- Full TDD implementation with comprehensive test coverage

## Impact
- Affected specs: organize (new capability)
- Affected code:
  - New: `fx_bin/organize.py` (core pure functions + module-specific types: DateSource, ConflictMode, OrganizeContext, etc.)
  - New: `fx_bin/organize_functional.py` (IO operations with returns library)
  - New: `tests/unit/test_organize.py` (unit tests for pure functions)
  - New: `tests/integration/test_organize_io.py` (IO layer and security-focused tests)
  - New: `tests/integration/test_organize_cli.py` (CLI integration tests)
  - Modified: `fx_bin/cli.py` (add organize command)
  - Modified: `fx_bin/errors.py` (add OrganizeError hierarchy)

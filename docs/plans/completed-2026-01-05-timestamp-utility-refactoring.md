# Common Utilities Refactoring Implementation Plan

## Overview

This plan describes the consolidation of fragmented utility logic across the `fx_bin` codebase. Currently, critical logic for timestamp generation, file extension extraction, and human-readable size formatting is duplicated in multiple modules (`backup.py`, `today.py`, `filter.py`, `common_functional.py`). This duplication increases the maintenance burden and makes unit testing inconsistent. We will centralize these utilities into `fx_bin/common.py` to provide a single, authoritative implementation for all commands.

## Current Issues (4 areas)

1.  **Timestamp Generation**: 
    *   **Locations**: `fx_bin/today.py` (lines 35, 116) and `fx_bin/backup.py` (lines 109, 170, 193) both use `datetime.now().strftime(format_str)`.
    *   **Problem**: Duplicated logic makes testing difficult as `datetime` must be patched in multiple places.

2.  **File Extension Handling**:
    *   **Locations**: `fx_bin/backup.py` (lines 30-76) implements `get_multi_ext` and `get_base_name` to handle `.tar.gz`. `fx_bin/filter.py` (line 95) and BDD steps (`tests/bdd/test_file_filter_steps.py`) use a simpler `Path(file).suffix` logic that fails on multi-part extensions.
    *   **Problem**: Inconsistent handling of archives like `.tar.gz` across different commands.

3.  **Human-Readable Size Formatting**:
    *   **Locations**: 
        *   `fx_bin/common.py:convert_size` (line 18) - Standard version.
        *   `fx_bin/common_functional.py:convert_size` (line 111) - Duplicated version.
        *   `fx_bin/filter.py:_format_file_size` (line 231) and `_format_file_size_aligned` (line 258) - Custom implementations with specific padding/rounding.
    *   **Problem**: Inconsistent rounding (integer vs. 1 decimal) and formatting across commands.

4.  **Path Safety Validation**:
    *   **Locations**: `fx_bin/today.py:validate_base_path` (line 159).
    *   **Problem**: This security logic is currently local to the `today` command but is relevant to any command taking a base directory (like `backup`).

## Proposed Solution (A, B, C)

*   **Solution A (Status Quo)**: Leave utilities duplicated. This is brittle and leads to subtle bugs where one command handles an edge case (like `.tar.gz`) while another doesn't.
*   **Solution B (Centralized Utilities - Recommended)**: Move all shared logic to `fx_bin/common.py`. Create a NEW `format_size_aligned()` function to support the specific alignment and precision needs of the `filter` command, while keeping the existing `convert_size()` function unchanged to preserve semantics. Use `common.py` as the single source of truth.
*   **Solution C (Shared Utils Package)**: Create a `fx_bin/utils/` directory with separate files for `time.py`, `files.py`, etc. This is likely overkill for a project of this size.

## Risk Mitigation Strategies

1.  **Backward Compatibility**: Keep wrapper functions in original modules for at least one release to avoid breaking external callers or internal dependencies during the transition.
2.  **Output Stability**: Create new formatting functions instead of modifying existing ones to ensure no silent changes in command output.
3.  **Incremental Rollout**: 4 separate PRs allow easy rollback and focused review if issues arise.
4.  **Test Coverage**: Add golden tests for format-sensitive outputs (like `fx filter`'s table) to ensure byte-for-byte identity.
5.  **Security Validation**: Maintain strict boundary checks in `validate_base_path` during migration.

## Implementation Tasks (Phases)

### Phase 1 (PR #1): Timestamp Utilities
- Add `generate_timestamp(format_str: str) -> str` to `common.py`.
- Update `backup.py` and `today.py` to use `common.generate_timestamp`.
- Update related tests.
- **Code Style Fixes**: Fix function signature formatting in `backup.py` (Black compliance) and run `make format`.
- Estimated effort: 1-2 hours.

### Phase 2 (PR #2): Extension Handling Utilities
- Move `get_multi_ext()`, `get_base_name()`, and `KNOWN_MULTI_EXTS` to `common.py`.
- Add backward-compatible wrappers in `backup.py`:
  ```python
  from .common import get_multi_ext as _get_multi_ext
  def get_multi_ext(filename: str) -> str:
      """Wrapper for backward compatibility."""
      return _get_multi_ext(filename)
  ```
- Update `filter.py` to use `get_multi_ext` for proper `.tar.gz` support.
- Create `tests/unit/test_common.py` for new utilities.
- Estimated effort: 2-3 hours.

### Phase 3 (PR #3): Size Formatting
- Add NEW `format_size_aligned(size: int, width: int = 9) -> str` to `common.py`. (Do NOT modify `convert_size` semantics).
- Update `filter.py` to use the new `format_size_aligned()` function.
- Remove duplicate `_format_file_size_aligned` and `_format_file_size` from `filter.py`.
- Remove duplicate `convert_size` from `common_functional.py`.
- Add golden tests for `fx filter` output preservation.
- Estimated effort: 1-2 hours.

### Phase 4 (PR #4): Path Safety & Refinement
- Migrate `validate_base_path` from `today.py` to `common.py`.
- Update `today.py` to use the centralized version.
- Run `make check` and `make test-coverage` to ensure >90% coverage for all new utilities.
- Estimated effort: 1 hour.

## Impact Analysis

*   **Maintenance**: Significant reduction in code volume. Fixes in `convert_size` (like YB support) will now propagate to all commands.
*   **Testability**: Test suites can now patch a single point in `common.py` for time-dependent or filesystem-dependent tests.
*   **Consistency**: All commands will now handle multi-part extensions and file sizes identically.
*   **Security**: Centralized path validation ensures that security fixes for path traversal are applied globally.

## Success Criteria

*   [ ] All existing imports of `fx_bin.backup.get_multi_ext` still work (via wrappers).
*   [ ] `fx filter` output format is byte-for-byte identical to the previous version (verified by golden tests).
*   [ ] Each PR can be merged independently and leaves the codebase in a stable state.
*   [ ] `tests/unit/test_common.py` created with >90% coverage of new utilities.
*   [ ] Zero duplicated logic for timestamps and size conversion.
*   [ ] All 400+ existing tests pass.
*   [ ] `make check` (Lint, Type, Format) passes with 100% compliance.

## Files Affected

- `/Users/frank/Projects/fx_bin/fx_bin/common.py`
- `/Users/frank/Projects/fx_bin/fx_bin/common_functional.py`
- `/Users/frank/Projects/fx_bin/fx_bin/backup.py`
- `/Users/frank/Projects/fx_bin/fx_bin/today.py`
- `/Users/frank/Projects/fx_bin/fx_bin/filter.py`
- `/Users/frank/Projects/fx_bin/tests/bdd/test_file_filter_steps.py`
- `/Users/frank/Projects/fx_bin/tests/unit/test_common.py` (New file)

# Test Reorganization and Project Cleanup Changelog
**Date**: 2025-09-05
**Version**: Pre-1.3.5
**Type**: Major Refactor

## Summary
Complete test suite reorganization, critical bug fixes, and project structure cleanup preparing for v1.3.5 release.

## Changes Made

### Test Suite Reorganization
- Restructured tests into categorized folders:
  - `tests/unit/` - Unit tests for individual functions
  - `tests/integration/` - Integration tests  
  - `tests/security/` - Security and safety tests
  - `tests/performance/` - Performance benchmarks
  - `tests/functional/` - End-to-end functional tests
- Consolidated duplicate test files:
  - Merged test_filter.py with test_filter_improvements_v1_3_1.py
  - Merged test_find_files.py with test_ff_exclude.py

### Bug Fixes
- **Critical**: Fixed replace command "str expected, not tuple" error
  - Refactored replace.py to separate CLI from logic
  - Created new replace_files function for core functionality
  - Updated all related tests to use new function
- Fixed 18 failing tests by adding pytest-forked for proper test isolation
- Fixed 26 warnings (24 pytest-bdd, 2 dataclass naming)
- Fixed 2 skipped tests in replace module

### Documentation Consolidation
- Merged README.rst → README.md (single Markdown source)
- Merged HISTORY.rst → CHANGELOG.md (modern changelog format)
- Created CONTRIBUTING.md from contributing.rst
- Removed 8 obsolete Sphinx documentation files

### Project Cleanup
- Removed all __pycache__ directories
- Cleaned .pytest_cache and .mypy_cache
- Updated .gitignore with comprehensive patterns
- Removed old build artifacts from dist/
- Updated Makefile to use --forked option for tests

## Technical Details

### Dependencies Added
```toml
[tool.poetry.group.dev.dependencies]
pytest-forked = "^1.6.0"
```

### Files Modified (Key Changes)
- `fx_bin/replace.py` - Refactored with new replace_files function
- `pyproject.toml` - Added pytest-forked dependency
- `Makefile` - Updated test command with --forked
- `.gitignore` - Comprehensive cleanup patterns

### Test Results
```
Before: 18 failed, 2 skipped, 26 warnings
After:  317 passed, 0 failed, 0 skipped, 0 warnings
```

## Migration Notes
- Tests now require `--forked` option for proper isolation
- Replace function API changed - use replace_files() for programmatic access
- All Sphinx documentation removed - use Markdown files in docs/

## Next Steps
1. Commit all changes for v1.3.5
2. Update version in pyproject.toml
3. Build and release v1.3.5
4. Update PyPI package
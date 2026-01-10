# Implementation Tasks

All tasks follow TDD discipline: RED (write failing test) -> GREEN (minimal code to pass) -> REFACTOR (clean up).

## 1. Testing Infrastructure Setup

### 1.1 Create Shared Test Fixtures
- [x] 1.1.1 **RED**: Write test that uses `temp_test_dir` fixture from conftest.py (expect ImportError)
- [x] 1.1.2 **GREEN**: Create `tests/conftest.py` with `temp_test_dir` fixture
- [x] 1.1.3 **REFACTOR**: Migrate `test_replace.py` setUp/tearDown to use fixture

### 1.2 Add pytest-hypothesis Dependency
- [x] 1.2.1 Add `hypothesis` to dev dependencies in `pyproject.toml`
- [x] 1.2.2 **RED**: Write property-based test for `replace.work()` (expect ImportError)
- [x] 1.2.3 **GREEN**: Install dependency, verify test runs
- [x] 1.2.4 **REFACTOR**: Document hypothesis usage in CLAUDE.md

## 2. Railway-Oriented Programming Refactor

### 2.1 Replace Direct `_inner_value` Access
- [x] 2.1.1 **RED**: Write test for `work_functional` using pattern matching
- [x] 2.1.2 **GREEN**: Refactor `replace_functional.py:177-196` to use proper API
- [x] 2.1.3 **VERIFY**: Run `poetry run pytest tests/unit/test_replace.py -v`

### 2.2 Implement `flow` Composition
- [x] 2.2.1 **RED**: Write test for composed pipeline in `work_functional`
- [x] 2.2.2 **GREEN**: Refactor to use `returns.pipeline.flow`
- [x] 2.2.3 **REFACTOR**: Apply same pattern to `work_batch_functional`
- [x] 2.2.4 **VERIFY**: Run full test suite

### 2.3 Separate Pure/IO Functions in common_functional.py
- [x] 2.3.1 **RED**: Write test for pure `process_entry` function
- [x] 2.3.2 **GREEN**: Extract pure logic from `_sum_folder_recursive`
- [x] 2.3.3 **REFACTOR**: Update docstrings and type hints
- [x] 2.3.4 **VERIFY**: Run `poetry run pytest tests/unit/test_common.py -v`

## 3. Error Type Hierarchy Improvement

### 3.1 Add Intermediate Error Classes
- [x] 3.1.1 **RED**: Write test expecting `FileOperationError` base class
- [x] 3.1.2 **GREEN**: Add `FileOperationError` to `errors.py`
- [x] 3.1.3 **GREEN**: Make `ReplaceError`, `IOError` inherit from it
- [x] 3.1.4 **REFACTOR**: Update error handling code to use hierarchy
- [x] 3.1.5 **VERIFY**: Run all security tests

## 4. Shared Backup Utilities

### 4.1 Create backup_utils Module
- [x] 4.1.1 **RED**: Write tests for `create_backup()` and `restore_backup()` functions
- [x] 4.1.2 **GREEN**: Create `fx_bin/backup_utils.py` with implementations
- [x] 4.1.3 **REFACTOR**: Update `replace.py` to use `backup_utils`
- [x] 4.1.4 **REFACTOR**: Update `replace_functional.py` to use `backup_utils`
- [x] 4.1.5 **VERIFY**: Run replace safety tests

### 4.2 Add Path Boundary Validation
- [x] 4.2.1 **RED**: Write security test for path traversal in `validate_file_access`
- [x] 4.2.2 **GREEN**: Add `allowed_base` parameter with boundary check
- [x] 4.2.3 **REFACTOR**: Update callers to pass appropriate base paths
- [x] 4.2.4 **VERIFY**: Run `poetry run pytest tests/security/ -v`

## 5. Test Code Modernization

### 5.1 Migrate to pytest Style
- [x] 5.1.1 **RED**: Write new test using pytest style (no TestCase)
- [x] 5.1.2 **GREEN**: Ensure test passes
- [x] 5.1.3 **REFACTOR**: Gradually migrate `test_replace.py` to pytest style

### 5.2 Improve Test Naming
- [x] 5.2.1 Rename tests to `test_given_X_when_Y_then_Z` pattern
- [x] 5.2.2 Update docstrings to match new names
- [x] 5.2.3 **VERIFY**: All tests pass with new names

### 5.3 Add Property-Based Tests
- [x] 5.3.1 **RED**: Write hypothesis test for text replacement invariants
- [x] 5.3.2 **GREEN**: Ensure test passes with current implementation
- [x] 5.3.3 **RED**: Write hypothesis test for size calculation
- [x] 5.3.4 **GREEN**: Ensure test passes
- [x] 5.3.5 **VERIFY**: Run `poetry run pytest -m "hypothesis" -v`

### 5.4 Simplify Mock Setups
- [x] 5.4.1 Create helper functions for common mock scenarios
- [x] 5.4.2 **REFACTOR**: Simplify `test_replace.py:196-207` mock setup
- [x] 5.4.3 **VERIFY**: Tests still pass and are more readable

## 6. Type Annotation Improvements

### 6.1 Update Function Signatures
- [x] 6.1.1 Change `Tuple[str, ...]` to `Sequence[str]` in `replace.py`
- [x] 6.1.2 Run mypy to verify type consistency
- [x] 6.1.3 **VERIFY**: `poetry run mypy fx_bin/`

## 7. Final Verification

### 7.1 Full Test Suite
- [x] 7.1.1 Run `poetry run pytest --cov=fx_bin --cov-report=term-missing`
- [x] 7.1.2 Verify coverage >= 80%
- [x] 7.1.3 Run `poetry run mypy fx_bin/`
- [x] 7.1.4 Run `poetry run flake8 fx_bin/`
- [x] 7.1.5 Run `poetry run bandit -r fx_bin/`

### 7.2 Documentation
- [x] 7.2.1 Update CLAUDE.md with new patterns
- [x] 7.2.2 Add inline comments for complex functional patterns
- [x] 7.2.3 Update CHANGELOG.md

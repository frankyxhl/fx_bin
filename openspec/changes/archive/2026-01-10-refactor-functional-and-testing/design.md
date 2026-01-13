# Design Document: Functional Programming and Testing Refactor

## Context

The fx_bin codebase uses the `returns` library for functional programming patterns but applies them inconsistently. The test suite has grown organically with duplication. This refactor aims to establish consistent patterns without breaking existing functionality.

### Stakeholders
- Maintainers who need to understand and extend the codebase
- CI/CD pipeline (must maintain 80% coverage)
- PyPI users (no breaking changes to CLI)

### Constraints
- Python 3.11+ compatibility
- No breaking changes to public API
- Must pass all existing tests

## Goals / Non-Goals

### Goals
- Consistent Railway-Oriented Programming patterns
- Reduced test code duplication
- Property-based tests for edge case discovery
- Cleaner separation of pure/impure code

### Non-Goals
- Full migration away from unittest (gradual approach)
- Adding new features
- Performance optimization (unless discovered during refactor)

## Decisions

### Decision 1: Use Pattern Matching for Result Types

**What**: Replace `isinstance(result._inner_value, Failure)` with pattern matching or proper API.

**Why**:
- `_inner_value` is a private attribute that may change
- Pattern matching (Python 3.10+) is more readable
- `returns` library provides `map`, `bind`, `alt` for composition

**Implementation**:
```python
# Before (bad)
if isinstance(replacement_result._inner_value, Failure):
    restore_from_backup(backup)

# After (good) - Option 1: Use bind/alt
result = (
    perform_replacement(context, backup)
    .alt(lambda err: restore_and_fail(backup, err))
)

# After (good) - Option 2: Use lash for error recovery
result = perform_replacement(context, backup).lash(
    lambda err: restore_and_return_error(backup, err)
)
```

**Alternatives considered**:
- Keep current pattern: Rejected - relies on private API
- Use try/except wrapper: Rejected - defeats functional purpose

### Decision 2: Shared Test Fixtures via conftest.py

**What**: Create `tests/conftest.py` with shared fixtures.

**Why**:
- Multiple test files duplicate `setUp`/`tearDown` for temp directories
- pytest fixtures provide automatic cleanup
- Enables easier test isolation

**Implementation**:
```python
# tests/conftest.py
import tempfile
import shutil
from pathlib import Path
import pytest

@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for tests."""
    test_dir = tempfile.mkdtemp()
    yield Path(test_dir)
    shutil.rmtree(test_dir, ignore_errors=True)

@pytest.fixture
def temp_file(temp_test_dir):
    """Create a temporary file in the test directory."""
    file_path = temp_test_dir / "test.txt"
    file_path.write_text("test content")
    return file_path
```

**Alternatives considered**:
- Base TestCase class: Rejected - doesn't work well with pytest fixtures
- Module-level setup: Rejected - reduces isolation

### Decision 3: Property-Based Testing with Hypothesis

**What**: Add hypothesis for property-based tests of core operations.

**Why**:
- Edge cases discovered automatically
- Stronger guarantees than example-based tests
- Shrinking helps debug failures

**Implementation**:
```python
from hypothesis import given, strategies as st

@given(
    search=st.text(min_size=1, max_size=100),
    replace=st.text(max_size=100),
    content=st.text(max_size=1000)
)
def test_replace_invariants(search, replace, content, temp_file):
    """Property: after replacement, search text only appears if replace contains it."""
    temp_file.write_text(content)
    work(search, replace, str(temp_file))
    result = temp_file.read_text()

    # Invariant: search shouldn't appear unless replace contains it
    if search not in replace:
        assert search not in result or search not in content
```

**Alternatives considered**:
- QuickCheck port: Rejected - hypothesis is standard for Python
- Manual edge case enumeration: Rejected - incomplete by nature

### Decision 4: Shared Backup Utilities Module

**What**: Create `fx_bin/backup_utils.py` with `create_backup`, `restore_backup`, `cleanup_backup`.

**Why**:
- `replace.py` and `replace_functional.py` duplicate backup logic
- Centralizes safety-critical code
- Easier to test and audit

**Implementation**:
```python
# fx_bin/backup_utils.py
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Optional

@dataclass(frozen=True)
class BackupHandle:
    original_path: Path
    backup_path: Path
    original_mode: int

def create_backup(file_path: Path) -> BackupHandle:
    """Create a backup of the file, returning a handle for restore/cleanup."""
    ...

def restore_backup(handle: BackupHandle) -> None:
    """Restore original file from backup."""
    ...

def cleanup_backup(handle: BackupHandle) -> None:
    """Remove backup file after successful operation."""
    ...
```

**Alternatives considered**:
- Keep separate implementations: Rejected - DRY violation
- Context manager approach: Considered - may add in future iteration

### Decision 5: Intermediate Error Type Hierarchy

**What**: Add `FileOperationError` as intermediate base class.

**Why**:
- Enables catching related errors together
- Better error handling granularity
- Clearer error categorization

**Implementation**:
```python
# fx_bin/errors.py
class FxBinError(Exception):
    """Base error type for all fx_bin operations."""
    pass

class FileOperationError(FxBinError):
    """Base for file operation errors."""
    pass

class ReplaceError(FileOperationError):
    """Errors during text replacement operations."""
    pass

class IOError(FileOperationError):
    """IO operation errors."""
    pass
```

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing tests | Medium | High | Run full suite after each change |
| Pattern matching incompatibility | Low | Medium | Use `returns` API methods instead |
| Hypothesis tests too slow | Low | Low | Configure max examples, use profiles |
| Import cycles with new modules | Medium | Medium | Careful module organization |

## Migration Plan

### Phase 1: Testing Infrastructure (Low Risk)
1. Add hypothesis dependency
2. Create conftest.py
3. Add first property-based test
4. Verify CI passes

### Phase 2: Error Hierarchy (Low Risk)
1. Add intermediate error classes
2. Update inheritance
3. No behavior change

### Phase 3: Shared Utilities (Medium Risk)
1. Create backup_utils.py with tests
2. Update replace.py to use it
3. Update replace_functional.py to use it
4. Verify all safety tests pass

### Phase 4: Functional Patterns (Medium Risk)
1. Refactor one function at a time
2. Keep old implementation until tests pass
3. Remove old code after verification

### Rollback Plan
Each phase is independent. If issues found:
1. Revert commits for that phase
2. Investigate root cause
3. Fix and re-attempt

## Open Questions

1. **Should we add `result.unwrap_or_raise()` helper?** - May simplify some transitions
2. **Migrate all tests to pytest style or keep hybrid?** - Start with new tests, migrate gradually
3. **Add `returns` contrib extensions?** - Evaluate after core refactor

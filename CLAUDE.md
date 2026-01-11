<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FX bin is a Python utility collection providing command-line tools for file operations, including file counting, size analysis, finding files, text replacement, and a simple upload server. The project is packaged using Poetry and distributed via PyPI as `fx-bin`.

## Development Commands

### Build and Package
```bash
# Build the package
poetry build

# Install dependencies
poetry install

# Install package locally for development
pip install -e .
```

### Testing
```bash
# Install all dependencies first
poetry install --with dev

# Run all tests with pytest (recommended)
poetry run pytest

# Run tests without coverage requirement
poetry run pytest --no-cov

# Run with coverage report
poetry run pytest --cov=fx_bin --cov-report=html --cov-report=term-missing

# Run only passing core tests
poetry run pytest tests/test_size.py tests/test_files.py tests/test_find_files.py tests/test_replace.py -v

# Run security tests only (CRITICAL - must pass)
poetry run pytest tests/test_*security*.py -v --no-cov

# Run specific test file
poetry run pytest tests/test_replace_safety.py -v --no-cov
poetry run pytest tests/test_filter.py -v --no-cov

# Run specific test
poetry run pytest tests/test_upload_server_security.py::TestUploadServerSecurity::test_path_traversal_attack_blocked -v

# Run tests in parallel
poetry run pytest -n auto --no-cov

# Run tests with timeout protection
poetry run pytest --timeout=30 --no-cov

# Run only fast tests (exclude slow/integration tests)
poetry run pytest -m "not slow" --no-cov

# Run integration tests only
poetry run pytest -m integration --no-cov

# Run performance tests only
poetry run pytest -m performance --no-cov

# Run property-based tests (hypothesis)
poetry run pytest -m hypothesis -v --no-cov

# Alternative test runners (no Poetry required)
python tests/runners/simple_test_runner.py
python tests/runners/run_simple_tests.py
python tests/runners/run_tdd_tests.py

# Using unittest via Poetry
poetry run python -m unittest discover tests
poetry run python -m unittest tests.test_size

# Quick test for basic functionality
poetry run python -m unittest tests.test_size tests.test_files tests.test_replace tests.test_find_files -v
```

### Code Quality
```bash
# Run flake8 linting
poetry run flake8 fx_bin

# Run flake8 on specific file
poetry run flake8 fx_bin/files.py

# Run type checking with mypy
poetry run mypy fx_bin/

# Run code formatting with black
poetry run black fx_bin/ tests/

# Check code formatting (dry run)
poetry run black --check fx_bin/ tests/
```

### Security Testing
```bash
# Run security analysis with bandit
poetry run bandit -r fx_bin/

# Check dependencies for known vulnerabilities
poetry run safety check

# Run comprehensive security test suite
poetry run tox -e security

# Run all security-related checks
poetry run pytest tests/test_*security*.py -v && poetry run bandit -r fx_bin/ && poetry run safety check
```

### BDD Testing with pytest-bdd

The project uses [pytest-bdd](https://pytest-bdd.readthedocs.io/) for behavior-driven development testing with Gherkin syntax.

**BDD Test Structure:**
- Feature files: `features/*.feature` (Gherkin scenarios)
- Step definitions: `tests/bdd/test_*_steps.py` (Python implementations)
- Test configuration: `tests/bdd/conftest.py` (shared fixtures)

**Running BDD tests:**
```bash
# Run all BDD tests
poetry run pytest tests/bdd/ -v

# Run specific BDD test file
poetry run pytest tests/bdd/test_organize_steps.py -v

# Run smoke tests (critical happy path scenarios)
poetry run pytest -m smoke -v

# Run BDD tests with coverage
poetry run pytest tests/bdd/ --cov=fx_bin --cov-report=term-missing

# Run BDD tests without coverage (faster)
poetry run pytest tests/bdd/ -v --no-cov
```

**BDD Test Organization:**
- `@smoke` tag: Critical happy path tests that must pass
- `@critical` tag: Essential functionality tests
- `@integration` tag: Tests requiring full system integration
- `@error_handling` tag: Edge case and error condition tests

**Current BDD Test Coverage:**
- File filter BDD tests: 10 scenarios covering filtering by extension
- File organize BDD tests: 50 scenarios covering date-based organization
- 43/50 organize tests passing (86% pass rate)
- All 72 integration tests passing

**Key BDD Features:**
- Gherkin syntax (Given/When/Then) for readable test scenarios
- Reusable step definitions across multiple scenarios
- Automatic test data generation with fixtures
- Command execution testing with Click's CliRunner

### Property-Based Testing with Hypothesis

The project uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing to automatically discover edge cases.

**When to use property-based tests:**
- Testing invariants that should hold for all inputs
- Discovering edge cases automatically
- Verifying mathematical properties (idempotency, commutativity, etc.)
- Boundary condition testing

**Example usage:**
```python
from hypothesis import given, strategies as st, settings, HealthCheck

@pytest.mark.hypothesis
@given(
    search=st.text(min_size=1, max_size=50),
    replace=st.text(max_size=50),
    content=st.text(max_size=500)
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_invariant(temp_test_dir, search, replace, content):
    """Test that invariant holds for all generated inputs."""
    # INVARIANT: After replacement, search shouldn't appear
    # unless replace contains it
    test_file = temp_test_dir / "test.txt"
    test_file.write_text(content)
    work(search, replace, str(test_file))
    result = test_file.read_text()

    if search not in replace:
        assert result.count(search) <= content.count(search)
```

**Important notes:**
- Mark tests with `@pytest.mark.hypothesis`
- Use `suppress_health_check=[HealthCheck.function_scoped_fixture]` when using pytest fixtures with `@given`
- Hypothesis generates many test cases (controlled by `max_examples`)
- Failed tests are automatically shrunk to minimal failing example
- Use `assume()` to filter out invalid inputs

**Running hypothesis tests:**
```bash
# Run all hypothesis tests
poetry run pytest -m hypothesis -v

# Run with more examples for thorough testing
poetry run pytest -m hypothesis --hypothesis-seed=random -v
```

## Architecture

### Package Structure
- **fx_bin/**: Main package directory containing all utility modules
  - Each utility is a standalone module with a `main()` function entry point
  - Scripts are registered in `pyproject.toml` under `[tool.poetry.scripts]`

### Available Commands (via unified `fx` CLI)
- `fx files`: Count files in directories (files.py)
- `fx size`: Analyze file/directory sizes (size.py)
- `fx ff`: Find files utility (find_files.py)
- `fx fff`: Find first file (alias for ff --first)
- `fx filter`: Filter files by extension and sort by time (filter.py)
- `fx replace`: Text replacement utility (replace.py)
- `fx root`: Find Git project root (root.py)
- `fx today`: Daily workspace manager (today.py)
- `fx list`: List all available commands

### Key Dependencies
- **click**: Command-line interface creation
- **loguru**: Logging functionality
- Python 3.11+ required

### Module Pattern
Each utility module follows this pattern:
1. Implements core functionality in functions/classes
2. Provides a `main()` function as the CLI entry point
3. Uses Click decorators for command-line argument parsing
4. Registered as a console script in pyproject.toml

### Testing Approach
- Uses unittest framework with pytest enhancements
- Tests located in `tests/` directory
- Test runners available in `tests/runners/` directory
- Testing documentation in `docs/testing/` directory
- Click's CliRunner used for testing CLI interfaces
- Test files follow `test_*.py` naming convention
- Virtual environment: `.venv/` (Python standard)
- Comprehensive security and safety tests implemented

### Functional Programming Patterns

The project uses functional programming principles with the [returns](https://returns.readthedocs.io/) library for safer, more composable code.

#### Railway-Oriented Programming (ROP)

Railway-Oriented Programming treats success and failure as two parallel "tracks" that functions operate on. Functions return `Result[SuccessType, ErrorType]` or `IOResult[SuccessType, ErrorType]` instead of raising exceptions.

**Core Concepts:**
- `Result[T, E]`: Pure computation that can succeed (T) or fail (E)
- `IOResult[T, E]`: IO operation that can succeed (T) or fail (E)
- `flow()`: Pipeline composition for chaining operations
- `bind()`: Continue on success track, short-circuit on failure
- `lash()`: Error recovery - handle failures and potentially return to success track

**Example from replace_functional.py:**
```python
from returns.pipeline import flow
from returns.pointfree import bind, lash

def work_functional(search_text: str, replace_text: str, filename: str) -> IOResult[None, ReplaceError]:
    """Replace text with automatic backup/restore on failure."""
    # Pure validation first
    validation = validate_file_access(filename)
    if isinstance(validation, Failure):
        return IOResult.from_failure(validation.failure())

    real_path = validation.unwrap()
    context = ReplaceContext(search_text, replace_text)

    # Functional pipeline: create backup -> perform replacement -> cleanup
    replacement_pipeline = _make_replacement_pipeline(context)

    return flow(
        create_backup(real_path),          # Create backup (IOResult)
        bind(replacement_pipeline),        # Replace on success, auto-restore on failure
    )
```

**Benefits:**
- Explicit error handling (no hidden exceptions)
- Composable operations (chain with `flow`, `bind`, `lash`)
- Type-safe (mypy verifies success/error types)
- Self-documenting (function signatures show what can fail)

#### Pure vs IO Functions Separation

The codebase separates pure logic from IO operations for better testability and reasoning.

**Pure Functions** (no side effects, deterministic):
```python
def should_process_directory(depth: int, context: FolderContext, dir_inode: Tuple[int, int] | None = None) -> bool:
    """Pure function - same inputs always give same output."""
    if depth > context.max_depth:
        return False
    if dir_inode is not None and dir_inode in context.visited_inodes:
        return False
    return True

def calculate_entry_contribution(entry_info: object) -> int:
    """Pure calculation - no IO, no mutations."""
    if hasattr(entry_info, "is_file") and entry_info.is_file:
        return getattr(entry_info, "size", 0)
    return 0
```

**IO Functions** (interact with file system):
```python
@impure_safe
def _sum_folder_recursive(path: str, context: FolderContext, depth: int) -> IOResult[int, FolderError]:
    """IO function - reads from file system, can fail."""
    try:
        dir_stat = os.stat(path)
        total = 0
        for entry in os.scandir(path):
            # ... file system operations
        return IOResult.from_value(total)
    except (OSError, PermissionError) as e:
        return IOResult.from_failure(FolderError(f"Cannot access {path}: {e}"))
```

**Key Decorator: `@impure_safe`**
- Wraps functions that perform IO operations
- Automatically catches exceptions and returns `IOResult`
- Signals to readers: "this function has side effects"

#### Shared Types Module

Common types are centralized in `fx_bin/shared_types.py` to eliminate duplication and prevent circular imports.

**Shared Types:**
```python
from fx_bin.shared_types import EntryType, FileBackup, FolderContext

# EntryType: Enum for FILE vs FOLDER
# FileBackup: Immutable backup metadata (original_path, backup_path, original_mode)
# FolderContext: Traversal state (visited_inodes, max_depth)
```

**Benefits:**
- Single source of truth for type definitions
- No circular import issues
- Easy to update types across entire codebase
- Better IDE autocomplete and type checking

#### Type Annotations Best Practices

The project uses precise type annotations for better static analysis:

**Use `Sequence[T]` for function parameters** (instead of `Tuple[T, ...]`):
```python
# GOOD - accepts tuple, list, or any sequence
def process_files(filenames: Sequence[str]) -> int:
    for name in filenames:
        process(name)

# AVOID - too restrictive, only accepts tuples
def process_files(filenames: Tuple[str, ...]) -> int:
    pass
```

**Why `Sequence` is better:**
- More abstract and flexible (covariant type)
- Accepts any sequence type (tuple, list, etc.)
- Recommended by mypy for read-only parameters
- Signals intent: "I only need to iterate, not mutate"

**Use `List[T]` for return values** (when you return a mutable list):
```python
def collect_results() -> List[Result[str, Error]]:
    results = []
    # ... populate results
    return results
```

#### RequiresContext Pattern

Functions that need shared context use `RequiresContext` to make dependencies explicit:

```python
from returns.context import RequiresContext

def sum_folder_size_functional(path: str = ".") -> RequiresContext[IOResult[int, FolderError], FolderContext]:
    """Function that requires FolderContext to execute."""
    def _sum_folder(context: FolderContext) -> IOResult[int, FolderError]:
        return _sum_folder_recursive(path, context, depth=0)
    return RequiresContext(_sum_folder)

# Usage:
context = FolderContext(visited_inodes=set(), max_depth=100)
result = sum_folder_size_functional("/path/to/folder")(context)  # Inject context
```

**Benefits:**
- Explicit dependencies (function signature shows what context is needed)
- Easy to test (inject different contexts for different scenarios)
- Avoids global state
- Composable (can map over context, chain operations)

#### Mock Helpers for Testing

Reusable context managers reduce test code duplication:

```python
from contextlib import contextmanager

@contextmanager
def mock_windows_file_ops():
    """Context manager for mocking Windows file operations."""
    with patch("os.remove") as mock_remove, \
         patch("os.rename") as mock_rename, \
         patch("os.unlink") as mock_unlink:

        mock_remove.return_value = None
        mock_rename.return_value = None
        mock_unlink.return_value = None

        yield {
            'remove': mock_remove,
            'rename': mock_rename,
            'unlink': mock_unlink
        }

# Usage in tests:
def test_windows_replacement(temp_test_dir):
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    with mock_windows_file_ops() as mocks:
        work("World", "Python", str(test_file))
        assert mocks['remove'].call_count == 1
        mocks['rename'].assert_called_once()
```

**Benefits:**
- DRY (Don't Repeat Yourself) - write mock setup once
- Clearer test intent - mock helper name explains what's being mocked
- Easier to maintain - update mock logic in one place
- Reduced boilerplate - 13 lines → 5 lines per test

#### Immutable Data Classes

All data classes use `frozen=True` for immutability:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ReplaceContext:
    """Immutable context - prevents accidental mutations."""
    search_text: str
    replace_text: str
    create_backup: bool = True
    preserve_permissions: bool = True

# This raises FrozenInstanceError:
# context.search_text = "new value"  # ❌ Error!

# Instead, create new instance:
new_context = ReplaceContext(
    search_text="new value",
    replace_text=context.replace_text,
    create_backup=context.create_backup
)
```

**Benefits:**
- Thread-safe (no mutations means no race conditions)
- Easier to reason about (data never changes unexpectedly)
- Hashable (can use as dict keys or set members)
- Prevents bugs (compiler catches mutation attempts)

#### Error Hierarchy

Custom exceptions use inheritance for polymorphic error handling:

```python
from fx_bin.errors import FileOperationError, IOError, ReplaceError, SecurityError

# Hierarchy:
# FileOperationError (base for all file operations)
# ├── ReplaceError (text replacement errors)
# ├── IOError (file I/O errors)
# └── SecurityError (security violations)

# Polymorphic handling:
try:
    work_functional(search, replace, filename)
except FileOperationError:
    # Catches ReplaceError, IOError, SecurityError
    handle_any_file_error()
except ReplaceError:
    # Catches only replacement-specific errors
    handle_replace_error()
```

#### Partial Application for Avoiding Lambdas

Use `functools.partial` to bind parameters without lambda functions:

```python
from functools import partial

# GOOD - uses partial to bind backup parameter
def _make_replacement_pipeline(context: ReplaceContext) -> Callable[[FileBackup], IOResult[None, ReplaceError]]:
    def execute_replacement(backup: FileBackup) -> IOResult[None, ReplaceError]:
        handle_failure = partial(_handle_replacement_failure, backup)
        handle_success = partial(_handle_replacement_success, backup)

        return flow(
            perform_replacement(context, backup),
            lash(handle_failure),  # No lambda needed!
            bind(handle_success),  # Cleaner than lambda
        )
    return execute_replacement

# AVOID - using lambdas
return flow(
    perform_replacement(context, backup),
    lash(lambda error: _handle_replacement_failure(backup, error)),  # Verbose
    bind(lambda _: _handle_replacement_success(backup, _)),  # Less clear
)
```

**Benefits:**
- More readable (no lambda syntax)
- Easier to debug (named functions in stack traces)
- Better type inference (mypy understands partial better)
- Follows functional composition principles
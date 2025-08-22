# Functional Python Refactor Plan

**Generated at:** 2025-08-23 02:02  
**Scope:** fx_bin/*.py  
**Mode:** light  
**Summary scorecard:** Hotspots: 8 · Refactor items: 12 · Est. effort: M

## Executive Summary

This plan refactors the fx_bin utility collection toward a functional style using `dry-python/returns` to improve safety, testability, and error handling. Currently, the codebase exhibits scattered `try/except` blocks (132 occurrences), implicit IO operations, nullable returns, and direct system exits. We will transform these patterns into composable, type-safe abstractions using `Result` for error handling, `Maybe` for nullable values, `IO/IOResult` for side effects, and `RequiresContext` for dependency injection.

The refactoring preserves backward compatibility while internally adopting functional patterns. Error handling becomes explicit and composable through `Result` types, eliminating silent failures. IO operations are marked and contained, making side effects visible in type signatures. This approach reduces runtime exceptions, improves testability through dependency injection, and creates more maintainable code with clear data flow.

## Inventory & Hotspots (sorted)

| Rank | Module:Symbol | Signals | Payoff | Effort | Risk | Confidence | Notes |
|------|---------------|---------|--------|--------|------|------------|-------|
| 1 | replace:work | try/except sprawl, hidden IO, backup complexity | 5 | 3 | 2 | 4 | Core functionality, high impact |
| 2 | pd:main | global state, sys.exit, exception leaks | 4 | 2 | 2 | 4 | Simple module, clear boundaries |
| 3 | common:sum_folder_size | None-pyramid, recursive complexity, hidden IO | 4 | 3 | 2 | 3 | Critical path, needs careful testing |
| 4 | upload_server:do_POST | security checks, IO mixing, error sprawl | 5 | 4 | 3 | 3 | Security-critical, complex |
| 5 | common:SizeEntry.from_scandir | try/except, nullable returns | 3 | 2 | 1 | 4 | Clean abstraction opportunity |
| 6 | find_files:find_files | hidden IO, exception leaks | 3 | 2 | 2 | 4 | Simple pattern matching |
| 7 | size:list_size | print side effects, mixed concerns | 3 | 3 | 2 | 3 | UI/logic separation needed |
| 8 | files:list_files_count | print side effects, mixed concerns | 3 | 3 | 2 | 3 | Similar to size module |

**PriorityScore = (2×Payoff + Confidence) − Effort − Risk**

## Numbered Refactor Items

### [R-1] fx_bin/replace.py:work

**Current Symptoms:**
- 8 separate try/except blocks with different error types
- Direct file IO without abstraction
- Complex backup/restore logic with implicit state
- Multiple early returns and error conditions
- Side effects (file operations) mixed with business logic

**Proposed Change:**
- Wrap file operations in `IOResult[T, Exception]` for explicit effect tracking
- Use `Result.do()` notation for sequential operations with error handling
- Create `BackupContext` with `RequiresContext` for dependency injection
- Chain operations with `flow` and `bind` for composable error handling
- Unify error types to `ReplaceError` supertype

**Diff Preview (illustrative):**
```python
# Before
def work(search_text: str, replace_text: str, filename: str) -> None:
    if not os.access(filename, os.W_OK):
        raise PermissionError(f"File {filename} is readonly")
    # ... complex try/except blocks

# After
from returns.result import Result, safe
from returns.io import IOResult, impure_safe
from returns.context import RequiresContext

@impure_safe
def work(search_text: str, replace_text: str, filename: str
) -> IOResult[None, ReplaceError]:
    return flow(
        validate_file_access(filename),
        bind(lambda _: create_backup(filename)),
        bind(lambda backup: perform_replacement(search_text, replace_text, filename, backup)),
        bind(lambda _: cleanup_backup(filename)),
    )
```

**Acceptance Criteria:**
- All file operations return `IOResult` types
- No uncaught exceptions escape the function
- Backup/restore is atomic and guaranteed
- Error messages are informative and typed

**Impact & Risk:** M/M - Core functionality, but well-tested  
**Rollback:** Keep original function as `work_legacy` during transition  
**Callers Affected:** CLI main function in replace.py

### [R-2] fx_bin/pd.py:main

**Current Symptoms:**
- Global mutable state (`pandas` variable)
- Direct `sys.exit()` calls (3 occurrences)
- Implicit ImportError handling
- Mixed concerns (validation, IO, business logic)

**Proposed Change:**
- Replace global state with `RequiresContext[PandasEnv, T]`
- Convert sys.exit to `Result[int, PdError]` returns
- Use `Maybe` for optional pandas availability
- Separate validation from execution with `Result` chain

**Diff Preview (illustrative):**
```python
# Before
def main(url, output_filename: str, args=None) -> int:
    if not output_filename.endswith(".xlsx"):
        output_filename += ".xlsx"
    if os.path.exists(output_filename):
        print("This file already exists. Skip")
        sys.exit(1)

# After
from returns.result import Result, Success, Failure
from returns.maybe import Maybe
from returns.context import RequiresContextResult

def main(url: str, output_filename: str
) -> RequiresContextResult[int, PandasEnv, PdError]:
    return flow(
        validate_output_filename(output_filename),
        bind(check_file_not_exists),
        bind(lambda name: process_json_to_excel(url, name)),
        map(lambda _: 0),  # Success returns 0
    )
```

**Acceptance Criteria:**
- No global state modifications
- All exits return Result types
- Pandas import is lazy and safe
- Error messages are structured

**Impact & Risk:** S/L - Simple module, easy to test  
**Rollback:** Wrapper function for CLI compatibility  
**Callers Affected:** CLI entry point

### [R-3] fx_bin/common.py:sum_folder_size

**Current Symptoms:**
- Complex recursion with mutable state tracking
- Hidden IO in os.scandir/os.stat calls
- Multiple try/except blocks at different levels
- Nullable returns on error conditions
- Depth and inode tracking via hidden parameters

**Proposed Change:**
- Wrap recursion in `IOResult` for explicit IO
- Use `RequiresContext` for visited_inodes state
- Convert to trampolined recursion with `Cont` monad
- Return `Result[int, FolderError]` for size calculation
- Separate pure logic from IO operations

**Diff Preview (illustrative):**
```python
# Before
def sum_folder_size(path: str = '.', _visited_inodes=None, _depth=0) -> int:
    if _visited_inodes is None:
        _visited_inodes = set()
    if _depth > 100:
        return 0
    # ... complex try/except with recursion

# After
from returns.io import IOResult
from returns.context import RequiresContextIOResult
from returns.result import safe

@impure_safe
def sum_folder_size(path: str
) -> RequiresContextIOResult[int, FolderEnv, FolderError]:
    return RequiresContextIOResult.from_value(path).bind(
        lambda p: scan_directory_recursive(p, depth=0)
    )
```

**Acceptance Criteria:**
- Stack-safe recursion handling
- Explicit IO boundary
- No mutable state leakage
- Proper cycle detection

**Impact & Risk:** M/M - Critical path function  
**Rollback:** Facade pattern over new implementation  
**Callers Affected:** size.py, files.py modules

### [R-4] fx_bin/upload_server.py:do_POST

**Current Symptoms:**
- Security validation mixed with business logic
- Multiple print statements for logging
- Complex multipart parsing with exceptions
- Direct file writes without abstraction
- Authentication checks scattered

**Proposed Change:**
- Create `SecurityContext` with `RequiresContext`
- Use `Result` chain for validation pipeline
- Wrap file operations in `IOResult`
- Separate authentication, validation, and execution
- Return structured responses via `Result`

**Diff Preview (illustrative):**
```python
# Before
def do_POST(self):
    if REQUIRE_AUTH and not self._check_auth():
        self.send_error(401, "Authentication required")
        return
    # ... complex parsing and validation

# After
from returns.pipeline import flow
from returns.result import Result
from returns.context import RequiresContextIOResult

def do_POST(self) -> RequiresContextIOResult[None, SecurityEnv, UploadError]:
    return flow(
        authenticate_request(self.headers),
        bind(lambda _: parse_multipart_data(self.rfile, self.headers)),
        bind(validate_upload_security),
        bind(save_uploaded_file),
        bind(send_success_response),
    )
```

**Acceptance Criteria:**
- All security checks return Result types
- File operations are atomic
- Authentication is centralized
- Errors are properly typed

**Impact & Risk:** L/H - Security-critical code  
**Rollback:** Feature flag for new upload handler  
**Callers Affected:** HTTP server framework

### [R-5] fx_bin/common.py:SizeEntry.from_scandir

**Current Symptoms:**
- Try/except with generic exception handling
- Returns None on permission errors
- Mixed concerns (stat, error handling, object creation)
- Implicit IO operations

**Proposed Change:**
- Return `Maybe[SizeEntry]` for optional results
- Use `IOResult` for file stat operations
- Separate permission handling from business logic
- Make error conditions explicit in types

**Diff Preview (illustrative):**
```python
# Before
@classmethod
def from_scandir(cls, entry: os.DirEntry, parent_dir: str = "") -> Optional["SizeEntry"]:
    try:
        stat = entry.stat(follow_symlinks=False)
        return cls(...)
    except (OSError, PermissionError):
        return None

# After
from returns.maybe import Maybe
from returns.io import IOResult

@classmethod
def from_scandir(cls, entry: os.DirEntry, parent_dir: str = ""
) -> IOResult[Maybe[SizeEntry], StatError]:
    return get_entry_stat(entry).map(
        lambda stat: Maybe.from_optional(
            cls(...) if stat else None
        )
    )
```

**Acceptance Criteria:**
- Explicit Maybe type for optional results
- IO operations marked with IOResult
- No silent error swallowing
- Type-safe error handling

**Impact & Risk:** S/L - Utility function, easy migration  
**Rollback:** Adapter method for compatibility  
**Callers Affected:** list_size, list_files_count functions

### [R-6] fx_bin/find_files.py:find_files

**Current Symptoms:**
- Direct os.walk without error handling
- Implicit IO operations
- Mixed filtering logic with IO
- No error recovery mechanism

**Proposed Change:**
- Wrap os.walk in `IOResult` generator
- Separate pure filtering from IO traversal
- Use `Result` for pattern matching
- Return `IOResult[List[str], FindError]`

**Diff Preview (illustrative):**
```python
# Before
def find_files(keyword: str, path: str = ".") -> List[str]:
    result = []
    for root, dirs, files in os.walk(path):
        # ... pattern matching
    return result

# After
from returns.io import IOResult
from returns.iterables import Fold

@impure_safe
def find_files(keyword: str, path: str = "."
) -> IOResult[List[str], FindError]:
    return flow(
        walk_directory_safe(path),
        bind(lambda entries: filter_matching_files(keyword, entries)),
        map(list),
    )
```

**Acceptance Criteria:**
- Safe directory traversal
- Explicit IO boundaries
- Error recovery on permission issues
- Pure filtering logic

**Impact & Risk:** S/L - Simple transformation  
**Rollback:** Wrapper function  
**Callers Affected:** CLI find_files command

### [R-7] fx_bin/size.py:list_size

**Current Symptoms:**
- Print statements mixed with logic
- Direct IO without abstraction
- Sorting and formatting concerns mixed
- No separation of concerns

**Proposed Change:**
- Separate data collection from presentation
- Use `IO` monad for print operations
- Return `IOResult[List[SizeEntry], SizeError]`
- Create pure formatting functions

**Diff Preview (illustrative):**
```python
# Before
def list_size(dir_path: str = ".") -> None:
    entries = []
    # ... collect and print

# After
from returns.io import IO, IOResult
from returns.pipeline import flow

def list_size(dir_path: str = "."
) -> IOResult[None, SizeError]:
    return flow(
        collect_size_entries(dir_path),
        map(sort_entries),
        map(format_entries),
        bind(print_entries),
    )
```

**Acceptance Criteria:**
- Pure business logic
- IO operations isolated
- Testable formatting
- Error handling

**Impact & Risk:** S/M - UI changes  
**Rollback:** Keep original for compatibility  
**Callers Affected:** CLI size command

### [R-8] fx_bin/files.py:list_files_count

**Current Symptoms:**
- Similar to list_size issues
- Print statements throughout
- Mixed data and presentation
- No error handling

**Proposed Change:**
- Mirror approach from [R-7]
- Share formatting utilities
- Use same IO patterns
- Return structured data

**Diff Preview (illustrative):**
```python
# Similar pattern to [R-7]
def list_files_count(dir_path: str = "."
) -> IOResult[None, FilesError]:
    return flow(
        collect_file_counts(dir_path),
        map(sort_counts),
        map(format_counts),
        bind(print_counts),
    )
```

**Acceptance Criteria:**
- Consistent with size module
- Reusable components
- Clear separation
- Testable

**Impact & Risk:** S/M - UI consistency  
**Rollback:** Gradual migration  
**Callers Affected:** CLI files command

### [R-9] Error Type Hierarchy

**Current Symptoms:**
- Generic Exception catching
- Inconsistent error messages
- No error type hierarchy
- Lost error context

**Proposed Change:**
- Create domain error types
- Establish error hierarchy
- Preserve error context
- Type-safe error handling

**Diff Preview (illustrative):**
```python
# New error hierarchy
from typing import Union

class FxBinError(Exception):
    """Base error type"""

class IOError(FxBinError):
    """IO operation errors"""

class ValidationError(FxBinError):
    """Input validation errors"""

class SecurityError(FxBinError):
    """Security violation errors"""

# Union type for Result
AppError = Union[IOError, ValidationError, SecurityError]
```

**Acceptance Criteria:**
- Complete error taxonomy
- Consistent error messages
- Error context preservation
- Type checking passes

**Impact & Risk:** S/L - Foundation work  
**Rollback:** N/A - additive change  
**Callers Affected:** All modules

### [R-10] Configuration Context

**Current Symptoms:**
- Global configuration variables
- Direct environment access
- Hardcoded values
- No dependency injection

**Proposed Change:**
- Create `AppConfig` context
- Use `RequiresContext` for config
- Centralize environment access
- Enable testing with different configs

**Diff Preview (illustrative):**
```python
from returns.context import RequiresContext
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    max_file_size: int
    require_auth: bool
    allowed_extensions: frozenset
    bind_localhost: bool

def with_config[T](f: Callable[[AppConfig], T]
) -> RequiresContext[T, AppConfig]:
    return RequiresContext(f)
```

**Acceptance Criteria:**
- No global state
- Config injection works
- Tests can override config
- Type-safe access

**Impact & Risk:** S/L - Infrastructure  
**Rollback:** Gradual adoption  
**Callers Affected:** upload_server primarily

### [R-11] Logging Infrastructure

**Current Symptoms:**
- Direct print statements
- Loguru logger without structure
- No log levels
- Mixed with business logic

**Proposed Change:**
- Create `LogContext` with `RequiresContext`
- Use `IO` for log operations
- Structured logging
- Separate logging from logic

**Diff Preview (illustrative):**
```python
from returns.context import RequiresContextIO
from returns.io import IO

class LogContext:
    def log(self, level: str, message: str) -> IO[None]:
        return IO(lambda: logger.log(level, message))

def with_logging[T](f: Callable[[LogContext], T]
) -> RequiresContextIO[T, LogContext]:
    return RequiresContextIO(f)
```

**Acceptance Criteria:**
- Structured logging
- Testable log output
- No print statements
- Clear log levels

**Impact & Risk:** S/L - Cross-cutting  
**Rollback:** Logging facade  
**Callers Affected:** All modules

### [R-12] Testing Utilities

**Current Symptoms:**
- Complex mocking
- Brittle test setup
- IO in tests
- Hard to test edge cases

**Proposed Change:**
- Create test contexts
- Property-based testing with Result
- IO simulation utilities
- Test data generators

**Diff Preview (illustrative):**
```python
# Test utilities
from returns.context import Reader
from hypothesis import strategies as st

def test_context() -> AppConfig:
    return AppConfig(
        max_file_size=1024,
        require_auth=False,
        allowed_extensions=frozenset(['.txt']),
        bind_localhost=True,
    )

@given(st.text())
def test_with_result(search_text):
    result = work(search_text, "replace", "test.txt").run(test_context())
    assert result.is_ok()
```

**Acceptance Criteria:**
- Property tests work
- IO is simulated
- Context injection works
- Coverage improves

**Impact & Risk:** S/L - Test only  
**Rollback:** Keep old tests  
**Callers Affected:** Test suite

## Step-by-Step Execution Plan

### Step 1 – Baseline & type tooling (Week 1)
- Add `returns` to dependencies: `poetry add dry-python-returns`
- Configure mypy plugin in pyproject.toml
- Add returns mypy plugin configuration
- Establish test baseline (current: 116 passing)
- Create error type hierarchy [R-9]
- **Checkpoint:** Type checking passes, tests green

### Step 2 – Pilot refactors (Week 2)
- Implement [R-2] pd.py refactor (simplest module)
- Implement [R-5] SizeEntry.from_scandir (isolated function)
- Create shared test utilities [R-12]
- Validate patterns with team
- **Checkpoint:** 2 modules using Result/Maybe, tests passing

### Step 3 – Core modules (Weeks 3-4)
- Implement [R-1] replace.py (high impact)
- Implement [R-3] common.py recursive functions
- Implement [R-10] configuration context
- Update integration tests
- **Checkpoint:** Core functionality migrated, performance validated

### Step 4 – UI and IO (Week 5)
- Implement [R-7] size.py presentation
- Implement [R-8] files.py presentation
- Implement [R-6] find_files.py
- Implement [R-11] logging infrastructure
- **Checkpoint:** All print statements removed, structured output

### Step 5 – Security-critical (Week 6)
- Implement [R-4] upload_server.py
- Security audit of Result chains
- Performance testing
- Documentation updates
- **Checkpoint:** Security tests passing, no regressions

### Step 6 – Stabilize (Week 7)
- Remove legacy code paths
- Update documentation
- Performance benchmarks
- Team training on patterns
- **Checkpoint:** Version 0.9.0 release ready

**Estimated timeline:** 7 weeks (M effort)  
**Risk mitigation:** Feature flags for gradual rollout

## Coding Patterns & Recipes

### Null → Maybe
```python
from returns.maybe import Maybe

# Before
result = get_value()
if result is None:
    return default
return process(result)

# After
Maybe.from_optional(get_value()).map(process).value_or(default)
```

### Exceptions → Result
```python
from returns.result import safe, Result

# Before
try:
    value = risky_operation()
    return process(value)
except Exception as e:
    logger.error(e)
    return None

# After
@safe
def risky_operation() -> Result[Value, Exception]:
    ...

risky_operation().map(process).value_or(None)
```

### Effects → IO/IOResult
```python
from returns.io import IO, impure_safe

# Before
def read_file(path):
    with open(path) as f:
        return f.read()

# After
@impure_safe
def read_file(path) -> IOResult[str, IOError]:
    ...
```

### DI → RequiresContext
```python
from returns.context import RequiresContext

# Before
def process(data):
    config = get_global_config()
    return transform(data, config)

# After
def process(data) -> RequiresContext[Result, Config]:
    return RequiresContext(lambda config: transform(data, config))
```

### Cross-container binds
```python
from returns.pointfree import bind
from returns.pipeline import flow

# Composing different containers
flow(
    get_value(),  # Result[str, Error]
    bind(validate),  # Result[Valid, Error]
    bind(process),  # IOResult[Output, Error]
    bind(save),  # IOResult[None, Error]
)
```

## Tooling & Config Snippets

### pyproject.toml additions
```toml
[tool.poetry.dependencies]
dry-python-returns = "^0.22.0"

[tool.mypy]
plugins = ["returns.contrib.mypy.returns_plugin"]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
addopts = "--cov=fx_bin --cov-report=term-missing"
```

### Pre-commit hooks
```yaml
repos:
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: poetry run mypy
        language: system
        types: [python]
```

### Example commands
```bash
# Type checking
poetry run mypy fx_bin/ --strict

# Testing
poetry run pytest -xvs

# Coverage
poetry run pytest --cov=fx_bin --cov-report=html

# Linting
poetry run ruff check fx_bin/
```

## Open Questions / Out-of-Scope

### Open Questions
1. **Error granularity:** Should we have module-specific error types or shared domain errors?
2. **Async support:** Future need for async IO operations with returns?
3. **API compatibility:** Maintain legacy function signatures or version bump?
4. **Performance targets:** Acceptable overhead for functional abstractions?

### Out-of-Scope
- Async/await refactoring (separate effort)
- GUI additions
- Database integration
- Network protocol changes
- Algorithm optimizations unrelated to functional style

## Reviewer Checklist

- [ ] Each `[R-n]` item has clear rationale and acceptance criteria
- [ ] Risk assessment is realistic for each change
- [ ] Rollback strategies are defined
- [ ] No .py files were edited by this plan
- [ ] Dependencies are clearly specified
- [ ] Timeline is achievable with current resources
- [ ] Test strategy covers all refactored code
- [ ] Security implications are addressed
- [ ] Performance impact is analyzed
- [ ] Documentation plan is included
- [ ] Team training needs are identified
- [ ] Error handling strategy is consistent
- [ ] Logging approach is structured
- [ ] Configuration management is centralized
- [ ] Integration points are identified

---

*This plan is ready for review. No code files have been modified. Implementation will begin after approval.*
# Design: Fix Organize Edge Cases

## Context

Code review of `fx organize` command identified 4 edge cases and resource leaks that need fixing. These are non-critical issues that improve robustness and correctness.

## Goals / Non-Goals

**Goals:**
- Fix file descriptor leak in EXDEV handling
- Make --yes respect --quiet flag
- Clarify or fix ASK mode runtime conflict behavior
- Fix directory creation path semantic inconsistency

**Non-Goals:**
- Changing core conflict resolution logic (already fixed)
- Modifying user-facing API or options

## Decisions

### Decision 1: Close File Descriptor After mkstemp()

**Current Code (organize_functional.py:423, 475):**
```python
fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(real_target))
try:
    shutil.copy2(real_source, temp_path)
    os.replace(temp_path, real_target)
    os.unlink(real_source)
finally:
    try:
        os.unlink(temp_path)
    except OSError:
        pass
```

**Problem:** `fd` is never closed, causing file descriptor leak.

**Fix:**
```python
fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(real_target))
os.close(fd)  # Close the fd we don't need
try:
    shutil.copy2(real_source, temp_path)  # Copy doesn't need fd
    os.replace(temp_path, real_target)
    os.unlink(real_source)
finally:
    try:
        os.unlink(temp_path)
    except OSError:
        pass
```

**Why:** tempfile.mkstemp() returns an open file descriptor to prevent race conditions. We close it immediately because we only need the unique filename, not the fd. shutil.copy2() opens its own fds.

### Decision 2: --yes Should Respect --quiet

**Current Code (cli.py:784):**
```python
if yes:
    click.echo(
        f"Organizing files from {source} to {context.output_dir or source}..."
    )
```

**Problem:** This prints even when `--quiet` is set, violating "errors and summary only".

**Fix:**
```python
if yes and not quiet:
    click.echo(
        f"Organizing files from {source} to {context.output_dir or source}..."
    )
```

**Why:** Users expect --quiet to suppress all non-essential output. The summary is still shown at the end.

### Decision 2.5: Configure loguru for Quiet/Verbose Modes

**Current State:**
- loguru is imported but not configured
- Default loguru level is INFO (WARNING messages always shown)
- --quiet and --verbose flags don't affect loguru output

**Problem:** ASK runtime warnings need to respect --quiet flag

**Fix:**
```python
# In organize() entry point (cli.py):
from loguru import logger

def organize(..., quiet: bool = False, verbose: bool = False, ...):
    # Configure loguru based on quiet/verbose
    if quiet:
        logger.remove()
        logger.add(sys.stderr, level="ERROR")  # Only ERROR and above
    elif verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")  # Show everything
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")   # Default level

    # Now logger.warning() respects --quiet flag
```

**Why:**
- loguru doesn't automatically respect CLI flags
- Explicit configuration ensures WARNING output is controlled
- CliRunner(mix_stderr=False) can verify stderr content in tests

### Decision 3: ASK Mode Runtime Conflicts

**Current Behavior:**
- Scan phase: Detects disk conflicts, prompts user (TTY) or skips (non-TTY)
- Execution phase: If new conflict appears (TOCTOU), move_file_safe() treats ASK as SKIP

**Decision:** Document current behavior - ASK only handles scan-time conflicts, runtime conflicts skip with warning

**Implementation:**
- Use loguru's `logger.warning()` for warning messages (respects --quiet)
- Update CLI help text to clarify behavior
- No click.echo() in non-quiet paths (would violate --quiet)

**Why:**
- Runtime conflicts are rare (only if files are modified between scan and execution)
- Implementing runtime prompts requires significant CLI refactoring
- Current behavior is safe (skip is conservative)
- Using loguru ensures --quiet is respected

### Decision 4: Use real_target for Directory Creation

**Current Code (organize_functional.py:453):**
```python
target_dir = os.path.dirname(target)
```

**Problem:** Should use `real_target` for consistency with the actual file being written.

**Fix:**
```python
target_dir = os.path.dirname(real_target)
```

**Why:** `target` may contain symbolic links or relative path components. `real_target` is the resolved absolute path. We should create the directory where the file will actually be written.

## Data Flow

```
File Descriptor Handling:
1. mkstemp() returns (fd, path)
2. os.close(fd) - release fd immediately
3. shutil.copy2() - copies with own fds
4. os.replace() - atomic replace
5. os.unlink() - remove source

Quiet Mode Flow:
1. User runs: fx organize --yes --quiet
2. CLI checks: if yes and not quiet
3. Only print "Organizing..." if not quiet
4. Summary always prints (regardless of quiet)

Directory Creation Flow:
1. Resolve real_target from target (symlinks resolved)
2. Get dirname of real_target (not target)
3. Create directory if needed
4. Write file to real_target
```

## Error Handling

| Error Type | Handling |
|------------|----------|
| os.close() error | Ignore (fd will be closed on process exit) |
| Directory creation failure | Existing error handling (returns IOResult.failure) |
| ASK runtime conflict | Skip with log entry |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| os.close() might fail | Catch and ignore (rare) |
| --quiet behavior change | Output reduction, improvement |
| ASK runtime behavior | Document clearly |
| real_target dirname | More correct semantics |

## Testing Requirements

| Category | Tests Required |
|----------|----------------|
| FD Leak | Test fd is closed (mock tempfile.mkstemp) |
| Quiet Mode | Test --yes + --quiet shows no extra output |
| ASK Runtime | Test runtime conflict skips with warning |
| Directory Creation | Test symlink scenario uses real path |
| Regression | All existing tests pass |

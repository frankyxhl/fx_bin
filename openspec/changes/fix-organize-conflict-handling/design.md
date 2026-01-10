# Design: Fix Organize Conflict Handling

## Context

Code review identified critical bugs in `fx organize` command's conflict handling:

1. **RENAME mode overwrites instead of renaming** on disk conflicts
2. **ASK mode is not implemented** (treated as SKIP)
3. **OVERWRITE mode lacks atomic semantics** and EXDEV handling
4. **--quiet mode doesn't show summary** when no errors
5. **Cross-device paths crash** with ValueError

## Goals / Non-Goals

**Goals:**
- Fix RENAME mode to actually rename on disk conflicts (prevent data loss)
- Decide ASK mode implementation or removal
- Implement atomic OVERWRITE with os.replace() and EXDEV handling
- Fix --quiet to match help text ("errors and summary only")
- Handle ValueError for cross-device paths

**Non-Goals:**
- Changing intra-run conflict resolution (already working correctly)
- Modifying plan generation logic
- Changing CLI argument structure

## Decisions

### Decision 1: RENAME Mode - Add New Helper for Disk Conflicts

**Current Behavior:**
```python
else:  # RENAME
    # Rename: add suffix to avoid conflict
    # This should be handled by the caller (generate_organize_plan)
    # If we get here with RENAME and target exists, it's a bug
    pass  # BUG: Falls through to shutil.move() which overwrites!
```

**Note:** The existing `resolve_conflict_rename(target_path, allocated_paths)` function handles intra-run conflicts (pure function, checks allocated_paths set). Disk conflicts require checking the filesystem.

**Fix:**
```python
# New helper function in organize_functional.py:
def resolve_disk_conflict_rename(target_path: str) -> str:
    """Resolve disk conflict by adding incrementing suffix.

    Checks filesystem for existing files and returns unique path.
    Uses get_base_name() and get_multi_ext() from common.py to handle
    multi-part extensions correctly (.tar.gz, etc.), matching the
    behavior of resolve_conflict_rename() for intra-run conflicts.
    """
    from .common import get_base_name, get_multi_ext

    base_name = get_base_name(target_path)
    extension = get_multi_ext(target_path)
    counter = 1
    while os.path.exists(target_path):
        target_path = f"{base_name}_{counter}{extension}"
        counter += 1
    return target_path

# In move_file_safe():
else:  # RENAME
    # Call disk-specific conflict resolution
    real_target = resolve_disk_conflict_rename(real_target)
```

**Why:**
- Existing `resolve_conflict_rename()` is for intra-run conflicts (pure, uses allocated_paths set)
- Disk conflicts need filesystem checks (IO operation via os.path.exists)
- Separate helper keeps concerns clear and testable
- **Reuses get_base_name()/get_multi_ext()** for consistent multi-part extension handling (.tar.gz → .tar_1.gz, not .tar.gz_1)

### Decision 2: ASK Mode - Implement in CLI Layer

**Options:**
- A) Implement click.prompt() in move_file_safe()
- B) Implement click.prompt() in CLI layer after plan execution
- C) Remove ASK from options

**Decision:** Option B - Implement in CLI layer

**Why:**
- move_file_safe() is a low-level IO function (no UI)
- CLI layer already handles other user interactions (confirmation prompt)
- Non-interactive scenarios (pipelines) need graceful fallback

**Implementation:**
```python
# In CLI, after plan execution but before execute_organize():
if any_conflicts and context.conflict_mode == ConflictMode.ASK:
    for item in conflicts:
        if not click.confirm(f"Overwrite {item.target}?"):
            # Skip this file
            plan.remove(item)
```

**Fallback:** If stdin is not a TTY, treat ASK as SKIP (same as confirmation behavior).

### Decision 3: OVERWRITE Mode with os.replace()

**Current Behavior:**
```python
elif conflict_mode == ConflictMode.OVERWRITE:
    # Overwrite: use atomic replace (will be done below)
    pass  # BUG: Falls through to shutil.move() which is NOT atomic
```

**Fix:**
```python
elif conflict_mode == ConflictMode.OVERWRITE:
    # Use os.replace() for atomic overwrite
    try:
        os.replace(real_source, real_target)
        return IOResult.from_value((None, dir_created))
    except OSError as e:
        if e.errno == errno.EXDEV:
            # Cross-device: copy to temp, then atomic replace
            import tempfile
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(real_target))
            try:
                shutil.copy2(real_source, temp_path)
                os.replace(temp_path, real_target)
                os.unlink(real_source)
                return IOResult.from_value((None, dir_created))
            finally:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
        raise
```

**Why:** os.replace() is atomic on POSIX systems (guaranteed to either succeed completely or fail without corrupting the target).

### Decision 4: --quiet Always Shows Summary

**Current Behavior:**
```python
if not quiet or summary.errors > 0:
    # Show summary
```

**Fix:**
```python
# Always show summary in quiet mode (help says "errors and summary only")
if not quiet:
    # Verbose mode: show per-file details
    ...
# Always show summary
click.echo(f"\nSummary: ...")
```

**Why:** Help text says "errors and summary only" for quiet mode, implying summary should ALWAYS be shown.

### Decision 5: Handle ValueError for Cross-Device Paths

**Current Code:**
```python
def _should_skip_entry(entry_path: str, output_dir: str) -> bool:
    return (
        bool(output_dir) and os.path.commonpath([entry_path, output_dir]) == output_dir
    )
```

**Fix:**
```python
def _should_skip_entry(entry_path: str, output_dir: str) -> bool:
    if not output_dir:
        return False
    try:
        return os.path.commonpath([entry_path, output_dir]) == output_dir
    except ValueError:
        # Paths on different drives (Windows) or otherwise incompatible
        return False  # Don't skip, let boundary check handle it
```

**Why:** os.path.commonpath() raises ValueError on Windows when paths are on different drives (e.g., C:\ vs D:\).

## Data Flow

```
User runs: fx organize /source --output /output --on-conflict rename

1. CLI parses arguments → OrganizeContext(conflict_mode=RENAME)
2. execute_organize() calls move_file_safe()
3. move_file_safe() detects disk conflict:
   - CHECK: Does target exist on disk?
   - YES: Apply conflict_mode strategy
     - RENAME: Call resolve_conflict_rename() for unique path
     - OVERWRITE: Use os.replace() atomic
     - ASK: (Handled in CLI layer)
     - SKIP: Return success without moving
4. Move or skip file
5. Return result with status
```

## Error Handling

| Error Type | Current | Fixed |
|------------|---------|-------|
| Disk conflict + RENAME | Overwrites! | Adds _1 suffix |
| Disk conflict + OVERWRITE | Non-atomic | os.replace() atomic |
| Cross-device copy | Crashes | EXDEV handling |
| Cross-device output check | Crashes | ValueError → False |
| ASK mode | Silent SKIP | Prompt or fallback |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| RENAME behavior change | Current is bug (data loss risk) |
| ASK implementation complexity | Fallback to SKIP for non-TTY |
| os.replace() availability | Python 3.3+ (project uses 3.11+) |
| Test coverage gaps | Add comprehensive tests |

## Testing Requirements

| Category | Tests Required |
|----------|----------------|
| Conflict | RENAME disk conflict adds suffix |
| Conflict | OVERWRITE is atomic |
| Conflict | OVERWRITE handles EXDEV |
| Conflict | ASK prompts user (or removed) |
| Output | --quiet always shows summary |
| Robustness | Cross-device paths don't crash |
| Regression | All existing tests pass |

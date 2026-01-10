# Design: Add Organize Command

## Context

The `fx organize` command organizes files into date-based directory hierarchies. This requires:
- Reading file metadata (creation/modification times)
- Creating directory structures
- Moving files safely with conflict handling
- Supporting dry-run preview mode

The design follows existing fx-bin patterns established in `replace.py`/`replace_functional.py`.

## Goals / Non-Goals

**Goals:**
- Provide safe, atomic file organization operations
- Support multiple date sources with graceful fallback
- Enable flexible directory depth configuration
- Handle filename conflicts gracefully (including intra-run collisions)
- Provide clear progress feedback and statistics
- Prevent security issues (symlink attacks, path traversal)

**Non-Goals:**
- EXIF metadata extraction (out of scope for v1)
- Undo/rollback functionality
- Watch mode / continuous monitoring
- Database-backed file tracking
- Windows hidden file attribute handling (v1 uses Unix `.` prefix only)

## Decisions

### Decision 1: Dual-Module Architecture
- **What:** Separate `organize.py` (pure functions + module-specific types) from `organize_functional.py` (IO operations)
- **Why:** Follows existing pattern (replace/replace_functional), enables thorough unit testing of pure logic
- **Types Location:** All organize-specific types (DateSource, ConflictMode, OrganizeContext, etc.) defined in `organize.py`, NOT in shared_types.py

### Decision 2: Creation Time Semantics (CRITICAL)
- **What:** `created` date source means:
  1. Use `st_birthtime` if available (macOS, some BSDs)
  2. Fall back to `st_mtime` if birthtime unavailable (most Linux filesystems)
  3. **NEVER use `st_ctime`** - on Unix this is inode change time, not creation time
- **Why:** Accurate original file dates for photo management; mtime is better fallback than ctime
- **Implementation:** Check `hasattr(stat_result, 'st_birthtime')` before access
- **User notification:** Log warning when falling back to mtime

### Decision 3: Immutable Dataclasses for Configuration
- **What:** Use `@dataclass(frozen=True)` for `OrganizeContext`, `FileOrganizeResult`, `OrganizeSummary`
- **Why:** Follows project convention, enables safe concurrent operations, prevents accidental mutation
- **Location:** Define in `fx_bin/organize.py`, NOT in shared_types.py (module-specific types)

### Decision 4: Confirmation Before Execution
- **What:** Default requires user confirmation before moving files, skippable with `-y/--yes`
- **Why:** File organization is destructive; users should review before execution
- **Non-interactive handling:** If stdin is not a TTY, treat as `--yes` (auto-confirm)

### Decision 5: Directory Depth via Integer
- **What:** `--depth 1|2|3` instead of named presets
- **Why:** Simpler, more intuitive than `--structure year-month-day`
- **Mapping:**
  - `--depth 3`: `2026/202601/20260110/` (default)
  - `--depth 2`: `2026/20260110/`
  - `--depth 1`: `20260110/`

### Decision 6: Symlink and Boundary Safety (CRITICAL)
- **What:** Adopt project's existing security primitives:
  1. `follow_symlinks=False` for all stat/scandir operations
  2. Inode-based cycle detection (reuse `FolderContext.visited_inodes` pattern)
  3. `os.path.commonpath()` for boundary check (NOT startswith)
  4. Skip symlink files entirely (don't follow, don't move)
  5. Maximum recursion depth: 100 (reuse `FolderContext.max_depth`)
- **Why:** Prevent path traversal attacks and infinite loops in recursive mode
- **Reference:** See `fx_bin/replace_functional.py:validate_file_access()` for correct boundary check pattern

### Decision 7: Intra-Run Collision Handling (CRITICAL)
- **What:** Conflicts are resolved deterministically at plan generation time, not execution time
- **Algorithm:**
  1. Sort source files by path (deterministic order)
  2. Track allocated target paths in a set during plan generation
  3. When target path already allocated:
     - If conflict mode is rename: apply rename to get unique path
     - If conflict mode is skip: skip the file
     - If conflict mode is ask/overwrite: use rename (ask/overwrite only for disk conflicts)
  4. Result: Plan contains final, unique target paths before any IO
- **Why:** Prevents race conditions, enables accurate dry-run preview, deterministic behavior

### Decision 8: Atomic Overwrite Semantics (CRITICAL)
- **What:** "Overwrite" mode uses `os.replace()` for atomic replacement
- **Cross-filesystem handling:**
  1. Attempt `os.replace()` first
  2. On EXDEV error: copy to temp file in target dir, then `os.replace()` temp over target
  3. Only delete source after successful replace
- **Failure behavior:** If overwrite fails, file is skipped and error logged (unless --fail-fast)

### Decision 9: Three-Phase Execution Model
- **What:** Strict separation of phases:
  1. **Scan Phase:** Collect files, read dates (IO)
  2. **Plan Phase:** Generate target paths, resolve all conflicts (Pure)
  3. **Execute Phase:** Perform moves (IO) - skipped in dry-run
- **Why:** Enables accurate dry-run, testable pure logic, clear error boundaries
- **Dry-run guarantee:** Scan and Plan phases MUST NOT create directories or modify files

### Decision 10: Output Directory Protection
- **What:** If output directory is inside source tree, exclude it from scanning
- **Implementation:** Use `os.path.commonpath([realpath(source), realpath(output)])` to safely determine containment (NOT startswith which fails for `/a/b` vs `/a/b2`)
- **Why:** Prevent re-scanning organized files in subsequent runs or recursive mode

### Decision 11: Filter Semantics
- **What:**
  - Pattern type: Shell glob using `fnmatch.fnmatchcase()` (case-sensitive)
  - Match target: Basename only, not full path
  - Option style: Repeatable (`--include "*.jpg" --include "*.png"`)
  - Evaluation order: Include first, then exclude from included set
- **Why:** Aligns with existing `fx_bin/find_files.py` which uses `fnmatchcase`, consistent behavior across tools
- **Note:** Avoid platform-dependent case sensitivity assumptions; fnmatchcase is always case-sensitive

### Decision 12: Timezone Handling
- **What:** Use local timezone for date bucketing
- **Why:** Users expect photos from "January 10th" to land in 20260110 based on their local time
- **Testing:** Include tests with explicit timezone fixtures

### Decision 13: No-op Handling
- **What:** Files already in correct target directory are skipped (not moved to same location)
- **Why:** Idempotent behavior, avoids unnecessary IO

### Decision 14: Empty Directory Cleanup Scope
- **What:** `--clean-empty` only removes directories under the original source root
- **Why:** Prevent accidentally deleting unrelated empty directories

### Decision 15: Reuse Existing Utilities
- **What:** Reuse existing project utilities for multi-part extension handling:
  - `fx_bin/common.py:get_multi_ext()` - extract multi-part extensions (.tar.gz, .tar.bz2)
  - `fx_bin/common.py:get_base_name()` - get filename without multi-part extension
- **Why:** Avoid duplicate implementation, ensure consistent behavior with backup command

## Data Flow

```
User Input
    |
    v
[CLI Layer] - Parse arguments, create OrganizeContext
    |
    v
=== SCAN PHASE (IO, read-only) ===
    |
[scan_files()] - Collect file paths based on filters
    |           - Skip symlinks, apply boundary checks
    |           - Exclude output directory if inside source
    |           - Enforce max_depth=100
    |
[get_file_date()] - Extract date for each file
    |             - birthtime -> mtime fallback
    |
    v
=== PLAN PHASE (Pure, no IO) ===
    |
[generate_organize_plan()] - Compute target paths
    |                      - Resolve ALL conflicts (including intra-run)
    |                      - Deterministic ordering
    |
    v
[Display Preview / Confirm]
    |
    v (skip if dry-run)
=== EXECUTE PHASE (IO, writes) ===
    |
[move_file_safe()] - Create dirs, execute moves
    |              - Atomic overwrites with os.replace()
    |
[remove_empty_dirs()] - Optional cleanup (scoped to source root)
    |
    v
[OrganizeSummary] - Return statistics
```

## Error Handling

| Error Type | Handling |
|------------|----------|
| Date unavailable (no birthtime) | Fall back to mtime, log warning |
| Permission denied | Log error, continue (unless --fail-fast) |
| Disk full | Abort with clear message |
| Target conflict (existing file) | Apply configured strategy |
| Intra-run conflict (same target) | Resolve at plan time with rename/skip |
| Cross-filesystem move | Atomic copy+replace pattern |
| Symlink encountered | Skip with warning |
| Path traversal attempt | Skip with security warning |
| Recursion depth exceeded | Skip with warning |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Accidental file moves | Default confirmation prompt + dry-run mode |
| Creation time unavailable on Linux | Automatic fallback to mtime with warning |
| Large file counts slow | Progress indicators, deterministic ordering |
| Conflicting filenames | Multiple resolution strategies, intra-run handling |
| Symlink attacks | follow_symlinks=False, boundary checks |
| Output inside source | Automatic exclusion using commonpath |
| Deep recursion DoS | max_depth=100 limit |

## Testing Requirements

| Category | Tests Required |
|----------|----------------|
| Security | Symlink directory traversal, path boundary checks, commonpath vs startswith |
| Cross-platform | Birthtime fallback, timezone handling |
| Atomicity | Cross-filesystem overwrite, crash safety |
| Conflicts | Intra-run collision (all modes), disk conflicts |
| Edge cases | Empty directory, special characters, long paths, depth limit |

## Open Questions

None - requirements fully specified during brainstorming session and code review.

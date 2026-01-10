# organize Specification

## Purpose
TBD - created by archiving change add-organize-command. Update Purpose after archive.
## Requirements
### Requirement: Date-Based File Organization
The system SHALL organize files into hierarchical date-based directories based on file timestamps using local timezone.

#### Scenario: Organize with default settings (depth 3)
- **WHEN** user runs `fx organize` in a directory with files
- **THEN** files are moved to `YYYY/YYYYMM/YYYYMMDD/` structure based on creation date
- **AND** original files are removed from source location

#### Scenario: Organize with depth 2
- **WHEN** user runs `fx organize --depth 2`
- **THEN** files are moved to `YYYY/YYYYMMDD/` structure

#### Scenario: Organize with depth 1
- **WHEN** user runs `fx organize --depth 1`
- **THEN** files are moved to `YYYYMMDD/` structure

#### Scenario: Organize to custom output directory
- **WHEN** user runs `fx organize --output /path/to/organized`
- **THEN** date directories are created in the specified output directory
- **AND** files are moved to the output directory structure

#### Scenario: Date bucketing uses local timezone
- **WHEN** a file has timestamp 2026-01-10T23:30:00 in local timezone
- **THEN** it is placed in `2026/202601/20260110/` based on local time
- **AND** NOT in `20260111/` even if UTC date differs

### Requirement: Date Source Selection with Correct Semantics
The system SHALL use st_birthtime for creation time, falling back to st_mtime. The system SHALL NEVER use st_ctime as creation time.

#### Scenario: Use creation time (default) on macOS
- **WHEN** user runs `fx organize` without --date-source on macOS
- **THEN** file creation time (st_birthtime) is used for date calculation

#### Scenario: Use modification time
- **WHEN** user runs `fx organize --date-source modified`
- **THEN** file modification time (st_mtime) is used for date calculation

#### Scenario: Fallback when creation time unavailable
- **WHEN** file system does not support st_birthtime (e.g., ext4 on Linux)
- **THEN** system automatically falls back to st_mtime
- **AND** a warning is logged indicating fallback occurred

#### Scenario: Never use ctime as creation time
- **WHEN** st_birthtime is unavailable
- **THEN** system uses st_mtime for fallback
- **AND** system does NOT use st_ctime (which is inode change time on Unix)

### Requirement: Dry-Run Purity
The system SHALL NOT create, modify, or delete any files or directories in dry-run mode.

#### Scenario: Preview with dry-run
- **WHEN** user runs `fx organize --dry-run`
- **THEN** planned moves are displayed
- **AND** no files are actually moved
- **AND** no directories are created
- **AND** no makedirs() calls are executed

#### Scenario: Verbose dry-run
- **WHEN** user runs `fx organize --dry-run --verbose`
- **THEN** source and target paths are shown for each file
- **AND** filesystem remains completely unchanged

### Requirement: File Conflict Resolution with Intra-Run Handling
The system SHALL handle filename conflicts with configurable strategies. Intra-run conflicts (multiple source files mapping to same target) are always resolved deterministically at plan time using rename or skip, regardless of --on-conflict mode.

#### Scenario: Rename on conflict with existing file (default)
- **WHEN** target file already exists on disk
- **AND** conflict mode is rename (default)
- **THEN** file is renamed with numeric suffix (e.g., `photo_1.jpg`, `photo_2.jpg`)

#### Scenario: Intra-run collision with rename mode
- **WHEN** two source files `a/photo.jpg` and `b/photo.jpg` have the same date
- **AND** both would be organized to the same target path
- **THEN** conflicts are resolved at plan generation time
- **AND** second file is renamed to `photo_1.jpg` before execution begins

#### Scenario: Intra-run collision with skip mode
- **WHEN** two source files map to the same target path
- **AND** conflict mode is skip
- **THEN** second file is skipped at plan time
- **AND** skip is recorded in statistics

#### Scenario: Intra-run collision with ask or overwrite mode
- **WHEN** two source files map to the same target path
- **AND** conflict mode is ask or overwrite
- **THEN** intra-run conflict is still resolved at plan time using rename strategy
- **AND** ask/overwrite mode only applies to conflicts with files already on disk

#### Scenario: Skip on conflict with existing file
- **WHEN** user runs `fx organize --on-conflict skip`
- **AND** target file already exists on disk
- **THEN** file is skipped
- **AND** skip is recorded in statistics

#### Scenario: Overwrite on conflict with atomic semantics
- **WHEN** user runs `fx organize --on-conflict overwrite`
- **AND** target file already exists on disk
- **THEN** target file is atomically replaced using os.replace()
- **AND** on cross-filesystem: temp copy then atomic replace

#### Scenario: Ask on conflict with existing disk file
- **WHEN** user runs `fx organize --on-conflict ask`
- **AND** target file already exists on disk
- **THEN** user is prompted to choose action for that specific conflict

### Requirement: Symlink and Security Safety
The system SHALL skip symlinks and enforce path boundaries to prevent security vulnerabilities.

#### Scenario: Skip symlink files
- **WHEN** a file in source directory is a symbolic link
- **THEN** the symlink is skipped
- **AND** a warning is logged

#### Scenario: Skip symlink directories in recursive mode
- **WHEN** user runs `fx organize --recursive`
- **AND** a subdirectory is a symbolic link
- **THEN** the symlink directory is NOT followed
- **AND** processing continues with regular directories

#### Scenario: Prevent path traversal attack
- **WHEN** a symlink points outside the source directory
- **AND** recursive processing is enabled
- **THEN** the symlink is skipped
- **AND** a security warning is logged

#### Scenario: Boundary check on file operations
- **WHEN** any file operation would affect a path outside source/output boundaries
- **THEN** the operation is blocked
- **AND** an error is logged

### Requirement: Output Directory Protection
The system SHALL exclude output directory from scanning when it is inside source tree using os.path.commonpath for safe comparison.

#### Scenario: Output inside source tree
- **WHEN** user runs `fx organize --output ./organized` in current directory
- **AND** `./organized/` is created during first run
- **THEN** files in `./organized/` are NOT re-scanned in subsequent runs

#### Scenario: Recursive with output inside source
- **WHEN** user runs `fx organize --recursive --output ./dated`
- **THEN** the `./dated/` directory and its contents are excluded from processing

#### Scenario: Similar prefix paths are not confused
- **WHEN** source is `/a/b` and output is `/a/b2`
- **THEN** `/a/b2` is NOT incorrectly treated as inside `/a/b`
- **AND** output directory exclusion is NOT triggered for `/a/b2`

### Requirement: No-op Handling
The system SHALL skip files that are already in their correct target location.

#### Scenario: File already organized
- **WHEN** a file is already located at its correct date-based path
- **THEN** the file is skipped (not moved to same location)
- **AND** skip is NOT counted as an error

#### Scenario: Idempotent operation
- **WHEN** user runs `fx organize` twice on same directory
- **THEN** second run reports no files to move
- **AND** previously organized files remain unchanged

### Requirement: File Filtering with Repeatable Options
The system SHALL support filtering files using repeatable --include and --exclude options with fnmatchcase (case-sensitive) glob patterns matching basename only.

#### Scenario: Include specific extensions with repeatable option
- **WHEN** user runs `fx organize --include "*.jpg" --include "*.png"`
- **THEN** only files matching any of the patterns are processed

#### Scenario: Exclude specific patterns with repeatable option
- **WHEN** user runs `fx organize --exclude "*.tmp" --exclude ".DS_Store"`
- **THEN** matching files are excluded from processing

#### Scenario: Combine include and exclude
- **WHEN** user uses both --include and --exclude
- **THEN** include is applied first, then exclude filters from included set

#### Scenario: Pattern matches basename only with case sensitivity
- **WHEN** user runs `fx organize --include "*.JPG"`
- **AND** file is at `photos/vacation/beach.jpg`
- **THEN** file does NOT match because pattern is case-sensitive

### Requirement: Hidden File Handling
The system SHALL handle hidden files (files starting with `.`) with configurable behavior.

#### Scenario: Ignore hidden files by default
- **WHEN** user runs `fx organize` without --hidden flag
- **THEN** files starting with `.` are not processed

#### Scenario: Include hidden files
- **WHEN** user runs `fx organize --hidden`
- **THEN** hidden files are processed like regular files

### Requirement: Recursive Processing with Depth Limit and Cycle Detection
The system SHALL support recursive directory traversal with maximum depth limit (100) and protection against infinite loops.

#### Scenario: Non-recursive by default
- **WHEN** user runs `fx organize` without --recursive flag
- **THEN** only files in the current directory are processed
- **AND** subdirectories are not traversed

#### Scenario: Recursive processing
- **WHEN** user runs `fx organize --recursive`
- **THEN** all files in subdirectories are also processed

#### Scenario: Maximum recursion depth enforced
- **WHEN** recursive processing exceeds 100 levels deep
- **THEN** directories beyond depth 100 are skipped
- **AND** a warning is logged

#### Scenario: Cycle detection via inode
- **WHEN** recursive processing encounters a directory already visited (same inode)
- **THEN** the duplicate is skipped
- **AND** processing continues without infinite loop

### Requirement: Confirmation Prompt with Non-Interactive Support
The system SHALL require confirmation before executing file moves. When stdin is not a TTY, the system treats it as if --yes was specified.

#### Scenario: Confirm before execution
- **WHEN** user runs `fx organize` (not dry-run)
- **AND** stdin is a TTY
- **THEN** a summary is displayed with file count
- **AND** user is prompted to confirm before proceeding

#### Scenario: Skip confirmation with --yes
- **WHEN** user runs `fx organize --yes`
- **THEN** execution proceeds without confirmation prompt

#### Scenario: Non-interactive stdin auto-confirms
- **WHEN** stdin is not a TTY (piped input)
- **AND** --yes is not specified
- **THEN** command proceeds as if --yes was specified

### Requirement: Empty Directory Cleanup with Scope Limits
The system SHALL optionally remove empty directories, scoped to source root only.

#### Scenario: Keep empty directories by default
- **WHEN** user runs `fx organize` without --clean-empty
- **THEN** source directories are left as-is even if empty

#### Scenario: Remove empty directories under source root
- **WHEN** user runs `fx organize --clean-empty`
- **THEN** empty directories under source root are removed after file moves
- **AND** directories outside source root are NOT removed

#### Scenario: Nested empty directory cleanup
- **WHEN** moving files creates nested empty directories
- **AND** --clean-empty is specified
- **THEN** empty directories are removed bottom-up

### Requirement: Error Handling
The system SHALL handle errors gracefully with configurable behavior.

#### Scenario: Continue on error (default)
- **WHEN** an error occurs during file move
- **THEN** error is logged
- **AND** processing continues with remaining files

#### Scenario: Fail fast on error
- **WHEN** user runs `fx organize --fail-fast`
- **AND** an error occurs
- **THEN** processing stops immediately
- **AND** completed moves are preserved

#### Scenario: Permission error
- **WHEN** user lacks permission to move a file
- **THEN** descriptive error message is displayed
- **AND** error count is included in summary

#### Scenario: Cross-filesystem move error recovery
- **WHEN** move fails with EXDEV (cross-device link)
- **THEN** system attempts copy+replace pattern
- **AND** source is deleted only after successful copy

### Requirement: Progress and Statistics
The system SHALL display progress and provide completion statistics.

#### Scenario: Simple progress (default)
- **WHEN** user runs `fx organize` (not quiet mode)
- **THEN** current file being processed is shown

#### Scenario: Verbose output
- **WHEN** user runs `fx organize --verbose`
- **THEN** source path, target path, and status are shown for each file

#### Scenario: Quiet mode
- **WHEN** user runs `fx organize --quiet`
- **THEN** only errors and final summary are displayed

#### Scenario: Completion statistics
- **WHEN** organization completes
- **THEN** summary shows: files moved, files skipped, errors, directories created

#### Scenario: Deterministic output order
- **WHEN** processing multiple files
- **THEN** output is sorted by source path for reproducible results


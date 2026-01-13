"""Functional IO operations for file organization using returns library.

This module provides safe file organization operations with functional
error handling using the returns library.

Error Hierarchy:
    FileOperationError (base for all file operations)
    ├── OrganizeError (organization-specific errors)
        ├── DateReadError (file date reading errors)
        └── MoveError (file move errors)
"""

import errno
import os
import shutil
import tempfile
from datetime import datetime
from typing import List, Set, Tuple, cast

from loguru import logger as L
from returns.io import IOResult

from fx_bin.errors import DateReadError, MoveError, OrganizeError
from fx_bin.lib import unsafe_ioresult_unwrap
from fx_bin.organize import (
    ConflictMode,
    DateSource,
    FileOrganizeResult,
    OrganizeContext,
    OrganizeSummary,
    generate_organize_plan,
)
from fx_bin.shared_types import FolderContext


def get_file_date(
    file_path: str, date_source: DateSource
) -> IOResult[datetime, DateReadError]:
    """Get file date based on date_source setting.

    Uses st_birthtime with st_mtime fallback. NEVER uses st_ctime.
    Returns IOResult for functional error handling.

    Args:
        file_path: Path to the file
        date_source: Which timestamp to use (CREATED or MODIFIED)

    Returns:
        IOResult with datetime or DateReadError

    Examples:
        >>> result = get_file_date("/path/to/file.jpg", DateSource.CREATED)
        >>> isinstance(result, IOResult)
        True
    """
    try:
        stat_info = os.stat(file_path)

        if date_source == DateSource.MODIFIED:
            # Use mtime directly for modified mode
            return IOResult.from_value(datetime.fromtimestamp(stat_info.st_mtime))

        # CREATED mode: try birthtime first, fallback to mtime
        if hasattr(stat_info, "st_birthtime"):
            birthtime = getattr(stat_info, "st_birthtime", 0)
            if birthtime > 0:  # Valid birthtime
                return IOResult.from_value(datetime.fromtimestamp(birthtime))
            else:
                # birthtime is 0 (invalid), fall back to mtime
                L.warning(f"File {file_path} has invalid birthtime (0), using mtime")
                return IOResult.from_value(datetime.fromtimestamp(stat_info.st_mtime))
        else:
            # Platform doesn't support birthtime, use mtime
            L.debug(
                f"Platform doesn't support st_birthtime for {file_path}, using mtime"
            )
            return IOResult.from_value(datetime.fromtimestamp(stat_info.st_mtime))

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            DateReadError(f"Cannot read file date for {file_path}: {e}")
        )


def resolve_disk_conflict_rename(target_path: str) -> str:
    """Resolve disk conflict by adding incrementing suffix.

    Checks filesystem for existing files and returns unique path.
    Uses get_base_name() and get_multi_ext() from common.py to handle
    multi-part extensions correctly (.tar.gz, etc.), matching the
    behavior of resolve_conflict_rename() for intra-run conflicts.

    Args:
        target_path: The target path that may conflict with existing files

    Returns:
        A unique path with incrementing suffix (_1, _2, etc.) if conflict exists,
        or the original path if no conflict

    Examples:
        >>> # When /output/photo.jpg already exists:
        >>> resolve_disk_conflict_rename("/output/photo.jpg")
        '/output/photo_1.jpg'
        >>> # When both .tar and .tar.gz exist:
        >>> resolve_disk_conflict_rename("/output/archive.tar.gz")
        '/output/archive_1.tar.gz'
    """
    from fx_bin.common import get_base_name, get_multi_ext

    # If no conflict, return original path
    if not os.path.exists(target_path):
        return target_path

    # Extract directory, base name, and extension
    dirname = os.path.dirname(target_path)
    filename = os.path.basename(target_path)

    base = get_base_name(filename)
    ext = get_multi_ext(filename)

    # Find the next available suffix by checking filesystem
    counter = 1
    while True:
        new_filename = f"{base}_{counter}{ext}"
        new_path = os.path.join(dirname, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def _should_skip_entry(entry_path: str, output_dir: str) -> bool:
    """Check if entry should be skipped (output directory).

    Returns True if entry_path is within output_dir (should skip).
    Returns False if output_dir is empty or if entry is outside output_dir.

    Handles ValueError from os.path.commonpath() which occurs when:
    - Paths are on different drives (Windows: C:\\ vs D:\\)
    - Paths are completely unrelated (Unix)
    """
    if not output_dir:
        return False
    try:
        return os.path.commonpath([entry_path, output_dir]) == output_dir
    except ValueError:
        # Paths on different drives (Windows) or otherwise incompatible
        return False  # Don't skip, let boundary check handle it


def _process_entry(
    entry: os.DirEntry, dir_path: str, output_dir: str, follow_symlinks: bool
) -> List[str]:
    """Process a single scandir entry for file collection.

    Returns list of file paths (empty for directories, which are handled separately).
    """
    files: List[str] = []
    entry_path = os.path.join(dir_path, entry.name)

    if _should_skip_entry(entry_path, output_dir):
        return files

    if entry.is_symlink():
        if follow_symlinks:
            target = os.path.realpath(entry_path)
            if os.path.isfile(target):
                files.append(entry_path)
        return files

    if entry.is_file():
        files.append(entry_path)

    return files


def scan_files(
    start_dir: str,
    recursive: bool = True,
    follow_symlinks: bool = False,
    max_depth: int = 100,
    output_dir: str = "",
    context: FolderContext | None = None,
) -> IOResult[List[str], OrganizeError]:
    """Scan directory for files to organize.

    Pure scanning logic with symlink handling and cycle detection.
    Returns IOResult for functional error handling.

    Args:
        start_dir: Directory to scan
        recursive: Whether to scan recursively
        follow_symlinks: Whether to follow symbolic links
        max_depth: Maximum recursion depth (default 100)
        output_dir: Output directory to exclude from scanning
        context: FolderContext for cycle detection (created if None)

    Returns:
        IOResult with list of file paths or OrganizeError
    """
    if context is None:
        context = FolderContext(visited_inodes=set(), max_depth=max_depth)

    try:
        files: List[str] = []
        start_dir_real = os.path.realpath(start_dir)
        output_dir_real = os.path.realpath(output_dir) if output_dir else ""

        if recursive:
            files.extend(
                _scan_recursive(
                    start_dir_real,
                    0,
                    max_depth,
                    output_dir_real,
                    context.visited_inodes,
                    follow_symlinks,
                )
            )
        else:
            files.extend(
                _scan_non_recursive(
                    start_dir_real,
                    output_dir_real,
                    follow_symlinks,
                )
            )

        return IOResult.from_value(files)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            OrganizeError(f"Cannot scan directory {start_dir}: {e}")
        )


def _scan_recursive(
    dir_path: str,
    depth: int,
    max_depth: int,
    output_dir: str,
    visited_inodes: Set[Tuple[int, int]],
    follow_symlinks: bool,
) -> List[str]:
    """Helper for recursive directory scanning."""
    if depth > max_depth:
        return []

    files: List[str] = []

    # First, get directory info for cycle detection
    try:
        dir_stat = os.stat(dir_path)
        dir_inode = (dir_stat.st_dev, dir_stat.st_ino)
    except (OSError, PermissionError):
        return files

    # Cycle detection
    if dir_inode in visited_inodes:
        L.debug(f"Skipping already visited directory: {dir_path}")
        return files

    visited_inodes.add(dir_inode)

    # Then, scan the directory entries
    try:
        entries = list(os.scandir(dir_path))
    except (OSError, PermissionError):
        return files

    for entry in entries:
        files.extend(
            _process_scan_entry(
                entry,
                dir_path,
                depth,
                max_depth,
                output_dir,
                visited_inodes,
                follow_symlinks,
            )
        )

    return files


def _handle_symlink_entry(
    entry_path: str,
    follow_symlinks: bool,
    depth: int,
    max_depth: int,
    output_dir: str,
    visited_inodes: Set[Tuple[int, int]],
) -> List[str]:
    """Handle symlink entry during directory scanning.

    Args:
        entry_path: Path to the symlink
        follow_symlinks: Whether to follow symbolic links
        depth: Current recursion depth
        max_depth: Maximum recursion depth
        output_dir: Output directory to skip
        visited_inodes: Set of visited directory inodes

    Returns:
        List of file paths found through this symlink
    """
    if not follow_symlinks:
        return []

    target = os.path.realpath(entry_path)
    if os.path.isdir(target):
        return _scan_recursive(
            target,
            depth + 1,
            max_depth,
            output_dir,
            visited_inodes,
            follow_symlinks,
        )
    return [entry_path]


def _handle_regular_entry(
    entry: "os.DirEntry[str]",
    entry_path: str,
    depth: int,
    max_depth: int,
    output_dir: str,
    visited_inodes: Set[Tuple[int, int]],
    follow_symlinks: bool,
) -> List[str]:
    """Handle regular (non-symlink) entry during directory scanning.

    Args:
        entry: Directory entry object
        entry_path: Full path to the entry
        depth: Current recursion depth
        max_depth: Maximum recursion depth
        output_dir: Output directory to skip
        visited_inodes: Set of visited directory inodes
        follow_symlinks: Whether to follow symbolic links

    Returns:
        List of file paths found from this entry
    """
    if entry.is_file():
        return [entry_path]
    elif entry.is_dir():
        return _scan_recursive(
            entry_path,
            depth + 1,
            max_depth,
            output_dir,
            visited_inodes,
            follow_symlinks,
        )
    return []


def _process_scan_entry(
    entry: "os.DirEntry[str]",
    dir_path: str,
    depth: int,
    max_depth: int,
    output_dir: str,
    visited_inodes: Set[Tuple[int, int]],
    follow_symlinks: bool,
) -> List[str]:
    """Process a single directory entry during recursive scanning.

    Args:
        entry: Directory entry object
        dir_path: Parent directory path
        depth: Current recursion depth
        max_depth: Maximum recursion depth
        output_dir: Output directory to skip
        visited_inodes: Set of visited directory inodes
        follow_symlinks: Whether to follow symbolic links

    Returns:
        List of file paths found from this entry
    """
    try:
        entry_path = os.path.join(dir_path, entry.name)

        # Skip output directory early
        if _should_skip_entry(entry_path, output_dir):
            L.debug(f"Skipping output directory: {entry_path}")
            return []

        # Handle symlinks - extract to reduce nesting
        if entry.is_symlink():
            return _handle_symlink_entry(
                entry_path,
                follow_symlinks,
                depth,
                max_depth,
                output_dir,
                visited_inodes,
            )

        # Handle regular entries
        return _handle_regular_entry(
            entry,
            entry_path,
            depth,
            max_depth,
            output_dir,
            visited_inodes,
            follow_symlinks,
        )

    except (OSError, PermissionError):
        return []


def _scan_non_recursive(
    dir_path: str,
    output_dir: str,
    follow_symlinks: bool,
) -> List[str]:
    """Helper for non-recursive directory scanning."""
    # First, ensure we can open the directory
    try:
        entries = list(os.scandir(dir_path))
    except (OSError, PermissionError):
        return []

    # Then process each entry, skipping any that fail
    files = []
    for entry in entries:
        try:
            files.extend(_process_entry(entry, dir_path, output_dir, follow_symlinks))
        except (OSError, PermissionError):
            continue

    return files


def _handle_cross_device_move(
    source: str, target: str, dir_created: bool
) -> IOResult[Tuple[None, bool], MoveError]:
    """Handle cross-device move using temp file for atomicity.

    When os.replace() fails with EXDEV (cross-device link), copy to temp
    file first, then atomic replace to target. This preserves atomic
    semantics even across filesystems.

    Args:
        source: Source file path
        target: Target file path
        dir_created: Whether parent directory was created

    Returns:
        IOResult with Tuple[None, dir_created] or MoveError
    """
    target_dir = os.path.dirname(target) or "."
    fd, temp_path = tempfile.mkstemp(dir=target_dir)
    os.close(fd)  # Close fd - we only need the unique filename

    try:
        shutil.copy2(source, temp_path)
        os.replace(temp_path, target)
        os.unlink(source)
        return IOResult.from_value((None, dir_created))
    except Exception as e:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        return IOResult.from_failure(
            MoveError(
                f"Cannot move {source} to {target}: cross-device link failed: {e}"
            )
        )


def _handle_disk_conflict(
    source: str, target: str, conflict_mode: ConflictMode
) -> "IOResult[Tuple[None, bool], MoveError] | None":
    """Handle disk conflict when target file exists.

    Args:
        source: Source file path
        target: Target file path
        conflict_mode: Strategy for handling the conflict

    Returns:
        - IOResult if conflict was fully handled (SKIP/OVERWRITE/ASK modes)
        - None if conflict handling should continue (RENAME mode modifies target)
    """
    match conflict_mode:
        case ConflictMode.SKIP:
            # Skip: return success but don't move (source remains)
            return IOResult.from_value((None, False))
        case ConflictMode.OVERWRITE:
            # Overwrite: use atomic replace with EXDEV handling
            try:
                os.replace(source, target)
                return IOResult.from_value((None, False))
            except OSError as e:
                if e.errno == errno.EXDEV:
                    return _handle_cross_device_move(source, target, False)
                raise
        case ConflictMode.ASK:
            # Runtime conflict: conflict appeared between scan and execution
            # ASK mode only handles scan-time conflicts, so skip with warning
            L.warning(
                f"Runtime conflict: {target} exists. "
                "Skipping (ASK mode only handles scan-time conflicts)."
            )
            return IOResult.from_value((None, False))
        case ConflictMode.RENAME:
            # Rename: add suffix to avoid conflict
            # Return None to indicate target should be renamed and move should continue
            return None


def _perform_move(
    source: str, target: str, conflict_mode: ConflictMode, dir_created: bool
) -> IOResult[Tuple[None, bool], MoveError]:
    """Perform the actual file move operation.

    Args:
        source: Source file path
        target: Target file path
        conflict_mode: Strategy for handling conflicts
        dir_created: Whether parent directory was created

    Returns:
        IOResult with Tuple[None, dir_created] or MoveError
    """
    match conflict_mode:
        case ConflictMode.OVERWRITE:
            # OVERWRITE always uses atomic replace
            try:
                os.replace(source, target)
                return IOResult.from_value((None, dir_created))
            except OSError as e:
                if e.errno == errno.EXDEV:
                    return _handle_cross_device_move(source, target, dir_created)
                raise
        case _:
            # For non-OVERWRITE modes, use shutil.move
            shutil.move(source, target)
            return IOResult.from_value((None, dir_created))


def move_file_safe(
    source: str,
    target: str,
    source_root: str,
    output_root: str,
    conflict_mode: ConflictMode,
) -> IOResult[Tuple[None, bool], MoveError]:
    """Safely move a file from source to target with boundary checks.

    Creates parent directories if needed. Handles cross-filesystem moves.
    Uses atomic overwrite to avoid data corruption.
    Enforces path boundaries to prevent path traversal attacks.
    Handles disk conflicts based on conflict_mode.

    Args:
        source: Source file path
        target: Target file path
        source_root: Root directory that source must be within
        output_root: Root directory that target must be within
        conflict_mode: Strategy for handling target file conflicts

    Returns:
        IOResult with Tuple[None, dir_created] or MoveError
        dir_created is True if a new directory was created
    """
    try:
        # Resolve real paths for boundary checking
        real_source = os.path.realpath(source)
        real_target = os.path.realpath(target)
        real_source_root = os.path.realpath(source_root)
        real_output_root = os.path.realpath(output_root)

        # Boundary check: source must be within source_root
        try:
            source_common = os.path.commonpath([real_source, real_source_root])
            if source_common != real_source_root:
                return IOResult.from_failure(
                    MoveError(
                        f"Source file {source} is outside source root {source_root}"
                    )
                )
        except ValueError:
            # Different drives on Windows - cannot determine common path
            return IOResult.from_failure(
                MoveError(f"Cannot move {source}: cross-device path from {source_root}")
            )

        # Boundary check: target must be within output_root
        # Get parent directory of target since target may not exist yet
        target_parent = os.path.dirname(real_target) or real_target
        try:
            target_common = os.path.commonpath([target_parent, real_output_root])
            if target_common != real_output_root:
                return IOResult.from_failure(
                    MoveError(
                        f"Target path {target} is outside output root {output_root}"
                    )
                )
        except ValueError:
            # Different drives on Windows
            return IOResult.from_failure(
                MoveError(
                    f"Cannot move to {target}: cross-device path to {output_root}"
                )
            )

        # Check if source and target are the same (no-op)
        if real_source == real_target:
            return IOResult.from_value((None, False))

        # Check for disk conflict (target file exists)
        if os.path.exists(real_target):
            conflict_result = _handle_disk_conflict(
                real_source, real_target, conflict_mode
            )
            if conflict_result is not None:
                # Conflict was fully handled (SKIP/OVERWRITE/ASK modes)
                return conflict_result
            # RENAME mode: conflict_result is None, rename target and continue
            real_target = resolve_disk_conflict_rename(real_target)

        # Create parent directories if needed and track if new
        dir_created = False
        target_dir = os.path.dirname(real_target)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            dir_created = True

        # Perform the move
        return _perform_move(source, real_target, conflict_mode, dir_created)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            MoveError(f"Cannot move {source} to {target}: {e}")
        )


def _try_remove_empty_dir(dirpath: str, source_root_real: str) -> bool:
    """Try to remove a single empty directory if it's within source_root.

    Args:
        dirpath: Directory path to check and potentially remove
        source_root_real: Real path of source root boundary

    Returns:
        True if directory was removed, False otherwise
    """
    # Skip if outside source root
    try:
        if os.path.commonpath([dirpath, source_root_real]) != source_root_real:
            return False
    except ValueError:
        # Paths on different drives, skip
        return False

    # Check if directory is currently empty
    # We need to check the actual filesystem state, not os.walk cache
    try:
        contents = list(os.scandir(dirpath))
        is_empty = len(contents) == 0
    except (OSError, PermissionError):
        return False

    if not is_empty:
        return False

    # Try to remove the empty directory
    try:
        os.rmdir(dirpath)
        return True
    except (OSError, PermissionError):
        # Directory might have been removed or became non-empty
        return False


def remove_empty_dirs(
    start_dir: str, source_root: str
) -> IOResult[None, OrganizeError]:
    """Remove empty directories starting from start_dir.

    Performs bottom-up recursive removal, only removing directories that
    are empty. Only removes directories within source_root boundary.

    Args:
        start_dir: Directory to start cleanup from
        source_root: Root directory boundary (don't remove above this)

    Returns:
        IOResult with None or OrganizeError
    """
    try:
        start_dir_real = os.path.realpath(start_dir)
        source_root_real = os.path.realpath(source_root)

        # Walk bottom-up (leaves first)
        # We need to repeatedly walk until no more empty dirs are found
        # because removing a dir can make its parent empty
        max_iterations = 100  # Prevent infinite loops
        for _ in range(max_iterations):
            empty_dirs_found = False

            for dirpath, dirnames, filenames in os.walk(start_dir_real, topdown=False):
                if _try_remove_empty_dir(dirpath, source_root_real):
                    empty_dirs_found = True

            if not empty_dirs_found:
                # No more empty dirs to remove
                break

        return IOResult.from_value(None)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            OrganizeError(f"Cannot cleanup directories {start_dir}: {e}")
        )


def _execute_move_with_error_handling(
    move_result: IOResult[Tuple[None, bool], MoveError],
    item: "FileOrganizeResult",
    fail_fast: bool,
) -> "IOResult[None, OrganizeError] | Tuple[int, int, int]":
    """Handle move result with error checking.

    Args:
        move_result: Result from move_file_safe
        item: File organize result item (for error messages)
        fail_fast: Whether to stop on first error

    Returns:
        - IOResult error if move failed and fail_fast is True
        - Tuple of (processed_delta, errors_delta, dir_created_delta) if move
          succeeded or failed with fail_fast=False:
          - Success: (1, 0, 1) or (1, 0, 0) depending on whether directory was
            created
          - Failure (non-fail-fast): (0, 1, 0) to indicate errors should be
            incremented (processed is unchanged)
    """
    try:
        _, dir_created = unsafe_ioresult_unwrap(move_result)
        return (1, 0, 1 if dir_created else 0)
    except Exception as e:
        if fail_fast:
            return IOResult.from_failure(
                OrganizeError(f"Failed to move {item.source} to {item.target}: {e}")
            )
        # Non-fail-fast: return deltas to increment errors (processed unchanged)
        return (0, 1, 0)


def _read_file_dates(
    files: "list[str]", context: OrganizeContext
) -> "dict[str, datetime] | tuple[None, str]":
    """Read file dates for all files, respecting fail_fast setting.

    Args:
        files: List of file paths to read dates for
        context: Organization context with date_source and fail_fast settings

    Returns:
        dict mapping file paths to their dates, or (None, error_message) if
        fail_fast error occurred
    """
    dates: "dict[str, datetime]" = {}
    for file_path in files:
        date_result = get_file_date(file_path, context.date_source)
        try:
            dates[file_path] = unsafe_ioresult_unwrap(date_result)
        except Exception as e:
            if context.fail_fast:
                # Signal fail_fast error to caller with specific error message
                return (None, f"Failed to read date for {file_path}: {e}")
    return dates


def _execute_moved_item(
    item: "FileOrganizeResult",
    source_dir: str,
    context: OrganizeContext,
) -> "IOResult[None, OrganizeError] | Tuple[int, int, int]":
    """Execute a single 'moved' action from the plan.

    Args:
        item: File organize result with action='moved'
        source_dir: Source directory root
        context: Organization context

    Returns:
        - IOResult error if move failed and fail_fast is True
        - Tuple of (processed_delta, errors_delta, dir_created_delta) otherwise
    """
    if context.dry_run:
        return (1, 0, 0)  # Dry run still counts as "processed"

    # Runtime conflicts can appear between planning and execution.
    # For SKIP/ASK conflict modes, treat an existing target as a skip.
    # This avoids counting a no-op "success" as processed.
    if context.conflict_mode in (ConflictMode.SKIP, ConflictMode.ASK):
        try:
            real_target = os.path.realpath(item.target)
        except OSError:
            real_target = item.target
        if os.path.exists(real_target):
            if context.conflict_mode == ConflictMode.ASK:
                L.warning(
                    f"Runtime conflict: {real_target} exists. "
                    "Skipping (ASK mode only handles scan-time conflicts)."
                )
            return (0, 0, 0)

    move_result = move_file_safe(
        item.source,
        item.target,
        source_dir,
        context.output_dir,
        context.conflict_mode,
    )
    exec_result = _execute_move_with_error_handling(
        move_result, item, context.fail_fast
    )
    return exec_result


def execute_organize(
    source_dir: str, context: OrganizeContext
) -> IOResult[Tuple[OrganizeSummary, List[FileOrganizeResult]], OrganizeError]:
    """Execute file organization operation.

    Main orchestration function that:
    1. Scans source directory for files
    2. Reads file dates
    3. Generates organization plan
    4. Executes moves (unless dry-run)
    5. Returns summary statistics and plan

    Args:
        source_dir: Source directory to organize
        context: Organization configuration context

    Returns:
        IOResult with Tuple[OrganizeSummary, plan] or OrganizeError
    """
    # Scan for files
    scan_result = scan_files(
        source_dir,
        recursive=context.recursive,
        follow_symlinks=False,
        max_depth=100,  # Max scan depth is always 100, independent of context.depth
        output_dir=context.output_dir,
    )

    # Try to unwrap - if it fails, convert and return error
    from .lib import unwrap_or_convert_error

    try:
        files = unwrap_or_convert_error(
            scan_result,
            OrganizeError,
            "Cannot scan source directory",
        )
    except OrganizeError as e:
        return IOResult.from_failure(e)

    # Read file dates
    dates_result = _read_file_dates(files, context)
    if isinstance(dates_result, tuple):
        # fail_fast error occurred
        _, error_msg = dates_result
        return IOResult.from_failure(OrganizeError(error_msg))
    dates = dates_result

    # Generate plan
    plan = generate_organize_plan(files, dates, context)

    # Execute plan and count results
    processed = 0
    skipped = 0
    errors = 0
    directories_created = 0

    for item in plan:
        match item.action:
            case "moved":
                exec_result = _execute_moved_item(item, source_dir, context)
                if isinstance(exec_result, IOResult):
                    # Error result - cast to expected return type
                    errors += 1
                    return cast(
                        "IOResult["
                        "Tuple[OrganizeSummary, List[FileOrganizeResult]], "
                        "OrganizeError"
                        "]",
                        exec_result,
                    )
                # Success or non-fail-fast error: unpack the tuple
                proc_delta, err_delta, dir_delta = exec_result
                processed += proc_delta
                errors += err_delta
                directories_created += dir_delta
                if proc_delta == 0 and err_delta == 0:
                    # Runtime skip (e.g., disk conflict in SKIP/ASK mode)
                    skipped += 1
            case "skipped":
                skipped += 1
            case "error":
                errors += 1
                if context.fail_fast:
                    return IOResult.from_failure(
                        OrganizeError(
                            f"Planning error for {item.source}: cannot organize file"
                        )
                    )

    summary = OrganizeSummary(
        total_files=len(files),
        processed=processed,
        skipped=skipped,
        errors=errors,
        dry_run=context.dry_run,
        directories_created=directories_created,
    )

    # Clean up empty directories if requested (only in non-dry-run mode)
    if context.clean_empty and not context.dry_run:
        remove_empty_dirs(source_dir, source_dir)
        # Cleanup failures are non-fatal, ignore and continue

    return IOResult.from_value((summary, plan))

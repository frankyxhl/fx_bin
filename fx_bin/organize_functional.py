"""Functional IO operations for file organization using returns library.

This module provides safe file organization operations with functional
error handling using the returns library.

Error Hierarchy:
    FileOperationError (base for all file operations)
    ├── OrganizeError (organization-specific errors)
        ├── DateReadError (file date reading errors)
        └── MoveError (file move errors)
"""

import os
import shutil
from datetime import datetime
from typing import List, Set, Tuple

from loguru import logger as L
from returns.io import IOResult

from fx_bin.errors import DateReadError, MoveError, OrganizeError
from fx_bin.lib import unsafe_ioresult_unwrap
from fx_bin.organize import (
    DateSource,
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
            birthtime = stat_info.st_birthtime
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


def _should_skip_entry(entry_path: str, output_dir: str) -> bool:
    """Check if entry should be skipped (output directory)."""
    return (
        bool(output_dir) and os.path.commonpath([entry_path, output_dir]) == output_dir
    )


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

    try:
        dir_stat = os.stat(dir_path)
        dir_inode = (dir_stat.st_dev, dir_stat.st_ino)

        # Cycle detection
        if dir_inode in visited_inodes:
            L.debug(f"Skipping already visited directory: {dir_path}")
            return files

        visited_inodes.add(dir_inode)

        with os.scandir(dir_path) as entries:
            for entry in entries:
                try:
                    entry_path = os.path.join(dir_path, entry.name)

                    # Skip output directory
                    if _should_skip_entry(entry_path, output_dir):
                        L.debug(f"Skipping output directory: {entry_path}")
                        continue

                    if entry.is_symlink():
                        if follow_symlinks:
                            target = os.path.realpath(entry_path)
                            if os.path.isdir(target):
                                files.extend(
                                    _scan_recursive(
                                        target,
                                        depth + 1,
                                        max_depth,
                                        output_dir,
                                        visited_inodes,
                                        follow_symlinks,
                                    )
                                )
                            else:
                                files.append(entry_path)
                        continue

                    if entry.is_file():
                        files.append(entry_path)
                    elif entry.is_dir() and not entry.is_symlink():
                        files.extend(
                            _scan_recursive(
                                entry_path,
                                depth + 1,
                                max_depth,
                                output_dir,
                                visited_inodes,
                                follow_symlinks,
                            )
                        )

                except (OSError, PermissionError):
                    continue

    except (OSError, PermissionError):
        pass

    return files


def _scan_non_recursive(
    dir_path: str,
    output_dir: str,
    follow_symlinks: bool,
) -> List[str]:
    """Helper for non-recursive directory scanning."""
    files: List[str] = []

    try:
        with os.scandir(dir_path) as entries:
            for entry in entries:
                try:
                    files.extend(
                        _process_entry(entry, dir_path, output_dir, follow_symlinks)
                    )
                except (OSError, PermissionError):
                    continue

    except (OSError, PermissionError):
        pass

    return files


def move_file_safe(
    source: str,
    target: str,
    source_root: str,
    output_root: str,
) -> IOResult[Tuple[None, bool], MoveError]:
    """Safely move a file from source to target with boundary checks.

    Creates parent directories if needed. Handles cross-filesystem moves.
    Uses atomic overwrite to avoid data corruption.
    Enforces path boundaries to prevent path traversal attacks.

    Args:
        source: Source file path
        target: Target file path
        source_root: Root directory that source must be within
        output_root: Root directory that target must be within

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
                MoveError(
                    f"Cannot move {source}: cross-device path from {source_root}"
                )
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

        # Create parent directories if they don't exist
        # Track if we create a new directory
        dir_created = False
        target_dir = os.path.dirname(target)
        if target_dir:
            # Check if directory exists before creating
            if not os.path.exists(target_dir):
                dir_created = True
            os.makedirs(target_dir, exist_ok=True)

        # Perform the move
        shutil.move(source, target)

        return IOResult.from_value((None, dir_created))

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            MoveError(f"Cannot move {source} to {target}: {e}")
        )


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
                # Skip if outside source root
                try:
                    if (
                        os.path.commonpath([dirpath, source_root_real])
                        != source_root_real
                    ):
                        continue
                except ValueError:
                    # Paths on different drives, skip
                    continue

                # Check if directory is currently empty
                # We need to check the actual filesystem state, not os.walk cache
                try:
                    contents = list(os.scandir(dirpath))
                    is_empty = len(contents) == 0
                except (OSError, PermissionError):
                    is_empty = False

                if is_empty:
                    try:
                        os.rmdir(dirpath)
                        empty_dirs_found = True
                    except (OSError, PermissionError):
                        # Directory might have been removed or became non-empty
                        pass

            if not empty_dirs_found:
                # No more empty dirs to remove
                break

        return IOResult.from_value(None)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            OrganizeError(f"Cannot cleanup directories {start_dir}: {e}")
        )


def execute_organize(
    source_dir: str, context: OrganizeContext
) -> IOResult[OrganizeSummary, OrganizeError]:
    """Execute file organization operation.

    Main orchestration function that:
    1. Scans source directory for files
    2. Reads file dates
    3. Generates organization plan
    4. Executes moves (unless dry-run)
    5. Returns summary statistics

    Args:
        source_dir: Source directory to organize
        context: Organization configuration context

    Returns:
        IOResult with OrganizeSummary or OrganizeError
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
    dates: "dict[str, datetime]" = {}
    date_errors = 0

    for file_path in files:
        date_result = get_file_date(file_path, context.date_source)
        try:
            dates[file_path] = unsafe_ioresult_unwrap(date_result)
        except Exception:
            date_errors += 1

    # Generate plan
    plan = generate_organize_plan(files, dates, context)

    # Execute plan and count results
    processed = 0
    skipped = 0
    errors = 0
    directories_created = 0

    for item in plan:
        if item.action == "moved":
            processed += 1
            if not context.dry_run:
                move_result = move_file_safe(
                    item.source,
                    item.target,
                    source_dir,  # source_root
                    context.output_dir,  # output_root
                )
                try:
                    _, dir_created = unsafe_ioresult_unwrap(move_result)
                    if dir_created:
                        directories_created += 1
                except Exception:
                    processed -= 1
                    errors += 1
        elif item.action == "skipped":
            skipped += 1
        elif item.action == "error":
            errors += 1

    summary = OrganizeSummary(
        total_files=len(files),
        processed=processed,
        skipped=skipped,
        errors=errors,
        dry_run=context.dry_run,
        directories_created=directories_created,
    )

    return IOResult.from_value(summary)

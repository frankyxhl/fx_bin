"""Pure functions and module-specific types for file organization.

This module contains all pure logic for organizing files into date-based
directory structures. Pure functions have no side effects and are deterministic.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from fnmatch import fnmatchcase
from typing import Dict, List, Sequence, Set


class DateSource(Enum):
    """File date source options.

    Determines which timestamp is used for organizing files into date directories.
    """

    CREATED = "created"  # Use file creation time (birthtime) with mtime fallback
    MODIFIED = "modified"  # Use file modification time (mtime)


class ConflictMode(Enum):
    """File conflict resolution strategies.

    Determines how to handle filename conflicts when organizing files.
    """

    RENAME = "rename"  # Auto-rename with _1, _2, etc. suffix
    SKIP = "skip"  # Skip files that would conflict
    OVERWRITE = "overwrite"  # Overwrite existing files
    ASK = "ask"  # Prompt user for conflicts only (intra-run uses rename)


@dataclass(frozen=True)
class OrganizeContext:
    """Configuration context for file organization operations.

    Immutable dataclass containing all configuration parameters for
    organizing files into date-based directory structures.

    Attributes:
        date_source: Which file timestamp to use (created/modified)
        depth: Directory depth (1, 2, or 3 levels)
        conflict_mode: Strategy for handling filename conflicts
        output_dir: Root output directory for organized files
        dry_run: If True, preview changes without executing
        include_patterns: Glob patterns for files to include (empty = all)
        exclude_patterns: Glob patterns for files to exclude (empty = none)
        recursive: If True, process subdirectories recursively
        clean_empty: If True, remove empty directories after organization
        fail_fast: If True, stop on first error instead of continuing
        hidden: If True, include hidden files (files starting with .)
    """

    date_source: DateSource
    depth: int  # 1, 2, or 3
    conflict_mode: ConflictMode
    output_dir: str
    dry_run: bool = False
    include_patterns: Sequence[str] = ()
    exclude_patterns: Sequence[str] = ()
    recursive: bool = False
    clean_empty: bool = False
    fail_fast: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class FileOrganizeResult:
    """Result of organizing a single file.

    Immutable dataclass containing the result of organizing one file.

    Attributes:
        source: Original source path
        target: Target path (may be modified for conflicts)
        action: Action taken ("moved", "skipped", "error")
    """

    source: str
    target: str
    action: str


@dataclass(frozen=True)
class OrganizeSummary:
    """Summary statistics for an organization operation.

    Immutable dataclass containing aggregate statistics after
    processing all files.

    Attributes:
        total_files: Total number of files scanned
        processed: Number of files successfully moved
        skipped: Number of files skipped (conflicts, filters, etc.)
        errors: Number of errors encountered
        dry_run: Whether this was a dry-run (preview only)
        directories_created: Number of directories created (0 in dry-run)
    """

    total_files: int
    processed: int
    skipped: int
    errors: int
    dry_run: bool
    directories_created: int = 0


def get_target_path(
    output_dir: str,
    filename: str,
    file_date: datetime,
    depth: int,
) -> str:
    """Calculate target path for organizing a file into date-based directories.

    Pure function that computes the target path based on the file's date and
    the configured directory depth.

    Args:
        output_dir: Root output directory
        filename: Name of the file (with extension)
        file_date: Date to use for organization (local timezone)
        depth: Directory depth (1, 2, or 3)

    Returns:
        Full target path with date-based directory structure

    Examples:
        >>> get_target_path("/output", "photo.jpg", datetime(2026, 1, 10), 3)
        '/output/2026/202601/20260110/photo.jpg'
        >>> get_target_path("/output", "photo.jpg", datetime(2026, 1, 10), 2)
        '/output/2026/20260110/photo.jpg'
        >>> get_target_path("/output", "photo.jpg", datetime(2026, 1, 10), 1)
        '/output/20260110/photo.jpg'
    """
    year = file_date.strftime("%Y")
    year_month = file_date.strftime("%Y%m")
    year_month_day = file_date.strftime("%Y%m%d")

    if depth == 3:
        date_path = os.path.join(year, year_month, year_month_day)
    elif depth == 2:
        date_path = os.path.join(year, year_month_day)
    elif depth == 1:
        date_path = year_month_day
    else:
        # Default to depth 3 if invalid value
        date_path = os.path.join(year, year_month, year_month_day)

    return os.path.join(output_dir, date_path, filename)


def is_hidden_file(filename: str) -> bool:
    """Check if a file is hidden (Unix-style: starts with dot).

    Pure function that checks if a filename starts with a dot,
    indicating a hidden file on Unix-like systems.

    Args:
        filename: Name of the file (can be basename or full path)

    Returns:
        True if file starts with '.', False otherwise

    Examples:
        >>> is_hidden_file(".gitignore")
        True
        >>> is_hidden_file("photo.jpg")
        False
    """
    basename = os.path.basename(filename)
    return basename.startswith(".")


def matches_glob_pattern(filename: str, pattern: str) -> bool:
    """Check if filename matches a glob pattern (case-sensitive).

    Pure function that performs case-sensitive glob matching on the
    basename only (not the full path). Uses fnmatch.fnmatchcase.

    Args:
        filename: Name of the file (can be basename or full path)
        pattern: Glob pattern (e.g., "*.jpg", "document.*")

    Returns:
        True if basename matches the pattern, False otherwise

    Examples:
        >>> matches_glob_pattern("photo.jpg", "*.jpg")
        True
        >>> matches_glob_pattern("photo.JPG", "*.jpg")  # Case-sensitive!
        False
        >>> matches_glob_pattern("/path/to/photo.jpg", "*.jpg")  # Matches basename
        True
    """
    basename = os.path.basename(filename)
    return fnmatchcase(basename, pattern)


def should_process_file(
    filename: str,
    include_patterns: Sequence[str] = (),
    exclude_patterns: Sequence[str] = (),
    hidden: bool = False,
) -> bool:
    """Determine if a file should be processed based on filter patterns.

    Pure function that applies include and exclude glob patterns.
    Evaluation order:
    1. If hidden=False (default), exclude hidden files (starting with .)
    2. If include_patterns specified, file must match at least one
    3. If exclude_patterns specified, file must not match any
    4. If no patterns specified, all non-hidden files are processed

    Args:
        filename: Name of the file
        include_patterns: Tuple of glob patterns to include (empty = all)
        exclude_patterns: Tuple of glob patterns to exclude (empty = none)
        hidden: If True, include hidden files (files starting with .)

    Returns:
        True if file should be processed, False otherwise

    Examples:
        >>> should_process_file("photo.jpg", ("*.jpg", "*.png"), ())
        True
        >>> should_process_file("doc.pdf", ("*.jpg", "*.png"), ())
        False
        >>> should_process_file(".hidden.jpg", ("*.jpg",), (".*"))
        False
        >>> should_process_file("photo.jpg", (), ())
        True
        >>> should_process_file(".hidden", (), ())
        False  # Hidden file excluded by default
        >>> should_process_file(".hidden", (), (), hidden=True)
        True  # Hidden file included with hidden=True
    """
    basename = os.path.basename(filename)

    # Check hidden files first (before pattern matching)
    if not hidden and is_hidden_file(basename):
        return False

    # Handle edge case where a single string is passed instead of a tuple
    # In Python, ("pattern") is just a string, not a tuple - needs ("pattern",)
    # We check if it's a string and treat it as a single-element tuple
    if isinstance(include_patterns, str):
        include_patterns = (include_patterns,)
    if isinstance(exclude_patterns, str):
        exclude_patterns = (exclude_patterns,)

    # Must match include patterns if specified
    if include_patterns and not any(
        matches_glob_pattern(basename, p) for p in include_patterns
    ):
        return False

    # Must not match exclude patterns if specified
    if exclude_patterns and any(
        matches_glob_pattern(basename, p) for p in exclude_patterns
    ):
        return False

    return True


def resolve_conflict_rename(target_path: str, allocated_paths: Set[str]) -> str:
    """Resolve filename conflict by adding incrementing suffix.

    Pure function that generates a unique filename by adding _1, _2, etc.
    Uses get_base_name() and get_multi_ext() from common.py to handle
    multi-part extensions correctly.

    Args:
        target_path: The conflicting target path
        allocated_paths: Set of already allocated target paths

    Returns:
        A unique path with incrementing suffix (_1, _2, etc.)

    Examples:
        >>> allocated = {"/output/2026/202601/20260110/photo.jpg"}
        >>> resolve_conflict_rename("/output/2026/202601/20260110/photo.jpg", allocated)
        '/output/2026/202601/20260110/photo_1.jpg'
    """
    from fx_bin.common import get_base_name, get_multi_ext

    if target_path not in allocated_paths:
        return target_path

    dirname = os.path.dirname(target_path)
    filename = os.path.basename(target_path)

    base = get_base_name(filename)
    ext = get_multi_ext(filename)

    # Find the next available suffix
    suffix = 1
    while True:
        new_filename = f"{base}_{suffix}{ext}"
        new_path = os.path.join(dirname, new_filename)
        if new_path not in allocated_paths:
            return new_path
        suffix += 1


def generate_organize_plan(
    files: Sequence[str],
    dates: Dict[str, datetime],
    context: OrganizeContext,
) -> List[FileOrganizeResult]:
    """Generate organization plan with conflict resolution.

    Pure function that creates a deterministic plan for organizing files.
    Handles intra-run collisions at plan time based on conflict mode.

    Args:
        files: Sequence of source file paths (list, tuple, or any sequence)
        dates: Dictionary mapping file paths to their dates
        context: Organization configuration context

    Returns:
        List of FileOrganizeResult objects with planned actions

    Examples:
        >>> files = ["/src/photo.jpg"]
        >>> dates = {"/src/photo.jpg": datetime(2026, 1, 10)}
        >>> ctx = OrganizeContext(
        ...     DateSource.CREATED, 3, ConflictMode.RENAME, "/output", False
        ... )
        >>> plan = generate_organize_plan(files, dates, ctx)
        >>> len(plan)
        1
    """
    # Sort for deterministic ordering
    sorted_files = sorted(files)

    allocated_paths: Set[str] = set()
    plan: List[FileOrganizeResult] = []

    for source_file in sorted_files:
        # Skip files that don't have date information
        if source_file not in dates:
            plan.append(FileOrganizeResult(source_file, "", "error"))
            continue

        file_date = dates[source_file]
        filename = os.path.basename(source_file)

        # Calculate target path
        target_path = get_target_path(
            context.output_dir,
            filename,
            file_date,
            context.depth,
        )

        # Check for no-op (file already at target)
        if os.path.realpath(source_file) == os.path.realpath(target_path):
            plan.append(FileOrganizeResult(source_file, source_file, "skipped"))
            continue

        # Handle intra-run conflicts
        if target_path in allocated_paths:
            if context.conflict_mode == ConflictMode.SKIP:
                plan.append(FileOrganizeResult(source_file, target_path, "skipped"))
                continue
            else:
                # RENAME, OVERWRITE, ASK all use rename for intra-run conflicts
                target_path = resolve_conflict_rename(target_path, allocated_paths)

        # Apply filters
        if not should_process_file(
            filename,
            context.include_patterns,
            context.exclude_patterns,
            context.hidden,
        ):
            plan.append(FileOrganizeResult(source_file, "", "skipped"))
            continue

        allocated_paths.add(target_path)
        plan.append(FileOrganizeResult(source_file, target_path, "moved"))

    return plan

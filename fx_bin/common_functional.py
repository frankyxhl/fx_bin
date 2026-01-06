"""Functional version of common.py utilities using returns library.

This module provides functional implementations of common utilities
with explicit error handling and IO operations.

Error Hierarchy:
    FileOperationError (base for all file operations)
    └── IOError (file I/O errors)

    FolderError (folder traversal errors)

IOError inherits from FileOperationError, enabling polymorphic
error handling for all file-related operations.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import total_ordering
from typing import Tuple, Set, Optional

from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure
from returns.io import IOResult, impure_safe
from returns.context import RequiresContext

from fx_bin.errors import FolderError, IOError as FxIOError
from fx_bin.shared_types import EntryType, FolderContext
from .common import convert_size
from .lib import unsafe_ioresult_value_or


@dataclass(frozen=True)
@total_ordering
class SizeEntry:
    """Immutable entry representing a file or folder with size information."""

    name: str
    size: int
    entry_type: EntryType
    path: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SizeEntry):
            return NotImplemented
        return self.size == other.size

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SizeEntry):
            return NotImplemented
        return self.size < other.size

    def __repr__(self) -> str:
        return f"{convert_size(self.size)}\t{self.name}"

    @classmethod
    def from_scandir_functional(
        cls, entry: os.DirEntry, parent_dir: str = ""
    ) -> IOResult[Maybe[SizeEntry], FxIOError]:
        """
        Create SizeEntry from os.DirEntry with functional error handling.

        Returns IOResult containing Maybe[SizeEntry] to handle both IO errors
        and cases where entry cannot be accessed.
        """

        @impure_safe
        def get_entry_stat() -> IOResult[os.stat_result, FxIOError]:
            """Safely get stat information for entry."""
            try:
                return IOResult.from_value(entry.stat(follow_symlinks=False))
            except (OSError, PermissionError) as e:
                # Return None wrapped in IOResult for permission errors
                # This is expected behavior - we skip inaccessible entries
                return IOResult.from_failure(
                    FxIOError(f"Cannot access {entry.path}: {e}")
                )

        @impure_safe
        def create_entry_from_stat(
            stat: os.stat_result,
        ) -> IOResult[SizeEntry, FxIOError]:
            """Create SizeEntry from stat result."""
            try:
                entry_type = EntryType.FOLDER if entry.is_dir() else EntryType.FILE
                full_path = (
                    os.path.join(parent_dir, entry.name) if parent_dir else entry.name
                )

                return IOResult.from_value(
                    cls(
                        name=entry.name,
                        size=stat.st_size,
                        entry_type=entry_type,
                        path=full_path,
                    )
                )
            except Exception as e:
                return IOResult.from_failure(FxIOError(f"Error creating entry: {e}"))

        # Try to get stat, if it fails return Nothing wrapped in Success
        stat_result = get_entry_stat()

        # If we can't stat the file, return Nothing (expected for permission
        # errors)
        if isinstance(unsafe_ioresult_value_or(stat_result, Nothing), Failure):
            return IOResult.from_value(Nothing)

        # Otherwise create the entry
        return stat_result.bind(create_entry_from_stat).map(Some)  # type: ignore


# ============================================================================
# Pure Functions - No IO, Easy to Test

# ============================================================================


def should_process_directory(
    depth: int,
    context: FolderContext,
    dir_inode: Tuple[int, int] | None = None,
) -> bool:
    """Check if directory should be processed (pure function).

    This pure function determines whether a directory should be traversed
    based on recursion depth limits and cycle detection. Being pure (no side
    effects, deterministic output), it's easily testable and composable.

    Args:
        depth: Current recursion depth (0-based, where 0 is the starting directory)
        context: Folder traversal context containing:
            - visited_inodes: Set of (device, inode) tuples already processed
            - max_depth: Maximum allowed recursion depth
        dir_inode: Optional (device, inode) tuple for cycle detection.
                  If provided and already in visited set, returns False.

    Returns:
        bool: True if directory should be processed, False if it should be
              skipped due to depth limit or cycle detection.

    Examples:
        >>> context = FolderContext(visited_inodes=set(), max_depth=10)
        >>> should_process_directory(5, context)
        True
        >>> should_process_directory(11, context)
        False
        >>> should_process_directory(5, context, dir_inode=(1, 2))
        True

    Note:
        This is a pure function with no side effects - perfect for unit testing.
        Given the same inputs, it always produces the same output.
    """
    # Check depth limit
    if depth > context.max_depth:
        return False

    # Check for cycles if inode provided
    if dir_inode is not None and dir_inode in context.visited_inodes:
        return False

    return True


def calculate_entry_contribution(entry_info: object) -> int:
    """Calculate size contribution of a single entry (pure function).

    This pure function determines what size a filesystem entry contributes
    to the total size calculation. Files contribute their actual size, while
    directories contribute 0 (their total size comes from recursive traversal).

    Args:
        entry_info: Object representing a filesystem entry with attributes:
            - is_file: bool indicating if this is a file
            - is_dir: bool indicating if this is a directory
            - size: int representing the entry's size in bytes

    Returns:
        int: Size contribution in bytes. Returns the file size for files,
             0 for directories (since directory sizes are calculated through
             recursive traversal of their contents).

    Examples:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class FileEntry:
        ...     is_file: bool
        ...     is_dir: bool
        ...     size: int
        >>> file_entry = FileEntry(is_file=True, is_dir=False, size=1024)
        >>> calculate_entry_contribution(file_entry)
        1024
        >>> dir_entry = FileEntry(is_file=False, is_dir=True, size=0)
        >>> calculate_entry_contribution(dir_entry)
        0

    Note:
        This is a pure function - given the same input, always returns same output.
        No side effects, no IO operations, perfect for unit testing.
    """
    if hasattr(entry_info, "is_file") and entry_info.is_file:
        return getattr(entry_info, "size", 0)
    return 0


def add_visited_inode(context: FolderContext, inode: Tuple[int, int]) -> FolderContext:
    """Create new context with additional visited inode (pure function).

    This pure, immutable function creates a new FolderContext with an additional
    inode marked as visited, without modifying the original context. This follows
    functional programming principles of immutability and referential transparency.

    Args:
        context: Original folder traversal context containing:
            - visited_inodes: Set of (device, inode) tuples already processed
            - max_depth: Maximum allowed recursion depth
        inode: (device, inode) tuple to add to the visited set.
               Represents a unique filesystem entry identifier.

    Returns:
        FolderContext: New context instance with the inode added to visited_inodes.
                      The original context remains unchanged (immutability).
                      Preserves max_depth from original context.

    Examples:
        >>> context = FolderContext(visited_inodes={(1, 2), (3, 4)}, max_depth=100)
        >>> new_inode = (5, 6)
        >>> new_context = add_visited_inode(context, new_inode)
        >>> new_inode in new_context.visited_inodes
        True
        >>> new_inode in context.visited_inodes  # Original unchanged
        False
        >>> new_context.max_depth == context.max_depth
        True

    Note:
        This is a pure, immutable function - original context is never modified.
        Given the same inputs, always produces the same output. No side effects.
        Perfect for functional composition and testing.
    """
    new_visited = context.visited_inodes | {inode}
    return FolderContext(visited_inodes=new_visited, max_depth=context.max_depth)


# ============================================================================
# IO Functions - Uses Pure Functions Above
# ============================================================================


def sum_folder_size_functional(
    path: str = ".",
) -> RequiresContext[IOResult[int, FolderError], FolderContext]:
    """
    Calculate total size of a folder using functional patterns.

    Returns a RequiresContext that when given a FolderContext,
    produces an IOResult with the total size or an error.

    RequiresContext Pattern:
    - Makes dependencies explicit (requires FolderContext to run)
    - Allows dependency injection for testing
    - Composable (can map, bind, etc.)

    Usage:
        context = FolderContext(visited_inodes=set(), max_depth=100)
        result = sum_folder_size_functional("/path")(context)  # Inject context
    """

    def _sum_folder(context: FolderContext) -> IOResult[int, FolderError]:
        # Delegate to recursive implementation with injected context
        return _sum_folder_recursive(path, context, depth=0)

    return RequiresContext(_sum_folder)


def _sum_folder_recursive(
    path: str, context: FolderContext, depth: int
) -> IOResult[int, FolderError]:
    """Recursive implementation of folder size calculation.

    This function has side effects (IO operations) and manually wraps
    results in IOResult for proper error handling.
    """

    # Check depth limit (uses pure function should_process_directory)
    if depth > context.max_depth:
        return IOResult.from_value(0)

    try:
        # Get directory's inode for cycle detection
        dir_stat = os.stat(path)
        dir_inode = (dir_stat.st_dev, dir_stat.st_ino)

        # Check for cycles (prevents infinite recursion on symlinks)
        if dir_inode in context.visited_inodes:
            return IOResult.from_value(0)

        # Immutability: Create NEW context instead of mutating existing one
        # This is thread-safe and easier to reason about
        new_visited = context.visited_inodes | {dir_inode}  # Set union (not mutation)
        new_context = FolderContext(new_visited, context.max_depth)

        total = 0

        # Scan directory entries
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                try:
                    total += entry.stat(follow_symlinks=False).st_size
                except (OSError, PermissionError):
                    # Skip files we can't access
                    pass
            elif entry.is_dir(follow_symlinks=False):
                # Recursive call with new context
                subdir_result = _sum_folder_recursive(
                    entry.path, new_context, depth + 1
                )
                # Extract value or use 0 on failure
                subdir_size = unsafe_ioresult_value_or(subdir_result, 0)
                total += subdir_size

        return IOResult.from_value(total)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(FolderError(f"Cannot access {path}: {e}"))


def sum_folder_files_count_functional(
    path: str = ".",
) -> RequiresContext[IOResult[int, FolderError], FolderContext]:
    """
    Count files in a folder using functional patterns.

    Returns a RequiresContext that when given a FolderContext,
    produces an IOResult with the file count or an error.
    """

    def _count_files(context: FolderContext) -> IOResult[int, FolderError]:
        return _count_files_recursive(path, context, depth=0)

    return RequiresContext(_count_files)


def _count_files_recursive(
    path: str, context: FolderContext, depth: int
) -> IOResult[int, FolderError]:
    """Recursive implementation of file counting.

    This function has side effects (IO operations) and manually wraps
    results in IOResult for proper error handling.
    """

    # Check depth limit
    if depth > context.max_depth:
        return IOResult.from_value(0)

    try:
        # Get directory's inode
        dir_stat = os.stat(path)
        dir_inode = (dir_stat.st_dev, dir_stat.st_ino)

        # Check for cycles
        if dir_inode in context.visited_inodes:
            return IOResult.from_value(0)

        # Create new context with updated visited set
        new_visited = context.visited_inodes | {dir_inode}
        new_context = FolderContext(new_visited, context.max_depth)

        count = 0

        # Scan directory entries
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                count += 1
            elif entry.is_dir(follow_symlinks=False):
                # Recursive call with new context
                subdir_result = _count_files_recursive(
                    entry.path, new_context, depth + 1
                )
                # Extract value or use 0 on failure
                subdir_count = unsafe_ioresult_value_or(subdir_result, 0)
                count += subdir_count

        return IOResult.from_value(count)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(FolderError(f"Cannot access {path}: {e}"))


# Compatibility wrappers for existing code


def sum_folder_size_legacy(
    path: str = ".",
    _visited_inodes: Optional[Set[Tuple[int, int]]] = None,
    _depth: int = 0,
) -> int:
    """Legacy interface for backward compatibility."""
    context = FolderContext(visited_inodes=_visited_inodes or set(), max_depth=100)
    result = sum_folder_size_functional(path)(context)
    return unsafe_ioresult_value_or(result, 0)


def sum_folder_files_count_legacy(
    path: str = ".",
    _visited_inodes: Optional[Set[Tuple[int, int]]] = None,
    _depth: int = 0,
) -> int:
    """Legacy interface for backward compatibility."""
    context = FolderContext(visited_inodes=_visited_inodes or set(), max_depth=100)
    result = sum_folder_files_count_functional(path)(context)
    return unsafe_ioresult_value_or(result, 0)

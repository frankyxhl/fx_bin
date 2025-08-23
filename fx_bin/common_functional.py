"""Functional version of common.py utilities using returns library.

This module provides functional implementations of common utilities
with explicit error handling and IO operations.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Set, Tuple

from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure
from returns.io import IOResult, impure_safe
from returns.context import RequiresContext

from fx_bin.errors import FolderError, IOError as FxIOError


class EntryType(Enum):
    """Type of filesystem entry."""
    FILE = 1
    FOLDER = 2


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
        cls,
        entry: os.DirEntry,
        parent_dir: str = ""
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
            stat: os.stat_result
        ) -> IOResult[SizeEntry, FxIOError]:
            """Create SizeEntry from stat result."""
            try:
                entry_type = (
                    EntryType.FOLDER if entry.is_dir() else EntryType.FILE
                )
                full_path = (
                    os.path.join(parent_dir, entry.name)
                    if parent_dir
                    else entry.name
                )

                return IOResult.from_value(cls(
                    name=entry.name,
                    size=stat.st_size,
                    entry_type=entry_type,
                    path=full_path
                ))
            except Exception as e:
                return IOResult.from_failure(
                    FxIOError(f"Error creating entry: {e}")
                )

        # Try to get stat, if it fails return Nothing wrapped in Success
        stat_result = get_entry_stat()

        # If we can't stat the file, return Nothing (expected for permission
        # errors)
        if isinstance(stat_result.run(), Failure):
            return IOResult.from_value(Nothing)

        # Otherwise create the entry
        return stat_result.bind(create_entry_from_stat).map(Some)


def convert_size(size: int) -> str:
    """Convert size in bytes to human-readable format (pure function)."""
    size_bytes = int(size)
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    # Clamp to valid index range
    i = min(i, len(size_name) - 1)
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{round(s)}{size_name[i]}"


@dataclass(frozen=True)
class FolderContext:
    """Context for folder traversal operations."""
    visited_inodes: Set[Tuple[int, int]]
    max_depth: int = 100


def sum_folder_size_functional(
    path: str = '.'
) -> RequiresContext[IOResult[int, FolderError], FolderContext]:
    """
    Calculate total size of a folder using functional patterns.

    Returns a RequiresContext that when given a FolderContext,
    produces an IOResult with the total size or an error.
    """
    def _sum_folder(context: FolderContext) -> IOResult[int, FolderError]:
        return _sum_folder_recursive(path, context, depth=0)

    return RequiresContext(_sum_folder)


@impure_safe
def _sum_folder_recursive(
    path: str,
    context: FolderContext,
    depth: int
) -> IOResult[int, FolderError]:
    """Recursive implementation of folder size calculation."""

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
                subdir_size = subdir_result.run().value_or(0)
                total += subdir_size

        return IOResult.from_value(total)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            FolderError(f"Cannot access {path}: {e}")
        )


def sum_folder_files_count_functional(
    path: str = '.'
) -> RequiresContext[IOResult[int, FolderError], FolderContext]:
    """
    Count files in a folder using functional patterns.

    Returns a RequiresContext that when given a FolderContext,
    produces an IOResult with the file count or an error.
    """
    def _count_files(context: FolderContext) -> IOResult[int, FolderError]:
        return _count_files_recursive(path, context, depth=0)

    return RequiresContext(_count_files)


@impure_safe
def _count_files_recursive(
    path: str,
    context: FolderContext,
    depth: int
) -> IOResult[int, FolderError]:
    """Recursive implementation of file counting."""

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
                subdir_count = subdir_result.run().value_or(0)
                count += subdir_count

        return IOResult.from_value(count)

    except (OSError, PermissionError) as e:
        return IOResult.from_failure(
            FolderError(f"Cannot access {path}: {e}")
        )


# Compatibility wrappers for existing code

def sum_folder_size_legacy(
    path: str = '.', _visited_inodes=None, _depth=0
) -> int:
    """Legacy interface for backward compatibility."""
    context = FolderContext(
        visited_inodes=_visited_inodes or set(),
        max_depth=100
    )
    result = sum_folder_size_functional(path)(context)
    return (result._inner_value.value_or(0)
            if hasattr(result, '_inner_value') else 0)


def sum_folder_files_count_legacy(
    path: str = '.', _visited_inodes=None, _depth=0
) -> int:
    """Legacy interface for backward compatibility."""
    context = FolderContext(
        visited_inodes=_visited_inodes or set(),
        max_depth=100
    )
    result = sum_folder_files_count_functional(path)(context)
    return (result._inner_value.value_or(0)
            if hasattr(result, '_inner_value') else 0)

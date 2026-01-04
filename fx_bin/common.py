"""Common utilities and classes for fx_bin package."""

import math
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import total_ordering
from typing import Any, Optional, Set, Tuple


class EntryType(Enum):
    """Type of filesystem entry."""

    FILE = 1
    FOLDER = 2


def generate_timestamp(format_str: str, now: Optional[datetime] = None) -> str:
    """Generate current timestamp with specified format.

    Args:
        format_str: strftime format string (e.g., "%Y%m%d%H%M%S%f")
        now: Optional datetime object to use instead of current time

    Returns:
        Formatted timestamp string

    Examples:
        >>> generate_timestamp("%Y%m%d")
        '20260105'
    """
    if now is None:
        now_dt = datetime.now()
    else:
        if not isinstance(now, datetime):
            raise TypeError("now must be a datetime object")
        now_dt = now
    return now_dt.strftime(format_str)


# Known multi-part extensions
KNOWN_MULTI_EXTS = (".tar.gz", ".tar.bz2", ".tar.xz")


def get_multi_ext(filename: str) -> str:
    """Extract multi-part or single extension from filename.

    Args:
        filename: Name of the file

    Returns:
        Extension string (e.g., '.tar.gz', '.txt', or '')

    Examples:
        >>> get_multi_ext("archive.tar.gz")
        '.tar.gz'
        >>> get_multi_ext("document.txt")
        '.txt'
        >>> get_multi_ext("README")
        ''
    """
    for multi_ext in KNOWN_MULTI_EXTS:
        if filename.endswith(multi_ext):
            return multi_ext

    if "." in filename:
        return "." + filename.rsplit(".", 1)[1]
    return ""


def get_base_name(filename: str) -> str:
    """Extract base name from filename, handling multi-part extensions.

    Args:
        filename: Name of the file

    Returns:
        Base name without extension

    Examples:
        >>> get_base_name("archive.tar.gz")
        'archive'
        >>> get_base_name("document.txt")
        'document'
        >>> get_base_name("README")
        'README'
    """
    ext = get_multi_ext(filename)
    if ext:
        return filename[: -len(ext)]
    return filename


def convert_size(size: int) -> str:
    """Convert size in bytes to human-readable format."""
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


def format_size_aligned(size: int, width: int = 9) -> str:
    """Format file size with alignment and spacing for table output.

    Args:
        size: Size in bytes
        width: Total width for alignment (default: 9)

    Returns:
        Right-aligned size string with unit (e.g., "   1.5 KB")

    Examples:
        >>> format_size_aligned(1536)
        '   1.5 KB'
        >>> format_size_aligned(0)
        '     0 B'
    """
    if size == 0:
        return f"{'0 B':>{width}}"

    size_bytes = int(size)
    if size_bytes < 1024:
        return f"{size_bytes} B".rjust(width)

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)

    return f"{s} {size_name[i]}".rjust(width)


def sum_folder_size(
    path: str = ".",
    _visited_inodes: Optional[Set[Tuple[int, int]]] = None,
    _depth: int = 0,
) -> int:
    """Recursively calculate total size of a folder with safety checks."""
    # Initialize visited inodes set on first call
    if _visited_inodes is None:
        _visited_inodes = set()

    # Prevent infinite recursion
    if _depth > 100:
        return 0

    total = 0
    try:
        # Get directory's inode to detect cycles
        dir_stat = os.stat(path)
        dir_inode = (dir_stat.st_dev, dir_stat.st_ino)

        # Check if we've already visited this directory (symlink loop)
        if dir_inode in _visited_inodes:
            return 0

        _visited_inodes.add(dir_inode)

        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
                elif entry.is_dir(follow_symlinks=False):
                    # Recursively calculate subdirectory size
                    total += sum_folder_size(entry.path, _visited_inodes, _depth + 1)
                elif entry.is_symlink():
                    # Handle symlinks carefully
                    try:
                        if entry.is_file():
                            total += entry.stat().st_size
                    except (OSError, ValueError):
                        # Skip broken symlinks or circular references
                        pass
        finally:
            # Remove from visited set when leaving directory
            _visited_inodes.discard(dir_inode)

    except (PermissionError, OSError, ValueError):
        pass  # Skip directories we can't access
    return total


def sum_folder_files_count(
    path: str = ".",
    _visited_inodes: Optional[Set[Tuple[int, int]]] = None,
    _depth: int = 0,
) -> int:
    """Recursively count total files in a folder with safety checks."""
    # Initialize visited inodes set on first call
    if _visited_inodes is None:
        _visited_inodes = set()

    # Prevent infinite recursion
    if _depth > 100:
        return 0

    total = 0
    try:
        # Get directory's inode to detect cycles
        dir_stat = os.stat(path)
        dir_inode = (dir_stat.st_dev, dir_stat.st_ino)

        # Check if we've already visited this directory (symlink loop)
        if dir_inode in _visited_inodes:
            return 0

        _visited_inodes.add(dir_inode)

        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += 1
                elif entry.is_dir(follow_symlinks=False):
                    # Recursively count files in subdirectory
                    total += sum_folder_files_count(
                        entry.path, _visited_inodes, _depth + 1
                    )
                elif entry.is_symlink():
                    # Handle symlinks carefully
                    try:
                        if entry.is_file():
                            total += 1
                    except (OSError, ValueError):
                        # Skip broken symlinks or circular references
                        pass
        finally:
            # Remove from visited set when leaving directory
            _visited_inodes.discard(dir_inode)

    except (PermissionError, OSError, ValueError):
        pass  # Skip directories we can't access
    return total


@dataclass
@total_ordering
class SizeEntry:
    """Entry for size-based operations."""

    __slots__ = ["name", "size", "tpe"]
    name: str
    size: int
    tpe: EntryType

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, SizeEntry):
            raise TypeError(f"Not same Type. Another type is {type(other)}")
        return self.size < other.size

    def __repr__(self) -> str:
        return f"{self.readable_size}\t{self.name}"

    @property
    def readable_size(self) -> str:
        return convert_size(self.size)

    @classmethod
    def from_scandir(cls, obj: os.DirEntry[str]) -> Optional["SizeEntry"]:
        """Create SizeEntry from os.DirEntry object."""
        try:
            if obj.is_file(follow_symlinks=False):
                return cls(
                    obj.name,
                    obj.stat(follow_symlinks=False).st_size,
                    EntryType.FILE,
                )
            elif obj.is_dir(follow_symlinks=False):
                total_size = sum_folder_size(obj.path)
                return cls(obj.name, total_size, EntryType.FOLDER)
        except (PermissionError, OSError):
            return None
        return None


@dataclass
@total_ordering
class FileCountEntry:
    """Entry for file count operations."""

    __slots__ = ["name", "count", "tpe"]
    name: str
    count: int
    tpe: EntryType

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, FileCountEntry):
            raise TypeError(f"Not same Type. Another type is {type(other)}")
        return (self.count, self.name) < (other.count, other.name)

    def display(self, count_max: int) -> str:
        return f"{self.count:>{count_max}} {self.name}"

    @classmethod
    def from_scandir(cls, obj: os.DirEntry[str]) -> Optional["FileCountEntry"]:
        """Create FileCountEntry from os.DirEntry object."""
        try:
            if obj.is_file(follow_symlinks=False):
                return cls(obj.name, 1, EntryType.FILE)
            elif obj.is_dir(follow_symlinks=False):
                count = sum_folder_files_count(obj.path)
                return cls(obj.name, count, EntryType.FOLDER)
        except (PermissionError, OSError):
            return None
        return None

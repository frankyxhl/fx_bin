"""Common utilities and classes for fx_bin package."""
import math
import os
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Optional


class EntryType(Enum):
    """Type of filesystem entry."""
    FILE = 1
    FOLDER = 2


def convert_size(size: int) -> str:
    """Convert size in bytes to human-readable format."""
    size_bytes = int(size)
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{round(s)}{size_name[i]}"


def sum_folder_size(path: str = '.', _visited_inodes=None, _depth=0) -> int:
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
                    total += sum_folder_size(
                        entry.path, _visited_inodes, _depth + 1
                    )
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
    path: str = '.', _visited_inodes=None, _depth=0
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
    __slots__ = ['name', 'size', 'tpe']
    name: str
    size: int
    tpe: EntryType

    def __lt__(self, other):
        if not isinstance(other, SizeEntry):
            raise TypeError(f"Not same Type. Another type is {type(other)}")
        return self.size < other.size

    def __repr__(self):
        return f"{self.readable_size}\t{self.name}"

    @property
    def readable_size(self) -> str:
        return convert_size(self.size)

    @classmethod
    def from_scandir(cls, obj) -> Optional['SizeEntry']:
        """Create SizeEntry from os.DirEntry object."""
        try:
            if obj.is_file():
                return cls(obj.name, obj.stat().st_size, EntryType.FILE)
            elif obj.is_dir():
                total_size = sum_folder_size(obj.path)
                return cls(obj.name, total_size, EntryType.FOLDER)
        except (PermissionError, OSError):
            return None


@dataclass
@total_ordering
class FileCountEntry:
    """Entry for file count operations."""
    __slots__ = ['name', 'count', 'tpe']
    name: str
    count: int
    tpe: EntryType

    def __lt__(self, other):
        if not isinstance(other, FileCountEntry):
            raise TypeError(f"Not same Type. Another type is {type(other)}")
        return (self.count, self.name) < (other.count, other.name)

    def display(self, count_max: int) -> str:
        return f"{self.count:>{count_max}} {self.name}"

    @classmethod
    def from_scandir(cls, obj) -> Optional['FileCountEntry']:
        """Create FileCountEntry from os.DirEntry object."""
        try:
            if obj.is_file():
                return cls(obj.name, 1, EntryType.FILE)
            elif obj.is_dir():
                count = sum_folder_files_count(obj.path)
                return cls(obj.name, count, EntryType.FOLDER)
        except (PermissionError, OSError):
            return None

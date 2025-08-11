"""Common utilities and classes for fx_bin package."""
import math
import os
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Optional, Tuple, List


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


def sum_folder_size(path: str = '.') -> int:
    """Recursively calculate total size of a folder."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += sum_folder_size(entry.path)
    except (PermissionError, OSError):
        pass  # Skip directories we can't access
    return total


def sum_folder_files_count(path: str = '.') -> int:
    """Recursively count total files in a folder."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += 1
            elif entry.is_dir():
                total += sum_folder_files_count(entry.path)
    except (PermissionError, OSError):
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
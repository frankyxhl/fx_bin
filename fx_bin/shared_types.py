"""Shared type definitions for fx_bin package.

This module contains type definitions that are shared across multiple modules
to avoid duplication and circular imports.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Set, Tuple


class EntryType(Enum):
    """Type of filesystem entry.

    Used across both imperative and functional code to distinguish
    between files and folders.
    """

    FILE = 1
    FOLDER = 2


@dataclass(frozen=True)
class FileBackup:
    """Represents a file backup with metadata.

    Immutable dataclass containing backup information needed for
    restore and cleanup operations.

    Attributes:
        original_path: Path to the original file
        backup_path: Path to the backup file
        original_mode: Original file permissions (stat mode)
    """

    original_path: str
    backup_path: str
    original_mode: int


@dataclass(frozen=True)
class FolderContext:
    """Context for folder traversal operations.

    Used in functional folder size/count calculations to track state
    during recursive directory traversal.

    Attributes:
        visited_inodes: Set of (device, inode) tuples to detect cycles
        max_depth: Maximum recursion depth to prevent stack overflow
    """

    visited_inodes: Set[Tuple[int, int]]
    max_depth: int = 100

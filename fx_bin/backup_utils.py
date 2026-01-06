"""Shared backup utilities for file operations.

This module provides reusable backup functionality that can be used
across different modules (replace.py, replace_functional.py, etc.).

Functions follow functional patterns with IOResult for error handling.
"""

import os
import shutil
import stat

from loguru import logger as L
from returns.io import IOResult

from fx_bin.errors import IOError as FxIOError
from fx_bin.shared_types import FileBackup

# Re-export for backward compatibility
__all__ = ["FileBackup", "create_backup", "restore_from_backup", "cleanup_backup"]


def create_backup(filename: str) -> IOResult[FileBackup, FxIOError]:
    """Create a backup of the file.

    Creates a backup copy of the specified file with preserved metadata.
    The backup file is created with a ".backup" suffix.

    Args:
        filename: Path to the file to backup

    Returns:
        IOResult containing:
            - Success: FileBackup object with backup metadata
            - Failure: FxIOError if backup creation fails

    Example:
        >>> from fx_bin.lib import unsafe_ioresult_unwrap
        >>> result = create_backup("/path/to/file.txt")
        >>> backup = unsafe_ioresult_unwrap(result)
        >>> print(backup.backup_path)
        /path/to/file.txt.backup
    """
    try:
        # Get original file stats
        original_stat = os.stat(filename)
        original_mode = original_stat.st_mode

        # Create backup path
        backup_path = f"{filename}.backup"

        # Copy file with metadata
        shutil.copy2(filename, backup_path)

        return IOResult.from_value(
            FileBackup(
                original_path=filename,
                backup_path=backup_path,
                original_mode=original_mode,
            )
        )
    except Exception as e:
        return IOResult.from_failure(FxIOError(f"Failed to create backup: {e}"))


def restore_from_backup(backup: FileBackup) -> IOResult[None, FxIOError]:
    """Restore original file from backup on failure.

    Restores the original file from the backup copy and restores
    the original file permissions. Gracefully handles missing backup
    files (already cleaned up).

    Args:
        backup: FileBackup object containing backup metadata

    Returns:
        IOResult containing:
            - Success: None (restore succeeded or backup already cleaned up)
            - Failure: FxIOError if restore operation fails

    Example:
        >>> backup = FileBackup(...)
        >>> result = restore_from_backup(backup)
    """
    try:
        if os.path.exists(backup.backup_path):
            # Restore the backup
            shutil.move(backup.backup_path, backup.original_path)
            # Restore permissions
            os.chmod(backup.original_path, stat.S_IMODE(backup.original_mode))
        return IOResult.from_value(None)
    except Exception as e:
        return IOResult.from_failure(FxIOError(f"Failed to restore from backup: {e}"))


def cleanup_backup(backup: FileBackup) -> IOResult[None, FxIOError]:
    """Remove backup file after successful operation.

    Cleans up the backup file after a successful operation.
    Gracefully handles missing backup files (already cleaned up).
    This is a non-critical operation - failures are logged but don't
    fail the overall operation.

    Args:
        backup: FileBackup object containing backup metadata

    Returns:
        IOResult containing:
            - Success: None (cleanup succeeded or backup already gone)
            - Failure: Never fails - errors logged but returns Success

    Example:
        >>> backup = FileBackup(...)
        >>> result = cleanup_backup(backup)
    """
    try:
        if os.path.exists(backup.backup_path):
            os.unlink(backup.backup_path)
        return IOResult.from_value(None)
    except Exception as e:
        # Non-critical error - log but don't fail
        L.warning(f"Could not remove backup {backup.backup_path}: {e}")
        return IOResult.from_value(None)

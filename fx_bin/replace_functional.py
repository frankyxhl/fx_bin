"""Functional version of replace.py using returns library.

This module provides safe text replacement with atomic operations,
backup/restore, and functional error handling.
"""

import os
import shutil
import stat
import tempfile
from dataclasses import dataclass
from typing import List

import click
from loguru import logger as L
from returns.result import Result, Success, Failure
from returns.io import IOResult, impure_safe

from fx_bin.errors import ReplaceError, IOError as FxIOError


@dataclass(frozen=True)
class ReplaceContext:
    """Context for replacement operations."""
    search_text: str
    replace_text: str
    create_backup: bool = True
    preserve_permissions: bool = True


@dataclass(frozen=True)
class FileBackup:
    """Represents a file backup."""
    original_path: str
    backup_path: str
    original_mode: int


def validate_file_access(filename: str) -> Result[str, ReplaceError]:
    """Validate that we can access and modify the file."""
    try:
        # Check if file exists
        if not os.path.exists(filename):
            return Failure(ReplaceError(f"File not found: {filename}"))

        # Check if file is writable
        if not os.access(filename, os.W_OK):
            return Failure(ReplaceError(f"File is not writable: {filename}"))

        # Follow symlinks to get real path
        real_path = (
            os.path.realpath(filename)
            if os.path.islink(filename)
            else filename
        )

        return Success(real_path)
    except Exception as e:
        return Failure(ReplaceError(f"Error validating file access: {e}"))


@impure_safe
def create_backup(filename: str) -> IOResult[FileBackup, FxIOError]:
    """Create a backup of the file."""
    try:
        # Get original file stats
        original_stat = os.stat(filename)
        original_mode = original_stat.st_mode

        # Create backup path
        backup_path = f"{filename}.backup"

        # Copy file with metadata
        shutil.copy2(filename, backup_path)

        return IOResult.from_value(FileBackup(
            original_path=filename,
            backup_path=backup_path,
            original_mode=original_mode
        ))
    except Exception as e:
        return IOResult.from_failure(
            FxIOError(f"Failed to create backup: {e}")
        )


@impure_safe
def perform_replacement(
    context: ReplaceContext,
    backup: FileBackup
) -> IOResult[str, FxIOError]:
    """Perform the actual text replacement."""
    try:
        # Create temporary file in same directory for atomic move
        temp_dir = os.path.dirname(os.path.abspath(backup.original_path))
        fd, tmp_path = tempfile.mkstemp(dir=temp_dir, prefix='.tmp_replace_')

        try:
            # Perform replacement
            with os.fdopen(fd, 'w', encoding='utf-8') as tmp_file:
                with open(
                    backup.original_path, 'r', encoding='utf-8'
                ) as original_file:
                    for line in original_file:
                        modified_line = line.replace(
                            context.search_text, context.replace_text
                        )
                        tmp_file.write(modified_line)

            # Preserve permissions if requested
            if context.preserve_permissions:
                os.chmod(tmp_path, stat.S_IMODE(backup.original_mode))

            # Atomic replacement
            if os.name == 'nt':  # Windows
                # Windows doesn't support atomic rename to existing file
                os.unlink(backup.original_path)
                os.rename(tmp_path, backup.original_path)
            else:  # Unix-like
                os.rename(tmp_path, backup.original_path)

            return IOResult.from_value(backup.original_path)

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e

    except Exception as e:
        return IOResult.from_failure(
            FxIOError(f"Failed to perform replacement: {e}")
        )


@impure_safe
def cleanup_backup(backup: FileBackup) -> IOResult[None, FxIOError]:
    """Remove backup file after successful operation."""
    try:
        if os.path.exists(backup.backup_path):
            os.unlink(backup.backup_path)
        return IOResult.from_value(None)
    except Exception as e:
        # Non-critical error - log but don't fail
        L.warning(f"Could not remove backup {backup.backup_path}: {e}")
        return IOResult.from_value(None)


@impure_safe
def restore_from_backup(backup: FileBackup) -> IOResult[None, FxIOError]:
    """Restore original file from backup on failure."""
    try:
        if os.path.exists(backup.backup_path):
            # Restore the backup
            shutil.move(backup.backup_path, backup.original_path)
            # Restore permissions
            os.chmod(backup.original_path, stat.S_IMODE(backup.original_mode))
        return IOResult.from_value(None)
    except Exception as e:
        return IOResult.from_failure(
            FxIOError(f"Failed to restore from backup: {e}")
        )


def work_functional(
    search_text: str,
    replace_text: str,
    filename: str
) -> IOResult[None, ReplaceError]:
    """
    Replace text in a file with functional error handling.

    This function performs atomic replacement with automatic backup/restore
    on failure, using functional composition.
    """
    # Validate file access (pure)
    validation = validate_file_access(filename)
    if isinstance(validation, Failure):
        return IOResult.from_failure(validation.failure())

    real_path = validation.unwrap()
    context = ReplaceContext(search_text, replace_text)

    # Create backup (IO)
    backup_result = create_backup(real_path)

    # Perform replacement with automatic restore on failure
    def replace_with_restore(
        backup: FileBackup
    ) -> IOResult[None, ReplaceError]:
        replacement_result = perform_replacement(context, backup)

        # Check the inner value without running
        if isinstance(replacement_result._inner_value, Failure):
            # Restore from backup on failure
            restore_from_backup(backup)
            # Return original error
            return IOResult.from_failure(
                ReplaceError(
                    f"Replacement failed: "
                    f"{replacement_result._inner_value.failure()}"
                )
            )

        # Success - cleanup backup
        cleanup_backup(backup)
        return IOResult.from_value(None)

    return backup_result.bind(replace_with_restore)


def work_batch_functional(
    search_text: str,
    replace_text: str,
    filenames: List[str]
) -> IOResult[List[Result[str, ReplaceError]], ReplaceError]:
    """
    Replace text in multiple files with transaction-like behavior.

    All files are processed, but if any fail, all are restored.
    """
    results = []
    backups = []

    # Phase 1: Validate all files
    for filename in filenames:
        validation = validate_file_access(filename)
        if isinstance(validation, Failure):
            return IOResult.from_failure(validation.failure())

    # Phase 2: Create backups for all files
    for filename in filenames:
        backup_result = create_backup(filename)
        if isinstance(backup_result.run(), Failure):
            # Restore any backups already created
            for backup in backups:
                restore_from_backup(backup)
            return IOResult.from_failure(
                ReplaceError(f"Failed to create backup for {filename}")
            )
        backups.append(backup_result.run().unwrap())

    # Phase 3: Perform replacements
    context = ReplaceContext(search_text, replace_text)
    failed = False

    for backup in backups:
        result = perform_replacement(context, backup)
        if isinstance(result.run(), Failure):
            failed = True
            results.append(Failure(ReplaceError(str(result.run().failure()))))
        else:
            results.append(Success(backup.original_path))

    # Phase 4: Commit or rollback
    if failed:
        # Rollback all changes
        for backup in backups:
            restore_from_backup(backup)
        return IOResult.from_failure(
            ReplaceError("Batch replacement failed - all changes rolled back")
        )
    else:
        # Cleanup all backups
        for backup in backups:
            cleanup_backup(backup)
        return IOResult.from_value(results)


# Legacy compatibility wrapper
def work(search_text: str, replace_text: str, filename: str) -> None:
    """Legacy interface for backward compatibility."""
    result = work_functional(search_text, replace_text, filename).run()

    if isinstance(result, Failure):
        error = result.failure()
        raise Exception(str(error))


@click.command()
@click.argument("search_text", nargs=1)
@click.argument("replace_text", nargs=1)
@click.argument("filenames", nargs=-1, required=True)
def main(search_text: str, replace_text: str, filenames: tuple) -> None:
    """
    Replace text in files with functional error handling.

    This CLI maintains backward compatibility while using functional internals.
    """
    L.info(f"search_text: {search_text}")
    L.info(f"replace_text: {replace_text}")

    if len(filenames) == 1:
        # Single file replacement
        result = work_functional(
            search_text, replace_text, filenames[0]
        ).run()

        if isinstance(result, Failure):
            L.error(f"Replacement failed: {result.failure()}")
            raise SystemExit(1)
        else:
            L.info(f"Successfully replaced in {filenames[0]}")
    else:
        # Batch replacement with transaction semantics
        result = work_batch_functional(
            search_text, replace_text, list(filenames)
        ).run()

        if isinstance(result, Failure):
            L.error(f"Batch replacement failed: {result.failure()}")
            raise SystemExit(1)
        else:
            success_count = sum(
                1 for r in result.unwrap() if isinstance(r, Success)
            )
            L.info(
                f"Successfully replaced in {success_count}/"
                f"{len(filenames)} files"
            )


if __name__ == "__main__":
    main()

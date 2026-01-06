"""Functional version of replace.py using returns library.

This module provides safe text replacement with atomic operations,
backup/restore, and functional error handling.

Error Hierarchy:
    FileOperationError (base for all file operations)
    ├── ReplaceError (text replacement errors)
    └── IOError (file I/O errors)

This hierarchy enables polymorphic error handling - you can catch
FileOperationError to handle all file-related errors, or catch
specific error types for more precise error recovery.
"""

import os
import stat
import tempfile
from dataclasses import dataclass
from functools import partial
from typing import List, Callable, Sequence

import click
from loguru import logger as L
from returns.result import Result, Success, Failure
from returns.io import IOResult
from returns.pipeline import flow
from returns.pointfree import bind, lash

from fx_bin.backup_utils import (
    FileBackup,
    create_backup,
    restore_from_backup,
    cleanup_backup,
)
from fx_bin.errors import ReplaceError, IOError as FxIOError, SecurityError
from .lib import unsafe_ioresult_to_result, unsafe_ioresult_unwrap


def _is_binary_file(file_path: str, sample_size: int = 8192) -> bool:
    """Check if a file appears to be binary by looking for null bytes.

    Args:
        file_path: Path to the file to check.
        sample_size: Number of bytes to read for detection (default: 8192).

    Returns:
        True if the file appears to be binary, False otherwise.
        Unreadable files are treated as binary (skipped).
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)
            return b"\x00" in chunk
    except (OSError, IOError):
        return True  # Treat unreadable files as binary (skip them)


@dataclass(frozen=True)
class ReplaceContext:
    """Context for replacement operations."""

    search_text: str
    replace_text: str
    create_backup: bool = True
    preserve_permissions: bool = True


def validate_file_access(
    filename: str, allowed_base: str | None = None
) -> Result[str, ReplaceError | SecurityError]:
    """Validate that we can access and modify the file.

    Args:
        filename: Path to the file to validate
        allowed_base: Optional base directory to restrict file access.
                     If provided, the file must be within this directory tree.
                     This prevents path traversal attacks.

    Returns:
        Result containing:
            - Success: Real path to the file (with symlinks resolved)
            - Failure: ReplaceError for file access issues,
                      SecurityError for path traversal attempts

    Security:
        When allowed_base is provided, this function prevents:
        - Parent directory traversal (../../../etc/passwd)
        - Absolute paths outside allowed base
        - Symlinks pointing outside allowed base
    """
    try:
        # Resolve to real path (normalize and prepare for security check)
        # Always normalize first to handle '..' and '.' components
        normalized = os.path.normpath(filename)

        # Then resolve to absolute path
        # For existing paths: realpath also follows symlinks
        # For non-existent paths: abspath provides absolute form
        if os.path.exists(normalized):
            real_path = os.path.realpath(normalized)
        else:
            real_path = os.path.abspath(normalized)

        # SECURITY: Path traversal check BEFORE file existence check
        # This prevents attackers from probing which files exist outside allowed base
        if allowed_base is not None:
            real_base = os.path.realpath(allowed_base)

            # Check if real_path is within allowed_base directory tree
            try:
                # os.path.commonpath raises ValueError if paths are on different drives
                common = os.path.commonpath([real_base, real_path])

                # File must be within base directory
                if common != real_base:
                    return Failure(
                        SecurityError(
                            f"Path traversal attempt: {filename} is outside "
                            f"allowed directory {allowed_base}"
                        )
                    )
            except ValueError:
                # Different drives or no common path - definitely outside base
                return Failure(
                    SecurityError(
                        f"Path traversal attempt: {filename} is outside "
                        f"allowed directory {allowed_base}"
                    )
                )

        # After security checks, verify file exists and is accessible
        # Use normalized path for existence check (handles .. and .)
        if not os.path.exists(normalized):
            return Failure(ReplaceError(f"File not found: {filename}"))

        # Check if file is writable (use normalized path)
        if not os.access(normalized, os.W_OK):
            return Failure(ReplaceError(f"File is not writable: {filename}"))

        # Re-resolve to real path for existing file (may differ from abspath)
        real_path = os.path.realpath(normalized)

        return Success(real_path)
    except Exception as e:
        return Failure(ReplaceError(f"Error validating file access: {e}"))


def perform_replacement(
    context: ReplaceContext, backup: FileBackup
) -> IOResult[str, FxIOError]:
    """Perform the actual text replacement."""
    try:
        # Create temporary file in same directory for atomic move
        temp_dir = os.path.dirname(os.path.abspath(backup.original_path))
        fd, tmp_path = tempfile.mkstemp(dir=temp_dir, prefix=".tmp_replace_")

        try:
            # Perform replacement
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                with open(backup.original_path, "r", encoding="utf-8") as original_file:
                    for line in original_file:
                        modified_line = line.replace(
                            context.search_text, context.replace_text
                        )
                        tmp_file.write(modified_line)

            # Preserve permissions if requested
            if context.preserve_permissions:
                os.chmod(tmp_path, stat.S_IMODE(backup.original_mode))

            # Atomic replacement
            if os.name == "nt":  # Windows
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
        return IOResult.from_failure(FxIOError(f"Failed to perform replacement: {e}"))


def _handle_replacement_failure(
    backup: FileBackup, error: ReplaceError
) -> IOResult[None, ReplaceError]:
    """Restore backup when replacement fails."""
    restore_from_backup(backup)
    return IOResult.from_failure(ReplaceError(f"Replacement failed: {error}"))


def _handle_replacement_success(
    backup: FileBackup, _: None
) -> IOResult[None, ReplaceError]:
    """Cleanup backup when replacement succeeds."""
    cleanup_backup(backup)
    return IOResult.from_value(None)


def _make_replacement_pipeline(
    context: ReplaceContext,
) -> Callable[[FileBackup], IOResult[None, ReplaceError]]:
    """Create a replacement pipeline for a given context.

    This factory function returns a pipeline that takes a FileBackup
    and performs the replacement with error recovery.

    Uses partial application to avoid lambda functions while maintaining
    access to the backup parameter in error/success handlers.
    """

    def execute_replacement(backup: FileBackup) -> IOResult[None, ReplaceError]:
        """Execute replacement with automatic error recovery and cleanup.

        Railway-Oriented Programming pattern:
        - SUCCESS track: perform_replacement → handle_success → cleanup backup
        - FAILURE track: perform_replacement → handle_failure → restore backup
        """
        # Use partial to "bake in" the backup parameter
        # Avoids lambdas: partial(func, arg1) vs lambda x: func(arg1, x)
        handle_failure = partial(_handle_replacement_failure, backup)
        handle_success = partial(_handle_replacement_success, backup)

        return flow(
            perform_replacement(context, backup),  # Try replacement (IOResult)
            lash(handle_failure),  # If failed, restore from backup
            bind(handle_success),  # If succeeded, cleanup backup
        )

    return execute_replacement


def work_functional(
    search_text: str, replace_text: str, filename: str
) -> IOResult[None, ReplaceError]:
    """
    Replace text in a file with functional error handling.

    This function performs atomic replacement with automatic backup/restore
    on failure, using functional pipeline composition.

    Railway-Oriented Programming:
    1. Pure validation first (fail fast before any IO)
    2. Skip binary files (prevents UnicodeDecodeError)
    3. IO pipeline: create_backup → replacement → cleanup/restore
    4. Automatic error recovery (restore on failure)
    """
    # Step 1: Validate file access (pure function, no side effects)
    # Returns Result[str, ReplaceError] - either valid path or error
    validation = validate_file_access(filename)
    if isinstance(validation, Failure):
        # Short-circuit: return failure without doing any IO
        return IOResult.from_failure(validation.failure())

    real_path = validation.unwrap()

    # Step 2: Skip binary files (same behavior as imperative version)
    # Binary files would cause UnicodeDecodeError - skip them silently
    if _is_binary_file(real_path):
        return IOResult.from_value(None)  # Success: skipped binary file

    # Step 3: Create immutable context
    context = ReplaceContext(search_text, replace_text)

    # Step 4: Functional pipeline with automatic error recovery
    # Pipeline: create backup → perform replacement → cleanup (or restore on error)
    replacement_pipeline = _make_replacement_pipeline(context)

    return flow(
        create_backup(real_path),  # IOResult[FileBackup, ReplaceError]
        bind(replacement_pipeline),  # Success: cleanup, Failure: restore
    )


def work_batch_functional(
    search_text: str, replace_text: str, filenames: List[str]
) -> IOResult[List[Result[str, ReplaceError]], ReplaceError]:
    """Replace text in multiple files with transaction-like behavior.

    All files are processed, but if any fail, all are restored.
    Uses Railway-Oriented Programming principles with proper error handling.

    Args:
        search_text: Text to search for in files
        replace_text: Text to replace search_text with
        filenames: List of file paths to process

    Returns:
        IOResult containing:
            - Success: List of Results for each file (path or error)
            - Failure: ReplaceError if validation or backup fails

    Note:
        Transaction semantics: Either all files succeed or all are rolled back.
        Individual file failures are collected, but trigger rollback.
    """
    # Phase 1: Validate all files (fail fast)
    for filename in filenames:
        validation = validate_file_access(filename)
        if isinstance(validation, Failure):
            return IOResult.from_failure(validation.failure())

    # Phase 2: Create backups for all files
    backups: List[FileBackup] = []
    for filename in filenames:

        backup_result = create_backup(filename)
        # Use helper to unpack IOResult safely
        if isinstance(unsafe_ioresult_to_result(backup_result), Failure):
            # Rollback: restore any backups already created
            for backup in backups:
                restore_from_backup(backup)
            return IOResult.from_failure(
                ReplaceError(f"Failed to create backup for {filename}")
            )
        # Extract successful backup
        backups.append(unsafe_ioresult_unwrap(backup_result))

    # Phase 3: Perform replacements with result collection
    context = ReplaceContext(search_text, replace_text)
    results: List[Result[str, ReplaceError]] = []
    failed = False

    for backup in backups:
        result = perform_replacement(context, backup)
        # Check if replacement succeeded
        result_inner = unsafe_ioresult_to_result(result)
        if isinstance(result_inner, Failure):
            failed = True
            error = result_inner.failure()
            results.append(Failure(ReplaceError(str(error))))
        else:
            results.append(Success(backup.original_path))

    # Phase 4: Commit or rollback based on results
    if failed:

        # Rollback: restore all files from backups
        for backup in backups:
            restore_from_backup(backup)
        return IOResult.from_failure(
            ReplaceError("Batch replacement failed - all changes rolled back")
        )

    # Commit: cleanup all backups
    for backup in backups:
        cleanup_backup(backup)
    return IOResult.from_value(results)


# Legacy compatibility wrapper
def work(search_text: str, replace_text: str, filename: str) -> None:
    """Legacy interface for backward compatibility."""
    result = unsafe_ioresult_to_result(
        work_functional(search_text, replace_text, filename)
    )

    if isinstance(result, Failure):
        error = result.failure()
        raise Exception(str(error))


@click.command()
@click.argument("search_text", nargs=1)
@click.argument("replace_text", nargs=1)
@click.argument("filenames", nargs=-1, required=True)
def main(search_text: str, replace_text: str, filenames: Sequence[str]) -> None:
    """
    Replace text in files with functional error handling.

    This CLI maintains backward compatibility while using functional internals.
    """
    L.info(f"search_text: {search_text}")
    L.info(f"replace_text: {replace_text}")

    if len(filenames) == 1:
        # Single file replacement
        single_result = unsafe_ioresult_to_result(
            work_functional(search_text, replace_text, filenames[0])
        )

        if isinstance(single_result, Failure):
            L.error(f"Replacement failed: {single_result.failure()}")
            raise SystemExit(1)
        else:
            L.info(f"Successfully replaced in {filenames[0]}")
    else:
        # Batch replacement with transaction semantics
        batch_result = unsafe_ioresult_to_result(
            work_batch_functional(search_text, replace_text, list(filenames))
        )

        if isinstance(batch_result, Failure):

            L.error(f"Batch replacement failed: {batch_result.failure()}")
            raise SystemExit(1)
        else:
            success_count = len(
                [r for r in batch_result.unwrap() if isinstance(r, Success)]
            )
            L.info(
                f"Successfully replaced in {success_count}/" f"{len(filenames)} files"
            )


if __name__ == "__main__":
    main()

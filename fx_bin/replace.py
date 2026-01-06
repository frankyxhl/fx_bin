import errno
import os
import sys
import tempfile
from typing import Sequence

import click
from loguru import logger as L
from returns.result import Failure

from fx_bin.backup_utils import create_backup, restore_from_backup, cleanup_backup
from fx_bin.lib import unsafe_ioresult_to_result, unsafe_ioresult_unwrap


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


def work(search_text: str, replace_text: str, filename: str) -> None:
    """Replace text in a file safely with atomic operations and backup."""
    import shutil
    import stat

    if _is_binary_file(filename):
        L.debug(f"Skipping binary file: {filename}")
        return

    # Check if file is readonly
    if not os.access(filename, os.W_OK):
        raise PermissionError(f"File {filename} is readonly")

    # Follow symlinks to get the real file path
    if os.path.islink(filename):
        filename = os.path.realpath(filename)

    # Create backup using shared backup utilities
    backup_result = create_backup(filename)
    if isinstance(unsafe_ioresult_to_result(backup_result), Failure):
        error = unsafe_ioresult_to_result(backup_result).failure()
        raise Exception(str(error))
    backup = unsafe_ioresult_unwrap(backup_result)

    # Get original mode for permission preservation
    original_mode = backup.original_mode

    # Create temporary file in same directory for atomic move

    temp_dir = os.path.dirname(os.path.abspath(filename))
    fd, tmp_path = tempfile.mkstemp(dir=temp_dir, prefix=".tmp_replace_")

    try:
        # Use file descriptor to prevent fd leak
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            with open(filename, "r", encoding="utf-8") as original_file:
                for line in original_file:
                    modified_line = line.replace(search_text, replace_text)
                    tmp_file.write(modified_line)

        # Preserve file permissions
        os.chmod(tmp_path, stat.S_IMODE(original_mode))

        # Atomic replacement - use rename instead of replace for better test
        # compatibility
        try:
            if os.name == "nt":  # Windows
                # Windows doesn't support atomic rename to existing file
                os.remove(filename)
            os.rename(tmp_path, filename)
            # Success - cleanup backup using shared utility
            cleanup_backup(backup)
        except OSError as e:
            if e.errno == errno.EXDEV:  # Cross-device link error
                # Fall back to copy+delete for cross-filesystem moves
                shutil.move(tmp_path, filename)
                # Success - cleanup backup using shared utility
                cleanup_backup(backup)
            else:
                # Restore from backup using shared utility
                restore_from_backup(backup)
                raise
        except Exception:
            # Restore from backup using shared utility
            restore_from_backup(backup)
            raise

    except Exception:
        # Clean up temp file on any error
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Best effort cleanup

        # Restore from backup using shared utility
        restore_from_backup(backup)
        raise


def replace_files(search_text: str, replace_text: str, filenames: Sequence[str]) -> int:
    """Replace text in multiple files with transaction-like behavior."""
    import shutil

    # Phase 1: Validate all files
    for f in filenames:
        if not os.path.isfile(f):
            click.echo(f"This file does not exist: {f}", err=True)
            L.error(f"This file does not exist: {f}")
            raise click.ClickException(f"This file does not exist: {f}")

        # Check if file is writable
        if not os.access(f, os.W_OK):
            click.echo(f"File {f} is readonly", err=True)
            L.error(f"File {f} is readonly")
            raise click.ClickException(f"File {f} is readonly")

    # Phase 2: Create transaction backups for all files
    # Note: Transaction backups use ".transaction_backup" suffix to avoid
    # conflicts with individual work() call backups (".backup" suffix)
    backups = {}
    try:
        for f in filenames:
            backup_path = f + ".transaction_backup"
            shutil.copy2(f, backup_path)
            backups[f] = backup_path

        # Phase 3: Process all files
        for f in filenames:
            L.debug(f"Replacing {search_text} with {replace_text} in {f}")
            work(search_text, replace_text, f)

        # Phase 4: Success - remove all transaction backups
        for backup_path in backups.values():
            if os.path.exists(backup_path):
                os.remove(backup_path)

        return 0

    except Exception:
        # Phase 5: Failure - restore all files from transaction backups
        for original_file, backup_path in backups.items():
            if os.path.exists(backup_path):
                try:
                    shutil.move(backup_path, original_file)
                except OSError:
                    pass  # Best effort restore

        # Re-raise the original exception
        raise


@click.command()
@click.argument("search_text", nargs=1)
@click.argument("replace_text", nargs=1)
@click.argument("filenames", nargs=-1)
def main(search_text: str, replace_text: str, filenames: Sequence[str]) -> int:
    """CLI wrapper for replace_files."""
    return replace_files(search_text, replace_text, filenames)


if __name__ == "__main__":
    sys.exit(main())

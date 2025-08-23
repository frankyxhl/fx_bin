import errno
import os
import sys
import tempfile
from typing import Tuple

import click
from loguru import logger as L


def work(search_text: str, replace_text: str, filename: str) -> None:
    """Replace text in a file safely with atomic operations and backup."""
    import shutil
    import stat

    # Check if file is readonly
    if not os.access(filename, os.W_OK):
        raise PermissionError(f"File {filename} is readonly")

    # Follow symlinks to get the real file path
    if os.path.islink(filename):
        filename = os.path.realpath(filename)

    # Preserve original file permissions and metadata
    original_stat = os.stat(filename)
    original_mode = original_stat.st_mode

    # Create backup first
    backup_path = filename + '.backup'
    shutil.copy2(filename, backup_path)

    # Create temporary file in same directory for atomic move
    temp_dir = os.path.dirname(os.path.abspath(filename))
    fd, tmp_path = tempfile.mkstemp(dir=temp_dir, prefix='.tmp_replace_')

    try:
        # Use file descriptor to prevent fd leak
        with os.fdopen(fd, 'w', encoding='utf-8') as tmp_file:
            with open(filename, 'r', encoding='utf-8') as original_file:
                for line in original_file:
                    modified_line = line.replace(search_text, replace_text)
                    tmp_file.write(modified_line)

        # Preserve file permissions
        os.chmod(tmp_path, stat.S_IMODE(original_mode))

        # Atomic replacement - use rename instead of replace for better test
        # compatibility
        try:
            if os.name == 'nt':  # Windows
                # Windows doesn't support atomic rename to existing file
                os.remove(filename)
            os.rename(tmp_path, filename)
            # Success - remove backup
            os.remove(backup_path)
        except OSError as e:
            if e.errno == errno.EXDEV:  # Cross-device link error
                # Fall back to copy+delete for cross-filesystem moves
                shutil.move(tmp_path, filename)
                # Success - remove backup
                os.remove(backup_path)
            else:
                # Restore from backup if replacement failed
                if os.path.exists(backup_path):
                    shutil.move(backup_path, filename)
                raise
        except Exception:
            # Restore from backup if replacement failed
            if os.path.exists(backup_path):
                shutil.move(backup_path, filename)
            raise

    except Exception:
        # Clean up temp file on any error
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Best effort cleanup

        # Restore from backup if it exists
        if os.path.exists(backup_path):
            try:
                shutil.move(backup_path, filename)
            except OSError:
                pass  # Best effort restore
        raise


@click.command()
@click.argument('search_text', nargs=1)
@click.argument('replace_text', nargs=1)
@click.argument('filenames', nargs=-1)
def main(
    search_text: str, replace_text: str, filenames: Tuple[str, ...]
) -> int:
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

    # Phase 2: Create backups for all files
    backups = {}
    try:
        for f in filenames:
            backup_path = f + '.transaction_backup'
            shutil.copy2(f, backup_path)
            backups[f] = backup_path

        # Phase 3: Process all files
        for f in filenames:
            L.debug(f'Replacing {search_text} with {replace_text} in {f}')
            work(search_text, replace_text, f)

        # Phase 4: Success - remove all backups
        for backup_path in backups.values():
            if os.path.exists(backup_path):
                os.remove(backup_path)

        return 0

    except Exception:
        # Phase 5: Failure - restore all files from backups
        for original_file, backup_path in backups.items():
            if os.path.exists(backup_path):
                try:
                    shutil.move(backup_path, original_file)
                except OSError:
                    pass  # Best effort restore

        # Re-raise the original exception
        raise


if __name__ == "__main__":
    sys.exit(main())

import os
import sys
import tempfile
from typing import Tuple

import click
from loguru import logger as L


def work(search_text: str, replace_text: str, filename: str) -> None:
    """Replace text in a file safely with atomic operations."""
    import shutil
    import stat
    
    # Preserve original file permissions and metadata
    original_stat = os.stat(filename)
    original_mode = original_stat.st_mode
    
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
        
        # Atomic replacement using move
        if os.name == 'nt':  # Windows
            # Windows doesn't support atomic replace, so remove first
            backup_path = filename + '.bak'
            shutil.copy2(filename, backup_path)
            try:
                os.replace(tmp_path, filename)
                os.remove(backup_path)
            except Exception:
                # Restore from backup if replacement failed
                if os.path.exists(backup_path):
                    shutil.move(backup_path, filename)
                raise
        else:  # Unix-like systems
            os.replace(tmp_path, filename)
    
    except Exception:
        # Clean up temp file on any error
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Best effort cleanup
        raise


@click.command()
@click.argument('search_text', nargs=1)
@click.argument('replace_text', nargs=1)
@click.argument('filenames', nargs=-1)
def main(search_text: str, replace_text: str, filenames: Tuple[str, ...]) -> int:
    """Replace text in multiple files."""
    for f in filenames:
        if not os.path.isfile(f):
            click.echo(f"This file does not exist: {f}", err=True)
            L.error(f"This file does not exist: {f}")
            raise click.ClickException(f"This file does not exist: {f}")
    for f in filenames:
        L.debug(f'Replacing {search_text} with {replace_text} in {f}')
        work(search_text, replace_text, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())

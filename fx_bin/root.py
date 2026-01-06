"""Find Git project root directory.

This module provides functionality to find the root directory of a Git repository
by walking up the directory tree from the current location.
"""

import sys
from pathlib import Path
from typing import Optional

import click


def find_git_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """Find the root directory of a Git repository.

    Args:
        start_path: Directory to start searching from. If None, uses current directory.

    Returns:
        Path to Git repository root, or None if not found.
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    current = start_path

    while True:
        git_dir = current / ".git"
        if git_dir.exists():
            return current

        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    return None


@click.command()
@click.option(
    "--cd",
    "-c",
    "output_for_cd",
    is_flag=True,
    help="Output path suitable for cd command (no extra text)",
)
def main(output_for_cd: bool) -> None:
    """Find and display Git project root directory.

    Searches upward from current directory to find the first directory
    containing a .git folder.

    Examples:
        fx root              # Show root directory with description
        fx root --cd         # Output just the path for cd command
        cd "$(fx root --cd)" # Change to root directory
    """
    try:
        git_root = find_git_root()

        if git_root is None:
            if not output_for_cd:
                click.echo(
                    "Error: No git repository found in current directory "
                    "or parent directories",
                    err=True,
                )
            sys.exit(1)

        if output_for_cd:
            # Just output the path for shell usage
            click.echo(str(git_root))
        else:
            # Friendly output with description
            click.echo(f"Git project root: {git_root}")

    except PermissionError as e:
        if not output_for_cd:
            click.echo(f"Error: Permission denied accessing directory: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if not output_for_cd:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

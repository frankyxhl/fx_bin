"""File and directory size listing utility."""
import os
from typing import List

from .common import SizeEntry

__all__ = ["list_size"]


def list_size(
    path: str = '.', ignore_dot_file: bool = True
) -> List[SizeEntry]:
    """
    List sizes of files and directories in the given path.

    Args:
        path: Directory path to analyze
        ignore_dot_file: Whether to ignore files/dirs starting with dot

    Returns:
        Sorted list of SizeEntry objects
    """
    result = []
    for entry in os.scandir(path):
        if ignore_dot_file and entry.name.startswith("."):
            continue
        size_entry = SizeEntry.from_scandir(entry)
        if size_entry is not None:
            result.append(size_entry)
    result.sort()
    return result


def main():
    """Main entry point for fx_size command."""
    import click

    @click.command()
    @click.option('--path', '-p', default='.', help='Path to analyze')
    @click.option(
        '--all', '-a', 'show_all', is_flag=True, help='Show hidden files'
    )
    def cli(path, show_all):
        """Display file and directory sizes in human-readable format."""
        lst = list_size(path, ignore_dot_file=not show_all)
        for entry in lst:
            click.echo(entry)

    cli()


if __name__ == '__main__':
    main()

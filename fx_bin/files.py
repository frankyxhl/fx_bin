#!/usr/bin/env python3
"""File counting utility."""
import os
from typing import List

from .common import FileCountEntry

__all__ = ["list_files_count"]


def list_files_count(
    path: str = '.', ignore_dot_file: bool = True
) -> List[FileCountEntry]:
    """
    Count files in directories.

    Args:
        path: Directory path to analyze
        ignore_dot_file: Whether to ignore files/dirs starting with dot

    Returns:
        Sorted list of FileCountEntry objects
    """
    result = []
    for entry in os.scandir(path):
        if ignore_dot_file and entry.name.startswith('.'):
            continue
        file_entry = FileCountEntry.from_scandir(entry)
        if file_entry is not None:
            result.append(file_entry)
    result.sort()
    return result


def main():
    """Main entry point for fx_files command."""
    import click

    @click.command()
    @click.option('--path', '-p', default='.', help='Path to analyze')
    @click.option(
        '--all', '-a', 'show_all', is_flag=True, help='Show hidden files'
    )
    def cli(path, show_all):
        """Count and display files in directories."""
        lst = list_files_count(path, ignore_dot_file=not show_all)

        if lst:
            # Calculate max width for count display
            max_count = max(entry.count for entry in lst)
            count_width = len(str(max_count))

            for entry in lst:
                click.echo(entry.display(count_width))
        else:
            click.echo("No files or directories found.")

    cli()


if __name__ == '__main__':
    main()

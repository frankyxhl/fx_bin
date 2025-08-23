#!/usr/bin/env python
"""Main CLI entry point for fx commands."""

import click
import sys
from typing import List, Tuple

# Command metadata for the list command
COMMANDS_INFO: List[Tuple[str, str]] = [
    ("files", "Count files in directories"),
    ("size", "Analyze file/directory sizes"),
    ("ff", "Find files by keyword"),
    ("replace", "Replace text in files"),
    ("json2excel", "Convert JSON to Excel"),
    ("upgrade", "Run upgrade program"),
    ("list", "List all available commands"),
]


@click.group(invoke_without_command=True, context_settings={'help_option_names': ['-h', '--help']})
@click.version_option()
@click.pass_context
def cli(ctx):
    """FX - A collection of file and text utilities.
    
    Use 'fx COMMAND --help' for more information on a specific command.
    """
    if ctx.invoked_subcommand is None:
        # If no subcommand is provided, show help
        click.echo(ctx.get_help())


@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
def files(paths):
    """Count files in directories.
    
    Examples:
        fx files          # Count files in current directory
        fx files /path    # Count files in specified path
    """
    from . import files as files_module
    # Convert tuple to list for compatibility
    paths_list = list(paths) if paths else ['.']
    # Call the list_files_count function with the paths
    for path in paths_list:
        files_list = files_module.list_files_count(path)
        for file_info in files_list:
            click.echo(file_info)
    return 0


@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
def size(paths):
    """Analyze file and directory sizes.
    
    Examples:
        fx size           # Show sizes in current directory
        fx size /path     # Show sizes in specified path
    """
    from . import size as size_module
    
    paths_list = list(paths) if paths else ['.']
    
    for path in paths_list:
        if len(paths_list) > 1:
            click.echo(f"\n{path}:")
        
        entries = size_module.list_size(path)
        if entries:
            for entry in entries:
                click.echo(entry)
        else:
            click.echo(f"No accessible files or directories in {path}")
    
    return 0


@cli.command()
@click.argument('keyword')
def ff(keyword):
    """Find files by keyword.
    
    Examples:
        fx ff config      # Find files containing 'config'
        fx ff "*.py"      # Find Python files
    """
    from . import find_files
    
    if not keyword or keyword.strip() == "":
        click.echo("Please type text to search. For example: fx ff bar", err=True)
        click.echo("Usage: fx ff KEYWORD", err=True)
        return 1
    find_files.find_files(keyword)
    return 0


@cli.command()
@click.argument('search_text')
@click.argument('replace_text')
@click.argument('filenames', nargs=-1, required=True)
def replace(search_text, replace_text, filenames):
    """Replace text in files.
    
    Examples:
        fx replace "old" "new" file.txt   # Replace in specific file
        fx replace "old" "new" *.txt      # Replace in multiple files
    """
    from . import replace as replace_module
    
    # Call the existing replace module's main function
    return replace_module.main(search_text, replace_text, filenames)


@cli.command()
@click.argument('url')
@click.argument('output_filename')
def json2excel(url, output_filename):
    """Convert JSON data to Excel file.
    
    Examples:
        fx json2excel data.json output.xlsx
        fx json2excel https://api.example.com/data output.xlsx
    """
    from . import pd
    # Call the existing main function from pd module
    return pd.main(url, output_filename)


@cli.command()
def upgrade():
    """Run the upgrade program."""
    from . import run_upgrade_program
    return run_upgrade_program.main()


@cli.command(name='list')
def list_commands():
    """List all available fx commands."""
    click.echo("\nAvailable fx commands:\n")
    
    # Calculate maximum command length for alignment
    max_len = max(len(cmd) for cmd, _ in COMMANDS_INFO)
    
    for cmd, description in COMMANDS_INFO:
        # Format with aligned descriptions
        click.echo(f"  fx {cmd:<{max_len}}  - {description}")
    
    click.echo("\nUse 'fx COMMAND --help' for more information on a specific command.")
    return 0


def main():
    """Main entry point for the fx command."""
    try:
        return cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
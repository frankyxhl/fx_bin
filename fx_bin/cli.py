#!/usr/bin/env python
"""Main CLI entry point for fx commands."""

import click
import sys
from typing import List, Tuple
import importlib.metadata

def get_version_info() -> str:
    """Get version information."""
    try:
        version = importlib.metadata.version("fx-bin")
        return f"""FX-Bin v{version}
Repository: https://github.com/frankyxhl/fx_bin"""
    except Exception:
        return "fx-bin (development version)"


# Command metadata for the list command
COMMANDS_INFO: List[Tuple[str, str]] = [
    ("files", "Count files in directories"),
    ("size", "Analyze file/directory sizes"),
    ("ff", "Find files by keyword"),
    ("filter", "Filter files by extension"),
    ("replace", "Replace text in files"),
    ("json2excel", "Convert JSON to Excel"),
    ("list", "List all available commands"),
    ("help", "Show help information (same as fx -h)"),
    ("version", "Show version and system information"),
]


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(version=None, message=get_version_info())
@click.pass_context
def cli(ctx):
    """FX - A collection of file and text utilities.

    Common commands:

    \b
      fx help      Show this help
      fx list      Show all commands  
      fx version   Show version info

    Use 'fx COMMAND --help' for more information on a specific command.
    """
    if ctx.invoked_subcommand is None:
        # If no subcommand is provided, show help
        click.echo(ctx.get_help())


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def files(paths):
    """Count files in directories.

    Examples:
        fx files          # Count files in current directory
        fx files /path    # Count files in specified path
    """
    from . import files as files_module

    # Convert tuple to list for compatibility
    paths_list = list(paths) if paths else ["."]
    # Call the list_files_count function with the paths
    for path in paths_list:
        files_list = files_module.list_files_count(path)
        if files_list:
            # Calculate max width for count display
            max_count = max(entry.count for entry in files_list)
            count_width = len(str(max_count))

            for file_info in files_list:
                click.echo(file_info.display(count_width))
        else:
            click.echo(f"No files or directories found in {path}.")
    return 0


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def size(paths):
    """Analyze file and directory sizes.

    Examples:
        fx size           # Show sizes in current directory
        fx size /path     # Show sizes in specified path
    """
    from . import size as size_module

    paths_list = list(paths) if paths else ["."]

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
@click.argument("keyword")
@click.option(
    "--include-ignored",
    is_flag=True,
    default=False,
    help="Include default-ignored dirs (.git, .venv, node_modules)",
)
@click.option(
    "--exclude",
    "excludes",
    multiple=True,
    help=(
        "Exclude names (repeatable). Supports globs, e.g. "
        "--exclude build --exclude '*.log'"
    ),
)
def ff(keyword, include_ignored, excludes):
    """Find files by keyword.

    Examples:
        fx ff config                      # Names containing 'config'
        fx ff test --include-ignored      # Include .git/.venv/node_modules
        fx ff test --exclude build --exclude "*.log"  # Exclude patterns
    """
    from . import find_files

    if not keyword or keyword.strip() == "":
        click.echo("Please type text to search. For example: fx ff bar", err=True)
        click.echo("Usage: fx ff KEYWORD", err=True)
        return 1
    # Backward-compatible call shape for default options
    exclude_list = list(excludes)
    if not include_ignored and not exclude_list:
        find_files.find_files(keyword)
    else:
        find_files.find_files(
            keyword, include_ignored=include_ignored, exclude=exclude_list
        )
    return 0


@cli.command()
@click.argument("extension")
@click.argument("paths", nargs=-1)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Search recursively in subdirectories (default: True)",
)
@click.option(
    "--sort-by",
    type=click.Choice(["created", "modified"]),
    default=None,
    help="Sort files by creation or modification time",
)
@click.option(
    "--reverse",
    is_flag=True,
    default=False,
    help="Reverse sort order (newest first for time sorts)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["simple", "detailed"]),
    default="detailed",
    help="Output format (default: detailed)",
)
@click.option(
    "--show-path",
    is_flag=True,
    default=False,
    help="Show relative file paths instead of just filenames",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit the number of results returned",
)
def filter(
    extension,
    paths,
    recursive,
    sort_by,
    reverse,
    output_format,
    show_path,
    limit,
):
    """Filter files by extension.

    Examples:
        fx filter txt                    # Find .txt files with detailed format
        fx filter py /path/to/code       # Find .py files in specific path
        fx filter "txt,py" .             # Find multiple extensions
        fx filter txt --no-recursive     # Search only current directory
        fx filter py --sort-by modified  # Sort by modification time
        fx filter txt --format simple    # Show only filenames
        fx filter txt --show-path        # Show relative paths
    """
    from . import filter as filter_module

    try:
        # Use current directory if no paths provided
        search_paths = list(paths) if paths else ["."]

        # Find files in all paths
        all_files = []
        for path in search_paths:
            files = filter_module.find_files_by_extension(path, extension, recursive)
            all_files.extend(files)

        # Sort if requested
        if sort_by:
            all_files = filter_module.sort_files_by_time(all_files, sort_by, reverse)

        # Apply limit if requested
        if limit is not None and limit > 0:
            all_files = all_files[:limit]

        # Format and display output
        output = filter_module.format_output(all_files, output_format, show_path)
        click.echo(output)

        return 0

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        return 1
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return 1
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        return 1


@cli.command()
@click.argument("search_text")
@click.argument("replace_text")
@click.argument("filenames", nargs=-1, required=True)
def replace(search_text, replace_text, filenames):
    """Replace text in files.

    Examples:
        fx replace "old" "new" file.txt   # Replace in specific file
        fx replace "old" "new" *.txt      # Replace in multiple files
    """
    from . import replace as replace_module

    # Call the replace_files function directly (not the Click-decorated main)
    return replace_module.replace_files(search_text, replace_text, filenames)


@cli.command()
@click.argument("url")
@click.argument("output_filename")
def json2excel(url, output_filename):
    """Convert JSON data to Excel file.

    Examples:
        fx json2excel data.json output.xlsx
        fx json2excel https://api.example.com/data output.xlsx
    """
    from . import pd

    # Call the existing main function from pd module
    return pd.main(url, output_filename)


@cli.command(name="list")
def list_commands():
    """List all available fx commands."""
    click.echo("\nAvailable fx commands:\n")

    # Calculate maximum command length for alignment
    max_len = max(len(cmd) for cmd, _ in COMMANDS_INFO)

    for cmd, description in COMMANDS_INFO:
        # Format with aligned descriptions
        click.echo(f"  fx {cmd:<{max_len}}  - {description}")

    click.echo(
        "\nUse 'fx COMMAND --help' for more information on a " "specific command."
    )
    return 0


@cli.command()
@click.pass_context
def help(ctx):
    """Show help information (same as fx -h).

    Examples:
        fx help           # Show main help
        fx help files     # Show help for files command (equivalent to fx files --help)
    """
    # Get the parent context to show the main help
    parent_ctx = ctx.parent
    if parent_ctx:
        click.echo(parent_ctx.get_help())
    else:
        # Fallback to showing available commands
        list_commands()
    return 0


@cli.command()
def version():
    """Show version and system information.
    
    Examples:
        fx version        # Show detailed version info
        fx --version      # Same as above
    """
    click.echo(get_version_info())
    return 0


def main():
    """Main entry point for the fx command."""
    try:
        return cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

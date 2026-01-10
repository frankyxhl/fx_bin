#!/usr/bin/env python
"""Main CLI entry point for fx commands."""

import click
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Any, Sequence

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
    ("fff", "Find first file matching keyword (alias for ff --first)"),
    ("filter", "Filter files by extension"),
    ("replace", "Replace text in files"),
    ("backup", "Create timestamped backups of files/dirs"),
    ("root", "Find Git project root directory"),
    ("realpath", "Get absolute path of a file or directory"),
    ("today", "Create/navigate to today's workspace directory"),
    ("organize", "Organize files into date-based directories"),
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
def cli(ctx: click.Context) -> None:
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
def files(paths: Tuple[str, ...]) -> int:
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
def size(paths: Tuple[str, ...]) -> int:
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


def _run_ff(
    keyword: str,
    include_ignored: bool,
    excludes: tuple,
    first: bool,
) -> int:
    """Shared implementation for ff and fff commands."""
    from . import find_files

    if not keyword or keyword.strip() == "":
        click.echo("Please type text to search. For example: fx ff bar", err=True)
        click.echo("Usage: fx ff KEYWORD", err=True)
        return 1
    find_files.find_files(
        keyword,
        include_ignored=include_ignored,
        exclude=list(excludes),
        first=first,
    )
    return 0


@cli.command()
@click.argument("keyword")
@click.option(
    "--first",
    is_flag=True,
    default=False,
    help="Stop after first match (for speed)",
)
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
def ff(
    keyword: str, first: bool, include_ignored: bool, excludes: Tuple[str, ...]
) -> int:
    """Find files whose names contain KEYWORD.

    \b
    Basic Examples:
      fx ff test                        # Find files with 'test' in name
      fx ff config                      # Find configuration files
      fx ff .py                         # Find Python files
      fx ff api --exclude build         # Find 'api' files, skip build dirs
      fx ff test --first                # Find first match only

    \b
    Real-World Use Cases:
      fx ff TODO --exclude .git         # Find TODO comments in code
      fx ff .bak                        # Find all backup files
      fx ff .log --exclude archive      # Find log files, skip archived
      fx ff config --exclude backup     # Find configs, skip backups
      fx ff jquery --exclude node_modules  # Find jQuery files
      fx ff test --exclude coverage     # Find tests, skip coverage reports
      fx ff Component --exclude node_modules  # Find React components

    \b
    Advanced Filtering:
      fx ff api --exclude build --exclude cache --exclude "*.pyc"
      fx ff src --exclude "*test*" --exclude "*spec*"

    \b
    By default, skips heavy directories: .git, .venv, node_modules
    Use --include-ignored to search these directories too.
    """
    return _run_ff(keyword, include_ignored, excludes, first)


@cli.command()
@click.argument("keyword")
def fff(keyword: str) -> int:
    """Find first file matching KEYWORD.

    Alias for `fx ff KEYWORD --first`. Returns only the first match
    and exits immediately for speed.

    \b
    Examples:
      fx fff test      # Find first file with 'test' in name
      fx fff config    # Find first config file
      fx fff .py       # Find first Python file
    """
    return _run_ff(keyword, include_ignored=False, excludes=(), first=True)


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
    extension: str,
    paths: Tuple[str, ...],
    recursive: bool,
    sort_by: Optional[str],
    reverse: bool,
    output_format: str,
    show_path: bool,
    limit: Optional[int],
) -> int:
    """Filter files by extension.

    \b
    Basic Examples:
      fx filter py                     # Find Python files
      fx filter "py,js,ts" .           # Find multiple file types
      fx filter txt --format simple   # Show only filenames
      fx filter py --sort-by modified --reverse  # Newest files first

    \b
    Real-World Use Cases:
      fx filter "jpg,png,gif"          # Find all images
      fx filter "pdf,docx" ~/Documents # Find documents in folder
      fx filter log --sort-by created  # Find logs by creation time
      fx filter "py,js" --limit 10     # Find recent source files
      fx filter csv ~/data --format detailed  # Analyze data files
      fx filter "md,txt" --no-recursive  # Docs in current dir only

    \b
    Project Analysis:
      fx filter py --sort-by modified  # Recent Python changes
      fx filter "js,ts,jsx,tsx"        # All JavaScript/TypeScript
      fx filter "yaml,yml,json"         # Find config files
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
def replace(search_text: str, replace_text: str, filenames: Tuple[str, ...]) -> int:
    """Replace text in files.

    Examples:
        fx replace "old" "new" file.txt   # Replace in specific file
        fx replace "old" "new" *.txt      # Replace in multiple files
    """
    from . import replace as replace_module

    # Call the replace_files function directly (not the Click-decorated main)
    return replace_module.replace_files(search_text, replace_text, filenames)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--compress",
    is_flag=True,
    default=False,
    help="Compress directory backup as .tar.xz",
)
@click.option(
    "--timestamp-format",
    default=None,
    help="Custom timestamp format (strftime)",
)
def backup(
    path: str,
    compress: bool,
    timestamp_format: Optional[str],
) -> int:
    """Create a timestamped backup of a file or directory.

    Examples:
        fx backup file.txt          # Backup to file_timestamp.txt (same level)
        fx backup mydir/ --compress # Backup to mydir_timestamp.tar.xz

    Backups are created in the same directory as the source by default.
    """
    from . import backup as backup_module
    from pathlib import Path

    try:
        ts_format = timestamp_format or backup_module.DEFAULT_TIMESTAMP_FORMAT
        path_obj = Path(path)

        if path_obj.is_file():
            result = backup_module.backup_file(path, None, ts_format)
        else:
            result = backup_module.backup_directory(path, None, ts_format, compress)

        click.echo(f"Backup created: {result}")

        return 0
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


@cli.command()
@click.option(
    "--cd",
    "-c",
    "output_for_cd",
    is_flag=True,
    help="Output path suitable for cd command (no extra text)",
)
def root(output_for_cd: bool) -> int:
    """Find Git project root directory.

    Searches upward from current directory to find the first directory
    containing a .git folder.

    Examples:
        fx root              # Show root directory with description
        fx root --cd         # Output just the path for cd command
        cd "$(fx root --cd)" # Change to root directory
    """
    from . import root as root_module

    try:
        git_root = root_module.find_git_root()

        if git_root is None:
            if output_for_cd:
                # Silent exit for --cd mode
                import sys

                sys.exit(1)
            else:
                # Print error and exit for regular mode
                raise click.ClickException(
                    "No git repository found in current directory or parent directories"
                )

        if output_for_cd:
            # Just output the path for shell usage
            click.echo(str(git_root))
        else:
            # Friendly output with description
            click.echo(f"Git project root: {git_root}")

        return 0

    except PermissionError as e:
        if not output_for_cd:
            click.echo(f"Error: Permission denied accessing directory: {e}", err=True)
        ctx = click.get_current_context()
        ctx.exit(1)
    except Exception as e:
        if not output_for_cd:
            click.echo(f"Error: {e}", err=True)
        ctx = click.get_current_context()
        ctx.exit(1)


@cli.command()
@click.argument("path", default=".")
def realpath(path: str) -> int:
    """Get absolute path of a file or directory.

    Resolves relative paths, symlinks, and ~ to the canonical absolute path.
    The path must exist.

    Examples:
        fx realpath .           # Current directory
        fx realpath ../foo      # Relative path
        fx realpath ~/Downloads # Home directory
    """
    from . import realpath as realpath_module

    try:
        resolved = realpath_module.resolve_path(path)
        click.echo(str(resolved))
        return 0
    except FileNotFoundError:
        click.echo(f"Error: Path does not exist: {path}", err=True)
        ctx = click.get_current_context()
        ctx.exit(1)
    except PermissionError:
        click.echo(f"Error: Permission denied: {path}", err=True)
        ctx = click.get_current_context()
        ctx.exit(1)
    except OSError as e:
        click.echo(f"Error: Cannot resolve path: {path} ({e})", err=True)
        ctx = click.get_current_context()
        ctx.exit(1)


@cli.command()
@click.option(
    "--cd",
    "-c",
    "output_for_cd",
    is_flag=True,
    help="Output path suitable for cd command (no extra text)",
)
@click.option(
    "--base",
    "-b",
    "base_dir",
    default="~/Downloads",
    help="Base directory for daily workspaces",
)
@click.option(
    "--format",
    "-f",
    "date_format",
    default="%Y%m%d",
    help="Date format (strftime) for directory names",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be created without creating it"
)
@click.option(
    "--no-exec", is_flag=True, help="Don't start new shell, just create directory"
)
def today(
    output_for_cd: bool,
    base_dir: str,
    date_format: str,
    verbose: bool,
    dry_run: bool,
    no_exec: bool,
) -> None:
    """Create and navigate to today's workspace directory.

    Creates a date-organized directory (default: ~/Downloads/YYYYMMDD)
    and starts a new shell there for daily work organization.

    Examples:
        fx today              # Create workspace and start new shell there
        fx today --no-exec    # Just create directory without starting shell
        fx today --cd         # Output path for shell integration
        fx today --base ~/Projects  # Use custom base directory
        fx today --format %Y-%m-%d  # Use custom date format
    """
    from . import today as today_module

    try:
        # Default behavior is to exec shell, unless disabled
        exec_shell = not no_exec and not output_for_cd and not dry_run
        today_module.main(
            output_for_cd, base_dir, date_format, verbose, dry_run, exec_shell
        )
    except Exception as e:
        if not output_for_cd:
            click.echo(f"Error: {e}", err=True)
        ctx = click.get_current_context()
        ctx.exit(1)


@cli.command(name="list")
def list_commands() -> int:
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
@click.argument(
    "source",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Output directory for organized files (default: ./organized)",
)
@click.option(
    "--date-source",
    type=click.Choice(["created", "modified"], case_sensitive=False),
    default="created",
    help="Which file date to use for organization (default: created)",
)
@click.option(
    "--depth",
    type=click.IntRange(1, 3),
    default=3,
    help="Directory depth: 1=day, 2=year/day, 3=year/month/day (default: 3)",
)
@click.option(
    "--on-conflict",
    type=click.Choice(["rename", "skip", "overwrite", "ask"], case_sensitive=False),
    default="rename",
    help="How to handle filename conflicts (default: rename)",
)
@click.option(
    "--include",
    "-i",
    multiple=True,
    help="Include only files matching these glob patterns (repeatable)",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Exclude files matching these glob patterns (repeatable)",
)
@click.option(
    "--hidden",
    "-H",
    is_flag=True,
    help="Include hidden files (files starting with .)",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Process files in subdirectories recursively",
)
@click.option(
    "--clean-empty",
    is_flag=True,
    help="Remove empty directories after organization",
)
@click.option(
    "--fail-fast",
    is_flag=True,
    help="Stop on first error instead of continuing",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Preview changes without actually moving files",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed progress information",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress progress output (errors and summary only)",
)
def organize(
    source: str,
    output: Optional[str],
    date_source: str,
    depth: int,
    on_conflict: str,
    include: Sequence[str],
    exclude: Sequence[str],
    hidden: bool,
    recursive: bool,
    clean_empty: bool,
    fail_fast: bool,
    dry_run: bool,
    yes: bool,
    verbose: bool,
    quiet: bool,
) -> int:
    """Organize files into date-based directories.

    Organizes files from SOURCE directory into OUTPUT directory using
    date-based folder structure (e.g., 2026/202601/20260110/).

    \b
    Examples:
      fx organize ~/Photos                    # Organize photos by date
      fx organize ~/Downloads -o ~/Sorted     # Custom output directory
      fx organize . --depth 2                 # Use year/day structure
      fx organize . --dry-run                 # Preview without changes
      fx organize . -i "*.jpg" -i "*.png"     # Only images
      fx organize . -e ".*"                   # Skip hidden files

    \b
    Date Sources:
      --date-source created    Use file creation time (default)
      --date-source modified   Use file modification time

    \b
    Directory Depth:
      --depth 1    output/20260110/
      --depth 2    output/2026/20260110/
      --depth 3    output/2026/202601/20260110/ (default)

    \b
    Conflict Modes:
      --on-conflict rename     Auto-rename with _1, _2 suffix (default)
      --on-conflict skip       Skip conflicting files
      --on-conflict overwrite  Overwrite existing files
      --on-conflict ask        Prompt for conflicts (uses rename for intra-run)
    """
    from .organize_functional import execute_organize
    from .organize import (
        DateSource,
        ConflictMode,
        OrganizeContext,
    )
    from .lib import unsafe_ioresult_unwrap, unsafe_ioresult_to_result

    # Set default output directory
    if output is None:
        output = str(Path(source) / "organized")

    # Map string options to enums using Enum[name] pattern
    date_source_enum = DateSource[date_source.upper()]
    conflict_mode_enum = ConflictMode[on_conflict.upper()]

    # Create context with all options
    context = OrganizeContext(
        date_source=date_source_enum,
        depth=depth,
        conflict_mode=conflict_mode_enum,
        output_dir=output,
        dry_run=dry_run,
        include_patterns=include,
        exclude_patterns=exclude,
        recursive=recursive,
        clean_empty=clean_empty,
        fail_fast=fail_fast,
        hidden=hidden,
    )

    # Show what we're doing
    if not quiet:
        if dry_run:
            click.echo(f"DRY RUN: Previewing organization of {source}")
        else:
            click.echo(f"Organizing files from {source}")

    # Execute organization
    result = execute_organize(source, context)

    # Check for errors
    try:
        summary = unsafe_ioresult_unwrap(result)
    except Exception:
        # It's a failure
        inner_result = unsafe_ioresult_to_result(result)
        error = inner_result.failure()
        click.echo(f"Error: {error}", err=True)
        return 1

    # Show summary
    if not quiet or summary.errors > 0:
        click.echo(
            f"\nSummary: {summary.total_files} files, "
            f"{summary.processed} processed, "
            f"{summary.skipped} skipped"
        )
        if summary.errors > 0:
            click.echo(f"  {summary.errors} errors")

    if dry_run and not quiet:
        click.echo("\nDry-run complete. No files were moved.")

    return 0


@cli.command()
@click.pass_context
def help(ctx: click.Context) -> int:
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
def version() -> int:
    """Show version and system information.

    Examples:
        fx version        # Show detailed version info
        fx --version      # Same as above
    """
    click.echo(get_version_info())
    return 0


def main() -> Any:
    """Main entry point for the fx command."""
    try:
        return cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

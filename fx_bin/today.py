"""Create and navigate to today's workspace directory.

This module provides functionality to create date-organized workspace directories,
typically in ~/Downloads/YYYYMMDD format, for organizing daily work files.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import click


def get_today_path(base_dir: str = "~/Downloads", date_format: str = "%Y%m%d") -> Path:
    """Get the path for today's workspace directory.

    Args:
        base_dir: Base directory where daily folders are created.
                  Defaults to ~/Downloads.
        date_format: strftime format for the date folder name. Defaults to %Y%m%d.

    Returns:
        Path object for today's workspace directory.
    """
    # Expand home directory if present
    base = Path(base_dir).expanduser()

    # If it's a relative path, resolve it relative to current directory
    if not base.is_absolute():
        base = Path.cwd() / base

    # Get today's date in the specified format
    today_str = datetime.now().strftime(date_format)

    return base / today_str


def ensure_directory_exists(path: Path) -> bool:
    """Ensure the directory exists, creating it if necessary.

    Args:
        path: Path to the directory to create.

    Returns:
        True if directory exists or was created successfully, False otherwise.
    """
    try:
        # Check if path exists and is a file (not directory)
        if path.exists() and not path.is_dir():
            click.echo(f"Error: {path} exists but is not a directory", err=True)
            return False

        # Create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)
        return True

    except PermissionError:
        click.echo(f"Error: Permission denied creating directory {path}", err=True)
        return False
    except Exception as e:
        click.echo(f"Error creating directory {path}: {e}", err=True)
        return False


def validate_date_format(date_format: Optional[str]) -> bool:
    """Validate that the date format string is valid and safe.

    Args:
        date_format: strftime format string to validate.

    Returns:
        True if valid and safe, False otherwise.
    """
    if not date_format:
        return False

    # Check if it contains at least one format code
    if "%" not in date_format:
        return False

    try:
        # Try to format current date with the given format
        result = datetime.now().strftime(date_format)
        # Make sure it produced something meaningful
        if not result or result == date_format:
            return False
            
        # SECURITY: Validate that the formatted result is safe
        # Import regex module once at the top of the validation block
        import re
        
        # Check for traversal sequences (most critical)
        if ".." in result:
            return False
            
        # For single directory names, ensure no path separators
        # For multi-level paths, ensure no traversal but allow valid structure
        if result != Path(result).name:
            # This is a multi-level path, check it's safe
            path_parts = Path(result).parts
            for part in path_parts:
                if part == ".." or part == ".":
                    return False
                if not part:  # Empty parts indicate // or similar
                    return False
                # Ensure each part contains only safe characters and at least one format result
                # This prevents arbitrary prefixes/suffixes like "prefix/20250906"
                if not re.match(r"^[A-Za-z0-9._-]+$", part):
                    return False
                # For security, require each part to contain at least one digit (date component)
                if not re.search(r"\d", part):
                    return False
        
        # Whitelist safe characters for directory names  
        # Allow alphanumeric, dots, underscores, hyphens, and path separators
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", result):
            return False
            
        return True
    except (ValueError, TypeError, Exception):
        return False


def validate_base_path(base_path: str) -> bool:
    """Validate that the base path is safe (no path traversal).

    Args:
        base_path: Base directory path to validate.

    Returns:
        True if path is safe, False otherwise.
    """
    # Check for path traversal attempts
    if ".." in base_path:
        return False

    return True


def detect_shell_executable() -> str:
    """Detect the user's preferred shell executable.
    
    Returns:
        Path to shell executable.
    """
    # Try environment variable first
    shell_env = os.environ.get("SHELL")
    if shell_env and os.path.isfile(shell_env):
        return shell_env
    
    # Platform-specific fallbacks
    if sys.platform == "win32":
        # Windows: prefer PowerShell, fallback to cmd
        if os.system("powershell -Command 'exit 0'") == 0:
            return "powershell"
        return "cmd"
    else:
        # Unix-like: try common shells
        for shell in ["/bin/zsh", "/bin/bash", "/bin/sh"]:
            if os.path.isfile(shell):
                return shell
        # Last resort
        return "/bin/sh"


def main(
    output_for_cd: bool = False,
    base_dir: str = "~/Downloads",
    date_format: str = "%Y%m%d",
    verbose: bool = False,
    dry_run: bool = False,
    exec_shell: bool = False,
) -> None:
    """Main function for the today command.

    Args:
        output_for_cd: If True, output just the path for shell integration.
        base_dir: Base directory for daily workspaces.
        date_format: strftime format for date folder names.
        verbose: If True, output verbose messages.
        dry_run: If True, don't actually create directories.
        exec_shell: If True, spawn a new shell in the target directory.
    """
    # Validate inputs
    if not validate_base_path(base_dir):
        click.echo("Error: Invalid base directory (path traversal detected)", err=True)
        sys.exit(1)

    if not validate_date_format(date_format):
        click.echo(f"Error: Invalid date format '{date_format}'", err=True)
        sys.exit(1)

    # Get the path for today's workspace
    today_path = get_today_path(base_dir, date_format)

    if verbose and not output_for_cd:
        click.echo(f"Creating directory: {today_path}")

    # Handle dry run mode
    if dry_run:
        if output_for_cd:
            click.echo(str(today_path))
        else:
            click.echo(f"Would create: {today_path}")
        return

    # Create the directory
    if not ensure_directory_exists(today_path):
        sys.exit(1)

    if verbose and not output_for_cd:
        click.echo("Directory created successfully")

    # Handle exec shell mode - spawn new shell in target directory
    if exec_shell:
        try:
            shell_cmd = detect_shell_executable()
            if not output_for_cd:
                click.echo(f"🚀 Starting new shell in: {today_path}")
                click.echo(f"Shell: {shell_cmd}")
                click.echo("Type 'exit' to return to the previous directory.")
                click.echo("-" * 50)
            
            # Change to target directory
            os.chdir(str(today_path))
            
            # Execute new shell (replaces current process)
            if sys.platform == "win32":
                if "powershell" in shell_cmd.lower():
                    os.execv(shell_cmd, [shell_cmd, "-NoLogo"])
                else:
                    # cmd.exe
                    os.execv(shell_cmd, [shell_cmd])
            else:
                # Unix-like systems
                shell_name = os.path.basename(shell_cmd)
                os.execv(shell_cmd, [shell_name])
                
        except Exception as e:
            click.echo(f"Error starting shell: {e}", err=True)
            sys.exit(1)

    # Output based on mode
    if output_for_cd:
        # Just output the path for shell usage
        click.echo(str(today_path))
    else:
        # Friendly output with description
        click.echo(f"Today's workspace: {today_path}")



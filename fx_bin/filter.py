"""File filtering utility for finding files by extension.

This module provides functionality to filter files by extension with various
sorting and formatting options.

Examples:
    >>> find_files_by_extension('/path/to/dir', 'py')
    ['/path/to/dir/script.py', '/path/to/dir/module.py']
    >>> parse_extensions('py,txt,json')
    ['py', 'txt', 'json']
"""

import fnmatch
import os
import time
from pathlib import Path
from typing import List


def find_files_by_extension(
    path: str, extension: str, recursive: bool = True
) -> List[str]:
    """Find files by extension in the given path.

    Args:
        path: Directory path to search in
        extension: File extension(s) to search for (comma-separated)
        recursive: Whether to search recursively (default: True)

    Returns:
        List of file paths matching the extension(s)

    Raises:
        FileNotFoundError: If the path doesn't exist

    Examples:
        >>> find_files_by_extension('.', 'py')  # doctest: +SKIP
        ['./script.py', './module.py']
    """
    path = os.path.abspath(path)  # Normalize path
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")

    if not os.path.isdir(path):
        raise FileNotFoundError(f"Path is not a directory: {path}")

    extensions = parse_extensions(extension)
    if not extensions:
        return []

    # Convert to lowercase once for performance
    extensions_lower = (
        [ext.lower() for ext in extensions] if "*" not in extensions else ["*"]
    )
    found_files = []

    if recursive:
        # Recursive search using os.walk
        for root, dirs, files in os.walk(path):
            found_files.extend(
                _filter_files_by_extension(root, files, extensions_lower)
            )
    else:
        # Non-recursive search - only current directory
        try:
            files = [
                f
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
            ]
            found_files.extend(
                _filter_files_by_extension(path, files, extensions_lower)
            )
        except (PermissionError, OSError):
            # Handle permission errors gracefully
            pass

    return found_files


def _filter_files_by_extension(
    directory: str, files: List[str], extensions_lower: List[str]
) -> List[str]:
    """Helper function to filter files by extension.

    Args:
        directory: Directory path
        files: List of filenames to filter
        extensions_lower: List of lowercase extensions to match

    Returns:
        List of matching file paths
    """
    matching_files = []
    for file in files:
        file_path = os.path.join(directory, file)
        file_ext = (
            Path(file).suffix[1:].lower()
        )  # Remove dot and convert to lowercase

        # Check for matches
        match_found = False
        for pattern in extensions_lower:
            if pattern == "*":
                # Match all files
                match_found = True
                break
            elif "*" in pattern or "?" in pattern:
                # Use glob pattern matching for extensions with wildcards
                if fnmatch.fnmatch(file_ext, pattern):
                    match_found = True
                    break
            elif file_ext == pattern:
                # Exact match
                match_found = True
                break

        if match_found:
            matching_files.append(file_path)

    return matching_files


def sort_files_by_time(
    files: List[str], sort_by: str = "created", reverse: bool = False
) -> List[str]:
    """Sort files by time (creation or modification).

    Args:
        files: List of file paths to sort
        sort_by: Sort criteria - 'created' or 'modified' (default: 'created')
        reverse: Whether to sort in reverse order (default: False)

    Returns:
        Sorted list of file paths

    Raises:
        ValueError: If sort_by is not 'created' or 'modified'
        FileNotFoundError: If any file in the list doesn't exist
        OSError: If file stats cannot be accessed
    """
    if not files:
        return []

    if sort_by not in ["created", "modified"]:
        raise ValueError(
            f"Invalid sort_by: {sort_by}. Must be 'created' or 'modified'"
        )

    def get_time(file_path: str) -> float:
        """Get file time based on sort criteria."""
        try:
            stat_info = os.stat(file_path)
            if sort_by == "created":
                # Use creation/birth time, or modified time as fallback
                return getattr(stat_info, "st_birthtime", stat_info.st_ctime)
            else:  # modified
                return stat_info.st_mtime
        except (FileNotFoundError, OSError) as e:
            raise e

    try:
        return sorted(files, key=get_time, reverse=reverse)
    except (FileNotFoundError, OSError):
        raise


def format_output(
    files: List[str], format: str = "detailed", show_path: bool = False
) -> str:
    """Format the output of found files.

    Args:
        files: List of file paths to format
        format: Output format - 'simple' or 'detailed' (default: 'detailed')
        show_path: Whether to show paths (default: False, shows filenames only)

    Returns:
        Formatted string output

    Raises:
        ValueError: If format is not supported

    Examples:
        >>> format_output(['file1.txt', 'file2.py'], 'simple')
        'file1.txt\\nfile2.py'
    """
    VALID_FORMATS = ["simple", "detailed"]
    if format not in VALID_FORMATS:
        raise ValueError(
            f"Invalid format: {format}. Must be one of {VALID_FORMATS}."
        )

    if not files:
        return "No files found"

    if format == "simple":
        return "\n".join(files)

    elif format == "detailed":
        output_lines = []
        for file_path in files:
            try:
                stat_info = os.stat(file_path)
                size = stat_info.st_size
                mtime = stat_info.st_mtime

                # Format date as YYYY-MM-DD HH:MM:SS
                date_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(mtime)
                )

                # Convert size to aligned human-readable format
                size_str = _format_file_size_aligned(size)

                # Choose filename display based on show_path flag
                if show_path:
                    display_name = file_path
                else:
                    display_name = os.path.basename(file_path)

                output_lines.append(f"{date_str}  {size_str}  {display_name}")
            except (FileNotFoundError, OSError):
                # For unavailable files, still maintain format
                display_name = (
                    os.path.basename(file_path) if not show_path else file_path
                )
                output_lines.append(
                    f"????-??-?? ??:??:??       ??? ??    {display_name}"
                )

        return "\n".join(output_lines)


def _format_file_size(size: int) -> str:
    """Helper function to format file size in human-readable format.

    Args:
        size: File size in bytes

    Returns:
        Human-readable file size string

    Examples:
        >>> _format_file_size(512)
        '512 bytes'
        >>> _format_file_size(1536)  # doctest: +ELLIPSIS
        '1.5 KB'
        >>> _format_file_size(2097152)  # doctest: +ELLIPSIS
        '2.0 MB'
    """
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"


def _format_file_size_aligned(size: int) -> str:
    """Helper function to format file size with aligned columns.

    Args:
        size: File size in bytes

    Returns:
        Right-aligned size with unit (total width 8 chars)

    Examples:
        >>> _format_file_size_aligned(100)
        '    100 B'
        >>> _format_file_size_aligned(1536)
        '  1.5 KB'
        >>> _format_file_size_aligned(2097152)
        '  2.0 MB'
    """
    if size < 1024:
        formatted = f"{size} B"
        return f"{formatted:>9}"
    elif size < 1024 * 1024:
        formatted = f"{size / 1024:.1f} KB"
        return f"{formatted:>8}"
    elif size < 1024 * 1024 * 1024:
        formatted = f"{size / (1024 * 1024):.1f} MB"
        return f"{formatted:>8}"
    else:
        formatted = f"{size / (1024 * 1024 * 1024):.1f} GB"
        return f"{formatted:>8}"


def parse_extensions(extension_string: str) -> List[str]:
    """Parse extension string into list of extensions.

    Args:
        extension_string: Comma-separated extension string

    Returns:
        List of extensions without leading dots

    Examples:
        >>> parse_extensions('py,txt,json')
        ['py', 'txt', 'json']
        >>> parse_extensions('.py, .txt , .json ')
        ['py', 'txt', 'json']
        >>> parse_extensions('')
        []
        >>> parse_extensions('*')
        ['*']
    """
    if not extension_string or not extension_string.strip():
        return []

    extensions = []
    for ext in extension_string.split(","):
        ext = ext.strip()
        if ext:
            # Remove leading dot if present and normalize
            ext = ext.lstrip(".")
            if ext:  # Only add non-empty extensions after stripping
                extensions.append(ext)

    return extensions

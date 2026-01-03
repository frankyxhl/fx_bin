"""Backup utility for creating timestamped copies of files and directories.

This module provides functionality to create backups with automatic timestamp
generation, multi-part extension handling, and optional compression.

Examples:
    >>> get_multi_ext("archive.tar.gz")
    '.tar.gz'
    >>> get_base_name("data.tar.bz2")
    'data'
"""

from typing import Tuple

# Known multi-part extensions
KNOWN_MULTI_EXTS = (".tar.gz", ".tar.bz2")

# Default timestamp format (YYYYMMDDHHMMSS)
DEFAULT_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"


def get_multi_ext(filename: str) -> str:
    """Extract multi-part or single extension from filename.

    Args:
        filename: Name of the file

    Returns:
        Extension string (e.g., '.tar.gz', '.txt', or '')

    Examples:
        >>> get_multi_ext("archive.tar.gz")
        '.tar.gz'
        >>> get_multi_ext("document.txt")
        '.txt'
        >>> get_multi_ext("README")
        ''
    """
    for multi_ext in KNOWN_MULTI_EXTS:
        if filename.endswith(multi_ext):
            return multi_ext

    if "." in filename:
        return "." + filename.rsplit(".", 1)[1]
    return ""


def get_base_name(filename: str) -> str:
    """Extract base name from filename, handling multi-part extensions.

    Args:
        filename: Name of the file

    Returns:
        Base name without extension

    Examples:
        >>> get_base_name("archive.tar.gz")
        'archive'
        >>> get_base_name("document.txt")
        'document'
        >>> get_base_name("README")
        'README'
    """
    ext = get_multi_ext(filename)
    if ext:
        return filename[: -len(ext)]
    return filename

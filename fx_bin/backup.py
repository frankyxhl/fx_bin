"""Backup utility for creating timestamped copies of files and directories.

This module provides functionality to create backups with automatic timestamp
generation, multi-part extension handling, and optional compression.

Examples:
    >>> get_multi_ext("archive.tar.gz")
    '.tar.gz'
    >>> get_base_name("data.tar.bz2")
    'data'
"""

import os
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
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


def backup_file(
    source_path: str,
    backup_dir: str = "backups",
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
) -> str:
    """Create a timestamped backup of a file.

    Args:
        source_path: Path to the file to backup
        backup_dir: Directory to store the backup (default: 'backups')
        timestamp_format: Format string for timestamp (default: '%Y%m%d%H%M%S')

    Returns:
        Path to the created backup file

    Raises:
        FileNotFoundError: If source file doesn't exist

    Examples:
        >>> backup_file("document.txt")  # doctest: +SKIP
        'backups/document_20250104120000.txt'
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")

    source_path_obj = Path(source_path)
    filename = source_path_obj.name
    base_name = get_base_name(filename)
    ext = get_multi_ext(filename)

    timestamp = datetime.now().strftime(timestamp_format)
    backup_filename = f"{base_name}_{timestamp}{ext}"

    backup_dir_path = Path(backup_dir)
    backup_dir_path.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir_path / backup_filename
    shutil.copy2(source_path, backup_path)

    return str(backup_path)


def backup_directory(
    source_path: str,
    backup_dir: str = "backups",
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
    compress: bool = False,
) -> str:
    """Create a timestamped backup of a directory.

    Args:
        source_path: Path to the directory to backup
        backup_dir: Directory to store the backup (default: 'backups')
        timestamp_format: Format string for timestamp (default: '%Y%m%d%H%M%S')
        compress: Whether to compress as .tar.gz (default: False)

    Returns:
        Path to the created backup directory or archive

    Raises:
        FileNotFoundError: If source directory doesn't exist

    Examples:
        >>> backup_directory("mydir/")  # doctest: +SKIP
        'backups/mydir_20250104120000/'
        >>> backup_directory("mydir/", compress=True)  # doctest: +SKIP
        'backups/mydir_20250104120000.tar.gz'
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source directory not found: {source_path}")

    if compress:
        return _backup_directory_compressed(source_path, backup_dir, timestamp_format)
    else:
        return _backup_directory_uncompressed(source_path, backup_dir, timestamp_format)


def _backup_directory_uncompressed(
    source_path: str, backup_dir: str, timestamp_format: str
) -> str:
    """Create uncompressed directory backup."""
    source_path_obj = Path(source_path)
    dir_name = source_path_obj.name

    timestamp = datetime.now().strftime(timestamp_format)
    backup_dirname = f"{dir_name}_{timestamp}"

    backup_dir_path = Path(backup_dir)
    backup_dir_path.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir_path / backup_dirname
    shutil.copytree(source_path, backup_path)

    return str(backup_path)


def _backup_directory_compressed(
    source_path: str, backup_dir: str, timestamp_format: str
) -> str:
    """Create compressed directory backup as .tar.gz."""
    source_path_obj = Path(source_path)
    dir_name = source_path_obj.name

    timestamp = datetime.now().strftime(timestamp_format)
    backup_filename = f"{dir_name}_{timestamp}.tar.gz"

    backup_dir_path = Path(backup_dir)
    backup_dir_path.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir_path / backup_filename

    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add(source_path, arcname=dir_name)

    return str(backup_path)


def cleanup_old_backups(backup_dir: str, base_name: str, max_backups: int) -> int:
    """Remove old backups keeping only the most recent ones.

    Args:
        backup_dir: Directory containing backups
        base_name: Base name of the file/directory to cleanup
        max_backups: Maximum number of backups to keep

    Returns:
        Number of backups removed
    """
    if max_backups <= 0:
        return 0

    backup_path = Path(backup_dir)
    if not backup_path.exists():
        return 0

    backups = list(backup_path.glob(f"{base_name}_*"))

    if len(backups) <= max_backups:
        return 0

    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    to_remove = backups[max_backups:]
    removed_count = 0
    for item in to_remove:
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
        removed_count += 1

    return removed_count

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
from typing import Optional

from .common import (
    generate_timestamp,
    get_base_name as _get_base_name_common,
    get_multi_ext as _get_multi_ext_common,
)
from .errors import FxBinError

# Default timestamp format (YYYYMMDDHHMMSSffffff)
DEFAULT_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S%f"


def get_multi_ext(filename: str) -> str:
    """Extract multi-part or single extension from filename.

    Deprecated: Use fx_bin.common.get_multi_ext instead.
    This wrapper maintained for backward compatibility.
    """
    return _get_multi_ext_common(filename)


def get_base_name(filename: str) -> str:
    """Extract base name from filename, handling multi-part extensions.

    Deprecated: Use fx_bin.common.get_base_name instead.
    This wrapper maintained for backward compatibility.
    """
    return _get_base_name_common(filename)


def backup_file(
    source_path: str,
    backup_dir: Optional[str] = None,
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
) -> str:
    """Create a timestamped backup of a file.

    Args:
        source_path: Path to the file to backup
        backup_dir: Directory to store the backup (default: None = same level as source)
        timestamp_format: Format string for timestamp (default: '%Y%m%d%H%M%S')

    Returns:
        Path to the created backup file

    Raises:
        FileNotFoundError: If source file doesn't exist

    Examples:
        >>> backup_file("document.txt")  # doctest: +SKIP
        'document_20250104120000.txt'
        >>> backup_file("document.txt", backup_dir="backups")  # doctest: +SKIP
        'backups/document_20250104120000.txt'
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")

    source_path_obj = Path(source_path)
    filename = source_path_obj.name
    base_name = get_base_name(filename)
    ext = get_multi_ext(filename)

    timestamp = generate_timestamp(timestamp_format, now=datetime.now())
    backup_filename = f"{base_name}_{timestamp}{ext}"

    # NEW DEFAULT: Same level as source, unless explicit backup_dir provided
    if backup_dir is None:
        backup_dir_path = source_path_obj.parent  # Parent directory of source
    else:
        backup_dir_path = Path(backup_dir)
        backup_dir_path.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir_path / backup_filename
    if backup_path.exists():
        raise FxBinError(f"Backup path already exists: {backup_path}")

    shutil.copy2(source_path, backup_path)

    return str(backup_path)


def backup_directory(
    source_path: str,
    backup_dir: Optional[str] = None,
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
    compress: bool = False,
) -> str:
    """Create a timestamped backup of a directory.

    Args:
        source_path: Path to the directory to backup
        backup_dir: Directory to store the backup (default: None = same level as source)
        timestamp_format: Format string for timestamp (default: '%Y%m%d%H%M%S')
        compress: Whether to compress as .tar.xz (default: False)

    Returns:
        Path to the created backup directory or archive

    Note:
        By default, symlinks within the source directory are preserved rather than
        followed. This prevents pulling in external files unexpectedly.

    Raises:
        FileNotFoundError: If source directory doesn't exist

    Examples:
        >>> backup_directory("mydir/")  # doctest: +SKIP
        'mydir_20250104120000/'
        >>> backup_directory("mydir/", compress=True)  # doctest: +SKIP
        'mydir_20250104120000.tar.xz'
        >>> backup_directory("mydir/", backup_dir="backups")  # doctest: +SKIP
        'backups/mydir_20250104120000/'
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source directory not found: {source_path}")

    if compress:
        return _backup_directory_compressed(source_path, backup_dir, timestamp_format)
    else:
        return _backup_directory_uncompressed(source_path, backup_dir, timestamp_format)


def _backup_directory_uncompressed(
    source_path: str,
    backup_dir: Optional[str],
    timestamp_format: str,
) -> str:
    """Create uncompressed directory backup."""
    source_path_obj = Path(source_path)
    dir_name = source_path_obj.name

    timestamp = generate_timestamp(timestamp_format, now=datetime.now())
    backup_dirname = f"{dir_name}_{timestamp}"

    # NEW DEFAULT: Same level as source, unless explicit backup_dir provided
    if backup_dir is None:
        backup_dir_path = source_path_obj.parent  # Parent directory of source
    else:
        backup_dir_path = Path(backup_dir)
        backup_dir_path.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir_path / backup_dirname
    if backup_path.exists():
        raise FxBinError(f"Backup path already exists: {backup_path}")

    # Preserve symlinks to avoid pulling in external files unexpectedly
    shutil.copytree(source_path, backup_path, symlinks=True)

    return str(backup_path)


def _backup_directory_compressed(
    source_path: str, backup_dir: Optional[str], timestamp_format: str
) -> str:
    """Create compressed directory backup as .tar.xz."""
    source_path_obj = Path(source_path)
    dir_name = source_path_obj.name

    timestamp = generate_timestamp(timestamp_format, now=datetime.now())
    backup_filename = f"{dir_name}_{timestamp}.tar.xz"

    # NEW DEFAULT: Same level as source, unless explicit backup_dir provided
    if backup_dir is None:
        backup_dir_path = source_path_obj.parent  # Parent directory of source
    else:
        backup_dir_path = Path(backup_dir)
        backup_dir_path.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir_path / backup_filename
    if backup_path.exists():
        raise FxBinError(f"Backup path already exists: {backup_path}")

    with tarfile.open(backup_path, "w:xz") as tar:
        tar.add(source_path, arcname=dir_name)

    return str(backup_path)

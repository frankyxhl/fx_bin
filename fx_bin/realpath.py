"""Resolve paths to their absolute canonical form.

This module provides functionality to resolve relative paths, symlinks,
and tilde expansion to absolute canonical paths.
"""

from pathlib import Path


def resolve_path(path: str) -> Path:
    """Resolve a path to its absolute canonical form.

    Args:
        path: Path to resolve (can be relative, contain ~, or be a symlink)

    Returns:
        Absolute path with symlinks resolved

    Raises:
        FileNotFoundError: If path does not exist
        PermissionError: If path is not accessible
        OSError: For circular symlinks or other path resolution errors
    """
    return Path(path).expanduser().resolve(strict=True)

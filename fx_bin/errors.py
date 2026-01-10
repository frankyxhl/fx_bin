"""Error type hierarchy for fx_bin using functional patterns.

This module defines the error types used throughout the fx_bin package
for type-safe error handling with the returns library.
"""

from typing import Union


class FxBinError(Exception):
    """Base error type for all fx_bin operations."""

    pass


class FileOperationError(FxBinError):
    """Base class for all file-related operation errors.

    This error type covers all operations that involve file system
    interactions including reading, writing, replacing, and backing up files.
    It provides a common base for file-related errors to enable polymorphic
    error handling.

    Examples:
        >>> try:
        ...     # File operation that might fail
        ...     pass
        ... except FileOperationError as e:
        ...     # Catches both IOError and ReplaceError
        ...     print(f"File operation failed: {e}")
    """

    pass


class IOError(FileOperationError):
    """IO operation errors (file read/write, network, etc).

    Inherits from FileOperationError since IO operations are file operations.
    """

    pass


class ValidationError(FxBinError):
    """Input validation errors."""

    pass


class SecurityError(FxBinError):
    """Security violation errors."""

    pass


class PermissionError(FxBinError):
    """Permission denied errors."""

    pass


# Module-specific errors


class ReplaceError(FileOperationError):
    """Errors during text replacement operations.

    Inherits from FileOperationError since replacement involves file operations.
    """

    pass


class FolderError(FxBinError):
    """Errors during folder traversal."""

    pass


class UploadError(SecurityError):
    """Errors during file upload operations."""

    pass


class SizeError(FxBinError):
    """Errors during size calculation."""

    pass


class FilesError(FxBinError):
    """Errors during file counting."""

    pass


class FindError(FxBinError):
    """Errors during file finding."""

    pass


class OrganizeError(FileOperationError):
    """Errors during file organization operations.

    Inherits from FileOperationError since organization involves file operations.
    """

    pass


class DateReadError(OrganizeError):
    """Errors during file date reading for organization.

    Inherits from OrganizeError since date reading is part of organization.
    """

    pass


class MoveError(OrganizeError):
    """Errors during file move operations.

    Inherits from OrganizeError since moving is part of organization.
    """

    pass


# Union types for Result error parameters
AppError = Union[
    FileOperationError,  # Base for IOError, ReplaceError, OrganizeError
    IOError,
    ValidationError,
    SecurityError,
    PermissionError,
    ReplaceError,
    FolderError,
    UploadError,
    SizeError,
    FilesError,
    FindError,
    OrganizeError,
]

# Specific error union types for modules
# Note: FileOperationError covers both ReplaceError and IOError
ReplaceErrors = Union[ReplaceError, IOError, PermissionError, FileOperationError]
CommonErrors = Union[FolderError, IOError, PermissionError, FileOperationError]
UploadErrors = Union[UploadError, SecurityError, ValidationError]
OrganizeErrors = Union[
    OrganizeError,
    DateReadError,
    MoveError,
    IOError,
    PermissionError,
    FileOperationError,
]

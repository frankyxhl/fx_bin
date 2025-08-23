"""Error type hierarchy for fx_bin using functional patterns.

This module defines the error types used throughout the fx_bin package
for type-safe error handling with the returns library.
"""

from typing import Union


class FxBinError(Exception):
    """Base error type for all fx_bin operations."""
    pass


class IOError(FxBinError):
    """IO operation errors (file read/write, network, etc)."""
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

class ReplaceError(FxBinError):
    """Errors during text replacement operations."""
    pass


class PdError(FxBinError):
    """Errors in pandas/Excel operations."""
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


# Union types for Result error parameters
AppError = Union[
    IOError,
    ValidationError,
    SecurityError,
    PermissionError,
    ReplaceError,
    PdError,
    FolderError,
    UploadError,
    SizeError,
    FilesError,
    FindError,
]

# Specific error union types for modules
ReplaceErrors = Union[ReplaceError, IOError, PermissionError]
PdErrors = Union[PdError, ValidationError, IOError]
CommonErrors = Union[FolderError, IOError, PermissionError]
UploadErrors = Union[UploadError, SecurityError, ValidationError]

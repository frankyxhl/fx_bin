"""Tests for error type hierarchy.

This module tests the error inheritance structure to ensure
proper exception handling and type safety.
"""

import pytest


def test_given_fileoperationerror_when_importing_then_exists():
    """RED: Test that FileOperationError base class exists.

    FileOperationError should be a base class for all file-related
    operations including replace, backup, and general IO errors.
    """
    from fx_bin.errors import FileOperationError

    # GIVEN: FileOperationError is imported
    # WHEN: checking its type
    # THEN: it should be a class that inherits from FxBinError
    from fx_bin.errors import FxBinError

    assert issubclass(FileOperationError, FxBinError)
    assert issubclass(FileOperationError, Exception)


def test_given_replaceerror_when_checking_inheritance_then_inherits_from_fileoperationerror():
    """RED: Test that ReplaceError inherits from FileOperationError.

    Replace operations are file operations, so ReplaceError should
    inherit from FileOperationError for proper error handling hierarchy.
    """
    from fx_bin.errors import ReplaceError, FileOperationError

    # GIVEN: ReplaceError is imported
    # WHEN: checking its inheritance
    # THEN: it should inherit from FileOperationError
    assert issubclass(ReplaceError, FileOperationError)


def test_given_ioerror_when_checking_inheritance_then_inherits_from_fileoperationerror():
    """RED: Test that IOError inherits from FileOperationError.

    IO operations are file operations, so IOError should inherit
    from FileOperationError for consistent error handling.
    """
    from fx_bin.errors import IOError, FileOperationError

    # GIVEN: IOError is imported
    # WHEN: checking its inheritance
    # THEN: it should inherit from FileOperationError
    assert issubclass(IOError, FileOperationError)


def test_given_fileoperationerror_when_catching_specific_errors_then_catches_both():
    """RED: Test that FileOperationError can catch both ReplaceError and IOError.

    This verifies the hierarchy enables polymorphic error handling.
    """
    from fx_bin.errors import FileOperationError, ReplaceError, IOError

    # GIVEN: exceptions are raised
    # WHEN: catching FileOperationError
    # THEN: both ReplaceError and IOError should be caught

    # Test ReplaceError is caught by FileOperationError
    with pytest.raises(FileOperationError):
        raise ReplaceError("Replace failed")

    # Test IOError is caught by FileOperationError
    with pytest.raises(FileOperationError):
        raise IOError("IO failed")


def test_given_error_hierarchy_when_creating_instances_then_messages_preserved():
    """RED: Test that error messages are preserved in the hierarchy.

    Error instances should preserve their messages through the
    inheritance chain for debugging purposes.
    """
    from fx_bin.errors import FileOperationError, ReplaceError, IOError

    # GIVEN: errors with specific messages
    # WHEN: creating error instances
    # THEN: messages should be preserved

    file_op_error = FileOperationError("File operation failed")
    assert str(file_op_error) == "File operation failed"

    replace_error = ReplaceError("Replacement failed")
    assert str(replace_error) == "Replacement failed"
    assert isinstance(replace_error, FileOperationError)

    io_error = IOError("IO operation failed")
    assert str(io_error) == "IO operation failed"
    assert isinstance(io_error, FileOperationError)


def test_given_error_types_when_using_isinstance_then_proper_hierarchy():
    """RED: Test isinstance checks work correctly with hierarchy.

    This ensures the error hierarchy supports runtime type checking
    for error recovery and logging purposes.
    """
    from fx_bin.errors import (
        FxBinError,
        FileOperationError,
        ReplaceError,
        IOError,
    )

    # GIVEN: a ReplaceError instance
    error = ReplaceError("test error")

    # WHEN: checking with isinstance
    # THEN: it should be instance of all parent classes
    assert isinstance(error, ReplaceError)
    assert isinstance(error, FileOperationError)
    assert isinstance(error, FxBinError)
    assert isinstance(error, Exception)

    # GIVEN: an IOError instance
    io_err = IOError("test io error")

    # WHEN: checking with isinstance
    # THEN: it should be instance of all parent classes
    assert isinstance(io_err, IOError)
    assert isinstance(io_err, FileOperationError)
    assert isinstance(io_err, FxBinError)
    assert isinstance(io_err, Exception)

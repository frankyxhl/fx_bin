"""Shared pytest fixtures for fx_bin tests.

This module provides reusable fixtures to reduce test code duplication
and improve test isolation.
"""

import tempfile
import shutil
from pathlib import Path
import pytest
from loguru import logger


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for tests.

    Yields:
        Path: A Path object pointing to a temporary directory.
              The directory is automatically cleaned up after the test.

    Example:
        def test_file_creation(temp_test_dir):
            test_file = temp_test_dir / "test.txt"
            test_file.write_text("content")
            assert test_file.exists()
    """
    test_dir = tempfile.mkdtemp()
    yield Path(test_dir)
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def temp_file(temp_test_dir):
    """Create a temporary file with default content in a test directory.

    Args:
        temp_test_dir: Fixture providing the temporary directory.

    Yields:
        Path: A Path object pointing to a temporary file with content "test content".

    Example:
        def test_file_reading(temp_file):
            content = temp_file.read_text()
            assert content == "test content"
    """
    file_path = temp_test_dir / "test.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture(autouse=True)
def silence_logger():
    """Silence logger output during tests.

    This fixture runs automatically for all tests to prevent log noise
    in test output. Logger state is restored after each test.

    Yields:
        None
    """
    # Remove all handlers
    logger.remove()
    yield
    # Logger will be reconfigured by next test or on import


# ============================================================================
# Mock Helper Functions
# ============================================================================

from contextlib import contextmanager
from unittest.mock import patch, MagicMock


@contextmanager
def mock_windows_file_ops():
    """Context manager for mocking Windows file operations.

    Mocks os.remove, os.rename, and os.unlink for Windows-specific file paths.
    All operations return successfully (None).

    Yields:
        dict: Dictionary with 'remove', 'rename', 'unlink' mock objects.

    Example:
        with mock_windows_file_ops() as mocks:
            work("search", "replace", "file.txt")
            assert mocks['remove'].call_count == 1
    """
    with (
        patch("os.remove") as mock_remove,
        patch("os.rename") as mock_rename,
        patch("os.unlink") as mock_unlink,
    ):

        # Configure mocks to succeed
        mock_remove.return_value = None
        mock_rename.return_value = None
        mock_unlink.return_value = None

        yield {"remove": mock_remove, "rename": mock_rename, "unlink": mock_unlink}


@contextmanager
def mock_file_operation_failure(operation, exception):
    """Context manager for mocking file operation failures.

    Args:
        operation: Name of the operation to mock (e.g., 'os.rename', 'tempfile.mkstemp')
        exception: Exception to raise when operation is called

    Yields:
        MagicMock: The mock object for the failed operation.

    Example:
        with mock_file_operation_failure('os.rename', RuntimeError("Disk full")):
            with pytest.raises(RuntimeError):
                work("search", "replace", "file.txt")
    """
    with patch(operation, side_effect=exception) as mock_op:
        yield mock_op


@contextmanager
def mock_backup_operations(restore_fails=False, cleanup_fails=False):
    """Context manager for mocking backup restore/cleanup operations.

    Args:
        restore_fails: If True, shutil.move raises OSError during restore
        cleanup_fails: If True, os.unlink raises OSError during cleanup

    Yields:
        dict: Dictionary with 'move', 'exists', 'unlink' mock objects.

    Example:
        with mock_backup_operations(restore_fails=True) as mocks:
            # Backup restoration will fail
            mocks['move'].assert_called()
    """
    with (
        patch("shutil.move") as mock_move,
        patch("os.path.exists", return_value=True) as mock_exists,
        patch("os.unlink") as mock_unlink,
    ):

        if restore_fails:
            mock_move.side_effect = OSError("Restore failed")
        if cleanup_fails:
            mock_unlink.side_effect = OSError("Cleanup failed")

        yield {"move": mock_move, "exists": mock_exists, "unlink": mock_unlink}

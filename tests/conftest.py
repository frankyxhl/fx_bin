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

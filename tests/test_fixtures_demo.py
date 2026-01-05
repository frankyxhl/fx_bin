"""Demo test to show temp_test_dir fixture usage (RED phase)."""

import pytest
from pathlib import Path


def test_given_temp_dir_when_creating_file_then_file_exists(temp_test_dir):
    """Test that temp_test_dir fixture provides a working temporary directory."""
    # GIVEN a temporary test directory from fixture
    assert temp_test_dir.exists()
    assert temp_test_dir.is_dir()

    # WHEN creating a file in that directory
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("test content")

    # THEN the file should exist and be readable
    assert test_file.exists()
    assert test_file.read_text() == "test content"


def test_given_temp_file_when_reading_then_content_available(temp_file):
    """Test that temp_file fixture provides a file with default content."""
    # GIVEN a temporary file from fixture
    assert temp_file.exists()

    # WHEN reading the file
    content = temp_file.read_text()

    # THEN it should have default content
    assert content == "test content"
    assert temp_file.parent.exists()

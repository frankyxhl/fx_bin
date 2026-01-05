"""Refactored tests for fx_replace module using pytest fixtures.

This demonstrates migrating from unittest.TestCase setUp/tearDown
to pytest fixtures for better test isolation and readability.
"""

from pathlib import Path
import pytest
from fx_bin.replace import work


# These tests use fixtures from conftest.py instead of setUp/tearDown


def test_given_file_with_single_match_when_replace_then_content_updated(temp_test_dir):
    """Test replacing a single occurrence."""
    # GIVEN a file with single occurrence
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    # WHEN replacing text
    work("World", "Python", str(test_file))

    # THEN content is updated
    content = test_file.read_text()
    assert content == "Hello Python"


def test_given_file_with_multiple_matches_when_replace_then_all_updated(temp_test_dir):
    """Test replacing multiple occurrences."""
    # GIVEN a file with multiple occurrences
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("test test test")

    # WHEN replacing text
    work("test", "demo", str(test_file))

    # THEN all occurrences are updated
    content = test_file.read_text()
    assert content == "demo demo demo"


def test_given_file_without_match_when_replace_then_content_unchanged(temp_test_dir):
    """Test when search text is not found."""
    # GIVEN a file without matching text
    test_file = temp_test_dir / "test.txt"
    original = "Hello World"
    test_file.write_text(original)

    # WHEN replacing non-existent text
    work("Python", "Java", str(test_file))

    # THEN content remains unchanged
    content = test_file.read_text()
    assert content == original


def test_given_multiline_file_when_replace_then_correct_line_updated(temp_test_dir):
    """Test replacing in multiline text."""
    # GIVEN a multiline file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("line1\nline2\nline3")

    # WHEN replacing text in middle line
    work("line2", "modified", str(test_file))

    # THEN only target line is updated
    content = test_file.read_text()
    assert content == "line1\nmodified\nline3"


def test_given_file_with_special_chars_when_replace_then_chars_replaced(temp_test_dir):
    """Test replacing special characters."""
    # GIVEN a file with special characters
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("foo.bar.baz")

    # WHEN replacing special character
    work(".", "_", str(test_file))

    # THEN all special characters are replaced
    content = test_file.read_text()
    assert content == "foo_bar_baz"


def test_given_empty_file_when_replace_then_file_stays_empty(temp_test_dir):
    """Test replacing in an empty file."""
    # GIVEN an empty file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("")

    # WHEN attempting replacement
    work("test", "demo", str(test_file))

    # THEN file remains empty
    content = test_file.read_text()
    assert content == ""

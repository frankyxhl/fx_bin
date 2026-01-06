"""Tests for fx_replace module using pytest.

Migrated from unittest.TestCase to pytest style with Given-When-Then structure.
Uses pytest fixtures for better test isolation and readability.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner

# Silence loguru during tests
from loguru import logger
logger.remove()

from fx_bin.replace import work, main


# ============================================================================
# Basic Replacement Tests (formerly TestReplaceWork)
# ============================================================================

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


# ============================================================================
# CLI Tests (formerly TestReplaceMain)
# ============================================================================

def test_given_single_file_when_main_invoked_then_replacement_succeeds(temp_test_dir):
    """Test replacing in a single file via CLI."""
    # GIVEN a file with content
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    # WHEN invoking CLI with replacement
    runner = CliRunner()
    result = runner.invoke(main, ["World", "Python", str(test_file)])

    # THEN command succeeds
    assert result.exit_code == 0
    # THEN content is updated
    content = test_file.read_text()
    assert content == "Hello Python"


def test_given_multiple_files_when_main_invoked_then_all_replaced(temp_test_dir):
    """Test replacing in multiple files."""
    # GIVEN multiple files with content
    file1 = temp_test_dir / "file1.txt"
    file2 = temp_test_dir / "file2.txt"
    file1.write_text("test content")
    file2.write_text("test data")

    # WHEN invoking CLI with multiple files
    runner = CliRunner()
    result = runner.invoke(main, ["test", "demo", str(file1), str(file2)])

    # THEN command succeeds
    assert result.exit_code == 0
    # THEN all files are updated
    assert file1.read_text() == "demo content"
    assert file2.read_text() == "demo data"


def test_given_nonexistent_file_when_main_invoked_then_error_returned(temp_test_dir):
    """Test error handling for nonexistent file."""
    # GIVEN a nonexistent file path
    nonexistent = temp_test_dir / "nonexistent.txt"

    # WHEN invoking CLI
    runner = CliRunner()
    result = runner.invoke(main, ["search", "replace", str(nonexistent)])

    # THEN command fails
    assert result.exit_code != 0
    # THEN error message mentions file
    assert "does not exist" in result.output


def test_given_no_files_when_main_invoked_then_handles_gracefully(temp_test_dir):
    """Test when no files are provided."""
    # GIVEN no file arguments
    # WHEN invoking CLI without files
    runner = CliRunner()
    result = runner.invoke(main, ["search", "replace"])

    # THEN command handles gracefully
    assert result.exit_code == 0


def test_given_mixed_files_when_main_invoked_then_validates_early(temp_test_dir):
    """Test with mix of existing and non-existing files."""
    # GIVEN one existing and one nonexistent file
    existing = temp_test_dir / "existing.txt"
    existing.write_text("test content")
    nonexistent = temp_test_dir / "nonexistent.txt"

    # WHEN invoking CLI with mixed files
    runner = CliRunner()
    result = runner.invoke(main, ["test", "demo", str(existing), str(nonexistent)])

    # THEN command fails due to validation
    assert result.exit_code != 0
    # THEN existing file is not modified (early exit)
    assert existing.read_text() == "test content"


# ============================================================================
# Error Handling Tests (formerly TestReplaceErrorHandling)
# ============================================================================

@patch("os.name", "nt")
def test_given_windows_when_replace_then_uses_windows_path(temp_test_dir):
    """Test Windows-specific file removal path."""
    # GIVEN a file on Windows
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    # WHEN replacing with mocked Windows operations
    with patch("os.remove") as mock_remove, \
         patch("os.rename") as mock_rename, \
         patch("os.unlink") as mock_unlink:
        # Make rename succeed after remove
        mock_rename.return_value = None
        mock_remove.return_value = None
        mock_unlink.return_value = None

        work("World", "Python", str(test_file))

        # THEN Windows path was taken (remove called once for file)
        assert mock_remove.call_count == 1
        mock_remove.assert_called_once_with(str(test_file))
        mock_rename.assert_called_once()
        # THEN backup cleanup uses os.unlink via cleanup_backup()
        assert mock_unlink.call_count == 1


def test_given_rename_fails_when_replace_then_restores_backup(temp_test_dir):
    """Test general exception handling during atomic replacement."""
    # GIVEN a file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    # WHEN rename raises unexpected error
    with patch("os.rename", side_effect=RuntimeError("Unexpected error")), \
         patch("shutil.move") as mock_move, \
         patch("os.path.exists", return_value=True):

        # THEN exception is raised
        with pytest.raises(RuntimeError):
            work("World", "Python", str(test_file))

        # THEN backup restoration was attempted
        mock_move.assert_called()


def test_given_temp_creation_fails_when_replace_then_cleans_up(temp_test_dir):
    """Test OSError during temp file cleanup."""
    # GIVEN a file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    # WHEN temp creation fails and cleanup also fails
    with patch("tempfile.mkstemp", side_effect=Exception("Temp creation failed")), \
         patch("os.path.exists", return_value=True), \
         patch("os.unlink", side_effect=OSError("Cleanup failed")):

        # THEN original exception is preserved
        with pytest.raises(Exception) as exc_info:
            work("World", "Python", str(test_file))

        assert "Temp creation failed" in str(exc_info.value)


def test_given_backup_restore_fails_when_replace_then_preserves_original_error(temp_test_dir):
    """Test OSError during backup restore."""
    # GIVEN a file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    # WHEN processing fails and restore also fails
    with patch("tempfile.mkstemp", side_effect=Exception("Processing failed")), \
         patch("os.path.exists", return_value=True), \
         patch("shutil.move", side_effect=OSError("Restore failed")):

        # THEN original exception is preserved
        with pytest.raises(Exception) as exc_info:
            work("World", "Python", str(test_file))

        assert "Processing failed" in str(exc_info.value)


def test_given_transaction_rollback_fails_when_batch_replace_then_handles_gracefully(temp_test_dir):
    """Test OSError during transaction rollback."""
    # GIVEN multiple files
    test_file1 = temp_test_dir / "file1.txt"
    test_file2 = temp_test_dir / "file2.txt"
    test_file1.write_text("content1")
    test_file2.write_text("content2")

    # WHEN work fails and rollback also fails
    runner = CliRunner()
    with patch("fx_bin.replace.work", side_effect=Exception("Work failed")), \
         patch("os.path.exists", return_value=True), \
         patch("shutil.move", side_effect=OSError("Rollback failed")):

        # THEN command exits with error
        result = runner.invoke(main, ["search", "replace", str(test_file1), str(test_file2)])
        assert result.exit_code != 0


def test_given_fdopen_fails_when_replace_then_attempts_all_cleanup(temp_test_dir):
    """Test remaining OSError paths in cleanup."""
    # GIVEN a file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("Hello World")

    # WHEN fdopen fails triggering exception cleanup
    with patch("tempfile.mkstemp") as mock_mkstemp, \
         patch("os.path.exists", return_value=True), \
         patch("os.unlink", side_effect=OSError("Cleanup unlink failed")) as mock_unlink, \
         patch("shutil.move", side_effect=OSError("Backup move failed")) as mock_move:

        # Make mkstemp return fake fd and path
        mock_mkstemp.return_value = (999, "/fake/temp/path")

        # Mock os.fdopen to fail
        with patch("os.fdopen", side_effect=Exception("fdopen failed")):
            # THEN exception is raised
            with pytest.raises(Exception) as exc_info:
                work("World", "Python", str(test_file))

            # THEN both cleanup paths were attempted despite errors
            mock_unlink.assert_called()  # Temp file cleanup OSError
            mock_move.assert_called()  # Backup restore OSError

            # THEN original exception is preserved
            assert "fdopen failed" in str(exc_info.value)


# ============================================================================
# Binary File Detection Tests (formerly TestBinaryFileDetection)
# ============================================================================

def test_given_binary_file_when_check_then_detected_as_binary(temp_test_dir):
    """Test that binary files are detected."""
    # GIVEN a binary file with null bytes
    from fx_bin.replace import _is_binary_file

    binary_file = temp_test_dir / "test.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03hello\x00world")

    # WHEN checking if binary
    is_binary = _is_binary_file(str(binary_file))

    # THEN detected as binary
    assert is_binary is True


def test_given_text_file_when_check_then_not_detected_as_binary(temp_test_dir):
    """Test that normal text files are not detected as binary."""
    # GIVEN a plain text file
    from fx_bin.replace import _is_binary_file

    text_file = temp_test_dir / "test.txt"
    text_file.write_text("Hello World\nThis is a text file.")

    # WHEN checking if binary
    is_binary = _is_binary_file(str(text_file))

    # THEN not detected as binary
    assert is_binary is False


def test_given_binary_file_when_work_called_then_file_skipped(temp_test_dir):
    """Test that work() skips binary files without raising errors."""
    # GIVEN a binary file
    binary_file = temp_test_dir / "test.bin"
    original_content = b"\x00\x01\x02\x03binary\x00data"
    binary_file.write_bytes(original_content)

    # WHEN calling work on binary file
    work("binary", "replaced", str(binary_file))

    # THEN file content is unchanged (skipped)
    assert binary_file.read_bytes() == original_content


def test_given_nonexistent_file_when_check_binary_then_treated_as_binary(temp_test_dir):
    """Test that unreadable files are treated as binary."""
    # GIVEN a nonexistent file path
    from fx_bin.replace import _is_binary_file

    nonexistent = str(temp_test_dir / "nonexistent.txt")

    # WHEN checking if binary
    is_binary = _is_binary_file(nonexistent)

    # THEN treated as binary (safe default for unreadable files)
    assert is_binary is True

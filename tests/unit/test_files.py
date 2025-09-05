"""Tests for fx_files module."""

import os
import tempfile
import unittest
from pathlib import Path

from fx_bin.common import FileCountEntry, EntryType
from fx_bin.files import list_files_count


class TestListFilesCount(unittest.TestCase):
    """Test list_files_count function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create test files
        (self.test_path / "file1.txt").touch()
        (self.test_path / "file2.txt").touch()
        (self.test_path / ".hidden").touch()

        # Create subdirectory with files
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "subfile1.txt").touch()
        (subdir / "subfile2.txt").touch()

        # Create nested subdirectory
        nested = subdir / "nested"
        nested.mkdir()
        (nested / "deep.txt").touch()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_list_files_count_basic(self):
        """Test basic file counting."""
        result = list_files_count(self.test_dir)

        # Should have file1.txt, file2.txt, and subdir (not .hidden)
        self.assertEqual(len(result), 3)

        # Check that entries are FileCountEntry objects
        for entry in result:
            self.assertIsInstance(entry, FileCountEntry)

    def test_list_files_count_with_hidden(self):
        """Test counting with hidden files."""
        result = list_files_count(self.test_dir, ignore_dot_file=False)

        # Should include .hidden file
        self.assertEqual(len(result), 4)

        # Check that .hidden is in the results
        names = [entry.name for entry in result]
        self.assertIn(".hidden", names)

    def test_file_count_values(self):
        """Test that file counts are correct."""
        result = list_files_count(self.test_dir)

        # Create a dict for easy lookup
        counts = {entry.name: entry.count for entry in result}

        # Individual files should have count 1
        self.assertEqual(counts.get("file1.txt"), 1)
        self.assertEqual(counts.get("file2.txt"), 1)

        # Subdir should have count 3 (subfile1, subfile2, deep.txt)
        self.assertEqual(counts.get("subdir"), 3)

    def test_list_files_count_sorting(self):
        """Test that results are sorted by count and name."""
        result = list_files_count(self.test_dir)

        # Check sorting order
        prev_count = 0
        prev_name = ""
        for entry in result:
            if entry.count == prev_count:
                # Same count, should be sorted by name
                self.assertGreater(entry.name, prev_name)
            else:
                # Different count, should be ascending
                self.assertGreater(entry.count, prev_count)
            prev_count = entry.count
            prev_name = entry.name

    def test_list_files_count_empty_dir(self):
        """Test counting in an empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            result = list_files_count(empty_dir)
            self.assertEqual(len(result), 0)
        finally:
            os.rmdir(empty_dir)

    def test_file_count_entry_display(self):
        """Test FileCountEntry display method."""
        entry = FileCountEntry("test.txt", 42, EntryType.FILE)

        # Test with different count widths
        self.assertEqual(entry.display(2), "42 test.txt")
        self.assertEqual(entry.display(5), "   42 test.txt")

    def test_file_vs_folder_type(self):
        """Test that files and folders have correct types."""
        result = list_files_count(self.test_dir)

        for entry in result:
            if entry.name in ["file1.txt", "file2.txt"]:
                self.assertEqual(entry.tpe, EntryType.FILE)
            elif entry.name == "subdir":
                self.assertEqual(entry.tpe, EntryType.FOLDER)

    def test_main_function_empty_directory(self):
        """Test main function with empty directory."""
        import io
        import sys
        from fx_bin.files import main

        # Create empty directory
        empty_dir = tempfile.mkdtemp()

        # Capture stdout
        captured_output = io.StringIO()
        original_stdout = sys.stdout

        try:
            sys.stdout = captured_output

            # Mock sys.argv to pass empty directory path
            original_argv = sys.argv
            sys.argv = ["fx_files", "--path", empty_dir]

            # This should trigger the "No files or directories found." message
            try:
                main()
            except SystemExit:
                pass  # Click exits with 0, which is expected

            # Check output
            output = captured_output.getvalue()
            self.assertIn("No files or directories found.", output)

        finally:
            sys.stdout = original_stdout
            sys.argv = original_argv
            os.rmdir(empty_dir)


if __name__ == "__main__":
    unittest.main()

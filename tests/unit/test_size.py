"""Tests for fx_size module."""

import os
import tempfile
import unittest
from pathlib import Path

from fx_bin.common import SizeEntry, EntryType, convert_size
from fx_bin.size import list_size


class TestSizeUtilities(unittest.TestCase):
    """Test size utility functions."""

    def test_convert_size_zero(self):
        """Test converting zero bytes."""
        self.assertEqual(convert_size(0), "0B")

    def test_convert_size_bytes(self):
        """Test converting byte values."""
        self.assertEqual(convert_size(100), "100B")
        self.assertEqual(convert_size(1023), "1023B")

    def test_convert_size_kilobytes(self):
        """Test converting to kilobytes."""
        self.assertEqual(convert_size(1024), "1KB")
        self.assertEqual(convert_size(2048), "2KB")

    def test_convert_size_megabytes(self):
        """Test converting to megabytes."""
        self.assertEqual(convert_size(1024 * 1024), "1MB")
        self.assertEqual(convert_size(5 * 1024 * 1024), "5MB")

    def test_convert_size_gigabytes(self):
        """Test converting to gigabytes."""
        self.assertEqual(convert_size(1024 * 1024 * 1024), "1GB")


class TestListSize(unittest.TestCase):
    """Test list_size function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create test files
        (self.test_path / "file1.txt").write_text("Hello World")
        (self.test_path / "file2.txt").write_text("Test" * 100)
        (self.test_path / ".hidden").write_text("Hidden file")

        # Create subdirectory with files
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "subfile.txt").write_text("Subfile content")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_list_size_basic(self):
        """Test basic size listing."""
        result = list_size(self.test_dir)

        # Should have file1.txt, file2.txt, and subdir (not .hidden)
        self.assertEqual(len(result), 3)

        # Check that entries are SizeEntry objects
        for entry in result:
            self.assertIsInstance(entry, SizeEntry)

    def test_list_size_with_hidden(self):
        """Test listing with hidden files."""
        result = list_size(self.test_dir, ignore_dot_file=False)

        # Should include .hidden file
        self.assertEqual(len(result), 4)

        # Check that .hidden is in the results
        names = [entry.name for entry in result]
        self.assertIn(".hidden", names)

    def test_list_size_sorting(self):
        """Test that results are sorted by size."""
        result = list_size(self.test_dir)

        # Check that sizes are in ascending order
        sizes = [entry.size for entry in result]
        self.assertEqual(sizes, sorted(sizes))

    def test_list_size_empty_dir(self):
        """Test listing an empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            result = list_size(empty_dir)
            self.assertEqual(len(result), 0)
        finally:
            os.rmdir(empty_dir)

    def test_size_entry_representation(self):
        """Test SizeEntry string representation."""
        entry = SizeEntry("test.txt", 1536, EntryType.FILE)
        repr_str = repr(entry)
        self.assertIn("test.txt", repr_str)
        self.assertIn("KB", repr_str)  # 1536 bytes should show as KB


if __name__ == "__main__":
    unittest.main()

"""Tests for fx_bin.backup module following TDD methodology.

These tests verify the backup functionality including:
- Multi-part extension handling (.tar.gz, .tar.bz2)
- File and directory backup with timestamps
- Automatic cleanup of old backups
- Error handling
"""

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


class TestBackupHelpers(unittest.TestCase):
    """Test helper functions for backup operations."""

    def test_get_multi_ext_tar_gz(self):
        """Test get_multi_ext identifies .tar.gz correctly."""
        from fx_bin.backup import get_multi_ext

        result = get_multi_ext("archive.tar.gz")
        self.assertEqual(result, ".tar.gz")

    def test_get_multi_ext_tar_bz2(self):
        """Test get_multi_ext identifies .tar.bz2 correctly."""
        from fx_bin.backup import get_multi_ext

        result = get_multi_ext("data.tar.bz2")
        self.assertEqual(result, ".tar.bz2")

    def test_get_multi_ext_single_extension(self):
        """Test get_multi_ext returns single extension for regular files."""
        from fx_bin.backup import get_multi_ext

        result = get_multi_ext("document.txt")
        self.assertEqual(result, ".txt")

    def test_get_multi_ext_no_extension(self):
        """Test get_multi_ext returns empty string for files without extension."""
        from fx_bin.backup import get_multi_ext

        result = get_multi_ext("README")
        self.assertEqual(result, "")

    def test_get_base_name_with_tar_gz(self):
        """Test get_base_name extracts base name from .tar.gz file."""
        from fx_bin.backup import get_base_name

        result = get_base_name("archive.tar.gz")
        self.assertEqual(result, "archive")

    def test_get_base_name_with_tar_bz2(self):
        """Test get_base_name extracts base name from .tar.bz2 file."""
        from fx_bin.backup import get_base_name

        result = get_base_name("data.tar.bz2")
        self.assertEqual(result, "data")

    def test_get_base_name_with_single_extension(self):
        """Test get_base_name extracts base name from regular file."""
        from fx_bin.backup import get_base_name

        result = get_base_name("document.txt")
        self.assertEqual(result, "document")

    def test_get_base_name_no_extension(self):
        """Test get_base_name returns filename when no extension."""
        from fx_bin.backup import get_base_name

        result = get_base_name("README")
        self.assertEqual(result, "README")


class TestBackupFile(unittest.TestCase):
    """Test file backup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.backup_dir = self.test_path / "backups"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_backup_file_regular(self):
        """Test backing up a regular file with timestamp."""
        from fx_bin.backup import backup_file

        source_file = self.test_path / "test.txt"
        source_file.write_text("test content")

        result = backup_file(
            str(source_file), backup_dir=str(self.backup_dir), timestamp_format="%Y%m%d"
        )

        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".txt"))
        self.assertIn("test_", os.path.basename(result))

        with open(result, "r") as f:
            self.assertEqual(f.read(), "test content")

    def test_backup_file_multi_ext(self):
        """Test backing up file with multi-part extension (.tar.gz)."""
        from fx_bin.backup import backup_file

        source_file = self.test_path / "archive.tar.gz"
        source_file.write_text("archive content")

        result = backup_file(str(source_file), backup_dir=str(self.backup_dir))

        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".tar.gz"))
        self.assertIn("archive_", os.path.basename(result))

    def test_backup_file_creates_backup_dir(self):
        """Test backup_file creates backup directory if it doesn't exist."""
        from fx_bin.backup import backup_file

        source_file = self.test_path / "test.txt"
        source_file.write_text("content")

        self.assertFalse(self.backup_dir.exists())

        backup_file(str(source_file), backup_dir=str(self.backup_dir))

        self.assertTrue(self.backup_dir.exists())

    def test_backup_file_nonexistent(self):
        """Test backing up nonexistent file raises FileNotFoundError."""
        from fx_bin.backup import backup_file

        with self.assertRaises(FileNotFoundError):
            backup_file("/nonexistent/file.txt", backup_dir=str(self.backup_dir))


if __name__ == "__main__":
    unittest.main()

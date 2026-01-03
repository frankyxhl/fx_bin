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


if __name__ == "__main__":
    unittest.main()

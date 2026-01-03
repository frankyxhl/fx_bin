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

    def test_backup_file_permission_error(self):
        from fx_bin.backup import backup_file
        import unittest.mock as mock

        source_file = self.test_path / "protected.txt"
        source_file.write_text("content")

        with mock.patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
            with self.assertRaises(PermissionError):
                backup_file(str(source_file), backup_dir=str(self.backup_dir))


class TestBackupDirectory(unittest.TestCase):
    """Test directory backup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.backup_dir = self.test_path / "backups"

        self.source_dir = self.test_path / "source_dir"
        self.source_dir.mkdir()
        (self.source_dir / "file1.txt").write_text("content1")
        (self.source_dir / "file2.txt").write_text("content2")

        subdir = self.source_dir / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested content")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_backup_directory_uncompressed(self):
        """Test backing up directory without compression."""
        from fx_bin.backup import backup_directory

        result = backup_directory(
            str(self.source_dir), backup_dir=str(self.backup_dir), compress=False
        )

        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.isdir(result))
        self.assertIn("source_dir_", os.path.basename(result))

        backup_file1 = Path(result) / "file1.txt"
        self.assertTrue(backup_file1.exists())
        self.assertEqual(backup_file1.read_text(), "content1")

        backup_nested = Path(result) / "subdir" / "nested.txt"
        self.assertTrue(backup_nested.exists())
        self.assertEqual(backup_nested.read_text(), "nested content")

    def test_backup_directory_compressed(self):
        """Test backing up directory with compression."""
        from fx_bin.backup import backup_directory
        import tarfile

        result = backup_directory(
            str(self.source_dir), backup_dir=str(self.backup_dir), compress=True
        )

        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".tar.gz"))
        self.assertIn("source_dir_", os.path.basename(result))

        with tarfile.open(result, "r:gz") as tar:
            members = tar.getnames()
            self.assertIn("source_dir/file1.txt", members)
            self.assertIn("source_dir/file2.txt", members)
            self.assertIn("source_dir/subdir/nested.txt", members)

    def test_backup_directory_nonexistent(self):
        """Test backing up nonexistent directory raises FileNotFoundError."""
        from fx_bin.backup import backup_directory

        with self.assertRaises(FileNotFoundError):
            backup_directory("/nonexistent/dir", backup_dir=str(self.backup_dir))


class TestBackupCleanup(unittest.TestCase):
    """Test backup cleanup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.backup_dir = self.test_path / "backups"
        self.backup_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_cleanup_old_backups_keeps_newest(self):
        """Test cleanup keeps only the N newest backups."""
        from fx_bin.backup import cleanup_old_backups
        import time

        base = "test"
        files = []
        for i in range(5):
            f = self.backup_dir / f"{base}_2025010100000{i}.txt"
            f.write_text(str(i))
            os.utime(f, (time.time() + i, time.time() + i))
            files.append(f)

        removed_count = cleanup_old_backups(
            str(self.backup_dir), base_name=base, max_backups=3
        )

        self.assertEqual(removed_count, 2)
        remaining = list(self.backup_dir.glob(f"{base}_*"))
        self.assertEqual(len(remaining), 3)

        remaining_names = [f.name for f in remaining]
        self.assertIn(f"{base}_20250101000002.txt", remaining_names)
        self.assertIn(f"{base}_20250101000003.txt", remaining_names)
        self.assertIn(f"{base}_20250101000004.txt", remaining_names)

    def test_cleanup_old_backups_under_limit(self):
        """Test cleanup does nothing if count is under limit."""
        from fx_bin.backup import cleanup_old_backups

        base = "test"
        for i in range(2):
            f = self.backup_dir / f"{base}_2025010100000{i}.txt"
            f.write_text(str(i))

        removed_count = cleanup_old_backups(
            str(self.backup_dir), base_name=base, max_backups=5
        )

        self.assertEqual(removed_count, 0)
        self.assertEqual(len(list(self.backup_dir.glob(f"{base}_*"))), 2)

    def test_cleanup_old_backups_mixed_types(self):
        """Test cleanup handles both files and directories."""
        from fx_bin.backup import cleanup_old_backups
        import time

        base = "app"
        f1 = self.backup_dir / f"{base}_20250101000000.txt"
        f1.write_text("v1")
        os.utime(f1, (time.time() - 100, time.time() - 100))

        d1 = self.backup_dir / f"{base}_20250101000001"
        d1.mkdir()
        os.utime(d1, (time.time() - 50, time.time() - 50))

        f2 = self.backup_dir / f"{base}_20250101000002.tar.gz"
        f2.write_text("v2")
        os.utime(f2, (time.time(), time.time()))

        removed_count = cleanup_old_backups(
            str(self.backup_dir), base_name=base, max_backups=1
        )

        self.assertEqual(removed_count, 2)
        remaining = list(self.backup_dir.glob(f"{base}_*"))
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].name, f"{base}_20250101000002.tar.gz")


if __name__ == "__main__":
    unittest.main()

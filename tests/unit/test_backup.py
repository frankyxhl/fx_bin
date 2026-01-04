"""Tests for fx_bin.backup module following TDD methodology.

These tests verify the backup functionality including:
- Multi-part extension handling (.tar.gz, .tar.bz2)
- File and directory backup with timestamps
- Error handling
"""

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from fx_bin.errors import FxBinError


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

        with mock.patch(
            "shutil.copy2", side_effect=PermissionError("Permission denied")
        ):
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
        self.assertTrue(result.endswith(".tar.xz"))
        self.assertIn("source_dir_", os.path.basename(result))

        with tarfile.open(result, "r:xz") as tar:
            members = tar.getnames()
            self.assertIn("source_dir/file1.txt", members)
            self.assertIn("source_dir/file2.txt", members)
            self.assertIn("source_dir/subdir/nested.txt", members)

    def test_backup_directory_preserves_symlinks(self):
        """Test backing up directory preserves symlinks (P1-1)."""
        from fx_bin.backup import backup_directory

        # Create a symlink in source directory
        target = self.test_path / "target.txt"
        target.write_text("target content")

        link = self.source_dir / "link.txt"
        link.symlink_to(target)

        self.assertTrue(link.is_symlink())

        result = backup_directory(
            str(self.source_dir), backup_dir=str(self.backup_dir), compress=False
        )

        backup_link = Path(result) / "link.txt"
        self.assertTrue(backup_link.is_symlink(), "Backup did not preserve symlink!")
        self.assertEqual(os.readlink(backup_link), str(target))

    def test_backup_file_collision_handling(self):
        """Test backup raises FxBinError on timestamp collisions."""
        from fx_bin.backup import backup_file
        import unittest.mock as mock

        source_file = self.test_path / "test.txt"
        source_file.write_text("content")

        # Mock datetime to always return the same time
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        with mock.patch("fx_bin.backup.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            # Use a fixed format that doesn't include microseconds for the test to force collision
            ts_format = "%Y%m%d"

            # First backup
            b1 = backup_file(
                str(source_file),
                backup_dir=str(self.backup_dir),
                timestamp_format=ts_format,
            )
            self.assertTrue(os.path.exists(b1))
            self.assertIn("test_20250101.txt", b1)

            with self.assertRaises(FxBinError) as cm:
                backup_file(
                    str(source_file),
                    backup_dir=str(self.backup_dir),
                    timestamp_format=ts_format,
                )
            self.assertIn("Backup path already exists", str(cm.exception))

    def test_backup_directory_collision_handling(self):
        """Test backup directory raises FxBinError on timestamp collisions."""
        from fx_bin.backup import backup_directory
        import unittest.mock as mock

        # Mock datetime to always return the same time
        fixed_now = datetime(2025, 1, 1, 12, 0, 0)
        with mock.patch("fx_bin.backup.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            ts_format = "%Y%m%d"

            backup_directory(
                str(self.source_dir),
                backup_dir=str(self.backup_dir),
                compress=False,
                timestamp_format=ts_format,
            )
            with self.assertRaises(FxBinError) as cm:
                backup_directory(
                    str(self.source_dir),
                    backup_dir=str(self.backup_dir),
                    compress=False,
                    timestamp_format=ts_format,
                )
            self.assertIn("Backup path already exists", str(cm.exception))

            backup_directory(
                str(self.source_dir),
                backup_dir=str(self.backup_dir),
                compress=True,
                timestamp_format=ts_format,
            )
            with self.assertRaises(FxBinError) as cm:
                backup_directory(
                    str(self.source_dir),
                    backup_dir=str(self.backup_dir),
                    compress=True,
                    timestamp_format=ts_format,
                )
            self.assertIn("Backup path already exists", str(cm.exception))

    def test_backup_directory_nonexistent(self):
        """Test backing up nonexistent directory raises FileNotFoundError."""
        from fx_bin.backup import backup_directory

        with self.assertRaises(FileNotFoundError):
            backup_directory("/nonexistent/dir", backup_dir=str(self.backup_dir))


if __name__ == "__main__":
    unittest.main()

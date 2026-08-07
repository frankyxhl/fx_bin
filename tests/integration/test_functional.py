"""Edge case tests for fx_bin.common."""

import os
import tempfile
import unittest
from pathlib import Path


class TestCommonEdgeCases(unittest.TestCase):
    """Test edge cases in common.py for improved coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_max_depth_recursion_limit(self):
        """Test depth limit reaches exactly 101 to trigger line 36 and 86."""
        from fx_bin.common import sum_folder_size, sum_folder_files_count

        # Test with exact depth limit to trigger the condition at line 36/86
        # We'll mock the _depth parameter to reach the limit

        # Create a simple directory structure
        test_file = self.test_path / "test.txt"
        test_file.write_text("test content")

        # Call with depth exactly at limit (101)
        result_size = sum_folder_size(
            str(self.test_path), _visited_inodes=set(), _depth=101
        )
        result_count = sum_folder_files_count(
            str(self.test_path), _visited_inodes=set(), _depth=101
        )

        # Should return 0 due to depth limit
        self.assertEqual(result_size, 0)
        self.assertEqual(result_count, 0)

    def test_symlink_cycle_detection_visited_inodes(self):
        """Test visited inode detection to trigger lines 46 and 96."""
        from fx_bin.common import sum_folder_size, sum_folder_files_count

        if os.name == "nt":  # Skip on Windows
            self.skipTest("Symlink test skipped on Windows")

        # Create directory structure
        test_file = self.test_path / "test.txt"
        test_file.write_text("test content")

        # Get the inode of the test directory
        dir_stat = os.stat(str(self.test_path))
        dir_inode = (dir_stat.st_dev, dir_stat.st_ino)

        # Call with this directory already in visited set
        visited_inodes = {dir_inode}

        result_size = sum_folder_size(
            str(self.test_path), _visited_inodes=visited_inodes, _depth=0
        )
        result_count = sum_folder_files_count(
            str(self.test_path), _visited_inodes=visited_inodes, _depth=0
        )

        # Should return 0 due to already visited
        self.assertEqual(result_size, 0)
        self.assertEqual(result_count, 0)

    def test_symlink_error_handling(self):
        """Test symlink error handling to trigger lines 63-66 and 113-116."""
        from fx_bin.common import sum_folder_size, sum_folder_files_count

        if os.name == "nt":  # Skip on Windows
            self.skipTest("Symlink test skipped on Windows")

        # Create a file and a symlink that points to it
        target_file = self.test_path / "target.txt"
        target_file.write_text("target content")

        symlink_file = self.test_path / "link_to_target"
        symlink_file.symlink_to(target_file)

        # Now delete the target to create a broken symlink
        target_file.unlink()

        # The broken symlink should be handled gracefully
        result_size = sum_folder_size(str(self.test_path))
        result_count = sum_folder_files_count(str(self.test_path))

        # Should not crash and return some result
        self.assertIsInstance(result_size, int)
        self.assertIsInstance(result_count, int)

    def test_from_scandir_permission_errors(self):
        """Test from_scandir methods with permission errors to trigger lines 186-187."""
        from fx_bin.common import SizeEntry, FileCountEntry
        from unittest.mock import MagicMock

        # Create a mock DirEntry that raises PermissionError for directories
        mock_entry_dir = MagicMock()
        mock_entry_dir.name = "restricted_dir"
        mock_entry_dir.is_file.return_value = False
        mock_entry_dir.is_dir.return_value = True
        mock_entry_dir.stat.side_effect = PermissionError("Access denied")
        mock_entry_dir.path = "/restricted/path"

        # Mock sum_folder_size to raise PermissionError
        from unittest.mock import patch

        with patch(
            "fx_bin.common.sum_folder_size",
            side_effect=PermissionError("Access denied"),
        ):
            with patch(
                "fx_bin.common.sum_folder_files_count",
                side_effect=PermissionError("Access denied"),
            ):
                # Test SizeEntry.from_scandir with permission error on directory
                result_size = SizeEntry.from_scandir(mock_entry_dir)
                self.assertIsNone(result_size)

                # Test FileCountEntry.from_scandir with permission error on directory
                result_count = FileCountEntry.from_scandir(mock_entry_dir)
                self.assertIsNone(result_count)

        # Test with file that raises PermissionError on stat()
        mock_entry_file = MagicMock()
        mock_entry_file.name = "restricted_file.txt"
        mock_entry_file.is_file.return_value = True
        mock_entry_file.is_dir.return_value = False
        mock_entry_file.stat.side_effect = OSError("I/O error")

        result_size_os = SizeEntry.from_scandir(mock_entry_file)
        self.assertIsNone(result_size_os)

    def test_symlink_file_access_errors(self):
        """Test handling of symlink file access errors."""
        from fx_bin.common import sum_folder_size, sum_folder_files_count
        from unittest.mock import patch, MagicMock

        if os.name == "nt":  # Skip on Windows
            self.skipTest("Symlink test skipped on Windows")

        # Create a real symlink to test with
        target_file = self.test_path / "target.txt"
        target_file.write_text("content")

        symlink_file = self.test_path / "test_link"
        symlink_file.symlink_to(target_file)

        # Mock os.scandir to return a DirEntry that causes errors
        original_scandir = os.scandir

        def mock_scandir(path):
            for entry in original_scandir(path):
                if entry.name == "test_link":
                    # Mock the entry to simulate various error conditions
                    mock_entry = MagicMock()
                    mock_entry.name = entry.name
                    mock_entry.path = entry.path
                    mock_entry.is_file.side_effect = (
                        lambda follow_symlinks=True: follow_symlinks and entry.is_file()
                    )
                    mock_entry.is_dir.side_effect = (
                        lambda follow_symlinks=True: follow_symlinks and entry.is_dir()
                    )
                    mock_entry.is_symlink.return_value = True
                    mock_entry.stat.side_effect = OSError("Stat error on symlink")
                    yield mock_entry
                else:
                    yield entry

        with patch("os.scandir", side_effect=mock_scandir):
            # This should trigger the error handling in symlink processing
            size = sum_folder_size(str(self.test_path))
            count = sum_folder_files_count(str(self.test_path))

            # Should handle the error gracefully
            self.assertIsInstance(size, int)
            self.assertIsInstance(count, int)


if __name__ == "__main__":
    unittest.main()

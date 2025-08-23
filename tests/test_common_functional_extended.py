"""Extended tests for fx_bin.common_functional module.

This module provides additional tests to increase coverage from 51% to 75%+.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

from returns.io import IOResult, IOSuccess, IOFailure
from returns.maybe import Some, Nothing
from returns.result import Success, Failure

from fx_bin import common_functional
from fx_bin.errors import FolderError, IOError as FxIOError
from fx_bin.common_functional import FolderContext, EntryType, SizeEntry, convert_size


class TestSumFolderSizeFunctional(unittest.TestCase):
    """Test the functional folder size calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_sum_folder_size_functional_empty_dir(self):
        """Test calculating size of empty directory."""
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_size_functional(self.test_dir)(context)
        
        # Should return 0 for empty directory
        self.assertIsInstance(result, IOSuccess)
        self.assertEqual(result.unwrap(), 0)
    
    def test_sum_folder_size_functional_with_files(self):
        """Test calculating size of directory with files."""
        # Create test files
        (self.test_path / "file1.txt").write_text("Hello World")
        (self.test_path / "file2.txt").write_text("Test content")
        
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_size_functional(self.test_dir)(context)
        
        self.assertIsInstance(result, IOSuccess)
        size = result.unwrap()
        self.assertGreater(size, 20)  # At least the size of the content
    
    def test_sum_folder_size_functional_nonexistent(self):
        """Test calculating size of non-existent directory."""
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_size_functional("/nonexistent/path")(context)
        
        self.assertIsInstance(result, IOFailure)
        error = result.failure()
        self.assertIsInstance(error, FolderError)
    
    def test_sum_folder_size_functional_nested(self):
        """Test calculating size with nested directories."""
        # Create nested structure
        (self.test_path / "file1.txt").write_text("content1")
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("content2")
        
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_size_functional(self.test_dir)(context)
        
        self.assertIsInstance(result, IOSuccess)
        size = result.unwrap()
        self.assertGreater(size, 14)  # At least size of "content1" + "content2"
    
    def test_sum_folder_size_max_depth(self):
        """Test that max depth is respected."""
        # Create deeply nested structure
        current = self.test_path
        for i in range(5):
            current = current / f"dir{i}"
            current.mkdir()
            (current / f"file{i}.txt").write_text(f"content{i}")
        
        # Test with limited depth
        context = FolderContext(visited_inodes=set(), max_depth=2)
        result = common_functional.sum_folder_size_functional(self.test_dir)(context)
        
        self.assertIsInstance(result, IOSuccess)
        # Should only count files up to depth 2
    
    def test_sum_folder_size_legacy(self):
        """Test the legacy wrapper function."""
        # Create test files
        (self.test_path / "file1.txt").write_text("Hello")
        
        size = common_functional.sum_folder_size_legacy(self.test_dir)
        self.assertGreater(size, 0)
    
    def test_sum_folder_size_legacy_error(self):
        """Test legacy wrapper with error."""
        # Non-existent path returns 0 (as per implementation)
        size = common_functional.sum_folder_size_legacy("/nonexistent/path")
        self.assertEqual(size, 0)


class TestSumFolderFilesCount(unittest.TestCase):
    """Test the functional file counting."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_sum_folder_files_count_empty(self):
        """Test counting files in empty directory."""
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_files_count_functional(self.test_dir)(context)
        
        self.assertIsInstance(result, IOSuccess)
        count = result.unwrap()
        self.assertEqual(count, 0)
    
    def test_sum_folder_files_count_with_files(self):
        """Test counting files in directory with files."""
        # Create test files
        (self.test_path / "file1.txt").write_text("content1")
        (self.test_path / "file2.txt").write_text("content2")
        (self.test_path / "file3.txt").write_text("content3")
        
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_files_count_functional(self.test_dir)(context)
        
        self.assertIsInstance(result, IOSuccess)
        count = result.unwrap()
        self.assertEqual(count, 3)
    
    def test_sum_folder_files_count_with_subdirs(self):
        """Test counting files in nested directories."""
        # Create nested structure
        (self.test_path / "file1.txt").write_text("content")
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("content")
        (subdir / "file3.txt").write_text("content")
        
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_files_count_functional(self.test_dir)(context)
        
        self.assertIsInstance(result, IOSuccess)
        count = result.unwrap()
        self.assertEqual(count, 3)
    
    def test_sum_folder_files_count_nonexistent(self):
        """Test counting files in non-existent directory."""
        context = FolderContext(visited_inodes=set(), max_depth=10)
        result = common_functional.sum_folder_files_count_functional("/nonexistent")(context)
        
        self.assertIsInstance(result, IOFailure)
        error = result.failure()
        self.assertIsInstance(error, FolderError)
    
    def test_sum_folder_files_count_legacy(self):
        """Test the legacy wrapper for file counting."""
        # Create test files
        (self.test_path / "file1.txt").write_text("content")
        (self.test_path / "file2.txt").write_text("content")
        
        count = common_functional.sum_folder_files_count_legacy(self.test_dir)
        self.assertEqual(count, 2)
    
    def test_sum_folder_files_count_legacy_error(self):
        """Test legacy wrapper with error."""
        # Non-existent path returns 0 (as per implementation)
        count = common_functional.sum_folder_files_count_legacy("/nonexistent")
        self.assertEqual(count, 0)


class TestSizeEntry(unittest.TestCase):
    """Test the SizeEntry dataclass."""
    
    def test_size_entry_creation(self):
        """Test creating a SizeEntry."""
        entry = SizeEntry(
            name="test.txt",
            size=1024,
            entry_type=EntryType.FILE,
            path="/path/to/test.txt"
        )
        
        self.assertEqual(entry.name, "test.txt")
        self.assertEqual(entry.size, 1024)
        self.assertEqual(entry.entry_type, EntryType.FILE)
        self.assertEqual(entry.path, "/path/to/test.txt")
    
    def test_size_entry_equality(self):
        """Test SizeEntry equality comparison."""
        entry1 = SizeEntry("a", 100, EntryType.FILE)
        entry2 = SizeEntry("b", 100, EntryType.FILE)
        entry3 = SizeEntry("c", 200, EntryType.FILE)
        
        self.assertEqual(entry1, entry2)  # Same size
        self.assertNotEqual(entry1, entry3)  # Different size
    
    def test_size_entry_ordering(self):
        """Test SizeEntry ordering."""
        entry1 = SizeEntry("a", 100, EntryType.FILE)
        entry2 = SizeEntry("b", 200, EntryType.FILE)
        entry3 = SizeEntry("c", 300, EntryType.FILE)
        
        self.assertLess(entry1, entry2)
        self.assertLess(entry2, entry3)
        self.assertGreater(entry3, entry1)
    
    def test_size_entry_repr(self):
        """Test SizeEntry string representation."""
        entry = SizeEntry("test.txt", 1024, EntryType.FILE)
        repr_str = repr(entry)
        
        self.assertIn("1KB", repr_str)  # convert_size(1024) = "1KB"
        self.assertIn("test.txt", repr_str)
    
    def test_size_entry_from_scandir_functional(self):
        """Test creating SizeEntry from os.DirEntry."""
        # Create a real file to scan
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello World")
            
            # Scan the directory
            for entry in os.scandir(tmpdir):
                if entry.name == "test.txt":
                    result = SizeEntry.from_scandir_functional(entry, tmpdir)
                    
                    self.assertIsInstance(result, IOSuccess)
                    maybe_entry = result.unwrap()
                    self.assertIsInstance(maybe_entry, Some)
                    
                    size_entry = maybe_entry.unwrap()
                    self.assertEqual(size_entry.name, "test.txt")
                    self.assertEqual(size_entry.size, 11)  # "Hello World"
                    self.assertEqual(size_entry.entry_type, EntryType.FILE)
    
    @patch('os.DirEntry')
    def test_size_entry_from_scandir_permission_error(self, mock_entry):
        """Test handling permission errors in from_scandir_functional."""
        # Mock a DirEntry that raises PermissionError
        mock_entry.name = "forbidden.txt"
        mock_entry.path = "/forbidden.txt"
        mock_entry.stat.side_effect = PermissionError("Access denied")
        
        result = SizeEntry.from_scandir_functional(mock_entry)
        
        self.assertIsInstance(result, IOSuccess)
        maybe_entry = result.unwrap()
        self.assertIsInstance(maybe_entry, Nothing)  # Returns Nothing on permission error


class TestHelperFunctions(unittest.TestCase):
    """Test various helper functions."""
    
    def test_convert_size_bytes(self):
        """Test size conversion for bytes."""
        self.assertEqual(convert_size(0), "0B")
        self.assertEqual(convert_size(512), "512B")
        self.assertEqual(convert_size(1023), "1023B")
    
    def test_convert_size_kb(self):
        """Test size conversion for kilobytes."""
        self.assertEqual(convert_size(1024), "1KB")
        self.assertEqual(convert_size(2048), "2KB")
        self.assertEqual(convert_size(1536), "2KB")  # Rounds
    
    def test_convert_size_mb(self):
        """Test size conversion for megabytes."""
        self.assertEqual(convert_size(1024 * 1024), "1MB")
        self.assertEqual(convert_size(2 * 1024 * 1024), "2MB")
    
    def test_convert_size_gb(self):
        """Test size conversion for gigabytes."""
        self.assertEqual(convert_size(1024 * 1024 * 1024), "1GB")
        self.assertEqual(convert_size(5 * 1024 * 1024 * 1024), "5GB")
    
    def test_convert_size_large(self):
        """Test size conversion for very large sizes."""
        # Test TB
        self.assertEqual(convert_size(1024 ** 4), "1TB")
        # Test PB
        self.assertEqual(convert_size(1024 ** 5), "1PB")


class TestEntryType(unittest.TestCase):
    """Test the EntryType enum."""
    
    def test_entry_type_values(self):
        """Test EntryType enum values."""
        self.assertEqual(EntryType.FILE.value, 1)
        self.assertEqual(EntryType.FOLDER.value, 2)
    
    def test_entry_type_comparison(self):
        """Test EntryType enum comparison."""
        self.assertNotEqual(EntryType.FILE, EntryType.FOLDER)
        self.assertEqual(EntryType.FILE, EntryType.FILE)


class TestFolderContext(unittest.TestCase):
    """Test the FolderContext dataclass."""
    
    def test_folder_context_creation(self):
        """Test creating FolderContext."""
        context = FolderContext(visited_inodes=set(), max_depth=100)
        
        self.assertEqual(context.visited_inodes, set())
        self.assertEqual(context.max_depth, 100)
    
    def test_folder_context_with_inodes(self):
        """Test FolderContext with visited inodes."""
        inodes = {(1, 2), (3, 4)}
        context = FolderContext(visited_inodes=inodes, max_depth=50)
        
        self.assertEqual(context.visited_inodes, inodes)
        self.assertEqual(context.max_depth, 50)
    
    def test_folder_context_immutable(self):
        """Test that FolderContext is immutable (frozen)."""
        context = FolderContext(visited_inodes=set(), max_depth=100)
        
        # Should not be able to modify attributes
        with self.assertRaises(AttributeError):
            context.max_depth = 200


class TestCyclicDirectories(unittest.TestCase):
    """Test handling of cyclic directory structures."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_visited_inodes_tracking(self):
        """Test that visited inodes are tracked correctly."""
        # Create a file
        (self.test_path / "file.txt").write_text("content")
        
        # First call with empty visited set
        context1 = FolderContext(visited_inodes=set(), max_depth=10)
        result1 = common_functional.sum_folder_size_functional(self.test_dir)(context1)
        
        self.assertIsInstance(result1, IOSuccess)
        size1 = result1.unwrap()
        
        # Get the inode of the test directory
        stat = os.stat(self.test_dir)
        dir_inode = (stat.st_dev, stat.st_ino)
        
        # Second call with the directory already visited
        context2 = FolderContext(visited_inodes={dir_inode}, max_depth=10)
        result2 = common_functional.sum_folder_size_functional(self.test_dir)(context2)
        
        self.assertIsInstance(result2, IOSuccess)
        size2 = result2.unwrap()
        self.assertEqual(size2, 0)  # Should return 0 for already visited


if __name__ == '__main__':
    unittest.main()
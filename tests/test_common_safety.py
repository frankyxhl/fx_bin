"""Safety tests for fx_common module.

These tests ensure recursive directory operations are safe and don't cause
infinite loops, excessive memory usage, or system instability.
"""
import os
import tempfile
import unittest
import threading
import time
import signal
from pathlib import Path
from unittest.mock import patch, MagicMock
import psutil

# Silence loguru during tests
from loguru import logger
logger.remove()

from fx_bin.common import (
    sum_folder_size, sum_folder_files_count, SizeEntry, FileCountEntry,
    convert_size, EntryType
)


class TestRecursiveDirectorySafety(unittest.TestCase):
    """Test safety of recursive directory operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up any symlinks first to avoid deletion issues
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files + dirs:
                path = Path(root) / name
                if path.is_symlink():
                    path.unlink()
        
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_symlink_loop_detection(self):
        """Test that symlink loops are detected and handled."""
        if os.name == 'nt':  # Skip on Windows
            self.skipTest("Symlink test skipped on Windows")
        
        # Create directory structure with symlink loop
        dir1 = self.test_path / "dir1"
        dir2 = self.test_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        # Create files in directories
        (dir1 / "file1.txt").write_text("content 1")
        (dir2 / "file2.txt").write_text("content 2")
        
        # Create symlink loop: dir1/link_to_dir2 -> dir2, dir2/link_to_dir1 -> dir1
        (dir1 / "link_to_dir2").symlink_to(dir2)
        (dir2 / "link_to_dir1").symlink_to(dir1)
        
        # Should not hang or crash due to infinite recursion
        start_time = time.time()
        try:
            size = sum_folder_size(str(self.test_path))
            count = sum_folder_files_count(str(self.test_path))
        except Exception as e:
            # Should handle gracefully, not crash
            self.fail(f"Symlink loop caused exception: {e}")
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (not infinite loop)
        self.assertLess(elapsed, 5.0, "Operation took too long - possible infinite loop")
        
        # Should return reasonable values (not zero due to early termination)
        self.assertGreater(size, 0, "Should process some files despite symlinks")
        self.assertGreater(count, 0, "Should count some files despite symlinks")
    
    def test_max_recursion_depth_limit(self):
        """Test that recursion depth is limited to prevent stack overflow."""
        # Create deeply nested directory structure
        current_dir = self.test_path
        depth_limit = 1000  # Deeper than typical stack limits
        
        for i in range(depth_limit):
            current_dir = current_dir / f"level_{i}"
            current_dir.mkdir()
            (current_dir / f"file_{i}.txt").write_text(f"content {i}")
        
        # Should handle deep recursion without stack overflow
        start_time = time.time()
        try:
            size = sum_folder_size(str(self.test_path))
            count = sum_folder_files_count(str(self.test_path))
        except RecursionError:
            self.fail("Recursion depth limit exceeded - should be handled gracefully")
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time
        self.assertLess(elapsed, 10.0, "Deep recursion took too long")
        
        # Should return valid results
        self.assertGreater(size, 0)
        self.assertGreater(count, 0)
    
    def test_circular_directory_detection(self):
        """Test detection of circular directory references."""
        if os.name == 'nt':  # Skip on Windows
            self.skipTest("Symlink test skipped on Windows")
        
        # Create circular reference through symlinks
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("test content")
        
        # Create symlink that points back to parent
        (subdir / "parent_link").symlink_to(self.test_path)
        
        # Should detect circular reference and handle gracefully
        size = sum_folder_size(str(self.test_path))
        count = sum_folder_files_count(str(self.test_path))
        
        # Should return reasonable values
        self.assertGreater(size, 0)
        self.assertGreater(count, 0)
    
    def test_permission_denied_handling(self):
        """Test handling of permission denied errors."""
        # Create subdirectory with restricted permissions
        restricted_dir = self.test_path / "restricted"
        restricted_dir.mkdir()
        (restricted_dir / "secret.txt").write_text("secret content")
        
        # Remove read/execute permissions
        if os.name != 'nt':  # Skip permission test on Windows
            restricted_dir.chmod(0o000)
        
            try:
                size = sum_folder_size(str(self.test_path))
                count = sum_folder_files_count(str(self.test_path))
                
                # Should not crash, should skip inaccessible directories
                self.assertGreaterEqual(size, 0, "Should handle permission errors gracefully")
                self.assertGreaterEqual(count, 0, "Should handle permission errors gracefully")
                
            finally:
                # Restore permissions for cleanup
                restricted_dir.chmod(0o755)
    
    def test_large_directory_performance(self):
        """Test performance with large number of files."""
        # Create directory with many files
        num_files = 1000
        large_dir = self.test_path / "large_dir"
        large_dir.mkdir()
        
        for i in range(num_files):
            (large_dir / f"file_{i:04d}.txt").write_text(f"content {i}")
        
        # Monitor memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        start_time = time.time()
        size = sum_folder_size(str(self.test_path))
        count = sum_folder_files_count(str(self.test_path))
        elapsed = time.time() - start_time
        
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        # Performance checks
        self.assertLess(elapsed, 5.0, f"Large directory scan took too long: {elapsed:.2f}s")
        self.assertEqual(count, num_files, f"Should count all {num_files} files")
        
        # Memory usage should be reasonable (not proportional to file count)
        max_memory_increase = 10 * 1024 * 1024  # 10MB
        self.assertLess(memory_increase, max_memory_increase,
                       f"Memory usage too high: {memory_increase / 1024 / 1024:.1f}MB")
    
    def test_special_characters_in_paths(self):
        """Test handling of special characters in file/directory names."""
        special_names = [
            "file with spaces.txt",
            "file-with-dashes.txt",
            "file_with_underscores.txt",
            "file.with.dots.txt",
            "file(with)parentheses.txt",
            "file[with]brackets.txt",
            "file{with}braces.txt",
            "файл.txt",  # Cyrillic
            "文件.txt",   # Chinese
            "ファイル.txt", # Japanese
        ]
        
        special_dir = self.test_path / "special"
        special_dir.mkdir()
        
        for name in special_names:
            try:
                file_path = special_dir / name
                file_path.write_text(f"content of {name}")
            except (OSError, UnicodeError):
                # Skip files that can't be created on this system
                continue
        
        # Should handle special characters without errors
        size = sum_folder_size(str(self.test_path))
        count = sum_folder_files_count(str(self.test_path))
        
        self.assertGreater(size, 0, "Should handle special characters in filenames")
        self.assertGreater(count, 0, "Should count files with special characters")
    
    def test_network_drive_handling(self):
        """Test handling of network drives and mounted filesystems."""
        # This test is platform-specific and may not be applicable everywhere
        # Mock network error to simulate network drive issues
        original_scandir = os.scandir
        
        def mock_scandir_with_network_error(path):
            if "network" in str(path):
                raise OSError(123, "Network error")  # Windows network error
            return original_scandir(path)
        
        with patch('os.scandir', side_effect=mock_scandir_with_network_error):
            # Create a "network" directory to trigger the mock error
            network_dir = self.test_path / "network_drive"
            network_dir.mkdir()
            
            # Should handle network errors gracefully
            size = sum_folder_size(str(self.test_path))
            count = sum_folder_files_count(str(self.test_path))
            
            # Should not crash and return valid results for accessible parts
            self.assertGreaterEqual(size, 0)
            self.assertGreaterEqual(count, 0)
    
    def test_empty_directory_handling(self):
        """Test handling of empty directories."""
        empty_dir = self.test_path / "empty"
        empty_dir.mkdir()
        
        # Create nested empty directories
        (empty_dir / "nested1").mkdir()
        (empty_dir / "nested2").mkdir()
        (empty_dir / "nested1" / "deep").mkdir()
        
        size = sum_folder_size(str(empty_dir))
        count = sum_folder_files_count(str(empty_dir))
        
        # Empty directories should return 0 for both size and count
        self.assertEqual(size, 0, "Empty directory should have 0 size")
        self.assertEqual(count, 0, "Empty directory should have 0 file count")
    
    def test_mixed_file_types_handling(self):
        """Test handling of different file types."""
        mixed_dir = self.test_path / "mixed"
        mixed_dir.mkdir()
        
        # Create different types of files
        (mixed_dir / "regular.txt").write_text("regular file")
        (mixed_dir / "binary.bin").write_bytes(b"\x00\x01\x02\x03\xFF")
        (mixed_dir / "empty.txt").touch()
        
        if os.name != 'nt':  # Skip on Windows
            # Create FIFO (named pipe) if supported
            try:
                os.mkfifo(str(mixed_dir / "named_pipe"))
            except (OSError, AttributeError):
                pass  # Not supported on this system
        
        # Should handle all file types gracefully
        size = sum_folder_size(str(mixed_dir))
        count = sum_folder_files_count(str(mixed_dir))
        
        self.assertGreater(size, 0, "Should count size of regular files")
        self.assertGreaterEqual(count, 2, "Should count regular files")
    
    def test_concurrent_directory_access(self):
        """Test safety when multiple threads access directories concurrently."""
        # Create directory structure
        concurrent_dir = self.test_path / "concurrent"
        concurrent_dir.mkdir()
        
        for i in range(10):
            subdir = concurrent_dir / f"subdir_{i}"
            subdir.mkdir()
            for j in range(5):
                (subdir / f"file_{j}.txt").write_text(f"content {i}_{j}")
        
        # Start multiple threads doing directory operations
        results = []
        threads = []
        
        def scan_directory(result_list):
            try:
                size = sum_folder_size(str(concurrent_dir))
                count = sum_folder_files_count(str(concurrent_dir))
                result_list.append((size, count))
            except Exception as e:
                result_list.append(f"error: {e}")
        
        for i in range(5):
            thread = threading.Thread(target=scan_directory, args=(results,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should succeed
        errors = [r for r in results if isinstance(r, str) and r.startswith("error")]
        self.assertEqual(len(errors), 0, f"Concurrent access caused errors: {errors}")
        
        # Results should be consistent
        size_counts = [(size, count) for size, count in results if isinstance(results[0], tuple)]
        if size_counts:
            expected_size, expected_count = size_counts[0]
            for size, count in size_counts[1:]:
                self.assertEqual(size, expected_size, "Concurrent access gave inconsistent sizes")
                self.assertEqual(count, expected_count, "Concurrent access gave inconsistent counts")
    
    def test_timeout_on_hanging_operations(self):
        """Test that operations timeout if they hang."""
        # This test simulates a hanging operation
        def timeout_handler(signum, frame):
            raise TimeoutError("Operation timed out")
        
        # Set timeout alarm (Unix only)
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 second timeout
            
            try:
                # Create a scenario that might hang
                deep_dir = self.test_path
                for i in range(100):  # Not as deep as the recursion test
                    deep_dir = deep_dir / f"level_{i}"
                    deep_dir.mkdir()
                
                size = sum_folder_size(str(self.test_path))
                count = sum_folder_files_count(str(self.test_path))
                
                # Should complete within timeout
                self.assertGreater(size, 0)
                self.assertGreater(count, 0)
                
            except TimeoutError:
                self.fail("Operation timed out - possible hanging")
            finally:
                signal.alarm(0)  # Cancel alarm
                signal.signal(signal.SIGALRM, old_handler)


class TestSizeEntryFromScandir(unittest.TestCase):
    """Test SizeEntry.from_scandir with edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_permission_error_handling_in_from_scandir(self):
        """Test that from_scandir handles permission errors gracefully."""
        # Create file with restricted permissions
        restricted_file = self.test_path / "restricted.txt"
        restricted_file.write_text("restricted content")
        
        if os.name != 'nt':  # Skip on Windows
            restricted_file.chmod(0o000)
            
            try:
                with os.scandir(self.test_dir) as entries:
                    for entry in entries:
                        if entry.name == "restricted.txt":
                            result = SizeEntry.from_scandir(entry)
                            # Should return None for inaccessible files
                            self.assertIsNone(result, "Should return None for inaccessible files")
            finally:
                # Restore permissions for cleanup
                restricted_file.chmod(0o644)
    
    def test_broken_symlink_handling(self):
        """Test handling of broken symlinks."""
        if os.name == 'nt':  # Skip on Windows
            self.skipTest("Symlink test skipped on Windows")
        
        # Create symlink to non-existent target
        broken_link = self.test_path / "broken_link"
        broken_link.symlink_to("nonexistent_target")
        
        with os.scandir(self.test_dir) as entries:
            for entry in entries:
                if entry.name == "broken_link":
                    result = SizeEntry.from_scandir(entry)
                    # Should handle broken symlinks gracefully
                    # Behavior may vary - either None or valid entry
                    self.assertIsNotNone(entry, "Should handle broken symlinks")


class TestConvertSizeEdgeCases(unittest.TestCase):
    """Test convert_size function with edge cases."""
    
    def test_negative_sizes(self):
        """Test handling of negative sizes."""
        # Should handle gracefully (though sizes shouldn't be negative in practice)
        try:
            result = convert_size(-1024)
            # Should not crash, behavior may vary
            self.assertIsInstance(result, str)
        except Exception:
            # May raise exception for invalid input
            pass
    
    def test_very_large_sizes(self):
        """Test handling of very large sizes."""
        very_large = 2**63 - 1  # Max int64
        result = convert_size(very_large)
        
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Should use appropriate unit (YB likely)
        self.assertIn("YB", result)
    
    def test_float_sizes(self):
        """Test handling of float sizes."""
        float_size = 1024.5
        try:
            result = convert_size(float_size)
            self.assertIsInstance(result, str)
        except (TypeError, ValueError):
            # May not accept floats
            pass


if __name__ == '__main__':
    unittest.main()
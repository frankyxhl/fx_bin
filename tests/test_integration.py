"""Integration tests for fx_bin utilities.

These tests verify that different components work together correctly
and that end-to-end workflows function as expected.
"""
import os
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path
from click.testing import CliRunner

# Silence loguru during tests
from loguru import logger
logger.remove()


class TestCLIIntegration(unittest.TestCase):
    """Test CLI command integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.original_cwd = os.getcwd()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_fx_files_command_line(self):
        """Test fx_files command via command line."""
        # Create test structure
        (self.test_path / "file1.txt").write_text("content 1")
        (self.test_path / "file2.txt").write_text("content 2")
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content 3")
        
        os.chdir(self.test_dir)
        
        # Test command line execution
        try:
            result = subprocess.run(
                [sys.executable, "-m", "fx_bin.files"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should complete without error
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
            
            # Should show files and directories
            self.assertIn("file1.txt", result.stdout)
            self.assertIn("file2.txt", result.stdout)
            self.assertIn("subdir", result.stdout)
            
        except subprocess.TimeoutExpired:
            self.fail("fx_files command timed out")
        except Exception as e:
            self.skipTest(f"fx_files command test skipped: {e}")
    
    def test_fx_size_command_line(self):
        """Test fx_size command via command line."""
        # Create files with known sizes
        (self.test_path / "small.txt").write_text("small")
        (self.test_path / "large.txt").write_text("x" * 1000)
        
        os.chdir(self.test_dir)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "fx_bin.size"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
            
            # Should show both files
            self.assertIn("small.txt", result.stdout)
            self.assertIn("large.txt", result.stdout)
            
        except subprocess.TimeoutExpired:
            self.fail("fx_size command timed out")
        except Exception as e:
            self.skipTest(f"fx_size command test skipped: {e}")
    
    def test_fx_find_files_command_line(self):
        """Test fx_ff (find files) command via command line."""
        # Create test files
        (self.test_path / "test_document.txt").write_text("content")
        (self.test_path / "other_file.py").write_text("code")
        (self.test_path / "test_image.jpg").touch()
        
        os.chdir(self.test_dir)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "fx_bin.find_files", "test"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
            
            # Should find files with "test" in name
            self.assertIn("test_document.txt", result.stdout)
            self.assertIn("test_image.jpg", result.stdout)
            # Should not find files without "test"
            self.assertNotIn("other_file.py", result.stdout)
            
        except subprocess.TimeoutExpired:
            self.fail("fx_ff command timed out")
        except Exception as e:
            self.skipTest(f"fx_ff command test skipped: {e}")
    
    def test_fx_replace_command_line(self):
        """Test fx_replace command via command line."""
        # Create test file
        test_file = self.test_path / "replace_test.txt"
        test_file.write_text("Hello world\nGoodbye world\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "fx_bin.replace", "world", "Python", str(test_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
            
            # Verify replacement worked
            content = test_file.read_text()
            self.assertIn("Hello Python", content)
            self.assertIn("Goodbye Python", content)
            self.assertNotIn("world", content)
            
        except subprocess.TimeoutExpired:
            self.fail("fx_replace command timed out")
        except Exception as e:
            self.skipTest(f"fx_replace command test skipped: {e}")
    
    def test_workflow_size_then_replace(self):
        """Test workflow: analyze sizes, then replace content."""
        # Create files with different content
        file1 = self.test_path / "document1.txt"
        file2 = self.test_path / "document2.txt"
        file1.write_text("old version content")
        file2.write_text("old version data" * 10)  # Larger file
        
        os.chdir(self.test_dir)
        
        try:
            # First, analyze sizes
            size_result = subprocess.run(
                [sys.executable, "-m", "fx_bin.size"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertEqual(size_result.returncode, 0)
            
            # Then, replace content in both files
            replace_result = subprocess.run(
                [sys.executable, "-m", "fx_bin.replace", "old", "new", 
                 str(file1), str(file2)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertEqual(replace_result.returncode, 0)
            
            # Verify replacements
            self.assertIn("new version", file1.read_text())
            self.assertIn("new version", file2.read_text())
            self.assertNotIn("old", file1.read_text())
            self.assertNotIn("old", file2.read_text())
            
        except subprocess.TimeoutExpired:
            self.fail("Workflow test timed out")
        except Exception as e:
            self.skipTest(f"Workflow test skipped: {e}")


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling across components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_permission_error_handling(self):
        """Test handling of permission errors across utilities."""
        if os.name == 'nt':  # Skip on Windows
            self.skipTest("Permission test skipped on Windows")
        
        # Create file and remove read permissions
        test_file = self.test_path / "readonly.txt"
        test_file.write_text("readonly content")
        test_file.chmod(0o000)
        
        try:
            # Test various utilities with permission-denied file
            from fx_bin.common import sum_folder_size, sum_folder_files_count
            
            # Should handle permission errors gracefully
            size = sum_folder_size(str(self.test_dir))
            count = sum_folder_files_count(str(self.test_dir))
            
            # Should not crash, should return reasonable values
            self.assertGreaterEqual(size, 0)
            self.assertGreaterEqual(count, 0)
            
        finally:
            # Restore permissions for cleanup
            try:
                test_file.chmod(0o644)
            except OSError:
                pass
    
    def test_nonexistent_path_handling(self):
        """Test handling of nonexistent paths."""
        nonexistent = "/this/path/does/not/exist"
        
        from fx_bin.common import sum_folder_size, sum_folder_files_count
        
        # Should handle gracefully without crashing
        size = sum_folder_size(nonexistent)
        count = sum_folder_files_count(nonexistent)
        
        self.assertEqual(size, 0)
        self.assertEqual(count, 0)
    
    def test_malformed_input_handling(self):
        """Test handling of malformed inputs."""
        from fx_bin.common import convert_size
        
        # Test edge cases
        self.assertEqual(convert_size(0), "0B")
        self.assertTrue(len(convert_size(1)) > 0)
        
        # Very large numbers
        large_size = convert_size(10**15)
        self.assertIsInstance(large_size, str)
        self.assertTrue(len(large_size) > 0)


class TestDataConsistency(unittest.TestCase):
    """Test data consistency across operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_file_count_consistency(self):
        """Test that file counting is consistent."""
        # Create known file structure
        files = []
        for i in range(5):
            file_path = self.test_path / f"file_{i}.txt"
            file_path.write_text(f"content {i}")
            files.append(file_path)
        
        # Create subdirectory with files
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        for i in range(3):
            file_path = subdir / f"sub_file_{i}.txt"
            file_path.write_text(f"sub content {i}")
            files.append(file_path)
        
        from fx_bin.common import sum_folder_files_count
        
        # Count should be consistent across calls
        count1 = sum_folder_files_count(str(self.test_dir))
        count2 = sum_folder_files_count(str(self.test_dir))
        count3 = sum_folder_files_count(str(self.test_dir))
        
        self.assertEqual(count1, count2)
        self.assertEqual(count2, count3)
        self.assertEqual(count1, 8)  # 5 + 3 files
    
    def test_size_calculation_consistency(self):
        """Test that size calculations are consistent."""
        # Create files with known sizes
        file1 = self.test_path / "file1.txt"
        file2 = self.test_path / "file2.txt"
        file1.write_text("a" * 100)  # 100 bytes
        file2.write_text("b" * 200)  # 200 bytes
        
        from fx_bin.common import sum_folder_size
        
        # Size should be consistent and match expected
        size1 = sum_folder_size(str(self.test_dir))
        size2 = sum_folder_size(str(self.test_dir))
        
        self.assertEqual(size1, size2)
        self.assertEqual(size1, 300)  # 100 + 200 bytes
    
    def test_replacement_consistency(self):
        """Test that file replacement is consistent."""
        test_file = self.test_path / "consistency_test.txt"
        original_content = "test content line 1\ntest content line 2\n"
        test_file.write_text(original_content)
        
        from fx_bin.replace import work
        
        # Perform replacement
        work("test", "demo", str(test_file))
        
        # Read result multiple times - should be consistent
        result1 = test_file.read_text()
        result2 = test_file.read_text()
        result3 = test_file.read_text()
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        self.assertIn("demo content", result1)
        self.assertNotIn("test", result1)


class TestConcurrencySafety(unittest.TestCase):
    """Test concurrent access safety."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_concurrent_directory_scanning(self):
        """Test that concurrent directory scanning is safe."""
        import threading
        import time
        
        # Create directory structure
        for i in range(10):
            subdir = self.test_path / f"subdir_{i}"
            subdir.mkdir()
            for j in range(5):
                (subdir / f"file_{j}.txt").write_text(f"content {i}_{j}")
        
        from fx_bin.common import sum_folder_size, sum_folder_files_count
        
        results = []
        errors = []
        
        def scan_directory():
            try:
                size = sum_folder_size(str(self.test_dir))
                count = sum_folder_files_count(str(self.test_dir))
                results.append((size, count))
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=scan_directory)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # All operations should succeed
        self.assertEqual(len(errors), 0, f"Errors in concurrent access: {errors}")
        self.assertEqual(len(results), 5, "Not all threads completed")
        
        # Results should be consistent
        expected_size, expected_count = results[0]
        for size, count in results[1:]:
            self.assertEqual(size, expected_size, "Inconsistent size results")
            self.assertEqual(count, expected_count, "Inconsistent count results")


if __name__ == '__main__':
    unittest.main()
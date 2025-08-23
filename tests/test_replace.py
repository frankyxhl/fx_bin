"""Tests for fx_replace module."""
import os
import tempfile
import unittest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

# Silence loguru during tests
from loguru import logger
logger.remove()

from fx_bin.replace import work, main


class TestReplaceWork(unittest.TestCase):
    """Test the work function for text replacement."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test.txt"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_replace_single_occurrence(self):
        """Test replacing a single occurrence."""
        self.test_file.write_text("Hello World")
        
        work("World", "Python", str(self.test_file))
        
        content = self.test_file.read_text()
        self.assertEqual(content, "Hello Python")
    
    def test_replace_multiple_occurrences(self):
        """Test replacing multiple occurrences."""
        self.test_file.write_text("test test test")
        
        work("test", "demo", str(self.test_file))
        
        content = self.test_file.read_text()
        self.assertEqual(content, "demo demo demo")
    
    def test_replace_no_match(self):
        """Test when search text is not found."""
        original = "Hello World"
        self.test_file.write_text(original)
        
        work("Python", "Java", str(self.test_file))
        
        content = self.test_file.read_text()
        self.assertEqual(content, original)
    
    def test_replace_multiline(self):
        """Test replacing in multiline text."""
        self.test_file.write_text("line1\nline2\nline3")
        
        work("line2", "modified", str(self.test_file))
        
        content = self.test_file.read_text()
        self.assertEqual(content, "line1\nmodified\nline3")
    
    def test_replace_special_characters(self):
        """Test replacing special characters."""
        self.test_file.write_text("foo.bar.baz")
        
        work(".", "_", str(self.test_file))
        
        content = self.test_file.read_text()
        self.assertEqual(content, "foo_bar_baz")
    
    def test_replace_empty_file(self):
        """Test replacing in an empty file."""
        self.test_file.write_text("")
        
        work("test", "demo", str(self.test_file))
        
        content = self.test_file.read_text()
        self.assertEqual(content, "")


class TestReplaceMain(unittest.TestCase):
    """Test the main CLI function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_main_single_file(self):
        """Test replacing in a single file via CLI."""
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Hello World")
        
        result = self.runner.invoke(main, ["World", "Python", str(test_file)])
        
        self.assertEqual(result.exit_code, 0)
        content = test_file.read_text()
        self.assertEqual(content, "Hello Python")
    
    def test_main_multiple_files(self):
        """Test replacing in multiple files."""
        file1 = Path(self.test_dir) / "file1.txt"
        file2 = Path(self.test_dir) / "file2.txt"
        file1.write_text("test content")
        file2.write_text("test data")
        
        result = self.runner.invoke(main, ["test", "demo", str(file1), str(file2)])
        
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(file1.read_text(), "demo content")
        self.assertEqual(file2.read_text(), "demo data")
    
    def test_main_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        nonexistent = Path(self.test_dir) / "nonexistent.txt"
        
        result = self.runner.invoke(main, ["search", "replace", str(nonexistent)])
        
        # Should return error code
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("does not exist", result.output)
    
    def test_main_no_files(self):
        """Test when no files are provided."""
        result = self.runner.invoke(main, ["search", "replace"])
        
        # Should handle gracefully (no files to process)
        self.assertEqual(result.exit_code, 0)
    
    def test_main_mixed_files(self):
        """Test with mix of existing and non-existing files."""
        existing = Path(self.test_dir) / "existing.txt"
        existing.write_text("test content")
        nonexistent = Path(self.test_dir) / "nonexistent.txt"
        
        result = self.runner.invoke(main, ["test", "demo", str(existing), str(nonexistent)])
        
        # Should fail due to nonexistent file
        self.assertNotEqual(result.exit_code, 0)
        # Existing file should not be modified due to early exit
        self.assertEqual(existing.read_text(), "test content")


class TestReplaceErrorHandling(unittest.TestCase):
    """Test error handling paths in replace functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test.txt"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('os.name', 'nt')
    def test_windows_file_removal_path(self):
        """Test Windows-specific file removal path (line 51)."""
        self.test_file.write_text("Hello World")
        
        with patch('os.remove') as mock_remove, \
             patch('os.rename') as mock_rename:
            # Make rename succeed after remove
            mock_rename.return_value = None
            mock_remove.return_value = None
            
            work("World", "Python", str(self.test_file))
            
            # Verify Windows path was taken (remove is called twice: once for file, once for backup)
            self.assertEqual(mock_remove.call_count, 2)
            # First call should be the target file
            mock_remove.assert_any_call(str(self.test_file))
            mock_rename.assert_called_once()
    
    def test_atomic_replacement_general_exception(self):
        """Test general exception handling during atomic replacement (lines 66-70)."""
        self.test_file.write_text("Hello World")
        
        # Mock os.rename to raise a non-OSError exception
        with patch('os.rename', side_effect=RuntimeError("Unexpected error")), \
             patch('shutil.move') as mock_move, \
             patch('os.path.exists', return_value=True):
            
            with self.assertRaises(RuntimeError):
                work("World", "Python", str(self.test_file))
            
            # Verify backup restoration was attempted
            mock_move.assert_called()
    
    def test_temp_file_cleanup_oserror(self):
        """Test OSError during temp file cleanup (lines 77-78)."""
        self.test_file.write_text("Hello World")
        
        # Mock tempfile creation to raise an exception, then mock cleanup to fail
        with patch('tempfile.mkstemp', side_effect=Exception("Temp creation failed")), \
             patch('os.path.exists', return_value=True), \
             patch('os.unlink', side_effect=OSError("Cleanup failed")):
            
            # Should not re-raise the cleanup error
            with self.assertRaises(Exception) as cm:
                work("World", "Python", str(self.test_file))
            
            # Original exception should be preserved
            self.assertIn("Temp creation failed", str(cm.exception))
    
    def test_backup_restore_oserror(self):
        """Test OSError during backup restore (lines 82-85)."""
        self.test_file.write_text("Hello World")
        
        # Mock file operations to trigger backup restore with OSError
        with patch('tempfile.mkstemp', side_effect=Exception("Processing failed")), \
             patch('os.path.exists', return_value=True), \
             patch('shutil.move', side_effect=OSError("Restore failed")):
            
            # Should not re-raise the restore error
            with self.assertRaises(Exception) as cm:
                work("World", "Python", str(self.test_file))
            
            # Original exception should be preserved
            self.assertIn("Processing failed", str(cm.exception))
    
    def test_transaction_rollback_oserror(self):
        """Test OSError during transaction rollback (lines 136-137)."""
        test_file1 = Path(self.test_dir) / "file1.txt"
        test_file2 = Path(self.test_dir) / "file2.txt"
        test_file1.write_text("content1")
        test_file2.write_text("content2")
        
        runner = CliRunner()
        
        # Mock work function to fail after creating backups
        with patch('fx_bin.replace.work', side_effect=Exception("Work failed")), \
             patch('os.path.exists', return_value=True), \
             patch('shutil.move', side_effect=OSError("Rollback failed")):
            
            # Should not re-raise rollback error
            result = runner.invoke(main, ["search", "replace", str(test_file1), str(test_file2)])
            
            # Should exit with error due to original exception
            self.assertNotEqual(result.exit_code, 0)
    
    def test_final_oserror_cleanup_paths(self):
        """Test remaining OSError paths in cleanup (lines 77-78, 84-85)."""
        self.test_file.write_text("Hello World")
        
        # Create a scenario that will fail and trigger the cleanup paths
        with patch('tempfile.mkstemp') as mock_mkstemp, \
             patch('os.path.exists', return_value=True), \
             patch('os.unlink', side_effect=OSError("Cleanup unlink failed")) as mock_unlink, \
             patch('shutil.move', side_effect=OSError("Backup move failed")) as mock_move:
            
            # Make mkstemp return a fake fd and path, then fail during processing
            mock_mkstemp.return_value = (999, '/fake/temp/path')
            
            # Mock os.fdopen to fail, triggering the exception cleanup
            with patch('os.fdopen', side_effect=Exception("fdopen failed")):
                
                with self.assertRaises(Exception) as cm:
                    work("World", "Python", str(self.test_file))
                
                # Both cleanup paths should have been attempted despite errors
                mock_unlink.assert_called()  # Line 77-78: temp file cleanup OSError
                mock_move.assert_called()    # Line 84-85: backup restore OSError
                
                # Original exception should be preserved
                self.assertIn("fdopen failed", str(cm.exception))


if __name__ == '__main__':
    unittest.main()
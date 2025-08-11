"""Tests for fx_replace module."""
import os
import tempfile
import unittest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

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


if __name__ == '__main__':
    unittest.main()
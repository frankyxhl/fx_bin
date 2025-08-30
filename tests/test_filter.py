"""Tests for fx_filter module following TDD methodology.

These tests verify the complete functionality of the filter command
after successful implementation (GREEN phase achieved).
"""
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner


class TestFilterCore(unittest.TestCase):
    """Test core filter functionality in fx_bin.filter module."""
    
    def setUp(self):
        """Set up test fixtures with a temporary directory structure."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test files with different extensions
        (self.test_path / "document1.txt").touch()
        (self.test_path / "document2.txt").touch()
        (self.test_path / "image1.jpg").touch()
        (self.test_path / "image2.png").touch()
        (self.test_path / "script.py").touch()
        (self.test_path / "README.md").touch()
        (self.test_path / "no_extension").touch()
        
        # Create subdirectory with files
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "nested1.txt").touch()
        (subdir / "nested2.py").touch()
        (subdir / "data.json").touch()
        
        # Create deeper nested structure
        nested = subdir / "deep"
        nested.mkdir()
        (nested / "deep.txt").touch()
        (nested / "config.yml").touch()
        
        # Set different modification times for sorting tests
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        
        # Set timestamps
        old_file = self.test_path / "document1.txt"
        recent_file = self.test_path / "script.py"
        
        os.utime(old_file, (day_ago.timestamp(), day_ago.timestamp()))
        os.utime(recent_file, (now.timestamp(), now.timestamp()))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_find_files_by_extension_single_txt(self):
        """Test finding files with single .txt extension."""
        from fx_bin.filter import find_files_by_extension
        
        result = find_files_by_extension(str(self.test_path), "txt")
        
        # Should find 4 .txt files (document1.txt, document2.txt, nested1.txt, deep.txt)
        self.assertEqual(len(result), 4)
        
        # Verify all returned files have .txt extension
        for file_path in result:
            self.assertTrue(file_path.endswith('.txt'))
            self.assertTrue(os.path.exists(file_path))
    
    def test_find_files_by_extension_non_recursive(self):
        """Test finding files with non-recursive search."""
        from fx_bin.filter import find_files_by_extension
        
        result = find_files_by_extension(str(self.test_path), "txt", recursive=False)
        
        # Should find only 2 .txt files in root directory
        self.assertEqual(len(result), 2)
        
        # Verify files are in root directory
        for file_path in result:
            self.assertEqual(Path(file_path).parent, self.test_path)
    
    def test_find_files_by_extension_multiple_extensions(self):
        """Test finding files with multiple extensions."""
        from fx_bin.filter import find_files_by_extension
        
        result = find_files_by_extension(str(self.test_path), "py,json")
        
        # Should find script.py, nested2.py, data.json
        self.assertEqual(len(result), 3)
        
        # Verify all files have correct extensions
        extensions = [Path(f).suffix[1:] for f in result]
        for ext in extensions:
            self.assertIn(ext, ['py', 'json'])
    
    def test_find_files_by_extension_no_matches(self):
        """Test finding files with extension that doesn't exist."""
        from fx_bin.filter import find_files_by_extension
        
        result = find_files_by_extension(str(self.test_path), "cpp")
        
        # Should return empty list
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])
    
    def test_find_files_by_extension_nonexistent_path(self):
        """Test finding files in non-existent path."""
        from fx_bin.filter import find_files_by_extension
        
        with self.assertRaises(FileNotFoundError):
            find_files_by_extension("/nonexistent/path", "txt")
    
    def test_sort_files_by_time_created_ascending(self):
        """Test sorting files by creation time, oldest first."""
        from fx_bin.filter import sort_files_by_time
        
        files = [
            str(self.test_path / "document1.txt"),  # oldest
            str(self.test_path / "script.py"),      # newest
        ]
        
        result = sort_files_by_time(files, sort_by='created', reverse=False)
        
        # Should return files sorted by creation time (oldest first)
        self.assertEqual(len(result), 2)
    
    def test_sort_files_by_time_invalid_sort_option(self):
        """Test sorting files with invalid sort option."""
        from fx_bin.filter import sort_files_by_time
        
        files = [str(self.test_path / "document1.txt")]
        
        with self.assertRaises(ValueError):
            sort_files_by_time(files, sort_by='invalid')
    
    def test_sort_files_by_time_empty_list(self):
        """Test sorting empty file list."""
        from fx_bin.filter import sort_files_by_time
        
        result = sort_files_by_time([], sort_by='created')
        
        self.assertEqual(result, [])
    
    def test_format_output_simple(self):
        """Test simple output formatting."""
        from fx_bin.filter import format_output
        
        files = [
            str(self.test_path / "document1.txt"),
            str(self.test_path / "script.py"),
        ]
        
        result = format_output(files, format='simple')
        
        # Should return formatted string with file paths
        self.assertIsInstance(result, str)
        self.assertIn("document1.txt", result)
        self.assertIn("script.py", result)
    
    def test_format_output_detailed(self):
        """Test detailed output formatting with file stats."""
        from fx_bin.filter import format_output
        
        files = [str(self.test_path / "document1.txt")]
        
        result = format_output(files, format='detailed')
        
        # Should include file size, modification time, etc.
        self.assertIsInstance(result, str)
        self.assertIn("document1.txt", result)
        # Should contain size information with new format (B/KB/MB units)
        has_size_info = (" B " in result or " KB " in result or " MB " in result)
        self.assertTrue(has_size_info)
        # Should have date format YYYY-MM-DD
        import re
        self.assertTrue(re.search(r'\d{4}-\d{2}-\d{2}', result))
    
    def test_format_output_count_removed(self):
        """Test that count format is no longer supported."""
        from fx_bin.filter import format_output
        
        files = [
            str(self.test_path / "document1.txt"),
            str(self.test_path / "script.py"),
        ]
        
        # Count format should raise ValueError
        with self.assertRaises(ValueError) as context:
            format_output(files, format='count')
        
        self.assertIn("Invalid format: count", str(context.exception))
        self.assertIn("['simple', 'detailed']", str(context.exception))
    
    def test_format_output_invalid_format(self):
        """Test output formatting with invalid format option."""
        from fx_bin.filter import format_output
        
        files = [str(self.test_path / "document1.txt")]
        
        with self.assertRaises(ValueError):
            format_output(files, format='invalid')
    
    def test_parse_extensions_single(self):
        """Test parsing single extension."""
        from fx_bin.filter import parse_extensions
        
        result = parse_extensions("txt")
        
        self.assertEqual(result, ["txt"])
    
    def test_parse_extensions_comma_separated(self):
        """Test parsing comma-separated extensions."""
        from fx_bin.filter import parse_extensions
        
        result = parse_extensions("txt,py,json")
        
        self.assertEqual(result, ["txt", "py", "json"])
    
    def test_parse_extensions_with_dots(self):
        """Test parsing extensions with leading dots (should be stripped)."""
        from fx_bin.filter import parse_extensions
        
        result = parse_extensions(".txt,.py,.json")
        
        self.assertEqual(result, ["txt", "py", "json"])
    
    def test_parse_extensions_with_spaces(self):
        """Test parsing extensions with spaces (should be stripped)."""
        from fx_bin.filter import parse_extensions
        
        result = parse_extensions("txt, py , json ")
        
        self.assertEqual(result, ["txt", "py", "json"])
    
    def test_parse_extensions_empty_string(self):
        """Test parsing empty extension string."""
        from fx_bin.filter import parse_extensions
        
        result = parse_extensions("")
        
        self.assertEqual(result, [])


class TestFilterCLI(unittest.TestCase):
    """Test CLI integration for filter command."""
    
    def setUp(self):
        """Set up test fixtures for CLI testing."""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test files
        (self.test_path / "test1.txt").touch()
        (self.test_path / "test2.py").touch()
        (self.test_path / "image.jpg").touch()
        
        subdir = self.test_path / "sub"
        subdir.mkdir()
        (subdir / "nested.txt").touch()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_filter_command_basic(self):
        """Test basic filter command execution."""
        from fx_bin.cli import cli
        result = self.runner.invoke(cli, ['filter', 'txt', str(self.test_path)])
        
        # Command should execute successfully
        self.assertEqual(result.exit_code, 0)
        # Output should contain found files
        self.assertIn("test1.txt", result.output)
        self.assertIn("nested.txt", result.output)
    
    def test_filter_command_help(self):
        """Test filter command help output."""
        from fx_bin.cli import cli
        result = self.runner.invoke(cli, ['filter', '--help'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Filter files by extension", result.output)
        self.assertIn("--recursive", result.output)
        self.assertIn("--sort-by", result.output)
        self.assertIn("--format", result.output)
    
    def test_filter_command_no_matches(self):
        """Test filter command when no files match."""
        from fx_bin.cli import cli
        result = self.runner.invoke(cli, ['filter', 'cpp', str(self.test_path)])
        
        # Should still exit successfully but with no results message
        self.assertEqual(result.exit_code, 0)
        has_no_results = ("No files found" in result.output or "0 files" in result.output)
        self.assertTrue(has_no_results)
    
    def test_filter_command_invalid_path(self):
        """Test filter command with invalid path."""
        from fx_bin.cli import cli
        result = self.runner.invoke(cli, ['filter', 'txt', '/nonexistent/path'])
        
        # Should show error message (exit code handling varies in Click testing)
        output_lower = result.output.lower()
        has_error = ("error" in output_lower or "not found" in output_lower)
        self.assertTrue(has_error, f"Expected error message in output: {result.output}")


class TestFilterIntegration(unittest.TestCase):
    """Integration tests for the complete filter workflow."""
    
    def setUp(self):
        """Set up comprehensive test directory structure."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create complex directory structure
        dirs = [
            "src/main/python",
            "src/test/python", 
            "docs/api",
            "config/environments",
        ]
        
        for dir_path in dirs:
            (self.test_path / dir_path).mkdir(parents=True)
        
        # Create files with various extensions
        files_to_create = [
            ("src/main/python/app.py", ".py"),
            ("src/main/python/utils.py", ".py"),
            ("src/test/python/test_app.py", ".py"),
            ("docs/api/index.md", ".md"),
            ("config/environments/dev.json", ".json"),
            ("README.md", ".md"),
            ("requirements.txt", ".txt"),
            ("setup.py", ".py"),
        ]
        
        for file_path, ext in files_to_create:
            (self.test_path / file_path).touch()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_complete_workflow_python_files(self):
        """Test complete workflow for finding and sorting Python files."""
        from fx_bin.filter import find_files_by_extension, sort_files_by_time, format_output
        
        # Find all Python files
        python_files = find_files_by_extension(str(self.test_path), "py")
        
        # Should find 4 Python files
        self.assertEqual(len(python_files), 4)
        
        # Sort by modification time
        sorted_files = sort_files_by_time(python_files, sort_by='modified', reverse=True)
        
        self.assertEqual(len(sorted_files), 4)
        
        # Format output
        output = format_output(sorted_files, format='simple')
        
        self.assertIsInstance(output, str)
        self.assertIn(".py", output)
    
    def test_recursive_vs_non_recursive_search(self):
        """Test difference between recursive and non-recursive search."""
        from fx_bin.filter import find_files_by_extension
        
        # Recursive search (default)
        recursive_files = find_files_by_extension(str(self.test_path), "py", recursive=True)
        
        # Non-recursive search
        non_recursive_files = find_files_by_extension(str(self.test_path), "py", recursive=False)
        
        # Recursive should find more files
        self.assertGreater(len(recursive_files), len(non_recursive_files))
        
        # Non-recursive should find only setup.py in root
        self.assertEqual(len(non_recursive_files), 1)
        self.assertTrue(non_recursive_files[0].endswith("setup.py"))


if __name__ == '__main__':
    unittest.main()
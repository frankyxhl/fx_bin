"""TDD tests for fx filter improvements in v1.3.1.

These tests are written FIRST following TDD methodology (RED phase).
They define the expected behavior for:
1. Removing 'count' format option
2. New detailed format with aligned columns
3. --show-path parameter for path display control
4. Default format changed to 'detailed'
"""
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from fx_bin import filter as filter_module
from fx_bin.cli import cli


class TestFormatOptionRemoval(unittest.TestCase):
    """Test removal of 'count' format option."""
    
    def test_count_format_no_longer_supported(self):
        """FAIL: Count format should raise ValueError."""
        files = ["test1.txt", "test2.txt"]
        
        with self.assertRaises(ValueError) as context:
            filter_module.format_output(files, 'count')
        
        self.assertIn("Invalid format: count", str(context.exception))
        self.assertIn("Must be one of ['simple', 'detailed']", str(context.exception))
    
    def test_valid_formats_only_simple_and_detailed(self):
        """PASS: Only 'simple' and 'detailed' formats are valid."""
        files = ["test.txt"]
        
        # These should work
        simple_output = filter_module.format_output(files, 'simple')
        detailed_output = filter_module.format_output(files, 'detailed')
        
        self.assertIsInstance(simple_output, str)
        self.assertIsInstance(detailed_output, str)
        
        # Invalid format should fail
        with self.assertRaises(ValueError):
            filter_module.format_output(files, 'invalid')


class TestNewDetailedFormat(unittest.TestCase):
    """Test the new detailed format with aligned columns."""
    
    def setUp(self):
        """Set up test files with known properties."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test files with specific sizes
        (self.test_path / "small.txt").write_text("x" * 100)  # 100 bytes
        (self.test_path / "medium.py").write_text("x" * 1536)  # 1.5 KB
        (self.test_path / "large.json").write_text("x" * 2097152)  # 2.0 MB
        
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_new_detailed_format_alignment(self):
        """FAIL: New detailed format should have aligned columns."""
        files = [
            str(self.test_path / "small.txt"),
            str(self.test_path / "medium.py"), 
            str(self.test_path / "large.json")
        ]
        
        output = filter_module.format_output(files, 'detailed')
        lines = output.split('\n')
        
        # Check that we have expected number of lines
        self.assertEqual(len(lines), 3)
        
        # Check format: YYYY-MM-DD HH:MM:SS    SIZE UNIT    FILENAME
        for line in lines:
            parts = line.split()
            self.assertGreaterEqual(len(parts), 4)
            
            # Date should be YYYY-MM-DD format
            date_part = parts[0]
            self.assertRegex(date_part, r'\d{4}-\d{2}-\d{2}')
            
            # Time should be HH:MM:SS format  
            time_part = parts[1]
            self.assertRegex(time_part, r'\d{2}:\d{2}:\d{2}')
            
            # Size and unit should be present
            size_part = parts[2]
            unit_part = parts[3]
            self.assertRegex(size_part, r'\d+(\.\d+)?')
            self.assertIn(unit_part, ['B', 'KB', 'MB', 'GB'])
    
    def test_format_file_size_alignment_helper(self):
        """FAIL: New helper function for aligned size formatting."""
        # This function should exist and format sizes with alignment
        result_100b = filter_module._format_file_size_aligned(100)
        result_1536b = filter_module._format_file_size_aligned(1536) 
        result_2mb = filter_module._format_file_size_aligned(2097152)
        
        # Check format: numbers right-aligned, units left-aligned
        self.assertRegex(result_100b, r'\s*100 B')
        self.assertRegex(result_1536b, r'\s*1\.5 KB')
        self.assertRegex(result_2mb, r'\s*2\.0 MB')
    
    def test_no_redundant_words_in_output(self):
        """FAIL: Output should not contain 'modified:', 'size:', etc."""
        files = [str(self.test_path / "small.txt")]
        output = filter_module.format_output(files, 'detailed')
        
        # Should not contain redundant words
        self.assertNotIn("modified:", output.lower())
        self.assertNotIn("size:", output.lower())
        self.assertNotIn("bytes", output.lower())


class TestShowPathParameter(unittest.TestCase):
    """Test --show-path parameter functionality."""
    
    def setUp(self):
        """Set up nested directory structure."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create nested structure
        (self.test_path / "root.txt").touch()
        docs_dir = self.test_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "guide.txt").touch()
        utils_dir = self.test_path / "src" / "utils"
        utils_dir.mkdir(parents=True)
        (utils_dir / "helper.txt").touch()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_format_output_with_show_path_false(self):
        """FAIL: Should show only filenames by default."""
        files = [
            str(self.test_path / "root.txt"),
            str(self.test_path / "docs" / "guide.txt"),
            str(self.test_path / "src" / "utils" / "helper.txt")
        ]
        
        # New signature: format_output(files, format, show_path=False)
        output = filter_module.format_output(files, 'detailed', show_path=False)
        lines = output.split('\n')
        
        # Should only show filenames
        self.assertIn("root.txt", lines[0])
        self.assertIn("guide.txt", lines[1]) 
        self.assertIn("helper.txt", lines[2])
        
        # Should not show paths
        self.assertNotIn("docs/", output)
        self.assertNotIn("src/utils/", output)
    
    def test_format_output_with_show_path_true(self):
        """FAIL: Should show relative paths when show_path=True."""
        files = [
            str(self.test_path / "root.txt"),
            str(self.test_path / "docs" / "guide.txt"),
            str(self.test_path / "src" / "utils" / "helper.txt")
        ]
        
        # Should show relative paths
        output = filter_module.format_output(files, 'detailed', show_path=True)
        
        self.assertIn("docs/guide.txt", output)
        self.assertIn("src/utils/helper.txt", output)


class TestDefaultFormatChange(unittest.TestCase):
    """Test that default format is now 'detailed'."""
    
    def test_cli_default_format_is_detailed(self):
        """FAIL: CLI should use detailed format by default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            
            runner = CliRunner()
            result = runner.invoke(cli, ['filter', 'txt', temp_dir])
            
            # Should succeed and use detailed format by default
            self.assertEqual(result.exit_code, 0)
            
            # Output should contain date/time and size (detailed format)
            self.assertRegex(result.output, r'\d{4}-\d{2}-\d{2}')
            self.assertRegex(result.output, r'\d{2}:\d{2}:\d{2}')
            self.assertRegex(result.output, r'\d+\s+(B|KB|MB|GB)')


class TestCLIParameterIntegration(unittest.TestCase):
    """Test CLI integration with new --show-path parameter."""
    
    def test_cli_show_path_parameter_exists(self):
        """FAIL: CLI should accept --show-path parameter."""
        runner = CliRunner()
        result = runner.invoke(cli, ['filter', '--help'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--show-path", result.output)
    
    def test_cli_count_format_removed(self):
        """FAIL: CLI should reject count format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.touch()
            
            runner = CliRunner()
            result = runner.invoke(cli, ['filter', 'txt', temp_dir, '--format', 'count'])
            
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid", result.output)


class TestBackwardsCompatibility(unittest.TestCase):
    """Test that existing functionality still works."""
    
    def test_simple_format_still_works(self):
        """PASS: Simple format should still work for backwards compatibility."""
        files = ["test1.txt", "test2.txt"]
        output = filter_module.format_output(files, 'simple')
        
        expected = "test1.txt\ntest2.txt"
        self.assertEqual(output, expected)
    
    def test_sorting_still_works(self):
        """PASS: Sorting functionality should be unchanged."""
        # This should pass as existing functionality
        with tempfile.TemporaryDirectory() as temp_dir:
            files = []
            for i in range(3):
                file_path = Path(temp_dir) / f"test{i}.txt"
                file_path.touch()
                files.append(str(file_path))
            
            sorted_files = filter_module.sort_files_by_time(files, 'created', False)
            self.assertEqual(len(sorted_files), 3)
            self.assertIsInstance(sorted_files, list)


class TestErrorHandling(unittest.TestCase):
    """Test error handling for invalid parameters."""
    
    def test_invalid_format_error_message_updated(self):
        """FAIL: Error message should reflect only 'simple' and 'detailed'."""
        with self.assertRaises(ValueError) as context:
            filter_module.format_output([], 'invalid')
        
        error_message = str(context.exception)
        self.assertIn("['simple', 'detailed']", error_message)
        self.assertNotIn("count", error_message)


if __name__ == '__main__':
    unittest.main()
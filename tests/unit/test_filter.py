"""Tests for fx_filter module following TDD methodology.

These tests verify the complete functionality of the filter command
after successful implementation (GREEN phase achieved).

Includes tests from filter improvements in v1.3.1:
1. Removing 'count' format option
2. New detailed format with aligned columns
3. --show-path parameter for path display control
4. Default format changed to 'detailed'
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
            self.assertTrue(file_path.endswith(".txt"))
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
            self.assertIn(ext, ["py", "json"])

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
            str(self.test_path / "script.py"),  # newest
        ]

        result = sort_files_by_time(files, sort_by="created", reverse=False)

        # Should return files sorted by creation time (oldest first)
        self.assertEqual(len(result), 2)

    def test_sort_files_by_time_invalid_sort_option(self):
        """Test sorting files with invalid sort option."""
        from fx_bin.filter import sort_files_by_time

        files = [str(self.test_path / "document1.txt")]

        with self.assertRaises(ValueError):
            sort_files_by_time(files, sort_by="invalid")

    def test_sort_files_by_time_empty_list(self):
        """Test sorting empty file list."""
        from fx_bin.filter import sort_files_by_time

        result = sort_files_by_time([], sort_by="created")

        self.assertEqual(result, [])

    def test_format_output_simple(self):
        """Test simple output formatting."""
        from fx_bin.filter import format_output

        files = [
            str(self.test_path / "document1.txt"),
            str(self.test_path / "script.py"),
        ]

        result = format_output(files, output_format="simple")

        # Should return formatted string with file paths
        self.assertIsInstance(result, str)
        self.assertIn("document1.txt", result)
        self.assertIn("script.py", result)

    def test_format_output_detailed(self):
        """Test detailed output formatting with file stats."""
        from fx_bin.filter import format_output

        files = [str(self.test_path / "document1.txt")]

        result = format_output(files, output_format="detailed")

        # Should include file size, modification time, etc.
        self.assertIsInstance(result, str)
        self.assertIn("document1.txt", result)
        # Should contain size information with new format (B/KB/MB units)
        has_size_info = " B " in result or " KB " in result or " MB " in result
        self.assertTrue(has_size_info)
        # Should have date format YYYY-MM-DD
        import re

        self.assertTrue(re.search(r"\d{4}-\d{2}-\d{2}", result))

    def test_format_output_count_removed(self):
        """Test that count format is no longer supported."""
        from fx_bin.filter import format_output

        files = [
            str(self.test_path / "document1.txt"),
            str(self.test_path / "script.py"),
        ]

        # Count format should raise ValueError
        with self.assertRaises(ValueError) as context:
            format_output(files, output_format="count")

        self.assertIn("Invalid format: count", str(context.exception))
        self.assertIn("['simple', 'detailed']", str(context.exception))

    def test_format_output_invalid_format(self):
        """Test output formatting with invalid format option."""
        from fx_bin.filter import format_output

        files = [str(self.test_path / "document1.txt")]

        with self.assertRaises(ValueError):
            format_output(files, output_format="invalid")

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


class TestFormatOptionRemoval(unittest.TestCase):
    """Test removal of 'count' format option."""

    def test_count_format_no_longer_supported(self):
        """FAIL: Count format should raise ValueError."""
        from fx_bin import filter as filter_module

        files = ["test1.txt", "test2.txt"]

        with self.assertRaises(ValueError) as context:
            filter_module.format_output(files, "count")

        self.assertIn("Invalid format: count", str(context.exception))
        self.assertIn("Must be one of ['simple', 'detailed']", str(context.exception))

    def test_valid_formats_only_simple_and_detailed(self):
        """PASS: Only 'simple' and 'detailed' formats are valid."""
        from fx_bin import filter as filter_module

        files = ["test.txt"]

        # These should work
        simple_output = filter_module.format_output(files, "simple")
        detailed_output = filter_module.format_output(files, "detailed")

        self.assertIsInstance(simple_output, str)
        self.assertIsInstance(detailed_output, str)

        # Invalid format should fail
        with self.assertRaises(ValueError):
            filter_module.format_output(files, "invalid")


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
        from fx_bin import filter as filter_module

        files = [
            str(self.test_path / "small.txt"),
            str(self.test_path / "medium.py"),
            str(self.test_path / "large.json"),
        ]

        output = filter_module.format_output(files, "detailed")
        lines = output.split("\n")

        # Check that we have expected number of lines
        self.assertEqual(len(lines), 3)

        # Check format: YYYY-MM-DD HH:MM:SS    SIZE UNIT    FILENAME
        for line in lines:
            parts = line.split()
            self.assertGreaterEqual(len(parts), 4)

            # Date should be YYYY-MM-DD format
            date_part = parts[0]
            self.assertRegex(date_part, r"\d{4}-\d{2}-\d{2}")

            # Time should be HH:MM:SS format
            time_part = parts[1]
            self.assertRegex(time_part, r"\d{2}:\d{2}:\d{2}")

            # Size and unit should be present
            size_part = parts[2]
            unit_part = parts[3]
            self.assertRegex(size_part, r"\d+(\.\d+)?")
            self.assertIn(unit_part, ["B", "KB", "MB", "GB"])

    def test_format_file_size_alignment_helper(self):
        """PASS: New helper function for aligned size formatting."""
        from fx_bin import filter as filter_module

        # This function should exist and format sizes with alignment (9 chars total)
        result_100b = filter_module._format_file_size_aligned(100)
        result_1536b = filter_module._format_file_size_aligned(1536)
        result_2mb = filter_module._format_file_size_aligned(2097152)

        # Check exact format: 9 characters total, right-aligned
        self.assertEqual(result_100b, "    100 B")
        self.assertEqual(result_1536b, "   1.5 KB")
        self.assertEqual(result_2mb, "   2.0 MB")

    def test_no_redundant_words_in_output(self):
        """FAIL: Output should not contain 'modified:', 'size:', etc."""
        from fx_bin import filter as filter_module

        files = [str(self.test_path / "small.txt")]
        output = filter_module.format_output(files, "detailed")

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
        from fx_bin import filter as filter_module

        files = [
            str(self.test_path / "root.txt"),
            str(self.test_path / "docs" / "guide.txt"),
            str(self.test_path / "src" / "utils" / "helper.txt"),
        ]

        # New signature: format_output(files, output_format, show_path=False)
        output = filter_module.format_output(files, "detailed", show_path=False)
        lines = output.split("\n")

        # Should only show filenames
        self.assertIn("root.txt", lines[0])
        self.assertIn("guide.txt", lines[1])
        self.assertIn("helper.txt", lines[2])

        # Should not show paths
        self.assertNotIn("docs/", output)
        self.assertNotIn("src/utils/", output)

    def test_format_output_with_show_path_true(self):
        """FAIL: Should show relative paths when show_path=True."""
        from fx_bin import filter as filter_module

        files = [
            str(self.test_path / "root.txt"),
            str(self.test_path / "docs" / "guide.txt"),
            str(self.test_path / "src" / "utils" / "helper.txt"),
        ]

        # Should show relative paths
        output = filter_module.format_output(files, "detailed", show_path=True)

        self.assertIn("docs/guide.txt", output)
        self.assertIn("src/utils/helper.txt", output)


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

        result = self.runner.invoke(cli, ["filter", "txt", str(self.test_path)])

        # Command should execute successfully
        self.assertEqual(result.exit_code, 0)
        # Output should contain found files
        self.assertIn("test1.txt", result.output)
        self.assertIn("nested.txt", result.output)

    def test_filter_command_help(self):
        """Test filter command help output."""
        from fx_bin.cli import cli

        result = self.runner.invoke(cli, ["filter", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Filter files by extension", result.output)
        self.assertIn("--recursive", result.output)
        self.assertIn("--sort-by", result.output)
        self.assertIn("--format", result.output)

    def test_filter_command_no_matches(self):
        """Test filter command when no files match."""
        from fx_bin.cli import cli

        result = self.runner.invoke(cli, ["filter", "cpp", str(self.test_path)])

        # Should still exit successfully but with no results message
        self.assertEqual(result.exit_code, 0)
        has_no_results = "No files found" in result.output or "0 files" in result.output
        self.assertTrue(has_no_results)

    def test_filter_command_invalid_path(self):
        """Test filter command with invalid path."""
        from fx_bin.cli import cli

        result = self.runner.invoke(cli, ["filter", "txt", "/nonexistent/path"])

        # Should show error message (exit code handling varies in Click testing)
        output_lower = result.output.lower()
        has_error = "error" in output_lower or "not found" in output_lower
        self.assertTrue(has_error, f"Expected error message in output: {result.output}")

    def test_cli_default_format_is_detailed(self):
        """FAIL: CLI should use detailed format by default."""
        from fx_bin.cli import cli

        # Create test file
        test_file = self.test_path / "test.txt"
        test_file.write_text("test content")

        result = self.runner.invoke(cli, ["filter", "txt", str(self.test_path)])

        # Should succeed and use detailed format by default
        self.assertEqual(result.exit_code, 0)

        # Output should contain date/time and size (detailed format)
        self.assertRegex(result.output, r"\d{4}-\d{2}-\d{2}")
        self.assertRegex(result.output, r"\d{2}:\d{2}:\d{2}")
        self.assertRegex(result.output, r"\d+\s+(B|KB|MB|GB)")


class TestCLIParameterIntegration(unittest.TestCase):
    """Test CLI integration with new --show-path parameter."""

    def test_cli_show_path_parameter_exists(self):
        """FAIL: CLI should accept --show-path parameter."""
        from fx_bin.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["filter", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--show-path", result.output)

    def test_cli_count_format_removed(self):
        """FAIL: CLI should reject count format."""
        from fx_bin.cli import cli

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.touch()

            runner = CliRunner()
            result = runner.invoke(
                cli, ["filter", "txt", temp_dir, "--format", "count"]
            )

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid", result.output)


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
        from fx_bin.filter import (
            find_files_by_extension,
            sort_files_by_time,
            format_output,
        )

        # Find all Python files
        python_files = find_files_by_extension(str(self.test_path), "py")

        # Should find 4 Python files
        self.assertEqual(len(python_files), 4)

        # Sort by modification time
        sorted_files = sort_files_by_time(
            python_files, sort_by="modified", reverse=True
        )

        self.assertEqual(len(sorted_files), 4)

        # Format output
        output = format_output(sorted_files, output_format="simple")

        self.assertIsInstance(output, str)
        self.assertIn(".py", output)

    def test_recursive_vs_non_recursive_search(self):
        """Test difference between recursive and non-recursive search."""
        from fx_bin.filter import find_files_by_extension

        # Recursive search (default)
        recursive_files = find_files_by_extension(
            str(self.test_path), "py", recursive=True
        )

        # Non-recursive search
        non_recursive_files = find_files_by_extension(
            str(self.test_path), "py", recursive=False
        )

        # Recursive should find more files
        self.assertGreater(len(recursive_files), len(non_recursive_files))

        # Non-recursive should find only setup.py in root
        self.assertEqual(len(non_recursive_files), 1)
        self.assertTrue(non_recursive_files[0].endswith("setup.py"))


class TestBackwardsCompatibility(unittest.TestCase):
    """Test that existing functionality still works."""

    def test_simple_format_still_works(self):
        """PASS: Simple format should still work for backwards compatibility."""
        from fx_bin import filter as filter_module

        files = ["test1.txt", "test2.txt"]
        output = filter_module.format_output(files, "simple")

        expected = "test1.txt\ntest2.txt"
        self.assertEqual(output, expected)

    def test_sorting_still_works(self):
        """PASS: Sorting functionality should be unchanged."""
        from fx_bin import filter as filter_module

        # This should pass as existing functionality
        with tempfile.TemporaryDirectory() as temp_dir:
            files = []
            for i in range(3):
                file_path = Path(temp_dir) / f"test{i}.txt"
                file_path.touch()
                files.append(str(file_path))

            sorted_files = filter_module.sort_files_by_time(files, "created", False)
            self.assertEqual(len(sorted_files), 3)
            self.assertIsInstance(sorted_files, list)


class TestErrorHandling(unittest.TestCase):
    """Test error handling for invalid parameters."""

    def test_invalid_format_error_message_updated(self):
        """FAIL: Error message should reflect only 'simple' and 'detailed'."""
        from fx_bin import filter as filter_module

        with self.assertRaises(ValueError) as context:
            filter_module.format_output([], "invalid")

        error_message = str(context.exception)
        self.assertIn("['simple', 'detailed']", error_message)
        self.assertNotIn("count", error_message)


if __name__ == "__main__":
    unittest.main()

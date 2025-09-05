"""Tests for fx_find_files module.

Includes tests for find_files functionality and exclusion patterns.
"""

import os
import sys
import tempfile
import unittest
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from fx_bin.find_files import find_files


def _run_ff(args, cwd: Path):
    """Run `fx ff ...` via Python module to avoid PATH dependency."""
    cmd = [sys.executable, "-m", "fx_bin.cli", "ff"] + list(args)
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=15)


class TestFindFiles(unittest.TestCase):
    """Test find_files function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.original_cwd = os.getcwd()

        # Create test structure
        (self.test_path / "test_file.txt").touch()
        (self.test_path / "another_test.py").touch()
        (self.test_path / "readme.md").touch()

        # Create subdirectory with files
        subdir = self.test_path / "test_dir"
        subdir.mkdir()
        (subdir / "test_nested.txt").touch()
        (subdir / "config.json").touch()

        # Create another subdirectory
        another_dir = self.test_path / "src"
        another_dir.mkdir()
        (another_dir / "main.py").touch()
        (another_dir / "test_main.py").touch()

        # Change to test directory
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.test_dir)

    @patch("sys.stdout", new_callable=StringIO)
    def test_find_files_keyword_in_filename(self, mock_stdout):
        """Test finding files with keyword in filename."""
        find_files("test")
        output = mock_stdout.getvalue()

        # Should find files and directories containing "test"
        self.assertIn("test_file.txt", output)
        self.assertIn("another_test.py", output)
        self.assertIn("test_dir", output)
        self.assertIn("test_nested.txt", output)
        self.assertIn("test_main.py", output)

        # Should not find files without "test"
        self.assertNotIn("readme.md", output)
        self.assertNotIn("config.json", output)
        # Note: main.py is not included, but test_main.py is

    @patch("sys.stdout", new_callable=StringIO)
    def test_find_files_keyword_in_dirname(self, mock_stdout):
        """Test finding directories with keyword."""
        find_files("dir")
        output = mock_stdout.getvalue()

        # Should find directory containing "dir"
        self.assertIn("test_dir", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_find_files_exact_match(self, mock_stdout):
        """Test finding files with exact match."""
        find_files("readme.md")
        output = mock_stdout.getvalue()

        # Should find exact match
        self.assertIn("readme.md", output)

        # Count occurrences (should be exactly 1)
        lines = output.strip().split("\n")
        self.assertEqual(len(lines), 1)

    @patch("sys.stdout", new_callable=StringIO)
    def test_find_files_extension(self, mock_stdout):
        """Test finding files by extension."""
        find_files(".py")
        output = mock_stdout.getvalue()

        # Should find all .py files
        self.assertIn("another_test.py", output)
        self.assertIn("main.py", output)
        self.assertIn("test_main.py", output)

        # Should not find other extensions
        self.assertNotIn(".txt", output)
        self.assertNotIn(".json", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_find_files_no_match(self, mock_stdout):
        """Test when no files match the keyword."""
        find_files("nonexistent")
        output = mock_stdout.getvalue()

        # Should have no output
        self.assertEqual(output.strip(), "")

    @patch("sys.stdout", new_callable=StringIO)
    def test_find_files_case_sensitive(self, mock_stdout):
        """Test that search is case-sensitive."""
        find_files("TEST")
        output = mock_stdout.getvalue()

        # Should not find lowercase "test" files
        self.assertNotIn("test_file.txt", output)
        self.assertNotIn("another_test.py", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_find_files_partial_match(self, mock_stdout):
        """Test partial matching in filenames."""
        find_files("conf")
        output = mock_stdout.getvalue()

        # Should find config.json
        self.assertIn("config.json", output)

        # Count occurrences
        lines = [l for l in output.strip().split("\n") if l]
        self.assertEqual(len(lines), 1)

    def test_main_function_empty_keyword(self):
        """Test main function with empty keyword using Click runner."""
        from click.testing import CliRunner
        from fx_bin.find_files import main

        runner = CliRunner()

        # Test with empty string argument (this should trigger the empty check)
        result = runner.invoke(main, [""])

        # Should show the help message
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "Please type text to search. For example: fx ff bar", result.output
        )


class TestFFExclude(unittest.TestCase):
    """Test fx ff command exclusion functionality."""

    def test_ff_skips_default_ignored_dirs(self):
        """Test that fx ff skips default ignored directories."""
        tmp = Path(tempfile.mkdtemp(prefix="fx_ff_test_"))
        try:
            # Create heavy/ignored directories
            (tmp / ".git").mkdir()
            (tmp / ".git" / "test_git.txt").write_text("x")
            (tmp / "node_modules").mkdir()
            (tmp / "node_modules" / "test_node.txt").write_text("x")
            (tmp / ".venv").mkdir()
            (tmp / ".venv" / "test_venv.txt").write_text("x")

            # Normal file that should be found
            (tmp / "test_normal.txt").write_text("x")

            result = _run_ff(["test"], tmp)
            assert result.returncode == 0, result.stderr
            out = result.stdout

            # Should find normal file
            assert "test_normal.txt" in out
            # Should NOT descend into default ignored directories
            assert "test_git.txt" not in out
            assert "test_node.txt" not in out
            assert "test_venv.txt" not in out
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_ff_includes_ignored_when_flag_set(self):
        """Test that fx ff includes ignored directories when flag is set."""
        tmp = Path(tempfile.mkdtemp(prefix="fx_ff_test_inc_"))
        try:
            (tmp / ".git").mkdir()
            (tmp / ".git" / "test_git.txt").write_text("x")
            (tmp / "node_modules").mkdir()
            (tmp / "node_modules" / "test_node.txt").write_text("x")
            (tmp / ".venv").mkdir()
            (tmp / ".venv" / "test_venv.txt").write_text("x")

            result = _run_ff(["test", "--include-ignored"], tmp)
            assert result.returncode == 0, result.stderr
            out = result.stdout

            # With flag, results from ignored directories should appear
            assert "test_git.txt" in out
            assert "test_node.txt" in out
            assert "test_venv.txt" in out
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_ff_exclude_patterns_and_names(self):
        """Test fx ff exclusion patterns and names."""
        tmp = Path(tempfile.mkdtemp(prefix="fx_ff_test_ex_"))
        try:
            # Directories
            (tmp / "build").mkdir()
            (tmp / "build" / "test_build.txt").write_text("x")
            (tmp / "dist").mkdir()
            (tmp / "dist" / "test_dist.txt").write_text("x")

            # Files in root
            (tmp / "test.log").write_text("x")
            (tmp / "test_keep.txt").write_text("x")

            # Exclude dir by name and files by glob
            result = _run_ff(["test", "--exclude", "build", "--exclude", "*.log"], tmp)
            assert result.returncode == 0, result.stderr
            out = result.stdout

            # build/ subtree pruned
            assert "test_build.txt" not in out
            # *.log excluded
            assert "test.log" not in out
            # Others remain
            assert "test_dist.txt" in out
            assert "test_keep.txt" in out
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
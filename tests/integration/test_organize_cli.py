"""Integration tests for organize CLI command."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from fx_bin.cli import cli


class TestOrganizeCLI(unittest.TestCase):
    """Test organize command CLI interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_organize_help_displays_options(self):
        """Test that 'fx organize --help' displays all available options."""
        result = self.runner.invoke(cli, ["organize", "--help"])

        self.assertEqual(result.exit_code, 0)
        # Check that main options are documented
        self.assertIn("--output", result.output)
        self.assertIn("--dry-run", result.output)
        self.assertIn("--date-source", result.output)
        self.assertIn("--depth", result.output)
        self.assertIn("--on-conflict", result.output)
        # Check for Phase 9 required options
        self.assertIn("--hidden", result.output)
        self.assertIn("--recursive", result.output)
        self.assertIn("--clean-empty", result.output)
        self.assertIn("--fail-fast", result.output)

    def test_organize_requires_source_argument(self):
        """Test that organize command requires a source directory argument."""
        result = self.runner.invoke(cli, ["organize"])

        # Should show error or help about missing argument
        self.assertNotEqual(result.exit_code, 0)

    def test_organize_dry_run_shows_plan(self):
        """Test that --dry-run shows what would be done without changes."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo1.jpg").write_text("photo1")
            (source_dir / "photo2.jpg").write_text("photo2")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Run organize in dry-run mode
            result = self.runner.invoke(
                cli,
                ["organize", str(source_dir), "--output", str(output_dir), "--dry-run"],
            )

            self.assertEqual(result.exit_code, 0)
            # Should show summary of what would be done
            self.assertIn("files", result.output.lower())
            # Verify source files still exist
            self.assertTrue((source_dir / "photo1.jpg").exists())
            self.assertTrue((source_dir / "photo2.jpg").exists())

    def test_organize_actual_execution_moves_files(self):
        """Test that organize actually moves files to date-based directories."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Run organize (not dry-run)
            result = self.runner.invoke(
                cli,
                [
                    "organize",
                    str(source_dir),
                    "--output",
                    str(output_dir),
                    "--yes",  # Skip confirmation
                ],
            )

            self.assertEqual(result.exit_code, 0)
            # Verify source file was moved
            self.assertFalse((source_dir / "photo.jpg").exists())
            # Verify file exists in output with date-based path
            output_files = list(output_dir.rglob("photo.jpg"))
            self.assertEqual(len(output_files), 1)


class TestAskModeInCLI(unittest.TestCase):
    """Test cases for ASK mode in CLI layer (Phase 2)."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_given_ask_mode_and_tty_when_disk_conflict_then_prompts_user(self):
        """Test that ASK mode prompts user for disk conflicts when stdin is TTY."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("source photo")

            # Create output directory with CONFLICTING file (disk conflict!)
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text("existing photo")

            # Mock sys.stdin.isatty() to return True to simulate TTY
            with patch('fx_bin.cli.sys') as mock_sys:
                mock_sys.stdin.isatty.return_value = True

                # Run organize with ASK mode
                result = self.runner.invoke(
                    cli,
                    [
                        "organize",
                        str(source_dir),
                        "--output",
                        str(output_dir),
                        "--on-conflict",
                        "ask",
                        "--yes",  # Skip initial confirmation
                    ],
                    # Simulate user answering "n" (no) to skip the conflict
                    input="n\n",
                )

            # Should succeed
            self.assertEqual(result.exit_code, 0)

            # Verify source file still exists (user chose to skip)
            self.assertTrue((source_dir / "photo.jpg").exists())

            # Verify existing file is unchanged
            existing = output_dir / "2026" / "202601" / "20260110" / "photo.jpg"
            self.assertTrue(existing.exists())
            self.assertEqual(existing.read_text(), "existing photo")

    def test_given_ask_mode_and_tty_when_user_confirms_then_moves_file(self):
        """Test that ASK mode moves file when user confirms the prompt."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("source photo")

            # Create output directory with CONFLICTING file (disk conflict!)
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text("existing photo")

            # Mock sys.stdin.isatty() to return True to simulate TTY
            with patch('fx_bin.cli.sys') as mock_sys:
                mock_sys.stdin.isatty.return_value = True

                # User answers "y" (yes) to overwrite - this should use OVERWRITE behavior
                result = self.runner.invoke(
                    cli,
                    [
                        "organize",
                        str(source_dir),
                        "--output",
                        str(output_dir),
                        "--on-conflict",
                        "ask",
                        "--yes",  # Skip initial confirmation
                    ],
                    # Simulate user answering "y" (yes) to overwrite
                    input="y\n",
                )

            # Should succeed
            self.assertEqual(result.exit_code, 0)

            # Verify source file is gone (moved and overwrote target)
            self.assertFalse((source_dir / "photo.jpg").exists())

            # Verify existing file was overwritten
            existing = output_dir / "2026" / "202601" / "20260110" / "photo.jpg"
            self.assertTrue(existing.exists())
            self.assertEqual(existing.read_text(), "source photo")

    def test_given_ask_mode_and_non_tty_when_disk_conflict_then_falls_back_to_skip(self):
        """Test that ASK mode falls back to SKIP when stdin is not a TTY."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("source photo")

            # Create output directory with CONFLICTING file (disk conflict!)
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text("existing photo")

            # Mock stdin.isatty() to return False (non-TTY, like piped input)
            with patch("fx_bin.cli.sys.stdin.isatty", return_value=False):
                result = self.runner.invoke(
                    cli,
                    [
                        "organize",
                        str(source_dir),
                        "--output",
                        str(output_dir),
                        "--on-conflict",
                        "ask",
                        "--yes",  # Skip initial confirmation
                    ],
                )

            # Should succeed (fallback to SKIP)
            self.assertEqual(result.exit_code, 0)

            # Verify source file still exists (skipped due to non-TTY)
            self.assertTrue((source_dir / "photo.jpg").exists())

            # Verify existing file is unchanged
            existing = output_dir / "2026" / "202601" / "20260110" / "photo.jpg"
            self.assertTrue(existing.exists())
            self.assertEqual(existing.read_text(), "existing photo")


if __name__ == "__main__":
    unittest.main()

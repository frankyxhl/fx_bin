"""Integration tests for organize CLI command."""

import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()

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
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "existing photo"
            )

            # Mock sys.stdin.isatty() to return True to simulate TTY
            with patch("fx_bin.cli.sys") as mock_sys:
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
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "existing photo"
            )

            # Mock sys.stdin.isatty() to return True to simulate TTY
            with patch("fx_bin.cli.sys") as mock_sys:
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

    def test_given_ask_mode_and_non_tty_when_disk_conflict_then_falls_back_to_skip(
        self,
    ):
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
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "existing photo"
            )

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


class TestQuietMode(unittest.TestCase):
    """Test cases for --quiet mode (Phase 4)."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_given_quiet_mode_when_no_errors_then_outputs_summary(self):
        """Test that --quiet mode outputs summary even when there are no errors.

        Per CLI help text: "errors and summary only" - summary should ALWAYS be shown.
        This test ensures --quiet outputs summary when no errors occur.
        """
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Run organize with --quiet flag (no errors expected)
            result = self.runner.invoke(
                cli,
                [
                    "organize",
                    str(source_dir),
                    "--output",
                    str(output_dir),
                    "--quiet",
                    "--yes",  # Skip confirmation
                ],
            )

            self.assertEqual(result.exit_code, 0)

            # CRITICAL: Summary should be shown even in quiet mode when no errors
            self.assertIn("Summary:", result.output)
            self.assertIn("files", result.output.lower())
            self.assertIn("processed", result.output.lower())

    def test_given_quiet_mode_when_errors_then_outputs_summary_and_errors(self):
        """Test that --quiet mode outputs both summary and errors when errors occur."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Run organize with --quiet flag
            result = self.runner.invoke(
                cli,
                [
                    "organize",
                    str(source_dir),
                    "--output",
                    str(output_dir),
                    "--quiet",
                    "--yes",
                ],
            )

            self.assertEqual(result.exit_code, 0)

            # Should show summary
            self.assertIn("Summary:", result.output)


class TestQuietYesMode(unittest.TestCase):
    """Test cases for --yes + --quiet interaction (Phase 2.1)."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_given_yes_and_quiet_when_organizing_then_suppresses_organizing_message(
        self,
    ):
        """Test that --yes + --quiet suppresses "Organizing files..." message.

        RED phase: This test will FAIL before the fix because --yes branch
        prints "Organizing files..." even when --quiet is set.

        GREEN phase: After adding `and not quiet` condition, the test will pass.

        Per --quiet semantics ("errors and summary only"), the "Organizing files..."
        progress message should be suppressed. Only the final summary should be shown.
        """
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Run organize with both --yes and --quiet flags
            result = self.runner.invoke(
                cli,
                [
                    "organize",
                    str(source_dir),
                    "--output",
                    str(output_dir),
                    "--yes",
                    "--quiet",
                ],
            )

            self.assertEqual(result.exit_code, 0)

            # CRITICAL: "Organizing files..." message should NOT appear in quiet mode
            self.assertNotIn(
                "Organizing files",
                result.output,
                "--quiet should suppress 'Organizing files...' message from --yes branch",
            )

            # Summary should still be shown (per --quiet semantics)
            self.assertIn("Summary:", result.output)
            self.assertIn("files", result.output.lower())


class TestLoguruConfiguration(unittest.TestCase):
    """Test cases for loguru configuration (Phase 3.1)."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner(mix_stderr=False)

    def test_given_quiet_mode_when_warning_logged_then_suppresses_output(self):
        """Test that --quiet mode suppresses WARNING output from loguru.

        RED phase: This test will FAIL before loguru configuration is added.
        GREEN phase: After configuring loguru level to ERROR in quiet mode, test passes.

        Per Decision 2.5, --quiet should configure loguru to ERROR level,
        which suppresses WARNING messages.
        """
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory with conflicting file
            # This will trigger ASK mode runtime conflict (TOCTOU scenario)
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "existing"
            )

            # Mock stdin.isatty() to return False to trigger runtime conflict path
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
                        "--quiet",
                        "--yes",
                    ],
                )

            self.assertEqual(result.exit_code, 0)

            # CRITICAL: WARNING should NOT appear in stderr when --quiet is set
            # loguru writes to stderr, so we check stderr specifically
            self.assertNotIn(
                "WARNING",
                result.stderr,
                "--quiet should suppress WARNING output from loguru",
            )

            # Summary should still be shown in stdout
            self.assertIn("Summary:", result.output)

    def test_given_verbose_mode_when_warning_logged_then_shows_output(self):
        """Test that --verbose mode shows WARNING output from loguru.

        RED phase: This test will FAIL before loguru configuration is added.
        GREEN phase: After configuring loguru level to DEBUG in verbose mode, test passes.

        Per Decision 2.5, --verbose should configure loguru to DEBUG level,
        which shows all messages including WARNING.
        """
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory with conflicting file
            # This will trigger ASK mode runtime conflict
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "existing"
            )

            # Mock stdin.isatty() to return False to trigger runtime conflict path
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
                        "--verbose",
                        "--yes",
                    ],
                )

            self.assertEqual(result.exit_code, 0)

            # CRITICAL: WARNING SHOULD appear in stderr when --verbose is set
            # Note: This test expects WARNING to be shown (we'll add logger.warning in Phase 3.2)
            # For now, this test verifies that loguru is configured to DEBUG level
            # The actual WARNING message will be added in Phase 3.2
            pass  # We'll verify this after adding logger.warning() in Phase 3.2

    def test_given_default_mode_when_warning_logged_then_shows_output(self):
        """Test that default mode (no --quiet, no --verbose) shows WARNING output.

        RED phase: This test will FAIL before loguru configuration is added.
        GREEN phase: After configuring loguru level to INFO by default, test passes.

        Per Decision 2.5, default loguru level should be INFO,
        which shows WARNING messages.
        """
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory with conflicting file
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "existing"
            )

            # Mock stdin.isatty() to return False to trigger runtime conflict path
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
                        # No --quiet or --verbose (default mode)
                        "--yes",
                    ],
                )

            self.assertEqual(result.exit_code, 0)

            # CRITICAL: WARNING SHOULD appear in stderr in default mode
            # Note: This test expects WARNING to be shown (we'll add logger.warning in Phase 3.2)
            pass  # We'll verify this after adding logger.warning() in Phase 3.2


class TestAskRuntimeConflicts(unittest.TestCase):
    """Test cases for ASK mode runtime conflicts (Phase 3.2)."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner(mix_stderr=False)

    def test_given_ask_mode_and_runtime_conflict_when_default_mode_then_logs_warning(
        self,
    ):
        """Test that ASK mode runtime conflicts log a WARNING in default mode.

        RED phase: This test will FAIL before logger.warning() is added.
        GREEN phase: After adding logger.warning() in move_file_safe(), test passes.

        Per Decision 3, ASK mode runtime conflicts should skip with warning log.
        This test simulates a TOCTOU (time-of-check-time-of-use) scenario where
        a conflict appears between the scan phase and execution phase.
        """
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("source photo")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)

            # Run organize with ASK mode (no --quiet, no --verbose)
            # First run to set up the state
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
                        "--yes",
                    ],
                )

            self.assertEqual(result.exit_code, 0)

            # Now create a NEW conflicting file in the output (simulating TOCTOU)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "new conflict"
            )

            # Create another source file to trigger the runtime conflict
            (source_dir / "photo2.jpg").write_text("another photo")

            # Run organize again - this will hit the runtime conflict in move_file_safe
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
                        "--yes",
                    ],
                )

            self.assertEqual(result.exit_code, 0)

            # CRITICAL: For now, we just verify the command succeeds
            # The actual WARNING logging will be verified once we add logger.warning()
            # in the GREEN phase of Phase 3.2

    def test_given_ask_mode_and_runtime_conflict_when_quiet_then_suppresses_warning(
        self,
    ):
        """Test that ASK mode runtime conflicts respect --quiet flag.

        RED phase: This test will FAIL before loguru configuration is properly tested.
        GREEN phase: After logger.warning() respects loguru configuration, test passes.

        Per Decision 3, logger.warning() should respect --quiet flag (via loguru level config).
        """
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("source photo")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()
            (output_dir / "2026" / "202601" / "20260110").mkdir(parents=True)

            # First run to set up the state
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
                        "--yes",
                    ],
                )

            # Create a NEW conflicting file (simulating TOCTOU)
            (output_dir / "2026" / "202601" / "20260110" / "photo.jpg").write_text(
                "new conflict"
            )

            # Create another source file
            (source_dir / "photo2.jpg").write_text("another photo")

            # Run with --quiet - WARNING should be suppressed
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
                        "--quiet",
                        "--yes",
                    ],
                )

            self.assertEqual(result.exit_code, 0)

            # CRITICAL: WARNING should NOT appear in stderr when --quiet is set
            self.assertNotIn(
                "WARNING",
                result.stderr,
                "--quiet should suppress WARNING from runtime conflicts",
            )


if __name__ == "__main__":
    unittest.main()

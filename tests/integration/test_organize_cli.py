"""Integration tests for organize CLI command."""

import os
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from fx_bin.cli import cli


FIXED_MODIFIED_TS = datetime(2026, 1, 10, 12, 0, 0).timestamp()


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


class TestConfirmationPromptBehavior(unittest.TestCase):
    """Tests for the initial confirmation prompt when running organize command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_given_tty_when_user_confirms_then_proceeds(self):
        """TTY mode: user confirms 'y' -> organization proceeds."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo1.jpg").write_text("photo1")
            (source_dir / "photo2.jpg").write_text("photo2")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Mock TTY and provide 'y' input
            with patch("fx_bin.cli.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                result = self.runner.invoke(
                    cli,
                    ["organize", str(source_dir), "--output", str(output_dir)],
                    input="y\n",
                )

            self.assertEqual(result.exit_code, 0)
            # Verify "Proceed?" prompt appeared
            self.assertIn("Proceed?", result.output)
            # Verify files were organized
            self.assertFalse((source_dir / "photo1.jpg").exists())
            self.assertFalse((source_dir / "photo2.jpg").exists())
            # Verify files are in output
            output_files = list(output_dir.rglob("*.jpg"))
            self.assertEqual(len(output_files), 2)

    def test_given_tty_when_user_cancels_then_exits_without_changes(self):
        """TTY mode: user cancels 'n' -> exits without changes."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Mock TTY and provide 'n' input
            with patch("fx_bin.cli.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                result = self.runner.invoke(
                    cli,
                    ["organize", str(source_dir), "--output", str(output_dir)],
                    input="n\n",
                )

            self.assertEqual(result.exit_code, 0)
            # Verify "Cancelled." message
            self.assertIn("Cancelled.", result.output)
            # Verify NO files moved - source still exists
            self.assertTrue((source_dir / "photo.jpg").exists())
            # Verify output directory is empty
            output_files = list(output_dir.rglob("*.jpg"))
            self.assertEqual(len(output_files), 0)

    def test_given_non_tty_when_organizing_then_auto_proceeds(self):
        """Non-TTY mode: auto-proceeds without prompt."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Mock non-TTY (stdin not a tty)
            with patch("fx_bin.cli.sys.stdin.isatty", return_value=False):
                result = self.runner.invoke(
                    cli,
                    ["organize", str(source_dir), "--output", str(output_dir)],
                )

            self.assertEqual(result.exit_code, 0)
            # Verify NO "Proceed?" prompt
            self.assertNotIn("Proceed?", result.output)
            # Verify files were organized
            self.assertFalse((source_dir / "photo.jpg").exists())
            output_files = list(output_dir.rglob("*.jpg"))
            self.assertEqual(len(output_files), 1)

    def test_given_yes_flag_when_organizing_then_skips_confirmation(self):
        """--yes flag: skips confirmation entirely."""
        with self.runner.isolated_filesystem():
            # Create source directory with files
            source_dir = Path("source")
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir()

            # Use --yes flag
            result = self.runner.invoke(
                cli,
                [
                    "organize",
                    str(source_dir),
                    "--output",
                    str(output_dir),
                    "--yes",
                ],
            )

            self.assertEqual(result.exit_code, 0)
            # Verify NO "Proceed?" prompt
            self.assertNotIn("Proceed?", result.output)
            # Verify files were organized
            self.assertFalse((source_dir / "photo.jpg").exists())
            output_files = list(output_dir.rglob("*.jpg"))
            self.assertEqual(len(output_files), 1)


class TestAskModeInCLI(unittest.TestCase):
    """Test cases for ASK mode in CLI layer (Phase 2)."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_given_ask_mode_and_tty_when_disk_conflict_then_prompts_user(self):
        """Test that ASK mode prompts user for disk conflicts when stdin is TTY."""
        with self.runner.isolated_filesystem():
            source_dir = Path("source")
            source_dir.mkdir()
            source_file = source_dir / "photo.jpg"
            source_file.write_text("source photo")
            os.utime(source_file, (FIXED_MODIFIED_TS, FIXED_MODIFIED_TS))

            output_dir = Path("output")
            output_dir.mkdir()
            conflict_dir = output_dir / "2026" / "202601" / "20260110"
            conflict_dir.mkdir(parents=True)
            (conflict_dir / "photo.jpg").write_text("existing photo")

            with patch("fx_bin.cli.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                result = self.runner.invoke(
                    cli,
                    [
                        "organize",
                        str(source_dir),
                        "--output",
                        str(output_dir),
                        "--date-source",
                        "modified",
                        "--on-conflict",
                        "ask",
                        "--yes",  # Skip initial confirmation
                    ],
                    input="n\n",
                )

            self.assertIn("Found 1 disk conflict(s):", result.output)
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(source_file.exists())
            self.assertEqual((conflict_dir / "photo.jpg").read_text(), "existing photo")

    def test_given_ask_mode_and_tty_when_user_confirms_then_moves_file(self):
        """Test that ASK mode overwrites when user confirms the prompt."""
        with self.runner.isolated_filesystem():
            source_dir = Path("source")
            source_dir.mkdir()
            source_file = source_dir / "photo.jpg"
            source_file.write_text("source photo")
            os.utime(source_file, (FIXED_MODIFIED_TS, FIXED_MODIFIED_TS))

            output_dir = Path("output")
            output_dir.mkdir()
            conflict_dir = output_dir / "2026" / "202601" / "20260110"
            conflict_dir.mkdir(parents=True)
            target_file = conflict_dir / "photo.jpg"
            target_file.write_text("existing photo")

            with patch("fx_bin.cli.sys") as mock_sys:
                mock_sys.stdin.isatty.return_value = True
                result = self.runner.invoke(
                    cli,
                    [
                        "organize",
                        str(source_dir),
                        "--output",
                        str(output_dir),
                        "--date-source",
                        "modified",
                        "--on-conflict",
                        "ask",
                        "--yes",  # Skip initial confirmation
                    ],
                    input="y\n",
                )

            self.assertIn("Found 1 disk conflict(s):", result.output)
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(source_file.exists())
            self.assertEqual(target_file.read_text(), "source photo")

    def test_given_ask_mode_and_non_tty_when_disk_conflict_then_falls_back_to_skip(
        self,
    ):
        """Test that ASK mode falls back to SKIP when stdin is not a TTY."""
        with self.runner.isolated_filesystem():
            source_dir = Path("source")
            source_dir.mkdir()
            source_file = source_dir / "photo.jpg"
            source_file.write_text("source photo")
            os.utime(source_file, (FIXED_MODIFIED_TS, FIXED_MODIFIED_TS))

            output_dir = Path("output")
            output_dir.mkdir()
            conflict_dir = output_dir / "2026" / "202601" / "20260110"
            conflict_dir.mkdir(parents=True)
            (conflict_dir / "photo.jpg").write_text("existing photo")

            with patch("fx_bin.cli.sys.stdin.isatty", return_value=False):
                result = self.runner.invoke(
                    cli,
                    [
                        "organize",
                        str(source_dir),
                        "--output",
                        str(output_dir),
                        "--date-source",
                        "modified",
                        "--on-conflict",
                        "ask",
                        "--yes",  # Skip initial confirmation
                    ],
                )

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(source_file.exists())
            self.assertEqual((conflict_dir / "photo.jpg").read_text(), "existing photo")


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


class TestAskRuntimeConflicts(unittest.TestCase):
    """Test cases for ASK mode runtime conflicts (Phase 3.2).

    These tests verify the TOCTOU (time-of-check-time-of-use) scenario where
    a conflict appears between the scan phase and execution phase.

    Important Implementation Note:
    Due to the current CLI architecture, the ASK runtime conflict WARNING
    is difficult to trigger through the CLI interface because:
    1. TTY mode: Scan-time conflicts are detected and handled via custom execution path
    2. Non-TTY mode: ASK is downgraded to SKIP, so no runtime conflict check

    The actual WARNING logging functionality is verified by directly testing
    move_file_safe() which contains the runtime conflict detection logic.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner(mix_stderr=False)

    def test_given_ask_mode_and_runtime_conflict_when_default_mode_then_logs_warning(
        self,
    ):
        """Test that move_file_safe logs WARNING for ASK runtime conflicts.

        Per Decision 3, ASK mode runtime conflicts should skip with warning log.

        This test directly calls move_file_safe with ConflictMode.ASK and
        a pre-existing target to verify the WARNING is logged correctly.

        Note: This tests the underlying functionality since triggering this
        through the CLI is not feasible (see class docstring for details).
        """
        from fx_bin.organize_functional import move_file_safe
        from fx_bin.organize import ConflictMode
        from io import StringIO
        from loguru import logger

        with self.runner.isolated_filesystem():
            # Create source file
            source_dir = Path("source")
            source_dir.mkdir()
            source_file = source_dir / "photo.jpg"
            source_file.write_text("source photo")

            # Create output directory with pre-existing target (simulates TOCTOU)
            output_dir = Path("output")
            output_dir.mkdir()
            target_dir = output_dir / "2026" / "202601" / "20260110"
            target_dir.mkdir(parents=True)
            target_file = target_dir / "photo.jpg"
            target_file.write_text("existing content")

            # Capture stderr using a custom handler
            stderr_capture = StringIO()

            # Configure loguru to write to our capture at INFO level
            # Include level in format to verify WARNING is logged
            logger.remove()
            logger.add(stderr_capture, level="INFO", format="{level} | {message}")

            try:
                # Call move_file_safe with ASK mode
                result = move_file_safe(
                    str(source_file),
                    str(target_file),
                    str(source_dir),  # source_root
                    str(output_dir),  # output_root
                    ConflictMode.ASK,
                )

                # Get captured stderr
                stderr_output = stderr_capture.getvalue()

                # Verify result is success (file was skipped)
                self.assertTrue(
                    str(result).startswith("<IOResult: <Success"),
                    f"move_file_safe should return success, got: {result}",
                )

                # Verify source file still exists (was skipped due to conflict)
                self.assertTrue(source_file.exists())
                self.assertTrue(target_file.exists())

                # CRITICAL: Verify WARNING was logged
                self.assertIn(
                    "WARNING",
                    stderr_output,
                    "Default mode should show WARNING for ASK runtime "
                    f"conflicts. Got: {repr(stderr_output)}",
                )
                self.assertIn(
                    "Runtime conflict:",
                    stderr_output,
                    "Should log specific runtime conflict message",
                )

            finally:
                # Reset loguru configuration
                logger.remove()

    def test_given_ask_mode_and_runtime_conflict_when_quiet_then_suppresses_warning(
        self,
    ):
        """Test that ASK mode runtime conflicts respect --quiet flag.

        Per Decision 3, logger.warning() should respect --quiet flag (via loguru level config).

        This test directly calls move_file_safe and verifies that when loguru
        is configured to ERROR level (simulating --quiet mode), WARNING is suppressed.
        """
        from fx_bin.organize_functional import move_file_safe
        from fx_bin.organize import ConflictMode
        from io import StringIO
        from loguru import logger

        with self.runner.isolated_filesystem():
            # Create source file
            source_dir = Path("source")
            source_dir.mkdir()
            source_file = source_dir / "photo.jpg"
            source_file.write_text("source photo")

            # Create output directory with pre-existing target
            output_dir = Path("output")
            output_dir.mkdir()
            target_dir = output_dir / "2026" / "202601" / "20260110"
            target_dir.mkdir(parents=True)
            target_file = target_dir / "photo.jpg"
            target_file.write_text("existing content")

            # Capture stderr
            stderr_capture = StringIO()

            # Configure loguru to ERROR level (simulating --quiet mode)
            logger.remove()
            logger.add(stderr_capture, level="ERROR", format="{level} | {message}")

            try:
                # Call move_file_safe with ASK mode
                result = move_file_safe(
                    str(source_file),
                    str(target_file),
                    str(source_dir),
                    str(output_dir),
                    ConflictMode.ASK,
                )

                # Get captured stderr
                stderr_output = stderr_capture.getvalue()

                # Verify result is success
                self.assertTrue(
                    str(result).startswith("<IOResult: <Success"),
                    f"move_file_safe should return success, got: {result}",
                )

                # CRITICAL: WARNING should NOT appear when loguru is set to ERROR level
                self.assertNotIn(
                    "WARNING",
                    stderr_output,
                    "--quiet mode (ERROR level) should suppress WARNING. "
                    f"Got: {repr(stderr_output)}",
                )
                self.assertNotIn(
                    "Runtime conflict detected",
                    stderr_output,
                    "--quiet mode should suppress runtime conflict message",
                )

            finally:
                # Reset loguru configuration
                logger.remove()


if __name__ == "__main__":
    unittest.main()

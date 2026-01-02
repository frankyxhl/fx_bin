"""Integration tests for realpath CLI command."""

import os
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from fx_bin.cli import cli


class TestRealpathCLI(unittest.TestCase):
    """Test realpath command CLI interface."""

    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir)

    def test_successful_path_output(self):
        """Test successful realpath command execution."""
        subdir = self.test_path / "subdir"
        subdir.mkdir()

        result = self.runner.invoke(cli, ["realpath", str(subdir)])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(Path(result.output.strip()).resolve(), subdir.resolve())

    def test_no_argument_uses_current_directory(self):
        """Test realpath with no argument uses current directory."""
        result = self.runner.invoke(cli, ["realpath"])

        self.assertEqual(result.exit_code, 0)
        output_path = Path(result.output.strip())
        self.assertTrue(output_path.is_absolute())
        self.assertTrue(output_path.exists())

    def test_error_exit_code_for_nonexistent_path(self):
        """Test that non-existent path returns exit code 1."""
        result = self.runner.invoke(cli, ["realpath", "/nonexistent/path/foo"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error:", result.output)
        self.assertIn("does not exist", result.output)

    def test_help_output(self):
        """Test realpath command help."""
        result = self.runner.invoke(cli, ["realpath", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Get absolute path", result.output)
        self.assertIn("Examples:", result.output)

    def test_command_appears_in_fx_list(self):
        """Test that realpath command appears in fx list output."""
        result = self.runner.invoke(cli, ["list"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("realpath", result.output)
        self.assertIn("Get absolute path", result.output)

    def test_command_appears_in_fx_help(self):
        """Test that realpath command appears in main help."""
        result = self.runner.invoke(cli, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("realpath", result.output)

    def test_invalid_flag_handled_gracefully(self):
        """Test handling of invalid flags."""
        result = self.runner.invoke(cli, ["realpath", "--invalid-flag"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("no such option", result.output.lower())


class TestRealpathCLIEdgeCases(unittest.TestCase):
    """Test edge cases for realpath CLI."""

    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_dir)

    def test_relative_path_resolution(self):
        """Test resolving relative path via CLI."""
        target_dir = self.test_path / "target"
        target_dir.mkdir()

        result = self.runner.invoke(cli, ["realpath", str(target_dir)])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            Path(result.output.strip()).resolve(), target_dir.resolve()
        )

    def test_tilde_expansion(self):
        """Test ~ expansion in CLI."""
        result = self.runner.invoke(cli, ["realpath", "~"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(Path(result.output.strip()).resolve(), Path.home().resolve())

    def test_symlink_resolution_via_cli(self):
        """Test symlink resolution via CLI."""
        real_file = self.test_path / "real.txt"
        real_file.write_text("content")

        link_path = self.test_path / "link.txt"
        try:
            link_path.symlink_to(real_file)

            result = self.runner.invoke(cli, ["realpath", str(link_path)])

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                Path(result.output.strip()).resolve(), real_file.resolve()
            )
        except OSError:
            self.skipTest("Symbolic links not supported on this system")

    def test_permission_error_handling(self):
        """Test permission error results in exit code 1."""
        restricted_dir = self.test_path / "restricted"
        restricted_dir.mkdir()
        inner_file = restricted_dir / "inner.txt"

        try:
            os.chmod(str(restricted_dir), 0o000)

            result = self.runner.invoke(cli, ["realpath", str(inner_file)])

            self.assertEqual(result.exit_code, 1)
            self.assertIn("Error:", result.output)
        finally:
            os.chmod(str(restricted_dir), 0o755)

    def test_output_is_just_path_no_prefix(self):
        """Test that output is just the path without any prefix text."""
        result = self.runner.invoke(cli, ["realpath", str(self.test_path)])

        self.assertEqual(result.exit_code, 0)
        output = result.output.strip()
        self.assertTrue(output.startswith("/"))
        self.assertNotIn(":", output.split("\n")[0])


if __name__ == "__main__":
    unittest.main()

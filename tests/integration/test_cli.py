"""Test cases for the unified CLI command interface."""

import unittest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
from fx_bin.cli import cli, list_commands, COMMANDS_INFO


class TestCLICommand(unittest.TestCase):
    """Test the main CLI command group."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_without_command_shows_help(self):
        """Test that running 'fx' without a command shows help."""
        result = self.runner.invoke(cli, [])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("FX - A collection of file and text utilities", result.output)
        self.assertIn("Commands:", result.output)

    def test_cli_with_help_flag(self):
        """Test that 'fx --help' shows help."""
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("FX - A collection of file and text utilities", result.output)
        self.assertIn("Commands:", result.output)

    def test_cli_with_version_flag(self):
        """Test that 'fx --version' shows version."""
        result = self.runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        # Version output format may vary

    def test_list_command_output(self):
        """Test that 'fx list' shows all available commands."""
        result = self.runner.invoke(cli, ["list"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Available fx commands:", result.output)

        # Check that all commands from COMMANDS_INFO are listed
        for cmd, description in COMMANDS_INFO:
            self.assertIn(f"fx {cmd}", result.output)
            self.assertIn(description, result.output)

        self.assertIn("Use 'fx COMMAND --help' for more information", result.output)

    def test_list_command_function_directly(self):
        """Test the list_commands function directly."""
        # Use CliRunner to test the function
        result = self.runner.invoke(list_commands, [])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Available fx commands:", result.output)


class TestFilesCommand(unittest.TestCase):
    """Test the 'fx files' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("fx_bin.files.list_files_count")
    def test_files_command_default_path(self, mock_list_files):
        """Test 'fx files' with default path (current directory)."""
        from fx_bin.common import FileCountEntry, EntryType

        mock_entries = [
            FileCountEntry("file1.txt", 1, EntryType.FILE),
            FileCountEntry("file2.txt", 1, EntryType.FILE),
        ]
        mock_list_files.return_value = mock_entries

        result = self.runner.invoke(cli, ["files"])
        self.assertEqual(result.exit_code, 0)
        mock_list_files.assert_called_once_with(".")
        self.assertIn("file1.txt", result.output)
        self.assertIn("file2.txt", result.output)

    @patch("fx_bin.files.list_files_count")
    def test_files_command_with_path(self, mock_list_files):
        """Test 'fx files /path' with specified path."""
        with self.runner.isolated_filesystem():
            import os

            os.makedirs("test_dir")

            from fx_bin.common import FileCountEntry, EntryType

            mock_entries = [FileCountEntry("test_file.txt", 1, EntryType.FILE)]
            mock_list_files.return_value = mock_entries

            result = self.runner.invoke(cli, ["files", "test_dir"])
            self.assertEqual(result.exit_code, 0)
            mock_list_files.assert_called_once_with("test_dir")
            self.assertIn("test_file.txt", result.output)

    @patch("fx_bin.files.list_files_count")
    def test_files_command_multiple_paths(self, mock_list_files):
        """Test 'fx files' with multiple paths."""
        with self.runner.isolated_filesystem():
            import os

            os.makedirs("dir1")
            os.makedirs("dir2")

            from fx_bin.common import FileCountEntry, EntryType

            mock_entries1 = [FileCountEntry("file1.txt", 1, EntryType.FILE)]
            mock_entries2 = [FileCountEntry("file2.txt", 1, EntryType.FILE)]
            mock_list_files.side_effect = [mock_entries1, mock_entries2]

            result = self.runner.invoke(cli, ["files", "dir1", "dir2"])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(mock_list_files.call_count, 2)


class TestSizeCommand(unittest.TestCase):
    """Test the 'fx size' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("fx_bin.size.list_size")
    def test_size_command_default_path(self, mock_list_size):
        """Test 'fx size' with default path."""
        mock_entry = MagicMock()
        mock_entry.__str__ = lambda self: "100B file.txt"
        mock_list_size.return_value = [mock_entry]

        result = self.runner.invoke(cli, ["size"])
        self.assertEqual(result.exit_code, 0)
        mock_list_size.assert_called_once_with(".")
        self.assertIn("100B file.txt", result.output)

    @patch("fx_bin.size.list_size")
    def test_size_command_with_path(self, mock_list_size):
        """Test 'fx size /path' with specified path."""
        with self.runner.isolated_filesystem():
            import os

            os.makedirs("test_dir")

            mock_entry = MagicMock()
            mock_entry.__str__ = lambda self: "1KB test.txt"
            mock_list_size.return_value = [mock_entry]

            result = self.runner.invoke(cli, ["size", "test_dir"])
            self.assertEqual(result.exit_code, 0)
            mock_list_size.assert_called_once_with("test_dir")
            self.assertIn("1KB test.txt", result.output)

    @patch("fx_bin.size.list_size")
    def test_size_command_empty_directory(self, mock_list_size):
        """Test 'fx size' with empty directory."""
        with self.runner.isolated_filesystem():
            import os

            os.makedirs("empty_dir")

            mock_list_size.return_value = []

            result = self.runner.invoke(cli, ["size", "empty_dir"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No accessible files or directories", result.output)


class TestFFCommand(unittest.TestCase):
    """Test the 'fx ff' (find files) command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_ff_command_without_keyword(self):
        """Test 'fx ff' without keyword shows error."""
        result = self.runner.invoke(cli, ["ff"])
        self.assertEqual(result.exit_code, 2)  # Click error for missing argument

    @patch("fx_bin.find_files.find_files")
    def test_ff_command_with_keyword(self, mock_find_files):
        """Test 'fx ff keyword' with valid keyword."""
        result = self.runner.invoke(cli, ["ff", "test"])
        self.assertEqual(result.exit_code, 0)
        mock_find_files.assert_called_once_with("test")

    @patch("fx_bin.find_files.find_files")
    def test_ff_command_with_empty_keyword(self, mock_find_files):
        """Test 'fx ff ""' with empty keyword."""
        # Note: When testing whitespace-only input, the check passes through
        # but the actual function should handle it. For now we expect exit_code 0
        # since the error message is shown but doesn't raise an exception
        result = self.runner.invoke(cli, ["ff", " "])
        # The CLI shows error but continues with exit code 0 based on current implementation
        self.assertIn("Please type text to search", result.output)
        mock_find_files.assert_not_called()

    @patch("fx_bin.find_files.find_files")
    def test_ff_command_with_pattern(self, mock_find_files):
        """Test 'fx ff' with pattern like '*.py'."""
        result = self.runner.invoke(cli, ["ff", "*.py"])
        self.assertEqual(result.exit_code, 0)
        mock_find_files.assert_called_once_with("*.py")


class TestReplaceCommand(unittest.TestCase):
    """Test the 'fx replace' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_replace_command_missing_arguments(self):
        """Test 'fx replace' with missing arguments."""
        result = self.runner.invoke(cli, ["replace"])
        self.assertEqual(result.exit_code, 2)  # Click error

        result = self.runner.invoke(cli, ["replace", "old"])
        self.assertEqual(result.exit_code, 2)  # Click error

        result = self.runner.invoke(cli, ["replace", "old", "new"])
        self.assertEqual(result.exit_code, 2)  # Click error - filenames required

    @patch("fx_bin.replace.replace_files")
    def test_replace_command_with_file(self, mock_replace_files):
        """Test 'fx replace old new file.txt'."""
        with self.runner.isolated_filesystem():
            # Create a test file
            with open("test.txt", "w") as f:
                f.write("test content")

            mock_replace_files.return_value = 0

            result = self.runner.invoke(cli, ["replace", "old", "new", "test.txt"])
            self.assertEqual(result.exit_code, 0)
            mock_replace_files.assert_called_once()

            # Check arguments passed to replace_files
            args = mock_replace_files.call_args[0]
            self.assertEqual(args[0], "old")
            self.assertEqual(args[1], "new")
            self.assertIn("test.txt", args[2])


class TestJson2ExcelCommand(unittest.TestCase):
    """Test the 'fx json2excel' command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_json2excel_command_missing_arguments(self):
        """Test 'fx json2excel' with missing arguments."""
        result = self.runner.invoke(cli, ["json2excel"])
        self.assertEqual(result.exit_code, 2)  # Click error

        result = self.runner.invoke(cli, ["json2excel", "input.json"])
        self.assertEqual(result.exit_code, 2)  # Click error

    @patch("fx_bin.pd.main")
    def test_json2excel_command_with_arguments(self, mock_pd_main):
        """Test 'fx json2excel input.json output.xlsx'."""
        mock_pd_main.return_value = 0

        result = self.runner.invoke(cli, ["json2excel", "input.json", "output.xlsx"])
        self.assertEqual(result.exit_code, 0)
        mock_pd_main.assert_called_once_with("input.json", "output.xlsx")

    @patch("fx_bin.pd.main")
    def test_json2excel_command_with_url(self, mock_pd_main):
        """Test 'fx json2excel' with URL."""
        mock_pd_main.return_value = 0

        result = self.runner.invoke(
            cli, ["json2excel", "https://api.example.com/data", "output.xlsx"]
        )
        self.assertEqual(result.exit_code, 0)
        mock_pd_main.assert_called_once_with(
            "https://api.example.com/data", "output.xlsx"
        )


class TestCommandHelp(unittest.TestCase):
    """Test help messages for each command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_files_command_help(self):
        """Test 'fx files --help'."""
        result = self.runner.invoke(cli, ["files", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Count files in directories", result.output)
        self.assertIn("Examples:", result.output)

    def test_size_command_help(self):
        """Test 'fx size --help'."""
        result = self.runner.invoke(cli, ["size", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Analyze file and directory sizes", result.output)
        self.assertIn("Examples:", result.output)

    def test_ff_command_help(self):
        """Test 'fx ff --help'."""
        result = self.runner.invoke(cli, ["ff", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Find files by keyword", result.output)
        self.assertIn("Examples:", result.output)

    def test_replace_command_help(self):
        """Test 'fx replace --help'."""
        result = self.runner.invoke(cli, ["replace", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Replace text in files", result.output)
        self.assertIn("Examples:", result.output)

    def test_json2excel_command_help(self):
        """Test 'fx json2excel --help'."""
        result = self.runner.invoke(cli, ["json2excel", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Convert JSON data to Excel file", result.output)
        self.assertIn("Examples:", result.output)

    def test_list_command_help(self):
        """Test 'fx list --help'."""
        result = self.runner.invoke(cli, ["list", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("List all available fx commands", result.output)

    def test_help_command(self):
        """Test 'fx help' command."""
        result = self.runner.invoke(cli, ["help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("FX - A collection of file and text utilities", result.output)
        self.assertIn("Commands:", result.output)
        self.assertIn("help", result.output)

    def test_help_command_help(self):
        """Test 'fx help --help'."""
        result = self.runner.invoke(cli, ["help", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Show help information", result.output)
        self.assertIn("same as fx -h", result.output)

    def test_version_command(self):
        """Test 'fx version' command."""
        result = self.runner.invoke(cli, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("FX-Bin v", result.output)
        self.assertIn("Repository:", result.output)

    def test_version_flag(self):
        """Test 'fx --version' flag."""
        result = self.runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("FX-Bin v", result.output)
        self.assertIn("Repository:", result.output)


if __name__ == "__main__":
    unittest.main()

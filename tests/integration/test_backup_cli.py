import shutil
import tempfile
import unittest
from pathlib import Path
from click.testing import CliRunner
from fx_bin.cli import cli


class TestBackupCLI(unittest.TestCase):
    """Test CLI with new same-level backup default."""

    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_backup_file_cli_success(self):
        """Test fx backup creates file in same directory as source."""
        test_file = self.test_path / "test.txt"
        test_file.write_text("hello")

        result = self.runner.invoke(cli, ["backup", str(test_file)])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backup created:", result.output)

        # Verify backup is in same directory as source
        backups = list(self.test_path.glob("test_*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].name.endswith(".txt"))
        self.assertEqual(backups[0].parent, self.test_path)

        # Verify no backups subdirectory was created
        backup_subdir = self.test_path / "backups"
        self.assertFalse(backup_subdir.exists())

    def test_backup_directory_cli_uncompressed_success(self):
        """Test fx backup creates directory in same location as source."""
        source_dir = self.test_path / "src"
        source_dir.mkdir()
        (source_dir / "f1.txt").write_text("content")

        result = self.runner.invoke(cli, ["backup", str(source_dir)])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backup created:", result.output)

        # Verify backup is in same directory as source
        backups = list(self.test_path.glob("src_*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].is_dir())
        self.assertEqual(backups[0].parent, self.test_path)

    def test_backup_directory_cli_compressed_success(self):
        """Test fx backup --compress creates archive in same location as source."""
        source_dir = self.test_path / "src"
        source_dir.mkdir()

        result = self.runner.invoke(cli, ["backup", str(source_dir), "--compress"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backup created:", result.output)

        # Verify backup is in same directory as source
        backups = list(self.test_path.glob("src_*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].name.endswith(".tar.xz"))
        self.assertEqual(backups[0].parent, self.test_path)

    def test_backup_cli_nonexistent_path_error(self):
        """Test fx backup with nonexistent path shows error."""
        result = self.runner.invoke(cli, ["backup", "/nonexistent/path"])
        self.assertEqual(result.exit_code, 2)

import shutil
import tempfile
import unittest
from pathlib import Path
from click.testing import CliRunner
from fx_bin.cli import cli


class TestBackupCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.backup_dir = self.test_path / "backups"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_backup_file_cli_success(self):
        test_file = self.test_path / "test.txt"
        test_file.write_text("hello")

        result = self.runner.invoke(
            cli, ["backup", str(test_file), "--backup-dir", str(self.backup_dir)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backup created:", result.output)
        
        backups = list(self.backup_dir.glob("test_*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].name.endswith(".txt"))

    def test_backup_directory_cli_uncompressed_success(self):
        source_dir = self.test_path / "src"
        source_dir.mkdir()
        (source_dir / "f1.txt").write_text("content")

        result = self.runner.invoke(
            cli, ["backup", str(source_dir), "--backup-dir", str(self.backup_dir)]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backup created:", result.output)
        
        backups = list(self.backup_dir.glob("src_*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].is_dir())

    def test_backup_directory_cli_compressed_success(self):
        source_dir = self.test_path / "src"
        source_dir.mkdir()

        result = self.runner.invoke(
            cli, ["backup", str(source_dir), "--backup-dir", str(self.backup_dir), "--compress"]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Backup created:", result.output)
        
        backups = list(self.backup_dir.glob("src_*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].name.endswith(".tar.gz"))

    def test_backup_cli_max_backups_cleanup(self):
        test_file = self.test_path / "test.txt"
        test_file.write_text("hello")

        import time
        for i in range(3):
            self.runner.invoke(
                cli, ["backup", str(test_file), "--backup-dir", str(self.backup_dir), "--max-backups", "2"]
            )
            time.sleep(1.1)

        backups = list(self.backup_dir.glob("test_*"))
        self.assertEqual(len(backups), 2)

    def test_backup_cli_nonexistent_path_error(self):
        result = self.runner.invoke(cli, ["backup", "/nonexistent/path"])
        self.assertEqual(result.exit_code, 2)

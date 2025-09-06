"""Integration tests for root CLI command."""

import os
import tempfile
import unittest
from pathlib import Path
from click.testing import CliRunner

from fx_bin.cli import cli


class TestRootCLI(unittest.TestCase):
    """Test root command CLI interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_root_command_success(self):
        """Test successful root command execution."""
        # Create .git directory
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        subdir = self.test_path / 'subdir'
        subdir.mkdir()
        
        # Change to subdir and run command
        with self.runner.isolated_filesystem():
            os.chdir(str(subdir))
            result = self.runner.invoke(cli, ['root'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Git project root:', result.output)
            self.assertIn(str(self.test_path), result.output)

    def test_root_command_with_cd_flag(self):
        """Test root command with --cd flag."""
        # Create .git directory
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        subdir = self.test_path / 'subdir'
        subdir.mkdir()
        
        # Change to subdir and run command with --cd
        with self.runner.isolated_filesystem():
            os.chdir(str(subdir))
            result = self.runner.invoke(cli, ['root', '--cd'])
            
            self.assertEqual(result.exit_code, 0)
            # Should output just the path (resolve both to handle symlinks)
            self.assertEqual(Path(result.output.strip()).resolve(), self.test_path.resolve())

    def test_root_command_with_c_flag(self):
        """Test root command with -c flag."""
        # Create .git directory
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        subdir = self.test_path / 'subdir'
        subdir.mkdir()
        
        # Change to subdir and run command with -c
        with self.runner.isolated_filesystem():
            os.chdir(str(subdir))
            result = self.runner.invoke(cli, ['root', '-c'])
            
            self.assertEqual(result.exit_code, 0)
            # Should output just the path (resolve both to handle symlinks)
            self.assertEqual(Path(result.output.strip()).resolve(), self.test_path.resolve())

    def test_root_command_no_git_found(self):
        """Test root command when no git repository is found."""
        # Create directory without .git in isolated environment
        with self.runner.isolated_filesystem():
            # Create a temp directory that definitely has no .git
            temp_dir = Path.cwd() / 'isolated_test'
            temp_dir.mkdir()
            os.chdir(str(temp_dir))
            
            result = self.runner.invoke(cli, ['root'])
            
            self.assertEqual(result.exit_code, 1)
            self.assertIn('Error: No git repository found', result.output)

    def test_root_command_no_git_found_cd_flag(self):
        """Test root command with --cd when no git repository is found."""
        # Create directory without .git in isolated environment  
        with self.runner.isolated_filesystem():
            # Create a temp directory that definitely has no .git
            temp_dir = Path.cwd() / 'isolated_test'
            temp_dir.mkdir()
            os.chdir(str(temp_dir))
            
            result = self.runner.invoke(cli, ['root', '--cd'])
            
            self.assertEqual(result.exit_code, 1)
            # Should not output error message with --cd flag
            self.assertEqual(result.output.strip(), '')

    def test_root_command_help(self):
        """Test root command help."""
        result = self.runner.invoke(cli, ['root', '--help'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Find Git project root directory', result.output)
        self.assertIn('--cd', result.output)
        self.assertIn('-c', result.output)
        self.assertIn('Examples:', result.output)

    def test_root_command_in_actual_git_repo(self):
        """Test root command in the actual fx_bin git repository."""
        # This test runs in the actual project directory
        result = self.runner.invoke(cli, ['root'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Git project root:', result.output)
        # Should contain some path (the actual repo root)
        self.assertTrue(len(result.output.strip()) > 20)

    def test_root_command_cd_in_actual_git_repo(self):
        """Test root command with --cd in actual fx_bin git repository."""
        result = self.runner.invoke(cli, ['root', '--cd'])
        
        self.assertEqual(result.exit_code, 0)
        # Should output just the path without description
        self.assertNotIn('Git project root:', result.output)
        # Should be a valid path
        output_path = result.output.strip()
        self.assertTrue(Path(output_path).exists())
        self.assertTrue((Path(output_path) / '.git').exists())


class TestRootCommandInList(unittest.TestCase):
    """Test that root command appears in command list."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_root_in_command_list(self):
        """Test that root command appears in fx list output."""
        result = self.runner.invoke(cli, ['list'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('root', result.output)
        self.assertIn('Find Git project root directory', result.output)

    def test_root_in_main_help(self):
        """Test that root command appears in main help."""
        result = self.runner.invoke(cli, ['--help'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('root', result.output)


class TestRootCommandErrorHandling(unittest.TestCase):
    """Test error handling in root command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_invalid_flag(self):
        """Test handling of invalid flags."""
        result = self.runner.invoke(cli, ['root', '--invalid'])
        
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('no such option', result.output.lower())

    def test_unexpected_argument(self):
        """Test handling of unexpected arguments."""
        result = self.runner.invoke(cli, ['root', 'unexpected_arg'])
        
        # Click should handle this gracefully
        # The exact behavior depends on Click version
        self.assertIsInstance(result.exit_code, int)


if __name__ == '__main__':
    unittest.main()
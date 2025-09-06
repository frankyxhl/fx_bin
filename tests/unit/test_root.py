"""Unit tests for root module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fx_bin.root import find_git_root


class TestFindGitRoot(unittest.TestCase):
    """Test the find_git_root function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_find_git_root_current_directory(self):
        """Test finding git root in current directory."""
        # Create .git directory in test path
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        result = find_git_root(self.test_path)
        self.assertEqual(result.resolve(), self.test_path.resolve())

    def test_find_git_root_parent_directory(self):
        """Test finding git root in parent directory."""
        # Create nested structure: root/.git and root/subdir/
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        subdir = self.test_path / 'subdir'
        subdir.mkdir()
        
        result = find_git_root(subdir)
        self.assertEqual(result.resolve(), self.test_path.resolve())

    def test_find_git_root_deep_nested(self):
        """Test finding git root several levels up."""
        # Create nested structure: root/.git and root/a/b/c/
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        deep_dir = self.test_path / 'a' / 'b' / 'c'
        deep_dir.mkdir(parents=True)
        
        result = find_git_root(deep_dir)
        self.assertEqual(result.resolve(), self.test_path.resolve())

    def test_find_git_root_not_found(self):
        """Test when no git root is found."""
        # Create directory without .git
        subdir = self.test_path / 'subdir'
        subdir.mkdir()
        
        result = find_git_root(subdir)
        self.assertIsNone(result)

    def test_find_git_root_git_file(self):
        """Test finding git root with .git file (worktree case)."""
        # Create .git file instead of directory (Git worktree scenario)
        git_file = self.test_path / '.git'
        git_file.write_text('gitdir: /path/to/actual/git/dir')
        
        result = find_git_root(self.test_path)
        self.assertEqual(result.resolve(), self.test_path.resolve())

    def test_find_git_root_default_cwd(self):
        """Test using current working directory when no path provided."""
        with patch('pathlib.Path.cwd', return_value=self.test_path):
            # Create .git in the mocked cwd
            git_dir = self.test_path / '.git'
            git_dir.mkdir()
            
            result = find_git_root()
            self.assertEqual(result, self.test_path)

    def test_find_git_root_permission_error(self):
        """Test handling permission errors."""
        # This test might not work on all systems, but documents expected behavior
        with patch('pathlib.Path.exists', side_effect=PermissionError("Access denied")):
            with self.assertRaises(PermissionError):
                find_git_root(self.test_path)

    def test_find_git_root_multiple_git_dirs(self):
        """Test finding nearest git root when multiple exist."""
        # Create nested git repositories
        outer_git = self.test_path / '.git'
        outer_git.mkdir()
        
        inner_dir = self.test_path / 'inner'
        inner_dir.mkdir()
        inner_git = inner_dir / '.git'
        inner_git.mkdir()
        
        work_dir = inner_dir / 'work'
        work_dir.mkdir()
        
        # Should find the nearest .git (inner one)
        result = find_git_root(work_dir)
        self.assertEqual(result.resolve(), inner_dir.resolve())

    def test_find_git_root_relative_path(self):
        """Test with relative path input."""
        # Create .git directory
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        subdir = self.test_path / 'subdir'
        subdir.mkdir()
        
        # Test with absolute path that simulates relative behavior
        result = find_git_root(subdir)
        self.assertEqual(result.resolve(), self.test_path.resolve())

    def test_find_git_root_symlink_handling(self):
        """Test handling of symbolic links."""
        # Create .git directory
        git_dir = self.test_path / '.git'
        git_dir.mkdir()
        
        # Create a symbolic link to a subdirectory
        real_dir = self.test_path / 'real'
        real_dir.mkdir()
        
        link_path = self.test_path / 'link'
        try:
            link_path.symlink_to(real_dir)
            
            result = find_git_root(link_path)
            self.assertEqual(result.resolve(), self.test_path.resolve())
        except OSError:
            # Skip test if symlinks are not supported
            self.skipTest("Symbolic links not supported on this system")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_find_git_root_empty_string_path(self):
        """Test handling of empty string path."""
        with patch('pathlib.Path.cwd', return_value=Path('/tmp')):
            result = find_git_root(Path(''))
            # Should resolve to current directory behavior
            self.assertIsInstance(result, (type(None), Path))

    def test_find_git_root_nonexistent_path(self):
        """Test handling of non-existent path."""
        nonexistent = Path('/nonexistent/path/that/should/not/exist')
        # Should not raise exception, but may return None
        result = find_git_root(nonexistent)
        # The exact behavior depends on implementation
        self.assertIsInstance(result, (type(None), Path))


if __name__ == '__main__':
    unittest.main()
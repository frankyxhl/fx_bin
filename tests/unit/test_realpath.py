"""Unit tests for realpath module."""

import os
import tempfile
import unittest
from pathlib import Path


from fx_bin.realpath import resolve_path


class TestResolvePath(unittest.TestCase):
    """Test the resolve_path function."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_current_directory_resolution(self):
        """Test resolving current directory '.'"""
        test_file = self.test_path / "test.txt"
        test_file.write_text("test")

        os.chdir(str(self.test_path))
        result = resolve_path(".")

        self.assertEqual(result, Path.cwd().resolve())

    def test_relative_path_resolution(self):
        """Test resolving relative path '../foo'"""
        foo_dir = self.test_path / "foo"
        foo_dir.mkdir()

        subdir = self.test_path / "subdir"
        subdir.mkdir()

        os.chdir(str(subdir))
        result = resolve_path("../foo")

        self.assertEqual(result.resolve(), foo_dir.resolve())

    def test_absolute_path_returns_correctly(self):
        """Test that absolute path returns correctly."""
        result = resolve_path(str(self.test_path))

        self.assertEqual(result.resolve(), self.test_path.resolve())

    def test_default_argument_handling(self):
        """Test that default argument '.' is handled correctly."""
        os.chdir(str(self.test_path))
        result = resolve_path(".")

        self.assertEqual(result, Path.cwd().resolve())

    def test_tilde_expansion_to_home_directory(self):
        """Test that ~ expands to home directory."""
        home = Path.home()
        result = resolve_path("~")

        self.assertEqual(result.resolve(), home.resolve())

    def test_symlink_resolution(self):
        """Test that symlinks are resolved to real target."""
        real_file = self.test_path / "real.txt"
        real_file.write_text("real content")

        link_path = self.test_path / "link.txt"
        try:
            link_path.symlink_to(real_file)

            result = resolve_path(str(link_path))

            self.assertEqual(result.resolve(), real_file.resolve())
        except OSError:
            self.skipTest("Symbolic links not supported on this system")

    def test_circular_symlink_raises_oserror(self):
        """Test that circular symlink raises OSError."""
        link_a = self.test_path / "link_a"
        link_b = self.test_path / "link_b"

        try:
            link_a.symlink_to(link_b)
            link_b.symlink_to(link_a)

            with self.assertRaises(OSError):
                resolve_path(str(link_a))
        except OSError as e:
            if "symbolic link" in str(e).lower():
                self.skipTest("Symbolic links not supported on this system")
            raise

    def test_file_not_found_error_for_nonexistent_path(self):
        """Test that FileNotFoundError is raised for non-existent paths."""
        nonexistent = self.test_path / "does_not_exist.txt"

        with self.assertRaises(FileNotFoundError):
            resolve_path(str(nonexistent))

    def test_permission_error_handling(self):
        """Test that PermissionError is raised for inaccessible paths."""
        restricted_dir = self.test_path / "restricted"
        restricted_dir.mkdir()
        inner_file = restricted_dir / "inner.txt"

        try:
            os.chmod(str(restricted_dir), 0o000)

            with self.assertRaises((PermissionError, OSError)):
                resolve_path(str(inner_file))
        finally:
            os.chmod(str(restricted_dir), 0o755)


class TestResolvePathEdgeCases(unittest.TestCase):
    """Test edge cases for resolve_path function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_path_with_multiple_slashes(self):
        """Test path with multiple slashes is normalized."""
        subdir = self.test_path / "subdir"
        subdir.mkdir()

        messy_path = str(self.test_path) + "///subdir///"
        result = resolve_path(messy_path)

        self.assertEqual(result.resolve(), subdir.resolve())

    def test_path_with_dot_components(self):
        """Test path with . and .. components."""
        subdir = self.test_path / "subdir"
        subdir.mkdir()

        messy_path = str(self.test_path) + "/./subdir/../subdir"
        result = resolve_path(messy_path)

        self.assertEqual(result.resolve(), subdir.resolve())

    def test_tilde_with_username(self):
        """Test ~username expansion (if applicable)."""
        import pwd

        try:
            username = pwd.getpwuid(os.getuid()).pw_name
            home_path = Path.home()

            result = resolve_path(f"~{username}")

            self.assertEqual(result.resolve(), home_path.resolve())
        except (KeyError, ImportError, AttributeError):
            self.skipTest("Unable to get current username on this system")

    def test_directory_path(self):
        """Test resolving a directory path."""
        subdir = self.test_path / "mydir"
        subdir.mkdir()

        result = resolve_path(str(subdir))

        self.assertEqual(result.resolve(), subdir.resolve())
        self.assertTrue(result.is_dir())

    def test_file_path(self):
        """Test resolving a file path."""
        test_file = self.test_path / "myfile.txt"
        test_file.write_text("content")

        result = resolve_path(str(test_file))

        self.assertEqual(result.resolve(), test_file.resolve())
        self.assertTrue(result.is_file())


class TestResolvePathReturnType(unittest.TestCase):
    """Test return type of resolve_path function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_returns_path_object(self):
        """Test that resolve_path returns a Path object."""
        result = resolve_path(str(self.test_path))

        self.assertIsInstance(result, Path)

    def test_returns_absolute_path(self):
        """Test that resolve_path returns an absolute path."""
        result = resolve_path(str(self.test_path))

        self.assertTrue(result.is_absolute())


if __name__ == "__main__":
    unittest.main()

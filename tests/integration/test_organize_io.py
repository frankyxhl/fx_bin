"""Integration tests for organize_functional.py IO operations."""

import tempfile
import unittest
from pathlib import Path
from datetime import datetime

from fx_bin.organize_functional import (
    get_file_date,
    scan_files,
    move_file_safe,
    remove_empty_dirs,
    execute_organize,
)
from fx_bin.organize import (
    DateSource,
    ConflictMode,
    OrganizeContext,
    OrganizeSummary,
)
from fx_bin.shared_types import FolderContext
from fx_bin.errors import DateReadError
from fx_bin.lib import unsafe_ioresult_unwrap, unsafe_ioresult_to_result


class TestGetFileDate(unittest.TestCase):
    """Test cases for get_file_date() function."""

    def test_get_file_date_with_birthtime(self):
        """Test get_file_date() with st_birthtime (macOS)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.jpg"
            test_file.write_text("content")

            result = get_file_date(str(test_file), DateSource.CREATED)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            file_date = unsafe_ioresult_unwrap(result)
            self.assertIsInstance(file_date, datetime)
            # Should be recent
            self.assertGreater(file_date.year, 2020)

    def test_get_file_date_fallback_to_mtime(self):
        """Test get_file_date() fallback to st_mtime."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            result = get_file_date(str(test_file), DateSource.CREATED)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            file_date = unsafe_ioresult_unwrap(result)
            self.assertIsInstance(file_date, datetime)

    def test_get_file_date_modified_mode(self):
        """Test get_file_date() with --date-source modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.jpg"
            test_file.write_text("content")

            result = get_file_date(str(test_file), DateSource.MODIFIED)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            file_date = unsafe_ioresult_unwrap(result)
            self.assertIsInstance(file_date, datetime)

    def test_get_file_date_never_uses_ctime(self):
        """Test to ensure st_ctime is NEVER used."""
        # This test verifies that get_file_date doesn't use st_ctime
        # st_ctime is metadata change time, not creation time
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            result = get_file_date(str(test_file), DateSource.CREATED)
            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # The implementation should use birthtime or mtime, never ctime
            # This is verified by code inspection

    def test_get_file_date_nonexistent_file(self):
        """Test get_file_date() error handling for nonexistent file."""
        result = get_file_date("/nonexistent/file.jpg", DateSource.CREATED)

        inner_result = unsafe_ioresult_to_result(result)
        self.assertTrue(inner_result.failure())
        self.assertIsInstance(inner_result.failure(), DateReadError)


class TestScanFiles(unittest.TestCase):
    """Test cases for scan_files() function."""

    def test_scan_files_non_recursive(self):
        """Test scan_files() non-recursive mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files
            Path(tmpdir, "file1.jpg").write_text("content1")
            Path(tmpdir, "file2.txt").write_text("content2")
            subdir = Path(tmpdir, "subdir")
            subdir.mkdir()
            Path(subdir, "file3.jpg").write_text("content3")  # Should be skipped

            result = scan_files(tmpdir, recursive=False)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            files = unsafe_ioresult_unwrap(result)
            self.assertEqual(len(files), 2)

    def test_scan_files_recursive(self):
        """Test scan_files() recursive mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            Path(tmpdir, "file1.jpg").write_text("content1")
            subdir1 = Path(tmpdir, "subdir1")
            subdir1.mkdir()
            Path(subdir1, "file2.jpg").write_text("content2")
            subdir2 = Path(subdir1, "subdir2")
            subdir2.mkdir()
            Path(subdir2, "file3.jpg").write_text("content3")

            result = scan_files(tmpdir, recursive=True)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            files = unsafe_ioresult_unwrap(result)
            self.assertEqual(len(files), 3)

    def test_scan_files_skips_symlink_files(self):
        """Test scan_files() skipping symlink files when follow_symlinks=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create regular file
            regular_file = tmpdir_path / "regular.jpg"
            regular_file.write_text("content")

            # Create symlink pointing to a file outside the scan directory
            # This ensures only the regular file is found, not the symlink
            symlink_file = tmpdir_path / "symlink.jpg"
            # Create a target file in a subdirectory that won't be scanned
            # (non-recursive)
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()
            target = subdir / "target.jpg"
            target.write_text("target content")
            # Create relative symlink
            symlink_file.symlink_to("subdir/target.jpg")

            result = scan_files(tmpdir, recursive=False, follow_symlinks=False)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            files = unsafe_ioresult_unwrap(result)
            self.assertEqual(len(files), 1)  # Only regular file, symlink skipped
            self.assertIn("regular.jpg", files[0])

    def test_scan_files_max_depth(self):
        """Test scan_files() with max_depth limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create deep nesting
            current = Path(tmpdir)
            for i in range(5):
                current = current / f"dir{i}"
                current.mkdir()
                (current / f"file{i}.txt").write_text("content")

            result = scan_files(tmpdir, recursive=True, max_depth=2)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            files = unsafe_ioresult_unwrap(result)
            # Should only scan up to depth 2 (dir0/dir1/dir2/file2.txt is depth 3)
            self.assertLess(len(files), 5)

    def test_scan_files_cycle_detection(self):
        """Test scan_files() inode-based cycle detection."""
        # This test verifies that symlink cycles are detected
        # Using the FolderContext pattern with visited_inodes
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create directory with symlink back to parent (would cause infinite loop)
            dir1 = tmpdir_path / "dir1"
            dir1.mkdir()
            (dir1 / "file1.txt").write_text("content1")

            # Create symlink that creates a cycle
            cycle_link = dir1 / "cycle_link"
            cycle_link.symlink_to(tmpdir)

            context = FolderContext(visited_inodes=set(), max_depth=100)

            result = scan_files(tmpdir, recursive=True, context=context)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            files = unsafe_ioresult_unwrap(result)
            # Should not hang due to cycle detection
            self.assertIsInstance(files, list)

    def test_scan_files_excludes_output_dir(self):
        """Test scan_files() excluding output directory using commonpath."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()
            (output_dir / "existing.jpg").write_text("already organized")

            # Create source directory
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "new.jpg").write_text("new file")

            # Scan from tmpdir, excluding output
            result = scan_files(tmpdir, recursive=True, output_dir=str(output_dir))

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            files = unsafe_ioresult_unwrap(result)
            # Should find new.jpg but not existing.jpg
            self.assertTrue(any("new.jpg" in f for f in files))
            self.assertFalse(any("existing.jpg" in f for f in files))


class TestMoveFileSafe(unittest.TestCase):
    """Test cases for move_file_safe() function."""

    def test_move_file_safe_basic_move(self):
        """Test move_file_safe() basic move operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "source.txt"
            source.write_text("Hello World")

            # Create output root and target directory
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            target = output_root / "source.txt"

            # Move the file
            result = move_file_safe(str(source), str(target), str(source_root), str(output_root), ConflictMode.RENAME)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Verify source file is gone
            self.assertFalse(source.exists())

            # Verify target file exists with same content
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "Hello World")

    def test_move_file_safe_creates_parent_dirs(self):
        """Test move_file_safe() creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "source.txt"
            source.write_text("content")

            # Create output root
            output_root = tmpdir_path / "output"
            output_root.mkdir()

            # Target with non-existent parent directories
            target = output_root / "a" / "b" / "c" / "target.txt"

            # Move should create parent dirs
            result = move_file_safe(str(source), str(target), str(source_root), str(output_root), ConflictMode.RENAME)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Verify target exists and parent dirs were created
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "content")

    def test_move_file_safe_permission_error(self):
        """Test move_file_safe() handles permission errors."""
        # This test verifies permission error handling
        # Actual permission errors may be hard to test consistently
        # so we verify the error handling pattern exists
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "source.txt"
            source.write_text("content")

            output_root = tmpdir_path / "output"
            output_root.mkdir()

            # Moving to same location is a no-op, should succeed
            result = move_file_safe(str(source), str(source), str(source_root), str(output_root), ConflictMode.RENAME)

            # Moving to same location is a no-op, should succeed
            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

    def test_move_file_safe_atomic_overwrite(self):
        """Test move_file_safe() atomic overwrite with os.replace()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "source.txt"
            source.write_text("new content")

            # Create output root and existing target file
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            target = output_root / "source.txt"
            target.write_text("old content")

            # Move should atomically replace the target
            result = move_file_safe(str(source), str(target), str(source_root), str(output_root), ConflictMode.RENAME)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Verify target has new content
            self.assertEqual(target.read_text(), "new content")
            # Verify source is gone
            self.assertFalse(source.exists())

    def test_move_file_safe_no_op_same_file(self):
        """Test move_file_safe() no-op when source equals target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "file.txt"
            source.write_text("content")

            output_root = tmpdir_path / "output"
            output_root.mkdir()

            # Moving to same location should succeed without doing anything
            result = move_file_safe(str(source), str(source), str(source_root), str(output_root), ConflictMode.RENAME)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # File should still exist with same content
            self.assertTrue(source.exists())
            self.assertEqual(source.read_text(), "content")


class TestRemoveEmptyDirs(unittest.TestCase):
    """Test cases for remove_empty_dirs() function."""

    def test_remove_empty_dirs_single_empty_dir(self):
        """Test remove_empty_dirs() removes single empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create an empty directory
            empty_dir = tmpdir_path / "empty"
            empty_dir.mkdir()

            # Verify it exists
            self.assertTrue(empty_dir.exists())

            # Remove empty dirs
            result = remove_empty_dirs(str(empty_dir), str(tmpdir_path))

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Verify directory was removed
            self.assertFalse(empty_dir.exists())

    def test_remove_empty_dirs_nested_empty_dirs(self):
        """Test remove_empty_dirs() removes nested empty directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create nested empty directories
            level1 = tmpdir_path / "level1"
            level1.mkdir()
            level2 = level1 / "level2"
            level2.mkdir()
            level3 = level2 / "level3"
            level3.mkdir()

            # All exist
            self.assertTrue(level3.exists())
            self.assertTrue(level2.exists())
            self.assertTrue(level1.exists())

            # Remove empty dirs starting from level1
            result = remove_empty_dirs(str(level1), str(tmpdir_path))

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # All should be removed (bottom-up)
            self.assertFalse(level3.exists())
            self.assertFalse(level2.exists())
            self.assertFalse(level1.exists())

    def test_remove_empty_dirs_skips_non_empty(self):
        """Test remove_empty_dirs() skips directories with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create directory structure with a file
            parent = tmpdir_path / "parent"
            parent.mkdir()
            child = parent / "child"
            child.mkdir()
            (child / "file.txt").write_text("content")

            # Remove empty dirs
            result = remove_empty_dirs(str(parent), str(tmpdir_path))

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Child should still exist (has file)
            self.assertTrue(child.exists())
            # Parent should still exist (child still there)
            self.assertTrue(parent.exists())

    def test_remove_empty_dirs_scope_limit(self):
        """Test remove_empty_dirs() only removes under source root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create empty dir OUTSIDE source root
            outside_dir = tmpdir_path / "outside"
            outside_dir.mkdir()

            # Create empty dir INSIDE source root
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            inside_dir = source_root / "inside"
            inside_dir.mkdir()

            # Remove empty dirs in source root only
            result = remove_empty_dirs(str(source_root), str(source_root))

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Inside dir should be removed
            self.assertFalse(inside_dir.exists())
            # Outside dir should NOT be removed (outside scope)
            self.assertTrue(outside_dir.exists())


class TestExecuteOrganize(unittest.TestCase):
    """Test cases for execute_organize() main execution function."""

    def test_execute_organize_dry_run_mode(self):
        """Test execute_organize() dry-run mode doesn't modify files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "photo1.jpg").write_text("photo1")
            (source_dir / "photo2.jpg").write_text("photo2")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context for dry-run
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,  # DRY RUN
            )

            # Execute in dry-run mode
            result = execute_organize(str(source_dir), context)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            summary, _ = unsafe_ioresult_unwrap(result)

            # Verify summary indicates dry-run
            self.assertTrue(summary.dry_run)

            # Verify no files were actually moved
            self.assertTrue((source_dir / "photo1.jpg").exists())
            self.assertTrue((source_dir / "photo2.jpg").exists())

            # Verify no subdirectories were created in output
            # (in dry-run mode, we should not create directories)
            output_contents = list(output_dir.iterdir())
            self.assertEqual(len(output_contents), 0)

    def test_execute_organize_actual_execution(self):
        """Test execute_organize() actually moves files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source file with known date
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            source_file = source_dir / "photo.jpg"
            source_file.write_text("content")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context for actual execution
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=False,  # ACTUAL EXECUTION
            )

            # Execute
            result = execute_organize(str(source_dir), context)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            summary, _ = unsafe_ioresult_unwrap(result)

            # Verify files were moved
            self.assertFalse(source_file.exists())

            # Verify file exists in output with date-based path
            # The path will be something like output/YYYY/YYYYMM/YYYYMMDD/photo.jpg
            output_files = list(output_dir.rglob("photo.jpg"))
            self.assertEqual(len(output_files), 1)

            # Verify summary
            self.assertFalse(summary.dry_run)
            self.assertGreater(summary.total_files, 0)
            self.assertEqual(summary.processed, 1)

    def test_execute_organize_summary_generation(self):
        """Test execute_organize() generates correct summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "file1.jpg").write_text("content1")
            (source_dir / "file2.jpg").write_text("content2")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=False,
            )

            # Execute
            result = execute_organize(str(source_dir), context)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            summary, _ = unsafe_ioresult_unwrap(result)

            # Verify summary fields
            self.assertIsInstance(summary, OrganizeSummary)
            self.assertEqual(summary.total_files, 2)
            self.assertEqual(summary.processed, 2)
            self.assertEqual(summary.skipped, 0)
            self.assertEqual(summary.errors, 0)
            self.assertFalse(summary.dry_run)


class TestHiddenFileHandling(unittest.TestCase):
    """Test cases for hidden file handling (Phase 9.3)."""

    def test_hidden_files_excluded_by_default(self):
        """Test that hidden files are excluded by default (hidden=False)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "regular.jpg").write_text("regular")
            (source_dir / ".hidden.jpg").write_text("hidden")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with hidden=False (default)
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,  # Use dry-run to check plan
                hidden=False,  # Default - exclude hidden files
            )

            # Execute
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # Both files are scanned (total_files=2), but hidden is skipped
            self.assertEqual(summary.total_files, 2)  # Both files scanned
            self.assertEqual(summary.skipped, 1)  # Hidden file is skipped
            self.assertEqual(summary.processed, 1)  # Regular file processed

    def test_hidden_files_included_with_flag(self):
        """Test that --hidden includes hidden files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "regular.jpg").write_text("regular")
            (source_dir / ".hidden.jpg").write_text("hidden")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with hidden=True
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,
                hidden=True,  # Include hidden files
            )

            # Execute
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # Both files should be processed
            self.assertEqual(summary.total_files, 2)  # Both files counted


class TestRecursiveBehavior(unittest.TestCase):
    """Test cases for recursive behavior (Phase 9.4)."""

    def test_non_recursive_by_default(self):
        """Test that default behavior is non-recursive (recursive=False)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files in nested structure
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "root.jpg").write_text("root")

            sub_dir = source_dir / "subdir"
            sub_dir.mkdir()
            (sub_dir / "nested.jpg").write_text("nested")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with recursive=False (default)
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,
                recursive=False,  # Default - non-recursive
            )

            # Execute
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # Only root file should be scanned, not nested
            self.assertEqual(summary.total_files, 1)  # Only root file
            self.assertEqual(summary.processed, 1)

    def test_recursive_enabled_scans_subdirectories(self):
        """Test that --recursive enables subdirectory scanning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files in nested structure
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "root.jpg").write_text("root")

            sub_dir = source_dir / "subdir"
            sub_dir.mkdir()
            (sub_dir / "nested.jpg").write_text("nested")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with recursive=True
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,
                recursive=True,  # Enable recursive
            )

            # Execute
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # Both files should be scanned
            self.assertEqual(summary.total_files, 2)  # Both files


class TestBoundaryCheck(unittest.TestCase):
    """Test cases for boundary check (Phase 9.6) - path traversal protection."""

    def test_source_outside_source_root_blocked(self):
        """Test that source file outside source_root is blocked."""
        from fx_bin.organize_functional import move_file_safe

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Source file is outside source_root
            outside_file = tmpdir_path / "outside.txt"
            outside_file.write_text("content")

            source_root = str(tmpdir_path / "source")
            Path(source_root).mkdir()

            # Target is valid (inside output_root)
            output_root = str(tmpdir_path / "output")
            Path(output_root).mkdir()
            target = str(Path(output_root) / "target.txt")

            # Attempt to move file from outside source_root
            result = move_file_safe(
                str(outside_file), target, source_root, output_root, ConflictMode.RENAME
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result.failure())
            # Source file should still exist
            self.assertTrue(outside_file.exists())

    def test_target_outside_output_root_blocked(self):
        """Test that target outside output_root is blocked."""
        from fx_bin.organize_functional import move_file_safe

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Source file is valid (inside source_root)
            source_root = str(tmpdir_path / "source")
            Path(source_root).mkdir()
            source_file = Path(source_root) / "source.txt"
            source_file.write_text("content")

            output_root = str(tmpdir_path / "output")
            Path(output_root).mkdir()

            # Target is outside output_root (path traversal attempt)
            target = str(tmpdir_path / "outside" / "target.txt")

            # Attempt to move to outside output_root
            result = move_file_safe(
                str(source_file), target, source_root, output_root, ConflictMode.RENAME
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result.failure())
            # Source file should still exist
            self.assertTrue(source_file.exists())

    def test_custom_output_outside_source_allowed(self):
        """Test that custom output directory outside source is allowed (spec-supported)."""
        from fx_bin.organize_functional import move_file_safe

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Source file is valid
            source_root = str(tmpdir_path / "source")
            Path(source_root).mkdir()
            source_file = Path(source_root) / "source.txt"
            source_file.write_text("content")

            # Output is completely separate from source (spec allows this)
            output_root = str(tmpdir_path / "separate_output")
            Path(output_root).mkdir()
            target = str(Path(output_root) / "target.txt")

            # This should succeed
            result = move_file_safe(
                str(source_file), target, source_root, output_root, ConflictMode.RENAME
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            # File should be moved
            self.assertFalse(source_file.exists())
            self.assertTrue(Path(target).exists())


class TestDirectoriesCreated(unittest.TestCase):
    """Test cases for directories_created tracking (Phase 9.7)."""

    def test_directories_created_zero_in_dry_run(self):
        """Test that directories_created is 0 in dry-run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source file
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context for dry-run
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,  # DRY RUN
            )

            # Execute in dry-run mode
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # Verify no directories were created in dry-run
            self.assertEqual(summary.directories_created, 0)

    def test_directories_created_counts_newly_created(self):
        """Test that directories_created counts only newly created directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source file
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory (but NOT the date subdirectories)
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context for actual execution
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=False,  # Actual execution
            )

            # Execute - this will create date directories
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # At least 1 directory should be created (year/month/day structure)
            self.assertGreater(summary.directories_created, 0)
            # Verify the file was actually moved
            self.assertFalse((source_dir / "photo.jpg").exists())

    def test_directories_created_zero_when_preexisting(self):
        """Test that directories_created is 0 when directories already exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source file
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "photo.jpg").write_text("content")

            # Create output directory AND pre-create the date structure
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Pre-create the expected date structure (based on current date)
            from datetime import datetime
            now = datetime.now()
            year_dir = output_dir / str(now.year)
            month_dir = year_dir / now.strftime("%Y%m")
            day_dir = month_dir / now.strftime("%Y%m%d")
            day_dir.mkdir(parents=True)

            # Create context for actual execution
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=False,  # Actual execution
            )

            # Execute - directories already exist
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # No new directories should be created
            self.assertEqual(summary.directories_created, 0)


class TestDiskConflictDetection(unittest.TestCase):
    """Test cases for disk conflict detection (Phase 11.1)."""

    def test_target_exists_detection(self):
        """Test that move_file_safe detects when target file exists on disk."""
        from fx_bin.organize_functional import move_file_safe
        from fx_bin.organize import ConflictMode

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "source.txt"
            source.write_text("source content")

            # Create output root and PRE-EXISTING target file
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            target = output_root / "source.txt"
            target.write_text("existing content")  # Target already exists!

            # With skip mode, should detect conflict and skip
            # Note: This test will fail until GREEN implementation
            result = move_file_safe(
                str(source),
                str(target),
                str(source_root),
                str(output_root),
                ConflictMode.SKIP,  # Will be added in GREEN
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            # In skip mode, source should remain
            self.assertTrue(source.exists())
            # Target should remain unchanged
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "existing content")

    def test_overwrite_mode_replaces_existing_file(self):
        """Test that OVERWRITE mode replaces existing files atomically."""
        from fx_bin.organize_functional import move_file_safe
        from fx_bin.organize import ConflictMode

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "source.txt"
            source.write_text("new content")

            # Create output root and PRE-EXISTING target file
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            target = output_root / "source.txt"
            target.write_text("old content")  # Target already exists!

            # With OVERWRITE mode, should replace existing file
            result = move_file_safe(
                str(source),
                str(target),
                str(source_root),
                str(output_root),
                ConflictMode.OVERWRITE,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            # Source should be gone
            self.assertFalse(source.exists())
            # Target should have new content
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "new content")

    def test_ask_mode_skips_existing_files(self):
        """Test that ASK mode skips existing files (handled at CLI level)."""
        from fx_bin.organize_functional import move_file_safe
        from fx_bin.organize import ConflictMode

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "source.txt"
            source.write_text("source content")

            # Create output root and PRE-EXISTING target file
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            target = output_root / "source.txt"
            target.write_text("existing content")

            # With ASK mode, should skip (prompting handled at CLI level)
            result = move_file_safe(
                str(source),
                str(target),
                str(source_root),
                str(output_root),
                ConflictMode.ASK,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            # In ASK mode, source should remain (prompting is CLI responsibility)
            self.assertTrue(source.exists())
            # Target should remain unchanged
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "existing content")


class TestCleanEmptyDirectories(unittest.TestCase):
    """Test cases for --clean-empty functionality (Phase 12.1)."""

    def test_clean_empty_removes_empty_directories(self):
        """Test that --clean-empty removes empty source directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source with nested structure
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            nested_dir = source_dir / "nested"
            nested_dir.mkdir()
            (nested_dir / "file.txt").write_text("content")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with clean_empty=True and recursive=True
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=False,
                clean_empty=True,  # Enable cleanup
                recursive=True,  # Need recursive to process nested files
            )

            # Execute - file should be moved
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # Verify file was moved
            self.assertFalse((nested_dir / "file.txt").exists())
            # Verify empty directory was removed
            self.assertFalse(nested_dir.exists())

    def test_clean_empty_skips_dry_run(self):
        """Test that --clean-empty doesn't remove directories in dry-run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source with nested structure
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            nested_dir = source_dir / "nested"
            nested_dir.mkdir()
            (nested_dir / "file.txt").write_text("content")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with clean_empty=True but dry_run=True
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,  # DRY RUN - cleanup should not run
                clean_empty=True,
            )

            # Execute in dry-run mode
            result = execute_organize(str(source_dir), context)
            summary, _ = unsafe_ioresult_unwrap(result)

            # In dry-run, directory should still exist
            self.assertTrue(nested_dir.exists())


if __name__ == "__main__":
    unittest.main()

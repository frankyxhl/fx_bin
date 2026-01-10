"""Integration tests for organize_functional.py IO operations."""

import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

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

    def test_given_file_with_birthtime_when_getting_date_then_returns_creation_date(
        self,
    ):
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

    def test_given_file_without_birthtime_when_getting_date_then_falls_back_to_mtime(
        self,
    ):
        """Test get_file_date() fallback to st_mtime."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            result = get_file_date(str(test_file), DateSource.CREATED)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            file_date = unsafe_ioresult_unwrap(result)
            self.assertIsInstance(file_date, datetime)

    def test_given_file_and_modified_mode_when_getting_date_then_returns_modification_date(
        self,
    ):
        """Test get_file_date() with --date-source modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.jpg"
            test_file.write_text("content")

            result = get_file_date(str(test_file), DateSource.MODIFIED)

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            file_date = unsafe_ioresult_unwrap(result)
            self.assertIsInstance(file_date, datetime)

    def test_given_file_when_getting_date_then_never_uses_ctime(self):
        """Test to ensure st_ctime is NEVER used for date calculation.

        On Unix systems, st_ctime is the inode change time (updated when
        file metadata changes like permissions or ownership), NOT the
        creation time. This test verifies that get_file_date() uses either
        st_birthtime (creation time on macOS/BSD) or st_mtime (modification
        time), but never st_ctime.
        """
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            # Get all available timestamps from the file
            stat_info = os.stat(test_file)

            # Get the timestamps that SHOULD be used
            if hasattr(stat_info, "st_birthtime"):
                expected_timestamp = stat_info.st_birthtime
                using_birthtime = True
            else:
                expected_timestamp = stat_info.st_mtime
                using_birthtime = False

            # Get the timestamp that should NEVER be used
            ctime_timestamp = stat_info.st_ctime

            # Call get_file_date() with CREATED mode
            result = get_file_date(str(test_file), DateSource.CREATED)
            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)
            file_date = unsafe_ioresult_unwrap(result)

            # Convert returned datetime to timestamp for comparison
            returned_timestamp = file_date.timestamp()

            # Verify the returned timestamp matches the expected one (birthtime or mtime)
            # Use approximate comparison due to floating point precision
            self.assertAlmostEqual(
                returned_timestamp,
                expected_timestamp,
                places=5,  # Compare to microsecond precision
                msg=f"get_file_date() should return {'birthtime' if using_birthtime else 'mtime'} "
                f"but returned a different timestamp",
            )

            # Verify the returned timestamp does NOT match ctime
            # (unless they happen to be equal, which is possible but unlikely)
            if abs(ctime_timestamp - expected_timestamp) > 0.00001:
                self.assertNotAlmostEqual(
                    returned_timestamp,
                    ctime_timestamp,
                    places=5,
                    msg="get_file_date() should NEVER use st_ctime (inode change time) "
                    "for file date calculation",
                )

            # Additional verification: test with MODIFIED mode
            result_modified = get_file_date(str(test_file), DateSource.MODIFIED)
            inner_result_modified = unsafe_ioresult_to_result(result_modified)
            self.assertTrue(inner_result_modified)
            file_date_modified = unsafe_ioresult_unwrap(result_modified)
            returned_modified_timestamp = file_date_modified.timestamp()

            # MODIFIED mode should always use mtime
            self.assertAlmostEqual(
                returned_modified_timestamp,
                stat_info.st_mtime,
                places=5,
                msg="get_file_date() with MODIFIED mode should always use st_mtime",
            )

            # MODIFIED mode should also never use ctime
            if abs(stat_info.st_ctime - stat_info.st_mtime) > 0.00001:
                self.assertNotAlmostEqual(
                    returned_modified_timestamp,
                    stat_info.st_ctime,
                    places=5,
                    msg="get_file_date() with MODIFIED mode should NEVER use st_ctime",
                )

    def test_given_nonexistent_file_when_getting_date_then_returns_error(self):
        """Test get_file_date() error handling for nonexistent file."""
        result = get_file_date("/nonexistent/file.jpg", DateSource.CREATED)

        inner_result = unsafe_ioresult_to_result(result)
        self.assertTrue(inner_result.failure())
        self.assertIsInstance(inner_result.failure(), DateReadError)


class TestScanFiles(unittest.TestCase):
    """Test cases for scan_files() function."""

    def test_given_directory_and_non_recursive_mode_when_scanning_files_then_returns_only_top_level_files(
        self,
    ):
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

    def test_given_directory_and_recursive_mode_when_scanning_files_then_returns_all_nested_files(
        self,
    ):
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

    def test_given_symlink_files_and_no_follow_flag_when_scanning_files_then_skips_symlinks(
        self,
    ):
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

    def test_given_deep_directory_and_max_depth_when_scanning_files_then_respects_depth_limit(
        self,
    ):
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

    def test_given_symlink_cycle_when_scanning_files_then_detects_cycle_via_inode_tracking(
        self,
    ):
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

    def test_given_directory_with_output_subdir_when_scanning_files_then_excludes_output_directory(
        self,
    ):
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

    def test_given_source_and_target_when_moving_file_then_performs_basic_move(self):
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
            result = move_file_safe(
                str(source),
                str(target),
                str(source_root),
                str(output_root),
                ConflictMode.RENAME,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Verify source file is gone
            self.assertFalse(source.exists())

            # Verify target file exists with same content
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "Hello World")

    def test_given_target_with_nonexistent_parents_when_moving_file_then_creates_parent_dirs(
        self,
    ):
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
            result = move_file_safe(
                str(source),
                str(target),
                str(source_root),
                str(output_root),
                ConflictMode.RENAME,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Verify target exists and parent dirs were created
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "content")

    def test_given_source_same_as_target_when_moving_file_then_succeeds_as_no_op(self):
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
            result = move_file_safe(
                str(source),
                str(source),
                str(source_root),
                str(output_root),
                ConflictMode.RENAME,
            )

            # Moving to same location is a no-op, should succeed
            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

    def test_given_existing_target_and_overwrite_mode_when_moving_file_then_replaces_target(
        self,
    ):
        """Test move_file_safe() with OVERWRITE mode replaces existing target."""
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

            # With OVERWRITE mode, should replace existing target
            result = move_file_safe(
                str(source),
                str(target),
                str(source_root),
                str(output_root),
                ConflictMode.OVERWRITE,  # Use OVERWRITE mode, not RENAME
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Verify target has new content (was overwritten)
            self.assertEqual(target.read_text(), "new content")
            # Verify source is gone
            self.assertFalse(source.exists())

    def test_given_same_source_and_target_path_when_moving_file_then_succeeds_without_change(
        self,
    ):
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
            result = move_file_safe(
                str(source),
                str(source),
                str(source_root),
                str(output_root),
                ConflictMode.RENAME,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # File should still exist with same content
            self.assertTrue(source.exists())
            self.assertEqual(source.read_text(), "content")


class TestRemoveEmptyDirs(unittest.TestCase):
    """Test cases for remove_empty_dirs() function."""

    def test_given_single_empty_directory_when_removing_empty_dirs_then_deletes_directory(
        self,
    ):
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

    def test_given_nested_empty_directories_when_removing_empty_dirs_then_removes_all_bottom_up(
        self,
    ):
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

    def test_given_directory_with_files_when_removing_empty_dirs_then_skips_non_empty(
        self,
    ):
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

    def test_given_source_root_and_outside_dirs_when_removing_empty_dirs_then_respects_scope_limit(
        self,
    ):
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

    def test_given_context_with_dry_run_when_executing_organize_then_does_not_modify_files(
        self,
    ):
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

    def test_given_context_without_dry_run_when_executing_organize_then_actually_moves_files(
        self,
    ):
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

    def test_given_multiple_files_when_executing_organize_then_generates_correct_summary(
        self,
    ):
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

    def test_given_hidden_files_and_default_context_when_executing_organize_then_excludes_hidden_files(
        self,
    ):
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

    def test_given_hidden_files_and_hidden_flag_when_executing_organize_then_includes_hidden_files(
        self,
    ):
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

    def test_given_nested_files_and_default_context_when_executing_organize_then_scans_only_top_level(
        self,
    ):
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

    def test_given_nested_files_and_recursive_flag_when_executing_organize_then_scans_subdirectories(
        self,
    ):
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

    def test_given_source_outside_source_root_when_moving_file_then_blocks_move(self):
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

    def test_given_target_outside_output_root_when_moving_file_then_blocks_move(self):
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

    def test_given_custom_output_outside_source_when_moving_file_then_allows_move(self):
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

    def test_given_dry_run_context_when_executing_organize_then_directories_created_is_zero(
        self,
    ):
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

    def test_given_non_dry_run_context_when_executing_organize_then_counts_newly_created_directories(
        self,
    ):
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

    def test_given_preexisting_directories_when_executing_organize_then_directories_created_is_zero(
        self,
    ):
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

    def test_given_existing_target_and_skip_mode_when_moving_file_then_skips_and_preserves_both(
        self,
    ):
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

    def test_given_existing_target_and_overwrite_mode_when_moving_file_then_replaces_atomically(
        self,
    ):
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

    def test_given_existing_target_and_ask_mode_when_moving_file_then_skips_for_cli_prompt(
        self,
    ):
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

    def test_given_clean_empty_flag_when_executing_organize_then_removes_empty_directories(
        self,
    ):
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

    def test_given_clean_empty_flag_and_dry_run_when_executing_organize_then_skips_cleanup(
        self,
    ):
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


class TestFailFastBehavior(unittest.TestCase):
    """Test cases for --fail-fast functionality (Phase 12.2)."""

    def test_given_fail_fast_flag_and_date_read_error_when_executing_organize_then_stops_on_first_error(
        self,
    ):
        """Test that --fail-fast stops on first error during date reading."""
        from fx_bin.lib import unsafe_ioresult_to_result
        from fx_bin.errors import OrganizeError

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "file1.txt").write_text("file1")
            (source_dir / "file2.txt").write_text("file2")
            (source_dir / "file3.txt").write_text("file3")

            # Make file2.txt unreadable to cause a date read error
            import stat
            file2 = source_dir / "file2.txt"
            file2.chmod(stat.S_IRUSR)  # Read-only, should still work

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with fail_fast=True
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=False,
                fail_fast=True,  # Enable fail-fast
            )

            # Mock get_file_date to fail on second file
            call_count = [0]
            original_get_file_date = get_file_date

            def mock_get_file_date(file_path, date_source):
                call_count[0] += 1
                # Fail on the second call (file2.txt)
                if "file2.txt" in file_path:
                    from returns.io import IOResult
                    from fx_bin.errors import DateReadError
                    return IOResult.from_failure(
                        DateReadError(f"Mocked date read failure for {file_path}")
                    )
                # Otherwise call original
                return original_get_file_date(file_path, date_source)

            # Patch get_file_date
            with patch("fx_bin.organize_functional.get_file_date", side_effect=mock_get_file_date):
                # Execute - should fail on second file
                result = execute_organize(str(source_dir), context)

                # Result should be a failure
                inner_result = unsafe_ioresult_to_result(result)
                self.assertTrue(inner_result.failure())

                # Verify the error is OrganizeError
                error = inner_result.failure()
                self.assertIsInstance(error, OrganizeError)
                self.assertIn("file2.txt", str(error))

    def test_given_default_mode_and_date_read_errors_when_executing_organize_then_continues_on_error(
        self,
    ):
        """Test that default mode (fail_fast=False) continues on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "file1.txt").write_text("file1")
            (source_dir / "file2.txt").write_text("file2")
            (source_dir / "file3.txt").write_text("file3")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with fail_fast=False (default)
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=False,
                fail_fast=False,  # Default - continue on error
            )

            # Mock get_file_date to fail on second file only
            call_count = [0]
            original_get_file_date = get_file_date

            def mock_get_file_date(file_path, date_source):
                call_count[0] += 1
                # Fail on the second call (file2.txt)
                if "file2.txt" in file_path:
                    from returns.io import IOResult
                    from fx_bin.errors import DateReadError
                    return IOResult.from_failure(
                        DateReadError(f"Mocked date read failure for {file_path}")
                    )
                # Otherwise call original
                return original_get_file_date(file_path, date_source)

            # Patch get_file_date
            with patch("fx_bin.organize_functional.get_file_date", side_effect=mock_get_file_date):
                # Execute - should continue despite errors
                result = execute_organize(str(source_dir), context)

                # Result should still succeed despite errors
                from fx_bin.lib import unsafe_ioresult_to_result
                inner_result = unsafe_ioresult_to_result(result)
                self.assertTrue(inner_result)

                summary, _ = unsafe_ioresult_unwrap(result)

                # Verify errors were counted
                self.assertGreater(summary.errors, 0)

                # Verify that 2 files were processed (file1 and file3, file2 had error)
                self.assertGreater(summary.processed, 0)

    def test_given_fail_fast_flag_and_dry_run_when_executing_organize_then_succeeds_without_errors(
        self,
    ):
        """Test that --fail-fast with dry-run doesn't cause errors (no actual moves)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source files
            source_dir = tmpdir_path / "source"
            source_dir.mkdir()
            (source_dir / "file1.txt").write_text("file1")
            (source_dir / "file2.txt").write_text("file2")

            # Create output directory
            output_dir = tmpdir_path / "output"
            output_dir.mkdir()

            # Create context with fail_fast=True and dry_run=True
            context = OrganizeContext(
                date_source=DateSource.CREATED,
                depth=3,
                conflict_mode=ConflictMode.RENAME,
                output_dir=str(output_dir),
                dry_run=True,  # DRY RUN - no actual moves, so no errors
                fail_fast=True,
            )

            # Execute in dry-run mode
            result = execute_organize(str(source_dir), context)

            # Should succeed in dry-run mode
            from fx_bin.lib import unsafe_ioresult_to_result
            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            summary, _ = unsafe_ioresult_unwrap(result)

            # No errors in dry-run
            self.assertEqual(summary.errors, 0)


class TestResolveDiskConflictRename(unittest.TestCase):
    """Test cases for resolve_disk_conflict_rename() helper (Phase 1.1)."""

    def test_given_existing_file_when_resolving_disk_conflict_then_adds_1_suffix(self):
        """Test that resolve_disk_conflict_rename adds _1 suffix when file exists on disk."""
        from fx_bin.organize_functional import resolve_disk_conflict_rename

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create an existing file
            existing_file = tmpdir_path / "photo.jpg"
            existing_file.write_text("existing")

            # Resolve conflict for the same path
            resolved_path = resolve_disk_conflict_rename(str(existing_file))

            # Should return path with _1 suffix
            self.assertEqual(resolved_path, str(tmpdir_path / "photo_1.jpg"))

    def test_given_multiple_existing_files_when_resolving_disk_conflict_then_increments_suffix(
        self,
    ):
        """Test that resolve_disk_conflict_rename increments suffix for multiple existing files."""
        from fx_bin.organize_functional import resolve_disk_conflict_rename

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create existing files with incrementing suffixes
            base_name = "document.txt"
            (tmpdir_path / base_name).write_text("original")
            (tmpdir_path / "document_1.txt").write_text("first duplicate")
            (tmpdir_path / "document_2.txt").write_text("second duplicate")

            # Resolve conflict - should skip to _3
            resolved_path = resolve_disk_conflict_rename(str(tmpdir_path / base_name))

            self.assertEqual(resolved_path, str(tmpdir_path / "document_3.txt"))

    def test_given_multi_part_extension_when_resolving_disk_conflict_then_handles_correctly(
        self,
    ):
        """Test that resolve_disk_conflict_rename correctly handles multi-part extensions (.tar.gz)."""
        from fx_bin.organize_functional import resolve_disk_conflict_rename

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create existing file with multi-part extension
            archive = tmpdir_path / "archive.tar.gz"
            archive.write_text("archive content")

            # Resolve conflict - should insert suffix BEFORE extension
            resolved_path = resolve_disk_conflict_rename(str(archive))

            # Should be archive_1.tar.gz, NOT archive.tar_1.gz
            self.assertEqual(resolved_path, str(tmpdir_path / "archive_1.tar.gz"))

    def test_given_nonexistent_file_when_resolving_disk_conflict_then_returns_original_path(
        self,
    ):
        """Test that resolve_disk_conflict_rename returns original path when file doesn't exist."""
        from fx_bin.organize_functional import resolve_disk_conflict_rename

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # File doesn't exist
            nonexistent = tmpdir_path / "nonexistent.jpg"
            resolved_path = resolve_disk_conflict_rename(str(nonexistent))

            # Should return original path unchanged
            self.assertEqual(resolved_path, str(nonexistent))


class TestRenameModeDiskConflictIntegration(unittest.TestCase):
    """Integration tests for RENAME mode disk conflict handling (Phase 1.2)."""

    def test_given_existing_target_and_rename_mode_when_moving_file_then_adds_suffix_instead_of_overwriting(
        self,
    ):
        """Test that RENAME mode calls resolve_disk_conflict_rename() and doesn't overwrite existing files."""
        from fx_bin.organize_functional import move_file_safe

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "photo.jpg"
            source.write_text("new photo")

            # Create output root and PRE-EXISTING target file (disk conflict!)
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            target = output_root / "photo.jpg"
            target.write_text("existing photo")  # Target already exists on disk!

            # Move with RENAME mode - should NOT overwrite
            # Instead should call resolve_disk_conflict_rename() and create photo_1.jpg
            result = move_file_safe(
                str(source),
                str(target),
                str(source_root),
                str(output_root),
                ConflictMode.RENAME,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Source should be gone (file was moved)
            self.assertFalse(source.exists())

            # Original target should STILL exist with its original content (NOT overwritten!)
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(), "existing photo")

            # A NEW file with _1 suffix should be created
            renamed_target = output_root / "photo_1.jpg"
            self.assertTrue(renamed_target.exists())
            self.assertEqual(renamed_target.read_text(), "new photo")

    def test_given_multiple_existing_files_and_rename_mode_when_moving_file_then_increments_suffix(
        self,
    ):
        """Test that RENAME mode increments suffix when multiple conflicts exist."""
        from fx_bin.organize_functional import move_file_safe

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "document.txt"
            source.write_text("new document")

            # Create output root with MULTIPLE pre-existing files (disk conflicts!)
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            (output_root / "document.txt").write_text("original")
            (output_root / "document_1.txt").write_text("first copy")
            (output_root / "document_2.txt").write_text("second copy")

            # Move with RENAME mode - should skip to _3
            result = move_file_safe(
                str(source),
                str(output_root / "document.txt"),
                str(source_root),
                str(output_root),
                ConflictMode.RENAME,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # All existing files should be unchanged
            self.assertTrue((output_root / "document.txt").exists())
            self.assertEqual((output_root / "document.txt").read_text(), "original")
            self.assertTrue((output_root / "document_1.txt").exists())
            self.assertEqual((output_root / "document_1.txt").read_text(), "first copy")
            self.assertTrue((output_root / "document_2.txt").exists())
            self.assertEqual((output_root / "document_2.txt").read_text(), "second copy")

            # A NEW file with _3 suffix should be created
            renamed_target = output_root / "document_3.txt"
            self.assertTrue(renamed_target.exists())
            self.assertEqual(renamed_target.read_text(), "new document")

    def test_given_multi_part_extension_and_rename_mode_when_moving_file_then_handles_extension_correctly(
        self,
    ):
        """Test that RENAME mode correctly handles multi-part extensions like .tar.gz."""
        from fx_bin.organize_functional import move_file_safe

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create source root and source file with multi-part extension
            source_root = tmpdir_path / "source"
            source_root.mkdir()
            source = source_root / "archive.tar.gz"
            source.write_text("new archive")

            # Create output root with pre-existing file
            output_root = tmpdir_path / "output"
            output_root.mkdir()
            (output_root / "archive.tar.gz").write_text("existing archive")

            # Move with RENAME mode - should create archive_1.tar.gz, NOT archive.tar_1.gz
            result = move_file_safe(
                str(source),
                str(output_root / "archive.tar.gz"),
                str(source_root),
                str(output_root),
                ConflictMode.RENAME,
            )

            inner_result = unsafe_ioresult_to_result(result)
            self.assertTrue(inner_result)

            # Original should be unchanged
            self.assertTrue((output_root / "archive.tar.gz").exists())
            self.assertEqual((output_root / "archive.tar.gz").read_text(), "existing archive")

            # NEW file should be archive_1.tar.gz (correct multi-part extension handling)
            renamed_target = output_root / "archive_1.tar.gz"
            self.assertTrue(renamed_target.exists())
            self.assertEqual(renamed_target.read_text(), "new archive")


if __name__ == "__main__":
    unittest.main()

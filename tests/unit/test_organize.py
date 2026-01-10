"""Unit tests for organize module - pure functions only."""

import unittest

from fx_bin.organize import DateSource, ConflictMode, OrganizeContext


class TestDateSource(unittest.TestCase):
    """Test cases for DateSource enum."""

    def test_given_datesource_enum_when_accessed_then_has_expected_values(self):
        """Test that DateSource enum is defined and has expected values."""
        # Test enum values exist
        self.assertTrue(hasattr(DateSource, "CREATED"))
        self.assertTrue(hasattr(DateSource, "MODIFIED"))

        # Test enum values are accessible
        self.assertEqual(DateSource.CREATED.value, "created")
        self.assertEqual(DateSource.MODIFIED.value, "modified")


class TestConflictMode(unittest.TestCase):
    """Test cases for ConflictMode enum."""

    def test_given_conflictmode_enum_when_accessed_then_has_expected_values(self):
        """Test that ConflictMode enum is defined and has expected values."""
        # Test enum values exist
        self.assertTrue(hasattr(ConflictMode, "RENAME"))
        self.assertTrue(hasattr(ConflictMode, "SKIP"))
        self.assertTrue(hasattr(ConflictMode, "OVERWRITE"))
        self.assertTrue(hasattr(ConflictMode, "ASK"))

        # Test enum values are accessible
        self.assertEqual(ConflictMode.RENAME.value, "rename")
        self.assertEqual(ConflictMode.SKIP.value, "skip")
        self.assertEqual(ConflictMode.OVERWRITE.value, "overwrite")
        self.assertEqual(ConflictMode.ASK.value, "ask")


class TestOrganizeContext(unittest.TestCase):
    """Test cases for OrganizeContext frozen dataclass."""

    def test_given_organizecontext_when_created_then_is_frozen_dataclass_with_all_fields(self):
        """Test that OrganizeContext is a frozen dataclass with all fields."""
        from fx_bin.organize import OrganizeContext
        from dataclasses import is_dataclass

        # Test it's a dataclass
        self.assertTrue(is_dataclass(OrganizeContext))

        # Test basic fields exist
        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.RENAME,
            output_dir="/output",
            dry_run=False,
        )

        # Test field values
        self.assertEqual(context.date_source, DateSource.CREATED)
        self.assertEqual(context.depth, 3)
        self.assertEqual(context.conflict_mode, ConflictMode.RENAME)
        self.assertEqual(context.output_dir, "/output")
        self.assertFalse(context.dry_run)

    def test_given_organizecontext_when_modification_attempted_then_raises_frozen_instance_error(self):
        """Test that OrganizeContext is frozen (immutable)."""
        from fx_bin.organize import OrganizeContext
        from dataclasses import FrozenInstanceError

        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.RENAME,
            output_dir="/output",
            dry_run=False,
        )

        # Attempting to modify should raise FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            context.depth = 2

    def test_given_organizecontext_when_created_then_phase9_fields_work_correctly(self):
        """Test that OrganizeContext has Phase 9 fields (recursive, clean_empty, fail_fast, hidden)."""
        from fx_bin.organize import OrganizeContext

        # Test all Phase 9 fields exist and work correctly
        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.RENAME,
            output_dir="/output",
            dry_run=False,
            recursive=False,
            clean_empty=False,
            fail_fast=False,
            hidden=False,
        )

        # Test Phase 9 field values
        self.assertFalse(context.recursive)
        self.assertFalse(context.clean_empty)
        self.assertFalse(context.fail_fast)
        self.assertFalse(context.hidden)


class TestFileOrganizeResult(unittest.TestCase):
    """Test cases for FileOrganizeResult frozen dataclass."""

    def test_given_fileorganizeresult_when_created_then_is_frozen_dataclass(self):
        """Test that FileOrganizeResult is a frozen dataclass."""
        from fx_bin.organize import FileOrganizeResult
        from dataclasses import is_dataclass

        # Test it's a dataclass
        self.assertTrue(is_dataclass(FileOrganizeResult))

        # Test fields exist
        result = FileOrganizeResult(
            source="/source/file.txt",
            target="/target/2026/202601/20260110/file.txt",
            action="moved",
        )

        self.assertEqual(result.source, "/source/file.txt")
        self.assertEqual(result.target, "/target/2026/202601/20260110/file.txt")
        self.assertEqual(result.action, "moved")

    def test_given_fileorganizeresult_when_modification_attempted_then_raises_frozen_instance_error(self):
        """Test that FileOrganizeResult is frozen."""
        from fx_bin.organize import FileOrganizeResult
        from dataclasses import FrozenInstanceError

        result = FileOrganizeResult(
            source="/source/file.txt",
            target="/target/2026/202601/20260110/file.txt",
            action="moved",
        )

        with self.assertRaises(FrozenInstanceError):
            result.action = "skipped"


class TestOrganizeSummary(unittest.TestCase):
    """Test cases for OrganizeSummary frozen dataclass."""

    def test_given_organizesummary_when_created_then_is_frozen_dataclass(self):
        """Test that OrganizeSummary is a frozen dataclass."""
        from fx_bin.organize import OrganizeSummary
        from dataclasses import is_dataclass

        # Test it's a dataclass
        self.assertTrue(is_dataclass(OrganizeSummary))

        # Test fields exist
        summary = OrganizeSummary(
            total_files=100,
            processed=95,
            skipped=5,
            errors=0,
            dry_run=True,
        )

        self.assertEqual(summary.total_files, 100)
        self.assertEqual(summary.processed, 95)
        self.assertEqual(summary.skipped, 5)
        self.assertEqual(summary.errors, 0)
        self.assertTrue(summary.dry_run)

    def test_given_organizesummary_when_modification_attempted_then_raises_frozen_instance_error(self):
        """Test that OrganizeSummary is frozen."""
        from fx_bin.organize import OrganizeSummary
        from dataclasses import FrozenInstanceError

        summary = OrganizeSummary(
            total_files=100,
            processed=95,
            skipped=5,
            errors=0,
            dry_run=False,
        )

        with self.assertRaises(FrozenInstanceError):
            summary.processed = 96


class TestGetTargetPath(unittest.TestCase):
    """Test cases for get_target_path() function."""

    def test_given_date_and_depth_3_when_calculating_target_then_returns_correct_path(self):
        """Test get_target_path with depth=3 (year/month/day)."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        # Test with a specific date: 2026-01-10 14:30:00
        test_date = datetime(2026, 1, 10, 14, 30, 0)
        result = get_target_path("/output", "photo.jpg", test_date, depth=3)

        # Should be: /output/2026/202601/20260110/photo.jpg
        expected = "/output/2026/202601/20260110/photo.jpg"
        self.assertEqual(result, expected)

    def test_given_date_and_depth_2_when_calculating_target_then_returns_correct_path(self):
        """Test get_target_path with depth=2 (year/day)."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        test_date = datetime(2026, 1, 10, 14, 30, 0)
        result = get_target_path("/output", "photo.jpg", test_date, depth=2)

        # Should be: /output/2026/20260110/photo.jpg
        expected = "/output/2026/20260110/photo.jpg"
        self.assertEqual(result, expected)

    def test_given_date_and_depth_1_when_calculating_target_then_returns_correct_path(self):
        """Test get_target_path with depth=1 (day only)."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        test_date = datetime(2026, 1, 10, 14, 30, 0)
        result = get_target_path("/output", "photo.jpg", test_date, depth=1)

        # Should be: /output/20260110/photo.jpg
        expected = "/output/20260110/photo.jpg"
        self.assertEqual(result, expected)

    def test_given_date_near_midnight_when_calculating_target_then_uses_local_timezone(self):
        """Test that get_target_path uses local timezone."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        # Test near midnight boundary - should use local time
        test_date = datetime(2026, 1, 10, 23, 59, 59)
        result = get_target_path("/output", "photo.jpg", test_date, depth=3)

        # Should be in the 20260110 directory
        self.assertIn("20260110", result)

    def test_given_filename_with_multi_part_extension_when_calculating_target_then_preserves_full_filename(self):
        """Test that filename with multi-part extension is preserved."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        test_date = datetime(2026, 1, 10, 14, 30, 0)
        result = get_target_path("/output", "archive.tar.gz", test_date, depth=3)

        # Should preserve full filename
        expected = "/output/2026/202601/20260110/archive.tar.gz"
        self.assertEqual(result, expected)


class TestIsHiddenFile(unittest.TestCase):
    """Test cases for is_hidden_file() function."""

    def test_given_filename_with_dot_prefix_when_checking_hidden_then_returns_true(self):
        """Test that files starting with . are detected as hidden."""
        from fx_bin.organize import is_hidden_file

        # Unix-style hidden files
        self.assertTrue(is_hidden_file(".gitignore"))
        self.assertTrue(is_hidden_file(".DS_Store"))
        self.assertTrue(is_hidden_file(".hidden_file.txt"))

    def test_given_filename_without_dot_prefix_when_checking_hidden_then_returns_false(self):
        """Test that normal files are not detected as hidden."""
        from fx_bin.organize import is_hidden_file

        # Regular files
        self.assertFalse(is_hidden_file("photo.jpg"))
        self.assertFalse(is_hidden_file("document.pdf"))
        self.assertFalse(is_hidden_file("archive.tar.gz"))
        self.assertFalse(is_hidden_file("README"))

    def test_given_filename_with_dot_in_middle_when_checking_hidden_then_returns_false(self):
        """Test that files with dots in the middle are not hidden."""
        from fx_bin.organize import is_hidden_file

        # Dots in filename are OK, only leading dot means hidden
        self.assertFalse(is_hidden_file("file.name.txt"))
        self.assertFalse(is_hidden_file("config.file"))
        self.assertFalse(is_hidden_file("version.1.2.txt"))


class TestMatchesGlobPattern(unittest.TestCase):
    """Test cases for matches_glob_pattern() function."""

    def test_given_filename_and_pattern_when_matching_basic_patterns_then_returns_correct_result(self):
        """Test basic glob pattern matching."""
        from fx_bin.organize import matches_glob_pattern

        # Simple patterns
        self.assertTrue(matches_glob_pattern("photo.jpg", "*.jpg"))
        self.assertTrue(matches_glob_pattern("document.pdf", "*.pdf"))
        self.assertFalse(matches_glob_pattern("photo.jpg", "*.pdf"))

    def test_given_filename_and_pattern_when_matching_case_sensitive_then_respects_case(self):
        """Test that matching is case-sensitive (fnmatchcase)."""
        from fx_bin.organize import matches_glob_pattern

        # Case sensitivity: *.JPG should NOT match beach.jpg
        self.assertFalse(matches_glob_pattern("beach.jpg", "*.JPG"))
        self.assertFalse(matches_glob_pattern("beach.JPG", "*.jpg"))
        self.assertTrue(matches_glob_pattern("beach.JPG", "*.JPG"))
        self.assertTrue(matches_glob_pattern("beach.jpg", "*.jpg"))

    def test_given_filename_with_path_and_pattern_when_matching_then_matches_basename_only(self):
        """Test that pattern matches basename only, not full path."""
        from fx_bin.organize import matches_glob_pattern

        # Should match on basename, ignore path
        self.assertTrue(matches_glob_pattern("photo.jpg", "*.jpg"))
        self.assertTrue(matches_glob_pattern("/path/to/photo.jpg", "*.jpg"))
        self.assertTrue(matches_glob_pattern("./photo.jpg", "*.jpg"))

    def test_given_filename_and_wildcard_pattern_when_matching_then_handles_various_wildcards(self):
        """Test various wildcard patterns."""
        from fx_bin.organize import matches_glob_pattern

        # Different wildcards
        self.assertTrue(matches_glob_pattern("photo.jpg", "*"))
        self.assertTrue(matches_glob_pattern("photo.jpg", "p*"))
        self.assertTrue(matches_glob_pattern("photo.jpg", "*.jp*"))
        self.assertTrue(matches_glob_pattern("photo.jpg", "ph*.jpg"))
        self.assertFalse(matches_glob_pattern("photo.jpeg", "*.jpg"))


class TestShouldProcessFile(unittest.TestCase):
    """Test cases for should_process_file() function."""

    def test_given_non_hidden_file_and_no_filters_when_checking_should_process_then_returns_true(self):
        """Test that non-hidden files are processed when no filters specified (hidden=False default)."""
        from fx_bin.organize import should_process_file

        # No filters, hidden=False (default) = process non-hidden files
        self.assertTrue(should_process_file("photo.jpg", (), ()))
        self.assertFalse(should_process_file(".gitignore", (), ()))  # Hidden files excluded by default
        self.assertTrue(should_process_file("document.pdf", (), ()))

    def test_given_hidden_file_and_hidden_flag_when_checking_should_process_then_returns_true(self):
        """Test that hidden=True includes hidden files."""
        from fx_bin.organize import should_process_file

        # With hidden=True, hidden files are included
        self.assertTrue(should_process_file(".gitignore", (), (), hidden=True))
        self.assertTrue(should_process_file("photo.jpg", (), (), hidden=True))

    def test_given_file_and_include_patterns_when_checking_should_process_then_filters_correctly(self):
        """Test include pattern filtering (tuple)."""
        from fx_bin.organize import should_process_file

        # Only include images
        self.assertTrue(should_process_file("photo.jpg", ("*.jpg", "*.png"), ()))
        self.assertTrue(should_process_file("image.png", ("*.jpg", "*.png"), ()))
        self.assertFalse(should_process_file("document.pdf", ("*.jpg", "*.png"), ()))

    def test_given_file_and_exclude_patterns_when_checking_should_process_then_filters_correctly(self):
        """Test exclude pattern filtering (tuple)."""
        from fx_bin.organize import should_process_file

        # Exclude hidden files and temp files
        self.assertFalse(should_process_file(".gitignore", (), (".*", "*.tmp")))
        self.assertFalse(should_process_file("temp.tmp", (), (".*", "*.tmp")))
        self.assertTrue(should_process_file("photo.jpg", (), (".*", "*.tmp")))

    def test_given_file_and_include_exclude_patterns_when_checking_should_process_then_applies_both(self):
        """Test combined include and exclude (include first, then exclude)."""
        from fx_bin.organize import should_process_file

        # Include images, but exclude hidden ones
        self.assertTrue(should_process_file("photo.jpg", ("*.jpg", "*.png"), (".*")))
        self.assertFalse(should_process_file(".hidden.jpg", ("*.jpg", "*.png"), (".*")))
        self.assertFalse(should_process_file("document.pdf", ("*.jpg", "*.png"), ()))

    def test_given_hidden_file_and_include_exclude_when_checking_should_process_then_exclude_takes_precedence(self):
        """Test that exclude patterns filter after include."""
        from fx_bin.organize import should_process_file

        # Include all jpg, but exclude hidden
        self.assertTrue(should_process_file("photo.jpg", ("*.jpg",), (".*")))
        self.assertFalse(should_process_file(".hidden.jpg", ("*.jpg",), (".*")))


class TestResolveConflictRename(unittest.TestCase):
    """Test cases for resolve_conflict_rename() function."""

    def test_given_non_conflicting_path_when_resolving_conflict_then_returns_path_unchanged(self):
        """Test that non-conflicting path is returned unchanged."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/other/path.jpg"}
        result = resolve_conflict_rename("/output/photo.jpg", allocated)
        self.assertEqual(result, "/output/photo.jpg")

    def test_given_conflicting_path_when_resolving_conflict_then_adds_1_suffix(self):
        """Test basic conflict resolution with _1 suffix."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/output/photo.jpg"}
        result = resolve_conflict_rename("/output/photo.jpg", allocated)
        self.assertEqual(result, "/output/photo_1.jpg")

    def test_given_conflicting_path_with_existing_suffixes_when_resolving_conflict_then_increments_suffix(self):
        """Test incrementing suffix for multiple conflicts."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/output/photo.jpg", "/output/photo_1.jpg", "/output/photo_2.jpg"}
        result = resolve_conflict_rename("/output/photo.jpg", allocated)
        self.assertEqual(result, "/output/photo_3.jpg")

    def test_given_multi_part_extension_when_resolving_conflict_then_inserts_suffix_correctly(self):
        """Test conflict resolution with multi-part extension (.tar.gz)."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/output/archive.tar.gz"}
        result = resolve_conflict_rename("/output/archive.tar.gz", allocated)
        self.assertEqual(result, "/output/archive_1.tar.gz")


class TestGenerateOrganizePlan(unittest.TestCase):
    """Test cases for generate_organize_plan() function."""

    def test_given_files_and_dates_when_generating_plan_then_creates_basic_plan(self):
        """Test basic plan generation."""
        from fx_bin.organize import generate_organize_plan
        from datetime import datetime

        files = ["/src/photo.jpg"]
        dates = {"/src/photo.jpg": datetime(2026, 1, 10)}
        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.RENAME,
            output_dir="/output",
            dry_run=False,
        )

        plan = generate_organize_plan(files, dates, context)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].source, "/src/photo.jpg")
        self.assertEqual(plan[0].action, "moved")
        self.assertIn("20260110", plan[0].target)

    def test_given_unsorted_files_when_generating_plan_then_processes_in_deterministic_order(self):
        """Test that files are processed in sorted order."""
        from fx_bin.organize import generate_organize_plan
        from datetime import datetime

        files = ["/src/zebra.jpg", "/src/apple.jpg", "/src/beta.jpg"]
        dates = {
            "/src/zebra.jpg": datetime(2026, 1, 10),
            "/src/apple.jpg": datetime(2026, 1, 10),
            "/src/beta.jpg": datetime(2026, 1, 10),
        }
        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.RENAME,
            output_dir="/output",
            dry_run=False,
        )

        plan = generate_organize_plan(files, dates, context)
        self.assertEqual(len(plan), 3)
        # Should be sorted: apple, beta, zebra
        self.assertIn("apple", plan[0].source)
        self.assertIn("beta", plan[1].source)
        self.assertIn("zebra", plan[2].source)

    def test_given_same_name_files_and_rename_mode_when_generating_plan_then_resolves_intra_run_conflicts(self):
        """Test intra-run conflict resolution with rename mode."""
        from fx_bin.organize import generate_organize_plan
        from datetime import datetime

        # Two files with same name going to same date directory
        files = ["/src/photo.jpg", "/src2/photo.jpg"]
        dates = {
            "/src/photo.jpg": datetime(2026, 1, 10),
            "/src2/photo.jpg": datetime(2026, 1, 10),
        }
        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.RENAME,
            output_dir="/output",
            dry_run=False,
        )

        plan = generate_organize_plan(files, dates, context)
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0].action, "moved")
        self.assertEqual(plan[1].action, "moved")
        # Second file should have _1 suffix
        self.assertTrue(plan[1].target.endswith("photo_1.jpg"))

    def test_given_same_name_files_and_skip_mode_when_generating_plan_then_skips_conflicts(self):
        """Test intra-run conflict with skip mode."""
        from fx_bin.organize import generate_organize_plan
        from datetime import datetime

        files = ["/src/photo.jpg", "/src2/photo.jpg"]
        dates = {
            "/src/photo.jpg": datetime(2026, 1, 10),
            "/src2/photo.jpg": datetime(2026, 1, 10),
        }
        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.SKIP,
            output_dir="/output",
            dry_run=False,
        )

        plan = generate_organize_plan(files, dates, context)
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0].action, "moved")
        self.assertEqual(plan[1].action, "skipped")

    def test_given_file_without_date_when_generating_plan_then_marks_as_error(self):
        """Test handling of files without date information."""
        from fx_bin.organize import generate_organize_plan
        from datetime import datetime

        files = ["/src/photo.jpg", "/src/no_date.jpg"]
        dates = {"/src/photo.jpg": datetime(2026, 1, 10)}
        context = OrganizeContext(
            date_source=DateSource.CREATED,
            depth=3,
            conflict_mode=ConflictMode.RENAME,
            output_dir="/output",
            dry_run=False,
        )

        plan = generate_organize_plan(files, dates, context)
        self.assertEqual(len(plan), 2)
        # After sorting: /src/no_date.jpg comes first (no date = error)
        # /src/photo.jpg second
        self.assertEqual(plan[0].action, "error")
        self.assertEqual(plan[1].action, "moved")


if __name__ == "__main__":
    unittest.main()

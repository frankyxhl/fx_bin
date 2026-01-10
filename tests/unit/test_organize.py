"""Unit tests for organize module - pure functions only."""

import unittest

from fx_bin.organize import DateSource, ConflictMode, OrganizeContext


class TestDateSource(unittest.TestCase):
    """Test cases for DateSource enum."""

    def test_datesource_enum_exists(self):
        """Test that DateSource enum is defined and has expected values."""
        # Test enum values exist
        self.assertTrue(hasattr(DateSource, "CREATED"))
        self.assertTrue(hasattr(DateSource, "MODIFIED"))

        # Test enum values are accessible
        self.assertEqual(DateSource.CREATED.value, "created")
        self.assertEqual(DateSource.MODIFIED.value, "modified")


class TestConflictMode(unittest.TestCase):
    """Test cases for ConflictMode enum."""

    def test_conflictmode_enum_exists(self):
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

    def test_organizecontext_exists_and_frozen(self):
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

    def test_organizecontext_immutable(self):
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


class TestFileOrganizeResult(unittest.TestCase):
    """Test cases for FileOrganizeResult frozen dataclass."""

    def test_fileorganizeresult_exists_and_frozen(self):
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

    def test_fileorganizeresult_immutable(self):
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

    def test_organizesummary_exists_and_frozen(self):
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

    def test_organizesummary_immutable(self):
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

    def test_get_target_path_depth_3(self):
        """Test get_target_path with depth=3 (year/month/day)."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        # Test with a specific date: 2026-01-10 14:30:00
        test_date = datetime(2026, 1, 10, 14, 30, 0)
        result = get_target_path("/output", "photo.jpg", test_date, depth=3)

        # Should be: /output/2026/202601/20260110/photo.jpg
        expected = "/output/2026/202601/20260110/photo.jpg"
        self.assertEqual(result, expected)

    def test_get_target_path_depth_2(self):
        """Test get_target_path with depth=2 (year/day)."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        test_date = datetime(2026, 1, 10, 14, 30, 0)
        result = get_target_path("/output", "photo.jpg", test_date, depth=2)

        # Should be: /output/2026/20260110/photo.jpg
        expected = "/output/2026/20260110/photo.jpg"
        self.assertEqual(result, expected)

    def test_get_target_path_depth_1(self):
        """Test get_target_path with depth=1 (day only)."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        test_date = datetime(2026, 1, 10, 14, 30, 0)
        result = get_target_path("/output", "photo.jpg", test_date, depth=1)

        # Should be: /output/20260110/photo.jpg
        expected = "/output/20260110/photo.jpg"
        self.assertEqual(result, expected)

    def test_get_target_path_timezone_aware(self):
        """Test that get_target_path uses local timezone."""
        from fx_bin.organize import get_target_path
        from datetime import datetime

        # Test near midnight boundary - should use local time
        test_date = datetime(2026, 1, 10, 23, 59, 59)
        result = get_target_path("/output", "photo.jpg", test_date, depth=3)

        # Should be in the 20260110 directory
        self.assertIn("20260110", result)

    def test_get_target_path_with_multi_part_extension(self):
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

    def test_is_hidden_file_with_dot_prefix(self):
        """Test that files starting with . are detected as hidden."""
        from fx_bin.organize import is_hidden_file

        # Unix-style hidden files
        self.assertTrue(is_hidden_file(".gitignore"))
        self.assertTrue(is_hidden_file(".DS_Store"))
        self.assertTrue(is_hidden_file(".hidden_file.txt"))

    def test_is_hidden_file_without_dot_prefix(self):
        """Test that normal files are not detected as hidden."""
        from fx_bin.organize import is_hidden_file

        # Regular files
        self.assertFalse(is_hidden_file("photo.jpg"))
        self.assertFalse(is_hidden_file("document.pdf"))
        self.assertFalse(is_hidden_file("archive.tar.gz"))
        self.assertFalse(is_hidden_file("README"))

    def test_is_hidden_file_with_dot_in_middle(self):
        """Test that files with dots in the middle are not hidden."""
        from fx_bin.organize import is_hidden_file

        # Dots in filename are OK, only leading dot means hidden
        self.assertFalse(is_hidden_file("file.name.txt"))
        self.assertFalse(is_hidden_file("config.file"))
        self.assertFalse(is_hidden_file("version.1.2.txt"))


class TestMatchesGlobPattern(unittest.TestCase):
    """Test cases for matches_glob_pattern() function."""

    def test_matches_glob_pattern_basic(self):
        """Test basic glob pattern matching."""
        from fx_bin.organize import matches_glob_pattern

        # Simple patterns
        self.assertTrue(matches_glob_pattern("photo.jpg", "*.jpg"))
        self.assertTrue(matches_glob_pattern("document.pdf", "*.pdf"))
        self.assertFalse(matches_glob_pattern("photo.jpg", "*.pdf"))

    def test_matches_glob_pattern_case_sensitive(self):
        """Test that matching is case-sensitive (fnmatchcase)."""
        from fx_bin.organize import matches_glob_pattern

        # Case sensitivity: *.JPG should NOT match beach.jpg
        self.assertFalse(matches_glob_pattern("beach.jpg", "*.JPG"))
        self.assertFalse(matches_glob_pattern("beach.JPG", "*.jpg"))
        self.assertTrue(matches_glob_pattern("beach.JPG", "*.JPG"))
        self.assertTrue(matches_glob_pattern("beach.jpg", "*.jpg"))

    def test_matches_glob_pattern_on_basename_only(self):
        """Test that pattern matches basename only, not full path."""
        from fx_bin.organize import matches_glob_pattern

        # Should match on basename, ignore path
        self.assertTrue(matches_glob_pattern("photo.jpg", "*.jpg"))
        self.assertTrue(matches_glob_pattern("/path/to/photo.jpg", "*.jpg"))
        self.assertTrue(matches_glob_pattern("./photo.jpg", "*.jpg"))

    def test_matches_glob_pattern_wildcards(self):
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

    def test_should_process_file_no_filters(self):
        """Test that all files are processed when no filters specified."""
        from fx_bin.organize import should_process_file

        # No filters = process all
        self.assertTrue(should_process_file("photo.jpg", (), ()))
        self.assertTrue(should_process_file(".gitignore", (), ()))
        self.assertTrue(should_process_file("document.pdf", (), ()))

    def test_should_process_file_include_only(self):
        """Test include pattern filtering (tuple)."""
        from fx_bin.organize import should_process_file

        # Only include images
        self.assertTrue(should_process_file("photo.jpg", ("*.jpg", "*.png"), ()))
        self.assertTrue(should_process_file("image.png", ("*.jpg", "*.png"), ()))
        self.assertFalse(should_process_file("document.pdf", ("*.jpg", "*.png"), ()))

    def test_should_process_file_exclude_only(self):
        """Test exclude pattern filtering (tuple)."""
        from fx_bin.organize import should_process_file

        # Exclude hidden files and temp files
        self.assertFalse(should_process_file(".gitignore", (), (".*", "*.tmp")))
        self.assertFalse(should_process_file("temp.tmp", (), (".*", "*.tmp")))
        self.assertTrue(should_process_file("photo.jpg", (), (".*", "*.tmp")))

    def test_should_process_file_combined_include_exclude(self):
        """Test combined include and exclude (include first, then exclude)."""
        from fx_bin.organize import should_process_file

        # Include images, but exclude hidden ones
        self.assertTrue(should_process_file("photo.jpg", ("*.jpg", "*.png"), (".*")))
        self.assertFalse(should_process_file(".hidden.jpg", ("*.jpg", "*.png"), (".*")))
        self.assertFalse(should_process_file("document.pdf", ("*.jpg", "*.png"), ()))

    def test_should_process_file_exclude_takes_precedence(self):
        """Test that exclude patterns filter after include."""
        from fx_bin.organize import should_process_file

        # Include all jpg, but exclude hidden
        self.assertTrue(should_process_file("photo.jpg", ("*.jpg",), (".*")))
        self.assertFalse(should_process_file(".hidden.jpg", ("*.jpg",), (".*")))


class TestResolveConflictRename(unittest.TestCase):
    """Test cases for resolve_conflict_rename() function."""

    def test_resolve_conflict_rename_no_conflict(self):
        """Test that non-conflicting path is returned unchanged."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/other/path.jpg"}
        result = resolve_conflict_rename("/output/photo.jpg", allocated)
        self.assertEqual(result, "/output/photo.jpg")

    def test_resolve_conflict_rename_basic_conflict(self):
        """Test basic conflict resolution with _1 suffix."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/output/photo.jpg"}
        result = resolve_conflict_rename("/output/photo.jpg", allocated)
        self.assertEqual(result, "/output/photo_1.jpg")

    def test_resolve_conflict_rename_incrementing(self):
        """Test incrementing suffix for multiple conflicts."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/output/photo.jpg", "/output/photo_1.jpg", "/output/photo_2.jpg"}
        result = resolve_conflict_rename("/output/photo.jpg", allocated)
        self.assertEqual(result, "/output/photo_3.jpg")

    def test_resolve_conflict_rename_multi_part_extension(self):
        """Test conflict resolution with multi-part extension (.tar.gz)."""
        from fx_bin.organize import resolve_conflict_rename

        allocated = {"/output/archive.tar.gz"}
        result = resolve_conflict_rename("/output/archive.tar.gz", allocated)
        self.assertEqual(result, "/output/archive_1.tar.gz")


class TestGenerateOrganizePlan(unittest.TestCase):
    """Test cases for generate_organize_plan() function."""

    def test_generate_organize_plan_basic(self):
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

    def test_generate_organize_plan_deterministic_ordering(self):
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

    def test_generate_organize_plan_intra_run_conflict_rename(self):
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

    def test_generate_organize_plan_intra_run_conflict_skip(self):
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

    def test_generate_organize_plan_missing_date(self):
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

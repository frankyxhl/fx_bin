"""Unit tests for common utilities."""

import unittest
from datetime import datetime
from fx_bin.common import (
    generate_timestamp,
    get_multi_ext,
    get_base_name,
    format_size_aligned,
    convert_size,
)


class TestCommonUtils(unittest.TestCase):
    """Test cases for common utility functions."""

    def test_generate_timestamp(self):
        """Test timestamp generation with various formats."""
        # Test default format (implicitly tested by calling with a format)
        ts = generate_timestamp("%Y%m%d")
        self.assertEqual(len(ts), 8)
        self.assertTrue(ts.isdigit())

        # Test with custom format
        ts_custom = generate_timestamp("%Y-%m-%d")
        self.assertRegex(ts_custom, r"^\d{4}-\d{2}-\d{2}$")

        # Test with provided 'now' object
        fixed_now = datetime(2026, 1, 5, 12, 0, 0)
        ts_fixed = generate_timestamp("%Y%m%d%H%M%S", now=fixed_now)
        self.assertEqual(ts_fixed, "20260105120000")

    def test_get_multi_ext(self):
        """Test extraction of multi-part and single extensions."""
        self.assertEqual(get_multi_ext("archive.tar.gz"), ".tar.gz")
        self.assertEqual(get_multi_ext("data.tar.bz2"), ".tar.bz2")
        self.assertEqual(get_multi_ext("archive.tar.xz"), ".tar.xz")
        self.assertEqual(get_multi_ext("document.txt"), ".txt")
        self.assertEqual(get_multi_ext("script.py"), ".py")
        self.assertEqual(get_multi_ext("README"), "")
        self.assertEqual(get_multi_ext(".gitignore"), ".gitignore")

    def test_get_base_name(self):
        """Test base name extraction with various extension types."""
        self.assertEqual(get_base_name("archive.tar.gz"), "archive")
        self.assertEqual(get_base_name("data.tar.bz2"), "data")
        self.assertEqual(get_base_name("archive.tar.xz"), "archive")
        self.assertEqual(get_base_name("document.txt"), "document")
        self.assertEqual(get_base_name("script.py"), "script")
        self.assertEqual(get_base_name("README"), "README")
        self.assertEqual(get_base_name(".gitignore"), "")

    def test_format_size_aligned(self):
        """Test aligned size formatting for various sizes."""
        self.assertEqual(format_size_aligned(0), "      0 B")
        self.assertEqual(format_size_aligned(100), "    100 B")
        self.assertEqual(format_size_aligned(1024), "   1.0 KB")
        self.assertEqual(format_size_aligned(1536), "   1.5 KB")
        self.assertEqual(format_size_aligned(1024 * 1024), "   1.0 MB")
        self.assertEqual(format_size_aligned(1024 * 1024 * 1024 * 2), "   2.0 GB")

        # Test custom width
        self.assertEqual(format_size_aligned(100, width=5), "100 B")

    def test_convert_size(self):
        """Test human-readable size conversion."""
        self.assertEqual(convert_size(0), "0B")
        self.assertEqual(convert_size(100), "100B")
        self.assertEqual(convert_size(1024), "1KB")
        self.assertEqual(convert_size(1536), "2KB")  # round(1.5) = 2
        self.assertEqual(convert_size(1024 * 1024), "1MB")


if __name__ == "__main__":
    unittest.main()

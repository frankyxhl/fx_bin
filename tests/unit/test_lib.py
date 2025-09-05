"""Tests for fx_bin.lib module - utility functions.

This module tests all utility functions in lib.py to achieve 100% coverage.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

from fx_bin import lib


class TestCharacterCounting(unittest.TestCase):
    """Test character counting functions."""

    def test_count_ascii_empty_string(self):
        """Test counting ASCII characters in empty string."""
        self.assertEqual(lib.count_ascii(""), 0)

    def test_count_ascii_all_ascii(self):
        """Test counting ASCII characters in pure ASCII string."""
        self.assertEqual(lib.count_ascii("Hello World!"), 12)
        self.assertEqual(lib.count_ascii("123 abc XYZ"), 11)

    def test_count_ascii_mixed_characters(self):
        """Test counting ASCII characters in mixed string."""
        # Mix of ASCII and non-ASCII
        self.assertEqual(lib.count_ascii("Hello你好"), 5)  # Only "Hello" is ASCII
        self.assertEqual(lib.count_ascii("café"), 3)  # "caf" are ASCII, é is not

    def test_count_ascii_unicode_only(self):
        """Test counting ASCII in pure Unicode string."""
        self.assertEqual(lib.count_ascii("你好世界"), 0)
        self.assertEqual(lib.count_ascii("日本語"), 0)

    def test_count_ascii_special_ascii(self):
        """Test counting special ASCII characters."""
        # All printable ASCII including special chars
        self.assertEqual(lib.count_ascii("!@#$%^&*()"), 10)
        self.assertEqual(lib.count_ascii("\t\n\r "), 4)  # Whitespace chars


class TestSpecialCharacterCounting(unittest.TestCase):
    """Test special character counting functions."""

    def test_count_special_char_lst_empty(self):
        """Test counting special characters in empty string."""
        self.assertEqual(lib.count_special_char_lst(""), 0)

    def test_count_special_char_lst_with_apostrophe(self):
        """Test counting apostrophes (curly apostrophe)."""
        # Note: SPECIAL_CHAR_LST contains curly quotes ' (U+2018) and ' (U+2019) not straight apostrophe '
        self.assertEqual(
            lib.count_special_char_lst("don’t"), 1
        )  # Using curly apostrophe
        self.assertEqual(
            lib.count_special_char_lst("it’s Bob’s"), 2
        )  # Using curly apostrophes

    def test_count_special_char_lst_with_endash(self):
        """Test counting en-dashes."""
        self.assertEqual(lib.count_special_char_lst("2020–2024"), 1)
        self.assertEqual(lib.count_special_char_lst("New York – Boston"), 1)

    def test_count_special_char_lst_mixed(self):
        """Test counting mixed special characters."""
        self.assertEqual(
            lib.count_special_char_lst("don’t stop – keep going"), 2
        )  # curly apostrophe + en-dash
        self.assertEqual(
            lib.count_special_char_lst("‘quoted’ – text"), 3
        )  # 2 curly apostrophes + en-dash

    def test_count_special_char_lst_none_present(self):
        """Test when no special characters are present."""
        self.assertEqual(lib.count_special_char_lst("Hello World"), 0)
        self.assertEqual(lib.count_special_char_lst("1234567890"), 0)


class TestFullwidthCounting(unittest.TestCase):
    """Test fullwidth character counting."""

    def test_count_fullwidth_empty(self):
        """Test counting fullwidth in empty string."""
        self.assertEqual(lib.count_fullwidth(""), 0)

    def test_count_fullwidth_ascii_only(self):
        """Test counting fullwidth in ASCII-only string."""
        self.assertEqual(lib.count_fullwidth("Hello"), 5)

    def test_count_fullwidth_with_special(self):
        """Test counting fullwidth with special characters."""
        # ASCII + special characters (using curly apostrophe)
        self.assertEqual(lib.count_fullwidth("don’t"), 5)  # 4 ASCII + 1 special
        self.assertEqual(lib.count_fullwidth("test–case"), 9)  # 8 ASCII + 1 special

    def test_count_fullwidth_mixed(self):
        """Test counting fullwidth with mixed content."""
        # Mix of ASCII, special, and non-ASCII
        self.assertEqual(lib.count_fullwidth("Hello’世界"), 6)  # 5 ASCII + 1 special
        self.assertEqual(lib.count_fullwidth("Test–你好"), 5)  # 4 ASCII + 1 special


class TestToolDetection(unittest.TestCase):
    """Test tool/command detection functionality."""

    @patch("shutil.which")
    def test_is_tool_exists(self, mock_which):
        """Test detecting when a tool exists."""
        mock_which.return_value = "/usr/bin/git"
        self.assertTrue(lib.is_tool("git"))
        mock_which.assert_called_once_with("git")

    @patch("shutil.which")
    def test_is_tool_not_exists(self, mock_which):
        """Test detecting when a tool doesn't exist."""
        mock_which.return_value = None
        self.assertFalse(lib.is_tool("nonexistent_tool"))
        mock_which.assert_called_once_with("nonexistent_tool")

    @patch("shutil.which")
    def test_is_tool_various_tools(self, mock_which):
        """Test detecting various common tools."""
        # Test multiple tools
        tools = {"python": "/usr/bin/python", "ls": "/bin/ls", "fake_tool": None}

        for tool, path in tools.items():
            mock_which.return_value = path
            if path:
                self.assertTrue(lib.is_tool(tool), f"{tool} should be found")
            else:
                self.assertFalse(lib.is_tool(tool), f"{tool} should not be found")


class TestOSDetection(unittest.TestCase):
    """Test operating system detection."""

    @patch("os.name", "nt")
    def test_is_windows_true(self):
        """Test detecting Windows OS."""
        self.assertTrue(lib.is_windows())

    @patch("os.name", "posix")
    def test_is_windows_false_posix(self):
        """Test detecting non-Windows (POSIX) OS."""
        self.assertFalse(lib.is_windows())

    @patch("os.name", "java")
    def test_is_windows_false_java(self):
        """Test detecting non-Windows (Java) OS."""
        self.assertFalse(lib.is_windows())


class TestSpecialCharacterSet(unittest.TestCase):
    """Test the SPECIAL_CHAR_LST constant."""

    def test_special_char_lst_content(self):
        """Test that SPECIAL_CHAR_LST contains expected characters."""
        self.assertIn("‘", lib.SPECIAL_CHAR_LST)  # Left single quotation mark (U+2018)
        self.assertIn("’", lib.SPECIAL_CHAR_LST)  # Right single quotation mark (U+2019)
        self.assertIn("–", lib.SPECIAL_CHAR_LST)  # En-dash (U+2013)
        self.assertEqual(len(lib.SPECIAL_CHAR_LST), 3)

    def test_special_char_lst_is_set(self):
        """Test that SPECIAL_CHAR_LST is a set."""
        self.assertIsInstance(lib.SPECIAL_CHAR_LST, set)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_very_long_string(self):
        """Test functions with very long strings."""
        long_string = "a" * 10000 + "–" * 100 + "你" * 100

        # Should handle long strings without issues
        ascii_count = lib.count_ascii(long_string)
        self.assertEqual(ascii_count, 10000)

        special_count = lib.count_special_char_lst(long_string)
        self.assertEqual(special_count, 100)

        fullwidth_count = lib.count_fullwidth(long_string)
        self.assertEqual(fullwidth_count, 10100)  # 10000 ASCII + 100 special

    def test_unicode_edge_cases(self):
        """Test with various Unicode edge cases."""
        # Emoji (non-ASCII)
        self.assertEqual(lib.count_ascii("😀😃😄"), 0)

        # Zero-width characters
        self.assertEqual(lib.count_ascii("a​b"), 2)  # Zero-width space between a and b

        # Combining characters
        self.assertEqual(lib.count_ascii("é"), 0)  # Combined character
        self.assertEqual(lib.count_ascii("e\u0301"), 1)  # e + combining accent


if __name__ == "__main__":
    unittest.main()

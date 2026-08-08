"""Tests for the shared fx_bin.clipboard module (CHG-2115).

Platform-matrix coverage for plan building lives in test_open_launcher.py
(kept there as the re-export compatibility guarantee); this file covers the
new module surface and error type.
"""

import unittest
from unittest.mock import patch


class TestClipboardModule(unittest.TestCase):
    def test_build_clipboard_plan_darwin(self):
        from fx_bin.clipboard import build_clipboard_plan

        plan = build_clipboard_plan(platform_name="darwin")
        self.assertEqual(plan.args, ("pbcopy",))

    def test_unsupported_platform_raises_clipboard_error(self):
        from fx_bin.clipboard import build_clipboard_plan
        from fx_bin.errors import ClipboardError

        with self.assertRaises(ClipboardError):
            build_clipboard_plan(platform_name="freebsd12")

    def test_clipboard_error_is_open_error(self):
        """Compat: fx open copy callers catching OpenError keep working."""
        from fx_bin.errors import ClipboardError, FxBinError, OpenError

        self.assertTrue(issubclass(ClipboardError, OpenError))
        self.assertTrue(issubclass(ClipboardError, FxBinError))

    def test_open_launcher_reexports_clipboard_names(self):
        from fx_bin import clipboard, open_launcher

        self.assertIs(
            open_launcher.build_clipboard_plan, clipboard.build_clipboard_plan
        )
        self.assertIs(open_launcher.copy_to_clipboard, clipboard.copy_to_clipboard)

    def test_copy_to_clipboard_pipes_text(self):
        from fx_bin.clipboard import DispatchPlan, copy_to_clipboard

        with patch("fx_bin.clipboard.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            copy_to_clipboard("hello", DispatchPlan(("pbcopy",)))
        self.assertEqual(mock_run.call_args.kwargs["input"], b"hello")

    def test_copy_failure_raises_clipboard_error(self):
        from fx_bin.clipboard import DispatchPlan, copy_to_clipboard
        from fx_bin.errors import ClipboardError

        with patch("fx_bin.clipboard.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            with self.assertRaises(ClipboardError):
                copy_to_clipboard("x", DispatchPlan(("pbcopy",)))


if __name__ == "__main__":
    unittest.main()

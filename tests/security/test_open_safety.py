"""Security tests for the fx open launcher."""

import os
import tempfile
import unittest
from pathlib import Path

import pytest


@pytest.mark.security
class TestOpenSafety(unittest.TestCase):
    """Verify unsafe targets and dispatch inputs are rejected."""

    def test_config_rejects_file_and_javascript_schemes(self) -> None:
        from fx_bin.open_launcher import OpenError, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Local"
slug = "local"
target = "file:///tmp/secret.txt"
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaises(OpenError):
                load_config(config_path)

            config_path.write_text(
                """
[[items]]
name = "Script"
slug = "script"
target = "javascript:alert(1)"
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaises(OpenError):
                load_config(config_path)

    def test_dispatch_uses_argument_vector_for_shell_sensitive_url(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, build_dispatch_plan

        plan = build_dispatch_plan(
            LaunchTarget(
                label="Sensitive",
                target="https://example.com/?q=$(touch /tmp/fx-open-bad)",
                slug="sensitive",
            ),
            platform_name="darwin",
        )

        self.assertEqual(plan.args[0], "open")
        self.assertIn("$(touch /tmp/fx-open-bad)", plan.args[-1])
        self.assertFalse(plan.shell)

    def test_local_path_beginning_with_dash_resolves_to_absolute_path(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, build_dispatch_plan

        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            path = cwd / "-image.png"
            path.write_text("data", encoding="utf-8")

            old_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                plan = build_dispatch_plan(
                    LaunchTarget(label="Image", target="./-image.png", slug=None),
                    platform_name="darwin",
                )
            finally:
                os.chdir(old_cwd)

        self.assertTrue(Path(plan.args[-1]).is_absolute())
        self.assertTrue(plan.args[-1].endswith("-image.png"))

    def test_nul_byte_target_returns_open_error(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with self.assertRaises(OpenError):
            build_dispatch_plan(
                LaunchTarget(label="Bad", target="/tmp/bad\x00file.png", slug=None),
                platform_name="darwin",
            )

    def test_directory_target_returns_open_error(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(OpenError):
                build_dispatch_plan(
                    LaunchTarget(label="Dir", target=temp_dir, slug=None),
                    platform_name="darwin",
                )

    def test_symlink_loop_path_returns_open_error(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with tempfile.TemporaryDirectory() as temp_dir:
            loop_path = Path(temp_dir) / "loop"
            try:
                loop_path.symlink_to(loop_path)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable on this platform")

            with self.assertRaises(OpenError):
                build_dispatch_plan(
                    LaunchTarget(label="Loop", target=str(loop_path), slug=None),
                    platform_name="darwin",
                )


if __name__ == "__main__":
    unittest.main()

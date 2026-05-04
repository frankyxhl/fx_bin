"""Unit tests for the fx open launcher."""

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


class TestOpenConfig(unittest.TestCase):
    """Test open launcher config parsing and ordering."""

    def test_load_config_orders_items_by_order_name_slug(self) -> None:
        from fx_bin.open_launcher import load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Zulu"
slug = "zulu"
target = "https://z.example"
order = 20

[[items]]
name = "Alpha"
slug = "alpha"
target = "https://a.example"
order = 10

[[items]]
name = "Beta"
slug = "beta"
target = "https://b.example"
order = 10
tags = ["docs", "usage"]
""".strip(),
                encoding="utf-8",
            )

            config = load_config(config_path)

        self.assertEqual(
            [item.slug for item in config.items],
            ["alpha", "beta", "zulu"],
        )
        self.assertEqual(config.items[1].tags, ("docs", "usage"))

    def test_load_config_uses_slug_as_final_ordering_tie_breaker(self) -> None:
        from fx_bin.open_launcher import load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Same"
slug = "same-b"
target = "https://b.example"
order = 10

[[items]]
name = "Same"
slug = "same-a"
target = "https://a.example"
order = 10
""".strip(),
                encoding="utf-8",
            )

            config = load_config(config_path)

        self.assertEqual([item.slug for item in config.items], ["same-a", "same-b"])

    def test_load_config_rejects_unknown_item_keys_and_duplicate_slugs(self) -> None:
        from fx_bin.open_launcher import OpenError, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "One"
slug = "same"
target = "https://one.example"
unknown = "typo"
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaises(OpenError):
                load_config(config_path)

            config_path.write_text(
                """
[[items]]
name = "One"
slug = "same"
target = "https://one.example"

[[items]]
name = "Two"
slug = "same"
target = "https://two.example"
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaises(OpenError):
                load_config(config_path)

    def test_default_config_path_respects_xdg_config_home(self) -> None:
        from fx_bin.open_launcher import default_config_path

        with tempfile.TemporaryDirectory() as temp_dir:
            path = default_config_path(
                platform_name="linux",
                environ={"XDG_CONFIG_HOME": temp_dir},
                home=Path("/home/frank"),
            )

        self.assertEqual(path, Path(temp_dir) / "fx-bin" / "open.toml")

    def test_default_config_path_macos_fallback(self) -> None:
        from fx_bin.open_launcher import default_config_path

        path = default_config_path(
            platform_name="darwin",
            environ={},
            home=Path("/Users/frank"),
        )

        self.assertEqual(path, Path("/Users/frank/.config/fx-bin/open.toml"))

    def test_load_config_rejects_dash_prefixed_browser(self) -> None:
        from fx_bin.open_launcher import OpenError, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Bad Browser"
slug = "bad-browser"
target = "https://example.com"
browser = "-Firefox"
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaises(OpenError):
                load_config(config_path)


class TestSelectorResolution(unittest.TestCase):
    """Test deterministic selector resolution."""

    def test_exact_slug_wins_over_bare_local_file(self) -> None:
        from fx_bin.open_launcher import OpenConfig, OpenItem, resolve_launch_target

        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            (cwd / "readme").write_text("local", encoding="utf-8")
            config = OpenConfig(
                [
                    OpenItem(
                        name="Configured Readme",
                        slug="readme",
                        target="https://docs.example",
                    )
                ]
            )

            target = resolve_launch_target("readme", config.items, cwd=cwd)

        self.assertEqual(target.target, "https://docs.example")
        self.assertEqual(target.label, "Configured Readme")

    def test_mixed_case_https_scheme_resolves_as_url(self) -> None:
        from fx_bin.open_launcher import resolve_launch_target

        target = resolve_launch_target("HTTPS://example.com/path", [])

        self.assertEqual(target.target, "HTTPS://example.com/path")
        self.assertEqual(target.label, "HTTPS://example.com/path")

    def test_bare_local_file_with_colon_resolves_as_path(self) -> None:
        from fx_bin.open_launcher import resolve_launch_target

        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            file_path = cwd / "report:2026.txt"
            file_path.write_text("report", encoding="utf-8")

            target = resolve_launch_target("report:2026.txt", [], cwd=cwd)

        self.assertEqual(target.target, str(file_path))
        self.assertEqual(target.label, "report:2026.txt")

    def test_index_applies_to_filtered_view(self) -> None:
        from fx_bin.open_launcher import OpenConfig, OpenItem, resolve_launch_target

        config = OpenConfig(
            [
                OpenItem(
                    name="A",
                    slug="a",
                    target="https://a.example",
                    tags=("work",),
                ),
                OpenItem(
                    name="B",
                    slug="b",
                    target="https://b.example",
                    tags=("home",),
                ),
                OpenItem(
                    name="C",
                    slug="c",
                    target="https://c.example",
                    tags=("work",),
                ),
            ]
        )

        target = resolve_launch_target("2", config.items, filter_tags=("work",))

        self.assertEqual(target.slug, "c")

    def test_slug_must_match_filtered_view(self) -> None:
        from fx_bin.open_launcher import OpenConfig, OpenError, OpenItem
        from fx_bin.open_launcher import resolve_launch_target

        config = OpenConfig(
            [
                OpenItem(
                    name="A",
                    slug="a",
                    target="https://a.example",
                    tags=("work",),
                ),
                OpenItem(
                    name="B",
                    slug="b",
                    target="https://b.example",
                    tags=("home",),
                ),
            ]
        )

        target = resolve_launch_target("a", config.items, filter_tags=("work",))
        self.assertEqual(target.slug, "a")

        with self.assertRaises(OpenError):
            resolve_launch_target("b", config.items, filter_tags=("work",))

    def test_unsupported_scheme_is_rejected(self) -> None:
        from fx_bin.open_launcher import OpenError, resolve_launch_target

        with self.assertRaises(OpenError):
            resolve_launch_target("javascript:alert(1)", [])

        with self.assertRaises(OpenError):
            resolve_launch_target("data:text/html,<h1>hello</h1>", [])

        with self.assertRaises(OpenError):
            resolve_launch_target("file:///tmp/test.png", [])

    def test_listing_120_entries_is_fast_and_indexed(self) -> None:
        from fx_bin.open_launcher import OpenItem, format_items, filter_items

        items = [
            OpenItem(
                name=f"Item {index:03d}",
                slug=f"item-{index:03d}",
                target=f"https://{index}.example",
                order=index,
            )
            for index in range(120, 0, -1)
        ]

        start = time.perf_counter()
        output = format_items(filter_items(items))
        elapsed = time.perf_counter() - start

        self.assertIn("1. Item 001 [item-001]", output)
        self.assertIn("120. Item 120 [item-120]", output)
        self.assertLess(elapsed, 0.5)


class TestAddWorkflow(unittest.TestCase):
    """Test add workflow metadata and TOML append behavior."""

    def test_build_new_item_generates_yahoo_slug(self) -> None:
        from fx_bin.open_launcher import build_new_item

        item = build_new_item("https://www.yahoo.co.jp", [], tags=("portal",))

        self.assertEqual(item.slug, "yahoo-co-jp")
        self.assertEqual(item.name, "Yahoo Co Jp")
        self.assertEqual(item.tags, ("portal",))

    def test_build_new_item_normalizes_bare_domain_to_https_url(self) -> None:
        from fx_bin.open_launcher import build_new_item

        item = build_new_item("yahoo.co.jp", [])

        self.assertEqual(item.target, "https://yahoo.co.jp")
        self.assertEqual(item.slug, "yahoo-co-jp")

    def test_build_new_item_accepts_mixed_case_https_scheme(self) -> None:
        from fx_bin.open_launcher import build_new_item

        item = build_new_item("HTTPS://example.com/path", [])

        self.assertEqual(item.target, "HTTPS://example.com/path")
        self.assertEqual(item.slug, "example-com")

    def test_build_new_item_rejects_empty_provided_slug_and_name(self) -> None:
        from fx_bin.open_launcher import OpenError, build_new_item

        with self.assertRaisesRegex(OpenError, "Slug must be non-empty"):
            build_new_item("https://example.com", [], slug="")

        with self.assertRaisesRegex(OpenError, "Name must be non-empty"):
            build_new_item("https://example.com", [], name="")

    def test_build_new_item_normalizes_existing_local_file(
        self,
    ) -> None:
        from fx_bin.open_launcher import build_new_item

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "notes.md"
            file_path.write_text("notes", encoding="utf-8")

            item = build_new_item(str(file_path), [])

        self.assertEqual(item.target, str(file_path.resolve()))

    def test_build_new_item_normalizes_bare_colon_file(self) -> None:
        from fx_bin.open_launcher import build_new_item

        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            file_path = cwd / "report:2026.txt"
            file_path.write_text("report", encoding="utf-8")

            old_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                item = build_new_item("report:2026.txt", [])
            finally:
                os.chdir(old_cwd)

        self.assertEqual(item.target, str(file_path.resolve()))
        self.assertEqual(item.slug, "report-2026")

    def test_append_item_writes_valid_toml_with_escaping(self) -> None:
        from fx_bin.open_launcher import OpenItem, append_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            item = OpenItem(
                name='Docs "Main"',
                slug="docs-main",
                target="https://example.com/docs?x=1",
                order=10,
                tags=("docs", "line\nbreak"),
            )

            append_item(config_path, item)
            config = load_config(config_path)

        self.assertEqual(config.items[0].name, 'Docs "Main"')
        self.assertEqual(config.items[0].tags, ("docs", "line\nbreak"))

    def test_append_item_preserves_windows_backslashes(self) -> None:
        from fx_bin.open_launcher import OpenItem, append_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            item = OpenItem(
                name="Windows File",
                slug="windows-file",
                target=r"C:\work\file.png",
                order=10,
            )

            append_item(config_path, item)
            config = load_config(config_path)

        self.assertEqual(config.items[0].target, r"C:\work\file.png")

    def test_append_item_allows_duplicate_targets_rejects_duplicate_slug(
        self,
    ) -> None:
        from fx_bin.open_launcher import OpenError, OpenItem, append_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            append_item(
                config_path,
                OpenItem(name="One", slug="one", target="https://example.com"),
            )
            append_item(
                config_path,
                OpenItem(name="Two", slug="two", target="https://example.com"),
            )

            config = load_config(config_path)
            self.assertEqual([item.slug for item in config.items], ["one", "two"])

            with self.assertRaises(OpenError):
                append_item(
                    config_path,
                    OpenItem(name="Again", slug="one", target="https://again.example"),
                )

    def test_append_item_assigns_stale_prebuilt_add_order_under_lock(self) -> None:
        from fx_bin.open_launcher import append_item, build_new_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            first = build_new_item("https://one.example", [])
            second = build_new_item("https://two.example", [])

            written_first = append_item(config_path, first)
            written_second = append_item(config_path, second)
            config = load_config(config_path)

        self.assertEqual(first.order, 0)
        self.assertEqual(second.order, 0)
        self.assertEqual(written_first.order, 10)
        self.assertEqual(written_second.order, 20)
        self.assertEqual(
            [(item.slug, item.order) for item in config.items],
            [("one-example", 10), ("two-example", 20)],
        )

    def test_append_item_rejects_active_lock_without_removing_it(self) -> None:
        from fx_bin.open_launcher import OpenError, OpenItem, append_item

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            lock_path = config_path.with_name("open.toml.lock")
            lock_path.write_text("locked", encoding="utf-8")

            with self.assertRaises(OpenError):
                append_item(
                    config_path,
                    OpenItem(name="One", slug="one", target="https://one.example"),
                )

            self.assertTrue(lock_path.exists())

    def test_append_item_replaces_stale_lock(self) -> None:
        from fx_bin.open_launcher import OpenItem, append_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            lock_path = config_path.with_name("open.toml.lock")
            lock_path.write_text("stale", encoding="utf-8")
            old_time = time.time() - 700
            os.utime(lock_path, (old_time, old_time))

            append_item(
                config_path,
                OpenItem(name="One", slug="one", target="https://one.example"),
            )
            config = load_config(config_path)

        self.assertEqual(config.items[0].slug, "one")


class TestDispatchPlanning(unittest.TestCase):
    """Test opener dispatch plans without launching applications."""

    def test_macos_browser_override_uses_open_app_argument_vector(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, build_dispatch_plan

        plan = build_dispatch_plan(
            LaunchTarget(label="Docs", target="https://example.com", slug="docs"),
            browser="Google Chrome",
            platform_name="darwin",
        )

        self.assertEqual(
            plan.args,
            ("open", "-a", "Google Chrome", "https://example.com"),
        )
        self.assertFalse(plan.shell)

    def test_app_name_starting_with_dash_is_rejected(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "image.png"
            file_path.write_text("png", encoding="utf-8")

            with self.assertRaises(OpenError):
                build_dispatch_plan(
                    LaunchTarget(label="Image", target=str(file_path), slug=None),
                    app="-Preview",
                    platform_name="darwin",
                )

    def test_linux_missing_xdg_open_is_clear_error(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with self.assertRaises(OpenError):
            build_dispatch_plan(
                LaunchTarget(label="Docs", target="https://example.com", slug="docs"),
                platform_name="linux",
                opener_lookup=lambda name: None,
            )

    def test_linux_ignores_saved_browser_for_url_target(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, build_dispatch_plan

        plan = build_dispatch_plan(
            LaunchTarget(
                label="Docs",
                target="https://example.com",
                slug="docs",
                browser="Firefox",
            ),
            platform_name="linux",
            opener_lookup=lambda name: "/usr/bin/xdg-open",
        )

        self.assertEqual(plan.args, ("/usr/bin/xdg-open", "https://example.com"))

    def test_linux_explicit_browser_override_is_rejected(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with self.assertRaises(OpenError):
            build_dispatch_plan(
                LaunchTarget(label="Docs", target="https://example.com", slug="docs"),
                browser="Firefox",
                platform_name="linux",
                opener_lookup=lambda name: "/usr/bin/xdg-open",
            )

    def test_browser_override_rejected_for_local_target(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "image.png"
            file_path.write_text("png", encoding="utf-8")

            with self.assertRaises(OpenError):
                build_dispatch_plan(
                    LaunchTarget(label="Image", target=str(file_path), slug=None),
                    browser="Firefox",
                    platform_name="darwin",
                )

    def test_file_scheme_is_rejected_before_dispatch(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with self.assertRaises(OpenError):
            build_dispatch_plan(
                LaunchTarget(label="Local", target="file:///tmp/test.png", slug=None),
                platform_name="darwin",
            )

    def test_expanduser_failure_returns_open_error(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with patch(
            "fx_bin.open_launcher.Path.expanduser",
            side_effect=RuntimeError("Could not determine home directory"),
        ):
            with self.assertRaisesRegex(OpenError, "Local path cannot be opened"):
                build_dispatch_plan(
                    LaunchTarget(label="Local", target="~/missing.png", slug=None),
                    platform_name="darwin",
                )


class TestAiMetadata(unittest.TestCase):
    """Test optional AI metadata provider handling."""

    def test_ai_invalid_json_returns_open_error(self) -> None:
        from fx_bin.open_launcher import OpenError, request_ai_metadata

        class Result:
            returncode = 0
            stdout = "not-json"
            stderr = ""

        with patch("fx_bin.open_launcher.subprocess.run", return_value=Result()):
            with self.assertRaises(OpenError):
                request_ai_metadata(
                    "https://example.com",
                    existing_slugs=("example",),
                    command="fake-ai",
                )

    def test_ai_timeout_returns_open_error(self) -> None:
        from subprocess import TimeoutExpired

        from fx_bin.open_launcher import OpenError, request_ai_metadata

        with patch(
            "fx_bin.open_launcher.subprocess.run",
            side_effect=TimeoutExpired("fake-ai", 10),
        ):
            with self.assertRaises(OpenError):
                request_ai_metadata(
                    "https://example.com",
                    existing_slugs=(),
                    command="fake-ai",
                )

    def test_ai_command_split_error_returns_open_error(self) -> None:
        from fx_bin.open_launcher import OpenError, request_ai_metadata

        with self.assertRaises(OpenError):
            request_ai_metadata(
                "https://example.com",
                existing_slugs=(),
                command="echo 'unclosed",
            )

    def test_ai_whitespace_command_returns_open_error(self) -> None:
        from fx_bin.open_launcher import OpenError, request_ai_metadata

        with patch("fx_bin.open_launcher.subprocess.run") as run:
            with self.assertRaisesRegex(OpenError, "FX_OPEN_AI_COMMAND"):
                request_ai_metadata(
                    "https://example.com",
                    existing_slugs=(),
                    command="   ",
                )

        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

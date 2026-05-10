"""Unit tests for the fx open launcher."""

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import table_cells


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

    def test_load_config_parses_disabled_field_and_default_filter_hides_it(
        self,
    ) -> None:
        from fx_bin.open_launcher import filter_items, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Enabled"
slug = "enabled"
target = "https://enabled.example"

[[items]]
name = "Disabled"
slug = "old"
target = "https://disabled.example"
disabled = true
""".strip(),
                encoding="utf-8",
            )

            config = load_config(config_path)

        by_slug = {item.slug: item for item in config.items}
        self.assertFalse(by_slug["enabled"].disabled)
        self.assertTrue(by_slug["old"].disabled)
        self.assertEqual(
            [item.slug for item in filter_items(config.items)], ["enabled"]
        )
        self.assertEqual(
            [item.slug for item in filter_items(config.items, visibility="disabled")],
            ["old"],
        )

    def test_load_config_reports_new_reserved_disable_slug_with_rename_guidance(
        self,
    ) -> None:
        from fx_bin.open_launcher import OpenError, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Disable"
slug = "disable"
target = "https://example.com"
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(OpenError, "Rename slug 'disable'"):
                load_config(config_path)

    def test_load_config_reports_new_reserved_search_slug_with_rename_guidance(
        self,
    ) -> None:
        from fx_bin.open_launcher import OpenError, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Search"
slug = "search"
target = "https://example.com"
""".strip(),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(OpenError, "Rename slug 'search'"):
                load_config(config_path)


class TestSearchItems(unittest.TestCase):
    """Test keyword search over saved launcher entries."""

    def test_search_matches_name_slug_tags_and_target(self) -> None:
        from fx_bin.open_launcher import OpenItem, search_items

        items = [
            OpenItem(
                name="Claude Code Usage",
                slug="cc-usage",
                target="https://claude.ai/settings/usage",
                tags=("claude", "usage"),
            ),
            OpenItem(
                name="SportPlus Snooker",
                slug="sportplus-snooker",
                target="https://en97.sportplus.live/snooker/",
                tags=("sports", "live"),
            ),
            OpenItem(
                name="Yahoo",
                slug="yahoo-jp",
                target="https://www.yahoo.co.jp",
                tags=("portal", "japan"),
            ),
        ]

        self.assertEqual(
            [item.slug for item in search_items(items, "claude")],
            ["cc-usage"],
        )
        self.assertEqual(
            [item.slug for item in search_items(items, "sportplus")],
            ["sportplus-snooker"],
        )
        self.assertEqual(
            [item.slug for item in search_items(items, "japan")],
            ["yahoo-jp"],
        )
        self.assertEqual(
            [item.slug for item in search_items(items, "en97")],
            ["sportplus-snooker"],
        )

    def test_search_is_case_insensitive_and_composes_with_tags(self) -> None:
        from fx_bin.open_launcher import OpenItem, search_items

        items = [
            OpenItem(
                name="Claude Usage",
                slug="claude-usage",
                target="https://claude.ai/settings/usage",
                tags=("claude", "usage"),
            ),
            OpenItem(
                name="DeepSeek Usage",
                slug="deepseek-usage",
                target="https://platform.deepseek.com/usage",
                tags=("deepseek", "usage"),
            ),
        ]

        self.assertEqual(
            [item.slug for item in search_items(items, "USAGE")],
            ["claude-usage", "deepseek-usage"],
        )
        self.assertEqual(
            [item.slug for item in search_items(items, "usage", ("deepseek",))],
            ["deepseek-usage"],
        )

    def test_search_respects_visibility_and_returns_no_matches(self) -> None:
        from fx_bin.open_launcher import OpenItem, search_items

        items = [
            OpenItem(
                name="Old Usage",
                slug="old-usage",
                target="https://old.example/usage",
                tags=("usage",),
                disabled=True,
            )
        ]

        self.assertEqual(search_items(items, "usage"), [])
        self.assertEqual(
            [item.slug for item in search_items(items, "usage", visibility="all")],
            ["old-usage"],
        )

    def test_search_indexed_items_preserves_visible_list_indices(self) -> None:
        from fx_bin.open_launcher import OpenItem, search_indexed_items

        items = [
            OpenItem(name="Alpha", slug="alpha", target="https://alpha.example"),
            OpenItem(name="Beta", slug="beta", target="https://beta.example"),
            OpenItem(name="Gamma", slug="gamma", target="https://gamma.example"),
        ]

        matches = search_indexed_items(items, "gamma")

        self.assertEqual(
            [(index, item.slug) for index, item in matches], [(3, "gamma")]
        )


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

    def test_disabled_slug_is_not_opened_by_default(self) -> None:
        from fx_bin.open_launcher import OpenError, OpenItem, resolve_launch_target

        with self.assertRaisesRegex(OpenError, "disabled"):
            resolve_launch_target(
                "old",
                [
                    OpenItem(
                        name="Old",
                        slug="old",
                        target="https://old.example",
                        disabled=True,
                    )
                ],
            )

    def test_disabled_slug_allows_same_named_local_path_fallback(self) -> None:
        from fx_bin.open_launcher import OpenItem, resolve_launch_target

        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = Path(temp_dir)
            local_path = cwd / "old"
            local_path.write_text("local", encoding="utf-8")

            target = resolve_launch_target(
                "old",
                [
                    OpenItem(
                        name="Old",
                        slug="old",
                        target="https://old.example",
                        disabled=True,
                    )
                ],
                cwd=cwd,
            )

        self.assertEqual(target.target, str(local_path))
        self.assertEqual(target.label, "old")

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

        self.assertIn("| 1   | item-001", output)
        self.assertIn("| 120 | item-120", output)
        self.assertLess(elapsed, 0.5)

    def test_format_items_renders_one_line_ascii_table_rows(self) -> None:
        from fx_bin.open_launcher import OpenItem, format_items

        output = format_items(
            [
                OpenItem(
                    name="Claude Code usage",
                    slug="cc-usage",
                    target="https://example.com/usage",
                    order=10,
                    tags=("usage", "claude-code"),
                ),
                OpenItem(
                    name="Yahoo",
                    slug="yahoo",
                    target="https://yahoo.co.jp",
                    order=20,
                ),
            ],
            terminal_width=100,
        )

        lines = output.splitlines()
        self.assertTrue(lines[0].startswith("+"))
        self.assertEqual(table_cells(lines[1])[:3], ["#", "Slug", "Name"])
        self.assertIn("| Target", lines[1])
        self.assertEqual(sum("https://" in line for line in lines), 2)
        self.assertNotIn("target:", output)
        self.assertNotIn("tags:", output)

    def test_format_items_truncates_long_target_to_terminal_width(self) -> None:
        from fx_bin.open_launcher import OpenItem, format_items

        output = format_items(
            [
                OpenItem(
                    name="Long target",
                    slug="long-target",
                    target="https://example.com/" + "very-long-path/" * 10,
                    order=10,
                    tags=("docs",),
                )
            ],
            terminal_width=72,
        )

        self.assertTrue(all(len(line) <= 72 for line in output.splitlines()))
        self.assertIn("...", output)

    def test_format_items_preserves_slug_second_in_narrow_terminal(self) -> None:
        from fx_bin.open_launcher import OpenItem, format_items

        output = format_items(
            [
                OpenItem(
                    name="Codex Cloud Analytics",
                    slug="cx",
                    target="https://chatgpt.com/codex/cloud/settings/analytics",
                    tags=("codex", "analytics"),
                ),
                OpenItem(
                    name="SportPlus Snooker",
                    slug="sp",
                    target="https://en97.sportplus.live/snooker/",
                    tags=("sports", "live"),
                ),
            ],
            terminal_width=60,
        )

        lines = output.splitlines()
        self.assertEqual(table_cells(lines[1])[:3], ["#", "Slug", "Name"])
        self.assertTrue(all(len(line) <= 60 for line in lines))

    def test_format_items_shrinks_target_before_slug_name_tags(self) -> None:
        """Regression for #68: narrow terminal + long URL must keep Slug/Name/Tags
        at natural width and truncate Target instead."""
        from fx_bin.open_launcher import OpenItem, format_items

        items = [
            OpenItem(
                name="Codex Cloud Analytics",
                slug="codex-analytics",
                target="https://chatgpt.com/codex/cloud/settings/analytics/very/long/path",
                tags=("codex", "analytics"),
            ),
        ]
        output = format_items(items, terminal_width=80)

        lines = output.splitlines()
        cells = [table_cells(line) for line in lines if line.startswith("|")]
        header_cells = cells[0]
        row_cells = cells[1]

        slug_col = header_cells.index("Slug")
        name_col = header_cells.index("Name")
        tags_col = header_cells.index("Tags")
        target_col = header_cells.index("Target")

        self.assertEqual(row_cells[slug_col], "codex-analytics")
        self.assertEqual(row_cells[name_col], "Codex Cloud Analytics")
        self.assertEqual(row_cells[tags_col], "codex, analytics")
        self.assertTrue(row_cells[target_col].endswith("..."))
        self.assertTrue(all(len(line) <= 80 for line in lines))

    def test_format_items_sanitizes_control_chars_and_handles_wide_text(self) -> None:
        from fx_bin.open_launcher import OpenItem, format_items

        output = format_items(
            [
                OpenItem(
                    name="中文文档\nbeta",
                    slug="zh-docs",
                    target="https://example.com/中文/文档",
                    order=10,
                    tags=("资料\t测试",),
                )
            ],
            terminal_width=80,
        )

        lines = output.splitlines()
        self.assertEqual(sum("zh-docs" in line for line in lines), 1)
        self.assertIn("中文文档 beta", output)
        self.assertIn("资料 测试", output)
        self.assertTrue(all(len(line) <= 80 for line in lines))


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

    def test_delete_item_removes_slug_and_preserves_remaining_item(self) -> None:
        from fx_bin.open_launcher import OpenItem, append_item, delete_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            append_item(
                config_path,
                OpenItem(
                    name="One",
                    slug="one",
                    target="https://one.example",
                    order=10,
                    tags=("docs",),
                    browser="Firefox",
                ),
            )
            append_item(
                config_path,
                OpenItem(name="Two", slug="two", target="https://two.example"),
            )

            deleted = delete_item(config_path, "one")
            config = load_config(config_path)

        self.assertEqual(deleted.slug, "one")
        self.assertEqual([item.slug for item in config.items], ["two"])
        self.assertEqual(config.items[0].target, "https://two.example")

    def test_delete_item_uses_filtered_index_view(self) -> None:
        from fx_bin.open_launcher import OpenItem, append_item, delete_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            append_item(
                config_path,
                OpenItem(
                    name="A",
                    slug="a",
                    target="https://a.example",
                    order=10,
                    tags=("work",),
                ),
            )
            append_item(
                config_path,
                OpenItem(
                    name="B",
                    slug="b",
                    target="https://b.example",
                    order=20,
                    tags=("home",),
                ),
            )
            append_item(
                config_path,
                OpenItem(
                    name="C",
                    slug="c",
                    target="https://c.example",
                    order=30,
                    tags=("work",),
                ),
            )

            deleted = delete_item(config_path, "2", filter_tags=("work",))
            config = load_config(config_path)

        self.assertEqual(deleted.slug, "c")
        self.assertEqual([item.slug for item in config.items], ["a", "b"])

    def test_delete_item_writes_empty_config_after_last_item(self) -> None:
        from fx_bin.open_launcher import OpenItem, append_item, delete_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            append_item(
                config_path,
                OpenItem(name="One", slug="one", target="https://one.example"),
            )

            delete_item(config_path, "one")
            config = load_config(config_path)
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(config.items, [])
        self.assertEqual(content, "")

    def test_mutation_preserves_non_item_top_level_config(self) -> None:
        from fx_bin.open_launcher import delete_item, load_config

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
version = 1
title = "Launcher"

[metadata]
owner = "Frank"
active = true

[[items]]
name = "One"
slug = "one"
target = "https://one.example"
order = 10

[[items]]
name = "Two"
slug = "two"
target = "https://two.example"
order = 20
""".strip(),
                encoding="utf-8",
            )

            deleted = delete_item(config_path, "one")
            config = load_config(config_path)
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(deleted.slug, "one")
        self.assertEqual([item.slug for item in config.items], ["two"])
        self.assertIn("version = 1", content)
        self.assertIn('title = "Launcher"', content)
        self.assertIn("[metadata]", content)
        self.assertIn('owner = "Frank"', content)
        self.assertIn("active = true", content)

    def test_delete_item_rejects_direct_url_without_changing_config(self) -> None:
        from fx_bin.open_launcher import OpenError, OpenItem, append_item, delete_item

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            append_item(
                config_path,
                OpenItem(name="One", slug="one", target="https://one.example"),
            )
            before = config_path.read_text(encoding="utf-8")

            with self.assertRaises(OpenError):
                delete_item(config_path, "https://one.example")

            after = config_path.read_text(encoding="utf-8")

        self.assertEqual(after, before)

    def test_disable_item_hides_entry_and_enable_restores_it(self) -> None:
        from fx_bin.open_launcher import (
            OpenItem,
            append_item,
            disable_item,
            enable_item,
            filter_items,
            load_config,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            append_item(
                config_path,
                OpenItem(name="One", slug="one", target="https://one.example"),
            )

            disabled = disable_item(config_path, "one")
            disabled_config = load_config(config_path)
            enabled = enable_item(config_path, "1")
            enabled_config = load_config(config_path)
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(disabled.slug, "one")
        self.assertTrue(disabled.disabled)
        self.assertEqual(filter_items(disabled_config.items), [])
        self.assertEqual(
            [
                item.slug
                for item in filter_items(disabled_config.items, visibility="disabled")
            ],
            ["one"],
        )
        self.assertEqual(enabled.slug, "one")
        self.assertFalse(enabled.disabled)
        self.assertEqual(
            [item.slug for item in filter_items(enabled_config.items)], ["one"]
        )
        self.assertNotIn("disabled = false", content)

    def test_format_items_shows_disabled_state_when_present(self) -> None:
        from fx_bin.open_launcher import OpenItem, format_items

        output = format_items(
            [
                OpenItem(
                    name="Old",
                    slug="old",
                    target="https://old.example",
                    disabled=True,
                )
            ],
            terminal_width=100,
        )

        self.assertEqual(
            table_cells(output.splitlines()[1])[:4],
            ["#", "Slug", "State", "Name"],
        )
        self.assertIn("disabled", output)


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


class TestDirectorySupport(unittest.TestCase):
    """Test directory target support."""

    def test_normalize_local_path_accepts_directory(self) -> None:
        from fx_bin.open_launcher import _normalize_local_path

        with tempfile.TemporaryDirectory() as temp_dir:
            result = _normalize_local_path(temp_dir)

        self.assertEqual(result, str(Path(temp_dir).resolve()))

    def test_build_new_item_normalizes_existing_directory(self) -> None:
        from fx_bin.open_launcher import build_new_item

        with tempfile.TemporaryDirectory() as temp_dir:
            item = build_new_item(str(temp_dir), [])

        self.assertEqual(item.target, str(Path(temp_dir).resolve()))

    def test_build_dispatch_plan_directory_on_macos(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, build_dispatch_plan

        with tempfile.TemporaryDirectory() as temp_dir:
            plan = build_dispatch_plan(
                LaunchTarget(label="Dir", target=temp_dir, slug=None),
                platform_name="darwin",
            )

        self.assertEqual(plan.args, ("open", str(Path(temp_dir).resolve())))
        self.assertFalse(plan.shell)

    def test_build_dispatch_plan_directory_rejected_on_linux(self) -> None:
        from fx_bin.open_launcher import LaunchTarget, OpenError, build_dispatch_plan

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(
                OpenError, "Opening local directories is only supported on macOS"
            ):
                build_dispatch_plan(
                    LaunchTarget(label="Dir", target=temp_dir, slug=None),
                    platform_name="linux",
                    opener_lookup=lambda name: "/usr/bin/xdg-open",
                )

    def test_classify_target_kind_returns_path_for_directory(self) -> None:
        from fx_bin.open_launcher import classify_target_kind

        with tempfile.TemporaryDirectory() as temp_dir:
            kind = classify_target_kind(temp_dir)

        self.assertEqual(kind, "path")


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

    def test_ai_windows_command_preserves_quoted_program_files_path(self) -> None:
        from fx_bin.open_launcher import request_ai_metadata

        class Result:
            returncode = 0
            stdout = '{"name":"Example"}'
            stderr = ""

        with patch("fx_bin.open_launcher.subprocess.run", return_value=Result()) as run:
            request_ai_metadata(
                "https://example.com",
                existing_slugs=(),
                command=(
                    r'"C:\Program Files\Fx AI\provider.exe" '
                    r'--mode json --label "two words"'
                ),
                platform_name="win32",
            )

        argv = run.call_args.args[0]
        self.assertEqual(
            argv,
            [
                r"C:\Program Files\Fx AI\provider.exe",
                "--mode",
                "json",
                "--label",
                "two words",
            ],
        )

    def test_ai_windows_command_merges_unquoted_executable_path(self) -> None:
        from fx_bin.open_launcher import request_ai_metadata

        class Result:
            returncode = 0
            stdout = '{"slug":"example"}'
            stderr = ""

        with patch("fx_bin.open_launcher.subprocess.run", return_value=Result()) as run:
            request_ai_metadata(
                "https://example.com",
                existing_slugs=(),
                command=r"C:\Program Files\Fx AI\provider.exe --mode json",
                platform_name="win32",
            )

        argv = run.call_args.args[0]
        self.assertEqual(
            argv,
            [r"C:\Program Files\Fx AI\provider.exe", "--mode", "json"],
        )


if __name__ == "__main__":
    unittest.main()

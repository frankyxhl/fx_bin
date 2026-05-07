"""Integration tests for the fx open CLI."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from fx_bin.cli import cli
from tests.helpers import table_cells


class TestOpenCli(unittest.TestCase):
    """Test the fx open command boundary."""

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_help_documents_ai_and_add_options(self) -> None:
        result = self.runner.invoke(cli, ["open", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("fx open search usage", result.output)
        self.assertIn("fx open add yahoo.co.jp", result.output)
        self.assertIn("--entry-tag", result.output)
        self.assertIn("--ai", result.output)
        self.assertIn("FX_OPEN_AI_COMMAND", result.output)

    def test_missing_config_lists_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "missing.toml"

            result = self.runner.invoke(cli, ["open", "--config", str(config_path)])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("No saved open targets", result.output)
        self.assertIn("fx open add", result.output)

    def test_list_config_outputs_1_based_indices(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Claude Code usage"
slug = "cc-usage"
target = "https://example.com/usage"
order = 10
tags = ["usage", "claude-code"]
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(cli, ["open", "--config", str(config_path)])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            table_cells(result.output.splitlines()[1])[:3],
            ["#", "Slug", "Name"],
        )
        self.assertIn("cc-usage", result.output)
        self.assertIn("usage", result.output)
        self.assertNotIn("target:", result.output)

    def test_tag_filtered_list_uses_slug_second_column_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Claude Usage"
slug = "cl"
target = "https://claude.ai/settings/usage"
tags = ["usage", "claude"]

[[items]]
name = "SportPlus Snooker"
slug = "sp"
target = "https://en97.sportplus.live/snooker/"
tags = ["sports", "live"]
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli, ["open", "--config", str(config_path), "--tag", "sports"]
            )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            table_cells(result.output.splitlines()[1])[:3],
            ["#", "Slug", "Name"],
        )
        self.assertIn("| 1 | sp", result.output)
        self.assertIn("SportPlus Snooker", result.output)
        self.assertNotIn("Claude Usage", result.output)

    def test_search_lists_case_insensitive_keyword_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Claude Usage"
slug = "claude-usage"
target = "https://claude.ai/settings/usage"
tags = ["claude", "usage"]

[[items]]
name = "SportPlus Snooker"
slug = "sportplus-snooker"
target = "https://en97.sportplus.live/snooker/"
tags = ["sports", "live"]
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli, ["open", "--config", str(config_path), "search", "SNOOKER"]
            )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            table_cells(result.output.splitlines()[1])[:3],
            ["#", "Slug", "Name"],
        )
        self.assertIn("| 2 | sportplus-snooker", result.output)
        self.assertIn("https://en97.sportplus.live/snooker/", result.output)
        self.assertNotIn("claude-usage", result.output)

    def test_search_requires_query(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli, ["open", "--config", str(config_path), "search"]
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Usage is fx open search QUERY", result.output)

    def test_search_composes_with_tag_filter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Claude Usage"
slug = "claude-usage"
target = "https://claude.ai/settings/usage"
tags = ["claude", "usage"]

[[items]]
name = "DeepSeek Usage"
slug = "deepseek-usage"
target = "https://platform.deepseek.com/usage"
tags = ["deepseek", "usage"]
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "search",
                    "--tag",
                    "deepseek",
                    "usage",
                ],
            )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            table_cells(result.output.splitlines()[1])[:3],
            ["#", "Slug", "Name"],
        )
        self.assertIn("deepseek-usage", result.output)
        self.assertIn("https://platform.deepseek.com/usage", result.output)
        self.assertNotIn("claude-usage", result.output)

    def test_search_no_match_outputs_helpful_message(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Claude Usage"
slug = "claude-usage"
target = "https://claude.ai/settings/usage"
tags = ["claude", "usage"]
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli, ["open", "--config", str(config_path), "search", "missing"]
            )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("No saved open targets matched query: missing", result.output)
        self.assertNotIn("claude-usage", result.output)

    def test_open_slug_dispatches_without_shell(self) -> None:
        from fx_bin.open_launcher import DispatchPlan

        dispatched = []

        def fake_execute(plan: DispatchPlan) -> None:
            dispatched.append(plan)

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Docs"
slug = "docs"
target = "https://example.com/docs"
""".strip(),
                encoding="utf-8",
            )

            with patch("fx_bin.open_launcher.execute_dispatch_plan", fake_execute):
                result = self.runner.invoke(
                    cli, ["open", "--config", str(config_path), "docs"]
                )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(len(dispatched), 1)
        self.assertIn("https://example.com/docs", dispatched[0].args)
        self.assertFalse(dispatched[0].shell)

    def test_add_requires_yes_in_non_interactive_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "add",
                    "https://example.com",
                ],
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("--yes", result.output)

    def test_add_with_entry_tags_writes_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "add",
                    "https://www.yahoo.co.jp",
                    "--name",
                    "Yahoo! JAPAN",
                    "--slug",
                    "yahoo-jp",
                    "--entry-tag",
                    "portal",
                    "--entry-tag",
                    "japan",
                    "--yes",
                ],
            )

            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Added yahoo-jp", result.output)
        self.assertIn('slug = "yahoo-jp"', content)
        self.assertIn('tags = ["portal", "japan"]', content)

    def test_add_bare_domain_writes_https_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "add",
                    "yahoo.co.jp",
                    "--yes",
                ],
            )

            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn('target = "https://yahoo.co.jp"', content)

    def test_tag_is_invalid_for_add_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "add",
                    "https://example.com",
                    "--tag",
                    "docs",
                    "--yes",
                ],
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("--entry-tag", result.output)

    def test_add_ai_requires_provider_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "add",
                    "https://example.com",
                    "--ai",
                    "--yes",
                ],
                env={"FX_OPEN_AI_COMMAND": ""},
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("FX_OPEN_AI_COMMAND", result.output)

    def test_delete_slug_requires_yes_in_non_interactive_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Docs"
slug = "docs"
target = "https://example.com/docs"
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli,
                ["open", "--config", str(config_path), "delete", "docs"],
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("--yes", result.output)

    def test_delete_slug_removes_config_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Docs"
slug = "docs"
target = "https://example.com/docs"

[[items]]
name = "Usage"
slug = "usage"
target = "https://example.com/usage"
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli,
                ["open", "--config", str(config_path), "delete", "docs", "--yes"],
            )
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Deleted docs", result.output)
        self.assertNotIn('slug = "docs"', content)
        self.assertIn('slug = "usage"', content)

    def test_delete_uses_tag_filtered_index_view(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Personal"
slug = "personal"
target = "https://example.com/personal"
order = 10
tags = ["personal"]

[[items]]
name = "Work"
slug = "work"
target = "https://example.com/work"
order = 20
tags = ["work"]
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "--tag",
                    "work",
                    "delete",
                    "1",
                    "--yes",
                ],
            )
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Deleted work", result.output)
        self.assertIn('slug = "personal"', content)
        self.assertNotIn('slug = "work"', content)

    def test_delete_index_mutation_uses_confirmed_slug(self) -> None:
        from fx_bin.open_launcher import OpenItem

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "One"
slug = "one"
target = "https://example.com/one"
order = 10

[[items]]
name = "Two"
slug = "two"
target = "https://example.com/two"
order = 20
""".strip(),
                encoding="utf-8",
            )

            with patch("fx_bin.open_launcher.delete_item") as delete_item:
                delete_item.return_value = OpenItem(
                    name="Two",
                    slug="two",
                    target="https://example.com/two",
                )
                result = self.runner.invoke(
                    cli,
                    ["open", "--config", str(config_path), "delete", "2", "--yes"],
                )

        self.assertEqual(result.exit_code, 0, result.output)
        delete_item.assert_called_once()
        self.assertEqual(delete_item.call_args.args[1], "two")

    def test_delete_disabled_entry_with_disabled_view(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Current"
slug = "current"
target = "https://example.com/current"
tags = ["active"]

[[items]]
name = "Old"
slug = "old"
target = "https://example.com/old"
tags = ["archive"]
disabled = true
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "--disabled",
                    "delete",
                    "old",
                    "--yes",
                ],
            )
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Deleted old", result.output)
        self.assertIn('slug = "current"', content)
        self.assertNotIn('slug = "old"', content)

    def test_delete_rejects_add_only_options(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "delete",
                    "docs",
                    "--slug",
                    "custom",
                    "--yes",
                ],
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("only valid with 'fx open add'", result.output)

    def test_disabled_entries_are_hidden_by_default_and_visible_with_flags(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Current"
slug = "current"
target = "https://example.com/current"
tags = ["active"]

[[items]]
name = "Old"
slug = "old"
target = "https://example.com/old"
tags = ["archive"]
disabled = true
""".strip(),
                encoding="utf-8",
            )

            default_result = self.runner.invoke(
                cli, ["open", "--config", str(config_path)]
            )
            disabled_result = self.runner.invoke(
                cli, ["open", "--config", str(config_path), "--disabled"]
            )
            all_result = self.runner.invoke(
                cli, ["open", "--config", str(config_path), "--all"]
            )
            tag_all_result = self.runner.invoke(
                cli,
                ["open", "--config", str(config_path), "--tag", "archive", "--all"],
            )
            tag_disabled_result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "--tag",
                    "archive",
                    "--disabled",
                ],
            )

        self.assertEqual(default_result.exit_code, 0, default_result.output)
        self.assertEqual(
            table_cells(default_result.output.splitlines()[1])[:3],
            ["#", "Slug", "Name"],
        )
        self.assertEqual(
            table_cells(default_result.output.splitlines()[3])[:3],
            ["1", "current", "Current"],
        )
        self.assertIn("current", default_result.output)
        self.assertNotIn("old", default_result.output)
        self.assertEqual(disabled_result.exit_code, 0, disabled_result.output)
        self.assertEqual(
            table_cells(disabled_result.output.splitlines()[1])[:4],
            ["#", "Slug", "State", "Name"],
        )
        self.assertEqual(
            table_cells(disabled_result.output.splitlines()[3])[:4],
            ["1", "old", "disabled", "Old"],
        )
        self.assertIn("old", disabled_result.output)
        self.assertNotIn("current", disabled_result.output)
        self.assertEqual(all_result.exit_code, 0, all_result.output)
        self.assertEqual(
            table_cells(all_result.output.splitlines()[1])[:4],
            ["#", "Slug", "State", "Name"],
        )
        self.assertEqual(
            table_cells(all_result.output.splitlines()[3])[:4],
            ["1", "current", "", "Current"],
        )
        self.assertEqual(
            table_cells(all_result.output.splitlines()[4])[:4],
            ["2", "old", "disabled", "Old"],
        )
        self.assertIn("current", all_result.output)
        self.assertIn("old", all_result.output)
        self.assertIn("disabled", all_result.output)
        self.assertEqual(tag_all_result.exit_code, 0, tag_all_result.output)
        self.assertEqual(
            table_cells(tag_all_result.output.splitlines()[1])[:4],
            ["#", "Slug", "State", "Name"],
        )
        self.assertEqual(
            table_cells(tag_all_result.output.splitlines()[3])[:4],
            ["1", "old", "disabled", "Old"],
        )
        self.assertIn("old", tag_all_result.output)
        self.assertNotIn("current", tag_all_result.output)
        self.assertEqual(
            tag_disabled_result.exit_code,
            0,
            tag_disabled_result.output,
        )
        self.assertEqual(
            table_cells(tag_disabled_result.output.splitlines()[1])[:4],
            ["#", "Slug", "State", "Name"],
        )
        self.assertEqual(
            table_cells(tag_disabled_result.output.splitlines()[3])[:4],
            ["1", "old", "disabled", "Old"],
        )
        self.assertIn("old", tag_disabled_result.output)
        self.assertNotIn("current", tag_disabled_result.output)

    def test_disable_and_enable_workflows_toggle_entry_visibility(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Docs"
slug = "docs"
target = "https://example.com/docs"
""".strip(),
                encoding="utf-8",
            )

            disable_result = self.runner.invoke(
                cli,
                ["open", "--config", str(config_path), "disable", "docs", "--yes"],
            )
            hidden_result = self.runner.invoke(
                cli, ["open", "--config", str(config_path)]
            )
            enable_result = self.runner.invoke(
                cli,
                ["open", "--config", str(config_path), "enable", "1", "--yes"],
            )
            restored_result = self.runner.invoke(
                cli, ["open", "--config", str(config_path)]
            )
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(disable_result.exit_code, 0, disable_result.output)
        self.assertIn("Disabled docs", disable_result.output)
        self.assertNotIn("docs", hidden_result.output)
        self.assertEqual(enable_result.exit_code, 0, enable_result.output)
        self.assertIn("Enabled docs", enable_result.output)
        self.assertIn("docs", restored_result.output)
        self.assertNotIn("disabled = false", content)

    def test_enable_workflow_accepts_disabled_slug(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Old"
slug = "old"
target = "https://example.com/old"
disabled = true
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli,
                ["open", "--config", str(config_path), "enable", "old", "--yes"],
            )
            restored_result = self.runner.invoke(
                cli, ["open", "--config", str(config_path)]
            )
            content = config_path.read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Enabled old", result.output)
        self.assertIn("old", restored_result.output)
        self.assertNotIn("disabled = true", content)

    def test_toggle_index_mutation_uses_confirmed_slug(self) -> None:
        from fx_bin.open_launcher import OpenItem

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "One"
slug = "one"
target = "https://example.com/one"
order = 10

[[items]]
name = "Two"
slug = "two"
target = "https://example.com/two"
order = 20
""".strip(),
                encoding="utf-8",
            )

            with patch("fx_bin.open_launcher.disable_item") as disable_item:
                disable_item.return_value = OpenItem(
                    name="Two",
                    slug="two",
                    target="https://example.com/two",
                    disabled=True,
                )
                result = self.runner.invoke(
                    cli,
                    ["open", "--config", str(config_path), "disable", "2", "--yes"],
                )

        self.assertEqual(result.exit_code, 0, result.output)
        disable_item.assert_called_once()
        self.assertEqual(disable_item.call_args.args[1], "two")

    def test_visibility_flags_are_invalid_for_open_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            config_path.write_text(
                """
[[items]]
name = "Docs"
slug = "docs"
target = "https://example.com/docs"
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(
                cli, ["open", "--config", str(config_path), "--all", "docs"]
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("--all", result.output)

    def test_visibility_flags_are_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"

            result = self.runner.invoke(
                cli,
                ["open", "--config", str(config_path), "--all", "--disabled"],
            )

        self.assertEqual(result.exit_code, 1)
        self.assertIn("cannot be combined", result.output)

    def test_add_local_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            target_dir = Path(temp_dir) / "my-project"
            target_dir.mkdir()
            resolved_target = str(target_dir.resolve())

            result = self.runner.invoke(
                cli,
                [
                    "open",
                    "--config",
                    str(config_path),
                    "add",
                    str(target_dir),
                    "--name",
                    "My Project",
                    "--slug",
                    "myprj",
                    "--yes",
                ],
            )
            content = config_path.read_text(encoding="utf-8")

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Added myprj", result.output)
            self.assertIn('slug = "myprj"', content)
            self.assertIn(resolved_target, content)

    def test_list_shows_directory_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            target_dir = Path(temp_dir) / "src"
            target_dir.mkdir()
            config_path.write_text(
                f"""
[[items]]
name = "Source"
slug = "src"
target = "{target_dir.resolve()}"
""".strip(),
                encoding="utf-8",
            )

            result = self.runner.invoke(cli, ["open", "--config", str(config_path)])

            self.assertEqual(result.exit_code, 0, result.output)
            cells = table_cells(result.output.splitlines()[3])
            self.assertEqual(cells[1], "src")

    def test_open_directory_dispatches_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "open.toml"
            target_dir = Path(temp_dir) / "src"
            target_dir.mkdir()
            resolved_target = str(target_dir.resolve())
            config_path.write_text(
                f"""
[[items]]
name = "Source"
slug = "src"
target = "{resolved_target}"
""".strip(),
                encoding="utf-8",
            )

            with patch("fx_bin.open_launcher.execute_dispatch_plan") as execute:
                result = self.runner.invoke(
                    cli,
                    ["open", "--config", str(config_path), "src"],
                )

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("Opened Source", result.output)
                execute.assert_called_once()
                plan = execute.call_args.args[0]
                self.assertEqual(plan.args[0], "open")
                self.assertEqual(plan.args[1], resolved_target)


if __name__ == "__main__":
    unittest.main()

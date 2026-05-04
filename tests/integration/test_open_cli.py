"""Integration tests for the fx open CLI."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from fx_bin.cli import cli


class TestOpenCli(unittest.TestCase):
    """Test the fx open command boundary."""

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_help_documents_ai_and_add_options(self) -> None:
        result = self.runner.invoke(cli, ["open", "--help"])

        self.assertEqual(result.exit_code, 0)
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
        self.assertIn("1.", result.output)
        self.assertIn("cc-usage", result.output)
        self.assertIn("usage, claude-code", result.output)

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


if __name__ == "__main__":
    unittest.main()

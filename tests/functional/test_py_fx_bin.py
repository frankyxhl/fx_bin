#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `py_fx_bin` package."""


import unittest
from click.testing import CliRunner

from fx_bin import cli


class TestPy_fx_bin(unittest.TestCase):
    """Tests for `py_fx_bin` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        # Test the Click command group, not the main function
        result = runner.invoke(cli.cli)
        assert result.exit_code == 0
        # The CLI should show help when no command is provided
        assert "FX - A collection of file and text utilities" in result.output

        # Test help command
        help_result = runner.invoke(cli.cli, ["--help"])
        assert help_result.exit_code == 0
        assert "--help" in help_result.output
        assert "Show this message and exit" in help_result.output

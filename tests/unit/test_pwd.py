import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from fx_bin.cli import cli
from fx_bin.errors import ClipboardError
from tests.helpers import stderr_capturing_runner


class TestPwdCommand(unittest.TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.test_dir = os.path.realpath(tempfile.mkdtemp())
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _invoke(self, args, tty=True, env=None):
        with (
            patch("fx_bin.cli._stdout_is_tty", return_value=tty),
            patch("fx_bin.clipboard.copy_to_clipboard") as mock_copy,
        ):
            result = CliRunner().invoke(cli, args, env=env)
        return result, mock_copy

    def test_prints_current_directory(self):
        result, _ = self._invoke(["pwd"], env={"PWD": self.test_dir})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), self.test_dir)

    def test_host_flag_prefixes_host_name(self):
        with patch("socket.gethostname", return_value="box"):
            result, _ = self._invoke(["pwd", "--host"], env={"PWD": self.test_dir})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), "box:" + self.test_dir)

    def test_short_host_flag_matches_long_flag(self):
        with patch("socket.gethostname", return_value="box"):
            result, _ = self._invoke(["pwd", "-H"], env={"PWD": self.test_dir})
        self.assertEqual(result.output.strip(), "box:" + self.test_dir)

    def test_host_name_ignores_environment_variable(self):
        with patch("socket.gethostname", return_value="box"):
            result, _ = self._invoke(
                ["pwd", "--host"],
                env={"PWD": self.test_dir, "HOSTNAME": "other", "HOST": "other"},
            )
        self.assertTrue(result.output.startswith("box:"))

    def test_copies_printed_line_on_tty(self):
        result, mock_copy = self._invoke(["pwd"], env={"PWD": self.test_dir})
        mock_copy.assert_called_once()
        self.assertEqual(mock_copy.call_args[0][0], result.output.strip())

    def test_copies_host_line_on_tty(self):
        with patch("socket.gethostname", return_value="box"):
            result, mock_copy = self._invoke(
                ["pwd", "--host"], env={"PWD": self.test_dir}
            )
        mock_copy.assert_called_once()
        self.assertEqual(mock_copy.call_args[0][0], "box:" + self.test_dir)
        self.assertEqual(mock_copy.call_args[0][0], result.output.strip())

    def test_no_copy_flag_disables_copy(self):
        result, mock_copy = self._invoke(
            ["pwd", "--no-copy"], env={"PWD": self.test_dir}
        )
        self.assertEqual(result.output.strip(), self.test_dir)
        mock_copy.assert_not_called()

    def test_no_copy_flag_disables_copy_with_host(self):
        with patch("socket.gethostname", return_value="box"):
            result, mock_copy = self._invoke(
                ["pwd", "--host", "--no-copy"], env={"PWD": self.test_dir}
            )
        self.assertEqual(result.output.strip(), "box:" + self.test_dir)
        mock_copy.assert_not_called()

    def test_no_copy_when_stdout_not_tty(self):
        result, mock_copy = self._invoke(["pwd"], tty=False, env={"PWD": self.test_dir})
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip(), self.test_dir)
        mock_copy.assert_not_called()

    def test_no_copy_when_stdout_not_tty_with_host(self):
        with patch("socket.gethostname", return_value="box"):
            result, mock_copy = self._invoke(
                ["pwd", "--host"], tty=False, env={"PWD": self.test_dir}
            )
        self.assertEqual(result.output.strip(), "box:" + self.test_dir)
        mock_copy.assert_not_called()

    def test_clipboard_failure_warns_but_exits_zero(self):
        with (
            patch("fx_bin.cli._stdout_is_tty", return_value=True),
            patch(
                "fx_bin.clipboard.copy_to_clipboard",
                side_effect=ClipboardError("no tool"),
            ),
        ):
            result = stderr_capturing_runner().invoke(
                cli, ["pwd"], env={"PWD": self.test_dir}
            )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), self.test_dir)
        self.assertIn("clipboard", result.stderr.lower())

    def test_symlinked_pwd_prints_symlink_path(self):
        link = self.test_dir + "-link"
        os.symlink(self.test_dir, link)
        try:
            result, _ = self._invoke(["pwd"], env={"PWD": link})
        finally:
            os.unlink(link)
        self.assertEqual(result.output.strip(), link)

    def test_stale_pwd_falls_back_to_physical_directory(self):
        other = os.path.realpath(tempfile.mkdtemp())
        try:
            result, _ = self._invoke(["pwd"], env={"PWD": other})
        finally:
            shutil.rmtree(other, ignore_errors=True)
        self.assertEqual(result.output.strip(), self.test_dir)

    def test_relative_pwd_falls_back_to_physical_directory(self):
        result, _ = self._invoke(["pwd"], env={"PWD": "."})
        self.assertEqual(result.output.strip(), self.test_dir)

    def test_listed_in_fx_list(self):
        result, _ = self._invoke(["list"])
        self.assertIn("pwd", result.output)


class TestPwdDeletedDirectory(unittest.TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.gone = os.path.realpath(tempfile.mkdtemp())
        os.chdir(self.gone)
        os.rmdir(self.gone)

    def tearDown(self):
        os.chdir(self.original_cwd)

    def _invoke(self, env):
        with (
            patch("fx_bin.cli._stdout_is_tty", return_value=True),
            patch("fx_bin.clipboard.copy_to_clipboard") as mock_copy,
        ):
            result = stderr_capturing_runner().invoke(cli, ["pwd"], env=env)
        return result, mock_copy

    def test_deleted_directory_with_pwd_unset_exits_one(self):
        result, mock_copy = self._invoke({"PWD": None})
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Cannot determine current directory", result.stderr)
        mock_copy.assert_not_called()

    def test_deleted_directory_with_pwd_still_set_exits_one(self):
        result, mock_copy = self._invoke({"PWD": self.gone})
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Cannot determine current directory", result.stderr)
        mock_copy.assert_not_called()


if __name__ == "__main__":
    unittest.main()

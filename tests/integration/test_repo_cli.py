"""CLI integration tests for ``fx repo``."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from fx_bin.cli import cli
from fx_bin.repo import MISSING_REMOTE


def _git(repository: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "project"
    repository.mkdir()
    _git(repository, "init")
    return repository


def test_repo_opens_origin_from_nested_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    _git(repository, "remote", "add", "fork", "git@github.com:other/fork.git")
    _git(
        repository,
        "remote",
        "add",
        "origin",
        "git@github.com:frankyxhl/fx_bin.git",
    )
    nested = repository / "src" / "nested"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    dispatch_plan = object()

    with (
        patch(
            "fx_bin.open_launcher.build_dispatch_plan",
            return_value=dispatch_plan,
        ) as build,
        patch("fx_bin.open_launcher.execute_dispatch_plan") as execute,
    ):
        result = CliRunner().invoke(cli, ["repo"])

    assert result.exit_code == 0
    assert result.output == "Opening https://github.com/frankyxhl/fx_bin\n"
    launch_target = build.call_args.args[0]
    assert launch_target.target == "https://github.com/frankyxhl/fx_bin"
    execute.assert_called_once_with(dispatch_plan)


def test_repo_explicit_remote_overrides_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    _git(repository, "remote", "add", "origin", "git@github.com:owner/main.git")
    _git(repository, "remote", "add", "fork", "git@github.com:owner/fork.git")
    monkeypatch.chdir(repository)
    dispatch_plan = object()

    with (
        patch(
            "fx_bin.open_launcher.build_dispatch_plan",
            return_value=dispatch_plan,
        ) as build,
        patch("fx_bin.open_launcher.execute_dispatch_plan") as execute,
    ):
        result = CliRunner().invoke(cli, ["repo", "--remote", "fork"])

    assert result.exit_code == 0
    assert result.output == "Opening https://github.com/owner/fork\n"
    launch_target = build.call_args.args[0]
    assert launch_target.target == "https://github.com/owner/fork"
    execute.assert_called_once_with(dispatch_plan)


def test_repo_without_git_repository_prints_single_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with patch("fx_bin.open_launcher.execute_dispatch_plan") as execute:
        result = CliRunner().invoke(cli, ["repo"])

    assert result.exit_code == 1
    assert result.output == f"{MISSING_REMOTE}\n"
    execute.assert_not_called()


def test_repo_without_remote_prints_single_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    monkeypatch.chdir(repository)

    with patch("fx_bin.open_launcher.execute_dispatch_plan") as execute:
        result = CliRunner().invoke(cli, ["repo"])

    assert result.exit_code == 1
    assert result.output == f"{MISSING_REMOTE}\n"
    execute.assert_not_called()


def test_repo_ambiguous_remotes_requests_explicit_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    _git(repository, "remote", "add", "fork", "git@github.com:owner/fork.git")
    _git(
        repository,
        "remote",
        "add",
        "upstream",
        "git@github.com:owner/upstream.git",
    )
    monkeypatch.chdir(repository)

    with patch("fx_bin.open_launcher.execute_dispatch_plan") as execute:
        result = CliRunner().invoke(cli, ["repo"])

    assert result.exit_code == 1
    assert result.output == (
        "Multiple Git remotes found: fork, upstream. Use --remote NAME.\n"
    )
    execute.assert_not_called()


def test_repo_rejects_non_github_remote_without_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path)
    _git(
        repository,
        "remote",
        "add",
        "origin",
        "https://gitlab.com/owner/project.git",
    )
    monkeypatch.chdir(repository)

    with patch("fx_bin.open_launcher.execute_dispatch_plan") as execute:
        result = CliRunner().invoke(cli, ["repo"])

    assert result.exit_code == 1
    assert result.output == ("Remote is not a supported GitHub.com repository URL.\n")
    execute.assert_not_called()


def test_list_command_includes_repo() -> None:
    result = CliRunner().invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "repo" in result.output
    assert "Open the current GitHub repository" in result.output

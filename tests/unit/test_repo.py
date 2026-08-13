"""Tests for the ``fx repo`` GitHub remote helpers."""

import pytest

from fx_bin.repo import RepoError, normalize_github_remote, select_remote_name


@pytest.mark.parametrize(
    ("remote_url", "expected"),
    [
        (
            "https://github.com/frankyxhl/fx_bin.git",
            "https://github.com/frankyxhl/fx_bin",
        ),
        (
            "git@github.com:frankyxhl/fx_bin.git",
            "https://github.com/frankyxhl/fx_bin",
        ),
        (
            "ssh://git@github.com/frankyxhl/fx_bin.git",
            "https://github.com/frankyxhl/fx_bin",
        ),
        (
            "https://github.com/frankyxhl/fx_bin",
            "https://github.com/frankyxhl/fx_bin",
        ),
    ],
)
def test_normalize_github_remote_supported_forms(
    remote_url: str, expected: str
) -> None:
    assert normalize_github_remote(remote_url) == expected


@pytest.mark.parametrize(
    "remote_url",
    [
        "https://gitlab.com/frankyxhl/fx_bin.git",
        "https://credential@github.com/frankyxhl/fx_bin.git",
        "file:///tmp/fx_bin",
        "/tmp/fx_bin",
        "git@github.com:missing-repository",
        "https://github.com/owner/repo/extra",
    ],
)
def test_normalize_github_remote_rejects_unsupported_urls(remote_url: str) -> None:
    with pytest.raises(RepoError, match="supported GitHub.com repository"):
        normalize_github_remote(remote_url)


def test_select_remote_name_uses_explicit_remote() -> None:
    assert select_remote_name(["fork", "origin"], "fork") == "fork"


def test_select_remote_name_prefers_origin() -> None:
    assert select_remote_name(["fork", "origin"], None) == "origin"


def test_select_remote_name_uses_only_remote_without_origin() -> None:
    assert select_remote_name(["upstream"], None) == "upstream"


def test_select_remote_name_reports_missing_remote() -> None:
    with pytest.raises(
        RepoError, match=r"^No Git remote found for the current directory\.$"
    ):
        select_remote_name([], None)


def test_select_remote_name_reports_unknown_explicit_remote() -> None:
    with pytest.raises(
        RepoError,
        match=r"^Git remote 'missing' was not found\. Available remotes: fork, origin\.$",
    ):
        select_remote_name(["origin", "fork"], "missing")


def test_select_remote_name_rejects_ambiguous_remotes() -> None:
    with pytest.raises(
        RepoError,
        match=(
            r"^Multiple Git remotes found: fork, upstream\. " r"Use --remote NAME\.$"
        ),
    ):
        select_remote_name(["upstream", "fork"], None)

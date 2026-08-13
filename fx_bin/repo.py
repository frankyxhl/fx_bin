"""Resolve GitHub remotes for the ``fx repo`` command."""

from __future__ import annotations

import re
import shutil
import subprocess  # nosec B404
from pathlib import Path
from typing import Optional, Sequence
from urllib.parse import urlsplit

from .errors import RepoError
from .root import find_git_root

UNSUPPORTED_REMOTE = "Remote is not a supported GitHub.com repository URL."
MISSING_REMOTE = "No Git remote found for the current directory."
OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
SCP_REMOTE_RE = re.compile(r"^git@github\.com:(.+)$", re.IGNORECASE)


def normalize_github_remote(remote_url: str) -> str:
    """Convert a supported GitHub remote into its HTTPS repository URL."""

    if not remote_url or any(
        ord(char) <= 32 or ord(char) == 127 for char in remote_url
    ):
        raise RepoError(UNSUPPORTED_REMOTE)

    scp_match = SCP_REMOTE_RE.fullmatch(remote_url)
    if scp_match:
        path = scp_match.group(1)
    else:
        path = _url_remote_path(remote_url)

    parts = path.strip("/").split("/")
    if len(parts) != 2:
        raise RepoError(UNSUPPORTED_REMOTE)

    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    if (
        not OWNER_RE.fullmatch(owner)
        or not REPOSITORY_RE.fullmatch(repository)
        or repository in {".", ".."}
    ):
        raise RepoError(UNSUPPORTED_REMOTE)

    return f"https://github.com/{owner}/{repository}"


def select_remote_name(
    remote_names: Sequence[str], requested_remote: Optional[str]
) -> str:
    """Select a remote using the ``fx repo`` command contract."""

    names = sorted(remote_names)
    if not names:
        raise RepoError(MISSING_REMOTE)
    if requested_remote is not None:
        if requested_remote in names:
            return requested_remote
        available = ", ".join(names)
        raise RepoError(
            f"Git remote '{requested_remote}' was not found. "
            f"Available remotes: {available}."
        )
    if "origin" in names:
        return "origin"
    if len(names) == 1:
        return names[0]
    available = ", ".join(names)
    raise RepoError(f"Multiple Git remotes found: {available}. Use --remote NAME.")


def resolve_github_repository_url(
    start_path: Optional[Path] = None,
    requested_remote: Optional[str] = None,
) -> str:
    """Resolve the selected remote for the Git repository at ``start_path``."""

    git_root = find_git_root(start_path)
    if git_root is None:
        raise RepoError(MISSING_REMOTE)

    remote_names = _run_git(git_root, "remote").splitlines()
    remote_name = select_remote_name(remote_names, requested_remote)
    remote_url = _run_git(git_root, "remote", "get-url", "--", remote_name)
    return normalize_github_remote(remote_url)


def _run_git(git_root: Path, *args: str) -> str:
    git_executable = shutil.which("git")
    if git_executable is None:
        raise RepoError("Git is not available on this system.")
    try:
        result = subprocess.run(  # nosec B603
            [git_executable, "-C", str(git_root), *args],
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RepoError("Could not read Git remote configuration.") from exc
    if result.returncode != 0:
        raise RepoError("Could not read Git remote configuration.")
    return result.stdout.strip()


def _url_remote_path(remote_url: str) -> str:
    try:
        parsed = urlsplit(remote_url)
        port = parsed.port
    except ValueError as exc:
        raise RepoError(UNSUPPORTED_REMOTE) from exc

    common_valid = (
        parsed.hostname is not None
        and parsed.hostname.lower() == "github.com"
        and port is None
        and parsed.password is None
        and not parsed.query
        and not parsed.fragment
    )
    https_valid = parsed.scheme == "https" and parsed.username is None
    ssh_valid = parsed.scheme == "ssh" and parsed.username == "git"
    if not common_valid or not (https_valid or ssh_valid):
        raise RepoError(UNSUPPORTED_REMOTE)
    return parsed.path


__all__ = [
    "MISSING_REMOTE",
    "RepoError",
    "normalize_github_remote",
    "resolve_github_repository_url",
    "select_remote_name",
]

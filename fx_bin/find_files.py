import os
import sys
import fnmatch
from typing import Iterable, List, Optional

import click


DEFAULT_IGNORED_DIRS: List[str] = [".git", ".venv", "node_modules"]


def find_files(
    keyword: str,
    include_ignored: bool = False,
    exclude: Optional[List[str]] = None,
    first: bool = False,
) -> None:
    """Print files/dirs under CWD whose names contain keyword.

    - By default, skips common heavy dirs: .git, .venv, node_modules.
    - Set include_ignored=True to include those directories.
    """
    cwd = os.getcwd()
    ignored = set() if include_ignored else set(DEFAULT_IGNORED_DIRS)
    patterns = list(exclude or [])

    def is_excluded(name: str) -> bool:
        if name in ignored:
            return True
        for pat in patterns:
            # Shell-style glob patterns (e.g., '*.py', 'build*')
            if fnmatch.fnmatchcase(name, pat):
                return True
        return False

    for root, dirs, files in os.walk(cwd, topdown=True, followlinks=False):
        if ignored or patterns:
            # Prune excluded directories to avoid unnecessary descent
            dirs[:] = [d for d in dirs if not is_excluded(d)]

        for name in dirs + files:
            if keyword in name and not is_excluded(name):
                click.echo(os.path.join(root, name))
                if first:
                    return


@click.command()
@click.argument("keyword")
@click.option(
    "--include-ignored",
    is_flag=True,
    default=False,
    help="Include normally skipped dirs (.git, .venv, node_modules)",
)
@click.option(
    "--exclude",
    "excludes",
    multiple=True,
    help=(
        "Exclude names/patterns (repeatable). Supports globs: "
        "--exclude build --exclude '*.log'"
    ),
)
def main(keyword: str, include_ignored: bool, excludes: Iterable[str]) -> int:
    if not keyword or keyword.strip() == "":
        click.echo("Please type text to search. For example: fx ff bar", err=True)
        click.echo("Usage: fx ff KEYWORD", err=True)
        return 1
    find_files(keyword, include_ignored=include_ignored, exclude=list(excludes))
    return 0


if __name__ == "__main__":
    sys.exit(main())

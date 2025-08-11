import os
import sys
import tempfile
from typing import Tuple

import click
from loguru import logger as L


def work(search_text: str, replace_text: str, filename: str) -> None:
    """Replace text in a file."""
    tmp = tempfile.mkstemp()[1]
    with open(filename) as fd1, open(tmp, 'w') as fd2:
        for line in fd1:
            line = line.replace(search_text, replace_text)
            fd2.write(line)
    os.rename(tmp, filename)


@click.command()
@click.argument('search_text', nargs=1)
@click.argument('replace_text', nargs=1)
@click.argument('filenames', nargs=-1)
def main(search_text: str, replace_text: str, filenames: Tuple[str, ...]) -> int:
    """Replace text in multiple files."""
    for f in filenames:
        if not os.path.isfile(f):
            click.echo(f"This file does not exist: {f}", err=True)
            L.error(f"This file does not exist: {f}")
            raise click.ClickException(f"This file does not exist: {f}")
    for f in filenames:
        L.debug(f'Replacing {search_text} with {replace_text} in {f}')
        work(search_text, replace_text, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())

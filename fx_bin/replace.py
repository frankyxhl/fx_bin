import os
# import os.path
import sys
import tempfile
import click
from loguru import logger as L


def work(s, t, f):
    tmp = tempfile.mkstemp()[1]
    with open(f) as fd1, open(tmp, 'w') as fd2:
        for line in fd1:
            line = line.replace(s, t)
            fd2.write(line)
    os.rename(tmp, f)


@click.command()
@click.argument('search_text', nargs=1)
@click.argument('replace_text', nargs=1)
@click.argument('filenames', nargs=-1)
def main(search_text: str, replace_text: str, file_names):
    for f in file_names:
        if not os.path.isfile(f):
            L.error(f"This file does not exist: {f}")
            return 1
    for f in file_names:
        L.debug(f'Replacing {search_text} with {replace_text} in {f}')
        work(search_text, replace_text, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())

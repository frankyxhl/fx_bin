import os
import sys
import click
from .lib import is_tool, is_windows


def find_files(keyword):
    if is_tool("find") and not is_windows():
        # cmd = 'find . -iname "*{}*" -type f -print'.format(keyword)
        cmd = 'find . -iname "*{}*" -print'.format(keyword)
        os.system(cmd)
        return
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        for d in dirs:
            if keyword in d:
                print(os.path.join(root, d))
        for f in files:
            if keyword in f:
                print(os.path.join(root, f))
    return


@click.command()
@click.argument('keyword')
def main(keyword, args=None):
    if not keyword:
        click.echo("Please type text to search. For example: ff bar")
    find_files(keyword)
    return 0


if __name__ == "__main__":
    sys.exit(main())

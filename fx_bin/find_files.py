import os
import sys
import click


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None


def find_files(keyword):
    if is_tool("find"):
    #     cmd = 'find . -iname "*{}*" -type f -print'.format(keyword)
        cmd = 'find . -iname "*{}*" -print'.format(keyword)
        os.system(cmd)
        return
    print("Using Python search:")
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if keyword in d:
                print(os.path.join(root, d))
        for f in files:
            if keyword in f:
                print(os.path.join(root, f))


@click.command()
@click.argument('keyword')
def main(keyword, args=None):
    if not keyword:
        click.echo("Please type text to search. For example: ff bar")
    find_files(keyword)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

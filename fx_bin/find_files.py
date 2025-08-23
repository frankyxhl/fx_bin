import os
import sys

import click


def find_files(keyword: str) -> None:
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        for item in dirs + files:
            if keyword in item:
                print(os.path.join(root, item))


@click.command()
@click.argument('keyword')
def main(keyword: str) -> int:
    if not keyword:
        click.echo("Please type text to search. For example: fx_ff bar")
    find_files(keyword)
    return 0


if __name__ == "__main__":
    sys.exit(main())

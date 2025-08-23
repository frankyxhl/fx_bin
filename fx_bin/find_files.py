import os
import sys

import click


def find_files(keyword: str) -> None:
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        for item in dirs + files:
            if keyword in item:
                click.echo(os.path.join(root, item))


@click.command()
@click.argument('keyword')
def main(keyword: str) -> int:
    if not keyword or keyword.strip() == "":
        click.echo("Please type text to search. For example: fx_ff bar", err=True)
        click.echo("Usage: fx_ff KEYWORD", err=True)
        return 1
    find_files(keyword)
    return 0


if __name__ == "__main__":
    sys.exit(main())

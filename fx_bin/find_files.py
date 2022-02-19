import os
import sys
import click


def find_files(keyword):
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        for o in [dirs+files]:
            if keyword in o:
                print(os.path.join(root, o))


@click.command()
@click.argument('keyword')
def main(keyword, args=None):
    if not keyword:
        click.echo("Please type text to search. For example: fx.ff bar")
    find_files(keyword)
    return 0


if __name__ == "__main__":
    sys.exit(main())

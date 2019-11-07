import os
import os.path
import sys
import click
try:
    import pandas
except ImportError:
    print("could not find pandas please install:")
    print("Command: python -m pip install pandas")


@click.command()
@click.argument('url', nargs=1)
@click.argument('output_filename', nargs=1)
def main(url, output_filename: str, args=None) -> int:
    if not output_filename.endswith(".xlsx"):
        output_filename += ".xlsx"
    if os.path.exists(output_filename):
        print("This file already exists. Skip")
        return 1
    pandas.read_json(url).to_excel(output_filename, index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())

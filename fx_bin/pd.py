import os
import os.path
import sys
import click

# Define a pandas placeholder that can be mocked by tests
pandas = None


def _check_pandas_available():
    """Check if pandas is available and import it if needed."""
    global pandas
    if pandas is None:
        try:
            import pandas as pd
            globals()['pandas'] = pd
        except ImportError:
            return False
    return True


@click.command()
@click.argument('url', nargs=1)
@click.argument('output_filename', nargs=1)
def main(url, output_filename: str, args=None) -> int:
    if not output_filename.endswith(".xlsx"):
        output_filename += ".xlsx"
    if os.path.exists(output_filename):
        print("This file already exists. Skip")
        sys.exit(1)
    
    # Check if pandas is available, unless it's already been set (e.g., by mocking)
    if pandas is None and not _check_pandas_available():
        print("could not find pandas please install:")
        print("Command: python -m pip install pandas")
        sys.exit(1)
    
    try:
        pandas.read_json(url).to_excel(output_filename, index=False)
        return 0
    except Exception as e:
        print(f"Error processing JSON or writing Excel file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())

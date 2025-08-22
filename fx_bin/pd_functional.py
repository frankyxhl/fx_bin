"""Functional version of pd.py using returns library.

This module provides JSON to Excel conversion with functional error handling.
"""

import os
import sys
from typing import Optional

import click
from returns.result import Result, Success, Failure, safe
from returns.maybe import Maybe
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.io import IOResult, impure_safe

from fx_bin.errors import PdError, ValidationError, IOError as FxIOError


# Pandas handling with Maybe monad
def check_pandas_available() -> Result[object, PdError]:
    """Check if pandas is available and return it."""
    try:
        import pandas as pd
        return Success(pd)
    except ImportError:
        return Failure(PdError(
            "could not find pandas please install:\n"
            "Command: python -m pip install pandas"
        ))


def validate_output_filename(filename: str) -> Result[str, ValidationError]:
    """Validate and normalize output filename."""
    normalized = filename if filename.endswith(".xlsx") else f"{filename}.xlsx"
    
    # Check for invalid characters or paths
    if os.path.sep in normalized or normalized.startswith('.'):
        return Failure(ValidationError(f"Invalid filename: {normalized}"))
    
    return Success(normalized)


def check_file_not_exists(filename: str) -> Result[str, ValidationError]:
    """Check that output file doesn't already exist."""
    if os.path.exists(filename):
        return Failure(ValidationError(f"File already exists: {filename}"))
    return Success(filename)


def validate_url(url: str) -> Result[str, ValidationError]:
    """Validate that URL is safe and well-formed."""
    # Basic URL validation
    if not url:
        return Failure(ValidationError("URL cannot be empty"))
    
    # Prevent local file access via file:// protocol
    if url.startswith('file://'):
        return Failure(ValidationError("Local file URLs not allowed"))
    
    # Could add more validation here (URL format, allowed domains, etc)
    return Success(url)


@impure_safe
def process_json_to_excel(
    pandas_module: object,
    url: str,
    output_filename: str
) -> IOResult[None, FxIOError]:
    """Process JSON from URL and save as Excel file."""
    try:
        # Use the pandas module that was validated
        pd = pandas_module
        pd.read_json(url).to_excel(output_filename, index=False)
        return IOResult.from_value(None)
    except Exception as e:
        return IOResult.from_failure(
            FxIOError(f"Error processing JSON or writing Excel: {e}")
        )


def main_functional(url: str, output_filename: str) -> Result[int, PdError]:
    """
    Main function with functional error handling.
    
    Returns Result[int, PdError] where int is the exit code.
    """
    # Check pandas first
    pandas_result = check_pandas_available()
    if isinstance(pandas_result, Failure):
        return pandas_result.map(lambda _: 1)  # Won't execute, type hint
    
    pandas_module = pandas_result.unwrap()
    
    # Validation pipeline
    validation_result = flow(
        validate_url(url),
        bind(lambda _: validate_output_filename(output_filename)),
        bind(check_file_not_exists),
    )
    
    if isinstance(validation_result, Failure):
        return validation_result.map(lambda _: 1)
    
    output_file = validation_result.unwrap()
    
    # Process the file
    io_result = process_json_to_excel(pandas_module, url, output_file)
    
    # Convert IOResult to Result for consistent return type
    result = io_result.run()
    
    if isinstance(result, Success):
        return Success(0)
    else:
        return Failure(PdError(str(result.failure())))


@click.command()
@click.argument('url', nargs=1)
@click.argument('output_filename', nargs=1)
def main(url: str, output_filename: str) -> None:
    """
    CLI entry point that bridges functional and traditional interfaces.
    
    This maintains backward compatibility while using functional internals.
    """
    result = main_functional(url, output_filename)
    
    if isinstance(result, Failure):
        error = result.failure()
        print(str(error), file=sys.stderr)
        sys.exit(1)
    else:
        sys.exit(result.unwrap())


# Compatibility wrapper for existing code
def main_legacy(url: str, output_filename: str, args=None) -> int:
    """Legacy interface for backward compatibility."""
    result = main_functional(url, output_filename)
    
    if isinstance(result, Failure):
        error = result.failure()
        print(str(error))
        return 1
    else:
        return result.unwrap()


if __name__ == "__main__":
    main()
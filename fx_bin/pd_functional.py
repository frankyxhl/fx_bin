"""Functional version of pd.py using returns library.

This module provides JSON to Excel conversion with functional error handling.
"""

import os
import sys
import ipaddress
from io import StringIO
from urllib.parse import urlparse

import click
from returns.result import Result, Success, Failure
from returns.pipeline import flow
from returns.pointfree import bind
from returns.io import IOResult, IOSuccess, IOFailure, impure_safe

from fx_bin.errors import PdError, ValidationError, IOError as FxIOError


# Pandas handling with Maybe monad
def check_pandas_available() -> Result[object, PdError]:
    """Check if pandas is available and return it."""
    try:
        import pandas as pd

        return Success(pd)
    except ImportError:
        return Failure(
            PdError(
                "could not find pandas please install:\n"
                "Command: python -m pip install pandas"
            )
        )


def validate_output_filename(filename: str) -> Result[str, ValidationError]:
    """Validate and normalize output filename."""
    normalized = filename if filename.endswith(".xlsx") else f"{filename}.xlsx"

    # Check for invalid characters or paths
    if os.path.sep in normalized or normalized.startswith("."):
        return Failure(ValidationError(f"Invalid filename: {normalized}"))

    return Success(normalized)


def check_file_not_exists(filename: str) -> Result[str, ValidationError]:
    """Check that output file doesn't already exist."""
    if os.path.exists(filename):
        return Failure(ValidationError(f"File already exists: {filename}"))
    return Success(filename)


def validate_url(url: str) -> Result[str, ValidationError]:
    """Validate that URL is safe and well-formed.

    Blocks:
    - file:// URLs
    - Internal network addresses (127.0.0.1, 10.x.x.x, 172.16-31.x.x, 192.168.x.x)
    - Cloud metadata addresses (169.254.169.254)
    """
    if not url:
        return Failure(ValidationError("URL cannot be empty"))

    # For local files, just check they exist (backward compatibility)
    if os.path.exists(url):
        return Success(url)

    # For JSON strings, accept them as-is
    if not url.startswith(("http://", "https://", "file://")):
        # Might be JSON content, let process_json_to_excel handle it
        return Success(url)

    # Now validate URLs
    try:
        parsed = urlparse(url)

        # Block file:// scheme
        if parsed.scheme.lower() == "file":
            return Failure(ValidationError("Local file URLs not allowed"))

        # Only allow http and https schemes
        if parsed.scheme.lower() not in ["http", "https"]:
            return Failure(ValidationError(f"Invalid URL scheme: {parsed.scheme}"))

        # Check for dangerous hostnames/IPs
        hostname = parsed.hostname
        if not hostname:
            return Failure(ValidationError("URL must have a hostname"))

        # Try to parse as IP address
        try:
            ip = ipaddress.ip_address(hostname)

            # Block private/internal networks
            if ip.is_private or ip.is_loopback:
                return Failure(
                    ValidationError(
                        f"Private/internal network access not allowed: {hostname}"
                    )
                )

            # Block cloud metadata service (AWS, GCP, Azure)
            if str(ip) == "169.254.169.254":
                return Failure(
                    ValidationError("Cloud metadata service access not allowed")
                )

        except ValueError:
            # Not an IP address, check for dangerous hostnames
            hostname_lower = hostname.lower()
            dangerous_hosts = [
                "localhost",
                "metadata.google.internal",
                "metadata.azure.com",
                "169.254.169.254",
            ]
            if hostname_lower in dangerous_hosts:
                return Failure(
                    ValidationError(f"Dangerous hostname not allowed: {hostname}")
                )

        return Success(url)

    except Exception as e:
        return Failure(ValidationError(f"Invalid URL: {e}"))


@impure_safe
def process_json_to_excel(
    pandas_module: object, url: str, output_filename: str
) -> IOResult[None, FxIOError]:
    """Process JSON from URL and save as Excel file."""
    try:
        # Use the pandas module that was validated
        pd = pandas_module

        # Check if url looks like a URL, file path, or JSON string
        if url.startswith(("http://", "https://")):
            # It's definitely a URL
            df = pd.read_json(url)
        elif os.path.exists(url):
            # It's a file path
            df = pd.read_json(url)
        else:
            # For anything else, assume it might be JSON content
            # Use StringIO to avoid FutureWarning
            # This will naturally fail with appropriate error if it's
            # not valid JSON
            df = pd.read_json(StringIO(url))

        df.to_excel(output_filename, index=False)
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

    # Handle both mocked results (direct IOSuccess/IOFailure) and real results
    # (nested structure)
    if isinstance(io_result, IOFailure):
        # Direct IOFailure (from mocking or other cases)
        error = io_result.failure()
        result = Failure(error)
    elif isinstance(io_result, IOSuccess):
        # Check if this is a direct IOSuccess or nested structure
        unwrapped = io_result.unwrap()
        if hasattr(unwrapped, "_inner_value"):
            # Could be nested structure: IOSuccess(IO(IOResult(...)))
            inner_result = unwrapped._inner_value
            if isinstance(inner_result, IOSuccess):
                final_value = inner_result.unwrap()._inner_value
                result = Success(final_value)
            elif isinstance(inner_result, IOFailure):
                final_error = inner_result.failure()._inner_value
                result = Failure(final_error)
            else:
                # Direct value wrapped in IO (from mocking like
                # IOSuccess(None))
                result = Success(inner_result)
        else:
            # Direct IOSuccess (from mocking)
            result = Success(unwrapped)
    else:
        result = Failure(PdError("Unexpected result type from process_json_to_excel"))

    if isinstance(result, Success):
        return Success(0)
    else:
        return Failure(PdError(str(result.failure())))


@click.command()
@click.argument("url", nargs=1)
@click.argument("output_filename", nargs=1)
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

import os
import os.path
import sys
import ipaddress
from urllib.parse import urlparse
import click
from io import StringIO

# Define a pandas placeholder that can be mocked by tests
pandas = None


def _check_pandas_available():
    """Check if pandas is available and import it if needed."""
    if pandas is None:
        try:
            import pandas as pd
            globals()['pandas'] = pd
        except ImportError:
            return False
    return True


def _validate_url(url: str) -> bool:
    """Validate URL to prevent security issues.

    Blocks:
    - file:// URLs
    - Internal network addresses (127.0.0.1, 10.x.x.x, 172.16-31.x.x,
      192.168.x.x)
    - Cloud metadata addresses (169.254.169.254)

    Returns:
        bool: True if URL is safe, False otherwise
    """
    try:
        parsed = urlparse(url)

        # Block file:// scheme
        if parsed.scheme.lower() == 'file':
            return False

        # Only allow http and https schemes
        if parsed.scheme.lower() not in ['http', 'https']:
            return False

        # Check for dangerous hostnames/IPs
        hostname = parsed.hostname
        if not hostname:
            return False

        # Try to parse as IP address
        try:
            ip = ipaddress.ip_address(hostname)

            # Block private/internal networks
            if ip.is_private or ip.is_loopback:
                return False

            # Block cloud metadata service (AWS, GCP, Azure)
            if str(ip) == '169.254.169.254':
                return False

        except ValueError:
            # Not an IP address, check for dangerous hostnames
            hostname_lower = hostname.lower()
            dangerous_hosts = [
                'localhost',
                'metadata.google.internal',
                'metadata.azure.com',
                '169.254.169.254'
            ]

            if hostname_lower in dangerous_hosts:
                return False

        return True

    except Exception:
        # If we can't parse the URL, consider it unsafe
        return False


@click.command()
@click.argument('url', nargs=1)
@click.argument('output_filename', nargs=1)
def main(url, output_filename: str, args=None) -> int:
    if not output_filename.endswith(".xlsx"):
        output_filename += ".xlsx"
    if os.path.exists(output_filename):
        click.echo("This file already exists. Skip", err=True)
        raise click.ClickException("Output file already exists")

    # Check if pandas is available, unless it's already been set
    # (e.g., by mocking)
    if pandas is None and not _check_pandas_available():
        click.echo("could not find pandas please install:", err=True)
        click.echo("Command: python -m pip install pandas", err=True)
        raise click.ClickException(
            "pandas package is required but not installed"
        )

    try:
        # Check if url looks like a URL, file path, or JSON string
        if url.startswith(('http://', 'https://')):
            # It's definitely a URL - validate it first
            if not _validate_url(url):
                click.echo(
                    "Error: URL is not allowed for security reasons",
                    err=True
                )
                click.echo("Blocked URLs include:", err=True)
                click.echo("- file:// URLs", err=True)
                click.echo(
                    "- Internal network addresses "
                    "(localhost, 127.x.x.x, 10.x.x.x, etc.)",
                    err=True
                )
                click.echo("- Cloud metadata services", err=True)
                raise click.ClickException("URL blocked for security reasons")
            df = pandas.read_json(url)
        elif os.path.exists(url):
            # It's a file path
            df = pandas.read_json(url)
        else:
            # For anything else, assume it might be JSON content
            # Use StringIO to avoid FutureWarning
            # This will naturally fail with appropriate error if it's not
            # valid JSON
            df = pandas.read_json(StringIO(url))

        df.to_excel(output_filename, index=False)
        return 0
    except Exception as e:
        click.echo(
            f"Error processing JSON or writing Excel file: {e}", err=True
        )
        raise click.ClickException(
            f"Failed to process JSON or write Excel file: {e}"
        )


if __name__ == "__main__":
    sys.exit(main())

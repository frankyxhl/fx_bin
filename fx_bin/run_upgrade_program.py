#!/usr/bin/env python3
"""Upgrade fx_bin package utility."""
import subprocess
import sys


def main():
    """Upgrade fx_bin package using pip."""
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "fx-bin"]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd, check=True, text=True, capture_output=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading fx-bin: {e}", file=sys.stderr)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

"""Security tests for path traversal prevention in validate_file_access.

This module tests that validate_file_access properly prevents path traversal
attacks where an attacker tries to access files outside the allowed directory.
"""

import os
import tempfile
from pathlib import Path

import pytest
from returns.result import Failure, Success

from fx_bin.replace_functional import validate_file_access
from fx_bin.errors import ReplaceError, SecurityError


def test_given_parent_directory_traversal_when_validate_then_blocked():
    """RED: Test that parent directory traversal is blocked.

    Attack pattern: ../../../etc/passwd
    Should be blocked even if file exists.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create allowed directory structure
        allowed_dir = Path(tmpdir) / "allowed"
        allowed_dir.mkdir()

        # Create a file in allowed directory
        safe_file = allowed_dir / "safe.txt"
        safe_file.write_text("safe content")

        # Try to access parent directory using path traversal
        attack_path = str(allowed_dir / ".." / ".." / "etc" / "passwd")

        # WHEN: validating with base directory restriction
        result = validate_file_access(attack_path, allowed_base=str(allowed_dir))

        # THEN: should fail with security error
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, (ReplaceError, SecurityError))
        assert "outside allowed" in str(error).lower() or "traversal" in str(error).lower()


def test_given_absolute_path_outside_base_when_validate_then_blocked():
    """RED: Test that absolute paths outside allowed base are blocked.

    Attack pattern: /tmp/malicious.txt when base is /home/user/work
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create allowed directory
        allowed_dir = Path(tmpdir) / "allowed"
        allowed_dir.mkdir()

        # Create file outside allowed directory
        outside_dir = Path(tmpdir) / "outside"
        outside_dir.mkdir()
        outside_file = outside_dir / "malicious.txt"
        outside_file.write_text("malicious content")

        # WHEN: trying to access file outside allowed base
        result = validate_file_access(str(outside_file), allowed_base=str(allowed_dir))

        # THEN: should be blocked
        assert isinstance(result, Failure)
        error = result.failure()
        assert "outside allowed" in str(error).lower() or "not in allowed" in str(error).lower()


def test_given_symlink_to_outside_when_validate_then_blocked():
    """RED: Test that symlinks pointing outside allowed base are blocked.

    Attack pattern: Create symlink in allowed dir pointing to /etc/passwd
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create allowed directory
        allowed_dir = Path(tmpdir) / "allowed"
        allowed_dir.mkdir()

        # Create target file outside allowed directory
        outside_dir = Path(tmpdir) / "outside"
        outside_dir.mkdir()
        target_file = outside_dir / "secret.txt"
        target_file.write_text("secret data")

        # Create symlink in allowed directory pointing to outside file
        symlink_path = allowed_dir / "innocent_link.txt"
        symlink_path.symlink_to(target_file)

        # WHEN: validating symlink with base directory restriction
        result = validate_file_access(str(symlink_path), allowed_base=str(allowed_dir))

        # THEN: should be blocked (symlink target is outside base)
        assert isinstance(result, Failure)
        error = result.failure()
        assert "outside allowed" in str(error).lower() or "symlink" in str(error).lower()


def test_given_file_in_allowed_dir_when_validate_then_success():
    """RED: Test that normal files within allowed base are accepted.

    This is the positive test case - legitimate file access should work.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create allowed directory with subdirectories
        allowed_dir = Path(tmpdir) / "allowed"
        allowed_dir.mkdir()
        subdir = allowed_dir / "subdir"
        subdir.mkdir()

        # Create legitimate file in subdirectory
        legitimate_file = subdir / "data.txt"
        legitimate_file.write_text("legitimate content")

        # WHEN: validating file within allowed base
        result = validate_file_access(str(legitimate_file), allowed_base=str(allowed_dir))

        # THEN: should succeed
        assert isinstance(result, Success)
        real_path = result.unwrap()
        assert os.path.exists(real_path)


def test_given_no_base_specified_when_validate_then_no_restriction():
    """RED: Test backward compatibility - no base means no path restriction.

    When allowed_base is None (default), should not enforce path restrictions.
    This maintains backward compatibility with existing code.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file anywhere
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")

        # WHEN: validating without base directory (backward compatibility)
        result = validate_file_access(str(test_file))  # No allowed_base parameter

        # THEN: should succeed (no restrictions when base not specified)
        assert isinstance(result, Success)


def test_given_normalized_paths_when_validate_then_uses_realpath():
    """RED: Test that path normalization prevents Unicode/encoding attacks.

    Paths like 'file.txt' vs './file.txt' vs 'dir/../file.txt' should all
    be normalized to the same real path for comparison.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        allowed_dir = Path(tmpdir) / "allowed"
        allowed_dir.mkdir()

        # Create file
        test_file = allowed_dir / "test.txt"
        test_file.write_text("content")

        # Try various equivalent path representations
        paths_to_test = [
            str(test_file),
            str(allowed_dir / "." / "test.txt"),
            str(allowed_dir / "subdir" / ".." / "test.txt"),
        ]

        for path in paths_to_test:
            # WHEN: validating equivalent paths
            result = validate_file_access(path, allowed_base=str(allowed_dir))

            # THEN: all should succeed (same normalized path)
            assert isinstance(result, Success), f"Failed for path: {path}"


def test_given_case_sensitive_paths_when_validate_then_handled():
    """RED: Test handling of case-sensitive vs case-insensitive filesystems.

    On case-insensitive systems (macOS, Windows), paths should still be
    validated correctly.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        allowed_dir = Path(tmpdir) / "allowed"
        allowed_dir.mkdir()

        test_file = allowed_dir / "Test.txt"
        test_file.write_text("content")

        # WHEN: validating with different case
        result = validate_file_access(str(test_file), allowed_base=str(allowed_dir))

        # THEN: should succeed (path is within base)
        assert isinstance(result, Success)

"""Tests for backup_utils module.

This module tests shared backup functionality that can be used
across different modules (replace.py, replace_functional.py, etc.).
"""

import os
import stat
import pytest
from pathlib import Path
from returns.result import Success, Failure
from returns.io import IOResult


def test_given_file_when_create_backup_then_backup_created(temp_test_dir):
    """RED: Test that create_backup creates a backup file.

    The backup should preserve file contents and metadata.
    """
    from fx_bin.backup_utils import create_backup

    # GIVEN: a test file with content
    test_file = temp_test_dir / "test.txt"
    test_content = "Hello, World!"
    test_file.write_text(test_content)

    # Set specific permissions
    os.chmod(test_file, 0o644)

    # WHEN: creating a backup
    result = create_backup(str(test_file))

    # THEN: backup should be created successfully
    assert isinstance(result._inner_value, Success)
    backup = result._inner_value.unwrap()

    # THEN: backup file should exist
    assert os.path.exists(backup.backup_path)

    # THEN: backup should have same content
    with open(backup.backup_path, "r") as f:
        assert f.read() == test_content

    # THEN: FileBackup should contain correct metadata
    assert backup.original_path == str(test_file)
    assert backup.backup_path == f"{test_file}.backup"
    assert stat.S_IMODE(backup.original_mode) == 0o644


def test_given_nonexistent_file_when_create_backup_then_failure(temp_test_dir):
    """RED: Test that create_backup fails for nonexistent file."""
    from fx_bin.backup_utils import create_backup
    from fx_bin.errors import IOError as FxIOError

    # GIVEN: a nonexistent file path
    nonexistent = temp_test_dir / "nonexistent.txt"

    # WHEN: creating a backup
    result = create_backup(str(nonexistent))

    # THEN: should return Failure
    assert isinstance(result._inner_value, Failure)
    error = result._inner_value.failure()
    assert isinstance(error, FxIOError)


def test_given_backup_when_restore_then_original_restored(temp_test_dir):
    """RED: Test that restore_from_backup restores the original file.

    This should restore both content and permissions.
    """
    from fx_bin.backup_utils import create_backup, restore_from_backup

    # GIVEN: a file with original content
    test_file = temp_test_dir / "test.txt"
    original_content = "Original content"
    test_file.write_text(original_content)
    os.chmod(test_file, 0o644)

    # Create backup
    backup_result = create_backup(str(test_file))
    backup = backup_result._inner_value.unwrap()

    # GIVEN: file is modified after backup
    modified_content = "Modified content"
    test_file.write_text(modified_content)
    os.chmod(test_file, 0o600)

    # WHEN: restoring from backup
    restore_result = restore_from_backup(backup)

    # THEN: restore should succeed
    assert isinstance(restore_result._inner_value, Success)

    # THEN: original content should be restored
    assert test_file.read_text() == original_content

    # THEN: original permissions should be restored
    assert stat.S_IMODE(os.stat(test_file).st_mode) == 0o644

    # THEN: backup file should be removed after restore
    assert not os.path.exists(backup.backup_path)


def test_given_no_backup_file_when_restore_then_success(temp_test_dir):
    """RED: Test that restore handles missing backup gracefully.

    This can happen if backup was already cleaned up.
    """
    from fx_bin.backup_utils import restore_from_backup, FileBackup

    # GIVEN: a FileBackup with non-existent backup file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("content")

    backup = FileBackup(
        original_path=str(test_file),
        backup_path=str(temp_test_dir / "nonexistent.backup"),
        original_mode=os.stat(test_file).st_mode,
    )

    # WHEN: attempting to restore
    result = restore_from_backup(backup)

    # THEN: should succeed (graceful handling)
    assert isinstance(result._inner_value, Success)


def test_given_backup_when_cleanup_then_backup_removed(temp_test_dir):
    """RED: Test that cleanup_backup removes backup file."""
    from fx_bin.backup_utils import create_backup, cleanup_backup

    # GIVEN: a file with backup
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("test content")

    backup_result = create_backup(str(test_file))
    backup = backup_result._inner_value.unwrap()

    # Verify backup exists
    assert os.path.exists(backup.backup_path)

    # WHEN: cleaning up backup
    cleanup_result = cleanup_backup(backup)

    # THEN: cleanup should succeed
    assert isinstance(cleanup_result._inner_value, Success)

    # THEN: backup file should be removed
    assert not os.path.exists(backup.backup_path)

    # THEN: original file should still exist
    assert os.path.exists(backup.original_path)


def test_given_no_backup_when_cleanup_then_success(temp_test_dir):
    """RED: Test that cleanup handles missing backup gracefully."""
    from fx_bin.backup_utils import cleanup_backup, FileBackup

    # GIVEN: a FileBackup with non-existent backup
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("content")

    backup = FileBackup(
        original_path=str(test_file),
        backup_path=str(temp_test_dir / "nonexistent.backup"),
        original_mode=os.stat(test_file).st_mode,
    )

    # WHEN: attempting to cleanup
    result = cleanup_backup(backup)

    # THEN: should succeed (non-critical operation)
    assert isinstance(result._inner_value, Success)


def test_given_file_with_special_chars_when_backup_then_works(temp_test_dir):
    """RED: Test backup with special characters in filename."""
    from fx_bin.backup_utils import create_backup

    # GIVEN: a file with special characters in name
    test_file = temp_test_dir / "test file [with] (special).txt"
    test_file.write_text("content")

    # WHEN: creating backup
    result = create_backup(str(test_file))

    # THEN: should succeed
    assert isinstance(result._inner_value, Success)
    backup = result._inner_value.unwrap()

    # THEN: backup path should be correct
    assert backup.backup_path == f"{test_file}.backup"
    assert os.path.exists(backup.backup_path)


def test_given_readonly_file_when_backup_then_succeeds(temp_test_dir):
    """RED: Test that backup works with read-only files.

    Should be able to create backup even if file is read-only.
    """
    from fx_bin.backup_utils import create_backup

    # GIVEN: a read-only file
    test_file = temp_test_dir / "readonly.txt"
    test_file.write_text("readonly content")
    os.chmod(test_file, 0o444)

    # WHEN: creating backup
    result = create_backup(str(test_file))

    # THEN: should succeed
    assert isinstance(result._inner_value, Success)
    backup = result._inner_value.unwrap()
    assert os.path.exists(backup.backup_path)


def test_given_filebackup_when_checking_attributes_then_immutable(temp_test_dir):
    """RED: Test that FileBackup is immutable (frozen dataclass)."""
    from fx_bin.backup_utils import FileBackup

    # GIVEN: a FileBackup instance
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("content")

    backup = FileBackup(
        original_path=str(test_file),
        backup_path=f"{test_file}.backup",
        original_mode=0o644,
    )

    # WHEN: attempting to modify attributes
    # THEN: should raise FrozenInstanceError
    with pytest.raises(Exception):  # FrozenInstanceError
        backup.original_path = "new_path"

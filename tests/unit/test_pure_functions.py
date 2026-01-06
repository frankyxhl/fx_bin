"""Tests for pure functions extracted from functional modules.

These tests verify that pure logic is separated from IO operations,
making code more testable and composable.
"""

import pytest
from dataclasses import dataclass
from typing import Set, Tuple

from fx_bin.common_functional import FolderContext


# Test data structures for pure function testing
@dataclass(frozen=True)
class EntryInfo:
    """Pure data representing a directory entry without IO."""
    name: str
    is_file: bool
    is_dir: bool
    size: int  # For files
    inode: Tuple[int, int]  # (device, inode)


def test_given_depth_exceeds_limit_when_should_process_then_returns_false():
    """RED: Test pure function for depth limit checking."""
    # This will be a pure function that just checks logic
    from fx_bin.common_functional import should_process_directory

    context = FolderContext(visited_inodes=set(), max_depth=10)

    # GIVEN: depth exceeds max_depth
    # WHEN: checking if should process
    # THEN: should return False
    assert should_process_directory(depth=11, context=context) is False
    assert should_process_directory(depth=10, context=context) is True
    assert should_process_directory(depth=9, context=context) is True


def test_given_inode_already_visited_when_should_process_then_returns_false():
    """RED: Test pure function for cycle detection."""
    from fx_bin.common_functional import should_process_directory

    inode = (1234, 5678)
    context = FolderContext(visited_inodes={inode}, max_depth=100)

    # GIVEN: inode already in visited set
    # WHEN: checking if should process
    # THEN: should return False
    assert should_process_directory(
        depth=0,
        context=context,
        dir_inode=inode
    ) is False


def test_given_file_entry_when_calculate_contribution_then_returns_file_size():
    """RED: Test pure function for calculating entry contribution.

    This separates the logic of "what to add" from the IO of "how to read it".
    """
    from fx_bin.common_functional import calculate_entry_contribution

    # GIVEN: a file entry with known size
    file_entry = EntryInfo(
        name="test.txt",
        is_file=True,
        is_dir=False,
        size=1024,
        inode=(1, 2)
    )

    # WHEN: calculating contribution
    # THEN: should return the file size
    result = calculate_entry_contribution(file_entry)
    assert result == 1024


def test_given_directory_entry_when_calculate_contribution_then_returns_zero():
    """RED: Test that directory entries contribute 0 (subdirectory sizes added separately).

    The actual directory size comes from recursive calls, not from the entry itself.
    """
    from fx_bin.common_functional import calculate_entry_contribution

    # GIVEN: a directory entry
    dir_entry = EntryInfo(
        name="subdir",
        is_file=False,
        is_dir=True,
        size=0,  # Directories don't have meaningful size
        inode=(1, 3)
    )

    # WHEN: calculating contribution
    # THEN: should return 0 (subdirectory handled by recursion)
    result = calculate_entry_contribution(dir_entry)
    assert result == 0


def test_given_context_when_add_inode_then_returns_new_context_with_inode():
    """RED: Test pure function for creating new context with additional inode.

    This should be immutable - returns new context without modifying original.
    """
    from fx_bin.common_functional import add_visited_inode

    # GIVEN: original context
    original_context = FolderContext(
        visited_inodes={(1, 2), (3, 4)},
        max_depth=100
    )

    new_inode = (5, 6)

    # WHEN: adding a new inode
    new_context = add_visited_inode(original_context, new_inode)

    # THEN: new context contains the inode
    assert new_inode in new_context.visited_inodes
    assert (1, 2) in new_context.visited_inodes
    assert (3, 4) in new_context.visited_inodes

    # THEN: original context is unchanged (immutability)
    assert new_inode not in original_context.visited_inodes

    # THEN: max_depth is preserved
    assert new_context.max_depth == original_context.max_depth

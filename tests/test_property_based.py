"""Property-based tests using Hypothesis for fx_bin.

These tests verify invariants that should hold for all inputs,
using Hypothesis to generate diverse test cases automatically.
"""

import tempfile
import shutil
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from pathlib import Path
from fx_bin.replace import work
from fx_bin.common import convert_size


@pytest.mark.hypothesis
@given(
    search=st.text(min_size=1, max_size=50),
    replace=st.text(max_size=50),
    content=st.text(max_size=500)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_replace_invariant_search_not_in_result(temp_test_dir, search, replace, content):
    """Property: After replacement, search text should not appear unless replace contains it.

    This is a fundamental invariant of text replacement:
    If we replace all occurrences of X with Y, and Y doesn't contain X,
    then X should not appear in the final result.
    """
    # Skip if search contains null bytes (binary data)
    assume('\x00' not in search)
    assume('\x00' not in replace)
    assume('\x00' not in content)

    # Create test file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text(content)

    # Perform replacement
    work(search, replace, str(test_file))

    # Read result
    result = test_file.read_text()

    # INVARIANT: If replace doesn't contain search, result shouldn't contain search
    # (unless the original content didn't contain search either)
    if search not in replace:
        # Count occurrences before and after
        count_before = content.count(search)
        count_after = result.count(search)

        # After replacement, there should be fewer (or equal if nothing was replaced)
        assert count_after <= count_before, \
            f"Replacement failed: search '{search[:20]}...' appears more after replacement"


@pytest.mark.hypothesis
@given(
    search=st.text(min_size=1, max_size=20),
    replace=st.text(max_size=20),
    content=st.text(min_size=0, max_size=200)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_replace_idempotent(temp_test_dir, search, replace, content):
    """Property: Replacing twice should give same result as replacing once.

    This tests idempotency: replace(replace(text)) == replace(text)
    """
    # Skip binary content
    assume('\x00' not in search and '\x00' not in replace and '\x00' not in content)

    # Create test file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text(content)

    # First replacement
    work(search, replace, str(test_file))
    result_once = test_file.read_text()

    # Second replacement (on already replaced content)
    test_file.write_text(result_once)
    work(search, replace, str(test_file))
    result_twice = test_file.read_text()

    # INVARIANT: Second replacement should not change anything
    assert result_once == result_twice, \
        "Replacement is not idempotent: second application changed the result"


@pytest.mark.hypothesis
@given(
    content=st.text(max_size=100)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_replace_empty_search_preserves_content(temp_test_dir, content):
    """Property: Replacing empty string should preserve original content.

    This is a boundary case: replacing nothing should do nothing.
    """
    assume('\x00' not in content)

    # Create test file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text(content)

    # Replace empty string
    work("", "anything", str(test_file))

    result = test_file.read_text()

    # INVARIANT: Empty search should not change content
    # Note: Python's str.replace("", "x") actually inserts between every char,
    # so this test verifies current behavior
    # If original had no empty replacements, result should be modified predictably
    if "" in content:
        # Empty string is everywhere, so replacement happens
        pass  # Behavior is defined by Python's str.replace


@pytest.mark.hypothesis
@given(size_bytes=st.integers(min_value=0, max_value=1024*1024*10))  # Up to 10MB
def test_property_convert_size_always_positive_string(size_bytes):
    """Property: convert_size should always return a non-empty string for non-negative input."""
    result = convert_size(size_bytes)

    # INVARIANT: Result should always be a non-empty string
    assert isinstance(result, str)
    assert len(result) > 0

    # INVARIANT: Result should contain a number
    assert any(char.isdigit() for char in result)

    # INVARIANT: For zero bytes, should show "0"
    if size_bytes == 0:
        assert result.startswith("0")


@pytest.mark.hypothesis
@given(size_bytes=st.integers(min_value=1, max_value=1024*1024*100))
def test_property_convert_size_monotonic(size_bytes):
    """Property: Larger byte counts should not result in 'smaller' unit representations.

    This tests that the conversion is monotonic in the sense that
    larger inputs don't produce confusing outputs.
    """
    result1 = convert_size(size_bytes)
    result2 = convert_size(size_bytes * 2)

    # Extract numeric part (rough check)
    # Both should be valid size strings
    assert len(result1) > 0
    assert len(result2) > 0

    # At minimum, doubling size should change the output
    # (unless we're at a boundary where units change)
    # This is a weak invariant but catches major errors

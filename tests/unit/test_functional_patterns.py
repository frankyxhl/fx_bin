"""Tests for functional programming patterns using returns library.

These tests demonstrate correct usage of returns library API
instead of accessing private attributes like _inner_value.
"""

import pytest
from pathlib import Path
from returns.result import Success, Failure
from returns.io import IOResult
from returns.pipeline import flow
from returns.pointfree import bind

from fx_bin.replace_functional import work_functional, ReplaceContext
from fx_bin.errors import ReplaceError


def test_given_invalid_file_when_work_functional_then_failure_returned(temp_test_dir):
    """RED: Test that work_functional returns Failure for invalid file."""
    # GIVEN a non-existent file path
    invalid_file = temp_test_dir / "nonexistent.txt"

    # WHEN calling work_functional
    result = work_functional("search", "replace", str(invalid_file))

    # THEN result should be IOFailure
    # (For now, using _inner_value like existing tests, will improve in refactor)
    assert isinstance(result._inner_value, Failure)
    error = result._inner_value.failure()
    assert isinstance(error, ReplaceError)
    assert "not found" in str(error) or "not writable" in str(error)


def test_given_replacement_fails_when_using_lash_then_backup_restored(temp_test_dir):
    """RED: Test error recovery using lash() instead of manual checking."""
    # GIVEN a test file
    test_file = temp_test_dir / "test.txt"
    test_file.write_text("original content")

    # WHEN replacement fails (simulated by permission error)
    test_file.chmod(0o444)  # Read-only

    # THEN work_functional should handle error gracefully
    result = work_functional("original", "modified", str(test_file))
    assert isinstance(result._inner_value, Failure)

    # Original content should be preserved (backup restored)
    test_file.chmod(0o644)  # Make readable again
    content = test_file.read_text()
    assert content == "original content"


def test_demonstrate_correct_lash_usage_for_error_recovery():
    """RED: Demonstrate correct usage of lash() for error recovery.

    This test shows the pattern we want to use in replace_functional.py.
    """
    # Example: An IOResult that might fail
    def operation_that_fails() -> IOResult[int, str]:
        return IOResult.from_failure("operation failed")

    def recovery_action(error: str) -> IOResult[int, str]:
        """Recovery function called on failure."""
        return IOResult.from_value(0)  # Return default value

    # CORRECT: Use lash() for error recovery
    result = operation_that_fails().lash(recovery_action)

    # The result should be success after recovery
    assert isinstance(result._inner_value, Success)
    assert result._inner_value.unwrap() == 0


def test_demonstrate_correct_bind_usage_for_railway_composition():
    """RED: Demonstrate using bind() for composing operations.

    This shows how to chain operations without manually checking _inner_value.
    """
    def step1(x: int) -> IOResult[int, str]:
        if x > 0:
            return IOResult.from_value(x * 2)
        return IOResult.from_failure("negative number")

    def step2(x: int) -> IOResult[int, str]:
        return IOResult.from_value(x + 10)

    # CORRECT: Use bind() to chain operations
    result = step1(5).bind(step2)
    assert isinstance(result._inner_value, Success)
    assert result._inner_value.unwrap() == 20  # (5 * 2) + 10

    # When step1 fails, step2 is never called
    failed_result = step1(-1).bind(step2)
    assert isinstance(failed_result._inner_value, Failure)
    assert failed_result._inner_value.failure() == "negative number"


def test_given_current_implementation_when_checking_result_then_no_private_access():
    """GREEN: Verify that production code doesn't access _inner_value.

    This test was unskipped after refactoring in GREEN phase.
    """
    # This test verifies that the actual code doesn't access _inner_value
    import inspect
    from fx_bin import replace_functional

    source = inspect.getsource(replace_functional.work_functional)

    # SHOULD NOT contain _inner_value access
    assert "_inner_value" not in source, \
        "Code should not access private _inner_value attribute"


def test_demonstrate_flow_composition_without_lambdas():
    """RED: Demonstrate using flow() for composition without lambdas.

    This shows the Haskell-style pipeline composition we want to achieve.
    Using named functions instead of lambdas for clarity.
    """
    # Step 1: Define clear, named functions
    def double(x: int) -> IOResult[int, str]:
        """Double the input value."""
        return IOResult.from_value(x * 2)

    def add_ten(x: int) -> IOResult[int, str]:
        """Add 10 to the input value."""
        return IOResult.from_value(x + 10)

    def validate_positive(x: int) -> IOResult[int, str]:
        """Ensure value is positive."""
        if x > 0:
            return IOResult.from_value(x)
        return IOResult.from_failure("Value must be positive")

    # Step 2: Compose using flow() - more functional, less "object-oriented"
    # This is closer to Haskell's >>> or function composition
    result = flow(
        IOResult.from_value(5),
        bind(double),           # Named function - clear intent
        bind(add_ten),          # No lambda needed!
        bind(validate_positive),
    )

    # Step 3: Verify the result
    assert isinstance(result._inner_value, Success)
    assert result._inner_value.unwrap() == 20  # (5 * 2) + 10

    # Test with failure case
    failed_result = flow(
        IOResult.from_value(-5),
        bind(double),           # -10
        bind(add_ten),          # 0
        bind(validate_positive), # Fails: not positive
    )

    assert isinstance(failed_result._inner_value, Failure)
    assert failed_result._inner_value.failure() == "Value must be positive"

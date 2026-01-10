import os
from typing import TypeVar, Any, Callable

from returns.io import IOResult
from returns.result import Result


def count_ascii(s: str) -> int:
    return sum(ord(c) < 128 for c in s)


SPECIAL_CHAR_LST = {"\u2018", "\u2019", "\u2013"}


def count_special_char_lst(s: str) -> int:
    return sum(c in SPECIAL_CHAR_LST for c in s)


def count_ascii_and_special(s: str) -> int:
    """Count ASCII characters plus special Unicode characters.

    This function counts ASCII characters and a predefined set of special
    Unicode characters (smart quotes and em-dash).

    Note: This was previously named count_fullwidth but was renamed for clarity
    as it doesn't actually count fullwidth characters.
    """
    _ascii = count_ascii(s)
    _special = count_special_char_lst(s)
    return _ascii + _special


# Keep the old function name for backward compatibility
# TODO: Remove this in a future major version
count_fullwidth = count_ascii_and_special


def is_tool(name: str) -> bool:
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which

    return which(name) is not None


def is_windows() -> bool:
    return os.name == "nt"


_ValueType = TypeVar("_ValueType")
_ErrorType = TypeVar("_ErrorType")
_NewErrorType = TypeVar("_NewErrorType", bound=Exception)


def unsafe_ioresult_unwrap(result: IOResult[_ValueType, _ErrorType]) -> _ValueType:
    """Unwrap IOResult value by accessing private attribute.

    IOResult does not expose a public method to get the value directly.
    This function encapsulates the necessary private access.
    """
    return result._inner_value.unwrap()


def unsafe_ioresult_value_or(
    result: IOResult[_ValueType, Any], default: _ValueType
) -> _ValueType:
    """Get IOResult value or default by accessing private attribute.

    IOResult does not expose a public method to extract the value directly.
    """
    return result._inner_value.value_or(default)


def unsafe_ioresult_to_result(
    result: IOResult[_ValueType, _ErrorType],
) -> Result[_ValueType, _ErrorType]:
    """Get the inner Result object from IOResult.

    IOResult wraps a Result object essentially as IOResult[Result[T, E]].
    This allows accessing the success/failure state directly.
    """
    return result._inner_value


def unwrap_or_convert_error(
    result: IOResult[_ValueType, _ErrorType],
    error_factory: Callable[[str], _NewErrorType],
    error_message: str,
) -> _ValueType:
    """Unwrap IOResult value or raise converted error.

    This helper reduces boilerplate when handling IOResult errors.
    If the result is success, returns the unwrapped value.
    If the result is failure, raises a new error with the original error message.

    Args:
        result: The IOResult to unwrap
        error_factory: Function to create new error from string message
        error_message: Prefix for error messages

    Returns:
        The unwrapped value if successful

    Raises:
        _NewErrorType: If the result is a failure

    Example:
        files = unwrap_or_convert_error(
            scan_result,
            OrganizeError,
            "Cannot scan source directory"
        )
    """
    try:
        return unsafe_ioresult_unwrap(result)
    except Exception:
        inner_result = unsafe_ioresult_to_result(result)
        error = inner_result.failure()
        raise error_factory(f"{error_message}: {error}")

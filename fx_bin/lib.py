import os


def count_ascii(s):
    return sum(ord(c) < 128 for c in s)


SPECIAL_CHAR_LST = {"\u2018", "\u2019", "\u2013"}


def count_special_char_lst(s):
    return sum(c in SPECIAL_CHAR_LST for c in s)


def count_ascii_and_special(s):
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


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None


def is_windows():
    return os.name == "nt"

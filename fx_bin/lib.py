import os


def count_ascii(s):
    return sum(ord(c) < 128 for c in s)


SPECIAL_CHAR_LST = {"‘", "–"}


def count_special_char_lst(s):
    return sum(c in SPECIAL_CHAR_LST for c in s)


def count_fullwidth(s):
    _ascii = count_ascii(s)
    _special = count_special_char_lst(s)
    return _ascii + _special


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None


def is_windows():
    return os.name == "nt"
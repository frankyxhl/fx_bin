import unicodedata


def count_ascii(s):
    return sum(ord(c) < 128 for c in s)


def wide_chars(s):
    return sum(unicodedata.east_asian_width(x) == 'F' for x in s)


def width(s):
    return len(s) + wide_chars(s)

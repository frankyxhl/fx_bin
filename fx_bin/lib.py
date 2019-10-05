def count_ascii(s):
    return sum(ord(c) < 128 for c in s)


SPECIAL_CHAR_LST = {"‘", "–"}


def count_special_char_lst(s):
    return sum(c in SPECIAL_CHAR_LST for c in s)


def count_fullwidth(s):
    _ascii = count_ascii(s)
    _special = count_special_char_lst(s)
    return _ascii + _special



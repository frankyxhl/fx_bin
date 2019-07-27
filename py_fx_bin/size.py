#!/usr/bin/env python3
import os
import math
from enum import Enum
from functools import total_ordering

__all__ = ["list_size"]


class EntryType(Enum):
    FILE = 1
    FOLDER = 2


def sum_folder_size(path='.') -> int:
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += sum_folder_size(entry.path)
    return total


def convert_size(size):
    size_bytes = int(size)
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s%s" % (round(s), size_name[i])


@total_ordering
class Entry:

    def __init__(self, name: str, size: int, tpe: EntryType):
        self.name = name
        self.size = size
        self.tpe = tpe

    def __lt__(self, other):
        if not isinstance(other, Entry):
            raise TypeError("Type is not same. Another type is {}".format(type(other)))
        return self.size < other.size

    def display(self, name_max, size_max):
        return "{name:<{name_max}} {size.py:>{size_max}}".format(
            name=self.name,
            name_max=name_max,
            size=self.readable_size,
            size_max=size_max)

    @property
    def readable_size(self) -> str:
        return convert_size(self.size)

    @classmethod
    def from_scandir(cls, obj: object):
        if obj.is_file():
            return Entry(obj.name, obj.stat().st_size, EntryType.FILE)
        elif obj.is_dir():
            total_size = sum_folder_size(obj.path)
            return Entry(obj.name, total_size, EntryType.FOLDER)


def list_size(path='.', ignore_dot_file=True) -> ([Entry], int, int):
    result = []
    _name_max = 0
    _size_max = 0
    for entry in os.scandir(path):
        if ignore_dot_file and entry.name.startswith("."):
            continue
        _e = Entry.from_scandir(entry)
        _name_max = max(_name_max, len(_e.name))
        _size_max = max(_size_max, len(_e.readable_size))
        result.append(_e)
    result.sort()
    return result, _name_max, _size_max


def main():
    lst, n, s = list_size()
    for e in lst:
        print(e.display(n, s))


if __name__ == '__main__':
    main()




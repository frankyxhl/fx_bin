#!/usr/bin/env python3
# from __future__ import absolute_import

import os
import math
from dataclasses import dataclass
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


@dataclass
@total_ordering
class Entry:
    __slots__ = ['name', 'size', 'tpe']
    name: str
    size: int
    tpe: EntryType

    def __lt__(self, other):
        if not isinstance(other, Entry):
            msg = "Not same Type. Another type is {}".format
            raise TypeError(msg(type(other)))
        return self.size < other.size

    def __repr__(self):
        return "{size:>5} {name}".format(
            name=self.name,
            size=self.readable_size)

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
    for entry in os.scandir(path):
        if ignore_dot_file and entry.name.startswith("."):
            continue
        _e = Entry.from_scandir(entry)
        if _e is None:
            continue
        result.append(_e)
    result.sort()
    return result


def main():
    lst = list_size()
    for e in lst:
        print(e)


if __name__ == '__main__':
    main()

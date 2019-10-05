#!/usr/bin/env python3
import os
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from fx_bin.lib import count_fullwidth

__all__ = ["list_files_count"]


class EntryType(Enum):
    FILE = 1
    FOLDER = 2


def sum_folder_files_count(path='.') -> int:
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += 1
        elif entry.is_dir():
            total += sum_folder_files_count(entry.path)
    return total


@dataclass
@total_ordering
class Entry:
    name: str
    count: int
    tpe: EntryType

    def __lt__(self, other):
        if not isinstance(other, Entry):
            raise TypeError("Type is not same. Another type is {}".format(type(other)))
        return (self.count, self.name) < (other.count, other.name)

    def display(self, name_max, count_max):
        length = len(self.name) - count_fullwidth(self.name)
        return "{name:<{name_max}} {count:>{count_max}}".format(
            name=self.name,
            name_max=name_max-length,
            count=self.count,
            count_max=count_max)

    @classmethod
    def from_scandir(cls, obj: object):
        if obj.is_file():
            return Entry(obj.name, 1, EntryType.FILE)
        elif obj.is_dir():
            _count = sum_folder_files_count(obj.path)
            return Entry(obj.name, _count, EntryType.FOLDER)


def list_files_count(path='.', ignore_dot_file=True) -> ([Entry], int, int):
    result = []
    _name_max = 0
    _count_max = 0
    for entry in os.scandir(path):
        if ignore_dot_file and entry.name.startswith("."):
            continue
        _e = Entry.from_scandir(entry)
        if _e is None:
            continue
        _name_max = max(_name_max, len(_e.name.encode()))
        _count_max = max(_count_max, len(str(_e.count)))
        result.append(_e)
    result.sort()
    return result, _name_max, _count_max


def main():
    lst, n, s = list_files_count()
    for e in lst:
        print(e.display(n, s))


if __name__ == '__main__':
    main()




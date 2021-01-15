#!/usr/bin/env python3
import os
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering

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
    __slots__ = ['name', 'count', 'tpe']
    name: str
    count: int
    tpe: EntryType

    def __lt__(self, other):
        if not isinstance(other, Entry):
            msg = "Not same Type. Another type is {}".format
            raise TypeError(msg(type(other)))
        return (self.count, self.name) < (other.count, other.name)

    def display(self, count_max):
        return "{count:>{count_max}} {name}".format(
            name=self.name,
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
    _count_max = 0
    for entry in os.scandir(path):
        if ignore_dot_file and entry.name.startswith("."):
            continue
        _e = Entry.from_scandir(entry)
        if _e is None:
            continue
        _count_max = max(_count_max, len(str(_e.count)))
        result.append(_e)
    result.sort()
    return result, _count_max


def main():
    lst, s = list_files_count()
    for e in lst:
        print(e.display(s))


if __name__ == '__main__':
    main()

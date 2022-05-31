# Standard Library
from abc import ABC
from dataclasses import dataclass, fields
from typing import Any


@dataclass()
class BaseResultData(ABC):
    def keys(self):
        return [f.name for f in fields(self)]

    def values(self):
        return [self.__dict__[f] for f in self.keys()]

    def __iter__(self):
        return iter(self.__dict__)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    @property
    def name(self):
        return self.__module__.split(".")[-1]


@dataclass(frozen=True)
class ResultSet:
    title: str
    body: str
    data: list[Any]

    @property
    def data_headers(self):
        try:
            return list(self.data[0].keys())
        except IndexError:
            return []

    @property
    def data_list(self):
        return [d.values() for d in self.data_flat_dict]

    @property
    def data_flat_dict(self):
        if not self.has_data:
            return []

        rows = []
        for row in self.data:
            _row = {key: ", ".join(row[key]) if isinstance(row[key], list) else row[key] for key in row}

            rows.append(_row)
        return rows

    @property
    def has_data(self):
        return len(self.data) > 0

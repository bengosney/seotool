# Standard Library
from typing import Dict, List

# Third Party
from pydantic.dataclasses import dataclass


@dataclass
class ResultSet:
    title: str
    body: str
    data: List[Dict[str, str]]

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

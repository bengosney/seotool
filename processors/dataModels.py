from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ResultSet:
    title: str
    body: str
    data: List[Dict[str, str]]

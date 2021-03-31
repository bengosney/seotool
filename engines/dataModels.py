# Third Party
from pydantic.dataclasses import dataclass


@dataclass
class response:
    status_code: int
    headers: dict
    body: str
    url: str

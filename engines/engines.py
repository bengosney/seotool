from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class response:
    status_code: int
    headers: dict
    body: str
    url: str


class engine(ABC):
    @abstractmethod
    def get(self, url:str, **kwargs):
        pass

class EngineException(Exception):
    pass
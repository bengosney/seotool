from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class response:
    status_code: int
    headers: dict
    body: str
    url: str


class engine(ABC):
    @abstractmethod
    async def get(self, url: str, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class EngineException(Exception):
    pass

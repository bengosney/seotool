# Standard Library
import asyncio
from types import TracebackType
from typing import Optional, Type

QueueType = asyncio.Queue[Optional[str]]


class Queue:
    def __init__(self, worker_count: int = 1) -> None:
        self._waiting: int = 0
        self._worker_count: int = worker_count
        self._queue: QueueType = asyncio.Queue()

    @property
    def waiting(self) -> int:
        return self._waiting

    @property
    def worker_count(self) -> int:
        return self._worker_count

    @property
    def queue(self) -> QueueType:
        return self._queue

    async def put(self, item: str) -> None:
        return await self.queue.put(item)

    def empty(self) -> bool:
        return self.queue.empty()

    async def try_stop(self) -> bool:
        if self.can_stop():
            await self.stop_waiting()
            return True
        return False

    def can_stop(self) -> bool:
        return self.waiting >= (self.worker_count - 1)

    async def stop_waiting(self) -> None:
        for _ in range(self.waiting):
            await self._queue.put(None)

    async def __aenter__(self) -> QueueType:
        self._waiting += 1
        return self._queue

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        self._waiting -= 1

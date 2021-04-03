# Standard Library
import asyncio


class Queue:
    def __init__(self, worker_count=1) -> None:
        self._waiting = 0
        self._worker_count = worker_count
        self._queue = asyncio.Queue()

    @property
    def waiting(self):
        return self._waiting

    @property
    def worker_count(self):
        return self._worker_count

    @property
    def queue(self):
        return self._queue

    async def put(self, item):
        return await self.queue.put(item)

    def empty(self):
        return self.queue.empty()

    async def try_stop(self):
        if self.can_stop():
            await self.stop_waiting()
            return True
        return False

    def can_stop(self):
        return self.waiting >= (self.worker_count - 1)

    async def stop_waiting(self):
        for _ in range(self.waiting):
            await self._queue.put(None)

    async def __aenter__(self):
        self._waiting += 1
        return self._queue

    async def __aexit__(self, exc_type, exc, tb):
        self._waiting -= 1

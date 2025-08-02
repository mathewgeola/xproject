from asyncio import PriorityQueue, TimeoutError, wait_for
from typing import Any


class AsyncioPriorityQueue(PriorityQueue):
    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize)

    async def get(self) -> Any:
        coroutine = super().get()
        try:
            return await wait_for(coroutine, timeout=0.1)
        except TimeoutError:
            return None

from abc import ABC
from collections.abc import Awaitable
from typing import Any, Self

from xproject.xcall import async_call_method


class AsyncCreateInstanceMixin(ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._is_closed: bool | None = None

    @classmethod
    def create_instance(cls, *args: Any, **kwargs: Any) -> Self | Awaitable[Self]:
        return cls(*args, **kwargs)

    async def open(self) -> None:
        if self.is_closed:
            await async_call_method(method=self._open)
        self._is_closed = False

    def _open(self) -> None:
        pass

    async def close(self) -> None:
        if not self.is_closed:
            await async_call_method(method=self._close)
        self._is_closed = True

    def _close(self) -> None:
        pass

    @property
    def is_closed(self) -> bool:
        return True if self._is_closed is True or self._is_closed is None else False

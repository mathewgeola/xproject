from abc import ABC
from asyncio import run
from atexit import register
from types import TracebackType
from typing import Any, Self

from xproject.xcall import async_call_method
from xproject.xmixins.xobject_mixins.xasync_create_instance_object_mixin import AsyncCreateInstanceObjectMixin


class AsyncContextManagerObjectMixin(AsyncCreateInstanceObjectMixin, ABC):
    @classmethod
    async def create_instance(cls, *args: Any, auto_call: bool = True, **kwargs: Any) -> Self:
        instance = await super().create_instance(*args, **kwargs)
        if auto_call:
            await async_call_method(method=instance._open)
            register(lambda: run(async_call_method(method=instance._close)))
        return instance

    async def __aenter__(self) -> Self:
        await async_call_method(method=self._open)
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> None:
        await async_call_method(method=self._close)

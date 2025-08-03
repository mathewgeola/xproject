from abc import ABC
from asyncio import run
from atexit import register
from types import TracebackType
from typing import Any, Self

from xproject.xmixins.xcreate_instance_mixin import CreateInstanceMixin
from xproject.xcall import async_call_method


class ContextManagerMixin(CreateInstanceMixin, ABC):
    @classmethod
    async def create_instance(cls, *args: Any, auto_call: bool = False, **kwargs: Any) -> Self:
        instance = cls(*args, **kwargs)
        if auto_call:
            await async_call_method(method=instance.open)
            register(lambda: run(async_call_method(method=instance.close)))
        return instance

    async def __aenter__(self) -> Self:
        await async_call_method(method=self.open)
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> None:
        await async_call_method(method=self.close)

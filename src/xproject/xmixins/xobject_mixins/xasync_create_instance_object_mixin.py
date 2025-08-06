from typing import Any, Self

from xproject.xcall import async_call_method
from xproject.xmixins.xobject_mixins.xobject_mixin import ObjectMixin


class AsyncCreateInstanceObjectMixin(ObjectMixin):
    @classmethod
    async def create_instance(cls, *args: Any, **kwargs: Any) -> Self:
        return super().create_instance(*args, **kwargs)

    async def _open(self) -> None:
        if self.is_closed:
            await async_call_method(method=self.open)
        self._is_closed = False

    async def _close(self) -> None:
        if not self.is_closed:
            await async_call_method(method=self.close)
        self._is_closed = True

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

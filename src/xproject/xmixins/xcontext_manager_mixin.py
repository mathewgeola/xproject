from abc import ABC
from atexit import register
from types import TracebackType
from typing import Any, Self

from xproject.xcall import call_method
from xproject.xmixins.xcreate_instance_mixin import CreateInstanceMixin


class ContextManagerMixin(CreateInstanceMixin, ABC):
    @classmethod
    def create_instance(cls, *args: Any, auto_call: bool = True, **kwargs: Any) -> Self:
        instance = cls(*args, **kwargs)
        if auto_call:
            call_method(method=instance.open)
            register(lambda: call_method(method=instance.close))
        return instance

    def __enter__(self) -> Self:
        call_method(method=self.open)
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> None:
        call_method(method=self.close)

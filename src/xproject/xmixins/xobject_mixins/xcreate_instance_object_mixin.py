from typing import Any, Self

from xproject.xcall import call_method
from xproject.xmixins.xobject_mixins.xobject_mixin import ObjectMixin


class CreateInstanceObjectMixin(ObjectMixin):
    @classmethod
    def create_instance(cls, *args: Any, **kwargs: Any) -> Self:
        return super().create_instance(*args, **kwargs)

    def _open(self) -> None:
        if self.is_closed:
            call_method(method=self.open)
        self._is_closed = False

    def _close(self) -> None:
        if not self.is_closed:
            call_method(method=self.close)
        self._is_closed = True

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

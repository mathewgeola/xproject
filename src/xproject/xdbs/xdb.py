from typing import Any, Self

from xproject.xmixins.xcontext_manager_mixin import ContextManagerMixin


class DB(ContextManagerMixin):
    @classmethod
    def from_uri(cls, *args: Any, **kwargs: Any) -> Self:
        ins = cls.create_instance(*args, **kwargs)
        return ins

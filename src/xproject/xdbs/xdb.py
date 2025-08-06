from typing import Any, Self

from xproject.xmixins.xobject_mixins.xcontext_manager_object_mixin import ContextManagerObjectMixin


class DB(ContextManagerObjectMixin):
    @classmethod
    def from_uri(cls, *args: Any, **kwargs: Any) -> Self:
        ins = super().create_instance(*args, **kwargs)
        return ins

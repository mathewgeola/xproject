import os
from abc import ABCMeta
from inspect import getmodule
from typing import Any, Self


class DirPathMixinMeta(ABCMeta):
    def __new__(
            mcls: type[Self],
            name: str,
            bases: tuple[type, ...],
            namespace: dict[str, Any],
            /,
            **kwargs: Any
    ) -> Self:
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        if namespace.get("dir_path") is None:
            if (module := getmodule(cls)) is not None and hasattr(module, "__file__"):
                cls.dir_path = os.path.dirname(os.path.abspath(module.__file__))
            else:
                cls.dir_path = None

        return cls


class DirPathMixin(metaclass=DirPathMixinMeta):
    dir_path: str | None

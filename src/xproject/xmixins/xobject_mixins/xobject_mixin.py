from abc import ABC
from typing import Any, Self


class ObjectMixin(ABC):
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        return super().__new__(cls)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._is_closed: bool | None = None

    @classmethod
    def create_instance(cls, *args: Any, **kwargs: Any) -> Self:
        return cls(*args, **kwargs)

    @property
    def is_closed(self) -> bool:
        return True if self._is_closed is True or self._is_closed is None else False

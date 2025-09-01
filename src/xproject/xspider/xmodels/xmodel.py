from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from xproject.xspider.xitems.xitem import Item


class Model(ABC):
    @classmethod
    @abstractmethod
    def columns(cls) -> list[str]:
        ...

    @classmethod
    def save(cls, data: dict[str, Any] | Item) -> bool:
        ...

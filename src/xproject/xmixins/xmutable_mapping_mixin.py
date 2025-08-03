from collections.abc import MutableMapping, Iterator
from copy import deepcopy
from pprint import pformat
from typing import Any, Self

from xproject.xtypes import ViewClasses, create_view_classes

Data = dict[str, Any]


class MutableMappingMixin(MutableMapping):
    def __init__(self) -> None:
        self._data: Data = dict()

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}\n{pformat(self._data)}\n>"

    __str__ = __repr__

    def to_dict(self) -> dict[str, Any]:
        return dict(self)

    def copy(self) -> Self:
        return deepcopy(self)

    @classmethod
    @property
    def view_classes(cls) -> ViewClasses:  # noqa
        return create_view_classes(cls.__name__)

    def items(self) -> ViewClasses.ItemsView:
        return self.view_classes.ItemsView(self)

    def keys(self) -> ViewClasses.KeysView:
        return self.view_classes.KeysView(self)

    def values(self) -> ViewClasses.ValuesView:
        return self.view_classes.ValuesView(self)

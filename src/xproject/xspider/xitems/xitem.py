from __future__ import annotations

import re
from abc import ABCMeta
from collections.abc import MutableMapping, Iterator
from copy import deepcopy
from pprint import pformat
from types import new_class
from typing import Any, Self, Final

from scrapy.item import Field as ScrapyField, Item as ScrapyItem

from xproject.xexceptions import InitException, GetattributeException
from xproject.xspider.xitems.xfield import Field
from xproject.xspider.xmodels.xmodel import Model
from xproject.xtypes import ViewClasses, create_view_classes


class ScrapyItemImpl(ScrapyItem):
    def to_item(self) -> Item: ...


class ItemMeta(ABCMeta):
    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> type:
        fields = dict()
        new_attrs = dict()

        if (model_class := attrs.get("MODEL")) is not None:
            model_class: Model
            for column in model_class.columns():
                fields[column] = Field()

        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
            else:
                new_attrs[key] = value

        cls = super().__new__(mcs, name, bases, new_attrs)

        cls._FIELDS = fields

        cls.SCRAPY_ITEM = new_class(
            re.sub(r"Item$", "", name) + "ScrapyItem", (ScrapyItem,),
            exec_body=lambda ns: ns.update(
                {field: ScrapyField() for field in cls._FIELDS} |
                {"to_item": lambda self: cls.create_by_scrapy_item(self)}  # noqa
            )
        )

        return cls


class Item(MutableMapping, metaclass=ItemMeta):
    _FIELDS: dict[str, Field]
    MODEL: Model
    SCRAPY_ITEM: type[ScrapyItemImpl]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._item: Final[dict[str, Any]] = dict()

        if args:
            raise InitException(
                f"{self.__class__.__name__} initialization failed: "
                "Positional arguments are not supported "
                "(use keyword arguments instead)"
            )
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._FIELDS:
            self._item[key] = value
        else:
            raise KeyError(
                f"{self.__class__.__name__} field assignment error: "
                f"Field {key!r} is not defined "
                f"(add the field to class definition first)"
            )

    def __delitem__(self, key: str) -> None:
        del self._item[key]

    def __getitem__(self, key: str) -> Any:
        return self._item[key]

    def __setattr__(self, name: str, value: Any) -> None:
        if name != "_item":
            raise AttributeError(
                f"{self.__class__.__name__} attribute assignment error: "
                f"Cannot set attribute {name!r} directly "
                f"(to set a field value, use item[{name!r}] = {value!r} instead)"
            )
        super().__setattr__(name, value)

    def __getattribute__(self, name: str) -> Any:
        fields = super().__getattribute__("_FIELDS")
        if name in fields:
            raise GetattributeException(
                f"{self.__class__.__name__} attribute access error: "
                f"Cannot get attribute {name!r} directly "
                f"(to access a field value, use item[{name!r}] instead)"
            )
        return super().__getattribute__(name)

    def __getattr__(self, name: str) -> None:
        raise AttributeError(
            f"{self.__class__.__name__} attribute access error: "
            f"Attribute {name!r} is not defined "
            f"(to access a field value, first add the field to class definition, then use item[{name!r}])"
        )

    def __iter__(self) -> Iterator[str]:
        return iter(self._item)

    def __len__(self) -> int:
        return len(self._item)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}\n{pformat(self._item)}\n>"

    __str__ = __repr__

    def to_dict(self) -> dict[str, Any]:
        return dict(self)

    def to_scrapy_item(self) -> ScrapyItemImpl:
        return self.SCRAPY_ITEM(**self.to_dict())

    @classmethod
    def create_by_scrapy_item(cls, scrapy_item: ScrapyItem) -> Self:
        return cls(**dict(scrapy_item))

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

    @property
    def unassigned_keys(self) -> list[str]:
        return [k for k in self._FIELDS.keys() if k not in self._item.keys()]


__all__ = [
    "Item"
]

if __name__ == '__main__':
    def main():
        class TestItem(Item):
            name = Field()
            age = Field()

        try:
            item = TestItem("xspider", 18)
        except Exception as e:
            print(type(e), e)

        try:
            item = TestItem()
            item["gender"] = "man"
        except Exception as e:
            print(type(e), e)

        try:
            item = TestItem()
            item.gender = "man"
        except Exception as e:
            print(type(e), e)

        try:
            item = TestItem()
            print(item.name)
        except Exception as e:
            print(type(e), e)

        try:
            item = TestItem()
            print(item.gender)
        except Exception as e:
            print(type(e), e)

        item = TestItem()
        item["name"] = "xproject"
        item["age"] = 18
        print(item)

        print(item.items())


    main()

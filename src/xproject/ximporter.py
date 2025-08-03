from __future__ import annotations

from importlib import import_module
from inspect import isclass

from xproject.xexceptions import ImportClassTypeError
from xproject.xvalidators import is_str


def import_class(class_ref: str | type) -> type:
    if is_str(class_ref):
        module_path, class_name = class_ref.rsplit(".", maxsplit=1)
        module = import_module(module_path)
        cls = getattr(module, class_name, None)
    elif isclass(class_ref):
        cls = class_ref
    else:
        raise ImportClassTypeError(
            f"Invalid type for 'class_ref': "
            f"Expected `str | type`, "
            f"but got {type(class_ref).__name__!r} (value: {class_ref!r})"
        )
    return cls

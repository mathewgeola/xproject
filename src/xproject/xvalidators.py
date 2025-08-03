from typing import Any, TypeGuard


def is_bool(obj: Any) -> TypeGuard[bool]:
    return isinstance(obj, bool)


def is_int(obj: Any) -> TypeGuard[int]:
    return isinstance(obj, int) and not isinstance(obj, bool)


def is_str(val: Any) -> TypeGuard[str]:
    return isinstance(val, str)


def is_list(val: Any) -> TypeGuard[list[Any]]:
    return isinstance(val, list)


def is_list_of[T](val: list[Any], ele_type: type[T]) -> TypeGuard[list[T]]:
    return isinstance(val, list) and all(isinstance(i, ele_type) for i in val)


__all__ = [
    "is_bool", "is_int", "is_str", "is_list", "is_list_of",
]

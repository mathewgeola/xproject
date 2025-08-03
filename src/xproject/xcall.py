from collections.abc import Callable, Awaitable
from inspect import iscoroutinefunction, ismethod
from typing import Any


async def async_call_method(
        *,
        method: Callable[..., Awaitable[Any] | Any] | None = None,
        obj: Any = None,
        method_name: str | None = None,
        method_args: tuple[Any, ...] | None = None,
        method_kwargs: dict[str, Any] | None = None
) -> Any:
    if method is None:
        if obj is not None and method_name is not None:
            method = getattr(obj, method_name, None)
    if method is None:
        return None
    if method_args is None:
        method_args = tuple()
    if method_kwargs is None:
        method_kwargs = dict()
    if iscoroutinefunction(method):
        return await method(*method_args, **method_kwargs)
    if ismethod(method):
        return method(*method_args, **method_kwargs)
    raise TypeError(
        f"Invalid type for 'method': "
        f"Expected `Callable[..., Awaitable[Any] | Any] | None`, "
        f"but got {type(method).__name__} (value: {method!r})"
    )

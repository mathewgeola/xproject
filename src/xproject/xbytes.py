from collections.abc import Buffer

from ujson import dumps


def to_bytes(
        data: bytes | str | dict,
        /, *,
        dict_sort_keys: bool = False,
        encoding: str = "utf-8"
) -> Buffer:
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode(encoding)
    if isinstance(data, dict):
        return dumps(data, sort_keys=dict_sort_keys).encode(encoding)
    raise TypeError(
        f"Invalid type for 'data': "
        f"Expected `bytes | str | dict`, "
        f"but got {type(data).__name__!r} (value: {data!r})"
    )

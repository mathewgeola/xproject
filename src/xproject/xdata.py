import hashlib
from typing import Any, Literal

ALGO_TYPE = Literal[
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s", "sha3_224", "sha3_256", "sha3_384",
    "sha3_512", "shake_128", "shake_256"
]


def gen_data_id(
        *args: Any,
        keys: list | None = None, item: dict | None = None,
        algo_type: ALGO_TYPE = "sha256"
) -> str:
    """
    >>> gen_data_id("123456")
    '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'

    :param args:
    :param keys:
    :param item:
    :param algo_type:
    :return:
    """
    m = hashlib.new(algo_type)
    if args:
        values = args
    elif keys is not None and item is not None:
        if isinstance(keys, list) and isinstance(item, dict):
            values = [item[k] for k in keys if k in item]
        else:
            raise TypeError(
                f"Invalid type for 'keys': "
                f"Expected `list | None`, "
                f"but got {type(keys).__name__} (value: {keys!r})\n"
                f"Invalid type for 'item': "
                f"Expected `dict | None`, "
                f"but got {type(item).__name__} (value: {item!r})"
            )
    elif item is not None:
        values = [item[k] for k in sorted(item.keys())]
    else:
        raise ValueError(
            f"Either args: {args!r} or keys: {keys!r} and item: {item!r} or item: {item!r} must be provided"
        )

    data = list(map(lambda x: str(x), values))

    for i in data:
        m.update(i.encode())

    data_id = m.hexdigest()
    return data_id

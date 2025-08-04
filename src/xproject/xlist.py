from typing import Any


def split_list(data: list[Any], num_parts: int | None = None, part_size: int | None = None) -> list[Any]:
    if not data:
        return []

    if num_parts:
        avg_size = len(data) // num_parts
        remainder = len(data) % num_parts

        result = []
        result.extend([data[start:start + avg_size] for start in range(0, len(data) - avg_size - remainder, avg_size)])
        result.append(data[len(data) - avg_size - remainder:])
        return result

    elif part_size:
        return [data[i:i + part_size] for i in range(0, len(data), part_size)]

    else:
        raise ValueError(
            f"Either num_parts: {num_parts!r} or part_size: {part_size!r} must be provided"
        )

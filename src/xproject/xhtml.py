import html
from typing import Any

from htmlmin import minify


def compress_html(*args: Any, **kwargs: Any) -> str:
    return minify(*args, **kwargs)


def escape(text: str) -> str:
    """
    >>> escape("<")
    '&lt;'

    """
    return html.escape(text)


def unescape(text: str) -> str:
    """
    >>> unescape("&lt;")
    '<'

    """
    return html.unescape(text)

import sqlparse
from typing import Any


def format_sql(sql: str, **kwargs: Any) -> str:
    if not kwargs:
        kwargs = dict(
            reindent=True,
            keyword_case="upper",
            identifier_case="lower",
            strip_comments=True
        )
    sql = sqlparse.format(sql, **kwargs)
    return sql

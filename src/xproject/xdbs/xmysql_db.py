from typing import Any

import pandas as pd
from pymysql import connect
from pymysql.connections import Connection
from pymysql.cursors import Cursor

from xproject.xdbs.xdb import DB


class MysqlDB(DB):

    def __init__(
            self,
            *args: Any,
            host: str = "localhost",
            port: int = 3306,
            username: str | None = None,
            password: str | None = None,
            dbname: str,
            charset: str = "utf8mb4",
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._dbname = dbname
        self._charset = charset

        self._connection: Connection | None = None
        self._cursor: Cursor | None = None

    def open_connect(self) -> tuple[Connection, Cursor]:
        connection = connect(
            user=self._username,
            password=self._password,
            host=self._host,
            database=self._dbname,
            port=self._port,
            charset=self._charset,
        )
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def close_connect(connection: Connection | None = None, cursor: Cursor | None = None) -> None:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

    def open(self) -> None:
        self._connection, self._cursor = self.open_connect()

    def close(self) -> None:
        self.close_connect(self._connection, self._cursor)

    @property
    def connection(self) -> Connection:
        return self._connection

    @property
    def cursor(self) -> Cursor:
        return self._cursor

    def query(
            self,
            sql: str,
            connection_cursor: tuple[Connection, Cursor] | None = None,
            use_new_connect: bool = True,  # Using False is in single thread
            return_df: bool = False
    ) -> list[dict[str, Any]] | pd.DataFrame:
        if connection_cursor is not None:
            connection, cursor = connection_cursor
        else:
            if use_new_connect:
                connection_cursor = self.open_connect()
                connection, cursor = connection_cursor
            else:
                connection, cursor = self._connection, self._cursor

        cursor.execute(sql)
        result = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
        rows = [dict(zip(columns, r)) for r in result]

        if connection_cursor is not None:
            self.close_connect(connection, cursor)

        if return_df:
            return pd.DataFrame(rows)

        return rows

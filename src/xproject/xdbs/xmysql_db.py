from typing import Any

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

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname
        self.charset = charset

        self._connection: Connection | None = None
        self._cursor: Cursor | None = None

    def open_connect(self) -> tuple[Connection, Cursor]:
        connection = connect(
            user=self.username,
            password=self.password,
            host=self.host,
            database=self.dbname,
            port=self.port,
            charset=self.charset,
        )
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def close_connect(connection: Connection | None = None, cursor: Cursor | None = None) -> None:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

    def _open(self) -> None:
        self._connection, self._cursor = self.open_connect()

    def _close(self) -> None:
        self.close_connect(self._connection, self._cursor)

    def query(self, sql: str, connection_cursor: tuple[Connection, Cursor] | None = None) -> list[dict[str, Any]]:
        if connection_cursor is not None:
            connection, cursor = connection_cursor
        else:
            connection, cursor = self._connection, self._cursor

        cursor.execute(sql)
        result = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
        rows = [dict(zip(columns, r)) for r in result]

        if connection_cursor is not None:
            self.close_connect(connection, cursor)

        return rows

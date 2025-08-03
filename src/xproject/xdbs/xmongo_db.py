from typing import Any
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from xproject.xdbs.xdb import DB


class MongoDB(DB):
    def __init__(
            self,
            *args: Any,
            host: str = "localhost",
            port: int = 27017,
            username: str | None = None,
            password: str | None = None,
            dbname: str,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname

        self.client: MongoClient | None = None
        self.db: Database | None = None

    def _open(self) -> None:
        if self.username and self.password:
            uri = "mongodb://%s:%s@%s:%s" % (quote_plus(self.username), quote_plus(self.password), self.host, self.port)
        else:
            uri = "mongodb://%s:%s" % (self.host, self.port)

        self.client = MongoClient(uri)
        self.db = self.client[self.dbname]

    def _close(self) -> None:
        self.db = None

        self.client.close()
        self.client = None

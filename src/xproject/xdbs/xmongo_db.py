from typing import Any, Self
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.database import Database

from xproject.xdbs.xdb import DB


class MongoDB(DB):
    def __init__(
            self,
            *args: Any,
            host: str = "localhost",
            port: int = 27017,
            username: str | None = None,
            password: str | None = None,
            uri: str | None = None,
            dbname: str,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._uri = uri
        self._dbname = dbname

        self._client: MongoClient | None = None
        self._db: Database | None = None

    @classmethod
    def from_uri(cls, uri: str, dbname: str) -> Self:
        ins = super().from_uri(**dict(uri=uri, dbname=dbname))
        return ins

    def open(self) -> None:
        if self._uri is not None:
            uri = self._uri
        else:
            if self._username is not None and self._password is not None:
                uri = "mongodb://%s:%s@%s:%s" % (
                    quote_plus(self._username), quote_plus(self._password), self._host, self._port
                )
            else:
                uri = "mongodb://%s:%s" % (self._host, self._port)

        self._client = MongoClient(uri)
        self._db = self._client[self._dbname]

    def close(self) -> None:
        self._db = None

        self._client.close()
        self._client = None

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def db(self) -> Database:
        return self._db

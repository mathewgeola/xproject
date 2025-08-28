from typing import Any, Self

from redis import Redis

from xproject.xdbs.xdb import DB
from xproject.xurl import get_furl_obj


class RedisDB(DB):
    def __init__(
            self,
            *args: Any,
            host: str = "localhost",
            port: int = 6379,
            password: str | None = None,
            dbname: int = 0,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self._host = host
        self._port = port
        self._password = password
        self._dbname = dbname

        self._redis: Redis | None = None

    def open(self) -> None:
        self._redis = Redis(
            host=self._host,
            port=self._port,
            db=self._dbname,
            password=self._password,
            encoding="utf-8",
            decode_responses=True
        )

    def close(self) -> None:
        self._redis.close()
        self._redis = None

    @property
    def redis(self) -> Redis:
        return self._redis

    @classmethod
    def from_uri(cls, uri: str) -> Self:
        furl = get_furl_obj(uri)
        kwargs = dict()
        kwargs["host"] = furl.host
        kwargs["port"] = furl.port
        kwargs["password"] = furl.password
        kwargs["dbname"] = furl.path.segments[0]
        return super().from_uri(**kwargs)

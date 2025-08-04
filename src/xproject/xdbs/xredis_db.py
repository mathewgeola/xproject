from typing import Any

from redis import Redis

from xproject.xdbs.xdb import DB


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

        self.host = host
        self.port = port
        self.password = password
        self.dbname = dbname

        self._redis: Redis | None = None

    def _open(self) -> None:
        self._redis = Redis(
            host=self.host,
            port=self.port,
            db=self.dbname,
            password=self.password,
            encoding="utf-8",
            decode_responses=True
        )

    def _close(self) -> None:
        self._redis.close()
        self._redis = None

import xproject


def test():
    redis_db = xproject.RedisDB.from_uri("redis://127.0.0.1:6379/0")
    redis_db.redis.lpush("test", 1, 2, 3)


if __name__ == '__main__':
    test()

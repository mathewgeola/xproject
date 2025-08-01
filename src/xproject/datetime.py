import arrow


def now(fmt: str = "YYYY-MM-DD HH:mm:ss") -> str:
    return arrow.now().format(fmt)


def delta(start_datetime_str: str, end_datetime_str: str) -> int:
    start_datetime = arrow.get(start_datetime_str).datetime
    end_datetime = arrow.get(end_datetime_str).datetime
    seconds = (end_datetime - start_datetime).total_seconds()
    return int(seconds)


if __name__ == '__main__':
    print(now())
    print(delta("2025-08-01 00:00:00", "2025-08-01 11:11:11"))

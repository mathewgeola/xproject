import xproject


def test_xlogger():
    logger = xproject.get_logger(to_file=True, file_max_bytes=1024 * 1, file_backup_count=3)
    for i in range(10000):
        logger.info(f"test-{i}")


if __name__ == '__main__':
    test_xlogger()

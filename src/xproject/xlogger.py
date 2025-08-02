import logging
import os
import sys
from logging import handlers
from typing import Any, Literal, Final, TypeVar, cast

import colorlog

FRAMEWORK: Final[int] = 55
SUCCESS: Final[int] = 25

logging.addLevelName(FRAMEWORK, "FRAMEWORK")
logging.addLevelName(SUCCESS, "SUCCESS")

LoggerLevel = Literal["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL", "FRAMEWORK"]
LoggerLevelT = TypeVar("LoggerLevelT", bound=LoggerLevel)


class Logger(logging.Logger):
    def framework(
            self,
            msg: str,
            *args: Any,
            level: LoggerLevelT = "DEBUG",
            **kwargs: Any
    ) -> None:
        if self.isEnabledFor(FRAMEWORK):
            msg = f"[{level}] {msg}"
            self._log(FRAMEWORK, msg, args, **kwargs, stacklevel=2)

    def success(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs, stacklevel=2)


logging.setLoggerClass(Logger)


class RotatingFileHandler(handlers.RotatingFileHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._zero_padding: Final[int] = len(str(self.backupCount)) if self.backupCount > 0 else 0

    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None  # noqa

        if self.backupCount > 0:
            oldest = self._format_backup_filename(self.backupCount)
            if os.path.exists(oldest):
                os.remove(oldest)

            for i in range(self.backupCount - 1, 0, -1):
                sfn = self._format_backup_filename(i)
                dfn = self._format_backup_filename(i + 1)
                if os.path.exists(sfn):
                    os.rename(sfn, dfn)

            dfn = self._format_backup_filename(1)
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)

        self.mode = "w"
        self.stream = self._open()

    def _format_backup_filename(self, index: int) -> str:
        base, ext = os.path.splitext(self.baseFilename)
        padded = str(index).zfill(self._zero_padding)
        return f"{base}.{padded}{ext}"


def _set_console_handler(
        _logger: Logger,
        console_level: str | int, console_fmt: str
) -> Logger:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    green = {
        "DEBUG": "green",
        "INFO": "green",
        "SUCCESS": "green",
        "WARNING": "green",
        "ERROR": "green",
        "CRITICAL": "green",
        "FRAMEWORK": "green",
    }
    bold_cyan = {
        "DEBUG": "bold_cyan",
        "INFO": "bold_cyan",
        "SUCCESS": "bold_cyan",
        "WARNING": "bold_cyan",
        "ERROR": "bold_cyan",
        "CRITICAL": "bold_cyan",
        "FRAMEWORK": "bold_cyan",
    }
    log_colors = {
        "DEBUG": "light_blue",
        "INFO": "light_white",
        "SUCCESS": "light_green",
        "WARNING": "light_yellow",
        "ERROR": "light_red",
        "CRITICAL": "bg_red,light_white",
        "FRAMEWORK": "light_red,bold",
    }
    secondary_log_colors = dict(
        asctime=green,
        name=bold_cyan,
        levelname=log_colors,
        process=bold_cyan,
        processName=bold_cyan,
        thread=bold_cyan,
        threadName=bold_cyan,
        pathname=bold_cyan,
        funcName=bold_cyan,
        lineno=bold_cyan,
        message=log_colors,
    )
    console_formatter = colorlog.ColoredFormatter(
        console_fmt,
        secondary_log_colors=secondary_log_colors,
    )
    console_handler.setFormatter(console_formatter)
    _logger.addHandler(console_handler)
    return _logger


def _set_file_handler(
        _logger: Logger,
        file_level: str | int, file_fmt: str,
        file_path: str, file_mode: str, file_max_bytes: int, file_backup_count: int, file_encoding: str,
) -> Logger:
    file_handler = RotatingFileHandler(
        file_path,
        mode=file_mode, maxBytes=file_max_bytes, backupCount=file_backup_count, encoding=file_encoding
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(file_fmt)
    file_handler.setFormatter(file_formatter)
    _logger.addHandler(file_handler)
    return _logger


def get_logger(
        name: str | None = None,
        level: str = "DEBUG",
        to_console: bool = True,
        console_level: str = "DEBUG",
        console_fmt: str = (
                "%(asctime_log_color)s%(asctime)s %(reset)s| "
                "%(name_log_color)s%(name)s %(reset)s| "
                "%(levelname_log_color)s%(levelname)s %(reset)s| "
                # "%(process_log_color)sProcess: %(process)d %(processName_log_color)s(%(processName)s) %(reset)s| "
                # "%(thread_log_color)sThread: %(thread)d %(threadName_log_color)s(%(threadName)s) %(reset)s| "
                # "%(pathname_log_color)s%(pathname)s %(reset)s| "
                "%(funcName_log_color)s%(funcName)s:%(lineno)d %(reset)s- "
                "%(message_log_color)s%(message)s"
        ),
        to_file: bool = False,
        file_level: str = "DEBUG",
        file_path: str | None = None,
        file_mode: str = "a",
        file_max_bytes: int = 10 * 1024 * 1024,
        file_backup_count: int = 20,
        file_encoding: str = "utf8",
        file_fmt: str = (
                "%(asctime)s | "
                "%(name)s | "
                "%(levelname)s | "
                # "Process: %(process)d (%(processName)s) | "
                # "Thread: %(thread)d (%(threadName)s) | "
                # "%(pathname)s | "
                "%(funcName)s:%(lineno)d - "
                "%(message)s"
        ),
) -> Logger:
    _path = os.path.abspath(sys.argv[0])
    _name = os.path.basename(_path)
    _prefix = os.path.splitext(_name)[0]
    _file_name = _prefix + ".log"
    _file_dir = os.path.dirname(_path)
    _file_path = os.path.join(_file_dir, _file_name)

    if name is None:
        name = _prefix
    _logger = cast(Logger, logging.getLogger(name))
    _logger.setLevel(level)

    if to_console:
        console_handler_exists = any(isinstance(handler, logging.StreamHandler) for handler in _logger.handlers)
        if not console_handler_exists:
            _set_console_handler(_logger,
                                 console_level=console_level,
                                 console_fmt=console_fmt)
    else:
        for handler in _logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                _logger.removeHandler(handler)

    if to_file:
        file_handler_exists = any(isinstance(handler, logging.FileHandler) for handler in _logger.handlers)
        if not file_handler_exists:
            if file_path is None:
                file_path = _file_path
            _set_file_handler(_logger,
                              file_level=file_level,
                              file_path=file_path, file_mode=file_mode, file_max_bytes=file_max_bytes,
                              file_backup_count=file_backup_count, file_encoding=file_encoding,
                              file_fmt=file_fmt)
    else:
        for handler in _logger.handlers:
            if isinstance(handler, logging.FileHandler):
                _logger.removeHandler(handler)

    return _logger


logger = get_logger()

__all__ = [
    "LoggerLevel",
    "Logger",
    "get_logger",
    "logger"
]

if __name__ == '__main__':
    logger.debug("debug message")
    logger.info("info message")
    logger.success("success message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    logger.framework("framework message")

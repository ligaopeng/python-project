from __future__ import annotations

import atexit
import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from queue import Queue
from typing import Any

from pythonjsonlogger.jsonlogger import JsonFormatter

# init root logger with null handler
logging.basicConfig(handlers=[logging.NullHandler()])

# init log queue for handler and listener
log_queue: Queue = Queue()
log_qlistener: QueueListener = QueueListener(log_queue, respect_handler_level=True)
log_qlistener.start()
atexit.register(log_qlistener.stop)


class StackdriverFormatter(JsonFormatter):
    def process_log_record(
        self: StackdriverFormatter, log_record: dict[str, Any]
    ) -> dict[str, Any]:
        log_record["severity"] = log_record["levelname"]
        return super().process_log_record(log_record)  # type: ignore [no-untyped-call]


def _get_log_formatter() -> StackdriverFormatter:
    # formatter
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(processName)s - %(threadName)s - %(filename)s - %(" \
                 "module)s - %(lineno)d - %(funcName)s - %(message)s "
    date_format = "%Y-%m-%dT%H:%M:%S"
    return StackdriverFormatter(
        fmt=log_format,
        datefmt=date_format,
        timestamp=True,
    )  # type: ignore[no-untyped-call]


def _get_file_handler(
    log_path: str = "main.log",
    log_level: int = logging.DEBUG,
    max_file_size_mb: int = 1,
    retention_days: int = 30,
) -> RotatingFileHandler:
    # 创建 "logs" 文件夹（如果不存在）
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_path_with_date = os.path.join(logs_folder, f"{log_path}.{current_date}")

    # 删除指定天数前的日志文件
    retention_date = datetime.now() - timedelta(days=retention_days)
    old_log_date = retention_date.strftime("%Y-%m-%d")
    old_log_path = f"{log_path}.{old_log_date}"
    if os.path.exists(old_log_path):
        os.remove(old_log_path)
    file_handler = RotatingFileHandler(
        log_path_with_date,
        maxBytes=max_file_size_mb * 2**20,  # 1 MB
        backupCount=10,  # 10 backups
        encoding="utf8",
        delay=True,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(_get_log_formatter())
    return file_handler


def _get_stdout_handler(log_level: int = logging.INFO) -> logging.StreamHandler:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    stdout_handler.setFormatter(_get_log_formatter())
    return stdout_handler


def configure_log_listener(
    *,
    console: bool = True,
    log_path: str = "main.log",
    max_file_size_mb: int = 1,
    retention_days: int = 30,
) -> QueueListener:
    """Configure log queue listener to log into file and console.

    Args:
    ----
        console (bool): whether to log on console
        log_path (str): path of log file
    Returns:
        log_qlistener (logging.handlers.QueueListener): configured log queue listener.
    """
    global log_qlistener  # noqa: PLW0603
    try:
        atexit.unregister(log_qlistener.stop)
        log_qlistener.stop()
    except (AttributeError, NameError):
        pass

    handlers: list[logging.Handler] = []

    # rotating file handler
    if log_path:
        file_handler = _get_file_handler(log_path, max_file_size_mb=max_file_size_mb, retention_days=retention_days)
        handlers.append(file_handler)

    # console handler
    if console:
        stdout_handler = _get_stdout_handler()
        handlers.append(stdout_handler)

    log_qlistener = QueueListener(log_queue, *handlers, respect_handler_level=True)
    log_qlistener.start()
    atexit.register(log_qlistener.stop)
    return log_qlistener


def get_logger(name: str, log_level: int = logging.DEBUG) -> logging.Logger:
    """Simple logging wrapper that returns logger
    configured to log into file and console.

    Args:
    ----
        name: name of logger
        log_level: log level
    Returns:
        logger: configured logger.
    """
    logger = logging.getLogger(name)
    for log_handler in logger.handlers[:]:
        logger.removeHandler(log_handler)

    logger.setLevel(log_level)
    logger.addHandler(QueueHandler(log_queue))

    return logger

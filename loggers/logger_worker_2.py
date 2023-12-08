"""
This module contains a function that configures
and initializes a logger for the application.
"""
import logging
from dirs_configs.config import LOG_DIR
import os


def get_worker_2_logger():
    """
    Configures and returns a Logger object.
    The logger is set up to write debug-level
    messages to
    """
    logger_worker_2 = logging.getLogger(__name__)
    logger_worker_2.setLevel(logging.DEBUG)
    log_file_path = LOG_DIR / "worker2.log"
    with open(log_file_path, "w", encoding='utf-8'):
        pass
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger_worker_2.addHandler(file_handler)
    return logger_worker_2

if __name__ == "__main__":
    logger_worker_2 = get_worker_2_logger()

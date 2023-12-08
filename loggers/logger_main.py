"""
This module contains a function that configures
and initializes a logger for the application.
"""
import logging
from dirs_configs.config import LOG_DIR
import os


def get_main_logger():
    """
    Configures and returns a Logger object.
    The logger is set up to write debug-level
    messages to
    """
    logger_main = logging.getLogger(__name__)
    logger_main.setLevel(logging.DEBUG)
    log_file_path = LOG_DIR / "main_py.log"
    with open(log_file_path, "w", encoding='utf-8'):
        pass
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger_main.addHandler(file_handler)
    return logger_main

if __name__ == "__main__":
    logger_main = get_main_logger()

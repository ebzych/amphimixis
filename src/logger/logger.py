"""Module to operate logging"""

import logging

LOG_FILE = "amixis.log"


def setup_logger() -> None:
    """Function to create root logger, which is used in other modules"""

    if logging.getLogger().hasHandlers():
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    """Function to return logger with specified name"""

    return logging.getLogger(name)

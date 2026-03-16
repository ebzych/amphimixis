"""Module to operate logging"""

import logging

LOG_FILE_NAME = "amphimixis.log"


def setup_logger(
    name: str, dummy_logging: bool = False, console_logging: bool = False
) -> logging.Logger:
    """Function to create logger with specified name"""

    if dummy_logging:
        logging.basicConfig(handlers=[logging.NullHandler()])
        return logging.getLogger(name.upper())

    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            handlers=[
                (
                    logging.FileHandler(LOG_FILE_NAME, encoding="utf-8")
                    if not console_logging
                    else logging.Handler()
                ),
            ],
        )

    return logging.getLogger(name.upper())

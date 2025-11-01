"""Module that contains constants for console output colors"""

from enum import Enum


class Colors(str, Enum):
    """Colors"""

    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    NONE = "\x1b[00m"

"""CLI module"""

from .parser import create_parser
from .templates import CONFIG_TEMPLATE, TOOLCHAIN_TEMPLATE

__all__ = [
    "create_parser",
    "TOOLCHAIN_TEMPLATE",
    "CONFIG_TEMPLATE",
]

"""CLI module"""

from amphimixis.cli.parser import create_parser
from amphimixis.cli.templates import CONFIG_TEMPLATE, TOOLCHAIN_TEMPLATE

__all__ = [
    "create_parser",
    "TOOLCHAIN_TEMPLATE",
    "CONFIG_TEMPLATE",
]

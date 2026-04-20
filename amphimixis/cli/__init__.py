"""CLI module"""

from amphimixis.cli.parser import create_parser
from amphimixis.cli.commands.add.input import get_unique_path
from amphimixis.cli.templates import CONFIG_TEMPLATE, TOOLCHAIN_TEMPLATE

__all__ = [
    "create_parser",
    "get_unique_path",
    "TOOLCHAIN_TEMPLATE",
    "CONFIG_TEMPLATE",
]

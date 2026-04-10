"""CLI module"""

from amphimixis.cli.parser import create_parser
from amphimixis.cli.templates import CONFIG_TEMPLATE, TOOLCHAIN_TEMPLATE
from amphimixis.general.constants import DEFAULT_CONFIG_PATH

__all__ = [
    "create_parser",
    "DEFAULT_CONFIG_PATH",
    "TOOLCHAIN_TEMPLATE",
    "CONFIG_TEMPLATE",
]

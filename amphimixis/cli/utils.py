"""CLI utilities - common functions for CLI commands."""

from pathlib import Path

DEFAULT_CONFIG_PATH = Path("input.yml").resolve()


def add_config_arg(parser):
    """Add --config argument to a parser.

    :param parser: subcommand parser to which arguments are added
    """

    parser.add_argument(
        "--config",
        nargs="?",
        const=str(DEFAULT_CONFIG_PATH),
        metavar="CONFIG",
        help="use a specific config file (default: input.yml)",
    )


def add_path_arg(parser):
    """Add positional 'path' argument to a parser.

    :param parser: subcommand parser to which arguments are added
    """

    parser.add_argument(
        "path",
        type=str,
        help="path to the project directory",
    )

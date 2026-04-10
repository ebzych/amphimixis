"""Parser for Amphimixis CLI with subcommands."""

import argparse
from pathlib import Path

from amphimixis.cli.commands import COMMANDS

DEFAULT_CONFIG_PATH = Path("input.yml").resolve()

MAIN_EXAMPLES = """
Examples:
  amixis run /path/to/project
      → Run full pipeline (analyze, build, profile)

  amixis analyze /path/to/project
      → Analyze project

  amixis build /path/to/project
      → Build project

  amixis profile /path/to/project --events cycles
      → Profile with perf events

  amixis validate input.yml
      → Validate config

  amixis compare file1.scriptout file2.scriptout
      → Compare two perf outputs

  amixis add input
      → Create input.yml interactively

  amixis add toolchain
      → Add toolchain to global config

  amixis clean
      → Clean builds interactively

  amixis clean --all
      → Clean all builds
"""

EXAMPLES = {
    "run": """Examples:
  amixis run /path/to/project
      → Run full pipeline (analyze, build, profile) on project""",
    "analyze": """Examples:
  amixis analyze /path/to/project
      → Analyze project and detect existing CI, tests, build systems, etc.""",
    "build": """Examples:
  amixis build /path/to/project
      → Build project according to generated configuration files
  amixis build /path/to/project --config custom.yml
      → Build with custom config file""",
    "profile": """Examples:
  amixis profile /path/to/project
      → Profile performance of builds
  amixis profile /path/to/project --events cycles cache-misses
      → Profile with specific perf events""",
    "validate": """Examples:
  amixis validate input.yml
      → Check config file correctness""",
    "compare": """Examples:
  amixis compare file1.scriptout file2.scriptout
      → Compare two perf output files
  amixis compare file1.scriptout file2.scriptout --max-rows 10
      → Compare with max 10 rows per event""",
    "clean": """Examples:
  amixis clean
      → Interactive mode: select builds to clean
  amixis clean --all
      → Clean all builds
  amixis clean build1 build2
      → Clean specific builds""",
    "add": """Examples:
  amixis add input
      → Interactively create input.yml configuration file
  amixis add toolchain
      → Interactively add a toolchain to global config""",
}


class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    """Custom formatter for better alignment."""

    def __init__(self, prog):
        super().__init__(prog, max_help_position=35)


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="amixis",
        formatter_class=CustomHelpFormatter,
        add_help=False,  # отключаем стандартный --help
        usage=argparse.SUPPRESS,
    )

    parser.add_argument(
        "-h",
        "--short-help",
        action="store_true",
        dest="short_help",
        help="show short help without examples",
    )
    parser.add_argument(
        "--help",
        action="store_true",
        dest="full_help",
        help="show full help with examples",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
        help="show version and exit",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="subcommands",
        required=False,
        metavar="<command>",
    )

    for name, cmd in COMMANDS.items():
        epilog = EXAMPLES.get(name, "")
        subparser = subparsers.add_parser(
            name,
            help=cmd.HELP_MESSAGE,
            epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        cmd.add_args(subparser)

    return parser


def add_config_arg(parser):
    """Add --config argument to a parser."""
    parser.add_argument(
        "--config",
        nargs="?",
        const=str(DEFAULT_CONFIG_PATH),
        metavar="CONFIG",
        help="use a specific config file (default: input.yml)",
    )


def add_path_arg(parser):
    """Add positional 'path' argument to a parser."""
    parser.add_argument(
        "path",
        type=str,
        help="path to the project directory",
    )

"""Opencode subcommands."""

from argparse import ArgumentParser, Namespace

from amphimixis.amixis.commands.opencode.install import run_opencode_install
from amphimixis.amixis.commands.opencode.run import run_opencode_run

HELP_MESSAGE = "Run Amphimixis LLM-agent in Opencode"

_INSTALL_SUBCMD = "install"
_RUN_SUBCMD = "run"


def opencode_args(parser: ArgumentParser) -> None:
    """Add arguments for opencode command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """

    subparsers = parser.add_subparsers(dest="add_subcommand", title="opencode options")
    subparsers.required = True

    subparsers.add_parser(
        _INSTALL_SUBCMD,
        help="install Amphimixis LLM-agent with tools into Opencode locally or globally",
    )

    subparsers.add_parser(
        _RUN_SUBCMD,
        help="run Amphimixis LLM-agent in Opencode with a specialized prompt",
    )


def run_add(args: Namespace) -> bool:
    """Execute add subcommand.

    :param Namespace args: parsed command line arguments
    :return: True if command succeeded, False otherwise
    :rtype: bool
    """

    add_subcommand = args.add_subcommand

    if add_subcommand == _INSTALL_SUBCMD:
        return run_opencode_install()

    if add_subcommand == _RUN_SUBCMD:
        return run_opencode_run()

    return False

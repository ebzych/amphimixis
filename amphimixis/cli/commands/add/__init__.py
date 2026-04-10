"""Add subcommands."""

import amphimixis.cli.commands.add.input
import amphimixis.cli.commands.add.toolchain

HELP_MESSAGE = "Add configuration files or toolchains interactively"


def add_args(parser):
    """Add arguments for add command.

    :param parser: subcommand parser to which arguments are added
    """

    subparsers = parser.add_subparsers(dest="add_subcommand", title="add options")
    subparsers.required = True

    subparsers.add_parser(
        "input",
        help="interactively create input.yml configuration file",
    )

    subparsers.add_parser(
        "toolchain",
        help="interactively add a toolchain to global config",
    )


def run_add(args):
    """Execute add subcommand.

    :param args: Parsed command line arguments
    :param ui: User interface for progress display
    """
    add_subcommand = args.add_subcommand

    if add_subcommand == "input":
        return amphimixis.cli.commands.add.input.run_add_input()

    if add_subcommand == "toolchain":
        return amphimixis.cli.commands.add.toolchain.run_add_toolchain()

    return False

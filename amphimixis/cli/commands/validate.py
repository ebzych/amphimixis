"""Validate command."""

from amphimixis.general import IUI, NullUI
from amphimixis.validator import validate

HELP_MESSAGE = "Check correctness of the configuration file"


def add_args(parser):
    """Add arguments for validate command.

    :param parser: subcommand parser to which arguments are added
    """

    parser.add_argument(
        "config_file",
        type=str,
        metavar="FILE",
        help="path to the configuration file",
    )


def validate_cmd(args, ui: IUI = NullUI()) -> bool:
    """Check correctness of the configuration file.

    :param args: Parsed command line arguments
    :param ui: User interface for progress display
    """

    ui.update_message("Config", f"Validate {args.config_file}...")

    if not validate(args.config_file, ui):
        ui.mark_failed(f"{args.config_file} is incorrect! See amphimixis.log")
        return False
    ui.mark_success(f"{args.config_file} is correct!")
    return True

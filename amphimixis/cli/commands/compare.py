"""Compare command."""

from argparse import ArgumentParser
from os import path

from amphimixis.cli.utils import add_events_arg
from amphimixis.general import IUI, NullUI
from amphimixis.perf_analyzer import main as compare_perf

HELP_MESSAGE = "Compare two perf output files (.scriptout) and display the results"


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for compare command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """

    add_events_arg(parser)
    parser.add_argument(
        "file1",
        type=str,
        metavar="FILE1",
        help="path to first perf output file",
    )
    parser.add_argument(
        "file2",
        type=str,
        metavar="FILE2",
        help="path to second perf output file",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=20,
        help="maximum number of rows (symbols) to display per event (default: 20)",
    )


def run_compare(args, ui: IUI = NullUI()) -> bool:
    """Compare two perf output files and print the top `max_rows` symbols
    with the most significant changes for specified events.

    :param Namespace args: parsed command line arguments
    :param IUI ui: User interface for progress display
    :return: True if command succeeded, False otherwise
    :rtype: bool
    """

    if not path.isfile(args.file1):
        ui.mark_failed(f"File not found: {args.file1}")
        return False
    if not path.isfile(args.file2):
        ui.mark_failed(f"File not found: {args.file2}")
        return False

    if (
        compare_perf(
            args.file1, args.file2, target_events=args.events, max_rows=args.max_rows
        )
        != 0
    ):
        ui.mark_failed("Comparison failed.")
        return False
    ui.mark_success("Comparison completed!")
    return True

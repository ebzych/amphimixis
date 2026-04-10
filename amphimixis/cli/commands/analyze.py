"""Analyze command."""

from os import path

from amphimixis.analyzer import analyze as analyze_func
from amphimixis.general import IUI, NullUI, Project

HELP_MESSAGE = "Analyze the project and detect existing CI, tests, build systems, etc."


def add_args(parser):
    """Add arguments for analyze command.

    :param parser: subcommand parser to which arguments are added
    """

    parser.add_argument("path", type=str, help="path to the project directory")
    parser.add_argument(
        "--config",
        nargs="?",
        const="input.yml",
        metavar="CONFIG",
        help="use a specific config file (default: input.yml)",
    )


def run_analyze(project: Project, ui: IUI = NullUI()) -> bool:
    """Execute project analysis.

    :param project: Project instance to analyze
    :param ui: User interface for progress display
    """

    project_name = path.basename(path.normpath(project.path))
    ui.update_message(project_name, "Analyzing project...")

    if not analyze_func(project):
        ui.mark_failed("Analysis failed. See amphimixis.log for details.")
        return False
    ui.mark_success("Analysis completed! See amphimixis.log for details.")
    return True

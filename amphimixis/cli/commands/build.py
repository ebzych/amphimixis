"""Build command."""

from amphimixis import Builder, parse_config
from amphimixis.general import IUI, NullUI, Project

HELP_MESSAGE = "Build the project according to the generated configuration files"


def add_args(parser):
    """Add arguments for build command.

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


def run_build(project: Project, config_file_path: str, ui: IUI = NullUI()) -> bool:
    """Execute project build.

    :param project: Project instance to build
    :param config_file_path: Path to YAML configuration file
    :param ui: User interface for progress display
    """

    if not project.builds and not parse_config(
        project, config_file_path=config_file_path, ui=ui
    ):
        return False

    there_are_built = False
    for build in project.builds:
        if Builder.build_for_linux(project, build, ui):
            there_are_built = True
            ui.mark_success("Build passed!")
        else:
            ui.mark_failed(build_id=build.build_name, error_message="Building failed")

    return there_are_built

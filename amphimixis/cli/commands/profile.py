"""Profile command."""

import shutil
import tempfile
from os import path

from amphimixis import Profiler, Shell, parse_config
from amphimixis.general import IUI, NullUI, Project

HELP_MESSAGE = "Profile the performance of builds"


def add_args(parser):
    """Add arguments for profile command.

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
    parser.add_argument(
        "--events",
        nargs="*",
        help="space-separated perf events (e.g., cycles cache-misses)",
    )


def setup_profiling_environment(project: Project, ui: IUI) -> bool:
    """Set up the profiling environment by copying the built binaries to the run machines.

    :param project: Project instance
    :param ui: User interface for progress display
    """

    success = True
    tmpdir = tempfile.mkdtemp("_amphimixis")
    for build in project.builds:
        if build.build_machine != build.run_machine:
            ui.update_message(build.build_name, "Copying built files to run machine")
            shell_build_machine = Shell(project, build.build_machine, ui=ui)
            shell_run_machine = Shell(project, build.run_machine, ui=ui)

            build_path = path.join(
                shell_build_machine.get_project_workdir(), build.build_name
            )
            if not shell_build_machine.copy_to_host(build_path, tmpdir):
                ui.mark_failed("Can't download built files from build machine")
                success = False

            if not shell_run_machine.copy_to_remote(
                path.join(tmpdir, build.build_name),
                shell_run_machine.get_project_workdir(),
            ):
                ui.mark_failed("Can't transfer built files to run machine")
                success = False

            if not shell_run_machine.copy_to_remote(
                project.path, path.dirname(shell_run_machine.get_source_dir())
            ):
                ui.mark_failed("Can't transfer source code to run machine")
                success = False

    shutil.rmtree(tmpdir)
    return success


def run_profile(
    project: Project,
    config_file_path: str,
    ui: IUI = NullUI(),
    events: list | None = None,
) -> bool:
    """Execute project profiling.

    :param project: Project instance
    :param config_file_path: Path to YAML configuration file
    :param ui: User interface for progress display
    :param events: List of perf events to record
    """

    if not project.builds and not parse_config(
        project, config_file_path=config_file_path, ui=ui
    ):
        return False

    setup_profiling_environment(project, ui)

    success = True

    for build in project.builds:
        if not build.successfully_built:
            continue
        profiler_ = Profiler(project, build, ui)
        successful_execs = profiler_.profile_all(events=events)
        profiler_.save_stats()
        profiler_.cleanup()
        if not successful_execs or (
            build.executables and successful_execs != build.executables
        ):
            ui.mark_failed("Some executables failed to be profiled")
            success = False
        else:
            ui.mark_success("Profiling completed!")

    return success

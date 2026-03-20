"""CLI command implementations for Amphimixis."""

import os
import tempfile
from os import path

from amphimixis import Builder, Profiler, analyze, general, parse_config
from amphimixis.general import IUI, NullUI
from amphimixis.shell.shell import Shell


def run_analyze(project: general.Project, ui: IUI = NullUI()) -> bool:
    """Execute project analysis.

    :param Project project: Project instance to analyze
    :param IUI ui: User interface for progress display
    """
    project_name = path.basename(path.normpath(project.path))
    ui.update_message(project_name, "Analyzing project...")

    if not analyze(project):
        ui.mark_failed("Analysis failed. See amphimixis.log for details")
        return False
    ui.mark_success("Analysis completed!")
    return True


def run_build(
    project: general.Project, config_file_path: str, ui: IUI = NullUI()
) -> bool:
    """Execute project build.

    :param Project project: Project instance to build
    :param str config_file: Path to YAML configuration file
    :param IUI ui: User interface for progress display
    """

    parse_config(project, config_file_path=str(config_file_path), ui=ui)
    for build in project.builds:
        if not Builder.build_for_linux(project, build, ui):
            ui.mark_failed()
            return False
        ui.mark_success("Build passed!")
    return True


def run_profile(
    project: general.Project, config_file_path: str, ui: IUI = NullUI()
) -> bool:
    """Execute project profiling.

    :param project: Project instance to profiler
    :param str config_file_path: Path to YAML configuration file
    :param IUI ui: User interface for progress display
    """

    if not project.builds:
        parse_config(project, config_file_path=str(config_file_path), ui=ui)

    setup_profiling_environment(project, ui)

    for build in project.builds:
        profiler_ = Profiler(project, build, ui)
        if not profiler_.profile_all():
            ui.mark_failed()
            return False
        profiler_.save_stats()
        ui.mark_success("Profiling completed!")
    return True


def setup_profiling_environment(project: general.Project, ui: general.IUI) -> bool:
    """
    Set up the profiling environment by copying the built binaries to the run machines.
    """
    success = True
    tmpdir = tempfile.mkdtemp("_amphimixis")
    for build in project.builds:
        if build.build_machine != build.run_machine:
            ui.update_message(build.build_name, "Copying built files to run machine")
            shell_build_machine = Shell(project, build.build_machine, ui=ui)
            shell_run_machine = Shell(project, build.run_machine, ui=ui)

            # copy builds
            build_path = os.path.join(
                shell_build_machine.get_project_workdir(), build.build_name
            )
            if not shell_build_machine.copy_to_host(build_path, tmpdir):
                ui.mark_failed("Can't download built files from build machine")
                success = False

            if not shell_run_machine.copy_to_remote(
                os.path.join(tmpdir, build.build_name),
                shell_run_machine.get_project_workdir(),
            ):
                ui.mark_failed("Can't transfer built files to run machine")
                success = False

            # copy source
            if not shell_run_machine.copy_to_remote(
                project.path, os.path.dirname(shell_run_machine.get_source_dir())
            ):
                ui.mark_failed("Can't transfer source code to run machine")
                success = False

    os.rmdir(tmpdir)
    return success

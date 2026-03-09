"""CLI command implementations for Amphimixis."""

from os import path

from amphimixis import Builder, Profiler, analyze, general, parse_config
from amphimixis.general import IUI, NullUI


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

    for build in project.builds:
        profiler_ = Profiler(project, build, ui)
        if not profiler_.profile_all(project.path):
            ui.mark_failed()
            return False
        profiler_.save_stats()
        ui.mark_success("Profiling completed!")
    return True

"""CLI command implementations for Amphimixis."""

from amphimixis import Builder, Profiler, analyze, general, parse_config
from amphimixis.general import IUI, NullUI


def run_analyze(project: general.Project, ui: IUI = NullUI()):
    """Execute project analysis.

    :param Project project: Project instance to analyze
    :param IUI ui: User interface for progress display
    """

    analyze(project)
    ui.mark_success()


def run_build(project: general.Project, config_file_path: str, ui: IUI = NullUI()):
    """Execute project build.

    :param Project project: Project instance to build
    :param str config_file: Path to YAML configuration file
    :param IUI ui: User interface for progress display
    """

    parse_config(project, config_file_path=str(config_file_path), ui=ui)
    Builder.build(project, ui)


def run_profile(project: general.Project, config_file_path: str, ui: IUI = NullUI()):
    """Execute project profiling.

    :param project: Project instance to profiler
    :param str config_file_path: Path to YAML configuration file
    :param IUI ui: User interface for progress display
    """

    if not project.builds:
        parse_config(project, config_file_path=str(config_file_path), ui=ui)

    for build in project.builds:
        print(f"Profiling {build.build_name}")
        profiler_ = Profiler(project, build, ui)
        if profiler_.profile_all():
            print(profiler_.stats)
        else:
            ui.mark_failed("Executables not found")

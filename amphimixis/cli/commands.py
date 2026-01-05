"""CLI command implementations for Amphimixis."""

from amphimixis import Builder, Profiler, analyze, parse_config


def run_analyze(project):
    """Execute project analysis.

    :param project: Project instance to analyze
    """

    analyze(project)


def run_build(project, config_file_path):
    """Execute project build.

    :param project: Project instance to build
    :param config_file: Path to YAML configuration file
    """

    parse_config(project, config_file_path=str(config_file_path))
    Builder.build(project)


def run_profile(project):
    """Execute project profiling.

    :param project: Project instance to profiler
    """
    for build in project.builds:
        print(f"Profiling {build.build_name}")
        profiler_ = Profiler(project, build)
        if profiler_.profile_all():
            print(profiler_.stats)
        else:
            print("Executables not found")

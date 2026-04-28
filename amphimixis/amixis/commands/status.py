"""Status command - shows builds from config and all processed builds."""

import json
import pickle
import glob
from argparse import ArgumentParser

from amphimixis.core import parse_config
from amphimixis.core.general import Project, Build
from amphimixis.amixis.utils import add_config_arg, add_path_arg


HELP_MESSAGE = "Show status of all builds: configured, built, profiled, or failed"


def add_args(parser: ArgumentParser) -> None:
    """Add arguments for status command.

    :param ArgumentParser parser: subcommand parser to which arguments are added
    """
    add_path_arg(parser)
    add_config_arg(parser)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format for programmatic use",
    )


def get_machine_name(machine) -> str:
    """Return machine identifier for display.

    :param machine: MachineInfo object
    :return: 'local' if address is None, otherwise the address
    :rtype: str
    """
    return "local" if machine.address is None else machine.address


def load_builds_cache():
    """Load builds cache from .builds file.

    :return: Dictionary of build_name -> Build objects
    :rtype: dict
    """
    try:
        builds_files = glob.glob(".builds")
        if builds_files:
            with open(".builds", "rb") as file:
                return pickle.load(file)
    except (FileNotFoundError, pickle.PickleError):
        pass
    return {}


def load_project_stats():
    """Load project profiling stats.

    :return: ProjectStats dictionary
    :rtype: dict
    """
    try:
        project_files = glob.glob("*.project")
        if project_files:
            project_name = project_files[0].replace(".project", "")
            with open(f"{project_name}{'.stats'}", "rb") as file:
                return pickle.load(file)
    except (FileNotFoundError, pickle.PickleError):
        pass
    return {}


def get_build_status(
    build_name: str, build: Build, builds_cache: dict, stats: dict
) -> str:
    """Determine the status of a build.

    :param str build_name: Name of the build
    :param Build build: Build object
    :param dict builds_cache: Cache of built projects
    :param dict stats: Profiling statistics
    :return: Status string: configured/built/profiled/failed
    :rtype: str
    """
    if build_name not in builds_cache:
        return "configured"
    if build_name in stats:
        for exe_stats in stats[build_name].values():
            if exe_stats.perf_record_name or exe_stats.perf_script_name:
                return "profiled"
    return "built" if build.successfully_built else "failed"


def run_status(
    project: Project, config_file_path: str, json_output: bool = False
) -> None:
    """Execute status command to show all builds and their states.

    :param Project project: Project instance
    :param str config_file_path: Path to YAML configuration file
    :param bool json_output: Whether to output in JSON format
    """
    if not project.builds and not parse_config(
        project, config_file_path=config_file_path
    ):
        print("No builds found in configuration")
        return

    builds_cache = load_builds_cache()
    stats = load_project_stats()

    result = []
    seen = set()

    for build in project.builds:
        status = get_build_status(build.build_name, build, builds_cache, stats)
        result.append(
            {
                "build_name": build.build_name,
                "build_machine": get_machine_name(build.build_machine),
                "run_machine": get_machine_name(build.run_machine),
                "recipe_id": build.build_name.split("_")[-1],
                "status": status,
                "executables": build.executables,
                "successfully_built": build.successfully_built,
                "source": "config",
            }
        )
        seen.add(build.build_name)

    for build_name, build in builds_cache.items():
        if build_name not in seen:
            status = get_build_status(build_name, build, builds_cache, stats)
            result.append(
                {
                    "build_name": build_name,
                    "build_machine": get_machine_name(build.build_machine),
                    "run_machine": get_machine_name(build.run_machine),
                    "recipe_id": build_name.split("_")[-1],
                    "status": status,
                    "executables": build.executables,
                    "successfully_built": build.successfully_built,
                    "source": "cache",
                }
            )

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"{'Build':<15} {'Build @':<12} {'Run @':<12} {'Recipe':<8} {'Status':<12} {'Source':<8}"
        )
        print("-" * 75)
        for r in result:
            print(
                f"{r['build_name']:<15} "
                f"{r['build_machine']:<12} "
                f"{r['run_machine']:<12} "
                f"{r['recipe_id']:<8} "
                f"{r['status']:<12} "
                f"{r['source']:<8}"
            )
        print(f"\nTotal: {len(result)} builds")

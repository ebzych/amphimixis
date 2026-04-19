"""Clean command."""

import pickle

from amphimixis import Builder
from amphimixis.general import Build, Project, tools

HELP_MESSAGE = "Clean build directories"


def add_args(parser):
    """Add arguments for clean command.

    :param parser: subcommand parser to which arguments are added
    """

    parser.add_argument(
        "build_names",
        nargs="*",
        metavar="BUILD_NAMES",
        help="name of builds to clean (if none, interactive mode)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="clean all builds",
    )


def open_alternate_term() -> None:
    """Uses Xterm control code to switch to an alternate terminal buffer"""

    print("\033[?1049h", end="")


def close_alternate_term() -> None:
    """Uses Xterm control code to return back to first terminal buffer"""

    print("\033[?1049l", end="")


def clean(*builds: Build) -> bool:
    """Clean builds directories"""

    project: Project
    try:
        project = tools.get_cache_project()
    except FileNotFoundError:
        print("Project file .project not found")
        return False
    success = True
    for b in builds:
        if not Builder.clean(project, b):
            success = False
    return success


def interactive_clean() -> bool:
    """Enumerate builds names and suggest choose which will be cleaned"""

    builds: dict[str, Build] = {}
    project: Project
    try:
        project = tools.get_cache_project()
        with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as file:
            builds = pickle.load(file)
    except FileNotFoundError:
        pass

    success = True
    try:
        for i, build_name in enumerate(builds.keys()):
            print(f"{i + 1}.\t{build_name}")
        nums = [
            int(n) - 1 for n in input("Enter the builds numbers to clean: ").split()
        ]

        for i, build in enumerate(builds.values()):
            if i in nums:
                if Builder.clean(project, build):
                    print(f"{build.build_name} was successfully cleaned")
                else:
                    success = False
                    print(f"{build.build_name} failed to clean")
    except ValueError:
        print("Not a number")
    except KeyboardInterrupt:
        print("Cancelled")
    return success


def run_clean(args) -> bool:
    """Execute clean command.

    :param args: Parsed command line arguments
    """

    builds_dict: dict[str, Build] = {}
    try:
        with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as f:
            builds_dict = pickle.load(f)
    except FileNotFoundError:
        if args.all or args.build_names:
            print("No builds remembered.")
            return False
        return interactive_clean()

    if args.all:
        return clean(*builds_dict.values())
    if args.build_names:
        to_clean = [b for b in builds_dict.values() if b.build_name in args.build_names]
        if not to_clean:
            print("No matching builds found")
            return False
        return clean(*to_clean)
    return interactive_clean()

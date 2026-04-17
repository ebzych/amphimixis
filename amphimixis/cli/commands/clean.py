"""Clean command."""

import pickle

from amphimixis import Builder
from amphimixis.general import Build, tools

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


def open_alternate_term():
    """Uses Xterm control code to switch to an alternate terminal buffer."""

    print("\033[?1049h", end="")


def close_alternate_term():
    """Uses Xterm control code to return back to first terminal buffer."""

    print("\033[?1049l", end="")


def clean(project: general.Project, *builds: Build) -> bool:
    """Clean build directories for specified builds.

    :param project: Project instance
    :param builds: Build objects to clean (variadic)
    """

    success = True
    for b in builds:
        if not Builder.clean(project, b):
            success = False
    return success


def interactive_clean(project: tools.Project, builds: dict[str, Build]) -> bool:
    """Interactive build cleaner.
    Opens an alternate terminal buffer, displays list of available builds,
    prompts user to select builds to clean, and removes selected build directories.

    :param project: Project instance
    :param builds: Dictionary of build name to Build objects
    """

    success = True
    try:
        open_alternate_term()

        for i, build_name in enumerate(builds.keys()):
            print(f"{i + 1}.\t{build_name}")
        nums = [
            int(n) - 1 for n in input("Enter the builds numbers to clean: ").split()
        ]

        close_alternate_term()

        for i, build in enumerate(builds.values()):
            if i in nums:
                if Builder.clean(project, build):
                    print(f"{build.build_name} was successfully cleaned")
                else:
                    success = False
                    print(f"{build.build_name} failed to clean")

    except KeyboardInterrupt:
        close_alternate_term()
    except ValueError:
        close_alternate_term()
        print("Not a number")
    finally:
        close_alternate_term()
    return success


def run_clean(args) -> bool:
    """Execute clean command.

    :param args: Parsed command line arguments
    """

    project: tools.Project
    try:
        project = tools.get_cache_project()
    except FileNotFoundError:
        print("Project file .project not found")
        return False

    builds: dict[str, Build] = {}
    try:
        with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as f:
            builds = pickle.load(f)
    except FileNotFoundError:
        print("No builds remembered")
        return True

    if args.all:
        return clean(project, *builds.values())

    if args.build_names:
        to_clean = [b for b in builds.values() if b.build_name in args.build_names]
        if not to_clean:
            print("No matching builds found")
            return False
        return clean(project, *to_clean)

    return interactive_clean(project, builds)

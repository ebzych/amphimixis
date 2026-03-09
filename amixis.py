#!/usr/bin/env python3

"""Amphimixis CLI tool for build automation and profiling."""

import sys
from pathlib import Path

from amphimixis import build_systems_dict, general, validate
from amphimixis.cli import (
    DEFAULT_CONFIG_PATH,
    create_parser,
    run_analyze,
    run_build,
    run_profile,
)
from amphimixis.cli.console_animation_printer import ConsoleAnimationPrinter


# pylint: disable=too-many-branches,too-many-statements
def main():
    """Main function for the Amphimixis CLI tool."""

    parser = create_parser()

    args = parser.parse_args()

    if args.config is not None:
        config_file = Path(args.config).expanduser().resolve()
    else:
        config_file = DEFAULT_CONFIG_PATH

    if args.validate:
        if not validate(args.validate):
            print(f"{args.validate} is incorrect!!")
            sys.exit(1)
        print(f"{args.validate} is correct!!")
        sys.exit(0)

    if not args.path:
        print("Error: please provide path to the project directory.")
        sys.exit(1)

    project = general.Project(
        str(Path(args.path).expanduser().resolve()),
        [],
        build_systems_dict["make"],
        build_systems_dict["cmake"],
    )

    ui = ConsoleAnimationPrinter()

    try:
        if not any([args.analyze, args.build, args.profile]):
            if not run_analyze(project, ui):
                sys.exit(1)

            if not run_build(project, config_file_path=str(config_file), ui=ui):
                sys.exit(1)

            if not run_profile(project, config_file_path=str(config_file), ui=ui):
                sys.exit(1)

            sys.exit(0)

        if args.analyze:
            if not run_analyze(project, ui):
                sys.exit(1)

        if args.build:
            if not run_build(project, config_file_path=str(config_file), ui=ui):
                sys.exit(1)

        if args.profile:
            if not run_profile(project, config_file_path=str(config_file), ui=ui):
                sys.exit(1)

        sys.exit(0)

    except (FileNotFoundError, ValueError, RuntimeError, LookupError, TypeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())

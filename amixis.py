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


# pylint: disable=too-many-branches
def main():
    """Main function for the Amphimixis CLI tool."""

    parser = create_parser()

    args = parser.parse_args()

    if args.config is not None:
        config_file = Path(args.config).expanduser().resolve()
    else:
        config_file = DEFAULT_CONFIG_PATH

    if args.validate:
        validate(args.validate)
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

    try:
        if not any([args.analyze, args.build, args.profile]):
            run_analyze(project)
            run_build(project, config_file_path=str(config_file))
            run_profile(project)

        if args.analyze:
            run_analyze(project)

        if args.build:
            run_build(project, config_file_path=str(config_file))

        if args.profile:
            run_profile(project)

        sys.exit(0)

    except (FileNotFoundError, ValueError, RuntimeError, LookupError, TypeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

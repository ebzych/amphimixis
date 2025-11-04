#!/usr/bin/env python3

import sys
import argparse
from amphimixis import *


def main():

    parser = argparse.ArgumentParser(
        prog="amixis",
        description="amphimixis — build automation and profiling tool "
        "for Linux projects across various architectures.",
        formatter_class=argparse.MetavarTypeHelpFormatter,
        usage=argparse.SUPPRESS,
        add_help=True,
    )

    parser.add_argument(
        "path",
        type=str,
        nargs="?",
        metavar="path",
        help="path to the project folder.",
    )

    parser.add_argument(
        "--analyzer",
        action="store_true",
        help="run only the project analyzer.",
    )
    parser.add_argument(
        "--configurator",
        action="store_true",
        help="run only the project configurator.",
    )
    parser.add_argument(
        "--builder",
        action="store_true",
        help="run only the build module.",
    )
    parser.add_argument(
        "--profiler",
        action="store_true",
        help="run only the performance profiler",
    )

    args = parser.parse_args()

    if not args.path:
        print("Error: please provide path to the project directory.")
        sys.exit(1)

    project = general.Project(
        args.path,
        [],
        general.build_systems_dict["make"],
        general.build_systems_dict["cmake"],
    )

    try:
        if not any([args.analyzer, args.configurator, args.builder, args.profiler]):

            analyze(project)

            parse_config(project)

            Builder.process(project)

            profiler_ = Profiler(project.builds[0])

            profiler_.execution_time()

            print(profiler_.stats)

        if args.analyzer:
            analyze(project)

        if args.configurator:
            parse_config(project)

        if args.builder:
            parse_config(project)
            Builder.process(project)

        if args.profiler:

            profiler_ = Profiler(project.builds[0])

            profiler_.execution_time()

            print(profiler_.stats)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

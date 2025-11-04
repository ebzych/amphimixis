#!/usr/bin/env python3

import sys
import argparse
from amphimixis import *


def main():

    parser = argparse.ArgumentParser(
        prog="amixis",
        description="amphimixis — build automation and profiling tool for Linux projects across various architectures.",
        formatter_class=argparse.MetavarTypeHelpFormatter,
        usage=argparse.SUPPRESS,
        add_help=True,
    )

    parser.add_argument(
        "path",
        type=str,
        metavar="path",
        help="path to the project folder.",
    )

    parser.add_argument(
        "--analyzer",
        type=str,
        metavar="PATH",
        help="run only the project analyzer.",
    )
    parser.add_argument(
        "--configurator",
        type=str,
        metavar="PATH",
        help="run only the project configurator.",
    )
    parser.add_argument(
        "--builder",
        type=str,
        metavar="PATH",
        help="run only the build module.",
    )
    parser.add_argument(
        "--profiler",
        type=str,
        metavar="PATH",
        help="run only the performance profiler",
    )

    args = parser.parse_args()

    project = general.Project(
        sys.argv[1],
        [],
        general.build_systems_dict["make"],
        general.build_systems_dict["cmake"],
    )

    if not (args.analyzer or args.configurator or args.builder or args.profiler):

        try:
            analyze(project)

        except FileNotFoundError as e:
            print(f"{e}")
            exit(-1)

        parse_config(project)

        Builder.process(project)

        profiler_ = Profiler(project.builds[0])

        profiler_.execution_time()

        print(profiler_.stats)

    if args.analyzer:
        try:
            analyze(project)

        except FileNotFoundError as e:
            print(f"{e}")
            exit(-1)

    if args.configurator:
        parse_config(project)

    if args.builder:
        parse_config(project)

        Builder.process(project)

    if args.profiler:
        profiler_ = Profiler(project.builds[0])

        profiler_.execution_time()

        print(profiler_.stats)


if __name__ == "__main__":
    main()

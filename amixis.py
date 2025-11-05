#!/usr/bin/env python3

import sys
import argparse
from amphimixis import *
import textwrap


class CustomFormatterClass(
    argparse.RawDescriptionHelpFormatter,
):

    def format_help(self) -> str:

        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        GRAY = "\033[90m"
        RESET = "\033[0m"

        banner = textwrap.dedent(
            f"""
            {GRAY}*****************************************************************{RESET}

                 {YELLOW}✰  Amphimixis — build automation and profiling tool  ✰{RESET}

            {GRAY}*****************************************************************{RESET}
        """
        )

        help_text = super().format_help()

        examples = textwrap.dedent(
            """
            Examples:

              amixis /path/to/folder/with/project
                  → Main mode. Runs all core modules: analyzer, configurator,
                    builder, and profiler.
                
              amixis --analyzer /path/to/folder/with/project
                  → Runs only the project analyzer module.

              amixis --builder /path/to/folder/with/project
                  → Runs both the analyzer and builder modules.

              amixis --analyzer --builder --profiler /path/to/folder/with/project
                  → Runs the analyzer, builder, and profiler modules.
        """
        )

        return f"{banner}\n{help_text}\n{examples}"


def main():

    parser = argparse.ArgumentParser(
        prog="amixis",
        formatter_class=CustomFormatterClass,
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
        "-a",
        "--analyzer",
        action="store_true",
        help="run only the project analyzer.",
    )
    parser.add_argument(
        "-c",
        "--configurator",
        action="store_true",
        help="run only the project configurator.",
    )
    parser.add_argument(
        "-b",
        "--builder",
        action="store_true",
        help="run only the build module.",
    )
    parser.add_argument(
        "-p",
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

            if not args.configurator:
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

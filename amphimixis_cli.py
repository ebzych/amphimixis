#!/usr/bin/env python3

"""Amphimixis CLI tool for build automation and profiling."""

import sys
import argparse
import textwrap
from amphimixis import general, analyze, parse_config, Builder, Profiler

YELLOW = "\033[93m"
GRAY = "\033[90m"
RESET = "\033[0m"


class CustomFormatterClass(
    argparse.RawDescriptionHelpFormatter,
):
    """Custom formatter class for argparse to enhance help output."""

    def format_help(self) -> str:
        """Format help message with custom banner and examples."""

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
                  → Main mode. Performs full project analysis, generates configuration files,
                  runs the build process, and performs profiling.
                
              amixis --analyzer /path/to/folder/with/project
                  → Performs project analysis. Detects existing CI, tests, benchmarks, etc.

              amixis --builder /path/to/folder/with/project
                  → Builds the project, implicitly calling --configurator to generate 
                  configuration files.
        """
        )

        return f"{banner}\n{help_text}\n{examples}"


def main():
    """Main function for the Amphimixis CLI tool."""

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
        help="path to the project folder to process (required in main mode).",
    )

    parser.add_argument(
        "-a",
        "--analyzer",
        action="store_true",
        help="analyzes the project to detect existing CI systems, tests, build systems, etc.",
    )
    parser.add_argument(
        "-c",
        "--configurator",
        action="store_true",
        help="generates configuration files for various builds.",
    )
    parser.add_argument(
        "-b",
        "--builder",
        action="store_true",
        help="builds the project according to the generated configuration files.",
    )
    parser.add_argument(
        "-p",
        "--profiler",
        action="store_true",
        help="profiles the performance of different builds, collects execution statistics, "
        "and compares traces.",
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

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

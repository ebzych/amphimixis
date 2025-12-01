#!/usr/bin/env python3

"""Amphimixis CLI tool for build automation and profiling."""

import argparse
import sys
import textwrap
from pathlib import Path

from amphimixis import (
    Builder,
    Profiler,
    analyze,
    build_systems_dict,
    general,
    parse_config,
    validate,
)

YELLOW = "\033[93m"
GRAY = "\033[90m"
RESET = "\033[0m"


class CustomFormatterClass(
    argparse.RawTextHelpFormatter,
):
    """Custom formatter class for argparse to enhance help output."""

    def __init__(self, prog):
        super().__init__(prog, max_help_position=35)

    def _format_action(self, action):
        parts = super()._format_action(action)
        return parts + "\n"

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

              amixis --analyze /path/to/folder/with/project
                  → Performs project analysis. Detects existing CI, tests, benchmarks, etc.

              amixis --build /path/to/folder/with/project
                  → Builds the project, implicitly calling --configure to generate.
                    configuration files.

              amixis --config=config_file /path/to/folder/with/project
                  → Specifies a custom configuration file to be used for the configuration process;
                    runs all steps including analysis, configuration, building, and profiling.
                    If no config file is specified, defaults to 'input.yml', 
                    which must be located in the working directory.

              amixis --validate=file_name
                  → Checks the config file correctness.

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

    default_config_path = Path("input.yml").resolve()

    parser.add_argument(
        "path",
        type=str,
        help="path to the project folder to process (required in main mode).",
    )

    parser.add_argument(
        "-v",
        "--validate",
        type=str,
        metavar="FILE",
        default=None,
        help="check correctness of the configuration file.",
    )

    parser.add_argument(
        "--config",
        nargs="?",
        const=str(default_config_path),
        metavar="CONFIG",
        help="use a specific config file (default: input.yml)\n"
        "for all steps: analysis, configuration, building, and profiling.",
    )

    parser.add_argument(
        "-a",
        "--analyze",
        action="store_true",
        help="analyze the project and detect existing CI/tests, build systems, etc.",
    )

    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        help="build the project according to the generated configuration files.",
    )

    parser.add_argument(
        "-p",
        "--profile",
        action="store_true",
        help="profile the performance of builds and compare execution traces",
    )

    args = parser.parse_args()

    if args.config is not None:
        config_file = Path(args.config).expanduser().resolve()
    else:
        config_file = default_config_path

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
            analyze(project)
            parse_config(project, config_file_path=str(config_file))
            Builder.build(project)
            profiler_ = Profiler(project.builds[0])
            profiler_.execution_time()
            print(profiler_.stats)

        if args.analyze:
            analyze(project)

        if args.build:
            parse_config(project, config_file_path=str(config_file))

            Builder.build(project)

        if args.profile:
            profiler_ = Profiler(project.builds[0])
            profiler_.execution_time()
            print(profiler_.stats)

        sys.exit(0)

    except (FileNotFoundError, ValueError, RuntimeError, LookupError, TypeError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

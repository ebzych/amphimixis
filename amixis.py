#!/usr/bin/env python3

"""Amphimixis CLI tool for build automation and profiling."""

import pickle
import sys
from pathlib import Path

from amphimixis import Builder, general, validate
from amphimixis.cli import (
    DEFAULT_CONFIG_PATH,
    clean,
    create_parser,
    interactive_clean,
    parse_full_pipeline_args,
    run_add_input,
    run_add_toolchain,
    run_analyze,
    run_build,
    run_compare,
    run_full_pipeline,
    run_profile,
    show_profiling_result,
)
from amphimixis.cli.console_animation_printer import ConsoleAnimationPrinter


# pylint: disable=too-many-branches,too-many-statements,too-many-return-statements
def main():
    """Main function for the Amphimixis CLI tool."""

    known_commands = {"analyze", "build", "profile", "validate", "compare", "add", "clean"}

    non_opts = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
    if non_opts and not any(arg in known_commands for arg in non_opts):
        path, config_file = parse_full_pipeline_args()
        if path is None or config_file is None:
            return 1
        if not path.exists():
            print(f"Error: path does not exist: {path}")
            return 1
        if not path.is_dir():
            print(f"Error: path is not a directory: {path}")
            return 1
        if config_file != DEFAULT_CONFIG_PATH and not config_file.exists():
            print(f"Error: config file '{config_file}' not found. "
                  f"Please specify the full filename with .yml extension.")
            return 1
        ui = ConsoleAnimationPrinter()
        return run_full_pipeline(str(path), config_file, ui)

    parser = create_parser()
    args = parser.parse_args()
    ui = ConsoleAnimationPrinter()

    if args.command is None:
        parser.print_help()
        return 0

    command = args.command

    match command:
        case "clean":
            builds = {}
            try:
                with open(Builder.BUILDS_LIST_FILE_NAME, "rb") as f:
                    builds = pickle.load(f)
            except FileNotFoundError:
                print("No builds remembered")
                return 0

            if args.all:
                return 0 if clean(*builds.values()) else 1
            if args.build_names:
                to_clean = [b for b in builds.values() if b.build_name in args.build_names]
                if not to_clean:
                    print("No matching builds found")
                    return 1
                return 0 if clean(*to_clean) else 1
            return 0 if interactive_clean() else 1

        case "analyze":
            if args.config is not None:
                config_file = Path(args.config).expanduser().resolve()
            else:
                config_file = DEFAULT_CONFIG_PATH

            project = general.Project(str(Path(args.path).expanduser().resolve()))
            return 0 if run_analyze(project, ui) else 1

        case "build":
            if args.config is not None:
                config_file = Path(args.config).expanduser().resolve()
            else:
                config_file = DEFAULT_CONFIG_PATH

            project = general.Project(str(Path(args.path).expanduser().resolve()))
            return (
                0 if run_build(project, config_file_path=str(config_file), ui=ui) else 1
            )

        case "profile":
            if args.config is not None:
                config_file = Path(args.config).expanduser().resolve()
            else:
                config_file = DEFAULT_CONFIG_PATH

            target_events = args.events if args.events else None
            project = general.Project(str(Path(args.path).expanduser().resolve()))

            if not run_profile(
                project,
                config_file_path=str(config_file),
                ui=ui,
                events=target_events,
            ):
                print("Error: Profiling failed.")
                return 1

            show_profiling_result(project)
            return 0

        case "validate":
            if not validate(args.config_file, ui):
                print(f"{args.config_file} is incorrect!")
                return 1
            print(f"{args.config_file} is correct!")
            return 0

        case "compare":
            if not run_compare(
                args.file1,
                args.file2,
                max_rows=args.max_rows,
                ui=ui,
            ):
                return 1
            return 0

        case "add":
            add_subcommand = args.add_subcommand

            if add_subcommand == "input":
                return 0 if run_add_input() else 1

            if add_subcommand == "toolchain":
                return 0 if run_add_toolchain() else 1

            parser.error(f"Unknown add subcommand: {add_subcommand}")
            return 1

        case _:
            parser.print_help()
            return 1


if __name__ == "__main__":
    sys.exit(main())

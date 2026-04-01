#!/usr/bin/env python3

"""Amphimixis CLI tool for build automation and profiling."""

from os import getcwd, path
import pickle
import sys
from pathlib import Path

from amphimixis import general, validate, Builder
from amphimixis.cli import (
    DEFAULT_CONFIG_PATH,
    create_parser,
    run_analyze,
    run_build,
    run_compare,
    run_profile,
    clean,
    interactive_clean,
    show_profiling_result,
)
from amphimixis.cli.console_animation_printer import ConsoleAnimationPrinter


# pylint: disable=too-many-branches,too-many-statements,too-many-return-statements
def main():
    """Main function for the Amphimixis CLI tool."""

    parser = create_parser()
    args = parser.parse_args()

    if args.all and not args.clean is not None:
        parser.error(f"--all can only be used with --clean")
    if args.clean is not None:
        builds: dict[str, general.Build] = []
        try:
            with open(
                path.join(getcwd(), Builder._BUILDS_LIST_FILE_NAME), "rb"
            ) as file:
                builds: dict[str, general.Build] = pickle.load(file)
        except FileNotFoundError:
            print("No builds remember")
        if args.all:
            return clean(*builds.values())
        if len(args.clean) > 0:
            to_clean: list[general.Build] = []
            for b in builds.values():
                if b.build_name in args.clean:
                    to_clean.append(b)
            return clean(*to_clean)
        else:
            return interactive_clean()

    if not args.compare and args.max_rows != 20:
        parser.error("--max-rows can only be used with --compare")

    if args.config is not None:
        config_file = Path(args.config).expanduser().resolve()
    else:
        config_file = DEFAULT_CONFIG_PATH

    if args.validate:
        if not validate(args.validate):
            print(f"{args.validate} is incorrect!!")
            return 1
        print(f"{args.validate} is correct!!")
        return 0

    if args.events == []:
        target_events = None
    else:
        target_events = args.events

    if args.compare:
        filename1, filename2 = args.compare
        ui = ConsoleAnimationPrinter()

        if not run_compare(
            filename1,
            filename2,
            target_events=target_events,
            max_rows=args.max_rows,
            ui=ui,
        ):
            return 1
        return 0

    if not args.path:
        print("Error: please provide path to the project directory.")
        return 1

    project = general.Project(str(Path(args.path).expanduser().resolve()))

    ui = ConsoleAnimationPrinter()

    try:
        if not any([args.analyze, args.build, args.profile]):
            if not run_analyze(project, ui):
                return 1

            if not run_build(project, config_file_path=str(config_file), ui=ui):
                return 1

            if not run_profile(
                project, config_file_path=str(config_file), ui=ui, events=target_events
            ):
                return 1

            show_profiling_result(project)
            return 0

        if args.analyze:
            if not run_analyze(project, ui):
                return 1

        if args.build:
            if not run_build(project, config_file_path=str(config_file), ui=ui):
                return 1

        if args.profile:
            if not run_profile(
                project, config_file_path=str(config_file), ui=ui, events=target_events
            ):
                return 1

            show_profiling_result(project)

        return 0

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
        LookupError,
        TypeError,
        KeyError,
        OSError,
        UnicodeDecodeError,
    ) as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

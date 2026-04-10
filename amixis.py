#!/usr/bin/env python3

"""Amphimixis CLI tool for build automation and profiling."""

import sys
from pathlib import Path

from amphimixis import general
from amphimixis.cli import create_parser
from amphimixis.cli.commands import COMMANDS  # type: ignore[attr-defined]
from amphimixis.cli.console_animation_printer import ConsoleAnimationPrinter
from amphimixis.cli.parser import MAIN_EXAMPLES
from amphimixis.general.constants import DEFAULT_CONFIG_PATH


def print_short_help(commands):
    """Print short help without examples."""

    print("amixis [-h] {run,analyze,build,profile,validate,compare,clean,add} ...\n")
    print(
        "Amphimixis — an automated project intelligence and evaluation tool\n"
        "for performance and migration readiness.\n"
    )
    print("options:")
    print("  -h, --short-help  show short help without examples")
    print("  --help           show full help with examples\n")
    print("subcommands:")
    for name, cmd in commands.items():
        print(f"  {name:12} - {cmd.HELP_MESSAGE}")


def print_full_help(commands):
    """Print full help with examples."""

    print("amixis [-h] {run,analyze,build,profile,validate,compare,clean,add} ...\n")
    print(
        "Amphimixis — an automated project intelligence and evaluation tool\n"
        "for performance and migration readiness.\n"
    )
    print("options:")
    print("  -h, --short-help  show short help without examples")
    print("  --help           show full help with examples\n")
    print("subcommands:")
    for name, cmd in commands.items():
        print(f"  {name:12} - {cmd.HELP_MESSAGE}")
    print("\n" + MAIN_EXAMPLES)


def main():
    """Main function for the Amphimixis CLI tool."""
    parser = create_parser()
    args = parser.parse_args()

    if args.short_help:
        print_short_help(COMMANDS)
        return 0

    if args.full_help:
        print_full_help(COMMANDS)
        return 0

    if args.command is None:
        print_short_help(COMMANDS)
        return 0

    ui = ConsoleAnimationPrinter()

    cmd = COMMANDS.get(args.command)
    if cmd is None:
        parser.print_help()
        return 1

    if args.command == "run":
        config_file = (
            Path(args.config).expanduser().resolve()
            if args.config
            else DEFAULT_CONFIG_PATH
        )
        project = general.Project(str(Path(args.path).expanduser().resolve()))
        result = cmd.run_full_pipeline(project, config_file, ui)
        return 0 if result else 1

    if args.command == "analyze":
        project = general.Project(str(Path(args.path).expanduser().resolve()))
        result = cmd.run_analyze(project, ui)
        return 0 if result else 1

    if args.command == "build":
        project = general.Project(str(Path(args.path).expanduser().resolve()))
        config_file_path = args.config or "input.yml"
        result = cmd.run_build(project, config_file_path, ui)
        return 0 if result else 1

    if args.command == "profile":
        project = general.Project(str(Path(args.path).expanduser().resolve()))
        config_file_path = args.config or "input.yml"
        target_events = args.events if args.events else None
        result = cmd.run_profile(project, config_file_path, ui, events=target_events)
        return 0 if result else 1

    if args.command == "validate":
        result = cmd.validate_cmd(args, ui)
        return 0 if result else 1

    if args.command == "compare":
        result = cmd.run_compare(args, ui)
        return 0 if result else 1

    if args.command == "clean":
        result = cmd.run_clean(args, ui)
        return 0 if result else 1

    if args.command == "add":
        result = cmd.run_add(args, ui)
        return 0 if result else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

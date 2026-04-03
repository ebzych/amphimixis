"""Parser for Amphimixis CLI with subcommands."""

import argparse
import textwrap
from pathlib import Path

YELLOW = "\033[93m"
GRAY = "\033[90m"
RESET = "\033[0m"
DEFAULT_CONFIG_PATH = Path("input.yml").resolve()


class CustomHelpFormatter(argparse.RawTextHelpFormatter):
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

              amixis analyze /path/to/folder/with/project
                  → Performs project analysis. Detects existing CI, tests, benchmarks, etc.

              amixis build /path/to/folder/with/project
                  → Builds the project, implicitly calling --configure to generate
                    configuration files.

              amixis profile /path/to/folder/with/project --events cycles cache-misses
                  → Runs only the profiling step and records only the specified perf events.

              amixis validate file_name
                  → Checks the config file correctness.

              amixis compare filename1.scriptout filename2.scriptout
                  → Compares two perf output files (.scriptout)
                    and displays the results in the console.

              amixis compare filename1.scriptout filename2.scriptout --max-rows 10
                  → Compares two perf output files (.scriptout)
                    and displays up to 10 symbols with the biggest delta per event.

              amixis add input
                  → Opens an editor with a configuration template.
                    After saving, validates the file and saves to input.yml.

              amixis add toolchain
                  → Opens an editor with a toolchain template.
                    After saving, validates and adds the toolchain to input.yml.

              amixis clean
                  → Interactive mode: select builds to clean.

              amixis clean --all
                  → Cleans all builds.
            """
        )

        return f"{banner}\n{help_text}\n{examples}"


def add_config_arg(parser):
    """Add argument config"""

    parser.add_argument(
        "--config",
        nargs="?",
        const=str(DEFAULT_CONFIG_PATH),
        metavar="CONFIG",
        help="use a specific config file (default: input.yml)",
    )

def add_path_arg(parser):
    """Add argument path of project"""

    parser.add_argument(
        "path",
        type=str,
        help="path to the project directory",
    )


def create_parser():
    """Create parser with subcommands."""

    parser = argparse.ArgumentParser(
        prog="amixis",
        formatter_class=CustomHelpFormatter,
        usage=argparse.SUPPRESS,
        add_help=True,
    )
    add_path_arg(parser)
    add_config_arg(parser)

    subparsers = parser.add_subparsers(dest="command", title="subcommands")

    parser_analyze = subparsers.add_parser(
        "analyze",
        help="analyze the project and detect existing CI, tests, build systems, etc.",
    )
    add_path_arg(parser_analyze)
    add_config_arg(parser_analyze)

    parser_build = subparsers.add_parser(
        "build",
        help="build the project according to the generated configuration files.",
    )
    add_path_arg(parser_build)
    add_config_arg(parser_build)

    parser_profile = subparsers.add_parser(
        "profile",
        help="profile the performance of builds.",
    )
    add_path_arg(parser_profile)
    add_config_arg(parser_profile)
    parser_profile.add_argument(
        "--events",
        nargs="*",
        help="space-separated perf events (e.g., cycles cache-misses)",
    )

    parser_validate = subparsers.add_parser(
        "validate",
        help="check correctness of the configuration file.",
    )
    parser_validate.add_argument(
        "config_file",
        type=str,
        metavar="FILE",
        help="path to the configuration file",
    )

    parser_compare = subparsers.add_parser(
        "compare",
        help="compare two perf output files (.scriptout) and display the results.",
    )
    parser_compare.add_argument(
        "file1",
        type=str,
        metavar="FILE1",
        help="path to first perf output file",
    )
    parser_compare.add_argument(
        "file2",
        type=str,
        metavar="FILE2",
        help="path to second perf output file",
    )
    parser_compare.add_argument(
        "--max-rows",
        type=int,
        default=20,
        help="maximum number of rows (symbols) to display per event (default: 20)",
    )

    parser_clean = subparsers.add_parser(
        "clean",
        help="clean build directories"
    )
    parser_clean.add_argument(
        "build_names",
        nargs="*",
        metavar="BUILD_NAMES",
        help="name of buillds to clean (if none, interactive mode)",
    )
    parser_clean.add_argument(
        "--all",
        action="store_true",
        help="clean all builds",
    )

    parser_add = subparsers.add_parser(
        "add",
        help="add configuration files or toolchains interactively",
    )
    add_subparsers = parser_add.add_subparsers(
        dest="add_subcommand", title="add options"
    )
    add_subparsers.required = True

    add_subparsers.add_parser(
        "input",
        help="interactively create input.yml configuration file",
    )

    add_subparsers.add_parser(
        "toolchain",
        help="interactively add a toolchain to input.yml",
    )

    return parser

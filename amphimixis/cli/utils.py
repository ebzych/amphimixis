"""CLI utilities - common functions for CLI commands."""

import os
import subprocess
import tempfile
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("input.yml").resolve()


def add_config_arg(parser):
    """Add --config argument to a parser.

    :param parser: subcommand parser to which arguments are added
    """

    parser.add_argument(
        "--config",
        nargs="?",
        const=str(DEFAULT_CONFIG_PATH),
        metavar="CONFIG",
        help="use a specific config file (default: input.yml)",
    )


def add_path_arg(parser):
    """Add positional 'path' argument to a parser.

    :param parser: subcommand parser to which arguments are added
    """

    parser.add_argument(
        "path",
        type=str,
        help="path to the project directory",
    )


def create_temp_file(content: str) -> Path:
    """Create a temporary file with given content.

    :param content: Content to write to the file
    """

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        return Path(f.name)


def launch_editor(editor: str, temp_path: Path) -> bool:
    """Launch the editor with the given file.

    :param editor: Editor command to use
    :param temp_path: Path to the file to edit
    """

    try:
        subprocess.call([editor, str(temp_path)])
        return True
    except FileNotFoundError:
        print(f"Error: Editor '{editor}' not found.")
        print("Please set the EDITOR environment variable to a valid editor.")
        os.unlink(temp_path)
        return False
    except OSError as e:
        print(f"Error launching editor: {e}")
        os.unlink(temp_path)
        return False


def read_file_content(temp_path: Path) -> str | None:
    """Read content from the file after editing.

    :param temp_path: Path to the file to read
    """

    try:
        with open(temp_path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print(f"Error reading file: {e}")
        os.unlink(temp_path)
        return None


def prompt_continue() -> bool:
    """Prompt user to continue after validation failure."""

    try:
        input("Press Enter to continue...")
        return True
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return False

"""Add input command."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from amphimixis.cli.templates import CONFIG_TEMPLATE
from amphimixis.validator import validate


def _get_initial_content(config_path: Path) -> str:
    """Get initial content for the editor.

    :param config_path: Path to the configuration file
    """

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read()
    return CONFIG_TEMPLATE


def _create_temp_file(content: str) -> Path:
    """Create a temporary file with given content.

    :param content: Content to write to the file
    """

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        return Path(f.name)


def _launch_editor(editor: str, temp_path: Path) -> bool:
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


def _read_file_content(temp_path: Path) -> str | None:
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


def _validate_config(temp_path: Path) -> bool:
    """Validate configuration file with error handling.

    :param temp_path: Path to the configuration file
    """

    try:
        return validate(str(temp_path))
    except yaml.YAMLError as e:
        print(f"\nError: Invalid YAML syntax: {e}")
        print("Editor will reopen for corrections...")
    except TypeError:
        print(
            "\nError: Configuration is invalid. Required fields are missing or empty."
        )
        print("Please fill in the required fields (platforms, recipes, builds).")
        print("Editor will reopen for corrections...")
    # pylint: disable=broad-except
    except Exception as e:
        print(f"\nError: Validation failed: {e}")
        print("Editor will reopen for corrections...")
    return False


def _save_config(temp_path: Path, config_path: Path) -> bool:
    """Save the configuration file to the target location.

    :param temp_path: Path to the temporary file
    :param config_path: Path to the target configuration file
    """

    try:
        shutil.move(str(temp_path), str(config_path))
    except OSError as e:
        print(f"Error saving file: {e}")
        return False
    print("Configuration file input.yml successfully created!")
    return True


def _prompt_continue() -> bool:
    """Prompt user to continue after validation failure."""

    try:
        input("Press Enter to continue...")
        return True
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return False


def run_add_input() -> bool:
    """Interactively create input.yml configuration file.

    Opens an editor with existing file if it exists, or with a template
    if not. Validates the result and saves to input.yml on success.
    """

    config_path = Path("input.yml")
    editor = os.environ.get("EDITOR", "nano")

    current_content = _get_initial_content(config_path)

    print(f"Opening editor: {editor}")
    print("Edit the configuration and save to validate.")
    print("The editor will reopen if validation fails.\n")

    while True:
        temp_path = _create_temp_file(current_content)

        if not _launch_editor(editor, temp_path):
            return False

        new_content = _read_file_content(temp_path)
        if new_content is None:
            return False

        current_content = new_content

        if _validate_config(temp_path):
            return _save_config(temp_path, config_path)

        print("\nValidation failed. Please fix the errors above.")
        if not _prompt_continue():
            if temp_path.exists():
                os.unlink(temp_path)
            return False

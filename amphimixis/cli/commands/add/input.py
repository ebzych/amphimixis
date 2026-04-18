"""Add input command."""

# pylint: disable=duplicate-code

import os
import shutil
from pathlib import Path

import yaml

from amphimixis.cli.templates import CONFIG_TEMPLATE
from amphimixis.cli.utils import (
    create_temp_file,
    edit_and_read_temp_file,
    prompt_continue,
)
from amphimixis.general.constants import DEFAULT_CONFIG_PATH
from amphimixis.validator import validate


def _validate_config(temp_path: Path) -> bool:
    """Validate configuration file with error handling.

    :param temp_path: Path to the configuration file
    """

    try:
        return validate(str(temp_path))

    except yaml.YAMLError as e:
        print(f"\nError: Invalid YAML syntax: {e}")
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
    print(f"Configuration file {config_path.name} successfully created!")
    return True


def _get_unique_path(base_path: Path) -> Path:
    """Return a unique file path by adding suffix if base exists."""

    if not base_path.exists():
        return base_path
    counter = 1
    while True:
        new_path = base_path.with_stem(f"{base_path.stem}-{counter}")
        if not new_path.exists():
            return new_path
        counter += 1


def run_add_input() -> bool:
    """Create input.yml from template using $EDITOR (nano by default).

    Validates after editing; reopens editor on failure. If input.yml exists,
    generates a unique name (input-1.yml, etc.) to avoid overwriting.
    """

    base_path = DEFAULT_CONFIG_PATH
    editor = os.environ.get("EDITOR", "nano")
    current_content = CONFIG_TEMPLATE

    print(f"Opening editor: {editor}")
    print("Edit the configuration and save to validate.")
    print("The editor will reopen if validation fails.\n")

    temp_path = create_temp_file(current_content)
    try:
        while True:
            new_content, ok = edit_and_read_temp_file(editor, temp_path)
            if not ok:
                return False
            current_content = new_content

            if _validate_config(temp_path):
                config_path = _get_unique_path(base_path)
                return _save_config(temp_path, config_path)

            print("\nValidation failed. Please fix the errors above.")
            if not prompt_continue():
                return False

    finally:
        if temp_path.exists():
            os.unlink(temp_path)

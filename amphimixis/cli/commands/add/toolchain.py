"""Add toolchain command."""

import os
import subprocess
import tempfile
from pathlib import Path

import yaml

from amphimixis.cli.templates import TOOLCHAIN_TEMPLATE
from amphimixis.laboratory_assistant import LaboratoryAssistant


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


def _validate_toolchain_yaml(content: str) -> tuple[dict | None, bool]:
    """Validate toolchain YAML content.

    :param content: YAML content to validate
    """

    try:
        toolchain = yaml.safe_load(content)
    except yaml.YAMLError as e:
        print(f"\nYAML parse error: {e}")
        print("Editor will reopen for corrections...")
        return None, False

    if not isinstance(toolchain, dict):
        print("\nError: Toolchain must be a dictionary.")
        print("Editor will reopen for corrections...")
        return None, False

    if "name" not in toolchain or not toolchain["name"]:
        print("\nError: Toolchain must have a 'name' field.")
        print("Editor will reopen for corrections...")
        return None, False

    return toolchain, True


def _check_toolchain_exists(toolchain_name: str, toolbox: dict) -> bool:
    """Check if toolchain with given name already exists.

    :param toolchain_name: Name of the toolchain
    :param toolbox: Toolbox configuration
    """

    if toolchain_name in toolbox.get("toolchains", {}):
        print(f"\nWarning: Toolchain '{toolchain_name}' already exists.")
        print("Not overwriting. Please choose a different name.")
        print("Editor will reopen for corrections...")
        return True
    return False


def _build_toolchain_data(new_toolchain: dict) -> dict:
    """Build toolchain data dict from user input.

    :param new_toolchain: Raw toolchain data from user
    """

    target_arch = new_toolchain.get("target_arch")
    sysroot = new_toolchain.get("sysroot")
    platform = new_toolchain.get("platform")
    attributes = new_toolchain.get("attributes", {})

    platform_value = platform if platform else "localhost"

    toolchain_data: dict = {"attributes": attributes}
    if target_arch:
        toolchain_data["target_arch"] = target_arch
    if sysroot:
        toolchain_data["sysroot"] = sysroot
    if platform:
        toolchain_data["platform"] = platform_value

    return toolchain_data


def _save_toolchain_to_config(
    toolbox: dict, toolchain_name: str, toolchain_data: dict, temp_path: Path
) -> bool:
    """Save toolchain to global config.

    :param toolbox: Toolbox configuration
    :param toolchain_name: Name of the toolchain
    :param toolchain_data: Toolchain data to save
    :param temp_path: Temporary file path to clean up
    """

    toolbox["toolchains"][toolchain_name] = toolchain_data

    try:
        # pylint: disable=protected-access
        LaboratoryAssistant._dump_config(toolbox)
    except OSError as e:
        print(f"Error saving toolchain: {e}")
        if temp_path.exists():
            os.unlink(temp_path)
        return False

    if temp_path.exists():
        os.unlink(temp_path)
    print(f"Toolchain '{toolchain_name}' added successfully!")
    return True


def _prompt_continue() -> bool:
    """Prompt user to continue after validation failure."""

    try:
        input("Press Enter to continue...")
        return True
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return False


def run_add_toolchain() -> bool:
    """Interactively add a toolchain to global config.

    Opens an editor with a toolchain template, validates the result,
    and adds the toolchain to global config (~/.config/amphimixis/toolbox.yml).
    """

    editor = os.environ.get("EDITOR", "nano")

    toolbox = LaboratoryAssistant.parse_config_file()

    if "toolchains" not in toolbox:
        toolbox["toolchains"] = {}

    current_content = TOOLCHAIN_TEMPLATE

    print(f"Opening editor: {editor}")
    print("Edit the toolchain template and save to validate.")
    print("The editor will reopen if validation fails.\n")

    while True:
        temp_path = _create_temp_file(current_content)

        if not _launch_editor(editor, temp_path):
            return False

        new_content = _read_file_content(temp_path)
        if new_content is None:
            return False

        current_content = new_content

        new_toolchain, is_valid = _validate_toolchain_yaml(current_content)
        if not is_valid or new_toolchain is None:
            if not _prompt_continue():
                if temp_path.exists():
                    os.unlink(temp_path)
                return False
            continue

        toolchain_name = new_toolchain["name"]

        if _check_toolchain_exists(toolchain_name, toolbox):
            if not _prompt_continue():
                if temp_path.exists():
                    os.unlink(temp_path)
                return False
            continue

        toolchain_data = _build_toolchain_data(new_toolchain)

        if _save_toolchain_to_config(
            toolbox, toolchain_name, toolchain_data, temp_path
        ):
            return True

        return False

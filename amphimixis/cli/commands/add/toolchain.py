"""Add toolchain command."""

import os

import yaml

from amphimixis.cli.templates import TOOLCHAIN_TEMPLATE
from amphimixis.cli.utils import (
    create_temp_file,
    edit_and_read_temp_file,
    prompt_continue,
)
from amphimixis.laboratory_assistant import LaboratoryAssistant


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
    toolbox: dict, toolchain_name: str, toolchain_data: dict
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
        return False
    print(f"Toolchain '{toolchain_name}' added successfully!")
    return True


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
        temp_path = create_temp_file(current_content)
        try:
            new_content, ok = edit_and_read_temp_file(editor, temp_path)
            if not ok:
                return False
            current_content = new_content

            new_toolchain, is_valid = _validate_toolchain_yaml(current_content)
            if not is_valid or new_toolchain is None:
                if not prompt_continue():
                    return False
                continue

            toolchain_name = new_toolchain["name"]

            if _check_toolchain_exists(toolchain_name, toolbox):
                if not prompt_continue():
                    return False
                continue

            toolchain_data = _build_toolchain_data(new_toolchain)
            return _save_toolchain_to_config(toolbox, toolchain_name, toolchain_data)
        finally:
            if temp_path.exists():
                os.unlink(temp_path)

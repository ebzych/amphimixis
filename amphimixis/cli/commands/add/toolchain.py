"""Add toolchain command."""

# pylint: disable=duplicate-code

import os

import yaml

from amphimixis.cli.templates import TOOLCHAIN_TEMPLATE
from amphimixis.cli.utils import (
    create_temp_file,
    edit_and_read_temp_file,
    prompt_continue,
)
from amphimixis.configurator import create_toolchain
from amphimixis.general.general import Arch
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


def _check_toolchain_exists(toolchain_name: str) -> bool:
    """Check if toolchain with given name already exists.

    :param toolchain_name: Name of the toolchain
    """

    if LaboratoryAssistant.find_toolchain_by_name(toolchain_name) is not None:
        print(f"\nWarning: Toolchain '{toolchain_name}' already exists.")
        print("Not overwriting. Please choose a different name.")
        print("Editor will reopen for corrections...")
        return True
    return False


def run_add_toolchain() -> bool:
    """Interactively add a toolchain to global config."""

    editor = os.environ.get("EDITOR", "nano")
    current_content = TOOLCHAIN_TEMPLATE

    print(f"Opening editor: {editor}")
    print("Edit the toolchain template and save to validate.")
    print("The editor will reopen if validation fails.\n")

    temp_path = create_temp_file(current_content)
    try:
        while True:
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

            if _check_toolchain_exists(toolchain_name):
                if not prompt_continue():
                    return False
                continue

            toolchain = create_toolchain(new_toolchain)
            if toolchain is None:
                print("Error: Failed to create toolchain object.")
                return False

            platform = new_toolchain.get("platform", "localhost")
            target_arch_str = new_toolchain.get("target_arch", "x86")
            try:
                target_arch = Arch(target_arch_str.lower())
            except ValueError:
                print(f"Error: Unsupported architecture '{target_arch_str}'")
                return False

            if LaboratoryAssistant.add_toolchain(toolchain, platform, target_arch):
                print(f"Toolchain '{toolchain_name}' added successfully!")
                return True
            print(f"Failed to add toolchain '{toolchain_name}'.")
            return False

    finally:
        if temp_path.exists():
            os.unlink(temp_path)

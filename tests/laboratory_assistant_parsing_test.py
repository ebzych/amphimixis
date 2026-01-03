"""Test of parsing toolbox file"""

from os import path, remove
from shutil import rmtree

import yaml

from amphimixis import LaboratoryAssistant
from amphimixis.laboratory_assistant import _PLATFORMS, _SYSROOTS, _TOOLCHAINS


def is_file_exists_and_correct(pth: str) -> bool:
    """Check if file creating correct"""
    is_exists = path.exists(pth)

    LaboratoryAssistant.CONFIG_DIR_PATH = "/tmp/amphimixis"
    LaboratoryAssistant.TOOLBOX_PATH = "/tmp/amphimixis/toolbox.yml"

    is_correct_filled = False
    with open(LaboratoryAssistant.TOOLBOX_PATH, "r", encoding="utf-8") as f_toolbox:
        toolbox = yaml.safe_load(f_toolbox)
        is_correct_filled = toolbox == {
            _PLATFORMS: {},
            _TOOLCHAINS: {},
            _SYSROOTS: {},
        }
    return is_exists and is_correct_filled


def test_creating_dir() -> None:
    """
    Remove f"{ToolchainManager.CONFIG_DIR_PATH}" and call _parse_config_file()
    Expected: create directory f"{ToolchainManager.CONFIG_DIR_PATH}"
    """
    LaboratoryAssistant.CONFIG_DIR_PATH = "/tmp/amphimixis"

    if path.exists(LaboratoryAssistant.CONFIG_DIR_PATH):
        rmtree(LaboratoryAssistant.CONFIG_DIR_PATH)

    LaboratoryAssistant.parse_config_file()
    assert path.exists(LaboratoryAssistant.CONFIG_DIR_PATH)


def test_creating_file() -> None:
    """
    Remove f"ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml" and call _parse_config_file()
    Expected: create file f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml" and fill it correct
    """
    LaboratoryAssistant.TOOLBOX_PATH = "/tmp/amphimixis/toolbox.yml"

    if path.exists(LaboratoryAssistant.TOOLBOX_PATH):
        remove(LaboratoryAssistant.TOOLBOX_PATH)

    LaboratoryAssistant.parse_config_file()
    assert is_file_exists_and_correct(LaboratoryAssistant.TOOLBOX_PATH)


def test_creating_dir_and_file():
    """Test if directory and file creating correct"""
    LaboratoryAssistant.TOOLBOX_PATH = "/tmp/amphimixis/toolbox.yml"

    rmtree(LaboratoryAssistant.CONFIG_DIR_PATH)
    LaboratoryAssistant.parse_config_file()

    assert path.exists(LaboratoryAssistant.CONFIG_DIR_PATH)
    assert is_file_exists_and_correct(LaboratoryAssistant.TOOLBOX_PATH)

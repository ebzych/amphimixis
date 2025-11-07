"""Test of parsing toolbox file"""

from os import remove, path
from shutil import rmtree
import yaml
from amphimixis.toolchain_manager import ToolchainManager


def is_file_exists_and_correct(pth: str) -> bool:
    """Check if file creating correct"""
    is_exists = path.exists(pth)

    is_correct_filled = False
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "r", encoding="utf-8"
    ) as f_toolbox:
        toolbox = yaml.safe_load(f_toolbox)
        is_correct_filled = toolbox == {
            "platforms": {},
            "toolchains": {},
            "sysroots": {},
        }
    return is_exists and is_correct_filled


def test_creating_dir() -> None:
    """
    Remove f"{ToolchainManager.CONFIG_DIR_PATH}" and call _parse_config_file()
    Expected: create directory f"{ToolchainManager.CONFIG_DIR_PATH}"
    """
    if path.exists(ToolchainManager.CONFIG_DIR_PATH):
        rmtree(ToolchainManager.CONFIG_DIR_PATH)

    ToolchainManager.parse_config_file()
    assert path.exists(ToolchainManager.CONFIG_DIR_PATH)


def test_creating_file() -> None:
    """
    Remove f"ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml" and call _parse_config_file()
    Expected: create file f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml" and fill it correct
    """
    if path.exists(f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml"):
        remove(f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml")

    ToolchainManager.parse_config_file()
    assert is_file_exists_and_correct(f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml")


def test_creating_dir_and_file():
    """Test if directory and file creating correct"""
    rmtree(ToolchainManager.CONFIG_DIR_PATH)
    ToolchainManager.parse_config_file()

    assert path.exists(ToolchainManager.CONFIG_DIR_PATH)
    assert is_file_exists_and_correct(f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml")

"""Tests of adding items in toolbox"""

from shutil import rmtree

import yaml

from amphimixis import ToolchainManager
from amphimixis.general import Arch, MachineAuthenticationInfo, MachineInfo


def test_adding_two_non_existing_platform_in_toolbox_file() -> None:
    """
    Test: Adding two non-existing platform to the toolbox
    Expected: Platforms appeared in the toolbox
    """
    ToolchainManager.CONFIG_DIR_PATH = "/tmp/amphimixis"
    rmtree(ToolchainManager.CONFIG_DIR_PATH, ignore_errors=True)

    # construct new platform
    platform_name = "platka-bianbu"
    machine = MachineInfo(
        Arch.X86,
        "333.666.069.404",
        MachineAuthenticationInfo("bzych", None, 8000),
    )

    # add platform to toolbox via ToolchainManager
    ToolchainManager.add_platform(platform_name, machine)

    # reload from file
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "r", encoding="utf-8"
    ) as f_toolbox:
        experimental = yaml.safe_load(f_toolbox)

    # check that platform was load correct from experimental
    assert experimental["platforms"][platform_name] == machine.__dictstr__

    # construct new platform
    platform_name = "platku-smazhem-bianbu"
    machine = MachineInfo(
        Arch.X86,
        "333.666.069.404",
        MachineAuthenticationInfo("bzych", "best-passwd", 8000),
    )

    # add platform to toolbox via ToolchainManager
    ToolchainManager.add_platform(platform_name, machine)

    # reload from file
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "r", encoding="utf-8"
    ) as f_toolbox:
        experimental = yaml.safe_load(f_toolbox)

    # check that toolchain was load correct from experimental
    assert experimental["platforms"][platform_name] == machine.__dictstr__


def test_adding_not_existing_toolchain_in_toolbox_file_with_specifying_machine_info() -> (
    None
):
    """
    Test: Adding non-existing toolchain to the toolbox with specifying machine info
    Expected: Toolchain appeared in the toolbox
    """
    ToolchainManager.CONFIG_DIR_PATH = "/tmp/amphimixis"
    rmtree(ToolchainManager.CONFIG_DIR_PATH, ignore_errors=True)

    # 1) construct new toolchain
    path_to_toolchain = "/bin/g++-14"
    target_arch = Arch.RISCV
    build_machine = MachineInfo(
        Arch.X86,
        "333.666.069.404",
        MachineAuthenticationInfo("bzych", None, 8000),
    )

    toolchain_name = "g++-14-platka"

    # 2) add toolchain to toolbox via ToolchainManager
    ToolchainManager.add_toolchain(
        toolchain_name,
        build_machine,
        path_to_toolchain,
        target_arch,
    )

    # 3) construct this toolchain as dictionary
    toolchain_data = {
        "path": path_to_toolchain,
        "target_arch": target_arch.value,
    }

    platform_name = ToolchainManager.find_platform_by_address(
        str(build_machine.address)
    )

    if platform_name:
        toolchain_data["platform"] = platform_name

    # 3) reload from file
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "r", encoding="utf-8"
    ) as f_toolbox:
        experimental = yaml.safe_load(f_toolbox)

    # 4) check that toolchain was load correct from experimental
    assert experimental["toolchains"][toolchain_name] == toolchain_data

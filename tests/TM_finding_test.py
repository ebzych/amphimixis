"""Tests of finding items in toolbox"""

from shutil import rmtree

from amphimixis import ToolchainManager
from amphimixis.general import Arch, MachineAuthenticationInfo, MachineInfo


def test_find_platform_by_addtess() -> None:
    """Find platform by address of machine
    Expect: find existing platform and not find non-existing"""
    ToolchainManager.CONFIG_DIR_PATH = "/tmp/amphimixis"
    rmtree(ToolchainManager.CONFIG_DIR_PATH, ignore_errors=True)
    _toolbox = ToolchainManager.parse_config_file()

    # construct new platform
    platform_name = "platku-smazhem-bianbu"
    platform_address = "333.666.069.404"
    machine = MachineInfo(
        Arch.X86,
        platform_address,
        MachineAuthenticationInfo("bzych", "best-passwd", 8000),
    )

    # add platform to toolbox via ToolchainManager
    ToolchainManager.add_platform(platform_name, machine)

    # check that platform was load correct from experimental
    assert ToolchainManager.find_platform_by_address(platform_address) == platform_name

    rmtree(ToolchainManager.CONFIG_DIR_PATH, ignore_errors=True)

    # construct new platform
    platform_name = "platku-smazhem-bianbu"
    platform_address = "333.666.069.404"
    machine = MachineInfo(
        Arch.X86,
        platform_address,
        MachineAuthenticationInfo("bzych", "best-passwd", 8000),
    )

    # add platform to toolbox via ToolchainManager
    ToolchainManager.add_platform(platform_name, machine)

    platform_address = "192.068.323.17"

    # check that platform not in toolbox
    assert not ToolchainManager.find_platform_by_address(platform_address)

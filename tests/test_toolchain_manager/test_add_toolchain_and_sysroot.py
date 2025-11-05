"""Tests of adding toolchains and sysroots"""

from shutil import rmtree

import yaml

from amphimixis import ToolchainManager
from amphimixis.general import Arch, MachineAuthenticationInfo, MachineInfo


def test_adding_not_existing_toolchain_in_toolbox_file() -> None:
    """
    Test: Adding non-existing toolchain to the toolbox
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
    toolchain_data = {
        "platform": build_machine.__dictstr__,
        "path": path_to_toolchain,
        "target_arch": target_arch,
    }

    # 2) add toolchain to toolbox via ToolchainManager
    ToolchainManager.add_toolchain(
        toolchain_name,
        build_machine,
        path_to_toolchain,
        target_arch,
    )

    # 3) reload from file
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "r", encoding="utf-8"
    ) as f_toolbox:
        experimental = yaml.safe_load(f_toolbox)

    # 4) check that toolchain was load correct from experimental
    assert experimental["toolchains"][toolchain_name] == toolchain_data

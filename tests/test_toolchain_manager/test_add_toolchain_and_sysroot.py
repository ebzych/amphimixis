"""Tests of adding toolchains and sysroots"""

import yaml
from amphimixis.general import (
    MachineInfo,
    MachineAuthenticationInfo,
    Arch,
)
from amphimixis import ToolchainManager


def test_adding_not_existing_toolchain_in_toolbox_file() -> None:
    """
    Test: Adding non-existing toolchain to the toolbox
    Expected: Toolchain appeared in the toolbox
    """

    # 1) save data from config
    saved = ToolchainManager.parse_config_file()  # for saving personal user toolbox
    experimental = saved  # copy to testing

    # 2) construct new toolchain
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

    # 3) remove constructed toolchain from testing toolbox and dump it
    experimental.pop(toolchain_name, False)
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "w", encoding="utf-8"
    ) as f_toolbox:
        yaml.safe_dump(experimental, f_toolbox)

    # 4) add toolchain to toolbox via ToolchainManager
    ToolchainManager.add_toolchain(
        toolchain_name,
        build_machine,
        path_to_toolchain,
        target_arch,
    )

    # 5) reload from file
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "r", encoding="utf-8"
    ) as f_toolbox:
        experimental = yaml.safe_load(f_toolbox)

    # 6) load saved user toolbox data
    with open(
        f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml", "w", encoding="utf-8"
    ) as f_toolbox:
        yaml.safe_dump(saved, f_toolbox)

    # 7) check that toolchain was load correct from experimental
    assert experimental["toolchains"][toolchain_name] == toolchain_data

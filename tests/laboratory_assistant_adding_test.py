"""Tests of adding items in toolbox"""

from shutil import rmtree

from amphimixis import LaboratoryAssistant
from amphimixis.general import (
    Arch,
    CompilerFlagsAttrs,
    MachineAuthenticationInfo,
    MachineInfo,
    Toolchain,
    ToolchainAttrs,
)
from amphimixis.laboratory_assistant import (
    _ATTRIBUTES,
    _PLATFORM,
    _PLATFORMS,
    _SYSROOT,
    _TARGET_ARCH,
    _TOOLCHAINS,
)


def test_adding_two_non_existing_platform_in_toolbox_file() -> None:
    """
    Test: Adding two non-existing platform to the toolbox
    Expected: Platforms appeared in the toolbox
    """

    LaboratoryAssistant.CONFIG_DIR_PATH = "/tmp/amphimixis"
    LaboratoryAssistant.TOOLBOX_PATH = "/tmp/amphimixis/toolbox.yml"
    rmtree(LaboratoryAssistant.CONFIG_DIR_PATH, ignore_errors=True)

    # construct new platform
    platform_name = "platka-bianbu"
    machine = MachineInfo(
        Arch.X86,
        "333.666.069.404",
        MachineAuthenticationInfo("bzych", None, 8000),
    )

    # add platform to toolbox via ToolchainManager
    LaboratoryAssistant.add_platform(platform_name, machine)

    # reload from file
    experimental = LaboratoryAssistant.parse_config_file()

    # check that platform was load correct from experimental
    assert experimental[_PLATFORMS][platform_name] == machine.__dictstr__

    # construct new platform
    platform_name = "platku-smazhem-bianbu"
    machine = MachineInfo(
        Arch.X86,
        "333.666.069.404",
        MachineAuthenticationInfo("bzych", "best-passwd", 8000),
    )

    # add platform to toolbox via ToolchainManager
    LaboratoryAssistant.add_platform(platform_name, machine)

    # reload from file
    experimental = LaboratoryAssistant.parse_config_file()

    # check that toolchain was load correct from experimental
    assert experimental[_PLATFORMS][platform_name] == machine.__dictstr__

    LaboratoryAssistant.reset_config_paths()


def test_adding_not_existing_toolchain_in_toolbox_file_with_specifying_machine_info() -> (
    None
):
    """
    Test: Adding non-existing toolchain to the toolbox with specifying machine info
    Expected: Toolchain appeared in the toolbox
    """

    LaboratoryAssistant.CONFIG_DIR_PATH = "/tmp/amphimixis"
    LaboratoryAssistant.TOOLBOX_PATH = "/tmp/amphimixis/toolbox.yml"
    rmtree(LaboratoryAssistant.CONFIG_DIR_PATH, ignore_errors=True)

    # 1) construct new toolchain
    toolchain_name = "g++-14-platka"
    sysroot = "/"
    path_cxx_compiler = "/bin/g++-14"
    build_machine = MachineInfo(
        Arch.X86,
        "8.8.8.8",
        MachineAuthenticationInfo("bzych", None, 8000),
    )
    target_arch = Arch.RISCV

    toolchain = Toolchain(toolchain_name, sysroot)
    toolchain.set(ToolchainAttrs.CXX_COMPILER, path_cxx_compiler)
    toolchain.set(CompilerFlagsAttrs.CXX_FLAGS, "-ftree-vectorize")

    # 2) add toolchain to toolbox via ToolchainManager
    LaboratoryAssistant.add_toolchain(toolchain, build_machine, target_arch)

    # 3) construct this toolchain as dictionary
    toolchain_data = {
        _ATTRIBUTES: {
            ToolchainAttrs.CXX_COMPILER: path_cxx_compiler,
            CompilerFlagsAttrs.CXX_FLAGS: "-ftree-vectorize",
        },
        _TARGET_ARCH: target_arch.value,
        _SYSROOT: sysroot,
    }

    platform_name = LaboratoryAssistant.find_platform_by_address(
        str(build_machine.address)
    )

    if platform_name:
        toolchain_data[_PLATFORM] = platform_name

    # 3) reload from file
    experimental = LaboratoryAssistant.parse_config_file()

    # 4) check that toolchain was load correct from experimental
    assert experimental[_TOOLCHAINS][toolchain_name] == toolchain_data

    LaboratoryAssistant.reset_config_paths()

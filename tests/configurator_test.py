"""Configurator tests"""

# pylint: skip-file

from os import environ
from shutil import rmtree

import pytest

from amphimixis import LaboratoryAssistant, configurator
from amphimixis.build_systems import build_systems
from amphimixis.general import (
    Arch,
    CompilerFlagsAttrs,
    MachineAuthenticationInfo,
    MachineInfo,
    Project,
    Toolchain,
    ToolchainAttrs,
)


class TestConfigurator:

    @pytest.fixture
    def _set_testing_environment(self):
        LaboratoryAssistant.CONFIG_DIR_PATH = "/tmp/amphimixis"
        LaboratoryAssistant.TOOLBOX_PATH = "/tmp/amphimixis/toolbox.yml"
        rmtree(LaboratoryAssistant.CONFIG_DIR_PATH, ignore_errors=True)

        yield None

        rmtree(LaboratoryAssistant.CONFIG_DIR_PATH, ignore_errors=True)

        LaboratoryAssistant.CONFIG_DIR_PATH = (
            f"{environ["HOME"]}/.config/amphimixis"
            if environ.get("XDG_CONFIG_HOME") is None
            else f"{environ.get("XDG_CONFIG_HOME")}/amphimixis"
        )
        LaboratoryAssistant.TOOLBOX_PATH = (
            LaboratoryAssistant.CONFIG_DIR_PATH + "/toolbox.yml"
        )

    @pytest.mark.parametrize(
        "arch, address, username, password, port",
        [
            ("x86", None, "cooltester", None, 22),
            ("riscv", None, "riscvuser", None, 8022),
        ],
    )
    def test_create_machine_without_address(
        self, arch, address, username, password, port
    ) -> None:
        """Create MachineInfo without address
        Expect: MachineInfo created with None address"""

        # all fields are assumed to be valid due to validator call before build construction in configurator

        machine_info = {
            "arch": arch,
            "address": address,
            "password": password,
            "port": port,
            "username": username,
        }

        machine = configurator.create_machine(machine_info)

        test_machine = MachineInfo(arch, address, None)

        assert machine == test_machine

    @pytest.mark.parametrize(
        "arch, address, username, password, port",
        [
            ("arm", "192.168.1.100", "armuser", None, 22),
            ("x86", "192.168.1.100", "topologyMaster", "gEmini", 8022),
        ],
    )
    def test_create_machine_with_address(
        self, arch, address, username, password, port
    ) -> None:
        """Create MachineInfo with address
        Expect: MachineInfo created with given address"""

        # all fields are assumed to be valid due to validator call before build construction in configurator

        machine_info = {
            "arch": arch,
            "address": address,
            "password": password,
            "port": port,
            "username": username,
        }

        machine = configurator.create_machine(machine_info)

        test_machine = MachineInfo(
            arch, address, MachineAuthenticationInfo(username, password, port)
        )

        assert machine == test_machine

    @pytest.mark.parametrize(
        "toolchain_name, sysroot, cxx_compiler_path, cxx_flags, target_arch, arch, address, username, password, port",
        [
            (
                "coolchain",
                "/",
                "/usr/bin/g++-15",
                "-O3 -march=native",
                Arch.X86,
                Arch.X86,
                "192.168.1.100",
                "cooltester",
                None,
                22,
            )
        ],
    )
    def test_create_toolchain_by_name(
        self,
        toolchain_name,
        sysroot,
        cxx_compiler_path,
        cxx_flags,
        target_arch,
        arch,
        address,
        username,
        password,
        port,
        _set_testing_environment,
    ) -> None:
        """Create Toolchain by name
        Expect: Toolchain created with given name"""

        # all fields are assumed to be valid due to validator call before build construction in configurator

        build_machine = MachineInfo(
            arch, address, MachineAuthenticationInfo(username, password, port)
        )

        test_toolchain = Toolchain(toolchain_name, sysroot)
        test_toolchain.set(ToolchainAttrs.CXX_COMPILER, cxx_compiler_path)
        test_toolchain.set(CompilerFlagsAttrs.CXX_FLAGS, cxx_flags)

        LaboratoryAssistant.add_toolchain(test_toolchain, build_machine, target_arch)
        toolchain = configurator.create_toolchain(toolchain_name)

        assert (
            toolchain
            and toolchain.get(ToolchainAttrs.CXX_COMPILER)
            == test_toolchain.get(ToolchainAttrs.CXX_COMPILER)
            and toolchain.get(CompilerFlagsAttrs.CXX_FLAGS)
            == test_toolchain.get(CompilerFlagsAttrs.CXX_FLAGS)
            and toolchain.sysroot == test_toolchain.sysroot
        )

    def test_create_toolchain_by_invalid_name(self) -> None:
        """Create Toolchain by invalid name
        Expect: Toolchain with None value"""

        toolchain = configurator.create_toolchain("unknown_chain")

        assert not toolchain

    @pytest.mark.parametrize(
        "sysroot, c_compiler_path, cxx_compiler_path, cxx_flags",
        [
            ("/", "/usr/bin/gcc-15", "/usr/bin/g++-15", "-O2"),
        ],
    )
    def test_create_toolchain_by_dict(
        self,
        sysroot,
        c_compiler_path,
        cxx_compiler_path,
        cxx_flags,
        _set_testing_environment,
    ) -> None:
        """Create Toolchain by dict
        Expect: Toolchain created with given dict"""

        # all fields are assumed to be valid due to validator call before build construction in configurator

        toolchain_dict = {
            "sysroot": sysroot,
            "c_compiler": c_compiler_path,
            "cxx_compiler": cxx_compiler_path,
            "cxx_flags": cxx_flags,
        }

        toolchain = configurator.create_toolchain(toolchain_dict)

        assert (
            toolchain
            and toolchain.sysroot == sysroot
            and toolchain.get(ToolchainAttrs.CXX_COMPILER) == cxx_compiler_path
            and toolchain.get(ToolchainAttrs.C_COMPILER) == c_compiler_path
            and toolchain.get(CompilerFlagsAttrs.CXX_FLAGS) == cxx_flags
        )

    def test_create_toolchain_by_dict_with_unknown_attribute(
        self,
        _set_testing_environment,
    ) -> None:
        """Create Toolchain by dict with unknown attribute
        Expect: Toolchain created without unknown attribute"""

        # all fields are assumed to be valid due to validator call before build construction in configurator

        toolchain_dict = {
            "sysroot": "/",
            "unknown_attr": "mongolian tugrik",
        }

        toolchain = configurator.create_toolchain(toolchain_dict)

        test_toolchain = Toolchain("unknown_chain", "/")

        assert toolchain and toolchain.data == test_toolchain.data

    @pytest.mark.parametrize("c_flags, cxx_flags", [("-O2", "-O3")])
    def test_create_flags(self, c_flags, cxx_flags) -> None:
        """Create CompilerFlags
        Expect: CompilerFlags created with given dict"""

        # all fields are assumed to be valid due to validator call before build construction in configurator

        flags_dict = {
            "c_flags": c_flags,
            "cxx_flags": cxx_flags,
        }

        flags = configurator.create_flags(flags_dict)

        assert (
            flags
            and flags.get(CompilerFlagsAttrs.C_FLAGS) == flags_dict["c_flags"]
            and flags.get(CompilerFlagsAttrs.CXX_FLAGS) == flags_dict["cxx_flags"]
        )

    def test_create_empty_flags(self) -> None:
        """Create empty CompilerFlags
        Expect: None returned"""

        flags = configurator.create_flags(None)

        assert not flags

    @pytest.mark.parametrize(
        "config_file_path",
        [("tests/integration/input_local.yaml"), ("tests/invalid.yaml")],
    )
    @pytest.mark.parametrize(
        "project",
        [
            Project(
                "/",
                [],
                build_systems.CMake,
                build_systems.CMake,
            )
        ],
    )
    def test_parse_config(self, config_file_path, project) -> None:
        """
        Test: Parsing configuration file
        Expected: Configuration successful on valid file, fails on invalid file
        """

        if config_file_path == "tests/integration/input_local.yaml":
            assert configurator.parse_config(project, config_file_path)
        else:
            assert not configurator.parse_config(project, config_file_path)

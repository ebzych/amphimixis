"""Class that manages and provides toolchains and sysroots"""

from os import makedirs, getlogin
from os.path import exists
from abc import ABC
import yaml
from shell import Shell
from general.architecture import Arch
from general.general import Build
from general.machine import MachineInfo


class ToolchainManager(ABC):
    """"""

    _config_path: str
    _toolbox: list[str]

    @staticmethod
    def _parse_config_file() -> None:
        """Search ~/.config/amphimixis/toolbox.yml and parse in __toolbox list or create it"""

        makedirs(f"/home/{getlogin()}/.config/amphimixis", exist_ok=True)
        if exists(f"/home/{getlogin()}/.config/amphimixis/toolbox.yml"):
            with open(
                f"/home/{getlogin()}/.config/amphimixis/toolbox.yml",
                "r",
                encoding="utf-8",
            ) as f:
                ToolchainManager._toolbox = yaml.safe_load(f)
                f.close()
        else:
            with open(
                f"/home/{getlogin()}/.config/amphimixis/toolbox.yml",
                "w",
                encoding="utf-8",
            ) as f:
                template = {"platforms": None, "toolchains": None, "sysroots": None}
                yaml.safe_dump(template, f)

    @staticmethod
    def _get_toolchain_by_name(name: str) -> tuple[MachineInfo, str]:
        """"""

        raise NotImplementedError

    @staticmethod
    def _get_sysroot_by_str(name: str) -> tuple[MachineInfo, str]:
        """"""

        raise NotImplementedError

    @staticmethod
    def _is_path_is_absolute_path(s: str) -> bool:
        __is_path = False
        # pylint: disable=consider-using-enumerate
        for i in range(len(s)):
            if s[i] == " " and (i >= 1 and s[i - 1] != "\\" or i == 0):
                raise ValueError("Invalid path to the toolchain")
            if s[i] == "/":
                __is_path = True
        if __is_path and s[0] != "/":
            raise ValueError("Absolute path required for toolchain")
        return __is_path

    @staticmethod
    def get_toolchain_from_build(build: Build) -> str | None:
        """Resolve string Build.toolchain: absolute path or name of known toolchain
        Return absolute path to toolchain on building machine"""
        if build.toolchain is None:
            if build.build_machine.arch != build.run_machine.arch:
                raise ValueError(
                    "Machine and toolchain compatible error: "
                    "architecture of running machine and "
                    "target architecture of toolchain is different"
                )
            return None

        toolchain_path: str
        # temporary pylint disabling while 'else' not implemented
        # pylint: disable=no-else-return
        if ToolchainManager._is_path_is_absolute_path(build.toolchain):
            toolchain_path = build.toolchain
        else:
            raise NotImplementedError

        shell = Shell(build.build_machine)
        shell.connect()
        if shell.run(f"ls {toolchain_path}")[0] != 0:
            raise ValueError("Toolchain not found on the building machine")

        return toolchain_path

    @staticmethod
    def get_sysroot_from_build(build: Build) -> str | None:
        """Resolve string Build.sysroot: absolute path or name of known sysroot
        Return absolute path to sysroot on building machine"""
        if build.sysroot is None:
            if build.build_machine.arch != build.run_machine.arch:
                raise ValueError(
                    "Machine and sysroot compatible error: "
                    "architecture of running machine and "
                    "architecture of sysroot is different"
                )
            return None

        sysroot_path: str
        # temporary pylint disabling while 'else' not implemented
        # pylint: disable=no-else-return
        if ToolchainManager._is_path_is_absolute_path(build.sysroot):
            sysroot_path = build.sysroot
        else:
            raise NotImplementedError

        shell = Shell(build.build_machine)
        shell.connect()
        if shell.run(f"ls {sysroot_path}")[0] != 0:
            raise ValueError("Sysroot not found on the building machine")

        return sysroot_path

    @staticmethod
    def add_toolchain(machine_name: str, path: str, arch: Arch) -> None:
        """"""

        raise NotImplementedError

    @staticmethod
    def add_sysroot(name_machine: str, path: str, arch: Arch) -> None:
        """"""

        raise NotImplementedError

    @staticmethod
    def install_to_sysroot(path_to_sysroot: str, *packages: str) -> int:
        """"""

        raise NotImplementedError

    @staticmethod
    def remove_toolchain(name: str) -> None:
        """"""

        raise NotImplementedError

    @staticmethod
    def remove_sysroot(name: str) -> None:
        """"""

        raise NotImplementedError

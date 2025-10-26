"""Class that manages and provides toolchains and sysroots"""

from abc import ABC
from os import environ, makedirs
from os.path import exists, isabs

import yaml

from general import Arch, Build, MachineInfo
from shell import Shell


class ToolchainManager(ABC):
    """Toolchain Manager"""

    _config_path: str
    _toolbox: list[str]

    @staticmethod
    def _parse_config_file() -> None:
        """Search ~/.config/amphimixis/toolbox.yml and parse in __toolbox list or create it"""

        makedirs(f"{environ["HOME"]}/.config/amphimixis", exist_ok=True)
        if exists(f"{environ["HOME"]}/.config/amphimixis/toolbox.yml"):
            with open(
                f"{environ["HOME"]}/.config/amphimixis/toolbox.yml",
                "r",
                encoding="utf-8",
            ) as f:
                ToolchainManager._toolbox = yaml.safe_load(f)
                f.close()
        else:
            with open(
                f"{environ["HOME"]}/.config/amphimixis/toolbox.yml",
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
        if isabs(build.toolchain):
            toolchain_path = build.toolchain
        else:
            if build.toolchain.isalpha():
                pass
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
        if isabs(build.sysroot):
            sysroot_path = build.sysroot
        else:
            if build.sysroot.isalpha():
                pass
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

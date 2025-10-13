"""Class that manages and provides toolchains and sysroots"""

from os import makedirs, getlogin
from os.path import exists
from abc import ABC
import yaml
from Arch import Arch
from general import Build, PathOnMachine, MachineInfo, MachineAuthenticationInfo
from shell import Shell


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
                template = {"platforms": None, "compilers": None, "sysroots": None}
                yaml.safe_dump(template, f)

    @staticmethod
    def _get_compiler_by_name(name: str) -> PathOnMachine:
        """"""

        raise NotImplementedError

    @staticmethod
    def _get_sysroot_by_str(name: str) -> PathOnMachine:
        """"""

        raise NotImplementedError

    @staticmethod
    def get_compiler_from_build(build: Build) -> str:
        """"""
        compiler: PathOnMachine
        if type(build.compiler) == str:
            compiler = ToolchainManager._get_compiler_by_name(build.compiler)
        elif type(build.compiler) == PathOnMachine:
            compiler = build.compiler
        verifier = Shell(
            str(compiler.machine.address),
            MachineAuthenticationInfo(compiler.machine.auth).port,
            compiler.machine.auth.username,
            compiler.machine.auth.password,
        )

        return ""

    @staticmethod
    def get_sysroot_from_build(build: Build) -> str:
        return ""

    @staticmethod
    def add_compiler(machine_name: str, path: str, arch: Arch) -> None:
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
    def remove_compiler(name: str) -> None:
        """"""

        raise NotImplementedError

    @staticmethod
    def remove_sysroot(name: str) -> None:
        """"""

        raise NotImplementedError

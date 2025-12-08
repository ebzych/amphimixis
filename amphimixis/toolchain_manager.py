"""Class that manages and provides toolchains and sysroots"""

from os import environ, makedirs
from os.path import exists, isabs

import yaml

from amphimixis import logger
from amphimixis.general.general import (
    Arch,
    Build,
    MachineAuthenticationInfo,
    MachineInfo,
    Toolchain,
)
from amphimixis.shell.shell import Shell

_logger = logger.setup_logger("TOOLCHAIN_MANAGER")

_PLATFORMS = "platforms"
_SYSROOTS = "sysroots"
_TOOLCHAINS = "toolchains"

_STD_INDENT = 4


class ToolchainManager:
    """Toolchain Manager"""

    CONFIG_DIR_PATH = (
        f"{environ["HOME"]}/.config/amphimixis"
        if environ.get("XDG_CONFIG_HOME") is None
        else f"{environ.get("XDG_CONFIG_HOME")}/amphimixis"
    )

    @staticmethod
    def parse_config_file() -> dict:
        """Search ~/.config/amphimixis/toolbox.yml and parse in __toolbox list or create it"""

        template: dict[str, dict] = {
            _PLATFORMS: {},
            _TOOLCHAINS: {},
            _SYSROOTS: {},
        }
        makedirs(ToolchainManager.CONFIG_DIR_PATH, exist_ok=True)
        if exists(f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml"):
            with open(
                f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml",
                "r",
                encoding="utf-8",
            ) as f_toolbox:
                if dict(_toolbox := yaml.safe_load(f_toolbox)).keys() == set(
                    [_PLATFORMS, _TOOLCHAINS, _SYSROOTS]
                ):
                    return _toolbox
        with open(
            f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml",
            "w",
            encoding="utf-8",
        ) as f_toolbox:
            yaml.safe_dump(template, f_toolbox)
            return template

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
    def find_platform(platform_name: str) -> MachineInfo | None:
        """Find platform in amphimixis global config (toolbox) by name

        :rtype: MachineInfo | None
        :return: info about machine if found else None"""
        _toolbox = ToolchainManager.parse_config_file()
        if platform_name in _toolbox[_PLATFORMS]:
            machine = _toolbox[_PLATFORMS][platform_name]
            auth: MachineAuthenticationInfo
            if "auth" in machine:
                auth = MachineAuthenticationInfo(
                    machine["auth"]["username"],
                    (
                        machine["auth"]["password"]
                        if "password" in machine["auth"]
                        else None
                    ),
                    machine["auth"]["port"],
                )
            return MachineInfo(
                Arch(machine["arch"]),
                machine["address"] if "address" in machine else None,
                auth,
            )
        return None

    @staticmethod
    def find_platform_by_address(address: str) -> str:
        """Find platform in amphimixis global config (toolbox) by address

        :rtype: str
        :return: platform name if platform exists else empty string"""
        _toolbox = ToolchainManager.parse_config_file()
        for name, machine in _toolbox["platforms"].items():
            if machine["address"] == address:
                return name
        return ""

    @staticmethod
    def add_platform(name: str, machine: MachineInfo) -> bool:
        """Add platform to amphimixis global config (toolbox)"""
        _toolbox = ToolchainManager.parse_config_file()
        _toolbox[_PLATFORMS][name] = machine.__dictstr__
        try:
            with open(
                f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml",
                "w",
                encoding="utf-8",
            ) as f_toolbox:
                yaml.safe_dump(_toolbox, f_toolbox)
            return True
        except FileExistsError:
            _logger.error("Error with writing to config file")
            return False

    @staticmethod
    def find_toolchain(toolchain_name: str) -> str:
        """Find toolchain in amphimixis global config (toolbox) by name

        :rtype: str
        :return: platform name if platform exists else empty string"""
        raise NotImplementedError

    @staticmethod
    def add_toolchain(
        toolchain: Toolchain,
        machine_or_name: MachineInfo | str,
        target_arch: Arch,
    ) -> bool:
        """Add toolchain to amphimixis global config (toolbox)"""
        # temporary pylint disable
        # pylint: disable=no-else-raise

        if not toolchain.data:
            return False

        toolchain_data: dict[str, str | dict[str, str]] = {}
        platform_name: str
        if isinstance(machine_or_name, str):
            if ToolchainManager.find_platform(machine_or_name) is None:
                return False
            toolchain_data["platform"] = machine_or_name
        else:
            if machine_or_name.address is not None:  # else: localhost
                if not (
                    platform_name := ToolchainManager.find_platform_by_address(
                        machine_or_name.address
                    )
                ):
                    platform_name = "".join(machine_or_name.address.split(sep="."))
                    ToolchainManager.add_platform(platform_name, machine_or_name)
                toolchain_data["platform"] = platform_name

        toolchain_data["target_arch"] = target_arch.value
        toolchain_data["attributes"] = toolchain.data
        if toolchain.sysroot:
            toolchain_data["sysroot"] = toolchain.sysroot

        _toolbox = ToolchainManager.parse_config_file()
        _toolbox[_TOOLCHAINS][toolchain.name] = toolchain_data
        with open(
            f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml",
            "w",
            encoding="utf-8",
        ) as f_toolbox:
            yaml.safe_dump(_toolbox, f_toolbox, indent=_STD_INDENT)
        return True

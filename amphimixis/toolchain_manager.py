"""Class that manages and provides toolchains and sysroots"""

from os import environ, makedirs
from os.path import exists, isabs

import yaml

from amphimixis.general.general import Arch, Build, MachineInfo
from amphimixis.shell.shell import Shell


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
            "platforms": {},
            "toolchains": {},
            "sysroots": {},
        }
        makedirs(ToolchainManager.CONFIG_DIR_PATH, exist_ok=True)
        if exists(f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml"):
            with open(
                f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml",
                "r",
                encoding="utf-8",
            ) as f_toolbox:

                if dict(_toolbox := yaml.safe_load(f_toolbox)).keys() == set(
                    ["platforms", "toolchains", "sysroots"]
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
    def add_toolchain(
        toolchain_name: str,
        machine_or_name: MachineInfo | str,
        path: str,
        target_arch: Arch,
    ) -> None:
        """Add toolchain to toolbox"""
        _toolbox = ToolchainManager.parse_config_file()
        # temporary pylint disable
        # pylint: disable=no-else-raise
        if isinstance(machine_or_name, str):
            raise NotImplementedError
        else:
            toolchain_data = {
                "platform": machine_or_name.__dictstr__,
                "path": path,
                "target_arch": target_arch.value,
            }

            _toolbox["toolchains"][toolchain_name] = toolchain_data
            with open(
                f"{ToolchainManager.CONFIG_DIR_PATH}/toolbox.yml",
                "w",
                encoding="utf-8",
            ) as f_toolbox:
                yaml.safe_dump(_toolbox, f_toolbox)

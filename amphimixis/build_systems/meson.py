"Meson build system implementation"

import os

from amphimixis import logger
from amphimixis.build_systems.ninja import Ninja
from amphimixis.general.general import (
    Build,
    BuildSystem,
    CompilerFlags,
    CompilerFlagsAttrs,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
    Toolchain,
)
from amphimixis.shell import Shell

_logger = logger.setup_logger("MESON")


class Meson(BuildSystem, IHighLevelBuildSystem):
    """Meson build system implementation.

    Meson uses Ninja as its default backend for building.
    Configuration is done via `meson setup`.
    """

    def _attrs_map(self, tool: str) -> str:
        value = "".join(tool.upper().split("_")).split("COMPILER", maxsplit=1)[0]
        match value.split("FLAGS")[0]:
            case "C":
                value = value.replace("C", "CC")
            case "FORTRAN":
                value = value.replace("FORTRAN", "FC")
            case _:
                return value
        return value

    def _generate_flags(self, flags: CompilerFlags | Toolchain):
        ret_flags = []
        for flag, value in flags.data.items():
            meson_option = self._attrs_map(flag)
            ret_flags.append(f"{meson_option}='{value}'")
        return " ".join(ret_flags)

    def build(self, build: Build) -> tuple[int, str, str]:
        """Configure and build via Meson.

        Runs `meson setup` to configure and `meson compile` to build.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        shell = Shell(build.build_machine, self._ui).connect()

        build_path = os.path.join(
            shell.get_project_workdir(self._project), build.build_name
        )
        source_dir = shell.get_source_dir(self._project)
        command = f"meson setup {build_path} {source_dir} "
        if build.config_flags is not None:
            command += f"{build.config_flags} "
        if build.compiler_flags is not None:
            command += f"{self._generate_flags(build.compiler_flags)} "
        if build.toolchain is not None:
            if build.toolchain.sysroot is not None:
                command += f"--sysroot={build.toolchain.sysroot} "
            command += f"{self._generate_flags(build.toolchain)} "

        err, stdout, stderr = shell.run(f"cd {source_dir}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        _logger.info(
            "Run building with '%s' and 'meson compile -C %s'", command, build_path
        )
        err, stdout, stderr = shell.run(command, f"meson compile -C {build_path}")
        if len(stdout) > 1:
            stdout[0].extend(stdout[1])
            stderr[0].extend(stderr[1])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

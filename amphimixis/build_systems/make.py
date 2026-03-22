"Make IBuildSystem implementation"

import os

from amphimixis import logger
from amphimixis.general import (
    Build,
    BuildSystem,
    CompilerFlags,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
    Toolchain,
)
from amphimixis.shell import Shell

_logger = logger.setup_logger("MAKE")


class Make(BuildSystem, IHighLevelBuildSystem, ILowLevelBuildSystem):
    """Make implementation of BuildSystem.

    Make can be used as:
    - High-level build system (build()) for simple Makefile-based projects
    - Low-level runner (run_building()) after CMake configuration

    Uses the base class methods for:
    - get_build_path(): Determines build path based on machine address
    """

    _GNU_standard_compability_warn_msg = (
        "Amphimixis only uses GNU standard flags for Makefile, "
        "if Makefile does not meet this standard, then using your toolchains and"
        " compilation flags may not work, you can fix it manually by specifying "
        "them in the config_flags field in the format used by the current Makefile"
    )

    def _toolchain_attrs_map(self, tool: str) -> str:
        value = "".join(tool.upper().split("_")).split("COMPILER")[0]
        match value:
            case "C":
                return "CC"
            case _:
                return value

    # pylint: disable=duplicate-code
    def _generate_lang_flags(self, flags: CompilerFlags):
        ret_flags = []
        for flag, value in flags.data.items():
            ret_flags.append(f"{"".join(flag.upper().split("_"))}='{value}'")
        return " ".join(ret_flags)

    def _generate_toolchain_flags(self, toolchain: Toolchain):
        ret_flags = []
        for tool, value in toolchain.data.items():
            ret_flags.append(f"{self._toolchain_attrs_map(tool)}='{value}'")
        return " ".join(ret_flags)

    # pylint: disable=too-many-locals
    def _build_install_clean(
        self, build: Build, configure: bool = False
    ) -> tuple[int, str, str]:
        shell = Shell(self._project, build.build_machine, self._ui).connect()
        build_path = os.path.join(shell.get_project_workdir(), build.build_name)
        command = "make "
        cd_dir = build_path
        if configure:
            if build.config_flags is not None:
                command += f"{build.config_flags} "
            if build.compiler_flags is not None:
                command += f"{self._generate_lang_flags(build.compiler_flags)} "
            if build.toolchain is not None:
                if build.toolchain.sysroot is not None:
                    command += f"SYSROOT={build.toolchain.sysroot} "
                command += f"{self._generate_toolchain_flags(build.toolchain)} "
            cd_dir = shell.get_source_dir()

        err_nproc, stdout_nproc, _ = shell.run("nproc")
        nproc = 1
        if err_nproc == 0 and stdout_nproc:
            nproc = int(stdout_nproc[0][0].strip())
            if nproc > 1:
                nproc -= 1
        command += f"-j{nproc} "

        err, stdout, stderr = shell.run(f"cd {cd_dir}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        _logger.info("Run building with '%s'", command)
        err, stdout, stderr = shell.run(command)
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))
        if configure:
            err_, stdout_, stderr_ = shell.run(
                f"make install DESTDIR={build_path}", "make clean"
            )
            err = err_ if err == 0 else err
            stdout[0].extend([line for cmd_stdout in stdout_ for line in cmd_stdout])
            stderr[0].extend([line for cmd_stderr in stderr_ for line in cmd_stderr])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

    def build(self, build: Build) -> tuple[int, str, str]:
        """Build via Make

        :param Build build: Build to build
        :return: Tuple of error code, stdout and stderr"""
        self._ui.print_warning(
            build.build_name,
            Make._GNU_standard_compability_warn_msg,
        )
        _logger.warning(Make._GNU_standard_compability_warn_msg)

        return self._build_install_clean(build, configure=True)

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run building via Make

        :param Build build: Build to run building
        :return: Tuple of error code, stdout and stderr"""
        return self._build_install_clean(build)

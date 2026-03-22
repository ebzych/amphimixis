"Gmake (GNU Make) build system implementation"

import os

from amphimixis import logger
from amphimixis.general.general import (
    Build,
    BuildSystem,
    CompilerFlags,
    IHighLevelBuildSystem,
    Toolchain,
)
from amphimixis.shell import Shell

_logger = logger.setup_logger("GMAKE")


class Gmake(BuildSystem, IHighLevelBuildSystem):
    """Gmake (GNU Make) implementation of IBuildSystem.

    Gmake is the GNU implementation of make with additional features
    compared to standard make. It follows the same interface as Make.

    Uses the base class methods for:
    - get_build_path(): Determines build path based on machine address
    """

    _GNU_standard_compability_warn_msg = (
        "Amphimixis only uses GNU standard flags for Gmake, "
        "if Makefile does not meet this standard, then using your toolchains and"
        " compilation flags may not work, you can fix it manually by specifying "
        "them in the config_flags field in the format used by the current Makefile"
    )

    _lang_flags_map = {
        "c_flags": "CFLAGS",
        "cxx_flags": "CXXFLAGS",
        "cuda_flags": "CUDAFLAGS",
        "objc_flags": "OBJCFLAGS",
        "objcxx_flags": "OBJCXXFLAGS",
        "fortran_flags": "FFLAGS",
        "hip_flags": "HIPFLAGS",
        "ispc_flags": "ISPCFLAGS",
        "swift_flags": "SWIFTFLAGS",
        "asm_flags": "ASMFLAGS",
        "asm_nasm_flags": "ASMFLAGS",
        "asm_marmasm_flags": "ASMFLAGS",
        "asm_masm_flags": "ASMFLAGS",
        "asm_att_flags": "ASMFLAGS",
        "csharp_flags": "CSHARPFLAGS",
    }

    def _toolchain_attrs_map(self, tool: str) -> str:
        value = tool.upper().split("_COMPILER")[0].strip("_")
        match value:
            case "C":
                return "CC"
            case _:
                return value

    def _generate_lang_flags(self, flags: CompilerFlags):
        ret_flags = []
        for flag, value in flags.data.items():
            gmake_flag = self._lang_flags_map.get(flag.value, flag.value.upper())
            ret_flags.append(f"{gmake_flag}='{value}'")
        return " ".join(ret_flags)

    def _generate_toolchain_flags(self, toolchain: Toolchain):
        ret_flags = []
        for tool, value in toolchain.data.items():
            ret_flags.append(f"{self._toolchain_attrs_map(tool)}='{value}'")
        return " ".join(ret_flags)

    def _build_install_clean(
        self, build: Build, configure: bool = False
    ) -> tuple[int, str, str]:
        shell = Shell(build.build_machine, self._ui).connect()
        build_path = os.path.join(
            shell.get_project_workdir(self._project), build.build_name
        )
        command = "gmake "
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
            cd_dir = shell.get_source_dir(self._project)

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
                f"gmake install DESTDIR={build_path}", "gmake clean"
            )
            err = err_ if err == 0 else err
            stdout[0].extend([line for cmd_stdout in stdout_ for line in cmd_stdout])
            stderr[0].extend([line for cmd_stderr in stderr_ for line in cmd_stderr])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

    def build(self, build: Build) -> tuple[int, str, str]:
        """Build via Gmake

        :param Build build: Build to build
        :return: Tuple of error code, stdout and stderr"""
        self._ui.print_warning(
            build.build_name,
            Gmake._GNU_standard_compability_warn_msg,
        )
        _logger.warning(Gmake._GNU_standard_compability_warn_msg)

        return self._build_install_clean(build, configure=True)

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run building via Gmake

        :param Build build: Build to run building
        :return: Tuple of error code, stdout and stderr"""
        return self._build_install_clean(build)

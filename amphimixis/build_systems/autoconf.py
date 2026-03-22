"Autoconf build system implementation"

import os

from amphimixis import logger
from amphimixis.build_systems.make import Make
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

_logger = logger.setup_logger("AUTOCONF")


class Autoconf(BuildSystem, IHighLevelBuildSystem):
    """Autoconf build system implementation.

    Autoconf uses ./configure script to configure the project,
    then make to build.
    """

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
        "asm_nasm_flags": "ASM_NASM_FLAGS",
        "asm_marmasm_flags": "ASM_MARMASM_FLAGS",
        "asm_masm_flags": "ASM_MASM_FLAGS",
        "asm_att_flags": "ASM_ATT_FLAGS",
        "csharp_flags": "CSHARPFLAGS",
    }

    _tool_flags_map = {
        "c_compiler": "CC",
        "cxx_compiler": "CXX",
        "cuda_compiler": "CUDA",
        "objc_compiler": "OBJC",
        "objcxx_compiler": "OBJCXX",
        "fortran_compiler": "FC",
        "hip_compiler": "HIP",
        "ispc_compiler": "ISPC",
        "swift_compiler": "SWIFT",
        "asm_compiler": "ASM",
        "ar": "AR",
        "as": "AS",
        "ld": "LD",
        "nm": "NM",
        "objcopy": "OBJCOPY",
        "objdump": "OBJDUMP",
        "ranlib": "RANLIB",
        "readelf": "READELF",
        "strip": "STRIP",
        "asm_nasm_compiler": "ASM_NASM",
        "asm_marmasm_compiler": "ASM_MARMASM",
        "asm_masm_compiler": "ASM_MASM",
        "asm_att_compiler": "ASM_ATT",
        "csharp_compiler": "CSHARP",
    }

    def _generate_lang_flags(self, flags: CompilerFlags):
        ret_flags = []
        for flag, value in flags.data.items():
            autoconf_flag = self._lang_flags_map.get(flag.value, flag.value.upper())
            ret_flags.append(f"{autoconf_flag}='{value}'")
        return " ".join(ret_flags)

    def _generate_toolchain_flags(self, toolchain: Toolchain):
        ret_flags = []
        for tool, value in toolchain.data.items():
            autoconf_flag = self._tool_flags_map.get(tool, tool.upper())
            ret_flags.append(f"{autoconf_flag}='{value}'")
        return " ".join(ret_flags)

    def build(self, build: Build) -> tuple[int, str, str]:
        """Configure and build via Autoconf/Make.

        Runs ./configure then make.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        shell = Shell(build.build_machine, self._ui).connect()

        build_path = os.path.join(
            shell.get_project_workdir(self._project), build.build_name
        )
        source_dir = shell.get_source_dir(self._project)

        err, stdout, stderr = shell.run(f"mkdir -p {build_path}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        command = f"./configure"
        if build.config_flags is not None:
            command += f" {build.config_flags}"
        if build.compiler_flags is not None:
            command += f" {self._generate_lang_flags(build.compiler_flags)}"
        if build.toolchain is not None:
            if build.toolchain.sysroot is not None:
                command += f" CPPFLAGS='-I{build.toolchain.sysroot}/include' LDFLAGS='-L{build.toolchain.sysroot}/lib'"
            command += f" {self._generate_toolchain_flags(build.toolchain)}"

        err, stdout, stderr = shell.run(f"cd {source_dir} && {command}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        err_nproc, stdout_nproc, _ = shell.run("nproc")
        nproc = 4
        if err_nproc == 0 and stdout_nproc:
            nproc = int(stdout_nproc[0][0])
            if nproc > 1:
                nproc -= 1

        _logger.info("Run building with 'make -j%d' in '%s'", nproc, build_path)
        err, stdout, stderr = shell.run(f"cd {source_dir} && make -j{nproc}")
        if len(stdout) > 1:
            stdout[0].extend(stdout[1])
            stderr[0].extend(stderr[1])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

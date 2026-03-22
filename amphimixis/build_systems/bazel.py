"Bazel build system implementation"

import os

from amphimixis import logger
from amphimixis.general.general import (
    Build,
    BuildSystem,
    CompilerFlags,
    CompilerFlagsAttrs,
    IHighLevelBuildSystem,
    Toolchain,
    ToolchainAttrs,
)
from amphimixis.shell import Shell

_logger = logger.setup_logger("BAZEL")


class Bazel(BuildSystem, IHighLevelBuildSystem):
    """Bazel build system implementation.

    Bazel is a build system that uses BUILD files to describe builds.
    It doesn't require a separate configuration step like CMake or Autoconf.

    Uses the base class methods for:
    - get_build_path(): Determines build path based on machine address
    """

    _lang_flags_map = {
        "c_flags": "--copt",
        "cxx_flags": "--cxxopt",
        "cuda_flags": "--cudaopt",
        "objc_flags": "--objcopt",
        "objcxx_flags": "--objcopt",
        "fortran_flags": "--fortranopt",
        "hip_flags": "--hipopt",
        "ispc_flags": "--ispcopt",
        "swift_flags": "--swiftopt",
        "asm_flags": "--asmopt",
        "asm_nasm_flags": "--asmopt",
        "asm_marmasm_flags": "--asmopt",
        "asm_masm_flags": "--asmopt",
        "asm_att_flags": "--asmopt",
        "csharp_flags": "--csharpopt",
    }

    _tool_options_map = {
        "c_compiler": "--compiler",
        "cxx_compiler": "--cxx",
        "cuda_compiler": "--cuda_compiler",
        "objc_compiler": "--objc_compiler",
        "objcxx_compiler": "--objcxx_compiler",
        "fortran_compiler": "--fortran_compiler",
        "hip_compiler": "--hip_compiler",
        "ispc_compiler": "--ispc_compiler",
        "swift_compiler": "--swift_compiler",
        "asm_compiler": "--asm_compiler",
    }

    def _generate_lang_flags(self, flags: CompilerFlags):
        ret_flags = []
        for flag, value in flags.data.items():
            bazel_option = self._lang_flags_map.get(flag.value, f"--{flag.value}")
            ret_flags.append(f"{bazel_option}='{value}'")
        return " ".join(ret_flags)

    def _generate_toolchain_options(self, toolchain: Toolchain):
        ret_flags = []
        for tool, value in toolchain.data.items():
            bazel_option = self._tool_options_map.get(tool, f"--{tool}")
            ret_flags.append(f"{bazel_option}={value}")
        return " ".join(ret_flags)

    def _generate_bazel_flags(self, build: Build) -> list[str]:
        flags = []

        if build.config_flags:
            flags.extend(build.config_flags.split())

        if build.compiler_flags is not None:
            flags.append(self._generate_lang_flags(build.compiler_flags))

        if build.toolchain is not None:
            if build.toolchain.sysroot:
                flags.append(f"--sysroot={build.toolchain.sysroot}")
            flags.append(self._generate_toolchain_options(build.toolchain))

        return flags

    def _get_default_target(self, build: Build) -> str:
        if build.executables:
            return build.executables[0]
        return "//..."

    def build(self, build: Build) -> tuple[int, str, str]:
        """Build via Bazel.

        Runs `bazel build` with configured targets and flags.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        shell = Shell(build.build_machine, self._ui).connect()

        source_dir = shell.get_source_dir(self._project)

        bazel_flags = self._generate_bazel_flags(build)
        target = self._get_default_target(build)

        flags_str = " ".join(bazel_flags) if bazel_flags else ""
        command = f"cd {source_dir} && bazel build {flags_str} {target}".strip()

        _logger.info("Bazel build: '%s'", command)
        err, stdout, stderr = shell.run(command)

        all_stdout: list[str] = []
        all_stderr: list[str] = []
        for line_list in stdout:
            all_stdout.extend(line_list)
        for line_list in stderr:
            all_stderr.extend(line_list)

        return (err, "".join(all_stdout), "".join(all_stderr))

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run Bazel build in project directory.

        Bazel doesn't need a separate build step after configuration,
        so this just runs bazel build again.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        return self.build(build)

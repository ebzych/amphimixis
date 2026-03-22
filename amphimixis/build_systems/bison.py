"Bison build system implementation"

import os

from amphimixis import logger
from amphimixis.general.general import (
    Build,
    BuildSystem,
    CompilerFlags,
    CompilerFlagsAttrs,
    IHighLevelBuildSystem,
)
from amphimixis.shell import Shell

_logger = logger.setup_logger("BISON")


class Bison(BuildSystem, IHighLevelBuildSystem):
    """Bison build system implementation.

    Bison is the GNU parser generator, compatible with yacc.
    It generates parser files from grammar specifications.

    Uses the base class methods for:
    - get_build_path(): Determines build path based on machine address
    """

    _lang_directives_map = {
        "c_flags": "%code",
        "cxx_flags": "%skeleton",
        "cuda_flags": "%skeleton",
        "objc_flags": "%code",
        "objcxx_flags": "%skeleton",
        "fortran_flags": "%skeleton",
        "hip_flags": "%skeleton",
        "ispc_flags": "%skeleton",
        "swift_flags": "%skeleton",
        "asm_flags": "%code",
        "csharp_flags": "%skeleton",
    }

    def _generate_directives(self, flags: CompilerFlags) -> str:
        ret_parts = []
        for flag, value in flags.data.items():
            directive = self._lang_directives_map.get(flag.value, "%code")
            ret_parts.append(f"{directive}{{{value}}}")
        return " ".join(ret_parts)

    def _generate_output_flags(self) -> str:
        return "-d"

    def build(self, build: Build) -> tuple[int, str, str]:
        """Build via Bison.

        Runs bison command to generate parser.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        shell = Shell(build.build_machine, self._ui).connect()

        source_dir = shell.get_source_dir(self._project)

        if not build.executables or len(build.executables) == 0:
            _logger.error("No source file specified for bison")
            return (1, "No source file specified", "No source file specified")

        source_file = build.executables[0]

        command = f"bison {self._generate_output_flags()}"
        if build.config_flags is not None:
            command += f" {build.config_flags}"
        if build.compiler_flags is not None:
            command += f" {self._generate_directives(build.compiler_flags)}"
        command += f" {source_file}"

        err, stdout, stderr = shell.run(f"cd {source_dir}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        _logger.info("Run bison with '%s'", command)
        err, stdout, stderr = shell.run(command)

        if len(stdout) > 1:
            stdout[0].extend(stdout[1])
            stderr[0].extend(stderr[1])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run bison to regenerate parser.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        return self.build(build)

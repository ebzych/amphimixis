"Yacc build system implementation"

import os

from amphimixis import logger
from amphimixis.general.general import (
    Build,
    BuildSystem,
    IHighLevelBuildSystem,
)
from amphimixis.shell import Shell

_logger = logger.setup_logger("YACC")


class Yacc(BuildSystem, IHighLevelBuildSystem):
    """Yacc (Yet Another Compiler Compiler) build system implementation.

    Yacc is a parser generator that generates a parser from a grammar specification.
    It typically generates a C file (y.tab.c) and header file (y.tab.h).

    Uses the base class methods for:
    - get_build_path(): Determines build path based on machine address
    """

    def _generate_output_flags(self) -> str:
        return "-d"

    def build(self, build: Build) -> tuple[int, str, str]:
        """Build via Yacc.

        Runs yacc command to generate parser.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        shell = Shell(build.build_machine, self._ui).connect()

        source_dir = shell.get_source_dir(self._project)

        if not build.executables or len(build.executables) == 0:
            _logger.error("No source file specified for yacc")
            return (1, "No source file specified", "No source file specified")

        source_file = build.executables[0]
        yacc_output_file = "y.tab.c"
        yacc_header_file = "y.tab.h"

        command = f"yacc {self._generate_output_flags()}"
        if build.config_flags is not None:
            command += f" {build.config_flags}"
        command += f" {source_file}"

        err, stdout, stderr = shell.run(f"cd {source_dir}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        _logger.info("Run yacc with '%s'", command)
        err, stdout, stderr = shell.run(command)

        if len(stdout) > 1:
            stdout[0].extend(stdout[1])
            stderr[0].extend(stderr[1])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run yacc to regenerate parser.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout, stderr)
        """
        return self.build(build)

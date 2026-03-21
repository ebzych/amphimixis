"Ninja build system implementation"

import os

from amphimixis import logger
from amphimixis.general.general import Build, BuildSystem, ILowLevelBuildSystem
from amphimixis.shell import Shell

_logger = logger.setup_logger("NINJA")


class Ninja(BuildSystem, ILowLevelBuildSystem):
    """Ninja build system implementation"""

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run ninja in the build directory.

        :param Build build: Build configuration
        :return: Tuple of (error_code, stdout_lines, stderr_lines)
        """
        shell = Shell(build.build_machine, self._ui).connect()
        build_path = os.path.join(
            shell.get_project_workdir(self._project), build.build_name
        )
        command = "ninja "
        err, stdout, stderr = shell.run(f"cd {build_path}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))
        _logger.info("Run building with '%s'", command)
        err, stdout, stderr = shell.run(command)

        return (err, "".join(stdout[0]), "".join(stderr[0]))

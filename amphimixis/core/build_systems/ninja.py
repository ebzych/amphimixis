"""Module working with Ninja build system"""

import os

from amphimixis.core import logger
from amphimixis.core.general.general import (
    Build,
    BuildSystem,
    ILowLevelBuildSystem,
    DummyRunner,
    Project,
    IUI,
    NullUI,
)
from amphimixis.core.shell import Shell


class Ninja(BuildSystem, ILowLevelBuildSystem):
    """Implementation of working with Ninja build system"""

    def __init__(
        self,
        project: Project,
        runner: ILowLevelBuildSystem = DummyRunner(),
        ui: IUI = NullUI(),
    ):
        super().__init__(
            project,
            runner,
            ui,
        )
        self._logger = BuildSystem.CustomLogger(logger.setup_logger("NINJA"), {})

    def run_building(self, build: Build) -> tuple[int, str, str]:
        """Run ninja in the build directory.

        :param Build build: Build configuration
        :rtype: tuple[int, str, str]
        :return: Tuple of error_code, stdout, stderr
        """
        self._logger.extra["build"] = build.build_name  # type: ignore[index]
        shell = Shell(self._project, build.build_machine, self._ui).connect()
        build_path = os.path.join(shell.get_project_workdir(), build.build_name)
        command = "ninja "
        if build.jobs:
            command += f"-j {build.jobs} "
        err, stdout, stderr = shell.run(f"cd {build_path}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))
        self._logger.info("Run building with '%s'", command)
        err, stdout, stderr = shell.run(command)

        return (err, "".join(stdout[0]), "".join(stderr[0]))

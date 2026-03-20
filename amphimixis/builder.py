"""Module that builds a build based on configuration"""

import os

from amphimixis import logger
from amphimixis.general import IUI, NullUI
from amphimixis.general.general import Build, Project
from amphimixis.shell.shell import Shell

_logger = logger.setup_logger("BUILDER")


class Builder:
    """The class is representing a module which builds a build based on its configuration"""

    @staticmethod
    def build(project: Project, ui: IUI = NullUI()) -> None:
        """The method build all builds"""

        for build in project.builds:
            _logger.info("Build the %s", build.build_name)

            if Builder.build_for_linux(project, build, ui):
                _logger.info("Build passed %s", build.build_name)
            else:
                _logger.info("Build failed %s", build.build_name)

    @staticmethod
    def build_for_linux(project: Project, build: Build, ui: IUI = NullUI()) -> bool:
        """The method build program on Linux"""

        ui.update_message(build.build_name, "Connecting...")
        shell = Shell(build.build_machine, ui).connect()

        # path to build on the machine
        path: str = os.path.join(shell.get_project_workdir(project), build.build_name)

        if build.build_machine.address is not None:  # if building on the remote machine
            ui.update_message(
                build.build_name, "Copying project sources to remote machine..."
            )
            if not shell.copy_to_remote(
                os.path.normpath(project.path), "~/amphimixis/"
            ):
                _logger.error("Error in copying source files")
                ui.mark_failed(f"{build.build_name}: error in copying source files")
                return False

        try:
            ui.update_message(build.build_name, "Building...")
            err, _, stderr = shell.run(f"mkdir -p {path}")

            if len(stderr) >= 1 and len(stderr[0]) != 0:
                _logger.error(
                    "Error in creating directory on current machine: %s",
                    "".join(stderr[0]),
                )

            err, sstdout, sstderr = project.build_system.build(build)
            _logger.info("Building output:\n%s", sstdout)
            _logger.info("Building stderr:\n%s", sstderr)

            if err != 0:
                ui.mark_failed(f"{build.build_name}: build failed")
                return False

            return True

        except FileNotFoundError:
            ui.mark_failed(f"{build.build_name}: build system not found")
            return False

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))

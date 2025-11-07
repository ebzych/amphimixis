"""Module that builds a build based on configuration"""

import os
import logging
from amphimixis.general.general import Project, Build
from amphimixis.shell.shell import Shell
from amphimixis.toolchain_manager import ToolchainManager

logging.basicConfig(
    level=logging.INFO,
    filename="amphimixis.log",
    encoding="utf-8",
    filemode="a",
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger(__name__)


class Builder:
    """The class is representing a module which builds a build based on its configuration"""

    @staticmethod
    def build(project: Project) -> None:
        """The method build all builds"""

        for build in project.builds:
            logger.info("Build the %s", os.path.basename(build.build_path))

            if Builder.build_for_linux(project, build):
                logger.info("Build passed")
            else:
                logger.info("Build failed")

    @staticmethod
    def build_for_linux(project: Project, build: Build) -> bool:
        """The method build program on Linux"""
        shell = Shell(build.build_machine).connect()

        path: str  # path to build on the machine
        if build.build_machine.address is not None:  # if building on the remote machine
            path = (
                "~/amphimixis/"
                f"{Builder._normbase(project.path)}_builds/"
                f"{Builder._normbase(build.build_path)}"
            )
            shell.copy_to_remote(os.path.normpath(project.path), "~/amphimixis/")
        else:
            path = f"{build.build_path}"  # if building on the local machine

        build.toolchain = ToolchainManager.get_toolchain_from_build(build)
        logger.info("Use %s", build.toolchain)
        build.sysroot = ToolchainManager.get_sysroot_from_build(build)
        logger.info("Use %s", build.sysroot)

        configuration_prompt = project.build_system.insert_config_flags(
            project, build, ""
        )
        logger.info("Configuration with: %s", configuration_prompt)

        runner_prompt = project.runner.insert_runner_flags(project, build, "")
        logger.info("Run building with: %s", runner_prompt)

        err, stdout, stderr = shell.run(
            f"mkdir -p {path}",
            f"cd {path}",
            configuration_prompt,
            runner_prompt,
        )
        logger.info("Configuration output:\n%s", "".join(stdout[2]))
        logger.info("Configuration stderr:\n%s", "".join(stderr[2]))

        logger.info("Building output:\n%s", "".join(stdout[3]))
        logger.info("Building stderr:\n%s", "".join(stderr[3]))

        return err == 0

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))

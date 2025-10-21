"""Module that builds a build based on configuration"""

import subprocess
import shlex
import os
from general import Project, Build
from shell import Shell


class Builder:
    """The class is representing a module which builds a build based on its configuration"""

    @staticmethod
    def build(project: Project) -> None:
        """The method build all builds"""
        for build in project.builds:
            print(f"Build the {os.path.basename(build.build_path)}")

            if Builder.build_for_linux(project, build):
                print("Build passed")
            else:
                print("Build failed")

    @staticmethod
    def build_for_linux(project: Project, build: Build) -> bool:
        """The method build program on Linux"""
        shell = Shell(build.build_machine).connect()

        path: str  # path to build on the machine
        if build.build_machine.address is not None:  # if building on the remote machine
            path = f"~/amphimixis/{os.path.basename(build.build_path)}"
        else:
            path = f"{build.build_path}"  # if building on the local machine

        shell.copy_to_remote(project.path, "~/amphimixis")
        shell.run(
            f"mkdir -p {path}",
            f"cd {path}",
        )

        return (
            shell.run(
                project.build_system.insert_config_flags(project, build, ""),
                project.runner.insert_runner_flags(project, build, ""),
            )[0]
            == 0
        )

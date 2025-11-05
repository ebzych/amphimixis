"""Module that builds a build based on configuration"""

import os
from amphimixis.general.general import Project, Build
from amphimixis.shell.shell import Shell


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
            path = (
                "~/amphimixis/"
                f"{Builder._normbase(project.path)}_builds/"
                f"{Builder._normbase(build.build_path)}"
            )
            if not shell.copy_to_remote(
                os.path.normpath(project.path), "~/amphimixis/"
            ):
                print("Error in copying source files")
                return False
        else:
            path = f"{build.build_path}"  # if building on the local machine

        try:
            return (
                shell.run(
                    f"mkdir -p {path}",
                    f"cd {path}",
                    project.build_system.insert_config_flags(project, build, ""),
                    project.runner.insert_runner_flags(project, build, ""),
                )[0]
                == 0
            )
        except FileNotFoundError:
            return False

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))

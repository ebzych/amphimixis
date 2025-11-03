"""Module that builds a build based on configuration"""

import subprocess
import shlex
import os
from amphimixis.general import Project, Build


def run_command(command: str, cwd: str = "") -> bool:
    """Run command via subproccess.run()"""
    command_formatted = shlex.split(command)
    try:
        process = subprocess.run(
            command_formatted,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return process.returncode == 0

    except ValueError as e:
        print(f'Error executing command "{command}": {e}')
        return False


class Builder:
    """The class is representing a module which builds a build based on its configuration"""

    @staticmethod
    def process(project: Project) -> None:
        """The method build all builds"""
        for build in project.builds:
            success = Builder.build_for_linux(project, build)

            if success:
                print("Build passed.")
            else:
                print("Build failed.")

    @staticmethod
    def build_for_linux(project: Project, build: Build) -> bool:
        """The method build program on Linux"""
        os.makedirs(build.build_path, exist_ok=True)

        commands = [
            project.build_system.insert_config_flags(project, build, ""),
            project.runner.insert_runner_flags(project, build, ""),
        ]

        for command in commands:
            if not run_command(command, build.build_path):
                return False
        return True

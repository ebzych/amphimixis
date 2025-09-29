"""Module that builds a build based on configuration"""

import subprocess
import shlex
import os
from general import Project, Build


def run_command(command: str, cwd=None):
    command_formatted = shlex.split(command)
    try:
        process = subprocess.run(
            command_formatted, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if process.returncode:
            print("Command executed successfully.")
            return True

    except Exception as e:
        print(f'Error executing command "{command}": {e}')
        return False


class Builder:
    """The class is representing a module which builds a build based on its configuration"""

    @staticmethod
    def process(project: Project):
        """The method build all builds"""
        for build in project.builds:
            if build.is_specified_script:
                success = Builder.build_with_specified_script(project, build)
            else:
                success = Builder.build_for_linux(project, build)

            if success:
                print("Build passed.")
            else:
                print("Build failed.")

    @staticmethod
    def build_for_linux(project: Project, build: Build):
        """The method build program on Linux"""
        os.makedirs(build.build_path, exist_ok=True)

        commands = [
            build.build_system.insert_config_flags(project, build, ""),
            build.runner.insert_runner_flags(project, build, ""),
        ]

        for command in commands:
            if not run_command(command, build.build_path):
                return False
        return True

    @staticmethod
    def build_with_specified_script(project: Project, build: Build):
        """The method handle case when user specify a script for building"""

        command = build.specified_script
        command = build.build_system.insert_config_flags(project, build, command)
        command = build.runner.insert_runner_flags(project, build, command)

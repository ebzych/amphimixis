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
        return process.returncode == 0

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
                Builder.build_with_specified_script(project, build)
            else:
                Builder.build_for_linux(project, build)

    @staticmethod
    def build_for_linux(project: Project, build: Build):
        """The method build program on Linux"""

        command = "mkdir -p " + build.build_path
        command += " && cd " + build.build_path
        command += " && " + project.build_system.insert_config_flags(project, build, "")
        command += " && " + project.runner.insert_runner_flags(project, build, "")
        # make install
        args = shlex.split(command)
        subprocess.Popen(["sh", "-c"] + [command])
        # terminal one?
        # windws trubles

    @staticmethod
    def build_with_specified_script(project: Project, build: Build):
        """The method handle case when user specify a script for building"""

        command = build.specified_script
        command = project.build_system.insert_config_flags(project, build, command)
        command = project.runner.insert_runner_flags(project, build, command)

"""Is a module which builds a build based on its configuration"""

import subprocess
import shlex
from general import Project, Build


class Builder:
    def build_with_specified_script(self, build: Build):
        return 0

    """The class is representing a module which builds a build based on its configuration"""

    @staticmethod
    def process(project: Project):
        """The method build all builds"""

        for build in project.builds:
            if build.is_specified_script:
                Builder.build_with_specified_script(build)
            else:
                Builder.build_for_linux(build)

    @staticmethod
    def build_for_linux(build: Build):
        """The method build program on Linux"""

        command = "mkdir " + build.build_path
        command += " && cd " + build.build_path
        command += " && cmake" + build.runner.insert_config_flags(build, "")
        command += " && make" + build.runner.insert_runner_flags(build, "")
        # make install
        args = shlex.split(command)
        subprocess.Popen(args)
        # terminal one?
        # windws trubles

    @staticmethod
    def build_with_specified_script(build: Build):
        """The method handle case when user specify a script for building"""

        command = build.specified_script
        command = build.build_system.insert_config_flags(build, command)
        command = build.runner.insert_runner_flags(build, command)

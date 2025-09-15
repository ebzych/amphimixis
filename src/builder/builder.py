from NonAmphimixis.src.general import general
import subprocess
import shlex
from general import Build
import os


class Builder:
    def process(self, project: general.Project):
        for build in project.builds:
            """specific"""
            if build.is_specified_script:
                Builder.build_with_specified_script(build)
            else:
                Builder.build_for_linux(build)

    def build_for_linux(self, build: general.Build):
        command = "mkdir " + build.build_path
        command += " && cd " + build.build_path
        command += " && cmake" + build.runner.insert_config_flags(build, "")
        command += " && make" + build.runner.insert_runner_flags(build, "")
        # make install
        args = shlex.split(command)
        subprocess.Popen(args)
        # terminal one?
        # windws trubles

    def build_with_specified_script(self, build: Build):
        return 0

"CMake IBuildSystem implementation"

import os

# pylint: disable=relative-beyond-top-level
from ..general import Build, IBuildSystem, Project


class CMake(IBuildSystem):
    """The CMake implementation of IBuildSystem"""

    @staticmethod
    def find_cmakelists_path(project: Project) -> str:
        """The method find first CMakeLists.txt file"""

        path_ = ""
        for root, _, files in os.walk(project.path):
            for name in files:
                if name == "CMakeLists.txt":
                    path_ = os.path.join(root, name)
                    return path_
        return path_

    @staticmethod
    def insert_config_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

        if command != "":
            raise NotImplementedError

        command = "cmake " + CMake.find_cmakelists_path(project) + " "
        command += build.config_flags
        command += " CXXFLAGS='" + build.compiler_flags + "'"
        command += " CFLAGS='" + build.compiler_flags + "'"
        command += " " + CMake.insert_toolchain(build)
        command += " " + CMake.insert_sysroot(build)
        return command

    @staticmethod
    def insert_runner_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""

        raise NotImplementedError

    @staticmethod
    def insert_toolchain(build: Build) -> str:
        """Return flag that specify toolchain in build system call"""
        path_to_toolchain = build.toolchain
        if path_to_toolchain is not None:
            flag_path_to_toolchain = "-DCMAKE_C_COMPILER='" + path_to_toolchain + "'"
            flag_path_to_toolchain += (
                " -DCMAKE_CXX_COMPILER='" + path_to_toolchain + "'"
            )
            return flag_path_to_toolchain
        return ""

    @staticmethod
    def insert_sysroot(build: Build) -> str:
        """Return flag that specify sysroot in build system call"""
        path_to_sysroot = build.sysroot
        if path_to_sysroot is not None:
            return "-DCMAKE_SYSROOT='" + path_to_sysroot + "'"
        return ""

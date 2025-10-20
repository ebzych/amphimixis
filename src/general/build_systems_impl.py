"""Implementations of IBuildSystem"""

from os import walk, cpu_count, path
from ToolchainManager import ToolchainManager
from .general import IBuildSystem, Build, Project


class CMake(IBuildSystem):
    """The CMake implementation of IBuildSystem"""

    @staticmethod
    def find_cmakelists_path(project: Project) -> str:
        """The method find first CMakeLists.txt file"""

        path_ = ""
        for root, _, files in walk(project.path):
            for name in files:
                if name == "CMakeLists.txt":
                    path_ = path.join(root, name)
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
        path_to_toolchain = ToolchainManager.get_toolchain_from_build(build)
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
        path_to_sysroot = ToolchainManager.get_sysroot_from_build(build)
        if path_to_sysroot is not None:
            return "-DCMAKE_SYSROOT='" + path_to_sysroot + "'"
        return ""


class Make(IBuildSystem):
    """The Make implementation of IBuildSystem"""

    @staticmethod
    def insert_config_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

        raise NotImplementedError

    @staticmethod
    def insert_runner_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""

        if command != "":
            raise NotImplementedError

        return "make -j" + str(cpu_count())

    @staticmethod
    def insert_toolchain(build: Build) -> str:
        """Return flag that specify toolchain in build system call"""
        raise NotImplementedError

    @staticmethod
    def insert_sysroot(build: Build) -> str:
        """Return flag that specify sysroot in build system call"""
        raise NotImplementedError


build_systems_dict: dict[str, type[IBuildSystem]] = {
    "cmake": CMake,
    "make": Make,
}

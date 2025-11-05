"CMake IBuildSystem implementation"

import os
from amphimixis.general.general import Build, IBuildSystem, Project, MachineInfo


class CMake(IBuildSystem):
    """CMake implementation of IBuildSystem"""

    @staticmethod
    def find_cmakelists_path(project: Project, machine: MachineInfo) -> str:
        """Find first CMakeLists.txt file"""

        max_level_depth = 2

        def _walk(path: str, level: int = 0) -> tuple[int, str]:
            if level > max_level_depth:
                return (0, "")  # don't lift up above max_level_depth

            lvl_path = (0, "")  # default return value
            for root, dirs, files in os.walk(path):
                for dir_ in dirs:
                    lvl_path = _walk(
                        os.path.join(root, dir_), level + 1
                    )  # if found in subdirs
                for file in files:
                    if file == "CMakeLists.txt":
                        return (
                            level,
                            os.path.join(root, file),
                        )  # if found in current dir return this because it has lower level
            return lvl_path  # if not found in files in this dir

        _path = _walk(project.path)[1]

        if machine.address is None:  # local machine
            return os.path.join(project.path, _path)

        return (
            f"~/amphimixis/{CMake._normbase(project.path)}"
            + _path[len(os.path.normpath(project.path)) :]
        )  # remote machine

    @staticmethod
    def insert_config_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

        if command != "":
            raise NotImplementedError

        command = (
            "cmake " + CMake.find_cmakelists_path(project, build.build_machine) + " "
        )
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
            flag_path_to_toolchain = "-DCMAKE_CXX_COMPILER='" + path_to_toolchain + "'"
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

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))

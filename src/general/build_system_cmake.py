"""CMake implementaion of IBuildSystem"""

from abc import abstractmethod
from general import Build, Project
from .build_system_interface import IBuildSystem


class CMake(IBuildSystem):
    """The CMake implementation of IBuildSystem"""

    @staticmethod
    def find_cmakelists_path(project: Project):
        """The method find CMakeLists.txt file"""

        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def insert_config_flags(
        project: Project, build: Build, command: str
    ) -> str:  # type of "build" is Build, type of "project" is Project
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

        if command != "":
            raise NotImplementedError

        command = "cmake " + CMake.find_cmakelists_path(project)
        command += " " + build.config_flags + " "
        command += " CXXFLAGS='" + build.compiler_flags + "'"
        command += " CFLAGS='" + build.compiler_flags + "'"
        command += " -DCMAKE_TOOLCHAIN_FILE=" + build.arch.compiler()
        return command

    @staticmethod
    @abstractmethod
    def insert_runner_flags(
        project: Project, build: Build, command: str
    ) -> str:  # type of "build" is Build, type of "project" is Project
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""

        raise NotImplementedError

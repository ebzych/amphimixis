"""The common module that is used in most other modules"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from os import cpu_count, path, walk


class Arch(str, Enum):
    """Supported architectures"""

    X86 = "x86"
    RISCV = "riscv"
    ARM = "arm"


@dataclass
class MachineAuthenticationInfo:
    """Information about authentication on a remote machine

    :var str username: Username for authentication.
    :var str | None password: Password for authentication.
    Password can be set to None if an SSH agent is used.

    :var int port: Port number for the SSH connection.
    """

    username: str
    password: str | None
    port: int


@dataclass
class MachineInfo:
    """Information about the machine

    :var Arch arch: Architecture of the machine.
    :var str | None address: IP address or hostname of the remote machine.
    If address is None, the machine is considered to be local.

    :var MachineAuthenticationInfo auth: Authentication info for the machine.
    """

    arch: Arch
    address: str | None
    auth: MachineAuthenticationInfo | None


@dataclass
class Build:
    """Class with information about one build of project

    :var MachineInfo machine: Information about the machine.
    :var str build_path: Path to the directory with this build.
    :var bool is_specified_script: True if user specified a build script, False if script is simple.
    :var str specified_script: The user-specified build script.
    :var str config_flags: Configuration flags for the build.
    :var str compiler_flags: Compiler flags for the build.
    """

    build_machine: MachineInfo
    run_machine: MachineInfo
    build_path: str
    toolchain: str | None
    sysroot: str | None
    is_specified_script: bool = False
    specified_script: str = ""
    config_flags: str = ""
    compiler_flags: str = ""


@dataclass
class Project:
    """Class with information about project and his builds

    :var str path: Path to project for research.
    :var type[IBuildSystem] build_system: High-level build system interface.
    :var type[IBuildSystem] runner: Low-level build system interface.
    :var list[Build]: List of project configurations to be build.
    """

    path: str
    builds: list[Build]
    build_system: "type[IBuildSystem]"
    runner: "type[IBuildSystem]"


class IBuildSystem(ABC):
    """Interface for classes implementing interaction with build system"""

    @staticmethod
    @abstractmethod
    def insert_config_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

    @staticmethod
    @abstractmethod
    def insert_runner_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""


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
        return command

    @staticmethod
    def insert_runner_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""

        raise NotImplementedError


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


build_systems_dict: dict[str, type[IBuildSystem]] = {
    "cmake": CMake,
    "make": Make,
}

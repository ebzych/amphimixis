"""The common module that is used in most other modules"""

from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Arch(str, Enum):
    """Supported architectures"""

    X86 = "x86"
    RISCV = "riscv"
    ARM = "arm"


@dataclass
class MachineAuthenticationInfo:
    """Information about authentication on remote machine"""

    username: str
    password: str | None
    port: int

    def reprJSON(self):
        """Method for correct JSON serialization"""
        return dict(username=self.username, password=self.password, port=self.port)


@dataclass
class MachineInfo:
    """Information about the machine

    :var arch Arch: Architecture of the remote machine.
    :var ip str: IP address of the remote machine.
    :var port int: Port of ssh service of the remote machine to connect.
    """

    arch: Arch
    ip: str
    auth: MachineAuthenticationInfo | None

    def reprJSON(self):
        """Method for correct JSON serialization"""

        return dict(
            arch=self.arch,
            ip=self.ip,
            auth=self.auth.reprJSON() if self.auth is not None else None,
        )


class IArch(ABC):
    """Interface for classes implementing interaction with arch of project build
    which specify compiler and sysroot"""

    @staticmethod
    @abstractmethod
    def compiler() -> str:
        """The getter of path to compiler"""

    @staticmethod
    @abstractmethod
    def sysroot() -> str:
        """The getter of path to sysroot"""


class IBuildSystem(ABC):
    """Interface for classes implementing interaction with build system"""

    @staticmethod
    @abstractmethod
    def insert_config_flags(
        project, build, command: str
    ) -> str:  # type of "build" is Build, type of "project" is Project
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

    @staticmethod
    @abstractmethod
    def insert_runner_flags(
        project, build, command: str
    ) -> str:  # type of "build" is Build, type of "project" is Project
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""


@dataclass
class Build:
    """Class with information about one build of project

    :var RemoteMachine machine: Information about the remote machine.
    :var str build_path: Path to the directory with this build.
    :var bool is_specified_script: True if user specified a build script, False if script is simple.
    :var str specified_script: The user-specified build script.
    :var str config_flags: Configuration flags for the build.
    :var str compiler_flags: Compiler flags for the build.
    """

    machine: MachineInfo
    build_path: str
    is_specified_script: bool = False
    specified_script: str = ""
    config_flags: str = ""
    compiler_flags: str = ""


@dataclass
class Project:
    """Class with information about project and his builds

    :var str path: Path to project for research.
    :var IBuildSystem build_system: High-level build system interface.
    :var IBuildSystem runner: Low-level build system interface.
    :var list[Build]: List of project configurations to be build.
    """

    path: str
    build_system: IBuildSystem | None
    runner: IBuildSystem | None
    builds: list[Build]

    def __init__(self, repo_path: str, builds: list[Build]):
        self.path = repo_path
        self.builds = builds
<<<<<<< HEAD


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
        command += ' CXXFLAGS="' + build.compiler_flags + '"'
        command += ' CFLAGS="' + build.compiler_flags
        # command += " COMPILER=" + build.arch.compiler()
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
=======
>>>>>>> 1ee3c5c (refactor: rename definitions.py to build_system_interface.py and separate CMake implementation, IBuildSystem and general.py)

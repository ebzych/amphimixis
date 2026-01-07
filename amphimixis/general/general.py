"""The common module that is used in most other modules"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


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


# pylint: disable=too-many-instance-attributes
@dataclass
class Build:
    """Class with information about one build of project

    :var MachineInfo build_machine: Information about the machine to build at.
    :var MachineInfo build_machine: Information about the machine to profile at.
    :var str build_name: Unique name of the build.
    :var list[str] executables: List of relative to `build path` paths to executables.
    :var str compiler_flags: Compiler flags for the build.
    """

    build_machine: MachineInfo
    run_machine: MachineInfo
    build_name: str
    executables: list[str]
    toolchain: str | None
    sysroot: str | None
    config_flags: str = ""
    compiler_flags: str = ""


@dataclass
class Project:
    """Class with information about project and his builds

    :var str path: Path to project for research.
    :var type[IBuildSystem] build_system: High-level build system interface.
    :var type[IBuildSystem] runner: Low-level build system interface.
    :var list[Build] builds: List of project configurations to be build.
    """

    path: str
    builds: list[Build]
    build_system: "type[IBuildSystem]"
    runner: "type[IBuildSystem]"


# pylint: disable=too-few-public-methods
class IUI(ABC):
    """Interface for User Interface (UI) classes"""

    @abstractmethod
    def step(self, build_id: str) -> None:
        """Advance the progress counter by one step

        :param str build_id: Build identifier
        """

    @abstractmethod
    def update_message(self, build_id: str, message: str) -> None:
        """Update message for specific build

        :param str build_id: Build identifier
        :param str message: Message to store
        """

    @abstractmethod
    def mark_success(self, build_id: str) -> None:
        """Mark build as successful.

        :param build_id: Build identifier
        """

    @abstractmethod
    def mark_failed(self, build_id: str, error: str = "") -> None:
        """Mark build as failed.

        :param build_id: Build identifier
        :param error: Error message
        """


class NullUI(IUI):
    """A UI implementation that does nothing (used to suppress output)"""

    def step(self, build_id: str) -> None:
        pass

    def update_message(self, build_id: str, message: str) -> None:
        pass

    def mark_success(self, build_id: str) -> None:
        pass

    def mark_failed(self, build_id: str, error: str = "") -> None:
        pass


class IBuildSystem(ABC):
    """Interface for classes implementing interaction with build system"""

    @staticmethod
    @abstractmethod
    def get_build_system_prompt(project: Project, build: Build) -> str:
        """Generate build system prompt with all specified flags"""

    @staticmethod
    @abstractmethod
    def get_runner_prompt(project: Project, build: Build) -> str:
        """Generate runner prompt"""

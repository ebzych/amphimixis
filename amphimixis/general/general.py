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

    @property
    def __dictstr__(self) -> dict:
        return {
            "arch": self.arch.value,
            "address": self.address,
            "auth": self.auth.__dict__,
        }


@dataclass
class Build:
    """Class with information about one build of project

    :var MachineInfo machine: Information about the machine.
    :var str build_path: Path to the directory with this build.
    :var str compiler_flags: Compiler flags for the build.
    """

    build_machine: MachineInfo
    run_machine: MachineInfo
    build_path: str
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
        """Insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

    @staticmethod
    @abstractmethod
    def insert_runner_flags(project: Project, build: Build, command: str) -> str:
        """Insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""

    @staticmethod
    @abstractmethod
    def insert_toolchain(build: Build) -> str:
        """Return flag that specify toolchain in build system call"""

    @staticmethod
    @abstractmethod
    def insert_sysroot(build: Build) -> str:
        """Return flag that specify sysroot in build system call"""


# pylint: disable=too-many-instance-attributes
@dataclass
class Toolchain:
    """Class that generalized idea of toolchain"""

    # SYSROOT
    sysroot: str

    # TOOLS: postfix "_t" means "tool"
    ar_t: str
    as_t: str
    ld_t: str
    nm_t: str
    objcopy_t: str
    objdump_t: str
    ranlib_t: str
    readelf_t: str
    strip_t: str

    # COMPILERS: with default flags
    c_compiler: str
    cxx_compiler: str
    csharp_compiler: str
    cuda_compiler: str
    objc_compiler: str
    objcxx_compiler: str
    fortran_compiler: str
    hip_compiler: str
    ispc_compiler: str
    swift_compiler: str
    asm_compiler: str
    asm_nasm_compiler: str
    asm_marmasm_compiler: str
    asm_masm_compiler: str
    asm_att_compiler: str

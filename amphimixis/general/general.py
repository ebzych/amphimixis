"""The common module that is used in most other modules"""

from abc import ABC, abstractmethod
from curses.ascii import isalpha
from dataclasses import dataclass
from enum import StrEnum


class Arch(StrEnum):
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

    @property
    def __dictstr__(self) -> dict[str, str]:
        ret = {"username": self.username}
        if self.password is not None:
            ret["password"] = self.password
        ret["port"] = str(self.port)
        return ret


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
        ret: dict[str, str | dict] = {"arch": self.arch.value}
        if self.address is not None:
            ret["address"] = self.address
        if self.auth is not None:
            ret["auth"] = self.auth.__dictstr__
        return ret


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
    def get_build_system_prompt(project: Project, build: Build) -> str:
        """Generate build system prompt with all specified flags"""

    @staticmethod
    @abstractmethod
    def get_runner_prompt(project: Project, build: Build) -> str:
        """Generate runner prompt"""


class CompilerFlags(StrEnum):
    """Enumeration for getting access to flags of concrete compiler"""

    C_FLAGS = "c_flags"
    CXX_FLAGS = "cxx_flags"
    CSHARP_FLAGS = "csharp_flags"
    CUDA_FLAGS = "cuda_flags"
    OBJC_FLAGS = "objc_flags"
    OBJCXX_FLAGS = "objcxx_flags"
    FORTRAN_FLAGS = "fortran_flags"
    HIP_FLAGS = "hip_flags"
    ISPC_FLAGS = "ispc_flags"
    SWIFT_FLAGS = "swift_flags"
    ASM_FLAGS = "asm_flags"
    ASM_NASM_FLAGS = "asm_nasm_flags"
    ASM_MARMASM_FLAGS = "asm_marmasm_flags"
    ASM_MASM_FLAGS = "asm_masm_flags"
    ASM_ATT_FLAGS = "asm_att_flags"


class ToolchainAttrs(StrEnum):
    """Constants for getting access to attributes from toolchain dictionary"""

    SYSROOT = "sysroot"

    # TOOLS: postfix "_t" means "tool"
    AR_T = "ar"
    AS_T = "as"
    LD_T = "ld"
    NM_T = "nm"
    OBJCOPY_T = "objcopy"
    OBJDUMP_T = "objdump"
    RANLIB_T = "ranlib"
    READELF_T = "readelf"
    STRIP_T = "strip"

    # COMPILERS
    C_COMPILER = "c_compiler"
    CXX_COMPILER = "cxx_compiler"
    CSHARP_COMPILER = "csharp_compiler"
    CUDA_COMPILER = "cuda_compiler"
    OBJC_COMPILER = "objc_compiler"
    OBJCXX_COMPILER = "objcxx_compiler"
    FORTRAN_COMPILER = "fortran_compiler"
    HIP_COMPILER = "hip_compiler"
    ISPC_COMPILER = "ispc_compiler"
    SWIFT_COMPILER = "swift_compiler"
    ASM_COMPILER = "asm_compiler"
    ASM_NASM_COMPILER = "asm_nasm_compiler"
    ASM_MARMASM_COMPILER = "asm_marmasm_compiler"
    ASM_MASM_COMPILER = "asm_masm_compiler"
    ASM_ATT_COMPILER = "asm_att_compiler"


class Toolchain:
    """Class that generalized idea of toolchain"""

    __tools: dict[ToolchainAttrs, str]  # attr -> [ /path/to/any | flags ]
    __name: str | None = None

    @property
    def name(self) -> str | None:
        """Name of toolchain getter"""
        return self.__name

    @name.setter
    def name(self, new_name: str) -> bool:
        """Name of toolchain setter"""
        if all(isalpha(ch) for ch in new_name):
            __name = new_name
            return True
        return False

    def get(self, attr: ToolchainAttrs) -> str | None:
        """Getter of toolchain attributes"""
        return self.__tools.get(attr)

    def set(self, attr: ToolchainAttrs, new_value: str) -> None:
        """Setter of toolchain attributes"""
        self.__tools[attr] = new_value

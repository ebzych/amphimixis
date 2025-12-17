"""The common module that is used in most other modules"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from os.path import isabs


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


# pylint: disable = too-many-instance-attributes
class CompilerFlagsAttrs(StrEnum):
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


# pylint: disable = too-many-instance-attributes
class ToolchainAttrs(StrEnum):
    """Constants for getting access to attributes from toolchain dictionary"""

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

    def __init__(self, name: str | None = None, sysroot: str | None = None):
        # attr -> [ /path/to/any | compiler_defualt_flags ]
        self.__attrs: dict[str, str] = {}
        self.__name = name
        self.sysroot = sysroot

    @property
    def name(self) -> str | None:
        """Name of toolchain getter"""
        return self.__name

    @property
    def sysroot(self) -> str | None:
        """Sysroot of toolchain getter"""
        return self.__sysroot

    @sysroot.setter
    def sysroot(self, new_path: None | str) -> None:
        """Sysroot of toolchain setter"""
        if new_path is None or isabs(new_path):
            self.__sysroot = new_path
        else:
            raise ValueError(
                f"Setting sysroot to toolchain error: path '{new_path}' is not absolute"
            )

    def get(self, attr: ToolchainAttrs | CompilerFlagsAttrs) -> str | None:
        """Getter of toolchain attributes"""
        return self.__attrs.get(attr.value)

    def set(self, attr: ToolchainAttrs | CompilerFlagsAttrs, new_value: str) -> None:
        """Setter of toolchain attributes

        :param ToolchainAttrs | CompilerFlagsAttrs attr: Tool / compiler / flags
            attribute of toolchain
        :param str new_value: absolute path to tool / compiler or flags of compiler
        """
        if isinstance(attr, ToolchainAttrs) and not isabs(new_value):
            raise ValueError(
                f"Setting {attr.value} to toolchain error: path '{new_value}' is not absolute"
            )
        self.__attrs[attr.value] = new_value

    @property
    def data(self) -> dict[str, str]:
        """Return dictionary with all tools"""
        return self.__attrs


class CompilerFlags:
    """Storing flags of compilers"""

    def __init__(self) -> None:
        self.__attrs: dict[CompilerFlagsAttrs, str] = {}  # attr -> compiler_flags

    def get(self, attr: CompilerFlagsAttrs) -> str | None:
        """Getter of compiler flags"""
        return self.__attrs.get(attr)

    def set(self, attr: CompilerFlagsAttrs, new_value: str) -> None:
        """Setter of compiler flags"""
        self.__attrs[attr] = new_value

    @property
    def data(self) -> dict[CompilerFlagsAttrs, str]:
        """Return dictionary with all tools"""
        return self.__attrs


@dataclass
class Build:
    """Class with information about one build of project

    :var MachineInfo build_machine: Information about the machine to build at
    :var MachineInfo run_machine: Information about the machine to profile at
    :var str build_name: Unique name of the build
    :var Toolchain | None toolchain: Toolchain used to building
    :var str | None sysroot: Path to sysroot or name of sysroot used to building
    :var list[str] executables: List of relative to `build path` paths to executables
    :var str compiler_flags: Compiler flags for the build
    """

    build_machine: MachineInfo
    run_machine: MachineInfo
    build_name: str
    executables: list[str]
    toolchain: Toolchain | None
    sysroot: str | None
    compiler_flags: CompilerFlags | None
    config_flags: None | str


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


# pylint: disable=too-few-public-methods
class IUI(ABC):
    """Interface for User Interface (UI) classes"""

    @abstractmethod
    def print(self, message: str) -> None:
        """Print message to user

        :param str message: Message to print to the user"""


class NullUI(IUI):
    """A UI implementation that does nothing (used to suppress output)"""

    def print(self, message: str) -> None:
        pass

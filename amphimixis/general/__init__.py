"""The common module that is used in most other modules"""

from amphimixis.general import constants
from amphimixis.general.general import (
    IUI,
    Arch,
    Build,
    CompilerFlags,
    CompilerFlagsAttrs,
    IBuildSystem,
    MachineAuthenticationInfo,
    MachineInfo,
    NullUI,
    Project,
    Toolchain,
    ToolchainAttrs,
)

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "Arch",
    "IBuildSystem",
    "MachineAuthenticationInfo",
    "constants",
    "MachineInfo",
    "MachineAuthenticationInfo",
    "IUI",
    "NullUI",
    "Toolchain",
    "ToolchainAttrs",
    "CompilerFlagsAttrs",
    "CompilerFlags",
]

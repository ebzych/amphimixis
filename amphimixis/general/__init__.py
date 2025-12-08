"""The common module that is used in most other modules"""

from amphimixis.general.colors import Colors
from amphimixis.general.general import (
    Arch,
    Build,
    CompilerFlags,
    IBuildSystem,
    MachineAuthenticationInfo,
    MachineInfo,
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
    "Colors",
    "MachineInfo",
    "MachineAuthenticationInfo",
    "Toolchain",
    "ToolchainAttrs",
    "CompilerFlags",
]

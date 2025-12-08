"""The common module that is used in most other modules"""

from amphimixis.general import constants
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
    "constants",
    "MachineInfo",
    "MachineAuthenticationInfo",
    "Toolchain",
    "ToolchainAttrs",
    "CompilerFlags",
]

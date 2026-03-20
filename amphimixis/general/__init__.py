"""The common module that is used in most other modules"""

from amphimixis.general import constants, tools
from amphimixis.general.general import (
    IUI,
    Arch,
    Build,
    CompilerFlags,
    CompilerFlagsAttrs,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
    BuildSystem,
    MachineAuthenticationInfo,
    MachineInfo,
    NullUI,
    ProfileStats,
    Project,
    ProjectStats,
    Toolchain,
    ToolchainAttrs,
)

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "Arch",
    "BuildSystem",
    "IHighLevelBuildSystem",
    "ILowLevelBuildSystem",
    "MachineAuthenticationInfo",
    "constants",
    "tools",
    "MachineInfo",
    "MachineAuthenticationInfo",
    "IUI",
    "NullUI",
    "Toolchain",
    "ToolchainAttrs",
    "CompilerFlagsAttrs",
    "CompilerFlags",
    "ProfileStats",
    "ProjectStats",
]

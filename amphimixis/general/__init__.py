"""The common module that is used in most other modules"""

from amphimixis.general import constants
from amphimixis.general.general import (
    IUI,
    Arch,
    Build,
    BuildSystem,
    CompilerFlags,
    CompilerFlagsAttrs,
    DummyBuildSystem,
    DummyRunner,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
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
    "BuildSystem",
    "IHighLevelBuildSystem",
    "ILowLevelBuildSystem",
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
    "DummyBuildSystem",
    "DummyRunner",
]

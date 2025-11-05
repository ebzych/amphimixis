"""The common module that is used in most other modules"""

from amphimixis.general.colors import (
    Colors,
)

from amphimixis.general.general import (
    Build,
    IBuildSystem,
    MachineAuthenticationInfo,
    MachineInfo,
    Project,
    Arch,
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
]

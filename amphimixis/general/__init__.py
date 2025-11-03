"""The common module that is used in most other modules"""

from amphimixis.general.colors import (
    Colors,
)

from amphimixis.general.general import (
    Project,
    Build,
    MachineInfo,
    IBuildSystem,
    MachineAuthenticationInfo,
    Arch,
    build_systems_dict,
)

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "IBuildSystem",
    "MachineAuthenticationInfo",
    "Arch",
    "build_systems_dict",
    "Colors",
]

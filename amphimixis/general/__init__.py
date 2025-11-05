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
)

from amphimixis.general.build_systems.cmake import CMake
from amphimixis.general.build_systems.make import Make
from amphimixis.general.build_systems.build_systems import build_systems_dict

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "IBuildSystem",
    "MachineAuthenticationInfo",
    "build_systems_dict",
    "Colors",
    "MachineInfo",
    "MachineAuthenticationInfo",
    "CMake",
    "Make",
]

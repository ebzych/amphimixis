"""The common module that is used in most other modules"""

from .colors import Colors
from .general import (
    Arch,
    Build,
    IBuildSystem,
    MachineAuthenticationInfo,
    MachineInfo,
    Project,
)

from .build_systems.cmake import CMake
from .build_systems.make import Make
from .build_systems.build_systems import build_systems_dict

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "IBuildSystem",
    "MachineAuthenticationInfo",
    "Arch",
    "build_systems_dict",
    "Colors",
    "MachineInfo",
    "MachineAuthenticationInfo",
    "CMake",
    "Make",
]

"""The common module that is used in most other modules"""

from .colors import (
    Colors,
)

from .general import (
    Project,
    Build,
    IBuildSystem,
)

from .build_systems_impl import build_systems_dict
from .architecture import Arch
from .machine import MachineAuthenticationInfo, MachineInfo

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
]

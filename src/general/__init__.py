"""The common module that is used in most other modules"""

<<<<<<< HEAD
from .general import (
    Project,
    Build,
    MachineInfo,
    IBuildSystem,
    MachineAuthenticationInfo,
    Arch,
)

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "IBuildSystem",
    "MachineAuthenticationInfo",
    "Arch",
]
=======
from .general import Project, Build, RemoteMachine, IBuildSystem
>>>>>>> 4b26d41 (refactor: using dataclasses and add class for remote machine)

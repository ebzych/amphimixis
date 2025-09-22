"""The common module that is used in most other modules"""

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 7ccc1f6 (refactor: renamed RemoteMachine into MachineInfo and add class for authentication info)
from .general import (
    Project,
    Build,
    MachineInfo,
    IBuildSystem,
    MachineAuthenticationInfo,
<<<<<<< HEAD
<<<<<<< HEAD
    Arch,
=======
>>>>>>> 7ccc1f6 (refactor: renamed RemoteMachine into MachineInfo and add class for authentication info)
=======
    Arch,
>>>>>>> b9853d6 (refactor: update Arch class to use string values)
)

__all__ = [
    "Project",
    "Build",
    "MachineInfo",
    "IBuildSystem",
    "MachineAuthenticationInfo",
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b9853d6 (refactor: update Arch class to use string values)
    "Arch",
]
=======
from .general import Project, Build, RemoteMachine, IBuildSystem
>>>>>>> 4b26d41 (refactor: using dataclasses and add class for remote machine)
=======
]
>>>>>>> 7ccc1f6 (refactor: renamed RemoteMachine into MachineInfo and add class for authentication info)

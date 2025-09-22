"""The common module that is used in most other modules"""

from abc import ABC, abstractmethod
from .build_system_interface import IBuildSystem


class IArch(ABC):
    """Interface for classes implementing interaction with arch of project build
    which specify compiler and sysroot"""

    @staticmethod
    @abstractmethod
    def compiler() -> str:
        """The getter of path to compiler"""

    @staticmethod
    @abstractmethod
    def sysroot() -> str:
        """The getter of path to sysroot"""


class Build:
    """Class with information about one build of project"""

    def __init__(
        self,
        # directory { dir:builded_project, file:config.json, file:build.log, ... }
        arch: IArch,
        #   and False if script is simple: configuration -> build
        build_system: IBuildSystem,  # is high-level build system
        runner: IBuildSystem,  # is low-level build system
        build_path: str,  # path to directory with this build;
        is_specified_script: bool = False,  # True if user specify build script
        specified_script: str = "",
        config_flags: str = "",
        compiler_flags: str = "",
    ):
        self.build_path = build_path
        self.arch = arch
        self.is_specified_script = is_specified_script
        self.specified_script = specified_script
        self.build_system = build_system
        self.config_flags = config_flags
        self.compiler_flags = compiler_flags
        self.runner = runner


class Project:
    """Class with information about project and his builds"""

    def __init__(self, repo_path: str, builds: list[Build]):
        self.path = repo_path
        self.builds = builds

"""The common module that is used in most other modules"""

from abc import ABC, abstractmethod


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


class IBuildSystem(ABC):
    """Interface for classes implementing interaction with build system"""

    @staticmethod
    @abstractmethod
    def insert_config_flags(build, command: str):  # type of "build" is Build
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags"""

    @staticmethod
    @abstractmethod
    def insert_runner_flags(build, command: str):  # type of "build" is Build
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags"""


class Build:
    """Class with information about one build of project"""

    def __init__(
        self,
        build_path: str,  # path to directory with this build;
        # directory { dir:builded_project, file:config.json, file:build.log, ... }
        arch: IArch,
        is_specified_script: bool,  # True if user specify build script
        #   and False if script is simple: configuration -> build
        specified_script: str,
        build_system: IBuildSystem,  # is high-level build system
        config_flags: str,
        compiler_flags: str,
        runner: IBuildSystem,  # is low-level build system
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

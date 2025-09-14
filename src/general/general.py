import os
from enum import Enum


class Arch(Enum):
    """Supported architectures"""

    X86 = 0
    RISCV = 1
    ARM = 2


class BuildSystem(Enum):
    """Supported build systems"""

    MAKE = 0
    CMAKE = 1
    NINJA = 2


class Build:
    """Class with information about one build of project"""

    def __init__(
        self,
        build_path: str,
        # path to directory with this build;
        # directory { dir:builded_project, file:config.json, file:build.log, ... }
        arch: Arch,
        is_specified_script: bool,
        # True if user specify build script
        #               and False if script is simple: configuration -> build
        build_system: BuildSystem,  # is high-level build system
        config_flags: str,
        cxx_flags: str,
        c_flags: str,
        runner: BuildSystem,
    ):  # is low-level build system
        self.build_path = build_path
        self.arch = arch
        self.is_specified_script = is_specified_script
        self.build_system = build_system
        self.config_flags = config_flags
        self.cxx_flags = cxx_flags
        self.c_flags = c_flags
        self.runner = runner


class Project:
    """Class with information about project and his builds"""

    def __init__(self, repo_path: str, builds: list[Build]):
        self.path = repo_path
        self.builds = builds

import os
<<<<<<< HEAD


class Project:
    def __init__(self, repo_path: str, builds_path: str = "build/"):
        self.path = repo_path
        self.builds_path = os.path.join(repo_path, builds_path)
        self.build_system = "cmake"
        self.targets = []
=======
from enum import Enum


"""Supported architectures"""
class Arch(Enum):
    X86 = 0
    RISCV = 1
    ARM = 2

"""Supported build systems"""
class BuildSystem(Enum):
    MAKE = 0
    CMAKE = 1
    NINJA = 2

class Build:
    def __init__(self, build_path   : str,
                 arch               : Arch,
                 build_system       : BuildSystem,              # is high-level build system
                 runner             : BuildSystem):             # is low-level build system
        self.build_path = build_path
        self.arch = arch
        self.build_system = build_system
        self.runner = runner

class Project:
    def __init__(self, repo_path: str,
                 builds : list[Build]):
        self.path = repo_path
        self.builds = []
>>>>>>> c5d5dcf (refactor: add Build class, Arch and BuildSystem enums, edit Project class fields: list[Build] instead str /path/to/builds)

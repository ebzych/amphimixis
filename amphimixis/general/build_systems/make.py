"Make IBuildSystem implementation"

# pylint: disable=relative-beyond-top-level
from ..general import Build, IBuildSystem, Project


class Make(IBuildSystem):
    """The Make implementation of IBuildSystem"""

    @staticmethod
    def insert_config_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of build system
        or return string with command which run build system with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${config_flags}'
        else return string 'command' with 'config_flags' inserted"""

        raise NotImplementedError

    @staticmethod
    # pylint: disable=unused-argument
    def insert_runner_flags(project: Project, build: Build, command: str) -> str:
        """Method insert flags in 'command' in line with call of runner
        or return string with command which run runner with inserted flags
        If 'command' is empty then return string in the format '${BuildSystem} ${runner_flags}'
        else return string 'command' with 'runner_flags' inserted"""

        if command != "":
            raise NotImplementedError

        return "make -j"

    @staticmethod
    def insert_toolchain(build: Build) -> str:
        """Return flag that specify toolchain in build system call"""
        raise NotImplementedError

    @staticmethod
    def insert_sysroot(build: Build) -> str:
        """Return flag that specify sysroot in build system call"""
        raise NotImplementedError

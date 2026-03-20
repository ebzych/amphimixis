"Make IBuildSystem implementation"

import os

from amphimixis.general import (
    Build,
    BuildSystem,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
    Project,
)
from amphimixis.shell import Shell


class Make(BuildSystem, IHighLevelBuildSystem, ILowLevelBuildSystem):
    """The Make implementation of IBuildSystem"""

    def build(self, build: Build) -> tuple[int, list[str], list[str]]:
        """Build via build system"""
        raise NotImplementedError

    # pylint: disable=unused-argument
    def run_building(self, build: Build) -> tuple[int, list[str], list[str]]:
        """Run building via build system"""
        shell = Shell(build.build_machine).connect()
        err, stdout, _ = shell.run("nproc")
        nproc = int(stdout[0][0])

        prompt = "make"
        if err == 0:
            if nproc > 1:
                nproc -= 1  # to prevent OM
            prompt += " -j" + str(nproc)

        return (0, [], [])

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))

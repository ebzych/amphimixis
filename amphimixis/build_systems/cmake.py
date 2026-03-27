"CMake IBuildSystem implementation"

import os

from amphimixis import logger
from amphimixis.build_systems.make import Make
from amphimixis.build_systems.ninja import Ninja
from amphimixis.general.general import (
    Build,
    BuildSystem,
    CompilerFlags,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
    Toolchain,
)
from amphimixis.shell import Shell

_logger = logger.setup_logger("CMAKE")


class CMake(BuildSystem, IHighLevelBuildSystem):
    """CMake implementation of IBuildSystem"""

    _generator_names_map: dict[type[ILowLevelBuildSystem], str] = {
        Make: '"Unix Makefiles"',
        Ninja: "Ninja",
    }

    def _generate_lang_flags(self, flags: CompilerFlags):
        ret_flags = []
        for flag, value in flags.data.items():
            ret_flags.append(f"-DCMAKE_{flag.upper()}='{value}'")
        return " ".join(ret_flags)

    def _generate_toolchain_flags(self, toolchain: Toolchain):
        ret_flags = []
        for tool, value in toolchain.data.items():
            ret_flags.append(f"-DCMAKE_{tool.upper()}='{value}'")
        return " ".join(ret_flags)

    def build(self, build: Build) -> tuple[int, str, str]:
        """Generate build system prompt with all specified flags"""
        shell = Shell(self._project, build.build_machine, self._ui).connect()

        build_path = os.path.join(shell.get_project_workdir(), build.build_name)
        cmakelists_dir = os.path.join(
            shell.get_source_dir(),
            self.find_relative_path("CMakeLists.txt"),
        )
        command = (
            f"cmake -G {self._generator_names_map[type(self.runner)]} "
            f"-B {build_path} -S {cmakelists_dir} "
        )
        if build.config_flags is not None:
            command += f"{build.config_flags} "
        if build.compiler_flags is not None:
            command += f"{self._generate_lang_flags(build.compiler_flags)} "
        if build.toolchain is not None:
            if build.toolchain.sysroot is not None:
                command += f"-DCMAKE_SYSROOT={build.toolchain.sysroot} "
            command += f"{self._generate_toolchain_flags(build.toolchain)} "

        err, stdout, stderr = shell.run(f"cd {cmakelists_dir}")
        if err != 0:
            return (err, "".join(stdout[0]), "".join(stderr[0]))

        _logger.info(
            "Run building with '%s' and 'cmake --build %s'", command, build_path
        )
        err, stdout, stderr = shell.run(command, f"cmake --build {build_path}")
        if len(stdout) > 1:
            stdout[0].extend(stdout[1])
            stderr[0].extend(stderr[1])

        return (err, "".join(stdout[0]), "".join(stderr[0]))

    def _normbase(self, path: str) -> str:
        return os.path.basename(os.path.normpath(path))

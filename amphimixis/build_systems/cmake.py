"CMake IBuildSystem implementation"

import os
import queue

from amphimixis import logger
from amphimixis.general.general import (
    Build,
    CompilerFlags,
    IBuildSystem,
    Project,
    Toolchain,
)

_logger = logger.setup_logger("CMAKE")


class CMake(IBuildSystem):
    """CMake implementation of IBuildSystem"""

    @staticmethod
    def find_cmakelists_path(proj_path: str, max_depth: int = 3) -> str:
        """Find first CMakeLists.txt file relative to project root.

        :param str proj_path: Path to project root
        :param int max_depth: Max depth of search
        :rtype: str
        :return: Path to CMakeLists.txt relative to project root
        """
        q_dirs: queue.Queue[tuple[str, int]] = queue.Queue()
        q_dirs.put((proj_path, 0))
        while not q_dirs.empty():
            curr_dir = q_dirs.get()
            if curr_dir[1] >= max_depth:
                continue
            if os.path.exists(os.path.join(curr_dir[0], "CMakeLists.txt")):
                return curr_dir[0]
            for el in os.scandir(curr_dir[0]):
                if el.is_dir():
                    q_dirs.put((el.path, curr_dir[1] + 1))

        raise FileNotFoundError("Can't find CMakeLists.txt")

    @staticmethod
    def _flags_generate(flags: CompilerFlags):
        ret_flags = []
        for flag, value in flags.data.items():
            ret_flags.append(f"-DCMAKE_{flag.upper()}={value}")
        return " ".join(ret_flags)

    @staticmethod
    def _toolchain_generate(toolchain: Toolchain):
        ret_flags = []
        for tool, value in toolchain.data.items():
            ret_flags.append(f"-DCMAKE_{tool.upper()}={value}")
        return " ".join(ret_flags)

    @staticmethod
    def get_build_system_prompt(project: Project, build: Build) -> str:
        """Generate build system prompt with all specified flags"""
        if build.build_machine.address is None:
            cmake_lists_path = os.path.normpath(project.path)
        else:
            cmake_lists_path = f"~/amphimixis/{CMake._normbase(project.path)}"

        try:
            cmake_lists_path += CMake.find_cmakelists_path(project.path)[
                len(os.path.normpath(project.path)) :
            ]
        except FileNotFoundError:
            _logger.error("CMakeLists.txt not found")

        command = f"cmake {cmake_lists_path} "

        if build.config_flags is not None:
            command += f"{build.config_flags} "

        if build.compiler_flags is not None:
            command += f"{CMake._flags_generate(build.compiler_flags)} "

        if build.toolchain is not None:
            if build.toolchain.sysroot is not None:
                command += f"-DCMAKE_SYSROOT={build.toolchain.sysroot} "
            command += f"{CMake._toolchain_generate(build.toolchain)} "

        # if cross-compiling -- add cmake mandatory variable for cross-compiling
        if build.build_machine.address != build.run_machine.address:
            command += "-DCMAKE_SYSTEM_NAME=Linux "

        return command

    @staticmethod
    def get_runner_prompt(project: Project, build: Build) -> str:
        """Generate runner prompt"""

        raise NotImplementedError

    @staticmethod
    def _normbase(path: str) -> str:
        return os.path.basename(os.path.normpath(path))

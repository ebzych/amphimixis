import subprocess
from pathlib import Path

import pytest
import pytest_mock

from amphimixis import Builder
from amphimixis.build_systems import build_systems_dict
from amphimixis.general import (
    Arch,
    Build,
    CompilerFlags,
    CompilerFlagsAttrs,
    MachineInfo,
    Project,
    Toolchain,
    ToolchainAttrs,
)

PROGRAM_NAME = "program"

GCC = Path("/bin/gcc")
SYSROOT = Path("/")

C_PROGRAM_SOURCE = "main.c"
SIMPLE_C_SUCCESSFULL_PROGRAM = "int main() { return 0; }"
SIMPLE_C_FAILED_PROGRAM = "int main() { return 1; }"

CMAKELISTS = "CMakeLists.txt"
SIMPLE_CMAKELISTS = "cmake_minimum_required(VERSION 3.10)\nproject(program)\nadd_executable(program main.c)"


@pytest.fixture
def proj_path(tmp_path: Path) -> Path:
    path = tmp_path / "proj_path"
    path.mkdir()
    return path


@pytest.fixture
def get_toolchain(
    t_attr: None | ToolchainAttrs = None,
    compiler: None | Path = None,
    f_attr: None | CompilerFlagsAttrs = None,
    flags: None | str = None,
    sysroot: None | str = None,
) -> None | Toolchain:
    toolchain = Toolchain(None, sysroot)
    if t_attr is not None and compiler is not None:
        toolchain.set(t_attr, str(compiler))
    if f_attr is not None and flags is not None:
        toolchain.set(f_attr, flags)
    if toolchain.data == {}:
        return None
    else:
        return toolchain


@pytest.fixture
def get_flags(
    f_attr: None | CompilerFlagsAttrs = None,
    flags: None | str = None,
) -> None | CompilerFlags:
    comp_flags = CompilerFlags()
    if f_attr is not None and flags is not None:
        comp_flags.set(f_attr, flags)
    if comp_flags.data == {}:
        return None
    else:
        return comp_flags


@pytest.fixture
def get_proj(
    _proj_path,
    toolchain: None | Toolchain,
    compiler_flags: None | CompilerFlags,
    config_flags: None | str,
    sysroot: None | str,
    build_system: str,
    runner: str,
) -> Project:
    return Project(
        str(_proj_path),
        [
            Build(
                MachineInfo(Arch.X86, None, None),
                MachineInfo(Arch.X86, None, None),
                "test_build",
                [str(_proj_path / "build" / PROGRAM_NAME)],
                toolchain,
                sysroot,
                compiler_flags,
                config_flags,
            )
        ],
        build_systems_dict[build_system],
        build_systems_dict[runner],
    )


@pytest.fixture
def get_builder(mocker: pytest_mock.MockerFixture):
    def _builder(path: Path) -> Builder:
        workdir_path_mock = mocker.Mock()
        workdir_path_mock.return_value = str(path)
        mocker.patch("amphimixis.Shell.get_project_workdir", workdir_path_mock)
        return Builder()

    return _builder


@pytest.fixture
def set_testing_environment():
    def _set_env(
        proj_path: Path,
        program_source: str,
        config_name: str,
        program_code: str,
        config: str,
    ):
        program = proj_path / program_source
        config_file = proj_path / config_name
        program.touch()
        config_file.touch()
        with program.open("w") as file:
            file.write(program_code)
        with config_file.open("w") as file:
            file.write(config)

    return _set_env


@pytest.mark.unit
class TestBuilder:
    @pytest.mark.parametrize(
        "toolchain, sysroot, compiler_flags, config_flags, build_system, runner",
        [None, None, None, None, "cmake", "make"],
    )
    @pytest.mark.parametrize(
        "program, expected",
        [(SIMPLE_C_SUCCESSFULL_PROGRAM, True), (SIMPLE_C_FAILED_PROGRAM, False)],
    )
    def test_simple_build(
        self,
        proj_path: Path,
        get_builder,
        set_testing_environment,
        get_proj,
        toolchain,
        sysroot,
        compiler_flags,
        config_flags,
        build_system,
        runner,
    ):
        builder: Builder = get_builder(proj_path)
        proj: Project = get_proj(
            proj_path,
            toolchain,
            sysroot,
            compiler_flags,
            config_flags,
            build_system,
            runner,
        )
        set_testing_environment()
        builder.build(proj)
        assert Path(proj.builds[0].executables[0]).exists(), "Build failed"

    # @pytest.mark.parametrize(
    #     "toolchain, sysroot, compiler_flags, config_flags, build_system, runner",
    #     [
    #         get_toolchain(
    #             ToolchainAttrs.C_COMPILER, GCC, CompilerFlagsAttrs.C_FLAGS, "", SYSROOT
    #         ),
    #         SYSROOT,
    #         get_flags(CompilerFlagsAttrs.C_FLAGS, ""),
    #         None,
    #     ],
    # )

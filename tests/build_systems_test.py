"""Tests for build systems: CMake, Make, Ninja, Meson, Autoconf, Bazel, Gmake, Yacc, Bison

This test suite validates:
- Flag generation (compiler flags, toolchain options)
- Command structure for each build system
- Sysroot handling
- Parallel build support
- Config flags passing
- Integration between high-level and low-level build systems
"""

from unittest.mock import MagicMock, patch

import pytest

from amphimixis.build_systems.autoconf import Autoconf
from amphimixis.build_systems.bazel import Bazel
from amphimixis.build_systems.bison import Bison
from amphimixis.build_systems.cmake import CMake
from amphimixis.build_systems.gmake import Gmake
from amphimixis.build_systems.make import Make
from amphimixis.build_systems.meson import Meson
from amphimixis.build_systems.ninja import Ninja
from amphimixis.build_systems.yacc import Yacc
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


@pytest.fixture
def local_machine():
    return MachineInfo(Arch.X86, None, None)


@pytest.fixture
def remote_machine():
    return MachineInfo(Arch.X86, "192.168.1.100", None)


@pytest.fixture
def mock_project(tmp_path):
    return Project(path=str(tmp_path))


@pytest.fixture
def mock_shell():
    shell_mock = MagicMock()
    shell_mock.get_project_workdir.return_value = "/mock/builds/project_build"
    shell_mock.get_source_dir.return_value = "/mock/source"
    shell_mock.connect.return_value = shell_mock
    shell_mock.run.return_value = (0, [["4"]], [[""]])
    return shell_mock


@pytest.mark.unit
class TestMake:
    """Tests for Make build system"""

    @pytest.fixture
    def make_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.make.Shell", return_value=mock_shell):
            make = Make(mock_project)
            yield make

    @pytest.mark.parametrize(
        "flag_attr,flag_value,expected_flag",
        [
            (CompilerFlagsAttrs.C_FLAGS, "-O2", "CFLAGS='-O2'"),
            (CompilerFlagsAttrs.CXX_FLAGS, "-Wall", "CXXFLAGS='-Wall'"),
            (
                CompilerFlagsAttrs.FORTRAN_FLAGS,
                "-ffast-math",
                "FORTRANFLAGS='-ffast-math'",
            ),
        ],
    )
    def test_generate_lang_flags(
        self, make_system, flag_attr, flag_value, expected_flag
    ):
        compiler_flags = CompilerFlags()
        compiler_flags.set(flag_attr, flag_value)
        result = make_system._generate_lang_flags(compiler_flags)
        assert expected_flag in result

    @pytest.mark.parametrize(
        "tool_attr,expected_tool",
        [
            (ToolchainAttrs.C_COMPILER, "CC"),
            (ToolchainAttrs.CXX_COMPILER, "CXX"),
            (ToolchainAttrs.AR_T, "AR"),
            (ToolchainAttrs.LD_T, "LD"),
        ],
    )
    def test_toolchain_attrs_map(self, make_system, tool_attr, expected_tool):
        result = make_system._toolchain_attrs_map(tool_attr.value)
        assert result == expected_tool

    def test_generate_toolchain_flags(self, make_system):
        toolchain = Toolchain()
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")
        toolchain.set(ToolchainAttrs.CXX_COMPILER, "/usr/bin/g++")
        result = make_system._generate_toolchain_flags(toolchain)
        assert "CC='/usr/bin/gcc'" in result
        assert "CXX='/usr/bin/g++'" in result

    def test_sysroot_handling(self, mock_project, mock_shell):
        sysroot = "/sysroot"
        toolchain = Toolchain(sysroot=sysroot)
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=[],
            toolchain=toolchain,
            sysroot=sysroot,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.make.Shell", return_value=mock_shell):
            make = Make(mock_project)
            make._build_install_clean(build, configure=True)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "SYSROOT=/sysroot" in combined_output

    def test_parallel_build(self, mock_project, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.make.Shell", return_value=mock_shell):
            make = Make(mock_project)
            make._build_install_clean(build, configure=False)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-j" in combined_output

    def test_warning_on_build(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.make.Shell", return_value=mock_shell):
            make = Make(mock_project)
            make._ui = MagicMock()
            make.build(
                Build(
                    build_machine=MachineInfo(Arch.X86, None, None),
                    run_machine=MachineInfo(Arch.X86, None, None),
                    build_name="test",
                    executables=[],
                    toolchain=None,
                    sysroot=None,
                    compiler_flags=None,
                    config_flags=None,
                )
            )
            assert make._ui.print_warning.call_count == 1


@pytest.mark.unit
class TestCMake:
    """Tests for CMake build system"""

    @pytest.fixture
    def cmake_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.cmake.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            cmake = CMake(mock_project, runner=ninja_runner)
            yield cmake

    @pytest.mark.parametrize(
        "flag_attr,flag_value,expected_flag",
        [
            (CompilerFlagsAttrs.C_FLAGS, "-O2", "-DCMAKE_C_FLAGS='-O2'"),
            (CompilerFlagsAttrs.CXX_FLAGS, "-Wall", "-DCMAKE_CXX_FLAGS='-Wall'"),
            (
                CompilerFlagsAttrs.CUDA_FLAGS,
                "-arch=sm_80",
                "-DCMAKE_CUDA_FLAGS='-arch=sm_80'",
            ),
        ],
    )
    def test_generate_lang_flags(
        self, cmake_system, flag_attr, flag_value, expected_flag
    ):
        compiler_flags = CompilerFlags()
        compiler_flags.set(flag_attr, flag_value)
        result = cmake_system._generate_lang_flags(compiler_flags)
        assert expected_flag in result

    @pytest.mark.parametrize(
        "tool_attr,tool_value,expected_flag",
        [
            (
                ToolchainAttrs.C_COMPILER,
                "/usr/bin/gcc",
                "-DCMAKE_C_COMPILER='/usr/bin/gcc'",
            ),
            (
                ToolchainAttrs.CXX_COMPILER,
                "/usr/bin/g++",
                "-DCMAKE_CXX_COMPILER='/usr/bin/g++'",
            ),
            (ToolchainAttrs.AR_T, "/usr/bin/ar", "-DCMAKE_AR='/usr/bin/ar'"),
        ],
    )
    def test_generate_toolchain_flags(
        self, cmake_system, tool_attr, tool_value, expected_flag
    ):
        toolchain = Toolchain()
        toolchain.set(tool_attr, tool_value)
        result = cmake_system._generate_toolchain_flags(toolchain)
        assert expected_flag in result

    def test_sysroot_in_command(self, mock_project, mock_shell):
        sysroot = "/sysroot"
        toolchain = Toolchain(sysroot=sysroot)
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="cmake_build",
            executables=[],
            toolchain=toolchain,
            sysroot=sysroot,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.cmake.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            cmake = CMake(mock_project, runner=ninja_runner)
            cmake.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-DCMAKE_SYSROOT=/sysroot" in combined_output

    def test_generator_selection_ninja(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.cmake.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            cmake = CMake(mock_project, runner=ninja_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            cmake.build(build)

            calls = [str(call) for call in mock_shell.run.call_args_list]
            combined_output = " ".join(calls)
            assert "Ninja" in combined_output

    def test_generator_selection_make(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.cmake.Shell", return_value=mock_shell):
            make_runner = Make(mock_project)
            cmake = CMake(mock_project, runner=make_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            cmake.build(build)

            calls = [str(call) for call in mock_shell.run.call_args_list]
            combined_output = " ".join(calls)
            assert "Unix Makefiles" in combined_output

    def test_config_flags_passed(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.cmake.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            cmake = CMake(mock_project, runner=ninja_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="-DCMAKE_BUILD_TYPE=Release",
            )
            cmake.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "CMAKE_BUILD_TYPE=Release" in combined_output

    def test_build_command_structure(self, cmake_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        cmake_system.build(build)

        cmake_call_found = False
        for call in mock_shell.run.call_args_list:
            call_str = str(call)
            if "cmake" in call_str and "-G" in call_str:
                cmake_call_found = True
                break

        assert cmake_call_found, "cmake command with -G generator not found"

    def test_cmake_and_build_steps(self, cmake_system, mock_shell):
        mock_shell.run.side_effect = [
            (0, [["Configuring..."]], [[""]]),
            (0, [["Building..."]], [[""]]),
        ]

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        cmake_system.build(build)

        assert mock_shell.run.call_count >= 2


@pytest.mark.unit
class TestBuildSystemIntegration:
    """Integration tests for build system command generation"""

    def test_toolchain_and_flags_combined(self, mock_project, mock_shell):
        toolchain = Toolchain()
        toolchain.set(ToolchainAttrs.C_COMPILER, "/custom/gcc")
        toolchain.set(ToolchainAttrs.CXX_COMPILER, "/custom/g++")

        compiler_flags = CompilerFlags()
        compiler_flags.set(CompilerFlagsAttrs.C_FLAGS, "-O3")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=toolchain,
            sysroot=None,
            compiler_flags=compiler_flags,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.make.Shell", return_value=mock_shell):
            make = Make(mock_project)
            make._build_install_clean(build, configure=True)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "/custom/gcc" in combined_output
        assert "/custom/g++" in combined_output
        assert "-O3" in combined_output


@pytest.mark.unit
class TestMeson:
    """Tests for Meson build system"""

    @pytest.fixture
    def meson_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.meson.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            meson = Meson(mock_project, runner=ninja_runner)
            yield meson

    @pytest.mark.parametrize(
        "flag_attr,flag_value,expected_flag",
        [
            (CompilerFlagsAttrs.C_FLAGS, "-O2", "-Dc_args='-O2'"),
            (CompilerFlagsAttrs.CXX_FLAGS, "-Wall", "-Dcpp_args='-Wall'"),
            (CompilerFlagsAttrs.ASM_FLAGS, "-fasm", "-Dasm_args='-fasm'"),
        ],
    )
    def test_generate_lang_flags(
        self, meson_system, flag_attr, flag_value, expected_flag
    ):
        compiler_flags = CompilerFlags()
        compiler_flags.set(flag_attr, flag_value)
        result = meson_system._generate_lang_flags(compiler_flags)
        assert expected_flag in result

    @pytest.mark.parametrize(
        "tool_attr,tool_value,expected_flag",
        [
            (ToolchainAttrs.C_COMPILER, "/usr/bin/gcc", "-Dcb=/usr/bin/gcc"),
            (ToolchainAttrs.CXX_COMPILER, "/usr/bin/g++", "-Dcpp=/usr/bin/g++"),
            (ToolchainAttrs.AR_T, "/usr/bin/ar", "-Dar=/usr/bin/ar"),
        ],
    )
    def test_generate_toolchain_options(
        self, meson_system, tool_attr, tool_value, expected_flag
    ):
        toolchain = Toolchain()
        toolchain.set(tool_attr, tool_value)
        result = meson_system._generate_toolchain_options(toolchain)
        assert expected_flag in result

    def test_sysroot_in_command(self, mock_project, mock_shell):
        sysroot = "/sysroot"
        toolchain = Toolchain(sysroot=sysroot)
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="meson_build",
            executables=[],
            toolchain=toolchain,
            sysroot=sysroot,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.meson.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            meson = Meson(mock_project, runner=ninja_runner)
            meson.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "--wipe" in combined_output or "--reconfigure" in combined_output

    def test_config_flags_passed(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.meson.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            meson = Meson(mock_project, runner=ninja_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="-Dbuildtype=release",
            )
            meson.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "buildtype=release" in combined_output

    def test_build_command_structure(self, meson_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        meson_system.build(build)

        meson_setup_call_found = False
        for call in mock_shell.run.call_args_list:
            call_str = str(call)
            if "meson" in call_str and "setup" in call_str:
                meson_setup_call_found = True
                break

        assert meson_setup_call_found, "meson setup command not found"

    def test_meson_compile_step(self, meson_system, mock_shell):
        mock_shell.run.side_effect = [
            (0, [["Setting up..."]], [[""]]),
            (0, [["Compiling..."]], [[""]]),
        ]

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        meson_system.build(build)

        assert mock_shell.run.call_count >= 2

    def test_connect_called(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.meson.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            meson = Meson(mock_project, runner=ninja_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            meson.build(build)

            mock_shell.connect.assert_called()

    def test_multiple_flags_combined(self, meson_system, mock_shell):
        compiler_flags = CompilerFlags()
        compiler_flags.set(CompilerFlagsAttrs.C_FLAGS, "-O2")
        compiler_flags.set(CompilerFlagsAttrs.CXX_FLAGS, "-Wall -Wextra")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=compiler_flags,
            config_flags=None,
        )

        meson_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-O2" in combined_output
        assert "-Wall" in combined_output


@pytest.mark.unit
class TestAutoconf:
    """Tests for Autoconf build system"""

    @pytest.fixture
    def autoconf_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.autoconf.Shell", return_value=mock_shell):
            make_runner = Make(mock_project)
            autoconf = Autoconf(mock_project, runner=make_runner)
            yield autoconf

    @pytest.mark.parametrize(
        "flag_attr,flag_value,expected_flag",
        [
            (CompilerFlagsAttrs.C_FLAGS, "-O2", "CFLAGS='-O2'"),
            (CompilerFlagsAttrs.CXX_FLAGS, "-Wall", "CXXFLAGS='-Wall'"),
            (CompilerFlagsAttrs.FORTRAN_FLAGS, "-ffast-math", "FFLAGS='-ffast-math'"),
        ],
    )
    def test_generate_lang_flags(
        self, autoconf_system, flag_attr, flag_value, expected_flag
    ):
        compiler_flags = CompilerFlags()
        compiler_flags.set(flag_attr, flag_value)
        result = autoconf_system._generate_lang_flags(compiler_flags)
        assert expected_flag in result

    @pytest.mark.parametrize(
        "tool_attr,tool_value,expected_flag",
        [
            (ToolchainAttrs.C_COMPILER, "/usr/bin/gcc", "CC='/usr/bin/gcc'"),
            (ToolchainAttrs.CXX_COMPILER, "/usr/bin/g++", "CXX='/usr/bin/g++'"),
            (ToolchainAttrs.AR_T, "/usr/bin/ar", "AR='/usr/bin/ar'"),
        ],
    )
    def test_generate_toolchain_flags(
        self, autoconf_system, tool_attr, tool_value, expected_flag
    ):
        toolchain = Toolchain()
        toolchain.set(tool_attr, tool_value)
        result = autoconf_system._generate_toolchain_flags(toolchain)
        assert expected_flag in result

    def test_sysroot_in_command(self, mock_project, mock_shell):
        sysroot = "/sysroot"
        toolchain = Toolchain(sysroot=sysroot)
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="autoconf_build",
            executables=[],
            toolchain=toolchain,
            sysroot=sysroot,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.autoconf.Shell", return_value=mock_shell):
            make_runner = Make(mock_project)
            autoconf = Autoconf(mock_project, runner=make_runner)
            autoconf.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "CPPFLAGS=" in combined_output or "LDFLAGS=" in combined_output

    def test_config_flags_passed(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.autoconf.Shell", return_value=mock_shell):
            make_runner = Make(mock_project)
            autoconf = Autoconf(mock_project, runner=make_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="--prefix=/usr/local",
            )
            autoconf.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "--prefix=/usr/local" in combined_output

    def test_build_command_structure(self, autoconf_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        autoconf_system.build(build)

        configure_call_found = False
        for call in mock_shell.run.call_args_list:
            call_str = str(call)
            if "./configure" in call_str:
                configure_call_found = True
                break

        assert configure_call_found, "./configure command not found"

    def test_configure_and_make_steps(self, autoconf_system, mock_shell):
        mock_shell.run.side_effect = [
            (0, [[""]], [[""]]),
            (0, [["Configuring..."]], [[""]]),
            (0, [["4"]], [[""]]),
            (0, [["Building..."]], [[""]]),
        ]

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        autoconf_system.build(build)

        assert mock_shell.run.call_count >= 4

    def test_connect_called(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.autoconf.Shell", return_value=mock_shell):
            make_runner = Make(mock_project)
            autoconf = Autoconf(mock_project, runner=make_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            autoconf.build(build)

            mock_shell.connect.assert_called()

    def test_parallel_make(self, autoconf_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        autoconf_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-j" in combined_output

    def test_multiple_flags_combined(self, autoconf_system, mock_shell):
        compiler_flags = CompilerFlags()
        compiler_flags.set(CompilerFlagsAttrs.C_FLAGS, "-O2")
        compiler_flags.set(CompilerFlagsAttrs.CXX_FLAGS, "-Wall -Wextra")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=compiler_flags,
            config_flags=None,
        )

        autoconf_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-O2" in combined_output
        assert "-Wall" in combined_output

    def test_toolchain_and_flags_combined(self, autoconf_system, mock_shell):
        toolchain = Toolchain()
        toolchain.set(ToolchainAttrs.C_COMPILER, "/custom/gcc")
        toolchain.set(ToolchainAttrs.CXX_COMPILER, "/custom/g++")

        compiler_flags = CompilerFlags()
        compiler_flags.set(CompilerFlagsAttrs.C_FLAGS, "-O3")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=toolchain,
            sysroot=None,
            compiler_flags=compiler_flags,
            config_flags=None,
        )

        autoconf_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "/custom/gcc" in combined_output
        assert "/custom/g++" in combined_output
        assert "-O3" in combined_output


@pytest.mark.unit
class TestMesonAutoconfIntegration:
    """Integration tests for Meson and Autoconf"""

    @pytest.mark.parametrize(
        "build_system_class,runner_class",
        [
            (Meson, Ninja),
            (Autoconf, Make),
        ],
    )
    def test_runner_assignment(
        self, mock_project, mock_shell, build_system_class, runner_class
    ):
        with patch("amphimixis.build_systems.meson.Shell", return_value=mock_shell):
            with patch(
                "amphimixis.build_systems.autoconf.Shell", return_value=mock_shell
            ):
                runner = runner_class(mock_project)
                if build_system_class == Meson:
                    bs = build_system_class(mock_project, runner=runner)
                else:
                    bs = build_system_class(mock_project, runner=runner)
                assert bs.runner is runner

    def test_meson_uses_ninja_commands(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.meson.Shell", return_value=mock_shell):
            ninja_runner = Ninja(mock_project)
            meson = Meson(mock_project, runner=ninja_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            meson.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "meson" in combined_output.lower()

    def test_autoconf_uses_make_commands(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.autoconf.Shell", return_value=mock_shell):
            make_runner = Make(mock_project)
            autoconf = Autoconf(mock_project, runner=make_runner)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            autoconf.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "make" in combined_output.lower() or "./configure" in combined_output


@pytest.mark.unit
class TestBazel:
    """Tests for Bazel build system"""

    @pytest.fixture
    def bazel_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.bazel.Shell", return_value=mock_shell):
            bazel = Bazel(mock_project)
            yield bazel

    @pytest.mark.parametrize(
        "flag_attr,flag_value,expected_flag",
        [
            (CompilerFlagsAttrs.C_FLAGS, "-O2", "--copt='-O2'"),
            (CompilerFlagsAttrs.CXX_FLAGS, "-Wall", "--cxxopt='-Wall'"),
            (CompilerFlagsAttrs.ASM_FLAGS, "-fasm", "--asmopt='-fasm'"),
        ],
    )
    def test_generate_lang_flags(
        self, bazel_system, flag_attr, flag_value, expected_flag
    ):
        compiler_flags = CompilerFlags()
        compiler_flags.set(flag_attr, flag_value)
        result = bazel_system._generate_lang_flags(compiler_flags)
        assert expected_flag in result

    @pytest.mark.parametrize(
        "tool_attr,tool_value,expected_flag",
        [
            (ToolchainAttrs.C_COMPILER, "/usr/bin/gcc", "--compiler=/usr/bin/gcc"),
            (ToolchainAttrs.CXX_COMPILER, "/usr/bin/g++", "--cxx=/usr/bin/g++"),
        ],
    )
    def test_generate_toolchain_options(
        self, bazel_system, tool_attr, tool_value, expected_flag
    ):
        toolchain = Toolchain()
        toolchain.set(tool_attr, tool_value)
        result = bazel_system._generate_toolchain_options(toolchain)
        assert expected_flag in result

    def test_sysroot_in_command(self, mock_project, mock_shell):
        sysroot = "/sysroot"
        toolchain = Toolchain(sysroot=sysroot)
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="bazel_build",
            executables=["//src:app"],
            toolchain=toolchain,
            sysroot=sysroot,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.bazel.Shell", return_value=mock_shell):
            bazel = Bazel(mock_project)
            bazel.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "--sysroot=/sysroot" in combined_output

    def test_config_flags_passed(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.bazel.Shell", return_value=mock_shell):
            bazel = Bazel(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=["//..."],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="--jobs=4",
            )
            bazel.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "--jobs=4" in combined_output

    def test_build_command_structure(self, bazel_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=["//src:main"],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        bazel_system.build(build)

        bazel_call_found = False
        for call in mock_shell.run.call_args_list:
            call_str = str(call)
            if "bazel" in call_str and "build" in call_str:
                bazel_call_found = True
                break

        assert bazel_call_found, "bazel build command not found"

    def test_connect_called(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.bazel.Shell", return_value=mock_shell):
            bazel = Bazel(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=["//..."],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            bazel.build(build)

            mock_shell.connect.assert_called()

    def test_default_target(self, bazel_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        bazel_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "//..." in combined_output

    def test_executable_target(self, bazel_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=["//foo:bar"],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        bazel_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "//foo:bar" in combined_output


@pytest.mark.unit
class TestGmake:
    """Tests for Gmake (GNU Make) build system"""

    @pytest.fixture
    def gmake_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.gmake.Shell", return_value=mock_shell):
            gmake = Gmake(mock_project)
            yield gmake

    @pytest.mark.parametrize(
        "flag_attr,flag_value,expected_flag",
        [
            (CompilerFlagsAttrs.C_FLAGS, "-O2", "CFLAGS='-O2'"),
            (CompilerFlagsAttrs.CXX_FLAGS, "-Wall", "CXXFLAGS='-Wall'"),
            (CompilerFlagsAttrs.FORTRAN_FLAGS, "-ffast-math", "FFLAGS='-ffast-math'"),
        ],
    )
    def test_generate_lang_flags(
        self, gmake_system, flag_attr, flag_value, expected_flag
    ):
        compiler_flags = CompilerFlags()
        compiler_flags.set(flag_attr, flag_value)
        result = gmake_system._generate_lang_flags(compiler_flags)
        assert expected_flag in result

    @pytest.mark.parametrize(
        "tool_attr,expected_tool",
        [
            (ToolchainAttrs.C_COMPILER, "CC"),
            (ToolchainAttrs.CXX_COMPILER, "CXX"),
            (ToolchainAttrs.AR_T, "AR"),
            (ToolchainAttrs.LD_T, "LD"),
        ],
    )
    def test_toolchain_attrs_map(self, gmake_system, tool_attr, expected_tool):
        result = gmake_system._toolchain_attrs_map(tool_attr.value)
        assert result == expected_tool

    def test_generate_toolchain_flags(self, gmake_system):
        toolchain = Toolchain()
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")
        toolchain.set(ToolchainAttrs.CXX_COMPILER, "/usr/bin/g++")
        result = gmake_system._generate_toolchain_flags(toolchain)
        assert "CC='/usr/bin/gcc'" in result
        assert "CXX='/usr/bin/g++'" in result

    def test_sysroot_handling(self, mock_project, mock_shell):
        sysroot = "/sysroot"
        toolchain = Toolchain(sysroot=sysroot)
        toolchain.set(ToolchainAttrs.C_COMPILER, "/usr/bin/gcc")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=[],
            toolchain=toolchain,
            sysroot=sysroot,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.gmake.Shell", return_value=mock_shell):
            gmake = Gmake(mock_project)
            gmake._build_install_clean(build, configure=True)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "SYSROOT=/sysroot" in combined_output

    def test_parallel_build(self, mock_project, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        with patch("amphimixis.build_systems.gmake.Shell", return_value=mock_shell):
            gmake = Gmake(mock_project)
            gmake._build_install_clean(build, configure=False)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-j" in combined_output
        assert "gmake" in combined_output.lower()

    def test_config_flags_passed(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.gmake.Shell", return_value=mock_shell):
            gmake = Gmake(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="-f Makefile.gnumake",
            )
            gmake._build_install_clean(build, configure=True)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "Makefile.gnumake" in combined_output

    def test_connect_called(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.gmake.Shell", return_value=mock_shell):
            gmake = Gmake(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=[],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            gmake._build_install_clean(build, configure=True)

            mock_shell.connect.assert_called()

    def test_multiple_flags_combined(self, gmake_system, mock_shell):
        compiler_flags = CompilerFlags()
        compiler_flags.set(CompilerFlagsAttrs.C_FLAGS, "-O2")
        compiler_flags.set(CompilerFlagsAttrs.CXX_FLAGS, "-Wall -Wextra")

        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=[],
            toolchain=None,
            sysroot=None,
            compiler_flags=compiler_flags,
            config_flags=None,
        )

        gmake_system._build_install_clean(build, configure=True)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-O2" in combined_output
        assert "-Wall" in combined_output


@pytest.mark.unit
class TestYacc:
    """Tests for Yacc build system"""

    @pytest.fixture
    def yacc_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.yacc.Shell", return_value=mock_shell):
            yacc = Yacc(mock_project)
            yield yacc

    def test_generate_output_flags(self, yacc_system):
        result = yacc_system._generate_output_flags()
        assert "-d" in result

    def test_config_flags_passed(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.yacc.Shell", return_value=mock_shell):
            yacc = Yacc(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=["parser.y"],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="-v",
            )
            yacc.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "-v" in combined_output
        assert "yacc" in combined_output.lower()

    def test_build_command_structure(self, yacc_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=["parser.y"],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        yacc_system.build(build)

        yacc_call_found = False
        for call in mock_shell.run.call_args_list:
            call_str = str(call)
            if "yacc" in call_str.lower() or "byacc" in call_str.lower():
                yacc_call_found = True
                break

        assert yacc_call_found, "yacc command not found"

    def test_connect_called(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.yacc.Shell", return_value=mock_shell):
            yacc = Yacc(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=["parser.y"],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            yacc.build(build)

            mock_shell.connect.assert_called()

    def test_executable_as_source(self, yacc_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=["syntax.y"],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        yacc_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "syntax.y" in combined_output


@pytest.mark.unit
class TestBison:
    """Tests for Bison build system"""

    @pytest.fixture
    def bison_system(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.bison.Shell", return_value=mock_shell):
            bison = Bison(mock_project)
            yield bison

    @pytest.mark.parametrize(
        "flag_attr,flag_value,expected_flag",
        [
            (CompilerFlagsAttrs.C_FLAGS, "-O2", "%code{-O2}"),
            (CompilerFlagsAttrs.ASM_FLAGS, "-fasm", "%code{-fasm}"),
        ],
    )
    def test_generate_directives(
        self, bison_system, flag_attr, flag_value, expected_flag
    ):
        compiler_flags = CompilerFlags()
        compiler_flags.set(flag_attr, flag_value)
        result = bison_system._generate_directives(compiler_flags)
        assert flag_value in result

    def test_generate_output_flags(self, bison_system):
        result = bison_system._generate_output_flags()
        assert "-d" in result

    def test_config_flags_passed(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.bison.Shell", return_value=mock_shell):
            bison = Bison(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=["parser.y"],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="--warnings=none",
            )
            bison.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "--warnings=none" in combined_output
        assert "bison" in combined_output.lower()

    def test_build_command_structure(self, bison_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test_build",
            executables=["grammar.y"],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        bison_system.build(build)

        bison_call_found = False
        for call in mock_shell.run.call_args_list:
            call_str = str(call)
            if "bison" in call_str.lower():
                bison_call_found = True
                break

        assert bison_call_found, "bison command not found"

    def test_connect_called(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.bison.Shell", return_value=mock_shell):
            bison = Bison(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=["parser.y"],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags=None,
            )
            bison.build(build)

            mock_shell.connect.assert_called()

    def test_executable_as_source(self, bison_system, mock_shell):
        build = Build(
            build_machine=MachineInfo(Arch.X86, None, None),
            run_machine=MachineInfo(Arch.X86, None, None),
            build_name="test",
            executables=["grammar.yy"],
            toolchain=None,
            sysroot=None,
            compiler_flags=None,
            config_flags=None,
        )

        bison_system.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "grammar.yy" in combined_output

    def test_language_option_cpp(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.bison.Shell", return_value=mock_shell):
            bison = Bison(mock_project)

            build = Build(
                build_machine=MachineInfo(Arch.X86, None, None),
                run_machine=MachineInfo(Arch.X86, None, None),
                build_name="test",
                executables=["parser.y"],
                toolchain=None,
                sysroot=None,
                compiler_flags=None,
                config_flags="--language=C++",
            )
            bison.build(build)

        calls = [str(call) for call in mock_shell.run.call_args_list]
        combined_output = " ".join(calls)
        assert "--language=C++" in combined_output


@pytest.mark.unit
class TestParserGeneratorIntegration:
    """Integration tests for parser generators (Yacc/Bison)"""

    def test_yacc_and_bison_both_use_defines(self, mock_project, mock_shell):
        with patch("amphimixis.build_systems.yacc.Shell", return_value=mock_shell):
            yacc = Yacc(mock_project)
            yacc_output = yacc._generate_output_flags()
            assert "-d" in yacc_output

        with patch("amphimixis.build_systems.bison.Shell", return_value=mock_shell):
            bison = Bison(mock_project)
            bison_output = bison._generate_output_flags()
            assert "-d" in bison_output


@pytest.mark.unit
class TestAllBuildSystemsIntegration:
    """Final integration tests for all build systems"""

    @pytest.mark.parametrize(
        "build_system_class,shell_patch",
        [
            (CMake, "amphimixis.build_systems.cmake.Shell"),
            (Meson, "amphimixis.build_systems.meson.Shell"),
            (Autoconf, "amphimixis.build_systems.autoconf.Shell"),
            (Bazel, "amphimixis.build_systems.bazel.Shell"),
            (Gmake, "amphimixis.build_systems.gmake.Shell"),
            (Yacc, "amphimixis.build_systems.yacc.Shell"),
            (Bison, "amphimixis.build_systems.bison.Shell"),
            (Ninja, "amphimixis.build_systems.ninja.Shell"),
            (Make, "amphimixis.build_systems.make.Shell"),
        ],
    )
    def test_all_build_systems_instantiate(
        self, mock_project, build_system_class, shell_patch
    ):
        with patch(shell_patch, return_value=MagicMock()):
            if build_system_class in (CMake, Meson, Autoconf):
                runner = (
                    Ninja(mock_project)
                    if build_system_class != Autoconf
                    else Make(mock_project)
                )
                bs = build_system_class(mock_project, runner=runner)
            else:
                bs = build_system_class(mock_project)

        assert bs is not None
        assert hasattr(bs, "build") or hasattr(bs, "run_building")

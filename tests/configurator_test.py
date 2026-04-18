"""Configurator tests"""

import os
import tempfile
from shutil import rmtree
from unittest.mock import MagicMock, patch

import pytest

import amphimixis.core.configurator as configurator
from amphimixis.core.general import Arch, Project


@pytest.mark.unit
class TestConfiguratorWithTestData:
    """Tests for configurator using input_configurator_test.yaml"""

    TEST_CONFIG_FILE = os.path.join(
        os.path.dirname(__file__), "integration/input_configurator_test.yaml"
    )

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary directory for the project"""
        temp_dir = tempfile.mkdtemp(prefix="test_project_")
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_cwd)
        rmtree(temp_dir, ignore_errors=True)
        for f in os.listdir(original_cwd):
            if f.endswith(".project"):
                os.remove(os.path.join(original_cwd, f))

    @pytest.fixture
    def mock_shell_remote(self):
        """Mock Shell.connect for remote machines to avoid connection errors"""
        mock_shell = MagicMock()
        mock_shell.run.return_value = (0, [["riscv64"]], [])
        mock_shell.connect.return_value = mock_shell

        with patch("amphimixis.core.configurator.Shell") as mock_shell_class:
            mock_shell_class.return_value.connect.return_value = mock_shell
            mock_shell_class.return_value.run.return_value = (0, [["x86_64"]], [])
            yield mock_shell_class

    def test_parse_config_with_test_data(self, temp_project_dir, mock_shell_remote):
        """Test parsing configuration file with test data
        Expect: Configuration successful with correct builds created"""
        project = Project(temp_project_dir)

        result = configurator.parse_config(project, self.TEST_CONFIG_FILE)

        assert result is True
        assert len(project.builds) == 2

        build1 = project.builds[0]
        assert build1.build_machine.arch == Arch.X86
        assert build1.run_machine.arch == Arch.X86
        assert "test/run-tests" in build1.executables

        build2 = project.builds[1]
        assert build2.build_machine.arch == Arch.X86
        assert build2.run_machine.arch == Arch.RISCV

    def test_parse_config_build_machine_info(self, temp_project_dir, mock_shell_remote):
        """Test that build_machine info is correctly resolved
        Expect: Build machine has correct architecture"""
        project = Project(temp_project_dir)

        configurator.parse_config(project, self.TEST_CONFIG_FILE)

        build1 = project.builds[0]
        assert build1.build_machine.arch == Arch.X86

    def test_parse_config_run_machine_local(self, temp_project_dir, mock_shell_remote):
        """Test that local run_machine (x86) is correctly resolved
        Expect: Run machine has correct architecture and no address"""
        project = Project(temp_project_dir)

        configurator.parse_config(project, self.TEST_CONFIG_FILE)

        build1 = project.builds[0]
        assert build1.run_machine.arch == Arch.X86
        assert build1.run_machine.address is None

    def test_parse_config_run_machine_remote(self, temp_project_dir, mock_shell_remote):
        """Test that remote run_machine (riscv) is correctly resolved
        Expect: Run machine has correct architecture and address"""
        project = Project(temp_project_dir)

        configurator.parse_config(project, self.TEST_CONFIG_FILE)

        build2 = project.builds[1]
        assert build2.run_machine.auth is not None
        assert build2.run_machine.arch == Arch.RISCV
        assert build2.run_machine.address == "10.0.40.2"
        assert build2.run_machine.auth.username == "root"
        assert build2.run_machine.auth.password == "password"

    def test_parse_config_recipe_config_flags(
        self, temp_project_dir, mock_shell_remote
    ):
        """Test that recipe config_flags are correctly parsed
        Expect: Build has correct config_flags"""
        project = Project(temp_project_dir)

        configurator.parse_config(project, self.TEST_CONFIG_FILE)

        build1 = project.builds[0]
        assert build1.config_flags is not None
        assert "-DCMAKE_BUILD_TYPE=RelWithDebInfo" in build1.config_flags

        build2 = project.builds[1]
        assert build2.config_flags is not None
        assert "-DCMAKE_BUILD_TYPE=RelWithDebInfo" in build2.config_flags
        assert (
            "-DCMAKE_TOOLCHAIN_FILE=/opt/toolchains/riscv.cmake" in build2.config_flags
        )

    def test_parse_config_recipe_jobs(self, temp_project_dir, mock_shell_remote):
        """Test that recipe jobs are correctly parsed
        Expect: Build has correct jobs value"""
        project = Project(temp_project_dir)

        configurator.parse_config(project, self.TEST_CONFIG_FILE)

        build1 = project.builds[0]
        assert build1.jobs == 3

    def test_parse_config_executables(self, temp_project_dir, mock_shell_remote):
        """Test that executables are correctly parsed
        Expect: Builds have correct executables list"""
        project = Project(temp_project_dir)

        configurator.parse_config(project, self.TEST_CONFIG_FILE)

        for build in project.builds:
            assert "test/run-tests" in build.executables

    def test_parse_config_build_system(self, temp_project_dir, mock_shell_remote):
        """Test that build system is correctly set from config
        Expect: Project has CMake build system"""
        project = Project(temp_project_dir)

        configurator.parse_config(project, self.TEST_CONFIG_FILE)

        assert project.build_system is not None

    def test_parse_config_invalid_project_path(self):
        """Test parse_config with invalid project path
        Expect: Returns False"""
        project = Project("/nonexistent/project/path")

        result = configurator.parse_config(project, self.TEST_CONFIG_FILE)

        assert result is False

    def test_parse_config_invalid_config_file(self, temp_project_dir):
        """Test parse_config with invalid config file path
        Expect: Returns False"""
        project = Project(temp_project_dir)

        result = configurator.parse_config(project, "nonexistent_config.yaml")

        assert result is False
        assert result is False

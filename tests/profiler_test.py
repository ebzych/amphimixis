# pylint: skip-file
import subprocess
from pathlib import Path

import pytest
import pytest_mock

import amphimixis
import amphimixis.profiler
from amphimixis import general

EXECUTABLE_FILENAME = "a.out"

C_PROGRAM_SUCCESSFUL_RUN = "int main() {return 0;}"
C_PROGRAM_FAILED_RUN = "int main() {return 1;}"
C_PROGRAM_SLEEP_1_SECONDS = "#include <unistd.h>\nint main() {sleep(1); return 0;}"
C_PROGRAM_SLEEP_3_SECONDS = "#include <unistd.h>\nint main() {sleep(3); return 0;}"


@pytest.fixture
def proj_path(tmp_path: Path) -> Path:
    path = tmp_path / "proj_path"
    path.mkdir()
    return path


@pytest.fixture
def build_executable():
    def _build(path: Path, program: str, exec_name: str, build_name: str):
        exec_path = path / build_name / exec_name
        c_program_path = path / "main.c"
        with c_program_path.open("w") as file:
            file.write(program)

        subprocess.run(
            ["gcc", "-o", str(exec_path), str(object=c_program_path)], check=True
        )

    return _build


@pytest.fixture
def get_profiler(mocker: pytest_mock.MockerFixture):
    def _profiler(path: Path, exec_name: str) -> amphimixis.Profiler:
        workdir_path_mock = mocker.Mock()
        workdir_path_mock.return_value = str(path)
        mocker.patch("amphimixis.Shell.get_project_workdir", workdir_path_mock)
        build = general.Build(
            general.MachineInfo(general.Arch.X86, None, None),
            general.MachineInfo(general.Arch.X86, None, None),
            "test_build",
            [exec_name],
            None,
            None,
        )
        (path / build.build_name).mkdir()

        project = general.Project(
            str(path),
            [build],
            amphimixis.build_systems_dict["cmake"],
            amphimixis.build_systems_dict["cmake"],
        )

        return amphimixis.Profiler(project, build)

    return _profiler


class TestProfiler:
    @pytest.mark.parametrize("program", [C_PROGRAM_SUCCESSFUL_RUN])
    def test_execution_time_updates_dictionary_with_correct_data(
        self, proj_path, get_profiler, build_executable, program: str
    ):
        profiler: amphimixis.Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        build_executable(
            proj_path, program, EXECUTABLE_FILENAME, profiler.build.build_name
        )

        assert profiler.execution_time(EXECUTABLE_FILENAME)

        for time_counter in (
            amphimixis.profiler.Stats.KERNEL_TIME,
            amphimixis.profiler.Stats.USER_TIME,
            amphimixis.profiler.Stats.REAL_TIME,
        ):
            assert float(profiler.stats[EXECUTABLE_FILENAME][time_counter]) >= 0

    @pytest.mark.parametrize(
        "program, expected",
        [
            (C_PROGRAM_SLEEP_1_SECONDS, 1),
            (C_PROGRAM_SLEEP_3_SECONDS, 3),
        ],
    )
    def test_execution_time_measures_right(
        self, proj_path, get_profiler, build_executable, program: str, expected: float
    ):
        profiler: amphimixis.Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        build_executable(
            proj_path, program, EXECUTABLE_FILENAME, profiler.build.build_name
        )

        assert profiler.execution_time(EXECUTABLE_FILENAME)

        assert (
            float(
                profiler.stats[EXECUTABLE_FILENAME][amphimixis.profiler.Stats.REAL_TIME]
            )
            > expected - 0.1
        )

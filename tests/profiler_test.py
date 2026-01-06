# pylint: skip-file
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
import pytest_mock

import amphimixis
import amphimixis.profiler
from amphimixis import Profiler, general

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
    def _profiler(path: Path, exec_name: str) -> Profiler:
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

        return Profiler(project, build)

    return _profiler


@pytest.mark.unit
class TestProfiler:
    @pytest.mark.parametrize(
        "method",
        [
            Profiler.test_executable,
            Profiler.execution_time,
            Profiler.perf_stat_collect,
            Profiler.perf_record_collect,
        ],
    )
    @pytest.mark.parametrize(
        "program, expected",
        [
            (C_PROGRAM_SUCCESSFUL_RUN, True),
            (C_PROGRAM_FAILED_RUN, False),
        ],
    )
    def test_basic_functions_return_appropriate_value(
        self,
        proj_path,
        get_profiler,
        build_executable,
        method: Callable[[Profiler, str], bool],
        program: str,
        expected: bool,
    ):
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        build_executable(
            proj_path, program, EXECUTABLE_FILENAME, profiler.build.build_name
        )

        assert method(profiler, EXECUTABLE_FILENAME) == expected

    @pytest.mark.parametrize("program", [C_PROGRAM_SUCCESSFUL_RUN])
    def test_execution_time_updates_dictionary_with_correct_data(
        self, proj_path, get_profiler, build_executable, program: str
    ):
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
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
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
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

    @pytest.mark.parametrize("program", [C_PROGRAM_SUCCESSFUL_RUN])
    def test_perf_data_collect_updates_dictionary_with_some_data_on_successful_run(
        self, proj_path, get_profiler, build_executable, program: str
    ):
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        build_executable(
            proj_path, program, EXECUTABLE_FILENAME, profiler.build.build_name
        )

        assert profiler.perf_stat_collect(EXECUTABLE_FILENAME)

        assert (
            profiler.stats[EXECUTABLE_FILENAME].get(amphimixis.profiler.Stats.PERF_STAT)
            is not None
        )

    @pytest.mark.parametrize("program", [C_PROGRAM_SUCCESSFUL_RUN])
    def test_perf_record_collect_creates_valid_perf_data_file(
        self, proj_path, get_profiler, build_executable, program: str
    ):
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        build_executable(
            proj_path, program, EXECUTABLE_FILENAME, profiler.build.build_name
        )

        assert profiler.perf_record_collect(EXECUTABLE_FILENAME)

        result = subprocess.run(
            ["perf", "report", "-i", profiler.get_record_filename(EXECUTABLE_FILENAME)],
        )

        assert result.returncode == 0

    @pytest.mark.parametrize("program", [C_PROGRAM_SUCCESSFUL_RUN])
    def test_profile_all_finds_executables_on_empty_list_in_build(
        self, proj_path, get_profiler, build_executable, program: str
    ):
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        profiler.executables.clear()

        build_executable(
            proj_path, program, EXECUTABLE_FILENAME + "test", profiler.build.build_name
        )

        assert profiler.profile_all(
            test_executable=False,
            execution_time=False,
            stat_collect=False,
            record_collect=False,
            max_number_of_executables=1,
        )

    @pytest.mark.parametrize("program", [C_PROGRAM_SUCCESSFUL_RUN])
    def test_profile_all_return_false_if_can_not_find_executables(
        self, proj_path, get_profiler, build_executable, program: str
    ):
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        profiler.executables.clear()

        assert not profiler.profile_all(
            test_executable=False,
            execution_time=False,
            stat_collect=False,
            record_collect=False,
            max_number_of_executables=1,
        )

    @pytest.mark.parametrize("program", [C_PROGRAM_SUCCESSFUL_RUN])
    def test_profile_all_calls_every_method(
        self,
        proj_path,
        get_profiler,
        build_executable,
        mocker: pytest_mock.MockerFixture,
        program: str,
    ):

        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        profiler.executables.clear()
        spies = [
            mocker.spy(profiler, "test_executable"),
            mocker.spy(profiler, "execution_time"),
            mocker.spy(profiler, "perf_stat_collect"),
            mocker.spy(profiler, "perf_record_collect"),
        ]

        build_executable(
            proj_path, program, EXECUTABLE_FILENAME + "test", profiler.build.build_name
        )

        assert profiler.profile_all(
            test_executable=True,
            execution_time=True,
            stat_collect=True,
            record_collect=True,
            max_number_of_executables=1,
        )

        assert all(
            s.call_count == 1 for s in spies
        ), "Not all profiler methods were called once"

    @pytest.mark.parametrize(
        "program_fail, program_ok", [(C_PROGRAM_FAILED_RUN, C_PROGRAM_SUCCESSFUL_RUN)]
    )
    def test_profile_all_skips_smoke_test_failed_executables(
        self,
        proj_path,
        get_profiler,
        build_executable,
        mocker: pytest_mock.MockerFixture,
        program_fail: str,
        program_ok: str,
    ):
        profiler: Profiler = get_profiler(proj_path, EXECUTABLE_FILENAME)
        profiler.executables.clear()
        spies = [
            mocker.spy(profiler, "test_executable"),
            mocker.spy(profiler, "execution_time"),
            mocker.spy(profiler, "perf_stat_collect"),
            mocker.spy(profiler, "perf_record_collect"),
        ]

        build_executable(
            proj_path,
            program_fail,
            EXECUTABLE_FILENAME + "fail_test",
            profiler.build.build_name,
        )

        build_executable(
            proj_path,
            program_ok,
            EXECUTABLE_FILENAME + "ok_test",
            profiler.build.build_name,
        )

        assert profiler.profile_all(
            test_executable=True,
            execution_time=True,
            stat_collect=True,
            record_collect=True,
            max_number_of_executables=2,
        )

        assert spies[0].call_count == 2
        assert all(s.call_count == 1 for s in spies[1:])
        assert (
            len(profiler.stats[EXECUTABLE_FILENAME + "fail_test"].keys()) == 1
        ), "Executable that failed smoke test is not skipped"
        assert (
            len(profiler.stats[EXECUTABLE_FILENAME + "ok_test"].keys()) == 5
        ), "Executable that passed smoke test is skipped"

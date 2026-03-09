"""Module for profiling executables within a project."""

import logging
import os
import pickle
from enum import Enum

from amphimixis import general, logger, shell
from amphimixis.general import IUI, NullUI


class Stats(Enum):
    """Profiler stats fields"""

    REAL_TIME = 0
    USER_TIME = 1
    KERNEL_TIME = 2
    EXECUTABLE_RUN_SUCCESS = 3
    PERF_STAT = 4


ProfilerStats = dict[Stats, str]


_commands_args: dict[str, dict[str, str]] = {
    "stat": {
        "cmd": "perf stat",
        "opt": "-ddd -x,",
        "cpu_affinity": "taskset -c 0",
    },
    "record": {"cmd": "perf record", "cpu_affinity": "taskset -c 0"},
    "time": {
        "cmd": "/bin/time",
        "format": '-f"%e\\n%U\\n%S"',
        "cpu_affinity": "taskset -c 0",
    },
}


# pylint: disable=too-many-instance-attributes
class Profiler:
    """Class for profiling a build within a project."""

    class CustomLogger(logging.LoggerAdapter):
        """Custom logger to add build and executable prefixes to log messages."""

        def process(self, msg, kwargs):
            if self.extra is None:
                return f"{msg}", kwargs

            build_prefix = self.extra.get("build")

            extra = kwargs.get("extra", {})
            exe_prefix = extra.get("target") if isinstance(extra, dict) else None

            if exe_prefix:
                prefix = f"{build_prefix} | {exe_prefix} |"
            else:
                prefix = f"{build_prefix} |"

            return f"{prefix} {msg}", kwargs

    def __init__(
        self, project: general.Project, build: general.Build, ui: IUI = NullUI()
    ):
        self.project = project
        self.logger = self.CustomLogger(
            logger.setup_logger("PROFILER"), {"build": build.build_name}
        )
        self.machine = build.run_machine
        self.build = build
        self.ui = ui
        self.executables = build.executables.copy()
        self.shell = shell.Shell(self.machine, ui).connect()
        self.stats: dict[str, ProfilerStats] = {}
        self.build_path = os.path.join(
            self.shell.get_project_workdir(project), build.build_name
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def profile_all(
        self,
        working_directory: str = "",
        test_executable: bool = True,
        execution_time: bool = True,
        stat_collect: bool = True,
        record_collect: bool = True,
        max_number_of_executables=1,
    ) -> bool:
        """
        Run profiling on every executable.\n
        If `build.executables` is empty, finds executables in `build.build_path`.

        :param working_directory: absolute path to set working directory.
        :type working_directory: str

        :type test_executable: bool
        :param test_executable: Run an executable smoke test if `True`.
            Saves result in `self.stats[EXECUTABLE][Stats.EXECUTABLE_RUN_SUCCESS]`.

        :type execution_time: bool
        :param execution_time: run an executable time measurement if `True`.
            Saves result in `self.stats[EXECUTABLE]` dictionary with keys `Stats.REAL_TIME`,
            `Stats.USER_TIME`, `Stats.KERNEL_TIME`.

        :type stat_collect: bool
        :param stat_collect: collect perfomance counters if `True`.
            Saves result in `self.stats[EXECUTABLE][Stats.PERF_STAT]`.

        :type record_collect: bool
        :param record_collect: collect counters using sampling if `True`.
            Saves `perf.data` into `self.get_record_filename()`
            file in the working directory.

        :return: False if no executable is found. Otherwise True.
        :rtype: bool
        """

        if working_directory == "":
            working_directory = self.shell.get_source_dir(self.project)

        if not self.executables:
            self.executables = self._find_executables(max_number_of_executables)
            self.ui.update_message(
                self.build.build_name, "Searching for executables..."
            )
            self.logger.info("Found executables:\n%s\n", "\n".join(self.executables))

        if not self.executables:
            self.logger.error("Can't find any executables")
            self.ui.update_message(self.build.build_name, "No executables found")
            return False

        for executable in self.executables:
            if test_executable:
                self.ui.update_message(self.build.build_name, "Testing...")
                if not self.test_executable(executable, working_directory):
                    continue

            if execution_time:
                self.ui.update_message(self.build.build_name, "Measuring time...")
                self.execution_time(executable, working_directory)

            if stat_collect:
                self.ui.update_message(self.build.build_name, "Perf stat collecting..")
                self.perf_stat_collect(executable, working_directory)

            if record_collect:
                self.ui.update_message(self.build.build_name, "Perf data recording ...")
                if self.perf_record_collect(executable, working_directory):
                    self.perf_script(
                        self.get_record_filename(executable), working_directory
                    )

        return True

    def execution_time(self, executable: str, working_directory: str) -> bool:
        """
        Measure execution time: real, user, kernel

        :param executable: relative to `build_path` path to executable
        :type executable: str

        :param working_directory: absolute path to set working directory.
        :type working_directory: str

        :return: `False` if non-zero error code is returned. Otherwise `True`
        :rtype: bool
        """

        self.logger.info(
            "Measuring execution time started",
            extra={"target": executable},
        )

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, _, stderr = self.shell.run(f"cd {working_directory}")
        if error != 0:
            self.logger.error(
                "".join(stderr[0]),
                extra={"target": executable},
            )

            return False

        command = self._time_command(
            os.path.join(self.build_path, executable), stderr_clear=False
        )
        self.logger.info(
            "Measure execution time\n\tCommand: %s",
            command,
            extra={"target": executable},
        )

        error, stdout, stderr = self.shell.run(command)
        if error != 0:
            stderr_message = "STDERR: " + "".join(stderr[0])
            stdout_message = "STDOUT: " + "".join(stdout[0])
            self.logger.error(
                "Measure execution time fail\n%s",
                stderr_message,
                extra={"target": executable},
            )

            self.logger.error(
                "Measure execution time fail\n%s",
                stdout_message,
                extra={"target": executable},
            )

            return False

        self.stats[executable].update(
            {
                Stats.REAL_TIME: stderr[0][-3].strip(),
                Stats.USER_TIME: stderr[0][-2].strip(),
                Stats.KERNEL_TIME: stderr[0][-1].strip(),
            }
        )

        self.logger.info(
            "Measuring execution time finished",
            extra={"target": executable},
        )

        return True

    def test_executable(self, executable: str, working_directory: str) -> bool:
        """
        Checks if executable runs and returns no errors.\n
        Updates `self.stats[EXECUTABLE]` dictionary with `Stats.EXECUTABLE_RUN_SUCCESS` key

        :param executable: relative to `build_path` path to executable
        :type executable: str

        :param working_directory: absolute path to set working directory.
        :type working_directory: str

        :return: True if the executable return 0. False if can't run the executable or
                 non-zero error code is returned.
        :rtype: bool
        """

        self.logger.info(
            "Smoke test started",
            extra={"target": executable},
        )

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, stdout, stderr = self.shell.run(
            f"cd {working_directory}", f"{os.path.join(self.build_path, executable)}"
        )

        if error != 0:
            stderr_message = "".join(line for cmd in stderr for line in cmd)
            self.logger.error(
                "Smoke test fail STDERR:\n%s",
                stderr_message,
                extra={"target": executable},
            )

            stdout_message = "".join(line for cmd in stdout for line in cmd)
            self.logger.error(
                "Smoke test fail STDOUT:\n%s",
                stdout_message,
                extra={"target": executable},
            )

        self.stats[executable].update(
            {Stats.EXECUTABLE_RUN_SUCCESS: "true" if error == 0 else "false"}
        )

        self.logger.info(
            "Smoke test finished",
            extra={"target": executable},
        )

        return error == 0

    def perf_stat_collect(
        self, executable: str, working_directory: str, options: str = "-ddd"
    ) -> bool:
        """
        Collect performance statistics using `perf stat`.\n
        Updates `self.stats[EXECUTABLE]` dictionary with `Stats.PERF_STAT` key

        :param executable: relative to `build_path` path to executable
        :type executable: str

        :param options: `perf stat` additional options. Default `"-ddd"`
        :type options: str

        :param working_directory: absolute path to set working directory.
        :type working_directory: str

        :return: `False` if `perf stat` return non-zero error code. Otherwise `True`
        :rtype: bool
        """

        self.logger.info(
            "Perf stat started",
            extra={"target": executable},
        )

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, _, stderr = self.shell.run(
            f"cd {working_directory}",
        )

        if error != 0:
            self.logger.error(
                "Perf stat fail STDERR:\n%s",
                "".join(stderr[0]),
                extra={"target": executable},
            )

            return False

        command = self._perf_stat_command(
            os.path.join(self.build_path, executable), options
        )
        self.logger.info(
            "Perf stat command:\n\t%s",
            command,
            extra={"target": executable},
        )

        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Perf stat fail. Executable returned %d code\n%s",
                error,
                "".join(stderr[0]),
                extra={"target": executable},
            )

            return False

        self.stats[executable].update({Stats.PERF_STAT: "".join(stderr[0])})

        self.logger.info(
            "Perf stat finished",
            extra={"target": executable},
        )

        return True

    def perf_record_collect(
        self,
        executable: str,
        working_directory: str,
        options: str = "-g -F 1000 -e cycles,cache-misses,branch-misses",
    ) -> bool:
        """
        Collect performance records using `perf record`.\n
        Saves `perf.data` with archive of object files into `self.get_record_filename()`
        and `self.get_record_filename()`.tar.bz2 file in the working directory.

        :param executable: relative to `build_path` path to executable
        :type executable: str

        :param options: `perf record` additional options.
         Default: `"-g -F 1000 -e cycles,cache-misses,branch-misses"`
        :type options: str

        :param working_directory: absolute path to set working directory.
        :type working_directory: str

        :return: `False` if can't collect samples. Otherwise `True`
        :rtype: bool
        """

        self.logger.info(
            "Perf record started",
            extra={"target": executable},
        )

        error, _, stderr = self.shell.run(
            f"cd {working_directory}",
        )

        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        options += f" -o {self.get_record_filename(executable)}"
        command = self._perf_record_command(
            os.path.join(self.build_path, executable), options
        )

        self.logger.info(
            "Perf record command:\n\t%s",
            command,
            extra={"target": executable},
        )

        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Perf record fail. Executable returned %d code\n%s",
                error,
                "".join(stderr[0]),
                extra={"target": executable},
            )

            self.shell.run(f"rm {self.get_record_filename(executable)}")
            return False

        error, _, stderr = self.shell.run(
            f"perf archive {self.get_record_filename(executable)}"
        )

        if error != 0:
            self.logger.error(
                "Perf archive fail STDERR:\n%s",
                "".join(stderr[0]),
                extra={"target": executable},
            )

        error, stdout, stderr = self.shell.run("pwd")

        if error != 0:
            self.logger.error(
                "Perf record fail STDERR:\n%s",
                "".join(stderr[0]),
                extra={"target": executable},
            )

            return False

        remote_workdir = stdout[0][0].strip()
        if not self.shell.copy_to_host(
            os.path.join(remote_workdir, self.get_record_filename(executable)),
            os.path.join(os.getcwd(), self.get_record_filename(executable)),
        ):
            self.logger.error(
                "Perf record fail. Can't copy perf.data file",
                extra={"target": executable},
            )

            return False

        if not self.shell.copy_to_host(
            os.path.join(remote_workdir, self.get_archive_filename(executable)),
            os.path.join(os.getcwd(), self.get_archive_filename(executable)),
        ):
            self.logger.error(
                "Perf record fail. Can't copy perf archive file",
                extra={"target": executable},
            )

            return False

        self.logger.info(
            "Perf record collecting finished",
            extra={"target": executable},
        )

        return True

    def perf_script(self, filename: str, working_directory: str) -> tuple[bool, str]:
        """
        Runs `perf script` on the provided perf data file and saves to `filename`.txt

        :param filename: the name of perf record file.
        :type working_directory: str

        :param working_directory: absolute path to set working directory.
        Should contain perf record file.
        :type working_directory: str

        :return: error code and perf script output file name
        :rtype: tuple[int,str]
        """

        error, _, stderr = self.shell.run(
            f"cd {working_directory}",
        )

        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False, ""

        command, perf_script_file = self._get_script_command(filename)
        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Perf script fail STDERR:\n%s",
                "".join(stderr[0]),
                extra={"target": filename},
            )

            return False, ""

        error, stdout, stderr = self.shell.run("pwd")

        if error != 0:
            self.logger.error(
                "Perf script fail STDERR:\n%s",
                "".join(stderr[0]),
                extra={"target": filename},
            )

            return False, ""

        remote_workdir = stdout[0][0].strip()
        if not self.shell.copy_to_host(
            os.path.join(remote_workdir, perf_script_file),
            os.path.join(os.getcwd(), perf_script_file),
        ):
            self.logger.error(
                "Perf script fail. Can't copy perf script file",
                extra={"target": perf_script_file},
            )

            return False, ""

        return True, perf_script_file

    def save_stats(self):
        """Save collected statistics to a file."""

        with open(os.path.join(os.getcwd(), self._get_stats_filename()), "wb") as file:
            pickle.dump(self.stats, file)

    def get_record_filename(self, executable: str) -> str:
        """Gets perf record output file name."""

        executable_path_flatten = os.path.normpath(executable).replace("/", "_")
        return f"{self.build.build_name}_{executable_path_flatten}.perfdata"

    def get_archive_filename(self, executable: str) -> str:
        """Gets perf archive file name."""
        return self.get_record_filename(executable) + ".tar.bz2"

    def _get_stats_filename(self) -> str:
        return f"{self.build.build_name}.stats"

    def _build_cmd(
        self,
        tool_base: str,
        executable: str,
        stdout_clear: bool = False,
        stderr_clear: bool = True,
    ) -> str:
        redirects = ""
        if stdout_clear:
            redirects += " 1>/dev/null"
        if stderr_clear:
            redirects += " 2>/dev/null"

        return f"{tool_base} taskset -c 0 sh -c '{executable}{redirects}'"

    def _perf_stat_command(self, executable: str, user_options: str, **kwargs):
        fixed_options = "-x,"
        full_prefix = f"perf stat {user_options} {fixed_options}"
        return self._build_cmd(full_prefix.strip(), executable, **kwargs)

    def _perf_record_command(
        self,
        executable: str,
        user_options: str,
        **kwargs,
    ):
        full_prefix = f"perf record {user_options}"
        return self._build_cmd(full_prefix.strip(), executable, **kwargs)

    def _get_script_command(
        self,
        perf_record_file: str,
        perf_script_output_file: str = "",
        user_options: str = "-F comm,event,ip,sym,dso,period",
    ) -> tuple[str, str]:
        fixed_options = f"-G -i {perf_record_file}"
        if not perf_script_output_file:
            perf_script_output_file = perf_record_file + ".scriptout"

        return (
            f"perf --no-pager script {user_options} {fixed_options} > {perf_script_output_file}",
            perf_script_output_file,
        )

    def _time_command(self, executable: str, **kwargs):
        fixed_format = '-f"%e\\n%U\\n%S"'
        full_prefix = f"/bin/time {fixed_format}"
        return self._build_cmd(full_prefix.strip(), executable, **kwargs)

    def _find_executables(self, max_number_of_executables=1) -> list[str]:
        error, stdout, stderr = self.shell.run(
            f"cd {self.build_path}", 'find -type f -executable -name "*test*"'
        )

        if error != 0:
            self.logger.error(
                "STDERR: %s", "".join(line for cmd in stderr for line in cmd)
            )
            return []

        return [
            os.path.normpath(line.strip())
            for line in stdout[1][:max_number_of_executables]
        ]


if __name__ == "__main__":
    raise NotImplementedError

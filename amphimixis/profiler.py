"""Module for profiling executables within a project."""

import logging
import os
import pickle
from enum import Enum

from amphimixis import general, logger, shell


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


class Profiler:
    """Class for profiling a build within a project."""

    class CustomLogger(logging.LoggerAdapter):
        """Custom logger to add build and executable prefixes to log messages."""

        def process(self, msg, kwargs):
            if self.extra is None:
                return f"{msg}", kwargs

            build_prefix = self.extra.get("build")

            extra = kwargs.get("extra", {})
            exe_prefix = extra.get("executable") if isinstance(extra, dict) else None

            if exe_prefix:
                prefix = f"{build_prefix} | {exe_prefix} |"
            else:
                prefix = f"{build_prefix} |"

            return f"{prefix} {msg}", kwargs

    def __init__(self, project: general.Project, build: general.Build):
        self.logger = self.CustomLogger(
            logger.setup_logger("PROFILER"), {"build": build.build_name}
        )
        self.machine = build.run_machine
        self.build = build
        self.executables = build.executables.copy()
        self.shell = shell.Shell(self.machine).connect()
        self.stats: dict[str, ProfilerStats] = {}
        self.build_path = os.path.join(
            self.shell.get_project_workdir(project), build.build_name
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def profile_all(
        self,
        test_executable: bool = True,
        execution_time: bool = True,
        stat_collect: bool = True,
        record_collect: bool = True,
        max_number_of_executables=1,
    ) -> bool:
        """
        Run profiling on every executable.\n
        If `build.executables` is empty, finds executables in `build.build_path`.

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

        if not self.executables:
            self.executables = self._find_executables(max_number_of_executables)
            self.logger.info("Found executables:\n%s\n", "\n".join(self.executables))

        if not self.executables:
            self.logger.error("Can't find any executables")
            return False

        for executable in self.executables:
            if test_executable:
                if not self.test_executable(executable):
                    continue

            if execution_time:
                self.execution_time(executable)

            if stat_collect:
                self.perf_stat_collect(executable)

            if record_collect:
                self.perf_record_collect(executable)

        return True

    def execution_time(self, executable: str) -> bool:
        """
        Measure execution time: real, user, kernel

        :param executable: relative to `build_path` path to executable
        :type executable: str
        :return: `False` if non-zero error code is returned. Otherwise `True`
        :rtype: bool
        """

        self.logger.info(
            "Measuring execution time started",
            extra={"executable": executable},
        )

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, _, stderr = self.shell.run(f"cd {self.build_path}")
        if error != 0:
            self.logger.error(
                "".join(stderr[0]),
                extra={"executable": executable},
            )

            return False

        command = self._command(executable, "time", stderr_clear=False)
        self.logger.info(
            "Measure execution time\n\tCommand: %s",
            command,
            extra={"executable": executable},
        )

        error, stdout, stderr = self.shell.run(command)
        if error != 0:
            stderr_message = "STDERR: " + "".join(stderr[0])
            stdout_message = "STDOUT: " + "".join(stdout[0])
            self.logger.error(
                "Measure execution time fail\n%s",
                stderr_message,
                extra={"executable": executable},
            )

            self.logger.error(
                "Measure execution time fail\n%s",
                stdout_message,
                extra={"executable": executable},
            )

            return False

        self.stats[executable].update(
            {
                Stats.REAL_TIME: stderr[0][-3],
                Stats.USER_TIME: stderr[0][-2],
                Stats.KERNEL_TIME: stderr[0][-1],
            }
        )

        self.logger.info(
            "Measuring execution time finished",
            extra={"executable": executable},
        )

        return True

    def test_executable(self, executable: str) -> bool:
        """
        Checks if executable runs and returns no errors.\n
        Updates `self.stats[EXECUTABLE]` dictionary with `Stats.EXECUTABLE_RUN_SUCCESS` key

        :param executable: relative to `build_path` path to executable
        :type executable: str
        :return: True if the executable return 0. False if can't run the executable or
                 non-zero error code is returned.
        :rtype: bool
        """

        self.logger.info(
            "Smoke test started",
            extra={"executable": executable},
        )

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, stdout, stderr = self.shell.run(
            f"cd {self.build_path}", f"./{executable}"
        )

        if error != 0:
            stderr_message = "".join(line for cmd in stderr for line in cmd)
            self.logger.error(
                "Smoke test fail STDERR:\n%s",
                stderr_message,
                extra={"executable": executable},
            )

            stdout_message = "".join(line for cmd in stdout for line in cmd)
            self.logger.error(
                "Smoke test fail STDOUT:\n%s",
                stdout_message,
                extra={"executable": executable},
            )

        self.stats[executable].update(
            {Stats.EXECUTABLE_RUN_SUCCESS: "true" if error == 0 else "false"}
        )

        self.logger.info(
            "Smoke test finished",
            extra={"executable": executable},
        )

        return error == 0

    def perf_stat_collect(self, executable: str, options: str = "") -> bool:
        """
        Collect performance statistics using `perf stat`.\n
        Updates `self.stats[EXECUTABLE]` dictionary with `Stats.PERF_STAT` key

        :param executable: relative to `build_path` path to executable
        :type executable: str
        :param options: `perf stat` additional options
        :type options: str
        :return: `False` if `perf stat` return non-zero error code. Otherwise `True`
        :rtype: bool
        """

        self.logger.info(
            "Perf stat started",
            extra={"executable": executable},
        )

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, _, stderr = self.shell.run(
            f"cd {self.build_path}",
        )

        if error != 0:
            self.logger.error(
                "Perf stat fail STDERR:\n%s",
                "".join(stderr[0]),
                extra={"executable": executable},
            )

            return False

        command = self._command(executable, "stat", options)
        self.logger.info(
            "Perf stat command:\n\t%s",
            command,
            extra={"executable": executable},
        )

        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Perf stat fail. Executable returned %d code\n%s",
                error,
                "".join(stderr[0]),
                extra={"executable": executable},
            )

            return False

        self.stats[executable].update({Stats.PERF_STAT: "".join(stderr[0])})

        self.logger.info(
            "Perf stat finished",
            extra={"executable": executable},
        )

        return True

    def perf_record_collect(self, executable: str, options: str = "") -> bool:
        """
        Collect performance records using `perf record`.\n
        Saves `perf.data` into `self.get_record_filename()` file in the working directory.

        :param executable: relative to `build_path` path to executable
        :type executable: str
        :param options: `perf record` additional options
        :type options: str
        :return: `False` if can't collect samples. Otherwise `True`
        :rtype: bool
        """

        self.logger.info(
            "Perf record started",
            extra={"executable": executable},
        )

        error, _, stderr = self.shell.run(
            f"cd {self.build_path}",
        )

        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        options += f"-o {self.get_record_filename(executable)}"
        command = self._command(executable, "record", options)
        self.logger.info(
            "Perf record command:\n\t%s",
            command,
            extra={"executable": executable},
        )

        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Perf record fail. Executable returned %d code\n%s",
                error,
                "".join(stderr[0]),
                extra={"executable": executable},
            )
            return False

        error, stdout, stderr = self.shell.run("pwd")

        if error != 0:
            self.logger.error(
                "Perf record fail STDERR:\n%s",
                "".join(stderr[0]),
                extra={"executable": executable},
            )

            return False

        remote_workdir = stdout[0][0].strip()
        if not self.shell.copy_to_host(
            os.path.join(remote_workdir, self.get_record_filename(executable)),
            os.path.join(os.getcwd(), self.get_record_filename(executable)),
        ):
            self.logger.error(
                "Perf record fail. Can't copy perf.data file",
                extra={"executable": executable},
            )

            return False

        self.logger.info(
            "Perf record collecting finished",
            extra={"executable": executable},
        )

        return True

    def save_stats(self):
        """Save collected statistics to a file."""

        with open(os.path.join(os.getcwd(), self._get_stats_filename()), "wb") as file:
            pickle.dump(self.stats, file)

    def get_record_filename(self, executable: str) -> str:
        """Gets perf record output file name."""

        executable_path_flatten = os.path.normpath(executable).replace("/", "_")

        return f"{self.build.build_name}_{executable_path_flatten}.data"

    def _get_stats_filename(self) -> str:
        return f"{self.build.build_name}.stats"

    # pylint: disable=too-many-positional-arguments,too-many-arguments
    def _command(
        self,
        executable: str,
        module: str,
        options: str = "",
        stdout_clear: bool = False,
        stderr_clear: bool = True,
    ) -> str:
        if module not in _commands_args:
            return ""

        command: list[str] = []
        command.append(_commands_args[module]["cmd"])
        if options:
            command.append(options)

        for arg in _commands_args[module]:
            if arg != "cmd":
                command.append(_commands_args[module][arg])

        command.append(f"sh -c './{executable}")
        if stdout_clear:
            command.append("1>/dev/null")

        if stderr_clear:
            command.append("2>/dev/null")

        command.append("'")

        return " ".join(command)

    def _find_executables(self, max_number_of_executables=1) -> list[str]:
        error, stdout, stderr = self.shell.run(
            f"cd {self.build_path}", 'find -type f -executable -name "*test*"'
        )

        if error != 0:
            self.logger.error(
                "STDERR: %s", "".join(line for cmd in stderr for line in cmd)
            )
            return []

        return [line.strip() for line in stdout[1][:max_number_of_executables]]


if __name__ == "__main__":
    raise NotImplementedError

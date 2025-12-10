"""Module for profiling executables within a project."""

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
    """Class for profiling an executable within a project."""

    def __init__(self, build: general.Build):
        self.logger = logger.setup_logger("PROFILER")
        self.machine = build.run_machine
        self.build = build
        self.executables = build.executables.copy()
        self.shell = shell.Shell(self.machine).connect()
        self.stats: dict[str, ProfilerStats]

    def profile_all(
        self,
        test_executable: bool = True,
        execution_time: bool = True,
        stat_collect: bool = True,
        record_collect: bool = True,
    ) -> bool:
        """Run profiler on every executable"""
        if not self.executables:
            self.executables = self._find_executables()

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
        """Measure execution time: real, user, kernel"""

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, _, stderr = self.shell.run(f"cd {self.build.build_path}")
        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        command = self._command(executable, "time", stderr_clear=False)
        self.logger.info(
            "Measure execution time %s\n\tCommand: %s", executable, command
        )

        error, stdout, stderr = self.shell.run(command)
        if error != 0:
            error_message = "STDERR: " + "".join(stderr[0])
            error_message += "STDOUT: " + "".join(stdout[0])
            self.logger.error(error_message)
            return False

        self.stats[executable].update(
            {
                Stats.REAL_TIME: stderr[0][-3],
                Stats.USER_TIME: stderr[0][-2],
                Stats.KERNEL_TIME: stderr[0][-1],
            }
        )

        return True

    def test_executable(self, executable: str) -> bool:
        """Checks if executable runs and returns no errors"""

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, stdout, stderr = self.shell.run(
            f"cd {self.build.build_path}", f"./{executable}"
        )

        if error != 0:
            error_message = "STDERR: " + "".join(line for cmd in stderr for line in cmd)
            error_message += "STDOUT: " + "".join(
                line for cmd in stdout for line in cmd
            )
            self.logger.error(error_message)

        self.stats[executable].update(
            {Stats.EXECUTABLE_RUN_SUCCESS: "true" if error == 0 else "false"}
        )

        return error == 0

    def perf_stat_collect(self, executable: str, options: str = "") -> bool:
        """Collect performance statistics using 'perf stat'."""

        if executable not in self.stats:
            self.stats.update({executable: {}})

        error, _, stderr = self.shell.run(
            f"cd {self.build.build_path}",
        )

        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        command = self._command(executable, "stat", options)
        self.logger.info("Collecting perfomance counters with:\n\t%s", command)
        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Executable returned %d code\n%s", error, "".join(stderr[0])
            )
            return False

        self.stats[executable].update({Stats.PERF_STAT: "".join(stderr[0])})

        return True

    def perf_record_collect(self, executable: str, options: str = "") -> bool:
        """Collect performance records using 'perf record'."""

        error, _, stderr = self.shell.run(
            f"cd {self.build.build_path}",
        )

        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        options += f"-o {self.get_record_filename(executable)}"
        command = self._command(executable, "record", options)
        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Executable returned %d code\n%s", error, "".join(stderr[0])
            )
            return False

        error, stdout, stderr = self.shell.run("pwd")

        if error != 0:
            self.logger.error("".join(stderr[0]))
            return False

        remote_workdir = stdout[0][0].strip()
        if not self.shell.copy_to_host(
            os.path.join(remote_workdir, self.get_record_filename(executable)),
            os.path.join(os.getcwd(), self.get_record_filename(executable)),
        ):
            self.logger.error("Can't copy perf.data file")
            return False

        return True

    def save_stats(self):
        """Save collected statistics to a file."""

        pickle.dump(
            self.stats,
            os.path.join(os.getcwd(), self._get_stats_filename()),
        )

    def get_record_filename(self, executable: str) -> str:
        """Gets perf record output file name."""

        return f"{self.build.build_id}_{os.path.normpath(executable)}.data"

    def _get_stats_filename(self) -> str:
        return f"{self.build.build_id}.stats"

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

    def _find_executables(self) -> list[str]:
        error, stdout, stderr = self.shell.run(
            f"cd {self.build.build_path}", 'find -type f -executable -name "*test*"'
        )

        if error != 0:
            self.logger.error(
                "STDERR: %s", "".join(line for cmd in stderr for line in cmd)
            )
            return []

        return [line.strip() for line in stdout[1]]


if __name__ == "__main__":
    raise NotImplementedError

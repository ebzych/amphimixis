"""Module for profiling executables within a project."""

from enum import Enum

from amphimixis import general, logger, shell


class Stats(Enum):
    """Profiler stats fields"""

    REAL_TIME = 0
    USER_TIME = 1
    KERNEL_TIME = 2
    EXECUTABLE_RUN_SUCCESS = 3
    PERF_STAT = 4


class Profiler:
    """Class for profiling an executable within a project."""

    def __init__(self, build: general.Build, executable: str = ""):
        self.logger = logger.setup_logger("PROFILER")
        self.machine = build.run_machine
        self.build = build
        self.executable = executable
        self.shell = shell.Shell(self.machine).connect()
        self.stats: dict[Stats, str] = {}

    def execution_time(self) -> bool:
        """Measure execution time: real, user, kernel"""

        error, _, stderr = self.shell.run(f"cd {self.build.build_path}")
        if error != 0:
            self.logger.error(" ".join(stderr[0]))
            return False

        command = f'/bin/time -f"%e\n%U\n%S" taskset -c 0 sh -c "./{self.executable}"'
        self.logger.info(
            "Measure execution time %s\n\tCommand: %s", self.executable, command
        )
        error, stdout, stderr = self.shell.run(command)
        if error != 0:
            error_message = "STDERR: " + "".join(stderr[0])
            error_message += "STDOUT: " + "".join(stdout[0])
            self.logger.error(error_message)
            return False

        self.stats.update(
            {
                Stats.REAL_TIME: stderr[0][-3],
                Stats.USER_TIME: stderr[0][-2],
                Stats.KERNEL_TIME: stderr[0][-1],
            }
        )
        return True

    def test_executable(self) -> bool:
        """Checks if executable runs and returns no errors"""

        error, stdout, stderr = self.shell.run(f"cd {self}", f"./{self.executable}")
        if error != 0:
            error_message = "STDERR: " + "".join(stderr[0])
            error_message += "STDOUT: " + "".join(stdout[0])
            self.logger.error(error_message)

        self.stats.update(
            {Stats.EXECUTABLE_RUN_SUCCESS: "true" if error == 0 else "false"}
        )

        return error == 0

    def perf_stat_collect(self, options: str = "") -> bool:
        """Collect performance statistics using 'perf stat'."""

        error, _, stderr = self.shell.run(
            f"cd {self.build.build_path}",
        )

        if error != 0:
            self.logger.error(" ".join(stderr[0]))
            return False

        command = f"perf stat {options} -ddd -x, taskset -c 0 sh -c './{self.executable} 2>/dev/null'"
        self.logger.info("Collecting perfomance counters with:\n\t%s", command)
        error, _, stderr = self.shell.run(command)

        if error != 0:
            self.logger.error(
                "Executable returned %d code\n%s", error, "".join(stderr[0])
            )
            return False

        self.stats.update({Stats.PERF_STAT: "".join(stderr[0])})

        return True

    def perf_record_collect(self):
        """Collect performance records using 'perf record'."""
        raise NotImplementedError

    def save_stats(self):
        """Save collected statistics to a file."""
        raise NotImplementedError


if __name__ == "__main__":
    raise NotImplementedError

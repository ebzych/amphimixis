"""Module for profiling executables within a project."""

import os
from ctypes import ArgumentError

import general
import shell

from .constants import Perf, PerfStrings, Stats


def _executable_choose(files):
    return files[0]


def _choose_executable(build: general.Build) -> str:
    executables = []
    files = os.listdir(os.path.join(build.build_path))
    for file in files:
        if os.path.isdir(os.path.join(build.build_path, file)):
            continue

        with open(os.path.join(build.build_path, file), "rb") as data:
            _bytes = data.read(4)
            if _bytes[:2] == "MZ" or _bytes == b"\x7fELF":
                executables.append(file)

    return os.path.join(build.build_path, _executable_choose(executables))


class Profiler:
    """Class for profiling an executable within a project."""

    def __init__(
        self, machine: general.MachineInfo, build: general.Build, executable: str = ""
    ):
        self.machine = machine
        self.build = build
        if executable == "":
            self.executable = _choose_executable(build)
        else:
            self.executable = executable
        self.shell = shell.Shell(self.machine).connect()

        self.stats: dict[str, str] = {}
        self.perf_stat: dict[str, dict[str, str]] = {}

    def test_executable(self) -> bool:
        """Checks if executable runs and returns no errors"""

        error, _, _ = self.shell.run(
            f"cd {self.build.build_path}", f"{self.executable}"
        )

        self.stats.update(
            {Stats.EXECUTABLE_RUN_SUCCESS: "true" if error == 0 else "false"}
        )

        return error == 0

    def perf_stat_collect(self):
        """Collect performance statistics using 'perf stat'."""

        error, _, stderr = self.shell.run(
            f"cd {self.build.build_path}",
        )

        if error != 0:
            raise ArgumentError(str(*stderr[0]))

        error, stdout, stderr = self.shell.run(
            f"perf stat -ddd -x, sh -c'{self.executable} 2>/dev/null'",
        )

        if error != 0:
            raise ArgumentError(str(*stderr[0]))

        self._parse_perf_stat(stdout[0])

    def perf_record_collect(self):
        """Collect performance records using 'perf record'."""
        raise NotImplementedError

    def save_stats(self):
        """Save collected statistics to a file."""
        raise NotImplementedError

    def _parse_perf_stat(self, perf_out: list[str]) -> None:
        for line in perf_out:
            parts = line.split(",")
            if parts[1] == "":
                continue
            perf_event: dict[str, str] = dict()
            for i, part in enumerate(parts):
                perf_event.update({PerfStrings[Perf(i)]: part})
            self.perf_stat.update({parts[Perf.EVENT]: perf_event})


if __name__ == "__main__":
    raise NotImplementedError

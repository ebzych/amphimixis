"""Module for profiling executables within a project."""

import os
from non_amphimixis import Project

STATS_EXECUTION_TIME_FIELD = "execution_time"


def _executable_choose(files):
    return files[0]


def _choose_executable(project: Project) -> str:
    executables = []
    files = os.listdir(project.builds_path)
    for file in files:
        with open(os.path.join(project.builds_path, file), "rb") as data:
            _bytes = data.read(4)
            if _bytes[:2] == "MZ" or _bytes == b"\x7fELF":
                executables.append(file)

    return _executable_choose(files)


class Profiler:
    """Class for profiling an executable within a project."""

    def __init__(self, project: Project, executable: str = ""):
        self.project = project
        if executable == "":
            self.executable = _choose_executable(project)
        else:
            self.executable = executable

        self.stats = {}

    def execution_time(self):
        """Measure execution time of the executable."""
        raise NotImplementedError

    def perf_stat_collect(self):
        """Collect performance statistics using 'perf stat'."""
        raise NotImplementedError

    def perf_record_collect(self):
        """Collect performance records using 'perf record'."""
        raise NotImplementedError

    def save_stats(self):
        """Save collected statistics to a file."""
        raise NotImplementedError


if __name__ == "__main__":
    raise NotImplementedError

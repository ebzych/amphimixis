"""Module for profiling executables within a project."""

from non_amphimixis import Project


class Profiler:
    """Class for profiling an executable within a project."""

    def __init__(self, project: Project, executable: str):
        self.project = project
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

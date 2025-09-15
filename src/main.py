"""Main entry point for configuring a project."""

import sys
from general import Project
from profiler import Profiler

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <repo_path>")
        sys.exit(1)
    project = Project(sys.argv[1], [])
    profiler = Profiler(project)
    profiler.execution_time()
    print(profiler.__dict__)

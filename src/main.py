import sys
from analyzer import Analyzer
import general
import configurator

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <repo_path>")
        sys.exit(1)
    project = general.Project(sys.argv[1])
    configurator.configure(project)

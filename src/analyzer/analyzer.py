"""Module that analyzes project's repository and creates file with its information"""

import glob
import os
import json
from general import Colors

_TAB = 16


class Analyzer:
    """Class that analyzes project's repository and creates file with its information"""

    ci_list = ["**/ci", "**/.github/workflows"]

    build_systems_list = {
        "**/CMakeLists.txt": "cmake",
        "**/configure.ac": "autoconf",
        "**/*meson": "meson",
        "**/*bazel": "bazel",
    }

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.results = {
            "tests": [],
            "benchmarks": [],
            "ci": [],
            "build_systems": {
                "cmake": False,
                "autoconf": False,
                "meson": False,
                "bazel": False,
            },
            "dependencies": [],
        }

    def _rel_path(self, paths):
        parent_dir = os.path.dirname(os.path.normpath(self.repo_path))
        return [os.path.relpath(p, parent_dir) for p in paths]

    def _find_paths(self, pattern):
        paths = glob.glob(os.path.join(self.repo_path, pattern), recursive=True)
        return [p for p in paths if os.path.isdir(p)]

    def _path_existence(self, key, paths):
        if paths:
            self.results[f"{key}"] = self._rel_path(paths)

    def _path_output(self, key, paths):
        if paths:
            first = self._rel_path(paths)[0]
            print(f"{key}:".ljust(_TAB) + Colors.GREEN + first + Colors.NONE + "\n")
        else:
            print(f"{key}:".ljust(_TAB) + Colors.RED + "not found\n" + Colors.NONE)

    def _search_tests(self):
        paths = self._find_paths("**/*test*")
        self._path_existence("tests", paths)
        self._path_output("tests", paths)

    def _search_benchmarks(self):
        paths = self._find_paths("**/*benchmark*")
        self._path_existence("benchmarks", paths)
        self._path_output("benchmarks", paths)

    def _search_ci(self):
        path = []
        for pattern in self.ci_list:
            path.extend(self._find_paths(pattern))
        self._path_existence("ci", path)
        self._path_output("ci", path)

    def _search_build_systems(self):
        print("build systems:")
        for pattern, system in self.build_systems_list.items():
            if glob.glob(os.path.join(self.repo_path, pattern), recursive=True):
                self.results["build_systems"][system] = True
                print("".ljust(_TAB) + f"{system}")
        if not any(self.results["build_systems"].values()):
            print("".ljust(_TAB) + Colors.RED + "not found" + Colors.NONE)
        print()

    def _search_dependencies(self):
        dep_path = os.path.join(self.repo_path, "third_party")
        if os.path.exists(dep_path):
            dirs = [
                d
                for d in os.listdir(dep_path)
                if os.path.isdir(os.path.join(dep_path, d))
            ]
            self.results["dependencies"].extend(dirs)
        print("dependencies:")
        if self.results["dependencies"]:
            for dep in self.results["dependencies"]:
                print("".ljust(_TAB) + f"{dep}")
        else:
            print("".ljust(_TAB) + "not found")
        print()

    def analyze(self):
        """Analyzes project and collects its information"""

        if not os.path.exists(self.repo_path):
            raise FileNotFoundError(f'Directory "{self.repo_path}" not found')

        print(
            f"Analyzing {os.path.basename(os.path.normpath(self.repo_path))}\n" + "\n"
        )

        self._search_tests()
        self._search_benchmarks()
        self._search_ci()
        self._search_build_systems()
        self._search_dependencies()

        print("\nAnalyzing done\n")

        with open("amphimixis.log", "w", encoding="utf8") as file:
            json.dump(self.results, file, indent=4)
            print()

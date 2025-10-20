"""Module that analyzes project's repository and creates file with its information"""

import glob
import os
import json
from general import Colors

_TAB = 16


class Analyzer:
    """Class that analyzes project's repository and creates file with its information"""

    ci_list = ["**/ci", "**/.github/workflows/*.yml"]

    build_systems_list = {
        "**/CMakeLists.txt": "cmake",
        "**/configure.ac": "autoconf",
        "**/*meson": "meson",
        "**/*bazel": "bazel",
    }

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.results = {
            "tests": False,
            "benchmarks": False,
            "ci": False,
            "build_systems": {
                "cmake": False,
                "autoconf": False,
                "meson": False,
                "bazel": False,
            },
            "dependencies": [],
        }

    def _path_existence(self, pattern, path):
        if path:
            self.results[f"{pattern}"] = True

    def _path_output(self, pattern, path):
        if path:
            first_found_dir = path[0]
            parent_dir = os.path.dirname(os.path.normpath(self.repo_path))
            rel_path = os.path.relpath(first_found_dir, parent_dir)
            print(
                f"{pattern}:".ljust(_TAB) + Colors.GREEN + rel_path + Colors.NONE + "\n"
            )
        else:
            print(f"{pattern}:".ljust(_TAB) + Colors.RED + "not found\n" + Colors.NONE)

    def _search_tests(self):
        path = glob.glob(os.path.join(self.repo_path, "**/*test*"), recursive=True)
        self._path_existence("tests", path)
        self._path_output("tests", path)

    def _search_benchmarks(self):
        path = glob.glob(os.path.join(self.repo_path, "**/*benchmark*"), recursive=True)
        self._path_existence("benchmarks", path)
        self._path_output("benchmarks", path)

    def _search_ci(self):
        path = ""
        for pattern in self.ci_list:
            if not path:
                path = glob.glob(os.path.join(self.repo_path, pattern), recursive=True)
            else:
                break
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

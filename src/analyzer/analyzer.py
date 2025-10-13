"""Module that analyzes project's repository and creates file with its information"""

import glob
import os
import json
from general import Colors

_tab = 16


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
        self.basename = os.path.basename(os.path.normpath(repo_path))
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

    def _search_tests(self):
        path = glob.glob(os.path.join(self.repo_path, "**/*test*"), recursive=True)
        if path:
            self.results["tests"] = True
            first_found_dir = path[0]
            parent_dir = os.path.dirname(os.path.normpath(self.repo_path))
            rel_path = os.path.relpath(first_found_dir, parent_dir)
            print("tests:".ljust(_tab) + Colors.GREEN + rel_path + Colors.NONE + "\n")
        else:
            print("tests:".ljust(_tab) + Colors.RED + "not found\n" + Colors.NONE)

    def _search_benchmarks(self):
        path = glob.glob(os.path.join(self.repo_path, "**/*benchmark*"), recursive=True)
        if path:
            self.results["benchmarks"] = True
            first_found_dir = path[0]
            parent_dir = os.path.dirname(os.path.normpath(self.repo_path))
            rel_path = os.path.relpath(first_found_dir, parent_dir)
            print(
                "benchmarks:".ljust(_tab) + Colors.GREEN + rel_path + Colors.NONE + "\n"
            )
        else:
            print("benchmarks:".ljust(_tab) + Colors.RED + "not found\n" + Colors.NONE)

    def _search_ci(self):
        path = ""
        for pattern in self.ci_list:
            path = glob.glob(os.path.join(self.repo_path, pattern), recursive=True)
        if path:
            self.results["ci"] = True
            first_found_dir = path[0]
            parent_dir = os.path.dirname(os.path.normpath(self.repo_path))
            rel_path = os.path.relpath(first_found_dir, parent_dir)
            print("ci:".ljust(_tab) + Colors.GREEN + rel_path + Colors.NONE + "\n")
        else:
            print("ci:".ljust(_tab) + Colors.RED + "not found\n" + Colors.NONE)

    def _search_build_systems(self):
        print("build systems:")
        for pattern, system in self.build_systems_list.items():
            if glob.glob(os.path.join(self.repo_path, pattern), recursive=True):
                self.results["build_systems"][system] = True
                print("".ljust(_tab) + f"{system}")
        if not any(self.results["build_systems"].values()):
            print("".ljust(_tab) + Colors.RED + "not found" + Colors.NONE)
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
                print("".ljust(_tab) + f"{dep}")
        else:
            print("".ljust(_tab) + "not found")
        print()

    def analyze(self):
        """Analyzes project and collects its information"""

        if not os.path.exists(self.repo_path):
            raise FileNotFoundError(f'Directory "{self.repo_path}" not found')

        print(f"Analyzing {self.basename}\n" + "\n")

        self._search_tests()
        self._search_benchmarks()
        self._search_ci()
        self._search_build_systems()
        self._search_dependencies()

        print("\nAnalyzing done\n")

        with open("amphimixis.log", "w", encoding="utf8") as file:
            json.dump(self.results, file, indent=4)
            print()

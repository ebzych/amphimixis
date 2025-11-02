"""Module that analyzes project's repository and creates file with its information"""

import glob
import json
from os import path, listdir
import general
from general import Colors

_TAB = 16

ci_list = ["**/ci", "**/.github/workflows"]

build_systems_list = {
    "**/CMakeLists.txt": "cmake",
    "**/configure.ac": "autoconf",
    "**/*meson": "meson",
    "**/*bazel": "bazel",
}

results = {
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


def analyze(project: general.Project):
    """Analyzes project and collects its information"""

    proj_path = project.path

    if not path.exists(proj_path):
        raise FileNotFoundError(f'Directory "{proj_path}" not found')

    try:

        print(f"Analyzing {path.basename(path.normpath(proj_path))}\n" + "\n")

        _search_tests(proj_path)
        _search_benchmarks(proj_path)
        _search_ci(proj_path)
        _search_build_systems(proj_path)
        _search_dependencies(proj_path)

        print("\nAnalyzing done\n")

        with open("amphimixis.log", "w", encoding="utf8") as file:
            json.dump(results, file, indent=4)
            print()

    except FileNotFoundError as e:
        print(f"{e}")
        exit(-1)


def _rel_path(proj_path, paths):
    parent_dir = path.dirname(path.normpath(proj_path))
    return [path.relpath(p, parent_dir) for p in paths]


def _find_paths(proj_path, pattern, dirs_only=True):
    paths = glob.glob(path.join(proj_path, pattern), recursive=True)
    return [p for p in paths if path.isdir(p)] if dirs_only else paths


def _path_existence(proj_path, key, paths):
    if paths:
        results[f"{key}"] = _rel_path(proj_path, paths)


def _path_output(proj_path, key, paths):
    if paths:
        first = _rel_path(proj_path, paths)[0]
        print(f"{key}:".ljust(_TAB) + Colors.GREEN + first + Colors.NONE + "\n")
    else:
        print(f"{key}:".ljust(_TAB) + Colors.RED + "not found\n" + Colors.NONE)


def _search_tests(proj_path):
    paths = _find_paths(proj_path, "**/*test*")
    _path_existence(proj_path, "tests", paths)
    _path_output(proj_path, "tests", paths)


def _search_benchmarks(proj_path):
    paths = _find_paths(proj_path, "**/*benchmark*")
    _path_existence(proj_path, "benchmarks", paths)
    _path_output(proj_path, "benchmarks", paths)


def _search_ci(
    proj_path,
):
    paths = []
    for pattern in ci_list:
        paths.extend(_find_paths(proj_path, pattern))
    _path_existence(proj_path, "ci", paths)
    _path_output(proj_path, "ci", paths)


def _search_build_systems(
    proj_path,
):
    print("build systems:")
    for pattern, system in build_systems_list.items():
        if _find_paths(proj_path, pattern, dirs_only=False):
            results["build_systems"][system] = True
            print("".ljust(_TAB) + f"{system}")
    if not any(results["build_systems"].values()):
        print("".ljust(_TAB) + Colors.RED + "not found" + Colors.NONE)
    print()


def _search_dependencies(proj_path):
    dep_path = path.join(proj_path, "third_party")
    if path.exists(dep_path):
        dirs = [d for d in listdir(dep_path) if path.isdir(path.join(dep_path, d))]
        results["dependencies"].extend(dirs)
    print("dependencies:")
    if results["dependencies"]:
        for dep in results["dependencies"]:
            print("".ljust(_TAB) + f"{dep}")
    else:
        print("".ljust(_TAB) + "not found")
    print()

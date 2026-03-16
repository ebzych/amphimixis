"""Module that analyzes project's repository and creates file with its information"""

import glob
import re
import sys
from logging import Logger
from os import listdir, path

import yaml

from amphimixis.build_systems import build_systems_dict
from amphimixis.general import general
from amphimixis.logger import setup_logger

ci_list = ["**/ci", "**/.github/workflows"]

build_systems_list = {
    "cmake": ["**/CMakeLists.txt"],
    "meson": ["**/*meson*"],
    "bazel": ["**/*bazel*", "**/BUILD", "**/WORKSPACE"],
    "make": ["**/Makefile", "**/makefile"],
    "SCons": ["**/*SCons*"],
    "autoconf": ["**/configure.ac", "**/configure.in"],
}


def analyze(
    project: general.Project, generating_files: bool = True, logging: bool = True
) -> dict | None:
    """Analyzes project and collects its information"""

    logger = setup_logger("analyzer", dummy_logging=logging)

    results: dict[str, list[str] | str | None] = {
        "tests": [],
        "benchmarks": [],
        "ci": [],
        "build_systems": [],
        "dependencies": [],
    }

    proj_path = project.path
    if not path.exists(proj_path):
        logger.error("Directory '%s' not found", proj_path)
        return None

    logger.info("Analyzing %s", path.basename(path.normpath(proj_path)))

    _search_tests(proj_path, results, logger)
    _search_benchmarks(proj_path, results, logger)
    _search_ci(proj_path, results, logger)
    _search_build_systems(proj_path, results, logger)
    _search_dependencies(proj_path, results, logger)

    if generating_files:
        _file_output(results["build_systems"])

    logger.info("Analyzing done")

    return results


def _rel_path(proj_path, p):
    parent_dir = path.dirname(path.normpath(proj_path))
    return path.relpath(p, parent_dir)


def _find_paths(proj_path, pattern, dirs_only=True):
    paths = glob.glob(path.join(proj_path, pattern), recursive=True)
    return [p for p in paths if path.isdir(p)] if dirs_only else paths


def _logger_results(proj_path, results, key, paths, logger: Logger):
    if paths:
        first_path = paths[0]
        rel_path = _rel_path(proj_path, first_path)
        results[key] = rel_path
        logger.info("found %s: %s", key, rel_path)
    else:
        logger.info("%s: not found", key)


def _file_output(results, file_name="amphimixis.analyzed"):
    with open(
        file_name,
        "w",
        encoding="utf8",
    ) as file:
        yaml.dump(results, file, sort_keys=False)


def _search_tests(proj_path, results, logger: Logger):
    paths = _find_paths(proj_path, "**/*test*")
    _logger_results(proj_path, results, "tests", paths, logger)


def _search_benchmarks(proj_path, results, logger: Logger):
    paths = _find_paths(proj_path, "**/*bench*")
    _logger_results(proj_path, results, "benchmarks", paths, logger)


def _search_ci(proj_path, results, logger: Logger):
    paths = []
    for pattern in ci_list:
        paths.extend(_find_paths(proj_path, pattern))

    _logger_results(proj_path, results, "ci", paths, logger)


def _search_build_systems(proj_path, results, logger: Logger):
    logger.info("build systems:")
    found = False
    for system, patterns in build_systems_list.items():
        for pat in patterns:
            matched_paths = _find_paths(proj_path, pat, dirs_only=False)
            matched_files = [p for p in matched_paths if path.isfile(p)]
            if matched_files:
                if system not in results["build_systems"]:
                    results["build_systems"].append(system)
                    logger.info("  %s", system)

                found = True
                break

    if not found:
        logger.info("  not found")


def _search_dependencies(proj_path, results, logger: Logger):
    logger.info("dependencies:")

    _third_party_dependencies(proj_path, results, logger)
    _cmake_dependencies(proj_path, results, logger)

    # no dependencies
    if not results["dependencies"]:
        logger.info("  not found")


def _third_party_dependencies(proj_path, results, logger):
    dep_path = path.join(proj_path, "third_party")
    if path.exists(dep_path):
        dirs = [d for d in listdir(dep_path) if path.isdir(path.join(dep_path, d))]
        for d in dirs:
            if d not in results["dependencies"]:
                results["dependencies"].append(d)
                logger.info("  %s", d)


def _cmake_dependencies(proj_path, results, logger):
    if "cmake" not in results["build_systems"]:
        return

    file_path = path.join(proj_path, "CMakeLists.txt")
    if not path.isfile(file_path):
        logger.info("  no CMakeLists.txt in project root")
        return

    with open(file_path, "r", encoding="utf8") as file:
        text = file.read()

    text = re.sub(r"#.*", "", text)
    pattern = r"find_package\s*\(\s*([\w+-]+)"
    packages = re.findall(pattern, text, flags=re.IGNORECASE)
    for package in packages:
        if package not in results["dependencies"]:
            results["dependencies"].append(package)
            logger.info("  %s", package)


if __name__ == "__main__":
    print(
        analyze(
            general.Project(sys.argv[1]),
            generating_files=False,
            logging=False,
        )
    )

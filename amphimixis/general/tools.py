"""Helpers for building and parsing readable, reversible profiling filenames.

This module contains utility functions for encoding build names and executable
paths into filesystem-friendly filenames and decoding them back without losing
information.
"""

import os
import pickle

from amphimixis.general.constants import PERF_STATS_EXT
from amphimixis.general.general import Project


def build_filename(build_name: str, executable: str) -> str:
    """Build a reversible filename."""

    escaped_build = escape_filename_part(build_name)
    escaped_executable = escape_filename_part(os.path.normpath(executable))
    return f"{escaped_build}..{escaped_executable}"


def parse_filename(filename: str) -> tuple[str, str]:
    """Decode a filename produced by `build_filename()`."""

    separator = filename.find("..")
    if separator == -1:
        raise ValueError(f"Invalid perf record filename: {filename}")

    build_name = unescape_filename_part(filename[:separator])
    executable = unescape_filename_part(filename[separator + 2 :])
    return build_name, executable


def escape_filename_part(value: str) -> str:
    """Escape a build or executable name for a readable, reversible filename."""

    escaped = []
    for char in value:
        if char.isalnum() or char == "-":
            escaped.append(char)
        elif char == "_":
            escaped.append("__")
        elif char == "/":
            escaped.append("_s")
        elif char == ".":
            escaped.append("_d")
        else:
            escaped.append(f"_x{ord(char):02x}_")
    return "".join(escaped)


def unescape_filename_part(value: str) -> str:
    """Decode a filename part produced by `escape_filename_part()`."""

    decoded = []
    idx = 0
    while idx < len(value):
        char = value[idx]
        if char != "_":
            decoded.append(char)
            idx += 1
            continue

        if idx + 1 >= len(value):
            raise ValueError(f"Invalid escaped filename part: {value}")

        marker = value[idx + 1]
        if marker == "_":
            decoded.append("_")
            idx += 2
        elif marker == "s":
            decoded.append("/")
            idx += 2
        elif marker == "d":
            decoded.append(".")
            idx += 2
        elif marker == "x":
            hex_end = value.find("_", idx + 2)
            if hex_end == -1:
                raise ValueError(f"Invalid escaped filename part: {value}")
            decoded.append(chr(int(value[idx + 2 : hex_end], 16)))
            idx = hex_end + 1
        else:
            raise ValueError(f"Invalid escaped filename part: {value}")

    return "".join(decoded)


def project_name(project: Project):
    """Generate project name based on project object"""
    return os.path.basename(os.path.normpath(project.path))


def load_project_stats(project: Project):
    """Loads profiler statistics of the project"""
    with open(
        escape_filename_part(project_name(project)) + PERF_STATS_EXT,
        "rb",
    ) as file:
        return pickle.load(file)

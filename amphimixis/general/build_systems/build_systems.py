"""Containing the dictionary with name strings of build systems and associated IBuildSystem implementations"""

# pylint: disable=relative-beyond-top-level
from .cmake import CMake

# pylint: disable=relative-beyond-top-level
from .make import Make

# pylint: disable=relative-beyond-top-level
from ..general import IBuildSystem

build_systems_dict: dict[str, "type[IBuildSystem]"] = {
    "cmake": CMake,
    "make": Make,
}

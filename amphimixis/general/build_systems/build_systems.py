"""Containing the dictionary with name strings of build systems and associated IBuildSystem implementations"""

from amphimixis.general.build_systems.cmake import CMake
from amphimixis.general.build_systems.make import Make
from amphimixis.general.general import IBuildSystem

build_systems_dict: dict[str, "type[IBuildSystem]"] = {
    "cmake": CMake,
    "make": Make,
}

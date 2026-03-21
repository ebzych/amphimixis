"""Containing the dictionary with name strings of "
"build systems and associated IBuildSystem implementations"""

from amphimixis.build_systems.cmake import CMake
from amphimixis.build_systems.make import Make
from amphimixis.build_systems.ninja import Ninja
from amphimixis.general.general import BuildSystem, ILowLevelBuildSystem

# First element -- class of matched build system,
# other are runners for this build system in priority
build_systems_dict: dict[str, list[type[BuildSystem]]] = {
    "cmake": [CMake, Ninja, Make],
    "make": [Make],
}

runners_dict: dict[str, type[ILowLevelBuildSystem]] = {
    "make": Make,
    "ninja": Ninja,
}

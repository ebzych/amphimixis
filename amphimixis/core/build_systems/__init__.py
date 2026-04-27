"""Module containing dictionary of build systems and implementations of build systems"""

from amphimixis.core.build_systems.build_systems import (
    get_build_system,
    get_runner,
    get_build_system_runner,
)
from amphimixis.core.build_systems.cmake import CMake
from amphimixis.core.build_systems.make import Make
from amphimixis.core.build_systems.ninja import Ninja

__all__ = [
    "get_build_system",
    "get_runner",
    "get_build_system_runner",
    "CMake",
    "Make",
    "Ninja",
]

"""Module containing dictionary of build systems and implementations of build systems"""

from amphimixis.build_systems.autoconf import Autoconf
from amphimixis.build_systems.bazel import Bazel
from amphimixis.build_systems.bison import Bison
from amphimixis.build_systems.build_systems import build_systems_dict, runners_dict
from amphimixis.build_systems.cmake import CMake
from amphimixis.build_systems.gmake import Gmake
from amphimixis.build_systems.make import Make
from amphimixis.build_systems.meson import Meson
from amphimixis.build_systems.ninja import Ninja
from amphimixis.build_systems.yacc import Yacc

__all__ = [
    "build_systems_dict",
    "runners_dict",
    "CMake",
    "Make",
    "Ninja",
    "Meson",
    "Autoconf",
    "Bazel",
    "Gmake",
    "Yacc",
    "Bison",
]

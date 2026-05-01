"""Containing the dictionaries with name strings of
build systems/runners and associated
IHighLevelBuildSystem/ILowLevelBuildSystem implementations
"""

from amphimixis.core.build_systems.cmake import CMake
from amphimixis.core.build_systems.make import Make
from amphimixis.core.build_systems.ninja import Ninja
from amphimixis.core.general.general import (
    BuildSystem,
    IHighLevelBuildSystem,
    ILowLevelBuildSystem,
    BuildSystemIsNotHighLevel,
    BuildSystemIsNotLowLevel,
)


def get_build_system(name: str) -> type[BuildSystem] | None:
    """Get build system type by build system name

    :param str name: Build system name
    :rtype: type[BuildSystem] | None
    :return: Build system type if found otherwise None
    :raises BuildSystemIsNotHighLevel:"""
    if name.lower() not in _build_systems_dict:
        return None
    bs = _build_systems_dict[name.lower()][BUILD_SYSTEM]
    if not issubclass(bs, IHighLevelBuildSystem):  # type: ignore[arg-type]
        raise BuildSystemIsNotHighLevel
    return bs  # type: ignore[return-value]


def get_runner(name: str) -> type[BuildSystem] | None:
    """Get runner type by runner name

    :param str name: Runner name
    :rtype: type[BuildSystem] | None
    :return: Build system type if found otherwise None
    :raises RunnerIsNotLowLevel:"""
    if name.lower() not in _runners_dict:
        return None
    rr = _runners_dict[name.lower()]
    if not issubclass(rr, ILowLevelBuildSystem):
        raise BuildSystemIsNotLowLevel
    return rr  # type: ignore[return-value]


def get_build_system_runner(build_system_name: str) -> type[BuildSystem] | None:
    """Get priority runner type by build system name

    :param str name: Build system name
    :rtype: type[BuildSystem] | None
    :return: Build system type if found otherwise None
    :raises RunnerIsNotLowLevel:"""
    if (
        len(
            _build_systems_dict[build_system_name.lower()][RUNNER_LIST]  # type: ignore[arg-type]
        )
        == 0
    ):
        return None
    rr = _build_systems_dict[build_system_name.lower()][RUNNER_LIST][
        PRIORITY_RUNNER
    ]  # type: ignore[index]
    if not issubclass(rr, ILowLevelBuildSystem) or rr not in _runners_dict.values():
        raise BuildSystemIsNotLowLevel
    return rr  # type: ignore[return-value]


BUILD_SYSTEM = 0
RUNNER_LIST = 1
PRIORITY_RUNNER = 0

# First element in tuple -- class of matched build system,
# types in second element are runners for this build system in priority
_build_systems_dict: dict[
    str,
    tuple[
        type[IHighLevelBuildSystem],
        list[type[ILowLevelBuildSystem]],
    ],
] = {
    "cmake": (CMake, [Ninja, Make]),
    "make": (Make, []),  # has no runners because it low-level build system
}


_runners_dict: dict[str, type[ILowLevelBuildSystem]] = {
    "make": Make,
    "ninja": Ninja,
}

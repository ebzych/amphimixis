"""Core module that contains director with main API and modules that he uses"""

from amphimixis.core.analyzer import analyze
from amphimixis.core.build_systems import (
    get_build_system,
    get_runner,
    get_build_system_runner,
)
from amphimixis.core.builder import Builder
from amphimixis.core.configurator import (
    create_flags,
    create_machine,
    create_toolchain,
    parse_config,
)
from amphimixis.core import general
from amphimixis.core.laboratory_assistant import LaboratoryAssistant
from amphimixis.core.profiler import Profiler
from amphimixis.core.shell import Shell
from amphimixis.core.validator import validate

# pylint: disable=duplicate-code
__all__ = [
    "general",
    "get_build_system",
    "get_runner",
    "get_build_system_runner",
    "analyze",
    "create_flags",
    "create_machine",
    "create_toolchain",
    "parse_config",
    "Builder",
    "Profiler",
    "Shell",
    "LaboratoryAssistant",
    "validate",
]

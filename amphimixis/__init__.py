"""Core module that contains director with main API and modules that he uses"""

from amphimixis.general import general, Colors
from amphimixis.general.build_systems import build_systems_dict
from amphimixis.analyzer import analyze
from amphimixis.configurator import parse_config
from amphimixis.builder import Builder
from amphimixis.profiler import Profiler
from amphimixis.shell import Shell
from amphimixis.toolchain_manager import ToolchainManager


__all__ = [
    "general",
    "build_systems_dict",
    "Colors",
    "analyze",
    "parse_config",
    "Builder",
    "Profiler",
    "Shell",
    "ToolchainManager",
]

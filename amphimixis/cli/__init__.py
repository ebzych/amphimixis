"""CLI module"""

from .commands import (
    clean,
    interactive_clean,
    parse_full_pipeline_args,
    run_add_input,
    run_add_toolchain,
    run_analyze,
    run_build,
    run_compare,
    run_full_pipeline,
    run_profile,
    show_profiling_result,
)
from .parser import DEFAULT_CONFIG_PATH, create_parser
from .templates import CONFIG_TEMPLATE, TOOLCHAIN_TEMPLATE

__all__ = [
    "create_parser",
    "run_analyze",
    "run_build",
    "run_compare",
    "run_profile",
    "run_add_input",
    "run_add_toolchain",
    "clean",
    "interactive_clean",
    "DEFAULT_CONFIG_PATH",
    "show_profiling_result",
    "parse_full_pipeline_args",
    "run_full_pipeline",
    "TOOLCHAIN_TEMPLATE",
    "CONFIG_TEMPLATE",
]
